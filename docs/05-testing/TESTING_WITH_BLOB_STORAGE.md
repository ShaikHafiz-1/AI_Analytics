# Testing Copilot Real-Time Answers with Blob Storage

## Overview

This guide explains how to test the Copilot Real-Time Answers implementation with your actual blob storage data.

---

## Prerequisites

### 1. Local Configuration
Ensure `planning_intelligence/local.settings.json` is configured with your credentials:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=rgscpmcpdev8f3d;...",
    "BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=planningdatapi;...",
    "BLOB_CONTAINER_NAME": "planning-data",
    "BLOB_CURRENT_FILE": "current.csv",
    "BLOB_PREVIOUS_FILE": "previous.csv"
  },
  "Host": {
    "CORS": "http://localhost:3000",
    "CORSCredentials": false
  },
  "ConnectionStrings": {}
}
```

### 2. Python Dependencies
```bash
pip install azure-storage-blob
pip install azure-functions
```

### 3. Environment Setup
```bash
cd planning_intelligence
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Testing Steps

### Step 1: Test Blob Storage Connection

```bash
cd planning_intelligence
python test_blob_integration.py
```

**Expected Output**:
```
================================================================================
BLOB STORAGE CONNECTION TEST
================================================================================
✓ Connection string found
✓ Blob service client created
✓ Container name: planning-data
✓ Container client created
✓ Found X blobs in container
  - current.csv (XXXX bytes)
  - previous.csv (XXXX bytes)
✓ Looking for files:
  - Current: current.csv
  - Previous: previous.csv
✓ File status:
  - current.csv: ✓ EXISTS
  - previous.csv: ✓ EXISTS
✓ Downloaded current.csv (XXXX bytes)
  - Lines: XXX
  - First line (header): ...
✓ BLOB STORAGE CONNECTION TEST PASSED
================================================================================
```

### Step 2: Test Copilot with Blob Data

The same script tests Copilot functionality:

```bash
python test_blob_integration.py
```

**Expected Output**:
```
[2/3] Testing Copilot with blob data...
✓ Loading data from blob storage...
✓ Loaded XXX current rows, XXX previous rows
✓ Normalizing data...
✓ Normalized XXX current records, XXX previous records
✓ Filtering data...
✓ Filtered XXX current records, XXX previous records
✓ Comparing records...
✓ Comparison complete
✓ Building response...
✓ Response built
✓ Response Summary:
  - Planning Health: XX/100
  - Changed Records: XXX
  - Total Records: XXX
  - Status: At Risk
✓ COPILOT REAL-TIME ANSWERS - BLOB DATA TEST PASSED
```

### Step 3: Test Explain Endpoint

The script also tests the explain endpoint:

```bash
python test_blob_integration.py
```

**Expected Output**:
```
[3/3] Testing explain endpoint...
✓ Loading data from blob storage...
✓ Processing data...
✓ Building context...
✓ Testing 4 questions:

  Q: What is the planning health?
  Query Type: summary
  Answer Mode: summary
  Answer: Planning health is XX/100 (At Risk). XX% of records changed...

  Q: What changed most?
  Query Type: summary
  Answer Mode: summary
  Answer: XXX records changed (XX% of total). Primary driver: ...

  Q: Show top contributing records
  Query Type: traceability
  Answer Mode: investigate
  Answer: 📊 Top 5 contributing records (by forecast delta):...

  Q: What should the planner do next?
  Query Type: action
  Answer Mode: summary
  Answer: Recommended actions:...

✓ COPILOT EXPLAIN ENDPOINT - BLOB DATA TEST PASSED
```

---

## Running Individual Tests

### Test 1: Blob Connection Only
```bash
python -c "from test_blob_integration import test_blob_connection; test_blob_connection()"
```

### Test 2: Copilot with Blob Data Only
```bash
python -c "from test_blob_integration import test_copilot_with_blob_data; test_copilot_with_blob_data()"
```

### Test 3: Explain Endpoint Only
```bash
python -c "from test_blob_integration import test_copilot_explain_endpoint; test_copilot_explain_endpoint()"
```

---

## Running Unit Tests

### Run All Unit Tests
```bash
python -m pytest tests/test_copilot_realtime.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_copilot_realtime.py::TestScopeExtraction -v
```

### Run with Coverage
```bash
python -m pytest tests/test_copilot_realtime.py --cov=function_app --cov-report=html
```

---

## Running Performance Tests

### Run Performance Validation
```bash
python performance_validation.py
```

**Expected Output**:
```
================================================================================
COPILOT REAL-TIME ANSWERS - PERFORMANCE VALIDATION REPORT
================================================================================

✓ PASS | Scope Extraction
  Average: 1.234ms (Target: 5ms)
  Maximum: 2.456ms

✓ PASS | Answer Mode Determination
  Average: 0.567ms (Target: 5ms)
  Maximum: 1.234ms

✓ PASS | Scoped Metrics Computation
  Average: 25.678ms (Target: 100ms)
  Maximum: 45.123ms

✓ PASS | Answer Generation
  Average: 12.345ms (Target: 50ms)
  Maximum: 23.456ms

✓ PASS | Total Response Time
  Average: 89.012ms (Target: 500ms)
  Maximum: 156.789ms

================================================================================
SUMMARY: 5 passed, 0 failed
================================================================================
```

---

## Troubleshooting

### Issue: Connection String Not Found
**Solution**: Ensure `local.settings.json` is in the `planning_intelligence` directory and contains the correct connection string.

### Issue: Blob Not Found
**Solution**: Verify that:
1. The blob container exists in your storage account
2. The CSV files (`current.csv`, `previous.csv`) are in the container
3. The `BLOB_CONTAINER_NAME` matches the actual container name

### Issue: CSV Parse Error
**Solution**: Ensure the CSV files have:
1. Proper headers in the first row
2. Consistent column count across all rows
3. Valid data format

### Issue: Import Errors
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

---

## Test Results Interpretation

### ✓ All Tests Pass
- Blob storage is properly configured
- Copilot implementation is working correctly
- Performance targets are met
- Ready for deployment

### ❌ Some Tests Fail
- Check the error message for details
- Verify blob storage configuration
- Check CSV file format
- Review error logs

---

## Next Steps

### After Successful Testing

1. **Verify Data Quality**
   - Check that CSV files have expected data
   - Verify record counts match expectations
   - Validate data format

2. **Test with Real Questions**
   - Use the explain endpoint with real questions
   - Verify answers are specific and relevant
   - Check performance metrics

3. **Deploy to Staging**
   - Deploy to Azure Functions staging slot
   - Run full test suite in staging
   - Verify performance in staging environment

4. **Deploy to Production**
   - Deploy to production slot
   - Monitor performance metrics
   - Collect user feedback

---

## Performance Benchmarks

### Expected Performance (with 1000 records)

| Operation | Target | Typical | Status |
|-----------|--------|---------|--------|
| Scope Extraction | < 5ms | 1-2ms | ✓ |
| Answer Mode Determination | < 5ms | 0.5-1ms | ✓ |
| Scoped Metrics Computation | < 100ms | 10-50ms | ✓ |
| Answer Generation | < 50ms | 5-20ms | ✓ |
| Total Response Time | < 500ms | 50-150ms | ✓ |

---

## Security Notes

⚠️ **IMPORTANT**:
- `local.settings.json` contains sensitive credentials
- **NEVER commit this file to Git**
- **NEVER share this file with others**
- **Rotate credentials after testing**
- Use Azure Key Vault for production

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error logs in detail
3. Verify blob storage configuration
4. Check CSV file format and data

---

**Last Updated**: April 5, 2026
**Status**: Ready for Testing
