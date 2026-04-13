# Blob Data Testing Guide - CURL Commands

## Overview
The system loads data from Azure Blob Storage. There are 3 endpoints that use blob data:
1. **planning-dashboard-v2** - Dashboard with blob-backed data
2. **daily-refresh** - Triggers daily refresh from blob storage
3. **debug-snapshot** - Debug endpoint for snapshot inspection

## Prerequisites
- Azure Functions running locally: `func start` (port 7071)
- Blob storage configured with:
  - Container: `planning-data`
  - Current file: `current.csv`
  - Previous file: `previous.csv`

## Endpoint 1: Planning Dashboard v2 (Blob-backed)

### Description
Reads from cached snapshot first; falls back to blob reload if no snapshot exists.

### CURL Command - Basic Request
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### CURL Command - With Filters
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "locationId": "LOC001",
    "materialGroup": "ELECTRONICS"
  }'
```

### CURL Command - With Pretty Print
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

### Expected Response
```json
{
  "dataMode": "blob",
  "lastRefreshedAt": "2026-04-11T17:30:00Z",
  "planningHealth": 75,
  "status": "Stable",
  "forecastNew": 50000.00,
  "forecastOld": 45000.00,
  "trendDirection": "Increase",
  "trendDelta": 5000.00,
  "datacenterCount": 5,
  "materialGroups": ["ELECTRONICS", "MECHANICAL", "OPTICAL"],
  "totalRecords": 1250,
  "changedRecordCount": 320,
  "unchangedRecordCount": 930,
  "newRecordCount": 45,
  "riskSummary": {...},
  "aiInsight": "Planning health is Stable. Forecast trend is Increase.",
  "rootCause": ["quantity", "Quantity + Design"],
  "recommendedActions": [...],
  "detailRecords": [...]
}
```

## Endpoint 2: Daily Refresh (Blob Reload)

### Description
Triggers daily refresh from Azure Blob Storage and saves a snapshot for future use.

### CURL Command - Trigger Refresh
```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}'
```

### CURL Command - With Verbose Output
```bash
curl -v -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

### Expected Response
```json
{
  "status": "success",
  "message": "Daily refresh completed",
  "recordsProcessed": 1250,
  "changedRecords": 320,
  "newRecords": 45,
  "timestamp": "2026-04-11T17:30:00Z",
  "dataMode": "blob",
  "planningHealth": 75,
  "forecastDelta": 5000.00
}
```

## Endpoint 3: Debug Snapshot

### Description
Debug endpoint for inspecting snapshot data and blob status.

### CURL Command - Get Snapshot Info
```bash
curl -X POST http://localhost:7071/api/debug-snapshot \
  -H "Content-Type: application/json" \
  -d '{}'
```

### CURL Command - With Pretty Print
```bash
curl -X POST http://localhost:7071/api/debug-snapshot \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

### Expected Response
```json
{
  "snapshotExists": true,
  "snapshotAge": "2 hours",
  "lastRefreshedAt": "2026-04-11T15:30:00Z",
  "blobStatus": "connected",
  "blobContainer": "planning-data",
  "currentFile": "current.csv",
  "previousFile": "previous.csv",
  "recordCount": 1250,
  "changedCount": 320,
  "newCount": 45
}
```

## Testing Scenarios

### Scenario 1: Test Blob Connection
```bash
# Trigger daily refresh to test blob connectivity
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.status'
```

### Scenario 2: Test Dashboard with Filters
```bash
# Test dashboard with specific location filter
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "locationId": "LOC001"
  }' | jq '.planningHealth, .totalRecords, .changedRecordCount'
```

### Scenario 3: Test Material Group Filter
```bash
# Test dashboard with material group filter
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "materialGroup": "ELECTRONICS"
  }' | jq '.materialGroupSummary'
```

### Scenario 4: Full Data Inspection
```bash
# Get complete response with all details
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.' > blob_response.json
```

## Troubleshooting

### Error: "Blob not found"
```bash
# Check blob configuration
curl -X POST http://localhost:7071/api/debug-snapshot \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.blobStatus'
```

### Error: "Authentication failed"
- Verify `BLOB_CONNECTION_STRING` in `local.settings.json`
- Check Azure Storage account credentials
- Ensure blob container exists

### Error: "Empty file content"
- Verify `current.csv` and `previous.csv` exist in blob container
- Check file sizes are not zero
- Ensure files have required columns: LOCID, PRDID, GSCEQUIPCAT

## Advanced Testing

### Test with Custom Headers
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -H "X-Debug: true" \
  -d '{}' | jq '.'
```

### Test with Timeout
```bash
curl --max-time 30 -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

### Save Response to File
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' > dashboard_response.json
```

### Extract Specific Fields
```bash
# Get only planning health and risk level
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '{planningHealth: .planningHealth, riskLevel: .riskSummary.level, changedCount: .changedRecordCount}'
```

## Data Flow

```
CURL Request
    ↓
Azure Functions (port 7071)
    ↓
planning-dashboard-v2 endpoint
    ↓
Check snapshot cache
    ├─ If exists → Return cached data (fast)
    └─ If not → Load from blob storage
         ↓
    blob_loader.load_current_previous_from_blob()
         ↓
    Azure Blob Storage (planningdatapi)
         ↓
    Download current.csv & previous.csv
         ↓
    Parse & normalize data
         ↓
    Run analytics pipeline
         ↓
    Build response
         ↓
    Return JSON response
```

## Performance Notes

- **First request**: ~2-5 seconds (loads from blob)
- **Subsequent requests**: <500ms (uses cached snapshot)
- **Daily refresh**: ~3-10 seconds (reloads all data)
- **Blob download**: Depends on file size (typically 1-3 seconds)

## Environment Variables

From `local.settings.json`:
```json
{
  "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;...",
  "BLOB_CONTAINER_NAME": "planning-data",
  "BLOB_CURRENT_FILE": "current.csv",
  "BLOB_PREVIOUS_FILE": "previous.csv"
}
```

## Next Steps

1. Run `func start` to start Azure Functions
2. Execute one of the CURL commands above
3. Verify response contains expected data
4. Check `dataMode` field shows "blob"
5. Inspect `detailRecords` for actual data
