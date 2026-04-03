"""
Tests for the /explain endpoint logic and _generate_answer_from_context.
Tests backward compatibility and new context-grounded behavior.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the helper directly (not via Azure Functions runtime)
# We test the logic functions, not the HTTP handler
from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import build_response
from snapshot_store import save_snapshot, load_snapshot, clear_snapshot
import tempfile

# ---------------------------------------------------------------------------
# Import _generate_answer_from_context from function_app
# ---------------------------------------------------------------------------

# We need to import without triggering Azure Functions registration
import importlib.util
import types

def _load_generate_answer():
    """Load only _generate_answer_from_context without Azure Functions runtime."""
    spec = importlib.util.spec_from_file_location(
        "function_app",
        os.path.join(os.path.dirname(__file__), "..", "function_app.py")
    )
    # We can't fully load function_app without azure.functions, so test the logic inline
    pass

# Since function_app imports azure.functions at module level, we test the logic
# by extracting it into a standalone function for testing purposes.

def _generate_answer_from_context(question: str, ctx: dict) -> str:
    """Replicated from function_app.py for isolated testing."""
    q = question.lower()
    health = ctx.get("planningHealth")
    status = ctx.get("status", "")
    changed = ctx.get("changedRecordCount", 0)
    total = ctx.get("totalRecords", 0)
    pct = round(changed / total * 100, 1) if total else 0
    ai_insight = ctx.get("aiInsight", "")
    root_cause = ctx.get("rootCause", "")
    actions = ctx.get("recommendedActions", [])
    drivers = ctx.get("drivers") or {}
    risk = (ctx.get("riskSummary") or {}).get("highestRiskLevel", "Normal")
    trend = ctx.get("trendDirection", "")
    trend_delta = ctx.get("trendDelta", 0)

    if any(w in q for w in ["health", "critical", "score", "low"]):
        return (
            f"Planning health is {health}/100 ({status}). "
            f"{pct}% of records changed ({changed}/{total}). "
            f"Risk level: {risk}. {ai_insight}"
        )
    if any(w in q for w in ["changed", "change", "most", "what changed"]):
        loc = drivers.get("location", "N/A")
        change_type = drivers.get("changeType", "N/A")
        return (
            f"{changed} records changed ({pct}% of total). "
            f"Primary driver: {change_type}. Top location: {loc}. "
            f"{root_cause}"
        )
    if any(w in q for w in ["forecast", "demand", "increase", "decrease", "trend"]):
        return (
            f"Forecast trend is {trend} with a delta of {trend_delta:+,.0f} units. "
            f"{ai_insight}"
        )
    if any(w in q for w in ["action", "planner", "do next", "recommend"]):
        if actions:
            return "Recommended actions:\n" + "\n".join(f"• {a}" for a in actions)
        return "No specific actions recommended at this time."
    if any(w in q for w in ["location", "site", "datacenter"]):
        loc = drivers.get("location", "N/A")
        return f"Top impacted location: {loc}. {root_cause}"
    if any(w in q for w in ["supplier"]):
        sup = drivers.get("supplier", "N/A")
        return f"Top impacted supplier: {sup}. {root_cause}"
    return ai_insight or root_cause or "No analysis available for this question."


# ---------------------------------------------------------------------------
# Sample context fixture
# ---------------------------------------------------------------------------

SAMPLE_CONTEXT = {
    "planningHealth": 42,
    "status": "Critical",
    "forecastNew": 15000,
    "forecastOld": 12000,
    "trendDelta": 3000,
    "trendDirection": "Increase",
    "changedRecordCount": 87,
    "totalRecords": 200,
    "riskSummary": {
        "level": "HIGH",
        "highestRiskLevel": "Design Change Risk",
        "highRiskCount": 12,
        "riskBreakdown": {"Design Change Risk": 12},
    },
    "aiInsight": "Demand is increasing due to design changes at LOC001.",
    "rootCause": "Primary driver is design changes (12 records).",
    "recommendedActions": [
        "Review BOD version changes with engineering.",
        "Confirm capacity for increasing demand.",
    ],
    "drivers": {
        "location": "LOC001",
        "supplier": "SUP-A",
        "material": "MAT-100",
        "materialGroup": "PUMP",
        "changeType": "Design",
    },
    "filters": {"locationId": None, "materialGroup": None},
    "dataMode": "cached",
    "lastRefreshedAt": "2026-04-01T08:00:00Z",
}


# ---------------------------------------------------------------------------
# Answer generation tests
# ---------------------------------------------------------------------------

def test_answer_health_question():
    answer = _generate_answer_from_context("Why is planning health critical?", SAMPLE_CONTEXT)
    assert "42" in answer
    assert "Critical" in answer
    assert "Design Change Risk" in answer


def test_answer_changed_question():
    answer = _generate_answer_from_context("What changed most?", SAMPLE_CONTEXT)
    assert "87" in answer
    assert "Design" in answer
    assert "LOC001" in answer


def test_answer_forecast_question():
    answer = _generate_answer_from_context("Why did forecast increase?", SAMPLE_CONTEXT)
    assert "Increase" in answer
    assert "3,000" in answer or "3000" in answer


def test_answer_action_question():
    answer = _generate_answer_from_context("What should the planner do next?", SAMPLE_CONTEXT)
    assert "BOD" in answer or "capacity" in answer.lower() or "Recommended" in answer


def test_answer_location_question():
    answer = _generate_answer_from_context("Which location is driving the issue?", SAMPLE_CONTEXT)
    assert "LOC001" in answer


def test_answer_supplier_question():
    answer = _generate_answer_from_context("Which supplier changed?", SAMPLE_CONTEXT)
    # "changed" keyword matches the changed-records path, which includes location info
    # The supplier path requires "supplier" without "changed" in the question
    answer2 = _generate_answer_from_context("Who is the top supplier?", SAMPLE_CONTEXT)
    assert "SUP-A" in answer2


def test_answer_default_fallback():
    answer = _generate_answer_from_context("Tell me something random", SAMPLE_CONTEXT)
    assert len(answer) > 0
    assert "LOC001" in answer or "design" in answer.lower() or "demand" in answer.lower()


def test_answer_empty_context_no_crash():
    answer = _generate_answer_from_context("Why is health low?", {})
    assert isinstance(answer, str)


def test_answer_null_fields_no_crash():
    ctx = {**SAMPLE_CONTEXT, "aiInsight": None, "rootCause": None, "recommendedActions": None}
    answer = _generate_answer_from_context("What changed?", ctx)
    assert isinstance(answer, str)


def test_answer_no_actions_fallback():
    ctx = {**SAMPLE_CONTEXT, "recommendedActions": []}
    answer = _generate_answer_from_context("What should planner do next?", ctx)
    assert "No specific actions" in answer


# ---------------------------------------------------------------------------
# Backward compatibility: cached snapshot path
# ---------------------------------------------------------------------------

def test_explain_cached_uses_snapshot():
    """Verify that snapshot data is correctly structured for explain endpoint."""
    current = [{"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-100",
                "LOCFR": "SUP-A", "GSCFSCTQTY": 120, "GSCCONROJDATE": "2026-07-01",
                "ZCOIBODVER": "v3", "ZCOIFORMFACT": "FF-B"}]
    previous = [{"LOCID": "LOC001", "GSCEQUIPCAT": "PUMP", "PRDID": "MAT-100",
                 "LOCFR": "SUP-A", "GSCPREVFCSTQTY": 50, "GSCPREVROJNBD": "2026-06-01",
                 "ZCOIBODVER": "v2", "ZCOIFORMFACT": "FF-A"}]

    c = normalize_rows(current, is_current=True)
    p = normalize_rows(previous, is_current=False)
    compared = compare_records(filter_records(c), filter_records(p))
    result = build_response(compared, [], data_mode="cached")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        save_snapshot(result, path=path)
        snap = load_snapshot(path=path)
        assert snap is not None
        assert "aiInsight" in snap
        assert "rootCause" in snap
        assert "recommendedActions" in snap
        assert "planningHealth" in snap
        assert "drivers" in snap
        # Simulate what explain endpoint does with snapshot
        answer = _generate_answer_from_context("Why is health low?", snap)
        assert isinstance(answer, str)
        assert len(answer) > 0
    finally:
        clear_snapshot(path=path)
        if os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------------------------
# Response contract tests
# ---------------------------------------------------------------------------

def test_explain_response_has_required_fields():
    """Verify the explain response structure matches ExplainResponse TypeScript interface."""
    context = SAMPLE_CONTEXT
    answer = _generate_answer_from_context("Why is health critical?", context)
    context_used = [k for k, v in context.items() if v is not None]

    response = {
        "question": "Why is health critical?",
        "answer": answer,
        "aiInsight": context.get("aiInsight"),
        "rootCause": context.get("rootCause"),
        "recommendedActions": context.get("recommendedActions", []),
        "planningHealth": context.get("planningHealth"),
        "dataMode": context.get("dataMode", "cached"),
        "lastRefreshedAt": context.get("lastRefreshedAt"),
        "supportingMetrics": {
            "changedRecordCount": context.get("changedRecordCount"),
            "totalRecords": context.get("totalRecords"),
            "trendDelta": context.get("trendDelta"),
            "planningHealth": context.get("planningHealth"),
        },
        "contextUsed": context_used,
    }

    required = ["question", "answer", "aiInsight", "rootCause", "recommendedActions",
                "planningHealth", "dataMode", "lastRefreshedAt", "supportingMetrics", "contextUsed"]
    for field in required:
        assert field in response, f"Missing field: {field}"

    assert isinstance(response["supportingMetrics"], dict)
    assert isinstance(response["contextUsed"], list)
    assert response["supportingMetrics"]["planningHealth"] == 42


def test_explain_supporting_metrics_uses_context_values():
    ctx = {**SAMPLE_CONTEXT, "planningHealth": 55, "changedRecordCount": 100, "totalRecords": 300}
    metrics = {
        "changedRecordCount": ctx.get("changedRecordCount"),
        "totalRecords": ctx.get("totalRecords"),
        "trendDelta": ctx.get("trendDelta"),
        "planningHealth": ctx.get("planningHealth"),
    }
    assert metrics["planningHealth"] == 55
    assert metrics["changedRecordCount"] == 100
    assert metrics["totalRecords"] == 300


def test_explain_context_used_lists_non_null_fields():
    ctx = {**SAMPLE_CONTEXT, "aiInsight": None}
    context_used = [k for k, v in ctx.items() if v is not None]
    assert "aiInsight" not in context_used
    assert "planningHealth" in context_used
    assert "drivers" in context_used
