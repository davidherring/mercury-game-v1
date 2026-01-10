import pytest
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, cast

from backend.ai import FakeLLM
from backend.db import get_session
from backend.main import app


@pytest.mark.asyncio(scope="session")
async def test_transcript_order_stable_by_index_and_id():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]

        fixed_ts = datetime(2020, 1, 1, tzinfo=timezone.utc)
        entries = [
          {"content": "msg1", "idx": 2},
          {"content": "msg0", "idx": 1},
        ]

        agen = get_session()
        session: AsyncSession = await agen.__anext__()
        try:
            async with session.begin():
                stmt = (
                    text(
                        """
                        INSERT INTO transcript_entries (game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata, created_at)
                        VALUES (:gid, 'USA', 'ROUND_2', 2, NULL, true, :content, :metadata, :created_at)
                        """
                    )
                    .bindparams(
                        bindparam("metadata", type_=JSONB),
                        bindparam("created_at", type_=TIMESTAMP(timezone=True)),
                    )
                )
                for e in entries:
                    await session.execute(
                        stmt,
                        {
                            "gid": game_id,
                            "content": e["content"],
                            "metadata": {"index": e["idx"]},
                            "created_at": fixed_ts,
                        },
                    )
        finally:
            await agen.aclose()

        resp = await client.get(f"/games/{game_id}/transcript")
        resp.raise_for_status()
        data = resp.json()
        assert [row["content"] for row in data] == ["msg0", "msg1"]


@pytest.mark.asyncio(scope="session")
async def test_round1_recognize_before_opening():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]
        # Confirm role and run first opening step
        await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        resp = await client.get(f"/games/{game_id}/transcript")
        resp.raise_for_status()
        contents = [row["content"] for row in resp.json()]
        recognize_idx = next((i for i, c in enumerate(contents) if "I recognize" in c), None)
        opening_idx = next((i for i, c in enumerate(contents) if "opening placeholder" in c), None)
        assert recognize_idx is not None and opening_idx is not None
        assert recognize_idx < opening_idx


@pytest.mark.asyncio(scope="session")
async def test_round2_human_before_ai():
    transport = ASGITransport(app=cast(Any, app))
    app.state.ai_responder = FakeLLM()
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create = await client.post("/games", json={})
        create.raise_for_status()
        game_id = create.json()["game_id"]
        await client.post(f"/games/{game_id}/advance", json={"event": "ROLE_CONFIRMED", "payload": {"human_role_id": "USA"}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_READY", "payload": {}})
        # consume openings
        state = (await client.get(f"/games/{game_id}")).json()["state"]
        order_len = len(state["round1"]["speaker_order"])
        for _ in range(order_len):
            await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_1_STEP", "payload": {}})
        await client.post(f"/games/{game_id}/advance", json={"event": "ROUND_2_READY", "payload": {}})
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_SELECTED", "payload": {"partner_role_id": "BRA"}},
        )
        test_msg = "hello-order-test"
        await client.post(
            f"/games/{game_id}/advance",
            json={"event": "CONVO_1_MESSAGE", "payload": {"content": test_msg}},
        )
        resp = await client.get(f"/games/{game_id}/transcript")
        resp.raise_for_status()
        contents = [row["content"] for row in resp.json()]
        human_idx = next((i for i, c in enumerate(contents) if test_msg in c), None)
        ai_idx = next((i for i, c in enumerate(contents) if "[FAKE_RESPONSE]" in c and test_msg in c), None)
        assert human_idx is not None and ai_idx is not None
        assert human_idx < ai_idx
