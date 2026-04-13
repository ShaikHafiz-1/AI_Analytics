# Critical Fixes Required Before Deployment

## Summary

Two critical issues must be fixed before deployment:

1. **Frontend timeout too short** (6 seconds → 35 seconds)
2. **detailRecords not sent from frontend** (add to context)

These are quick fixes that will prevent timeout errors and improve response times.

---

## Fix 1: Frontend Timeout (5 minutes)

### File: `frontend/src/components/CopilotPanel.tsx`

### Current Code (Line ~90):
```typescript
const timeoutId = setTimeout(() => {
  setLoading(false);
  setInput(question.trim());
  setMessages((prev) => [...prev, { role: "assistant", content: "⏱ Request timed out. Your question has been preserved — please try again.", timestamp: Date.now() }]);
}, 6000);  // ← 6 seconds
```

### Fixed Code:
```typescript
const timeoutId = setTimeout(() => {
  setLoading(false);
  setInput(question.trim());
  setMessages((prev) => [...prev, { role: "assistant", content: "⏱ Request timed out. Your question has been preserved — please try again.", timestamp: Date.now() }]);
}, 35000);  // ← 35 seconds (30s backend + 5s buffer)
```

### Why:
- Backend LLM timeout: 30 seconds
- Frontend timeout: 6 seconds (too short!)
- Result: Users see timeout errors on complex queries
- Fix: Increase to 35 seconds to allow backend to complete

### Testing:
```
Test 1: Simple greeting "Hi"
  Expected: Response in <2 seconds
  
Test 2: Complex query "What are the top risks?"
  Expected: Response in 5-10 seconds
  
Test 3: Very complex query with multiple conditions
  Expected: Response in 15-30 seconds (no timeout)
```

---

## Fix 2: Pass detailRecords from Frontend (10 minutes)

### File: `frontend/src/components/CopilotPanel.tsx`

### Current Code (Line ~96):
```typescript
const res = await fetchExplain({ question: question.trim(), context });
```

### Fixed Code:
```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data?.detailRecords || []  // ← Add this line
  }
});
```

### Why:
- Frontend builds context from DashboardResponse
- DashboardResponse may not include detailRecords
- Backend has to load from snapshot (adds latency)
- Fix: Include records directly in context

### Impact:
- **Before**: Backend loads from snapshot (1-2 seconds)
- **After**: Backend uses provided records (immediate)
- **Result**: 1-2 second faster response

### Testing:
```
Test 1: Check backend logs
  Expected: "Processing question with 13148 records"
  
Test 2: Measure response time
  Expected: 1-2 seconds faster than before
  
Test 3: Verify records are used
  Expected: LLM has full context
```

---

## Implementation Steps

### Step 1: Fix Timeout

1. Open `frontend/src/components/CopilotPanel.tsx`
2. Find line with `}, 6000);`
3. Change to `}, 35000);`
4. Save file

### Step 2: Fix detailRecords

1. Open `frontend/src/components/CopilotPanel.tsx`
2. Find line with `const res = await fetchExplain({ question: question.trim(), context });`
3. Replace with:
```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data?.detailRecords || []
  }
});
```
4. Save file

### Step 3: Test Locally

```bash
# Start frontend
cd frontend
npm start

# In another terminal, start backend
cd planning_intelligence
func start

# Test in browser
# 1. Type "Hi" - should respond in <2s
# 2. Type "What are the risks?" - should respond in <10s
# 3. Type complex query - should not timeout
```

### Step 4: Deploy

```bash
# Deploy frontend (if using Blob Storage)
cd frontend
npm run build
# Upload build/ to Blob Storage

# Deploy backend
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence --build remote
```

---

## Verification Checklist

### Before Deployment

- [ ] Timeout changed from 6000 to 35000
- [ ] detailRecords added to context
- [ ] No syntax errors
- [ ] Local testing passed
- [ ] Simple queries respond in <2s
- [ ] Complex queries respond in <30s
- [ ] No premature timeouts

### After Deployment

- [ ] Test "Hi" in production
- [ ] Test "What's the health?" in production
- [ ] Test complex query in production
- [ ] Monitor Azure logs for errors
- [ ] Verify response times improved
- [ ] No timeout errors in logs

---

## Rollback Plan

If issues occur:

```bash
# Revert frontend
git checkout frontend/src/components/CopilotPanel.tsx

# Revert backend (if needed)
git checkout planning_intelligence/function_app.py

# Redeploy
npm run build  # frontend
func azure functionapp publish pi-planning-intelligence --build remote  # backend
```

---

## Expected Results

### Before Fixes

```
User: "Hi"
Response time: 1-2 seconds ✓

User: "What are the top risks?"
Response time: 5-10 seconds ✓

User: "Complex query with multiple conditions"
Response time: 15-20 seconds
Frontend timeout at 6 seconds ✗
User sees: "Request timed out"
Backend continues processing (wasted)
```

### After Fixes

```
User: "Hi"
Response time: 1-2 seconds ✓

User: "What are the top risks?"
Response time: 4-8 seconds ✓ (1-2s faster)

User: "Complex query with multiple conditions"
Response time: 12-18 seconds ✓ (1-2s faster)
Frontend timeout at 35 seconds ✓
No premature timeouts ✓
```

---

## Code Diff

### CopilotPanel.tsx Changes

```diff
- const res = await fetchExplain({ question: question.trim(), context });
+ const res = await fetchExplain({ 
+   question: question.trim(), 
+   context: {
+     ...context,
+     detailRecords: data?.detailRecords || []
+   }
+ });

- }, 6000);
+ }, 35000);
```

---

## Why These Fixes Are Critical

### Fix 1: Timeout

**Without**: Users see timeout errors on complex queries
**With**: All queries complete successfully

**Impact**: Prevents user frustration and support tickets

### Fix 2: detailRecords

**Without**: Backend loads from snapshot (slower, may fail)
**With**: Backend uses provided records (faster, reliable)

**Impact**: 1-2 second faster response, more reliable

---

## Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Fix timeout | 2 min | TODO |
| Fix detailRecords | 3 min | TODO |
| Local testing | 10 min | TODO |
| Deploy frontend | 5 min | TODO |
| Deploy backend | 5 min | TODO |
| Verify in production | 5 min | TODO |
| **Total** | **30 min** | **TODO** |

---

## Success Criteria

✓ Timeout changed to 35 seconds
✓ detailRecords included in context
✓ No syntax errors
✓ Simple queries: <2 seconds
✓ Complex queries: <30 seconds
✓ No premature timeouts
✓ Response time improved by 1-2 seconds
✓ All tests passing

---

## Questions?

If you have questions about these fixes:

1. **Why 35 seconds?**
   - Backend timeout: 30 seconds
   - Buffer: 5 seconds
   - Total: 35 seconds

2. **Why include detailRecords?**
   - Faster: No snapshot load needed
   - Reliable: Direct data from frontend
   - Better: LLM has full context immediately

3. **Will this break anything?**
   - No: Both changes are backward compatible
   - No: No API changes
   - No: No breaking changes

4. **When should we deploy?**
   - After these fixes are applied
   - After local testing passes
   - Before production use

---

## Next Steps

1. Apply Fix 1 (timeout)
2. Apply Fix 2 (detailRecords)
3. Test locally
4. Deploy to production
5. Monitor for issues
6. After deployment: Add Phase 2 features (conversation history, session tracking)

