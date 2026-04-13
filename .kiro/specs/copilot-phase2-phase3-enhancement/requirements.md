# Phase 2 & 3 Enhancement - Requirements

**Status:** In Progress  
**Priority:** CRITICAL  
**Timeline:** 2-3 weeks

---

## PHASE 2: VALIDATION HARDENING

### R1: Fix Data Mapping (TOP PRIORITY)

**Current Issue:** Incorrect field mapping causing zero/null errors

**Requirements:**

1. **Forecast Mapping**
   - Current: `GSCFSCTQTY`
   - Previous: `GSCPREVFCSTQTY`
   - Delta: `FCST_Delta Qty`
   - Ensure: Non-zero delta computed correctly

2. **ROJ (Release Order Date) Mapping**
   - Current: `GSCCONROJDATE`
   - Previous: `GSCPREVROJNBDNBD`
   - Delta: `NBD_DeltaDays`
   - Ensure: Date difference calculated correctly

3. **Supplier Mapping**
   - Current: `GSCSUPLDATE`
   - Previous: `GSCPREVSUPLDATE`
   - Flag: `Is_SupplierDateMissing`
   - Ensure: Missing dates detected

4. **Design Mapping**
   - BOD Version: `ZCOIBODVER`
   - Form Factor: `ZCOIFORMFACT`
   - Ensure: Both tracked for design changes

**Acceptance Criteria:**
- ✅ No zero-only outputs when data exists
- ✅ All deltas computed correctly
- ✅ Composite key join: (LOCID, GSCEQUIPCAT, PRDID)
- ✅ Current vs previous rows matched correctly

---

### R2: Fix Record Matching

**Current Issue:** Records not matched correctly, missing rows

**Requirements:**

1. **Composite Key Matching**
   - Use: (LOCID, GSCEQUIPCAT, PRDID)
   - Match current to previous using this key
   - Handle missing current/previous rows gracefully

2. **Null Handling**
   - Never return null if data exists
   - Return "No data" only if truly empty
   - Distinguish between 0 and null

3. **Record Deduplication**
   - Ensure unique records
   - No duplicates in output
   - Correct sorting (delta, risk, design)

**Acceptance Criteria:**
- ✅ All records matched correctly
- ✅ No missing rows
- ✅ No duplicates
- ✅ Correct sorting

---

### R3: Fix Intent Parsing

**Current Issue:** Entity extraction contaminated with prefixes

**Requirements:**

1. **Entity Extraction**
   - Input: "Compare UPS vs MVSXRM"
   - Extract: entity1 = "UPS", entity2 = "MVSXRM"
   - Remove prefix contamination

2. **Scope Extraction**
   - Location: LOC001, AVC11_F01C01, CMH02_F01C01
   - Supplier: SUP001, 310_AMER, 540_EMEA
   - Material Group: UPS, PUMP, VALVE, MVSXRM
   - Material ID: MAT001, C00000560-001

3. **Query Type Classification**
   - comparison, root_cause, why_not, traceability, summary
   - Correct classification for all 40+ prompt types

**Acceptance Criteria:**
- ✅ No prefix contamination
- ✅ Correct entity extraction
- ✅ Correct query type classification
- ✅ All 40+ prompt types supported

---

### R4: Fix Engine Routing

**Current Issue:** Queries routed to wrong engines, global summary leakage

**Requirements:**

1. **Strict Routing**
   - Supplier queries → Supplier Engine
   - Design queries → Design Engine
   - Forecast queries → Forecast Engine
   - Schedule queries → ROJ Engine
   - Comparison queries → Comparison Engine
   - Record queries → Record Engine
   - Traceability queries → Contributing-Record Engine

2. **No Fallback**
   - NO fallback to global summary
   - If scoped query, return scoped answer
   - If no data, return "No data found"

3. **Validation**
   - If response contains global summary for scoped query → FAIL
   - Automated validation before returning

**Acceptance Criteria:**
- ✅ Correct routing for all query types
- ✅ No global summary leakage
- ✅ Scoped queries return scoped answers
- ✅ Validation enforced

---

### R5: Fix Design Change Logic

**Current Issue:** Design changes not detected correctly

**Requirements:**

1. **Design Change Detection**
   - TRUE if: ZCOIBODVER changed OR ZCOIFORMFACT changed
   - FALSE if: Only new demand or cancelled

2. **Exclusions**
   - Exclude new demand
   - Exclude cancelled items
   - Only count actual design changes

**Acceptance Criteria:**
- ✅ Design changes detected correctly
- ✅ No false positives
- ✅ Correct exclusions

---

### R6: Fix Forecast Trend Logic

**Current Issue:** Incorrect sign handling for forecast deltas

**Requirements:**

1. **Trend Direction**
   - If delta > 0 → Increase
   - If delta < 0 → Decrease
   - If delta = 0 → No change

2. **Sign Handling**
   - Correct sign for all calculations
   - No inverted signs
   - Consistent across all engines

**Acceptance Criteria:**
- ✅ Correct trend direction
- ✅ Correct sign handling
- ✅ Consistent across engines

---

### R7: Fix Risk Logic

**Current Issue:** Risk flagged incorrectly

**Requirements:**

1. **Risk Conditions**
   - Risk = TRUE if:
     - Change % > threshold (e.g., 20%)
     - Design changes exist
     - Supplier issues exist
   - Risk = FALSE if:
     - 0% change AND no design changes AND no supplier issues

2. **Threshold**
   - Configurable threshold (default: 20%)
   - Applied consistently

**Acceptance Criteria:**
- ✅ Risk flagged correctly
- ✅ 0% change → NOT risky
- ✅ Threshold applied consistently

---

### R8: Fix Filtered Responses

**Current Issue:** Global data returned for scoped queries

**Requirements:**

1. **Scoped Filtering**
   - Query: "Which suppliers have design changes?"
   - Return: ONLY matching suppliers
   - If none: "No design changes found"

2. **No Leakage**
   - No global summary in scoped response
   - No unrelated data
   - Only requested scope

**Acceptance Criteria:**
- ✅ Correct filtering
- ✅ No data leakage
- ✅ Correct "no data" message

---

### R9: Fix Traceability

**Current Issue:** Duplicate records, incorrect sorting

**Requirements:**

1. **Unique Records**
   - No duplicates
   - Correct deduplication

2. **Correct Sorting**
   - Sort by delta (descending)
   - Sort by risk (high to low)
   - Sort by design changes (yes to no)

3. **Record Details**
   - Include all relevant fields
   - Correct values
   - Traceable to source

**Acceptance Criteria:**
- ✅ Unique records
- ✅ Correct sorting
- ✅ All details included

---

### R10: Enforce Validation Rules

**Current Issue:** No validation before returning responses

**Requirements:**

1. **Validation Rules**
   - For scoped queries: IF response contains global summary → FAIL
   - For filtered queries: IF response contains unrelated data → FAIL
   - For comparisons: IF missing entity → FAIL

2. **Automated Validation**
   - Check before returning
   - Log validation failures
   - Return error if validation fails

**Acceptance Criteria:**
- ✅ All validation rules enforced
- ✅ Automated validation
- ✅ Clear error messages

---

### R11: Add Automated Tests

**Current Issue:** No tests for correctness

**Requirements:**

1. **Test Coverage**
   - No zero-only outputs
   - Correct deltas
   - Correct routing
   - Correct record matching
   - Correct comparisons

2. **Test Data**
   - Real data from blob storage
   - 40+ prompt types
   - Edge cases (missing data, zero values, etc.)

3. **Test Automation**
   - Run on every deployment
   - Fail if any test fails
   - Report results

**Acceptance Criteria:**
- ✅ 100+ tests
- ✅ All tests passing
- ✅ Automated execution

---

## PHASE 3: AZURE OPENAI INTEGRATION

### R12: Implement LLM Service

**Requirements:**

1. **Functions**
   - `classify_intent(query)` → query_type
   - `extract_entities(query)` → entities
   - `generate_response(mcp_context)` → response

2. **Usage**
   - Intent classification
   - Entity extraction
   - Clarification prompts
   - Response formatting

3. **Non-Usage**
   - DO NOT use for computations
   - DO NOT use for aggregations
   - DO NOT use for data access

**Acceptance Criteria:**
- ✅ LLM service implemented
- ✅ Correct usage patterns
- ✅ No misuse

---

### R13: Add Guardrails

**Requirements:**

1. **Number Validation**
   - All numbers from deterministic engine
   - No hallucinated values
   - Validate before returning

2. **Response Validation**
   - Check for hallucinations
   - Verify numbers match source
   - Reject if invalid

**Acceptance Criteria:**
- ✅ No hallucinated values
- ✅ All numbers validated
- ✅ Correct responses

---

### R14: Implement MCP (Model Context Protocol)

**Requirements:**

1. **MCP Context**
   - planningHealth
   - forecastNew / forecastOld
   - trendDelta
   - changedRecordCount
   - totalRecords
   - drivers
   - riskSummary
   - supplierSummary
   - materialGroupSummary
   - datacenterSummary
   - detailRecords
   - blobFileNamesUsed
   - lastRefreshedAt

2. **SAP Field Dictionary**
   - LOCID, PRDID, GSCEQUIPCAT
   - GSCFSCTQTY, GSCPREVFCSTQTY
   - GSCSUPLDATE, GSCPREVSUPLDATE
   - ZCOIBODVER, ZCOIFORMFACT
   - NBD_DeltaDays

3. **Semantic Mapping**
   - forecast_change
   - design_change
   - supplier_issues
   - schedule_issue

**Acceptance Criteria:**
- ✅ MCP context complete
- ✅ SAP field dictionary provided
- ✅ Semantic mapping defined

---

### R15: Implement Interactive Clarification

**Requirements:**

1. **Incomplete Query Handling**
   - Detect incomplete queries
   - Ask for clarification
   - Provide options

2. **Example Flow**
   - User: "What changed at AVC11?"
   - Copilot: "Select material group at AVC11"
   - Options: UPS, PUMP, VALVE
   - Then: "Select material ID"
   - Then: Execute reasoning

3. **Guided Exploration**
   - Step-by-step guidance
   - Clear options
   - Confirmation before execution

**Acceptance Criteria:**
- ✅ Incomplete queries detected
- ✅ Clarification requested
- ✅ Guided exploration working

---

### R16: Implement Performance Optimization

**Requirements:**

1. **Prompt Cache**
   - Key: hash(query + context)
   - TTL: 1 hour
   - Invalidate on refresh

2. **Metrics Cache**
   - Cache computed aggregates per scope
   - TTL: 1 hour
   - Invalidate on refresh

3. **Batching**
   - Parallelize multiple prompt execution
   - Batch similar queries
   - Async/await support

4. **Performance Targets**
   - First response: <200ms
   - Cached response: <5ms
   - Throughput: 50+ prompts/sec

**Acceptance Criteria:**
- ✅ Caching implemented
- ✅ Batching implemented
- ✅ Performance targets met

---

### R17: Implement Response Structure

**Requirements:**

1. **Response Format**
   - Decision
   - Metrics
   - Drivers
   - Risk
   - Actions
   - Traceability (optional)

2. **Consistency**
   - All responses follow format
   - All fields populated
   - Clear and actionable

**Acceptance Criteria:**
- ✅ Response structure implemented
- ✅ All responses follow format
- ✅ Consistent across all query types

---

## SUCCESS CRITERIA

### Correctness (MUST HAVE)
- ✅ No zero/null errors when data exists
- ✅ No global summary leakage
- ✅ All prompt types produce correct scoped answers
- ✅ Correct forecast/design/supplier/ROJ values

### Intelligence (SHOULD HAVE)
- ✅ Copilot is interactive
- ✅ Copilot is intelligent
- ✅ Azure OpenAI integration working

### Performance (NICE TO HAVE)
- ✅ Performance improved significantly
- ✅ Caching working
- ✅ Batching working

### Production Readiness (MUST HAVE)
- ✅ System is production-ready
- ✅ All tests passing
- ✅ No known issues

---

## PRIORITY ORDER

1. **CRITICAL (Week 1)**
   - R1: Fix Data Mapping
   - R2: Fix Record Matching
   - R3: Fix Intent Parsing
   - R4: Fix Engine Routing

2. **HIGH (Week 2)**
   - R5: Fix Design Change Logic
   - R6: Fix Forecast Trend Logic
   - R7: Fix Risk Logic
   - R8: Fix Filtered Responses
   - R9: Fix Traceability
   - R10: Enforce Validation Rules
   - R11: Add Automated Tests

3. **MEDIUM (Week 3)**
   - R12: Implement LLM Service
   - R13: Add Guardrails
   - R14: Implement MCP
   - R15: Implement Interactive Clarification
   - R16: Implement Performance Optimization
   - R17: Implement Response Structure

---

## ACCEPTANCE CRITERIA

**Phase 2 Complete When:**
- All 11 requirements implemented
- All tests passing
- No zero/null errors
- No global summary leakage
- All prompt types working correctly

**Phase 3 Complete When:**
- All 6 requirements implemented
- Azure OpenAI integration working
- MCP context complete
- Performance targets met
- System production-ready

