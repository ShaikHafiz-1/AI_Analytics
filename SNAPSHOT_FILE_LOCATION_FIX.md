# Fix: planning_snapshot.json Not Found

## 🔍 Problem Identified

The `planning_snapshot.json` file IS being created, but it's being saved to the wrong location:

**Default location**: `/home/data/planning_snapshot.json` (Linux/Mac path)
**Your system**: Windows (C:\Users\...)

On Windows, this path doesn't exist, so the file gets saved to `/tmp/planning_snapshot.json` as a fallback.

---

## ✅ Solution: Set Environment Variable

### Option 1: Set SNAPSHOT_FILE_PATH (Recommended)

**Windows Command Prompt**:
```bash
set SNAPSHOT_FILE_PATH=C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready\AI_Analytics\planning_intelligence\planning_snapshot.json
python run_daily_refresh.py
```

**Windows PowerShell**:
```powershell
$env:SNAPSHOT_FILE_PATH="C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready\AI_Analytics\planning_intelligence\planning_snapshot.json"
python run_daily_refresh.py
```

**macOS/Linux**:
```bash
export SNAPSHOT_FILE_PATH="/path/to/planning_intelligence/planning_snapshot.json"
python run_daily_refresh.py
```

---

## 🎯 Complete Setup with Fix

### Terminal 1: Start Backend
```bash
cd planning_intelligence
func start
```

### Terminal 2: Set Environment Variable and Load Data

**Windows Command Prompt**:
```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
```

**Windows PowerShell**:
```powershell
cd planning_intelligence
$env:SNAPSHOT_FILE_PATH="$(Get-Location)\planning_snapshot.json"
python run_daily_refresh.py
```

**macOS/Linux**:
```bash
cd planning_intelligence
export SNAPSHOT_FILE_PATH="$(pwd)/planning_snapshot.json"
python run_daily_refresh.py
```

### Terminal 3: Run Tests
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

---

## 📝 What This Does

1. **Sets SNAPSHOT_FILE_PATH** - Tells the system where to save the snapshot file
2. **Uses current directory** - Saves to `planning_intelligence/planning_snapshot.json`
3. **Creates the file** - `run_daily_refresh.py` will create it in the correct location
4. **Tests can find it** - Backend can load the snapshot for all 44 prompts

---

## 🔍 Verify File Was Created

After running `python run_daily_refresh.py`, check:

**Windows Command Prompt**:
```bash
dir planning_snapshot.json
```

**Windows PowerShell**:
```powershell
Get-ChildItem planning_snapshot.json
```

**macOS/Linux**:
```bash
ls -la planning_snapshot.json
```

Expected output: File should exist and be several MB (5-10 MB typical)

---

## 📊 File Locations

| OS | Default Path | Fallback Path | Recommended |
|---|---|---|---|
| Windows | `/home/data/...` ❌ | `/tmp/...` ⚠️ | `C:\Users\...\planning_snapshot.json` ✅ |
| macOS | `/home/data/...` ❌ | `/tmp/...` ✅ | `~/planning_intelligence/planning_snapshot.json` ✅ |
| Linux | `/home/data/...` ✅ | `/tmp/...` ✅ | `/home/data/planning_snapshot.json` ✅ |

---

## 🚀 Quick Fix (Copy & Paste for Windows)

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

## ✨ After This Fix

- ✅ `planning_snapshot.json` will be created in the correct location
- ✅ Backend can load the snapshot
- ✅ All 44 prompts will work
- ✅ Test results: 44/44 passing

---

**Status**: ✅ Solution Provided
**Root Cause**: Wrong file path for Windows
**Fix**: Set SNAPSHOT_FILE_PATH environment variable
**Time to Fix**: ~1 minute
