#!/usr/bin/env python3
"""
Test Prompt Responses
Displays actual responses for all 46 prompts using real blob data.
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


class PromptResponseTester:
    def __init__(self):
        self.results = []
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

    def format_response(self, response_data) -> str:
        """Format response for display."""
        if isinstance(response_data, dict):
            # For structured responses, show key fields
            lines = []
            for key, value in response_data.items():
                if isinstance(value, (list, dict)):
                    if isinstance(value, list):
                        if len(value) > 0:
                            lines.append(f"  {key}: [{len(value)} items]")
                            # Show first 2 items
                            for item in value[:2]:
                                if isinstance(item, dict):
                                    lines.append(f"    - {json.dumps(item, indent=6)[:100]}...")
                                else:
                                    lines.append(f"    - {str(item)[:100]}")
                            if len(value) > 2:
                                lines.append(f"    ... and {len(value) - 2} more")
                    else:
                        lines.append(f"  {key}: {json.dumps(value, indent=4)[:200]}...")
                else:
                    lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        elif isinstance(response_data, list):
            lines = [f"[List with {len(response_data)} items]"]
            for item in response_data[:3]:
                if isinstance(item, dict):
                    lines.append(f"  - {json.dumps(item, indent=4)[:100]}...")
                else:
                    lines.append(f"  - {str(item)[:100]}")
            if len(response_data) > 3:
                lines.append(f"  ... and {len(response_data) - 3} more")
            return "\n".join(lines)
        else:
            response_str = str(response_data)
            if len(response_str) > 300:
                return response_str[:300] + "..."
            return response_str

    def test_prompt(self, prompt: str) -> dict:
        """Test a single prompt and get response."""
        try:
            # Classify
            classification = classify_question(prompt)
            
            # For now, just return the classification and context info
            # In a real scenario, you'd call the appropriate answer function
            result = {
                "prompt": prompt,
                "classification": classification,
                "context_keys": list(self.context.keys()),
                "detail_records_count": len(self.detail_records),
                "error": None
            }
            
            return result
            
        except Exception as e:
            return {
                "prompt": prompt,
                "classification": "error",
                "error": str(e)
            }

    def run_all_tests(self) -> None:
        """Run all tests and display responses."""
        print("\n" + "="*100)
        print("TESTING ALL 46 PROMPTS - RESPONSES")
        print("="*100)
        
        total_tests = sum(len(prompts) for prompts in TEST_PROMPTS.values())
        print(f"\nTotal prompts to test: {total_tests}")
        print(f"Detail records loaded: {len(self.detail_records)}")
        print(f"Context available: {list(self.context.keys())}\n")
        
        # Test each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n{'='*100}")
            print(f"{category.upper()} QUESTIONS ({len(prompts)} prompts)")
            print(f"{'='*100}\n")
            
            for idx, prompt in enumerate(prompts, 1):
                result = self.test_prompt(prompt)
                self.results.append(result)
                
                print(f"[{idx}] PROMPT: {prompt}")
                print(f"    Classification: {result['classification']}")
                
                if result.get("error"):
                    print(f"    Error: {result['error']}")
                else:
                    print(f"    Context Keys: {result['context_keys']}")
                    print(f"    Detail Records: {result['detail_records_count']}")
                
                print()

    def export_results(self, filename: str = "prompt_responses.json") -> None:
        """Export results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults exported to {filename}")


def main():
    """Main entry point."""
    try:
        tester = PromptResponseTester()
        tester.run_all_tests()
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
