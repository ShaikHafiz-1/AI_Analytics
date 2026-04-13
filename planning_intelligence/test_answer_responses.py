#!/usr/bin/env python3
"""
Test Answer Responses
Generates and displays actual answers for all 46 prompts using real blob data.
"""

import logging
import os
import sys
import json
import time

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


class AnswerResponseTester:
    def __init__(self):
        self.results = []
        self.detail_records = []
        self.context = {}
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

    def format_answer(self, answer_data, max_length=500) -> str:
        """Format answer for display."""
        if isinstance(answer_data, dict):
            # For structured responses, show key fields
            lines = []
            for key, value in answer_data.items():
                if isinstance(value, (list, dict)):
                    if isinstance(value, list):
                        if len(value) > 0:
                            lines.append(f"  {key}: [{len(value)} items]")
                            # Show first 2 items
                            for item in value[:2]:
                                if isinstance(item, dict):
                                    item_str = json.dumps(item)[:80]
                                    lines.append(f"    - {item_str}...")
                                else:
                                    lines.append(f"    - {str(item)[:80]}")
                            if len(value) > 2:
                                lines.append(f"    ... and {len(value) - 2} more")
                    else:
                        val_str = json.dumps(value)[:100]
                        lines.append(f"  {key}: {val_str}...")
                else:
                    val_str = str(value)
                    if len(val_str) > 100:
                        lines.append(f"  {key}: {val_str[:100]}...")
                    else:
                        lines.append(f"  {key}: {val_str}")
            return "\n".join(lines)
        elif isinstance(answer_data, list):
            lines = [f"[List with {len(answer_data)} items]"]
            for item in answer_data[:3]:
                if isinstance(item, dict):
                    item_str = json.dumps(item)[:80]
                    lines.append(f"  - {item_str}...")
                else:
                    lines.append(f"  - {str(item)[:80]}")
            if len(answer_data) > 3:
                lines.append(f"  ... and {len(answer_data) - 3} more")
            return "\n".join(lines)
        else:
            answer_str = str(answer_data)
            if len(answer_str) > max_length:
                return answer_str[:max_length] + "..."
            return answer_str

    def test_prompt(self, prompt: str, category: str) -> dict:
        """Test a single prompt and generate answer."""
        try:
            # Classify
            classification = classify_question(prompt)
            
            # Get answer function
            answer_func = self.answer_functions.get(classification)
            
            if not answer_func:
                return {
                    "prompt": prompt,
                    "category": category,
                    "classification": classification,
                    "answer": None,
                    "error": f"No answer function for {classification}"
                }
            
            # Generate answer
            start_time = time.time()
            
            # Different functions have different signatures
            if classification in ["health", "risk", "change", "impact"]:
                answer = answer_func(self.detail_records, self.context)
            elif classification in ["forecast", "schedule", "entity", "comparison"]:
                answer = answer_func(self.context, prompt)
            else:
                answer = answer_func(self.detail_records, self.context)
            
            response_time = time.time() - start_time
            
            result = {
                "prompt": prompt,
                "category": category,
                "classification": classification,
                "answer": answer,
                "response_time_ms": round(response_time * 1000, 2),
                "error": None
            }
            
            return result
            
        except Exception as e:
            return {
                "prompt": prompt,
                "category": category,
                "classification": "error",
                "answer": None,
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests and display responses."""
        print("\n" + "="*120)
        print("TESTING ALL 46 PROMPTS - ANSWER RESPONSES")
        print("="*120)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to test: {total_tests}")
        print(f"Detail records loaded: {len(self.detail_records)}")
        print(f"Context keys: {list(self.context.keys())}\n")
        
        # Test each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{'='*120}")
            print(f"{category.upper()} QUESTIONS ({len(prompts)} prompts)")
            print(f"{'='*120}\n")
            
            category_success = 0
            category_errors = 0
            
            for idx, prompt in enumerate(prompts, 1):
                result = self.test_prompt(prompt, category)
                self.results.append(result)
                
                print(f"[{idx}] PROMPT: {prompt}")
                print(f"    Classification: {result['classification']}")
                
                if result.get("error"):
                    print(f"    ✗ Error: {result['error']}")
                    category_errors += 1
                else:
                    print(f"    ✓ Response Time: {result['response_time_ms']}ms")
                    print(f"    Answer:")
                    answer_formatted = self.format_answer(result['answer'])
                    for line in answer_formatted.split('\n'):
                        print(f"      {line}")
                    category_success += 1
                
                print()
            
            print(f"Category Summary: {category_success} successful, {category_errors} errors")

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "="*120)
        print("SUMMARY")
        print("="*120)
        
        total = len(self.results)
        errors = sum(1 for r in self.results if r.get("error"))
        success = total - errors
        
        print(f"\nTotal Tests: {total}")
        print(f"Successful: {success} ✓")
        print(f"Errors: {errors} ✗")
        
        if errors > 0:
            print(f"\nFailed Prompts:")
            for result in self.results:
                if result.get("error"):
                    print(f"• '{result['prompt']}'")
                    print(f"  Error: {result['error']}")
        
        # Response time stats
        response_times = [r['response_time_ms'] for r in self.results if r.get('response_time_ms')]
        if response_times:
            print(f"\nResponse Time Statistics:")
            print(f"  Average: {sum(response_times) / len(response_times):.2f}ms")
            print(f"  Min: {min(response_times):.2f}ms")
            print(f"  Max: {max(response_times):.2f}ms")

    def export_results(self, filename: str = "answer_responses.json") -> None:
        """Export results to JSON file."""
        # Convert non-serializable objects
        export_data = []
        for result in self.results:
            export_result = result.copy()
            if export_result.get('answer'):
                export_result['answer'] = str(export_result['answer'])
            export_data.append(export_result)
        
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    try:
        tester = AnswerResponseTester()
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
