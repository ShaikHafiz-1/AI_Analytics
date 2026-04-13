# Comprehensive Response Fixes - All Issues Addressed

## Issues Identified & Fixes

### Issue 1: "undefined" Values in Supporting Metrics

**Root Cause:** Context dictionary structure doesn't match expected keys in `answer_engine.py`

**Fix:** Standardize context structure and add validation

**Files to Update:**
1. `planning_intelligence/function_app.py` - Ensure consistent context structure
2. `planning_intelligence/answer_engine.py` - Add field validation

### Issue 2: Timeout Errors

**Root Causes:**
- No timeout wrapper for blob loading
- No retry logic for LLM calls
- Azure OpenAI calls have no timeout handling

**Fixes:**
1. Add timeout wrapper to blob loading
2. Add retry logic with exponential backoff
3. Add timeout to Azure OpenAI calls

### Issue 3: Incorrect Location Comparisons

**Root Cause:** String comparison without normalization (DSM18_F01C010 vs DSM18_F01C01)

**Fix:** Implement location ID normalization function

### Issue 4: Missing Business Context in Responses

**Root Cause:** Incomplete system prompt and metrics not passed to LLM

**Fix:** Enhance system prompt and ensure detail records are passed

## Implementation Plan

### Step 1: Fix Context Structure (function_app.py)

Ensure all answer generation functions return consistent context:

```python
def _build_consistent_context(detail_records, context):
    """Build consistent context structure for all responses."""
    return {
        "planningHealth": context.get("planningHealth", 0),
        "status": context.get("status", "Unknown"),
        "changedRecordCount": len([r for r in detail_records if r.get("changed")]),
        "totalRecords": len(detail_records),
        "designChanges": context.get("riskSummary", {}).get("designChangedCount", 0),
        "supplierChanges": context.get("riskSummary", {}).get("supplierChangedCount", 0),
        "qtyChanges": sum(1 for r in detail_records if r.get("qtyChanged")),
        "trendDirection": context.get("trendDirection", "Stable"),
        "riskLevel": context.get("riskSummary", {}).get("level", "Unknown"),
        "highRiskCount": context.get("riskSummary", {}).get("highRiskCount", 0),
    }
```

### Step 2: Add Location Normalization (scoped_metrics.py)

```python
def normalize_location_id(location_id: str) -> str:
    """Normalize location ID for consistent comparison."""
    if not location_id:
        return ""
    # Remove trailing zeros from location codes
    # DSM18_F01C010 -> DSM18_F01C01
    normalized = location_id.upper().strip()
    # Remove trailing zeros from numeric parts
    parts = normalized.split('_')
    normalized_parts = []
    for part in parts:
        # Remove trailing zeros but keep at least one digit
        if part and part[-1].isdigit():
            part = part.rstrip('0') or '0'
        normalized_parts.append(part)
    return '_'.join(normalized_parts)

def filter_by_location(records, location_id):
    """Filter records by normalized location ID."""
    if not location_id:
        return records
    normalized_target = normalize_location_id(location_id)
    return [r for r in records if normalize_location_id(r.get("locationId", "")) == normalized_target]
```

### Step 3: Add Timeout & Retry Logic (llm_service.py)

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_response_with_retry(self, prompt: str, context: Dict, detail_records: List[Dict] = None) -> str:
    """Generate response with retry logic."""
    try:
        return self.generate_response(prompt, context, detail_records)
    except Exception as e:
        logger.warning(f"LLM call failed: {str(e)}. Retrying...")
        raise
```

### Step 4: Add Blob Loading Timeout (function_app.py)

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Blob loading exceeded timeout")

def load_current_previous_from_blob_with_timeout(timeout_seconds=30):
    """Load blob data with timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        return load_current_previous_from_blob()
    finally:
        signal.alarm(0)  # Cancel alarm
```

### Step 5: Enhance System Prompt (llm_service.py)

Add more business context to system prompt:

```python
ENHANCED_SYSTEM_PROMPT = """
You are a Planning Intelligence Copilot for supply chain analytics.

BUSINESS CONTEXT:
- Design changes (ZCOIBODVER or ZCOIFORMFACT) require engineering review
- Forecast changes impact supplier capacity and delivery timelines
- Supplier changes need coordination and contingency planning
- ROJ shifts affect procurement timing
- Location codes: CYS20_F01C01, DSM18_F01C01, etc.

RESPONSE REQUIREMENTS:
1. Explain WHY changes happened (business impact)
2. Connect forecast, supplier, design, and schedule impacts
3. Provide specific metrics and numbers
4. Include recommended actions
5. Use natural, conversational tone

CRITICAL RULES:
- Never compute values - use provided metrics
- Never hallucinate data or logic
- Always respect SAP field definitions
- Always include business impact explanation
"""
```

## Deployment Sequence

1. **Fix Context Structure** → Deploy function_app.py
2. **Add Location Normalization** → Deploy scoped_metrics.py
3. **Add Timeout & Retry** → Deploy llm_service.py
4. **Enhance System Prompt** → Deploy llm_service.py
5. **Test All Fixes** → Validate responses

## Testing Checklist

- [ ] "What's the planning health?" → No undefined metrics
- [ ] "List suppliers for UPS at CYS20" → Correct location filtering
- [ ] "Compare CYS20_F01C01 vs DSM18_F01C01" → Correct comparison
- [ ] Complex query → No timeout error
- [ ] "Hi" → Fast response with business context
- [ ] All responses include business impact explanation
- [ ] All responses include recommended actions

## Expected Results After Fixes

✅ No "undefined" values in Supporting Metrics
✅ No timeout errors on any queries
✅ Correct location comparisons (DSM18_F01C010 = DSM18_F01C01)
✅ All responses include business context and recommendations
✅ Consistent response structure across all query types
✅ Retry logic handles transient failures
✅ Fast responses for simple queries
✅ Comprehensive responses for complex queries
