# Simple Checklist - Organization Laptop

## 3 Files to Edit

### ✅ File 1: `planning_intelligence/local.settings.json`

```
Location: planning_intelligence/local.settings.json

Find this:
  "BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE"

Replace with your connection string from Azure Portal:
  "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"

Status: [ ] DONE
```

### ✅ File 2: `planning_intelligence/.env`

```
Location: planning_intelligence/.env

Find this:
  BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net

Replace with your connection string:
  BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net

Status: [ ] DONE
```

### ✅ File 3: `frontend/.env`

```
Location: frontend/.env

Just verify these lines are correct:
  REACT_APP_API_URL=http://localhost:7071/api
  REACT_APP_USE_MOCK=false

No changes needed - just verify.

Status: [ ] DONE
```

---

## 3 Azure Portal Checks

### ✅ Check 1: Container Exists

```
Go to: Azure Portal → Storage Account → Containers

Look for: "planning-data"

If missing:
  1. Click "+ Container"
  2. Name: planning-data
  3. Click "Create"

Status: [ ] DONE
```

### ✅ Check 2: Files Exist

```
Go to: Azure Portal → Containers → planning-data

Look for:
  - current.csv
  - previous.csv

If missing:
  1. Click "Upload"
  2. Select both CSV files
  3. Click "Upload"

Status: [ ] DONE
```

### ✅ Check 3: CSV Format

```
Download: current.csv from Blob Storage

Open in: Excel or text editor

Check for columns:
  - LOCID
  - PRDID
  - GSCEQUIPCAT

If missing:
  1. Update CSV file
  2. Re-upload to Blob Storage

Status: [ ] DONE
```

---

## 4 Quick Tests

### ✅ Test 1: Run Diagnostic

```bash
cd planning_intelligence
python debug_blob.py
```

Expected: All tests PASS ✅

Status: [ ] DONE

### ✅ Test 2: Start Backend

```bash
cd planning_intelligence
func start
```

Expected: Backend running on http://localhost:7071/api

Status: [ ] DONE

### ✅ Test 3: Start Frontend

```bash
cd frontend
npm start
```

Expected: Frontend running on http://localhost:3000

Status: [ ] DONE

### ✅ Test 4: Open Dashboard

```
Browser: http://localhost:3000
```

Expected: Dashboard shows data from Blob Storage

Status: [ ] DONE

---

## Summary

| Item | File/Location | What to Do | Status |
|------|---------------|-----------|--------|
| 1 | `planning_intelligence/local.settings.json` | Add connection string | [ ] |
| 2 | `planning_intelligence/.env` | Add connection string | [ ] |
| 3 | `frontend/.env` | Verify API URL | [ ] |
| 4 | Azure Portal | Create container | [ ] |
| 5 | Azure Portal | Upload CSV files | [ ] |
| 6 | Azure Portal | Verify CSV format | [ ] |
| 7 | Terminal | Run diagnostic | [ ] |
| 8 | Terminal | Start backend | [ ] |
| 9 | Terminal | Start frontend | [ ] |
| 10 | Browser | Open dashboard | [ ] |

---

## That's It!

Once all items are checked:
- ✅ Blob Storage is working
- ✅ Dashboard shows data
- ✅ Ready to develop

Good luck! 🚀
