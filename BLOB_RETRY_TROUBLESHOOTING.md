# Blob Retry Failure - Troubleshooting Guide

## Quick Diagnosis

When "Retry Blob" fails from the UI, follow these steps to identify the issue:

### Step 1: Run Blob Connection Test
```bash
cd planning_intelligence
python test_blob_connection.py
```

This will test:
1. ✅ Connection string validation
2. ✅ BlobServiceClient creation
3. ✅ Container access
4. ✅ Required blob files exist
5. ✅ Blob loading works

### Step 2: Check Azure Functions Logs
Look at the terminal where `func start` is running for error messages like:
```
Blob load failed: Blob not found: planning-data/current.csv
Blob load failed: Authentication failed for blob
Blob load failed: Empty file content
```

### Step 3: Test Endpoint Directly
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

Check the response for error details.

---

## Common Issues and Solutions

### Issue 1: "Blob not found"
**Error Message**: `Blob load failed: Blob not found: planning-data/current.csv`

**Causes**:
- Container doesn't exist
- Files don't exist in container
- Wrong container name in `local.settings.json`
- Wrong file names in `local.settings.json`

**Solutions**:
1. Check `local.settings.json`:
   ```json
   {
     "BLOB_CONTAINER_NAME": "planning-data",
     "BLOB_CURRENT_FILE": "current.csv",
     "BLOB_PREVIOUS_FILE": "previous.csv"
   }
   ```

2. Verify files exist in Azure Storage Explorer:
   - Open Azure Storage Explorer
   - Navigate to: Storage Accounts → planningdatapi → Blob Containers → planning-data
   - Verify `current.csv` and `previous.csv` exist

3. If files don't exist, upload them:
   - Download sample CSV files
   - Upload to `planning-data` container
   - Ensure file names match exactly

### Issue 2: "Authentication failed"
**Error Message**: `Blob load failed: Authentication failed for blob`

**Causes**:
- Invalid connection string
- Account key is expired/rotated
- Wrong account name
- Credentials don't have access

**Solutions**:
1. Verify connection string in `local.settings.json`:
   ```json
   {
     "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=...;EndpointSuffix=core.windows.net"
   }
   ```

2. Check account name matches: `planningdatapi`

3. Regenerate account key if needed:
   - Go to Azure Portal
   - Storage Accounts → planningdatapi
   - Access Keys → Regenerate key1
   - Copy new key to `local.settings.json`

4. Restart Azure Functions:
   ```bash
   # Stop: Ctrl+C
   # Start: func start
   ```

### Issue 3: "Empty file content"
**Error Message**: `Blob load failed: Empty file content for current`

**Causes**:
- CSV file is empty (0 bytes)
- CSV file only has headers, no data rows
- File is corrupted

**Solutions**:
1. Check file size in Azure Storage Explorer
2. Download file and verify it has data rows
3. Re-upload file if corrupted
4. Ensure file format is valid CSV

### Issue 4: "Missing required columns"
**Error Message**: `Blob load failed: Missing required columns in current: {'LOCID', 'PRDID', 'GSCEQUIPCAT'}`

**Causes**:
- CSV columns don't match expected names
- Column names are case-sensitive
- File has wrong structure

**Solutions**:
1. Verify CSV has these exact columns:
   - `LOCID` (Location ID)
   - `PRDID` (Product ID)
   - `GSCEQUIPCAT` (Equipment Category)

2. Column names are case-sensitive - must be UPPERCASE

3. Re-upload CSV with correct column names

### Issue 5: "Connection timeout"
**Error Message**: `Blob load failed: Connection timeout` or `Connection refused`

**Causes**:
- Network connectivity issue
- Azure Storage is unreachable
- Firewall blocking connection
- Azure account is down

**Solutions**:
1. Check network connectivity:
   ```bash
   ping storage.azure.com
   ```

2. Verify Azure Storage account is accessible:
   - Go to Azure Portal
   - Check Storage Account status
   - Verify account is not disabled

3. Check firewall rules:
   - Ensure your IP is not blocked
   - Check if VPN is needed

4. Try again after a few minutes

---

## Workarounds

### Workaround 1: Use Mock Data
If blob is not available, use mock data from UI:
1. Click "Retry Blob" button
2. When it fails, click "Load Mock Data" button
3. UI will load sample data for testing

### Workaround 2: Trigger Daily Refresh First
Daily refresh creates a cached snapshot, so subsequent retries use cache:
```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

After daily refresh succeeds, retry blob should work (uses cached snapshot).

### Workaround 3: Use Debug Endpoint
Test if snapshot exists:
```bash
curl -X POST http://localhost:7071/api/debug-snapshot \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

If snapshot exists, retry blob will use it (fast path).

---

## Advanced Debugging

### Enable Verbose Logging
Add logging to blob_loader.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Test Blob Connection Directly
```python
from azure.storage.blob import BlobServiceClient
import os

conn_str = os.environ.get('BLOB_CONNECTION_STRING')
container = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')

try:
    client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = client.get_blob_client(container=container, blob=current_file)
    data = blob_client.download_blob().readall()
    print(f"✅ Downloaded {len(data)} bytes")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Check Blob Properties
```python
from azure.storage.blob import BlobServiceClient
import os

conn_str = os.environ.get('BLOB_CONNECTION_STRING')
container = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')

client = BlobServiceClient.from_connection_string(conn_str)
container_client = client.get_container_client(container)

for blob in container_client.list_blobs():
    print(f"Name: {blob.name}")
    print(f"Size: {blob.size} bytes")
    print(f"Last Modified: {blob.last_modified}")
    print()
```

---

## Prevention

### Best Practices
1. **Always verify blob files exist** before testing
2. **Keep connection string updated** when account keys are rotated
3. **Monitor blob storage** for quota/access issues
4. **Use daily refresh** to create cached snapshots
5. **Test blob connection** regularly with `test_blob_connection.py`

### Monitoring
```bash
# Run test periodically
cd planning_intelligence
python test_blob_connection.py
```

### Backup Plan
1. Keep mock data available for testing
2. Have alternative data source ready
3. Document blob configuration
4. Keep account keys secure

---

## Support Checklist

Before contacting support, verify:
- [ ] Ran `test_blob_connection.py` and all tests pass
- [ ] Verified blob files exist in Azure Storage Explorer
- [ ] Checked `local.settings.json` has correct configuration
- [ ] Verified network connectivity to Azure
- [ ] Checked Azure Storage account status
- [ ] Tried daily refresh to create snapshot
- [ ] Checked Azure Functions logs for error messages
- [ ] Tried mock data as workaround

---

## Quick Reference

| Issue | Command | Expected Result |
|-------|---------|-----------------|
| Test blob connection | `python test_blob_connection.py` | All tests pass ✅ |
| Test endpoint | `curl -X POST http://localhost:7071/api/planning-dashboard-v2 -H "Content-Type: application/json" -d '{}'` | JSON response with data |
| Trigger refresh | `curl -X POST http://localhost:7071/api/daily-refresh -H "Content-Type: application/json" -d '{}'` | `{"status": "ok", ...}` |
| Check snapshot | `curl -X POST http://localhost:7071/api/debug-snapshot -H "Content-Type: application/json" -d '{}'` | Snapshot data or 404 |

---

## Next Steps

1. Run `test_blob_connection.py` to identify the specific issue
2. Follow the solution for that issue
3. Retry blob from UI
4. If still failing, check Azure Functions logs
5. Contact support with test results and error messages
