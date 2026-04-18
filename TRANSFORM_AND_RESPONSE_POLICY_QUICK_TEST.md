# Transform & Response Policy - Quick Test Guide

## What Was Fixed

1. **Transform queries no longer call LLM** - "Show as table" now returns instantly
2. **Analysis queries return final LLM answer** - Not template, actual LLM-generated analysis
3. **Session memory caches responses** - Transform requests reuse cached data
4. **Deterministic table formatting** - No LLM needed for formatting

---

## Quick Test Scenarios

### Test 1: Transform Intent Detection

**Prompt 1:**
```
What ROJ changes happened?
```

**Expected:**
- Question type: `schedule` (not `general`)
- Response time: 2-3 seconds
- Log shows: `Question type: schedule`
- Log shows: `[LLM] Generated final answer:`

**Prompt 2:**
```
Show as table
```

**Expected:**
- Question type: `transform` (not `general`)
- Response time: <100ms (instant)
- Log shows: `Question type: transform`
- Log shows: `[TRANSFORM] Transform intent detected`
- Log shows: `[TRANSFORM] Successfully formatted cached response as table`
- **NO log showing LLM initialization**

---

### Test 2: Response Policy (LLM Answer, Not Template)

**Prompt:**
```
What are the main risks?
```

**Expected:**
- Response contains final LLM-generated analysis
- NOT a template answer
- Log shows: `[LLM] Generated final answer:`
- Answer should be specific to your data

**How to verify:**
- Check if answer is unique/specific (not generic template)
- Check logs for `[LLM]` message
- Compare with previous template answers (should be different)

---

### Test 3: Session Memory

**Prompt 1:**
```
What changed?
```

**Expected:**
- Response time: 2-3 seconds
- Log shows: `[SESSION] Updated context - intent: change`
- Session ID returned in response

**Prompt 2:**
```
Display in tabular format
```

**Expected:**
- Response time: <100ms
- Uses cached response from Prompt 1
- Log shows: `[TRANSFORM] Handled transform request - returned cached response as table`

---

### Test 4: Transform Without Prior Response

**Prompt (first message):**
```
Show as table
```

**Expected:**
- Error response: "No previous result is available to transform. Please ask a question first."
- Response time: <100ms
- Log shows: `[TRANSFORM] No cached response available`

---

### Test 5: Multiple Transform Keywords

**Prompt 1:**
```
What materials have highest impact?
```

**Expected:**
- Question type: `entity` (not `transform`)
- Response time: 2-3 seconds

**Prompt 2:**
```
Convert to table
```

**Expected:**
- Question type: `transform`
- Response time: <100ms
- Formatted as table

**Prompt 3:**
```
Show in spreadsheet format
```

**Expected:**
- Question type: `transform`
- Response time: <100ms
- Formatted as table

---

## Key Logging to Monitor

### Transform Detection
```
[TRANSFORM] Detected transform intent - keyword: 'show as table'
[TRANSFORM] Transform intent detected - using cached response
[TRANSFORM] Successfully formatted cached response as table
[TRANSFORM] Formatted response as table
```

### Session Management
```
[SESSION] Created new session: session-123
[SESSION] Updated context - intent: schedule, question: What ROJ...
```

### LLM Response
```
[LLM] Generated final answer: ...
```

### Question Classification
```
Question type: transform
Question type: schedule
Question type: general
```

---

## Performance Benchmarks

| Scenario | Expected Time | Indicator |
|----------|---------------|-----------|
| Analysis query | 2-3 seconds | LLM call happening |
| Transform query | <100ms | Instant response |
| Transform without prior | <100ms | Error returned immediately |
| Session expired | <100ms | Error returned immediately |

---

## What Should NOT Happen

❌ Transform query calls LLM (should be instant)
❌ Transform query recomputes metrics (should use cached)
❌ Analysis query returns template (should return LLM answer)
❌ Transform query classified as "general" (should be "transform")
❌ No session memory (should store last response)

---

## Verification Checklist

- [ ] Transform queries return <100ms
- [ ] Transform queries don't show LLM initialization in logs
- [ ] Analysis queries show `[LLM]` in logs
- [ ] Analysis queries return specific LLM answers (not templates)
- [ ] Session memory shows `[SESSION]` in logs
- [ ] Transform without prior response returns error
- [ ] Multiple transform keywords work (table, tabular, format, etc.)
- [ ] Session ID returned in response
- [ ] Response schema unchanged

---

## Troubleshooting

### Issue: Transform query takes 2-3 seconds
**Solution**: Check logs for `[TRANSFORM]` message. If not present, transform intent not detected. Check keyword spelling.

### Issue: Transform query shows LLM initialization
**Solution**: Check classify_question() - transform keywords may not be matching. Verify keyword is in the list.

### Issue: Analysis query returns template answer
**Solution**: Check logs for `[LLM]` message. If not present, LLM not being called. Check answer generation function.

### Issue: Session memory not working
**Solution**: Check logs for `[SESSION]` message. If not present, session not being updated. Verify session_memory.py is imported.

### Issue: Transform returns "No previous result"
**Solution**: This is correct behavior if no prior analysis query. Ask an analysis question first, then transform.

---

## Test Prompts

### Quick Test (5 minutes)

1. "What changed?" → Wait for response → Check logs for `[LLM]`
2. "Show as table" → Should be instant → Check logs for `[TRANSFORM]`
3. "Display in tabular format" → Should be instant → Check logs for `[TRANSFORM]`

### Full Test (15 minutes)

1. "What are the risks?" → 2-3 seconds
2. "Convert to table" → <100ms
3. "Show in spreadsheet" → <100ms
4. "What materials?" → 2-3 seconds
5. "Format as table" → <100ms
6. "Show as table" (first message in new session) → Error

---

## Expected Logs

### Analysis Query
```
Question: What ROJ changes happened?
Question type: schedule
[LLM] Generated final answer: ...
[SESSION] Updated context - intent: schedule, question: What ROJ changes...
Explain endpoint returning response
```

### Transform Query
```
Question: Show as table
Question type: transform
[TRANSFORM] Transform intent detected - using cached response
[TRANSFORM] Successfully formatted cached response as table
Explain endpoint returning response
```

### Transform Without Prior
```
Question: Show as table
Question type: transform
[TRANSFORM] Transform intent detected - using cached response
[TRANSFORM] No cached response available
```

---

## Success Criteria

✅ All transform queries return <100ms
✅ All analysis queries show `[LLM]` in logs
✅ All analysis queries return specific LLM answers
✅ Session memory working (shows `[SESSION]` in logs)
✅ Transform without prior returns error
✅ Response schema unchanged
✅ No breaking changes to existing queries
