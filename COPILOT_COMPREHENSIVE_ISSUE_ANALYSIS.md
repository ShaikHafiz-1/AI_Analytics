# Copilot Comprehensive Issue Analysis

## Problem Summary

The Copilot is returning irrelevant generic answers for 40+ prompts because:

1. **Missing Entity Question Handler** - Questions about suppliers, materials, locations are classified as "entity" but there's no `generate_entity_answer()` function
2. **Missing Comparison Handler** - Questions like "Compare X vs Y" have no handler
3. **Missing Impact Handler** - Questions like "What is the impact?" have no handler
4. **No Location/Supplier Filtering** - Questions with specific location IDs (e.g., "CYS20_F01C01") aren't being filtered to that location

---

## Current Question Classification

The `classify_question()` function categorizes questions into:
- ✅ `health` - Has handler: `generate_health_answer()`
- ✅ `forecast` - Has handler: `generate_forecast_answer()`
- ✅ `risk` - Has handler: `generate_risk_answer()`
- ✅ `change` - Has handler: `generate_change_answer()`
- ❌ `entity` - **NO HANDLER** - Falls back to generic answer
- ❌ `comparison` - **NO HANDLER** - Falls back to generic answer
- ❌ `impact` - **NO HANDLER** - Falls back to generic answer
- ✅ `general` - Has handler: `generate_general_answer()`

---

## Problematic Questions & Root Causes

### 1. Entity Questions (Suppliers, Materials, Locations)

**Questions**:
- "List suppliers for CYS20_F01C01"
- "Which materials are affected?"
- "Which suppliers at CYS20_F01C01 have design changes?"

**Current Behavior**: Classified as "entity" → Falls through to generic answer
**Expected Behavior**: Should return filtered list of suppliers/materials for that location

**Root Cause**: 
- No `generate_entity_answer()` function
- No location/supplier filtering logic
- No extraction of location ID from question

---

### 2. Comparison Questions

**Questions**:
- "Compare CYS20_F01C01 vs DSM18_F01C01"

**Current Behavior**: Classified as "general" → Returns generic health answer
**Expected Behavior**: Should compare metrics between two locations

**Root Cause**:
- No comparison classification in `classify_question()`
- No `generate_comparison_answer()` function
- No location extraction logic

---

### 3. Impact Questions

**Questions**:
- "What is the impact?"
- "Which supplier has the most impact?"

**Current Behavior**: Classified as "general" → Returns generic health answer
**Expected Behavior**: Should return impact analysis (which suppliers/materials have most changes)

**Root Cause**:
- No impact classification in `classify_question()`
- No `generate_impact_answer()` function

---

## Data Structure Analysis

### Available Data in Context

From `planning_dashboard_v2` endpoint, the context includes:

```python
{
    "planningHealth": 37,
    "status": "Critical",
    "detailRecords": [
        {
            "locationId": "CYS20_F01C01",
            "materialGroup": "ABC123",
            "supplier": "Supplier A",
            "changed": True,
            "changeType": "Design",  # or "Supplier", "Quantity"
            ...
        },
        ...
    ],
    "riskSummary": {
        "level": "High",
        "highestRiskLevel": "Design + Supplier",
        "highRiskCount": 1200,
        "riskBreakdown": {
            "Design": 1926,
            "Supplier": 1499,
            "Quantity": 4725
        },
        "designChangedCount": 1926,
        "supplierChangedCount": 1499,
        "quantityChangedCount": 4725
    }
}
```

### What We Can Extract

From `detailRecords`, we can:
- Filter by `locationId` (e.g., "CYS20_F01C01")
- Filter by `materialGroup`
- Filter by `supplier`
- Filter by `changeType` (Design, Supplier, Quantity)
- Count unique suppliers per location
- Count unique materials per location
- Calculate impact (which has most changes)

---

## Solution Architecture

### Step 1: Enhance Question Classification

Add new question types to `classify_question()`:

```python
def classify_question(question: str) -> str:
    q_lower = question.lower()
    
    # Risk questions - CHECK FIRST
    if any(word in q_lower for word in ["risk", "risks", "risky", "danger", "dangerous", "high-risk", "top risk"]):
        return "risk"
    
    # Health questions
    elif any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "at risk", "planning"]):
        return "health"
    
    # Forecast questions
    elif any(word in q_lower for word in ["forecast", "trend", "delta", "increase", "decrease", "units"]):
        return "forecast"
    
    # Change questions
    elif any(word in q_lower for word in ["change", "changed", "changes", "quantity", "roj"]):
        return "change"
    
    # Comparison questions - NEW
    elif any(word in q_lower for word in ["compare", "vs", "versus", "difference", "between"]):
        return "comparison"
    
    # Impact questions - NEW
    elif any(word in q_lower for word in ["impact", "affected", "effect", "consequence", "most impact"]):
        return "impact"
    
    # Entity questions - LAST (most general)
    elif any(word in q_lower for word in ["list", "supplier", "material", "location", "group", "datacenter", "which"]):
        return "entity"
    
    else:
        return "general"
```

### Step 2: Add Helper Functions

Add utility functions to extract location/supplier/material from questions:

```python
def extract_location_id(question: str) -> Optional[str]:
    """Extract location ID from question (e.g., 'CYS20_F01C01')"""
    import re
    # Pattern: uppercase letters followed by numbers and underscores
    match = re.search(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    return match.group(1) if match else None

def extract_supplier_name(question: str) -> Optional[str]:
    """Extract supplier name from question"""
    # Look for quoted text or common supplier patterns
    import re
    match = re.search(r'"([^"]+)"', question)
    return match.group(1) if match else None

def filter_records_by_location(records: list, location_id: str) -> list:
    """Filter records to specific location"""
    return [r for r in records if r.get("locationId") == location_id]

def filter_records_by_change_type(records: list, change_type: str) -> list:
    """Filter records by change type (Design, Supplier, Quantity)"""
    return [r for r in records if r.get("changeType") == change_type]

def get_unique_suppliers(records: list) -> list:
    """Get unique suppliers from records"""
    suppliers = set()
    for r in records:
        if r.get("supplier"):
            suppliers.add(r.get("supplier"))
    return sorted(list(suppliers))

def get_unique_materials(records: list) -> list:
    """Get unique materials from records"""
    materials = set()
    for r in records:
        if r.get("materialGroup"):
            materials.add(r.get("materialGroup"))
    return sorted(list(materials))

def get_impact_ranking(records: list) -> dict:
    """Get suppliers/materials ranked by impact (number of changes)"""
    supplier_impact = {}
    material_impact = {}
    
    for r in records:
        if r.get("changed"):
            supplier = r.get("supplier", "Unknown")
            material = r.get("materialGroup", "Unknown")
            
            supplier_impact[supplier] = supplier_impact.get(supplier, 0) + 1
            material_impact[material] = material_impact.get(material, 0) + 1
    
    return {
        "suppliers": sorted(supplier_impact.items(), key=lambda x: x[1], reverse=True),
        "materials": sorted(material_impact.items(), key=lambda x: x[1], reverse=True)
    }
```

### Step 3: Add Answer Generators

Add new answer generator functions:

```python
def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions (suppliers, materials, locations)"""
    location_id = extract_location_id(question)
    
    if location_id:
        # Filter to specific location
        location_records = filter_records_by_location(detail_records, location_id)
        if not location_records:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": {"location": location_id, "recordCount": 0}
            }
        
        suppliers = get_unique_suppliers(location_records)
        materials = get_unique_materials(location_records)
        changed = sum(1 for r in location_records if r.get("changed"))
        
        answer = f"Location {location_id}: {len(location_records)} records. "
        answer += f"Suppliers: {', '.join(suppliers[:5])}. "
        answer += f"Materials: {', '.join(materials[:5])}. "
        answer += f"Changed: {changed}."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "location": location_id,
                "recordCount": len(location_records),
                "suppliers": suppliers,
                "materials": materials,
                "changedCount": changed
            }
        }
    else:
        # General entity question
        impact = get_impact_ranking(detail_records)
        top_suppliers = impact["suppliers"][:5]
        top_materials = impact["materials"][:5]
        
        answer = "Top affected suppliers: "
        answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
        answer += "Top affected materials: "
        answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "topSuppliers": top_suppliers,
                "topMaterials": top_materials
            }
        }

def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions"""
    # Extract location IDs from question
    import re
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

def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact questions"""
    impact = get_impact_ranking(detail_records)
    top_suppliers = impact["suppliers"][:3]
    top_materials = impact["materials"][:3]
    
    answer = "Impact analysis: "
    answer += "Top suppliers affected: "
    answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
    answer += "Top materials affected: "
    answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "topSuppliers": top_suppliers,
            "topMaterials": top_materials
        }
    }
```

### Step 4: Update Explain Endpoint

Update the `explain()` function to handle new question types:

```python
# In the explain() function, replace the answer generation section:

if q_type == "health":
    result = generate_health_answer(detail_records, context)
elif q_type == "forecast":
    result = generate_forecast_answer(detail_records, context)
elif q_type == "risk":
    result = generate_risk_answer(detail_records, context)
elif q_type == "change":
    result = generate_change_answer(detail_records, context)
elif q_type == "entity":
    result = generate_entity_answer(detail_records, context, question)  # Pass question
elif q_type == "comparison":
    result = generate_comparison_answer(detail_records, context, question)  # Pass question
elif q_type == "impact":
    result = generate_impact_answer(detail_records, context)
else:
    result = generate_general_answer(detail_records, context)
```

---

## Expected Results After Fix

### Entity Questions

**Q: "List suppliers for CYS20_F01C01"**
- Before: "Planning health is 37/100. 5,927 of 13,148 records have changed..."
- After: "Location CYS20_F01C01: 245 records. Suppliers: Supplier A, Supplier B, Supplier C. Materials: MAT001, MAT002. Changed: 87."

**Q: "Which materials are affected?"**
- Before: "Planning health is 37/100..."
- After: "Top affected materials: MAT001 (1200 changes), MAT002 (950 changes), MAT003 (750 changes)."

### Comparison Questions

**Q: "Compare CYS20_F01C01 vs DSM18_F01C01"**
- Before: "Planning health is 37/100..."
- After: "Comparison: CYS20_F01C01 vs DSM18_F01C01. CYS20_F01C01: 245 records, 87 changed. DSM18_F01C01: 312 records, 125 changed."

### Impact Questions

**Q: "Which supplier has the most impact?"**
- Before: "Planning health is 37/100..."
- After: "Impact analysis: Top suppliers affected: Supplier A (450 changes), Supplier B (380 changes), Supplier C (290 changes)."

---

## Implementation Checklist

- [ ] Add helper functions for location/supplier/material extraction
- [ ] Add helper functions for filtering and ranking
- [ ] Update `classify_question()` to recognize comparison and impact questions
- [ ] Add `generate_entity_answer()` function
- [ ] Add `generate_comparison_answer()` function
- [ ] Add `generate_impact_answer()` function
- [ ] Update `explain()` endpoint to route to new handlers
- [ ] Test with all 40+ prompts
- [ ] Verify no syntax errors
- [ ] Restart backend and test

---

## Files to Modify

- `planning_intelligence/function_app.py` - Add all new functions and update routing

---

## Testing Strategy

After implementation, test with:

1. **Entity questions**: "List suppliers for CYS20_F01C01", "Which materials are affected?"
2. **Comparison questions**: "Compare CYS20_F01C01 vs DSM18_F01C01"
3. **Impact questions**: "Which supplier has the most impact?", "What is the impact?"
4. **Existing questions**: Verify health, forecast, risk, change questions still work
5. **Edge cases**: Invalid location IDs, missing data, etc.

