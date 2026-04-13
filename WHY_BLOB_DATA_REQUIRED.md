# Why the System Needs to Read Details from Blob Files

## Overview
The Planning Intelligence Copilot system requires reading detailed data from Azure Blob Storage files because the blob data contains the **raw planning records** that are essential for answering user questions accurately.

---

## What Data is in the Blob Files?

The blob storage contains two CSV/Excel files:
1. **current.csv** - Current planning data snapshot
2. **previous.csv** - Previous planning data snapshot (for comparison)

Each file contains planning records with these required columns:
- **LOCID** - Location ID (e.g., "CYS20_F01C01")
- **PRDID** - Product/Material ID
- **GSCEQUIPCAT** - Equipment Category/Material Group

Plus additional fields like:
- `changed` - Whether the record changed
- `changeType` - Type of change (design, supplier, material, schedule)
- `riskLevel` - Risk level (high, medium, low)
- `qtyDelta` - Quantity change
- `supplierChanged` - Supplier change flag
- `designChanged` - Design change flag

---

## Why This Data is Critical

### 1. **Answer Generation Requires Actual Data**
When a user asks a question, the system needs real data to generate accurate answers:

```
User: "What's the current planning health status?"
→ System needs: Total records, changed records, risk breakdown
→ Source: detail_records from blob

User: "Which suppliers are affected?"
→ System needs: List of unique suppliers in changed records
→ Source: detail_records from blob

User: "What's the impact on suppliers?"
→ System needs: Count of changes per supplier
→ Source: detail_records from blob
```

### 2. **Scoped Metrics Computation**
The system filters records by scope to answer location/supplier/material-specific questions:

```python
# From phase1_core_functions.py
if scope_type == "location":
    filtered = [r for r in detail_records if r.get("LOCID") == scope_value]
elif scope_type == "supplier":
    filtered = [r for r in detail_records if r.get("LOCFR") == scope_value]
elif scope_type == "material_group":
    filtered = [r for r in detail_records if r.get("GSCEQUIPCAT") == scope_value]
```

### 3. **Change Analysis**
The system compares current vs. previous data to identify:
- What changed
- How many records changed
- Which suppliers/materials/locations are affected
- Risk levels and drivers

### 4. **Context Building for Answers**
The detail_records are used to build comprehensive context:

```python
# From nlp_endpoint.py
changed_count = sum(1 for r in detail_records if r.get("changed", False))
total_count = len(detail_records)
change_rate = round(changed_count / max(total_count, 1) * 100, 1)

# Compute drivers
qty_changed = sum(1 for r in detail_records if r.get("qtyChanged", False))
supplier_changed = sum(1 for r in detail_records if r.get("supplierChanged", False))
design_changed = sum(1 for r in detail_records if r.get("designChanged", False))
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Azure Blob Storage                                          │
│ ├─ current.csv (1000+ planning records)                    │
│ └─ previous.csv (1000+ planning records)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ blob_loader.py             │
        │ load_current_previous_     │
        │ from_blob()                │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ detail_records (list[dict])│
        │ 1000+ planning records     │
        └────────────┬───────────────┘
                     │
        ┌────────────┴────────────────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────────┐              ┌──────────────────────┐
│ Answer Generation    │              │ Metrics Computation  │
│ - Health answers     │              │ - Scoped metrics     │
│ - Risk answers       │              │ - Change analysis    │
│ - Change answers     │              │ - Driver analysis    │
│ - Impact answers     │              │ - Trend analysis     │
└──────────────────────┘              └──────────────────────┘
        │                                             │
        └────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ User Response              │
        │ (Accurate, data-driven)    │
        └────────────────────────────┘
```

---

## Example: How Blob Data Powers Answers

### Question: "What supplier changes?"

**Step 1: Load blob data**
```python
current_records, previous_records = load_current_previous_from_blob()
# Returns 1000+ records with supplier info
```

**Step 2: Classify question**
```python
q_type = classify_question("What supplier changes?")
# Returns: "change"
```

**Step 3: Generate answer using detail_records**
```python
answer = generate_change_answer(detail_records, context)
# Analyzes detail_records to find supplier changes
# Returns: "45 supplier changes detected across 3 locations"
```

---

## Why Not Use Aggregated Data?

You might ask: "Why not just store pre-computed metrics instead of raw records?"

**Answer:** Because:

1. **Flexibility** - Users ask diverse questions requiring different slices of data
2. **Accuracy** - Raw data allows precise filtering and computation
3. **Traceability** - Can drill down to specific records for investigation
4. **Real-time** - Latest blob data always reflects current state
5. **Scope-specific** - Can compute metrics for any location/supplier/material combination

---

## Summary

The blob files are **not optional** - they are the **source of truth** for all planning data. Without them:
- ❌ Cannot answer "what changed?" questions
- ❌ Cannot compute health scores
- ❌ Cannot identify risks
- ❌ Cannot analyze impact
- ❌ Cannot provide accurate metrics

The system is designed to read blob data on every request to ensure answers are always based on the latest planning information.
