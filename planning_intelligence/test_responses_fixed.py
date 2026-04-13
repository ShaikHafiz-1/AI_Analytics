#!/usr/bin/env python3
"""
Test Responses - Fixed Version
Generates and displays actual answers for all 46 prompts.
Shows the actual response content, not just context.
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
                for key, value in settings.get("Values", {}).items():
                    if key not in os.environ:
                        os.environ[key] = value
        except Exception as e:
            pass

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
    generate_impact_answer,
    _normalize_detail_records
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Test prompts
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


class ResponseTester:
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
            current_rows, previous_rows = load_current_previous_from_blob()
            logger.info(f"✓ Loaded {len(current_rows)} current, {len(previous_rows)} previous rows")
            
            current_records = normalize_rows(current_rows, is_current=True)
            previous_records = normalize_rows(previous_rows, is_current=False)
            
            compared = compare_records(current_records, previous_records)
            logger.info(f"✓ Compared {len(compared)} records")
            
            response = build_response(compared, [], None, None, data_mode="cached")
            logger.info(f"✓ Built response")
            
            # Normalize detail records to dicts (ComparedRecord objects need to be converted)
            normalized_records = _normalize_detail_records(compared)
            logger.info(f"✓ Normalized {len(normalized_records)} records")
            
            self.detail_records = normalized_records
            self.context = response
            
            logger.info(f"✓ Ready with {len(self.detail_records)} detail records")
            
        except Exception as e:
            logger.error(f"✗ Failed to load blob data: {e}")
            raise

    def format_value(self, value, max_length=150) -> str:
        """Format a value for display."""
        if isinstance(value, dict):
            if len(value) == 0:
                return "{}"
            # Show first few key-value pairs
            items = list(value.items())[:3]
            formatted = ", ".join([f"{k}: {str(v)[:50]}" for k, v in items])
            if len(value) > 3:
                formatted += f", ... ({len(value)} total keys)"
            return "{" + formatted + "}"
        elif isinstance(value, list):
            if len(value) == 0:
                return "[]"
            # Show first few items
            items_str = ", ".join([str(item)[:40] for item in value[:3]])
            if len(value) > 3:
                items_str += f", ... ({len(value)} total items)"
            return "[" + items_str + "]"
        else:
            val_str = str(value)
            if len(val_str) > max_length:
                return val_str[:max_length] + "..."
            return val_str

    def test_prompt(self, prompt: str, category: str) -> dict:
        """Test a single prompt and generate answer."""
        try:
            classification = classify_question(prompt)
            answer_func = self.answer_functions.get(classification)
            
            if not answer_func:
                return {
                    "prompt": prompt,
                    "category": category,
                    "classification": classification,
                    "answer": None,
                    "response_time_ms": 0,
                    "error": f"No answer function for {classification}"
                }
            
            # Call the answer function with correct parameters
            start_time = time.time()
            
            # Check function signature - some need question parameter
            if classification in ["health", "risk", "change", "impact"]:
                # These take (detail_records, context)
                answer = answer_func(self.detail_records, self.context)
            elif classification in ["forecast", "schedule", "entity", "comparison"]:
                # These take (detail_records, context, question)
                answer = answer_func(self.detail_records, self.context, prompt)
            else:
                # Default to (detail_records, context)
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
                "response_time_ms": 0,
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests and display responses."""
        print("\n" + "="*130)
        print("TESTING ALL 46 PROMPTS - ACTUAL RESPONSES")
        print("="*130)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts: {total_tests}")
        print(f"Detail records: {len(self.detail_records)}")
        print(f"Context keys: {len(self.context)} keys\n")
        
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{'='*130}")
            print(f"{category.upper()} ({len(prompts)} prompts)")
            print(f"{'='*130}\n")
            
            success_count = 0
            error_count = 0
            
            for idx, prompt in enumerate(prompts, 1):
                result = self.test_prompt(prompt, category)
                self.results.append(result)
                
                print(f"[{idx}] {prompt}")
                print(f"    Classification: {result['classification']} | Time: {result['response_time_ms']}ms")
                
                if result.get("error"):
                    print(f"    ✗ ERROR: {result['error']}")
                    error_count += 1
                else:
                    print(f"    ✓ RESPONSE:")
                    answer = result['answer']
                    
                    if isinstance(answer, dict):
                        for key, value in answer.items():
                            formatted_val = self.format_value(value)
                            print(f"      {key}: {formatted_val}")
                    elif isinstance(answer, list):
                        print(f"      [List with {len(answer)} items]")
                        for item in answer[:2]:
                            formatted_item = self.format_value(item, 80)
                            print(f"        - {formatted_item}")
                        if len(answer) > 2:
                            print(f"        ... and {len(answer) - 2} more")
                    else:
                        formatted = self.format_value(answer, 200)
                        print(f"      {formatted}")
                    
                    success_count += 1
                
                print()
            
            print(f"Category: {success_count} success, {error_count} errors")

    def print_summary(self) -> None:
        """Print summary."""
        print("\n" + "="*130)
        print("SUMMARY")
        print("="*130)
        
        total = len(self.results)
        errors = sum(1 for r in self.results if r.get("error"))
        success = total - errors
        
        print(f"\nTotal: {total}")
        print(f"Success: {success} ✓")
        print(f"Errors: {errors} ✗")
        
        if errors > 0:
            print(f"\nFailed Prompts:")
            for result in self.results:
                if result.get("error"):
                    print(f"  • {result['prompt']}")
                    print(f"    Error: {result['error']}")
        
        # Response time stats
        times = [r['response_time_ms'] for r in self.results if r.get('response_time_ms')]
        if times:
            print(f"\nResponse Times:")
            print(f"  Average: {sum(times) / len(times):.2f}ms")
            print(f"  Min: {min(times):.2f}ms")
            print(f"  Max: {max(times):.2f}ms")

    def export_results(self, filename: str = "responses_fixed.json") -> None:
        """Export results to JSON."""
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
        tester = ResponseTester()
        tester.run_all_tests()
        tester.print_summary()
        tester.export_results()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
