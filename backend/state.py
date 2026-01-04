import hashlib
import random
from typing import Dict, List, Optional, Sequence


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
    salted_seed = _stable_int(seed, f"opening-{role_id}")
    idx = salted_seed % len(candidates)
    return candidates[idx]


__all__ = [
    "CHAIR",
    "COUNTRIES",
    "VOTE_ORDER",
    "NGOS",
    "ISSUES",
    "initial_state",
    "ensure_default_stances",
    "speaker_order_with_constraint",
    "pick_opening_variant",
]
