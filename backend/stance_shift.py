from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple


MAX_ACCEPTANCE_DELTA = 0.10
MAX_FIRMNESS_DELTA = 0.05
ACCEPTANCE_DELTA_ON_MENTION = 0.05
FIRMNESS_DELTA_ON_ISSUE_MENTION = 0.02
TRIGGER_SNIPPET_LEN = 80


def apply_stance_shift(
    *,
    role_id: str,
    round_id: int,
    issue_id: Optional[str],
    trigger_text: str,
    stance_snapshot: Dict[str, Any],
    issue_option_spec: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    updated = copy.deepcopy(stance_snapshot)
    reasons: List[Dict[str, Any]] = []
    trigger = trigger_text or ""
    trigger_snippet = trigger[:TRIGGER_SNIPPET_LEN]

    if _is_role_indexed(updated, role_id):
        role_stances = updated.get(role_id, {})
    else:
        role_stances = updated

    matched_issue_ids = _matched_issue_ids(issue_id, trigger, issue_option_spec)
    if not matched_issue_ids:
        return updated, reasons

    for matched_issue_id in matched_issue_ids:
        issue_def = issue_option_spec.get(matched_issue_id, {})
        options = issue_def.get("options") if isinstance(issue_def, dict) else None
        if not isinstance(options, list):
            continue
        issue_stance = role_stances.get(matched_issue_id)
        if not isinstance(issue_stance, dict):
            continue
        acceptance = issue_stance.get("acceptance")
        if not isinstance(acceptance, dict):
            continue

        for opt in options:
            if not isinstance(opt, dict):
                continue
            option_id = opt.get("option_id")
            if not isinstance(option_id, str):
                continue
            if option_id not in acceptance:
                continue
            if acceptance.get(option_id) is None:
                continue
            if option_id not in trigger:
                continue
            current_val = float(acceptance.get(option_id, 0.0))
            delta = min(ACCEPTANCE_DELTA_ON_MENTION, MAX_ACCEPTANCE_DELTA)
            new_val = _clamp01(current_val + delta)
            if new_val != current_val:
                acceptance[option_id] = new_val
                reasons.append(
                    {
                        "role_id": role_id,
                        "round_id": round_id,
                        "issue_id": matched_issue_id,
                        "option_id": option_id,
                        "delta_acceptance": new_val - current_val,
                        "rule": "option_mention_acceptance_increase",
                        "trigger": trigger_snippet,
                    }
                )

        if matched_issue_id in trigger:
            firmness_val = issue_stance.get("firmness")
            if isinstance(firmness_val, (int, float)):
                delta = min(FIRMNESS_DELTA_ON_ISSUE_MENTION, MAX_FIRMNESS_DELTA)
                new_val = _clamp01(float(firmness_val) + delta)
                if new_val != float(firmness_val):
                    issue_stance["firmness"] = new_val
                    reasons.append(
                        {
                            "role_id": role_id,
                            "round_id": round_id,
                            "issue_id": matched_issue_id,
                            "delta_firmness": new_val - float(firmness_val),
                            "rule": "issue_mention_firmness_increase",
                            "trigger": trigger_snippet,
                        }
                    )

    return updated, reasons


def _matched_issue_ids(
    issue_id: Optional[str], trigger: str, issue_option_spec: Dict[str, Any]
) -> List[str]:
    matched: List[str] = []
    if issue_id:
        if issue_id in trigger or _any_option_id_in_trigger(issue_option_spec, issue_id, trigger):
            matched.append(issue_id)
        return matched
    for issue_key in issue_option_spec.keys():
        if not isinstance(issue_key, str):
            continue
        if issue_key in trigger or _any_option_id_in_trigger(issue_option_spec, issue_key, trigger):
            matched.append(issue_key)
    return matched


def _any_option_id_in_trigger(
    issue_option_spec: Dict[str, Any], issue_id: str, trigger: str
) -> bool:
    issue_def = issue_option_spec.get(issue_id, {})
    if not isinstance(issue_def, dict):
        return False
    options = issue_def.get("options")
    if not isinstance(options, list):
        return False
    for opt in options:
        if not isinstance(opt, dict):
            continue
        option_id = opt.get("option_id")
        if isinstance(option_id, str) and option_id in trigger:
            return True
    return False


def _is_role_indexed(stance_snapshot: Dict[str, Any], role_id: str) -> bool:
    role_stance = stance_snapshot.get(role_id)
    return isinstance(role_stance, dict)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
