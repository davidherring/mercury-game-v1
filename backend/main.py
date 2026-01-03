import datetime
import json
import random
import uuid
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .state import (
    COUNTRIES,
    CHAIR,
    NGOS,
    ensure_default_stances,
    initial_state,
    pick_opening_variant,
    speaker_order_with_constraint,
)


app = FastAPI(title="Mercury Game Backend")


class CreateGameRequest(BaseModel):
    user_id: Optional[uuid.UUID] = Field(default=None)


class AdvanceRequest(BaseModel):
    event: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class GameResponse(BaseModel):
    game_id: uuid.UUID
    state: Dict[str, Any]


def utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


async def get_or_create_user(session: AsyncSession, user_id: Optional[uuid.UUID]) -> uuid.UUID:
    if user_id:
        existing = await session.execute(
            text("SELECT id FROM users WHERE id = :id LIMIT 1"), {"id": str(user_id)}
        )
        if existing.scalar_one_or_none():
            return uuid.UUID(str(user_id))
    display_name = "anonymous"
    inserted = await session.execute(
        text("INSERT INTO users (id, display_name) VALUES (COALESCE(:id, gen_random_uuid()), :name) RETURNING id"),
        {"id": str(user_id) if user_id else None, "name": display_name},
    )
    return uuid.UUID(str(inserted.scalar_one()))


async def fetch_game_with_state(session: AsyncSession, game_id: uuid.UUID) -> Dict[str, Any]:
    result = await session.execute(
        text(
            """
            SELECT g.id, g.status, g.seed, g.human_role_id, gs.state
            FROM games g
            JOIN game_state gs ON gs.game_id = g.id
            WHERE g.id = :id
            FOR UPDATE
            """
        ),
        {"id": str(game_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    state = row["state"] if isinstance(row["state"], dict) else json.loads(row["state"])
    return {
        "id": uuid.UUID(str(row["id"])),
        "status": row["status"],
        "seed": int(row["seed"]),
        "human_role_id": row["human_role_id"],
        "state": state,
    }


async def persist_state(
    session: AsyncSession,
    game_id: uuid.UUID,
    status: str,
    state: Dict[str, Any],
    checkpoint_transcript_id: Optional[uuid.UUID] = None,
) -> None:
    state["status"] = status
    state["updated_at"] = utc_iso()
    await session.execute(
        text("UPDATE games SET status = :status WHERE id = :id"),
        {"status": status, "id": str(game_id)},
    )
    await session.execute(
        text("UPDATE game_state SET state = :state, updated_at = now() WHERE game_id = :id"),
        {"state": json.dumps(state), "id": str(game_id)},
    )
    checkpoint = await session.execute(
        text(
            """
            INSERT INTO checkpoints (game_id, transcript_entry_id, status, state_snapshot)
            VALUES (:game_id, :transcript_entry_id, :status, :snapshot)
            RETURNING id, created_at
            """
        ),
        {
            "game_id": str(game_id),
            "transcript_entry_id": str(checkpoint_transcript_id) if checkpoint_transcript_id else None,
            "status": status,
            "snapshot": json.dumps(state),
        },
    )
    cp_row = checkpoint.mappings().first()
    if cp_row:
        state.setdefault("checkpoints", [])
        state["checkpoints"].append(
            {
                "checkpoint_id": str(cp_row["id"]),
                "created_at": cp_row["created_at"].replace(tzinfo=datetime.timezone.utc).isoformat()
                if hasattr(cp_row["created_at"], "isoformat")
                else str(cp_row["created_at"]),
                "status": status,
                "transcript_upto": None if checkpoint_transcript_id is None else str(checkpoint_transcript_id),
            }
        )


async def insert_transcript_entry(
    session: AsyncSession,
    game_id: uuid.UUID,
    role_id: str,
    phase: str,
    content: str,
    visible_to_human: bool = True,
    round_number: Optional[int] = None,
    issue_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    metadata_json = json.dumps(metadata) if metadata else None
    result = await session.execute(
        text(
            """
            INSERT INTO transcript_entries
            (game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata)
            VALUES (:game_id, :role_id, :phase, :round, :issue_id, :visible_to_human, :content, :metadata)
            RETURNING id
            """
        ),
        {
            "game_id": str(game_id),
            "role_id": role_id,
            "phase": phase,
            "round": round_number,
            "issue_id": issue_id,
            "visible_to_human": visible_to_human,
            "content": content,
            "metadata": metadata_json,
        },
    )
    return uuid.UUID(str(result.scalar_one()))


async def fetch_japan_script(session: AsyncSession, script_key: str) -> Optional[str]:
    row = (
        await session.execute(
            text("SELECT template FROM japan_scripts WHERE script_key = :key LIMIT 1"), {"key": script_key}
        )
    ).scalar_one_or_none()
    return row


def render_script(template: Optional[str], **kwargs: Any) -> str:
    if not template:
        return ""
    try:
        return template.format(**kwargs)
    except Exception:
        return template


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/games", response_model=GameResponse)
async def create_game(req: CreateGameRequest, session: AsyncSession = Depends(get_session)):
    seed = random.getrandbits(63)
    async with session.begin():
        user_id = await get_or_create_user(session, req.user_id)
        inserted = await session.execute(
            text(
                """
                INSERT INTO games (user_id, human_role_id, status, seed)
                VALUES (:user_id, NULL, :status, :seed)
                RETURNING id
                """
            ),
            {"user_id": str(user_id), "status": "ROLE_SELECTION", "seed": seed},
        )
        game_id = uuid.UUID(str(inserted.scalar_one()))
        state = initial_state()
        now_iso = utc_iso()
        state["game_id"] = str(game_id)
        state["created_at"] = now_iso
        state["updated_at"] = now_iso
        ensure_default_stances(state)
        await session.execute(
            text("INSERT INTO game_state (game_id, state) VALUES (:id, :state)"),
            {"id": str(game_id), "state": json.dumps(state)},
        )
        await session.execute(
            text(
                """
                INSERT INTO checkpoints (game_id, transcript_entry_id, status, state_snapshot)
                VALUES (:game_id, NULL, :status, :snapshot)
                """
            ),
            {"game_id": str(game_id), "status": "ROLE_SELECTION", "snapshot": json.dumps(state)},
        )
    return {"game_id": game_id, "state": state}


@app.post("/games/{game_id}/advance", response_model=GameResponse)
async def advance_game(game_id: uuid.UUID, req: AdvanceRequest, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        game = await fetch_game_with_state(session, game_id)
        state = game["state"]
        current_status = game["status"]
        event = req.event

        if event == "ROLE_CONFIRMED":
            if current_status != "ROLE_SELECTION":
                raise HTTPException(status_code=400, detail="ROLE_CONFIRMED only allowed from ROLE_SELECTION")
            human_role_id = req.payload.get("human_role_id")
            if human_role_id is None or human_role_id == CHAIR:
                raise HTTPException(status_code=400, detail="Invalid human_role_id")
            if human_role_id not in state.get("roles", {}):
                raise HTTPException(status_code=400, detail="Unknown role")
            await session.execute(
                text("UPDATE games SET human_role_id = :rid WHERE id = :gid"),
                {"rid": human_role_id, "gid": str(game_id)},
            )
            state["human_role_id"] = human_role_id
            ensure_default_stances(state)
            await persist_state(session, game_id, "ROUND_1_SETUP", state)
            return {"game_id": game_id, "state": state}

        if event == "ROUND_1_READY":
            if current_status != "ROUND_1_SETUP":
                raise HTTPException(status_code=400, detail="ROUND_1_READY only allowed from ROUND_1_SETUP")
            seed = game["seed"]
            human_role_id = state.get("human_role_id")
            if not human_role_id:
                raise HTTPException(status_code=400, detail="Human role not set")

            speaker_order = speaker_order_with_constraint(seed, human_role_id)
            state.setdefault("round1", {})
            state["round1"]["speaker_order"] = speaker_order
            state["round1"]["cursor"] = 0

            variants_rows = await session.execute(
                text(
                    """
                    SELECT id, role_id, opening_text, initial_stances
                    FROM opening_variants
                    ORDER BY role_id ASC, id ASC
                    """
                )
            )
            openings_by_role: Dict[str, List[Dict[str, Any]]] = {}
            for row in variants_rows.mappings():
                openings_by_role.setdefault(row["role_id"], []).append(
                    {
                        "id": str(row["id"]),
                        "role_id": row["role_id"],
                        "opening_text": row["opening_text"],
                        "initial_stances": row.get("initial_stances"),
                    }
                )

            openings: Dict[str, Dict[str, Any]] = {}
            for role_id in state.get("roles", {}):
                if role_id == CHAIR:
                    continue
                chosen = pick_opening_variant(role_id, seed, openings_by_role.get(role_id, []))
                openings[role_id] = {"variant_id": chosen["id"], "text": chosen["opening_text"]}
            state["round1"]["openings"] = openings

            japan_open_template = await fetch_japan_script(session, "R1_OPEN")
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=render_script(japan_open_template),
                visible_to_human=True,
            )

            await persist_state(session, game_id, "ROUND_1_OPENING_STATEMENTS", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "ROUND_1_STEP":
            if current_status != "ROUND_1_OPENING_STATEMENTS":
                raise HTTPException(status_code=400, detail="ROUND_1_STEP only allowed during opening statements")
            round1 = state.get("round1", {})
            cursor = int(round1.get("cursor", 0))
            order = round1.get("speaker_order") or []
            if cursor >= len(order):
                raise HTTPException(status_code=400, detail="Round 1 already completed")

            speaker_id = order[cursor]
            openings = round1.get("openings", {})
            opening = openings.get(speaker_id)
            if not opening:
                raise HTTPException(status_code=400, detail=f"No opening text for {speaker_id}")

            japan_intro_template = await fetch_japan_script(session, "R1_CALL_SPEAKER")
            intro_text = render_script(japan_intro_template, speaker=speaker_id)
            japan_transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=intro_text,
                visible_to_human=True,
                metadata={"cursor": cursor},
            )
            speaker_transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=speaker_id,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=opening["text"],
                visible_to_human=True,
                metadata={"cursor": cursor},
            )

            round1["cursor"] = cursor + 1
            next_status = "ROUND_1_OPENING_STATEMENTS"
            if round1["cursor"] >= len(order):
                next_status = "ROUND_2_SETUP"
            state["round1"] = round1
            await persist_state(session, game_id, next_status, state, speaker_transcript_id)
            return {"game_id": game_id, "state": state}

        raise HTTPException(status_code=400, detail="Unsupported event")
