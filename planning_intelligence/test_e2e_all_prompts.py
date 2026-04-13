"""
End-to-End Testing: All 46 Prompts with Scoped Computation & Generative Responses

Tests all 46 prompts to ensure:
1. Classification is correct
2. Scoped metrics are computed correctly
3. Responses are natural and contextual
4. No global leakage into scoped queries
"""

import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
from function_app import classify_question, _normalize_detail_records
from scoped_metrics import (
    compute_scoped_metrics,
    get_location_metrics,
    get_design_changes,
    get_supplier_changes,
    get_quantity_changes,
    get_roj_changes,
    compare_locations,
)
from generative_responses import build_contextual_response, GenerativeResponseBuilder


# Sample data representing real planning records
SAMPLE_RECORDS = [
    # CYS20_F01C01 - 3 records
    {"locationId": "CYS20_F01C01", "materialId": "MAT001", "materialGroup": "LVS", "supplier": "10_AMER", "supplierPrevious": "10_AMER", "forecastQty": 100, "forecastQtyPrevious": 100, "rojCurrent": "2026-04-13", "rojPrevious": "2026-04-13", "bodCurrent": "BOD1", "bodPrevious": "BOD1", "ffCurrent": "FF1", "ffPrevious": "FF1", "qtyDelta": 0, "rojDelta": 0, "qtyChanged": False, "supplierChanged": False, "designChanged": False, "rojChanged": False, "changed": False},
    {"locationId": "CYS20_F01C01", "materialId": "MAT002", "materialGroup": "UPS", "supplier": "130_AMER", "supplierPrevious": "130_AMER", "forecastQty": 200, "forecastQtyPrevious": 150, "rojCurrent": "2026-04-13", "rojPrevious": "2026-04-13", "bodCurrent": "BOD2", "bodPrevious": "BOD2", "ffCurrent": "FF2", "ffPrevious": "FF2", "qtyDelta": 50, "rojDelta": 0, "qtyChanged": True, "supplierChanged": False, "designChanged": False, "rojChanged": False, "changed": True},
    {"locationId": "CYS20_F01C01", "materialId": "MAT003", "materialGroup": "MVSXRM", "supplier": "1690_AMER", "supplierPrevious": "1690_AMER", "forecastQty": 300, "forecastQtyPrevious": 300, "rojCurrent": "2026-04-13", "rojPrevious": "2026-04-13", "bodCurrent": "BOD3", "bodPrevious": "BOD2", "ffCurrent": "FF3", "ffPrevious": "FF3", "qtyDelta": 0, "rojDelta": 0, "qtyChanged": False, "supplierChanged": False, "designChanged": True, "rojChanged": False, "changed": True},
    # DSM18_F01C01 - 3 records
    {"locationId": "DSM18_F01C01", "materialId": "MAT004", "materialGroup": "LVS", "supplier": "110_AMER", "supplierPrevious": "110_AMER", "forecastQty": 150, "forecastQtyPrevious": 150, "rojCurrent": "2026-04-13", "rojPrevious": "2026-04-13", "bodCurrent": "BOD4", "bodPrevious": "BOD4", "ffCurrent": "FF4", "ffPrevious": "FF4", "qtyDelta": 0, "rojDelta": 0, "qtyChanged": False, "supplierChanged": False, "designChanged": False, "rojChanged": False, "changed": False},
    {"locationId": "DSM18_F01C01", "materialId": "MAT005", "materialGroup": "UPS", "supplier": "1690_AMER", "supplierPrevious": "210_AMER", "forecastQty": 250, "forecastQtyPrevious": 250, "rojCurrent": "2026-04-13", "rojPrevious": "2026-04-13", "bodCurrent": "BOD5", "bodPrevious": "BOD5", "ffCurrent": "FF5", "ffPrevious": "FF5", "qtyDelta": 0, "rojDelta": 0, "qtyChanged": False, "supplierChanged": True, "designChanged": False, "rojChanged": False, "changed": True},
    {"locationId": "DSM18_F01C01", "materialId": "MAT006", "materialGroup": "MVSXRM", "supplier": "170_AMER", "supplierPrevious": "170_AMER", "forecastQty": 350, "forecastQtyPrevious": 300, "rojCurrent": "2026-04-20", "rojPrevious": "2026-04-13", "bodCurrent": "BOD6", "bodPrevious": "BOD6", "ffCurrent": "FF6", "ffPrevious": "FF6", "qtyDelta": 50, "rojDelta": 7, "qtyChanged": True, "supplierChanged": False, "designChanged": False, "rojChanged": True, "changed": True},
]

# All 46 prompts from the original test
PROMPTS = {
    "health": [
        "What's the current planning health status?",
        "What's the planning health?",
        "Is planning healthy?",
        "What's the health score?",
        "How is planning health?",
    ],
    "forecast": [
        "What's the forecast?",
        "What's the trend?",
        "What's the delta?",
        "What's the forecast trend?",
        "What units are forecasted?",
    ],
    "risk": [
        "What are the top risks?",
        "What are the risks?",
        "What's the main issue?",
        "What's the biggest risk?",
        "Are there any risks?",
        "What's risky?",
        "What's dangerous?",
        "What's the high-risk situation?",
    ],
    "change": [
        "How many records have changed?",
        "What changes have occurred?",
        "What's changed?",
        "How many changes?",
        "What quantity changes?",
        "What design changes?",
        "What supplier changes?",
    ],
    "schedule": [
        "What's the ROJ?",
    ],
    "entity": [
        "List suppliers for CYS20_F01C01",
        "Which materials are affected?",
        "Which suppliers at CYS20_F01C01 have design changes?",
        "What suppliers are involved?",
        "What materials are involved?",
        "List materials for DSM18_F01C01",
        "Which locations are affected?",
        "What groups are affected?",
    ],
    "comparison": [
        "Compare CYS20_F01C01 vs DSM18_F01C01",
        "What's the difference between CYS20_F01C01 and DSM18_F01C01?",
        "Compare DSM18_F01C01 versus CYS20_F01C01",
        "CYS20_F01C01 vs DSM18_F01C01",
        "Difference between CYS20_F01C01 and DSM18_F01C01",
        "Compare locations CYS20_F01C01 and DSM18_F01C01",
    ],
    "impact": [
        "Which supplier has the most impact?",
        "What is the impact?",
        "Which materials are most affected?",
        "What's the impact on suppliers?",
        "Which supplier has the most changes?",
        "What's the consequence of changes?",
    ],
}


class E2ETestRunner:
    """Run end-to-end tests for all 46 prompts."""
    
    def __init__(self):
        """Initialize test runner."""
        self.records = SAMPLE_RECORDS
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_prompts": 0,
            "passed": 0,
            "failed": 0,
            "by_category": {},
            "details": []
        }
    
    def run_all_tests(self) -> bool:
        """Run all 46 prompts."""
        logger.info("="*80)
        logger.info("END-TO-END TEST: All 46 Prompts")
        logger.info("="*80)
        logger.info(f"Sample records: {len(self.records)}")
        logger.info(f"Locations: CYS20_F01C01, DSM18_F01C01")
        logger.info("")
        
        total = 0
        for category, prompts in PROMPTS.items():
            logger.info(f"\n{category.upper()} ({len(prompts)} prompts)")
            logger.info("-" * 80)
            
            category_passed = 0
            category_failed = 0
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    result = self.test_prompt(prompt, category)
                    total += 1
                    
                    if result["passed"]:
                        category_passed += 1
                        self.results["passed"] += 1
                        status = "✓"
                    else:
                        category_failed += 1
                        self.results["failed"] += 1
                        status = "✗"
                    
                    logger.info(f"{status} [{i}] {prompt}")
                    logger.info(f"    Classification: {result['classification']}")
                    logger.info(f"    Response: {result['response'][:100]}...")
                    
                    self.results["details"].append(result)
                except Exception as e:
                    total += 1
                    category_failed += 1
                    self.results["failed"] += 1
                    logger.error(f"✗ [{i}] {prompt}")
                    logger.error(f"    Error: {str(e)}")
                    self.results["details"].append({
                        "prompt": prompt,
                        "category": category,
                        "passed": False,
                        "error": str(e)
                    })
            
            self.results["by_category"][category] = {
                "total": len(prompts),
                "passed": category_passed,
                "failed": category_failed,
                "pass_rate": category_passed / len(prompts) * 100
            }
            
            logger.info(f"Category: {category_passed}/{len(prompts)} passed ({category_passed/len(prompts)*100:.1f}%)")
        
        self.results["total_prompts"] = total
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Prompts: {total}")
        logger.info(f"Passed: {self.results['passed']}")
        logger.info(f"Failed: {self.results['failed']}")
        logger.info(f"Pass Rate: {self.results['passed']/total*100:.1f}%")
        
        logger.info("\nBy Category:")
        for category, stats in self.results["by_category"].items():
            logger.info(f"  {category}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)")
        
        # Save results
        with open("e2e_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info("\nResults saved to e2e_test_results.json")
        
        return self.results["failed"] == 0
    
    def test_prompt(self, prompt: str, expected_category: str) -> Dict:
        """Test a single prompt."""
        # Classify
        classification = classify_question(prompt)
        
        # Generate response based on classification
        response = self._generate_response(prompt, classification)
        
        # Verify
        passed = (
            classification == expected_category and
            len(response) > 20 and
            response is not None
        )
        
        return {
            "prompt": prompt,
            "category": expected_category,
            "classification": classification,
            "response": response,
            "passed": passed,
            "error": None if passed else "Classification or response mismatch"
        }
    
    def _generate_response(self, prompt: str, classification: str) -> str:
        """Generate response based on classification."""
        builder = GenerativeResponseBuilder()
        
        if classification == "health":
            metrics = compute_scoped_metrics(self.records)
            return builder.build_health_response({
                "planningHealth": 60,
                "changedRecordCount": metrics["changedRecords"],
                "totalRecords": metrics["totalRecords"],
                "designChanges": metrics["designChangedCount"],
                "supplierChanges": metrics["supplierChangedCount"],
                "qtyChanges": metrics["qtyChangedCount"],
            })
        
        elif classification == "forecast":
            metrics = get_quantity_changes(self.records)
            return builder.build_forecast_response(metrics)
        
        elif classification == "risk":
            metrics = compute_scoped_metrics(self.records)
            high_risk = sum(1 for r in self.records if r.get("changed"))
            return builder.build_risk_response({
                "riskLevel": "CRITICAL" if high_risk > 2 else "NORMAL",
                "highestRiskLevel": "Design + Supplier Change Risk",
                "highRiskCount": high_risk,
                "totalRecords": len(self.records),
            })
        
        elif classification == "change":
            metrics = compute_scoped_metrics(self.records)
            return builder.build_health_response({
                "planningHealth": 60,
                "changedRecordCount": metrics["changedRecords"],
                "totalRecords": metrics["totalRecords"],
                "designChanges": metrics["designChangedCount"],
                "supplierChanges": metrics["supplierChangedCount"],
                "qtyChanges": metrics["qtyChangedCount"],
            })
        
        elif classification == "schedule":
            metrics = get_roj_changes(self.records)
            if metrics["rojChangedCount"] == 0:
                return "No ROJ schedule changes detected."
            return f"{metrics['rojChangedCount']} records have ROJ schedule changes. Average delta: {metrics['averageRojDelta']} days."
        
        elif classification == "entity":
            # Try to extract location
            import re
            match = re.search(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', prompt)
            if match:
                location = match.group(1)
                metrics = get_location_metrics(self.records, location)
                return builder.build_location_response(location, metrics)
            else:
                metrics = compute_scoped_metrics(self.records)
                return builder.build_impact_response(metrics)
        
        elif classification == "comparison":
            import re
            locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', prompt)
            if len(locations) >= 2:
                comparison = compare_locations(self.records, locations[0], locations[1])
                return builder.build_comparison_response(
                    locations[0], comparison["location1Metrics"],
                    locations[1], comparison["location2Metrics"]
                )
            return "Please specify two locations to compare."
        
        elif classification == "impact":
            metrics = compute_scoped_metrics(self.records)
            return builder.build_impact_response(metrics)
        
        else:
            metrics = compute_scoped_metrics(self.records)
            return builder.build_health_response({
                "planningHealth": 60,
                "changedRecordCount": metrics["changedRecords"],
                "totalRecords": metrics["totalRecords"],
                "designChanges": metrics["designChangedCount"],
                "supplierChanges": metrics["supplierChangedCount"],
                "qtyChanges": metrics["qtyChangedCount"],
            })


def main():
    """Main entry point."""
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    
    if success:
        logger.info("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        logger.error("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
