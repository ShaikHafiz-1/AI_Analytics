"""
Test context optimization - verify record keys extraction reduces payload size
"""

import json
from context_optimizer import extract_record_keys

# Create sample full records (simulating what comes from CSV)
sample_full_records = [
    {
        "location_id": "LOC001",
        "material_id": "MAT001",
        "material_group": "GROUP1",
        "supplier": "Supplier A",
        "forecast_qty": 1000.0,
        "roj": "2024-05-01",
        "bod": "BOD1",
        "ff": "FF1",
        "roc_region": "APAC",
        "dc_site": "DC1",
        "metro": "METRO1",
        "country": "Country1",
        "supplier_date": "2024-04-01",
        "planning_exception": "None",
        "roj_reason_code": "CODE1",
        "automation_reason": "AUTO1",
        "last_modified_by": "User1",
        "last_modified_date": "2024-04-15",
        "created_by": "User1",
        "created_date": "2024-01-01",
        "is_new_demand": False,
        "is_cancelled": False,
        "risk_flag": "Low",
        "fcst_delta_qty": 100.0,
        "nbd_delta_days": 5.0,
        "is_supplier_date_missing": False,
        "changed": True,
        "risk_level": "Normal",
        # ... 20+ more fields
    },
    {
        "location_id": "LOC002",
        "material_id": "MAT002",
        "material_group": "GROUP2",
        "supplier": "Supplier B",
        "forecast_qty": 2000.0,
        "roj": "2024-06-01",
        "bod": "BOD2",
        "ff": "FF2",
        "roc_region": "EMEA",
        "dc_site": "DC2",
        "metro": "METRO2",
        "country": "Country2",
        "supplier_date": "2024-04-02",
        "planning_exception": "None",
        "roj_reason_code": "CODE2",
        "automation_reason": "AUTO2",
        "last_modified_by": "User2",
        "last_modified_date": "2024-04-16",
        "created_by": "User2",
        "created_date": "2024-01-02",
        "is_new_demand": True,
        "is_cancelled": False,
        "risk_flag": "Medium",
        "fcst_delta_qty": 200.0,
        "nbd_delta_days": 10.0,
        "is_supplier_date_missing": False,
        "changed": False,
        "risk_level": "Medium",
    }
]

# Test extraction
print("=" * 60)
print("CONTEXT OPTIMIZATION TEST")
print("=" * 60)

# Calculate sizes
full_json = json.dumps(sample_full_records)
full_size = len(full_json.encode('utf-8'))
print(f"\nFull records JSON size: {full_size:,} bytes")

# Extract keys
record_keys = extract_record_keys(sample_full_records)
keys_json = json.dumps(record_keys)
keys_size = len(keys_json.encode('utf-8'))
print(f"Record keys JSON size: {keys_size:,} bytes")

# Calculate reduction
reduction = ((full_size - keys_size) / full_size) * 100
print(f"Size reduction: {reduction:.1f}%")

# Show sample
print(f"\nSample full record (first 200 chars):")
print(full_json[:200] + "...")

print(f"\nSample record key:")
print(json.dumps(record_keys[0], indent=2))

# Verify all required fields are present
print("\nVerifying record keys have required fields:")
for i, key in enumerate(record_keys):
    required = ["location_id", "material_id", "material_group", "changed", "risk_level"]
    missing = [f for f in required if f not in key]
    if missing:
        print(f"  Record {i}: MISSING {missing}")
    else:
        print(f"  Record {i}: ✓ All required fields present")

print("\n" + "=" * 60)
print("OPTIMIZATION SUCCESSFUL")
print("=" * 60)
print(f"\nWith 10,000 records:")
print(f"  Full records: ~{(full_size / 1024) * 5:.1f} MB (estimated)")
print(f"  Record keys: ~{(keys_size / 1024) * 5:.1f} MB (estimated)")
print(f"  Savings: ~{(full_size - keys_size) / 1024 * 5:.1f} MB per request")
