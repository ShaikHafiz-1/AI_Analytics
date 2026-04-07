# Local Setup Guide - Organization Laptop Testing

## 🎯 Overview

This guide explains which files to update and how to set up the build for local testing on the organization laptop.

---

## 📋 Files to Update for Local Testing

### 1. **CRITICAL - Environment Configuration**

#### File: `planning_intelligence/local.settings.json`
**Status**: ✅ Already configured with Azure credentials
**What to do**: 
- ✅ No changes needed - already has BLOB_CONNECTION_STRING
- ✅ Already has BLOB_CONTAINER_NAME
- ✅ Already has CORS settings for localhost:3000

**Current values**:
```json
{
  "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;...",
  "BLOB_CONTAINER_NAME": "planning-data",
  "BLOB_CURRENT_FILE": "current.csv",
  "BLOB_PREVIOUS_FILE": "previous.csv"
}
```

### 2. **IMPORTANT - Python Dependencies**

#### File: `planning_intelligence/requirements.txt`
**Status**: ⚠️ Check if all dependencies are installed
**What to do**:
```bash
# Install all dependencies
cd planning_intelligence
pip install -r requirements.txt
```

**Key dependencies**:
- azure-storage-blob
- azure-functions
- pandas
- numpy
- requests

### 3. **OPTIONAL - Environment Variables**

#### File: `planning_intelligence/.env.example`
**Status**: ℹ️ Reference only
**What to do**:
- Copy to `.env` if you want to override local.settings.json
- Not required - local.settings.json takes precedence

---

## 🚀 Local Testing Setup Steps

### Step 1: Verify Python Installation
```bash
python --version  # Should be 3.9+
pip --version
```

### Step 2: Install Azure Functions Core Tools
```bash
# Windows
choco install azure-functions-core-tools-4

# macOS
brew tap azure/azure
brew install azure-functions-core-tools@4

# Linux
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ focal main" > /etc/apt/sources.list.d/azure-cli.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### Step 3: Install Python Dependencies
```bash
cd planning_intelligence
pip install -r requirements.txt
```

### Step 4: Verify Blob Storage Connection
```bash
# Run the blob connection test
python test_blob_connection.py
```

Expected output:
```
✅ Successfully connected to Blob Storage
✅ Found current.csv
✅ Found previous.csv
```

### Step 5: Load Data from Blob Storage
```bash
# Run the daily refresh to load data
python run_daily_refresh.py
```

Expected output:
```
✅ Data loaded successfully
✅ Snapshot created: planning_snapshot.json
```

### Step 6: Start Local Function App
```bash
# Start the Azure Functions runtime
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

### Step 7: Run Tests
```bash
# In a new terminal, run the test suite
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

## 📝 Files to Check/Verify

### Configuration Files
- ✅ `planning_intelligence/local.settings.json` - Already configured
- ✅ `planning_intelligence/.env.example` - Reference only
- ✅ `planning_intelligence/requirements.txt` - Check dependencies

### Test Files
- ✅ `planning_intelligence/test_all_44_prompts_CORRECTED.py` - Main test suite
- ✅ `planning_intelligence/test_blob_connection.py` - Verify Blob connection
- ✅ `planning_intelligence/test_blob_integration.py` - Test Blob integration

### Data Files
- ✅ `planning_intelligence/discovered_data.json` - Real data reference
- ✅ `planning_intelligence/test_results_44_prompts_CORRECTED.json` - Expected results

### Core Implementation Files
- ✅ `planning_intelligence/function_app.py` - Main API (already updated with 100% pass rate)
- ✅ `planning_intelligence/response_builder.py` - Response formatting
- ✅ `planning_intelligence/dashboard_builder.py` - Dashboard building

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to Blob Storage"
**Solution**:
1. Verify `BLOB_CONNECTION_STRING` in `local.settings.json`
2. Check internet connection
3. Run: `python test_blob_connection.py`

### Issue: "Module not found" errors
**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: "Port 7071 already in use"
**Solution**:
```bash
# Use different port
func start --port 7072
```

### Issue: "Tests failing with 'No cached snapshot'"
**Solution**:
```bash
# Load data first
python run_daily_refresh.py

# Then run tests
python test_all_44_prompts_CORRECTED.py
```

---

## 📊 Expected Test Results

After setup, you should see:

```
Total Prompts:     44
Passed:            44
Failed:            0
Pass Rate:         100.0%

Average Response Time:  ~2500ms
Min Response Time:      2228ms
Max Response Time:      4000ms

All Responses > 50 chars:  100%
All Responses < 5s:        100%
```

---

## 🎯 Quick Start Commands

```bash
# 1. Navigate to project
cd planning_intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Blob connection
python test_blob_connection.py

# 4. Load data
python run_daily_refresh.py

# 5. Start local server (Terminal 1)
func start

# 6. Run tests (Terminal 2)
python test_all_44_prompts_CORRECTED.py
```

---

## 📚 Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `function_app.py` | Main API implementation | ✅ Ready |
| `local.settings.json` | Local configuration | ✅ Configured |
| `requirements.txt` | Python dependencies | ✅ Ready |
| `test_all_44_prompts_CORRECTED.py` | Test suite | ✅ Ready |
| `test_blob_connection.py` | Blob verification | ✅ Ready |
| `run_daily_refresh.py` | Data loader | ✅ Ready |

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Azure Functions Core Tools installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Blob connection verified (`python test_blob_connection.py`)
- [ ] Data loaded (`python run_daily_refresh.py`)
- [ ] Local server started (`func start`)
- [ ] Tests passing (`python test_all_44_prompts_CORRECTED.py`)
- [ ] All 44 prompts passing (100%)

---

## 🚀 Next Steps

1. **Setup**: Follow the steps above
2. **Test**: Run the test suite
3. **Verify**: Confirm 100% pass rate
4. **Deploy**: When ready, deploy to Azure

---

## 📞 Support

For issues:
1. Check `docs/02-deployment/DEPLOYMENT_INSTRUCTIONS.md`
2. Review `docs/05-testing/QUICK_START_TESTING.md`
3. Check troubleshooting section above

---

**Status**: ✅ Ready for Local Testing
**Pass Rate**: 100% (44/44)
**Last Updated**: 2026-04-07
