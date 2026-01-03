import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, cast

from backend.main import app
from backend.db import get_session


@pytest.mark.asyncio(scope="session")
async def test_transcript_empty_returns_list():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_resp = await client.post("/games", json={})
        assert create_resp.status_code == 200
        game_id = create_resp.json()["game_id"]

        resp = await client.get(f"/games/{game_id}/transcript")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio(scope="session")
async def test_transcript_filtering_and_ordering():
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_resp = await client.post("/games", json={})
        assert create_resp.status_code == 200
        game_id = create_resp.json()["game_id"]

        # Insert transcript entries directly
        async for session in get_session():
            assert isinstance(session, AsyncSession)
            async with session.begin():
                await session.execute(
                    text(
                        """
                        INSERT INTO transcript_entries
                        (game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata, created_at)
                        VALUES
                        (:gid, 'JPN', 'ROUND_1', 1, NULL, true, 'msg1', :meta1, '2020-01-01T00:00:01Z'),
                        (:gid, 'USA', 'ROUND_1', 1, NULL, true, 'msg2', :meta2, '2020-01-01T00:00:02Z'),
                        (:gid, 'BRA', 'ROUND_1', 1, NULL, false, 'msg3', :meta3, '2020-01-01T00:00:03Z')
                        """
                    ),
                    {
                        "gid": game_id,
                        "meta1": json.dumps({"order": 1}),
                        "meta2": json.dumps({"order": 2}),
                        "meta3": json.dumps({"order": 3}),
                    },
                )
            break  # ensure only one session iteration

        # All entries
        resp_all = await client.get(f"/games/{game_id}/transcript")
        assert resp_all.status_code == 200
        all_entries = resp_all.json()
        assert len(all_entries) == 3
        # Ordered by created_at/id; ensure content order matches insertion order under ASC
        contents_all = [e["content"] for e in all_entries]
        assert contents_all == ["msg1", "msg2", "msg3"]

        # Filter visible true
        resp_true = await client.get(f"/games/{game_id}/transcript", params={"visible_to_human": "true"})
        assert resp_true.status_code == 200
        entries_true = resp_true.json()
        assert len(entries_true) == 2
        assert all(e["visible_to_human"] is True for e in entries_true)
        contents_true = [e["content"] for e in entries_true]
        assert contents_true == ["msg1", "msg2"]

        # Filter visible false
        resp_false = await client.get(f"/games/{game_id}/transcript", params={"visible_to_human": "false"})
        assert resp_false.status_code == 200
        entries_false = resp_false.json()
        assert len(entries_false) == 1
        assert entries_false[0]["visible_to_human"] is False
        assert entries_false[0]["content"] == "msg3"
