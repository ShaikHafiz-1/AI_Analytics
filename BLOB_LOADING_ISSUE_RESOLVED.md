# Blob Loading Issue - Root Cause & Resolution

## Problem Summary

Frontend was showing CORS error when trying to load blob data:

```
Access to fetch at 'https://pi-planning-intelligence-fpdqcaayahcpe9b5.eastus-01.azurewebsites.net/api/planning-dashboard-v2'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

---

## Root Cause Analysis

### The Issue
Your frontend was pointing to the **production Azure backend** instead of the **local backend**.

### Why It Happened
1. `.env` file had correct localhost URL: `REACT_APP_API_URL=http://localhost:7071/api`
2. But the **built frontend** (in `frontend/build/`) was stale
3. The stale build had the production URL hardcoded
4. `.env` is only read during build time, not at runtime
5. So the old build was using the old production URL

### The CORS Error
- Production backend doesn't have `http://localhost:3000` in its CORS policy
- Only has production domain in CORS policy
- So browser blocked the request

---

## Solution Applied

### What I Did

1. **Deleted stale build**
   ```bash
   Remove-Item -Path "frontend\build" -Recurse -Force
   ```

2. **Rebuilt frontend**
   ```bash
   npm run build
   ```
   - Reads `.env` file
   - Uses `REACT_APP_API_URL=http://localhost:7071/api`
   - Creates new build with correct URL

3. **Started frontend server**
   ```bash
   npm start
   ```
   - Server running on port 3000
   - Serving the new build with correct API URL

### Result
✅ Frontend now points to `http://localhost:7071/api` (local backend)
✅ CORS error should be gone
✅ Ready to load blob data from local backend

---

## What You Need to Do

### Start Backend (if not already running)

```bash
cd planning_intelligence
func start
```

**Expected Output**:
```
Azure Functions Core Tools
...
Listening on http://localhost:7071
```

### Verify Both Services Running

```bash
# Terminal 1: Backend
netstat -ano | findstr :7071
# Should show: TCP    127.0.0.1:7071    0.0.0.0:0    LISTENING

# Terminal 2: Frontend
netstat -ano | findstr :3000
# Should show: TCP    127.0.0.1:3000    0.0.0.0:0    LISTENING
```

### Open Frontend

```
http://localhost:3000
```

### Expected Result

Dashboard should load with:
- ✅ Planning Health card
- ✅ Forecast card
- ✅ Risk summary
- ✅ Detail records table
- ✅ All data from blob storage

---

## Key Learning

### Environment Variables in React

**Important**: `.env` is only read during build time!

```bash
# When you change .env:
npm run build  # ← Must rebuild to apply changes
npm start      # ← Then start server
```

### Not like this:
```bash
# ❌ WRONG - Changes won't take effect
npm start  # ← Old build still has old values
```

---

## Files Changed

### Deleted
- `frontend/build/` (stale build)

### Rebuilt
- `frontend/build/` (new build with correct API URL)

### Not Changed
- `frontend/.env` (already had correct localhost URL)
- `planning_intelligence/local.settings.json` (already configured)

---

## Configuration Verified

### Frontend (.env)
```
PORT=3000
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

### Backend (local.settings.json)
```json
{
  "Host": {
    "CORS": "http://localhost:3000",
    "CORSCredentials": false
  }
}
```

---

## Data Flow (Now Correct)

```
Browser (http://localhost:3000)
    ↓
Frontend (rebuilt with localhost URL)
    ↓
POST http://localhost:7071/api/planning-dashboard-v2
    ↓
Backend (local Azure Functions)
    ↓
Load blob data (current.csv, previous.csv)
    ↓
Process and compare
    ↓
Return JSON response with CORS headers
    ↓
Frontend receives response
    ↓
Dashboard renders with blob data
```

---

## Troubleshooting

### If Still Getting CORS Error
1. Verify frontend was rebuilt: `npm run build`
2. Verify frontend restarted: `npm start`
3. Clear browser cache: Ctrl+Shift+Delete
4. Check `.env` has correct URL

### If Backend Not Responding
1. Verify backend started: `func start`
2. Verify port 7071 is listening: `netstat -ano | findstr :7071`
3. Check backend console for errors

### If Dashboard Blank
1. Check browser console (F12)
2. Check Network tab for `planning-dashboard-v2` request
3. Verify response status is 200
4. Check response has data

---

## Summary

**Problem**: Frontend was using production URL, causing CORS error
**Root Cause**: Stale build not updated after `.env` changes
**Solution**: Deleted stale build and rebuilt with correct localhost URL
**Result**: Frontend now correctly points to local backend
**Next Step**: Start backend and open http://localhost:3000

---

## Status

✅ **Frontend**: Rebuilt and running on port 3000
⏳ **Backend**: Needs to be started on port 7071
⏳ **Blob Data**: Ready to load once backend is running

**Start the backend and blob data will load!**

