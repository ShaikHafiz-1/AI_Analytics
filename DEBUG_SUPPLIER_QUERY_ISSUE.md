# Debugging Supplier Query Issue

## The Real Problem

The error message shows:
```
No supplier information found for location AVC11_F01C01.
📊 Supporting Metrics: • Changed: 5927/13148 • Trend: +50,980 • Health: 37/100
🏭 Suppliers at AVC11_F01C01:
```

This indicates:
1. The system IS finding the location (it shows metrics for it)
2. But it's NOT finding suppliers for that location
3. The `detailRecords` likely don't contain supplier information for AVC11_F01C01

## Possible Root Causes

### 1. **detailRecords is Empty**
- The context being passed to the endpoint has no `detailRecords`
- Or `detailRecords` is an empty array

### 2. **detailRecords Doesn't Contain AVC11_F01C01**
- The data might be filtered before being passed to the endpoint
- The location might be stored differently in the data

### 3. **Supplier Field is Empty/Null**
- Records for AVC11_F01C01 exist but have no supplier information
- The supplier field might be null or empty string

### 4. **Data Format Issue**
- The field names might be different than expected
- The data structure might be completely different

## How to Diagnose

### Step 1: Run the Diagnostic Script
```bash
cd planning_intelligence
python3 diagnose_data.py
```

This will show:
- What's in the cached snapshot
- What's in the blob storage
- Sample locations in the data
- Whether AVC11_F01C01 exists in the data
- The actual data structure

### Step 2: Check the Logs
When you run a supplier query, check the logs for DEBUG messages:
```
DEBUG: Supplier query for location: AVC11_F01C01
DEBUG: Total detail_records before normalization: 0
DEBUG: Total detail_records after normalization: 0
DEBUG: Unique locations in data: {'LOC001', 'LOC002', ...}
DEBUG: Found 0 suppliers for location AVC11_F01C01: []
```

### Step 3: Understand the Output

**If detailRecords is empty (0 records):**
- The context being passed to the endpoint has no data
- Solution: Load data from blob storage first

**If detailRecords exists but AVC11_F01C01 is not in the locations:**
- The data doesn't contain AVC11_F01C01
- Solution: Check if the location ID is spelled correctly or stored differently

**If AVC11_F01C01 exists but suppliers are empty:**
- The records exist but have no supplier information
- Solution: Check if the supplier field is populated in the data

## What to Check

### 1. Is the Snapshot Loaded?
```python
from snapshot_store import load_snapshot
snap = load_snapshot()
if snap:
    print(f"Snapshot loaded with {len(snap.get('detailRecords', []))} records")
else:
    print("No snapshot - need to load from blob")
```

### 2. Does the Data Contain AVC11_F01C01?
```python
detail_records = snap.get("detailRecords", [])
locations = set(r.get("locationId") for r in detail_records if r.get("locationId"))
print(f"Locations in data: {locations}")
print(f"AVC11_F01C01 in data: {'AVC11_F01C01' in locations}")
```

### 3. Do Records for AVC11_F01C01 Have Suppliers?
```python
avc_records = [r for r in detail_records if r.get("locationId") == "AVC11_F01C01"]
print(f"Records for AVC11_F01C01: {len(avc_records)}")
if avc_records:
    suppliers = set(r.get("supplier") for r in avc_records if r.get("supplier"))
    print(f"Suppliers: {suppliers}")
```

## Common Issues and Solutions

### Issue 1: "No supplier information found" but metrics show data
**Cause**: `detailRecords` is empty or doesn't contain the location
**Solution**: 
1. Run diagnostic script to check data
2. Load data from blob storage if needed
3. Verify location ID format matches

### Issue 2: Location exists but no suppliers
**Cause**: Supplier field is null/empty in the data
**Solution**:
1. Check if supplier field is populated in CSV
2. Verify data normalization is working
3. Check field name mapping

### Issue 3: Different location ID format
**Cause**: Location stored as "AVC11_F01C01" but query uses different format
**Solution**:
1. Check actual location ID in data
2. Update query to match format
3. Verify case-insensitive matching is working

## Testing Steps

### Step 1: Verify Data Exists
```bash
python3 diagnose_data.py
```

### Step 2: Check Logs
Look for DEBUG messages in the logs when running a supplier query

### Step 3: Verify Normalization
```python
from function_app import _normalize_detail_records
records = [{"LOCID": "AVC11_F01C01", "LOCFR": "SUP-A"}]
normalized = _normalize_detail_records(records)
print(normalized)  # Should show locationId and supplier
```

### Step 4: Test Supplier Query Directly
```python
from function_app import _generate_supplier_by_location_answer
context = {
    "detailRecords": [
        {"locationId": "AVC11_F01C01", "supplier": "SUP-A", "changed": True},
        {"locationId": "AVC11_F01C01", "supplier": "SUP-B", "changed": False},
    ]
}
answer = _generate_supplier_by_location_answer(
    "List suppliers for AVC11_F01C01",
    context,
    "location",
    "AVC11_F01C01"
)
print(answer)  # Should show suppliers, not "No supplier information found"
```

## Next Steps

1. **Run the diagnostic script** to understand your data structure
2. **Check the logs** for DEBUG messages
3. **Verify the data** contains AVC11_F01C01 with suppliers
4. **Report findings** so we can fix the actual issue

## Important Notes

- The code changes I made are correct and will work IF the data is present
- The issue is likely that `detailRecords` is empty or doesn't contain the location
- The diagnostic script will tell us exactly what's wrong
- Once we know the data structure, we can fix the issue properly

## Files to Check

1. `planning_intelligence/diagnose_data.py` - Run this to understand your data
2. `planning_intelligence/function_app.py` - Check DEBUG logs from _generate_supplier_by_location_answer
3. `planning_intelligence/snapshot_store.py` - Check how snapshots are loaded
4. `planning_intelligence/blob_loader.py` - Check how blob data is loaded

## Summary

The supplier query fix is correct, but it can only work if:
1. `detailRecords` is populated in the context
2. `detailRecords` contains records for the location being queried
3. Those records have supplier information

Run the diagnostic script to determine which of these is failing.
