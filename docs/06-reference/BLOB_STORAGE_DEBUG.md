# Blob Storage Debugging Guide

If you see "Blob data unavailable" error, follow this step-by-step debugging guide.

## Quick Diagnosis

Run this command to test Blob Storage connection:

```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'
```

**Expected response:**
```json
{
  "status": "ok",
  "lastRefreshedAt": "2026-04-05T10:30:00Z",
  "totalRecords": 1234,
  "changedRecordCount": 45,
  "planningHealth": 87
}
```

**If you get an error**, follow the debugging steps below.

---

## Step 1: Check Environment Variables

### 1.1 Verify local.settings.json

```bash
cd planning_intelligence
cat local.settings.json
```

**Should contain:**
```json
{
  "Values": {
    "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv"
  }
}
```

### 1.2 Verify .env file

```bash
cat .env
```

**Should contain:**
```env
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
```

### 1.3 Check if variables are loaded

Add this test script:

```bash
cat > test_env.py << 'EOF'
import os
import json

print("=== Environment Variables ===")
print(f"BLOB_CONNECTION_STRING: {os.environ.get('BLOB_CONNECTION_STRING', 'NOT SET')[:50]}...")
print(f"BLOB_CONTAINER_NAME: {os.environ.get('BLOB_CONTAINER_NAME', 'NOT SET')}")
print(f"BLOB_CURRENT_FILE: {os.environ.get('BLOB_CURRENT_FILE', 'NOT SET')}")
print(f"BLOB_PREVIOUS_FILE: {os.environ.get('BLOB_PREVIOUS_FILE', 'NOT SET')}")

# Try to load local.settings.json
try:
    with open('local.settings.json', 'r') as f:
        settings = json.load(f)
        print("\n=== local.settings.json ===")
        print(json.dumps(settings, indent=2))
except Exception as e:
    print(f"Error reading local.settings.json: {e}")
EOF

python test_env.py
```

---

## Step 2: Check Blob Storage Connection

### 2.1 Verify Connection String Format

Your connection string should look like:
```
DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
```

**Common issues:**
- ❌ Missing `DefaultEndpointsProtocol=https;`
- ❌ Missing `AccountName=`
- ❌ Missing `AccountKey=`
- ❌ Missing `EndpointSuffix=core.windows.net`
- ❌ Extra spaces or line breaks

### 2.2 Test Connection with Python

```bash
cat > test_blob_connection.py << 'EOF'
import os
from azure.storage.blob import BlobServiceClient

connection_string = os.environ.get('BLOB_CONNECTION_STRING')
container_name = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')

if not connection_string:
    print("❌ ERROR: BLOB_CONNECTION_STRING not set")
    exit(1)

print(f"Connection String: {connection_string[:50]}...")
print(f"Container: {container_name}")

try:
    # Create client
    client = BlobServiceClient.from_connection_string(connection_string)
    print("✅ Connected to Blob Storage")
    
    # List containers
    containers = client.list_containers()
    print("\n✅ Available containers:")
    for container in containers:
        print(f"  - {container.name}")
    
    # Check if our container exists
    container_client = client.get_container_client(container_name)
    if container_client.exists():
        print(f"\n✅ Container '{container_name}' exists")
        
        # List blobs
        blobs = container_client.list_blobs()
        print(f"\n✅ Blobs in '{container_name}':")
        for blob in blobs:
            print(f"  - {blob.name} ({blob.size} bytes)")
    else:
        print(f"\n❌ Container '{container_name}' does NOT exist")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"\nError type: {type(e).__name__}")
    
    # Provide specific guidance
    if "AuthenticationFailed" in str(e) or "403" in str(e):
        print("\n💡 Hint: Check your AccountKey in the connection string")
    elif "BlobNotFound" in str(e) or "404" in str(e):
        print("\n💡 Hint: Container or blob not found")
    elif "InvalidConnectionString" in str(e):
        print("\n💡 Hint: Connection string format is invalid")
EOF

python test_blob_connection.py
```

---

## Step 3: Check Blob Files

### 3.1 Verify Files Exist

```bash
cat > test_blob_files.py << 'EOF'
import os
from azure.storage.blob import BlobServiceClient

connection_string = os.environ.get('BLOB_CONNECTION_STRING')
container_name = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')
previous_file = os.environ.get('BLOB_PREVIOUS_FILE', 'previous.csv')

print(f"Looking for files in: {container_name}")
print(f"  - Current: {current_file}")
print(f"  - Previous: {previous_file}")

try:
    client = BlobServiceClient.from_connection_string(connection_string)
    container_client = client.get_container_client(container_name)
    
    # Check current file
    current_blob = container_client.get_blob_client(current_file)
    if current_blob.exists():
        props = current_blob.get_blob_properties()
        print(f"\n✅ {current_file} exists ({props.size} bytes)")
    else:
        print(f"\n❌ {current_file} NOT FOUND")
    
    # Check previous file
    previous_blob = container_client.get_blob_client(previous_file)
    if previous_blob.exists():
        props = previous_blob.get_blob_properties()
        print(f"✅ {previous_file} exists ({props.size} bytes)")
    else:
        print(f"❌ {previous_file} NOT FOUND")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
EOF

python test_blob_files.py
```

### 3.2 Download and Inspect Files

```bash
cat > test_blob_download.py << 'EOF'
import os
import io
import pandas as pd
from azure.storage.blob import BlobServiceClient

connection_string = os.environ.get('BLOB_CONNECTION_STRING')
container_name = os.environ.get('BLOB_CONTAINER_NAME', 'planning-data')
current_file = os.environ.get('BLOB_CURRENT_FILE', 'current.csv')

try:
    client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = client.get_blob_client(container=container_name, blob=current_file)
    
    # Download
    data = blob_client.download_blob().readall()
    print(f"✅ Downloaded {current_file} ({len(data)} bytes)")
    
    # Parse CSV
    df = pd.read_csv(io.BytesIO(data), dtype=str)
    print(f"\n✅ Parsed CSV: {len(df)} rows, {len(df.columns)} columns")
    
    # Show columns
    print(f"\nColumns: {list(df.columns)}")
    
    # Check required columns
    required = {"LOCID", "PRDID", "GSCEQUIPCAT"}
    columns_upper = {c.upper() for c in df.columns}
    missing = required - columns_upper
    
    if missing:
        print(f"\n❌ Missing required columns: {missing}")
    else:
        print(f"\n✅ All required columns present")
    
    # Show first row
    print(f"\nFirst row:")
    print(df.iloc[0].to_dict())
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
EOF

python test_blob_download.py
```

---

## Step 4: Check Backend Logs

### 4.1 Run Backend with Verbose Logging

```bash
# Stop current backend (Ctrl+C)

# Start with debug logging
func start --verbose
```

**Look for these messages:**
- `Downloaded blob planning-data/current.csv`
- `Loaded current: X rows, Y columns`
- `Daily refresh triggered`

### 4.2 Check for Errors

**Common error messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required environment variable: BLOB_CONNECTION_STRING` | Env var not set | Check local.settings.json |
| `Blob not found: planning-data/current.csv` | File doesn't exist | Upload file to Blob Storage |
| `Authentication failed for blob` | Invalid connection string | Check AccountKey |
| `Missing required columns: {'LOCID', 'PRDID'}` | CSV format wrong | Check CSV column names |
| `Empty file content` | File is empty | Upload valid CSV file |

---

## Step 5: Test Full Pipeline

### 5.1 Test Daily Refresh Endpoint

```bash
# Terminal 1: Start backend
cd planning_intelligence
func start

# Terminal 2: Test endpoint
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'
```

**Expected response:**
```json
{
  "status": "ok",
  "lastRefreshedAt": "2026-04-05T10:30:00Z",
  "totalRecords": 1234,
  "changedRecordCount": 45,
  "planningHealth": 87
}
```

### 5.2 Test Dashboard Endpoint

```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected response:**
```json
{
  "planningHealth": 87,
  "status": "Healthy",
  "changedRecordCount": 45,
  "totalRecords": 1234,
  ...
}
```

---

## Step 6: Check Frontend

### 6.1 Verify Frontend Can Reach Backend

```bash
# Terminal 3: Check frontend .env
cd frontend
cat .env
```

**Should contain:**
```env
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_USE_MOCK=false
```

### 6.2 Check Browser Console

1. Open browser: http://localhost:3000
2. Press F12 to open Developer Tools
3. Go to **Console** tab
4. Look for errors like:
   - `Failed to fetch` - Backend not running
   - `404 Not Found` - Wrong API URL
   - `CORS error` - CORS not configured

### 6.3 Check Network Tab

1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Refresh page
4. Look for requests to `/api/planning-dashboard-v2`
5. Check response status and body

---

## Common Issues & Solutions

### Issue 1: "Connection refused"

**Symptom:** `Error: connect ECONNREFUSED 127.0.0.1:7071`

**Causes:**
- Backend not running
- Wrong port
- Firewall blocking

**Solution:**
```bash
# Make sure backend is running
cd planning_intelligence
func start

# Check it's listening on port 7071
netstat -an | grep 7071  # Linux/Mac
netstat -ano | findstr 7071  # Windows
```

### Issue 2: "Authentication failed"

**Symptom:** `AuthenticationFailed: Server failed to authenticate the request`

**Causes:**
- Invalid AccountKey
- Connection string corrupted
- Expired credentials

**Solution:**
```bash
# Get fresh connection string from Azure Portal
# 1. Go to Storage Account
# 2. Click "Access keys"
# 3. Copy Connection string
# 4. Update local.settings.json
# 5. Restart backend
```

### Issue 3: "Blob not found"

**Symptom:** `BlobNotFound: The specified blob does not exist`

**Causes:**
- File not uploaded
- Wrong filename
- Wrong container name

**Solution:**
```bash
# Check what files exist
python test_blob_files.py

# Upload files to Azure Portal
# 1. Go to Storage Account
# 2. Click "Containers"
# 3. Click "planning-data"
# 4. Click "Upload"
# 5. Select current.csv and previous.csv
```

### Issue 4: "Missing required columns"

**Symptom:** `Missing required columns in current: {'LOCID', 'PRDID'}`

**Causes:**
- CSV has different column names
- Column names have spaces or special characters
- Wrong file format

**Solution:**
```bash
# Check CSV columns
python test_blob_download.py

# CSV must have these columns (case-insensitive):
# - LOCID (or LOC ID, Location ID)
# - PRDID (or PRD ID, Material ID)
# - GSCEQUIPCAT (or Equipment Category)
```

### Issue 5: "Empty file content"

**Symptom:** `Empty file content for current`

**Causes:**
- File is empty
- File is corrupted
- Wrong file uploaded

**Solution:**
```bash
# Check file size
python test_blob_files.py

# File should be > 0 bytes
# Re-upload file if corrupted
```

---

## Complete Debugging Checklist

- [ ] Check `local.settings.json` has connection string
- [ ] Check `.env` has connection string
- [ ] Run `test_env.py` - variables loaded?
- [ ] Run `test_blob_connection.py` - can connect?
- [ ] Run `test_blob_files.py` - files exist?
- [ ] Run `test_blob_download.py` - can download?
- [ ] Backend logs show no errors
- [ ] Test `/api/daily-refresh` endpoint
- [ ] Test `/api/planning-dashboard-v2` endpoint
- [ ] Frontend `.env` has correct API URL
- [ ] Browser console shows no errors
- [ ] Network tab shows successful requests

---

## Debug Scripts Summary

### Quick Test All

```bash
cat > debug_all.sh << 'EOF'
#!/bin/bash
echo "=== Testing Environment Variables ==="
python test_env.py

echo -e "\n=== Testing Blob Connection ==="
python test_blob_connection.py

echo -e "\n=== Testing Blob Files ==="
python test_blob_files.py

echo -e "\n=== Testing Blob Download ==="
python test_blob_download.py

echo -e "\n=== Testing API Endpoint ==="
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'
EOF

chmod +x debug_all.sh
./debug_all.sh
```

---

## Getting Help

If you're still stuck:

1. **Collect debug info:**
   ```bash
   python test_env.py > debug_env.txt
   python test_blob_connection.py > debug_connection.txt
   python test_blob_files.py > debug_files.txt
   ```

2. **Check backend logs:**
   ```bash
   func start 2>&1 | tee backend.log
   ```

3. **Check browser console:**
   - F12 → Console tab
   - Screenshot any errors

4. **Share with team:**
   - debug_env.txt
   - debug_connection.txt
   - debug_files.txt
   - backend.log
   - Browser console screenshot

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python test_env.py` | Check environment variables |
| `python test_blob_connection.py` | Test Blob Storage connection |
| `python test_blob_files.py` | Check if files exist |
| `python test_blob_download.py` | Download and inspect file |
| `func start --verbose` | Run backend with debug logging |
| `curl -X POST http://localhost:7071/api/daily-refresh` | Test API endpoint |

---

## Next Steps

Once Blob Storage is working:

1. ✅ Backend loads data from Blob Storage
2. ✅ Frontend displays dashboard
3. ✅ Copilot panel responds to questions
4. ✅ Ready for production deployment

Good luck! 🚀
