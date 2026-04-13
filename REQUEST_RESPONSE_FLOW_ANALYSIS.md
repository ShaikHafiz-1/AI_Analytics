# Request/Response Flow Analysis: Frontend Ask Copilot → Backend

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React Dashboard)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. USER TYPES PROMPT IN COPILOT PANEL                                      │
│     └─ CopilotPanel.tsx: User enters question in textarea                   │
│     └─ Example: "What's the planning health?"                               │
│                                                                              │
│  2. USER CLICKS "SEND" OR PRESSES ENTER                                     │
│     └─ sendMessage() callback triggered                                     │
│     └─ Input validation: trim, check if empty                               │
│                                                                              │
│  3. ADD USER MESSAGE TO CHAT                                                │
│     └─ setMessages() adds {role: "user", content: question}                 │
│     └─ Display in UI immediately                                            │
│     └─ Clear input field                                                    │
│     └─ Set loading = true                                                   │
│                                                                              │
│  4. SEND REQUEST TO BACKEND                                                 │
│     └─ fetchExplain() called from api.ts                                    │
│     └─ Endpoint: POST /api/explain                                          │
│     └─ Payload:                                                             │
│        {                                                                    │
│          "question": "What's the planning health?",                         │
│          "context": {                                                       │
│            "detailRecords": [...],  // Full dashboard context               │
│            "planningHealth": 65,                                            │
│            "changedRecordCount": 5,                                         │
│            "totalRecords": 20,                                              │
│            "riskSummary": {...},                                            │
│            "supplierSummary": {...},                                        │
│            ...                                                              │
│          }                                                                  │
│        }                                                                    │
│                                                                              │
│  5. TIMEOUT PROTECTION (6 seconds)                                          │
│     └─ If no response in 6s, show timeout message                           │
│     └─ Preserve user input for retry                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Azure Function App)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  6. EXPLAIN ENDPOINT RECEIVES REQUEST                                       │
│     └─ function_app.py: explain() handler                                   │
│     └─ Extract question and context from JSON body                          │
│     └─ Validate: question required, max 500 chars                           │
│                                                                              │
│  7. LOAD DETAIL RECORDS                                                     │
│     └─ If context has detailRecords: use them                               │
│     └─ Else: load from snapshot (cached blob data)                          │
│     └─ If no records: return 404 error                                      │
│                                                                              │
│  8. NORMALIZE RECORDS                                                       │
│     └─ _normalize_detail_records() ensures consistent schema                │
│     └─ Handle missing fields, type conversions                              │
│                                                                              │
│  9. CLASSIFY QUESTION                                                       │
│     └─ classify_question() determines question type                         │
│     └─ Types: health, forecast, risk, change, entity, comparison,           │
│              impact, design, schedule, location, material, general          │
│     └─ Uses keyword matching and NLP patterns                               │
│                                                                              │
│  10. GENERATE ANSWER BASED ON TYPE                                          │
│      └─ Route to specific generator function:                               │
│         • generate_health_answer()                                          │
│         • generate_forecast_answer()                                        │
│         • generate_risk_answer()                                            │
│         • generate_change_answer()                                          │
│         • generate_entity_answer()                                          │
│         • generate_comparison_answer()                                      │
│         • generate_impact_answer()                                          │
│         • generate_design_answer()                                          │
│         • generate_schedule_answer()                                        │
│         • generate_location_answer()                                        │
│         • generate_material_answer()                                        │
│         • generate_general_answer()                                         │
│                                                                              │
│  11. EACH GENERATOR FUNCTION:                                               │
│      ┌─────────────────────────────────────────────────────────────────┐   │
│      │ a) Compute scoped metrics from detail_records                   │   │
│      │    └─ Only include relevant records for this question           │   │
│      │    └─ Example: For location query, filter by location_id        │   │
│      │                                                                 │   │
│      │ b) Build response using GenerativeResponseBuilder               │   │
│      │    └─ Try LLM first (if API key available)                      │   │
│      │    └─ If LLM fails → FALLBACK to templates                      │   │
│      │                                                                 │   │
│      │ c) Return dict with:                                            │   │
│      │    {                                                            │   │
│      │      "answer": "Natural language response",                     │   │
│      │      "supportingMetrics": {...}                                 │   │
│      │    }                                                            │   │
│      └─────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  12. ERROR HANDLING                                                         │
│      └─ Try/catch around answer generation                                  │
│      └─ If error: return generic "Unable to generate answer" message        │
│      └─ Log error for debugging                                             │
│                                                                              │
│  13. BUILD RESPONSE OBJECT                                                  │
│      └─ Include:                                                            │
│         • question (original)                                              │
│         • answer (generated)                                               │
│         • queryType (classification)                                       │
│         • supportingMetrics (computed)                                     │
│         • mcpContext (for future MCP integration)                          │
│         • dataMode ("blob")                                                │
│         • timestamp                                                        │
│                                                                              │
│  14. RETURN RESPONSE                                                        │
│      └─ JSON response with CORS headers                                     │
│      └─ Status 200 (success) or error code                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React Dashboard) - Response                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  15. RECEIVE RESPONSE                                                       │
│      └─ fetchExplain() promise resolves                                     │
│      └─ Clear timeout                                                       │
│      └─ Extract answer from response                                        │
│                                                                              │
│  16. HANDLE RESPONSE FIELDS                                                 │
│      └─ Primary: res.answer                                                 │
│      └─ Fallback: res.aiInsight                                             │
│      └─ If both missing: buildFallbackAnswer() (client-side)                │
│                                                                              │
│  17. ENHANCE RESPONSE WITH METRICS                                          │
│      └─ If supportingMetrics: append to answer                              │
│      └─ If comparisonMetrics: append comparison data                        │
│      └─ If supplierMetrics: append supplier details                         │
│      └─ If recordComparison: append record changes                          │
│      └─ If explainability.isStale: add data freshness warning               │
│      └─ If confidence < 50%: add confidence warning                         │
│                                                                              │
│  18. BUILD FOLLOW-UP SUGGESTIONS                                            │
│      └─ buildFollowUps() generates next questions                           │
│      └─ Based on question type and context                                  │
│      └─ Display as clickable buttons                                        │
│                                                                              │
│  19. ADD ASSISTANT MESSAGE TO CHAT                                          │
│      └─ setMessages() adds {role: "assistant", content: finalAnswer}        │
│      └─ Include followUps array                                             │
│      └─ Display in UI                                                       │
│                                                                              │
│  20. SET LOADING = FALSE                                                    │
│      └─ Stop showing "Thinking..." spinner                                  │
│      └─ Enable input field                                                  │
│      └─ User can send next question                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Fallback Logic Flow

### Scenario 1: LLM Available (API Key Set)

```
Question → Backend → Classify → Generate Answer
                                    ↓
                            Try LLM (ChatGPT)
                                    ↓
                        ┌───────────┴───────────┐
                        ↓                       ↓
                    SUCCESS              EXCEPTION
                        ↓                       ↓
                  Return LLM        Use Template
                  Response          Response
                        ↓                       ↓
                        └───────────┬───────────┘
                                    ↓
                            Return to Frontend
```

### Scenario 2: LLM Not Available (No API Key)

```
Question → Backend → Classify → Generate Answer
                                    ↓
                        use_llm = False
                                    ↓
                        Use Template
                        Response
                                    ↓
                            Return to Frontend
```

### Scenario 3: LLM Fails (API Error, Timeout, etc.)

```
Question → Backend → Classify → Generate Answer
                                    ↓
                            Try LLM (ChatGPT)
                                    ↓
                        EXCEPTION (API Error)
                                    ↓
                        Log Error
                        Fall back to Template
                                    ↓
                            Return to Frontend
```

### Scenario 4: Frontend Timeout (6 seconds)

```
Question → Frontend sends request
                ↓
        Wait for response (6s timeout)
                ↓
        ┌───────┴───────┐
        ↓               ↓
    RESPONSE        TIMEOUT
        ↓               ↓
    Display       Show timeout
    Answer        message
                  Preserve input
                  for retry
```

---

## Code Flow: GenerativeResponseBuilder

### With LLM Integration

```python
class GenerativeResponseBuilder:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        if use_llm:
            self.llm_service = get_llm_service(use_mock=True)
    
    def build_health_response(self, metrics: Dict) -> str:
        if self.use_llm and self.llm_service:
            try:
                # Try LLM first
                return self.llm_service.generate_response(
                    "What is the current planning health status?",
                    metrics
                )
            except Exception as e:
                # LLM failed, log and fallback
                logger.warning(f"LLM failed: {str(e)}. Using template.")
        
        # Fallback to template
        return self._build_health_response_template(metrics)
    
    def _build_health_response_template(self, metrics: Dict) -> str:
        # Template-based response
        health_score = metrics.get("planningHealth", 50)
        status = self._get_health_status(health_score)
        changed = metrics.get("changedRecordCount", 0)
        total = metrics.get("totalRecords", 1)
        change_rate = (changed / total * 100) if total > 0 else 0
        
        template = random.choice(self.health_templates)
        return template.format(
            health=health_score,
            status=status,
            changed_count=changed,
            total_count=total,
            change_rate=round(change_rate, 1),
            drivers=drivers_str
        )
```

---

## LLM Service Fallback

### LLMService.generate_response()

```python
def generate_response(self, prompt: str, context: Dict) -> str:
    if self.use_mock:
        # Mock mode (for testing without API key)
        return self._generate_mock_response(prompt, context)
    
    try:
        # Try real API call
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[...],
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )
        return response.choices[0].message.content
    
    except Exception as e:
        # API error - exception propagates to caller
        logger.error(f"LLM API error: {str(e)}")
        raise  # Caller catches and falls back to template
```

---

## Error Handling Layers

### Layer 1: LLM Service
- **Error**: API timeout, invalid key, rate limit
- **Action**: Log error, raise exception
- **Fallback**: Caller catches exception

### Layer 2: Response Builder
- **Error**: LLM service exception
- **Action**: Log warning, catch exception
- **Fallback**: Use template-based response

### Layer 3: Backend Endpoint
- **Error**: Response builder exception
- **Action**: Log error, catch exception
- **Fallback**: Return generic "Unable to generate answer"

### Layer 4: Frontend
- **Error**: Backend timeout (6s), network error
- **Action**: Show timeout message
- **Fallback**: buildFallbackAnswer() (client-side template)

---

## Data Flow: Context Passing

### Frontend → Backend

```
CopilotPanel.tsx
    ↓
sendMessage(question)
    ↓
fetchExplain({
    question: "What's the planning health?",
    context: {
        detailRecords: [...],      // Full blob data
        planningHealth: 65,
        changedRecordCount: 5,
        totalRecords: 20,
        riskSummary: {...},
        supplierSummary: {...},
        materialGroupSummary: {...},
        datacenterSummary: {...},
        designSummary: {...},
        rojSummary: {...},
        dataMode: "blob",
        lastRefreshedAt: "2026-04-13T14:30:00Z"
    }
})
    ↓
POST /api/explain
```

### Backend Processing

```
explain() endpoint
    ↓
Extract question & context
    ↓
Load detail_records (from context or snapshot)
    ↓
Normalize records
    ↓
classify_question(question)
    ↓
Route to generator (e.g., generate_health_answer)
    ↓
Compute scoped metrics
    ↓
GenerativeResponseBuilder.build_health_response(metrics)
    ├─ Try LLM
    └─ Fallback to template
    ↓
Return answer + supportingMetrics
```

### Backend → Frontend

```
{
    "question": "What's the planning health?",
    "answer": "Planning health is 65/100 (Acceptable)...",
    "queryType": "health",
    "supportingMetrics": {
        "changedRecordCount": 5,
        "totalRecords": 20,
        "trendDelta": 150,
        "planningHealth": 65
    },
    "mcpContext": {...},
    "dataMode": "blob",
    "timestamp": "2026-04-13T14:30:00Z"
}
```

### Frontend Response Handling

```
CopilotPanel.tsx
    ↓
fetchExplain() resolves
    ↓
Extract answer
    ├─ Primary: res.answer
    ├─ Fallback: res.aiInsight
    └─ Last resort: buildFallbackAnswer()
    ↓
Enhance with metrics
    ├─ supportingMetrics
    ├─ comparisonMetrics
    ├─ supplierMetrics
    └─ recordComparison
    ↓
Generate follow-ups
    ↓
Add to chat messages
    ↓
Display in UI
```

---

## Key Fallback Points

| Layer | Fallback Trigger | Fallback Action | Result |
|-------|------------------|-----------------|--------|
| **LLM Service** | API error, timeout, invalid key | Raise exception | Exception propagates |
| **Response Builder** | LLM exception caught | Use template | Template response |
| **Backend Endpoint** | Response builder exception | Generic message | "Unable to generate answer" |
| **Frontend (6s timeout)** | No response in 6 seconds | Show timeout | Preserve input for retry |
| **Frontend (missing answer)** | res.answer is null | buildFallbackAnswer() | Client-side template |

---

## Testing the Flow

### Test 1: With LLM (API Key Available)
```
Question → LLM generates response → Return to frontend
```

### Test 2: Without LLM (No API Key)
```
Question → Template generates response → Return to frontend
```

### Test 3: LLM Fails
```
Question → LLM error → Catch exception → Template generates response → Return to frontend
```

### Test 4: Frontend Timeout
```
Question → Wait 6s → No response → Show timeout → User can retry
```

### Test 5: Backend Error
```
Question → Backend exception → Generic error message → Return to frontend
```

---

## Summary

**Request Flow:**
1. User types prompt in Copilot panel
2. Frontend sends to `/api/explain` endpoint
3. Backend classifies question
4. Backend generates answer (LLM or template)
5. Backend returns response
6. Frontend displays answer with follow-ups

**Fallback Chain:**
- **Primary**: LLM (ChatGPT) if API key available
- **Secondary**: Template-based response if LLM fails
- **Tertiary**: Generic error message if both fail
- **Quaternary**: Client-side fallback if backend timeout

**Error Handling:**
- LLM errors logged and caught
- Template always available as backup
- Frontend has 6-second timeout protection
- User input preserved on timeout for retry
