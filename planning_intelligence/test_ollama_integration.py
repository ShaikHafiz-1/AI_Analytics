"""
Local Testing Script for Ollama Integration
Tests Ollama service with Planning Intelligence Copilot

Usage:
    python test_ollama_integration.py

Requirements:
    - Ollama running on localhost:11434
    - Model pulled (mistral or llama2)
    - requests library installed
"""

import sys
import json
import time
from typing import Dict, List

# Test configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"  # or "llama2" - mistral is 3x faster

# Sample planning data for testing
SAMPLE_RECORDS = [
    {
        "locationId": "Dallas",
        "materialId": "ELEC-001",
        "materialGroup": "Electronics",
        "supplier": "Supplier A",
        "forecastQty": 100,
        "forecastQtyPrevious": 95,
        "rojCurrent": "2026-05-15",
        "rojPrevious": "2026-05-10",
        "bodCurrent": "v2.0",
        "bodPrevious": "v1.0",
        "ffCurrent": "FF-2026",
        "ffPrevious": "FF-2025",
        "qtyChanged": True,
        "supplierChanged": False,
        "designChanged": True,
        "rojChanged": True
    },
    {
        "locationId": "Houston",
        "materialId": "MECH-001",
        "materialGroup": "Mechanical",
        "supplier": "Supplier B",
        "forecastQty": 50,
        "forecastQtyPrevious": 50,
        "rojCurrent": "2026-06-01",
        "rojPrevious": "2026-06-01",
        "bodCurrent": "v1.0",
        "bodPrevious": "v1.0",
        "ffCurrent": "FF-2026",
        "ffPrevious": "FF-2026",
        "qtyChanged": False,
        "supplierChanged": False,
        "designChanged": False,
        "rojChanged": False
    }
]

# Test questions (12 types)
TEST_QUESTIONS = [
    ("Health Status", "What's the overall planning health status?"),
    ("Forecast", "What's the forecast for the next 30 days?"),
    ("Risk Assessment", "What are the top risks in our supply chain?"),
    ("Design Change", "How will the new design affect our planning?"),
    ("General Planning", "Tell me about the current planning situation"),
    ("Greeting", "Hi, how are you?"),
    ("Design Specification", "What designs do we have?"),
    ("Schedule", "What's the current schedule status?"),
    ("Location", "How is Dallas performing?"),
    ("Material", "What about electronics materials?"),
    ("Entity", "Tell me about Supplier A"),
    ("Comparison", "Compare Dallas and Houston")
]


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text: str):
    """Print formatted section"""
    print(f"\n>>> {text}")


def print_success(text: str):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text: str):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text: str):
    """Print info message"""
    print(f"ℹ️  {text}")


def test_ollama_connection() -> bool:
    """Test if Ollama is running and accessible"""
    print_section("Testing Ollama Connection")
    
    try:
        import requests
        
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name") for m in data.get("models", [])]
            
            print_success(f"Ollama is running at {OLLAMA_BASE_URL}")
            print_info(f"Available models: {', '.join(models)}")
            
            if OLLAMA_MODEL in [m.split(":")[0] for m in models]:
                print_success(f"Model '{OLLAMA_MODEL}' is available")
                return True
            else:
                print_error(f"Model '{OLLAMA_MODEL}' not found")
                print_info(f"Pull it with: ollama pull {OLLAMA_MODEL}")
                return False
        else:
            print_error(f"Ollama returned status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print_info("Make sure Ollama is running: ollama serve")
        return False
    
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False


def test_ollama_generation() -> bool:
    """Test if Ollama can generate responses"""
    print_section("Testing Ollama Response Generation")
    
    try:
        import requests
        
        prompt = "What is supply chain planning?"
        
        print_info(f"Sending test prompt: '{prompt}'")
        
        start_time = time.time()
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=120
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get("response", "").strip()
            
            print_success(f"Response generated in {elapsed_time:.2f} seconds")
            print_info(f"Response length: {len(generated_text)} characters")
            print_info(f"Response preview: {generated_text[:100]}...")
            
            return True
        else:
            print_error(f"Generation failed with status {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Generation test failed: {e}")
        return False


def test_ollama_service():
    """Test the OllamaLLMService class"""
    print_section("Testing OllamaLLMService Class")
    
    try:
        from ollama_llm_service import OllamaLLMService
        
        service = OllamaLLMService(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        # Test availability
        if service.is_available():
            print_success("OllamaLLMService is available")
        else:
            print_error("OllamaLLMService is not available")
            return False
        
        # Test status
        status = service.get_status()
        print_info(f"Service status: {json.dumps(status, indent=2)}")
        
        # Test response generation
        print_info("Testing response generation with business context...")
        
        context = {
            "planningHealth": 78,
            "changedRecordCount": 5,
            "totalRecords": 100,
            "designChanges": 2,
            "supplierChanges": 1,
            "qtyChanges": 2
        }
        
        prompt = "What's the planning health status?"
        
        start_time = time.time()
        response = service.generate_response(prompt, context, SAMPLE_RECORDS)
        elapsed_time = time.time() - start_time
        
        print_success(f"Response generated in {elapsed_time:.2f} seconds")
        print_info(f"Response: {response[:200]}...")
        
        return True
    
    except ImportError:
        print_error("Cannot import OllamaLLMService")
        print_info("Make sure ollama_llm_service.py is in planning_intelligence/")
        return False
    
    except Exception as e:
        print_error(f"Service test failed: {e}")
        return False


def test_all_question_types():
    """Test all 12 question types"""
    print_section("Testing All 12 Question Types")
    
    try:
        from ollama_llm_service import OllamaLLMService
        
        service = OllamaLLMService(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        context = {
            "planningHealth": 78,
            "changedRecordCount": 5,
            "totalRecords": 100,
            "designChanges": 2,
            "supplierChanges": 1,
            "qtyChanges": 2
        }
        
        results = []
        
        for question_type, question in TEST_QUESTIONS:
            print_info(f"Testing {question_type}: '{question}'")
            
            try:
                start_time = time.time()
                response = service.generate_response(question, context, SAMPLE_RECORDS)
                elapsed_time = time.time() - start_time
                
                print_success(f"  ✓ Response in {elapsed_time:.2f}s ({len(response)} chars)")
                
                results.append({
                    "type": question_type,
                    "question": question,
                    "response_length": len(response),
                    "response_time": elapsed_time,
                    "status": "✅ PASS"
                })
            
            except Exception as e:
                print_error(f"  ✗ Failed: {e}")
                
                results.append({
                    "type": question_type,
                    "question": question,
                    "status": "❌ FAIL",
                    "error": str(e)
                })
        
        # Print summary
        print_section("Question Type Test Summary")
        
        passed = sum(1 for r in results if r["status"] == "✅ PASS")
        failed = sum(1 for r in results if r["status"] == "❌ FAIL")
        
        print_info(f"Passed: {passed}/{len(results)}")
        print_info(f"Failed: {failed}/{len(results)}")
        
        for result in results:
            status_icon = "✅" if result["status"] == "✅ PASS" else "❌"
            print(f"{status_icon} {result['type']}: {result['status']}")
        
        return failed == 0
    
    except Exception as e:
        print_error(f"Question type test failed: {e}")
        return False


def test_performance():
    """Test performance metrics"""
    print_section("Testing Performance Metrics")
    
    try:
        from ollama_llm_service import OllamaLLMService
        
        service = OllamaLLMService(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        context = {
            "planningHealth": 78,
            "changedRecordCount": 5,
            "totalRecords": 100
        }
        
        # Test multiple requests
        num_requests = 5
        response_times = []
        
        print_info(f"Running {num_requests} requests...")
        
        for i in range(num_requests):
            start_time = time.time()
            response = service.generate_response(
                "What's the planning health?",
                context,
                SAMPLE_RECORDS
            )
            elapsed_time = time.time() - start_time
            response_times.append(elapsed_time)
            
            print_info(f"  Request {i+1}: {elapsed_time:.2f}s")
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print_section("Performance Statistics")
        print_info(f"Average response time: {avg_time:.2f}s")
        print_info(f"Min response time: {min_time:.2f}s")
        print_info(f"Max response time: {max_time:.2f}s")
        
        if avg_time < 5:
            print_success("Performance is acceptable (< 5s average)")
            return True
        else:
            print_error("Performance is slow (> 5s average)")
            return False
    
    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False


def main():
    """Run all tests"""
    print_header("OLLAMA INTEGRATION LOCAL TESTING")
    
    print_info(f"Ollama URL: {OLLAMA_BASE_URL}")
    print_info(f"Model: {OLLAMA_MODEL}")
    
    # Run tests
    tests = [
        ("Connection Test", test_ollama_connection),
        ("Generation Test", test_ollama_generation),
        ("Service Test", test_ollama_service),
        ("Question Types Test", test_all_question_types),
        ("Performance Test", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print final summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print_section("Overall Results")
    print_info(f"Passed: {passed}/{len(results)}")
    print_info(f"Failed: {failed}/{len(results)}")
    
    if failed == 0:
        print_success("All tests passed! Ollama integration is working correctly.")
        return 0
    else:
        print_error(f"{failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
