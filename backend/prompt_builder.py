from __future__ import annotations

import json
from pathlib import Path

from typing import Any, Dict, List, Optional


_ROUND2_BEHAVIOR_PATH = Path(__file__).resolve().parent / "prompts" / "round2_behavior_instructions_v1.txt"
_ROUND2_BEHAVIOR_TEMPLATE: Optional[str] = None


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
    human_role: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Centralized Round 2 prompt builder (deterministic).
    Keeps current FakeLLM behavior by using the human content as the prompt text.
    """
    prompt_version = "r2_convo_v3"
    context_payload = context or {}
    prompt_text = _render_round2_prompt(
        human_content=human_content,
        context=context_payload,
        role=role_id,
        human_role=human_role,
    )
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
        "context": context_payload,
    }
    return {
        "prompt_version": prompt_version,
        "prompt": prompt_text,
        "request_payload": request_payload,
    }


def build_round2_context(
    *,
    game_id: str,
    active_convo_index: Optional[int],
    active_convo: Dict[str, Any],
    partner_role: str,
    partner_opening: Optional[Dict[str, Any]],
    human_opening_text: Optional[str],
    transcript_tail: List[Dict[str, Any]],
    issues: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    normalized_partner_opening = dict(partner_opening or {})
    if normalized_partner_opening.get("initial_stances") is None:
        normalized_partner_opening["initial_stances"] = {}
    if normalized_partner_opening.get("conversation_interests") is None:
        normalized_partner_opening["conversation_interests"] = {}

    normalized_transcript_tail = transcript_tail or []
    normalized_human_opening = human_opening_text or ""
    normalized_issues: List[Dict[str, Any]] = []
    if issues:
        issue_limit = 4
        option_limit = 8
        for issue in issues[:issue_limit]:
            if not isinstance(issue, dict):
                continue
            options = issue.get("options") or []
            compact_options: List[Dict[str, Any]] = []
            if isinstance(options, list):
                for opt in options[:option_limit]:
                    if not isinstance(opt, dict):
                        continue
                    compact_options.append(
                        {"option_id": opt.get("option_id"), "label": opt.get("label")}
                    )
            normalized_issues.append(
                {
                    "issue_id": issue.get("issue_id"),
                    "title": issue.get("title"),
                    "options": compact_options,
                }
            )

    round2_snapshot = {
        "active_convo_index": active_convo_index,
        "active_convo": {
            "partner_role": active_convo.get("partner_role"),
            "status": active_convo.get("status"),
            "human_turns_used": active_convo.get("human_turns_used"),
            "ai_turns_used": active_convo.get("ai_turns_used"),
            "phase": active_convo.get("phase"),
            "post_interrupt": active_convo.get("post_interrupt"),
            "final_human_sent": active_convo.get("final_human_sent"),
            "final_ai_sent": active_convo.get("final_ai_sent"),
        },
    }
    openings = {
        "partner_role": partner_role,
        "partner_opening": normalized_partner_opening,
        "human_opening_text": normalized_human_opening,
    }
    context: Dict[str, Any] = {
        "game_id": game_id,
        "round2": round2_snapshot,
        "openings": openings,
        "transcript_tail": normalized_transcript_tail,
        "issues": normalized_issues,
    }
    return context


def _render_round2_prompt(
    *,
    human_content: str,
    context: Dict[str, Any],
    role: str,
    human_role: str,
) -> str:
    instructions = _load_round2_behavior_instructions(role=role, human_role=human_role)
    transcript_tail = context.get("transcript_tail") or []
    compact_transcript = [
        {"role_id": entry.get("role_id"), "content": entry.get("content")}
        for entry in transcript_tail
        if isinstance(entry, dict)
    ]
    openings = context.get("openings") or {}
    issues = context.get("issues")
    compact_issues = None
    if isinstance(issues, list):
        compact_issues = []
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            options = issue.get("options") or []
            compact_options = []
            if isinstance(options, list):
                for opt in options:
                    if not isinstance(opt, dict):
                        continue
                    compact_options.append(
                        {"option_id": opt.get("option_id"), "label": opt.get("label")}
                    )
            compact_issues.append(
                {
                    "issue_id": issue.get("issue_id"),
                    "title": issue.get("title"),
                    "options": compact_options,
                }
            )
    context_block = {
        "openings": openings,
        "transcript_tail": compact_transcript,
    }
    if compact_issues is not None:
        context_block["issues"] = compact_issues
    context_json = json.dumps(context_block, sort_keys=True, separators=(",", ":"))
    return f"{instructions}\n\nContext:\n{context_json}\n\nHuman message:\n{human_content}"


def _load_round2_behavior_instructions(*, role: str, human_role: str) -> str:
    global _ROUND2_BEHAVIOR_TEMPLATE
    if _ROUND2_BEHAVIOR_TEMPLATE is None:
        if not _ROUND2_BEHAVIOR_PATH.exists():
            raise RuntimeError(f"Round 2 instructions file not found: {_ROUND2_BEHAVIOR_PATH}")
        _ROUND2_BEHAVIOR_TEMPLATE = _ROUND2_BEHAVIOR_PATH.read_text(encoding="utf-8")
    return (
        _ROUND2_BEHAVIOR_TEMPLATE.replace("{ROLE}", role)
        .replace("{HUMAN_ROLE}", human_role)
        .strip()
    )


__all__ = ["build_round2_conversation_prompt", "build_round2_context"]
