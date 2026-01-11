import datetime
import json
import random
import uuid
import hashlib
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .ai import FakeLLM, AIResponder
from .db import get_session
from .state import (
    COUNTRIES,
    VOTE_ORDER,
    ISSUES,
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


class ReviewResponse(BaseModel):
    game_id: uuid.UUID
    transcript: List[Dict[str, Any]]
    votes: List[Dict[str, Any]]


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
    # Ensure deterministic vote ordering before persisting
    if isinstance(state, dict):
        ai = state.get("round3", {}).get("active_issue") if isinstance(state.get("round3"), dict) else None
        if isinstance(ai, dict):
            _canonicalize_votes(ai)
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


async def persist_state_no_checkpoint(session: AsyncSession, game_id: uuid.UUID, status: str, state: Dict[str, Any]) -> None:
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


def _proposal_support(state: Dict[str, Any], issue_id: str, options: List[Dict[str, Any]]) -> Dict[str, float]:
    stances = state.get("stances", {})
    totals: Dict[str, float] = {}
    for opt in options:
        oid = opt.get("option_id")
        if not isinstance(oid, str) or not oid:
            continue
        total = 0.0
        for country in COUNTRIES:
            role_stance = stances.get(country, {}).get(issue_id, {})
            acc = role_stance.get("acceptance", {}).get(oid)
            if acc is None:
                acc = 0.0
            total += float(acc)
        totals[oid] = total
    return totals


def _canonicalize_votes(ai: Dict[str, Any]) -> None:
    votes = ai.get("votes")
    if isinstance(votes, dict):
        ai["votes"] = {role: votes[role] for role in VOTE_ORDER if role in votes}


async def _ensure_resolution_transcript(
    session: AsyncSession, game_id: uuid.UUID, state: Dict[str, Any], ai: Dict[str, Any], issue_id: str
) -> Optional[uuid.UUID]:
    # Idempotent: write only once
    if ai.get("resolution_written"):
        return None
    votes = ai.get("votes", {})
    passed = len(votes) == len(COUNTRIES) and all(v == "YES" for v in votes.values())
    res_template = await fetch_japan_script(session, "VOTE_RESULT_PASS" if passed else "VOTE_RESULT_FAIL")
    res_text = render_script(res_template)
    res_tid = await insert_transcript_entry(
        session,
        game_id,
        role_id=CHAIR,
        phase="ISSUE_VOTE",
        content=res_text,
        visible_to_human=True,
        round_number=3,
        metadata={"issue_id": issue_id, "passed": passed},
    )
    ai["resolution"] = {"passed": passed, "final_votes": votes}
    ai["resolution_written"] = True
    state["round3"].setdefault("closed_issues", [])
    if issue_id not in state["round3"]["closed_issues"]:
        state["round3"]["closed_issues"].append(issue_id)
    state["round3"]["active_issue"] = ai
    _canonicalize_votes(ai)
    return res_tid


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


def get_ai_responder() -> AIResponder:
    responder = getattr(app.state, "ai_responder", None)
    if responder:
        return responder
    if not hasattr(app.state, "_default_ai_responder"):
        app.state._default_ai_responder = FakeLLM()
    return app.state._default_ai_responder


def _stable_int(seed: int, salt: str) -> int:
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(digest, 16) % (2**63)


def _human_placement(queue: List[str], human_role_id: Optional[str], choice: str, seed: int, salt: str) -> List[str]:
    if not human_role_id or human_role_id not in queue:
        return queue
    if human_role_id == CHAIR:
        return [r for r in queue if r != human_role_id]
    if choice == "skip":
        return [r for r in queue if r != human_role_id]
    if choice == "first":
        others = [r for r in queue if r != human_role_id]
        return [human_role_id] + others
    # deterministic random placement
    others = [r for r in queue if r != human_role_id]
    if not others:
        return [human_role_id]
    idx = _stable_int(seed, salt) % (len(others) + 1)
    return others[:idx] + [human_role_id] + others[idx:]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/games/{game_id}")
async def get_game(game_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        text(
            """
            SELECT g.id, g.user_id, g.human_role_id, g.status, g.seed, g.created_at, g.updated_at, gs.state
            FROM games g
            JOIN game_state gs ON gs.game_id = g.id
            WHERE g.id = :id
            """
        ),
        {"id": str(game_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Game not found")
    state = row["state"] if isinstance(row["state"], dict) else json.loads(row["state"])
    if state is None:
        raise HTTPException(status_code=404, detail="Game state not found")

    def _iso(val: Any) -> Optional[str]:
        if val is None:
            return None
        return val.replace(tzinfo=datetime.timezone.utc).isoformat() if hasattr(val, "isoformat") else str(val)

    game_obj = {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]) if row["user_id"] else None,
        "human_role_id": row["human_role_id"],
        "status": row["status"],
        "seed": int(row["seed"]),
        "created_at": _iso(row["created_at"]),
        "updated_at": _iso(row["updated_at"]),
    }
    return {"game": game_obj, "state": state}


@app.get("/games/{game_id}/transcript")
async def get_transcript(
    game_id: uuid.UUID, visible_to_human: Optional[bool] = None, session: AsyncSession = Depends(get_session)
):
    # Verify game exists
    exists = await session.execute(text("SELECT 1 FROM games WHERE id = :id LIMIT 1"), {"id": str(game_id)})
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Game not found")

    where_clause = "WHERE game_id = :game_id"
    params: Dict[str, Any] = {"game_id": str(game_id)}
    if visible_to_human is not None:
        where_clause += " AND visible_to_human = :visible"
        params["visible"] = visible_to_human

    result = await session.execute(
        text(
            f"""
            SELECT id, game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata, created_at
            FROM transcript_entries
            {where_clause}
            ORDER BY created_at ASC, COALESCE((metadata->>'index')::int, 0) ASC, id ASC
            """
        ),
        params,
    )
    entries = []
    for row in result.mappings():
        created_at = row["created_at"]
        created_at_str = created_at.replace(tzinfo=datetime.timezone.utc).isoformat() if hasattr(created_at, "isoformat") else str(created_at)
        entries.append(
            {
                "id": str(row["id"]),
                "game_id": str(row["game_id"]),
                "role_id": row["role_id"],
                "phase": row["phase"],
                "round": row["round"],
                "issue_id": row["issue_id"],
                "visible_to_human": row["visible_to_human"],
                "content": row["content"],
                "metadata": row["metadata"],
                "created_at": created_at_str,
            }
    )
    return entries


@app.get("/games/{game_id}/review", response_model=ReviewResponse)
async def get_review(game_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    # Transcript: include all except round2 hidden; require ordering by created_at then id
    result = await session.execute(
        text(
            """
            SELECT id, game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata, created_at
            FROM transcript_entries
            WHERE game_id = :gid
              AND (
                (round = 2 AND visible_to_human = true) OR (round != 2 OR round IS NULL)
              )
            ORDER BY created_at ASC, COALESCE((metadata->>'index')::int, 0) ASC, id ASC
            """
        ),
        {"gid": str(game_id)},
    )
    transcript = []
    for row in result.mappings():
        created_at = row["created_at"]
        created_at_str = created_at.replace(tzinfo=datetime.timezone.utc).isoformat() if hasattr(created_at, "isoformat") else str(created_at)
        transcript.append(
            {
                "id": str(row["id"]),
                "game_id": str(row["game_id"]),
                "role_id": row["role_id"],
                "phase": row["phase"],
                "round": row["round"],
                "issue_id": row["issue_id"],
                "visible_to_human": row["visible_to_human"],
                "content": row["content"],
                "metadata": row["metadata"],
                "created_at": created_at_str,
            }
        )

    votes_rows = await session.execute(
        text(
            """
            SELECT id, issue_id, proposal_option_id, votes_by_country, passed, created_at
            FROM votes
            WHERE game_id = :gid
            ORDER BY created_at ASC, id ASC
            """
        ),
        {"gid": str(game_id)},
    )
    votes_list = []
    for row in votes_rows.mappings():
        c_at = row["created_at"]
        votes_list.append(
            {
                "id": str(row["id"]),
                "issue_id": row["issue_id"],
                "proposal_option_id": row["proposal_option_id"],
                "votes_by_country": row["votes_by_country"],
                "passed": row["passed"],
                "created_at": c_at.replace(tzinfo=datetime.timezone.utc).isoformat() if hasattr(c_at, "isoformat") else str(c_at),
            }
        )

    return {"game_id": game_id, "transcript": transcript, "votes": votes_list}


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
            for role_id in sorted(state.get("roles", {})):
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
                # Already complete; ensure state reflects transition.
                await persist_state(session, game_id, "ROUND_2_SETUP", state)
                return {"game_id": game_id, "state": state}

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
                metadata={"cursor": cursor, "index": cursor * 2},
            )
            speaker_transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=speaker_id,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=opening["text"],
                visible_to_human=True,
                metadata={"cursor": cursor, "index": cursor * 2 + 1},
            )

            round1["cursor"] = cursor + 1
            next_status = "ROUND_1_OPENING_STATEMENTS"
            if round1["cursor"] >= len(order):
                next_status = "ROUND_2_SETUP"
            state["round1"] = round1
            await persist_state(session, game_id, next_status, state, speaker_transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "HUMAN_OPENING_STATEMENT":
            if current_status != "ROUND_1_OPENING_STATEMENTS":
                raise HTTPException(status_code=400, detail="HUMAN_OPENING_STATEMENT only allowed during opening statements")
            text_payload = req.payload.get("text") if isinstance(req.payload, dict) else None
            if not text_payload or not str(text_payload).strip():
                raise HTTPException(status_code=400, detail="text required")
            round1 = state.get("round1", {})
            cursor = int(round1.get("cursor", 0))
            order = round1.get("speaker_order") or []
            if cursor >= len(order):
                raise HTTPException(status_code=400, detail="No pending speaker")
            speaker_id = order[cursor]
            if speaker_id != state.get("human_role_id"):
                raise HTTPException(status_code=400, detail="Not human turn")

            japan_intro_template = await fetch_japan_script(session, "R1_CALL_SPEAKER")
            intro_text = render_script(japan_intro_template, speaker=speaker_id)
            japan_transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=intro_text,
                visible_to_human=True,
                metadata={"cursor": cursor, "index": cursor * 2},
            )
            speaker_transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=speaker_id,
                phase="ROUND_1_OPENING_STATEMENTS",
                content=str(text_payload).strip(),
                visible_to_human=True,
                metadata={"cursor": cursor, "index": cursor * 2 + 1},
            )

            round1["cursor"] = cursor + 1
            next_status = "ROUND_1_OPENING_STATEMENTS"
            if round1["cursor"] >= len(order):
                next_status = "ROUND_2_SETUP"
            state["round1"] = round1
            await persist_state(session, game_id, next_status, state, speaker_transcript_id or japan_transcript_id)
            return {"game_id": game_id, "state": state}

        # ---- Round 2 setup, partner selection, conversations, wrap-up ----
        if event == "ROUND_2_READY":
            if current_status != "ROUND_2_SETUP":
                raise HTTPException(status_code=400, detail="ROUND_2_READY only allowed from ROUND_2_SETUP")
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_2",
                content="Entering private negotiations (Round 2 setup).",
                visible_to_human=True,
                round_number=2,
            )
            state.setdefault("round2", {})
            state["round2"]["active_convo_index"] = None
            await persist_state(session, game_id, "ROUND_2_SELECT_CONVO_1", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "CONVO_1_SELECTED":
            if current_status != "ROUND_2_SELECT_CONVO_1":
                raise HTTPException(status_code=400, detail="CONVO_1_SELECTED only allowed from ROUND_2_SELECT_CONVO_1")
            partner = req.payload.get("partner_role_id")
            if not partner:
                raise HTTPException(status_code=400, detail="partner_role_id required")
            if partner == state.get("human_role_id") or partner == CHAIR:
                raise HTTPException(status_code=400, detail="Invalid partner_role_id")
            if partner not in state.get("roles", {}):
                raise HTTPException(status_code=400, detail="Unknown partner_role_id")

            state.setdefault("round2", {})
            state["round2"]["active_convo_index"] = 1
            state["round2"]["convo1"] = {
                "partner_role": partner,
                "status": "ACTIVE",
                "human_turns_used": 0,
                "ai_turns_used": 0,
                "phase": "OPEN",
            }

            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_2",
                content=f"Private negotiation started with {partner}.",
                visible_to_human=True,
                round_number=2,
                metadata={"partner": partner},
            )
            await persist_state(session, game_id, "ROUND_2_CONVERSATION_ACTIVE", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event in ("CONVO_1_MESSAGE", "CONVO_2_MESSAGE", "CONVO_MESSAGE"):
            if current_status != "ROUND_2_CONVERSATION_ACTIVE":
                raise HTTPException(status_code=400, detail="CONVO_MESSAGE only allowed in ROUND_2_CONVERSATION_ACTIVE")
            # Tests and UI send message text as "content"; accept "text" as a tolerant fallback.
            content = req.payload.get("content") or req.payload.get("text")
            if not content:
                raise HTTPException(status_code=400, detail="content required")
            round2 = state.setdefault("round2", {})
            active_idx = round2.get("active_convo_index") or 1
            convo_key = f"convo{active_idx}"
            convo = round2.get(convo_key)
            if not convo or convo.get("status") == "CLOSED":
                raise HTTPException(status_code=400, detail="Conversation is closed")
            human_role_id = state.get("human_role_id")
            partner = convo.get("partner_role")
            if not human_role_id or not partner:
                raise HTTPException(status_code=400, detail="Conversation not initialized")

            post_interrupt = bool(convo.get("post_interrupt"))
            final_human = bool(convo.get("final_human_sent"))
            final_ai = bool(convo.get("final_ai_sent"))
            human_turns = int(convo.get("human_turns_used", 0))
            ai_turns = int(convo.get("ai_turns_used", 0))

            if post_interrupt:
                if final_human:
                    raise HTTPException(status_code=400, detail="No human turns remaining")
            else:
                if human_turns >= 5:
                    raise HTTPException(status_code=400, detail="No human turns remaining")

            human_tid = await insert_transcript_entry(
                session,
                game_id,
                role_id=human_role_id,
                phase="ROUND_2",
                content=content,
                visible_to_human=True,
                round_number=2,
                metadata={"partner": partner, "sender": "human", "index": human_turns * 2, "convo": convo_key},
            )
            convo["human_turns_used"] = human_turns + 1
            if post_interrupt:
                convo["final_human_sent"] = True
            await persist_state(session, game_id, "ROUND_2_CONVERSATION_ACTIVE", state, human_tid)

            reply = await get_ai_responder().respond(content)
            ai_tid = await insert_transcript_entry(
                session,
                game_id,
                role_id=partner,
                phase="ROUND_2",
                content=reply,
                visible_to_human=True,
                round_number=2,
                metadata={"partner": human_role_id, "sender": "ai", "index": ai_turns * 2 + 1, "convo": convo_key},
            )
            convo["ai_turns_used"] = ai_turns + 1
            if post_interrupt:
                convo["final_ai_sent"] = True

            next_status = "ROUND_2_CONVERSATION_ACTIVE"
            interrupt_tid = None
            if not post_interrupt and convo["human_turns_used"] >= 5 and convo["ai_turns_used"] >= 5:
                interrupt_tid = await insert_transcript_entry(
                    session,
                    game_id,
                    role_id=CHAIR,
                    phase="ROUND_2",
                    content="The Chair interrupts. Please move to final statements.",
                    visible_to_human=True,
                    round_number=2,
                    metadata={"interrupt": True, "convo": convo_key, "index": convo["human_turns_used"] + convo["ai_turns_used"]},
                )
                convo["post_interrupt"] = True
                convo["phase"] = "POST_INTERRUPT"

            if convo.get("post_interrupt") and convo.get("final_human_sent") and convo.get("final_ai_sent"):
                convo["status"] = "CLOSED"
                convo["phase"] = "CLOSED"
                round2["active_convo_index"] = None
                if active_idx == 1:
                    next_status = "ROUND_2_SELECT_CONVO_2"
                else:
                    next_status = "ROUND_2_WRAP_UP"

            await persist_state(session, game_id, next_status, state, ai_tid)

            if interrupt_tid:
                await persist_state(session, game_id, "ROUND_2_CONVERSATION_ACTIVE", state, interrupt_tid)

            if next_status == "ROUND_2_WRAP_UP" and convo.get("status") == "CLOSED" and convo.get("final_ai_sent"):
                wrap_tid = await insert_transcript_entry(
                    session,
                    game_id,
                    role_id=CHAIR,
                    phase="ROUND_2",
                    content="Private negotiations concluded. Preparing to move to Round 3.",
                    visible_to_human=True,
                    round_number=2,
                    metadata={
                        "convo": convo_key,
                        "index": convo.get("human_turns_used", 0) + convo.get("ai_turns_used", 0) + 1,
                        "concluded": True,
                    },
                )
                # ensure concluded message is last: write it after final exchange, then persist status
                await persist_state(session, game_id, "ROUND_2_WRAP_UP", state, wrap_tid)

            return {"game_id": game_id, "state": state}

        if event == "CONVO_END_EARLY":
            if current_status != "ROUND_2_CONVERSATION_ACTIVE":
                raise HTTPException(status_code=400, detail="CONVO_END_EARLY only allowed in ROUND_2_CONVERSATION_ACTIVE")
            round2 = state.setdefault("round2", {})
            active_idx = round2.get("active_convo_index") or 1
            convo_key = f"convo{active_idx}"
            convo = round2.get(convo_key)
            if not convo or convo.get("status") == "CLOSED":
                raise HTTPException(status_code=400, detail="Conversation is closed")
            human_role_id = state.get("human_role_id")
            partner = convo.get("partner_role")
            if not human_role_id or not partner:
                raise HTTPException(status_code=400, detail="Conversation not initialized")

            # Only allow on human turn: before the AI reply is sent for a message
            post_interrupt = bool(convo.get("post_interrupt"))
            final_human = bool(convo.get("final_human_sent"))
            final_ai = bool(convo.get("final_ai_sent"))
            human_turns = int(convo.get("human_turns_used", 0))
            ai_turns = int(convo.get("ai_turns_used", 0))
            if post_interrupt and final_human:
                raise HTTPException(status_code=400, detail="No human turns remaining")
            if not post_interrupt and human_turns >= 5:
                raise HTTPException(status_code=400, detail="No human turns remaining")

            convo["status"] = "CLOSED"
            convo["phase"] = "CLOSED"
            round2["active_convo_index"] = None
            next_status = "ROUND_2_SELECT_CONVO_2" if active_idx == 1 else "ROUND_2_WRAP_UP"
            await persist_state(session, game_id, next_status, state)
            return {"game_id": game_id, "state": state}

        if event == "CONVO_2_SELECTED":
            if current_status != "ROUND_2_SELECT_CONVO_2":
                raise HTTPException(status_code=400, detail="CONVO_2_SELECTED only allowed from ROUND_2_SELECT_CONVO_2")
            partner = req.payload.get("partner_role_id")
            if not partner:
                raise HTTPException(status_code=400, detail="partner_role_id required")
            if partner == state.get("human_role_id") or partner == CHAIR:
                raise HTTPException(status_code=400, detail="Invalid partner_role_id")
            convo1_partner = state.get("round2", {}).get("convo1", {}).get("partner_role")
            if partner == convo1_partner:
                raise HTTPException(status_code=400, detail="partner_role_id already used")
            if partner not in state.get("roles", {}):
                raise HTTPException(status_code=400, detail="Unknown partner_role_id")

            state.setdefault("round2", {})
            state["round2"]["active_convo_index"] = 2
            state["round2"]["convo2"] = {
                "partner_role": partner,
                "status": "ACTIVE",
                "human_turns_used": 0,
                "ai_turns_used": 0,
                "phase": "OPEN",
            }

            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_2",
                content=f"Second private negotiation started with {partner}.",
                visible_to_human=True,
                round_number=2,
                metadata={"partner": partner},
            )
            await persist_state(session, game_id, "ROUND_2_CONVERSATION_ACTIVE", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "CONVO_2_SKIPPED":
            if current_status != "ROUND_2_SELECT_CONVO_2":
                raise HTTPException(status_code=400, detail="CONVO_2_SKIPPED only allowed from ROUND_2_SELECT_CONVO_2")
            state.setdefault("round2", {})
            state["round2"]["active_convo_index"] = None
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_2",
                content="Second private negotiation skipped.",
                visible_to_human=True,
                round_number=2,
            )
            await persist_state(session, game_id, "ROUND_2_WRAP_UP", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "ROUND_2_WRAP_READY":
            if current_status != "ROUND_2_WRAP_UP":
                raise HTTPException(status_code=400, detail="ROUND_2_WRAP_READY only allowed from ROUND_2_WRAP_UP")
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ROUND_2",
                content="Round 2 complete. Moving to Round 3 setup.",
                visible_to_human=True,
                round_number=2,
            )
            await persist_state(session, game_id, "ROUND_3_SETUP", state, transcript_id)
            return {"game_id": game_id, "state": state}

        # ---- Round 3 Issue 1 setup and intro ----
        if event == "ROUND_3_START_ISSUE":
            if current_status != "ROUND_3_SETUP":
                raise HTTPException(status_code=400, detail="ROUND_3_START_ISSUE only allowed from ROUND_3_SETUP")
            issue_id = req.payload.get("issue_id", "1")
            human_choice = req.payload.get("human_placement", "random")
            if human_choice not in ("first", "random", "skip"):
                raise HTTPException(status_code=400, detail="Invalid human_placement")

            issue_row = await session.execute(
                text("SELECT id, title, description, options FROM issue_definitions WHERE id = :id"),
                {"id": issue_id},
            )
            issue = issue_row.mappings().first()
            if not issue:
                raise HTTPException(status_code=404, detail="Issue not found")
            opts = issue["options"]
            if isinstance(opts, str):
                opts = json.loads(opts)
            opts_sorted = sorted(opts, key=lambda o: o.get("option_id"))

            countries = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "country"])
            ngos = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "ngo"])
            human_role = state.get("human_role_id")
            seed = game["seed"]
            countries = _human_placement(countries, human_role, human_choice, seed, f"{issue_id}-countries-1")
            ngos = _human_placement(ngos, human_role, human_choice, seed, f"{issue_id}-ngos-1")
            debate_queue = countries + ngos

            state.setdefault("round3", {})
            state["round3"]["active_issue"] = {
                "issue_id": issue_id,
                "issue_title": issue["title"],
                "ui_prompt": issue["description"],
                "options": opts_sorted,
                "human_placement_choice": human_choice,
                "round_index": 1,
                "debate_queue": debate_queue,
                "debate_cursor": 0,
            }
            state["round3"]["active_issue_index"] = 0

            issue_intro_template = await fetch_japan_script(session, "ISSUE_INTRO")
            options_list = "; ".join([f"{o.get('option_id')} {o.get('label')}" for o in opts_sorted])
            intro_text = render_script(
                issue_intro_template,
                issue_id=issue_id,
                issue_title=issue["title"],
                options_list=options_list,
            )
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ISSUE_INTRO",
                content=intro_text,
                visible_to_human=True,
                round_number=3,
                metadata={"issue_id": issue_id},
            )
            await persist_state(session, game_id, "ISSUE_INTRO", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if event == "ISSUE_INTRO_CONTINUE":
            if current_status != "ISSUE_INTRO":
                raise HTTPException(status_code=400, detail="ISSUE_INTRO_CONTINUE only allowed from ISSUE_INTRO")
            ai = state.get("round3", {}).get("active_issue") or {}
            ai["debate_round"] = 1
            ai["debate_cursor"] = 0
            state["round3"]["active_issue"] = ai
            # State-only transition: no transcript, so no checkpoint
            await persist_state_no_checkpoint(session, game_id, "ISSUE_DEBATE_ROUND_1", state)
            return {"game_id": game_id, "state": state}

        # ---- Issue debate rounds ----
        if current_status in ("ISSUE_DEBATE_ROUND_1", "ISSUE_DEBATE_ROUND_2"):
            ai = state.get("round3", {}).get("active_issue") or {}
            issue_id = ai.get("issue_id", "1")
            human_choice = ai.get("human_placement_choice", "random")
            debate_round = ai.get("debate_round", 1)
            cursor = int(ai.get("debate_cursor", 0))
            queue = ai.get("debate_queue", [])

            # If queue exhausted, advance to next round/state
            if cursor >= len(queue):
                if current_status == "ISSUE_DEBATE_ROUND_1":
                    # build round 2 queue
                    countries = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "country"])
                    ngos = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "ngo"])
                    human_role = state.get("human_role_id")
                    seed = game["seed"]
                    countries = _human_placement(countries, human_role, human_choice, seed, f"{issue_id}-countries-2")
                    ngos = _human_placement(ngos, human_role, human_choice, seed, f"{issue_id}-ngos-2")
                    ai["debate_queue"] = countries + ngos
                    ai["debate_cursor"] = 0
                    ai["debate_round"] = 2
                    state["round3"]["active_issue"] = ai
                    await persist_state_no_checkpoint(session, game_id, "ISSUE_DEBATE_ROUND_2", state)
                    return {"game_id": game_id, "state": state}
                else:
                    await persist_state_no_checkpoint(session, game_id, "ISSUE_POSITION_FINALIZATION", state)
                    return {"game_id": game_id, "state": state}

            speaker = queue[cursor]
            human_role = state.get("human_role_id")
            is_human = speaker == human_role

            if is_human:
                if event != "HUMAN_DEBATE_MESSAGE":
                    raise HTTPException(status_code=400, detail="Human debate turn requires HUMAN_DEBATE_MESSAGE")
                content = req.payload.get("text")
                if not content:
                    raise HTTPException(status_code=400, detail="text required")
                transcript_id = await insert_transcript_entry(
                    session,
                    game_id,
                    role_id=speaker,
                    phase=current_status,
                    content=content,
                    visible_to_human=True,
                    round_number=3,
                    metadata={"issue_id": issue_id, "round": debate_round, "speaker": speaker},
                )
                ai["debate_cursor"] = cursor + 1
                state["round3"]["active_issue"] = ai
                await persist_state(session, game_id, current_status, state, transcript_id)
                return {"game_id": game_id, "state": state}

            # AI speaker
            opts = ai.get("options", [])
            options_text = "; ".join([f"{o.get('option_id')} {o.get('label')}: {o.get('short_description')}" for o in opts])
            prompt = (
                f"Role: {speaker}\n"
                f"Issue: {ai.get('issue_title')} ({issue_id})\n"
                f"Prompt: {ai.get('ui_prompt')}\n"
                f"Options: {options_text}\n"
                f"Deliver a short debate statement (1-2 paragraphs) advocating a position and responding to prior discussion."
            )
            reply = await get_ai_responder().respond(prompt)
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=speaker,
                phase=current_status,
                content=reply,
                visible_to_human=True,
                round_number=3,
                metadata={"issue_id": issue_id, "round": debate_round, "speaker": speaker},
            )
            ai["debate_cursor"] = cursor + 1
            state["round3"]["active_issue"] = ai
            await persist_state(session, game_id, current_status, state, transcript_id)

            # After writing, check if we should transition on next call
            if ai["debate_cursor"] >= len(queue):
                if current_status == "ISSUE_DEBATE_ROUND_1":
                    countries = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "country"])
                    ngos = sorted([r for r in state.get("roles", {}) if state["roles"][r].get("type") == "ngo"])
                    human_role = state.get("human_role_id")
                    seed = game["seed"]
                    countries = _human_placement(countries, human_role, human_choice, seed, f"{issue_id}-countries-2")
                    ngos = _human_placement(ngos, human_role, human_choice, seed, f"{issue_id}-ngos-2")
                    ai["debate_queue"] = countries + ngos
                    ai["debate_cursor"] = 0
                    ai["debate_round"] = 2
                    state["round3"]["active_issue"] = ai
                    await persist_state_no_checkpoint(session, game_id, "ISSUE_DEBATE_ROUND_2", state)
                else:
                    await persist_state_no_checkpoint(session, game_id, "ISSUE_POSITION_FINALIZATION", state)

            return {"game_id": game_id, "state": state}

        if current_status == "ISSUE_POSITION_FINALIZATION":
            current_status = "ISSUE_PROPOSAL_SELECTION"

        if current_status == "ISSUE_PROPOSAL_SELECTION":
            ai = state.get("round3", {}).get("active_issue") or {}
            issue_id = ai.get("issue_id", "1")
            opts = ai.get("options", [])
            support = _proposal_support(state, issue_id, opts)
            if support:
                proposed_option = sorted(support.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            else:
                proposed_option = opts[0].get("option_id") if opts else None
            if not proposed_option:
                raise HTTPException(status_code=400, detail="No options available")
            ai["proposed_option_id"] = proposed_option
            ai["proposal_support_snapshot"] = support
            ai["vote_order"] = VOTE_ORDER.copy()
            ai["next_voter_index"] = 0
            ai["votes"] = {}
            state["round3"]["active_issue"] = ai

            proposal_template = await fetch_japan_script(session, "PROPOSAL")
            proposal_text = render_script(proposal_template, option_id=proposed_option)
            transcript_id = await insert_transcript_entry(
                session,
                game_id,
                role_id=CHAIR,
                phase="ISSUE_PROPOSAL_SELECTION",
                content=proposal_text,
                visible_to_human=True,
                round_number=3,
                metadata={"issue_id": issue_id, "proposed_option_id": proposed_option},
            )
            await persist_state(session, game_id, "ISSUE_VOTE", state, transcript_id)
            return {"game_id": game_id, "state": state}

        if current_status == "ISSUE_VOTE":
            ai = state.get("round3", {}).get("active_issue") or {}
            issue_id = ai.get("issue_id", "1")
            proposed_option = ai.get("proposed_option_id")
            vote_order = ai.get("vote_order", VOTE_ORDER)
            idx = int(ai.get("next_voter_index", 0))
            votes = ai.get("votes", {})

            if idx >= len(vote_order):
                await persist_state_no_checkpoint(session, game_id, "ISSUE_RESOLUTION", state)
                return {"game_id": game_id, "state": state}

            voter = vote_order[idx]
            human_role = state.get("human_role_id")
            if voter == human_role:
                if event != "HUMAN_VOTE":
                    raise HTTPException(status_code=400, detail="Human vote required")
                vote_val = req.payload.get("vote")
                if vote_val not in ("YES", "NO"):
                    raise HTTPException(status_code=400, detail="Invalid vote")
            else:
                stance = state.get("stances", {}).get(voter, {}).get(issue_id, {}).get("acceptance", {})
                acc = stance.get(proposed_option)
                if acc is None:
                    acc = 0.0
                vote_val = "YES" if acc >= 0.7 else "NO"

            votes[voter] = vote_val
            ai["votes"] = votes
            _canonicalize_votes(ai)
            ai["next_voter_index"] = idx + 1
            state["round3"]["active_issue"] = ai

            vote_text = f"{voter} votes {vote_val}."
            vote_tid = await insert_transcript_entry(
                session,
                game_id,
                role_id=voter,
                phase="ISSUE_VOTE",
                content=vote_text,
                visible_to_human=True,
                round_number=3,
                metadata={"issue_id": issue_id, "voter": voter, "vote": vote_val},
            )
            await persist_state(session, game_id, "ISSUE_VOTE", state, vote_tid)

            if ai["next_voter_index"] >= len(vote_order):
                # Persist final vote record to votes table
                await session.execute(
                    text(
                        """
                        INSERT INTO votes (game_id, issue_id, proposal_option_id, votes_by_country, passed)
                        VALUES (:game_id, :issue_id, :proposal_option_id, :votes_by_country, :passed)
                        """
                    ),
                    {
                        "game_id": str(game_id),
                        "issue_id": issue_id,
                        "proposal_option_id": proposed_option,
                        "votes_by_country": json.dumps(ai.get("votes", {})),
                        "passed": len(ai.get("votes", {})) == len(COUNTRIES) and all(v == "YES" for v in ai.get("votes", {}).values()),
                    },
                )
                await persist_state_no_checkpoint(session, game_id, "ISSUE_RESOLUTION", state)

            return {"game_id": game_id, "state": state}

        if current_status == "ISSUE_RESOLUTION":
            ai = state.get("round3", {}).get("active_issue") or {}
            issue_id = ai.get("issue_id", "1")

            async def ensure_resolution_written() -> Optional[uuid.UUID]:
                return await _ensure_resolution_transcript(session, game_id, state, ai, issue_id)

            if event == "ISSUE_DEBATE_STEP":
                res_tid = await ensure_resolution_written()
                state["round3"]["active_issue"] = ai
                await persist_state(session, game_id, "ISSUE_RESOLUTION", state, res_tid)
                return {"game_id": game_id, "state": state}

            if event == "ISSUE_RESOLUTION_CONTINUE":
                res_tid = await ensure_resolution_written()
                issues_list = state.get("round3", {}).get("issues", ISSUES)
                closed = state.get("round3", {}).get("closed_issues", [])
                closed_count = len(closed) if isinstance(closed, list) else 0
                total_issues = len(issues_list) if isinstance(issues_list, list) else len(ISSUES)
                all_closed = closed_count >= total_issues

                next_status = "REVIEW" if all_closed else "ROUND_3_SETUP"
                if not all_closed and isinstance(state.get("round3"), dict):
                    state["round3"]["active_issue"] = None
                state["status"] = next_status
                await persist_state(session, game_id, next_status, state, res_tid)
                return {"game_id": game_id, "state": state}

            # Unsupported event while in ISSUE_RESOLUTION
            raise HTTPException(status_code=400, detail="ISSUE_RESOLUTION_CONTINUE or ISSUE_DEBATE_STEP required")

        raise HTTPException(status_code=400, detail="Unsupported event")
