# Files to Check - Visual Guide

## Quick Answer: What Files to Check?

### 3 Files You MUST Edit

```
planning-intelligence/
├── planning_intelligence/
│   ├── local.settings.json          ← EDIT THIS #1
│   └── .env                         ← EDIT THIS #2
│
└── frontend/
    └── .env                         ← VERIFY THIS #3
```

---

## File #1: `planning_intelligence/local.settings.json`

**Location:** `planning_intelligence/local.settings.json`

**What it looks like:**
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "YOUR_CONNECTION_STRING_HERE",
    "BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv"
  },
  "Host": {
    "CORS": "http://localhost:3000",
    "CORSCredentials": false
  }
}
```

**What to change:**
```
BEFORE:
"BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE"

AFTER:
"BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
```

**Where to get connection string:**
1. Go to Azure Portal
2. Find Storage Account
3. Click "Access keys"
4. Copy "Connection string"
5. Paste into this file

---

## File #2: `planning_intelligence/.env`

**Location:** `planning_intelligence/.env`

**What it looks like:**
```env
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
```

**What to change:**
```
BEFORE:
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net

AFTER:
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=myactualkey;EndpointSuffix=core.windows.net
```

**If file doesn't exist:**
```bash
cd planning_intelligence
cp .env.example .env
# Then edit with your connection string
```

---

## File #3: `frontend/.env`

**Location:** `frontend/.env`

**What it looks like:**
```env
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

**What to check:**
- ✅ `REACT_APP_API_URL=http://localhost:7071/api` (should be correct)
- ✅ `REACT_APP_USE_MOCK=false` (should be false)

**Usually no changes needed** - just verify it's correct.

**If file doesn't exist:**
```bash
cd frontend
cp .env.example .env
```

---

## Azure Portal - What to Verify

### Check 1: Storage Account

**Go to:** Azure Portal → Storage Account

**Verify:**
- [ ] Storage Account exists
- [ ] You can access it

### Check 2: Container

**Go to:** Storage Account → Containers

**Verify:**
- [ ] Container named `planning-data` exists
- [ ] If not, create it

### Check 3: Files

**Go to:** Containers → planning-data

**Verify:**
- [ ] File `current.csv` exists
- [ ] File `previous.csv` exists
- [ ] Both files are > 0 bytes (not empty)

### Check 4: CSV Format

**Download:** `current.csv` from Blob Storage

**Open in:** Excel or text editor

**Verify columns exist:**
- [ ] `LOCID` (Location ID)
- [ ] `PRDID` (Product/Material ID)
- [ ] `GSCEQUIPCAT` (Equipment Category)

---

## Complete File Checklist

### Configuration Files (3 files)

| File | Location | What to Check | Status |
|------|----------|---------------|--------|
| local.settings.json | `planning_intelligence/` | `BLOB_CONNECTION_STRING` set? | [ ] |
| .env | `planning_intelligence/` | `BLOB_CONNECTION_STRING` set? | [ ] |
| .env | `frontend/` | `REACT_APP_API_URL` correct? | [ ] |

### Azure Portal (4 checks)

| Item | Location | What to Check | Status |
|------|----------|---------------|--------|
| Storage Account | Azure Portal | Exists and accessible? | [ ] |
| Container | Containers | `planning-data` exists? | [ ] |
| current.csv | planning-data | Exists and > 0 bytes? | [ ] |
| previous.csv | planning-data | Exists and > 0 bytes? | [ ] |

### CSV Format (1 check)

| Item | Location | What to Check | Status |
|------|----------|---------------|--------|
| Columns | current.csv | Has LOCID, PRDID, GSCEQUIPCAT? | [ ] |

---

## Step-by-Step: What to Do

### Step 1: Edit `planning_intelligence/local.settings.json`

```bash
# Open the file
code planning_intelligence/local.settings.json

# Find this line:
"BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE"

# Replace with your actual connection string:
"BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"

# Save file (Ctrl+S)
```

### Step 2: Edit `planning_intelligence/.env`

```bash
# Open the file
code planning_intelligence/.env

# Find this line:
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net

# Replace with your actual connection string:
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net

# Save file (Ctrl+S)
```

### Step 3: Verify `frontend/.env`

```bash
# Open the file
code frontend/.env

# Verify these lines:
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_USE_MOCK=false

# Should be correct - no changes needed
```

### Step 4: Verify Azure Portal

1. Go to Azure Portal
2. Find Storage Account
3. Click "Containers"
4. Verify `planning-data` exists
5. Click `planning-data`
6. Verify `current.csv` and `previous.csv` exist

### Step 5: Run Diagnostic

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

---

## Connection String Format

**Your connection string should look like:**

```
DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey123456789==;EndpointSuffix=core.windows.net
```

**Parts:**
- `DefaultEndpointsProtocol=https;` - Always this
- `AccountName=myaccount` - Your storage account name
- `AccountKey=mykey123456789==` - Your access key
- `EndpointSuffix=core.windows.net` - Always this

**Where to get it:**
1. Azure Portal
2. Storage Account
3. "Access keys"
4. Copy "Connection string"

---

## Common Mistakes

### ❌ Mistake 1: Placeholder Connection String

```
WRONG:
"BLOB_CONNECTION_STRING": "YOUR_CONNECTION_STRING_HERE"

RIGHT:
"BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
```

### ❌ Mistake 2: Missing Container

```
WRONG:
Container "planning-data" doesn't exist in Azure

RIGHT:
Create container "planning-data" in Azure Portal
```

### ❌ Mistake 3: Missing Files

```
WRONG:
Files "current.csv" and "previous.csv" not uploaded

RIGHT:
Upload both files to "planning-data" container
```

### ❌ Mistake 4: Wrong API URL

```
WRONG:
REACT_APP_API_URL=http://localhost:3000

RIGHT:
REACT_APP_API_URL=http://localhost:7071/api
```

### ❌ Mistake 5: CSV Missing Columns

```
WRONG:
CSV has columns: Name, Value, Date

RIGHT:
CSV has columns: LOCID, PRDID, GSCEQUIPCAT (+ others)
```

---

## Quick Reference

### Files to Edit

| File | Edit What | With What |
|------|-----------|-----------|
| `planning_intelligence/local.settings.json` | `BLOB_CONNECTION_STRING` | Your connection string |
| `planning_intelligence/.env` | `BLOB_CONNECTION_STRING` | Your connection string |
| `frontend/.env` | Nothing | Just verify |

### Azure Portal to Check

| Location | Check What | Should Be |
|----------|-----------|-----------|
| Storage Account | Exists | Yes |
| Containers | `planning-data` exists | Yes |
| planning-data | `current.csv` exists | Yes |
| planning-data | `previous.csv` exists | Yes |
| current.csv | Has LOCID, PRDID, GSCEQUIPCAT | Yes |

---

## Summary

**On your organization laptop:**

1. ✅ Edit `planning_intelligence/local.settings.json` - add connection string
2. ✅ Edit `planning_intelligence/.env` - add connection string
3. ✅ Verify `frontend/.env` - should be correct
4. ✅ Verify Azure Portal - container and files exist
5. ✅ Run `python debug_blob.py` - verify everything works

**That's it!** Then run:
```bash
func start          # Terminal 1
npm start           # Terminal 2
# Open http://localhost:3000
```

---

## Need Help?

- **Quick fixes:** See `BLOB_DEBUG_QUICK.md`
- **Detailed guide:** See `BLOB_STORAGE_DEBUG.md`
- **Run diagnostic:** `python planning_intelligence/debug_blob.py`
