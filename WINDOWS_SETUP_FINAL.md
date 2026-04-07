# Windows Organization Laptop - Final Setup

## 🎯 Your Issue
`planning_snapshot.json` is not being created in the right location on Windows.

## ✅ Solution: 3 Terminals with Environment Variable

### Terminal 1: Start Backend
```bash
cd planning_intelligence
func start
```

**Wait for**:
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

**Keep this open** ✅

---

### Terminal 2: Load Data (NEW WINDOW)

**Copy and paste this EXACTLY**:

```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
```

**Expected output**:
```
2026-04-07 23:31:08,197 INFO Starting daily planning refresh from Blob Storage...
✅ Data loaded successfully
✅ Snapshot saved to C:\Users\...\planning_intelligence\planning_snapshot.json
```

**Verify file was created**:
```bash
dir planning_snapshot.json
```

Should show: `planning_snapshot.json` file exists

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

## 🎯 Key Points

1. **Terminal 1**: `func start` - Keep it running
2. **Terminal 2**: Set `SNAPSHOT_FILE_PATH` environment variable BEFORE running `python run_daily_refresh.py`
3. **Terminal 3**: Run tests

---

## 📋 Step-by-Step Checklist

- [ ] Terminal 1: `func start` running
- [ ] Terminal 2: Set `SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json`
- [ ] Terminal 2: Run `python run_daily_refresh.py`
- [ ] Terminal 2: See "Snapshot saved to..." message
- [ ] Terminal 2: Verify file with `dir planning_snapshot.json`
- [ ] Terminal 3: Run `python test_all_44_prompts_CORRECTED.py`
- [ ] Terminal 3: See "Pass rate: 100.0%"

---

## 🆘 If File Still Doesn't Exist

### Check 1: Verify Environment Variable is Set
```bash
echo %SNAPSHOT_FILE_PATH%
```

Should show: `C:\Users\...\planning_intelligence\planning_snapshot.json`

### Check 2: Verify Directory Exists
```bash
cd planning_intelligence
dir
```

Should show: `planning_intelligence` folder contents

### Check 3: Check /tmp Folder
```bash
dir C:\tmp\planning_snapshot.json
```

If file exists here, it means the environment variable wasn't set correctly.

---

## 📝 Complete Command Sequence

Copy and paste these commands in order:

**Terminal 1**:
```bash
cd planning_intelligence
func start
```

**Terminal 2** (NEW WINDOW):
```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
dir planning_snapshot.json
```

**Terminal 3** (NEW WINDOW):
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

---

## ✨ Expected Result

After following these steps:
- ✅ `planning_snapshot.json` created in `planning_intelligence` folder
- ✅ All 44 prompts working
- ✅ Test results: 44/44 passing (100%)

---

**Status**: ✅ Ready to Setup
**Time Required**: ~5 minutes
**Expected Result**: 44/44 prompts working
