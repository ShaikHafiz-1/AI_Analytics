#!/usr/bin/env python3
"""
Test all 44 prompts systematically.
This script helps validate that all query types work correctly.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:7071/api"
EXPLAIN_ENDPOINT = f"{BASE_URL}/explain"

# Test data
LOCATIONS = ["AVC11_F01C01", "LOC001", "CMH02_F01C01"]
MATERIALS = ["MAT-001", "MAT-002", "MAT-003"]
MATERIAL_GROUPS = ["PUMP", "VALVE"]
SUPPLIERS = ["SUP-A", "SUP-B"]

# All 44 prompts organized by category
PROMPTS = {
    "Supplier Queries": [
        "List suppliers for AVC11_F01C01",
        "List suppliers for LOC001",
        "Which suppliers at AVC11_F01C01 have design changes?",
        "Which supplier has the most impact?",
    ],
    "Comparison Queries": [
        "Compare LOC001 vs LOC002",
        "Compare AVC11_F01C01 vs LOC001",
        "Compare PUMP vs VALVE",
    ],
    "Record Detail Queries": [
        "What changed for MAT-001?",
        "What changed for MAT-001 at AVC11_F01C01?",
        "Show current vs previous for MAT-001",
    ],
    "Root Cause Queries": [
        "Why is AVC11_F01C01 risky?",
        "Why is LOC001 not risky?",
        "Why is planning health critical?",
        "What is driving the risk?",
    ],
    "Traceability Queries": [
        "Show top contributing records",
        "Which records have the most impact?",
        "Show records with design changes",
        "Which records are highest risk?",
    ],
    "Location Queries": [
        "Which locations have the most changes?",
        "Which locations need immediate attention?",
        "What changed at LOC001?",
        "Which locations are change hotspots?",
    ],
    "Material Group Queries": [
        "Which material groups changed the most?",
        "What changed in PUMP?",
        "Which material groups have design changes?",
        "Which material groups are most impacted?",
    ],
    "Forecast/Demand Queries": [
        "Why did forecast increase by +50,980?",
        "Where are we seeing new demand surges?",
        "Is this demand-driven or design-driven?",
        "Show forecast trends",
    ],
    "Design/BOD Queries": [
        "Which materials have BOD changes?",
        "Which materials have Form Factor changes?",
        "Any design changes at AVC11_F01C01?",
        "Which supplier has the most design changes?",
    ],
    "Schedule/ROJ Queries": [
        "Which locations have ROJ delays?",
        "Which supplier is failing to meet ROJ dates?",
        "Are there ROJ delays at LOC001?",
        "Show schedule changes",
    ],
    "Health/Status Queries": [
        "What is the current planning health?",
        "Why is planning health at 37/100?",
        "What is the risk level?",
        "Show KPI summary",
    ],
    "Action/Recommendation Queries": [
        "What are the top planner actions?",
        "What should be done for AVC11_F01C01?",
    ],
}


def test_prompt(prompt: str, context: dict = None) -> dict:
    """Test a single prompt and return results."""
    start_time = time.time()
    
    try:
        payload = {
            "question": prompt,
            "context": context,
        }
        
        response = requests.post(EXPLAIN_ENDPOINT, json=payload, timeout=10)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            
            # Determine if response is meaningful
            is_meaningful = (
                len(answer) > 50 and
                "No analysis available" not in answer and
                "Could not" not in answer and
                "error" not in answer.lower()
            )
            
            return {
                "status": "PASS" if is_meaningful else "FAIL",
                "time_ms": round(elapsed_time * 1000, 1),
                "answer_length": len(answer),
                "query_type": data.get("queryType", "unknown"),
                "answer_mode": data.get("answerMode", "unknown"),
                "error": None,
            }
        else:
            return {
                "status": "FAIL",
                "time_ms": round(elapsed_time * 1000, 1),
                "answer_length": 0,
                "query_type": "unknown",
                "answer_mode": "unknown",
                "error": f"HTTP {response.status_code}",
            }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "status": "FAIL",
            "time_ms": round(elapsed_time * 1000, 1),
            "answer_length": 0,
            "query_type": "unknown",
            "answer_mode": "unknown",
            "error": str(e),
        }


def run_all_tests(context: dict = None) -> dict:
    """Run all 44 prompts and collect results."""
    results = {}
    total_prompts = 0
    passed_prompts = 0
    
    print("\n" + "=" * 80)
    print("TESTING ALL 44 PROMPTS")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for category, prompts in PROMPTS.items():
        print(f"\n📋 {category} ({len(prompts)} prompts)")
        print("-" * 80)
        
        results[category] = {}
        
        for idx, prompt in enumerate(prompts, 1):
            total_prompts += 1
            
            # Test the prompt
            result = test_prompt(prompt, context)
            results[category][prompt] = result
            
            # Print result
            status_icon = "✓" if result["status"] == "PASS" else "✗"
            print(f"{status_icon} [{idx}] {prompt[:60]:<60} | {result['status']:<4} | {result['time_ms']:>6}ms")
            
            if result["error"]:
                print(f"    Error: {result['error']}")
            
            if result["status"] == "PASS":
                passed_prompts += 1
            
            # Small delay between requests
            time.sleep(0.1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total prompts: {total_prompts}")
    print(f"Passed: {passed_prompts}")
    print(f"Failed: {total_prompts - passed_prompts}")
    pass_rate = round(passed_prompts / total_prompts * 100, 1) if total_prompts > 0 else 0
    print(f"Pass rate: {pass_rate}%")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print category summary
    print("\n" + "-" * 80)
    print("CATEGORY SUMMARY")
    print("-" * 80)
    for category, prompts_dict in results.items():
        cat_passed = sum(1 for r in prompts_dict.values() if r["status"] == "PASS")
        cat_total = len(prompts_dict)
        cat_rate = round(cat_passed / cat_total * 100, 1) if cat_total > 0 else 0
        print(f"{category:<35} {cat_passed:>2}/{cat_total:<2} ({cat_rate:>5.1f}%)")
    
    return {
        "total": total_prompts,
        "passed": passed_prompts,
        "failed": total_prompts - passed_prompts,
        "pass_rate": pass_rate,
        "results": results,
    }


def print_failures(results: dict):
    """Print detailed information about failed prompts."""
    print("\n" + "=" * 80)
    print("FAILED PROMPTS DETAILS")
    print("=" * 80)
    
    failed_count = 0
    for category, prompts_dict in results["results"].items():
        for prompt, result in prompts_dict.items():
            if result["status"] == "FAIL":
                failed_count += 1
                print(f"\n❌ [{failed_count}] {prompt}")
                print(f"   Query Type: {result['query_type']}")
                print(f"   Answer Mode: {result['answer_mode']}")
                print(f"   Time: {result['time_ms']}ms")
                if result["error"]:
                    print(f"   Error: {result['error']}")


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive test of all 44 prompts...")
    print("Make sure backend is running on http://localhost:7071")
    
    # Run tests
    results = run_all_tests()
    
    # Print failures
    if results["failed"] > 0:
        print_failures(results)
    
    # Save results to file
    with open("test_results_44_prompts.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to test_results_44_prompts.json")
    
    # Exit with appropriate code
    exit(0 if results["pass_rate"] >= 90 else 1)
