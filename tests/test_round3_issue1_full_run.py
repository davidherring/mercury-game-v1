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


async def _post_ok(client: AsyncClient, url: str, payload: dict) -> None:
    resp = await client.post(url, json=payload)
    resp.raise_for_status()
    await resp.aread()


async def _post_json(client: AsyncClient, url: str, payload: dict) -> dict:
    resp = await client.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    await resp.aread()
    return data


async def _get_json(client: AsyncClient, url: str) -> dict:
    resp = await client.get(url)
    resp.raise_for_status()
    data = resp.json()
    await resp.aread()
    return data


async def _with_session(fn):
    agen = get_session()
    session: AsyncSession = await agen.__anext__()
    try:
        return await fn(session)
    finally:
        await agen.aclose()


async def _reach_position_finalization(client: AsyncClient, human_role: str = "AMAP", human_placement: str = "skip", seed: int = 12345) -> str:
    # Note: Japan (JPN) cannot be chosen as human. Using NGO default keeps debate AI-only when placement is skip.
    # human_placement="skip" prevents HUMAN_DEBATE_MESSAGE requirements unless explicitly testing human debate turns.
    create_payload = await _post_json(client, "/games", {})
    game_id = create_payload["game_id"]
    # Set deterministic seed
    async def _set_seed(session: AsyncSession):
        async with session.begin():
            await session.execute(text("UPDATE games SET seed = :seed WHERE id = :gid"), {"seed": seed, "gid": game_id})

    await _with_session(_set_seed)
    await _post_ok(
        client,
        f"/games/{game_id}/advance",
        {"event": "ROLE_CONFIRMED", "payload": {"human_role_id": human_role}},
    )
    r1_ready = await _post_json(client, f"/games/{game_id}/advance", {"event": "ROUND_1_READY", "payload": {}})
    order_len = len(r1_ready["state"]["round1"]["speaker_order"])
    for _ in range(order_len):
        await _post_ok(client, f"/games/{game_id}/advance", {"event": "ROUND_1_STEP", "payload": {}})
    await _post_ok(client, f"/games/{game_id}/advance", {"event": "ROUND_2_READY", "payload": {}})
    await _post_ok(
        client,
        f"/games/{game_id}/advance",
        {"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
    )
    for i in range(5):
        await _post_ok(
            client,
            f"/games/{game_id}/advance",
            {"event": "CONVO_1_MESSAGE", "payload": {"content": f"h{i}"}},
        )
    await _post_ok(
        client,
        f"/games/{game_id}/advance",
        {"event": "CONVO_1_MESSAGE", "payload": {"content": "final"}},
    )
    await _post_ok(client, f"/games/{game_id}/advance", {"event": "CONVO_2_SKIPPED", "payload": {}})
    await _post_ok(client, f"/games/{game_id}/advance", {"event": "ROUND_2_WRAP_READY", "payload": {}})
    await _post_ok(
        client,
        f"/games/{game_id}/advance",
        {"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": "1", "human_placement": human_placement}},
    )
    await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_INTRO_CONTINUE", "payload": {}})
    # consume debate rounds fully (all AI)
    state = (await _get_json(client, f"/games/{game_id}"))["state"]
    queue1 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue1)):
        await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
    state = (await _get_json(client, f"/games/{game_id}"))["state"]
    queue2 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue2)):
        await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
    return game_id


@pytest.mark.asyncio
async def test_full_issue1_ai_votes_and_resolution():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        game_id = await _reach_position_finalization(client, human_role="AMAP", human_placement="skip")

        state = (await _get_json(client, f"/games/{game_id}"))["state"]
        assert state["status"] == "ISSUE_POSITION_FINALIZATION"

        async def _read_before(session: AsyncSession):
            t_before = await _count(session, "transcript_entries", game_id)
            c_before = await _count(session, "checkpoints", game_id)
            return t_before, c_before

        t_before, c_before = await _with_session(_read_before)

        # Proposal selection
        prop_payload = await _post_json(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
        state = prop_payload["state"]
        assert state["status"] == "ISSUE_VOTE"
        proposed = state["round3"]["active_issue"]["proposed_option_id"]
        assert proposed in ("1.1", "1.2")

        # 6 votes
        for _ in range(6):
            await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
        state = (await _get_json(client, f"/games/{game_id}"))["state"]
        assert state["status"] == "ISSUE_RESOLUTION"

        # resolution transcript
        res_payload = await _post_json(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
        final_state = res_payload["state"]
        assert final_state["status"] == "ISSUE_RESOLUTION"
        votes = final_state["round3"]["active_issue"]["votes"]
        assert len(votes) == 6

        async def _read_after(session: AsyncSession):
            t_after = await _count(session, "transcript_entries", game_id)
            c_after = await _count(session, "checkpoints", game_id)
            return t_after, c_after

        t_after, c_after = await _with_session(_read_after)

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
        await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
        state = (await _get_json(client, f"/games/{game_id}"))["state"]
        assert state["status"] == "ISSUE_VOTE"

        # first voter is BRA; progress until USA turn
        idx = 0
        while True:
            state = (await _get_json(client, f"/games/{game_id}"))["state"]
            ai = state["round3"]["active_issue"]
            order = ai["vote_order"]
            cur = ai["next_voter_index"]
            voter = order[cur]
            async def _read_before(session: AsyncSession):
                t_before = await _count(session, "transcript_entries", game_id)
                c_before = await _count(session, "checkpoints", game_id)
                return t_before, c_before

            t_before, c_before = await _with_session(_read_before)
            if voter == "USA":
                bad = await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
                assert bad.status_code == 400
                await bad.aread()
                await _post_ok(
                    client,
                    f"/games/{game_id}/advance",
                    {"event": "HUMAN_VOTE", "payload": {"vote": "YES"}},
                )
                async def _read_after(session: AsyncSession):
                    t_after = await _count(session, "transcript_entries", game_id)
                    c_after = await _count(session, "checkpoints", game_id)
                    return t_after, c_after

                t_after, c_after = await _with_session(_read_after)
                assert t_after - t_before == 1
                assert c_after - c_before == 1
                break
            else:
                await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
            idx += 1


@pytest.mark.asyncio
async def test_issue1_determinism():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    transcripts = []
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for _ in range(2):
            game_id = await _reach_position_finalization(client, human_role="AMAP", human_placement="skip")
            await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
            for _ in range(6):
                await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
            await _post_ok(client, f"/games/{game_id}/advance", {"event": "ISSUE_DEBATE_STEP", "payload": {}})
            entries = (await _get_json(client, f"/games/{game_id}/transcript"))
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
