"""
Validate scoped computation fixes using existing test data.

This script validates the scoped_metrics and generative_responses modules
without requiring Azure Blob Storage credentials.
"""

import json
import logging
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Import the new modules
from scoped_metrics import (
    compute_scoped_metrics,
    get_location_metrics,
    get_design_changes,
    get_supplier_changes,
    get_quantity_changes,
    get_roj_changes,
    compare_locations,
    get_top_locations,
    get_top_suppliers,
    get_top_materials,
)
from generative_responses import build_contextual_response, GenerativeResponseBuilder


def create_sample_records() -> List[Dict]:
    """Create sample records for testing."""
    records = [
        # Location CYS20_F01C01 - 3 records with 1 change
        {
            "locationId": "CYS20_F01C01",
            "materialId": "MAT001",
            "materialGroup": "LVS",
            "supplier": "10_AMER",
            "supplierPrevious": "10_AMER",
            "forecastQty": 100,
            "forecastQtyPrevious": 100,
            "rojCurrent": "2026-04-13",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD1",
            "bodPrevious": "BOD1",
            "ffCurrent": "FF1",
            "ffPrevious": "FF1",
            "qtyDelta": 0,
            "rojDelta": 0,
            "qtyChanged": False,
            "supplierChanged": False,
            "designChanged": False,
            "rojChanged": False,
            "changed": False,
        },
        {
            "locationId": "CYS20_F01C01",
            "materialId": "MAT002",
            "materialGroup": "UPS",
            "supplier": "130_AMER",
            "supplierPrevious": "130_AMER",
            "forecastQty": 200,
            "forecastQtyPrevious": 150,
            "rojCurrent": "2026-04-13",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD2",
            "bodPrevious": "BOD2",
            "ffCurrent": "FF2",
            "ffPrevious": "FF2",
            "qtyDelta": 50,
            "rojDelta": 0,
            "qtyChanged": True,
            "supplierChanged": False,
            "designChanged": False,
            "rojChanged": False,
            "changed": True,
        },
        {
            "locationId": "CYS20_F01C01",
            "materialId": "MAT003",
            "materialGroup": "MVSXRM",
            "supplier": "1690_AMER",
            "supplierPrevious": "1690_AMER",
            "forecastQty": 300,
            "forecastQtyPrevious": 300,
            "rojCurrent": "2026-04-13",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD3",
            "bodPrevious": "BOD2",
            "ffCurrent": "FF3",
            "ffPrevious": "FF3",
            "qtyDelta": 0,
            "rojDelta": 0,
            "qtyChanged": False,
            "supplierChanged": False,
            "designChanged": True,
            "rojChanged": False,
            "changed": True,
        },
        # Location DSM18_F01C01 - 3 records with 2 changes
        {
            "locationId": "DSM18_F01C01",
            "materialId": "MAT004",
            "materialGroup": "LVS",
            "supplier": "110_AMER",
            "supplierPrevious": "110_AMER",
            "forecastQty": 150,
            "forecastQtyPrevious": 150,
            "rojCurrent": "2026-04-13",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD4",
            "bodPrevious": "BOD4",
            "ffCurrent": "FF4",
            "ffPrevious": "FF4",
            "qtyDelta": 0,
            "rojDelta": 0,
            "qtyChanged": False,
            "supplierChanged": False,
            "designChanged": False,
            "rojChanged": False,
            "changed": False,
        },
        {
            "locationId": "DSM18_F01C01",
            "materialId": "MAT005",
            "materialGroup": "UPS",
            "supplier": "1690_AMER",
            "supplierPrevious": "210_AMER",
            "forecastQty": 250,
            "forecastQtyPrevious": 250,
            "rojCurrent": "2026-04-13",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD5",
            "bodPrevious": "BOD5",
            "ffCurrent": "FF5",
            "ffPrevious": "FF5",
            "qtyDelta": 0,
            "rojDelta": 0,
            "qtyChanged": False,
            "supplierChanged": True,
            "designChanged": False,
            "rojChanged": False,
            "changed": True,
        },
        {
            "locationId": "DSM18_F01C01",
            "materialId": "MAT006",
            "materialGroup": "MVSXRM",
            "supplier": "170_AMER",
            "supplierPrevious": "170_AMER",
            "forecastQty": 350,
            "forecastQtyPrevious": 300,
            "rojCurrent": "2026-04-20",
            "rojPrevious": "2026-04-13",
            "bodCurrent": "BOD6",
            "bodPrevious": "BOD6",
            "ffCurrent": "FF6",
            "ffPrevious": "FF6",
            "qtyDelta": 50,
            "rojDelta": 7,
            "qtyChanged": True,
            "supplierChanged": False,
            "designChanged": False,
            "rojChanged": True,
            "changed": True,
        },
    ]
    return records


def test_location_scoped_metrics():
    """Test 1: Location-scoped metrics are correct."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Location-Scoped Metrics")
    logger.info("="*80)
    
    records = create_sample_records()
    
    # Test CYS20_F01C01
    metrics_cys = get_location_metrics(records, "CYS20_F01C01")
    logger.info(f"CYS20_F01C01 metrics:")
    logger.info(f"  Total records: {metrics_cys['totalRecords']}")
    logger.info(f"  Changed records: {metrics_cys['changedRecords']}")
    logger.info(f"  Change rate: {metrics_cys['changeRate']}%")
    logger.info(f"  Design changes: {metrics_cys['designChangedCount']}")
    logger.info(f"  Supplier changes: {metrics_cys['supplierChangedCount']}")
    logger.info(f"  Qty changes: {metrics_cys['qtyChangedCount']}")
    
    # Verify
    assert metrics_cys['totalRecords'] == 3, f"Expected 3 records, got {metrics_cys['totalRecords']}"
    assert metrics_cys['changedRecords'] == 2, f"Expected 2 changed, got {metrics_cys['changedRecords']}"
    assert metrics_cys['designChangedCount'] == 1, f"Expected 1 design change, got {metrics_cys['designChangedCount']}"
    assert metrics_cys['qtyChangedCount'] == 1, f"Expected 1 qty change, got {metrics_cys['qtyChangedCount']}"
    
    logger.info("✓ CYS20_F01C01 metrics correct")
    
    # Test DSM18_F01C01
    metrics_dsm = get_location_metrics(records, "DSM18_F01C01")
    logger.info(f"\nDSM18_F01C01 metrics:")
    logger.info(f"  Total records: {metrics_dsm['totalRecords']}")
    logger.info(f"  Changed records: {metrics_dsm['changedRecords']}")
    logger.info(f"  Change rate: {metrics_dsm['changeRate']}%")
    logger.info(f"  Design changes: {metrics_dsm['designChangedCount']}")
    logger.info(f"  Supplier changes: {metrics_dsm['supplierChangedCount']}")
    logger.info(f"  Qty changes: {metrics_dsm['qtyChangedCount']}")
    logger.info(f"  ROJ changes: {metrics_dsm['rojChangedCount']}")
    
    # Verify
    assert metrics_dsm['totalRecords'] == 3, f"Expected 3 records, got {metrics_dsm['totalRecords']}"
    assert metrics_dsm['changedRecords'] == 2, f"Expected 2 changed, got {metrics_dsm['changedRecords']}"
    assert metrics_dsm['supplierChangedCount'] == 1, f"Expected 1 supplier change, got {metrics_dsm['supplierChangedCount']}"
    assert metrics_dsm['qtyChangedCount'] == 1, f"Expected 1 qty change, got {metrics_dsm['qtyChangedCount']}"
    assert metrics_dsm['rojChangedCount'] == 1, f"Expected 1 ROJ change, got {metrics_dsm['rojChangedCount']}"
    
    logger.info("✓ DSM18_F01C01 metrics correct")
    return True


def test_design_filtering():
    """Test 2: Design filtering works correctly."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Design Filtering")
    logger.info("="*80)
    
    records = create_sample_records()
    
    # Get design changes globally
    design_global = get_design_changes(records)
    logger.info(f"Global design changes: {design_global['designChangedCount']}")
    logger.info(f"Affected suppliers: {design_global['affectedSuppliers']}")
    
    assert design_global['designChangedCount'] == 1, f"Expected 1 global design change, got {design_global['designChangedCount']}"
    
    # Get design changes for CYS20_F01C01
    design_cys = get_design_changes(records, location_id="CYS20_F01C01")
    logger.info(f"\nCYS20_F01C01 design changes: {design_cys['designChangedCount']}")
    logger.info(f"Affected suppliers: {design_cys['affectedSuppliers']}")
    
    assert design_cys['designChangedCount'] == 1, f"Expected 1 design change at CYS20, got {design_cys['designChangedCount']}"
    assert "1690_AMER" in design_cys['affectedSuppliers'], "Expected 1690_AMER in suppliers"
    
    # Get design changes for DSM18_F01C01
    design_dsm = get_design_changes(records, location_id="DSM18_F01C01")
    logger.info(f"\nDSM18_F01C01 design changes: {design_dsm['designChangedCount']}")
    
    assert design_dsm['designChangedCount'] == 0, f"Expected 0 design changes at DSM18, got {design_dsm['designChangedCount']}"
    
    logger.info("✓ Design filtering correct")
    return True


def test_comparison():
    """Test 3: Comparison shows real differences."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Comparison")
    logger.info("="*80)
    
    records = create_sample_records()
    
    comparison = compare_locations(records, "CYS20_F01C01", "DSM18_F01C01")
    
    logger.info(f"CYS20_F01C01: {comparison['location1Metrics']['totalRecords']} records, "
               f"{comparison['location1Metrics']['changedRecords']} changes")
    logger.info(f"DSM18_F01C01: {comparison['location2Metrics']['totalRecords']} records, "
               f"{comparison['location2Metrics']['changedRecords']} changes")
    logger.info(f"Differences: {comparison['differences']}")
    
    # Verify
    assert comparison['location1Metrics']['changedRecords'] == 2, "CYS20 should have 2 changes"
    assert comparison['location2Metrics']['changedRecords'] == 2, "DSM18 should have 2 changes"
    assert comparison['differences']['changedRecords'] == 0, "Both should have same change count"
    
    logger.info("✓ Comparison correct")
    return True


def test_generative_responses():
    """Test 4: Generative responses are natural and varied."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Generative Responses")
    logger.info("="*80)
    
    records = create_sample_records()
    metrics = compute_scoped_metrics(records)
    
    # Build health response
    builder = GenerativeResponseBuilder()
    health_response = builder.build_health_response({
        "planningHealth": 60,
        "changedRecordCount": metrics["changedRecords"],
        "totalRecords": metrics["totalRecords"],
        "designChanges": metrics["designChangedCount"],
        "supplierChanges": metrics["supplierChangedCount"],
        "qtyChanges": metrics["qtyChangedCount"],
    })
    
    logger.info(f"Health Response: {health_response}")
    assert len(health_response) > 20, "Response too short"
    assert "records" in health_response.lower(), "Response should mention records"
    assert ("changed" in health_response.lower() or "affected" in health_response.lower()), "Response should mention changes or affected"
    
    # Build location response
    location_metrics = get_location_metrics(records, "CYS20_F01C01")
    location_response = builder.build_location_response("CYS20_F01C01", location_metrics)
    
    logger.info(f"Location Response: {location_response}")
    assert len(location_response) > 20, "Response too short"
    assert "CYS20_F01C01" in location_response, "Response should mention location"
    
    # Build design response
    design_metrics = get_design_changes(records)
    design_response = builder.build_design_response(design_metrics)
    
    logger.info(f"Design Response: {design_response}")
    assert len(design_response) > 20, "Response too short"
    assert "design" in design_response.lower(), "Response should mention design"
    
    logger.info("✓ Generative responses correct")
    return True


def test_roj_logic():
    """Test 5: ROJ logic works correctly."""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: ROJ Schedule Logic")
    logger.info("="*80)
    
    records = create_sample_records()
    
    # Get ROJ changes globally
    roj_global = get_roj_changes(records)
    logger.info(f"Global ROJ changes: {roj_global['rojChangedCount']}")
    logger.info(f"Total ROJ delta: {roj_global['totalRojDelta']} days")
    logger.info(f"Average ROJ delta: {roj_global['averageRojDelta']} days")
    
    assert roj_global['rojChangedCount'] == 1, f"Expected 1 ROJ change, got {roj_global['rojChangedCount']}"
    assert roj_global['totalRojDelta'] == 7, f"Expected 7 days delta, got {roj_global['totalRojDelta']}"
    
    # Get ROJ changes for DSM18_F01C01
    roj_dsm = get_roj_changes(records, location_id="DSM18_F01C01")
    logger.info(f"\nDSM18_F01C01 ROJ changes: {roj_dsm['rojChangedCount']}")
    
    assert roj_dsm['rojChangedCount'] == 1, f"Expected 1 ROJ change at DSM18, got {roj_dsm['rojChangedCount']}"
    
    logger.info("✓ ROJ logic correct")
    return True


def main():
    """Run all validation tests."""
    logger.info("Starting Scoped Computation Validation Tests")
    logger.info("="*80)
    
    tests = [
        ("Location-Scoped Metrics", test_location_scoped_metrics),
        ("Design Filtering", test_design_filtering),
        ("Comparison", test_comparison),
        ("Generative Responses", test_generative_responses),
        ("ROJ Schedule Logic", test_roj_logic),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {name} FAILED: {e}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Total: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Pass Rate: {passed / len(tests) * 100:.1f}%")
    
    if failed == 0:
        logger.info("\n✓ ALL TESTS PASSED - Scoped computation fixes are working correctly!")
        return True
    else:
        logger.error(f"\n✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
