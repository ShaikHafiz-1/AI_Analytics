# Ollama Quick Start - 15 Minutes to Running

**Goal**: Get Ollama running locally in 15 minutes  
**Status**: ✅ Ready to execute

---

## ⚡ 5-Minute Setup

### Step 1: Download Ollama (2 minutes)

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows**:
- Download from https://ollama.ai/download
- Run installer
- Restart computer

### Step 2: Pull Model (2 minutes)

```bash
# Pull Llama 2 (recommended)
ollama pull llama2

# Or pull Mistral (faster)
ollama pull mistral
```

### Step 3: Start Server (1 minute)

```bash
# Start Ollama
ollama serve

# Or run in background
ollama serve &
```

**Expected output**:
```
2026-04-17 10:30:00 Listening on 127.0.0.1:11434
```

---

## ✅ Verify Installation

### Test Ollama API

```bash
# Test the API
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "What is planning intelligence?",
  "stream": false
}'
```

**Expected response**:
```json
{
  "model": "llama2",
  "created_at": "2026-04-17T10:30:00Z",
  "response": "Planning intelligence is...",
  "done": true
}
```

---

## 🚀 Use with Planning Intelligence Copilot

### Step 1: Update Backend

**Update `planning_intelligence/function_app.py`**:

```python
# Replace this:
from planning_intelligence.llm_service import get_llm_service

# With this:
from planning_intelligence.ollama_llm_service import get_ollama_service

# Then replace:
llm_service = get_llm_service()

# With:
llm_service = get_ollama_service()
```

### Step 2: Set Environment Variable

```bash
# Use Ollama instead of Azure
export USE_OLLAMA=true
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
```

### Step 3: Run Backend

```bash
cd planning_intelligence
python -m azure.functions start
```

### Step 4: Test

```bash
# Ask a question
curl -X POST http://localhost:7071/api/planning_intelligence_nlp \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the planning health?",
    "location": "Dallas"
  }'
```

---

## 📊 Model Options

### Llama 2 (Recommended)
```bash
ollama pull llama2
# Size: 4GB
# Speed: 1-3 seconds
# Quality: Excellent
```

### Mistral (Fastest)
```bash
ollama pull mistral
# Size: 4GB
# Speed: 1-2 seconds
# Quality: Good
```

### Neural Chat
```bash
ollama pull neural-chat
# Size: 4GB
# Speed: 1-3 seconds
# Quality: Good for chat
```

### Orca Mini (Smallest)
```bash
ollama pull orca-mini
# Size: 2GB
# Speed: 1-2 seconds
# Quality: Good reasoning
```

---

## 🔧 Configuration

### local.settings.json

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "USE_OLLAMA": "true",
    "OLLAMA_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "llama2"
  }
}
```

### Environment Variables

```bash
# Use Ollama
export USE_OLLAMA=true
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama2

# Or use Azure (default)
export USE_OLLAMA=false
```

---

## 🐛 Troubleshooting

### Ollama Not Starting

```bash
# Check if port 11434 is in use
lsof -i :11434

# Kill process using port
kill -9 <PID>

# Try different port
ollama serve --host 0.0.0.0:11435
```

### Model Not Found

```bash
# List available models
ollama list

# Pull model
ollama pull llama2

# Check model size
du -sh ~/.ollama/models/
```

### Slow Responses

```bash
# Check system resources
top

# Use smaller model
ollama pull mistral

# Increase timeout in code
timeout=120  # seconds
```

### Memory Issues

```bash
# Check available memory
free -h

# Use smaller model
ollama pull orca-mini

# Or increase system memory
```

---

## 📈 Performance

### Response Times

| Model | Time |
|-------|------|
| Llama 2 | 1-3 sec |
| Mistral | 1-2 sec |
| Neural Chat | 1-3 sec |
| Orca Mini | 1-2 sec |

### Memory Usage

| Model | Memory |
|-------|--------|
| Llama 2 | 8GB |
| Mistral | 8GB |
| Neural Chat | 8GB |
| Orca Mini | 4GB |

---

## 🎯 Next Steps

1. ✅ Install Ollama
2. ✅ Pull model
3. ✅ Start server
4. ✅ Update backend code
5. ✅ Set environment variables
6. ✅ Test with sample question
7. ✅ Deploy to production

---

## 💰 Cost Comparison

| Aspect | Azure OpenAI | Ollama |
|--------|--------------|--------|
| Monthly | $500-1,000 | $0 |
| Annual | $6,000-12,000 | $0 |
| Setup | 45 min | 15 min |
| Vendor Lock-in | High | None |

**Savings**: $6,000-12,000/year

---

## ✅ Checklist

- [ ] Download Ollama
- [ ] Install Ollama
- [ ] Pull model (llama2)
- [ ] Start Ollama server
- [ ] Test API with curl
- [ ] Update function_app.py
- [ ] Set environment variables
- [ ] Run backend
- [ ] Test with sample question
- [ ] Verify response quality

---

## 📞 Support

### Common Issues

**Q: Ollama won't start**
A: Check if port 11434 is in use. Kill process and try again.

**Q: Model download is slow**
A: Models are 4GB. Check internet connection.

**Q: Responses are slow**
A: Use smaller model (Mistral) or increase system memory.

**Q: Memory error**
A: Use smaller model (Orca Mini) or increase RAM.

---

## 🚀 Ready?

```bash
# 1. Install
brew install ollama

# 2. Pull model
ollama pull llama2

# 3. Start server
ollama serve

# 4. In another terminal, test
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello!",
  "stream": false
}'
```

**Done!** Ollama is running. Now update your backend code.

---

**Time to Complete**: 15 minutes  
**Cost Savings**: $6,000-12,000/year  
**Status**: ✅ Ready to Deploy
