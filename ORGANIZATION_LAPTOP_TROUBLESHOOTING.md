# Organization Laptop Troubleshooting - Prompts Not Working

## 🔍 Problem Identified

Some prompts are not working on your organization laptop because the **data snapshot file is missing**.

### What's Missing
- ❌ `planning_intelligence/planning_snapshot.json` - This file is NOT in git (it's generated locally)

### Why This Matters
The system needs this file to:
1. Cache data from Blob Storage
2. Provide fast responses to queries
3. Support all 44 prompts

---

## ✅ Solution: Generate the Missing File

### Step 1: Ensure Backend is Running
```bash
# Terminal 1: Start the backend
cd planning_intelligence
func start
```

Expected output:
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

### Step 2: Load Data (Generate Snapshot)
```bash
# Terminal 2: Load data from Blob Storage
cd planning_intelligence
python run_daily_refresh.py
```

Expected output:
```
✅ Data loaded successfully
✅ Snapshot created: planning_snapshot.json
```

### Step 3: Verify File Was Created
```bash
# Check if file exists
ls -la planning_intelligence/planning_snapshot.json
# or on Windows:
dir planning_intelligence\planning_snapshot.json
```

Expected: File should exist and be several MB in size

### Step 4: Run Tests
```bash
# Terminal 3: Run tests
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

Expected: 44/44 passing ✅

---

## 🔧 Why This Happens

The `planning_snapshot.json` file is:
- ✅ Generated locally when you run `python run_daily_refresh.py`
- ❌ NOT committed to git (it's in .gitignore)
- ❌ NOT transferred when you move the build to a new laptop

**Solution**: Always run `python run_daily_refresh.py` after cloning/moving the build.

---

## 📋 Complete Setup Checklist for Organization Laptop

```bash
# 1. Install dependencies
cd planning_intelligence
pip install -r requirements.txt

# 2. Verify Blob connection
python test_blob_connection.py
# Expected: ✅ Successfully connected to Blob Storage

# 3. Load data (CRITICAL - generates planning_snapshot.json)
python run_daily_refresh.py
# Expected: ✅ Snapshot created: planning_snapshot.json

# 4. Start server (Terminal 1)
func start

# 5. Run tests (Terminal 2)
python test_all_44_prompts_CORRECTED.py
# Expected: 44/44 passing ✅
```

---

## 🚨 If Prompts Still Don't Work After This

Check these:

### 1. Verify Snapshot File Exists
```bash
ls -la planning_intelligence/planning_snapshot.json
```

Should show a file that's several MB (e.g., 5-10 MB)

### 2. Check Backend is Running
```bash
# Should see responses from:
curl http://localhost:7071/api/explain
```

### 3. Check Data is Loaded
```bash
# Run this to see what data is available
python discover_real_data.py
```

### 4. Check Logs
```bash
# Look for errors in the backend logs
# Terminal 1 should show any errors
```

---

## 📝 Files That Need to Exist

| File | Status | Purpose |
|------|--------|---------|
| `planning_intelligence/planning_snapshot.json` | ❌ Missing (needs to be generated) | Data cache |
| `planning_intelligence/function_app.py` | ✅ Exists | Main API |
| `planning_intelligence/local.settings.json` | ✅ Exists | Configuration |
| `planning_intelligence/requirements.txt` | ✅ Exists | Dependencies |

---

## 🎯 Quick Fix (Copy & Paste)

```bash
# Run these commands in order:

# 1. Navigate to project
cd planning_intelligence

# 2. Install dependencies (if not done)
pip install -r requirements.txt

# 3. Load data (CRITICAL - generates snapshot)
python run_daily_refresh.py

# 4. Start server (Terminal 1)
func start

# 5. In new terminal, run tests (Terminal 2)
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

**Expected Result**: 44/44 passing ✅

---

## 📊 What Should Happen

### Before Fix
```
Query: "Which suppliers at AVC03_F01C02 have design changes?"
Response: "No supplier information found for location AVC03_F01C02"
Reason: planning_snapshot.json is missing
```

### After Fix
```
Query: "Which suppliers at AVC03_F01C02 have design changes?"
Response: 
📊 Suppliers at AVC03_F01C02:
• 540_AMER: 2 records, Forecast: +0, Design changes: 0
• 530_AMER: 4 records, Forecast: +0, Design changes: 0
... (full response with all suppliers)
Reason: planning_snapshot.json exists with data
```

---

## ✅ Verification

After running `python run_daily_refresh.py`, you should see:

1. ✅ File created: `planning_snapshot.json`
2. ✅ File size: Several MB (5-10 MB typical)
3. ✅ All 44 prompts working
4. ✅ Responses showing full data

---

## 🚀 Next Steps

1. Run `python run_daily_refresh.py` on your organization laptop
2. Verify `planning_snapshot.json` was created
3. Run tests: `python test_all_44_prompts_CORRECTED.py`
4. Confirm 44/44 passing ✅

---

**Status**: ✅ Solution Identified
**Root Cause**: Missing planning_snapshot.json
**Fix**: Run `python run_daily_refresh.py`
**Time to Fix**: ~2 minutes
