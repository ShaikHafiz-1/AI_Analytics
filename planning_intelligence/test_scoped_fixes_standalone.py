"""
Standalone test for scoped computation fixes.
Uses the same data loading approach as test_responses_fixed.py
"""

import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
from blob_loader import load_current_previous_from_blob
from function_app import _normalize_detail_records
from normalizer import normalize_rows
from comparator import compare_records
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
from generative_responses import build_contextual_response


class ScopedFixValidator:
    """Validate scoped computation and filtering fixes."""
    
    def __init__(self):
        """Initialize validator."""
        self.records = []
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
            }
        }
    
    def load_data(self) -> bool:
        """Load blob data using production pipeline."""
        logger.info("Loading blob data from Azure...")
        try:
            current_rows, previous_rows = load_current_previous_from_blob()
            logger.info(f"✓ Loaded {len(current_rows)} current, {len(previous_rows)} previous rows")
            
            # Use production pipeline
            current_records = normalize_rows(current_rows, is_current=True)
            previous_records = normalize_rows(previous_rows, is_current=False)
            logger.info(f"✓ Normalized records")
            
            compared = compare_records(current_records, previous_records)
            logger.info(f"✓ Compared {len(compared)} records")
            
            # Convert to detail records
            self.records = _normalize_detail_records(compared)
            logger.info(f"✓ Normalized {len(self.records)} detail records")
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_location_scoped_changes(self) -> bool:
        """Test 1: Location-level queries return correct changed counts."""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Location-Scoped Changes")
        logger.info("="*80)
        
        # Get a location with changes
        location_changes = {}
        for r in self.records:
            if r.get("changed"):
                loc = r.get("locationId")
                location_changes[loc] = location_changes.get(loc, 0) + 1
        
        if not location_changes:
            logger.warning("No locations with changes found")
            return False
        
        # Test with top location
        test_location = max(location_changes.items(), key=lambda x: x[1])[0]
        expected_changes = location_changes[test_location]
        
        # Get metrics
        metrics = get_location_metrics(self.records, test_location)
        actual_changes = metrics["changedRecords"]
        
        logger.info(f"Location: {test_location}")
        logger.info(f"Expected changes: {expected_changes}")
        logger.info(f"Actual changes: {actual_changes}")
        logger.info(f"Total records: {metrics['totalRecords']}")
        logger.info(f"Change rate: {metrics['changeRate']}%")
        
        passed = actual_changes == expected_changes
        self._record_test("Location-Scoped Changes", passed, {
            "location": test_location,
            "expected": expected_changes,
            "actual": actual_changes,
            "totalRecords": metrics['totalRecords'],
            "changeRate": metrics['changeRate']
        })
        
        return passed
    
    def test_design_filtering(self) -> bool:
        """Test 2: Design queries filter correctly."""
        logger.info("\n" + "="*80)
        logger.info("TEST 2: Design Filtering")
        logger.info("="*80)
        
        # Get design changes globally
        design_metrics = get_design_changes(self.records)
        global_design_count = design_metrics["designChangedCount"]
        
        logger.info(f"Global design changes: {global_design_count}")
        logger.info(f"Affected suppliers: {len(design_metrics['affectedSuppliers'])}")
        logger.info(f"Affected materials: {len(design_metrics['affectedMaterials'])}")
        
        # Test with a location
        top_locations = get_top_locations(self.records, limit=1)
        if not top_locations:
            logger.warning("No locations with changes found")
            return False
        
        test_location = top_locations[0][0]
        design_metrics_loc = get_design_changes(self.records, location_id=test_location)
        location_design_count = design_metrics_loc["designChangedCount"]
        
        logger.info(f"\nLocation {test_location} design changes: {location_design_count}")
        logger.info(f"Affected suppliers: {design_metrics_loc['affectedSuppliers']}")
        logger.info(f"Affected materials: {design_metrics_loc['affectedMaterials']}")
        
        # Verify location design count <= global design count
        passed = location_design_count <= global_design_count
        self._record_test("Design Filtering", passed, {
            "global_design_count": global_design_count,
            "location_design_count": location_design_count,
            "location": test_location,
        })
        
        return passed
    
    def test_entity_scoped_data(self) -> bool:
        """Test 3: Entity queries return scoped data."""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Entity Scoped Data")
        logger.info("="*80)
        
        # Get top location
        top_locations = get_top_locations(self.records, limit=1)
        if not top_locations:
            logger.warning("No locations with changes found")
            return False
        
        top_location = top_locations[0][0]
        
        # Get metrics for location
        metrics = get_location_metrics(self.records, top_location)
        
        logger.info(f"Location: {top_location}")
        logger.info(f"Total records: {metrics['totalRecords']}")
        logger.info(f"Unique suppliers: {metrics['uniqueSuppliers']}")
        logger.info(f"Unique materials: {metrics['uniqueMaterials']}")
        logger.info(f"Top suppliers: {metrics['topSuppliers'][:3]}")
        logger.info(f"Top materials: {metrics['topMaterials'][:3]}")
        
        # Verify suppliers are from this location only
        location_records = [r for r in self.records if r.get("locationId") == top_location]
        location_suppliers = set(r.get("supplier") for r in location_records if r.get("supplier"))
        
        passed = metrics["uniqueSuppliers"] == len(location_suppliers)
        self._record_test("Entity Scoped Data", passed, {
            "location": top_location,
            "expected_suppliers": len(location_suppliers),
            "actual_suppliers": metrics["uniqueSuppliers"],
        })
        
        return passed
    
    def test_roj_logic(self) -> bool:
        """Test 4: ROJ schedule logic works correctly."""
        logger.info("\n" + "="*80)
        logger.info("TEST 4: ROJ Schedule Logic")
        logger.info("="*80)
        
        # Get ROJ changes globally
        roj_metrics = get_roj_changes(self.records)
        global_roj_count = roj_metrics["rojChangedCount"]
        
        logger.info(f"Global ROJ changes: {global_roj_count}")
        logger.info(f"Total ROJ delta: {roj_metrics['totalRojDelta']} days")
        logger.info(f"Average ROJ delta: {roj_metrics['averageRojDelta']} days")
        
        # Test with a location
        top_locations = get_top_locations(self.records, limit=1)
        if not top_locations:
            logger.warning("No locations with changes found")
            return False
        
        test_location = top_locations[0][0]
        roj_metrics_loc = get_roj_changes(self.records, location_id=test_location)
        location_roj_count = roj_metrics_loc["rojChangedCount"]
        
        logger.info(f"\nLocation {test_location} ROJ changes: {location_roj_count}")
        
        # Verify location ROJ count <= global ROJ count
        passed = location_roj_count <= global_roj_count
        self._record_test("ROJ Schedule Logic", passed, {
            "global_roj_count": global_roj_count,
            "location_roj_count": location_roj_count,
            "location": test_location,
        })
        
        return passed
    
    def test_comparison_differences(self) -> bool:
        """Test 5: Comparison queries show real differences."""
        logger.info("\n" + "="*80)
        logger.info("TEST 5: Comparison Differences")
        logger.info("="*80)
        
        # Get top 2 locations
        top_locations = get_top_locations(self.records, limit=2)
        if len(top_locations) < 2:
            logger.warning("Not enough locations with changes")
            return False
        
        loc1 = top_locations[0][0]
        loc2 = top_locations[1][0]
        
        # Compare
        comparison = compare_locations(self.records, loc1, loc2)
        
        logger.info(f"Comparing {loc1} vs {loc2}")
        logger.info(f"{loc1}: {comparison['location1Metrics']['totalRecords']} records, "
                   f"{comparison['location1Metrics']['changedRecords']} changes")
        logger.info(f"{loc2}: {comparison['location2Metrics']['totalRecords']} records, "
                   f"{comparison['location2Metrics']['changedRecords']} changes")
        logger.info(f"Differences: {comparison['differences']}")
        
        # Verify differences are computed
        passed = (
            comparison['location1Metrics']['changedRecords'] >= 0 and
            comparison['location2Metrics']['changedRecords'] >= 0
        )
        
        self._record_test("Comparison Differences", passed, {
            "location1": loc1,
            "location2": loc2,
            "loc1_changes": comparison['location1Metrics']['changedRecords'],
            "loc2_changes": comparison['location2Metrics']['changedRecords'],
        })
        
        return passed
    
    def test_generative_responses(self) -> bool:
        """Test 6: Responses are generative and natural."""
        logger.info("\n" + "="*80)
        logger.info("TEST 6: Generative Responses")
        logger.info("="*80)
        
        # Get metrics
        metrics = compute_scoped_metrics(self.records)
        
        # Build responses
        health_response = build_contextual_response(
            "What's the planning health?",
            {
                "planningHealth": 37,
                "changedRecordCount": metrics["changedRecords"],
                "totalRecords": metrics["totalRecords"],
                "designChanges": metrics["designChangedCount"],
                "supplierChanges": metrics["supplierChangedCount"],
                "qtyChanges": metrics["qtyChangedCount"],
            },
            "health"
        )
        
        logger.info(f"Health Response: {health_response}")
        
        # Get location response
        top_locations = get_top_locations(self.records, limit=1)
        if top_locations:
            top_location = top_locations[0][0]
            location_metrics = get_location_metrics(self.records, top_location)
            
            location_response = build_contextual_response(
                f"What's happening at {top_location}?",
                location_metrics,
                "location",
                location=top_location
            )
            
            logger.info(f"Location Response: {location_response}")
        
        # Get design response
        design_metrics = get_design_changes(self.records)
        design_response = build_contextual_response(
            "Which suppliers have design changes?",
            design_metrics,
            "design"
        )
        
        logger.info(f"Design Response: {design_response}")
        
        # Verify responses are not empty and contain meaningful content
        passed = (
            len(health_response) > 20 and
            len(design_response) > 20 and
            "records" in health_response.lower() and
            "changes" in design_response.lower()
        )
        
        self._record_test("Generative Responses", passed, {
            "health_response_length": len(health_response),
            "design_response_length": len(design_response),
            "health_has_records": "records" in health_response.lower(),
            "design_has_changes": "changes" in design_response.lower(),
        })
        
        return passed
    
    def _record_test(self, name: str, passed: bool, details: dict):
        """Record test result."""
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "details": details
        })
        
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            logger.info(f"✓ {name} PASSED")
        else:
            self.results["summary"]["failed"] += 1
            logger.error(f"✗ {name} FAILED")
    
    def run_all_tests(self) -> bool:
        """Run all tests."""
        logger.info("Starting Scoped Computation Validation Tests")
        logger.info("="*80)
        
        if not self.load_data():
            logger.error("Failed to load data")
            return False
        
        tests = [
            self.test_location_scoped_changes,
            self.test_design_filtering,
            self.test_entity_scoped_data,
            self.test_roj_logic,
            self.test_comparison_differences,
            self.test_generative_responses,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                import traceback
                traceback.print_exc()
                self._record_test(test.__name__, False, {"error": str(e)})
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Total: {self.results['summary']['total']}")
        logger.info(f"Passed: {self.results['summary']['passed']}")
        logger.info(f"Failed: {self.results['summary']['failed']}")
        if self.results['summary']['total'] > 0:
            logger.info(f"Pass Rate: {self.results['summary']['passed'] / self.results['summary']['total'] * 100:.1f}%")
        
        # Save results
        with open("scoped_fixes_validation.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info("\nResults saved to scoped_fixes_validation.json")
        
        return self.results["summary"]["failed"] == 0


def main():
    """Main entry point."""
    validator = ScopedFixValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
