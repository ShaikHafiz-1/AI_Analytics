# Supplier Query Issue Analysis

## Problem Statement

When querying for suppliers at a specific location (e.g., "List suppliers at location AVC11_F01C01"), the system returns:
```
No supplier information found for location LOCATION AVC11_F01C01.
```

However, the system should be searching the CSV data and returning actual supplier information with metrics.

## Root Cause Analysis

### Issue 1: Data Structure Mismatch

**Problem**: The code expects `detailRecords` to be a list of `ComparedRecord` objects with attributes like:
- `location_id` (accessed via `getattr(r, 'location_id', '')`)
- `supplier` (accessed via `getattr(r, 'supplier', '')`)

**Reality**: The data being passed is likely:
- Raw CSV dictionaries with keys like `"LOCID"`, `"LOCFR"` (not `location_id`, `supplier`)
- OR the data structure doesn't match what the code expects

**Evidence**:
```python
# In response_builder.py, line 469
location_records = [r for r in records if getattr(r, 'location_id', '').upper() == location.upper()]

# In response_builder.py, line 472-473
for r in location_records:
    supplier = getattr(r, 'supplier', None)
```

The code uses `getattr()` with defaults, which means if the attribute doesn't exist, it returns empty string or None, resulting in no matches.

### Issue 2: Location ID Format Mismatch

**Problem**: The location ID being queried is `AVC11_F01C01`, but the code might be:
1. Not normalizing the location ID format
2. Comparing against different location ID formats in the data
3. The data might use different location ID naming conventions

**Evidence**: The error message shows `LOCATION AVC11_F01C01` which suggests the location ID wasn't properly extracted or normalized.

### Issue 3: Missing Data Normalization

**Problem**: The supplier query handler doesn't normalize the incoming data before searching.

**Current Flow**:
1. Question comes in: "List suppliers at location AVC11_F01C01"
2. Scope extraction: `scope_value = "AVC11_F01C01"`
3. Direct search: `get_suppliers_for_location(detail_records, "AVC11_F01C01")`
4. **No normalization of detail_records structure**

**Expected Flow**:
1. Question comes in
2. Scope extraction
3. **Normalize detail_records to ComparedRecord objects**
4. Search with normalized data

### Issue 4: Schema Mismatch Between CSV and Code

**CSV Field Names** (from models.py):
- `LOCID` → should map to `location_id`
- `LOCFR` / `LOCFRDESCR` → should map to `supplier`
- `GSCFSCTQTY` → forecast quantity
- `GSCCONROJDATE` → ROJ date

**Code Expects**:
- `location_id` (attribute)
- `supplier` (attribute)
- `qty_delta` (attribute)
- `design_changed` (attribute)

**Problem**: If `detail_records` contains raw dictionaries with CSV field names, the `getattr()` calls will fail silently and return defaults.

## Testing Evidence

From `test_blob_integration.py`, the test data shows:
```python
current = [
    {
        "LOCID": "LOC001",           # CSV field name
        "GSCEQUIPCAT": "Electronics",
        "PRDID": "MAT-001",
        "LOCFR": "SUP-A",            # CSV field name for supplier
        ...
    }
]
```

But the code expects:
```python
location_records = [r for r in records if getattr(r, 'location_id', '').upper() == location.upper()]
```

This will fail because dictionaries don't have `location_id` attribute.

## Impact

### What's Broken
1. **Supplier queries return "No supplier information found"** even when data exists
2. **All supplier-by-location queries fail** (list suppliers, supplier behavior analysis, etc.)
3. **Supplier metrics are empty** in responses
4. **The system can't answer questions like**:
   - "List suppliers for LOC001"
   - "Which supplier at LOC001 has design changes?"
   - "Show supplier impact at AVC11_F01C01"

### What Works
- Comparison queries (location vs location)
- Root cause queries (why is LOC001 risky?)
- Traceability queries (top contributing records)
- Record detail queries (what changed for MAT-001?)

These work because they don't rely on the `supplier` field extraction.

## Solution Approach

### Step 1: Normalize Data Structure
Ensure `detail_records` are converted to `ComparedRecord` objects before supplier queries:

```python
def _normalize_detail_records(records):
    """Convert raw CSV dicts to ComparedRecord objects."""
    normalized = []
    for r in records:
        if isinstance(r, dict):
            # Map CSV field names to ComparedRecord attributes
            normalized.append(ComparedRecord(
                location_id=r.get("LOCID", ""),
                material_group=r.get("GSCEQUIPCAT", ""),
                material_id=r.get("PRDID", ""),
                supplier_current=r.get("LOCFR", ""),
                # ... other fields
            ))
        else:
            normalized.append(r)
    return normalized
```

### Step 2: Update Supplier Query Handler
```python
def _generate_supplier_by_location_answer(question: str, ctx: dict, scope_type: str, scope_value: str) -> str:
    detail_records = ctx.get("detailRecords", [])
    
    # NORMALIZE DATA FIRST
    detail_records = _normalize_detail_records(detail_records)
    
    # Then proceed with supplier search
    suppliers = get_suppliers_for_location(detail_records, scope_value)
    ...
```

### Step 3: Add Schema Validation
Add validation to ensure data structure matches expectations:

```python
def _validate_record_schema(record):
    """Validate record has required fields."""
    required = ['location_id', 'material_group', 'material_id', 'supplier_current']
    return all(hasattr(record, field) for field in required)
```

### Step 4: Add Logging
Add debug logging to understand what's happening:

```python
def get_suppliers_for_location(records, location):
    location_records = [r for r in records if getattr(r, 'location_id', '').upper() == location.upper()]
    
    # DEBUG
    print(f"Searching for location: {location}")
    print(f"Total records: {len(records)}")
    print(f"Matching records: {len(location_records)}")
    if records:
        print(f"First record type: {type(records[0])}")
        print(f"First record: {records[0]}")
    
    suppliers = set()
    for r in location_records:
        supplier = getattr(r, 'supplier_current', None) or getattr(r, 'supplier', None)
        if supplier:
            suppliers.add(supplier)
    return sorted(list(suppliers))
```

## Questions to Verify

1. **What is the actual structure of `detailRecords` being passed to the endpoint?**
   - Is it raw CSV dictionaries?
   - Is it ComparedRecord objects?
   - Is it something else?

2. **What are the actual field names in the data?**
   - Is it `LOCID` or `location_id`?
   - Is it `LOCFR` or `supplier`?

3. **Is data normalization happening before the supplier query?**
   - Where does `detailRecords` come from?
   - Is it normalized in `build_response()` or elsewhere?

4. **Are there any data loading/transformation steps we're missing?**
   - Is there a `normalize_rows()` call that should happen?
   - Is there a `compare_records()` call that should happen?

## Recommended Next Steps

1. **Add logging to understand actual data structure**
2. **Check where `detailRecords` is populated in the context**
3. **Verify data normalization is happening**
4. **Add schema validation before supplier queries**
5. **Update supplier query handler to normalize data if needed**
6. **Add unit tests with actual data structure**

## Files to Check

- `planning_intelligence/function_app.py` - Where context is built
- `planning_intelligence/response_builder.py` - Where supplier queries are handled
- `planning_intelligence/normalizer.py` - Data normalization logic
- `planning_intelligence/comparator.py` - Record comparison logic
- Test files to understand expected data structure

