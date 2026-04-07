# Organization Laptop Setup Checklist

## 📋 Files to Update - NONE! ✅

**All files are already configured.** No code changes needed.

---

## 🚀 Setup Steps (Copy & Paste)

### Terminal 1: Setup & Verification
```bash
# 1. Navigate to project
cd planning_intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Blob connection
python test_blob_connection.py

# 4. Load data from Blob Storage
python run_daily_refresh.py

# 5. Start local server
func start
```

### Terminal 2: Run Tests
```bash
# In a NEW terminal window
cd planning_intelligence

# Run the test suite
python test_all_44_prompts_CORRECTED.py
```

---

## ✅ Expected Results

```
Total Prompts:     44
Passed:            44
Failed:            0
Pass Rate:         100.0%
```

---

## 🔍 Files Already Configured

| File | Status |
|------|--------|
| `planning_intelligence/local.settings.json` | ✅ Has Azure credentials |
| `planning_intelligence/requirements.txt` | ✅ All dependencies listed |
| `planning_intelligence/function_app.py` | ✅ 100% pass rate |
| `planning_intelligence/response_builder.py` | ✅ Fixed |
| `planning_intelligence/dashboard_builder.py` | ✅ Fixed |

---

## 🆘 Troubleshooting

**"Cannot connect to Blob Storage"**
- Check internet connection
- Verify `BLOB_CONNECTION_STRING` in `local.settings.json`
- Run: `python test_blob_connection.py`

**"Module not found"**
- Reinstall: `pip install --upgrade -r requirements.txt`

**"Port 7071 already in use"**
- Use different port: `func start --port 7072`

**"Tests failing with 'No cached snapshot'"**
- Load data first: `python run_daily_refresh.py`
- Then run tests: `python test_all_44_prompts_CORRECTED.py`

---

## 📚 Documentation

- **LOCAL_SETUP_GUIDE.md** - Full setup guide
- **ORGANIZATION_LAPTOP_SETUP.md** - Quick reference
- **DEPLOYMENT_INSTRUCTIONS.md** - Production deployment

---

**Status**: Ready to Setup ✅
**Pass Rate Target**: 100% (44/44)
