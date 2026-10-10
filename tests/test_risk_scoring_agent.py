"""RiskScoringAgent.score without XMPP: the agent is built but never started."""
import pytest

from src.agents.risk_scoring import RiskScoringAgent
from src.core import ontology, risk_tiers, wqi
from src.sim import load_data


@pytest.fixture(scope="module")
def agent():
    frame = load_data.load_wqi_method()
    return RiskScoringAgent("risk_scoring@localhost", "x", subscribers=[],
                            method=wqi.method_from_frame(frame),
                            classes=risk_tiers.classes_from_frame(frame))


@pytest.fixture(scope="module")
def readings():
    return load_data.load_monthly_readings()


def _body(rows, ds="Padaviya", source="synthetic", month_index=0):
    return {"type": "well_readings", "month_index": month_index, "ds_division": ds,
            "source": source, "readings": rows}


def _rows(readings, ds="Padaviya", month=1):
    return readings[(readings["ds_division"] == ds) & (readings["month"] == month)].to_dict("records")


def test_scores_a_division_and_emits_a_valid_risk_record(agent, readings):
    body = _body(_rows(readings))
    ontology.validate(ontology.INFORM, body)  # the input itself follows the ontology
    record, detail = agent.score(body)
    ontology.validate(ontology.INFORM, record)
    assert record["wqi"] is not None and record["tier"] != risk_tiers.UNKNOWN_TIER
    assert detail["n_wells"] == 20 and detail["error"] is None


@pytest.mark.parametrize("bad", [-1.0, "n/a", float("inf"), True])
def test_one_unusable_well_is_dropped_and_the_rest_still_scored(agent, readings, bad):
    # Regression: one typo used to turn the whole village "Unknown", so its VillageAgent
    # would refuse the CFP ("no need") and lose the resource.
    rows = _rows(readings)
    rows[0]["F_mg_L"] = bad
    record, detail = agent.score(_body(rows))
    ontology.validate(ontology.INFORM, record)
    assert record["tier"] != risk_tiers.UNKNOWN_TIER and detail["error"] is None
    assert detail["n_wells"] == 20 and detail["n_scored"] == 19 and detail["n_rejected"] == 1
    assert rows[0]["well_id"] in detail["rejected"]


def test_all_wells_unusable_is_unknown_with_reason(agent, readings):
    rows = _rows(readings)
    for r in rows:
        r["F_mg_L"] = -1.0
    record, detail = agent.score(_body(rows))
    assert record["tier"] == risk_tiers.UNKNOWN_TIER and "unusable" in detail["error"]


@pytest.mark.parametrize("break_it,reason", [
    (lambda rows: rows[0].update(source="real"), "real"),
    (lambda rows: rows[0].pop("well_id"), "identifier"),
    (lambda rows: rows.__setitem__(1, dict(rows[0])), "duplicate"),
])
def test_contract_violations_give_unknown_instead_of_crashing(agent, readings, break_it, reason):
    rows = _rows(readings)
    break_it(rows)
    record, detail = agent.score(_body(rows))
    ontology.validate(ontology.INFORM, record)
    assert record["wqi"] is None and record["tier"] == risk_tiers.UNKNOWN_TIER
    assert reason in detail["error"]


def test_message_spanning_two_months_is_rejected(agent, readings):
    record, detail = agent.score(_body(_rows(readings, month=1) + _rows(readings, month=7)))
    assert record["tier"] == risk_tiers.UNKNOWN_TIER and "one month" in detail["error"]


def test_parameter_blank_in_every_well_is_renormalised(agent, readings):
    # Regression: an all-None column became object dtype and voided the village.
    rows = _rows(readings)
    for r in rows:
        r["F_mg_L"] = None
    record, detail = agent.score(_body(rows))
    assert detail["error"] is None and record["wqi"] is not None
    assert "F" not in detail["params_used"]


def test_every_parameter_blank_reports_why(agent, readings):
    rows = _rows(readings)
    for r in rows:
        for c in ("pH", "alkalinity_mg_L", "hardness_mg_L", "F_mg_L", "DOC_mg_L",
                  "Cl_mg_L", "SO4_mg_L", "Fe_ug_L"):
            r[c] = None
    record, detail = agent.score(_body(rows))
    assert record["tier"] == risk_tiers.UNKNOWN_TIER
    assert detail["error"] == "no WQI parameter present in any well"


def test_a_blank_parameter_is_renormalised_not_rejected(agent, readings):
    rows = _rows(readings)
    rows[0]["pH"] = None
    record, detail = agent.score(_body(rows))
    assert detail["error"] is None and record["wqi"] is not None
    assert detail["weight_covered"] < 31 / 48  # that well was scored without pH


def test_empty_and_mislabelled_messages(agent, readings):
    record, detail = agent.score(_body([]))
    assert record["tier"] == risk_tiers.UNKNOWN_TIER and "no readings" in detail["error"]
    record, detail = agent.score(_body(_rows(readings), ds="Kandy"))
    assert record["tier"] == risk_tiers.UNKNOWN_TIER and "other divisions" in detail["error"]
