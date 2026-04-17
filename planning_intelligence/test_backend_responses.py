#!/usr/bin/env python3
"""
Backend Response Testing Script
Tests all 46 prompts against the backend endpoints to verify correct responses.
"""

import requests
import json
import time
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:7071"  # Azure Functions local emulator
ENDPOINTS = {
    "health": "/api/health",
    "forecast": "/api/forecast",
    "risk": "/api/risk",
    "change": "/api/change",
    "schedule": "/api/schedule",
    "entity": "/api/entity",
    "comparison": "/api/comparison",
    "impact": "/api/impact",
    "general": "/api/explain"
}

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


class BackendResponseTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        self.session = requests.Session()
        self.session.timeout = 120  # 120 seconds - matches Ollama and Azure OpenAI timeouts

    def test_prompt(self, prompt: str, expected_category: str) -> Dict[str, Any]:
        """Test a single prompt against the backend."""
        try:
            # Use the general explain endpoint for all prompts
            url = f"{self.base_url}{ENDPOINTS['general']}"
            
            payload = {
                "question": prompt,
                "context": {}
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract classification from response
            classification = data.get("classification", "unknown")
            
            # Check if classification matches expected
            passed = classification == expected_category
            
            result = {
                "prompt": prompt,
                "expected": expected_category,
                "got": classification,
                "passed": passed,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "has_answer": "answer" in data,
                "error": None
            }
            
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            return result
            
        except requests.exceptions.Timeout:
            self.results["errors"] += 1
            return {
                "prompt": prompt,
                "expected": expected_category,
                "got": "timeout",
                "passed": False,
                "status_code": None,
                "response_time": None,
                "has_answer": False,
                "error": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            self.results["errors"] += 1
            return {
                "prompt": prompt,
                "expected": expected_category,
                "got": "connection_error",
                "passed": False,
                "status_code": None,
                "response_time": None,
                "has_answer": False,
                "error": "Connection error - is the backend running?"
            }
        except Exception as e:
            self.results["errors"] += 1
            return {
                "prompt": prompt,
                "expected": expected_category,
                "got": "error",
                "passed": False,
                "status_code": None,
                "response_time": None,
                "has_answer": False,
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests and display results."""
        print("\n" + "="*80)
        print("BACKEND RESPONSE TESTING")
        print("="*80)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to test: {total_tests}")
        print(f"Backend URL: {self.base_url}")
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
                response_time = f"{result['response_time']:.2f}s" if result['response_time'] else "N/A"
                
                print(f"{status} '{prompt}'")
                print(f"   → Expected: {result['expected']}, Got: {result['got']}, Time: {response_time}")
                
                if result["error"]:
                    print(f"   → Error: {result['error']}")
                
                if result["passed"]:
                    category_passed += 1
                else:
                    category_failed += 1
                
                # Small delay between requests
                time.sleep(0.1)
            
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
                print(f"  Average: {avg_time:.3f}s")
                print(f"  Min: {min_time:.3f}s")
                print(f"  Max: {max_time:.3f}s")

    def export_results(self, filename: str = "backend_test_results.json") -> None:
        """Export results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    tester = BackendResponseTester()
    
    try:
        tester.run_all_tests()
        tester.print_summary()
        tester.export_results()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
