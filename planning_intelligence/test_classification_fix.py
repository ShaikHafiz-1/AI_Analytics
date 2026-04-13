#!/usr/bin/env python3
"""
Test script to verify question classification fix.
Run from planning_intelligence directory: python test_classification_fix.py
"""

import sys
sys.path.insert(0, '.')

from function_app import classify_question

# Test prompts from the 40+ prompt test guide
TEST_CASES = {
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

def main():
    print("\n" + "="*80)
    print("QUESTION CLASSIFICATION TEST")
    print("="*80)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for expected_type, prompts in TEST_CASES.items():
        print(f"\n{expected_type.upper()} QUESTIONS ({len(prompts)} prompts):")
        print("-" * 80)
        
        for prompt in prompts:
            total_tests += 1
            result = classify_question(prompt)
            status = "✓" if result == expected_type else "✗"
            
            if result == expected_type:
                passed_tests += 1
                print(f"  {status} '{prompt}'")
                print(f"     → {result}")
            else:
                failed_tests.append((prompt, expected_type, result))
                print(f"  {status} '{prompt}'")
                print(f"     → {result} (expected: {expected_type})")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Failed: {len(failed_tests)} ✗")
    print(f"Pass Rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests:
        print("\nFAILED TESTS:")
        for prompt, expected, actual in failed_tests:
            print(f"  • '{prompt}'")
            print(f"    Expected: {expected}, Got: {actual}")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
