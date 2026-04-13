# Quick Start - Frontend & Backend Integration

## 30-Second Setup

### Terminal 1: Start Backend
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

### Terminal 2: Start Frontend
```bash
cd frontend
npm start
```
**Expected Output**:
```
Server running on port 3000
```

### Browser
Open: **http://localhost:3000**

---

## What Should Happen

1. **Page loads** with loading skeleton
2. **Dashboard appears** with data from blob storage
3. **Cards show**:
   - Planning Health score
   - Forecast data
   - Risk summary
   - Alert banner (if any)
   - Detail records table

---

## If It Doesn't Work

### Step 1: Check Backend
```bash
# Is port 7071 listening?
netstat -ano | findstr :7071

# Should show: TCP    127.0.0.1:7071    0.0.0.0:0    LISTENING
```

### Step 2: Check Frontend
```bash
# Is port 3000 listening?
netstat -ano | findstr :3000

# Should show: TCP    127.0.0.1:3000    0.0.0.0:0    LISTENING
```

### Step 3: Test API
1. Open: http://localhost:3000/test-api.html
2. Click: "Test API"
3. Check response status and data

### Step 4: Check Browser Console
1. Open: http://localhost:3000
2. Press: F12
3. Go to: Console tab
4. Look for errors

### Step 5: Check Network Tab
1. In DevTools: Network tab
2. Reload: F5
3. Look for: `planning-dashboard-v2` request
4. Check: Status (should be 200)
5. Check: Response (should have data)

---

## Common Issues

### "Cannot GET /"
**Problem**: Frontend not running
**Solution**: 
```bash
cd frontend
npm start
```

### "Blob data unavailable"
**Problem**: Backend error
**Solution**:
1. Check backend console for error
2. Verify blob connection string in `local.settings.json`
3. Verify blob files exist in Azure Storage

### CORS Error
**Problem**: Backend not allowing frontend
**Solution**:
1. Check `local.settings.json` has `"CORS": "http://localhost:3000"`
2. Restart backend

### Blank Page
**Problem**: Frontend stuck loading
**Solution**:
1. Check browser console (F12)
2. Check Network tab for failed requests
3. Verify backend is responding

### Changes to .env Not Working
**Problem**: Frontend build is stale
**Solution**:
```bash
cd frontend
npm run build
npm start
```

---

## Verify Everything Works

### Test 1: Backend Responding
```bash
# Should return JSON with data
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test 2: Frontend Loading
```bash
# Should show "Server running on port 3000"
# Open http://localhost:3000 in browser
```

### Test 3: Data Displaying
1. Open http://localhost:3000
2. Should see dashboard with:
   - Planning Health card
   - Forecast card
   - Risk summary
   - Detail records

### Test 4: API Test Page
1. Open http://localhost:3000/test-api.html
2. Click "Test API"
3. Should see response with data

---

## Debug Mode

### Enable Debug Panel
1. Edit `frontend/.env`
2. Add: `REACT_APP_DEBUG_MODE=true`
3. Run: `npm run build && npm start`
4. Open http://localhost:3000
5. Look for yellow "Debug Panel" button in bottom-right

### Debug Panel Shows
- Raw API response
- Card-to-field mapping
- Health score calculation
- Copy full JSON button

---

## File Locations

### Frontend
- **Main**: `frontend/src/pages/DashboardPage.tsx`
- **API**: `frontend/src/services/api.ts`
- **Config**: `frontend/.env`
- **Build**: `frontend/build/`

### Backend
- **Main**: `planning_intelligence/function_app.py`
- **Response**: `planning_intelligence/response_builder.py`
- **Blob**: `planning_intelligence/blob_loader.py`
- **Config**: `planning_intelligence/local.settings.json`

---

## Environment Variables

### Frontend (.env)
```
PORT=3000
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_USE_MOCK=false
REACT_APP_DEBUG_MODE=false
```

### Backend (local.settings.json)
```json
{
  "BLOB_CONNECTION_STRING": "...",
  "BLOB_CONTAINER_NAME": "planning-data",
  "BLOB_CURRENT_FILE": "current.csv",
  "BLOB_PREVIOUS_FILE": "previous.csv",
  "Host": {
    "CORS": "http://localhost:3000"
  }
}
```

---

## Next Steps

1. ✅ Start backend: `func start`
2. ✅ Start frontend: `npm start`
3. ✅ Open http://localhost:3000
4. ✅ Verify data displays
5. ✅ Test API with test-api.html
6. ✅ Check debug panel for details

---

## Need Help?

### Check These Files
- `COMPLETE_FRONTEND_BACKEND_INTEGRATION_GUIDE.md` - Full architecture
- `FRONTEND_LOADING_TROUBLESHOOTING.md` - Detailed troubleshooting
- `FRONTEND_BACKEND_INTEGRATION_DIAGNOSTIC.md` - Diagnostic info
- `LOCAL_TESTING_SETUP.md` - Setup verification

### Check Backend Logs
- Look for error messages in terminal
- Check blob connection errors
- Check CSV parsing errors

### Check Browser Console
- F12 → Console tab
- Look for fetch errors
- Look for validation errors

### Check Network Tab
- F12 → Network tab
- Look for `planning-dashboard-v2` request
- Check response status and body

