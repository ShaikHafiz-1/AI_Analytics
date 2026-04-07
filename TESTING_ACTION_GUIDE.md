# Testing Action Guide

## What Was Fixed

The regex pattern for extracting location IDs in comparison queries was too restrictive. It couldn't match location IDs like `CMH02_F01C01`.

**Old Pattern**: `[A-Z]{2,}\d+_[A-Z0-9]+` (required 2+ uppercase letters)
**New Pattern**: `[A-Z]+\d+_[A-Z0-9]+` (allows 1+ uppercase letters)

Now matches:
- `CMH02_F01C01` ✓
- `AVC11_F01C01` ✓
- `LOC001` ✓

---

## What to Do Now

### Step 1: Restart the Backend

```bash
# Stop func start (Ctrl+C)

# Then restart:
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
func start
```

### Step 2: Test All 44 Prompts

Use the **FULL_TESTING_CHECKLIST.md** to test all prompts systematically.

**Quick Start** (test these first):
1. `List suppliers for AVC11_F01C01` - Should return supplier list
2. `Compare LOC001 vs LOC002` - Should return side-by-side comparison
3. `Why is AVC11_F01C01 risky?` - Should return risk analysis
4. `Show top contributing records` - Should return top records

### Step 3: Document Results

Mark each prompt as PASS or FAIL in the checklist.

### Step 4: Calculate Pass Rate

Count passes and calculate percentage.

---

## Expected Results

### ✓ PASS Criteria
- Response is relevant to the query
- Response includes data/metrics
- Response time < 500ms
- No errors in logs

### ✗ FAIL Criteria
- Response is generic/fallback
- Response has no data
- Response time > 500ms
- Errors in logs

---

## Success Threshold

✓ **SUCCESS** if pass rate >= 90% (40+ out of 44 prompts)

---

## Testing Timeline

- Restart backend: 1-2 minutes
- Test all 44 prompts: 15-20 minutes
- Document results: 5 minutes

**Total: ~20-30 minutes**

---

## Key Prompts to Test First

### Supplier Queries
```
List suppliers for AVC11_F01C01
```
Expected: Supplier list with metrics

### Comparison Queries
```
Compare LOC001 vs LOC002
```
Expected: Side-by-side comparison table

### Root Cause Queries
```
Why is AVC11_F01C01 risky?
```
Expected: Risk analysis with drivers

### Traceability Queries
```
Show top contributing records
```
Expected: Top records with impact

---

## If a Prompt Fails

1. **Check the response** - Is it generic or specific?
2. **Check the logs** - Are there errors?
3. **Try a similar prompt** - Does the category work?
4. **Note the issue** - Document in the checklist

---

## Troubleshooting

### If Comparison Query Returns Global Metrics
- The regex fix should resolve this
- Restart the backend
- Try again

### If Supplier Query Returns "No supplier information found"
- Check if the location exists
- Try a different location
- Check the logs

### If Response Time is Slow
- Check backend logs
- Verify no errors
- Try a simpler query

---

## Next Steps

1. **Restart backend** with the regex fix
2. **Test all 44 prompts** using the checklist
3. **Document results** with pass/fail for each
4. **Calculate pass rate**
5. **Report findings**

---

## Summary

**What Changed**: Regex pattern for location ID extraction
**Why**: To support location IDs like CMH02_F01C01
**Expected Impact**: Comparison queries now work correctly
**Testing**: Use FULL_TESTING_CHECKLIST.md to verify all prompts

---

**Ready to test? Start with Step 1: Restart the backend!**
