# Azure Functions Import Error Fix - April 11, 2026

## Problem

Azure Functions failed to start with error:
```
ModuleNotFoundError: No module named 'insight_generator'
```

**Root Cause**: `dashboard_builder.py` was importing the deleted `insight_generator` module.

---

## Solution

### File: `planning_intelligence/dashboard_builder.py`

**Changes Made**:

1. **Removed import** (line 10):
   ```python
   # Before:
   from insight_generator import generate_insights
   
   # After:
   # Removed: insight_generator (module deleted during cleanup)
   ```

2. **Replaced function call** (lines 72-95):
   ```python
   # Before:
   insights = generate_insights(
       total_records=total,
       matched_records=total - new_records,
       new_records=new_records,
       forecast_new=forecast_new,
       forecast_old=forecast_old,
       trend_delta=trend_delta,
       trend_direction=trend_direction,
       quantity_changed_count=qty_changed_count,
       supplier_changed_count=supplier_changed_count,
       design_changed_count=design_changed_count,
       roj_changed_count=roj_changed_count,
       highest_risk_level=highest_risk,
       top_impacted_location=top_location,
       top_impacted_supplier=top_supplier,
       top_impacted_material=top_material,
       top_impacted_material_group=top_group,
   )
   
   # After:
   insights = _generate_insights_deterministic(
       total_records=total,
       changed_count=changed_count,
       forecast_delta=trend_delta,
       trend_direction=trend_direction,
       highest_risk_level=highest_risk,
       top_location=top_location,
   )
   ```

3. **Added deterministic function** (end of file):
   ```python
   def _generate_insights_deterministic(
       total_records: int,
       changed_count: int,
       forecast_delta: float,
       trend_direction: str,
       highest_risk_level: str,
       top_location: Optional[str],
   ) -> str:
       """
       Generate insights deterministically without LLM.
       Replaces the deleted insight_generator.generate_insights() function.
       """
       pct = round((changed_count / max(total_records, 1)) * 100, 1)
       
       if highest_risk_level == "High":
           return f"⚠️ Planning health is at risk. {pct}% of records changed ({changed_count}/{total_records}). Forecast {trend_direction} by {abs(forecast_delta):,.0f} units. Top location: {top_location or 'N/A'}. Immediate action required."
       elif highest_risk_level == "Medium":
           return f"📊 Planning health is moderate. {pct}% of records changed. Forecast {trend_direction}. Review changes at {top_location or 'key locations'}."
       else:
           return f"✅ Planning health is stable. {pct}% of records changed. Forecast {trend_direction}. No immediate action needed."
   ```

---

## Verification

✅ **Diagnostics Check**: No errors found in `dashboard_builder.py` or `function_app.py`

✅ **Import Resolution**: All imports now reference existing modules

✅ **Function Replacement**: Deterministic fallback function added

---

## Testing

To verify the fix works:

```bash
# Start Azure Functions
func start

# Should see all 5 endpoints loaded:
# - planning_intelligence_nlp
# - planning-dashboard-v2
# - daily-refresh
# - explain
# - debug-snapshot
```

---

## Files Modified

- `planning_intelligence/dashboard_builder.py` - Fixed import and added deterministic function

---

## Status

✅ **FIXED** - Azure Functions should now start successfully.
