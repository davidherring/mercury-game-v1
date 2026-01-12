from __future__ import annotations

from typing import Any, Dict


def build_round2_conversation_prompt(
    *,
    game_id: str,
    role_id: str,
    status: str,
    human_content: str,
    partner_role: str,
    convo_key: str,
    human_turns: int,
    ai_turns: int,
) -> Dict[str, Any]:
    """
    Centralized Round 2 prompt builder (deterministic).
    Keeps current FakeLLM behavior by using the human content as the prompt text.
    """
    prompt_version = "r2_convo_v1"
    prompt_text = human_content
    request_payload: Dict[str, Any] = {
        "game_id": game_id,
        "role_id": role_id,
        "status": status,
        "partner_role": partner_role,
        "convo": convo_key,
        "human_turns": human_turns,
        "ai_turns": ai_turns,
        "prompt": prompt_text,
        "prompt_version": prompt_version,
    }
    return {
        "prompt_version": prompt_version,
        "prompt": prompt_text,
        "request_payload": request_payload,
    }


__all__ = ["build_round2_conversation_prompt"]
