# Switching from Llama2 to Mistral

## Why Switch?
- **Mistral**: 3x faster (1-2 seconds per response)
- **Llama2**: Slower (5-10+ seconds per response)
- Both are high quality, but Mistral is optimized for speed

## Quick Setup

### Step 1: Pull Mistral Model
```bash
ollama pull mistral
```
This downloads the Mistral model (~4GB). Takes 5-10 minutes depending on internet speed.

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
**Windows (PowerShell):**
```powershell
$env:OLLAMA_MODEL = "mistral"
```

**Windows (CMD):**
```cmd
set OLLAMA_MODEL=mistral
```

**Linux/Mac:**
```bash
export OLLAMA_MODEL=mistral
```

### Step 4: Verify in .env (Optional)
Edit `planning_intelligence/.env`:
```
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 5: Test
```bash
cd planning_intelligence
python test_ollama_quick.py
```

Expected output:
```
✅ Generated in 1.5s  (instead of timeout)
```

## Performance Comparison

| Metric | Llama2 | Mistral |
|--------|--------|---------|
| Response Time | 5-10s | 1-2s |
| Quality | Excellent | Excellent |
| Model Size | 3.8 GB | 4.1 GB |
| Parameters | 7B | 7B |
| Best For | Quality | Speed |

## Rollback to Llama2
If you want to switch back:
```bash
set OLLAMA_MODEL=llama2
```

## Troubleshooting

**Q: Mistral not found after pulling?**
- Restart Ollama: `ollama serve`
- Check: `ollama list`

**Q: Still getting timeouts?**
- Increase timeout in test: `timeout=60`
- Check system resources (RAM, CPU)
- Restart Ollama service

**Q: Which model should I use for production?**
- **Mistral**: Recommended for user-facing copilot (fast responses)
- **Llama2**: Use if you need maximum quality and can accept slower responses
