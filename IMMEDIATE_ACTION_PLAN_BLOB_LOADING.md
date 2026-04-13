# Immediate Action Plan - Blob Data Loading

## Current Status

✅ **Frontend**: Running on port 3000 (rebuilt with correct localhost API URL)
❌ **Backend**: NOT running on port 7071

---

## What You Need to Do NOW

### Step 1: Start Backend (New Terminal)

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

### Step 2: Verify Backend Started

```bash
netstat -ano | findstr :7071
```

**Expected Output**:
```
TCP    127.0.0.1:7071    0.0.0.0:0    LISTENING    [PID]
```

### Step 3: Open Frontend

```
http://localhost:3000
```

**Expected Result**:
- Dashboard loads
- Shows planning health, forecast, risk data
- Shows detail records from blob storage

---

## If Backend Fails to Start

### Check for Errors
1. Look at the terminal output
2. Common errors:
   - `Port 7071 already in use` → Kill existing process
   - `Module not found` → Run `pip install -r requirements.txt`
   - `Connection error` → Check blob connection string

### Kill Existing Process
```bash
# Find process on port 7071
netstat -ano | findstr :7071

# Kill it (replace PID with actual process ID)
taskkill /PID [PID] /F
```

### Install Dependencies
```bash
cd planning_intelligence
pip install -r requirements.txt
```

### Verify Configuration
```bash
# Check local.settings.json exists
ls planning_intelligence/local.settings.json

# Check it has BLOB_CONNECTION_STRING
cat planning_intelligence/local.settings.json
```

---

## If Frontend Still Shows Error

### Check Browser Console
1. Open http://localhost:3000
2. Press F12
3. Go to Console tab
4. Look for errors

### Check Network Tab
1. In DevTools: Network tab
2. Reload: F5
3. Look for `planning-dashboard-v2` request
4. Check:
   - Status: Should be 200 (not CORS error)
   - Response: Should have data

### Common Issues

**Issue**: Still shows CORS error
- **Cause**: Frontend build is still stale
- **Fix**: 
  ```bash
  cd frontend
  npm run build
  npm start
  ```

**Issue**: 404 on planning-dashboard-v2
- **Cause**: Backend not running
- **Fix**: Start backend with `func start`

**Issue**: 500 error from backend
- **Cause**: Blob connection failed
- **Fix**: Check backend console for error message

**Issue**: Blank page or infinite loading
- **Cause**: Frontend stuck
- **Fix**: Check browser console for errors

---

## Complete Setup (Both Services)

### Terminal 1: Backend
```bash
cd planning_intelligence
func start
```

### Terminal 2: Frontend
```bash
cd frontend
npm start
```

### Browser
```
http://localhost:3000
```

---

## Verification Checklist

- [ ] Backend running on port 7071
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000
- [ ] No CORS errors in console
- [ ] Dashboard loads with data
- [ ] Planning health card shows value
- [ ] Forecast card shows data
- [ ] Risk summary displays
- [ ] Detail records table populated

---

## Quick Troubleshooting

### Backend Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :7071

# Kill process if needed
taskkill /PID [PID] /F

# Try again
func start
```

### Frontend Shows Blank Page
```bash
# Rebuild frontend
cd frontend
npm run build
npm start
```

### Still Getting CORS Error
```bash
# Verify .env has correct URL
cat frontend/.env

# Rebuild if needed
npm run build
npm start
```

### Backend Returns 500 Error
1. Check backend console for error message
2. Common causes:
   - Blob connection failed
   - CSV parsing error
   - Missing environment variables

---

## Expected Data Flow

```
Browser (http://localhost:3000)
    ↓
Frontend loads
    ↓
Calls http://localhost:7071/api/planning-dashboard-v2
    ↓
Backend processes blob data
    ↓
Returns JSON response
    ↓
Frontend renders dashboard
    ↓
You see:
- Planning Health: 75/100
- Forecast: 50,000 units
- Risk Level: Medium
- Detail Records: 150 total, 45 changed
```

---

## Next Steps

1. **Start Backend**: `cd planning_intelligence && func start`
2. **Verify Running**: `netstat -ano | findstr :7071`
3. **Open Frontend**: http://localhost:3000
4. **Check Data**: Should see dashboard with blob data
5. **If Error**: Check browser console and backend logs

---

## Summary

The frontend is now correctly configured to use the local backend. You just need to:

1. ✅ Start the backend on port 7071
2. ✅ Verify it's running
3. ✅ Open http://localhost:3000
4. ✅ Check that blob data loads

**The CORS error is fixed. The frontend is ready. Just start the backend!**

