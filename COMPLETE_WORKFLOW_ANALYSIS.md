# Complete Workflow Analysis: Frontend to Backend

## Overview

This document analyzes the complete data flow from user input in the frontend to backend response, identifying context passing, state management, and potential issues.

---

## 1. FRONTEND WORKFLOW

### 1.1 User Input Flow

```
User Types Question in CopilotPanel
    ↓
sendMessage() callback triggered
    ↓
Question added to chat messages (local state)
    ↓
fetchExplain() called with:
    - question: string
    - context: DashboardContext (from parent)
    ↓
HTTP POST to /api/explain
```

### 1.2 Frontend Context Building

**File**: `frontend/src/pages/DashboardPage.tsx`

```typescript
const context = buildDashboardContext(data);
```

**What's in context**:
```typescript
{
  planningHealth: number,
  totalRecords: number,
  changedRecords: number,
  changeRate: number,
  drivers: {...},
  riskSummary: {...},
  supplierSummary: {...},
  materialSummary: {...},
  detailRecords: [] // ← CRITICAL: May or may not be included
}
```

### 1.3 Frontend API Call

**File**: `frontend/src/services/api.ts`

```typescript
export async function fetchExplain(payload: {
  question: string;
  location_id?: string;
  material_group?: string;
  context?: Partial<DashboardContext>;
}): Promise<ExplainResponse> {
  const res = await fetch(endpoint("explain"), {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
```

**What's sent to backend**:
```json
{
  "question": "Hi",
  "context": {
    "planningHealth": 37,
    "totalRecords": 13148,
    "changedRecords": 2951,
    "changeRate": 22.4,
    "drivers": {...},
    "riskSummary": {...},
    "supplierSummary": {...},
    "materialSummary": {...},
    "detailRecords": [] // ← May be empty or missing!
  }
}
```

### 1.4 Frontend Timeout Handling

**File**: `frontend/src/components/CopilotPanel.tsx`

```typescript
const timeoutId = setTimeout(() => {
  setLoading(false);
  setInput(question.trim());
  setMessages((prev) => [...prev, { 
    role: "assistant", 
    content: "⏱ Request timed out. Your question has been preserved — please try again.", 
    timestamp: Date.now() 
  }]);
}, 6000);  // ← 6 second timeout on frontend
```

**Issue**: Frontend timeout is 6 seconds, but backend timeout is 30 seconds. This can cause frontend to timeout before backend completes.

---

## 2. BACKEND WORKFLOW

### 2.1 Explain Endpoint Entry Point

**File**: `planning_intelligence/function_app.py` (Line 1258)

```python
@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
```

### 2.2 Context Reception

```python
body = req.get_json()
question = body.get("question", "").strip()
context = body.get("context", {})
detail_records = context.get("detailRecords", [])
```

**Problem 1**: Frontend may not send `detailRecords` in context
- Frontend builds context from `DashboardResponse`
- `DashboardResponse` may not include full `detailRecords`
- Backend falls back to loading from snapshot

### 2.3 Fallback to Snapshot

```python
if not detail_records:
    snap = load_snapshot()
    if snap:
        detail_records = snap.get("detailRecords", [])
        context = snap
```

**This is good** - Backend has fallback mechanism

### 2.4 Question Classification

```python
q_type = classify_question(question)
```

**Routing**:
- "greeting" → `generate_greeting_answer()`
- "health" → `generate_health_answer()`
- "forecast" → `generate_forecast_answer()`
- ... (12 types total)
- "general" → `generate_general_answer()`

### 2.5 Answer Generation

Each handler receives:
```python
def generate_*_answer(detail_records: list, context: dict, question: str) -> dict:
```

**Key Point**: Each handler now passes `detail_records` to LLM:
```python
llm_service.generate_response(
    prompt=question,
    context=context,
    detail_records=detail_records  # ← ALL 13,148 records
)
```

### 2.6 LLM Service Processing

**File**: `planning_intelligence/llm_service.py`

```python
def generate_response(self, prompt: str, context: Dict, detail_records: List[Dict] = None) -> str:
    system_message = self._build_system_prompt()
    user_message = self._build_user_prompt(prompt, context, detail_records)
    
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        max_tokens=self.max_tokens,
        timeout=self.timeout  # 30 seconds
    )
```

### 2.7 Response Building

```python
response = {
    "question": question,
    "answer": answer,
    "queryType": q_type,
    "supportingMetrics": supporting_metrics,
    "mcpContext": mcp_context,
    "dataMode": "blob",
    "timestamp": get_last_updated_time(),
}
```

---

## 3. COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Types: "Hi"                                              │
│       ↓                                                         │
│  CopilotPanel.sendMessage()                                    │
│       ↓                                                         │
│  Builds payload:                                               │
│  {                                                             │
│    question: "Hi",                                             │
│    context: {                                                  │
│      planningHealth: 37,                                       │
│      totalRecords: 13148,                                      │
│      changedRecords: 2951,                                     │
│      drivers: {...},                                           │
│      riskSummary: {...},                                       │
│      detailRecords: [] ← ISSUE: May be empty!                 │
│    }                                                           │
│  }                                                             │
│       ↓                                                         │
│  fetchExplain() → HTTP POST /api/explain                       │
│       ↓                                                         │
│  Frontend timeout: 6 seconds ← ISSUE: Too short!              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (Azure Functions)                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  explain() endpoint receives request                           │
│       ↓                                                         │
│  Extract: question, context, detailRecords                     │
│       ↓                                                         │
│  IF detailRecords empty:                                       │
│    Load from snapshot (load_snapshot())                        │
│       ↓                                                         │
│  Normalize records (_normalize_detail_records())               │
│       ↓                                                         │
│  Classify question (classify_question())                       │
│       ↓                                                         │
│  Route to handler:                                             │
│    "greeting" → generate_greeting_answer()                     │
│       ↓                                                         │
│  Handler builds context and calls LLM:                         │
│    llm_service.generate_response(                              │
│      prompt="Hi",                                              │
│      context={...},                                            │
│      detail_records=[...13,148 records...]  ← FULL CONTEXT    │
│    )                                                           │
│       ↓                                                         │
│  LLM Service:                                                  │
│    - Build system prompt (business rules)                      │
│    - Build user prompt (question + metrics + sample records)   │
│    - Call ChatGPT API (30 second timeout)                      │
│    - Retry logic (3 attempts, exponential backoff)             │
│       ↓                                                         │
│  Return response:                                              │
│  {                                                             │
│    "question": "Hi",                                           │
│    "answer": "Hello! I'm your Planning Intelligence Copilot...",
│    "queryType": "greeting",                                    │
│    "supportingMetrics": {...},                                 │
│    "mcpContext": {...},                                        │
│    "dataMode": "blob",                                         │
│    "timestamp": "..."                                          │
│  }                                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (React) - Response Handling                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Receive response                                              │
│       ↓                                                         │
│  Extract: answer, supportingMetrics, followUpQuestions         │
│       ↓                                                         │
│  Add to chat messages                                          │
│       ↓                                                         │
│  Display to user                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. CONTEXT PASSING ANALYSIS

### 4.1 What Context is Passed

**From Frontend to Backend**:
```
✓ question (string)
✓ planningHealth (number)
✓ totalRecords (number)
✓ changedRecords (number)
✓ changeRate (number)
✓ drivers (object)
✓ riskSummary (object)
✓ supplierSummary (object)
✓ materialSummary (object)
? detailRecords (array) - May be empty or missing
```

### 4.2 What Context is Missing

**Issues**:

1. **detailRecords Not Sent from Frontend**
   - Frontend builds context from `DashboardResponse`
   - `DashboardResponse` may not include full `detailRecords`
   - Backend has to load from snapshot (adds latency)

2. **No Conversation History**
   - Each question is independent
   - No context from previous questions
   - LLM doesn't know what was asked before

3. **No User Session ID**
   - No way to track user across requests
   - No way to maintain conversation state
   - Each request is stateless

4. **No Request ID for Tracing**
   - No correlation ID between frontend and backend
   - Hard to debug issues across requests

---

## 5. STATE MANAGEMENT ANALYSIS

### 5.1 Frontend State

**CopilotPanel.tsx**:
```typescript
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [input, setInput] = useState("");
const [loading, setLoading] = useState(false);
const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
```

**State Management**:
- ✓ Chat messages stored locally
- ✓ Input text preserved
- ✓ Loading state tracked
- ✓ Selected entity tracked
- ✗ No persistence (lost on page refresh)
- ✗ No sync with backend

### 5.2 Backend State

**Function App**:
- ✗ No session state
- ✗ No conversation history
- ✗ No user tracking
- ✓ Snapshot-based data (cached)
- ✓ Blob storage as source of truth

### 5.3 State Issues

**Problem 1: No Conversation Context**
```
User: "Hi"
Backend: "Hello! I'm your Planning Intelligence Copilot..."

User: "What about health?"
Backend: Doesn't know this is follow-up to greeting
         Treats as independent question
```

**Problem 2: No Session Tracking**
```
User A: "What's the health?"
User B: "What's the health?"
Backend: Can't distinguish between users
         No way to maintain separate conversations
```

**Problem 3: No Request Correlation**
```
Frontend sends request
Backend processes
If error occurs, hard to trace which request failed
No correlation ID to link frontend and backend logs
```

---

## 6. TIMEOUT ANALYSIS

### 6.1 Timeout Mismatch

| Component | Timeout | Issue |
|-----------|---------|-------|
| Frontend | 6 seconds | Too short for complex queries |
| Backend LLM | 30 seconds | Reasonable for ChatGPT |
| Backend Retry | 3 attempts | Good |

**Problem**: Frontend times out before backend completes

**Scenario**:
1. User asks complex question
2. Backend takes 8 seconds to process
3. Frontend times out at 6 seconds
4. User sees "Request timed out"
5. Backend continues processing (wasted resources)

### 6.2 Recommended Timeout

- Frontend: 35-40 seconds (allow backend 30s + buffer)
- Backend LLM: 30 seconds (current, good)
- Backend Retry: 3 attempts (current, good)

---

## 7. MISSING FEATURES

### 7.1 Conversation History

**Current**: Each question is independent
**Needed**: Track conversation context

```python
# Backend should track:
{
  "session_id": "user-123-session-456",
  "conversation_history": [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "What's the health?"},
    {"role": "assistant", "content": "Planning health is..."}
  ]
}
```

### 7.2 User Session Tracking

**Current**: No user identification
**Needed**: Session ID or user ID

```python
# Backend should receive:
{
  "session_id": "unique-session-identifier",
  "user_id": "optional-user-identifier",
  "question": "Hi"
}
```

### 7.3 Request Correlation

**Current**: No way to link frontend and backend logs
**Needed**: Correlation ID

```python
# Backend should receive:
{
  "correlation_id": "req-123-456-789",
  "question": "Hi"
}
```

### 7.4 Conversation Persistence

**Current**: Chat history lost on page refresh
**Needed**: Store conversation in backend or localStorage

```typescript
// Frontend should persist:
localStorage.setItem("conversation", JSON.stringify(messages));
```

---

## 8. CRITICAL ISSUES FOUND

### Issue 1: Frontend Timeout Too Short ⚠️

**Severity**: HIGH
**Impact**: Users see timeout errors on complex queries
**Fix**: Increase frontend timeout from 6s to 35-40s

```typescript
// Current
}, 6000);

// Should be
}, 35000);  // 35 seconds
```

### Issue 2: detailRecords Not Sent from Frontend ⚠️

**Severity**: MEDIUM
**Impact**: Backend has to load from snapshot (adds latency)
**Fix**: Include detailRecords in frontend context

```typescript
// Current
const res = await fetchExplain({ question: question.trim(), context });

// Should be
const res = await fetchExplain({ 
  question: question.trim(), 
  context: {
    ...context,
    detailRecords: data.detailRecords  // Include full records
  }
});
```

### Issue 3: No Conversation History ⚠️

**Severity**: MEDIUM
**Impact**: LLM can't understand follow-up questions
**Fix**: Pass conversation history to backend

```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  conversation_history: messages  // Include chat history
});
```

### Issue 4: No Session Tracking ⚠️

**Severity**: LOW
**Impact**: Can't track user conversations
**Fix**: Add session ID to requests

```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  session_id: getOrCreateSessionId()
});
```

### Issue 5: No Request Correlation ⚠️

**Severity**: LOW
**Impact**: Hard to debug issues
**Fix**: Add correlation ID

```typescript
const res = await fetchExplain({ 
  question: question.trim(), 
  context,
  correlation_id: generateCorrelationId()
});
```

---

## 9. RECOMMENDATIONS

### Priority 1 (Critical)

1. **Increase Frontend Timeout**
   - Change from 6s to 35-40s
   - Prevents premature timeout errors

2. **Pass detailRecords from Frontend**
   - Include full records in context
   - Reduces backend latency

### Priority 2 (Important)

3. **Add Conversation History**
   - Pass previous messages to backend
   - Enable follow-up question understanding

4. **Add Session Tracking**
   - Generate session ID on frontend
   - Pass with each request
   - Enables conversation persistence

### Priority 3 (Nice to Have)

5. **Add Request Correlation**
   - Generate correlation ID
   - Link frontend and backend logs

6. **Persist Conversation**
   - Store in localStorage or backend
   - Recover on page refresh

---

## 10. IMPLEMENTATION CHECKLIST

### Frontend Changes

- [ ] Increase timeout from 6s to 35-40s
- [ ] Include detailRecords in context
- [ ] Add conversation history to payload
- [ ] Generate and track session ID
- [ ] Generate correlation ID
- [ ] Persist messages to localStorage

### Backend Changes

- [ ] Accept conversation_history in payload
- [ ] Accept session_id in payload
- [ ] Accept correlation_id in payload
- [ ] Pass conversation history to LLM
- [ ] Log correlation ID for tracing
- [ ] Store conversation in database (optional)

---

## Summary

**Current State**: ✓ Working but with limitations
- Questions are answered correctly
- Context is passed but incomplete
- No conversation history
- No session tracking
- Frontend timeout too short

**After Fixes**: ✓ Production-ready
- Full context passed
- Conversation history maintained
- Session tracking enabled
- Proper timeout handling
- Better debugging capability

