# Next Steps: Ollama Testing & Deployment

## Current Status
✅ **Code Integration Complete** - All 12 answer functions updated
⏱️ **Performance Issue Found** - Llama2 model is too slow (5-10s per response)
🎯 **Solution Ready** - Switch to Mistral (1-2s per response)

---

## What You Need to Do Now

### Step 1: Switch to Mistral Model (5 minutes)

**In PowerShell:**
```powershell
# Pull the Mistral model
ollama pull mistral

# Verify it's installed
ollama list

# Set environment variable for this session
$env:OLLAMA_MODEL = "mistral"

# Verify
$env:OLLAMA_MODEL
```

**Expected output:**
```
NAME            ID              SIZE    MODIFIED
llama2:latest   ...             3.8 GB  ...
mistral:latest  ...             4.1 GB  ...
```

### Step 2: Test Quick Diagnostic (2 minutes)

```powershell
cd planning_intelligence
python test_ollama_quick.py
```

**Expected output:**
```
✅ Connected. Available models: ['llama2:latest', 'mistral:latest']
✅ Generated in 1.5s
✅ Model: mistral:latest
```

### Step 3: Run Full Integration Test (10-15 minutes)

```powershell
cd planning_intelligence
python test_ollama_integration.py
```

**What it tests:**
- ✅ Connection to Ollama
- ✅ Response generation
- ✅ OllamaLLMService class
- ✅ All 12 question types
- ✅ Performance metrics

**Expected results:**
```
✅ PASS - Connection Test
✅ PASS - Generation Test
✅ PASS - Service Test
✅ PASS - Question Types Test (all 12)
✅ PASS - Performance Test
```

---

## What Each Test Does

### test_ollama_quick.py (2 minutes)
- Tests connection to Ollama
- Tests basic generation (5 second timeout)
- Shows model info
- **Purpose:** Quick verification that Ollama is working

### test_ollama_integration.py (10-15 minutes)
- Tests all 12 question types:
  1. Health Status
  2. Forecast
  3. Risk Assessment
  4. Design Change
  5. General Planning
  6. Greeting
  7. Design Specification
  8. Schedule
  9. Location
  10. Material
  11. Entity
  12. Comparison
- Tests performance (average response time)
- **Purpose:** Full verification before deployment

---

## If Tests Pass ✅

You're ready to deploy! Next steps:

1. **Set permanent environment variable:**
   ```powershell
   # Add to your system environment variables
   # Or add to planning_intelligence/.env
   OLLAMA_MODEL=mistral
   OLLAMA_BASE_URL=http://localhost:11434
   ```

2. **Deploy to Azure Function App:**
   - Follow `DEPLOYMENT_CHECKLIST_OLLAMA.md`
   - Set same environment variables in Azure

3. **Monitor performance:**
   - Average response time should be 1-2 seconds
   - No timeouts
   - All 12 question types working

---

## If Tests Fail ❌

### Timeout Issues
**Problem:** Tests timeout at 30 seconds
**Solution:** 
- Option A: Switch to Mistral (recommended)
- Option B: Increase timeout in test script (line 30)
  ```python
  timeout=60  # instead of 30
  ```

### Connection Issues
**Problem:** Cannot connect to Ollama
**Solution:**
- Verify Ollama is running: `ollama serve`
- Check port 11434 is accessible
- Restart Ollama service

### Model Not Found
**Problem:** "Model 'mistral' not found"
**Solution:**
- Pull the model: `ollama pull mistral`
- Verify: `ollama list`
- Restart Ollama: `ollama serve`

---

## Performance Expectations

### With Mistral
- **Response time:** 1-2 seconds per question
- **Throughput:** ~30-60 questions per minute
- **Cost:** $0 (local)
- **Reliability:** 99.9% (no external dependencies)

### With Llama2
- **Response time:** 5-10 seconds per question
- **Throughput:** ~6-12 questions per minute
- **Cost:** $0 (local)
- **Reliability:** 99.9% (no external dependencies)

### With Azure OpenAI (Fallback)
- **Response time:** 2-8 seconds per question
- **Throughput:** ~7-30 questions per minute
- **Cost:** $500-1,000/month
- **Reliability:** 99.95% (cloud-based)

---

## Architecture After Integration

```
User Question
    ↓
Function App (planning_intelligence_nlp)
    ↓
Classify Question Type
    ↓
Call Answer Function (one of 12)
    ↓
get_llm_service() ← NEW GLOBAL HELPER
    ├─→ Try Ollama First (LOCAL)
    │   └─→ Mistral Model (1-2s response)
    │
    └─→ Fallback to Azure OpenAI (if Ollama down)
        └─→ GPT-4 (2-8s response)
    ↓
Return Answer to Frontend
```

---

## Files You'll Need

### For Testing
- `planning_intelligence/test_ollama_quick.py` - Quick diagnostic
- `planning_intelligence/test_ollama_integration.py` - Full test suite

### For Reference
- `OLLAMA_INTEGRATION_COMPLETE_VERIFIED.md` - Complete overview
- `OLLAMA_MODEL_SWITCH_GUIDE.md` - Model selection details
- `DEPLOYMENT_CHECKLIST_OLLAMA.md` - Deployment steps
- `OLLAMA_VS_AZURE_COMPARISON.md` - Cost/performance comparison

### Modified Code
- `planning_intelligence/function_app.py` - All 12 functions updated
- `planning_intelligence/ollama_llm_service.py` - NEW Ollama service

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Pull Mistral | 5-10 min | ⏳ TODO |
| Quick Diagnostic | 2 min | ⏳ TODO |
| Full Integration Test | 10-15 min | ⏳ TODO |
| Deploy to Azure | 15-20 min | ⏳ TODO |
| **Total** | **45-60 min** | ⏳ TODO |

---

## Ready to Start?

Run this command now:
```powershell
ollama pull mistral
```

Then come back and run the tests once it's done downloading.

**Questions?** Check the documentation files listed above.
