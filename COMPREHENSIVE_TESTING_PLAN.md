# Comprehensive Testing Plan - All 44 Prompts

## Overview

This document provides a systematic testing plan for all 44 query types with detail level enhancements.

## Recent Fixes Applied

1. **Comparison Query AttributeError** - Fixed list handling in `_compute_scoped_metrics()`
2. **Design/Form Factor Query** - Added `design_filter` query type with dedicated handler
3. **Detail Level Support** - Added `detail_level` parameter to responses (summary/detailed/full)

## Testing Instructions

### Setup
1. Restart backend: `func start`
2. Restart frontend: `npm start`
3. Open Copilot in UI
4. Use exact location IDs: `AVC11_F01C01`, `LOC001`, `CMH02_F01C01`

### For Each Prompt
1. Copy prompt from below
2. Paste into Copilot chat
3. Wait for response
4. Mark PASS/FAIL
5. Note any issues

### Detail Level Options

After getting a response, you can ask for more details:
- **Summary**: Basic metrics (default)
- **Detailed**: Add Location ID, Equipment Category, Supplier info
- **Full**: Complete record details with all fields

Example follow-ups:
- "Show more details"
- "Include location IDs"
- "Show all materials"
- "Which suppliers have design changes?"

---

## Test Categories

### 1. Supplier Queries (4)

**Query 1**: List suppliers for AVC11_F01C01
- Expected: Supplier list with record counts, changes, risk
- Detail levels: summary → detailed → full
- Follow-up: "Which suppliers have design changes?"

**Query 2**: List suppliers for LOC001
- Expected: Supplier list for LOC001
- Detail levels: summary → detailed → full
- Follow-up: "Show forecast impact for each supplier"

**Query 3**: Which suppliers at AVC11_F01C01 have design changes?
- Expected: Filtered supplier list (design changes only)
- Detail levels: summary → detailed → full
- Follow-up: "Which materials are affected?"

**Query 4**: Which supplier has the most impact?
- Expected: Top supplier with metrics
- Detail levels: summary → detailed → full
- Follow-up: "Show all materials from this supplier"

---

### 2. Comparison Queries (3)

**Query 5**: Compare LOC001 vs LOC002
- Expected: Side-by-side comparison table
- Metrics: Records, changed, forecast delta, design changes, risk
- Follow-up: "Which location has more design changes?"

**Query 6**: Compare AVC11_F01C01 vs LOC001
- Expected: Side-by-side comparison table
- Metrics: Records, changed, forecast delta, design changes, risk
- Follow-up: "Show top materials in each location"

**Query 7**: Compare PUMP vs VALVE
- Expected: Material group comparison
- Metrics: Records, changed, forecast delta, design changes, risk
- Follow-up: "Which material group has more risk?"

---

### 3. Record Detail Queries (3)

**Query 8**: What changed for MAT-001?
- Expected: Current vs previous values
- Fields: Forecast, ROJ, Supplier date, BOD, Form Factor
- Follow-up: "Show location and supplier for this material"

**Query 9**: What changed for MAT-001 at AVC11_F01C01?
- Expected: Location-specific record detail
- Fields: Current vs previous, location, supplier
- Follow-up: "Show all materials at this location"

**Query 10**: Show current vs previous for MAT-001
- Expected: Current vs previous comparison
- Fields: Forecast, ROJ, Supplier date, BOD, Form Factor
- Follow-up: "Show all changes for this material"

---

### 4. Root Cause Queries (4)

**Query 11**: Why is AVC11_F01C01 risky?
- Expected: Risk analysis with drivers
- Metrics: Changed count, change rate, primary driver
- Follow-up: "Which materials are causing the risk?"

**Query 12**: Why is LOC001 not risky?
- Expected: Explanation of low risk/stability
- Metrics: Changed count, change rate, stability
- Follow-up: "Show all materials at LOC001"

**Query 13**: Why is planning health critical?
- Expected: Health score analysis
- Metrics: Health score, status, risk level
- Follow-up: "What are the top issues?"

**Query 14**: What is driving the risk?
- Expected: Risk drivers analysis
- Metrics: Primary driver, contribution breakdown
- Follow-up: "Which locations have the most risk?"

---

### 5. Traceability Queries (4)

**Query 15**: Show top contributing records
- Expected: List of high-impact records
- Metrics: Location, Material, Forecast delta, Risk
- Follow-up: "Show more details for top record"

**Query 16**: Which records have the most impact?
- Expected: Top records with metrics
- Metrics: Location, Material, Forecast delta, Risk
- Follow-up: "Show all records at this location"

**Query 17**: Show records with design changes
- Expected: Filtered design change records
- Metrics: Location, Material, Design type, Risk
- Follow-up: "Which suppliers have these materials?"

**Query 18**: Which records are highest risk?
- Expected: High-risk records list
- Metrics: Location, Material, Risk level, Drivers
- Follow-up: "Show all records at this location"

---

### 6. Location Queries (4)

**Query 19**: Which locations have the most changes?
- Expected: Location ranking by changes
- Metrics: Location, Changed count, Change rate
- Follow-up: "Show materials at top location"

**Query 20**: Which locations need immediate attention?
- Expected: High-risk locations
- Metrics: Location, Risk level, Changed count
- Follow-up: "Show all materials at this location"

**Query 21**: What changed at LOC001?
- Expected: Summary of changes at location
- Metrics: Changed count, Primary driver, Risk
- Follow-up: "Show all materials at this location"

**Query 22**: Which locations are change hotspots?
- Expected: Locations with high change rate
- Metrics: Location, Change rate, Changed count
- Follow-up: "Show top materials at each location"

---

### 7. Material Group Queries (4)

**Query 23**: Which material groups changed the most?
- Expected: Material group ranking
- Metrics: Group, Changed count, Change rate
- Follow-up: "Show all materials in top group"

**Query 24**: What changed in PUMP?
- Expected: Changes in PUMP material group
- Metrics: Changed count, Primary driver, Risk
- Follow-up: "Show all materials in PUMP"

**Query 25**: Which material groups have design changes?
- Expected: Filtered material groups
- Metrics: Group, Design changes, Changed count
- Follow-up: "Show all materials with design changes"

**Query 26**: Which material groups are most impacted?
- Expected: Material groups by impact
- Metrics: Group, Impact score, Changed count
- Follow-up: "Show top materials in each group"

---

### 8. Forecast/Demand Queries (4)

**Query 27**: Why did forecast increase by +50,980?
- Expected: Forecast analysis
- Metrics: Forecast delta, Drivers, Locations
- Follow-up: "Which materials are driving this?"

**Query 28**: Where are we seeing new demand surges?
- Expected: Locations with demand increases
- Metrics: Location, Forecast delta, Changed count
- Follow-up: "Show all materials at these locations"

**Query 29**: Is this demand-driven or design-driven?
- Expected: Analysis of change drivers
- Metrics: Driver breakdown, Contribution %
- Follow-up: "Which locations have design changes?"

**Query 30**: Show forecast trends
- Expected: Forecast trend analysis
- Metrics: Trend direction, Trend delta, Volatility
- Follow-up: "Which materials are trending up?"

---

### 9. Design/BOD Queries (4)

**Query 31**: Which materials have BOD changes?
- Expected: List of BOD change records
- Metrics: Material, Location, BOD change, Risk
- Detail levels: summary → detailed → full
- Follow-up: "Show suppliers for these materials"

**Query 32**: Which materials have Form Factor changes?
- Expected: List of form factor change records
- Metrics: Material, Location, Form Factor change, Risk
- Detail levels: summary → detailed → full
- Follow-up: "Show locations for these materials"

**Query 33**: Any design changes at AVC11_F01C01?
- Expected: Design changes at location
- Metrics: Changed count, Materials affected, Risk
- Follow-up: "Show all materials with design changes"

**Query 34**: Which supplier has the most design changes?
- Expected: Supplier with design changes
- Metrics: Supplier, Design changes, Materials affected
- Follow-up: "Show all materials from this supplier"

---

### 10. Schedule/ROJ Queries (4)

**Query 35**: Which locations have ROJ delays?
- Expected: Locations with ROJ changes
- Metrics: Location, ROJ changes, Changed count
- Follow-up: "Show all materials with ROJ changes"

**Query 36**: Which supplier is failing to meet ROJ dates?
- Expected: Supplier with ROJ issues
- Metrics: Supplier, ROJ issues, Materials affected
- Follow-up: "Show all materials from this supplier"

**Query 37**: Are there ROJ delays at LOC001?
- Expected: ROJ status at location
- Metrics: ROJ changes, Changed count, Risk
- Follow-up: "Show all materials with ROJ changes"

**Query 38**: Show schedule changes
- Expected: Schedule change analysis
- Metrics: Changed count, Primary driver, Risk
- Follow-up: "Which locations have schedule changes?"

---

### 11. Health/Status Queries (4)

**Query 39**: What is the current planning health?
- Expected: Health score and status
- Metrics: Health score, Status, Risk level
- Follow-up: "Why is health at this level?"

**Query 40**: Why is planning health at 37/100?
- Expected: Health analysis
- Metrics: Health score, Status, Contributing factors
- Follow-up: "What are the top issues?"

**Query 41**: What is the risk level?
- Expected: Risk summary
- Metrics: Risk level, High-risk count, Risk concentration
- Follow-up: "Which locations have high risk?"

**Query 42**: Show KPI summary
- Expected: KPI metrics
- Metrics: Design rate, Supplier reliability, Demand volatility, Schedule stability, Risk concentration
- Follow-up: "Which KPI is most concerning?"

---

### 12. Action/Recommendation Queries (2)

**Query 43**: What are the top planner actions?
- Expected: Recommended actions
- Metrics: Action list, Priority
- Follow-up: "What should I do for location X?"

**Query 44**: What should be done for AVC11_F01C01?
- Expected: Location-specific actions
- Metrics: Action list, Priority, Rationale
- Follow-up: "Show all materials at this location"

---

## Testing Checklist

### Supplier Queries
- [ ] Query 1: List suppliers for AVC11_F01C01
- [ ] Query 2: List suppliers for LOC001
- [ ] Query 3: Which suppliers at AVC11_F01C01 have design changes?
- [ ] Query 4: Which supplier has the most impact?

### Comparison Queries
- [ ] Query 5: Compare LOC001 vs LOC002
- [ ] Query 6: Compare AVC11_F01C01 vs LOC001
- [ ] Query 7: Compare PUMP vs VALVE

### Record Detail Queries
- [ ] Query 8: What changed for MAT-001?
- [ ] Query 9: What changed for MAT-001 at AVC11_F01C01?
- [ ] Query 10: Show current vs previous for MAT-001

### Root Cause Queries
- [ ] Query 11: Why is AVC11_F01C01 risky?
- [ ] Query 12: Why is LOC001 not risky?
- [ ] Query 13: Why is planning health critical?
- [ ] Query 14: What is driving the risk?

### Traceability Queries
- [ ] Query 15: Show top contributing records
- [ ] Query 16: Which records have the most impact?
- [ ] Query 17: Show records with design changes
- [ ] Query 18: Which records are highest risk?

### Location Queries
- [ ] Query 19: Which locations have the most changes?
- [ ] Query 20: Which locations need immediate attention?
- [ ] Query 21: What changed at LOC001?
- [ ] Query 22: Which locations are change hotspots?

### Material Group Queries
- [ ] Query 23: Which material groups changed the most?
- [ ] Query 24: What changed in PUMP?
- [ ] Query 25: Which material groups have design changes?
- [ ] Query 26: Which material groups are most impacted?

### Forecast/Demand Queries
- [ ] Query 27: Why did forecast increase by +50,980?
- [ ] Query 28: Where are we seeing new demand surges?
- [ ] Query 29: Is this demand-driven or design-driven?
- [ ] Query 30: Show forecast trends

### Design/BOD Queries
- [ ] Query 31: Which materials have BOD changes?
- [ ] Query 32: Which materials have Form Factor changes?
- [ ] Query 33: Any design changes at AVC11_F01C01?
- [ ] Query 34: Which supplier has the most design changes?

### Schedule/ROJ Queries
- [ ] Query 35: Which locations have ROJ delays?
- [ ] Query 36: Which supplier is failing to meet ROJ dates?
- [ ] Query 37: Are there ROJ delays at LOC001?
- [ ] Query 38: Show schedule changes

### Health/Status Queries
- [ ] Query 39: What is the current planning health?
- [ ] Query 40: Why is planning health at 37/100?
- [ ] Query 41: What is the risk level?
- [ ] Query 42: Show KPI summary

### Action/Recommendation Queries
- [ ] Query 43: What are the top planner actions?
- [ ] Query 44: What should be done for AVC11_F01C01?

---

## Pass Criteria

✓ **PASS** if:
- Response is relevant to the query
- Response includes data/metrics
- Response time < 500ms
- No errors in logs
- Detail level options work (summary → detailed → full)

✗ **FAIL** if:
- Response is generic/fallback
- Response has no data
- Response time > 500ms
- Errors in logs
- Detail level options don't work

---

## Success Criteria

✓ **SUCCESS** if:
- Pass rate >= 90% (40+ out of 44)
- All critical query types work
- No major errors in logs
- Response times < 500ms
- Detail level options work for all queries

---

## Next Steps

1. Run all 44 prompts
2. Document pass/fail for each
3. Fix any failures
4. Re-test failed prompts
5. Calculate final pass rate
6. Deploy to production

