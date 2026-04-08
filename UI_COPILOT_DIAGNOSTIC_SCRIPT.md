# UI Copilot Diagnostic Script

## Problem Summary
- ✅ Backend tests pass 44/44 prompts
- ❌ UI Copilot fails with "No supplier information found"
- This means: Backend is working, but frontend context passing is broken

## Root Cause Analysis

The issue is likely one of these:

1. **Dashboard data fetch is failing silently** - The UI loads but doesn't get data
2. **Context is not being passed to Copilot** - The context object is empty or undefined
3. **Browser cache issue** - Old code is still running
4. **API endpoint mismatch** - Frontend is calling wrong endpoint

## Diagnostic Steps

### Step 1: Check Backend is Running
```bash
# Terminal 1 should show:
func start

# Output should include:
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  planning-dashboard-v2: [POST] http://localhost:7071/api/planning-dashboard-v2
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

### Step 2: Check Data is Loaded
```bash
# Terminal 2 should have run:
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py

# Verify file exists:
dir planning_snapshot.json

# Should show file size > 5MB
```

### Step 3: Test Backend API Directly
```bash
# Test dashboard endpoint
curl -X POST http://localhost:7071/api/planning-dashboard-v2 ^
  -H "Content-Type: application/json" ^
  -d "{\"mode\":\"blob\"}"

# Should return JSON with detailRecords field
# Look for: "detailRecords": [...]
```

### Step 4: Test Explain Endpoint with Context
```bash
# First, get the dashboard response
$dashboard = Invoke-WebRequest -Uri "http://localhost:7071/api/planning-dashboard-v2" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"mode":"blob"}' | ConvertFrom-Json

# Then test explain with context
$context = @{
  planningHealth = $dashboard.planningHealth
  detailRecords = $dashboard.detailRecords
  # ... other fields
}

$explainPayload = @{
  question = "Which suppliers at CYS20_F01C01 have design changes?"
  context = $context
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:7071/api/explain" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $explainPayload | ConvertFrom-Json | ConvertTo-Json
```

### Step 5: Check Browser Console
1. Open UI: http://localhost:3000
2. Press F12 to open Developer Tools
3. Go to "Console" tab
4. Look for errors like:
   - "Failed to fetch dashboard"
   - "Cannot read property 'detailRecords'"
   - "API error 400/500"
5. Go to "Network" tab
6. Refresh page
7. Look for requests:
   - `planning-dashboard-v2` - Check response includes `detailRecords`
   - `explain` - Check request includes `context` parameter

### Step 6: Check Frontend Code
1. Open DevTools (F12)
2. Go to "Sources" tab
3. Find `DashboardPage.tsx` in the file tree
4. Look at the `buildDashboardContext` function
5. Verify it's extracting `detailRecords` from the response

---

## Expected Outputs

### When Working:
```json
{
  "planningHealth": 45,
  "status": "At Risk",
  "detailRecords": [
    {
      "locationId": "CYS20_F01C01",
      "materialId": "C00000560-001",
      "supplier": "UPS",
      "forecastQtyCurrent": 100,
      "qtyChanged": true,
      "designChanged": false,
      "supplierChanged": false,
      "rojChanged": false
    },
    ...
  ],
  "supplierSummary": {...},
  "datacenterSummary": [...],
  ...
}
```

### When Broken:
```json
{
  "planningHealth": 45,
  "status": "At Risk",
  "detailRecords": [],  // EMPTY!
  "supplierSummary": {...},
  "datacenterSummary": [...],
  ...
}
```

---

## Quick Fixes to Try

### Fix 1: Hard Refresh Browser
```
Ctrl + Shift + Delete  (Windows)
or
Cmd + Shift + Delete   (Mac)
```
Then clear cache and reload.

### Fix 2: Restart Frontend Dev Server
```bash
# If running npm start, stop it and restart:
cd frontend
npm start
```

### Fix 3: Check Environment Variables
```bash
# Verify API URL is correct
echo %REACT_APP_API_URL%

# Should output: http://localhost:7071/api
# If empty, set it:
set REACT_APP_API_URL=http://localhost:7071/api
```

### Fix 4: Rebuild Frontend
```bash
cd frontend
npm run build
npm start
```

---

## If Still Not Working

### Check 1: Verify detailRecords in Dashboard Response
```bash
# Run this to see what the dashboard API returns
python -c "
import requests
import json

response = requests.post(
    'http://localhost:7071/api/planning-dashboard-v2',
    json={'mode': 'blob'}
)

data = response.json()
print('Has detailRecords:', 'detailRecords' in data)
print('detailRecords count:', len(data.get('detailRecords', [])))
print('First record:', json.dumps(data.get('detailRecords', [{}])[0], indent=2))
"
```

### Check 2: Verify Explain Endpoint Receives Context
Add logging to `function_app.py` in the `explain` function:
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    context = body.get("context")
    
    # ADD THIS:
    logging.info(f"Explain called with context: {context is not None}")
    if context:
        logging.info(f"Context has detailRecords: {'detailRecords' in context}")
        logging.info(f"detailRecords count: {len(context.get('detailRecords', []))}")
```

Then check Terminal 1 logs when you ask Copilot a question.

### Check 3: Verify Frontend is Passing Context
Add console.log to `CopilotPanel.tsx` in the `sendMessage` function:
```typescript
const sendMessage = useCallback(async (question: string) => {
  // ADD THIS:
  console.log("Sending question:", question);
  console.log("Context:", context);
  console.log("Context has detailRecords:", context.detailRecords?.length);
  
  const res = await fetchExplain({ question: question.trim(), context });
  // ...
}, [loading, context, selectedEntity]);
```

Then open DevTools Console and check what's being logged.

---

## Summary

**If tests pass but UI fails:**
1. Backend is working ✅
2. Frontend data fetch might be failing ❌
3. Frontend context passing might be broken ❌
4. Browser cache might be stale ❌

**Next steps:**
1. Hard refresh browser (Ctrl+Shift+Delete)
2. Check browser console for errors (F12)
3. Check Network tab for API responses
4. Verify detailRecords is in dashboard response
5. Verify context is being passed to explain endpoint
6. Restart frontend dev server if needed

