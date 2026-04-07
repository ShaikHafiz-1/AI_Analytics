# Organization Laptop - Final Setup (Step by Step)

## 🎯 Your Current Issue
```
ERROR: Missing required environment variable: BLOB_CONNECTION_STRING
```

## ✅ Solution: Follow These Steps Exactly

### Step 1: Open Terminal 1
```bash
cd planning_intelligence
func start
```

**Wait for this output**:
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

**Keep this terminal open** ✅

---

### Step 2: Open Terminal 2 (NEW WINDOW)
```bash
cd planning_intelligence
python run_daily_refresh.py
```

**Expected output**:
```
2026-04-07 23:31:08,197 INFO Starting daily planning refresh from Blob Storage...
✅ Data loaded successfully
✅ Snapshot created: planning_snapshot.json
```

**If you see this, you're done with data loading** ✅

---

### Step 3: Open Terminal 3 (NEW WINDOW)
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

**If you see this, all prompts are working** ✅

---

## 🎯 What Each Terminal Does

| Terminal | Command | Purpose | Keep Open? |
|----------|---------|---------|-----------|
| Terminal 1 | `func start` | Loads environment variables | ✅ YES |
| Terminal 2 | `python run_daily_refresh.py` | Generates data snapshot | ❌ NO |
| Terminal 3 | `python test_all_44_prompts_CORRECTED.py` | Tests all prompts | ❌ NO |

---

## 🚨 Important Notes

1. **Terminal 1 must be running first** - This loads the environment variables
2. **Don't close Terminal 1** - Keep it running in the background
3. **Open Terminal 2 and 3 in new windows** - Don't close Terminal 1

---

## 📋 Verification Checklist

After completing all steps:

- [ ] Terminal 1 shows: `Http Functions: explain, daily-refresh`
- [ ] Terminal 2 shows: `✅ Snapshot created: planning_snapshot.json`
- [ ] Terminal 3 shows: `Pass rate: 100.0%`
- [ ] File exists: `planning_intelligence/planning_snapshot.json`

---

## ✨ After This Setup

All 44 prompts will work:
- ✅ Supplier Queries
- ✅ Comparison Queries
- ✅ Record Detail Queries
- ✅ Root Cause Queries
- ✅ Traceability Queries
- ✅ Location Queries
- ✅ Material Group Queries
- ✅ Forecast/Demand Queries
- ✅ Design/BOD Queries
- ✅ Schedule/ROJ Queries
- ✅ Health/Status Queries
- ✅ Action/Recommendation Queries

---

## 🆘 If Something Goes Wrong

### Error: "Port 7071 already in use"
```bash
# Use different port
func start --port 7072
```

### Error: "Module not found"
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Error: "Cannot connect to Blob Storage"
- Check internet connection
- Verify `local.settings.json` has BLOB_CONNECTION_STRING
- Check file: `planning_intelligence/local.settings.json`

---

## 🎯 Quick Reference

```bash
# Terminal 1 (Keep Open)
cd planning_intelligence
func start

# Terminal 2 (New Window)
cd planning_intelligence
python run_daily_refresh.py

# Terminal 3 (New Window)
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

---

**Status**: ✅ Ready to Setup
**Time Required**: ~5 minutes
**Expected Result**: 44/44 prompts working
