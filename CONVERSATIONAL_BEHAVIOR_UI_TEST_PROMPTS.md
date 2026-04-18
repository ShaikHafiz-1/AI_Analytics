# Conversational Behavior Fixes - UI Test Prompts

## Overview
Test the new conversational behavior features:
- Session memory (context persistence)
- Transform intent detection (table/tabular/format)
- Historical data availability detection
- Follow-up query handling

---

## Test Scenario 1: Transform Intent Detection

### Setup
- Open the dashboard
- Ensure you have a session ID (or let it default)

### Test Sequence

**Prompt 1: Initial ROJ Analysis**
```
What ROJ changes happened last month?
```

**Expected Response:**
- Detailed ROJ analysis
- Supporting metrics (rojCurrent, rojPrevious, rojDelta, etc.)
- List of impacted records
- Response time: 2-3 seconds

**Prompt 2: Transform to Table (Instant)**
```
Show as table
```

**Expected Response:**
- Same data formatted as markdown table
- Metrics table with values
- Top impacted records table
- Response time: <100ms (instant)
- **Key indicator**: Should NOT recompute, should use cached response

**Prompt 3: Another Transform**
```
Display in tabular format
```

**Expected Response:**
- Same table format
- Response time: <100ms
- Uses cached response from Prompt 1

---

## Test Scenario 2: Transform Keywords Detection

### Test Sequence

**Prompt 1: Initial Analysis**
```
What materials have the highest ROJ impact?
```

**Expected Response:**
- Material-focused analysis
- Supporting metrics
- Top materials listed
- Response time: 2-3 seconds

**Prompt 2: Format Request (Various Keywords)**
```
Convert to table
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

**Prompt 3: Another Format Keyword**
```
Show in spreadsheet format
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

**Prompt 4: CSV Format**
```
Export as CSV
```

**Expected Response:**
- Formatted as table (CSV-like format)
- Response time: <100ms

---

## Test Scenario 3: Historical Data Availability

### Test Sequence

**Prompt 1: Time Window Query**
```
Compare ROJ changes last month vs last quarter
```

**Expected Response:**
- If historical data available: Comparison analysis
- If historical data NOT available: Message added to answer
  - "Historical ROJ comparison is not available in current dataset. Showing current ROJ changes only."
- Supporting metrics
- Response time: 2-3 seconds

**Prompt 2: Another Time Window**
```
What changed in the last 30 days?
```

**Expected Response:**
- Change analysis
- If no historical data: Message about current changes only
- Response time: 2-3 seconds

---

## Test Scenario 4: Follow-up Queries with Context

### Test Sequence

**Prompt 1: Initial Question**
```
What are the top risk factors?
```

**Expected Response:**
- Risk analysis
- Top risk factors listed
- Supporting metrics
- Response time: 2-3 seconds

**Prompt 2: Follow-up (Uses Session Context)**
```
What about location LOC-001?
```

**Expected Response:**
- Location-specific risk analysis
- Uses context from Prompt 1
- Filtered to LOC-001
- Response time: 2-3 seconds

**Prompt 3: Another Follow-up**
```
Show as table
```

**Expected Response:**
- Location-specific data formatted as table
- Response time: <100ms
- Uses cached response from Prompt 2

---

## Test Scenario 5: Multiple Sessions

### Setup
- Open two browser tabs/windows
- Each should have different session IDs

### Test Sequence

**Tab 1 - Prompt 1:**
```
What changed?
```

**Tab 2 - Prompt 1:**
```
What are the risks?
```

**Tab 1 - Prompt 2:**
```
Show as table
```

**Expected Response:**
- Tab 1 shows "What changed?" data as table
- Uses Tab 1's session memory

**Tab 2 - Prompt 2:**
```
Show as table
```

**Expected Response:**
- Tab 2 shows "What are the risks?" data as table
- Uses Tab 2's session memory
- Different from Tab 1's table

**Key Indicator**: Sessions are isolated, each maintains own context

---

## Test Scenario 6: Session Timeout

### Setup
- Ask a question
- Wait 30+ minutes
- Ask a follow-up

### Test Sequence

**Prompt 1:**
```
What ROJ changes happened?
```

**Wait**: 30+ minutes

**Prompt 2:**
```
Show as table
```

**Expected Response:**
- Error or message: "No previous response to transform. Please ask a question first."
- Session expired after 30 minutes
- User needs to ask new question

---

## Test Scenario 7: Transform Without Prior Response

### Test Sequence

**Prompt 1 (First Message):**
```
Show as table
```

**Expected Response:**
- Error: "No previous response to transform. Please ask a question first."
- Explains that user needs to ask a question first

**Prompt 2:**
```
What changed?
```

**Expected Response:**
- Normal analysis response
- Response time: 2-3 seconds

**Prompt 3:**
```
Show as table
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

---

## Test Scenario 8: Mixed Transform Keywords

### Test Sequence

**Prompt 1:**
```
What are the top 10 materials by ROJ impact?
```

**Expected Response:**
- Material analysis
- Top 10 materials
- Response time: 2-3 seconds

**Prompt 2:**
```
Format these in table format
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

**Prompt 3:**
```
Can you show this as columns?
```

**Expected Response:**
- Formatted as table (columns)
- Response time: <100ms

**Prompt 4:**
```
Display in rows
```

**Expected Response:**
- Formatted as table (rows)
- Response time: <100ms

---

## Test Scenario 9: Complex Follow-up Chain

### Test Sequence

**Prompt 1:**
```
What are the main drivers of change?
```

**Expected Response:**
- Driver analysis
- Supporting metrics
- Response time: 2-3 seconds

**Prompt 2:**
```
Focus on location LOC-001
```

**Expected Response:**
- Location-specific driver analysis
- Uses session context
- Response time: 2-3 seconds

**Prompt 3:**
```
Show as table
```

**Expected Response:**
- Location-specific data as table
- Response time: <100ms

**Prompt 4:**
```
What about material MAT-001?
```

**Expected Response:**
- Material-specific analysis
- Uses session context
- Response time: 2-3 seconds

**Prompt 5:**
```
Display in tabular form
```

**Expected Response:**
- Material-specific data as table
- Response time: <100ms

---

## Test Scenario 10: Error Handling

### Test Sequence

**Prompt 1:**
```
Show as table
```

**Expected Response:**
- Error: "No previous response to transform. Please ask a question first."

**Prompt 2:**
```
What changed?
```

**Expected Response:**
- Normal analysis
- Response time: 2-3 seconds

**Prompt 3:**
```
Convert to spreadsheet
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

**Prompt 4:**
```
Show as CSV
```

**Expected Response:**
- Formatted as table
- Response time: <100ms

---

## Performance Benchmarks

### Expected Response Times

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| Initial analysis | 2-3 seconds | Computes metrics, calls LLM |
| Transform request | <100ms | Uses cached response, formats only |
| Follow-up query | 2-3 seconds | Uses session context, recomputes |
| Session expired | <100ms | Returns error immediately |
| No prior response | <100ms | Returns error immediately |

---

## Logging to Monitor

### Backend Logs to Check

**Session Creation:**
```
[SESSION] Created new session: <session_id>
```

**Transform Intent Detection:**
```
[TRANSFORM] Detected transform intent - keyword: table
[TRANSFORM] Formatted response as table
[TRANSFORM] Handled transform request - returned cached response as table
```

**Historical Data:**
```
[HISTORY] No historical ROJ data available
[HISTORY] ROJ delta is 0 - no historical comparison
```

**Session Updates:**
```
[SESSION] Updated context - intent: schedule, has_historical: true
[SESSION] Session expired for <session_id>
```

---

## Checklist for Testing

- [ ] Transform intent detected for "table" keyword
- [ ] Transform intent detected for "tabular" keyword
- [ ] Transform intent detected for "format" keyword
- [ ] Transform intent detected for "show as" keyword
- [ ] Transform intent detected for "display as" keyword
- [ ] Transform request returns <100ms response
- [ ] Transform request uses cached response (no recomputation)
- [ ] Session memory stores last response
- [ ] Session memory stores last intent
- [ ] Session memory stores last question
- [ ] Follow-up queries use session context
- [ ] Historical data availability detected
- [ ] Message added when historical data missing
- [ ] Session timeout after 30 minutes
- [ ] Error returned for transform without prior response
- [ ] Multiple sessions isolated from each other
- [ ] Session ID returned in response
- [ ] Logging shows session operations
- [ ] Logging shows transform operations
- [ ] Logging shows historical data checks

---

## Troubleshooting

### Issue: Transform request returns error
**Solution**: Ensure you asked a question first before requesting transform

### Issue: Transform request takes 2-3 seconds
**Solution**: Check logs for `[TRANSFORM]` messages. If not present, transform intent not detected. Check keyword spelling.

### Issue: Follow-up query doesn't use context
**Solution**: Ensure session ID is consistent between requests. Check logs for `[SESSION]` messages.

### Issue: Historical data message not appearing
**Solution**: Check if historical data is actually available in dataset. Check logs for `[HISTORY]` messages.

### Issue: Session timeout not working
**Solution**: Wait 30+ minutes and try again. Check `SESSION_TIMEOUT_MINUTES` in session_memory.py.

---

## Next Steps

1. Run through each test scenario
2. Monitor backend logs for expected messages
3. Verify response times match benchmarks
4. Check that session memory is working
5. Verify transform requests are instant
6. Confirm historical data detection works
7. Test multiple sessions in parallel
8. Document any issues found
