# Fix: BLOB_CONNECTION_STRING Missing Error

## 🔍 Problem
When running `python run_daily_refresh.py`, you get:
```
ERROR Blob data load failed: Missing required environment variable: BLOB_CONNECTION_STRING
```

## ✅ Solution

The issue is that `local.settings.json` is NOT automatically loaded when running Python scripts directly. You need to use Azure Functions to load it.

### Option 1: Use Azure Functions (Recommended)
```bash
# Terminal 1: Start Azure Functions (this loads local.settings.json)
cd planning_intelligence
func start
```

### Option 2: Set Environment Variable Manually (Windows)
```bash
# Terminal 2: Set the environment variable from local.settings.json
# Copy the BLOB_CONNECTION_STRING value from planning_intelligence/local.settings.json
set BLOB_CONNECTION_STRING=<your-connection-string-from-local.settings.json>

# Then run the script
python run_daily_refresh.py
```

### Option 3: Set Environment Variable Manually (macOS/Linux)
```bash
# Terminal 2: Set the environment variable from local.settings.json
# Copy the BLOB_CONNECTION_STRING value from planning_intelligence/local.settings.json
export BLOB_CONNECTION_STRING="<your-connection-string-from-local.settings.json>"

# Then run the script
python run_daily_refresh.py
```

---

## 🚀 Recommended Workflow

### Terminal 1: Start Backend (Loads Environment Variables)
```bash
cd planning_intelligence
func start
```

Expected output:
```
Azure Functions Core Tools
Version 4.x.x
...
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

### Terminal 2: Load Data
```bash
cd planning_intelligence
python run_daily_refresh.py
```

Expected output:
```
✅ Data loaded successfully
✅ Snapshot created: planning_snapshot.json
```

### Terminal 3: Run Tests
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

Expected output:
```
Total prompts: 44
Passed: 44
Failed: 0
Pass rate: 100.0%
```

---

## 📝 Why This Happens

- `local.settings.json` is used by Azure Functions runtime
- When you run `func start`, it loads all environment variables from `local.settings.json`
- When you run `python run_daily_refresh.py` directly, it doesn't automatically load `local.settings.json`
- Solution: Either use `func start` first, or manually set the environment variable

---

## ✅ Quick Fix (Copy & Paste for Windows)

```bash
# Terminal 1: Start backend
cd planning_intelligence
func start

# Terminal 2: Load data (in new terminal)
cd planning_intelligence
python run_daily_refresh.py

# Terminal 3: Run tests (in new terminal)
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

---

## 🔐 Where to Find the Connection String

The `BLOB_CONNECTION_STRING` is stored in:
- **File**: `planning_intelligence/local.settings.json`
- **Key**: `Values.BLOB_CONNECTION_STRING`

**Note**: Never commit secrets to git. Always use `func start` to load from `local.settings.json`.

---

## 📊 Expected Results After Fix

After following the steps above:
- ✅ `planning_snapshot.json` will be created
- ✅ All 44 prompts will work
- ✅ Test results: 44/44 passing

---

**Status**: ✅ Solution Provided
**Root Cause**: Environment variable not loaded when running script directly
**Fix**: Use `func start` first or manually set environment variable
**Time to Fix**: ~1 minute
