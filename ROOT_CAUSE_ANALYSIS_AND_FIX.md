# Root Cause Analysis - Why All Tests Failed

## The Real Issue

All 44 tests failed with HTTP 404 errors because:

1. ❌ **Backend not running** - No service listening on http://localhost:7071
2. ❌ **No data loaded** - No cached snapshot available
3. ❌ **No blob connection** - Missing `BLOB_CONNECTION_STRING` environment variable

---

## What This Means

The test script couldn't connect to the backend because:
- The backend service wasn't started
- Even if it was, there would be no data to query
- The system needs data from Azure Blob Storage to work

---

## How to Fix This

### Step 1: Set Up Environment Variables

**Create a `.env` file in the project root** with:
```
BLOB_CONNECTION_STRING=<your-blob-connection-string>
```

Or set it in your terminal:
```bash
# Windows PowerShell
$env:BLOB_CONNECTION_STRING="<your-blob-connection-string>"

# Windows CMD
set BLOB_CONNECTION_STRING=<your-blob-connection-string>

# Linux/Mac
export BLOB_CONNECTION_STRING="<your-blob-connection-string>"
```

### Step 2: Load Data from Blob Storage

**Option A: Using the daily-refresh endpoint**
```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Option B: Using Python script**
```bash
cd planning_intelligence
python.exe -c "from run_daily_refresh import run_daily_refresh; run_daily_refresh()"
```

### Step 3: Start the Backend

```bash
func start
```

Wait for message: "Listening on http://localhost:7071"

### Step 4: Verify Data is Loaded

```bash
cd planning_intelligence
python.exe diagnose_data.py
```

Expected output:
```
✓ Snapshot has data
✓ Blob has data
✓ Sample Locations: [AVC11_F01C01, LOC001, ...]
✓ Records with AVC11_F01C01: 1234
```

### Step 5: Run Tests

```bash
cd planning_intelligence
python.exe test_all_44_prompts.py
```

Expected result: Pass rate >= 90% (40+ out of 44)

---

## Understanding the Data Flow

```
Azure Blob Storage
        ↓
   (daily-refresh)
        ↓
   Cached Snapshot
        ↓
   Backend Service
        ↓
   Test Script
```

**Current Status**:
- ❌ Blob Storage: Not connected (missing env var)
- ❌ Cached Snapshot: Empty
- ❌ Backend Service: Not running
- ❌ Test Script: Can't connect

---

## What Data You Need

The system needs:
- **Location IDs**: e.g., AVC11_F01C01, LOC001, CMH02_F01C01
- **Material IDs**: e.g., MAT-001, MAT-002, MAT-003
- **Equipment Categories**: e.g., PUMP, VALVE
- **Suppliers**: e.g., SUP-A, SUP-B
- **Records**: Detail records with changes, forecasts, risks, etc.

---

## Complete Setup Checklist

- [ ] Set `BLOB_CONNECTION_STRING` environment variable
- [ ] Start backend: `func start`
- [ ] Load data: Call `/api/daily-refresh` endpoint
- [ ] Verify data: Run `diagnose_data.py`
- [ ] Run tests: Run `test_all_44_prompts.py`
- [ ] Check results: Pass rate >= 90%

---

## Troubleshooting

### If Backend Won't Start
```bash
# Check if port 7071 is in use
netstat -ano | findstr :7071

# Kill existing process
taskkill /PID <PID> /F

# Try different port
func start --port 7072
```

### If Data Won't Load
```bash
# Check environment variable
echo %BLOB_CONNECTION_STRING%

# Verify blob connection
python.exe -c "from blob_loader import load_current_previous_from_blob; load_current_previous_from_blob()"
```

### If Tests Still Fail
```bash
# Check what data is available
python.exe diagnose_data.py

# Check backend logs
# Look at func start output for errors

# Check test results
cat test_results_44_prompts.json
```

---

## Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Set env var | 1 min | ⏳ TODO |
| Start backend | 2 min | ⏳ TODO |
| Load data | 2 min | ⏳ TODO |
| Verify data | 1 min | ⏳ TODO |
| Run tests | 2 min | ⏳ TODO |
| **TOTAL** | **~8 min** | ⏳ TODO |

---

## Next Steps

1. **Get your Blob Connection String**
   - From Azure Portal
   - From your team/documentation
   - From environment setup

2. **Set the environment variable**
   ```bash
   $env:BLOB_CONNECTION_STRING="<your-connection-string>"
   ```

3. **Start the backend**
   ```bash
   func start
   ```

4. **Load data**
   ```bash
   curl -X POST http://localhost:7071/api/daily-refresh -H "Content-Type: application/json" -d '{}'
   ```

5. **Run tests**
   ```bash
   cd planning_intelligence
   python.exe test_all_44_prompts.py
   ```

---

## Questions?

The issue is clear now:
- ✅ Code is ready (all fixes applied)
- ❌ Backend not running
- ❌ Data not loaded
- ❌ Environment not configured

Once you set up the environment and load data, the tests should pass!

