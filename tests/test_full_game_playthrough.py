import json
from typing import Any, Dict, List, Tuple, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app
from backend.state import VOTE_ORDER
from tests.test_round3_issues_2_4_full_run import _reach_round3_setup_generic


async def _count(session: AsyncSession, table: str, game_id: str) -> int:
    res = await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE game_id = :gid"), {"gid": game_id})
    return res.scalar_one()


async def _run_issue_to_resolution(
    client: AsyncClient, *, issue_id: str, human_role: str = "AMAP", seed: int = 12345
) -> Tuple[str, Dict[str, Any]]:
    game_id = await _reach_round3_setup_generic(client, human_role=human_role, seed=seed)
    await client.post(
        f"/games/{game_id}/advance",
        json={"event": "ROUND_3_START_ISSUE", "payload": {"issue_id": issue_id, "human_placement": "skip"}},
    )
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_INTRO_CONTINUE", "payload": {}})

    # Debate rounds
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue1 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue1)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    state = (await client.get(f"/games/{game_id}")).json()["state"]
    queue2 = state["round3"]["active_issue"]["debate_queue"]
    for _ in range(len(queue2)):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    # Proposal
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    # Votes
    for _ in range(6):
        await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})

    # Resolution
    await client.post(f"/games/{game_id}/advance", json={"event": "ISSUE_DEBATE_STEP", "payload": {}})
    final_state = (await client.get(f"/games/{game_id}")).json()["state"]
    return game_id, final_state


async def _round_counts(session: AsyncSession, game_id: str) -> Dict[int, int]:
    res = await session.execute(
        text("SELECT COALESCE(round,0) as rnd, COUNT(*) FROM transcript_entries WHERE game_id = :gid GROUP BY rnd"),
        {"gid": game_id},
    )
    return {int(row[0]): row[1] for row in res}


@pytest.mark.asyncio
async def test_full_game_playthrough():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()

    issues = ["1", "2", "3", "4"]
    summary: List[Dict[str, Any]] = []

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for idx, issue_id in enumerate(issues):
            game_id, final_state = await _run_issue_to_resolution(
                client, issue_id=issue_id, human_role="AMAP", seed=12345 + idx
            )

            # Basic state assertions
            assert final_state["status"] == "ISSUE_RESOLUTION"
            active = final_state["round3"]["active_issue"]
            assert active["issue_id"] == issue_id
            votes = active.get("votes", {})
            assert set(votes.keys()) == set(VOTE_ORDER)

            # Transcript/checkpoint counts
            agen = get_session()
            session = await agen.__anext__()
            try:
                totals_by_round = await _round_counts(session, game_id)
                t_total = await _count(session, "transcript_entries", game_id)
                c_total = await _count(session, "checkpoints", game_id)

                # Extract vote order from transcript for this issue
                vote_rows = await session.execute(
                    text(
                        """
                        SELECT role_id
                        FROM transcript_entries
                        WHERE game_id = :gid
                          AND phase = 'ISSUE_VOTE'
                          AND (metadata ->> 'issue_id') = :iid
                          AND metadata ? 'vote'
                        ORDER BY created_at ASC, id ASC
                        """
                    ),
                    {"gid": game_id, "iid": issue_id},
                )
                vote_sequence = [r[0] for r in vote_rows.fetchall()]
            finally:
                await agen.aclose()

            assert c_total <= t_total
            assert vote_sequence == list(VOTE_ORDER)

            summary.append(
                {
                    "issue_id": issue_id,
                    "game_id": game_id,
                    "status": final_state["status"],
                    "votes": votes,
                    "transcripts_by_round": totals_by_round,
                    "checkpoints": c_total,
                    "transcripts_total": t_total,
                }
            )

    print(json.dumps(summary, indent=2))
