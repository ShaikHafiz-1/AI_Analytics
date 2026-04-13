# ChatGPT Integration Plan for Planning Intelligence Copilot

## Overview
This plan outlines how to integrate OpenAI's ChatGPT API to replace the current template-based response generation with natural language responses.

---

## Current State
- **Response Generation**: Template-based (deterministic, consistent)
- **LLM Integration**: None
- **API Calls**: Only to Azure Blob Storage for data
- **Response Quality**: Good for structured data, but repetitive

---

## Proposed Architecture

### 1. Add OpenAI API Integration

**Step 1: Install OpenAI Library**
```bash
pip install openai
```

**Step 2: Add Environment Variables**
```
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4-turbo  # or gpt-3.5-turbo for cost savings
OPENAI_TEMPERATURE=0.7    # Balance between deterministic and creative
```

**Step 3: Create OpenAI Wrapper Module**
Create `planning_intelligence/llm_service.py`:
```python
import os
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    def generate_response(self, prompt: str, context: dict) -> str:
        """Generate natural language response using ChatGPT."""
        system_message = self._build_system_prompt()
        user_message = self._build_user_prompt(prompt, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _build_system_prompt(self) -> str:
        return """You are a Planning Intelligence Copilot assistant. 
Your role is to provide clear, concise, business-focused insights about planning data.
- Be specific with numbers and metrics
- Highlight risks and opportunities
- Use professional but conversational tone
- Keep responses under 200 words
- Focus on actionable insights"""
    
    def _build_user_prompt(self, prompt: str, context: dict) -> str:
        return f"""User Question: {prompt}

Data Context:
{self._format_context(context)}

Please provide a natural language response based on this data."""
    
    def _format_context(self, context: dict) -> str:
        """Format metrics context for ChatGPT."""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
```

---

### 2. Modify Response Generation

**Update `generative_responses.py`:**

Replace template-based generation with LLM calls:

```python
from llm_service import LLMService

class GenerativeResponseBuilder:
    def __init__(self, use_llm=True):
        self.use_llm = use_llm
        if use_llm:
            self.llm = LLMService()
    
    def build_health_response(self, metrics: Dict) -> str:
        if self.use_llm:
            return self.llm.generate_response(
                "What is the planning health status?",
                metrics
            )
        else:
            # Fallback to templates
            return self._build_health_response_template(metrics)
    
    def build_risk_response(self, metrics: Dict) -> str:
        if self.use_llm:
            return self.llm.generate_response(
                "What are the main risks?",
                metrics
            )
        else:
            return self._build_risk_response_template(metrics)
    
    # ... similar for other response types
```

---

### 3. Update Function App

**Modify `function_app.py`:**

```python
from generative_responses import GenerativeResponseBuilder

# Initialize with LLM enabled
response_builder = GenerativeResponseBuilder(use_llm=True)

@app.route('planning-dashboard-v2', methods=['POST'])
def planning_dashboard_v2(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # ... existing code ...
        
        # Generate response with ChatGPT
        response = response_builder.build_response(
            classification=classification,
            metrics=metrics,
            prompt=user_prompt
        )
        
        return func.HttpResponse(
            json.dumps({"response": response}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        # Fallback to templates if LLM fails
        logger.error(f"LLM error: {str(e)}")
        response = response_builder.build_response_template(...)
        return func.HttpResponse(...)
```

---

### 4. Cost Optimization

**Option A: Use GPT-3.5-turbo (Cheaper)**
- Cost: ~$0.0005 per 1K tokens
- Speed: Fast
- Quality: Good for structured data

**Option B: Use GPT-4-turbo (Better Quality)**
- Cost: ~$0.01 per 1K tokens
- Speed: Slower
- Quality: Excellent for complex reasoning

**Recommendation**: Start with GPT-3.5-turbo, upgrade to GPT-4 if needed.

---

### 5. Fallback Strategy

**If ChatGPT API fails:**
1. Log the error
2. Fall back to template-based response
3. Alert monitoring system
4. Retry with exponential backoff

```python
def generate_response_with_fallback(self, prompt, metrics):
    try:
        return self.llm.generate_response(prompt, metrics)
    except Exception as e:
        logger.warning(f"LLM failed, using templates: {str(e)}")
        return self._generate_template_response(prompt, metrics)
```

---

### 6. Testing Strategy

**Unit Tests:**
```python
def test_llm_response_generation():
    builder = GenerativeResponseBuilder(use_llm=True)
    metrics = {"health": 75, "changes": 5}
    response = builder.build_health_response(metrics)
    assert len(response) > 0
    assert "health" in response.lower()

def test_fallback_on_llm_error():
    builder = GenerativeResponseBuilder(use_llm=True)
    # Mock LLM failure
    builder.llm.generate_response = Mock(side_effect=Exception("API Error"))
    response = builder.build_health_response({})
    assert response is not None  # Should use template
```

**Integration Tests:**
- Test all 46 prompts with ChatGPT
- Verify response quality
- Monitor API latency
- Track costs

---

### 7. Deployment Steps

1. **Local Testing**
   - Add OpenAI API key to `.env`
   - Test with sample prompts
   - Verify fallback behavior

2. **Azure Deployment**
   - Add `OPENAI_API_KEY` to Function App settings
   - Deploy updated code
   - Monitor logs for errors

3. **Gradual Rollout**
   - Enable for 10% of requests first
   - Monitor quality and costs
   - Gradually increase to 100%

---

### 8. Monitoring & Metrics

**Track:**
- API response time (target: <2 seconds)
- Error rate (target: <1%)
- Cost per request
- Response quality (user feedback)
- Token usage

**Alerts:**
- API errors > 5%
- Response time > 5 seconds
- Daily cost > threshold

---

### 9. Configuration Options

**Environment Variables:**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
OPENAI_TIMEOUT=10
USE_LLM=true
LLM_FALLBACK_ENABLED=true
```

---

### 10. Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 1-2 days | Setup OpenAI, create LLM service, local testing |
| **Phase 2** | 1 day | Update response builder, add fallback logic |
| **Phase 3** | 1 day | Deploy to Azure, monitor, test all 46 prompts |
| **Phase 4** | Ongoing | Monitor costs, optimize, gather user feedback |

---

## Benefits

✅ **Natural Language**: More conversational, less repetitive
✅ **Flexible**: Can handle unexpected prompts
✅ **Scalable**: Easy to add new prompt types
✅ **Intelligent**: Better context understanding
✅ **Fallback**: Templates still available if API fails

## Risks

⚠️ **Cost**: ~$0.0005-0.01 per request
⚠️ **Latency**: Adds 1-2 seconds per response
⚠️ **API Dependency**: Requires OpenAI API availability
⚠️ **Quality Variance**: Responses may vary slightly

---

## Next Steps

1. Get OpenAI API key
2. Create `llm_service.py` module
3. Update `generative_responses.py`
4. Test locally with sample prompts
5. Deploy to Azure
6. Monitor and optimize

Ready to proceed?
