#!/usr/bin/env python3
"""
Simple test script to verify Copilot question classification and answer generation.
Run from planning_intelligence directory: python test_prompts_simple.py
"""

import sys
import json

# Add parent directory to path so we can import modules
sys.path.insert(0, '.')

# Test data - sample records
SAMPLE_RECORDS = [
    {
        "locationId": "CYS20_F01C01",
        "materialId": "MAT001",
        "materialGroup": "UPS",
        "supplier": "Supplier A",
        "forecastQty": 100,
        "forecastQtyPrevious": 90,
        "rojCurrent": "2024-01-15",
        "rojPrevious": "2024-01-10",
        "bodCurrent": "v1",
        "bodPrevious": "v0",
        "ffCurrent": "FF1",
        "ffPrevious": "FF0",
        "qtyDelta": 10,
        "rojDelta": 5,
        "qtyChanged": True,
        "supplierChanged": False,
        "designChanged": True,
        "rojChanged": True,
        "changed": True,
        "changeType": "Design"
    },
    {
        "locationId": "CYS20_F01C01",
        "materialId": "MAT002",
        "materialGroup": "POWER",
        "supplier": "Supplier B",
        "forecastQty": 200,
        "forecastQtyPrevious": 200,
        "rojCurrent": "2024-01-20",
        "rojPrevious": "2024-01-20",
        "bodCurrent": "v1",
        "bodPrevious": "v1",
        "ffCurrent": "FF1",
        "ffPrevious": "FF1",
        "qtyDelta": 0,
        "rojDelta": 0,
        "qtyChanged": False,
        "supplierChanged": False,
        "designChanged": False,
        "rojChanged": False,
        "changed": False,
        "changeType": "Unchanged"
    },
    {
        "locationId": "DSM18_F01C01",
        "materialId": "MAT003",
        "materialGroup": "COOLING",
        "supplier": "Supplier C",
        "forecastQty": 150,
        "forecastQtyPrevious": 140,
        "rojCurrent": "2024-02-01",
        "rojPrevious": "2024-01-25",
        "bodCurrent": "v2",
        "bodPrevious": "v1",
        "ffCurrent": "FF2",
        "ffPrevious": "FF1",
        "qtyDelta": 10,
        "rojDelta": 7,
        "qtyChanged": True,
        "supplierChanged": True,
        "designChanged": True,
        "rojChanged": True,
        "changed": True,
        "changeType": "Design"
    }
]

SAMPLE_CONTEXT = {
    "planningHealth": 37,
    "status": "Critical",
    "riskSummary": {
        "level": "High",
        "designChangedCount": 1926,
        "supplierChangedCount": 1499,
        "quantityChangedCount": 4725
    }
}

# Test prompts organized by category
TEST_PROMPTS = {
    "health": [
        "What's the current planning health status?",
        "What's the planning health?",
    ],
    "entity": [
        "List suppliers for CYS20_F01C01",
        "Which materials are affected?",
        "Which suppliers at CYS20_F01C01 have design changes?",
    ],
    "comparison": [
        "Compare CYS20_F01C01 vs DSM18_F01C01",
        "What's the difference between CYS20_F01C01 and DSM18_F01C01?",
    ],
    "impact": [
        "Which supplier has the most impact?",
        "What is the impact?",
    ],
    "risk": [
        "What are the top risks?",
        "What are the risks?",
    ],
    "change": [
        "How many records have changed?",
        "What changes have occurred?",
    ]
}

def test_classification():
    """Test question classification"""
    print("\n" + "="*80)
    print("TESTING QUESTION CLASSIFICATION")
    print("="*80)
    
    try:
        from function_app import classify_question
    except ImportError as e:
        print(f"ERROR: Could not import classify_question: {e}")
        return False
    
    all_pass = True
    for category, prompts in TEST_PROMPTS.items():
        print(f"\n{category.upper()} QUESTIONS:")
        for prompt in prompts:
            result = classify_question(prompt)
            status = "✓" if result == category else "✗"
            if result != category:
                all_pass = False
            print(f"  {status} '{prompt}' → {result} (expected: {category})")
    
    return all_pass

def test_answer_generation():
    """Test answer generation for each question type"""
    print("\n" + "="*80)
    print("TESTING ANSWER GENERATION")
    print("="*80)
    
    try:
        from function_app import (
            classify_question,
            generate_health_answer,
            generate_entity_answer,
            generate_comparison_answer,
            generate_impact_answer,
            generate_risk_answer,
            generate_change_answer
        )
    except ImportError as e:
        print(f"ERROR: Could not import answer generators: {e}")
        return False
    
    all_pass = True
    
    # Test entity questions
    print("\nENTITY QUESTIONS:")
    entity_prompts = [
        "List suppliers for CYS20_F01C01",
        "Which materials are affected?",
    ]
    
    for prompt in entity_prompts:
        q_type = classify_question(prompt)
        print(f"\n  Question: '{prompt}'")
        print(f"  Classification: {q_type}")
        
        if q_type == "entity":
            try:
                result = generate_entity_answer(SAMPLE_RECORDS, SAMPLE_CONTEXT, prompt)
                answer = result.get("answer", "")
                print(f"  Answer: {answer[:80]}...")
                
                # Check if answer is generic health answer
                if "Planning health is" in answer:
                    print(f"  ✗ FAIL: Returned generic health answer instead of entity answer")
                    all_pass = False
                elif "Location" in answer or "Top affected" in answer or "Suppliers:" in answer:
                    print(f"  ✓ PASS: Returned entity-specific answer")
                else:
                    print(f"  ? UNKNOWN: Answer doesn't match expected patterns")
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                import traceback
                traceback.print_exc()
                all_pass = False
        else:
            print(f"  ✗ FAIL: Classified as '{q_type}' instead of 'entity'")
            all_pass = False
    
    # Test comparison questions
    print("\n\nCOMPARISON QUESTIONS:")
    comparison_prompts = [
        "Compare CYS20_F01C01 vs DSM18_F01C01",
    ]
    
    for prompt in comparison_prompts:
        q_type = classify_question(prompt)
        print(f"\n  Question: '{prompt}'")
        print(f"  Classification: {q_type}")
        
        if q_type == "comparison":
            try:
                result = generate_comparison_answer(SAMPLE_RECORDS, SAMPLE_CONTEXT, prompt)
                answer = result.get("answer", "")
                print(f"  Answer: {answer[:80]}...")
                
                if "Comparison:" in answer or "vs" in answer:
                    print(f"  ✓ PASS: Returned comparison answer")
                else:
                    print(f"  ? UNKNOWN: Answer doesn't match expected patterns")
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                import traceback
                traceback.print_exc()
                all_pass = False
        else:
            print(f"  ✗ FAIL: Classified as '{q_type}' instead of 'comparison'")
            all_pass = False
    
    # Test impact questions
    print("\n\nIMPACT QUESTIONS:")
    impact_prompts = [
        "Which supplier has the most impact?",
    ]
    
    for prompt in impact_prompts:
        q_type = classify_question(prompt)
        print(f"\n  Question: '{prompt}'")
        print(f"  Classification: {q_type}")
        
        if q_type == "impact":
            try:
                result = generate_impact_answer(SAMPLE_RECORDS, SAMPLE_CONTEXT)
                answer = result.get("answer", "")
                print(f"  Answer: {answer[:80]}...")
                
                if "Impact" in answer or "Top suppliers" in answer or "Top materials" in answer:
                    print(f"  ✓ PASS: Returned impact answer")
                else:
                    print(f"  ? UNKNOWN: Answer doesn't match expected patterns")
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                import traceback
                traceback.print_exc()
                all_pass = False
        else:
            print(f"  ✗ FAIL: Classified as '{q_type}' instead of 'impact'")
            all_pass = False
    
    return all_pass

if __name__ == "__main__":
    print("COPILOT DIAGNOSTIC TEST")
    print("Testing question classification and answer generation")
    
    classification_pass = test_classification()
    answer_pass = test_answer_generation()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Classification: {'✓ PASS' if classification_pass else '✗ FAIL'}")
    print(f"Answer Generation: {'✓ PASS' if answer_pass else '✗ FAIL'}")
    
    if classification_pass and answer_pass:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. See details above.")
        sys.exit(1)
