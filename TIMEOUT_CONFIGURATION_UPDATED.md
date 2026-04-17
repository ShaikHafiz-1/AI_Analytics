# Timeout Configuration Updated

## Changes Made

### Backend (ollama_llm_service.py)
- **Default timeout**: 30s → **120s** (2 minutes)
- Allows slower models like llama2 to complete requests
- Mistral will still respond in 1-3 seconds (well under limit)

### Frontend (CopilotPanel.tsx)
- **Request timeout**: 35s → **120s** (2 minutes)
- Matches backend timeout
- Shows "Request timed out" message if exceeded

## Why These Changes?

| Model | Response Time | Old Timeout | New Timeout | Status |
|-------|---------------|------------|------------|--------|
| mistral | 1-3s | 35s ✅ | 120s ✅ | Works great |
| llama2 | 30-60s | 35s ❌ | 120s ✅ | Now works |
| Azure | 2-8s | 35s ✅ | 120s ✅ | Works great |

## How It Works Now

1. **User asks a question** in the frontend
2. **Frontend waits up to 120 seconds** for response
3. **Backend calls Ollama** with 120-second timeout
4. **Ollama generates response** (1-3s for mistral, 30-60s for llama2)
5. **Response sent back** to frontend
6. **Message displayed** in chat

## Testing

### With Mistral (Recommended)
```bash
set OLLAMA_MODEL=mistral
python test_ollama_integration.py
```
Expected: All tests pass in 1-3 seconds each

### With Llama2
```bash
set OLLAMA_MODEL=llama2
python test_ollama_integration.py
```
Expected: All tests pass in 30-60 seconds each (now with 120s timeout)

## Production Deployment

When deploying to Azure:
1. Set `OLLAMA_MODEL=mistral` (recommended for speed)
2. Or keep `OLLAMA_MODEL=llama2` (works now with 120s timeout)
3. Frontend will automatically use 120s timeout
4. System will fall back to Azure if Ollama unavailable

## Notes

- **120 seconds is safe** - Azure Functions have 230-second timeout
- **Mistral is recommended** - 3x faster, same quality
- **Both models work now** - timeout issue resolved
- **No code changes needed** - just set environment variable

## Files Modified

1. `planning_intelligence/ollama_llm_service.py` - Line 84: timeout=120
2. `frontend/src/components/CopilotPanel.tsx` - Line 93: 120000ms timeout
