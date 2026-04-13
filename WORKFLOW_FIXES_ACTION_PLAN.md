# Workflow Fixes Action Plan

## Critical Issues to Fix Before Deployment

### Issue 1: Frontend Timeout Too Short (6 seconds)

**Current Code** (frontend/src/components/CopilotPanel.tsx):
```typescript
const timeoutId = setTimeout(() => {
  setLoading(false);
  setInput(question.trim());
  setMessages((prev) => [...prev, { 
    role: "assistant", 
    content: "⏱ Request timed out. Your question has been preserved — please try again.", 
    timestamp: Date.now() 
  }]);
}, 6000);  // ← TOO SHORT!
```

**Problem**:
- Backend LLM timeout is 30 seconds
- Frontend times out at 6 seconds
- Users see timeout errors on complex queries
- Backend continues processing (wasted resources)

**Fix**:
```typescript
}, 35000);  // 35 seconds (30s backend + 5s buffer)
```

**Impact**: Prevents premature timeout errors

---

### Issue 2: detailRecords Not Sent from Frontend

**Current Code** (frontend/src/components/CopilotPanel.tsx):
```typescript
const res = await fetchExplain({ question: question.trim(), context });
```

**Problem**:
- Frontend context may not include detailRecords
- Backend has to load from snapshot (adds latency)
- Snapshot load can fail if not refreshed

**Fix**:
```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data?.detailRecords || []  // Include records
  }
});
```

**Impact**: Faster response, no snapshot dependency

---

### Issue 3: No Conversation History

**Current**: Each question is independent
```
User: "Hi"
Backend: "Hello!"

User: "What about health?"
Backend: Doesn't know this is follow-up
```

**Problem**:
- LLM can't understand follow-up questions
- No context from previous messages
- Each question treated as standalone

**Fix**:
```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  conversation_history: messages.map(m => ({
    role: m.role,
    content: m.content
  }))
});
```

**Backend Update**:
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    question = body.get("question", "").strip()
    context = body.get("context", {})
    conversation_history = body.get("conversation_history", [])
    
    # Pass to LLM
    llm_service.generate_response(
        prompt=question,
        context=context,
        detail_records=detail_records,
        conversation_history=conversation_history  # ← NEW
    )
```

**Impact**: Better understanding of follow-up questions

---

### Issue 4: No Session Tracking

**Current**: No way to identify user or conversation

**Problem**:
- Can't track user across requests
- Can't maintain conversation state
- Can't debug which user had issues

**Fix - Frontend**:
```typescript
// Generate session ID on first load
const getOrCreateSessionId = () => {
  let sessionId = sessionStorage.getItem("copilot_session_id");
  if (!sessionId) {
    sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem("copilot_session_id", sessionId);
  }
  return sessionId;
};

// Use in request
const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  session_id: getOrCreateSessionId()
});
```

**Fix - Backend**:
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    session_id = body.get("session_id", "unknown")
    
    logging.info(f"Session {session_id}: Processing question: {question}")
```

**Impact**: Better tracking and debugging

---

### Issue 5: No Request Correlation

**Current**: No way to link frontend and backend logs

**Problem**:
- Hard to debug issues across requests
- Can't trace request through system
- No correlation between frontend and backend logs

**Fix - Frontend**:
```typescript
const generateCorrelationId = () => {
  return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  correlation_id: generateCorrelationId()
});
```

**Fix - Backend**:
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    correlation_id = body.get("correlation_id", "unknown")
    
    logging.info(f"[{correlation_id}] Processing question: {question}")
    # ... rest of processing ...
    logging.info(f"[{correlation_id}] Response generated")
```

**Impact**: Better debugging and tracing

---

## Implementation Priority

### Phase 1: Critical (Do Before Deployment)

1. **Fix Frontend Timeout** (5 minutes)
   - Change 6000ms to 35000ms
   - Test with complex queries
   - Verify no premature timeouts

2. **Pass detailRecords** (10 minutes)
   - Include records in context
   - Verify backend receives them
   - Test response time improvement

### Phase 2: Important (Do After Deployment)

3. **Add Conversation History** (30 minutes)
   - Pass messages to backend
   - Update LLM service to use history
   - Test follow-up questions

4. **Add Session Tracking** (20 minutes)
   - Generate session ID
   - Pass with requests
   - Log session ID in backend

### Phase 3: Nice to Have (Future)

5. **Add Request Correlation** (15 minutes)
   - Generate correlation ID
   - Pass with requests
   - Log in backend

6. **Persist Conversation** (30 minutes)
   - Store in localStorage
   - Recover on page refresh
   - Optional backend storage

---

## Testing Checklist

### Phase 1 Testing

- [ ] Test simple greeting ("Hi") - should complete in <2s
- [ ] Test complex query - should complete in <30s
- [ ] Test timeout - should not timeout at 6s anymore
- [ ] Test detailRecords - verify backend receives them
- [ ] Test response time - should be faster with direct records

### Phase 2 Testing

- [ ] Test follow-up question - LLM understands context
- [ ] Test conversation history - messages passed correctly
- [ ] Test session ID - logged in backend
- [ ] Test multiple users - separate sessions

### Phase 3 Testing

- [ ] Test correlation ID - links frontend and backend logs
- [ ] Test conversation persistence - survives page refresh
- [ ] Test backend storage - conversations saved

---

## Code Changes Summary

### Frontend Changes

**File**: `frontend/src/components/CopilotPanel.tsx`

```typescript
// Change 1: Increase timeout
}, 35000);  // was 6000

// Change 2: Include detailRecords
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data?.detailRecords || []
  }
});

// Change 3: Add session ID
const getOrCreateSessionId = () => {
  let sessionId = sessionStorage.getItem("copilot_session_id");
  if (!sessionId) {
    sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem("copilot_session_id", sessionId);
  }
  return sessionId;
};

// Change 4: Add correlation ID
const generateCorrelationId = () => {
  return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Change 5: Pass all to backend
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data?.detailRecords || []
  },
  session_id: getOrCreateSessionId(),
  correlation_id: generateCorrelationId(),
  conversation_history: messages.map(m => ({
    role: m.role,
    content: m.content
  }))
});
```

### Backend Changes

**File**: `planning_intelligence/function_app.py`

```python
# Change 1: Accept new fields
def explain(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    question = body.get("question", "").strip()
    context = body.get("context", {})
    session_id = body.get("session_id", "unknown")
    correlation_id = body.get("correlation_id", "unknown")
    conversation_history = body.get("conversation_history", [])
    
    # Change 2: Log with correlation ID
    logging.info(f"[{correlation_id}] Session {session_id}: Question: {question}")
    
    # Change 3: Pass to LLM
    llm_service.generate_response(
        prompt=question,
        context=context,
        detail_records=detail_records,
        conversation_history=conversation_history
    )
```

---

## Deployment Strategy

### Before Deployment

1. ✓ Fix greeting detection (DONE)
2. ✓ Update all answer functions (DONE)
3. ✓ Remove duplicate functions (DONE)
4. ✓ Verify no syntax errors (DONE)
5. **→ Fix frontend timeout (CRITICAL)**
6. **→ Pass detailRecords (CRITICAL)**

### After Deployment

7. Monitor for timeout errors
8. Verify response times improved
9. Add conversation history (Phase 2)
10. Add session tracking (Phase 2)

---

## Risk Assessment

### Phase 1 Changes (Low Risk)

- Timeout increase: No breaking changes
- detailRecords: Backward compatible
- Both are additive changes

### Phase 2 Changes (Medium Risk)

- Conversation history: Requires LLM update
- Session tracking: Requires backend logging
- Test thoroughly before production

### Phase 3 Changes (Low Risk)

- Correlation ID: Logging only
- Conversation persistence: Frontend only
- No backend changes required

---

## Success Criteria

### Phase 1

- ✓ No timeout errors on complex queries
- ✓ Response time < 5 seconds for simple queries
- ✓ Response time < 30 seconds for complex queries
- ✓ detailRecords received by backend

### Phase 2

- ✓ Follow-up questions understood correctly
- ✓ Session ID logged in backend
- ✓ Conversation history passed to LLM
- ✓ LLM uses history for context

### Phase 3

- ✓ Correlation ID links frontend and backend logs
- ✓ Conversation persists on page refresh
- ✓ Backend stores conversations (optional)

---

## Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Fix timeout | 5 min | TODO |
| 1 | Pass detailRecords | 10 min | TODO |
| 1 | Test Phase 1 | 15 min | TODO |
| 1 | Deploy | 5 min | TODO |
| 2 | Add conversation history | 30 min | TODO |
| 2 | Add session tracking | 20 min | TODO |
| 2 | Test Phase 2 | 20 min | TODO |
| 3 | Add correlation ID | 15 min | TODO |
| 3 | Persist conversation | 30 min | TODO |

**Total Phase 1**: ~35 minutes
**Total Phase 2**: ~70 minutes
**Total Phase 3**: ~45 minutes

---

## Conclusion

**Current State**: Working but with limitations
- Timeout too short
- Missing context
- No conversation history
- No session tracking

**After Phase 1**: Production-ready
- Proper timeout handling
- Full context passed
- Better response times

**After Phase 2**: Enhanced
- Conversation history
- Session tracking
- Better debugging

**After Phase 3**: Optimized
- Request correlation
- Conversation persistence
- Full traceability

