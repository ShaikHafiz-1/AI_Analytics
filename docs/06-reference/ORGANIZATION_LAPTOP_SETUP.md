# Organization Laptop Setup - Quick Reference

## 🎯 What You Need to Know

You've moved the build to your organization laptop. **Good news**: Most files are already configured. You just need to follow a few setup steps.

---

## ✅ Files Already Configured (No Changes Needed)

These files are ready to go - no updates required:

| File | Status | Why |
|------|--------|-----|
| `planning_intelligence/local.settings.json` | ✅ Ready | Has BLOB_CONNECTION_STRING and all Azure credentials |
| `planning_intelligence/requirements.txt` | ✅ Ready | All Python dependencies listed |
| `planning_intelligence/function_app.py` | ✅ Ready | Main API with 100% pass rate (44/44 prompts) |
| `planning_intelligence/response_builder.py` | ✅ Ready | Response formatting (already fixed) |
| `planning_intelligence/dashboard_builder.py` | ✅ Ready | Dashboard building (already fixed) |

---

## 🔧 What You Need to Do on Organization Laptop

### Step 1: Install Python & Tools
```bash
# Check Python version (need 3.9+)
python --version

# Install Azure Functions Core Tools
# Windows: choco install azure-functions-core-tools-4
# macOS: brew install azure-functions-core-tools@4
# Linux: See LOCAL_SETUP_GUIDE.md
```

### Step 2: Install Dependencies
```bash
cd planning_intelligence
pip install -r requirements.txt
```

### Step 3: Verify Blob Connection
```bash
python test_blob_connection.py
```

Expected output:
```
✅ Successfully connected to Blob Storage
✅ Found current.csv
✅ Found previous.csv
```

### Step 4: Load Data
```bash
python run_daily_refresh.py
```

### Step 5: Start Local Server (Terminal 1)
```bash
func start
```

### Step 6: Run Tests (Terminal 2)
```bash
python test_all_44_prompts_CORRECTED.py
```

Expected: **44/44 passing (100%)**

---

## 📋 Files to Verify (Read-Only)

These files are reference only - just verify they exist:

| File | Purpose |
|------|---------|
| `planning_intelligence/test_all_44_prompts_CORRECTED.py` | Main test suite with real data |
| `planning_intelligence/test_blob_connection.py` | Blob connection verification |
| `planning_intelligence/discovered_data.json` | Real data reference (Location IDs, Material IDs, etc.) |
| `planning_intelligence/test_results_44_prompts_CORRECTED.json` | Expected test results |

---

## 🚨 If You Need to Update Configuration

**Only update these if your organization has different Azure credentials:**

### File: `planning_intelligence/local.settings.json`
```json
{
  "Values": {
    "BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv"
  }
}
```

**Where to get BLOB_CONNECTION_STRING**:
1. Go to Azure Portal
2. Find Storage Account: `planningdatapi`
3. Copy Connection String from "Access keys"
4. Paste into `local.settings.json`

---

## 🎯 Quick Checklist

- [ ] Python 3.9+ installed
- [ ] Azure Functions Core Tools installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Blob connection verified: `python test_blob_connection.py`
- [ ] Data loaded: `python run_daily_refresh.py`
- [ ] Local server running: `func start`
- [ ] Tests passing: `python test_all_44_prompts_CORRECTED.py`
- [ ] Result: 44/44 (100%)

---

## 📚 Full Documentation

For detailed setup instructions, see:
- **LOCAL_SETUP_GUIDE.md** - Complete step-by-step guide
- **DEPLOYMENT_INSTRUCTIONS.md** - Production deployment
- **QUICK_START_TESTING.md** - Quick testing reference

---

## 🚀 You're Ready!

Once you complete the checklist above, you'll have:
- ✅ Local development environment running
- ✅ All 44 prompts passing (100%)
- ✅ Ready to test and deploy

**Next**: Follow the steps above and run the test suite!

---

**Status**: ✅ Ready for Organization Laptop
**Pass Rate**: 100% (44/44)
**Last Updated**: 2026-04-07
