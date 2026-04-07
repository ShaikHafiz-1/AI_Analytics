# Blob Storage Debugging - Quick Start

If you see "Blob data unavailable", follow these steps.

## Step 1: Run Complete Diagnostic (2 minutes)

```bash
cd planning_intelligence
python debug_blob.py
```

This will test:
- ✅ Environment variables
- ✅ local.settings.json
- ✅ Blob Storage connection
- ✅ Container exists
- ✅ Files exist
- ✅ Files can be parsed
- ✅ API endpoint works

**If all pass**: Your Blob Storage is working! Skip to "Verify Frontend"

**If any fail**: See the specific error below

---

## Step 2: Fix Common Issues

### Issue: "BLOB_CONNECTION_STRING not set"

**Fix:**
1. Open `planning_intelligence/local.settings.json`
2. Find `BLOB_CONNECTION_STRING`
3. Replace `YOUR_CONNECTION_STRING_HERE` with your actual connection string

**Get connection string:**
1. Go to Azure Portal
2. Find your Storage Account
3. Click **Access keys** (left sidebar)
4. Copy **Connection string** from Key 1
5. Paste into `local.settings.json`

### Issue: "Container does NOT exist"

**Fix:**
1. Go to Azure Portal
2. Find your Storage Account
3. Click **Containers** (left sidebar)
4. Click **+ Container**
5. Name: `planning-data`
6. Click **Create**

### Issue: "Files NOT FOUND"

**Fix:**
1. Go to Azure Portal
2. Find your Storage Account
3. Click **Containers**
4. Click **planning-data**
5. Click **Upload**
6. Upload `current.csv` and `previous.csv`

### Issue: "Missing required columns"

**Fix:**
Your CSV files must have these columns (case-insensitive):
- `LOCID` (Location ID)
- `PRDID` (Product/Material ID)
- `GSCEQUIPCAT` (Equipment Category)

Check your CSV file has these columns. If not, update the file.

### Issue: "Cannot connect to backend"

**Fix:**
Make sure backend is running:
```bash
cd planning_intelligence
func start
```

---

## Step 3: Test Individual Components

### Test 1: Connection Only
```bash
python test_blob_connection.py
```

### Test 2: Download & Parse
```bash
python test_blob_download.py
```

### Test 3: API Endpoint
```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'
```

---

## Step 4: Verify Frontend

1. Open browser: http://localhost:3000
2. Press F12 (Developer Tools)
3. Go to **Console** tab
4. Look for errors
5. Go to **Network** tab
6. Refresh page
7. Look for requests to `/api/planning-dashboard-v2`
8. Check response status (should be 200)

---

## Step 5: Check Backend Logs

```bash
# Stop backend (Ctrl+C)

# Start with verbose logging
func start --verbose

# Look for these messages:
# - "Downloaded blob planning-data/current.csv"
# - "Loaded current: X rows, Y columns"
# - "Daily refresh triggered"
```

---

## Quick Checklist

- [ ] Run `python debug_blob.py` - all tests pass?
- [ ] Connection string in `local.settings.json`?
- [ ] Container `planning-data` exists in Azure?
- [ ] Files `current.csv` and `previous.csv` uploaded?
- [ ] Files have required columns (LOCID, PRDID, GSCEQUIPCAT)?
- [ ] Backend running (`func start`)?
- [ ] Frontend can reach backend (no CORS errors)?
- [ ] Dashboard shows data?

---

## Still Stuck?

1. **Collect debug info:**
   ```bash
   python debug_blob.py > debug_output.txt
   ```

2. **Check backend logs:**
   ```bash
   func start 2>&1 | tee backend.log
   ```

3. **Check browser console:**
   - F12 → Console tab
   - Screenshot any errors

4. **Share with team:**
   - debug_output.txt
   - backend.log
   - Browser console screenshot

---

## Common Error Messages

| Error | Solution |
|-------|----------|
| `BLOB_CONNECTION_STRING not set` | Add to local.settings.json |
| `Container does NOT exist` | Create in Azure Portal |
| `Files NOT FOUND` | Upload to Azure Portal |
| `Missing required columns` | Check CSV has LOCID, PRDID, GSCEQUIPCAT |
| `Cannot connect to backend` | Run `func start` |
| `CORS error` | Check REACT_APP_API_URL in frontend/.env |
| `API returned 500` | Check backend logs with `func start --verbose` |

---

## Files Created for Debugging

- `planning_intelligence/debug_blob.py` - Complete diagnostic
- `planning_intelligence/test_blob_connection.py` - Test connection only
- `planning_intelligence/test_blob_download.py` - Test download & parse
- `BLOB_STORAGE_DEBUG.md` - Detailed debugging guide

---

## Next Steps

Once Blob Storage is working:

1. ✅ Backend loads data
2. ✅ Frontend displays dashboard
3. ✅ Ready for production

Good luck! 🚀
