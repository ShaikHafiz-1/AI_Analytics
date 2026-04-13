# Complete Frontend-Backend Integration Guide

## Overview

The Planning Intelligence system has two main components:

1. **Frontend** (React + TypeScript) - Port 3000
2. **Backend** (Azure Functions + Python) - Port 7071

The frontend loads blob data by making API calls to the backend, which fetches data from Azure Blob Storage.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Port 3000)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DashboardPage.tsx                                       │   │
│  │  - Loads on mount                                        │   │
│  │  - Calls fetchDashboard()                                │   │
│  │  - Shows loading skeleton                                │   │
│  │  - Renders dashboard with data                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    HTTP POST Request
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Port 7071)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  planning_dashboard_v2() endpoint                        │   │
│  │  - Receives request                                      │   │
│  │  - Tries load_snapshot() (cached)                        │   │
│  │  - If no cache: load_current_previous_from_blob()        │   │
│  │  - Calls build_response()                                │   │
│  │  - Returns JSON + CORS headers                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    HTTP Response (JSON)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Blob Storage                            │
│  - current.csv (latest data)                                    │
│  - previous.csv (historical data)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend Flow (Detailed)

### 1. Application Entry Point
**File**: `frontend/src/index.tsx`
```typescript
ReactDOM.render(<App />, document.getElementById('root'));
```

### 2. App Component
**File**: `frontend/src/App.tsx`
```typescript
const App: React.FC = () => <DashboardPage />;
```

### 3. Dashboard Page - Initial Load
**File**: `frontend/src/pages/DashboardPage.tsx`

**Key Code**:
```typescript
const USE_MOCK = process.env.REACT_APP_USE_MOCK === "true"; // false by default

useEffect(() => {
  if (USE_MOCK) {
    loadMockData();
    return;
  }
  
  // Call backend API
  fetchDashboard({})
    .then((d) => {
      validateDashboardResponse(d);
      setData(d);
      setLoading(false);
    })
    .catch((err) => {
      setError(`Blob data unavailable: ${err.message}`);
      setBlobFailed(true);
      setLoading(false);
    });
}, []);
```

**What happens**:
1. Component mounts
2. Checks if `REACT_APP_USE_MOCK` is true
3. If false (default), calls `fetchDashboard({})`
4. Shows loading skeleton while fetching
5. On success: renders dashboard with data
6. On error: shows error banner with retry options

### 4. API Service - Making the Request
**File**: `frontend/src/services/api.ts`

**Key Code**:
```typescript
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:7071/api";

export async function fetchDashboard(payload?: {
  location_id?: string;
  material_group?: string;
}): Promise<DashboardResponse> {
  const res = await fetch(endpoint("planning-dashboard-v2"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "blob", ...payload }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}
```

**What happens**:
1. Constructs URL: `http://localhost:7071/api/planning-dashboard-v2`
2. Makes POST request with `{ mode: "blob" }`
3. Waits for response
4. If not OK (status != 200): throws error
5. If OK: parses JSON and returns

### 5. Response Validation
**File**: `frontend/src/services/validation.ts`

Validates that response has all required fields before rendering.

### 6. Dashboard Rendering
**File**: `frontend/src/pages/DashboardPage.tsx`

**Key Code**:
```typescript
const context = buildDashboardContext(data);

return (
  <div className="min-h-screen bg-bg text-white">
    {/* Header */}
    {/* KPI Cards: Health, Forecast, Trend */}
    {/* Alerts */}
    {/* Risk Table */}
    {/* Location & Material Cards */}
    {/* Supplier, Design, ROJ Cards */}
    {/* Copilot Panel */}
  </div>
);
```

---

## Backend Flow (Detailed)

### 1. Endpoint Registration
**File**: `planning_intelligence/function_app.py`

**Key Code**:
```python
@app.route(route="planning-dashboard-v2", methods=["POST", "OPTIONS"])
def planning_dashboard_v2(req: func.HttpRequest) -> func.HttpResponse:
    """Blob-first AI dashboard endpoint."""
```

### 2. Request Handling
```python
if req.method == "OPTIONS":
    return _cors_response("", 200)

try:
    body = req.get_json()
except ValueError:
    body = {}

location_id: Optional[str] = body.get("location_id")
material_group: Optional[str] = body.get("material_group")
```

### 3. Snapshot Loading (Fast Path)
```python
snap = load_snapshot()
if snap:
    if location_id or material_group:
        snap = _filter_snapshot(snap, location_id, material_group)
    return _cors_response(json.dumps(snap, default=str))
```

**What happens**:
- Tries to load cached snapshot from disk
- If exists and no filters: returns immediately (fast)
- If filters applied: filters snapshot and returns

### 4. Blob Loading (Slow Path)
```python
logging.info("No snapshot found, loading from blob.")
try:
    from blob_loader import load_current_previous_from_blob
    current_rows, previous_rows = load_current_previous_from_blob()
except Exception as e:
    error_msg = str(e)
    logging.error(f"Blob load failed: {error_msg}")
    return _error(f"Blob load failed: {error_msg}", 500)
```

**What happens**:
- Calls `blob_loader.py` to download CSV files from Azure
- If fails: returns 500 error with message
- If succeeds: continues to processing

### 5. Data Processing
```python
current_records = normalize_rows(current_rows, is_current=True)
previous_records = normalize_rows(previous_rows, is_current=False)
current_filtered = filter_records(current_records, location_id, material_group)
previous_filtered = filter_records(previous_records, location_id, material_group)
compared = compare_records(current_filtered, previous_filtered)
```

**What happens**:
1. Normalizes CSV rows to standard format
2. Filters by location/material group if provided
3. Compares current vs previous to find changes

### 6. Response Building
```python
result = build_response(
    compared, [], location_id, material_group,
    data_mode="blob",
)
```

**File**: `planning_intelligence/response_builder.py`

**What happens**:
1. Computes health score
2. Calls MCP tools (analytics, risk, root cause, recommendations, alerts)
3. Generates AI insights
4. Builds summaries (datacenter, material group, supplier, design, ROJ)
5. Returns complete dashboard response

### 7. Response Return
```python
return _cors_response(json.dumps(result, default=str))
```

**What happens**:
- Converts response to JSON
- Adds CORS headers: `Access-Control-Allow-Origin: http://localhost:3000`
- Returns to frontend

---

## Configuration Files

### Frontend Configuration

**File**: `frontend/.env`
```
PORT=3000
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

**Important**: After changing `.env`, rebuild with `npm run build`

### Backend Configuration

**File**: `planning_intelligence/local.settings.json`
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "...",
    "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;...",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv",
    "AZURE_OPENAI_KEY": "...",
    "AZURE_OPENAI_ENDPOINT": "...",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-5.2-chat",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview"
  },
  "Host": {
    "CORS": "http://localhost:3000",
    "CORSCredentials": false
  },
  "ConnectionStrings": {}
}
```

---

## Expected API Response

### Success Response (200)
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
  "unchangedRecordCount": 105,
  "newRecordCount": 5,
  "riskSummary": {
    "level": "Medium",
    "highestRiskLevel": "Design + Supplier",
    "quantityChangedCount": 20,
    "supplierChangedCount": 15,
    "designChangedCount": 10,
    "rojChangedCount": 0,
    "highRiskCount": 12,
    "riskBreakdown": {...}
  },
  "aiInsight": "Planning health is stable with moderate changes...",
  "rootCause": {...},
  "recommendedActions": [...],
  "drivers": {...},
  "datacenterSummary": [...],
  "materialGroupSummary": [...],
  "supplierSummary": {...},
  "designSummary": {...},
  "rojSummary": {...},
  "detailRecords": [
    {
      "material": "MAT001",
      "location": "LOC001",
      "quantity_current": 100,
      "quantity_previous": 90,
      "changed": true,
      ...
    },
    ...
  ],
  "alerts": {...},
  "filters": {
    "locationId": null,
    "materialGroup": null
  }
}
```

### Error Response (500)
```json
{
  "error": "Blob load failed: Connection timeout"
}
```

---

## Troubleshooting Checklist

### ✓ Backend Running?
```bash
# Check port 7071
netstat -ano | findstr :7071

# If not running:
cd planning_intelligence
func start
```

### ✓ Frontend Running?
```bash
# Check port 3000
netstat -ano | findstr :3000

# If not running:
cd frontend
npm start
```

### ✓ API Responding?
1. Open http://localhost:3000/test-api.html
2. Click "Test API"
3. Check response status and data

### ✓ Blob Connection?
1. Check `local.settings.json` has valid `BLOB_CONNECTION_STRING`
2. Verify blob container `planning-data` exists
3. Verify files `current.csv` and `previous.csv` exist

### ✓ CORS Configured?
1. Check `local.settings.json` has `"CORS": "http://localhost:3000"`
2. Restart backend after changes
3. Check browser console for CORS errors

### ✓ Frontend Build Current?
```bash
cd frontend
npm run build
npm start
```

### ✓ Environment Variables?
1. Frontend: `REACT_APP_API_URL=http://localhost:7071/api`
2. Backend: All values in `local.settings.json`

---

## Testing Tools

### 1. API Test Page
**Location**: `frontend/test-api.html`
**Access**: http://localhost:3000/test-api.html
**Features**:
- Test API endpoint directly
- See response status and data
- Check system status
- View data flow diagram

### 2. Debug Panel
**Enable**: Add `REACT_APP_DEBUG_MODE=true` to `frontend/.env`
**Location**: Bottom-right corner of dashboard
**Shows**:
- Raw API response
- Card-to-field mapping
- Health score calculation trace
- Copy full JSON button

### 3. Browser DevTools
**Open**: F12 in browser
**Check**:
- Console tab: Errors and logs
- Network tab: API requests and responses
- Application tab: Local storage and cookies

### 4. Backend Logs
**Location**: Azure Functions terminal output
**Shows**:
- Request received
- Snapshot load attempt
- Blob load attempt
- Processing steps
- Response sent

---

## Common Issues & Solutions

### Issue: "Blob data unavailable"
**Cause**: Backend returned error
**Solution**:
1. Check backend console for error message
2. Verify blob connection string
3. Verify blob files exist
4. Check Azure Storage connectivity

### Issue: Blank page or infinite loading
**Cause**: Frontend stuck in loading state
**Solution**:
1. Check browser console for errors
2. Check Network tab for failed requests
3. Verify backend is responding
4. Try "Load Mock Data" button

### Issue: CORS error in console
**Cause**: Backend not allowing frontend origin
**Solution**:
1. Check `local.settings.json` has `"CORS": "http://localhost:3000"`
2. Restart backend
3. Clear browser cache

### Issue: 404 on planning-dashboard-v2
**Cause**: Endpoint not found
**Solution**:
1. Verify backend is running
2. Check endpoint name in `function_app.py`
3. Restart backend

### Issue: Changes to .env not reflected
**Cause**: Frontend build is stale
**Solution**:
```bash
cd frontend
npm run build
npm start
```

---

## Performance Optimization

### Caching Strategy
- **Snapshot Cache**: Fast path for repeated requests
- **Blob Load**: Slow path, only when no snapshot
- **Daily Refresh**: Updates snapshot with latest blob data

### Response Size
- **Full Response**: ~50-100 KB (with detail records)
- **Cached Response**: ~30-50 KB
- **Network Time**: 100-500ms depending on blob size

### Optimization Tips
1. Use filters (location_id, material_group) to reduce data
2. Enable snapshot caching for repeated requests
3. Run daily refresh during off-peak hours
4. Monitor blob file sizes

---

## Deployment

### Local Testing
```bash
# Terminal 1: Backend
cd planning_intelligence
func start

# Terminal 2: Frontend
cd frontend
npm start

# Access: http://localhost:3000
```

### Production Deployment
- Backend: Azure Functions
- Frontend: Azure Static Web Apps
- Blob Storage: Azure Blob Storage
- Configuration: Environment variables in Azure

---

## Next Steps

1. **Verify System**: Run through troubleshooting checklist
2. **Test API**: Use `test-api.html` to verify backend
3. **Check Logs**: Review backend console for errors
4. **Enable Debug**: Add `REACT_APP_DEBUG_MODE=true` to see raw data
5. **Rebuild Frontend**: Ensure latest build with correct config

