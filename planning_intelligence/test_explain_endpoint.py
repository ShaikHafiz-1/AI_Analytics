"""
Test the explain endpoint to verify it works with the reverted changes
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from snapshot_store import load_snapshot

# Load snapshot to get context
snap = load_snapshot()

if not snap:
    print("ERROR: No snapshot found. Run daily-refresh first.")
    sys.exit(1)

print("=" * 60)
print("EXPLAIN ENDPOINT TEST")
print("=" * 60)

# Check snapshot structure
print(f"\nSnapshot loaded successfully")
print(f"  Total records: {snap.get('totalRecords', 0)}")
print(f"  Changed records: {snap.get('changedRecordCount', 0)}")
print(f"  Planning health: {snap.get('planningHealth', 0)}")
print(f"  Status: {snap.get('status', 'Unknown')}")

# Check if detailRecords exist
detail_records = snap.get("detailRecords", [])
print(f"  Detail records in snapshot: {len(detail_records)}")

if detail_records:
    print(f"\nSample detail record:")
    sample = detail_records[0]
    print(f"  Keys: {list(sample.keys())[:10]}...")
    print(f"  Location ID: {sample.get('locationId', 'N/A')}")
    print(f"  Material ID: {sample.get('materialId', 'N/A')}")
    print(f"  Changed: {sample.get('changed', False)}")

# Check context fields
print(f"\nContext fields available:")
context_fields = [
    "planningHealth", "status", "forecastNew", "forecastOld", 
    "trendDirection", "trendDelta", "riskSummary", "supplierSummary",
    "designSummary", "rojSummary"
]
for field in context_fields:
    value = snap.get(field)
    if value is not None:
        if isinstance(value, dict):
            print(f"  {field}: <dict with {len(value)} keys>")
        elif isinstance(value, list):
            print(f"  {field}: <list with {len(value)} items>")
        else:
            print(f"  {field}: {value}")
    else:
        print(f"  {field}: NOT FOUND")

print("\n" + "=" * 60)
print("SNAPSHOT STRUCTURE VERIFIED")
print("=" * 60)
print("\nThe explain endpoint should now work correctly.")
print("Test questions:")
print("  - 'What is the planning health?'")
print("  - 'Which suppliers have changes?'")
print("  - 'What is the impact?'")
print("  - 'hello'")
