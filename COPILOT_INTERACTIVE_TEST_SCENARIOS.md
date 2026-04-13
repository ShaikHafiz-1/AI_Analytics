# Copilot Interactive Test Scenarios

## Scenario 1: Executive Dashboard Review (10 minutes)

**Goal**: Get a quick overview of planning status

### Step 1: Open Copilot
- Click "Ask Copilot" button
- Copilot panel opens on right

### Step 2: Ask Health Question
```
What is the current planning health?
```
**Expected Response**:
- Health score (e.g., 75/100)
- Status (Healthy/Stable/At Risk/Critical)
- Key factors affecting health
- Recommendation

**Follow-up**: Click suggested follow-up or ask:
```
What's the main issue?
```

### Step 3: Ask Forecast Question
```
What is the current forecast?
```
**Expected Response**:
- Current forecast value
- Previous forecast value
- Delta (change amount)
- Trend direction

**Follow-up**:
```
What is driving the forecast change?
```

### Step 4: Ask Risk Question
```
What are the top risks?
```
**Expected Response**:
- Risk level
- High-risk record count
- Risk breakdown (Design, Supplier, etc.)
- Affected areas

**Follow-up**:
```
How do we mitigate these risks?
```

### Step 5: Ask Action Question
```
What should we do?
```
**Expected Response**:
- Recommended actions
- Priority order
- Expected impact
- Effort required

---

## Scenario 2: Supplier Impact Analysis (15 minutes)

**Goal**: Understand supplier-related issues

### Step 1: Ask Supplier Overview
```
Which suppliers are affected?
```
**Expected Response**:
- List of affected suppliers
- Number of affected records per supplier
- Forecast impact per supplier

### Step 2: Drill-Down on Top Supplier
1. Note the top supplier from response
2. Scroll to "Supplier + Design + ROJ" section
3. Click on the top supplier in the Supplier Card
4. Blue banner shows: "Viewing context: supplier · [supplier name]"

### Step 3: Ask Supplier-Specific Question
```
What is this supplier's impact?
```
**Expected Response**:
- Supplier-specific analysis
- Affected materials
- Forecast impact
- Design changes

### Step 4: Ask Follow-Up
```
Which materials does this supplier affect?
```
**Expected Response**:
- List of materials from this supplier
- Change count per material
- Risk level per material

### Step 5: Ask Mitigation Question
```
How can we reduce this supplier's impact?
```
**Expected Response**:
- Mitigation strategies
- Alternative suppliers (if available)
- Timeline for resolution

---

## Scenario 3: Location-Based Analysis (15 minutes)

**Goal**: Analyze planning issues by location

### Step 1: Ask Location Overview
```
Which locations are most affected?
```
**Expected Response**:
- Top affected locations
- Change count per location
- Risk level per location

### Step 2: Drill-Down on Top Location
1. Note the top location from response
2. Scroll to "Location + Material View" section
3. Click on the top location in the Datacenter Card
4. Blue banner shows: "Viewing context: location · [location name]"

### Step 3: Ask Location-Specific Question
```
Tell me about this location
```
**Expected Response**:
- Location-specific analysis
- Materials affected
- Suppliers involved
- Risk level

### Step 4: Ask Material Question
```
What materials are affected here?
```
**Expected Response**:
- List of materials at this location
- Change count per material
- Risk level per material

### Step 5: Ask Comparison Question
```
How does this location compare to others?
```
**Expected Response**:
- Comparison metrics
- Relative performance
- Recommendations

---

## Scenario 4: Material Group Deep Dive (15 minutes)

**Goal**: Analyze specific material group issues

### Step 1: Ask Material Group Overview
```
Which material groups have the most changes?
```
**Expected Response**:
- Top material groups by change count
- Change count per group
- Percentage of total changes

### Step 2: Drill-Down on Top Material Group
1. Note the top material group from response
2. Scroll to "Location + Material View" section
3. Click on the top material group in the Material Group Card
4. Blue banner shows: "Viewing context: material · [material group name]"

### Step 3: Ask Material Group Question
```
What's happening with this material group?
```
**Expected Response**:
- Material group-specific analysis
- Changes by type
- Affected suppliers
- Risk level

### Step 4: Ask Supplier Question
```
Which suppliers affect this group?
```
**Expected Response**:
- Suppliers for this material group
- Change count per supplier
- Impact per supplier

### Step 5: Ask Trend Question
```
Is this material group improving or declining?
```
**Expected Response**:
- Trend analysis
- Direction (improving/declining/stable)
- Rate of change

---

## Scenario 5: Risk Mitigation Planning (15 minutes)

**Goal**: Develop risk mitigation strategy

### Step 1: Ask Risk Overview
```
What are the top risks?
```
**Expected Response**:
- Risk level
- High-risk record count
- Risk breakdown

### Step 2: Ask Risk Details
```
What is the highest risk level?
```
**Expected Response**:
- Highest risk level
- Affected records
- Root causes

### Step 3: Ask Specific Risk Question
```
Which materials have the highest risk?
```
**Expected Response**:
- Top risky materials
- Risk level per material
- Reason for risk

### Step 4: Ask Mitigation Question
```
How do we mitigate these risks?
```
**Expected Response**:
- Risk mitigation strategies
- Priority order
- Timeline

### Step 5: Ask Impact Question
```
What would happen if we resolved all risks?
```
**Expected Response**:
- Potential health improvement
- Forecast impact
- Timeline for resolution

---

## Scenario 6: Change Analysis (15 minutes)

**Goal**: Understand what changed and why

### Step 1: Ask Change Overview
```
How many records have changed?
```
**Expected Response**:
- Changed count
- Total count
- Percentage changed

### Step 2: Ask Change Breakdown
```
What types of changes are we seeing?
```
**Expected Response**:
- Breakdown by type (quantity, supplier, design, ROJ)
- Count per type
- Percentage per type

### Step 3: Ask Top Changes
```
Which materials changed the most?
```
**Expected Response**:
- Top changed materials
- Change type per material
- Impact per material

### Step 4: Ask Root Cause
```
Why did these changes happen?
```
**Expected Response**:
- Root cause analysis
- Primary drivers
- Contributing factors

### Step 5: Ask Impact Question
```
What's the impact of these changes?
```
**Expected Response**:
- Forecast impact
- Risk impact
- Health impact

---

## Scenario 7: Comparative Analysis (10 minutes)

**Goal**: Compare current state to previous period

### Step 1: Ask Comparison
```
How does this compare to last period?
```
**Expected Response**:
- Comparison of key metrics
- Changes in health, forecast, risk
- Trends

### Step 2: Ask Improvement Question
```
Are we better or worse than before?
```
**Expected Response**:
- Overall trend assessment
- Key improvements
- Key deteriorations

### Step 3: Ask Change Question
```
What changed since last refresh?
```
**Expected Response**:
- New changes
- Resolved issues
- Ongoing issues

---

## Scenario 8: Follow-Up Question Testing (10 minutes)

**Goal**: Test follow-up suggestion functionality

### Step 1: Ask Initial Question
```
What is the current planning health?
```

### Step 2: Click Follow-Up Suggestion
- Look for suggested follow-up button
- Click on it
- Observe response

### Step 3: Ask Another Question
```
What are the top risks?
```

### Step 4: Click Follow-Up Suggestion
- Look for suggested follow-up button
- Click on it
- Observe response

### Step 5: Ask Action Question
```
What should we do?
```

### Step 6: Click Follow-Up Suggestion
- Look for suggested follow-up button
- Click on it
- Observe response

---

## Scenario 9: Context Switching (10 minutes)

**Goal**: Test switching between different contexts

### Step 1: Select Location
1. Scroll to "Location + Material View"
2. Click on a location
3. Ask: "Tell me about this location"

### Step 2: Switch to Material Group
1. Click on a material group
2. Ask: "What's happening with this material group?"

### Step 3: Switch to Supplier
1. Scroll to "Supplier + Design + ROJ"
2. Click on a supplier
3. Ask: "What is this supplier's impact?"

### Step 4: Clear Context
1. Click "✕ Clear" button in blue banner
2. Ask: "What is the current planning health?"
3. Verify response is global, not location-specific

---

## Scenario 10: Edge Cases & Error Handling (10 minutes)

**Goal**: Test error handling and edge cases

### Step 1: Ask Unclear Question
```
Tell me everything
```
**Expected**: Fallback answer with available data

### Step 2: Ask Out-of-Scope Question
```
What is the weather?
```
**Expected**: Polite decline or redirect to planning data

### Step 3: Ask Duplicate Question
```
What is the current planning health?
```
(Ask same question twice)
**Expected**: Consistent answer both times

### Step 4: Ask Complex Question
```
What is the relationship between supplier changes and forecast impact?
```
**Expected**: Correlation analysis or fallback answer

### Step 5: Test Timeout
1. Ask a question
2. Wait 6+ seconds
3. Observe timeout handling

---

## Scoring Rubric

### Response Quality (0-10)
- 10: Directly answers question, provides supporting data, suggests follow-ups
- 8: Answers question, provides some data, may lack follow-ups
- 6: Partially answers question, limited data
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

## Test Results Template

```
Scenario: [Name]
Date: [Date]
Tester: [Name]

Questions Asked:
1. [Question] - Response Quality: [0-10], Performance: [0-10]
2. [Question] - Response Quality: [0-10], Performance: [0-10]
3. [Question] - Response Quality: [0-10], Performance: [0-10]

Overall Score: [Average]
Issues Found: [List]
Recommendations: [List]
```

---

## Success Criteria

✅ **All Scenarios Passed If**:
- All responses are relevant and accurate
- All responses complete within 6 seconds
- Follow-up suggestions appear and work
- Context switching works smoothly
- No errors or timeouts
- Data matches dashboard

❌ **Any Scenario Failed If**:
- Response is irrelevant
- Response times out
- Context switching fails
- Data doesn't match dashboard
- Errors occur

