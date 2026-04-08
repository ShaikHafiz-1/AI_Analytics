# UI Copilot Not Working - Diagnostic & Fix

## 🔍 Problem

You're opening the UI and clicking "Ask Copilot", but it's answering only some prompts and showing "No supplier information found" errors.

## 🎯 Root Cause

The dashboard context is not being populated with `detailRecords` because:

1. **Backend is not returning detailRecords** - The API response doesn't include the detail records
2. **Frontend is not passing context** - The Copilot is not receiving the dashboard context
3. **Data is not loaded** - The dashboard data fetch is failing or incomplete

---

## ✅ Diagnostic Steps

### Step 1: Check if Backend is Running
```bash
# In Terminal 1, should see:
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

### Step 2: Check if Data is Loaded
```bash
# In Terminal 2, verify snapshot file exists
dir planning_snapshot.json

# Should show file exists and is several MB
```

### Step 3: Check Browser Console for Errors
1. Open UI in browser
2. Press F12 to open Developer Tools
3. Go to "Console" tab
4. Look for any error messages
5. Check "Network" tab to see API responses

### Step 4: Test API Directly
```bash
# Test the explain endpoint
curl -X POST http://localhost:7071/api/explain ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is the current planning health?\"}"
```

Expected response should include:
```json
{
  "answer": "...",
  "queryType": "...",
  "answerMode": "..."
}
```

---

## 🚀 Solution: Restart Everything

### Step 1: Stop All Terminals
- Close Terminal 1 (func start)
- Close Terminal 2 (if running)
- Close Terminal 3 (if running)

### Step 2: Clean Up
```bash
cd planning_intelligence
del planning_snapshot.json
```

### Step 3: Start Fresh

**Terminal 1**:
```bash
cd planning_intelligence
func start
```

Wait for:
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

**Terminal 2** (NEW WINDOW):
```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
```

Wait for:
```
✅ Data loaded successfully
✅ Snapshot saved to ...
```

**Terminal 3** (NEW WINDOW):
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

Should show:
```
Pass rate: 100.0%
```

### Step 4: Refresh UI
1. Close browser tab
2. Open new tab
3. Go to http://localhost:3000
4. Wait for dashboard to load
5. Click "Ask Copilot"
6. Try a prompt

---

## 📋 Checklist

Before using Copilot, verify:

- [ ] Terminal 1: `func start` is running and shows "Http Functions"
- [ ] Terminal 1: No error messages
- [ ] Terminal 2: `python run_daily_refresh.py` completed successfully
- [ ] Terminal 2: `planning_snapshot.json` file exists
- [ ] Terminal 3: Tests show 44/44 passing
- [ ] Browser: Dashboard loads without errors
- [ ] Browser: Console (F12) shows no errors
- [ ] Browser: Network tab shows successful API calls

---

## 🔧 If Still Not Working

### Check 1: Verify Backend is Responding
```bash
# In PowerShell
$response = Invoke-WebRequest -Uri "http://localhost:7071/api/explain" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"question":"What is the current planning health?"}'

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### Check 2: Check Backend Logs
- Look at Terminal 1 output
- Check for any error messages
- Look for "ERROR" or "Exception" messages

### Check 3: Verify Snapshot File
```bash
# Check file size
dir planning_snapshot.json

# Should be several MB (5-10 MB typical)
# If file is very small or empty, data didn't load correctly
```

### Check 4: Check Frontend Network Requests
1. Open Browser DevTools (F12)
2. Go to "Network" tab
3. Refresh page
4. Look for requests to:
   - `planning-dashboard-v2` - Should return dashboard data
   - `explain` - Should return Copilot answers
5. Check response status (should be 200)
6. Check response body for `detailRecords` field

---

## 📊 Expected Behavior

### When Working Correctly:
1. Dashboard loads with data
2. All cards show metrics
3. "Ask Copilot" button is active
4. Typing a prompt shows suggestions
5. Copilot answers with full responses
6. No "No supplier information found" errors

### When Not Working:
1. Dashboard shows "Blob data unavailable"
2. Cards show skeleton loaders
3. "Ask Copilot" button is disabled
4. Copilot shows "No supplier information found"
5. Browser console shows errors

---

## 🎯 Quick Fix Summary

1. **Stop everything** - Close all terminals
2. **Clean up** - Delete `planning_snapshot.json`
3. **Restart** - Follow the 3-terminal setup above
4. **Verify** - Run tests and check 44/44 passing
5. **Refresh UI** - Close and reopen browser
6. **Test Copilot** - Try asking a prompt

---

**Status**: ✅ Diagnostic Guide Ready
**Most Common Issue**: Backend not running or data not loaded
**Solution**: Restart all terminals and reload UI
