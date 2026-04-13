#!/usr/bin/env python3
"""
Local Backend Response Testing Script
Tests all 46 prompts by directly calling the backend functions without HTTP.
"""

import sys
import time
from typing import Dict, List, Any, Tuple

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


class LocalBackendTester:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        self.classify_question = None
        self._load_classifier()

    def _load_classifier(self) -> None:
        """Load the classify_question function from function_app."""
        try:
            from function_app import classify_question
            self.classify_question = classify_question
            print("✓ Successfully loaded classify_question from function_app")
        except ImportError as e:
            print(f"✗ Failed to import classify_question: {e}")
            print("  Make sure you're running this from the planning_intelligence directory")
            sys.exit(1)

    def test_prompt(self, prompt: str, expected_category: str) -> Dict[str, Any]:
        """Test a single prompt by calling classify_question directly."""
        try:
            start_time = time.time()
            classification = self.classify_question(prompt)
            response_time = time.time() - start_time
            
            passed = classification == expected_category
            
            result = {
                "prompt": prompt,
                "expected": expected_category,
                "got": classification,
                "passed": passed,
                "response_time": response_time,
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
                "response_time": None,
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests and display results."""
        print("\n" + "="*80)
        print("LOCAL BACKEND RESPONSE TESTING")
        print("="*80)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to test: {total_tests}")
        print("\nStarting tests...\n")
        
        # Test each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{category.upper()} QUESTIONS ({len(prompts)} prompts):")
            print("-" * 80)
            
            category_passed = 0
            category_failed = 0
            
            for prompt in prompts:
                result = self.test_prompt(prompt, category)
                self.results["details"].append(result)
                
                status = "✓" if result["passed"] else "✗"
                response_time = f"{result['response_time']*1000:.2f}ms" if result['response_time'] else "N/A"
                
                print(f"{status} '{prompt}'")
                print(f"   → Expected: {result['expected']}, Got: {result['got']}, Time: {response_time}")
                
                if result["error"]:
                    print(f"   → Error: {result['error']}")
                
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
        
        # Statistics
        if self.results["details"]:
            response_times = [d["response_time"] for d in self.results["details"] if d["response_time"]]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                print(f"\nResponse Time Statistics:")
                print(f"  Average: {avg_time*1000:.2f}ms")
                print(f"  Min: {min_time*1000:.2f}ms")
                print(f"  Max: {max_time*1000:.2f}ms")


def main():
    """Main entry point."""
    tester = LocalBackendTester()
    
    try:
        tester.run_all_tests()
        tester.print_summary()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
