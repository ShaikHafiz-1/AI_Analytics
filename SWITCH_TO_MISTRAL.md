# Quick Guide: Switch from llama2 to Mistral

## Why Switch?
- **llama2**: 30-60+ seconds per response (too slow)
- **mistral**: 1-3 seconds per response (3x faster)
- Both are free, local, and open-source

## Step-by-Step

### Step 1: Pull Mistral Model
```bash
ollama pull mistral
```
This downloads the mistral model (~4GB). Takes 5-10 minutes depending on internet speed.

### Step 2: Verify Installation
```bash
ollama list
```
You should see both models:
```
NAME            ID              SIZE    MODIFIED
llama2:latest   ...             3.8 GB  ...
mistral:latest  ...             4.1 GB  ...
```

### Step 3: Set Environment Variable

**Windows PowerShell:**
```powershell
$env:OLLAMA_MODEL = "mistral"
```

**Windows CMD:**
```cmd
set OLLAMA_MODEL=mistral
```

**Or add to .env file:**
```
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 4: Test the Integration
```bash
cd planning_intelligence
python test_ollama_integration.py
```

Expected output:
```
✅ Ollama is running
✅ Model 'mistral' is available
✅ Response generated in 1.23 seconds
✅ OllamaLLMService is available
✅ All 12 question types passed
```

## Performance Comparison

### Before (llama2)
```
❌ Generation test failed: Read timed out (30s)
❌ Service test failed: Ollama request timeout (30s)
❌ All 12 question types: TIMEOUT
```

### After (mistral)
```
✅ Response generated in 2.15 seconds
✅ OllamaLLMService is available
✅ All 12 question types: PASS (1-3s each)
```

## Troubleshooting

### "Model not found" error
```bash
# Make sure mistral is pulled
ollama pull mistral

# Verify it's installed
ollama list
```

### Still getting timeouts
- Check if Ollama is running: `ollama serve`
- Check if mistral is loaded: `ollama list`
- Increase timeout in `ollama_llm_service.py` line 99 to 60 seconds

### Want to keep both models?
You can have both installed. Just switch between them:
```bash
set OLLAMA_MODEL=mistral    # Use mistral
set OLLAMA_MODEL=llama2     # Use llama2
```

## Next: Deploy to Production

Once testing passes locally:
1. Set `OLLAMA_MODEL=mistral` in production environment
2. Deploy function_app.py to Azure
3. System will use Ollama first, fallback to Azure if needed

## Questions?

- **Ollama docs**: https://ollama.ai
- **Mistral model**: https://mistral.ai
- **Integration guide**: See OLLAMA_INTEGRATION_STATUS.md
