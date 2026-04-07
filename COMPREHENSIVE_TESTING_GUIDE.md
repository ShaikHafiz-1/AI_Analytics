# Comprehensive Testing Guide - All Query Types

## Overview

Now that the fix is working, test all query types to ensure the system works end-to-end.

---

## Query Types to Test

### 1. Supplier Queries ✓ (Already Working)

**Query**: "List suppliers for AVC11_F01C01"
**Expected**: Supplier list with metrics
**Status**: ✓ WORKING

**Query**: "List suppliers for LOC001"
**Expected**: Supplier list with metrics
**Status**: Test this

**Query**: "Which suppliers at AVC11_F01C01 have design changes?"
**Expected**: Filtered supplier list with design change details
**Status**: Test this

---

### 2. Comparison Queries

**Query**: "Compare LOC001 vs LOC002"
**Expected**: Side-by-side comparison of metrics
```
📊 Comparison: LOC001 vs LOC002

LOC001:
  • Total Records: X
  • Changed: Y
  • Forecast Delta: +Z
  • Design Changes: A
  • Supplier Changes: B

LOC002:
  • Total Records: X
  • Changed: Y
  • Forecast Delta: +Z
  • Design Changes: A
  • Supplier Changes: B
```
**Status**: Test this

**Query**: "Compare PUMP vs VALVE"
**Expected**: Material group comparison
**Status**: Test this

**Query**: "Compare MAT-001 vs MAT-002"
**Expected**: Material comparison
**Status**: Test this

---

### 3. Record Detail Queries

**Query**: "What changed for MAT-001?"
**Expected**: Current vs previous values
```
📋 Record Comparison: MAT-001

Current:
  • Forecast: X
  • ROJ: YYYY-MM-DD
  • Supplier: SUP-A
  • BOD: ABC
  • Form Factor: XYZ

Previous:
  • Forecast: X
  • ROJ: YYYY-MM-DD
  • Supplier: SUP-B
  • BOD: ABC
  • Form Factor: XYZ

Changes:
  • Forecast Delta: +100
  • Supplier Changed: Yes
  • Design Changed: No
```
**Status**: Test this

**Query**: "What changed for MAT-001 at AVC11_F01C01?"
**Expected**: Location-specific record detail
**Status**: Test this

---

### 4. Root Cause Queries

**Query**: "Why is AVC11_F01C01 risky?"
**Expected**: Risk analysis with drivers
```
⚠️ Risk Analysis: AVC11_F01C01

Risk Level: HIGH
Primary Drivers:
  • Supplier Changes: 5 records
  • Design Changes: 3 records
  • Forecast Increase: +450 units
  • ROJ Delays: 2 records

Affected Records: 15
High Risk Count: 8

Recommended Actions:
  • Validate supplier transitions
  • Review design changes with engineering
  • Confirm capacity for increased demand
```
**Status**: Test this

**Query**: "Why is LOC001 not risky?"
**Expected**: Explanation of low risk
**Status**: Test this

**Query**: "Why is planning health critical?"
**Expected**: Health score analysis
**Status**: Test this

---

### 5. Traceability Queries

**Query**: "Show top contributing records"
**Expected**: List of records with highest impact
```
📊 Top Contributing Records:

1. MAT-001 at LOC001
   • Forecast Delta: +500
   • Risk Level: HIGH
   • Changes: Qty, Supplier, Design

2. MAT-002 at AVC11_F01C01
   • Forecast Delta: +300
   • Risk Level: MEDIUM
   • Changes: Qty, ROJ

3. MAT-003 at LOC002
   • Forecast Delta: +200
   • Risk Level: LOW
   • Changes: Qty
```
**Status**: Test this

**Query**: "Which records have the most impact?"
**Expected**: Same as above
**Status**: Test this

**Query**: "Show records with design changes"
**Expected**: Filtered list of design change records
**Status**: Test this

---

### 6. Location Queries

**Query**: "Which locations have the most changes?"
**Expected**: Location ranking by change count
**Status**: Test this

**Query**: "Which locations need immediate attention?"
**Expected**: High-risk locations
**Status**: Test this

**Query**: "What changed at LOC001?"
**Expected**: Summary of changes at that location
**Status**: Test this

---

### 7. Material Group Queries

**Query**: "Which material groups changed the most?"
**Expected**: Material group ranking
**Status**: Test this

**Query**: "What changed in PUMP?"
**Expected**: Changes in PUMP material group
**Status**: Test this

**Query**: "Which material groups have design changes?"
**Expected**: Filtered material groups
**Status**: Test this

---

### 8. Forecast/Demand Queries

**Query**: "Why did forecast increase by +50,980?"
**Expected**: Forecast analysis
**Status**: Test this

**Query**: "Where are we seeing new demand surges?"
**Expected**: Locations with demand increases
**Status**: Test this

**Query**: "Is this demand-driven or design-driven?"
**Expected**: Analysis of change drivers
**Status**: Test this

---

### 9. Design/BOD Queries

**Query**: "Which materials have BOD changes?"
**Expected**: List of BOD change records
**Status**: Test this

**Query**: "Which materials have Form Factor changes?"
**Expected**: List of form factor change records
**Status**: Test this

**Query**: "Any design changes at AVC11_F01C01?"
**Expected**: Design changes at that location
**Status**: Test this

---

### 10. Schedule/ROJ Queries

**Query**: "Which locations have ROJ delays?"
**Expected**: Locations with ROJ changes
**Status**: Test this

**Query**: "Which supplier is failing to meet ROJ dates?"
**Expected**: Supplier with ROJ issues
**Status**: Test this

**Query**: "Are there ROJ delays at LOC001?"
**Expected**: ROJ status at that location
**Status**: Test this

---

### 11. Health/Status Queries

**Query**: "What is the current planning health?"
**Expected**: Health score and status
**Status**: Test this

**Query**: "Why is planning health at 37/100?"
**Expected**: Health analysis
**Status**: Test this

**Query**: "What is the risk level?"
**Expected**: Risk summary
**Status**: Test this

---

### 12. Action/Recommendation Queries

**Query**: "What are the top planner actions?"
**Expected**: Recommended actions
**Status**: Test this

**Query**: "What should be done for AVC11_F01C01?"
**Expected**: Location-specific actions
**Status**: Test this

**Query**: "Which issues are likely to escalate?"
**Expected**: Escalation risk analysis
**Status**: Test this

---

## Testing Procedure

### For Each Query:

1. **Open the Copilot** (Ask Copilot button)
2. **Type the query** exactly as shown
3. **Wait for response** (should be < 500ms)
4. **Check the response**:
   - Is it relevant to the query?
   - Does it include data/metrics?
   - Are there no errors?
5. **Check the logs** (backend):
   - Look for DEBUG messages
   - Verify detailRecords count > 0
   - No exceptions or errors
6. **Mark as PASS or FAIL**

---

## Expected Results

### ✓ PASS Criteria
- Response is relevant to the query
- Response includes data/metrics
- Response time < 500ms
- No errors in logs
- DEBUG logs show detailRecords > 0

### ✗ FAIL Criteria
- Response is generic/fallback
- Response has no data
- Response time > 500ms
- Errors in logs
- DEBUG logs show detailRecords = 0

---

## Testing Checklist

### Supplier Queries
- [ ] "List suppliers for AVC11_F01C01" - PASS
- [ ] "List suppliers for LOC001" - PASS
- [ ] "Which suppliers at AVC11_F01C01 have design changes?" - PASS

### Comparison Queries
- [ ] "Compare LOC001 vs LOC002" - PASS
- [ ] "Compare PUMP vs VALVE" - PASS
- [ ] "Compare MAT-001 vs MAT-002" - PASS

### Record Detail Queries
- [ ] "What changed for MAT-001?" - PASS
- [ ] "What changed for MAT-001 at AVC11_F01C01?" - PASS

### Root Cause Queries
- [ ] "Why is AVC11_F01C01 risky?" - PASS
- [ ] "Why is LOC001 not risky?" - PASS
- [ ] "Why is planning health critical?" - PASS

### Traceability Queries
- [ ] "Show top contributing records" - PASS
- [ ] "Which records have the most impact?" - PASS
- [ ] "Show records with design changes" - PASS

### Location Queries
- [ ] "Which locations have the most changes?" - PASS
- [ ] "Which locations need immediate attention?" - PASS
- [ ] "What changed at LOC001?" - PASS

### Material Group Queries
- [ ] "Which material groups changed the most?" - PASS
- [ ] "What changed in PUMP?" - PASS
- [ ] "Which material groups have design changes?" - PASS

### Forecast/Demand Queries
- [ ] "Why did forecast increase by +50,980?" - PASS
- [ ] "Where are we seeing new demand surges?" - PASS
- [ ] "Is this demand-driven or design-driven?" - PASS

### Design/BOD Queries
- [ ] "Which materials have BOD changes?" - PASS
- [ ] "Which materials have Form Factor changes?" - PASS
- [ ] "Any design changes at AVC11_F01C01?" - PASS

### Schedule/ROJ Queries
- [ ] "Which locations have ROJ delays?" - PASS
- [ ] "Which supplier is failing to meet ROJ dates?" - PASS
- [ ] "Are there ROJ delays at LOC001?" - PASS

### Health/Status Queries
- [ ] "What is the current planning health?" - PASS
- [ ] "Why is planning health at 37/100?" - PASS
- [ ] "What is the risk level?" - PASS

### Action/Recommendation Queries
- [ ] "What are the top planner actions?" - PASS
- [ ] "What should be done for AVC11_F01C01?" - PASS
- [ ] "Which issues are likely to escalate?" - PASS

---

## Troubleshooting

### If a Query Returns "No supplier information found"
1. Check the logs for DEBUG messages
2. Verify detailRecords count > 0
3. Check if the location/supplier exists in the data
4. Try a different location

### If a Query Returns Generic/Fallback Answer
1. Check the logs for errors
2. Verify the query is clear and specific
3. Try rephrasing the query
4. Check if the data exists for that query

### If Response Time is Slow (> 500ms)
1. Check backend logs for performance issues
2. Verify no errors in logs
3. Try a simpler query
4. Check system resources

### If Errors Appear in Logs
1. Check the error message
2. Look for stack traces
3. Verify all files are updated
4. Restart both frontend and backend

---

## Success Criteria

✓ All 40+ queries return relevant responses
✓ All responses include data/metrics
✓ All response times < 500ms
✓ No errors in logs
✓ DEBUG logs show detailRecords > 0 for all queries

---

## Next Steps

1. **Run through all queries** using the checklist above
2. **Mark PASS/FAIL** for each query
3. **Document any failures** with query and response
4. **Report results** with pass rate

---

## Summary

The fix enables:
✓ Supplier queries for ANY location
✓ Comparison queries for ANY entities
✓ Record detail queries for ANY material
✓ Root cause analysis for ANY location
✓ Traceability queries for ALL records
✓ All other query types

All queries should now work correctly with the detailRecords fix!
