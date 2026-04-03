"""
Tests for the /debug-snapshot endpoint logic.
Tests intermediate pipeline values and response structure.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import build_response
from analytics import is_changed
from collections import Counter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CURRENT_ROWS = [
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-100",
     "LOCFR": "SUP-A", "GSCFSCTQTY": 120, "GSCCONROJDATE": "2026-07-01",
     "ZCOIBODVER": "v3", "ZCOIFORMFACT": "FF-B"},
    {"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-101",
     "LOCFR": "SUP-B", "GSCFSCTQTY": 50, "GSCCONROJDATE": "2026-06-15",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"},
    {"LOCID": "LOC002", "GSCEQUIPCAT": "VALVE", "PRDID": "MAT-200",
     "LOCFR": "SUP-C", "GSCFSCTQTY": 30, "GSCCONROJDATE": "2026-08-01",
     "ZCOIBODVER": "v1", "ZCOIFORMFACT": "FF-A"},
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


def _run_debug_pipeline(current_rows, previous_rows, location_id=None, material_group=None):
    """Simulates the debug-snapshot pipeline, returning intermediate values."""
    current_records = normalize_rows(current_rows, is_current=True)
    previous_records = normalize_rows(previous_rows, is_current=False)
    current_filtered = filter_records(current_records, location_id, material_group)
    previous_filtered = filter_records(previous_records, location_id, material_group)
    compared = compare_records(current_filtered, previous_filtered)

    changed_records = [r for r in compared if is_changed(r)]
    changed_count = len(changed_records)
    total_count = len(compared)

    risk_counts = Counter(r.risk_level for r in changed_records if r.risk_level != "Normal")
    design_count = sum(1 for r in changed_records if r.design_changed)
    supplier_count = sum(1 for r in changed_records if r.supplier_changed)
    highest_risk = next(
        (r for r in ["Design + Supplier Change Risk", "Design Change Risk",
                     "Supplier Change Risk", "High Demand Spike"] if r in risk_counts),
        "Normal"
    )

    change_ratio_ded = round((changed_count / max(total_count, 1)) * 40)
    risk_ded = (25 if "Design + Supplier" in highest_risk
                else 15 if any(x in highest_risk for x in ["Design", "Supplier"])
                else 10 if "Spike" in highest_risk else 0)
    design_ded = min(design_count * 2, 10)
    supplier_ded = min(supplier_count * 2, 10)

    result = build_response(compared, [], location_id, material_group, data_mode="live")

    return {
        "normalizedCount": len(current_records),
        "filteredCount": len(current_filtered),
        "comparedCount": total_count,
        "changedCount": changed_count,
        "healthScoreInputs": {
            "total": total_count,
            "changed": changed_count,
            "riskCounts": dict(risk_counts),
            "designCount": design_count,
            "supplierCount": supplier_count,
            "highestRisk": highest_risk,
            "deductions": {
                "changeRatio": change_ratio_ded,
                "riskLevel": risk_ded,
                "designPenalty": design_ded,
                "supplierPenalty": supplier_ded,
            },
        },
        "dashboardResponse": result,
    }


# ---------------------------------------------------------------------------
# Debug snapshot structure tests
# ---------------------------------------------------------------------------

def test_debug_snapshot_has_all_required_fields():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    required = ["normalizedCount", "filteredCount", "comparedCount", "changedCount",
                "healthScoreInputs", "dashboardResponse"]
    for field in required:
        assert field in snap, f"Missing field: {field}"


def test_debug_snapshot_health_score_inputs_structure():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    hsi = snap["healthScoreInputs"]
    required = ["total", "changed", "riskCounts", "designCount", "supplierCount",
                "highestRisk", "deductions"]
    for field in required:
        assert field in hsi, f"Missing healthScoreInputs field: {field}"
    deductions = hsi["deductions"]
    for d in ["changeRatio", "riskLevel", "designPenalty", "supplierPenalty"]:
        assert d in deductions, f"Missing deduction: {d}"


def test_debug_snapshot_counts_are_correct():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    assert snap["normalizedCount"] == 3
    assert snap["filteredCount"] == 3
    assert snap["comparedCount"] == 3
    assert snap["changedCount"] == 1  # Only MAT-100 changed


def test_debug_snapshot_design_count_correct():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    assert snap["healthScoreInputs"]["designCount"] == 1


def test_debug_snapshot_highest_risk_correct():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    assert snap["healthScoreInputs"]["highestRisk"] == "Design Change Risk"


def test_debug_snapshot_deductions_non_negative():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    deductions = snap["healthScoreInputs"]["deductions"]
    for key, val in deductions.items():
        assert val >= 0, f"Deduction {key} is negative: {val}"


def test_debug_snapshot_deductions_within_bounds():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    d = snap["healthScoreInputs"]["deductions"]
    assert d["changeRatio"] <= 40
    assert d["riskLevel"] <= 25
    assert d["designPenalty"] <= 10
    assert d["supplierPenalty"] <= 10


def test_debug_snapshot_dashboard_response_present():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    dr = snap["dashboardResponse"]
    assert "planningHealth" in dr
    assert "totalRecords" in dr
    assert dr["totalRecords"] == 3


def test_debug_snapshot_with_location_filter():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS, location_id="LOC001")
    assert snap["filteredCount"] == 2
    assert snap["comparedCount"] == 2


def test_debug_snapshot_with_no_matching_filter():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS, location_id="LOC999")
    assert snap["filteredCount"] == 0
    assert snap["changedCount"] == 0


def test_debug_snapshot_json_serializable():
    snap = _run_debug_pipeline(CURRENT_ROWS, PREVIOUS_ROWS)
    serialized = json.dumps(snap, default=str)
    parsed = json.loads(serialized)
    assert parsed["comparedCount"] == 3


def test_debug_snapshot_empty_input():
    snap = _run_debug_pipeline([], [])
    assert snap["normalizedCount"] == 0
    assert snap["changedCount"] == 0
    assert snap["healthScoreInputs"]["total"] == 0
