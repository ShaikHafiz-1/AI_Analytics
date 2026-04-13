# Scoped Computation & Filtering Issues - Root Cause Analysis

## Critical Issues Identified

### 1. **Location-Level Queries Show Changed = 0 Incorrectly**

**Root Cause**: The `changed` flag is computed at normalization time BEFORE filtering. When you filter by location, you're checking if the record's `changed` flag is true, but this flag was computed globally.

**Problem Flow**:
```
1. Record normalized: changed = (qtyChanged OR supplierChanged OR designChanged OR rojChanged)
2. Location filter applied: filter records WHERE locationId = "CYS20_F01C01"
3. Count changed: sum(1 for r in filtered if r.get("changed"))
4. Result: Shows 0 because the record's "changed" flag was computed globally
```

**Why It's Wrong**: A record might have `changed=true` globally, but when filtered to a specific location, we need to recompute if THAT location has changes.

---

### 2. **Design Queries Do Not Filter Results**

**Root Cause**: `generate_design_answer()` calls `get_records_by_change_type(detail_records, "design")` which filters globally, not by the question context.

**Current Logic**:
```python
design_records = get_records_by_change_type(detail_records, "design")
# Returns ALL records with design changes globally
# Does NOT filter by location if question asks "Which suppliers at CYS20_F01C01 have design changes?"
```

**Problem**: Question context (location, supplier, material) is ignored.

---

### 3. **Entity Queries Return Global Data Instead of Scoped Data**

**Root Cause**: `generate_entity_answer()` doesn't extract location/supplier context from the question. It returns top suppliers/materials globally.

**Example**:
- Question: "Which suppliers at CYS20_F01C01 have design changes?"
- Current Response: Top 5 suppliers globally (9999_AMER, 210_AMER, etc.)
- Expected Response: Only suppliers at CYS20_F01C01 with design changes

---

### 4. **ROJ Schedule Logic Not Working**

**Root Cause**: ROJ delta computation happens at normalization, but:
1. Date parsing might fail silently
2. `rojChanged` flag is computed but never used in schedule answer generation
3. `generate_schedule_answer()` doesn't properly filter or compute ROJ changes

**Current Issue**:
```python
# In normalization:
roj_delta = (roj_current_dt - roj_previous_dt).days  # Computed
rojChanged = roj_current != roj_previous  # Flag set

# In generate_schedule_answer():
# But this function doesn't use rojChanged or rojDelta properly
```

---

### 5. **Comparison Queries Return Incorrect Results**

**Root Cause**: Comparison uses the same flawed `changed` flag that was computed globally.

**Example**:
- Compare CYS20_F01C01 vs DSM18_F01C01
- Both show "0 changed" even though global data shows 3,777 changes
- Reason: The `changed` flag was computed globally, not per-location

---

### 6. **Responses Are Not Generative (Too Template-Based)**

**Root Cause**: All responses use simple string templates without:
- Contextual explanation
- Business meaning
- Natural language variation
- Azure OpenAI integration

**Current Pattern**:
```
"Location {location_id}: {len(location_records)} records total, {changed} changed."
```

**Expected Pattern**:
```
"At {location_id}, activity appears stable with {changed} recent changes across 
{len(location_records)} tracked materials. {business_context}."
```

---

## The Core Problem: Compute Order

**Current (WRONG)**:
```
1. Normalize records (compute changed flag GLOBALLY)
2. Filter by location/supplier/material
3. Count changed records (using globally-computed flag)
4. Generate response
```

**Correct Order**:
```
1. Normalize records (compute deltas: qtyDelta, rojDelta, etc.)
2. Filter by location/supplier/material
3. Recompute change flags AFTER filtering
4. Generate response
5. Enhance with generative layer (Azure OpenAI)
```

---

## Solution Architecture

### Phase 1: Fix Scoped Computation
- Create `compute_scoped_metrics()` function
- Compute deltas FIRST (qtyDelta, rojDelta, designChanged, supplierChanged)
- Apply filters SECOND
- Recompute aggregates THIRD

### Phase 2: Fix Filtering Logic
- Update all answer functions to filter BEFORE computing metrics
- Extract context from questions (location, supplier, material)
- Apply filters in correct order

### Phase 3: Fix Design Filtering
- Extract location/supplier context from question
- Filter records by context
- Then filter by design changes
- Return only matching records

### Phase 4: Fix Entity Query Scope
- Detect if question has location/supplier context
- If yes: filter and return scoped results
- If no: ask for clarification or return top-level analysis

### Phase 5: Fix ROJ Logic
- Ensure date parsing works correctly
- Use `rojDelta` and `rojChanged` flags properly
- Count records where `rojChanged = true`

### Phase 6: Fix Comparison Engine
- Filter records for each location independently
- Recompute metrics for each location
- Compare the scoped metrics

### Phase 7: Add Generative Response Layer
- Integrate Azure OpenAI
- Convert metrics into natural language
- Add contextual business meaning
- Vary phrasing to avoid repetition

### Phase 8: Add Context-Aware Responses
- Detect ambiguous queries
- Ask for clarification when needed
- Provide scoped analysis by default

---

## Implementation Priority

1. **CRITICAL**: Fix scoped computation (Phase 1)
2. **CRITICAL**: Fix filtering logic (Phase 2)
3. **HIGH**: Fix design filtering (Phase 3)
4. **HIGH**: Fix comparison engine (Phase 6)
5. **HIGH**: Fix ROJ logic (Phase 5)
6. **MEDIUM**: Add generative layer (Phase 7)
7. **MEDIUM**: Add context-aware responses (Phase 8)

---

## Expected Outcomes

### Before Fix
```
Q: "List suppliers for CYS20_F01C01"
A: "Location CYS20_F01C01: 15 records, 0 changed."
   (Wrong: Shows 0 because changed flag was computed globally)

Q: "Compare CYS20_F01C01 vs DSM18_F01C01"
A: "CYS20_F01C01: 15 records, 0 changed. DSM18_F01C01: 15 records, 0 changed."
   (Wrong: Both show 0 even though global data shows 3,777 changes)

Q: "Which suppliers have design changes?"
A: "9999_AMER, 210_AMER, 530_AMER (global top 3)"
   (Wrong: Ignores location context if provided)
```

### After Fix
```
Q: "List suppliers for CYS20_F01C01"
A: "At CYS20_F01C01, 15 materials are tracked across 5 suppliers. 
    Recent activity shows 3 design changes and 2 supplier transitions. 
    Key suppliers: 10_AMER, 130_AMER, 1690_AMER."
   (Correct: Scoped to location, shows actual changes)

Q: "Compare CYS20_F01C01 vs DSM18_F01C01"
A: "CYS20_F01C01 shows 15 materials with 3 recent changes (design: 2, supplier: 1).
    DSM18_F01C01 shows 15 materials with 5 recent changes (design: 3, supplier: 2).
    DSM18_F01C01 has higher change activity."
   (Correct: Scoped comparison with actual differences)

Q: "Which suppliers have design changes?"
A: "Design changes detected across 8 suppliers. Top affected: 9999_AMER (599 changes),
    210_AMER (456 changes), 530_AMER (357 changes). Would you like to analyze by 
    location or supplier group?"
   (Correct: Global analysis with option to scope)
```

---

## Next Steps

1. Create `compute_scoped_metrics()` function
2. Update all answer functions to use scoped computation
3. Fix filtering logic in each answer function
4. Add generative response layer
5. Test with real blob data
6. Validate scoped results match expected values
