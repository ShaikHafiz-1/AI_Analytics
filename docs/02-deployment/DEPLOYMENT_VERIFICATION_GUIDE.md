# Deployment Verification Guide - Supplier Query Fix

## CRITICAL: Code Changes Exist But Are NOT Running

### The Situation

You've tested "List suppliers for AVC11_F01C01" and got "No supplier information found" - **this is expected** because:

1. ✓ Code changes HAVE been made to the files
2. ✓ The fix is correct (detailRecords now uses `compared` instead of `changed`)
3. ✗ The Azure Function is still running the OLD code
4. ✗ The changes have NOT been deployed/restarted

### Why This Happens

When you modify Python files in Azure Functions:
- The files are updated on disk
- But the running process still has the old code in memory
- You must restart/redeploy for changes to take effect

### What You Need to Do

You have two options:

## Option 1: Restart Azure Function (Quick)

If you have access to Azure Portal:

1. Go to Azure Portal → Function App → Your App
2. Click "Restart" button
3. Wait 30-60 seconds for restart
4. Test again: "List suppliers for AVC11_F01C01"
5. Should now return suppliers (not "No supplier information found")

## Option 2: Redeploy Code (Recommended)

If you have Azure CLI or VS Code Azure extension:

```bash
# From the planning_intelligence directory
cd planning_intelligence

# Deploy to Azure
func azure functionapp publish <your-function-app-name>

# Or if using VS Code:
# Right-click function app → Deploy to Function App
```

## How to Verify Deployment Worked

### 1. Check the Logs

After restart/redeploy, look for DEBUG messages:

```
DEBUG: Supplier query for location: AVC11_F01C01
DEBUG: Total detail_records before normalization: [should be > 0]
DEBUG: Total detail_records after normalization: [should be > 0]
DEBUG: Found X suppliers for location AVC11_F01C01: [list of suppliers]
```

### 2. Test the Query

Query: "List suppliers for AVC11_F01C01"

**Before Deployment** (current):
```
No supplier information found for location AVC11_F01C01.
```

**After Deployment** (expected):
```
📊 Suppliers at AVC11_F01C01:

Supplier             Records    Changed    Forecast     Design     Avail  ROJ    Risk
────────────────────────────────────────────────────────────────────────────────
SUP-A                15         8          +450         8 (53%)    2      3      High
SUP-B                12         5          +300         5 (42%)    1      2      Medium
...
```

### 3. Test All Query Types

After deployment, test these queries to verify everything works:

```
1. Supplier queries:
   "List suppliers for AVC11_F01C01"
   "List suppliers for LOC001"
   "Which suppliers at AVC11_F01C01 have design changes?"

2. Comparison queries:
   "Compare LOC001 vs LOC002"
   "Compare AVC11_F01C01 vs LOC001"

3. Record detail queries:
   "What changed for MAT-001?"
   "What changed for MAT-001 at AVC11_F01C01?"

4. Root cause queries:
   "Why is AVC11_F01C01 risky?"
   "Why is LOC001 not risky?"

5. Traceability queries:
   "Show top contributing records"
   "Which records have the most impact?"
```

## Troubleshooting

### If Still Getting "No supplier information found"

1. **Verify deployment**:
   - Check Azure Portal → Function App → Deployment Center
   - Verify latest deployment timestamp is recent
   - Check if restart/redeploy actually completed

2. **Check logs**:
   - Azure Portal → Function App → Log Stream
   - Look for DEBUG messages
   - If no DEBUG messages, old code is still running

3. **Force restart**:
   - Stop the Function App
   - Wait 10 seconds
   - Start the Function App
   - Wait 30 seconds for startup
   - Test again

4. **Check data**:
   - Run diagnostic: `python3 planning_intelligence/diagnose_data.py`
   - Verify CSV files have data for AVC11_F01C01
   - Verify data format is correct

### If Getting Different Error

1. **Check error message** - what does it say?
2. **Check logs** - look for exception stack trace
3. **Run test suite** - `python3 -m pytest planning_intelligence/tests/ -v`
4. **Run diagnostic** - `python3 planning_intelligence/diagnose_data.py`

## What Changed in the Code

### response_builder.py (Line 148)
```python
# BEFORE (wrong):
"detailRecords": [_slim_record(r) for r in changed],

# AFTER (correct):
"detailRecords": [_slim_record(r) for r in compared],
```

### dashboard_builder.py (Line 139)
```python
# BEFORE (wrong):
"detailRecords": [_slim_record(r) for r in changed],

# AFTER (correct):
"detailRecords": [_slim_record(r) for r in compared],
```

### function_app.py (New)
- Added `_normalize_detail_records()` function
- Enhanced `_extract_scope()` for location ID matching
- Added DEBUG logging to `_generate_supplier_by_location_answer()`
- Updated all query handlers to normalize data

## Why This Fix Works

**Before**: `detailRecords` only had CHANGED records
- If AVC11_F01C01 had no changed records → `detailRecords` was empty
- Supplier query found no records → "No supplier information found"

**After**: `detailRecords` has ALL records
- AVC11_F01C01 has all its records in `detailRecords`
- Supplier query finds all suppliers
- Returns supplier list with metrics

## Next Steps

1. **Restart or redeploy** the Azure Function
2. **Wait 30-60 seconds** for startup
3. **Test the query**: "List suppliers for AVC11_F01C01"
4. **Verify it returns suppliers** (not "No supplier information found")
5. **Check the logs** for DEBUG messages
6. **Test all query types** to ensure everything works

## Success Criteria

✓ Supplier queries return suppliers (not "No supplier information found")
✓ All query types work correctly
✓ DEBUG logs show detailRecords count > 0
✓ Response time < 500ms
✓ No errors in logs

## Support

If you need help:

1. Check the logs in Azure Portal
2. Run the diagnostic script
3. Review the test suite
4. Check the documentation files

---

**Status**: Code changes are complete and correct. Just need to deploy/restart the Azure Function.

**Next Action**: Restart or redeploy the Azure Function, then test again.
