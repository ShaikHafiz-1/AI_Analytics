# Frontend Not Loading Blob Data - Troubleshooting Guide

## Quick Checklist

- [ ] Backend running on port 7071?
- [ ] Frontend running on port 3000?
- [ ] Can you access http://localhost:3000 in browser?
- [ ] Does browser console show any errors?
- [ ] Does Network tab show `planning-dashboard-v2` request?
- [ ] What's the response status (200, 500, etc.)?
- [ ] Is blob data actually in Azure Storage?

## Step 1: Verify Backend is Running

### Windows PowerShell
```powershell
# Check if port 7071 is listening
netstat -ano | findstr :7071

# Should show something like:
# TCP    127.0.0.1:7071    0.0.0.0:0    LISTENING    12345
```

### If NOT running:
```bash
cd planning_intelligence
func start
```

---

## Step 2: Verify Frontend is Running

### Windows PowerShell
```powershell
# Check if port 3000 is listening
netstat -ano | findstr :3000

# Should show something like:
# TCP    127.0.0.1:3000    0.0.0.0:0    LISTENING    54321
```

### If NOT running:
```bash
cd frontend
npm start
```

---

## Step 3: Open Browser and Check Console

1. **Open**: http://localhost:3000
2. **Press**: F12 (or right-click → Inspect)
3. **Go to**: Console tab
4. **Look for errors** like:
   - `Failed to fetch`
   - `CORS error`
   - `Cannot read property`
   - `API error 500`

---

## Step 4: Check Network Tab

1. **In DevTools**: Click Network tab
2. **Reload page**: F5
3. **Look for**: `planning-dashboard-v2` request
4. **Check**:
   - **Status**: Should be 200 (not 404, 500, etc.)
   - **Type**: Should be `fetch` or `xhr`
   - **Response**: Click on it, go to Response tab
   - **Should see**: JSON with `planningHealth`, `totalRecords`, etc.

### If Status is 500:
- Backend error occurred
- Check backend console for error message
- Common issues:
  - Blob connection failed
  - CSV parsing error
  - Missing environment variables

### If Status is 404:
- Endpoint not found
- Check if backend is actually running
- Verify endpoint name is correct

### If CORS Error:
- Browser blocked the request
- Check `local.settings.json` has correct CORS setting
- Should have: `"CORS": "http://localhost:3000"`

---

## Step 5: Test Backend Directly

### Using Python (if available):
```python
import requests
import json

url = "http://localhost:7071/api/planning-dashboard-v2"
headers = {"Content-Type": "application/json"}
payload = {}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
```

### Using Node.js:
```javascript
const fetch = require('node-fetch');

fetch('http://localhost:7071/api/planning-dashboard-v2', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
})
  .then(r => r.json())
  .then(data => console.log(JSON.stringify(data, null, 2)))
  .catch(err => console.error('Error:', err));
```

---

## Step 6: Check Blob Connection

### Verify Blob Files Exist:
1. Go to Azure Portal
2. Navigate to Storage Account: `planningdatapi`
3. Go to Blob Containers
4. Open `planning-data` container
5. Should see:
   - `current.csv`
   - `previous.csv`

### If Files Don't Exist:
- Upload test CSV files
- Or check if blob connection string is wrong

### Check Connection String:
```bash
# In planning_intelligence/local.settings.json
# Should have BLOB_CONNECTION_STRING with:
# - AccountName: planningdatapi
# - AccountKey: (valid key)
# - EndpointSuffix: core.windows.net
```

---

## Step 7: Enable Debug Mode

### Add to frontend/.env:
```
REACT_APP_DEBUG_MODE=true
```

### Rebuild and restart:
```bash
cd frontend
npm run build
npm start
```

### In browser:
- Look for yellow "Debug Panel" button in bottom-right
- Click to expand
- Shows raw API response
- Shows calculation trace
- Can copy full JSON

---

## Step 8: Check Frontend Build

### Rebuild frontend:
```bash
cd frontend
npm run build
npm start
```

### Why rebuild?
- `.env` changes require rebuild
- TypeScript compilation
- Tailwind CSS generation

### Verify build succeeded:
- Should see: `Compiled successfully`
- Should see: `Server running on port 3000`

---

## Common Issues & Solutions

### Issue: "Blob data unavailable"
**Cause**: Backend returned error
**Solution**:
1. Check backend console for error
2. Verify blob connection string
3. Verify blob files exist
4. Check Azure Storage connectivity

### Issue: "Cannot read property 'planningHealth'"
**Cause**: Response missing expected fields
**Solution**:
1. Check API response in Network tab
2. Verify `build_response()` is returning all fields
3. Check `response_builder.py` for errors

### Issue: Blank page or infinite loading
**Cause**: Frontend stuck in loading state
**Solution**:
1. Check browser console for errors
2. Check Network tab for failed requests
3. Verify backend is responding
4. Try "Load Mock Data" button if available

### Issue: CORS error in console
**Cause**: Backend not allowing frontend origin
**Solution**:
1. Check `local.settings.json`:
   ```json
   "Host": {
     "CORS": "http://localhost:3000"
   }
   ```
2. Restart backend after changing
3. Verify `_cors_response()` is being called

### Issue: 404 on planning-dashboard-v2
**Cause**: Endpoint not registered
**Solution**:
1. Check `function_app.py` has `@app.route()` decorator
2. Verify function name is `planning_dashboard_v2`
3. Restart backend

---

## Debug Response Format

When you see the API response, it should look like:

```json
{
  "dataMode": "blob",
  "lastRefreshedAt": "2024-04-13T10:30:00Z",
  "planningHealth": 75,
  "status": "Stable",
  "forecastNew": 50000,
  "forecastOld": 45000,
  "trendDirection": "Increasing",
  "trendDelta": 5000,
  "totalRecords": 150,
  "changedRecordCount": 45,
  "riskSummary": {
    "level": "Medium",
    "highestRiskLevel": "Design + Supplier",
    "highRiskCount": 12,
    "riskBreakdown": {...}
  },
  "detailRecords": [
    {
      "material": "MAT001",
      "location": "LOC001",
      "quantity_current": 100,
      "quantity_previous": 90,
      "changed": true
    },
    ...
  ],
  ...
}
```

### Key Fields to Check:
- `totalRecords > 0` (should have data)
- `detailRecords` array populated
- `planningHealth` is a number
- `riskSummary` has all fields
- `dataMode` is "blob" (not "mock")

---

## If Still Not Working

### Collect Debug Info:
1. **Browser Console**: Screenshot or copy all errors
2. **Network Response**: Copy full JSON response
3. **Backend Console**: Copy error messages
4. **Environment**: 
   - What OS? (Windows, Mac, Linux)
   - What Node version? (`node --version`)
   - What Python version? (`python --version`)

### Then:
- Check `BLOB_RETRY_DETAILED_DIAGNOSIS.md` for blob-specific issues
- Review `LOCAL_TESTING_SETUP.md` for setup verification
- Check `COMPLETE_CLEANUP_AND_DEPLOYMENT_SUMMARY.md` for system overview

