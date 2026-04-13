# Copilot Testing Summary - Complete Guide

## Overview

I've created comprehensive test prompts and scenarios for the Planning Intelligence Copilot feature. The Copilot can answer questions about planning health, forecasts, risks, suppliers, materials, locations, and recommended actions.

---

## Test Documents Created

### 1. **COPILOT_TEST_PROMPTS.md** (53 Prompts)
- 12 categories of test questions
- 53 specific prompts to test
- Expected responses for each
- Testing workflow (7 phases)
- Metrics to track

### 2. **COPILOT_QUICK_TEST_GUIDE.md** (Quick Start)
- 5-minute quick test
- 10-minute extended test
- Drill-down testing
- Follow-up testing
- Common issues & fixes

### 3. **COPILOT_INTERACTIVE_TEST_SCENARIOS.md** (10 Scenarios)
- 10 detailed test scenarios
- Step-by-step instructions
- Expected responses
- Scoring rubric
- Success criteria

---

## Quick Start (5 Minutes)

### Copy & Paste These Prompts:

1. **"What is the current planning health?"**
   - Tests: Health status, score, explanation

2. **"What is the current forecast?"**
   - Tests: Forecast data, trend, delta

3. **"What are the top risks?"**
   - Tests: Risk analysis, high-risk count

4. **"How many records have changed?"**
   - Tests: Change analysis, breakdown

5. **"What should we do?"**
   - Tests: Recommendations, actions

---

## Test Categories (53 Prompts)

### Category 1: Planning Health & Status (4 prompts)
- Current health status
- Health trend
- Health drivers
- Health explanation

### Category 2: Forecast & Trends (4 prompts)
- Current forecast
- Forecast change
- Forecast drivers
- Forecast trend

### Category 3: Risk Analysis (4 prompts)
- Top risks
- High-risk count
- Highest risk level
- Risky materials

### Category 4: Change Analysis (4 prompts)
- Changed records count
- Change types
- Most changed materials
- New records

### Category 5: Supplier Analysis (4 prompts)
- Affected suppliers
- Top supplier impact
- Supplier change count
- Top supplier by changes

### Category 6: Design Changes (4 prompts)
- Design changes existence
- Design change count
- Design change types
- Materials with design changes

### Category 7: Location & Material (4 prompts)
- Most affected locations
- Location situation
- Material groups with changes
- Material group status

### Category 8: Recommended Actions (4 prompts)
- What to do
- Top priorities
- Health improvement
- Recommended actions

### Category 9: Comparative Analysis (3 prompts)
- Comparison to last period
- Better or worse
- Changes since last refresh

### Category 10: Drill-Down (6 prompts)
- Location analysis
- Location materials
- Material group analysis
- Material group suppliers
- Supplier impact
- Supplier materials

### Category 11: Follow-Ups (6 prompts)
- Improvement recommendations
- Main issues
- Risk mitigation
- Urgent risks
- Change reasons
- Change impact

### Category 12: Edge Cases (3 prompts)
- Supplier-forecast correlation
- Design-health correlation
- Scenario analysis

---

## Test Scenarios (10 Scenarios)

### Scenario 1: Executive Dashboard Review (10 min)
- Health overview
- Forecast analysis
- Risk assessment
- Action recommendations

### Scenario 2: Supplier Impact Analysis (15 min)
- Supplier overview
- Drill-down on top supplier
- Supplier-specific analysis
- Mitigation strategies

### Scenario 3: Location-Based Analysis (15 min)
- Location overview
- Drill-down on top location
- Location-specific analysis
- Material analysis

### Scenario 4: Material Group Deep Dive (15 min)
- Material group overview
- Drill-down on top group
- Group-specific analysis
- Supplier analysis

### Scenario 5: Risk Mitigation Planning (15 min)
- Risk overview
- Risk details
- Specific risk analysis
- Mitigation strategies

### Scenario 6: Change Analysis (15 min)
- Change overview
- Change breakdown
- Top changes
- Root cause analysis

### Scenario 7: Comparative Analysis (10 min)
- Comparison to last period
- Improvement assessment
- Change tracking

### Scenario 8: Follow-Up Testing (10 min)
- Test follow-up suggestions
- Click suggested questions
- Verify responses

### Scenario 9: Context Switching (10 min)
- Select location
- Switch to material group
- Switch to supplier
- Clear context

### Scenario 10: Edge Cases (10 min)
- Unclear questions
- Out-of-scope questions
- Duplicate questions
- Complex questions

---

## Testing Workflow

### Phase 1: Basic Questions (5-10 min)
1. Health questions (1-4)
2. Forecast questions (5-8)
3. Risk questions (9-12)

### Phase 2: Detailed Analysis (10-15 min)
4. Change questions (13-16)
5. Supplier questions (17-20)
6. Design questions (21-24)

### Phase 3: Location & Material (5-10 min)
7. Location questions (25-26)
8. Material questions (27-28)

### Phase 4: Actions & Recommendations (5 min)
9. Action questions (29-32)

### Phase 5: Drill-Down Testing (10-15 min)
10. Select location, ask questions
11. Select material group, ask questions
12. Select supplier, ask questions

### Phase 6: Follow-Ups (5-10 min)
13. Click follow-up suggestions
14. Ask follow-up questions

### Phase 7: Edge Cases (5-10 min)
15. Ask complex questions
16. Ask clarification questions

---

## Expected Responses

### Successful Response ✅
- Answers question directly
- Provides supporting metrics
- Shows relevant data
- Offers follow-up suggestions
- Completes within 6 seconds

### Acceptable Response ⚠️
- Generic but relevant answer
- Shows available data
- Suggests related questions
- Completes within 6 seconds

### Problem Response ❌
- Doesn't answer question
- Missing data
- Timeout (> 6 seconds)
- Irrelevant answer

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

## Scoring Rubric

### Response Quality (0-10)
- 10: Directly answers, provides data, suggests follow-ups
- 8: Answers question, provides some data
- 6: Partially answers, limited data
- 4: Generic answer, minimal data
- 2: Irrelevant answer
- 0: No response or error

### Performance (0-10)
- 10: Responds in < 2 seconds
- 8: Responds in 2-4 seconds
- 6: Responds in 4-6 seconds
- 4: Responds in 6-8 seconds
- 2: Responds in 8-10 seconds
- 0: Timeout (> 10 seconds)

### User Experience (0-10)
- 10: Smooth, intuitive, helpful
- 8: Good experience, minor issues
- 6: Acceptable experience
- 4: Frustrating but functional
- 2: Very frustrating
- 0: Broken

---

## Test Execution Plan

### Day 1: Quick Test (30 minutes)
1. Run 5-minute quick test
2. Run 10-minute extended test
3. Document results

### Day 2: Scenario Testing (1-2 hours)
1. Run Scenario 1-3 (Executive, Supplier, Location)
2. Document results
3. Note any issues

### Day 3: Deep Dive (1-2 hours)
1. Run Scenario 4-7 (Material, Risk, Change, Comparison)
2. Test follow-ups
3. Document results

### Day 4: Edge Cases (1 hour)
1. Run Scenario 8-10 (Follow-ups, Context, Edge Cases)
2. Test error handling
3. Document results

### Day 5: Final Review (30 minutes)
1. Review all results
2. Identify patterns
3. Create final report

---

## Success Criteria

✅ **Test Passed If**:
- Copilot opens without errors
- Responds to all test prompts
- Responses are relevant and accurate
- Follow-up suggestions appear and work
- Drill-down works with selected entities
- No timeouts or errors
- Data matches dashboard

❌ **Test Failed If**:
- Copilot won't open
- Responses are irrelevant
- Timeouts occur
- Drill-down doesn't work
- Data doesn't match dashboard
- Errors occur

---

## Common Issues & Fixes

### Issue: Copilot Won't Open
- **Fix**: Refresh page (F5), try again

### Issue: "Thinking..." Spinner Stuck
- **Fix**: Wait 6 seconds, it will timeout

### Issue: Same Answer Repeated
- **Fix**: Try different question

### Issue: Data Looks Wrong
- **Fix**: Check if using mock data

### Issue: Timeout Errors
- **Fix**: Check backend is running

---

## Next Steps

1. ✅ Open http://localhost:3000
2. ✅ Click "Ask Copilot" button
3. ✅ Copy first prompt from COPILOT_QUICK_TEST_GUIDE.md
4. ✅ Paste into Copilot input
5. ✅ Press Enter or click Send
6. ✅ Observe response
7. ✅ Repeat with other prompts
8. ✅ Document results

---

## Files Created

1. ✅ `COPILOT_TEST_PROMPTS.md` - 53 test prompts
2. ✅ `COPILOT_QUICK_TEST_GUIDE.md` - Quick start guide
3. ✅ `COPILOT_INTERACTIVE_TEST_SCENARIOS.md` - 10 scenarios
4. ✅ `COPILOT_TESTING_SUMMARY.md` - This file

---

## Summary

You now have:
- **53 test prompts** across 12 categories
- **10 detailed test scenarios** with step-by-step instructions
- **Quick test guide** for 5-minute testing
- **Scoring rubric** for evaluating responses
- **Success criteria** for test completion

**Start with the 5-minute quick test, then move to scenarios!**

