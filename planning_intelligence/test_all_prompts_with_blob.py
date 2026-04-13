#!/usr/bin/env python3
"""
Test All 46 Prompts with Real Blob Data
Loads actual data from Azure Blob Storage and tests all prompts.
Similar to run_daily_refresh.py but focused on testing responses.
"""

import logging
import os
import sys
import json

# Allow running standalone
sys.path.insert(0, os.path.dirname(__file__))

# Load local.settings.json if running standalone
def _load_local_settings():
    """Load environment variables from local.settings.json for local development."""
    settings_path = os.path.join(os.path.dirname(__file__), "local.settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
                # Load Values section into environment
                for key, value in settings.get("Values", {}).items():
                    if key not in os.environ:
                        os.environ[key] = value
                logging.info(f"Loaded environment variables from {settings_path}")
        except Exception as e:
            logging.warning(f"Could not load local.settings.json: {e}")

# Load settings before importing modules
_load_local_settings()

from blob_loader import load_current_previous_from_blob
from normalizer import normalize_rows
from filters import filter_records
from comparator import compare_records
from response_builder import build_response
from function_app import classify_question

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Test prompts organized by category
TEST_PROMPTS = {
    "health": [
        "What's the current planning health status?",
        "What's the planning health?",
        "Is planning healthy?",
        "What's the health score?",
        "How is planning health?"
    ],
    "forecast": [
        "What's the forecast?",
        "What's the trend?",
        "What's the delta?",
        "What's the forecast trend?",
        "What units are forecasted?"
    ],
    "risk": [
        "What are the top risks?",
        "What are the risks?",
        "What's the main issue?",
        "What's the biggest risk?",
        "Are there any risks?",
        "What's risky?",
        "What's dangerous?",
        "What's the high-risk situation?"
    ],
    "change": [
        "How many records have changed?",
        "What changes have occurred?",
        "What's changed?",
        "How many changes?",
        "What quantity changes?",
        "What design changes?",
        "What supplier changes?"
    ],
    "schedule": [
        "What's the ROJ?"
    ],
    "entity": [
        "List suppliers for CYS20_F01C01",
        "Which materials are affected?",
        "Which suppliers at CYS20_F01C01 have design changes?",
        "What suppliers are involved?",
        "What materials are involved?",
        "List materials for DSM18_F01C01",
        "Which locations are affected?",
        "What groups are affected?"
    ],
    "comparison": [
        "Compare CYS20_F01C01 vs DSM18_F01C01",
        "What's the difference between CYS20_F01C01 and DSM18_F01C01?",
        "Compare DSM18_F01C01 versus CYS20_F01C01",
        "CYS20_F01C01 vs DSM18_F01C01",
        "Difference between CYS20_F01C01 and DSM18_F01C01",
        "Compare locations CYS20_F01C01 and DSM18_F01C01"
    ],
    "impact": [
        "Which supplier has the most impact?",
        "What is the impact?",
        "Which materials are most affected?",
        "What's the impact on suppliers?",
        "Which supplier has the most changes?",
        "What's the consequence of changes?"
    ]
}


class BlobDataPromptTester:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        self.detail_records = []
        self.context = {}
        self._load_blob_data()

    def _load_blob_data(self) -> None:
        """Load real data from Azure Blob Storage."""
        logger.info("Loading data from Azure Blob Storage...")
        
        try:
            # Step 1: Load from blob
            current_rows, previous_rows = load_current_previous_from_blob()
            logger.info(f"✓ Loaded {len(current_rows)} current rows, {len(previous_rows)} previous rows")
            
            # Step 2: Normalize
            current_records = normalize_rows(current_rows, is_current=True)
            previous_records = normalize_rows(previous_rows, is_current=False)
            logger.info(f"✓ Normalized records")
            
            # Step 3: Compare
            compared = compare_records(current_records, previous_records)
            logger.info(f"✓ Compared {len(compared)} records")
            
            # Step 4: Build response (this creates the context)
            response = build_response(compared, [], None, None, data_mode="cached")
            logger.info(f"✓ Built response with context")
            
            # Store for testing
            self.detail_records = compared
            self.context = response
            
            logger.info(f"✓ Ready to test with {len(self.detail_records)} detail records")
            
        except Exception as e:
            logger.error(f"✗ Failed to load blob data: {e}")
            raise

    def test_classification(self, prompt: str, expected_category: str) -> dict:
        """Test question classification."""
        try:
            classification = classify_question(prompt)
            passed = classification == expected_category
            
            result = {
                "prompt": prompt,
                "expected": expected_category,
                "got": classification,
                "passed": passed,
                "error": None
            }
            
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            return result
            
        except Exception as e:
            self.results["errors"] += 1
            return {
                "prompt": prompt,
                "expected": expected_category,
                "got": "error",
                "passed": False,
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests."""
        print("\n" + "="*80)
        print("TESTING ALL 46 PROMPTS WITH REAL BLOB DATA")
        print("="*80)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to test: {total_tests}")
        print(f"Detail records loaded: {len(self.detail_records)}")
        print(f"Context keys: {list(self.context.keys())}\n")
        
        # Test each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{category.upper()} QUESTIONS ({len(prompts)} prompts):")
            print("-" * 80)
            
            category_passed = 0
            category_failed = 0
            
            for idx, prompt in enumerate(prompts, 1):
                result = self.test_classification(prompt, category)
                self.results["details"].append(result)
                
                status = "✓" if result["passed"] else "✗"
                
                print(f"{status} [{idx}] '{prompt}'")
                print(f"    → Expected: {result['expected']}, Got: {result['got']}")
                
                if result["error"]:
                    print(f"    → Error: {result['error']}")
                
                if result["passed"]:
                    category_passed += 1
                else:
                    category_failed += 1
            
            category_total = category_passed + category_failed
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"\nCategory Result: {category_passed}/{category_total} passed ({category_rate:.1f}%)")

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        total = self.results["passed"] + self.results["failed"] + self.results["errors"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        print(f"Errors: {self.results['errors']} ⚠")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Show failed tests
        if self.results["failed"] > 0:
            print(f"\nFAILED TESTS ({self.results['failed']}):")
            for detail in self.results["details"]:
                if not detail["passed"] and detail["error"] is None:
                    print(f"• '{detail['prompt']}'")
                    print(f"  Expected: {detail['expected']}, Got: {detail['got']}")
        
        # Show errors
        if self.results["errors"] > 0:
            print(f"\nERRORS ({self.results['errors']}):")
            for detail in self.results["details"]:
                if detail["error"]:
                    print(f"• '{detail['prompt']}'")
                    print(f"  Error: {detail['error']}")

    def export_results(self, filename: str = "prompt_test_results.json") -> None:
        """Export results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    try:
        tester = BlobDataPromptTester()
        tester.run_all_tests()
        tester.print_summary()
        tester.export_results()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
