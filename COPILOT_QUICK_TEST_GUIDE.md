# Copilot Quick Test Guide - 5 Minute Setup

## Start Here

### 1. Open Dashboard
```
http://localhost:3000
```

### 2. Click "Ask Copilot" Button
- Located in top-right area
- Blue button with ✦ icon
- Opens Copilot panel on right side

### 3. You're Ready to Test!

---

## 5-Minute Quick Test

Copy and paste these prompts one by one:

### Prompt 1: Health Status
```
What is the current planning health?
```
**Expected**: Health score (e.g., 75/100), status, and explanation

### Prompt 2: Forecast
```
What is the current forecast?
```
**Expected**: Current forecast, previous forecast, delta, and trend

### Prompt 3: Risk
```
What are the top risks?
```
**Expected**: Risk level, high-risk count, and affected areas

### Prompt 4: Changes
```
How many records have changed?
```
**Expected**: Changed count, total count, percentage, and breakdown

### Prompt 5: Actions
```
What should we do?
```
**Expected**: Recommended actions and priorities

---

## 10-Minute Extended Test

Add these prompts:

### Prompt 6: Suppliers
```
Which suppliers are affected?
```
**Expected**: List of suppliers, affected records, impact

### Prompt 7: Design
```
Are there any design changes?
```
**Expected**: Design change count, BOD changes, form factor changes

### Prompt 8: Locations
```
Which locations are most affected?
```
**Expected**: Top locations, change count, impact

### Prompt 9: Material Groups
```
Which material groups have the most changes?
```
**Expected**: Top material groups, change count, percentage

### Prompt 10: Comparison
```
How does this compare to last period?
```
**Expected**: Comparison of key metrics, trends

---

## Drill-Down Testing (5 minutes)

### Step 1: Select a Location
1. Scroll down to "Location + Material View" section
2. Click on a location in the Datacenter Card
3. Blue banner appears: "Viewing context: location · [location name]"

### Step 2: Ask Location Question
```
Tell me about this location
```
**Expected**: Location-specific analysis

### Step 3: Select a Material Group
1. Click on a material group in the Material Group Card
2. Blue banner updates: "Viewing context: material · [material name]"

### Step 4: Ask Material Question
```
What's happening with this material group?
```
**Expected**: Material group-specific analysis

### Step 5: Select a Supplier
1. Scroll to "Supplier + Design + ROJ" section
2. Click on a supplier in the Supplier Card
3. Blue banner updates: "Viewing context: supplier · [supplier name]"

### Step 6: Ask Supplier Question
```
What is this supplier's impact?
```
**Expected**: Supplier-specific analysis

---

## Follow-Up Testing (5 minutes)

After each answer, the Copilot suggests follow-up questions. Click them to test:

### Example Follow-Ups
- "What can we do to improve it?"
- "Why did these changes happen?"
- "Which ones need immediate attention?"
- "What's the impact of these changes?"

---

## What to Look For

### ✅ Good Response
- [ ] Answers the question directly
- [ ] Shows relevant metrics
- [ ] Provides supporting data
- [ ] Suggests follow-up questions
- [ ] Completes in < 6 seconds

### ⚠️ Acceptable Response
- [ ] Generic but relevant answer
- [ ] Shows available data
- [ ] Suggests related questions
- [ ] Completes in < 6 seconds

### ❌ Problem Response
- [ ] Doesn't answer question
- [ ] Missing data
- [ ] Timeout (> 6 seconds)
- [ ] Irrelevant answer

---

## Common Issues & Fixes

### Issue: Copilot Panel Won't Open
- **Fix**: Refresh page (F5), try again

### Issue: "Thinking..." Spinner Stuck
- **Fix**: Wait 6 seconds, it will timeout and show error

### Issue: No Follow-Up Suggestions
- **Fix**: Normal - not all responses have follow-ups

### Issue: Same Answer Repeated
- **Fix**: This is a known issue - try different question

### Issue: Data Looks Wrong
- **Fix**: Check if using mock data (yellow badge in header)

---

## Test Scenarios

### Scenario 1: Health Analysis
1. "What is the current planning health?"
2. "Why is it at this level?"
3. "What can we do to improve it?"

### Scenario 2: Risk Assessment
1. "What are the top risks?"
2. "How many high-risk records do we have?"
3. "Which materials have the highest risk?"

### Scenario 3: Forecast Impact
1. "What is the current forecast?"
2. "How much has it changed?"
3. "What is driving the change?"

### Scenario 4: Supplier Analysis
1. "Which suppliers are affected?"
2. (Select a supplier)
3. "What is this supplier's impact?"

### Scenario 5: Location Deep Dive
1. "Which locations are most affected?"
2. (Select a location)
3. "Tell me about this location"
4. "What materials are affected here?"

---

## Performance Checklist

- [ ] All responses complete within 6 seconds
- [ ] No timeout errors
- [ ] Follow-up suggestions appear
- [ ] Context switching works (location/material/supplier)
- [ ] Drill-down questions are relevant
- [ ] Data matches dashboard metrics

---

## Data Validation

Check that Copilot answers match dashboard:

### Health Score
- Dashboard shows: Planning Health card
- Copilot should say: Same value

### Forecast
- Dashboard shows: Forecast card
- Copilot should say: Same values

### Risk
- Dashboard shows: Risk Card
- Copilot should say: Same risk level

### Changes
- Dashboard shows: Summary Tiles
- Copilot should say: Same change count

### Records
- Dashboard shows: Top Risk Table
- Copilot should reference: Same records

---

## Quick Troubleshooting

### Backend Not Running?
```bash
cd planning_intelligence
func start
```

### Frontend Not Running?
```bash
cd frontend
npm start
```

### Stale Build?
```bash
cd frontend
npm run build
npm start
```

### Clear Cache?
- Press: Ctrl+Shift+Delete
- Clear: Cookies and cached files
- Reload: Page

---

## Success Criteria

✅ **Test Passed If**:
- Copilot opens without errors
- Responds to all 5 quick test prompts
- Responses are relevant and accurate
- Follow-up suggestions appear
- Drill-down works with selected entities
- No timeouts or errors

❌ **Test Failed If**:
- Copilot won't open
- Responses are irrelevant
- Timeouts occur
- Drill-down doesn't work
- Data doesn't match dashboard

---

## Next Steps

1. ✅ Run 5-minute quick test
2. ✅ Run 10-minute extended test
3. ✅ Test drill-down functionality
4. ✅ Test follow-up questions
5. ✅ Document any issues
6. ✅ Report results

---

## Support

If issues occur:
1. Check browser console (F12)
2. Check backend logs
3. Verify backend is running
4. Verify frontend is running
5. Try clearing cache and reloading

