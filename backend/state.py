import hashlib
import random
from typing import Any, Dict, List, Optional, Sequence


COUNTRIES: List[str] = ["BRA", "CAN", "CHN", "EU", "TZA", "USA"]
NGOS: List[str] = ["AMAP", "MFF", "WCPA"]
CHAIR: str = "JPN"
ISSUES: List[str] = ["1", "2", "3", "4"]
VOTE_ORDER: List[str] = COUNTRIES


def _stable_int(seed: int, salt: str) -> int:
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    return int(digest, 16) % (2**63)


def initial_state(human_role_id: Optional[str] = None) -> Dict:
    roles = {role: {"type": "country"} for role in COUNTRIES}
    roles.update({role: {"type": "ngo"} for role in NGOS})
    roles[CHAIR] = {"type": "chair"}

    return {
        "version": "v1",
        "status": "ROLE_SELECTION",
        "human_role_id": human_role_id,
        "roles": roles,
        "round1": {"speaker_order": [], "openings": {}, "cursor": 0},
        "round2": {"human_conversations": [], "second_conversation_available": True},
        "round3": {"issues": ISSUES.copy(), "active_issue_index": None, "active_issue": None},
        "stances": {},
        "votes": {},
        "checkpoints": [],
    }


def ensure_default_stances(state: Dict, default_firmness: float = 0.5) -> None:
    if "stances" not in state or not isinstance(state["stances"], dict):
        state["stances"] = {}
    for role_id in state.get("roles", {}):
        state["stances"].setdefault(role_id, {})
        for issue_id in ISSUES:
            state["stances"][role_id].setdefault(
                issue_id, {"acceptance": {}, "firmness": default_firmness}
            )


def merge_initial_stances(state: Dict, role_id: str, initial_stances: Any) -> None:
    if not isinstance(initial_stances, dict):
        return
    stances = state.setdefault("stances", {})
    role_stances = stances.setdefault(role_id, {})
    issue_map: Any = initial_stances.get("by_issue_id")
    if not isinstance(issue_map, dict):
        issue_map = initial_stances
    for issue_key, issue_data in issue_map.items():
        issue_id = _normalize_issue_id(issue_key)
        if not issue_id or not isinstance(issue_data, dict):
            continue
        issue_stance = role_stances.setdefault(issue_id, {"acceptance": {}})
        acceptance = issue_stance.setdefault("acceptance", {})
        init_acceptance = issue_data.get("acceptance")
        if isinstance(init_acceptance, dict):
            for opt_id, val in init_acceptance.items():
                if opt_id in acceptance:
                    continue
                if val is None:
                    acceptance[opt_id] = None
                elif isinstance(val, (int, float)):
                    acceptance[opt_id] = _clamp01(float(val))
        if "preferred" not in issue_stance:
            preferred = issue_data.get("preferred")
            if isinstance(preferred, str):
                issue_stance["preferred"] = preferred
                if preferred not in acceptance:
                    acceptance[preferred] = 0.7
        if "firmness" not in issue_stance:
            firmness = issue_data.get("firmness")
            if isinstance(firmness, (int, float)):
                issue_stance["firmness"] = _clamp01(float(firmness))


def _normalize_issue_id(issue_key: Any) -> Optional[str]:
    if not isinstance(issue_key, str):
        return None
    if issue_key.startswith("ISSUE_"):
        return issue_key.split("_", 1)[1]
    return issue_key


def deterministic_shuffle(items: Sequence[str], seed: int, salt: str) -> List[str]:
    items_list = list(items)
    rnd = random.Random(_stable_int(seed, salt))
    rnd.shuffle(items_list)
    return items_list


def speaker_order_with_constraint(seed: int, human_role_id: Optional[str]) -> List[str]:
    countries = deterministic_shuffle(COUNTRIES, seed, "round1-countries")
    ngos = deterministic_shuffle(NGOS, seed, "round1-ngos")

    def nudge(group: List[str]) -> List[str]:
        if human_role_id and human_role_id in group and group and group[0] == human_role_id:
            if len(group) > 1:
                group[0], group[1] = group[1], group[0]
        return group

    countries = nudge(countries)
    ngos = nudge(ngos)
    return countries + ngos


def pick_opening_variant(role_id: str, seed: int, candidates: List[Dict]) -> Dict:
    if not candidates:
        raise ValueError(f"No opening variants available for role {role_id}")
    ordered = sorted(candidates, key=lambda c: (str(c.get("id")), c.get("opening_text", "")))
    salted_seed = _stable_int(seed, f"opening-{role_id}")
    rng = random.Random(salted_seed)
    return rng.choice(ordered)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


__all__ = [
    "CHAIR",
    "COUNTRIES",
    "VOTE_ORDER",
    "NGOS",
    "ISSUES",
    "initial_state",
    "ensure_default_stances",
    "merge_initial_stances",
    "speaker_order_with_constraint",
    "pick_opening_variant",
]
