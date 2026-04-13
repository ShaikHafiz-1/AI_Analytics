# Function App Integration Guide - Scoped Computation Fixes

## Overview

This guide shows exactly how to update `function_app.py` to use the new scoped computation and generative response modules.

---

## Step 1: Add Imports

Add these imports at the top of `function_app.py`:

```python
from scoped_metrics import (
    compute_scoped_metrics,
    get_location_metrics,
    get_design_changes,
    get_supplier_changes,
    get_quantity_changes,
    get_roj_changes,
    compare_locations,
    get_top_locations,
    get_top_suppliers,
    get_top_materials,
)
from generative_responses import build_contextual_response, ask_for_clarification
```

---

## Step 2: Update Answer Functions

### 1. Update `generate_location_answer()`

**BEFORE**:
```python
def generate_location_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for location-specific questions"""
    from copilot_helpers import extract_location_id, filter_records_by_location, get_top_locations_by_change
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Specific location query
        location_records = filter_records_by_location(detail_records, location_id)
        if not location_records:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": {"location": location_id, "recordCount": 0}
            }
        
        changed = sum(1 for r in location_records if r.get("changed"))
        answer = f"Location {location_id}: {len(location_records)} records total, {changed} changed."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "location": location_id,
                "recordCount": len(location_records),
                "changedCount": changed
            }
        }
    else:
        # Top locations query
        top_locations = get_top_locations_by_change(detail_records, limit=5)
        if not top_locations:
            return {
                "answer": "No location changes detected.",
                "supportingMetrics": {"topLocations": []}
            }
        
        answer = "Top locations by change count: "
        answer += ", ".join([f"{loc[0]} ({loc[1]} changes)" for loc in top_locations]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {"topLocations": top_locations}
        }
```

**AFTER**:
```python
def generate_location_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for location-specific questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Get scoped metrics
        metrics = get_location_metrics(detail_records, location_id)
        
        if metrics["totalRecords"] == 0:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": metrics
            }
        
        # Build generative response
        answer = build_contextual_response(
            question,
            metrics,
            "location",
            location=location_id
        )
        
        return {
            "answer": answer,
            "supportingMetrics": metrics
        }
    else:
        # Top locations query
        top_locations = get_top_locations(detail_records, limit=5)
        if not top_locations:
            return {
                "answer": "No location changes detected.",
                "supportingMetrics": {"topLocations": []}
            }
        
        answer = "Top locations by change count: "
        answer += ", ".join([f"{loc[0]} ({loc[1]} changes)" for loc in top_locations]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {"topLocations": top_locations}
        }
```

### 2. Update `generate_design_answer()`

**BEFORE**:
```python
def generate_design_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for design change questions"""
    from copilot_helpers import get_records_by_change_type, get_unique_suppliers, get_unique_materials
    
    design_records = get_records_by_change_type(detail_records, "design")
    if not design_records:
        return {
            "answer": "No design changes detected in the current data.",
            "supportingMetrics": {"designChangedCount": 0, "totalRecords": len(detail_records)}
        }
    
    suppliers = get_unique_suppliers(design_records)
    materials = get_unique_materials(design_records)
    
    answer = f"{len(design_records)} records have design changes (BOD or Form Factor). "
    if suppliers:
        answer += f"Affected suppliers: {', '.join(suppliers[:3])}. "
    if materials:
        answer += f"Affected materials: {', '.join(materials[:3])}."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "designChangedCount": len(design_records),
            "totalRecords": len(detail_records),
            "affectedSuppliers": suppliers,
            "affectedMaterials": materials
        }
    }
```

**AFTER**:
```python
def generate_design_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for design change questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    # Get design changes (scoped if location provided)
    metrics = get_design_changes(detail_records, location_id=location_id)
    
    if metrics["designChangedCount"] == 0:
        return {
            "answer": "No design changes detected.",
            "supportingMetrics": metrics
        }
    
    # Build generative response
    answer = build_contextual_response(
        question,
        metrics,
        "design"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

### 3. Update `generate_comparison_answer()`

**BEFORE**:
```python
def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions"""
    import re
    from copilot_helpers import filter_records_by_location
    
    # Extract location IDs from question
    locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    
    if len(locations) < 2:
        return {
            "answer": "Please specify two locations to compare (e.g., 'Compare CYS20_F01C01 vs DSM18_F01C01').",
            "supportingMetrics": {}
        }
    
    loc1, loc2 = locations[0], locations[1]
    records1 = filter_records_by_location(detail_records, loc1)
    records2 = filter_records_by_location(detail_records, loc2)
    
    changed1 = sum(1 for r in records1 if r.get("changed"))
    changed2 = sum(1 for r in records2 if r.get("changed"))
    
    answer = f"Comparison: {loc1} vs {loc2}. "
    answer += f"{loc1}: {len(records1)} records, {changed1} changed. "
    answer += f"{loc2}: {len(records2)} records, {changed2} changed."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "location1": loc1,
            "location1Records": len(records1),
            "location1Changed": changed1,
            "location2": loc2,
            "location2Records": len(records2),
            "location2Changed": changed2
        }
    }
```

**AFTER**:
```python
def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions"""
    import re
    
    # Extract location IDs from question
    locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    
    if len(locations) < 2:
        return {
            "answer": "Please specify two locations to compare (e.g., 'Compare CYS20_F01C01 vs DSM18_F01C01').",
            "supportingMetrics": {}
        }
    
    loc1, loc2 = locations[0], locations[1]
    
    # Get scoped comparison
    comparison = compare_locations(detail_records, loc1, loc2)
    
    # Build generative response
    answer = build_contextual_response(
        question,
        comparison,
        "comparison"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": comparison
    }
```

### 4. Update `generate_schedule_answer()` (ROJ)

**BEFORE**:
```python
def generate_schedule_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for ROJ/schedule change questions"""
    from copilot_helpers import compute_roi_metrics
    
    schedule_records = [r for r in detail_records if r.get("rojChanged", False)]
    if not schedule_records:
        return {
            "answer": "No ROJ (Release of Judgment) schedule changes detected.",
            "supportingMetrics": {"roiChangedCount": 0, "totalRecords": len(detail_records)}
        }
    
    metrics = compute_roi_metrics(schedule_records)
    
    answer = f"{metrics['roiChangedCount']} records have ROJ schedule changes. "
    if metrics['averageRoiDelta'] != 0:
        answer += f"Average ROJ delta: {metrics['averageRoiDelta']} days."
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

**AFTER**:
```python
def generate_schedule_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for ROJ schedule questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    # Get ROJ changes (scoped if location provided)
    metrics = get_roj_changes(detail_records, location_id=location_id)
    
    if metrics["rojChangedCount"] == 0:
        answer = f"No ROJ schedule changes detected{f' at {location_id}' if location_id else ''}."
    else:
        answer = f"{metrics['rojChangedCount']} records have ROJ schedule changes. " \
                f"Average delta: {metrics['averageRojDelta']} days."
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

### 5. Update `generate_entity_answer()`

**BEFORE**:
```python
def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions"""
    from copilot_helpers import get_records_by_change_type, get_unique_suppliers, get_unique_materials
    
    # ... existing logic that returns global results
```

**AFTER**:
```python
def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Get scoped metrics
        metrics = get_location_metrics(detail_records, location_id)
        
        answer = build_contextual_response(
            question,
            metrics,
            "location",
            location=location_id
        )
    else:
        # Ambiguous query - ask for clarification
        answer = ask_for_clarification(question)
        metrics = {}
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

### 6. Update `generate_forecast_answer()`

**BEFORE**:
```python
def generate_forecast_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for forecast-related questions"""
    forecast_new = context.get("forecastNew", 0)
    forecast_old = context.get("forecastOld", 0)
    delta = context.get("trendDelta", 0)
    trend = context.get("trendDirection", "Stable")
    
    pct_change = (delta / forecast_old * 100) if forecast_old > 0 else 0
    
    answer = f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. "
    answer += f"Change: {delta:+,.0f} units ({pct_change:+.1f}%). Trend: {trend}."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "forecastNew": forecast_new,
            "forecastOld": forecast_old,
            "trendDelta": delta,
            "trendDirection": trend,
            "percentChange": pct_change
        }
    }
```

**AFTER**:
```python
def generate_forecast_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for forecast-related questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    # Get quantity changes (scoped if location provided)
    metrics = get_quantity_changes(detail_records, location_id=location_id)
    
    # Build generative response
    answer = build_contextual_response(
        question,
        metrics,
        "forecast"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

### 7. Update `generate_risk_answer()`

**BEFORE**:
```python
def generate_risk_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for risk-related questions"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    # More detailed answer
    answer = f"Risk level is {level}. "
    answer += f"Highest risk type: {highest}. "
    answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
    
    # Add breakdown if available
    breakdown = risk_summary.get("riskBreakdown", {})
    if breakdown:
        answer += f"Breakdown: "
        for risk_type, count in breakdown.items():
            answer += f"{risk_type} ({count}), "
        answer = answer.rstrip(", ") + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "riskLevel": level,
            "highestRiskLevel": highest,
            "highRiskCount": high_risk_count,
            "totalRecords": total,
            "percentHighRisk": pct_high_risk,
            "riskBreakdown": breakdown
        }
    }
```

**AFTER**:
```python
def generate_risk_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for risk-related questions"""
    
    # Build generative response
    answer = build_contextual_response(
        "What are the risks?",
        context,
        "risk"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": context
    }
```

### 8. Update `generate_impact_answer()`

**BEFORE**:
```python
def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact-related questions"""
    # ... existing logic
```

**AFTER**:
```python
def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact-related questions"""
    
    # Get scoped metrics
    metrics = compute_scoped_metrics(detail_records)
    
    # Build generative response
    answer = build_contextual_response(
        "What is the impact?",
        metrics,
        "impact"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": metrics
    }
```

---

## Step 3: Update Health Answer Function

**BEFORE**:
```python
def generate_health_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for health-related questions"""
    health = context.get("planningHealth", 0)
    status = context.get("status", "Unknown")
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    
    answer = f"Planning health is {health}/100 ({status}). {changed:,} of {total:,} records have changed ({pct_changed:.1f}%). "
    answer += f"Primary drivers: Design changes ({design_changes}), Supplier changes ({supplier_changes})."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "planningHealth": health,
            "status": status,
            "changedRecordCount": changed,
            "totalRecords": total,
            "designChanges": design_changes,
            "supplierChanges": supplier_changes
        }
    }
```

**AFTER**:
```python
def generate_health_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for health-related questions"""
    
    # Build generative response
    answer = build_contextual_response(
        "What's the planning health?",
        context,
        "health"
    )
    
    return {
        "answer": answer,
        "supportingMetrics": context
    }
```

---

## Step 4: Testing

After making these changes, test with:

```bash
cd planning_intelligence
python test_responses_fixed.py
```

Expected: All 46 prompts should work with improved, natural responses.

---

## Validation Checklist

- [ ] All imports added to `function_app.py`
- [ ] All 8 answer functions updated
- [ ] No syntax errors
- [ ] Tests pass with 100% success rate
- [ ] Responses are natural and contextual
- [ ] Scoped queries return correct values
- [ ] Design queries filter correctly
- [ ] Comparison queries show differences
- [ ] ROJ logic works
- [ ] Ready for deployment

---

## Rollback Plan

If issues occur:

1. Keep a backup of original `function_app.py`
2. Revert to backup
3. Investigate issue
4. Re-apply changes incrementally

---

## Support

For issues:
1. Check test results in `scoped_fixes_validation.json`
2. Review error logs
3. Verify blob data is loading correctly
4. Ensure all imports are available
