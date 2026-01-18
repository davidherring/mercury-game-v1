import copy

from backend.stance_shift import apply_stance_shift


ISSUE_OPTION_SPEC = {
    "ISSUE_1": {
        "options": [
            {"option_id": "1.1"},
            {"option_id": "1.2"},
        ]
    }
}


def test_stance_shift_null_immutability():
    stance = {
        "ISSUE_1": {
            "acceptance": {"1.1": None, "1.2": 0.4},
            "firmness": 0.5,
        }
    }
    updated, reasons = apply_stance_shift(
        role_id="USA",
        round_id=2,
        issue_id="ISSUE_1",
        trigger_text="Discuss 1.1 and 1.2",
        stance_snapshot=copy.deepcopy(stance),
        issue_option_spec=ISSUE_OPTION_SPEC,
    )
    acc = updated["ISSUE_1"]["acceptance"]
    assert acc["1.1"] is None
    assert acc["1.2"] == 0.45
    assert any(r.get("option_id") == "1.2" for r in reasons)


def test_stance_shift_clamp_and_max_delta():
    stance = {
        "ISSUE_1": {
            "acceptance": {"1.1": 0.98, "1.2": 0.2},
            "firmness": 0.98,
        }
    }
    updated, reasons = apply_stance_shift(
        role_id="USA",
        round_id=3,
        issue_id="ISSUE_1",
        trigger_text="ISSUE_1 mentions 1.1 1.1",
        stance_snapshot=copy.deepcopy(stance),
        issue_option_spec=ISSUE_OPTION_SPEC,
    )
    acc = updated["ISSUE_1"]["acceptance"]
    assert acc["1.1"] == 1.0
    assert acc["1.2"] == 0.2
    firmness = updated["ISSUE_1"]["firmness"]
    assert firmness == 1.0
    option_reasons = [r for r in reasons if r.get("option_id") == "1.1"]
    assert len(option_reasons) == 1
    assert option_reasons[0]["delta_acceptance"] <= 0.10


def test_stance_shift_requires_mentions():
    stance = {
        "ISSUE_1": {
            "acceptance": {"1.1": 0.4, "1.2": 0.6},
            "firmness": 0.5,
        }
    }
    updated, reasons = apply_stance_shift(
        role_id="USA",
        round_id=2,
        issue_id=None,
        trigger_text="No issue ids here.",
        stance_snapshot=copy.deepcopy(stance),
        issue_option_spec=ISSUE_OPTION_SPEC,
    )
    assert updated == stance
    assert reasons == []
