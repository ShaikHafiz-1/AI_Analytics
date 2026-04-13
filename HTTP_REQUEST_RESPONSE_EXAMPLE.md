# HTTP Request/Response Example - detailRecords Flow

## Complete Example: User Asks "What are the risks?"

---

## Step 1: Frontend Sends HTTP POST Request

### URL
```
POST https://pi-planning-intelligence.azurewebsites.net/api/explain
```

### Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Request Body (AFTER FIX)
```json
{
  "question": "What are the risks?",
  "context": {
    "planningHealth": 75,
    "status": "Stable",
    "forecastNew": 5000,
    "forecastOld": 4800,
    "trendDelta": 200,
    "trendDirection": "Increase",
    "changedRecordCount": 150,
    "totalRecords": 13148,
    "riskSummary": {
      "level": "MEDIUM",
      "highestRiskLevel": "HIGH",
      "highRiskCount": 45,
      "riskBreakdown": {
        "LOW": 12000,
        "MEDIUM": 1000,
        "HIGH": 45,
        "CRITICAL": 3
      },
      "quantityChangedCount": 150,
      "supplierChangedCount": 25,
      "designChangedCount": 10,
      "rojChangedCount": 5
    },
    "aiInsight": "Forecast increased by 200 units",
    "rootCause": "Supplier changes and design updates",
    "recommendedActions": [
      "Review supplier changes",
      "Validate design updates",
      "Monitor forecast trends"
    ],
    "alerts": {
      "shouldTrigger": true,
      "severity": "warning",
      "triggerType": "FORECAST_CHANGE",
      "message": "Forecast changed by 200 units",
      "drivers": {
        "location": "LOC1",
        "supplier": "SUPPLIER1",
        "material": "MAT001",
        "materialGroup": "GROUP1",
        "changeType": "QUANTITY_CHANGE"
      },
      "recommendedAction": "Review changes"
    },
    "drivers": {
      "location": "LOC1",
      "supplier": "SUPPLIER1",
      "material": "MAT001",
      "materialGroup": "GROUP1",
      "changeType": "QUANTITY_CHANGE"
    },
    "filters": {
      "locationId": "LOC1",
      "materialGroup": "GROUP1"
    },
    "dataMode": "blob",
    "lastRefreshedAt": "2024-04-15T10:00:00Z",
    "datacenterSummary": [
      {
        "locationId": "LOC1",
        "dcSite": "DC1",
        "total": 5000,
        "changed": 150
      }
    ],
    "materialGroupSummary": [
      {
        "materialGroup": "GROUP1",
        "total": 3000,
        "changed": 100,
        "qtyChanged": 80,
        "designChanged": 10,
        "supplierChanged": 10
      }
    ],
    "supplierSummary": {
      "changed": 25,
      "topSupplier": "SUPPLIER1"
    },
    "designSummary": {
      "status": "CHANGED",
      "bodChangedCount": 5,
      "formFactorChangedCount": 5
    },
    "rojSummary": {
      "status": "CHANGED",
      "changedCount": 5
    },
    "datacenterCount": 3,
    "materialGroups": ["GROUP1", "GROUP2", "GROUP3"],
    "highRiskRecordCount": 45,
    "detailRecords": [
      {
        "locationId": "LOC1",
        "materialGroup": "GROUP1",
        "materialId": "MAT001",
        "supplier": "SUPPLIER1",
        "forecastQtyCurrent": 1000,
        "forecastQtyPrevious": 950,
        "qtyDelta": 50,
        "rojCurrent": "2024-04-15",
        "rojPrevious": "2024-04-10",
        "bodCurrent": "BOD1",
        "bodPrevious": "BOD1",
        "ffCurrent": "FF1",
        "ffPrevious": "FF1",
        "changeType": "QUANTITY_CHANGE",
        "riskLevel": "MEDIUM",
        "qtyChanged": true,
        "supplierChanged": false,
        "designChanged": false,
        "rojChanged": true,
        "dcSite": "DC1",
        "country": "USA",
        "lastModifiedBy": "SYSTEM",
        "lastModifiedDate": "2024-04-15T10:00:00Z"
      },
      {
        "locationId": "LOC1",
        "materialGroup": "GROUP1",
        "materialId": "MAT002",
        "supplier": "SUPPLIER2",
        "forecastQtyCurrent": 500,
        "forecastQtyPrevious": 480,
        "qtyDelta": 20,
        "rojCurrent": "2024-04-20",
        "rojPrevious": "2024-04-18",
        "bodCurrent": "BOD2",
        "bodPrevious": "BOD2",
        "ffCurrent": "FF2",
        "ffPrevious": "FF2",
        "changeType": "QUANTITY_CHANGE",
        "riskLevel": "LOW",
        "qtyChanged": true,
        "supplierChanged": false,
        "designChanged": false,
        "rojChanged": true,
        "dcSite": "DC1",
        "country": "USA",
        "lastModifiedBy": "SYSTEM",
        "lastModifiedDate": "2024-04-15T10:00:00Z"
      },
      // ... 13,146 more records ...
      {
        "locationId": "LOC3",
        "materialGroup": "GROUP3",
        "materialId": "MAT13148",
        "supplier": "SUPPLIER50",
        "forecastQtyCurrent": 100,
        "forecastQtyPrevious": 100,
        "qtyDelta": 0,
        "rojCurrent": "2024-05-01",
        "rojPrevious": "2024-05-01",
        "bodCurrent": "BOD1",
        "bodPrevious": "BOD1",
        "ffCurrent": "FF1",
        "ffPrevious": "FF1",
        "changeType": "NO_CHANGE",
        "riskLevel": "LOW",
        "qtyChanged": false,
        "supplierChanged": false,
        "designChanged": false,
        "rojChanged": false,
        "dcSite": "DC3",
        "country": "GERMANY",
        "lastModifiedBy": "SYSTEM",
        "lastModifiedDate": "2024-04-10T10:00:00Z"
      }
    ]
  }
}
```

### Request Size
- **Total Size**: ~5-10 MB (compressed)
- **Records**: 13,148
- **Fields per Record**: 22

---

## Step 2: Backend Processes Request

### Backend Code (explain endpoint)
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    """Explainability endpoint"""
    
    # Parse request
    body = req.get_json()
    question = body.get("question", "").strip()
    context = body.get("context", {})
    
    # Extract detailRecords from context
    detail_records = context.get("detailRecords", [])
    
    logging.info(f"Question: {question}")
    logging.info(f"Processing question with {len(detail_records)} records")
    # ↑ Logs: "Processing question with 13148 records"
    
    # If no records in context, try to load from snapshot (fallback)
    if not detail_records:
        snap = load_snapshot()
        if snap:
            detail_records = snap.get("detailRecords", [])
            context = snap
    
    if not detail_records:
        return _error("No detail records available", 404)
    
    # Normalize records
    detail_records = _normalize_detail_records(detail_records)
    
    # Classify question
    q_type = classify_question(question)  # → "risk"
    
    # Generate answer
    result = generate_risk_answer(detail_records, context)
    
    # Build response
    response = {
        "question": question,
        "answer": result.get("answer"),
        "queryType": q_type,
        "supportingMetrics": result.get("supportingMetrics"),
        "dataMode": "blob",
        "timestamp": get_last_updated_time(),
    }
    
    return _cors_response(json.dumps(response, default=str))
```

### Processing Steps
1. ✅ Receives request with detailRecords
2. ✅ Extracts detailRecords from context
3. ✅ Logs: "Processing question with 13148 records"
4. ✅ Classifies question as "risk"
5. ✅ Calls generate_risk_answer()
6. ✅ Passes detailRecords to answer function
7. ✅ Answer function calls ChatGPT with full context
8. ✅ ChatGPT analyzes 13,148 records
9. ✅ Generates intelligent response

---

## Step 3: Backend Returns HTTP Response

### Response Headers
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

### Response Body
```json
{
  "question": "What are the risks?",
  "answer": "Based on the analysis of 13,148 records, the top risks are:\n\n1. **Supplier Changes (25 records)**: SUPPLIER1 has changed for 25 materials, affecting forecast accuracy. Recommendation: Validate supplier quality and lead times.\n\n2. **Design Changes (10 records)**: BOD and Form Factor changes detected for 10 materials. Recommendation: Review design impact on supply chain.\n\n3. **ROJ Changes (5 records)**: Receipt of Goods dates have shifted for 5 materials. Recommendation: Coordinate with suppliers on delivery schedules.\n\n4. **Quantity Changes (150 records)**: Forecast quantities changed by 200 units total. Recommendation: Review demand forecast accuracy.\n\nOverall Risk Level: MEDIUM\nHigh Risk Records: 45\nCritical Records: 3\n\nImmediate Actions:\n- Review the 3 critical records\n- Validate supplier changes\n- Coordinate with planning team on forecast changes",
  "queryType": "risk",
  "supportingMetrics": {
    "changedRecordCount": 150,
    "totalRecords": 13148,
    "trendDelta": 200,
    "planningHealth": 75
  },
  "mcpContext": {
    "computedMetrics": {
      "totalRecords": 13148,
      "changedRecords": 150,
      "changeRate": 1.14,
      "riskLevel": "MEDIUM",
      "healthScore": 75
    },
    "drivers": {
      "location": "LOC1",
      "supplier": "SUPPLIER1",
      "material": "MAT001",
      "materialGroup": "GROUP1",
      "changeType": "QUANTITY_CHANGE"
    },
    "riskSummary": {
      "level": "MEDIUM",
      "highestRiskLevel": "HIGH",
      "highRiskCount": 45,
      "riskBreakdown": {
        "LOW": 12000,
        "MEDIUM": 1000,
        "HIGH": 45,
        "CRITICAL": 3
      }
    },
    "blobFileName": "current.csv",
    "lastRefreshed": "2024-04-15T10:00:00Z"
  },
  "dataMode": "blob",
  "timestamp": "2024-04-15T10:00:00Z"
}
```

### Response Size
- **Total Size**: ~2-5 KB
- **Answer**: ~1-2 KB
- **Metrics**: ~1-2 KB

---

## Step 4: Frontend Receives Response

### Frontend Code (CopilotPanel)
```typescript
try {
  const res = await fetchExplain({ 
    question: question.trim(), 
    context: { 
      ...context, 
      detailRecords: context.detailRecords || [] 
    } 
  });
  
  clearTimeout(timeoutId);
  
  // Extract response fields
  const answer = res.answer || res.aiInsight || buildFallbackAnswer(...);
  const followUps = res.followUpQuestions || buildFollowUps(...);
  
  // Display response
  setMessages((prev) => [...prev, { 
    role: "assistant", 
    content: answer, 
    timestamp: Date.now(), 
    followUps 
  }]);
  
} catch (error) {
  clearTimeout(timeoutId);
  // Error handling...
}
```

### Display to User
```
User: "What are the risks?"