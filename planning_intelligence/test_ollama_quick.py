"""
Quick Ollama diagnostic - tests connection and basic performance
"""
import requests
import time
import json

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"

print("=" * 70)
print("OLLAMA QUICK DIAGNOSTIC")
print("=" * 70)

# Test 1: Connection
print("\n1. Testing connection...")
try:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"✅ Connected. Available models: {[m['name'] for m in models]}")
    else:
        print(f"❌ Connection failed: {response.status_code}")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

# Test 2: Quick generation with short timeout
print("\n2. Testing quick generation (5 second timeout)...")
try:
    start = time.time()
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": "Hi",
            "stream": False,
            "temperature": 0.7
        },
        timeout=5
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"✅ Generated in {elapsed:.2f}s")
    else:
        print(f"❌ Generation failed: {response.status_code}")
except requests.exceptions.Timeout:
    print(f"⏱️  TIMEOUT: Model is too slow (>5s)")
    print("   Recommendation: Use 'mistral' model instead (faster)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check model size
print("\n3. Checking model info...")
try:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/show",
        json={"name": OLLAMA_MODEL},
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Model: {data.get('name')}")
        print(f"   Parameters: {data.get('parameters', 'unknown')}")
        print(f"   Quantization: {data.get('quantization', 'unknown')}")
    else:
        print(f"❌ Failed to get model info")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
If you see TIMEOUT above:
  - llama2 is a 7B parameter model that's slower
  - Switch to 'mistral' for 3x faster responses
  
To switch models:
  1. Pull mistral: ollama pull mistral
  2. Set env var: OLLAMA_MODEL=mistral
  3. Restart your app
  
Or increase timeout in test_ollama_integration.py (line 30):
  timeout=60  # instead of 30
""")
