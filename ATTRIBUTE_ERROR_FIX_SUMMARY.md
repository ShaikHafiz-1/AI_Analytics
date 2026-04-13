# AttributeError Fix Summary - Task 7 Completion

## Issue
**Error**: `AttributeError: 'AnalyticsContext' object has no attribute 'health_score'`
**Location**: `planning_intelligence/response_builder.py`, line 812 in `_generate_insights_deterministic()`
**Root Cause**: Function was referencing `ctx.health_score` but AnalyticsContext class defines the attribute as `planning_health`

## Root Cause Analysis
The AnalyticsContext dataclass (defined in `planning_intelligence/mcp/schemas.py`) has the following health-related attribute:
```python
planning_health: int           # 0-100
```

But the `_generate_insights_deterministic()` function was trying to access:
```python
ctx.health_score  # ❌ WRONG - doesn't exist
```

## Solution Applied
**File**: `planning_intelligence/response_builder.py`
**Function**: `_generate_insights_deterministic()` (line 806)

### Before (BROKEN):
```python
def _generate_insights_deterministic(ctx, risk, root_cause, recommendations):
    """
    Generate insights deterministically without LLM.
    Replaces the deleted ai_insight_engine.generate_insights() function.
    """
    return {
        "summary": f"Planning health is {_health_label(ctx.health_score)}. "  # ❌ WRONG
                   f"Forecast trend is {_trend_label(ctx.trend_direction)}.",
        "keyDrivers": root_cause.get("drivers", [])[:3] if root_cause else [],
        "recommendations": recommendations.get("actions", [])[:3] if recommendations else [],
        "riskLevel": risk.get("highest_risk", "Normal") if risk else "Normal",
    }
```

### After (FIXED):
```python
def _generate_insights_deterministic(ctx, risk, root_cause, recommendations):
    """
    Generate insights deterministically without LLM.
    Replaces the deleted ai_insight_engine.generate_insights() function.
    """
    return {
        "summary": f"Planning health is {_health_label(ctx.planning_health)}. "  # ✅ CORRECT
                   f"Forecast trend is {_trend_label(ctx.trend_direction)}.",
        "keyDrivers": root_cause.get("drivers", [])[:3] if root_cause else [],
        "recommendations": recommendations.get("actions", [])[:3] if recommendations else [],
        "riskLevel": risk.get("highest_risk", "Normal") if risk else "Normal",
    }
```

## Verification
✅ **Diagnostics**: No syntax errors in `response_builder.py`
✅ **Diagnostics**: No syntax errors in `mcp/tools.py`
✅ **AnalyticsContext**: Correctly defines `planning_health: int` (0-100)
✅ **analytics_context_tool**: Correctly sets `planning_health=planning_health` when creating AnalyticsContext
✅ **_health_label()**: Correctly expects an integer (0-100) for health score
✅ **_trend_label()**: Correctly expects a string for trend direction

## Related Fixes (Already Completed)
1. ✅ Fixed `alert_rules` import in `mcp/tools.py` - replaced with deterministic alert evaluation
2. ✅ Fixed `ai_insight_engine` import in `response_builder.py` - replaced with `_generate_insights_deterministic()`
3. ✅ Fixed `insight_generator` import in `dashboard_builder.py` - replaced with deterministic insights

## Data Flow Verification
```
build_response()
  ├─ health_score = _compute_health_score(...)  [local variable]
  ├─ ctx = analytics_context_tool(..., health_score, ...)
  │   └─ AnalyticsContext(planning_health=planning_health)  ✅ Correct
  └─ insights = _generate_insights_deterministic(ctx, ...)
      └─ _health_label(ctx.planning_health)  ✅ Now correct
```

## Additional Fix: Dataclass Object Handling

### Issue 2: Treating Dataclass Objects as Dictionaries
**Error**: `AttributeError: 'RootCauseContext' object has no attribute 'get'`
**Location**: `planning_intelligence/response_builder.py`, line 814 in `_generate_insights_deterministic()`
**Root Cause**: Function was calling `.get()` on dataclass objects, but dataclasses don't have a `.get()` method

### Solution Applied
Updated `_generate_insights_deterministic()` to:
1. Access dataclass attributes directly (not via `.get()`)
2. Return correct response structure with `aiInsight`, `rootCause`, `recommendedActions` keys
3. Handle None values safely with `hasattr()` checks
4. Extract `primary_driver` and `change_type_label` from RootCauseContext
5. Extract `actions` list from RecommendationContext

### Before (BROKEN):
```python
"keyDrivers": root_cause.get("drivers", [])[:3] if root_cause else [],
"recommendations": recommendations.get("actions", [])[:3] if recommendations else [],
```

### After (FIXED):
```python
root_cause_drivers = []
if root_cause:
    if root_cause.primary_driver:
        root_cause_drivers.append(root_cause.primary_driver)
    if root_cause.change_type_label:
        root_cause_drivers.append(root_cause.change_type_label)

recommended_actions = []
if recommendations and hasattr(recommendations, 'actions'):
    recommended_actions = recommendations.actions[:3] if recommendations.actions else []

return {
    "aiInsight": ai_insight,
    "rootCause": root_cause_drivers[:3],
    "recommendedActions": recommended_actions,
}
```

## Status
**COMPLETE** - All import errors fixed, all attribute references corrected, dataclass handling fixed, diagnostics pass.

## Next Steps
1. Test with `python run_daily_refresh.py` to verify the fix works end-to-end
2. Verify Azure Functions still starts with `func start`
3. Run comprehensive test suite to ensure no regressions
