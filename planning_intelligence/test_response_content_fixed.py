#!/usr/bin/env python3
"""
Response Content Review Script (Fixed)
Tests all 46 prompts and displays the actual response content generated.
Properly mocks the required context and detail_records parameters.
"""

import sys
import json
from typing import Dict, List, Any

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


def create_mock_context() -> Dict[str, Any]:
    """Create mock context data for testing."""
    return {
        "planningHealth": 75,
        "status": "Healthy",
        "totalRecords": 1000,
        "changedRecords": 150,
        "riskSummary": {
            "designChangedCount": 45,
            "supplierChangedCount": 60,
            "materialChangedCount": 30,
            "highRiskCount": 12,
            "mediumRiskCount": 35,
            "lowRiskCount": 103
        },
        "forecastData": {
            "trend": "increasing",
            "delta": 15,
            "units": 250
        },
        "locations": ["CYS20_F01C01", "DSM18_F01C01", "LOC03"],
        "suppliers": ["Supplier A", "Supplier B", "Supplier C"],
        "materials": ["Material X", "Material Y", "Material Z"]
    }


def create_mock_detail_records() -> List[Dict[str, Any]]:
    """Create mock detail records for testing."""
    records = []
    for i in range(100):
        records.append({
            "id": f"REC{i:04d}",
            "location": ["CYS20_F01C01", "DSM18_F01C01", "LOC03"][i % 3],
            "supplier": ["Supplier A", "Supplier B", "Supplier C"][i % 3],
            "material": ["Material X", "Material Y", "Material Z"][i % 3],
            "changed": i % 3 == 0,
            "changeType": "design" if i % 5 == 0 else "supplier" if i % 7 == 0 else "material",
            "riskLevel": "high" if i % 10 == 0 else "medium" if i % 5 == 0 else "low"
        })
    return records


class ResponseContentReviewer:
    def __init__(self):
        self.results = []
        self.answer_functions = {}
        self.classify_question = None
        self.mock_context = create_mock_context()
        self.mock_records = create_mock_detail_records()
        self._load_answer_functions()

    def _load_answer_functions(self) -> None:
        """Load all answer generation functions from function_app."""
        try:
            from function_app import (
                classify_question,
                generate_health_answer,
                generate_forecast_answer,
                generate_risk_answer,
                generate_change_answer,
                generate_schedule_answer,
                generate_entity_answer,
                generate_comparison_answer,
                generate_impact_answer
            )
            
            self.classify_question = classify_question
            self.answer_functions = {
                "health": generate_health_answer,
                "forecast": generate_forecast_answer,
                "risk": generate_risk_answer,
                "change": generate_change_answer,
                "schedule": generate_schedule_answer,
                "entity": generate_entity_answer,
                "comparison": generate_comparison_answer,
                "impact": generate_impact_answer
            }
            print("✓ Successfully loaded all answer generation functions")
        except ImportError as e:
            print(f"✗ Failed to import functions: {e}")
            print("  Make sure you're running this from the planning_intelligence directory")
            sys.exit(1)

    def generate_response(self, prompt: str, question_type: str) -> Dict[str, Any]:
        """Generate response for a prompt."""
        try:
            # Get the appropriate answer function
            answer_func = self.answer_functions.get(question_type)
            
            if not answer_func:
                return {
                    "prompt": prompt,
                    "type": question_type,
                    "answer": "No answer function found",
                    "error": f"Unknown question type: {question_type}"
                }
            
            # Call the answer function with proper parameters
            # Different functions have different signatures
            if question_type in ["health", "risk", "change", "impact"]:
                # These take (detail_records, context)
                answer = answer_func(self.mock_records, self.mock_context)
            elif question_type in ["forecast", "schedule", "entity", "comparison"]:
                # These take (context, question)
                answer = answer_func(self.mock_context, prompt)
            else:
                answer = answer_func(self.mock_records, self.mock_context)
            
            return {
                "prompt": prompt,
                "type": question_type,
                "answer": answer,
                "error": None
            }
        except Exception as e:
            return {
                "prompt": prompt,
                "type": question_type,
                "answer": None,
                "error": str(e)
            }

    def review_all_responses(self) -> None:
        """Review responses for all prompts."""
        print("\n" + "="*80)
        print("RESPONSE CONTENT REVIEW")
        print("="*80)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to review: {total_tests}\n")
        
        # Review each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{'='*80}")
            print(f"{category.upper()} QUESTIONS ({len(prompts)} prompts)")
            print(f"{'='*80}\n")
            
            for idx, prompt in enumerate(prompts, 1):
                # Classify the question
                classification = self.classify_question(prompt)
                
                # Generate response
                response = self.generate_response(prompt, classification)
                self.results.append(response)
                
                # Display the response
                print(f"[{idx}] Question: {prompt}")
                print(f"    Type: {classification}")
                
                if response["error"]:
                    print(f"    ✗ Error: {response['error']}")
                else:
                    answer = response["answer"]
                    
                    # Format answer based on type
                    if isinstance(answer, dict):
                        print(f"    ✓ Answer (structured):")
                        for key, value in answer.items():
                            if isinstance(value, (list, dict)):
                                if isinstance(value, list) and len(value) > 3:
                                    print(f"      {key}: [{len(value)} items]")
                                else:
                                    print(f"      {key}: {json.dumps(value, indent=8)}")
                            else:
                                print(f"      {key}: {value}")
                    elif isinstance(answer, list):
                        print(f"    ✓ Answer (list with {len(answer)} items):")
                        for item in answer[:3]:  # Show first 3 items
                            if isinstance(item, dict):
                                print(f"      - {json.dumps(item, indent=8)}")
                            else:
                                print(f"      - {item}")
                        if len(answer) > 3:
                            print(f"      ... and {len(answer) - 3} more items")
                    else:
                        answer_str = str(answer)
                        if len(answer_str) > 200:
                            print(f"    ✓ Answer: {answer_str[:200]}...")
                        else:
                            print(f"    ✓ Answer: {answer_str}")
                
                print()

    def print_summary(self) -> None:
        """Print summary of responses."""
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        total = len(self.results)
        errors = sum(1 for r in self.results if r["error"])
        success = total - errors
        
        print(f"\nTotal Responses: {total}")
        print(f"Successful: {success} ✓")
        print(f"Errors: {errors} ✗")
        
        if errors > 0:
            print(f"\nFailed Responses:")
            for result in self.results:
                if result["error"]:
                    print(f"• '{result['prompt']}'")
                    print(f"  Error: {result['error']}")
        
        # Group by type
        print(f"\nResponses by Type:")
        type_counts = {}
        for result in self.results:
            q_type = result["type"]
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        for q_type, count in sorted(type_counts.items()):
            print(f"  {q_type}: {count}")

    def export_results(self, filename: str = "response_content_review.json") -> None:
        """Export results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    reviewer = ResponseContentReviewer()
    
    try:
        reviewer.review_all_responses()
        reviewer.print_summary()
        reviewer.export_results()
    except KeyboardInterrupt:
        print("\n\nReview interrupted by user")
        reviewer.print_summary()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
