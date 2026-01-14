import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any, cast
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.ai import FakeLLM
from backend.db import get_session


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _reach_position_finalization(client: AsyncClient, human_role: str = "AMAP", human_placement: str = "skip", seed: int = 12345) -> str:
    # Note: Japan (JPN) cannot be chosen as human. Using NGO default keeps debate AI-only when placement is skip.
    # human_placement="skip" prevents HUMAN_DEBATE_MESSAGE requirements unless explicitly testing human debate turns.
    create_resp = await client.post("/games", json={})
    assert create_resp.status_code == 200
    game_id = create_resp.json()["game_id"]
    # Set deterministic seed
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        async with session.begin():
            await session.execute(text("UPDATE games SET seed = :seed WHERE id = :gid"), {"seed": seed, "gid": game_id})
        break
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": human_role}})
    assert resp.status_code == 200
    r1_ready = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
    assert r1_ready.status_code == 200
    order_len = len(r1_ready.json()["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        step_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        assert step_resp.status_code == 200
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
    assert resp.status_code == 200
    resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    assert resp.status_code == 200
    for i in range(5):
        resp = await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
        )
        assert resp.status_code == 200
    resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
    )
    assert resp.status_code == 200
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "CONVO_2_SKIPPED", "payload": {}})
    assert resp.status_code == 200
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_WRAP_READY", "payload": {}})
    assert resp.status_code == 200
    resp = await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": human_placement}},
    )
    assert resp.status_code == 200
    resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
    assert resp.status_code == 200
    # consume debate rounds fully (all AI)
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue1 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue1)):
        step = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert step.status_code == 200
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue2 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue2)):
        step = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert step.status_code == 200
    return game_id


@pytest.mark.asyncio
async def test_full_issue1_ai_votes_and_resolution():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_position_finalization(client, human_role="AMAP", human_placement="skip")

        state = (await client.get(f"/games/{game_id}")).json()["state"]
        assert state["status"] == "ISSUE_POSITION_FINALIZATION"

        t_before = c_before = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            break

        # Proposal selection
        prop_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert prop_resp.status_code == 200
        state = prop_resp.json()["state"]
        assert state["status"] == "ISSUE_VOTE"
        proposed = state["round3"]["active_issue"]["proposed_option_id"]
        assert proposed in ("1.1", "1.2")

        # 6 votes
        for _ in range(6):
            vote_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            assert vote_resp.status_code == 200
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        assert state["status"] == "ISSUE_RESOLUTION"

        # resolution transcript
        res_resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        assert res_resp.status_code == 200
        final_state = res_resp.json()["state"]
        assert final_state["status"] == "ISSUE_RESOLUTION"
        votes = final_state["round3"]["active_issue"]["votes"]
        assert len(votes) == 6

        t_after = c_after = 0
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            break

        # deltas: +1 proposal +6 votes +1 resolution
        assert t_after - t_before == 8
        assert c_after - c_before == 8


@pytest.mark.asyncio
async def test_human_vote_required():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_position_finalization(client, human_role="USA", human_placement="skip")
        # proposal
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        assert state["status"] == "ISSUE_VOTE"

        # first voter is BRA; progress until USA turn
        idx = 0
        while True:
            state = (await client.get(f"/games/{game_id}")).json()["state"]
            ai = state["round3"]["active_issue"]
            order = ai["vote_order"]
            cur = ai["next_voter_index"]
            voter = order[cur]
            t_before = c_before = 0
            async for session in get_session():
                assert isinstance(session, AsyncSession)
                t_before = await _count(session, "transcript_entries", game_id)
                c_before = await _count(session, "checkpoints", game_id)
                break
            if voter == "USA":
                bad = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
                assert bad.status_code == 400
                good = await client.post(
                    f"/games/{game_id}/advance",
                    json={"event": "HUMAN_VOTE", "payload": {"vote": "YES"}},
                )
                assert good.status_code == 200
                t_after = c_after = 0
                async for session in get_session():
                    assert isinstance(session, AsyncSession)
                    t_after = await _count(session, "transcript_entries", game_id)
                    c_after = await _count(session, "checkpoints", game_id)
                    break
                assert t_after - t_before == 1
                assert c_after - c_before == 1
                break
            else:
                resp = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
                assert resp.status_code == 200
            idx += 1


@pytest.mark.asyncio
async def test_issue1_determinism():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    transcripts = []
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for _ in range(2):
            game_id = await _reach_position_finalization(client, human_role="AMAP", human_placement="skip")
            await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            for _ in range(6):
                await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
            resp = await client.get(f"/games/{game_id}/transcript")
            entries = resp.json()
            # Filter to Round 3 issue transcript only
            round3_entries = []
            for e in entries:
                round_val = e.get("round")
                phase = e.get("phase")
                content = e.get("content", "")
                if round_val == 3:
                    round3_entries.append((e["role_id"], content))
                elif phase and phase.startswith("ISSUE_"):
                    round3_entries.append((e["role_id"], content))
                elif content.startswith("We now consider Issue 1:"):
                    round3_entries.append((e["role_id"], content))
            transcripts.append(round3_entries)

    assert transcripts[0] == transcripts[1]
