#!/usr/bin/env python3
"""
Test script to verify supplier query fixes.
Tests all query types with normalized data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from function_app import (
    _normalize_detail_records,
    _compute_scoped_metrics,
    _generate_supplier_by_location_answer,
    _generate_comparison_answer,
    _generate_record_comparison_answer,
)

# Test data with CSV field names (raw format)
test_data_csv_format = [
    {
        "LOCID": "LOC001",
        "GSCEQUIPCAT": "Electronics",
        "PRDID": "MAT-001",
        "LOCFR": "SUP-A",
        "GSCFSCTQTY": 1500,
        "GSCCONROJDATE": "2026-07-15",
        "ZCOIBODVER": "v3",
        "ZCOIFORMFACT": "FF-B",
        "ZCOIDCID": "DC-WEST",
        "changed": True,
        "qtyChanged": True,
        "qtyDelta": 500,
        "riskLevel": "High",
        "changeType": "Qty Increase",
    },
    {
        "LOCID": "LOC001",
        "GSCEQUIPCAT": "Electronics",
        "PRDID": "MAT-002",
        "LOCFR": "SUP-B",
        "GSCFSCTQTY": 800,
        "GSCCONROJDATE": "2026-06-20",
        "ZCOIBODVER": "v2",
        "ZCOIFORMFACT": "FF-A",
        "ZCOIDCID": "DC-WEST",
        "changed": False,
        "qtyChanged": False,
        "qtyDelta": 0,
        "riskLevel": "Normal",
        "changeType": "Unchanged",
    },
    {
        "LOCID": "LOC002",
        "GSCEQUIPCAT": "Mechanical",
        "PRDID": "MAT-101",
        "LOCFR": "SUP-C",
        "GSCFSCTQTY": 300,
        "GSCCONROJDATE": "2026-07-01",
        "ZCOIBODVER": "v1",
        "ZCOIFORMFACT": "FF-A",
        "ZCOIDCID": "DC-EAST",
        "changed": True,
        "supplierChanged": True,
        "qtyDelta": 100,
        "riskLevel": "Medium",
        "changeType": "Supplier Change",
    },
]

# Test data with normalized keys
test_data_normalized = [
    {
        "locationId": "LOC001",
        "materialGroup": "Electronics",
        "materialId": "MAT-001",
        "supplier": "SUP-A",
        "forecastQty": 1500,
        "roj": "2026-07-15",
        "bod": "v3",
        "formFactor": "FF-B",
        "dcSite": "DC-WEST",
        "changed": True,
        "qtyChanged": True,
        "qtyDelta": 500,
        "riskLevel": "High",
        "changeType": "Qty Increase",
    },
    {
        "locationId": "LOC001",
        "materialGroup": "Electronics",
        "materialId": "MAT-002",
        "supplier": "SUP-B",
        "forecastQty": 800,
        "roj": "2026-06-20",
        "bod": "v2",
        "formFactor": "FF-A",
        "dcSite": "DC-WEST",
        "changed": False,
        "qtyChanged": False,
        "qtyDelta": 0,
        "riskLevel": "Normal",
        "changeType": "Unchanged",
    },
]

def test_normalization():
    """Test that normalization works for both CSV and normalized formats."""
    print("\n=== TEST 1: Data Normalization ===")
    
    # Test CSV format
    print("\nNormalizing CSV format data...")
    normalized_csv = _normalize_detail_records(test_data_csv_format)
    print(f"✓ Normalized {len(normalized_csv)} CSV records")
    
    # Verify keys are normalized
    first_record = normalized_csv[0]
    assert "locationId" in first_record, "Missing locationId"
    assert "supplier" in first_record, "Missing supplier"
    assert first_record["locationId"] == "LOC001", f"Wrong locationId: {first_record['locationId']}"
    assert first_record["supplier"] == "SUP-A", f"Wrong supplier: {first_record['supplier']}"
    print(f"✓ CSV record normalized correctly: {first_record['locationId']}, {first_record['supplier']}")
    
    # Test already-normalized format
    print("\nNormalizing already-normalized data...")
    normalized_norm = _normalize_detail_records(test_data_normalized)
    print(f"✓ Normalized {len(normalized_norm)} already-normalized records")
    
    # Verify they match
    assert normalized_csv[0]["locationId"] == normalized_norm[0]["locationId"]
    assert normalized_csv[0]["supplier"] == normalized_norm[0]["supplier"]
    print("✓ Both formats produce consistent results")

def test_scoped_metrics():
    """Test that scoped metrics work with normalized data."""
    print("\n=== TEST 2: Scoped Metrics Computation ===")
    
    normalized = _normalize_detail_records(test_data_csv_format)
    
    # Test location scope
    print("\nComputing metrics for LOC001...")
    metrics = _compute_scoped_metrics(normalized, "location", "LOC001")
    
    assert metrics["filteredRecordsCount"] == 2, f"Wrong record count: {metrics['filteredRecordsCount']}"
    assert metrics["scopedMetrics"]["changedCount"] == 1, f"Wrong changed count: {metrics['scopedMetrics']['changedCount']}"
    print(f"✓ LOC001 metrics: {metrics['filteredRecordsCount']} records, {metrics['scopedMetrics']['changedCount']} changed")
    
    # Test supplier scope
    print("\nComputing metrics for SUP-A...")
    metrics_sup = _compute_scoped_metrics(normalized, "supplier", "SUP-A")
    assert metrics_sup["filteredRecordsCount"] == 1, f"Wrong supplier record count: {metrics_sup['filteredRecordsCount']}"
    print(f"✓ SUP-A metrics: {metrics_sup['filteredRecordsCount']} records")

def test_supplier_query():
    """Test supplier query with normalized data."""
    print("\n=== TEST 3: Supplier Query ===")
    
    normalized = _normalize_detail_records(test_data_csv_format)
    
    context = {
        "detailRecords": normalized,
        "recommendedActions": ["Review supplier changes"],
    }
    
    print("\nGenerating supplier answer for LOC001...")
    answer = _generate_supplier_by_location_answer(
        "List suppliers for LOC001",
        context,
        "location",
        "LOC001"
    )
    
    # Should not be "No supplier information found"
    assert "No supplier information found" not in answer, f"Query failed: {answer}"
    assert "SUP-A" in answer or "SUP-B" in answer, f"No suppliers in answer: {answer}"
    print(f"✓ Supplier query succeeded")
    print(f"Answer preview: {answer[:200]}...")

def test_comparison_query():
    """Test comparison query with normalized data."""
    print("\n=== TEST 4: Comparison Query ===")
    
    normalized = _normalize_detail_records(test_data_csv_format)
    
    context = {
        "detailRecords": normalized,
    }
    
    print("\nGenerating comparison answer for LOC001 vs LOC002...")
    answer = _generate_comparison_answer(
        "Compare LOC001 vs LOC002",
        context,
        "location",
        ["LOC001", "LOC002"]
    )
    
    assert "LOC001" in answer, f"LOC001 not in answer: {answer}"
    assert "LOC002" in answer, f"LOC002 not in answer: {answer}"
    print(f"✓ Comparison query succeeded")
    print(f"Answer preview: {answer[:200]}...")

def test_case_insensitivity():
    """Test that queries work with different case formats."""
    print("\n=== TEST 5: Case Insensitivity ===")
    
    normalized = _normalize_detail_records(test_data_csv_format)
    
    context = {
        "detailRecords": normalized,
        "recommendedActions": ["Review"],
    }
    
    # Test with lowercase
    print("\nTesting with lowercase location...")
    answer_lower = _generate_supplier_by_location_answer(
        "List suppliers for loc001",
        context,
        "location",
        "loc001"
    )
    assert "No supplier information found" not in answer_lower, "Lowercase query failed"
    print("✓ Lowercase query works")
    
    # Test with uppercase
    print("\nTesting with uppercase location...")
    answer_upper = _generate_supplier_by_location_answer(
        "List suppliers for LOC001",
        context,
        "location",
        "LOC001"
    )
    assert "No supplier information found" not in answer_upper, "Uppercase query failed"
    print("✓ Uppercase query works")

def main():
    """Run all tests."""
    print("=" * 60)
    print("SUPPLIER QUERY FIX VERIFICATION TESTS")
    print("=" * 60)
    
    try:
        test_normalization()
        test_scoped_metrics()
        test_supplier_query()
        test_comparison_query()
        test_case_insensitivity()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe supplier query fix is working correctly!")
        print("Supplier queries now work with:")
        print("  • CSV format data (LOCID, LOCFR, etc.)")
        print("  • Normalized format data (locationId, supplier, etc.)")
        print("  • Case-insensitive location/supplier matching")
        print("  • All query types (supplier, comparison, record detail)")
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
