# Copilot Fix - Implementation Guide

## Overview

The Copilot is showing generic responses because the backend `explain` endpoint returns a hardcoded answer instead of actually processing the question.

**Fix**: Implement proper question classification and answer generation in the backend.

---

## Files to Modify

### 1. `planning_intelligence/function_app.py`

Add these functions before the `explain` endpoint:

```python
# ============================================================================
# Question Classification & Answer Generation
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

## Update the Explain Endpoint

Replace the current `explain` function with:

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

## Testing the Fix

### Step 1: Restart Backend

```bash
cd planning_intelligence
func start
```

### Step 2: Open Frontend

```
http://localhost:3000
```

### Step 3: Test Copilot

Click "Ask Copilot" and try these questions:

1. **"What is the current planning health?"**
   - Expected: Specific health score, status, and drivers

2. **"What is the current forecast?"**
   - Expected: Forecast values, delta, and trend

3. **"What are the top risks?"**
   - Expected: Risk level, high-risk count, breakdown

4. **"How many records have changed?"**
   - Expected: Changed count, percentage, breakdown by type

---

## Expected Results

### Before Fix
```
User: "What is the current planning health?"
Copilot: "Explainability analysis complete."
```

### After Fix
```
User: "What is the current planning health?"
Copilot: "Planning health is 37/100 (Critical). 5927 of 9400 records have changed (63.1%). 
Primary drivers: Design changes (2500), Supplier changes (2100).

📊 Supporting Metrics:
• Planning Health: 37/100
• Changed Records: 5927/9400
• Design Changes: 2500
• Supplier Changes: 2100"
```

---

## Verification Checklist

- [ ] Backend restarted
- [ ] Frontend loaded
- [ ] Copilot opens
- [ ] Health question returns specific answer
- [ ] Forecast question returns specific answer
- [ ] Risk question returns specific answer
- [ ] Change question returns specific answer
- [ ] Supporting metrics display
- [ ] No "Explainability analysis complete" message
- [ ] Answers match dashboard data

---

## Troubleshooting

### Issue: Still Showing Generic Response
- **Fix**: Ensure backend was restarted after code changes
- **Check**: Backend logs for errors
- **Verify**: Code changes were saved

### Issue: Error in Backend Logs
- **Fix**: Check Python syntax
- **Verify**: All functions are properly indented
- **Check**: No missing imports

### Issue: Answers Don't Match Dashboard
- **Fix**: Verify context is being passed correctly
- **Check**: Detail records are populated
- **Verify**: Calculations match dashboard logic

---

## Code Location Reference

### File: `planning_intelligence/function_app.py`

**Add these functions** (before the `explain` endpoint):
- `classify_question()`
- `generate_health_answer()`
- `generate_forecast_answer()`
- `generate_risk_answer()`
- `generate_change_answer()`
- `generate_general_answer()`

**Replace the `explain` endpoint** (around line 227):
- Remove hardcoded response
- Add question classification
- Add answer generation logic
- Return structured response

---

## Next Steps

1. ✅ Add helper functions to `function_app.py`
2. ✅ Replace `explain` endpoint
3. ✅ Restart backend
4. ✅ Test with sample questions
5. ✅ Verify answers are specific and accurate
6. ✅ Check supporting metrics display

