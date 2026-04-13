# Frontend-Backend Integration Diagnostic Report

## Issue Summary
Frontend loads on port 3000 but blob data is not displaying. The dashboard shows loading state or error.

## Frontend Flow Analysis

### 1. **Entry Point: DashboardPage.tsx**
- **Location**: `frontend/src/pages/DashboardPage.tsx`
- **Initial Load**: 
  - Checks `REACT_APP_USE_MOCK` environment variable (set to `false` in `.env`)
  - Calls `fetchDashboard({})` on component mount
  - Shows loading skeleton while fetching

### 2. **API Service: api.ts**
- **Location**: `frontend/src/services/api.ts`
- **API_URL**: `http://localhost:7071/api` (from `.env`)
- **Endpoint Called**: `POST /api/planning-dashboard-v2`
- **Request Body**: `{ mode: "blob" }`
- **Expected Response**: `DashboardResponse` object with:
  - `planningHealth`, `status`
  - `forecastNew`, `forecastOld`, `trendDelta`, `trendDirection`
  - `totalRecords`, `changedRecordCount`
  - `riskSummary`, `aiInsight`, `rootCause`
  - `alerts`, `drivers`, `filters`
  - `datacenterSummary`, `materialGroupSummary`
  - `supplierSummary`, `designSummary`, `rojSummary`
  - `detailRecords` (array of records)

### 3. **Error Handling**
- If API call fails: Shows error banner with "Retry Blob" and "Load Mock Data" buttons
- If blob fails but data exists: Falls back to mock data
- If no data: Shows "No planning data available"

## Backend Flow Analysis

### 1. **Endpoint: planning-dashboard-v2**
- **Location**: `planning_intelligence/function_app.py` (line 154)
- **Method**: POST
- **Flow**:
  1. Parse request body for `location_id` and `material_group`
  2. Try to load cached snapshot first (fast path)
  3. If no snapshot, load from blob:
     - Call `load_current_previous_from_blob()` from `blob_loader.py`
     - Normalize rows
     - Filter by location/material group
     - Compare current vs previous
     - Call `build_response()` to construct response
  4. Return JSON response with CORS headers

### 2. **Response Builder: response_builder.py**
- **Function**: `build_response()` (line 21)
- **Process**:
  1. Compute health score
  2. Call MCP tools:
     - `analytics_context_tool()`
     - `risk_summary_tool()`
     - `root_cause_driver_tool()`
     - `recommendation_tool()`
     - `alert_trigger_tool()`
  3. Generate AI insights (deterministic, no LLM)
  4. Build summaries (datacenter, material group, supplier, design, ROJ)
  5. Return complete dashboard response

### 3. **Blob Loading: blob_loader.py**
- **Function**: `load_current_previous_from_blob()`
- **Process**:
  1. Connect to Azure Blob Storage using `BLOB_CONNECTION_STRING`
  2. Download `current.csv` and `previous.csv`
  3. Parse CSV files
  4. Return rows as dictionaries

## Potential Issues & Diagnostics

### Issue 1: Backend Not Running
**Symptom**: Connection refused on port 7071
**Check**:
```bash
# Verify backend is running
netstat -ano | findstr :7071
# Or check Azure Functions logs
```

### Issue 2: CORS Issues
**Symptom**: Browser console shows CORS error
**Check**:
- `local.settings.json` has `"CORS": "http://localhost:3000"`
- Backend returns `Access-Control-Allow-Origin: http://localhost:3000` header
- Check `_cors_response()` function in `function_app.py`

### Issue 3: Blob Connection Failure
**Symptom**: Error message "Blob load failed"
**Check**:
- `BLOB_CONNECTION_STRING` is valid in `local.settings.json`
- Blob container `planning-data` exists
- Files `current.csv` and `previous.csv` exist in container
- Network connectivity to Azure Blob Storage

### Issue 4: API Response Format Mismatch
**Symptom**: Dashboard shows but no data displays
**Check**:
- Response includes all required fields
- `detailRecords` array is populated
- `totalRecords > 0`
- No null/undefined values in critical fields

### Issue 5: Frontend Build Stale
**Symptom**: Changes to `.env` not reflected
**Check**:
- Frontend needs rebuild after `.env` changes
- Run: `npm run build` in `frontend/` directory
- Restart `npm start`

## Current Configuration

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
  "BLOB_CONNECTION_STRING": "...",
  "BLOB_CONTAINER_NAME": "planning-data",
  "BLOB_CURRENT_FILE": "current.csv",
  "BLOB_PREVIOUS_FILE": "previous.csv",
  "AZURE_OPENAI_KEY": "...",
  "AZURE_OPENAI_ENDPOINT": "...",
  "Host": {
    "CORS": "http://localhost:3000"
  }
}
```

## Testing Steps

### Step 1: Verify Backend is Running
```bash
# Check if port 7071 is listening
netstat -ano | findstr :7071
```

### Step 2: Test API Directly
```bash
# Test the endpoint
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Step 3: Check Browser Console
1. Open http://localhost:3000 in browser
2. Open DevTools (F12)
3. Check Console tab for errors
4. Check Network tab:
   - Look for `planning-dashboard-v2` request
   - Check response status (should be 200)
   - Check response body (should have data)

### Step 4: Check Frontend Build
```bash
cd frontend
npm run build
npm start
```

### Step 5: Enable Debug Mode
Add to `frontend/.env`:
```
REACT_APP_DEBUG_MODE=true
```
Then rebuild and restart. This shows a debug panel in bottom-right corner.

## Data Flow Diagram

```
Browser (http://localhost:3000)
    ↓
DashboardPage.tsx (useEffect on mount)
    ↓
fetchDashboard() from api.ts
    ↓
POST http://localhost:7071/api/planning-dashboard-v2
    ↓
Backend: planning_dashboard_v2()
    ↓
Try load_snapshot() → if exists, return cached
    ↓
If no snapshot:
  - load_current_previous_from_blob()
  - normalize_rows()
  - filter_records()
  - compare_records()
  - build_response()
    ↓
Return JSON response with CORS headers
    ↓
Frontend receives response
    ↓
validateDashboardResponse()
    ↓
buildDashboardContext()
    ↓
Render dashboard with data
```

## Next Steps

1. **Verify Backend Running**: Check if Azure Functions is running on port 7071
2. **Test API Endpoint**: Make direct API call to see response
3. **Check Browser Console**: Look for specific error messages
4. **Verify Blob Connection**: Ensure blob files exist and are accessible
5. **Rebuild Frontend**: Ensure latest build with correct `.env` values
6. **Enable Debug Mode**: Use debug panel to see raw response data

