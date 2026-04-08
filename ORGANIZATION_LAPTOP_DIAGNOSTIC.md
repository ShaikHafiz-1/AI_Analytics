# Organization Laptop - Diagnostic & Troubleshooting

## 🔍 Common Issues & Solutions

### Issue 1: Running `func start` from Wrong Folder

**Problem**: You ran `func start` from the root folder instead of `planning_intelligence` folder

**Solution**:
```bash
# WRONG ❌
cd AI_Analytics
func start

# CORRECT ✅
cd AI_Analytics\planning_intelligence
func start
```

**Why**: Azure Functions looks for `function_app.py` in the current directory. It must be run from `planning_intelligence` folder.

---

### Issue 2: Backend Not Starting

**Symptoms**:
- `func start` shows errors
- No "Http Functions" output
- Port 7071 not responding

**Solutions**:

**Check 1: Verify you're in the right folder**
```bash
# Should show function_app.py
dir function_app.py

# If not found, you're in wrong folder
cd planning_intelligence
dir function_app.py
```

**Check 2: Verify Azure Functions Core Tools is installed**
```bash
func --version
```

Should show: `Azure Functions Core Tools 4.x.x`

If not installed:
```bash
# Windows
choco install azure-functions-core-tools-4

# macOS
brew install azure-functions-core-tools@4
```

**Check 3: Check if port 7071 is already in use**
```bash
# Windows PowerShell
netstat -ano | findstr :7071

# If port is in use, use different port:
func start --port 7072
```

---

### Issue 3: BLOB_CONNECTION_STRING Not Found

**Symptoms**:
```
ERROR Blob data load failed: Missing required environment variable: BLOB_CONNECTION_STRING
```

**Solutions**:

**Check 1: Verify `func start` is running**
- Terminal 1 should show "Http Functions" output
- If not, start it first

**Check 2: Verify `local.settings.json` exists**
```bash
# Should show the file
dir planning_intelligence\local.settings.json
```

**Check 3: Run from correct terminal**
- Terminal 1: `func start` (loads environment variables)
- Terminal 2: `python run_daily_refresh.py` (uses loaded variables)

---

### Issue 4: planning_snapshot.json Not Created

**Symptoms**:
- `python run_daily_refresh.py` runs but no snapshot file created
- Tests fail with "No cached snapshot"

**Solutions**:

**Check 1: Set SNAPSHOT_FILE_PATH environment variable**
```bash
# Windows Command Prompt
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py

# Windows PowerShell
$env:SNAPSHOT_FILE_PATH="$(Get-Location)\planning_snapshot.json"
python run_daily_refresh.py
```

**Check 2: Verify file was created**
```bash
# Windows
dir planning_snapshot.json

# Should show file exists and is several MB
```

**Check 3: Check for errors in Terminal 1**
- Look at Terminal 1 (where `func start` is running)
- Check for any error messages

---

### Issue 5: Tests Failing

**Symptoms**:
```
FAIL: [1] List suppliers for CYS20_F01C01
Error: Connection refused
```

**Solutions**:

**Check 1: Verify backend is running**
```bash
# In Terminal 1, should see:
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

**Check 2: Verify snapshot file exists**
```bash
dir planning_snapshot.json
```

**Check 3: Test backend manually**
```bash
# In Terminal 3, test the API
curl http://localhost:7071/api/explain -X POST -H "Content-Type: application/json" -d "{\"question\":\"What is the current planning health?\"}"
```

---

## ✅ Correct Setup Procedure

### Terminal 1: Start Backend
```bash
cd planning_intelligence
func start
```

**Wait for output**:
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

**Keep this terminal open** ✅

---

### Terminal 2: Load Data (NEW WINDOW)
```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
```

**Expected output**:
```
✅ Data loaded successfully
✅ Snapshot saved to C:\...\planning_snapshot.json
```

---

### Terminal 3: Run Tests (NEW WINDOW)
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

**Expected output**:
```
Total prompts: 44
Passed: 44
Failed: 0
Pass rate: 100.0%
```

---

## 🔧 Restart Procedure

If things aren't working, try a clean restart:

### Step 1: Stop All Terminals
- Close Terminal 1 (func start)
- Close Terminal 2 (if running)
- Close Terminal 3 (if running)

### Step 2: Clean Up
```bash
# Delete old snapshot file
cd planning_intelligence
del planning_snapshot.json
```

### Step 3: Start Fresh
Follow the "Correct Setup Procedure" above

---

## 📋 Verification Checklist

Before running tests, verify:

- [ ] You're in `planning_intelligence` folder
- [ ] Terminal 1: `func start` is running and shows "Http Functions"
- [ ] Terminal 1: No error messages
- [ ] Terminal 2: `SNAPSHOT_FILE_PATH` environment variable is set
- [ ] Terminal 2: `python run_daily_refresh.py` completed successfully
- [ ] Terminal 2: `planning_snapshot.json` file exists
- [ ] Terminal 3: Backend is responding (Terminal 1 still running)
- [ ] Terminal 3: Tests show 44/44 passing

---

## 🚀 Quick Restart Commands

```bash
# Terminal 1
cd planning_intelligence
func start

# Terminal 2 (NEW WINDOW)
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py

# Terminal 3 (NEW WINDOW)
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

---

**Status**: ✅ Diagnostic Guide Ready
**Most Common Issue**: Running `func start` from wrong folder
**Solution**: Always run from `planning_intelligence` folder
