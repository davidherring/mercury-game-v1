from __future__ import annotations

import json
from pathlib import Path

from typing import Any, Dict, List, Optional


_ROUND2_BEHAVIOR_PATH = Path(__file__).resolve().parent / "prompts" / "round2_behavior_instructions_v1.txt"
_ROUND2_BEHAVIOR_TEMPLATE: Optional[str] = None
_ROUND3_DEBATE_SPEECH_INSTRUCTIONS_PATH = (
    Path(__file__).resolve().parent / "prompts" / "round3_debate_speech_instructions_v1.txt"
)
_ROUND3_DEBATE_SPEECH_INSTRUCTIONS_TEMPLATE: Optional[str] = None
ROUND3_PUBLIC_DEBATE_TAIL_LIMIT = 8
ROUND3_DEBATE_SNIPPET_LEN = 240


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


def build_round3_debate_speech_prompt_v1(
    *,
    state: Dict[str, Any],
    active_issue: Dict[str, Any],
    speaker_role: str,
    debate_round: int,
    speech_number: int = 1,
    public_debate_tail: List[Dict[str, Any]],
) -> Dict[str, Any]:
    issue_id = active_issue.get("issue_id")
    issue_title = active_issue.get("issue_title")
    options = active_issue.get("options") or []
    options_payload: List[Dict[str, Any]] = []
    if isinstance(options, list):
        for opt in options:
            if not isinstance(opt, dict):
                continue
            options_payload.append(
                {
                    "id": opt.get("option_id"),
                    "label": opt.get("label"),
                    "short_text": opt.get("short_description") or opt.get("label"),
                }
            )

    roles = state.get("roles", {})
    role_info = roles.get(speaker_role, {}) if isinstance(roles, dict) else {}
    role_name = role_info.get("display_name") or speaker_role
    opening_text = state.get("round1", {}).get("openings", {}).get(speaker_role, {}).get("text") or ""
    opening_summary = _summarize_public_opening(opening_text)
    stance_snapshot = _extract_public_stance_snapshot(state, speaker_role, issue_id)

    tail = public_debate_tail[-ROUND3_PUBLIC_DEBATE_TAIL_LIMIT:]
    tail_payload: List[Dict[str, Any]] = []
    for entry in tail:
        if not isinstance(entry, dict):
            continue
        entry_role = entry.get("role_id")
        entry_role_name = roles.get(entry_role, {}).get("display_name") if isinstance(roles, dict) else None
        if not entry_role_name:
            entry_role_name = entry_role
        content = entry.get("content") or ""
        snippet = content[:ROUND3_DEBATE_SNIPPET_LEN]
        tail_payload.append(
            {"role_id": entry_role, "role_name": entry_role_name, "text_snippet": snippet}
        )

    context_payload: Dict[str, Any] = {
        "active_issue": {"id": issue_id, "title": issue_title, "options": options_payload},
        "speech_slot": {"speech_number": speech_number, "debate_round": debate_round},
        "speaker": {"role_id": speaker_role, "role_name": role_name, "is_human": False},
        "speaker_opening_summary": opening_summary,
        "speaker_issue_stance_snapshot": stance_snapshot,
        "debate_transcript_tail": tail_payload,
    }

    prompt_version = "r3_debate_speech_v1"
    request_payload: Dict[str, Any] = {
        "prompt_version": prompt_version,
        "speech_number": speech_number,
        "round_number": 3,
        "issue_id": issue_id,
        "issue_title": issue_title,
        "options": options_payload,
        "speaker_role": speaker_role,
        "speaker_role_name": role_name,
        "speaker_opening_summary": opening_summary,
        "speaker_issue_stance_snapshot": stance_snapshot,
        "debate_transcript_tail": tail_payload,
        "debate_round": debate_round,
        "context": context_payload,
    }

    instructions = _load_round3_debate_speech_instructions()
    context_json = json.dumps(context_payload, sort_keys=True, separators=(",", ":"))
    prompt_text = f"{instructions}\n\nContext:\n{context_json}\n\nSpeech:\n"

    return {"prompt_text": prompt_text, "request_payload": request_payload}


def _load_round3_debate_speech_instructions() -> str:
    global _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_TEMPLATE
    if _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_TEMPLATE is None:
        if not _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_PATH.exists():
            raise RuntimeError(
                f"Round 3 debate instructions file not found: {_ROUND3_DEBATE_SPEECH_INSTRUCTIONS_PATH}"
            )
        _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_TEMPLATE = (
            _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_PATH.read_text(encoding="utf-8")
        )
    return _ROUND3_DEBATE_SPEECH_INSTRUCTIONS_TEMPLATE.strip()


def _summarize_public_opening(opening_text: str) -> str:
    if not opening_text:
        return ""
    first_sentence = opening_text.split(".", 1)[0].strip()
    if first_sentence:
        return f"{first_sentence}."
    return opening_text[:ROUND3_DEBATE_SNIPPET_LEN]


def _extract_public_stance_snapshot(
    state: Dict[str, Any], role_id: str, issue_id: Optional[str]
) -> Dict[str, Any]:
    if not issue_id:
        return {}
    stances = state.get("stances", {}).get(role_id, {}).get(issue_id, {})
    if not isinstance(stances, dict):
        return {}
    snapshot: Dict[str, Any] = {}
    for key in ("preferred", "firmness", "acceptance", "conditions"):
        if key in stances:
            snapshot[key] = stances.get(key)
    return snapshot


__all__ = [
    "build_round2_conversation_prompt",
    "build_round2_context",
    "build_round3_debate_speech_prompt_v1",
]
