"""
Tests for response_builder.py — health score, response contract, null safety.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import build_response, _compute_health_score, _health_label

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CURRENT_ROWS = [
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-100",
     "LOCFR": "SUP-A", "GSCFSCTQTY": 120, "GSCCONROJDATE": "2026-07-01",
     "ZCOIBODVER": "v3", "ZCOIFORMFACT": "FF-B", "ZCOIDCID": "DC-WEST"},
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-101",
     "LOCFR": "SUP-B", "GSCFSCTQTY": 50, "GSCCONROJDATE": "2026-06-15",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A", "ZCOIDCID": "DC-WEST"},
    {"LOCID": "LOC002", "GSCEQUIPCAT": "VALVE", "PRDID": "MAT-200",
     "LOCFR": "SUP-C", "GSCFSCTQTY": 30, "GSCCONROJDATE": "2026-08-01",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A", "ZCOIDCID": "DC-EAST"},
]

PREVIOUS_ROWS = [
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-100",
     "LOCFR": "SUP-A", "GSCPREVFCSTQTY": 50, "GSCPREVROJNBD": "2026-06-01",
     "ZCOIBODVER": "v2", "ZCOIFORMFACT": "FF-A"},
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-101",
     "LOCFR": "SUP-B", "GSCPREVFCSTQTY": 50, "GSCPREVROJNBD": "2026-06-15",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"},
    {"LOCID": "LOC002", "GSCEQUIPCAT": "VALVE", "PRDID": "MAT-200",
     "LOCFR": "SUP-C", "GSCPREVFCSTQTY": 30, "GSCPREVROJNBD": "2026-08-01",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"},
]


def _pipeline(current=None, previous=None):
    c = normalize_rows(current or CURRENT_ROWS, is_current=True)
    p = normalize_rows(previous or PREVIOUS_ROWS, is_current=False)
    return compare_records(filter_records(c), filter_records(p))


# ---------------------------------------------------------------------------
# Health score tests
# ---------------------------------------------------------------------------

def test_health_score_100_for_no_changes():
    same = [{"LOCID": "L1", "GSCEQUIPCAT": "P", "PRDID": "M1",
             "LOCFR": "S1", "GSCFSCTQTY": 10, "GSCCONROJDATE": "2026-01-01",
             "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"}]
    prev = [{"LOCID": "L1", "GSCEQUIPCAT": "P", "PRDID": "M1",
             "LOCFR": "S1", "GSCPREVFCSTQTY": 10, "GSCPREVROJNBD": "2026-01-01",
             "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"}]
    compared = _pipeline(same, prev)
    score = _compute_health_score(compared, [])
    assert score == 100


def test_health_score_clamped_to_zero():
    # 100% changed with design+supplier risk
    current = [{"LOCID": f"L{i}", "GSCEQUIPCAT": "P", "PRDID": f"M{i}",
                "LOCFR": "NEW", "GSCFSCTQTY": 999, "GSCCONROJDATE": "2026-01-01",
                "ZCOIBODVER": "v9", "ZCOIFORMFACT": "FF-Z"} for i in range(20)]
    previous = [{"LOCID": f"L{i}", "GSCEQUIPCAT": "P", "PRDID": f"M{i}",
                 "LOCFR": "OLD", "GSCPREVFCSTQTY": 1, "GSCPREVROJNBD": "2025-01-01",
                 "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"} for i in range(20)]
    compared = _pipeline(current, previous)
    score = _compute_health_score(compared, [r for r in compared])
    assert score >= 0


def test_health_score_between_0_and_100():
    compared = _pipeline()
    changed = [r for r in compared if r.change_type != "Unchanged"]
    score = _compute_health_score(compared, changed)
    assert 0 <= score <= 100


def test_health_label_bands():
    assert _health_label(85) == "Healthy"
    assert _health_label(65) == "Stable"
    assert _health_label(45) == "At Risk"
    assert _health_label(20) == "Critical"
    assert _health_label(80) == "Healthy"
    assert _health_label(60) == "Stable"
    assert _health_label(40) == "At Risk"
    assert _health_label(0) == "Critical"


# ---------------------------------------------------------------------------
# Response contract tests
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "dataMode", "lastRefreshedAt", "planningHealth", "status",
    "forecastNew", "forecastOld", "trendDirection", "trendDelta",
    "totalRecords", "changedRecordCount", "unchangedRecordCount",
    "riskSummary", "aiInsight", "rootCause", "recommendedActions",
    "drivers", "alerts", "filters", "datacenterSummary",
    "materialGroupSummary", "supplierSummary", "designSummary", "rojSummary",
]


def test_build_response_contains_all_required_fields():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    for field in REQUIRED_FIELDS:
        assert field in result, f"Missing field: {field}"


def test_build_response_data_mode_preserved():
    compared = _pipeline()
    for mode in ("live", "cached", "blob"):
        result = build_response(compared, [], data_mode=mode)
        assert result["dataMode"] == mode


def test_build_response_counts_correct():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    assert result["totalRecords"] == len(compared)
    assert result["changedRecordCount"] + result["unchangedRecordCount"] == result["totalRecords"]


def test_build_response_risk_summary_structure():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    rs = result["riskSummary"]
    assert "level" in rs
    assert "highestRiskLevel" in rs
    assert "highRiskCount" in rs
    assert "riskBreakdown" in rs
    assert isinstance(rs["riskBreakdown"], dict)


def test_build_response_recommended_actions_is_list():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    assert isinstance(result["recommendedActions"], list)
    assert len(result["recommendedActions"]) > 0


def test_build_response_json_serializable():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    serialized = json.dumps(result, default=str)
    parsed = json.loads(serialized)
    assert parsed["totalRecords"] == len(compared)


def test_build_response_empty_records():
    result = build_response([], [], data_mode="live")
    assert result["totalRecords"] == 0
    assert result["changedRecordCount"] == 0
    assert result["planningHealth"] == 100


def test_build_response_filters_preserved():
    compared = _pipeline()
    result = build_response(compared, [], location_id="LOC001", material_group="PUMP", data_mode="live")
    assert result["filters"]["locationId"] == "LOC001"
    assert result["filters"]["materialGroup"] == "PUMP"


def test_build_response_drivers_structure():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    d = result["drivers"]
    assert "location" in d
    assert "supplier" in d
    assert "material" in d
    assert "materialGroup" in d
    assert "changeType" in d


def test_build_response_design_summary_structure():
    compared = _pipeline()
    result = build_response(compared, [], data_mode="live")
    ds = result["designSummary"]
    assert "status" in ds
    assert "bodChangedCount" in ds
    assert "formFactorChangedCount" in ds
    assert "details" in ds
    assert isinstance(ds["details"], list)
