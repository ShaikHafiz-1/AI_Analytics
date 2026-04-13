# Dataclass Handling Fix - Error #5

## Issue
**Error**: `AttributeError: 'RootCauseContext' object has no attribute 'get'`
**Location**: `planning_intelligence/response_builder.py`, line 814 in `_generate_insights_deterministic()`
**Root Cause**: Function was treating dataclass objects as dictionaries, calling `.get()` method which doesn't exist on dataclasses

## Root Cause Analysis

The function was written to handle dictionary objects:
```python
root_cause.get("drivers", [])  # ❌ WRONG - RootCauseContext is a dataclass, not a dict
recommendations.get("actions", [])  # ❌ WRONG - RecommendationContext is a dataclass, not a dict
```

But the actual objects passed are dataclasses:
- `RootCauseContext` - has attributes: `primary_driver`, `change_type_label`, etc.
- `RecommendationContext` - has attribute: `actions` (a list)

## Solution Applied

### Step 1: Understand the Dataclass Structures
From `planning_intelligence/mcp/schemas.py`:

```python
@dataclass
class RootCauseContext:
    primary_driver: str            # "quantity" | "supplier" | "design" | "schedule"
    primary_driver_count: int
    driver_location: Optional[str]
    driver_supplier: Optional[str]
    driver_material: Optional[str]
    driver_material_group: Optional[str]
    change_type_label: str         # human-readable e.g. "Quantity + Design"
    is_stable: bool

@dataclass
class RecommendationContext:
    actions: List[str]
```

### Step 2: Understand Expected Return Structure
From `planning_intelligence/response_builder.py` (line 130-132):

```python
"aiInsight": insights["aiInsight"],
"rootCause": insights["rootCause"],
"recommendedActions": insights["recommendedActions"],
```

The function must return a dict with these exact keys.

### Step 3: Rewrite Function to Handle Dataclasses

**Before (BROKEN)**:
```python
def _generate_insights_deterministic(ctx, risk, root_cause, recommendations):
    return {
        "summary": f"Planning health is {_health_label(ctx.planning_health)}. "
                   f"Forecast trend is {_trend_label(ctx.trend_direction)}.",
        "keyDrivers": root_cause.get("drivers", [])[:3] if root_cause else [],  # ❌ WRONG
        "recommendations": recommendations.get("actions", [])[:3] if recommendations else [],  # ❌ WRONG
        "riskLevel": risk.get("highest_risk", "Normal") if risk else "Normal",  # ❌ WRONG
    }
```

**After (FIXED)**:
```python
def _generate_insights_deterministic(ctx, risk, root_cause, recommendations):
    """
    Generate insights deterministically without LLM.
    Replaces the deleted ai_insight_engine.generate_insights() function.
    
    Args:
        ctx: AnalyticsContext dataclass
        risk: RiskSummary dataclass
        root_cause: RootCauseContext dataclass
        recommendations: RecommendationContext dataclass
    
    Returns:
        dict with aiInsight, rootCause, recommendedActions keys
    """
    # Build AI insight summary
    health_label = _health_label(ctx.planning_health) if ctx else "Unknown"
    trend_label = _trend_label(ctx.trend_direction) if ctx else "Unknown"
    ai_insight = f"Planning health is {health_label}. Forecast trend is {trend_label}."
    
    # Extract root cause drivers
    root_cause_drivers = []
    if root_cause:
        if root_cause.primary_driver:
            root_cause_drivers.append(root_cause.primary_driver)
        if root_cause.change_type_label:
            root_cause_drivers.append(root_cause.change_type_label)
    
    # Extract recommendations
    recommended_actions = []
    if recommendations and hasattr(recommendations, 'actions'):
        recommended_actions = recommendations.actions[:3] if recommendations.actions else []
    
    return {
        "aiInsight": ai_insight,
        "rootCause": root_cause_drivers[:3],
        "recommendedActions": recommended_actions,
    }
```

## Key Changes

1. **Access attributes directly** instead of using `.get()`:
   - `root_cause.primary_driver` instead of `root_cause.get("primary_driver")`
   - `recommendations.actions` instead of `recommendations.get("actions")`

2. **Use `hasattr()` for safe attribute checking**:
   - `if recommendations and hasattr(recommendations, 'actions')`
   - Prevents AttributeError if object structure changes

3. **Return correct keys**:
   - `aiInsight` instead of `summary`
   - `rootCause` instead of `keyDrivers`
   - `recommendedActions` instead of `recommendations`

4. **Extract multiple drivers from RootCauseContext**:
   - Combines `primary_driver` and `change_type_label` into a list
   - Limits to 3 items with `[:3]` slice

5. **Handle None values safely**:
   - Check `if ctx` before accessing attributes
   - Check `if root_cause` before accessing attributes
   - Check `if recommendations and hasattr(...)` before accessing attributes

## Data Flow

```
build_response()
  ├─ root_cause = root_cause_driver_tool(compared)  [returns RootCauseContext]
  ├─ recommendations = recommendation_tool(...)  [returns RecommendationContext]
  └─ insights = _generate_insights_deterministic(ctx, risk, root_cause, recommendations)
      ├─ Accesses root_cause.primary_driver  ✅ Correct
      ├─ Accesses root_cause.change_type_label  ✅ Correct
      ├─ Accesses recommendations.actions  ✅ Correct
      └─ Returns dict with aiInsight, rootCause, recommendedActions  ✅ Correct
```

## Verification

✅ **Diagnostics**: No syntax errors in `response_builder.py`
✅ **Dataclass attributes**: All accessed correctly
✅ **Return structure**: Matches expected keys in response
✅ **None handling**: Safe checks prevent AttributeError
✅ **Type safety**: Uses `hasattr()` for defensive programming

## Status
**COMPLETE** - Dataclass handling fixed, all attribute accesses corrected, diagnostics pass.
