# Frontend-Backend Integration - Visual Flow

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          USER OPENS BROWSER                                │
│                      http://localhost:3000                                 │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    FRONTEND: DashboardPage.tsx                             │
│                                                                             │
│  1. Component mounts                                                       │
│  2. useEffect hook runs                                                    │
│  3. Checks REACT_APP_USE_MOCK (false)                                      │
│  4. Calls fetchDashboard({})                                               │
│  5. Shows loading skeleton                                                 │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    FRONTEND: api.ts - fetchDashboard()                     │
│                                                                             │
│  1. Constructs URL:                                                        │
│     http://localhost:7071/api/planning-dashboard-v2                        │
│  2. Makes POST request                                                     │
│  3. Body: { mode: "blob" }                                                 │
│  4. Headers: { "Content-Type": "application/json" }                        │
│  5. Waits for response                                                     │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │   CORS Preflight     │        │   Actual Request     │
        │   OPTIONS Request    │        │   POST Request       │
        │                      │        │                      │
        │  Backend responds:   │        │  Backend processes   │
        │  200 OK              │        │  and responds        │
        │  CORS headers        │        │                      │
        └──────────────────────┘        └──────────────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              BACKEND: function_app.py - planning_dashboard_v2()            │
│                                                                             │
│  1. Receives POST request                                                  │
│  2. Parses JSON body                                                       │
│  3. Extracts location_id, material_group (if provided)                     │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │  FAST PATH           │        │  SLOW PATH           │
        │  Snapshot Cache      │        │  Blob Loading        │
        │                      │        │                      │
        │  1. load_snapshot()  │        │  1. load_current_    │
        │  2. If exists:       │        │     previous_from_   │
        │     - Filter if      │        │     blob()           │
        │       needed         │        │  2. normalize_rows() │
        │     - Return cached  │        │  3. filter_records() │
        │       response       │        │  4. compare_records()│
        │     - DONE!          │        │  5. Continue...      │
        │                      │        │                      │
        └──────────────────────┘        └──────────────────────┘
                    │                                 │
                    │                                 ▼
                    │                    ┌──────────────────────┐
                    │                    │  BACKEND: Blob       │
                    │                    │  Storage             │
                    │                    │                      │
                    │                    │  1. Connect to       │
                    │                    │     Azure Blob       │
                    │                    │  2. Download         │
                    │                    │     current.csv      │
                    │                    │  3. Download         │
                    │                    │     previous.csv     │
                    │                    │  4. Parse CSV        │
                    │                    │  5. Return rows      │
                    │                    │                      │
                    │                    └──────────────────────┘
                    │                                 │
                    │                                 ▼
                    │                    ┌──────────────────────┐
                    │                    │  BACKEND:            │
                    │                    │  response_builder.py │
                    │                    │                      │
                    │                    │  1. Compute health   │
                    │                    │  2. Call MCP tools   │
                    │                    │  3. Generate insights│
                    │                    │  4. Build summaries  │
                    │                    │  5. Return response  │
                    │                    │                      │
                    │                    └──────────────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              BACKEND: Return Response with CORS Headers                    │
│                                                                             │
│  HTTP 200 OK                                                               │
│  Access-Control-Allow-Origin: http://localhost:3000                        │
│  Content-Type: application/json                                            │
│                                                                             │
│  Body: {                                                                   │
│    "dataMode": "blob",                                                     │
│    "planningHealth": 75,                                                   │
│    "totalRecords": 150,                                                    │
│    "changedRecordCount": 45,                                               │
│    "riskSummary": {...},                                                   │
│    "detailRecords": [...]                                                  │
│  }                                                                          │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              FRONTEND: Receive Response in fetchDashboard()                │
│                                                                             │
│  1. Check response.ok (should be true)                                     │
│  2. Parse JSON                                                             │
│  3. Return data                                                            │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              FRONTEND: DashboardPage.tsx - .then() Handler                 │
│                                                                             │
│  1. validateDashboardResponse(data)                                        │
│  2. setData(data)                                                          │
│  3. setLoading(false)                                                      │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              FRONTEND: buildDashboardContext(data)                         │
│                                                                             │
│  Transforms API response into context object:                             │
│  - planningHealth, status                                                  │
│  - forecastNew, forecastOld, trendDelta, trendDirection                    │
│  - totalRecords, changedRecordCount                                        │
│  - riskSummary, aiInsight, rootCause                                       │
│  - alerts, drivers, filters                                                │
│  - datacenterSummary, materialGroupSummary                                 │
│  - supplierSummary, designSummary, rojSummary                              │
│  - detailRecords                                                           │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              FRONTEND: Render Dashboard                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Header: Planning Intelligence                                       │  │
│  │ Data Mode: blob | Last Refreshed: 2024-04-13T10:30:00Z             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ AI Insight Card | Ask Copilot Button                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────┬──────────────────┬──────────────────┐               │
│  │ Planning Health  │ Forecast         │ Trend & Changes  │               │
│  │ 75/100           │ +5,000 units     │ Increasing       │               │
│  └──────────────────┴──────────────────┴──────────────────┘               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Summary Tiles: Total Records, Changed, Unchanged, New              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Alert Banner (if triggered)                                         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Top Risk Areas Table                                                │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────┬──────────────────┐                                  │
│  │ Datacenter Card  │ Material Group   │                                  │
│  └──────────────────┴──────────────────┘                                  │
│                                                                             │
│  ┌──────────────────┬──────────────────┬──────────────────┐               │
│  │ Supplier Card    │ Design Card      │ ROJ Card         │               │
│  └──────────────────┴──────────────────┴──────────────────┘               │
│                                                                             │
│  ┌──────────────────┬──────────────────┐                                  │
│  │ Risk Card        │ Root Cause Card  │                                  │
│  └──────────────────┴──────────────────┘                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Recommended Actions Panel                                           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Copilot Panel (if open)                                             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                          ✅ DASHBOARD DISPLAYS
                          ✅ DATA VISIBLE
                          ✅ USER CAN INTERACT
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    fetchDashboard() Error Handling                         │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │  Network Error       │        │  API Error (500)     │
        │  (Connection Failed) │        │  (Backend Error)     │
        │                      │        │                      │
        │  .catch() triggered  │        │  .catch() triggered  │
        │  Error message:      │        │  Error message:      │
        │  "Failed to fetch"   │        │  "API error 500:..." │
        │                      │        │                      │
        └──────────────────────┘        └──────────────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              DashboardPage.tsx - .catch() Handler                          │
│                                                                             │
│  1. setError(`Blob data unavailable: ${err.message}`)                      │
│  2. setBlobFailed(true)                                                    │
│  3. setLoading(false)                                                      │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              FRONTEND: Show Error Banner                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ ❌ Blob data unavailable                                            │  │
│  │ Error: Failed to fetch                                              │  │
│  │                                                                     │  │
│  │ [Retry Blob] [Load Mock Data]                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │  User Clicks         │        │  User Clicks         │
        │  "Retry Blob"        │        │  "Load Mock Data"    │
        │                      │        │                      │
        │  Retry API call      │        │  Load sample_payload │
        │  (same flow)         │        │  Set isMockData=true │
        │                      │        │  Render dashboard    │
        └──────────────────────┘        └──────────────────────┘
```

## Component Hierarchy

```
App.tsx
  └── DashboardPage.tsx
      ├── Header
      │   ├── Logo
      │   ├── Title
      │   ├── Data Mode Badge
      │   └── Timestamp
      │
      ├── Error Banner (if error)
      │   ├── Error Message
      │   ├── Retry Button
      │   └── Load Mock Data Button
      │
      ├── Main Content
      │   ├── AI Insight Card
      │   ├── Ask Copilot Button
      │   │
      │   ├── KPI Cards
      │   │   ├── PlanningHealthCard
      │   │   ├── ForecastCard
      │   │   └── TrendCard
      │   │
      │   ├── SummaryTiles
      │   │   ├── Total Records
      │   │   ├── Changed Records
      │   │   ├── Unchanged Records
      │   │   └── New Records
      │   │
      │   ├── Alert Banner (if triggered)
      │   │
      │   ├── TopRiskTable
      │   │
      │   ├── Location & Material Cards
      │   │   ├── DatacenterCard
      │   │   └── MaterialGroupCard
      │   │
      │   ├── Supplier, Design, ROJ Cards
      │   │   ├── SupplierCard
      │   │   ├── DesignCard
      │   │   └── RojCard
      │   │
      │   ├── Risk & Root Cause Cards
      │   │   ├── RiskCard
      │   │   └── RootCauseCard
      │   │
      │   └── ActionsPanel
      │
      ├── CopilotPanel (if open)
      │   ├── Question Input
      │   ├── Chat History
      │   └── Answer Display
      │
      ├── DrillDownPanel (if selected)
      │   ├── Location Details
      │   ├── Material Details
      │   ├── Supplier Details
      │   └── Risk Details
      │
      └── DebugPanel (if DEBUG_MODE=true)
          ├── Raw Response Fields
          ├── Card-to-Field Mapping
          ├── Calculation Trace
          └── Copy JSON Button
```

## State Management

```
DashboardPage State:
├── data: DashboardResponse | null
│   └── Contains all dashboard data from API
│
├── loading: boolean
│   └── true while fetching, false when done
│
├── error: string | null
│   └── Error message if API fails
│
├── copilotOpen: boolean
│   └── true if Copilot panel is open
│
├── blobFailed: boolean
│   └── true if blob load failed
│
├── isMockData: boolean
│   └── true if using mock data
│
└── drillDown: { type: DrillDownType; item: string } | null
    └── Current drill-down selection
```

## Configuration Flow

```
Environment Variables
├── Frontend (.env)
│   ├── PORT=3000
│   ├── REACT_APP_API_URL=http://localhost:7071/api
│   ├── REACT_APP_USE_MOCK=false
│   └── REACT_APP_DEBUG_MODE=false
│
└── Backend (local.settings.json)
    ├── BLOB_CONNECTION_STRING
    ├── BLOB_CONTAINER_NAME=planning-data
    ├── BLOB_CURRENT_FILE=current.csv
    ├── BLOB_PREVIOUS_FILE=previous.csv
    ├── AZURE_OPENAI_KEY
    ├── AZURE_OPENAI_ENDPOINT
    └── Host.CORS=http://localhost:3000
```

