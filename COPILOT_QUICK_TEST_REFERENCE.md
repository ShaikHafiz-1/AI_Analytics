# Copilot Quick Test Reference

## Quick Test Prompts (Copy & Paste)

### Health & Status (5 seconds each)
```
1. "What is the current planning health status?"
2. "Is planning health improving or declining?"
3. "What factors are affecting our planning health the most?"
```

### Risk Analysis (5 seconds each)
```
4. "What are the main risks in our planning data?"
5. "Tell me about the design changes detected."
6. "What supplier-related risks do we have?"
7. "Are there any schedule or ROJ changes?"
```

### Location Analysis (5 seconds each)
```
8. "Which location has the most changes?"
9. "What's happening at LOC001?"
10. "Compare the planning situation across all locations."
```

### Material Groups (5 seconds each)
```
11. "Which material group has the most changes?"
12. "Tell me about the PUMP material group changes."
13. "How do PUMP, VALVE, and MOTOR compare?"
```

### Forecast & Demand (5 seconds each)
```
14. "What's the forecast trend?"
15. "How is the demand change affecting our planning?"
16. "What's driving the forecast increase?"
```

### Changes & Drivers (5 seconds each)
```
17. "Give me a summary of all changes."
18. "What quantity changes have occurred?"
19. "Where are the changes concentrated?"
```

### Suppliers (5 seconds each)
```
20. "What supplier changes do we have?"
21. "What's the impact of the SUP-A supplier change?"
22. "Are there supplier-related risks we should be concerned about?"
```

### Design & Engineering (5 seconds each)
```
23. "What design changes have been made?"
24. "Tell me about the BOD version changes."
25. "How do design changes affect procurement?"
```

### Actions & Recommendations (5 seconds each)
```
26. "What actions should we take?"
27. "What's the most urgent action we need to take?"
28. "What should we do next?"
```

### Exploratory (10 seconds each)
```
29. "What should I know about our planning health?"
30. "What are the biggest concerns?"
31. "What do you recommend we focus on?"
```

---

## Expected Data Points

### Key Metrics
- **Health Score**: 72/100
- **Status**: Stable
- **Forecast**: 3,900 → 4,850 units (+950)
- **Total Records**: 120
- **Changed Records**: 34 (28%)
- **New Records**: 3

### Locations
- **LOC001** (DC-WEST): 60 records, 18 changed
- **LOC002** (DC-EAST): 40 records, 12 changed
- **LOC003** (DC-SOUTH): 20 records, 4 changed

### Material Groups
- **PUMP**: 50 records, 18 changed
- **VALVE**: 40 records, 10 changed
- **MOTOR**: 30 records, 6 changed

### Change Breakdown
- **Quantity**: 20 changes
- **Supplier**: 6 changes
- **Design**: 4 changes
- **ROJ**: 8 changes

### Risk Levels
- **Overall Risk**: HIGH
- **Highest Risk Type**: Design Change Risk
- **High-Risk Records**: 12
- **Risk Breakdown**:
  - Design Change Risk: 4
  - Supplier Change Risk: 6
  - High Demand Spike: 2

### Key Drivers
- **Location**: LOC001
- **Supplier**: SUP-A
- **Material**: MAT-100
- **Material Group**: PUMP
- **Change Type**: Quantity

### Alerts
- **Severity**: High
- **Trigger Type**: Design Change
- **Message**: 4 design changes detected (BOD/Form Factor)

---

## Validation Checklist

### Response Should Include
- [ ] Accurate data from dashboard
- [ ] Relevant context and explanation
- [ ] Specific numbers and metrics
- [ ] Location/material group references
- [ ] Actionable recommendations

### Data Accuracy
- [ ] Health score matches (72/100)
- [ ] Forecast change correct (+950)
- [ ] Record counts accurate (120 total, 34 changed)
- [ ] Location data correct
- [ ] Material group data correct
- [ ] Risk levels accurate

### Quality Indicators
- [ ] Response is clear and concise
- [ ] Response uses domain terminology correctly
- [ ] Response provides context
- [ ] Response suggests next steps
- [ ] Response maintains conversation flow

---

## Test Scenarios

### Scenario 1: New User (5 min)
1. "What is the current planning health status?"
2. "What are the main risks?"
3. "What should we do?"

### Scenario 2: Risk Focus (5 min)
1. "What are the biggest concerns?"
2. "Tell me about the design changes."
3. "What's the impact of SUP-A?"

### Scenario 3: Location Analysis (5 min)
1. "Which location has the most changes?"
2. "What's happening at LOC001?"
3. "Compare all locations."

### Scenario 4: Material Group Analysis (5 min)
1. "Which material group has the most changes?"
2. "Tell me about PUMP changes."
3. "How do they compare?"

### Scenario 5: Forecast & Demand (5 min)
1. "What's the forecast trend?"
2. "How is demand change affecting us?"
3. "What's driving the increase?"

### Scenario 6: Action Planning (5 min)
1. "What actions should we take?"
2. "What's most urgent?"
3. "What should we do next?"

---

## Common Issues to Check

### Data Accuracy
- ❌ Wrong health score
- ❌ Incorrect forecast numbers
- ❌ Wrong record counts
- ❌ Missing location data
- ❌ Incorrect risk levels

### Response Quality
- ❌ Vague or generic answers
- ❌ Missing specific data points
- ❌ No context or explanation
- ❌ No actionable recommendations
- ❌ Inconsistent with dashboard

### Feature Issues
- ❌ Doesn't understand questions
- ❌ Provides irrelevant answers
- ❌ Loses context in follow-ups
- ❌ Can't drill down by location/material
- ❌ Doesn't reference alerts

---

## Success Criteria

✅ **Copilot should**:
1. Answer all 31 test prompts accurately
2. Reference real data from dashboard
3. Provide context and explanation
4. Suggest actionable next steps
5. Handle follow-up questions
6. Maintain conversation context
7. Understand planning terminology
8. Identify patterns and trends
9. Assess risks appropriately
10. Recommend prioritized actions

---

## Testing Time Estimate

- **Quick Test** (10 prompts): 2-3 minutes
- **Standard Test** (20 prompts): 5-7 minutes
- **Full Test** (31 prompts): 10-15 minutes
- **Scenario Tests** (6 scenarios): 30 minutes

---

## Notes

- Test with both mock and real blob data
- Verify responses match dashboard exactly
- Check that recommendations align with alerts
- Ensure context persists across questions
- Test drill-down with filters
- Verify error handling for invalid questions

