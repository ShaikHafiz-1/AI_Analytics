# Full Testing Checklist - All 44 Prompts

## Instructions

1. **Restart the backend** (code fix applied)
2. **Test each prompt** in order
3. **Mark PASS/FAIL** based on whether response includes data/metrics
4. **Note any issues** in the "Notes" column

---

## Supplier Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 1 | List suppliers for AVC11_F01C01 | Supplier list with metrics | [ ] PASS / [ ] FAIL | |
| 2 | List suppliers for LOC001 | Supplier list with metrics | [ ] PASS / [ ] FAIL | |
| 3 | Which suppliers at AVC11_F01C01 have design changes? | Filtered supplier list | [ ] PASS / [ ] FAIL | |
| 4 | Which supplier has the most impact? | Top supplier with metrics | [ ] PASS / [ ] FAIL | |

---

## Comparison Queries (3)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 5 | Compare LOC001 vs LOC002 | Side-by-side comparison table | [ ] PASS / [ ] FAIL | |
| 6 | Compare AVC11_F01C01 vs LOC001 | Side-by-side comparison table | [ ] PASS / [ ] FAIL | |
| 7 | Compare PUMP vs VALVE | Material group comparison | [ ] PASS / [ ] FAIL | |

---

## Record Detail Queries (3)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 8 | What changed for MAT-001? | Current vs previous values | [ ] PASS / [ ] FAIL | |
| 9 | What changed for MAT-001 at AVC11_F01C01? | Location-specific record detail | [ ] PASS / [ ] FAIL | |
| 10 | Show current vs previous for MAT-001 | Current vs previous comparison | [ ] PASS / [ ] FAIL | |

---

## Root Cause Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 11 | Why is AVC11_F01C01 risky? | Risk analysis with drivers | [ ] PASS / [ ] FAIL | |
| 12 | Why is LOC001 not risky? | Explanation of low risk | [ ] PASS / [ ] FAIL | |
| 13 | Why is planning health critical? | Health score analysis | [ ] PASS / [ ] FAIL | |
| 14 | What is driving the risk? | Risk drivers analysis | [ ] PASS / [ ] FAIL | |

---

## Traceability Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 15 | Show top contributing records | List of high-impact records | [ ] PASS / [ ] FAIL | |
| 16 | Which records have the most impact? | Top records with metrics | [ ] PASS / [ ] FAIL | |
| 17 | Show records with design changes | Filtered design change records | [ ] PASS / [ ] FAIL | |
| 18 | Which records are highest risk? | High-risk records list | [ ] PASS / [ ] FAIL | |

---

## Location Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 19 | Which locations have the most changes? | Location ranking by changes | [ ] PASS / [ ] FAIL | |
| 20 | Which locations need immediate attention? | High-risk locations | [ ] PASS / [ ] FAIL | |
| 21 | What changed at LOC001? | Summary of changes at location | [ ] PASS / [ ] FAIL | |
| 22 | Which locations are change hotspots? | Locations with high change rate | [ ] PASS / [ ] FAIL | |

---

## Material Group Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 23 | Which material groups changed the most? | Material group ranking | [ ] PASS / [ ] FAIL | |
| 24 | What changed in PUMP? | Changes in PUMP material group | [ ] PASS / [ ] FAIL | |
| 25 | Which material groups have design changes? | Filtered material groups | [ ] PASS / [ ] FAIL | |
| 26 | Which material groups are most impacted? | Material groups by impact | [ ] PASS / [ ] FAIL | |

---

## Forecast/Demand Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 27 | Why did forecast increase by +50,980? | Forecast analysis | [ ] PASS / [ ] FAIL | |
| 28 | Where are we seeing new demand surges? | Locations with demand increases | [ ] PASS / [ ] FAIL | |
| 29 | Is this demand-driven or design-driven? | Analysis of change drivers | [ ] PASS / [ ] FAIL | |
| 30 | Show forecast trends | Forecast trend analysis | [ ] PASS / [ ] FAIL | |

---

## Design/BOD Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 31 | Which materials have BOD changes? | List of BOD change records | [ ] PASS / [ ] FAIL | |
| 32 | Which materials have Form Factor changes? | List of form factor change records | [ ] PASS / [ ] FAIL | |
| 33 | Any design changes at AVC11_F01C01? | Design changes at location | [ ] PASS / [ ] FAIL | |
| 34 | Which supplier has the most design changes? | Supplier with design changes | [ ] PASS / [ ] FAIL | |

---

## Schedule/ROJ Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 35 | Which locations have ROJ delays? | Locations with ROJ changes | [ ] PASS / [ ] FAIL | |
| 36 | Which supplier is failing to meet ROJ dates? | Supplier with ROJ issues | [ ] PASS / [ ] FAIL | |
| 37 | Are there ROJ delays at LOC001? | ROJ status at location | [ ] PASS / [ ] FAIL | |
| 38 | Show schedule changes | Schedule change analysis | [ ] PASS / [ ] FAIL | |

---

## Health/Status Queries (4)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 39 | What is the current planning health? | Health score and status | [ ] PASS / [ ] FAIL | |
| 40 | Why is planning health at 37/100? | Health analysis | [ ] PASS / [ ] FAIL | |
| 41 | What is the risk level? | Risk summary | [ ] PASS / [ ] FAIL | |
| 42 | Show KPI summary | KPI metrics | [ ] PASS / [ ] FAIL | |

---

## Action/Recommendation Queries (2)

| # | Prompt | Expected | Status | Notes |
|---|--------|----------|--------|-------|
| 43 | What are the top planner actions? | Recommended actions | [ ] PASS / [ ] FAIL | |
| 44 | What should be done for AVC11_F01C01? | Location-specific actions | [ ] PASS / [ ] FAIL | |

---

## Summary

**Total Prompts**: 44
**Passed**: _____ / 44
**Failed**: _____ / 44
**Pass Rate**: _____%

---

## Pass Criteria

✓ **PASS** if:
- Response is relevant to the query
- Response includes data/metrics
- Response time < 500ms
- No errors in logs

✗ **FAIL** if:
- Response is generic/fallback
- Response has no data
- Response time > 500ms
- Errors in logs

---

## Notes Section

Use this space to document any issues found:

```
Issue 1: [Prompt number] - [Description]
Issue 2: [Prompt number] - [Description]
Issue 3: [Prompt number] - [Description]
```

---

## Testing Steps

1. **Restart backend** with the regex fix
2. **Open Copilot** in the UI
3. **Copy each prompt** from above
4. **Paste into chat** and wait for response
5. **Mark PASS/FAIL** based on criteria
6. **Note any issues** in the Notes section
7. **Calculate pass rate** at the end

---

## Expected Results

- **Supplier Queries**: Should return supplier lists with metrics
- **Comparison Queries**: Should return side-by-side comparison tables
- **Record Detail Queries**: Should return current vs previous values
- **Root Cause Queries**: Should return analysis with drivers
- **Traceability Queries**: Should return top records with impact
- **Location Queries**: Should return location-specific analysis
- **Material Group Queries**: Should return material group analysis
- **Forecast Queries**: Should return forecast analysis
- **Design/BOD Queries**: Should return design change details
- **Schedule/ROJ Queries**: Should return schedule analysis
- **Health Queries**: Should return health metrics
- **Action Queries**: Should return recommended actions

---

## Success Criteria

✓ **SUCCESS** if:
- Pass rate >= 90% (40+ out of 44)
- All critical query types work (Supplier, Comparison, Root Cause)
- No major errors in logs
- Response times < 500ms

✗ **NEEDS WORK** if:
- Pass rate < 90%
- Critical query types fail
- Errors in logs
- Response times > 500ms

---

## Next Steps

1. Complete the testing checklist
2. Document any failures
3. Report pass rate
4. Fix any issues found
5. Re-test failed prompts

---

## Notes

- Use exact location/material IDs from your data
- If a prompt doesn't work, try a similar one
- Check backend logs for DEBUG messages
- All prompts should work with the regex fix!
