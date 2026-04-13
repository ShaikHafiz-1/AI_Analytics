# Blob Retry Failure Diagnosis

## Issue
When clicking "Retry Blob" from the UI, the blob data loading is failing.

## Root Causes to Check

### 1. Blob Connection String Invalid
**Check**: `local.settings.json` - `BLOB_CONNECTION_STRING`
- Verify the connection string is correct
- Check if account key is still valid
- Verify account name matches: `planningdatapi`

### 2. Blob Container/Files Don't Exist
**Check**: Azure Storage Explorer
- Container: `planning-data`
- Files: `current.csv`, `previous.csv`
- Verify files are not empty
- Verify files have required columns: LOCID, PRDID, GSCEQUIPCAT

### 3. Authentication Failed
**Check**: Azure Storage credentials
- Account name: `planningdatapi`
- Account key in `local.settings.json`
- Verify key hasn't been rotated

### 4. Network/Connectivity Issue
**Check**: Network connectivity
- Can you reach Azure Storage from your machine?
- Is there a firewall blocking the connection?
- Is the Azure Storage account accessible?

## Debugging Steps

### Step 1: Test Blob Connection Directly
```bash
# Test with curl to debug-snapshot endpoint
curl -X POST http://localhost:7071/api/debug-snapshot \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

Expected response should show snapshot info or error details.

### Step 2: Check Azure Functions Logs
```bash
# In the terminal where func start is running, look for error messages
# Should show: "Blob load failed: ..." with specific error
```

### Step 3: Verify Blob Configuration
```bash
# Check local.settings.json
cat planning_intelligence/local.settings.json | jq '.Values | {BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME, BLOB_CURRENT_FILE, BLOB_PREVIOUS_FILE}'
```

### Step 4: Test Blob Loader Directly
```bash
# Run Python script to test blob loading
cd planning_intelligence
python -c "
from blob_loader import load_current_previous_from_blob
try:
    current, previous = load_current_previous_from_blob()
    print(f'Success: {len(current)} current, {len(previous)} previous records')
except Exception as e:
    print(f'Error: {e}')
"
```

## Common Error Messages and Solutions

### Error: "Blob not found: planning-data/current.csv"
**Solution**:
1. Verify container name in `local.settings.json`
2. Verify file names in `local.settings.json`
3. Check Azure Storage Explorer to confirm files exist
4. Upload files if missing

### Error: "Authentication failed for blob"
**Solution**:
1. Verify `BLOB_CONNECTION_STRING` in `local.settings.json`
2. Check if account key is still valid
3. Regenerate account key if needed
4. Update `local.settings.json` with new key

### Error: "Empty file content"
**Solution**:
1. Verify CSV files are not empty
2. Check file sizes in Azure Storage Explorer
3. Re-upload files if corrupted
4. Ensure files have data rows (not just headers)

### Error: "Missing required columns"
**Solution**:
1. Verify CSV files have columns: LOCID, PRDID, GSCEQUIPCAT
2. Check column names are exact (case-sensitive)
3. Re-upload files with correct column names

## Frontend Retry Logic

When user clicks "Retry Blob" button:
1. Frontend calls `fetchDashboard({})`
2. Backend tries to load from cached snapshot first
3. If no snapshot, loads from blob storage
4. If blob load fails, returns 500 error
5. Frontend catches error and shows error message

## Blob Loading Flow

```
Frontend "Retry Blob" button
    ↓
fetchDashboard({})
    ↓
POST /api/planning-dashboard-v2
    ↓
Check cached snapshot
    ├─ If exists → Return cached data ✅
    └─ If not → Load from blob
         ↓
    load_current_previous_from_blob()
         ↓
    BlobServiceClient.from_connection_string()
         ↓
    Download current.csv & previous.csv
         ↓
    Parse CSV files
         ↓
    Validate required columns
         ↓
    Return data ✅ or Error ❌
```

## Quick Fixes

### Fix 1: Verify Blob Connection String
```bash
# Check if connection string is valid
cd planning_intelligence
python -c "
import os
from azure.storage.blob import BlobServiceClient

conn_str = os.environ.get('BLOB_CONNECTION_STRING')
if not conn_str:
    print('ERROR: BLOB_CONNECTION_STRING not set')
else:
    try:
        client = BlobServiceClient.from_connection_string(conn_str)
        print('✅ Connection string is valid')
        print(f'Account name: {client.account_name}')
    except Exception as e:
        print(f'❌ Connection string error: {e}')
"
```

### Fix 2: Verify Blob Files Exist
```bash
# Check if files exist in blob storage
cd planning_intelligence
python -c "
import os
from azure.storage.blob import BlobServiceClient

conn_str = os.environ.get('BLOB_CONNECTION_STRING')
container = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')
previous_file = os.environ.get('BLOB_PREVIOUS_FILE', 'previous.csv')

try:
    client = BlobServiceClient.from_connection_string(conn_str)
    container_client = client.get_container_client(container)
    
    blobs = list(container_client.list_blobs())
    print(f'Blobs in {container}:')
    for blob in blobs:
        print(f'  - {blob.name} ({blob.size} bytes)')
    
    if not any(b.name == current_file for b in blobs):
        print(f'❌ Missing: {current_file}')
    if not any(b.name == previous_file for b in blobs):
        print(f'❌ Missing: {previous_file}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Fix 3: Trigger Daily Refresh
```bash
# Trigger daily refresh to create snapshot
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

After daily refresh succeeds, retry blob should work (uses cached snapshot).

## Monitoring

### Check Azure Functions Logs
```bash
# Look for blob-related errors in the terminal where func start is running
# Should show: "Blob load failed: ..." with specific error message
```

### Check Response Status
```bash
# Use curl with verbose output to see response details
curl -v -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' 2>&1 | grep -A 20 "< HTTP"
```

## Next Steps

1. Run diagnostic commands above to identify the specific error
2. Check Azure Storage Explorer to verify blob files exist
3. Verify connection string in `local.settings.json`
4. Run daily refresh to create snapshot
5. Retry blob loading from UI

## Support

If blob retry continues to fail:
1. Check Azure Storage account status
2. Verify network connectivity to Azure
3. Check if account key needs to be regenerated
4. Verify CSV files are valid and not corrupted
5. Check Azure Functions logs for detailed error messages
