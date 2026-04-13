# Blob Retry Fix Guide

## Issue
When clicking "Retry Blob" from the UI, the blob data loading fails.

## Root Cause
The blob files (`current.csv` and `previous.csv`) likely don't exist in the Azure Blob Storage container `planning-data`, or there's an authentication issue.

## Configuration Verified ✅
Your `local.settings.json` has:
- ✅ BLOB_CONNECTION_STRING: Valid format
- ✅ BLOB_CONTAINER_NAME: `planning-data`
- ✅ BLOB_CURRENT_FILE: `current.csv`
- ✅ BLOB_PREVIOUS_FILE: `previous.csv`

## Solution: Upload CSV Files to Blob Storage

### Step 1: Prepare CSV Files
You need two CSV files with the following structure:

**current.csv** (Current data):
```csv
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT
LOC001,MAT001,ELECTRONICS,SUPPLIER1,1000,2026-04-15,BOD1,FF1
LOC001,MAT002,ELECTRONICS,SUPPLIER2,2000,2026-04-20,BOD2,FF2
LOC002,MAT003,MECHANICAL,SUPPLIER1,1500,2026-04-25,BOD3,FF3
```

**previous.csv** (Previous data for comparison):
```csv
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT
LOC001,MAT001,ELECTRONICS,SUPPLIER1,900,2026-04-10,BOD1,FF1
LOC001,MAT002,ELECTRONICS,SUPPLIER1,2000,2026-04-15,BOD2,FF2
LOC002,MAT003,MECHANICAL,SUPPLIER1,1500,2026-04-20,BOD3,FF3
```

### Step 2: Upload to Azure Blob Storage

#### Option A: Using Azure Portal
1. Go to Azure Portal → Storage Accounts → planningdatapi
2. Click "Containers" → "planning-data"
3. Click "Upload"
4. Select `current.csv` and `previous.csv`
5. Click "Upload"

#### Option B: Using Azure Storage Explorer
1. Open Azure Storage Explorer
2. Navigate to: Storage Accounts → planningdatapi → Blob Containers → planning-data
3. Right-click → "Upload Files"
4. Select `current.csv` and `previous.csv`
5. Click "Upload"

#### Option C: Using Azure CLI
```bash
# Login to Azure
az login

# Upload current.csv
az storage blob upload \
  --account-name planningdatapi \
  --container-name planning-data \
  --name current.csv \
  --file current.csv

# Upload previous.csv
az storage blob upload \
  --account-name planningdatapi \
  --container-name planning-data \
  --name previous.csv \
  --file previous.csv
```

### Step 3: Verify Files Uploaded
```bash
# List blobs in container
az storage blob list \
  --account-name planningdatapi \
  --container-name planning-data \
  --output table
```

Expected output:
```
Name           Blob Type    Length
-----------    ---------    ------
current.csv    BlockBlob    1234
previous.csv   BlockBlob    1234
```

### Step 4: Test Blob Retry from UI
1. Go to http://localhost:3000
2. Click "Retry Blob" button
3. Should now load data successfully ✅

## Alternative: Use Mock Data (Temporary)
If you don't have CSV files ready, use mock data for testing:
1. Click "Retry Blob" button
2. When it fails, click "Load Mock Data" button
3. UI will load sample data for testing

## Troubleshooting

### Error: "Blob not found"
**Solution**: Upload CSV files to blob container (see Step 2 above)

### Error: "Authentication failed"
**Solution**: Verify connection string in `local.settings.json`:
```json
{
  "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;AccountKey=...;EndpointSuffix=core.windows.net"
}
```

### Error: "Empty file content"
**Solution**: Ensure CSV files have data rows (not just headers)

### Error: "Missing required columns"
**Solution**: Ensure CSV has these columns:
- LOCID (Location ID)
- PRDID (Product ID)
- GSCEQUIPCAT (Equipment Category)

## Sample CSV Files

### current.csv
```csv
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT,ZCOIDCID,ZCOIMETROID,ZCOICOUNTRY,GSCSUPLDATE
LOC001,MAT001,ELECTRONICS,SUPPLIER1,1000,2026-04-15,BOD1,FF1,DC1,METRO1,US,2026-04-01
LOC001,MAT002,ELECTRONICS,SUPPLIER2,2000,2026-04-20,BOD2,FF2,DC1,METRO1,US,2026-04-02
LOC001,MAT003,ELECTRONICS,SUPPLIER1,1500,2026-04-25,BOD1,FF1,DC1,METRO1,US,2026-04-03
LOC002,MAT004,MECHANICAL,SUPPLIER3,2500,2026-05-01,BOD3,FF3,DC2,METRO2,EU,2026-04-04
LOC002,MAT005,MECHANICAL,SUPPLIER1,3000,2026-05-05,BOD4,FF4,DC2,METRO2,EU,2026-04-05
LOC003,MAT006,OPTICAL,SUPPLIER4,1200,2026-05-10,BOD5,FF5,DC3,METRO3,APAC,2026-04-06
```

### previous.csv
```csv
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT,ZCOIDCID,ZCOIMETROID,ZCOICOUNTRY,GSCSUPLDATE
LOC001,MAT001,ELECTRONICS,SUPPLIER1,900,2026-04-10,BOD1,FF1,DC1,METRO1,US,2026-03-25
LOC001,MAT002,ELECTRONICS,SUPPLIER1,2000,2026-04-15,BOD2,FF2,DC1,METRO1,US,2026-03-26
LOC001,MAT003,ELECTRONICS,SUPPLIER1,1500,2026-04-20,BOD1,FF1,DC1,METRO1,US,2026-03-27
LOC002,MAT004,MECHANICAL,SUPPLIER3,2500,2026-04-25,BOD3,FF3,DC2,METRO2,EU,2026-03-28
LOC002,MAT005,MECHANICAL,SUPPLIER1,2800,2026-04-30,BOD4,FF4,DC2,METRO2,EU,2026-03-29
LOC003,MAT006,OPTICAL,SUPPLIER4,1200,2026-05-05,BOD5,FF5,DC3,METRO3,APAC,2026-03-30
```

## Verification Checklist

- [ ] CSV files created with required columns
- [ ] Files uploaded to `planning-data` container
- [ ] Files are not empty (have data rows)
- [ ] Column names are correct (LOCID, PRDID, GSCEQUIPCAT)
- [ ] Connection string in `local.settings.json` is correct
- [ ] Azure Functions restarted after uploading files
- [ ] Retry Blob button works from UI

## Next Steps

1. Create or obtain CSV files with planning data
2. Upload to Azure Blob Storage (planning-data container)
3. Restart Azure Functions: `func start`
4. Click "Retry Blob" from UI
5. Data should load successfully ✅

## Support

If blob retry still fails after uploading files:
1. Check Azure Storage Explorer to verify files exist
2. Verify file sizes are not zero
3. Check Azure Functions logs for detailed error messages
4. Verify connection string is correct
5. Try daily refresh: `curl -X POST http://localhost:7071/api/daily-refresh -H "Content-Type: application/json" -d '{}'`
