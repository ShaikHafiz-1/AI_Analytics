# Copilot Fix - Complete Code to Copy-Paste

## Overview

This document contains the complete code to fix the Copilot issue. Copy and paste into `planning_intelligence/function_app.py`.

---

## Step 1: Add Helper Functions

Add these functions to `planning_intelligence/function_app.py` **BEFORE** the `explain` endpoint (before line 227).

### Location in File

Find this line:
```python
@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
```

Add all the code below **BEFORE** this line.

---

## Complete Code to Add

```python
# ============================================================================
# COPILOT: Question Classification & Answer Generation
# ============================================================================

def classify_question(question: str) -> str:
    """
    Classify the question type to determine how to answer it.
    Returns: "health", "forecast", "risk", "change", "entity", or "general"
    """
    q_lower = question.lower()
    
    # Health questions
    if any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "at risk"]):
        return "health"
    
    # Forecast questions
    elif any(word in q_lower for word in ["forecast", "trend", "delta", "change", "increase", "decrease"]):
        return "forecast"
    
    # Risk questions
    elif any(word in q_lower for word in ["risk", "risky", "danger", "dangerous", "high-risk"]):
        return "risk"
    
    # Change questions
    elif any(word in q_lower for word in ["change", "changed", "supplier", "design", "quantity", "roj"]):
        return "change"
    
    # Entity questions (location, material, supplier)
    elif any(word in q_lower for word in ["location", "material", "group", "supplier", "datacenter"]):
        return "entity"
    
    # Default
    else:
        return "general"


def generate_health_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for health-related questions"""
    health = context.get("planningHealth", 0)
    status = context.get("status", "Unknown")
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    
    answer = f"Planning health is {health}/100 ({status}). {changed:,} of {total:,} records have changed ({pct_changed:.1f}%). "
    answer += f"Primary drivers: Design changes ({design_changes}), Supplier changes ({supplier_changes})."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "planningHealth": health,
            "status": status,
            "changedRecordCount": changed,
            "totalRecords": total,
            "designChanges": design_changes,
            "supplierChanges": supplier_changes
        }
    }


def generate_forecast_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for forecast-related questions"""
    forecast_new = context.get("forecastNew", 0)
    forecast_old = context.get("forecastOld", 0)
    delta = context.get("trendDelta", 0)
    trend = context.get("trendDirection", "Stable")
    
    pct_change = (delta / forecast_old * 100) if forecast_old > 0 else 0
    
    answer = f"Current forecast is {forecast_new:,.0f} units. Previous was {forecast_old:,.0f} units. "
    answer += f"Change: {delta:+,.0f} units ({pct_change:+.1f}%). Trend: {trend}."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "forecastNew": forecast_new,
            "forecastOld": forecast_old,
            "trendDelta": delta,
            "trendDirection": trend,
            "percentChange": pct_change
        }
    }


def generate_risk_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for risk-related questions"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    answer = f"Risk level is {level}. Highest risk type: {highest}. "
    answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%)."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "riskLevel": level,
            "highestRiskLevel": highest,
            "highRiskCount": high_risk_count,
            "totalRecords": total,
            "percentHighRisk": pct_high_risk
        }
    }


def generate_change_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for change-related questions"""
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    risk_summary = context.get("riskSummary", {})
    design_changes = risk_summary.get("designChangedCount", 0)
    supplier_changes = risk_summary.get("supplierChangedCount", 0)
    quantity_changes = risk_summary.get("quantityChangedCount", 0)
    
    pct_changed = (changed / total * 100) if total > 0 else 0
    
    answer = f"{changed:,} records have changed out of {total:,} total ({pct_changed:.1f}%). "
    answer += f"Breakdown: Design ({design_changes}), Supplier ({supplier_changes}), Quantity ({quantity_changes})."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "changedRecordCount": changed,
            "totalRecords": total,
            "percentChanged": pct_changed,
            "designChanges": design_changes,
            "supplierChanges": supplier_changes,
            "quantityChanges": quantity_changes
        }
    }


def generate_general_answer(detail_records: list, context: dict) -> dict:
    """Generate general answer when question type is unclear"""
    health = context.get("planningHealth", 0)
    total = len(detail_records)
    changed = sum(1 for r in detail_records if r.get("changed"))
    
    answer = f"Planning health is {health}/100. {changed:,} of {total:,} records have changed. "
    answer += "Ask about health, forecast, risks, or changes for more details."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "planningHealth": health,
            "changedRecordCount": changed,
            "totalRecords": total
        }
    }
```

---

## Step 2: Replace the Explain Endpoint

Find this function (around line 227):

```python
@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Explainability endpoint - provides detailed explanations for dashboard insights.
    """
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
    
    # Get detail records from request or context
    detail_records = body.get("detailRecords", [])
    if not detail_records:
        context = body.get("context", {})
        detail_records = context.get("detailRecords", [])
    
    # If still no records, try loading from snapshot
    if not detail_records:
        snap = load_snapshot()
        if snap:
            detail_records = snap.get("detailRecords", [])
    
    if not detail_records:
        return _error("No detail records available. Provide detailRecords or run daily-refresh.", 404)
    
    # Normalize records
    detail_records = _normalize_detail_records(detail_records)
    
    # Build explainability response
    response = {
        "question": question,
        "answer": "Explainability analysis complete.",
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

**Replace it with this:**

```python
@app.route(route="explain", methods=["POST", "OPTIONS"])
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Explainability endpoint - provides detailed explanations for dashboard insights.
    Analyzes questions and returns specific, data-driven answers.
    """
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
    
    logging.info(f"Question: {question}")
    
    # Get context from request
    context = body.get("context", {})
    detail_records = context.get("detailRecords", [])
    
    # If no records in context, try to load from snapshot
    if not detail_records:
        snap = load_snapshot()
        if snap:
            detail_records = snap.get("detailRecords", [])
            context = snap
    
    if not detail_records:
        logging.warning("No detail records available")
        return _error("No detail records available. Run daily-refresh first.", 404)
    
    logging.info(f"Processing question with {len(detail_records)} records")
    
    # Normalize records
    detail_records = _normalize_detail_records(detail_records)
    
    # Classify question
    q_type = classify_question(question)
    logging.info(f"Question type: {q_type}")
    
    # Generate answer based on question type
    try:
        if q_type == "health":
            result = generate_health_answer(detail_records, context)
        elif q_type == "forecast":
            result = generate_forecast_answer(detail_records, context)
        elif q_type == "risk":
            result = generate_risk_answer(detail_records, context)
        elif q_type == "change":
            result = generate_change_answer(detail_records, context)
        else:
            result = generate_general_answer(detail_records, context)
        
        answer = result.get("answer", "Unable to generate answer")
        supporting_metrics = result.get("supportingMetrics", {})
        
        logging.info(f"Generated answer: {answer[:100]}...")
        
    except Exception as e:
        logging.error(f"Error generating answer: {str(e)}")
        answer = "Unable to generate answer. Please try a different question."
        supporting_metrics = {}
    
    # Build response
    response = {
        "question": question,
        "answer": answer,
        "supportingMetrics": supporting_metrics,
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    logging.info("Explain endpoint returning response")
    return _cors_response(json.dumps(response, default=str))
```

---

## Step 3: Verify Changes

### Check 1: Helper Functions Added
- [ ] `classify_question()` function exists
- [ ] `generate_health_answer()` function exists
- [ ] `generate_forecast_answer()` function exists
- [ ] `generate_risk_answer()` function exists
- [ ] `generate_change_answer()` function exists
- [ ] `generate_general_answer()` function exists

### Check 2: Explain Endpoint Updated
- [ ] Old hardcoded response removed
- [ ] Question classification added
- [ ] Answer generation logic added
- [ ] Supporting metrics included
- [ ] Error handling in place

---

## Step 4: Restart Backend

```bash
cd planning_intelligence
func start
```

---

## Step 5: Test

1. Open http://localhost:3000
2. Click "Ask Copilot"
3. Ask: "What is the current planning health?"
4. Verify: Specific answer with metrics

---

## Expected Output

### Question
```
"What is the current planning health?"
```

### Response
```
{
  "question": "What is the current planning health?",
  "answer": "Planning health is 37/100 (Critical). 5927 of 9400 records have changed (63.1%). Primary drivers: Design changes (2500), Supplier changes (2100).",
  "supportingMetrics": {
    "planningHealth": 37,
    "status": "Critical",
    "changedRecordCount": 5927,
    "totalRecords": 9400,
    "designChanges": 2500,
    "supplierChanges": 2100
  },
  "dataMode": "blob",
  "timestamp": "2024-04-13T10:30:00Z"
}
```

### Frontend Display
```
Planning health is 37/100 (Critical). 5927 of 9400 records have changed (63.1%). 
Primary drivers: Design changes (2500), Supplier changes (2100).

📊 Supporting Metrics:
• Planning Health: 37/100
• Changed Records: 5927/9400
• Design Changes: 2500
• Supplier Changes: 2100
```

---

## Troubleshooting

### Issue: Syntax Error
- **Check**: Indentation is correct
- **Verify**: All functions are at module level (not nested)
- **Fix**: Copy code again carefully

### Issue: Still Showing Generic Response
- **Check**: Backend was restarted
- **Verify**: Code changes were saved
- **Fix**: Clear browser cache (Ctrl+Shift+Delete)

### Issue: Error in Backend Logs
- **Check**: Python syntax
- **Verify**: All imports are present
- **Fix**: Check for typos in function names

---

## Summary

1. ✅ Add 6 helper functions before `explain` endpoint
2. ✅ Replace `explain` endpoint with new implementation
3. ✅ Restart backend
4. ✅ Test with sample questions
5. ✅ Verify answers are specific and accurate

**That's it! Copilot will now provide specific, data-driven answers!**

