# Local Testing Guide - Supplier Query Fix

## Your Setup

You're running:
- **Backend**: `func start` from `planning_intelligence` folder
- **Frontend**: `npm start` from `frontend` folder
- **Location**: D:\MA_Power_Automate\AI_Analytics\AI_Analytics\

This is perfect for testing the fix locally!

---

## The Issue

When you query "List suppliers for AVC11_F01C01", you get:
```
No supplier information found for location AVC11_F01C01
```

**Why**: The Azure Function code has been updated in the files, but `func start` is running the old code from memory.

---

## How to Deploy the Fix Locally

### Step 1: Stop the Running Function

In the terminal where `func start` is running:
```
Press Ctrl+C to stop the function
```

### Step 2: Verify the Code Changes

Check that the files have been updated:

**response_builder.py (Line 148):**
```bash
# From planning_intelligence folder
grep -n "detailRecords.*compared" response_builder.py
# Should show: "detailRecords": [_slim_record(r) for r in compared],
```

**dashboard_builder.py (Line 139):**
```bash
grep -n "detailRecords.*compared" dashboard_builder.py
# Should show: "detailRecords": [_slim_record(r) for r in compared],
```

### Step 3: Restart the Function

```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
func start
```

Wait for the function to start. You should see:
```
Azure Functions Core Tools
Core Tools Version:       4.x.x
Function Runtime Version: 4.x.x

Functions:

    copilot_realtime_answers: [POST] http://localhost:7071/api/copilot_realtime_answers
    copilot_personalization_conversational: [POST] http://localhost:7071/api/copilot_personalization_conversational

For detailed output, run func with --verbose flag.
Listening on 'http://localhost:7071'
```

### Step 4: Test the Query

Open the UI and test:
```
Query: "List suppliers for AVC11_F01C01"
```

**Expected Result (After Fix):**
```
📊 Suppliers at AVC11_F01C01:

Supplier             Records    Changed    Forecast     Design     Avail  ROJ    Risk
────────────────────────────────────────────────────────────────────────────────
SUP-A                15         8          +450         8 (53%)    2      3      High
SUP-B                12         5          +300         5 (42%)    1      2      Medium
```

**If Still Getting "No supplier information found":**
- The code changes may not have been saved
- Check the files again
- Verify line 148 in response_builder.py uses `compared`
- Verify line 139 in dashboard_builder.py uses `compared`

---

## Checking the Logs

When `func start` is running, you should see DEBUG messages:

```
DEBUG: Supplier query for location: AVC11_F01C01
DEBUG: Total detail_records before normalization: [should be > 0]
DEBUG: Total detail_records after normalization: [should be > 0]
DEBUG: Unique locations in data: {'AVC11_F01C01', 'LOC001', ...}
DEBUG: Found X suppliers for location AVC11_F01C01: ['SUP-A', 'SUP-B', ...]
```

If you don't see these DEBUG messages, the old code is still running.

---

## Testing All Query Types

After the supplier query works, test these:

### 1. Comparison Query
```
Query: "Compare LOC001 vs LOC002"
Expected: Side-by-side comparison of metrics
```

### 2. Record Detail Query
```
Query: "What changed for MAT-001?"
Expected: Current vs previous values
```

### 3. Root Cause Query
```
Query: "Why is AVC11_F01C01 risky?"
Expected: Analysis of risk factors
```

### 4. Traceability Query
```
Query: "Show top contributing records"
Expected: List of top records with impact
```

---

## Troubleshooting

### Issue: Still Getting "No supplier information found"

**Solution 1: Verify Code Changes**
```bash
# Check response_builder.py line 148
cd planning_intelligence
grep -A2 -B2 "detailRecords.*slim_record" response_builder.py | head -10
# Should show: [_slim_record(r) for r in compared],
```

**Solution 2: Check File Timestamps**
```bash
# Verify files were recently modified
ls -la response_builder.py dashboard_builder.py
# Should show recent modification times
```

**Solution 3: Clear Python Cache**
```bash
# Remove Python cache
rm -r planning_intelligence/__pycache__
rm -r planning_intelligence/mcp/__pycache__
rm -r planning_intelligence/tests/__pycache__

# Restart func start
func start
```

**Solution 4: Check for Syntax Errors**
```bash
# Run Python syntax check
python3 -m py_compile planning_intelligence/response_builder.py
python3 -m py_compile planning_intelligence/dashboard_builder.py
python3 -m py_compile planning_intelligence/function_app.py

# If no output, syntax is OK
```

### Issue: Getting Different Error

**Check the logs** for the error message and stack trace.

**Run diagnostics:**
```bash
cd planning_intelligence
python3 diagnose_data.py
```

**Run tests:**
```bash
cd planning_intelligence
python3 -m pytest tests/ -v
```

---

## Local Testing Workflow

1. **Stop func start** (Ctrl+C)
2. **Verify code changes** are in the files
3. **Clear Python cache** (optional but recommended)
4. **Restart func start**
5. **Test the query** in the UI
6. **Check the logs** for DEBUG messages
7. **Verify response** includes suppliers

---

## Files to Check

### response_builder.py (Line 148)
```python
# Should be:
"detailRecords": [_slim_record(r) for r in compared],

# NOT:
"detailRecords": [_slim_record(r) for r in changed],
```

### dashboard_builder.py (Line 139)
```python
# Should be:
"detailRecords": [_slim_record(r) for r in compared],

# NOT:
"detailRecords": [_slim_record(r) for r in changed],
```

### function_app.py
Should have:
- `_normalize_detail_records()` function
- DEBUG logging in `_generate_supplier_by_location_answer()`
- Updated query handlers

---

## Success Indicators

✓ Supplier query returns suppliers (not "No supplier information found")
✓ DEBUG logs show detailRecords count > 0
✓ All query types work correctly
✓ Response time < 500ms
✓ No errors in logs

---

## Next Steps

1. **Stop func start** (Ctrl+C)
2. **Verify code changes** in the files
3. **Restart func start**
4. **Test the supplier query**
5. **Check the logs**
6. **Verify the response**

If everything works locally, the fix is ready for production deployment!

---

## Questions?

- **How to verify code changes?** See the grep commands above
- **How to clear Python cache?** See the rm commands above
- **How to run diagnostics?** Run `python3 diagnose_data.py`
- **How to run tests?** Run `python3 -m pytest tests/ -v`
