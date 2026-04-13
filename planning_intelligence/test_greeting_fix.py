"""
Test greeting detection and response generation.
Verifies that simple greetings like "Hi" and "Hello" are properly classified
and routed to ChatGPT for natural conversational responses.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from function_app import classify_question, generate_greeting_answer


def test_greeting_classification():
    """Test that greetings are correctly classified"""
    test_cases = [
        ("Hi", "greeting"),
        ("Hello", "greeting"),
        ("Hey", "greeting"),
        ("Greetings", "greeting"),
        ("Good morning", "greeting"),
        ("Good afternoon", "greeting"),
        ("Good evening", "greeting"),
        ("Hi there", "greeting"),
        ("Hello friend", "greeting"),
        # Non-greetings should not be classified as greeting
        ("Hi, what's the health status?", "health"),  # Too long, has other keywords
        ("Hello, compare CYS20 vs DSM18", "comparison"),  # Has comparison keywords
        ("What is the health?", "health"),
        ("Show me the forecast", "forecast"),
    ]
    
    print("Testing greeting classification...")
    for question, expected_type in test_cases:
        result = classify_question(question)
        status = "✓" if result == expected_type else "✗"
        print(f"{status} '{question}' → {result} (expected: {expected_type})")
        assert result == expected_type, f"Failed for '{question}': got {result}, expected {expected_type}"
    
    print("\n✓ All greeting classification tests passed!")


def test_greeting_answer_generation():
    """Test that greeting answers are generated correctly"""
    # Mock context
    context = {
        "planningHealth": 37,
        "totalRecords": 13148,
        "changedRecords": 2951,
        "changeRate": 22.4
    }
    
    # Mock detail records
    detail_records = [
        {"changed": True} for _ in range(2951)
    ] + [
        {"changed": False} for _ in range(13148 - 2951)
    ]
    
    print("\nTesting greeting answer generation...")
    
    # Test various greetings
    greetings = ["Hi", "Hello", "Hey", "Good morning"]
    
    for greeting in greetings:
        try:
            result = generate_greeting_answer(detail_records, context, greeting)
            answer = result.get("answer", "")
            metrics = result.get("supportingMetrics", {})
            
            # Verify response structure
            assert "answer" in result, f"Missing 'answer' in response for '{greeting}'"
            assert "supportingMetrics" in result, f"Missing 'supportingMetrics' in response for '{greeting}'"
            assert len(answer) > 0, f"Empty answer for '{greeting}'"
            
            # Verify metrics
            assert metrics.get("planningHealth") == 37, f"Wrong health score for '{greeting}'"
            assert metrics.get("changedRecordCount") == 2951, f"Wrong changed count for '{greeting}'"
            assert metrics.get("totalRecords") == 13148, f"Wrong total records for '{greeting}'"
            
            print(f"✓ '{greeting}' → Generated response ({len(answer)} chars)")
            print(f"  Answer preview: {answer[:80]}...")
            
        except Exception as e:
            print(f"✗ '{greeting}' → Error: {str(e)}")
            raise
    
    print("\n✓ All greeting answer generation tests passed!")


if __name__ == "__main__":
    test_greeting_classification()
    test_greeting_answer_generation()
    print("\n" + "="*60)
    print("✓ ALL GREETING TESTS PASSED!")
    print("="*60)
