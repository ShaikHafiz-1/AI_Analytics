# Planning Intelligence — System Design

**Version:** 2.0  
**Date:** March 2026  
**Status:** Production

---

## 1. Introduction

### Business Problem

Enterprise demand planning teams face three core challenges:

- **Visibility** — No real-time view of what changed between planning cycles
- **Change Tracking** — Manual effort to identify quantity, supplier, design, and schedule changes
- **Risk Detection** — No automated mechanism to flag high-risk records before they impact supply

### Goal

Transform static Excel-based planning reports into an AI-driven intelligence platform that:

- Automatically detects and classifies changes between planning versions
- Generates business-readable insights using GenAI
- Surfaces risk, root cause, and recommended actions without manual analysis
- Evolves toward auto-triggered proactive intelligence

---

## 2. System Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     UI LAYER                            │
│         React Dashboard  /  Copilot Studio              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP POST
┌────────────────────────▼────────────────────────────────┐
│                    API LAYER                            │
│         Azure Function App (pi-planning-intelligence)   │
│  /planning-dashboard-v2  /daily-refresh  /explain       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   DATA LAYER                            │
│         Azure Blob Storage                              │
│         current.xlsx  |  previous.xlsx                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                ANALYTICS LAYER                          │
│  Normalize → Filter → Compare → Classify → Aggregate   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    AI LAYER                             │
│         LLM Insight Engine (Azure OpenAI)               │
│         MCP — Model Context Protocol                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               RESPONSE BUILDER                          │
│         Dashboard JSON  |  Insights  |  Alerts          │
└─────────────────────────────────────────────────────────┘
```

### End-to-End Data Flow

1. Daily refresh loads `current.xlsx` and `previous.xlsx` from Azure Blob Storage
2. Analytics pipeline normalizes, filters, compares, and classifies records
3. LLM Insight Engine converts structured analytics into business narrative
4. Response Builder assembles the full dashboard payload
5. Snapshot saved to persistent storage for fast UI load
6. React UI fetches cached snapshot and renders cards, charts, and insights

---

## 3. Data Ingestion Layer

### Primary Source — Azure Blob Storage

Blob Storage is the default and primary data source. Two Excel files are expected per planning cycle:

| File | Purpose |
|------|---------|
| `current.xlsx` | Current planning version |
| `previous.xlsx` | Previous planning version for comparison |

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `BLOB_CONNECTION_STRING` | Azure Storage connection string |
| `BLOB_CONTAINER_NAME` | Container name (default: `planning-data`) |
| `BLOB_CURRENT_FILE` | Blob name for current file (default: `current.xlsx`) |
| `BLOB_PREVIOUS_FILE` | Blob name for previous file (default: `previous.xlsx`) |

### Column Requirements

Files must contain these columns (aliases supported):

| Canonical Name | Accepted Aliases |
|---------------|-----------------|
| `LOCID` | `LOC ID` |
| `PRDID` | `PRD ID`, `MATERIAL ID` |
| `GSCEQUIPCAT` | `EQUIPMENT CATEGORY` |

### Legacy Source — SharePoint (Optional)

SharePoint remains supported as a fallback via `mode=sharepoint`. It is no longer the default. Configure via `SHAREPOINT_*` environment variables if needed.

---

## 4. Analytics Engine

### Pipeline

```
Raw Excel Rows
     │
     ▼
normalize_rows()        — standardize fields, types, casing
     │
     ▼
filter_records()        — optional location_id / material_group filter
     │
     ▼
compare_records()       — match current vs previous by LOCID + PRDID
     │
     ▼
Change Detection:
  - Quantity changed     (FCSTQTY delta)
  - Supplier changed     (SUPPLIER field)
  - Design changed       (BOD / FF fields)
  - ROJ changed          (need-by date shift)
     │
     ▼
Classification:
  - Change type label    (quantity-driven, supplier-driven, etc.)
  - Risk level           (Normal / Medium / High / Critical)
     │
     ▼
Aggregation:
  - changes_by_location()
  - changes_by_material_group()
  - change_driver_analysis()
  - high_risk_records()
```

---

## 5. Trend Engine

Multi-snapshot analysis across historical planning cycles.

### Input

Array of snapshots, each representing one planning cycle.

### Features

| Feature | Description |
|---------|-------------|
| Consistently Increasing | Records with demand growing across all snapshots |
| Recurring Changes | Records that change repeatedly (configurable threshold) |
| One-Off Spikes | Isolated large changes not seen in other cycles |
| Change Streaks | Records with N consecutive cycles of change |

### Key Functions

- `analyze_trends()` — full multi-snapshot analysis
- `get_consistently_increasing()` — upward trend detection
- `get_recurring_changes()` — repeat change detection
- `get_one_off_spikes()` — anomaly detection
- `get_change_streaks()` — streak analysis

---

## 6. Dashboard Model

The response builder assembles a structured JSON payload consumed by the UI.

### Output Structure

```json
{
  "planningHealth": 82,
  "status": "At Risk",
  "forecastNew": 142500,
  "forecastOld": 138000,
  "trendDelta": 4500,
  "trendDirection": "increasing",
  "totalRecords": 320,
  "changedRecordCount": 47,
  "datacenterSummary": [...],
  "materialGroupSummary": [...],
  "supplierSummary": [...],
  "designSummary": [...],
  "rojSummary": [...],
  "riskSummary": { "highRiskCount": 12, "riskBreakdown": {...} },
  "rootCause": { "primaryDriver": "quantity", ... },
  "aiInsight": "...",
  "recommendedActions": ["...", "..."],
  "alerts": { "shouldTrigger": true, "message": "..." },
  "drivers": {...},
  "dataMode": "cached",
  "lastRefreshedAt": "2026-03-29T12:00:00Z"
}
```

---

## 7. LLM Insight Engine

### Purpose

Converts structured analytics context into executive-ready business narrative using Azure OpenAI.

### Outputs

| Field | Description |
|-------|-------------|
| `aiInsight` | Plain-language summary of the planning situation |
| `rootCause` | Primary driver of change with supporting evidence |
| `recommendedActions` | Actionable steps for planners |
| `alerts` | Triggered when risk or change thresholds are exceeded |

### Guardrail System

Before calling the LLM, the engine applies deterministic guardrails:

- Fully stable → skip LLM, return static message
- Only quantity changed → return quantity-specific narrative
- Only supplier changed → return supplier-specific narrative
- Only schedule changed → return ROJ-specific narrative
- Mixed changes → call LLM for nuanced reasoning

### Fallback

If LLM is unavailable or not configured, a deterministic fallback generates structured insights from analytics data without any AI call.

### Explainability Endpoint

`POST /explain` accepts a natural language question and returns focused insight from the cached snapshot or live analytics:

```json
{
  "question": "Why did forecast increase at LOC001?",
  "mode": "cached",
  "location_id": "LOC001"
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_KEY` | API key |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name (e.g. `gpt-4o`) |
| `AZURE_OPENAI_API_VERSION` | API version (default: `2024-02-01`) |
| `LLM_TIMEOUT_SECONDS` | Request timeout (default: `10`) |

---

## 8. MCP Architecture

### Model Context Protocol

MCP provides a standardized interface layer between the analytics engine, LLM, and UI consumers (including Copilot Studio).

### Purpose

- Structures analytics context into typed schemas before LLM consumption
- Enables reusable, testable prompt construction
- Decouples analytics logic from LLM implementation
- Supports enterprise scalability and auditability

### Key Schemas

| Schema | Description |
|--------|-------------|
| `AnalyticsContext` | Full analytics summary passed to LLM |
| `RiskSummary` | Risk level breakdown |
| `RootCauseContext` | Primary driver and change type |
| `RecommendationContext` | Deterministic action list |

### MCP Tools

Defined in `mcp/tools.py` — expose analytics capabilities as callable tools for Copilot Studio or agent frameworks.

---

## 9. API Layer — Azure Functions

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/planning-intelligence` | POST | Raw analytics queries (summary, trends, risk) |
| `/planning-dashboard` | POST | Full dashboard payload (v1) |
| `/planning-dashboard-v2` | POST | Hybrid AI dashboard with mode switching |
| `/daily-refresh` | POST | Triggers blob load, analytics, snapshot save |
| `/explain` | POST | Focused insight for a specific question |

### Modes (`/planning-dashboard-v2`)

| Mode | Description |
|------|-------------|
| `cached` (default) | Returns stored daily snapshot instantly |
| `live` | Processes `current_rows` / `previous_rows` from request body |
| `blob` | Reads directly from Azure Blob Storage |
| `sharepoint` | Reads from SharePoint (legacy fallback) |

### Authentication

All endpoints use Azure Function key authentication (`?code=<key>`).

---

## 10. Snapshot & Auto-Trigger System

### Daily Refresh Job

`run_daily_refresh.py` orchestrates the full pipeline:

1. Load `current.xlsx` + `previous.xlsx` from Blob Storage
2. Run normalize → filter → compare → analytics
3. Call LLM Insight Engine
4. Build full dashboard response
5. Save snapshot to `snapshot.json`

Triggered via `POST /daily-refresh` — can be scheduled using Azure Logic Apps or a Timer Trigger.

### Snapshot Storage

- Default path: `/tmp/planning_snapshot.json`
- Production: mount Azure Files share, set `SNAPSHOT_FILE_PATH`
- In-memory fallback if file system is unavailable

### Benefits

- Sub-100ms UI load (no live computation on page load)
- Historical comparison across refresh cycles
- Foundation for auto-triggered alerts

---

## 11. UI Layer

### React Dashboard

Built with React (TypeScript), Tailwind CSS, hosted on Azure Blob static website.

### Cards

| Card | Data Source |
|------|------------|
| Planning Health | `planningHealth` score (0–100) |
| Forecast | `forecastNew`, `forecastOld`, `trendDelta` |
| Trend | `trendDirection`, `changedRecordCount` |
| Summary Tiles | KPI counts |
| AI Insight | `aiInsight` (LLM-generated) |
| Root Cause | `rootCause` |
| Risk | `riskSummary` |
| Datacenter | `datacenterSummary` |
| Material Group | `materialGroupSummary` |
| Supplier | `supplierSummary` |
| Design | `designSummary` |
| ROJ | `rojSummary` |
| Actions Panel | `recommendedActions` |

### Configuration

| Variable | Description |
|----------|-------------|
| `REACT_APP_USE_MOCK` | Set to `false` for live data |
| `REACT_APP_API_URL` | Azure Function App base URL |
| `REACT_APP_API_KEY` | Function host key |

---

## 12. Auto-Triggered Insights

### Vision

Move from query-driven to proactive intelligence — the system detects anomalies and triggers alerts without user action.

### Capabilities (Current)

- Alert rules evaluate risk thresholds on every refresh
- `alerts.shouldTrigger` flag drives UI banner display
- `/explain` endpoint supports Copilot Studio integration for conversational drill-down

### Roadmap

- Timer-triggered daily refresh with alert dispatch
- Email / Teams notification on threshold breach
- Anomaly scoring per record
- Predictive demand shift detection

---

## 13. Deployment Architecture

```
GitHub (main branch)
     │
     ├── push to planning_intelligence/**
     │        └── deploy.yml → Azure Functions (pi-planning-intelligence)
     │
     └── push to frontend/**
              └── deploy-frontend.yml → Azure Blob ($web container)
                                         planningdatapi.z30.web.core.windows.net
```

### Components

| Component | Azure Service |
|-----------|--------------|
| Backend API | Azure Function App (Python 3.13, Consumption plan) |
| Data Files | Azure Blob Storage (`planning-data` container) |
| Snapshot | Azure Files (mounted) or `/tmp` fallback |
| Frontend UI | Azure Blob Static Website |
| CI/CD | GitHub Actions |

---

## 14. Security & Access

- All API endpoints protected by Azure Function key (`AuthLevel.FUNCTION`)
- Blob Storage accessed via connection string (stored in Function App settings)
- Azure OpenAI key stored as environment variable, never in code
- Frontend `.env` excluded from git via `.gitignore`
- GitHub Secrets used for all CI/CD credentials
- CORS configured on Function App to allow only the static website origin

---

## 15. Known Issues & Limitations

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| CORS must be configured manually | Browser blocks API calls | Add static website URL to Function App CORS settings |
| Snapshot stored in `/tmp` | Lost on Function App restart | Mount Azure Files share, set `SNAPSHOT_FILE_PATH` |
| UI falls back to mock data if API fails | Shows stale data silently | Add visible error state in UI |
| `react-scripts` incompatible with Node 24 | Build fails | Use Node 18 LTS via nvm |
| Python version mismatch (local 3.11 vs Azure 3.13) | Potential module errors | Align local and Azure Python versions |

---

## 16. Future Enhancements

| Enhancement | Description |
|-------------|-------------|
| Real-time streaming | WebSocket or SSE for live planning updates |
| Agent-based decisioning | Autonomous planning recommendations via AI agents |
| Predictive forecasting | ML models for demand shift prediction |
| ERP integration | Direct SAP / D365 data ingestion |
| Multi-tenant support | Isolated analytics per business unit |
| Audit trail | Change history log per planning record |
| Teams integration | Proactive alerts via Microsoft Teams adaptive cards |
| Power BI connector | Expose analytics as Power BI dataset |
