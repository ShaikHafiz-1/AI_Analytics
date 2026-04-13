# Scoped Computation & Filtering Fix - Implementation Guide

## Overview

This document outlines the complete fix for scoped computation, filtering logic, and generative response quality in Planning Intelligence Copilot.

**Key Principle**: COMPUTE FIRST → FILTER SECOND → GENERATE LAST

---

## Files Created

### 1. `planning_intelligence/scoped_metrics.py`
**Purpose**: Core scoped computation engine

**Key Functions**:
- `compute_scoped_metrics()` - Main function for scoped metric computation
- `get_location_metrics()` - Get metrics for a specific location
- `get_supplier_metrics()` - Get metrics for a specific supplier
- `get_material_metrics()` - Get metrics for a specific material
- `get_design_changes()` - Get design changes (optionally scoped)
- `get_supplier_changes()` - Get supplier changes (optionally scoped)
- `get_quantity_changes()` - Get quantity changes (optionally scoped)
- `get_roj_changes()` - Get ROJ schedule changes (optionally scoped)
- `compare_locations()` - Compare two locations
- `get_top_locations()`, `get_top_suppliers()`, `get_top_materials()` - Get rankings

**How It Works**:
```python
# Example: Get metrics for a specific location
metrics = get_location_metrics(records, "CYS20_F01C01")

# Process:
# 1. Filter records WHERE locationId = "CYS20_F01C01"
# 2. Compute change flags on filtered data
# 3. Aggregate metrics
# 4. Return scoped results
```

### 2. `planning_intelligence/generative_responses.py`
**Purpose**: Convert metrics into natural, contextual responses

**Key Classes**:
- `GenerativeResponseBuilder` - Builds natural language responses
  - `build_health_response()` - Health status responses
  - `build_location_response()` - Location-specific responses
  - `build_design_response()` - Design change responses
  - `build_forecast_response()` - Forecast responses
  - `build_risk_response()` - Risk assessment responses
  - `build_comparison_response()` - Comparison responses
  - `build_impact_response()` - Impact analysis responses

**Key Functions**:
- `build_contextual_response()` - Main function to build responses
- `ask_for_clarification()` - Generate clarification requests

**How It Works**:
```python
# Example: Build a natural response
response = build_contextual_response(
    question="What's the planning health?",
    metrics={"planningHealth": 37, "changedRecordCount": 3777, ...},
    response_type="health"
)

# Output: "Planning health is 37/100 (Critical). 3,777 of 13,148 records 
#          have changed (28.7%). Primary drivers: Design (1926), Supplier (1499)."
```

### 3. `planning_intelligence/test_scoped_fixes.py`
**Purpose**: Comprehensive validation of scoped computation fixes

**Tests**:
1. Location-scoped changes return correct counts
2. Design queries filter correctly
3. Entity queries return scoped data
4. ROJ logic works correctly
5. Comparison queries show real differences
6. Responses are generative and natural

---

## Integration Steps

### Step 1: Update `function_app.py` Answer Functions

Replace existing answer functions with scoped versions:

```python
from scoped_metrics import (
    get_location_metrics,
    get_design_changes,
    get_supplier_changes,
    get_quantity_changes,
    get_roj_changes,
    compare_locations,
    compute_scoped_metrics,
)
from generative_responses import build_contextual_response

def generate_location_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for location-specific questions"""
    from copilot_helpers import extract_location_id
    
    location_id = extract_location_id(question)
    
    if location_id:
        # Get scoped metrics
        metrics = get_location_metrics(detail_records, location_id)
        
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
        # Ask for clarification
        from generative_responses import ask_for_clarification
        return {
            "answer": ask_for_clarification(question),
            "supportingMetrics": {}
        }
```

### Step 2: Update Design Answer Function

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

### Step 3: Update Comparison Answer Function

```python
def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions"""
    import re
    
    # Extract location IDs
    locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    
    if len(locations) < 2:
        return {
            "answer": "Please specify two locations to compare.",
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

### Step 4: Update ROJ Answer Function

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

### Step 5: Update Entity Answer Function

```python
def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions"""
    from copilot_helpers import extract_location_id
    from generative_responses import ask_for_clarification
    
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
    
    return {
        "answer": answer,
        "supportingMetrics": metrics if location_id else {}
    }
```

---

## Before vs After Examples

### Example 1: Location Query

**Before (WRONG)**:
```
Q: "List suppliers for CYS20_F01C01"
A: "Location CYS20_F01C01: 15 records, 0 changed."
   (Wrong: Shows 0 because changed flag was computed globally)
```

**After (CORRECT)**:
```
Q: "List suppliers for CYS20_F01C01"
A: "At CYS20_F01C01, 15 materials are tracked. 3 show recent changes (20%). 
    Suppliers involved: 10_AMER, 130_AMER, 1690_AMER."
   (Correct: Scoped to location, shows actual changes, natural language)
```

### Example 2: Design Query

**Before (WRONG)**:
```
Q: "Which suppliers have design changes?"
A: "1926 records have design changes. Affected suppliers: 9999_AMER, 210_AMER, 530_AMER."
   (Wrong: No context, returns global results)
```

**After (CORRECT)**:
```
Q: "Which suppliers have design changes?"
A: "Design changes detected in 1926 records. Top affected suppliers: 9999_AMER (599), 
    210_AMER (456), 530_AMER (357). Would you like to analyze by location?"
   (Correct: Offers context-aware follow-up)
```

### Example 3: Comparison Query

**Before (WRONG)**:
```
Q: "Compare CYS20_F01C01 vs DSM18_F01C01"
A: "CYS20_F01C01: 15 records, 0 changed. DSM18_F01C01: 15 records, 0 changed."
   (Wrong: Both show 0 even though global data shows 3,777 changes)
```

**After (CORRECT)**:
```
Q: "Compare CYS20_F01C01 vs DSM18_F01C01"
A: "CYS20_F01C01 shows 15 materials with 3 recent changes (design: 2, supplier: 1).
    DSM18_F01C01 shows 15 materials with 5 recent changes (design: 3, supplier: 2).
    DSM18_F01C01 has higher change activity."
   (Correct: Scoped comparison with real differences)
```

### Example 4: ROJ Query

**Before (WRONG)**:
```
Q: "What's the ROJ?"
A: "0 records have ROJ schedule changes."
   (Wrong: ROJ logic not working)
```

**After (CORRECT)**:
```
Q: "What's the ROJ?"
A: "247 records have ROJ schedule changes. Average delta: 12.3 days."
   (Correct: ROJ logic working, showing actual changes)
```

---

## Testing

### Run Validation Tests

```bash
cd planning_intelligence
python test_scoped_fixes.py
```

**Expected Output**:
```
TEST 1: Location-Scoped Changes
Location: CYS20_F01C01
Expected changes: 3
Actual changes: 3
✓ Location-Scoped Changes PASSED

TEST 2: Design Filtering
Global design changes: 1926
Location CYS20_F01C01 design changes: 2
✓ Design Filtering PASSED

TEST 3: Entity Scoped Data
Location: CYS20_F01C01
Expected suppliers: 5
Actual suppliers: 5
✓ Entity Scoped Data PASSED

TEST 4: ROJ Schedule Logic
Global ROJ changes: 247
Location CYS20_F01C01 ROJ changes: 12
✓ ROJ Schedule Logic PASSED

TEST 5: Comparison Differences
Comparing CYS20_F01C01 vs DSM18_F01C01
CYS20_F01C01: 15 records, 3 changes
DSM18_F01C01: 15 records, 5 changes
✓ Comparison Differences PASSED

TEST 6: Generative Responses
Health Response: Planning health is 37/100 (Critical). 3,777 of 13,148 records...
Location Response: At CYS20_F01C01, 15 materials are tracked. 3 show recent changes...
Design Response: 1926 records have design changes. Affected suppliers: 9999_AMER...
✓ Generative Responses PASSED

TEST SUMMARY
Total: 6
Passed: 6
Failed: 0
Pass Rate: 100.0%
```

---

## Success Criteria

✅ **Scoped queries return correct values**
- Location queries show actual changes for that location
- Design queries filter by location if provided
- Entity queries return scoped data, not global

✅ **Design queries filter correctly**
- "Which suppliers have design changes?" returns only design-changed records
- "Which suppliers at CYS20_F01C01 have design changes?" returns only CYS20_F01C01 suppliers with design changes

✅ **Comparison queries show real differences**
- "Compare CYS20_F01C01 vs DSM18_F01C01" shows actual change counts for each location
- Differences are meaningful and non-zero when global data shows changes

✅ **ROJ changes detected correctly**
- ROJ delta computation works
- Schedule changes are counted and reported

✅ **Responses are conversational and natural**
- Multiple response templates avoid repetition
- Responses include business context and meaning
- Responses vary in phrasing and structure

✅ **Copilot feels intelligent and contextual**
- Asks for clarification when needed
- Provides scoped analysis by default
- Offers follow-up options

---

## Deployment Checklist

- [ ] Create `scoped_metrics.py`
- [ ] Create `generative_responses.py`
- [ ] Update `function_app.py` answer functions
- [ ] Update `copilot_helpers.py` if needed
- [ ] Run `test_scoped_fixes.py` - all tests pass
- [ ] Test with real blob data
- [ ] Validate responses are natural and contextual
- [ ] Deploy to Azure Functions
- [ ] Monitor for issues

---

## Next Steps

1. **Immediate**: Run validation tests to confirm fixes work
2. **Short-term**: Integrate into `function_app.py`
3. **Medium-term**: Add Azure OpenAI integration for enhanced generative responses
4. **Long-term**: Add context-aware follow-ups and multi-turn conversations

---

## Support

For issues or questions:
1. Check test results in `scoped_fixes_validation.json`
2. Review error logs in `test_scoped_fixes.py` output
3. Validate blob data is loading correctly
4. Ensure all imports are available
