# Planning Intelligence Copilot - Technical Details

## Part 1: Backend Architecture Deep Dive

### Data Structures

#### ComparedRecord (models.py)
```python
@dataclass
class ComparedRecord:
    location_id: str
    material_id: str
    material_group: str
    supplier_current: str
    supplier_previous: str
    forecast_qty_current: float
    forecast_qty_previous: float
    qty_delta: float
    qty_changed: bool
    roj_current: str
    roj_previous: str
    roj_changed: bool
    bod_current: str
    bod_previous: str
    ff_current: str
    ff_previous: str
    design_changed: bool
    supplier_changed: bool
    risk_level: str
    change_type: str
    # ... 20+ more fields
```

#### DetailRecord (frontend/src/types/dashboard.ts)
```typescript
interface DetailRecord {
  locationId: string;
  materialGroup: string;
  materialId: string;
  supplier: string | null;
  forecastQtyCurrent: number | null;
  forecastQtyPrevious: number | null;
  qtyDelta: number | null;
  rojCurrent: string | null;
  rojPrevious: string | null;
  bodCurrent: string | null;
  bodPrevious: string | null;
  ffCurrent: string | null;
  ffPrevious: string | null;
  changeType: string;
  riskLevel: string;
  qtyChanged: boolean;
  supplierChanged: boolean;
  designChanged: boolean;
  rojChanged: boolean;
  dcSite: string | null;
  country: string | null;
  lastModifiedBy: string | null;
  lastModifiedDate: string | null;
}
```

### Key Functions

#### blob_loader.py

**`load_current_previous_from_blob()`**
- Downloads current.csv and previous.csv from Azure Blob Storage
- Parses CSV/Excel files
- Validates required columns (LOCID, PRDID, GSCEQUIPCAT)
- Returns: (current_rows, previous_rows) as list[dict]

**Error Handling**:
- BlobNotFound → Detailed error with verification steps
- AuthenticationFailed → Detailed error with credential checks
- ConnectionError → Detailed error with network checks

#### normalizer.py

**`normalize_rows(rows, is_current)`**
- Standardizes column names (uppercase, strip whitespace)
- Maps SAP columns to canonical names (LOC ID → LOCID)
- Converts to ComparedRecord objects
- Validates required fields

#### comparator.py

**`compare_records(current, previous)`**
- Matches records by (LOCID, PRDID)
- Detects changes:
  - qty_changed: forecast_qty_current != forecast_qty_previous
  - supplier_changed: supplier_current != supplier_previous
  - design_changed: bod_current != bod_previous OR ff_current != ff_previous
  - roj_changed: roj_current != roj_previous
- Computes qty_delta
- Assigns risk_level based on changes

#### analytics.py

**`build_summary(compared)`**
- Computes health_score (0-100)
  - Base: 100
  - Deduction: (changed_count / total) * 40
  - Deduction: risk_level penalties (25, 15, 10)
  - Deduction: design/supplier change penalties
- Classifies trend_direction (increasing, decreasing, stable, volatile)
- Computes contribution breakdown (qty, supplier, design, schedule)
- Identifies primary driver

#### response_builder.py

**`build_response(compared, trends, location_id, material_group, data_mode)`**
- Calls MCP tools:
  - analytics_context_tool()
  - risk_summary_tool()
  - root_cause_driver_tool()
  - recommendation_tool()
  - alert_trigger_tool()
- Generates AI insights (deterministic, no LLM)
- Builds UI-ready response JSON
- Includes detailRecords for Copilot

### Phase 1-4 Pipeline

#### Phase 1: Classification & Scope Extraction

**QuestionClassifier.classify_question(question)**
```python
# Returns one of:
# - "comparison" (Compare X vs Y)
# - "root_cause" (Why is X risky?)
# - "why_not" (Why is X stable?)
# - "traceability" (Show top records)
# - "summary" (What's the status?)
```

**ScopeExtractor.extract_scope(question)**
```python
# Returns: (scope_type, scope_value)
# scope_type: "location" | "supplier" | "material_group" | "material_id" | "risk_type"
# scope_value: "CYS20_F01C01" | "Supplier A" | "UPS" | "MAT001" | None
```

**AnswerModeDecider.determine_answer_mode(query_type, scope_type)**
```python
# Returns: "summary" | "investigate"
# investigate mode for: comparison, traceability, scoped root_cause/why_not
```

#### Phase 2: Answer Generation

**AnswerTemplates.generate_*_answer()**
- comparison_answer: "📊 Entity A vs Entity B..."
- root_cause_answer: "In [entity], [what changed]..."
- why_not_answer: "[Entity] is stable because..."
- traceability_answer: "📊 Top [N] contributing records..."
- summary_answer: "Planning health is [X]..."

**ResponseBuilder.build_response()**
- Adds supporting metrics
- Adds explainability metadata
- Adds suggested actions
- Adds follow-up questions
- Adds investigate mode fields (if applicable)

#### Phase 3: Integration

**Phase3Integration.process_question_with_phases()**
- Orchestrates Phase 1-2
- Handles comparison questions
- Handles root_cause questions
- Handles why_not questions
- Handles traceability questions
- Falls back to summary

#### Phase 4: Comprehensive Testing

- 19 end-to-end tests
- Tests all question types
- Tests error cases
- Tests edge cases

---

## Part 2: Frontend Architecture Deep Dive

### Component Hierarchy

```
App.tsx
  ├── DashboardPage.tsx (600+ lines)
  │   ├── PlanningHealthCard
  │   ├── ForecastCard
  │   ├── TrendCard
  │   ├── RiskCard
  │   ├── RojCard
  │   ├── DesignCard
  │   ├── SummaryTiles
  │   ├── AIInsightCard
  │   ├── RootCauseCard
  │   ├── AlertBanner
  │   ├── DatacenterCard
  │   ├── MaterialGroupCard
  │   ├── SupplierCard
  │   ├── TopRiskTable
  │   ├── ActionsPanel
  │   ├── Tooltip
  │   ├── DrillDownPanel
  │   └── CopilotPanel (546 lines)
  │       ├── Chat messages
  │       ├── Starter prompts
  │       ├── Follow-up suggestions
  │       └── Input textarea
```

### Data Flow in Frontend

```
DashboardPage.useEffect()
  ↓
fetchDashboard()
  ↓
POST /api/planning-dashboard-v2
  ↓
Receive DashboardResponse
  ↓
validateResponse()
  ↓
buildContext()
  ↓
setContext()
  ↓
Render 18 components
```

### Copilot Panel Flow

```
User types question
  ↓
sendMessage(question)
  ↓
setMessages([...prev, userMsg])
  ↓
fetchExplain({question, context})
  ↓
POST /api/planning_intelligence_nlp
  ↓
Receive ExplainResponse
  ↓
Extract answer + metrics
  ↓
buildFollowUps()
  ↓
setMessages([...prev, assistantMsg])
```

### Utility Functions

**answerGenerator.ts**:
- buildGreeting(ctx, entity) → string
- buildFallbackAnswer(question, ctx, entity) → string
- filterDetailsByEntity(details, entity) → DetailRecord[]
- contextLabel(entity) → string

**promptGenerator.ts**:
- buildSmartPrompts(ctx, entity) → string[]
- buildEntityPrompts(ctx, entity) → string[]
- selectDiversePrompts(candidates, maxCount) → string[]
- buildFollowUps(question, ctx, entity) → string[]

---

## Part 3: Current Issues & Root Causes

### Issue 1: Entity Questions Return Generic Answers

**Example Question**: "List suppliers for CYS20_F01C01"

**Current Flow**:
1. classify_question() → "entity"
2. generate_entity_answer() called
3. BUT: generate_entity_answer() is defined in function_app.py (line 446)
4. BUT: It's NOT called from explain() endpoint
5. Falls through to generate_general_answer()
6. Returns: "Planning health is 37/100..."

**Root Cause**: 
- generate_entity_answer() exists but is never called
- No location extraction logic
- No filtering logic

**Fix Required**:
1. Extract location ID from question
2. Filter detailRecords to location
3. Get unique suppliers/materials
4. Return specific answer

### Issue 2: Comparison Questions Return Generic Answers

**Example Question**: "Compare CYS20_F01C01 vs DSM18_F01C01"

**Current Flow**:
1. classify_question() → "general" (not recognized as comparison)
2. Falls through to generate_general_answer()
3. Returns: "Planning health is 37/100..."

**Root Cause**:
- "compare" keyword not in classify_question()
- No comparison handler
- No location extraction

**Fix Required**:
1. Add "compare" to classify_question()
2. Implement generate_comparison_answer()
3. Extract two locations from question
4. Compare metrics between them

### Issue 3: Impact Questions Return Generic Answers

**Example Question**: "Which supplier has the most impact?"

**Current Flow**:
1. classify_question() → "general" (not recognized as impact)
2. Falls through to generate_general_answer()
3. Returns: "Planning health is 37/100..."

**Root Cause**:
- "impact" keyword not in classify_question()
- No impact handler
- No ranking logic

**Fix Required**:
1. Add "impact" to classify_question()
2. Implement generate_impact_answer()
3. Rank suppliers/materials by change count
4. Return top impacted entities

### Issue 4: Azure OpenAI Integration Incomplete

**File**: nlp_endpoint.py, lines 100-150

**Current Code**:
```python
if self.use_azure_openai:
    try:
        intent_result = self.openai_client.extract_intent_and_entities(...)
        query_type = intent_result.get("intent", "summary")
        # ... extract entities ...
        confidence = intent_result.get("confidence", 0.8)
        response["azureOpenAIUsed"] = True
    except Exception as e:
        # Fall back to rule-based
```

**Issues**:
1. Line 150: `context` variable used but not defined
2. Entity extraction incomplete (only LOCID, LOCFR, PRDID)
3. No error logging
4. No timeout handling

**Fix Required**:
1. Define `context` variable
2. Expand entity extraction
3. Add error logging
4. Add timeout handling

### Issue 5: Data Normalization Issues

**File**: function_app.py, lines 95-160

**Current Code**:
```python
norm = {
    "locationId": r.get("locationId") or r.get("LOCID") or r.get("location_id") or "",
    "materialGroup": r.get("materialGroup") or r.get("GSCEQUIPCAT") or r.get("material_group") or "",
    # ... other fields ...
}
```

**Issues**:
1. Defaults to empty string instead of None
2. Missing fields from blob data
3. Type inconsistency (strings vs numbers vs booleans)
4. Normalization happens too late (in function_app.py)

**Fix Required**:
1. Use None instead of empty string
2. Add all fields from blob data
3. Ensure consistent types
4. Move normalization to response_builder.py

---

## Part 4: Missing Implementations

### Missing Helper Functions

```python
def extract_location_id(question: str) -> Optional[str]:
    """Extract location ID from question (e.g., 'CYS20_F01C01')"""
    import re
    match = re.search(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    return match.group(1) if match else None

def extract_supplier_name(question: str) -> Optional[str]:
    """Extract supplier name from question"""
    import re
    match = re.search(r'"([^"]+)"', question)
    return match.group(1) if match else None

def filter_records_by_location(records: list, location_id: str) -> list:
    """Filter records to specific location"""
    return [r for r in records if r.get("locationId") == location_id]

def filter_records_by_change_type(records: list, change_type: str) -> list:
    """Filter records by change type (Design, Supplier, Quantity)"""
    return [r for r in records if r.get("changeType") == change_type]

def get_unique_suppliers(records: list) -> list:
    """Get unique suppliers from records"""
    suppliers = set()
    for r in records:
        if r.get("supplier"):
            suppliers.add(r.get("supplier"))
    return sorted(list(suppliers))

def get_unique_materials(records: list) -> list:
    """Get unique materials from records"""
    materials = set()
    for r in records:
        if r.get("materialGroup"):
            materials.add(r.get("materialGroup"))
    return sorted(list(materials))

def get_impact_ranking(records: list) -> dict:
    """Get suppliers/materials ranked by impact (number of changes)"""
    supplier_impact = {}
    material_impact = {}
    
    for r in records:
        if r.get("changed"):
            supplier = r.get("supplier", "Unknown")
            material = r.get("materialGroup", "Unknown")
            
            supplier_impact[supplier] = supplier_impact.get(supplier, 0) + 1
            material_impact[material] = material_impact.get(material, 0) + 1
    
    return {
        "suppliers": sorted(supplier_impact.items(), key=lambda x: x[1], reverse=True),
        "materials": sorted(material_impact.items(), key=lambda x: x[1], reverse=True)
    }
```

### Missing Answer Generators

```python
def generate_entity_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for entity questions"""
    location_id = extract_location_id(question)
    
    if location_id:
        location_records = filter_records_by_location(detail_records, location_id)
        if not location_records:
            return {
                "answer": f"No records found for location {location_id}.",
                "supportingMetrics": {"location": location_id, "recordCount": 0}
            }
        
        suppliers = get_unique_suppliers(location_records)
        materials = get_unique_materials(location_records)
        changed = sum(1 for r in location_records if r.get("changed"))
        
        answer = f"Location {location_id}: {len(location_records)} records. "
        answer += f"Suppliers: {', '.join(suppliers[:5])}. "
        answer += f"Materials: {', '.join(materials[:5])}. "
        answer += f"Changed: {changed}."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "location": location_id,
                "recordCount": len(location_records),
                "suppliers": suppliers,
                "materials": materials,
                "changedCount": changed
            }
        }
    else:
        impact = get_impact_ranking(detail_records)
        top_suppliers = impact["suppliers"][:5]
        top_materials = impact["materials"][:5]
        
        answer = "Top affected suppliers: "
        answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
        answer += "Top affected materials: "
        answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
        
        return {
            "answer": answer,
            "supportingMetrics": {
                "topSuppliers": top_suppliers,
                "topMaterials": top_materials
            }
        }

def generate_comparison_answer(detail_records: list, context: dict, question: str) -> dict:
    """Generate answer for comparison questions"""
    import re
    locations = re.findall(r'([A-Z]{2,}[0-9]{2,}_[A-Z0-9]{2,})', question)
    
    if len(locations) < 2:
        return {
            "answer": "Please specify two locations to compare.",
            "supportingMetrics": {}
        }
    
    loc1, loc2 = locations[0], locations[1]
    records1 = filter_records_by_location(detail_records, loc1)
    records2 = filter_records_by_location(detail_records, loc2)
    
    changed1 = sum(1 for r in records1 if r.get("changed"))
    changed2 = sum(1 for r in records2 if r.get("changed"))
    
    answer = f"Comparison: {loc1} vs {loc2}. "
    answer += f"{loc1}: {len(records1)} records, {changed1} changed. "
    answer += f"{loc2}: {len(records2)} records, {changed2} changed."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "location1": loc1,
            "location1Records": len(records1),
            "location1Changed": changed1,
            "location2": loc2,
            "location2Records": len(records2),
            "location2Changed": changed2
        }
    }

def generate_impact_answer(detail_records: list, context: dict) -> dict:
    """Generate answer for impact questions"""
    impact = get_impact_ranking(detail_records)
    top_suppliers = impact["suppliers"][:3]
    top_materials = impact["materials"][:3]
    
    answer = "Impact analysis: "
    answer += "Top suppliers affected: "
    answer += ", ".join([f"{s[0]} ({s[1]} changes)" for s in top_suppliers]) + ". "
    answer += "Top materials affected: "
    answer += ", ".join([f"{m[0]} ({m[1]} changes)" for m in top_materials]) + "."
    
    return {
        "answer": answer,
        "supportingMetrics": {
            "topSuppliers": top_suppliers,
            "topMaterials": top_materials
        }
    }
```

---

## Part 5: Integration Points

### Frontend → Backend

**API Endpoints**:
1. POST /api/planning-dashboard-v2
   - Request: {mode: "blob", location_id?, material_group?}
   - Response: DashboardResponse

2. POST /api/planning_intelligence_nlp
   - Request: {question, context}
   - Response: ExplainResponse

### Backend → Azure Services

**Blob Storage**:
- Download current.csv
- Download previous.csv
- Connection string from environment

**Azure OpenAI** (optional):
- Extract intent and entities
- Graceful fallback to rule-based

### Data Structures

**DashboardResponse** (from backend):
- planningHealth, status, forecast, trend, risk, drivers
- detailRecords (for Copilot)
- datacenterSummary, materialGroupSummary, supplierSummary
- alerts, recommendations

**ExplainResponse** (from backend):
- question, answer, queryType, answerMode
- scopeType, scopeValue
- supportingMetrics, investigateMode
- followUpQuestions

---

## Part 6: Performance Metrics

### Response Times

| Operation | Time | Bottleneck |
|-----------|------|-----------|
| Dashboard (cached) | <10ms | Snapshot load |
| Dashboard (blob) | 1-5s | Blob download |
| NLP (rule-based) | <50ms | Phase 1-3 |
| NLP (Azure OpenAI) | 500ms-2s | LLM call |
| NLP (fallback) | <50ms | Rule-based |

### Optimization Opportunities

1. **Snapshot caching** ✅ Already implemented
2. **Incremental blob updates** ⚠️ Not implemented
3. **Response caching** ⚠️ Not implemented
4. **Parallel processing** ⚠️ Not implemented
5. **Compression** ⚠️ Not implemented

---

## Part 7: Error Handling

### Current Error Handling

✅ Blob not found → Detailed error message
✅ Authentication failed → Detailed error message
✅ Connection error → Detailed error message
✅ Invalid JSON → 400 error
✅ Missing question → 400 error
✅ No detail records → 404 error

### Missing Error Handling

❌ Question too long → No validation
❌ detailRecords malformed → No validation
❌ Azure OpenAI timeout → No timeout handling
❌ Rate limiting → No rate limiting
❌ Invalid location ID → No validation

---

## Conclusion

The Planning Intelligence Copilot is a well-engineered system with solid architecture and comprehensive testing. The main issues are:

1. **Missing question handlers** (entity, comparison, impact)
2. **Incomplete Azure OpenAI integration** (undefined context variable)
3. **Missing helper functions** (location extraction, filtering, ranking)
4. **Data normalization issues** (null values, missing fields)

All of these are straightforward to fix and don't require architectural changes.

