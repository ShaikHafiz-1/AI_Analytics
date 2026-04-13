# Static Frontend → Backend Connection

## YES - It Works Perfectly!

Static React apps connect to backends all the time. This is the standard architecture.

## How It Works

```
User Browser
    ↓
Static React App (from blob storage)
    ↓
Makes HTTP/HTTPS requests
    ↓
Backend API (Azure Functions)
    ↓
Returns JSON data
    ↓
React displays data
```

## Your Setup

**Frontend (Static)**
- URL: `https://planningdatapi.z5.web.core.windows.net/`
- Files: HTML, JS, CSS (static)
- Runs in: Browser (client-side)

**Backend (API)**
- URL: `https://pi-planning-intelligence.azurewebsites.net/api`
- Code: Python Azure Functions
- Runs in: Azure (server-side)

## How Frontend Calls Backend

Your `frontend/src/services/api.ts` does this:

```typescript
const API_URL = process.env.REACT_APP_API_URL; // https://pi-planning-intelligence.azurewebsites.net/api

// Make API call from browser
const response = await fetch(`${API_URL}/planning-dashboard-v2`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});

const result = await response.json();
```

This works because:
1. Browser downloads React app from blob storage
2. React runs in browser
3. Browser makes HTTP request to backend
4. Backend returns data
5. React displays data

## CORS Requirement

For this to work, backend needs CORS headers:

```
Access-Control-Allow-Origin: https://planningdatapi.z5.web.core.windows.net
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
```

Your backend already has this configured in `planning_intelligence/function_app.py`:

```python
@app.route(route='planning-dashboard-v2', methods=['POST'])
def planning_dashboard_v2(req: func.HttpRequest) -> func.HttpResponse:
    # CORS headers already set
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    # ... rest of code
```

## Data Flow Example

1. **User visits**: `https://planningdatapi.z5.web.core.windows.net/`
2. **Browser downloads**: React app (HTML/JS/CSS)
3. **React loads**: Runs in browser
4. **React calls**: `https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2`
5. **Backend processes**: Loads blob data, calculates metrics
6. **Backend returns**: JSON with dashboard data
7. **React displays**: Dashboard with real data

## Real-World Examples

This is how major apps work:
- **Netflix**: Static React frontend → Backend API
- **Spotify**: Static React frontend → Backend API
- **Twitter**: Static React frontend → Backend API
- **Your app**: Static React frontend → Backend API

## Advantages

✅ Frontend and backend are **independent**  
✅ Can deploy separately  
✅ Can scale independently  
✅ Backend can be Python, Node, Java, etc.  
✅ Frontend can be React, Vue, Angular, etc.  
✅ Perfect for microservices  

## Deployment Summary

| Component | Type | Location | URL |
|-----------|------|----------|-----|
| Frontend | Static React | Blob Storage | `https://planningdatapi.z5.web.core.windows.net/` |
| Backend | Python API | Azure Functions | `https://pi-planning-intelligence.azurewebsites.net/api` |
| Data | Blob Storage | Azure Storage | `planningdatapi` container |

## Verification

To verify connection works:

```powershell
# Test backend endpoint
$url = "https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2?code=<YOUR_FUNCTION_KEY>"
$response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
Write-Host "Status: $($response.StatusCode)"
Write-Host "Data: $($response.Content)"
```

If you get 200 and JSON data, backend is working.

Then visit frontend URL and check browser console for any errors.
