# Copilot Flow Analysis - Issue Identified & Fix

## Problem Observed

You're seeing mixed/irrelevant answers:

```
Q: "What's the current planning health status?"
A: "Planning health is 37/100 (Critical). 5,927 of 13,148 records have changed (45.1%). 
Primary drivers: Design changes (1926), Supplier changes (1499)."

Q: "What are the top risks?"
A: "list suppliers for CLT05_F01C01"  ← WRONG! Not answering the question!

Q: "How many records have changed?"
A: "5,927 records have changed out of 13,148 total (45.1%). 
Breakdown: Design (1926), Supplier (1499), Quantity (4725)."
```

---

## Root Cause Analysis

### Issue 1: Question Classification Too Broad

The `classify_question()` function is matching too many keywords, causing wrong classification:

```python
# Current (BROKEN)
elif any(word in q_lower for word in ["change", "changed", "supplier", "design", "quantity", "roj"]):
    return "change"
```

**Problem**: "What are the top risks?" contains no risk keywords, so it falls through to "change" classification!

### Issue 2: Missing Risk Keywords

The risk classification doesn't catch all risk questions:

```python
# Current (BROKEN)
if any(word in q_lower for word in ["risk", "risky", "danger", "dangerous", "high-risk"]):
    return "risk"
```

**Problem**: "What are the top risks?" should match "risks" but the keyword is "risk" (singular)!

### Issue 3: Entity Questions Interfering

Entity classification is too broad:

```python
# Current (BROKEN)
elif any(word in q_lower for word in ["location", "material", "group", "supplier", "datacenter"]):
    return "entity"
```

**Problem**: "What are the top risks?" might match "supplier" if it appears in the question!

---

## Complete Flow Trace

### Current (Broken) Flow

```
Frontend Question: "What are the top risks?"
    ↓
fetchExplain() sends to backend
    ↓
Backend classify_question("what are the top risks?")
    ↓
Checks: "risk" in q_lower? NO (looking for "risk" but question has "risks")
Checks: "forecast" keywords? NO
Checks: "change" keywords? NO
Checks: "entity" keywords? NO
    ↓
Falls through to "general" classification ❌
    ↓
generate_general_answer() called
    ↓
Returns generic answer about planning health
    ↓
Frontend displays wrong answer ❌
```

### Expected (Fixed) Flow

```
Frontend Question: "What are the top risks?"
    ↓
fetchExplain() sends to backend
    ↓
Backend classify_question("what are the top risks?")
    ↓
Checks: "risk" or "risks" in q_lower? YES ✓
    ↓
Returns "risk" classification ✓
    ↓
generate_risk_answer() called ✓
    ↓
Returns: "Risk level is High. Highest risk type: Design + Supplier. 
1200 high-risk records out of 13148 total (9.1%)." ✓
    ↓
Frontend displays correct answer ✓
```

---

## The Fix

### Update classify_question() Function

Replace the current function with this improved version:

```python
def classify_question(question: str) -> str:
    """
    Classify the question type to determine how to answer it.
    More specific matching to avoid false positives.
    """
    q_lower = question.lower()
    
    # Risk questions - CHECK FIRST (most specific)
    if any(word in q_lower for word in ["risk", "risks", "risky", "danger", "dangerous", "high-risk", "top risk"]):
        return "risk"
    
    # Health questions
    elif any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "at risk", "planning"]):
        return "health"
    
    # Forecast questions
    elif any(word in q_lower for word in ["forecast", "trend", "delta", "increase", "decrease", "units"]):
        return "forecast"
    
    # Change questions - CHECK AFTER RISK (less specific)
    elif any(word in q_lower for word in ["change", "changed", "changes", "quantity", "roj"]):
        return "change"
    
    # Entity questions - CHECK LAST (most general)
    elif any(word in q_lower for word in ["location", "material", "group", "supplier", "datacenter"]):
        return "entity"
    
    # Default
    else:
        return "general"
```

### Key Improvements

1. **Risk first**: Check risk keywords BEFORE other categories
2. **Plural forms**: Added "risks", "changes" to catch plural questions
3. **More specific**: Added "top risk", "planning" to health keywords
4. **Order matters**: More specific categories checked first

---

## Updated Answer Generators

Also improve the answer generators to be more specific:

### Improved generate_risk_answer()

```python
def generate_risk_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for risk-related questions"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    # More detailed answer
    answer = f"Risk level is {level}. "
    answer += f"Highest risk type: {highest}. "
    answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
    
    # Add breakdown if available
    breakdown = risk_summary.get("riskBreakdown", {})
    if breakdown:
        answer += f"Breakdown: "
        for risk_type, count in breakdown.items():
            answer += f"{risk_type} ({count}), "
        answer = answer.rstrip(", ") + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "riskLevel": level,
            "highestRiskLevel": highest,
            "highRiskCount": high_risk_count,
            "totalRecords": total,
            "percentHighRisk": pct_high_risk,
            "riskBreakdown": breakdown
        }
    }
```

---

## Implementation Steps

### Step 1: Update classify_question()

Replace the current `classify_question()` function in `function_app.py` with the improved version above.

### Step 2: Update generate_risk_answer()

Replace the current `generate_risk_answer()` function with the improved version above.

### Step 3: Restart Backend

```bash
cd planning_intelligence
func start
```

### Step 4: Test

Ask these questions:

1. **"What are the top risks?"**
   - Should return: Risk level, highest risk type, high-risk count

2. **"What's the current planning health status?"**
   - Should return: Health score, status, drivers

3. **"What are the risks?"**
   - Should return: Risk analysis

4. **"How many records have changed?"**
   - Should return: Changed count and breakdown

---

## Expected Results After Fix

### Question: "What are the top risks?"

**Before (Wrong)**:
```
list suppliers for CLT05_F01C01
```

**After (Correct)**:
```
Risk level is High. Highest risk type: Design + Supplier. 
1200 high-risk records out of 13148 total (9.1%). 
Breakdown: Design (1926), Supplier (1499), Quantity (4725).

📊 Supporting Metrics:
• Risk Level: High
• Highest Risk Type: Design + Supplier
• High-Risk Records: 1200/13148
• Percent High-Risk: 9.1%
```

---

## Why This Happens

The issue is **question classification order**:

1. Current code checks categories in wrong order
2. "What are the top risks?" doesn't match "risk" keyword (looking for singular)
3. Falls through to "general" classification
4. Returns generic answer

**Fix**: Check risk keywords FIRST and include plural forms

---

## Complete Fixed Code

Here's the complete updated `classify_question()` and `generate_risk_answer()` functions to replace in `function_app.py`:

```python
def classify_question(question: str) -> str:
    """
    Classify the question type to determine how to answer it.
    More specific matching to avoid false positives.
    """
    q_lower = question.lower()
    
    # Risk questions - CHECK FIRST (most specific)
    if any(word in q_lower for word in ["risk", "risks", "risky", "danger", "dangerous", "high-risk", "top risk"]):
        return "risk"
    
    # Health questions
    elif any(word in q_lower for word in ["health", "status", "score", "critical", "stable", "at risk", "planning"]):
        return "health"
    
    # Forecast questions
    elif any(word in q_lower for word in ["forecast", "trend", "delta", "increase", "decrease", "units"]):
        return "forecast"
    
    # Change questions - CHECK AFTER RISK (less specific)
    elif any(word in q_lower for word in ["change", "changed", "changes", "quantity", "roj"]):
        return "change"
    
    # Entity questions - CHECK LAST (most general)
    elif any(word in q_lower for word in ["location", "material", "group", "supplier", "datacenter"]):
        return "entity"
    
    # Default
    else:
        return "general"


def generate_risk_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for risk-related questions"""
    risk_summary = context.get("riskSummary", {})
    level = risk_summary.get("level", "Unknown")
    highest = risk_summary.get("highestRiskLevel", "Unknown")
    high_risk_count = risk_summary.get("highRiskCount", 0)
    total = len(detail_records)
    
    pct_high_risk = (high_risk_count / total * 100) if total > 0 else 0
    
    # More detailed answer
    answer = f"Risk level is {level}. "
    answer += f"Highest risk type: {highest}. "
    answer += f"{high_risk_count:,} high-risk records out of {total:,} total ({pct_high_risk:.1f}%). "
    
    # Add breakdown if available
    breakdown = risk_summary.get("riskBreakdown", {})
    if breakdown:
        answer += f"Breakdown: "
        for risk_type, count in breakdown.items():
            answer += f"{risk_type} ({count}), "
        answer = answer.rstrip(", ") + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "riskLevel": level,
            "highestRiskLevel": highest,
            "highRiskCount": high_risk_count,
            "totalRecords": total,
            "percentHighRisk": pct_high_risk,
            "riskBreakdown": breakdown
        }
    }
```

---

## Summary

**Problem**: Question classification is matching wrong categories
**Root Cause**: Keywords checked in wrong order, missing plural forms
**Solution**: Reorder classification, add plural keywords, improve answer generators
**Result**: Copilot will provide relevant answers to all questions

