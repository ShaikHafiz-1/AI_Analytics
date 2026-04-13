# Copilot Issue - Root Cause Analysis & Fix

## Problem Statement

Copilot is showing repeated generic responses:
```
"Planning health is concerning (37%). 5927 records have changed.
What is the current planning health?
Explainability analysis complete.
What are the top risks?
What's the main issue?
Explainability analysis complete."
```

Instead of answering questions with specific insights.

---

## Root Cause Identified

### The Issue: Hardcoded Response in Backend

**File**: `planning_intelligence/function_app.py`
**Endpoint**: `explain` (Line 227)
**Problem**: Returns hardcoded response instead of actual answer

```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    # ... validation code ...
    
    # Build explainability response
    response = {
        "question": question,
        "answer": "Explainability analysis complete.",  # ❌ HARDCODED!
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

### Why This Happens

1. **Frontend sends question** to `/api/explain` endpoint
2. **Backend receives question** but doesn't process it
3. **Backend returns hardcoded response** "Explainability analysis complete."
4. **Frontend displays hardcoded response** instead of real answer
5. **Fallback answer engine** kicks in and shows generic text

---

## Data Flow Analysis

### Current (Broken) Flow

```
Frontend (CopilotPanel.tsx)
    ↓
User types: "What is the current planning health?"
    ↓
fetchExplain() called
    ↓
POST /api/explain
{
  "question": "What is the current planning health?",
  "context": { ... dashboard data ... }
}
    ↓
Backend (function_app.py - explain endpoint)
    ↓
Receives question ✓
Validates input ✓
BUT: Returns hardcoded response ❌
    ↓
Response:
{
  "question": "What is the current planning health?",
  "answer": "Explainability analysis complete.",  ❌ WRONG!
  "dataMode": "blob"
}
    ↓
Frontend receives response
    ↓
CopilotPanel checks for answer field
    ↓
Displays: "Explainability analysis complete."
    ↓
Fallback answer engine also triggers
    ↓
Shows generic response
    ↓
User sees repeated/generic answers ❌
```

### Expected (Fixed) Flow

```
Frontend (CopilotPanel.tsx)
    ↓
User types: "What is the current planning health?"
    ↓
fetchExplain() called
    ↓
POST /api/explain
{
  "question": "What is the current planning health?",
  "context": { ... dashboard data ... }
}
    ↓
Backend (function_app.py - explain endpoint)
    ↓
Receives question ✓
Validates input ✓
Analyzes question ✓
Queries detail records ✓
Generates specific answer ✓
    ↓
Response:
{
  "question": "What is the current planning health?",
  "answer": "Planning health is 37/100 (Critical). This is driven by 5927 changed records (63% of total). Primary factors: Design changes (45%), Supplier changes (35%), Quantity changes (20%).",
  "supportingMetrics": {
    "planningHealth": 37,
    "changedRecordCount": 5927,
    "totalRecords": 9400
  }
}
    ↓
Frontend receives response
    ↓
CopilotPanel displays answer ✓
    ↓
User sees specific, relevant answer ✓
```

---

## What Needs to Be Fixed

### Backend Issue

The `explain` endpoint needs to:

1. **Parse the question** to understand what user is asking
2. **Query detail records** to get relevant data
3. **Analyze the data** based on question type
4. **Generate specific answer** with metrics
5. **Return structured response** with answer + supporting data

### Current Code (Broken)

```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    # ... validation ...
    
    response = {
        "question": question,
        "answer": "Explainability analysis complete.",  # ❌ HARDCODED
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

### What It Should Do

```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    # ... validation ...
    
    # 1. Parse question
    question_type = classify_question(question)  # health, forecast, risk, etc.
    
    # 2. Get detail records
    detail_records = get_detail_records()
    
    # 3. Analyze based on question type
    if question_type == "health":
        answer = analyze_health(detail_records)
    elif question_type == "forecast":
        answer = analyze_forecast(detail_records)
    elif question_type == "risk":
        answer = analyze_risk(detail_records)
    # ... etc ...
    
    # 4. Build response with metrics
    response = {
        "question": question,
        "answer": answer,  # ✓ SPECIFIC ANSWER
        "supportingMetrics": metrics,
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

---

## Frontend Processing

### How Frontend Handles Response

**File**: `frontend/src/components/CopilotPanel.tsx` (Line 100-150)

```typescript
const res = await fetchExplain({ question: question.trim(), context });

// Gets answer from response
const answer = res.answer || res.aiInsight || buildFallbackAnswer(...);

// Tries to add supporting metrics
const supportingMetrics = (res as any).supportingMetrics;
if (supportingMetrics && answer) {
  finalAnswer = `${answer}\n\n📊 Supporting Metrics:\n...`;
}

// If no answer, uses fallback
if (!answer) {
  const answer = buildFallbackAnswer(question, context, selectedEntity);
}
```

### The Problem

1. Backend returns: `"answer": "Explainability analysis complete."`
2. Frontend displays this hardcoded text
3. Frontend also calls `buildFallbackAnswer()` as fallback
4. Result: User sees generic/repeated responses

---

## Request/Response Trace

### Frontend Request

```json
POST http://localhost:7071/api/explain
{
  "question": "What is the current planning health?",
  "location_id": null,
  "material_group": null,
  "context": {
    "planningHealth": 37,
    "status": "Critical",
    "totalRecords": 9400,
    "changedRecordCount": 5927,
    "riskSummary": { ... },
    "detailRecords": [ ... ]
  }
}
```

### Backend Response (Current - Broken)

```json
{
  "question": "What is the current planning health?",
  "answer": "Explainability analysis complete.",
  "dataMode": "blob",
  "timestamp": "2024-04-13T10:30:00Z"
}
```

### Backend Response (Expected - Fixed)

```json
{
  "question": "What is the current planning health?",
  "answer": "Planning health is 37/100 (Critical). This is driven by 5927 changed records (63% of total). Primary factors: Design changes (45%), Supplier changes (35%), Quantity changes (20%).",
  "supportingMetrics": {
    "planningHealth": 37,
    "changedRecordCount": 5927,
    "totalRecords": 9400,
    "trendDelta": 5000,
    "riskLevel": "High"
  },
  "dataMode": "blob",
  "timestamp": "2024-04-13T10:30:00Z"
}
```

---

## Frontend Display

### Current (Broken)

```
User: "What is the current planning health?"

Copilot: "Explainability analysis complete."

[Fallback answer also shows]
```

### Expected (Fixed)

```
User: "What is the current planning health?"

Copilot: "Planning health is 37/100 (Critical). This is driven by 5927 changed records (63% of total). Primary factors: Design changes (45%), Supplier changes (35%), Quantity changes (20%).

📊 Supporting Metrics:
• Changed: 5927/9400
• Trend: +5,000
• Health: 37/100"
```

---

## Solution

### Step 1: Implement Question Classification

Add to `function_app.py`:

```python
def classify_question(question: str) -> str:
    """Classify question type"""
    q_lower = question.lower()
    
    if any(word in q_lower for word in ["health", "status", "score"]):
        return "health"
    elif any(word in q_lower for word in ["forecast", "trend", "delta"]):
        return "forecast"
    elif any(word in q_lower for word in ["risk", "risky", "danger"]):
        return "risk"
    elif any(word in q_lower for word in ["change", "changed", "supplier", "design"]):
        return "change"
    elif any(word in q_lower for word in ["location", "material", "group"]):
        return "entity"
    else:
        return "general"
```

### Step 2: Implement Answer Generators

Add to `function_app.py`:

```python
def generate_health_answer(detail_records: list, context: dict) -> str:
    """Generate health-specific answer"""
    health = context.get("planningHealth", 0)
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    status = "Critical" if health < 40 else "At Risk" if health < 60 else "Stable" if health < 80 else "Healthy"
    
    return f"Planning health is {health}/100 ({status}). {changed} of {total} records have changed ({changed/total*100:.0f}%)."

def generate_forecast_answer(detail_records: list, context: dict) -> str:
    """Generate forecast-specific answer"""
    forecast_new = context.get("forecastNew", 0)
    forecast_old = context.get("forecastOld", 0)
    delta = forecast_new - forecast_old
    
    return f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. Change: {delta:+,.0f} ({delta/forecast_old*100:+.1f}%)."

def generate_risk_answer(detail_records: list, context: dict) -> str:
    """Generate risk-specific answer"""
    risk_summary = context.get("riskSummary", {})
    high_risk = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    return f"Risk level is {risk_summary.get('level', 'Unknown')}. {high_risk} high-risk records out of {total} total ({high_risk/total*100:.1f}%)."
```

### Step 3: Update Explain Endpoint

Replace the hardcoded response with:

```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """Explainability endpoint - provides detailed explanations"""
    if req.method == "OPTIONS":
        return _cors_response("", 200)
    
    logging.info("Explain endpoint triggered.")
    
    try:
        body = req.get_json()
    except ValueError:
        return _error("Invalid JSON body.", 400)
    
    question = body.get("question", "").strip()
    if not question:
        return _error("question is required", 400)
    
    # Get context
    context = body.get("context", {})
    detail_records = context.get("detailRecords", [])
    
    if not detail_records:
        return _error("No detail records available.", 404)
    
    # Classify question
    q_type = classify_question(question)
    
    # Generate answer based on question type
    if q_type == "health":
        answer = generate_health_answer(detail_records, context)
    elif q_type == "forecast":
        answer = generate_forecast_answer(detail_records, context)
    elif q_type == "risk":
        answer = generate_risk_answer(detail_records, context)
    else:
        answer = generate_general_answer(detail_records, context)
    
    # Build response
    response = {
        "question": question,
        "answer": answer,  # ✓ SPECIFIC ANSWER
        "supportingMetrics": {
            "planningHealth": context.get("planningHealth"),
            "changedRecordCount": context.get("changedRecordCount"),
            "totalRecords": context.get("totalRecords"),
            "trendDelta": context.get("trendDelta"),
            "riskLevel": context.get("riskSummary", {}).get("level")
        },
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

---

## Summary

### Problem
- Backend `explain` endpoint returns hardcoded "Explainability analysis complete."
- Frontend displays this generic response
- User sees repeated/generic answers instead of specific insights

### Root Cause
- Endpoint not implemented to actually answer questions
- No question classification
- No answer generation logic

### Solution
- Implement question classification
- Implement answer generators for each question type
- Update explain endpoint to generate specific answers
- Return structured response with supporting metrics

### Impact
- Copilot will provide specific, relevant answers
- Answers will be grounded in actual data
- User experience will improve significantly

