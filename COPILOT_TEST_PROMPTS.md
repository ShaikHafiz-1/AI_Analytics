# Copilot Test Prompts - Comprehensive Testing Guide

## Overview

The Planning Intelligence Copilot can answer questions about:
- Planning health and status
- Forecast trends and changes
- Risk analysis and drivers
- Supplier and design changes
- Material group performance
- Location-based insights
- Recommended actions

---

## Category 1: Planning Health & Status

### Basic Health Questions
1. **"What is the current planning health?"**
   - Expected: Health score (e.g., 75/100), status (Healthy/Stable/At Risk/Critical)
   - Should show: Health band, dominant factors

2. **"Is our planning health improving or declining?"**
   - Expected: Trend analysis, comparison to previous period
   - Should show: Direction, rate of change

3. **"Why is planning health at this level?"**
   - Expected: Root causes, contributing factors
   - Should show: Change ratio %, risk level, design/supplier impact

4. **"What does a health score of 75 mean?"**
   - Expected: Explanation of health bands
   - Should show: Healthy (≥80), Stable (60-79), At Risk (40-59), Critical (<40)

---

## Category 2: Forecast & Trends

### Forecast Questions
5. **"What is the current forecast?"**
   - Expected: Current forecast value, previous value, delta
   - Should show: Trend direction (Increasing/Decreasing/Stable)

6. **"How much has the forecast changed?"**
   - Expected: Delta value, percentage change
   - Should show: Absolute and relative change

7. **"What is driving the forecast change?"**
   - Expected: Root causes (supplier changes, design changes, quantity changes)
   - Should show: Top drivers, affected materials

8. **"Is the forecast trend positive or negative?"**
   - Expected: Trend direction with explanation
   - Should show: Impact on planning

---

## Category 3: Risk Analysis

### Risk Questions
9. **"What are the top risks in our planning?"**
   - Expected: Risk summary, highest risk level
   - Should show: Design risks, supplier risks, spike risks

10. **"How many high-risk records do we have?"**
    - Expected: Count of high-risk records
    - Should show: Percentage of total, risk breakdown

11. **"What is the highest risk level?"**
    - Expected: Risk level (Design, Supplier, Design + Supplier, Spike)
    - Should show: Affected records, impact

12. **"Which materials have the highest risk?"**
    - Expected: Top risky materials
    - Should show: Risk level, reason, affected records

---

## Category 4: Change Analysis

### Change Questions
13. **"How many records have changed?"**
    - Expected: Changed count, total count, percentage
    - Should show: Breakdown by type (quantity, supplier, design, ROJ)

14. **"What types of changes are we seeing?"**
    - Expected: Change breakdown (quantity, supplier, design, ROJ)
    - Should show: Count and percentage for each type

15. **"Which materials changed the most?"**
    - Expected: Top changed materials
    - Should show: Change type, impact on forecast

16. **"Are there any new records?"**
    - Expected: New record count
    - Should show: Impact on planning

---

## Category 5: Supplier Analysis

### Supplier Questions
17. **"Which suppliers are affected?"**
    - Expected: List of affected suppliers
    - Should show: Number of affected records, impact

18. **"What is the top supplier impact?"**
    - Expected: Supplier with most impact
    - Should show: Affected records, forecast impact

19. **"How many supplier changes do we have?"**
    - Expected: Count of supplier changes
    - Should show: Percentage of total changes

20. **"Which supplier has the most changes?"**
    - Expected: Top supplier by change count
    - Should show: Affected materials, impact

---

## Category 6: Design Changes

### Design Questions
21. **"Are there any design changes?"**
    - Expected: Yes/No, count if yes
    - Should show: BOD changes, form factor changes

22. **"How many design changes do we have?"**
    - Expected: Total design change count
    - Should show: BOD changes, form factor changes

23. **"What design changes are we seeing?"**
    - Expected: Breakdown of design changes
    - Should show: BOD changes, form factor changes, affected materials

24. **"Which materials have design changes?"**
    - Expected: List of materials with design changes
    - Should show: Type of change, impact

---

## Category 7: Location & Material Group Analysis

### Location Questions
25. **"Which locations are most affected?"**
    - Expected: Top affected locations
    - Should show: Change count, impact

26. **"What is the situation at [location]?"**
    - Expected: Location-specific analysis
    - Should show: Changes, risks, forecast impact

### Material Group Questions
27. **"Which material groups have the most changes?"**
    - Expected: Top material groups by change count
    - Should show: Change count, percentage

28. **"What is the status of [material group]?"**
    - Expected: Material group-specific analysis
    - Should show: Changes, risks, health

---

## Category 8: Recommended Actions

### Action Questions
29. **"What should we do about the planning issues?"**
    - Expected: Recommended actions
    - Should show: Priority, impact, effort

30. **"What are the top priorities?"**
    - Expected: Priority list
    - Should show: Action, reason, expected impact

31. **"How can we improve planning health?"**
    - Expected: Improvement recommendations
    - Should show: Actions, expected impact

32. **"What actions are recommended?"**
    - Expected: List of recommended actions
    - Should show: Priority, reason, impact

---

## Category 9: Comparative Analysis

### Comparison Questions
33. **"How does this compare to last period?"**
    - Expected: Comparison of key metrics
    - Should show: Changes, trends

34. **"Are we better or worse than before?"**
    - Expected: Overall trend assessment
    - Should show: Key improvements/deteriorations

35. **"What changed since last refresh?"**
    - Expected: Changes since last update
    - Should show: New changes, resolved issues

---

## Category 10: Drill-Down Questions (With Selected Entity)

### When Location Selected
36. **"Tell me about this location"**
    - Expected: Location-specific analysis
    - Should show: Changes, risks, materials affected

37. **"What materials are affected here?"**
    - Expected: Materials at this location
    - Should show: Change count, risk level

### When Material Group Selected
38. **"What's happening with this material group?"**
    - Expected: Material group analysis
    - Should show: Changes, risks, suppliers affected

39. **"Which suppliers affect this group?"**
    - Expected: Suppliers for this material group
    - Should show: Change count, impact

### When Supplier Selected
40. **"What is this supplier's impact?"**
    - Expected: Supplier-specific analysis
    - Should show: Affected materials, forecast impact

41. **"Which materials does this supplier affect?"**
    - Expected: Materials from this supplier
    - Should show: Change count, risk level

---

## Category 11: Follow-Up Questions

### After Health Question
42. **"What can we do to improve it?"**
    - Expected: Improvement recommendations
    - Should show: Actions, expected impact

43. **"What's the main issue?"**
    - Expected: Primary driver
    - Should show: Root cause, impact

### After Risk Question
44. **"How do we mitigate these risks?"**
    - Expected: Risk mitigation strategies
    - Should show: Actions, priority

45. **"Which ones need immediate attention?"**
    - Expected: High-priority risks
    - Should show: Risk level, impact

### After Change Question
46. **"Why did these changes happen?"**
    - Expected: Root cause analysis
    - Should show: Drivers, impact

47. **"What's the impact of these changes?"**
    - Expected: Impact analysis
    - Should show: Forecast impact, risk impact

---

## Category 12: Edge Cases & Complex Questions

### Complex Analysis
48. **"What is the relationship between supplier changes and forecast impact?"**
    - Expected: Correlation analysis
    - Should show: Supplier changes, forecast delta

49. **"Are design changes correlated with health decline?"**
    - Expected: Correlation analysis
    - Should show: Design changes, health impact

50. **"What would happen if we resolved all supplier issues?"**
    - Expected: Scenario analysis
    - Should show: Potential health improvement

### Clarification Questions
51. **"What do you mean by planning health?"**
    - Expected: Definition and explanation
    - Should show: Calculation method, factors

52. **"How is risk calculated?"**
    - Expected: Risk calculation explanation
    - Should show: Risk factors, thresholds

53. **"What is a high-risk record?"**
    - Expected: Definition of high-risk
    - Should show: Criteria, examples

---

## Testing Workflow

### Phase 1: Basic Questions (5-10 minutes)
1. Start with questions 1-4 (Health)
2. Then questions 5-8 (Forecast)
3. Then questions 9-12 (Risk)

### Phase 2: Detailed Analysis (10-15 minutes)
4. Questions 13-16 (Changes)
5. Questions 17-20 (Suppliers)
6. Questions 21-24 (Design)

### Phase 3: Location & Material (5-10 minutes)
7. Questions 25-28 (Location & Material Group)

### Phase 4: Actions & Recommendations (5 minutes)
8. Questions 29-32 (Recommended Actions)

### Phase 5: Drill-Down Testing (10-15 minutes)
9. Select a location, ask questions 36-37
10. Select a material group, ask questions 38-39
11. Select a supplier, ask questions 40-41

### Phase 6: Follow-Ups (5-10 minutes)
12. Ask follow-up questions based on previous answers

### Phase 7: Edge Cases (5-10 minutes)
13. Ask complex questions 48-50
14. Ask clarification questions 51-53

---

## Expected Behaviors

### Successful Response
- ✅ Answers question directly
- ✅ Provides supporting metrics
- ✅ Shows relevant data
- ✅ Offers follow-up suggestions
- ✅ Completes within 6 seconds

### Fallback Response
- ⚠️ Generic answer based on data
- ⚠️ Shows available metrics
- ⚠️ Suggests related questions
- ⚠️ Completes within 6 seconds

### Error Response
- ❌ Timeout (>6 seconds)
- ❌ No answer provided
- ❌ Irrelevant response
- ❌ Missing supporting data

---

## Metrics to Track

### Response Quality
- [ ] Accuracy: Does answer match data?
- [ ] Completeness: Does answer address question?
- [ ] Clarity: Is answer understandable?
- [ ] Relevance: Is answer relevant to question?

### Performance
- [ ] Response time: < 6 seconds?
- [ ] No timeouts?
- [ ] Consistent performance?

### User Experience
- [ ] Follow-up suggestions helpful?
- [ ] Context switching smooth?
- [ ] Error handling graceful?

---

## Test Data Expectations

Based on typical blob data:
- **Planning Health**: 37-100 (varies by data)
- **Total Records**: 100-500
- **Changed Records**: 20-100
- **High-Risk Records**: 5-50
- **Suppliers**: 5-20
- **Material Groups**: 3-10
- **Locations**: 2-5

---

## Quick Test (5 minutes)

If you only have 5 minutes, test these:
1. "What is the current planning health?" (Health)
2. "What is the current forecast?" (Forecast)
3. "What are the top risks?" (Risk)
4. "How many records have changed?" (Changes)
5. "What actions are recommended?" (Actions)

---

## Comprehensive Test (30 minutes)

For full testing:
1. Run Phase 1-4 (30 minutes total)
2. Document any issues
3. Test drill-down with selected entities
4. Test follow-up questions
5. Test edge cases

