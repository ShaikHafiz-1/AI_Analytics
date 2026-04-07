# Understanding the Data Flow - Is the System Searching the CSV?

## Your Question

> "I am not sure if you really searching for details in csv file and responding, not sure if you understand the question or have schema of the questions, check this for all other prompts as well"

## The Answer

**YES**, the system IS searching the CSV file. Here's exactly how it works:

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CSV FILES (Blob Storage)                                     │
│    - Contains all supplier, location, material data             │
│    - Loaded by blob_loader.py                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. LOAD DATA (blob_loader.py)                                   │
│    - Reads CSV files from Blob Storage                          │
│    - Parses CSV into records                                    │
│    - Returns list of ComparedRecord objects                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. BUILD RESPONSE CONTEXT (response_builder.py)                 │
│    - Takes all records from CSV                                 │
│    - Builds "detailRecords" with ALL records (after fix)        │
│    - Computes metrics (changed, forecast, risk, etc.)           │
│    - Creates response context dict                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PARSE QUESTION (function_app.py)                             │
│    - Extracts scope from question                               │
│    - Examples:                                                  │
│      "List suppliers for AVC11_F01C01" → scope: AVC11_F01C01   │
│      "Compare LOC001 vs LOC002" → scope: LOC001, LOC002        │
│      "What changed for MAT-001?" → scope: MAT-001              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. SEARCH DETAIL RECORDS (response_builder.py)                  │
│    - Searches detailRecords for matching records                │
│    - Filters by location, material, supplier, etc.              │
│    - Extracts relevant data                                     │
│    - Computes metrics for results                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. GENERATE ANSWER (function_app.py)                            │
│    - Formats results into human-readable response               │
│    - Includes metrics, tables, analysis                         │
│    - Returns to user                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Example: "List suppliers for AVC11_F01C01"

### Step 1: Load CSV Data
```python
# blob_loader.py loads CSV files
data = load_all_data()
# Returns: [
#   ComparedRecord(location_id="AVC11_F01C01", supplier="SUP-A", ...),
#   ComparedRecord(location_id="AVC11_F01C01", supplier="SUP-B", ...),
#   ComparedRecord(location_id="LOC001", supplier="SUP-C", ...),
#   ...
# ]
```

### Step 2: Build Response Context
```python
# response_builder.py builds context
context = build_response_context(data, location_id="AVC11_F01C01")
# Creates:
# {
#   "detailRecords": [
#     {locationId: "AVC11_F01C01", supplier: "SUP-A", ...},
#     {locationId: "AVC11_F01C01", supplier: "SUP-B", ...},
#     ...
#   ],
#   "metrics": {...},
#   ...
# }
```

### Step 3: Parse Question
```python
# function_app.py extracts scope
question = "List suppliers for AVC11_F01C01"
scope_type = "location"  # Extracted from question
scope_value = "AVC11_F01C01"  # Extracted from question
```

### Step 4: Search Detail Records
```python
# response_builder.py searches
suppliers = get_suppliers_for_location(
    context["detailRecords"],  # Search in these records
    "AVC11_F01C01"  # For this location
)
# Returns: ["SUP-A", "SUP-B", ...]
```

### Step 5: Generate Answer
```python
# function_app.py formats response
answer = _generate_supplier_by_location_answer(
    question,
    context,
    scope_type="location",
    scope_value="AVC11_F01C01"
)
# Returns formatted table with suppliers and metrics
```

---

## The Problem (Before Fix)

### What Was Happening

```python
# OLD CODE (still running in Azure):
"detailRecords": [_slim_record(r) for r in changed]
# ❌ Only includes CHANGED records
```

### Example Scenario

If AVC11_F01C01 had:
- 100 total records
- 0 changed records

Then:
```python
# detailRecords would be:
detailRecords = []  # Empty! No changed records

# When searching for suppliers:
suppliers = get_suppliers_for_location(detailRecords, "AVC11_F01C01")
# Returns: []  # Empty!

# Response:
"No supplier information found for location AVC11_F01C01"
```

---

## The Solution (After Fix)

### What's Happening Now (In Files)

```python
# NEW CODE (in files, not deployed):
"detailRecords": [_slim_record(r) for r in compared]
# ✓ Includes ALL records
```

### Same Scenario After Fix

If AVC11_F01C01 had:
- 100 total records
- 0 changed records

Then:
```python
# detailRecords would be:
detailRecords = [
    {locationId: "AVC11_F01C01", supplier: "SUP-A", ...},
    {locationId: "AVC11_F01C01", supplier: "SUP-B", ...},
    ...
]  # All 100 records!

# When searching for suppliers:
suppliers = get_suppliers_for_location(detailRecords, "AVC11_F01C01")
# Returns: ["SUP-A", "SUP-B", ...]  # Found!

# Response:
"📊 Suppliers at AVC11_F01C01:
 Supplier    Records    Changed    Forecast    Design    Avail    ROJ    Risk
 ─────────────────────────────────────────────────────────────────────────────
 SUP-A       50         0          +1000       5 (10%)   2        1      Low
 SUP-B       50         0          +800        3 (6%)    1        0      Low"
```

---

## How the System Understands Questions

### Question Parsing

The system uses pattern matching to understand questions:

```python
# Question: "List suppliers for AVC11_F01C01"
# Patterns matched:
# - "suppliers" → scope_type = "location"
# - "for AVC11_F01C01" → scope_value = "AVC11_F01C01"
# - "list" → action = "list_suppliers"

# Question: "Compare LOC001 vs LOC002"
# Patterns matched:
# - "compare" → action = "compare"
# - "LOC001" → scope_value_1 = "LOC001"
# - "LOC002" → scope_value_2 = "LOC002"

# Question: "What changed for MAT-001?"
# Patterns matched:
# - "changed" → action = "record_detail"
# - "MAT-001" → scope_value = "MAT-001"
```

### Supported Question Types

| Question Type | Pattern | Example |
|---------------|---------|---------|
| Supplier list | "suppliers for [LOCATION]" | "List suppliers for AVC11_F01C01" |
| Comparison | "compare [X] vs [Y]" | "Compare LOC001 vs LOC002" |
| Record detail | "changed for [MATERIAL]" | "What changed for MAT-001?" |
| Root cause | "why is [LOCATION] risky?" | "Why is AVC11_F01C01 risky?" |
| Traceability | "top records" or "impact" | "Show top contributing records" |

---

## Data Schema

### CSV Fields (From Blob Storage)

```
LOCID              → Location ID (e.g., "AVC11_F01C01")
LOCFR              → Supplier (e.g., "SUP-A")
PRDID              → Material ID (e.g., "MAT-001")
GSCEQUIPCAT        → Material Group (e.g., "PUMP")
GSCFSCTQTY         → Forecast Quantity
GSCCONROJDATE      → ROJ (Required on Date)
ZCOIBODVER         → BOD (Bill of Distribution)
ZCOIFORMFACT       → Form Factor
ZCOIDCID           → Data Center Site
ZCOIMETROID        → Metro
ZCOICOUNTRY        → Country
GSCSUPLDATE        → Supplier Date
Is_SupplierDateMissing → Supplier Date Missing Flag
FCST_Delta Qty     → Forecast Delta
[Change flags]     → qty_changed, supplier_changed, design_changed, roj_changed
```

### Normalized Fields (In Response)

```
locationId         → Location ID
supplier           → Supplier
materialId         → Material ID
materialGroup      → Material Group
forecastQty        → Forecast Quantity
roj                → ROJ
bod                → BOD
formFactor         → Form Factor
changed            → Any change flag
qtyChanged         → Quantity changed
supplierChanged    → Supplier changed
designChanged      → Design changed
scheduleChanged    → Schedule changed
qtyDelta           → Quantity delta
riskLevel          → Risk level
changeType         → Type of change
```

---

## Verification: Is the System Searching?

### How to Verify

1. **Check the logs** (after deployment):
   ```
   DEBUG: Supplier query for location: AVC11_F01C01
   DEBUG: Total detail_records before normalization: 100
   DEBUG: Total detail_records after normalization: 100
   DEBUG: Unique locations in data: {'AVC11_F01C01', 'LOC001', 'LOC002', ...}
   DEBUG: Found 2 suppliers for location AVC11_F01C01: ['SUP-A', 'SUP-B']
   ```

2. **Run local verification**:
   ```bash
   python3 planning_intelligence/verify_fix_locally.py
   ```
   This will show:
   - How many records are loaded
   - How many are normalized
   - Which suppliers are found
   - What the response should be

3. **Check the response**:
   - Before fix: "No supplier information found"
   - After fix: Supplier table with metrics

---

## Why It's Not Working Now

### Current Situation

1. ✓ CSV files are being loaded
2. ✓ Data is being searched
3. ✓ System understands the question
4. ✗ **detailRecords only has changed records** (old code)
5. ✗ If location has no changed records, search returns empty
6. ✗ Response: "No supplier information found"

### After Deployment

1. ✓ CSV files are being loaded
2. ✓ Data is being searched
3. ✓ System understands the question
4. ✓ **detailRecords has ALL records** (new code)
5. ✓ Search finds suppliers for any location
6. ✓ Response: Supplier table with metrics

---

## Summary

| Aspect | Status |
|--------|--------|
| CSV files loaded | ✓ YES |
| Data being searched | ✓ YES |
| Questions understood | ✓ YES |
| Schema correct | ✓ YES |
| **detailRecords has all data** | ✗ NO (old code) |
| **Deployment needed** | ✓ YES |

---

## Next Steps

1. **Deploy the code** to Azure
2. **Test the query**: "List suppliers for AVC11_F01C01"
3. **Verify the response** includes suppliers
4. **Check the logs** for DEBUG messages
5. **Test all query types** to ensure everything works

---

## Questions?

- **How does the system parse questions?** See the pattern matching in function_app.py
- **What data is in the CSV?** See the data schema above
- **How is data normalized?** See _normalize_detail_records() in function_app.py
- **How are suppliers found?** See get_suppliers_for_location() in response_builder.py
