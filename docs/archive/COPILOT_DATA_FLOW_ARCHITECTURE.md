# Copilot Real-Time Answers: Complete Data Flow & Architecture

## System Overview

The Copilot Real-Time Answers system processes natural language questions and returns data-driven answers. It consists of two main data flows:

1. **Dashboard Data Flow** - Loads and caches planning data
2. **NLP Query Flow** - Processes natural language questions

---

## 1. DASHBOARD DATA FLOW

### Entry Point: `planning_dashboard_v2` Endpoint

```
Frontend (React)
    ↓
    POST /api/planning-dashboard-v2
    {
      location_id?: string,
      material_group?: string
    }
    ↓
function_app.planning_dashboard_v2()
    ↓
    ┌─────────────────────────────────────┐
    │ Try Load Cached Snapshot (FAST)     │
    │ snapshot_store.load_snapshot()      │
    └─────────────────────────────────────┘
         ↓ (if exists)
    Return cached data with filters applied
    
    ↓ (if NOT exists)
    
    ┌─────────────────────────────────────┐
    │ Load from Azure Blob (SLOW)         │
    │ blob_loader.load_current_previous() │
    └─────────────────────────────────────┘
         ↓
    Download current.csv from blob
    Download previous.csv from blob
         ↓
    ┌─────────────────────────────────────┐
    │ Normalize Data                      │
    │ normalizer.normalize_rows()         │
    │ - Convert CSV to dict format        │
    │ - Standardize field names           │
    │ - Handle missing values             │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Filter Records                      │
    │ filters.filter_records()            │
    │ - By location_id (if provided)      │
    │ - By material_group (if provided)   │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Compare Current vs Previous         │
    │ comparator.compare_records()        │
    │ - Detect changes                    │
    │ - Compute deltas                    │
    │ - Identify change drivers           │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Build Response                      │
    │ response_builder.build_response()   │
    │ - Compute KPIs                      │
    │ - Build summaries                   │
    │ - Compute health score              │
    │ - Identify risk levels              │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Cache Snapshot                      │
    │ snapshot_store.save_snapshot()      │
    │ - Save to /home/data/               │
    │ - Add metadata (timestamp, mode)    │
    └─────────────────────────────────────┘
         ↓
    Return JSON response to frontend
    {
      dataMode: "blob" | "cached",
      lastRefreshedAt: ISO timestamp,
      planningHealth: 0-100,
      changedRecordCount: number,
      summaryTiles: {...},
      detailRecords: [...],
      ...
    }
```

### Data Structures

**Input (from Blob)**:
```
current.csv / previous.csv
├── LOCID (Location ID)
├── PRDID (Material ID)
├── GSCEQUIPCAT (Equipment Category)
├── LOCFR (Supplier)
├── GSCFSCTQTY (Forecast Quantity)
├── GSCCONROJDATE (ROJ Date)
├── ZCOIBODVER (BOD)
├── ZCOIFORMFACT (Form Factor)
└── ... (other SAP fields)
```

**After Normalization**:
```python
{
  "locationId": "CYS20_F01C01",
  "materialGroup": "UPS",
  "materialId": "MAT-101",
  "supplier": "SUP-001",
  "forecastQty": 100,
  "roj": "2024-04-15",
  "bod": "2024-04-10",
  "formFactor": "Standard",
  "changed": True,
  "qtyChanged": True,
  "supplierChanged": False,
  "designChanged": False,
  "scheduleChanged": False,
  "qtyDelta": 50,
  "riskLevel": "High",
  "changeType": "Quantity Change"
}
```

**After Comparison**:
```python
ComparedRecord {
  location_id: "CYS20_F01C01",
  material_group: "UPS",
  material_id: "MAT-101",
  supplier_current: "SUP-001",
  supplier_previous: "SUP-002",
  forecast_qty_current: 100,
  forecast_qty_previous: 50,
  qty_changed: True,
  qty_delta: 50,
  supplier_changed: True,
  design_changed: False,
  roj_changed: False,
  risk_level: "High",
  change_type: "Supplier Change"
}
```

**Final Response**:
```json
{
  "dataMode": "blob",
  "lastRefreshedAt": "2024-04-11T10:30:00Z",
  "planningHealth": 75,
  "changedRecordCount": 42,
  "summaryTiles": {
    "totalRecords": 500,
    "changedRecords": 42,
    "changeRate": 8.4,
    "topRisks": ["Supplier Change", "Quantity Change"],
    "healthTrend": "Stable"
  },
  "detailRecords": [
    {
      "locationId": "CYS20_F01C01",
      "materialGroup": "UPS",
      "materialId": "MAT-101",
      "supplier": "SUP-001",
      "changed": true,
      "changeType": "Supplier Change",
      "riskLevel": "High"
    },
    ...
  ]
}
```

---

## 2. NLP QUERY FLOW

### Entry Point: `planning_intelligence_nlp` Endpoint

```
Frontend (React) - Copilot Panel
    ↓
    POST /api/planning_intelligence_nlp
    {
      question: "Why is CYS20_F01C01 risky?",
      detail_records: [...],
      conversation_history: [...]
    }
    ↓
function_app.planning_intelligence_nlp()
    ↓
nlp_endpoint.handle_nlp_query()
    ↓
NLPEndpointHandler.process_question()
    ↓
    ┌─────────────────────────────────────┐
    │ Check if Out-of-Scope               │
    │ is_out_of_scope(question)           │
    │ Keywords: "joke", "weather", etc.   │
    └─────────────────────────────────────┘
         ↓ (if out-of-scope)
    Return: "I'm a Planning Intelligence assistant..."
    
    ↓ (if in-scope)
    
    ┌─────────────────────────────────────┐
    │ Check if Planning Question          │
    │ is_planning_question(question)      │
    │ Keywords: "planning", "risk", etc.  │
    └─────────────────────────────────────┘
         ↓ (if NOT planning)
    Return: "Could you rephrase it to be more specific..."
    
    ↓ (if planning question)
    
    ┌─────────────────────────────────────┐
    │ Try Azure OpenAI (if available)     │
    │ azure_openai_integration.py         │
    │ - Extract intent & entities         │
    │ - Confidence scoring                │
    └─────────────────────────────────────┘
         ↓ (if Azure OpenAI available)
    Intent: "root_cause" | "comparison" | "why_not" | "traceability" | "summary"
    Entities: {LOCID: ["CYS20_F01C01"], ...}
    Confidence: 0.95
    
    ↓ (if Azure OpenAI fails or unavailable)
    
    ┌─────────────────────────────────────┐
    │ Fall Back to Rule-Based NLP         │
    │ phase1_core_functions.py            │
    │ - QuestionClassifier.classify()     │
    │ - ScopeExtractor.extract_scope()    │
    └─────────────────────────────────────┘
         ↓
    Query Type: "root_cause"
    Scope Type: "location"
    Scope Value: "CYS20_F01C01"
    
    ↓
    ┌─────────────────────────────────────┐
    │ Determine Answer Mode               │
    │ AnswerModeDecider.determine()       │
    │ - "summary" (overview)              │
    │ - "investigate" (detailed)          │
    │ - "compare" (side-by-side)          │
    └─────────────────────────────────────┘
         ↓
    Answer Mode: "investigate"
    
    ↓
    ┌─────────────────────────────────────┐
    │ Compute Scoped Metrics              │
    │ ScopedMetricsComputer.compute()     │
    │ - Filter records by scope           │
    │ - Compute metrics for scope         │
    │ - Identify drivers                  │
    └─────────────────────────────────────┘
         ↓
    Metrics: {
      filteredRecordsCount: 15,
      changedCount: 8,
      changeRate: 53.3,
      scopedDrivers: {
        primary: "supplier",
        quantity: 3,
        supplier: 8,
        design: 2,
        schedule: 1
      }
    }
    
    ↓
    ┌─────────────────────────────────────┐
    │ Generate Answer                     │
    │ AnswerTemplateRouter.generate()     │
    │ phase2_answer_templates.py          │
    │ - Select template by query type     │
    │ - Fill template with metrics        │
    │ - Format for readability            │
    └─────────────────────────────────────┘
         ↓
    Answer: "📊 CYS20_F01C01 is risky due to supplier changes..."
    
    ↓
    ┌─────────────────────────────────────┐
    │ Add to Conversation History         │
    │ - Keep last 10 turns                │
    │ - Add timestamp                     │
    └─────────────────────────────────────┘
    
    ↓
    Return JSON response to frontend
    {
      question: "Why is CYS20_F01C01 risky?",
      answer: "📊 CYS20_F01C01 is risky due to supplier changes...",
      queryType: "root_cause",
      scopeType: "location",
      scopeValue: "CYS20_F01C01",
      answerMode: "investigate",
      confidence: 0.95,
      conversationHistory: [...]
    }
```

### Data Structures

**Input**:
```json
{
  "question": "Why is CYS20_F01C01 risky?",
  "detail_records": [
    {
      "locationId": "CYS20_F01C01",
      "materialGroup": "UPS",
      "materialId": "MAT-101",
      "supplier": "SUP-001",
      "changed": true,
      "changeType": "Supplier Change",
      "riskLevel": "High"
    },
    ...
  ],
  "conversation_history": []
}
```

**Processing Steps**:

1. **Question Classification** (Phase 1)
   ```python
   query_type = "root_cause"  # Why is X risky?
   ```

2. **Scope Extraction** (Phase 1)
   ```python
   scope_type = "location"
   scope_value = "CYS20_F01C01"
   ```

3. **Answer Mode Decision** (Phase 1)
   ```python
   answer_mode = "investigate"  # Detailed analysis
   ```

4. **Scoped Metrics Computation** (Phase 1)
   ```python
   metrics = {
     "filteredRecordsCount": 15,
     "changedCount": 8,
     "changeRate": 53.3,
     "scopedDrivers": {
       "primary": "supplier",
       "quantity": 3,
       "supplier": 8,
       "design": 2,
       "schedule": 1
     }
   }
   ```

5. **Answer Generation** (Phase 2)
   ```python
   template = "root_cause_investigate"
   answer = template.format(
     entity="CYS20_F01C01",
     metrics=metrics,
     scope_type="location"
   )
   ```

**Output**:
```json
{
  "question": "Why is CYS20_F01C01 risky?",
  "answer": "📊 CYS20_F01C01 is risky due to supplier changes (8 records affected, 53.3% change rate). Primary driver: Supplier changes (8 records). Secondary drivers: Quantity changes (3 records), Design changes (2 records). Recommendation: Review supplier changes and validate new suppliers.",
  "queryType": "root_cause",
  "scopeType": "location",
  "scopeValue": "CYS20_F01C01",
  "answerMode": "investigate",
  "confidence": 0.95,
  "conversationHistory": [
    {
      "question": "Why is CYS20_F01C01 risky?",
      "answer": "📊 CYS20_F01C01 is risky due to supplier changes...",
      "queryType": "root_cause",
      "timestamp": "2024-04-11T10:30:00Z"
    }
  ]
}
```

---

## 3. COUPLING ANALYSIS

### Tight Coupling (Necessary)

**Phase 1 → Phase 2 → Phase 3**
- Phase 1 outputs (query_type, scope_type, metrics) are inputs to Phase 2
- Phase 2 outputs (answer) are inputs to Phase 3
- **Reason**: Sequential pipeline, each phase depends on previous
- **Status**: ✅ Acceptable - by design

**NLP Pipeline → Detail Records**
- NLP pipeline requires detail_records from frontend
- **Reason**: Need actual data to compute metrics
- **Status**: ✅ Acceptable - necessary for data-driven answers

**Azure OpenAI → Fallback to Rule-Based**
- If Azure OpenAI fails, system falls back to rule-based NLP
- **Reason**: Graceful degradation
- **Status**: ✅ Acceptable - improves reliability

### Loose Coupling (Good)

**Frontend ↔ Backend**
- Frontend calls two independent endpoints: `planning_dashboard_v2` and `planning_intelligence_nlp`
- Backend doesn't know about frontend implementation
- **Status**: ✅ Good - clean separation

**Blob Storage ↔ Snapshot Cache**
- Dashboard can use either blob or cache
- Snapshot is optional optimization
- **Status**: ✅ Good - flexible data source

**Azure OpenAI ↔ Rule-Based NLP**
- Two independent implementations
- Can switch between them
- **Status**: ✅ Good - pluggable

**Analytics ↔ Response Building**
- Analytics computes metrics
- Response builder formats metrics
- No direct dependency
- **Status**: ✅ Good - separation of concerns

### Problematic Coupling (To Avoid)

**❌ NOT PRESENT**: Direct database queries in response generation
- All data comes from detail_records parameter
- No hidden data sources

**❌ NOT PRESENT**: Hardcoded values in templates
- All values come from metrics
- Templates are data-driven

**❌ NOT PRESENT**: LLM making calculations
- LLM only generates text
- All calculations done by deterministic engine
- **Status**: ✅ Good - maintains correctness

---

## 4. CONTROL FLOW

### Request Routing

```
HTTP Request
    ↓
Azure Functions Router
    ├─ POST /api/planning-dashboard-v2
    │  └─ planning_dashboard_v2()
    │
    └─ POST /api/planning_intelligence_nlp
       └─ planning_intelligence_nlp()
           └─ handle_nlp_query()
               └─ NLPEndpointHandler.process_question()
```

### Error Handling

```
Any Step
    ↓
    ┌─ Exception?
    │
    ├─ YES: Log error
    │       Return error response
    │       (with HTTP status code)
    │
    └─ NO: Continue to next step
```

### Caching Strategy

```
Dashboard Request
    ↓
    ┌─ Snapshot exists?
    │
    ├─ YES: Return cached (FAST: <10ms)
    │
    └─ NO: Load from blob (SLOW: 1-5s)
           ↓
           Process data
           ↓
           Save snapshot
           ↓
           Return result
```

---

## 5. LLM INTEGRATION POINTS

### Where Azure OpenAI is Used

1. **Intent Classification** (Optional)
   - Input: User question
   - Output: Intent type (root_cause, comparison, etc.)
   - Fallback: Rule-based classifier
   - **Status**: Intelligence layer (can fail gracefully)

2. **Entity Extraction** (Optional)
   - Input: User question
   - Output: Entities (LOCID, PRDID, etc.)
   - Fallback: Rule-based extractor
   - **Status**: Intelligence layer (can fail gracefully)

3. **Clarification Prompts** (Optional)
   - Input: Missing context fields
   - Output: Natural language clarification
   - Fallback: Template-based clarification
   - **Status**: UX enhancement (not critical)

### Where Azure OpenAI is NOT Used

❌ **Calculations** - All done by deterministic engine
❌ **Data Access** - All data from parameters
❌ **Aggregations** - All done by analytics module
❌ **Comparisons** - All done by comparator module
❌ **Trend Analysis** - All done by trend_analyzer module

**Principle**: MCP = Context (truth), Azure OpenAI = Intelligence (enhancement)

---

## 6. ANALYTICS COMPUTATION PIPELINE

```
Detail Records
    ↓
    ┌─────────────────────────────────────┐
    │ Compute Global Metrics              │
    │ analytics.build_summary()           │
    │ - Total records                     │
    │ - Changed records                   │
    │ - Change rate                       │
    │ - Change drivers                    │
    │ - Risk distribution                 │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Compute Location Summaries          │
    │ analytics.changes_by_location()     │
    │ - Records per location              │
    │ - Changes per location              │
    │ - Risk per location                 │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Compute Material Group Summaries    │
    │ analytics.changes_by_material_group()
    │ - Records per group                 │
    │ - Changes per group                 │
    │ - Risk per group                    │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Compute Change Driver Analysis      │
    │ analytics.change_driver_analysis()  │
    │ - Qty-driven changes                │
    │ - Supplier-driven changes           │
    │ - Design-driven changes             │
    │ - Schedule-driven changes           │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │ Identify High-Risk Records          │
    │ analytics.high_risk_records()       │
    │ - Filter by risk level              │
    │ - Sort by severity                  │
    └─────────────────────────────────────┘
         ↓
    Aggregated Metrics
```

---

## 7. DATA RETURNED TO USER

### Dashboard Response

```json
{
  "dataMode": "blob|cached",
  "lastRefreshedAt": "ISO timestamp",
  "planningHealth": 0-100,
  "changedRecordCount": number,
  "summaryTiles": {
    "totalRecords": number,
    "changedRecords": number,
    "changeRate": percentage,
    "topRisks": ["Risk1", "Risk2"],
    "healthTrend": "Improving|Stable|Declining"
  },
  "detailRecords": [
    {
      "locationId": string,
      "materialGroup": string,
      "materialId": string,
      "supplier": string,
      "changed": boolean,
      "changeType": string,
      "riskLevel": "Low|Medium|High",
      "qtyDelta": number,
      "changeDrivers": {
        "quantity": boolean,
        "supplier": boolean,
        "design": boolean,
        "schedule": boolean
      }
    }
  ],
  "locationSummary": [
    {
      "location": string,
      "totalRecords": number,
      "changedRecords": number,
      "changeRate": percentage,
      "topRisk": string
    }
  ],
  "materialGroupSummary": [
    {
      "materialGroup": string,
      "totalRecords": number,
      "changedRecords": number,
      "changeRate": percentage,
      "topRisk": string
    }
  ]
}
```

### NLP Response

```json
{
  "question": string,
  "answer": string,
  "queryType": "root_cause|comparison|why_not|traceability|summary",
  "scopeType": "location|supplier|material|null",
  "scopeValue": string,
  "answerMode": "summary|investigate|compare",
  "confidence": 0.0-1.0,
  "conversationHistory": [
    {
      "question": string,
      "answer": string,
      "queryType": string,
      "timestamp": "ISO timestamp"
    }
  ]
}
```

---

## 8. PERFORMANCE CHARACTERISTICS

### Dashboard Load Times

| Scenario | Time | Path |
|----------|------|------|
| Cached snapshot | <10ms | Load from memory |
| Blob load (first time) | 1-5s | Download + process |
| Blob load (subsequent) | <10ms | Use cached snapshot |

### NLP Query Times

| Scenario | Time | Path |
|----------|------|------|
| Rule-based NLP | <50ms | Phase 1-3 pipeline |
| Azure OpenAI | 500ms-2s | LLM call + fallback |
| With fallback | <50ms | Fallback to rule-based |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Snapshot cache | ~5-10MB |
| Detail records (1000 items) | ~2-3MB |
| NLP conversation history | <1MB |

---

## 9. DEPLOYMENT ARCHITECTURE

```
Azure Functions (Backend)
├── planning_dashboard_v2 (HTTP trigger)
├── planning_intelligence_nlp (HTTP trigger)
└── daily_refresh (Timer trigger)

Azure Blob Storage
├── current.csv (current planning data)
└── previous.csv (previous planning data)

Azure OpenAI (Optional)
└── gpt-4 deployment

Frontend (React)
├── DashboardPage
├── CopilotPanel
└── API service (api.ts)
```

---

## Summary

The Copilot Real-Time Answers system is a **clean, modular architecture** with:

✅ **Clear separation of concerns** - Each component has one responsibility
✅ **Loose coupling** - Components can be swapped or updated independently
✅ **Graceful degradation** - System works even if Azure OpenAI fails
✅ **Data-driven answers** - All responses grounded in actual data
✅ **Deterministic engine** - Calculations are reproducible and testable
✅ **Intelligent layer** - Azure OpenAI enhances UX without affecting correctness

