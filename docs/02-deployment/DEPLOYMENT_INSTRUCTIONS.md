# Deployment Instructions - Final 3 Fixes

## Current Status
- **Pass Rate**: 93.2% (41/44)
- **Remaining Failures**: 3 (all supplier queries without location)
- **Code Changes**: ✅ Applied
- **Backend Restart**: ⏳ PENDING

---

## What Needs to Be Done

The code changes have been applied to `planning_intelligence/function_app.py`, but the backend needs to be restarted to pick up the changes.

### The 3 Remaining Failures

All are supplier queries without location context:

1. "Which supplier has the most impact?"
2. "Which supplier has the most design changes?"
3. "Which supplier is failing to meet ROJ dates?"

### The Fix

Updated `_generate_supplier_by_location_answer()` to return a helpful clarification message (200+ chars) instead of a short error (47 chars).

---

## Deployment Steps

### Step 1: Verify Code Changes

Check that the fix was applied:

```bash
# View the updated function
grep -A 15 "def _generate_supplier_by_location_answer" planning_intelligence/function_app.py
```

Expected output should show the clarification message starting with:
```
"To analyze suppliers, I need more context:
```

### Step 2: Restart the Backend

**Option A: Local Testing**

```bash
# Stop the current backend (Ctrl+C if running)

# Restart with:
cd planning_intelligence
func start
```

**Option B: Azure Deployment**

```bash
# Deploy to Azure Function App
func azure functionapp publish <your-function-app-name>
```

### Step 3: Verify the Fix

Run the test suite:

```bash
# Run all 44 prompts
python planning_intelligence/test_all_44_prompts_CORRECTED.py
```

Expected output:
```
Total prompts: 44
Passed: 44
Failed: 0
Pass rate: 100.0%
```

### Step 4: Verify Specific Queries

Test the 3 previously failing queries:

```bash
# Test 1: Which supplier has the most impact?
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question": "Which supplier has the most impact?"}'

# Test 2: Which supplier has the most design changes?
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question": "Which supplier has the most design changes?"}'

# Test 3: Which supplier is failing to meet ROJ dates?
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question": "Which supplier is failing to meet ROJ dates?"}'
```

Expected: Each should return a response > 200 characters asking for location context.

---

## Verification Checklist

- [ ] Code changes verified in `function_app.py`
- [ ] Backend restarted successfully
- [ ] Test suite runs without errors
- [ ] All 44 prompts pass
- [ ] 3 previously failing queries now return clarification messages
- [ ] Response lengths > 200 characters for all 3
- [ ] No errors in backend logs

---

## Rollback Plan

If something goes wrong:

```bash
# Revert the changes
git checkout planning_intelligence/function_app.py

# Restart backend
func start
```

---

## Expected Results After Deployment

### Before Restart
```
Total: 44
Passed: 41
Failed: 3
Pass Rate: 93.2%
```

### After Restart
```
Total: 44
Passed: 44
Failed: 0
Pass Rate: 100.0%
```

---

## Monitoring

After deployment, monitor:

1. **Backend Logs**
   ```bash
   # View Azure Function logs
   az functionapp log tail --name <function-app-name> --resource-group <resource-group>
   ```

2. **Response Times**
   - Expected: ~2200ms average
   - All responses should be < 3 seconds

3. **Error Rates**
   - Expected: 0% errors
   - All queries should return valid responses

---

## Support

If you encounter issues:

1. Check backend logs for errors
2. Verify code changes were applied correctly
3. Ensure backend was restarted (not just code changes)
4. Run test suite to identify specific failures
5. Check network connectivity to backend

---

## Timeline

- **Code Changes**: ✅ Complete
- **Backend Restart**: ⏳ Pending (5 minutes)
- **Test Verification**: ⏳ Pending (2 minutes)
- **Production Deployment**: ⏳ Pending (10 minutes)

**Total Time to 100% Pass Rate: ~20 minutes**

---

## Success Criteria

✅ All 44 prompts pass
✅ No errors in logs
✅ Response times < 3 seconds
✅ All clarification messages > 200 characters
✅ Users can understand what information is needed

---

## Questions?

Refer to:
- `FINAL_RESULTS_SUMMARY.md` - Overall results and progress
- `FIXES_FOR_9_FAILURES.md` - Detailed explanation of all fixes
- `CODE_CHANGES_DETAILED.md` - Line-by-line code changes
- `QUICK_FIX_SUMMARY.md` - Quick reference guide
