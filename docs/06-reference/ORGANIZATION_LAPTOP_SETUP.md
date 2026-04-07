# Organization Laptop Setup - File Checklist

Running on your organization laptop? Follow this checklist to verify everything is configured correctly.

## Files to Check (In Order)

### 1. ✅ Check: `planning_intelligence/local.settings.json`

**Location**: `planning_intelligence/local.settings.json`

**What to look for:**
```json
{
  "Values": {
    "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv"
  }
}
```

**Check these:**
- [ ] `BLOB_CONNECTION_STRING` is NOT `YOUR_CONNECTION_STRING_HERE`
- [ ] `BLOB_CONNECTION_STRING` starts with `DefaultEndpointsProtocol=https;`
- [ ] `BLOB_CONNECTION_STRING` contains `AccountName=`
- [ ] `BLOB_CONNECTION_STRING` contains `AccountKey=`
- [ ] `BLOB_CONTAINER_NAME` is `planning-data`
- [ ] `BLOB_CURRENT_FILE` is `current.csv`
- [ ] `BLOB_PREVIOUS_FILE` is `previous.csv`

**If missing or wrong:**
1. Get connection string from Azure Portal:
   - Go to Storage Account
   - Click "Access keys"
   - Copy "Connection string"
2. Update `local.settings.json`
3. Save file

---

### 2. ✅ Check: `planning_intelligence/.env`

**Location**: `planning_intelligence/.env`

**What to look for:**
```env
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
```

**Check these:**
- [ ] File exists (if not, copy from `.env.example`)
- [ ] `BLOB_CONNECTION_STRING` is set (not empty)
- [ ] `BLOB_CONNECTION_STRING` is NOT `YOUR_KEY`
- [ ] `BLOB_CONTAINER_NAME` is `planning-data`
- [ ] `BLOB_CURRENT_FILE` is `current.csv`
- [ ] `BLOB_PREVIOUS_FILE` is `previous.csv`

**If missing:**
```bash
cd planning_intelligence
cp .env.example .env
# Then edit .env with your connection string
```

---

### 3. ✅ Check: `frontend/.env`

**Location**: `frontend/.env`

**What to look for:**
```env
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

**Check these:**
- [ ] File exists (if not, copy from `.env.example`)
- [ ] `REACT_APP_API_URL=http://localhost:7071/api`
- [ ] `REACT_APP_USE_MOCK=false`

**If missing:**
```bash
cd frontend
cp .env.example .env
```

---

### 4. ✅ Check: Azure Portal - Blob Storage

**Go to Azure Portal and verify:**

**Container:**
- [ ] Storage Account exists
- [ ] Container named `planning-data` exists
- [ ] Container is accessible

**Files:**
- [ ] File `current.csv` exists in container
- [ ] File `previous.csv` exists in container
- [ ] Both files are > 0 bytes (not empty)

**How to check:**
1. Go to Azure Portal
2. Find your Storage Account
3. Click "Containers"
4. Click "planning-data"
5. You should see `current.csv` and `previous.csv`

---

### 5. ✅ Check: CSV File Format

**Files to check:**
- `current.csv` (in Blob Storage)
- `previous.csv` (in Blob Storage)

**Required columns (case-insensitive):**
- [ ] `LOCID` (Location ID)
- [ ] `PRDID` (Product/Material ID)
- [ ] `GSCEQUIPCAT` (Equipment Category)

**How to check:**
1. Download `current.csv` from Azure Portal
2. Open in Excel or text editor
3. Check first row has these columns

---

## Quick Verification Steps

### Step 1: Check Configuration Files (2 minutes)

```bash
# Check local.settings.json
cat planning_intelligence/local.settings.json

# Check .env files
cat planning_intelligence/.env
cat frontend/.env
```

**Look for:**
- ✅ Connection string is set (not placeholder)
- ✅ Container name is `planning-data`
- ✅ File names are `current.csv` and `previous.csv`

### Step 2: Run Diagnostic (1 minute)

```bash
cd planning_intelligence
python debug_blob.py
```

**Expected output:**
```
✅ PASS: Environment Variables
✅ PASS: local.settings.json
✅ PASS: Blob Storage Connection
✅ PASS: Container & Files
✅ PASS: File Parsing
✅ PASS: API Endpoint
```

**If any FAIL:**
- Read the error message
- Fix the issue
- Re-run diagnostic

### Step 3: Start Backend (1 minute)

```bash
cd planning_intelligence
func start
```

**Expected output:**
```
Http Functions:
  planning-intelligence: [POST] http://localhost:7071/api/planning-intelligence
  planning-dashboard-v2: [POST] http://localhost:7071/api/planning-dashboard-v2
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

### Step 4: Start Frontend (1 minute)

```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view planning-intelligence-frontend in the browser.
  Local:            http://localhost:3000
```

### Step 5: Open Dashboard (1 minute)

1. Open browser: http://localhost:3000
2. You should see the Planning Intelligence Dashboard
3. Data should be loaded from Blob Storage

---

## File Checklist Summary

| File | Location | What to Check | Status |
|------|----------|---------------|--------|
| local.settings.json | `planning_intelligence/` | Connection string set? | [ ] |
| .env | `planning_intelligence/` | Connection string set? | [ ] |
| .env | `frontend/` | API URL correct? | [ ] |
| current.csv | Azure Blob Storage | Exists and > 0 bytes? | [ ] |
| previous.csv | Azure Blob Storage | Exists and > 0 bytes? | [ ] |
| CSV columns | Azure Blob Storage | Has LOCID, PRDID, GSCEQUIPCAT? | [ ] |

---

## Common Issues on Organization Laptop

### Issue 1: "Connection string not set"

**Files to check:**
- `planning_intelligence/local.settings.json`
- `planning_intelligence/.env`

**Fix:**
1. Open `planning_intelligence/local.settings.json`
2. Find `BLOB_CONNECTION_STRING`
3. Replace with actual connection string from Azure Portal
4. Save file

### Issue 2: "Container does not exist"

**Files to check:**
- Azure Portal (not a file)

**Fix:**
1. Go to Azure Portal
2. Find Storage Account
3. Click "Containers"
4. Click "+ Container"
5. Name: `planning-data`
6. Click "Create"

### Issue 3: "Files not found"

**Files to check:**
- Azure Portal (not a file)

**Fix:**
1. Go to Azure Portal
2. Click "Containers"
3. Click "planning-data"
4. Click "Upload"
5. Upload `current.csv` and `previous.csv`

### Issue 4: "Missing required columns"

**Files to check:**
- `current.csv` (in Blob Storage)
- `previous.csv` (in Blob Storage)

**Fix:**
1. Download CSV from Blob Storage
2. Open in Excel
3. Check columns: LOCID, PRDID, GSCEQUIPCAT
4. If missing, update CSV file
5. Re-upload to Blob Storage

### Issue 5: "Cannot connect to backend"

**Files to check:**
- `frontend/.env`

**Fix:**
1. Open `frontend/.env`
2. Check `REACT_APP_API_URL=http://localhost:7071/api`
3. Make sure backend is running: `func start`

---

## Step-by-Step Setup on Organization Laptop

### 1. Clone Repository
```bash
git clone https://gitlab.your-org.com/your-group/planning-intelligence.git
cd planning-intelligence
```

### 2. Setup Backend
```bash
cd planning_intelligence

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env with your connection string

# Copy and configure local.settings.json
# (should already be there, just update connection string)
```

### 3. Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Copy and configure .env
cp .env.example .env
# Should already have correct values
```

### 4. Verify Configuration
```bash
# Check all files are configured
cd ../planning_intelligence
python debug_blob.py
```

### 5. Run Backend
```bash
cd planning_intelligence
func start
```

### 6. Run Frontend (new terminal)
```bash
cd frontend
npm start
```

### 7. Open Dashboard
- Browser: http://localhost:3000
- Should see data from Blob Storage

---

## Files You Need to Edit

### Must Edit:
1. **`planning_intelligence/local.settings.json`**
   - Add your Blob Storage connection string
   - This is CRITICAL

2. **`planning_intelligence/.env`**
   - Add your Blob Storage connection string
   - Or copy from local.settings.json

### Should Verify:
3. **`frontend/.env`**
   - Should already be correct
   - Just verify `REACT_APP_API_URL=http://localhost:7071/api`

### Don't Edit:
- `planning_intelligence/function_app.py`
- `frontend/src/services/api.ts`
- Any other code files

---

## Getting Connection String

**From Azure Portal:**
1. Go to Azure Portal
2. Find your Storage Account
3. Click "Access keys" (left sidebar)
4. Copy "Connection string" from Key 1
5. Paste into `planning_intelligence/local.settings.json`

**Format should be:**
```
DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
```

---

## Verification Checklist

Before running the dashboard:

- [ ] Cloned repository from GitLab
- [ ] Created Python virtual environment
- [ ] Installed Python dependencies
- [ ] Installed Node dependencies
- [ ] Updated `planning_intelligence/local.settings.json` with connection string
- [ ] Updated `planning_intelligence/.env` with connection string
- [ ] Verified `frontend/.env` has correct API URL
- [ ] Verified Blob Storage container exists
- [ ] Verified CSV files uploaded to Blob Storage
- [ ] Verified CSV files have required columns
- [ ] Ran `python debug_blob.py` - all tests pass
- [ ] Started backend: `func start`
- [ ] Started frontend: `npm start`
- [ ] Opened dashboard: http://localhost:3000
- [ ] Dashboard shows data

---

## Quick Reference

| Task | File to Check | What to Look For |
|------|---------------|------------------|
| Connection string | `planning_intelligence/local.settings.json` | `BLOB_CONNECTION_STRING` set? |
| Connection string | `planning_intelligence/.env` | `BLOB_CONNECTION_STRING` set? |
| API URL | `frontend/.env` | `REACT_APP_API_URL=http://localhost:7071/api` |
| Container | Azure Portal | `planning-data` exists? |
| Files | Azure Portal | `current.csv` and `previous.csv` exist? |
| CSV format | Azure Portal | Has LOCID, PRDID, GSCEQUIPCAT? |

---

## Still Having Issues?

1. **Run diagnostic:**
   ```bash
   python planning_intelligence/debug_blob.py
   ```

2. **Check backend logs:**
   ```bash
   func start --verbose
   ```

3. **Check frontend console:**
   - Open http://localhost:3000
   - Press F12
   - Go to Console tab
   - Look for errors

4. **Read detailed guide:**
   - See `BLOB_STORAGE_DEBUG.md`

---

## Summary

**On your organization laptop, you need to:**

1. ✅ Edit `planning_intelligence/local.settings.json` - add connection string
2. ✅ Edit `planning_intelligence/.env` - add connection string
3. ✅ Verify `frontend/.env` - should be correct
4. ✅ Verify Azure Portal - container and files exist
5. ✅ Run `python debug_blob.py` - verify everything works
6. ✅ Run `func start` - start backend
7. ✅ Run `npm start` - start frontend
8. ✅ Open http://localhost:3000 - see dashboard

That's it! 🚀
