# Phase 2 & 3 Implementation Plan

**Status:** Ready for Implementation  
**Timeline:** 2-3 weeks  
**Priority:** CRITICAL

---

## EXECUTIVE SUMMARY

This plan addresses critical correctness issues in the Planning Intelligence Copilot and enhances it with Azure OpenAI integration, MCP grounding, and performance optimization.

### Current Issues
- ❌ Zero/null errors when data exists
- ❌ Global summary leakage in scoped queries
- ❌ Incorrect data mapping (forecast, ROJ, supplier, design)
- ❌ Prefix contamination in entity extraction
- ❌ Wrong engine routing
- ❌ No Azure OpenAI integration
- ❌ No MCP context
- ❌ No performance optimization

### Deliverables
- ✅ Production-ready Copilot
- ✅ Correct data mapping
- ✅ Correct engine routing
- ✅ Azure OpenAI integration
- ✅ MCP context
- ✅ Performance optimization (5-50x faster)
- ✅ 100+ automated tests
- ✅ Interactive clarification

---

## PHASE 2: VALIDATION HARDENING (Week 1-2)

### Objective
Fix all correctness issues before optimization.

### Key Components

#### 1. Data Mapper (`planning_intelligence/data_mapper.py`)
- Maps SAP fields to internal representation
- Handles forecast, ROJ, supplier, design fields
- Computes deltas correctly
- Detects design changes
- Computes risk flags
- Handles nulls properly

#### 2. Record Matcher (`planning_intelligence/record_matcher.py`)
- Matches current to previous using composite key: (LOCID, GSCEQUIPCAT, PRDID)
- Handles missing rows
- Deduplicates records
- Sorts correctly

#### 3. Intent Parser (`planning_intelligence/intent_parser.py`)
- Classifies query type (5 types)
- Extracts entities (location, supplier, material_group, material_id)
- Removes prefix contamination
- Validates parsed intent

#### 4. Engine Router (`planning_intelligence/engine_router.py`)
- Routes to correct engine based on query type
- Validates no global summary leakage
- Enforces scoped responses for scoped queries

#### 5. Response Validator (`planning_intelligence/response_validator.py`)
- Validates no hallucinations
- Validates no global summary leakage
- Validates required fields
- Enforces correctness

### Fixes Applied

| Issue | Fix | Component |
|-------|-----|-----------|
| Zero/null errors | Proper null handling | DataMapper |
| Global summary leakage | Validation enforcement | EngineRouter, ResponseValidator |
| Incorrect mapping | Correct field mapping | DataMapper |
| Prefix contamination | Regex-based extraction | IntentParser |
| Wrong routing | Strict routing logic | EngineRouter |
| Design change logic | BOD + FormFactor check | DataMapper |
| Forecast trend | Correct sign handling | DataMapper |
| Risk logic | Threshold-based | DataMapper |
| Filtered responses | Scope enforcement | All Engines |
| Traceability | Deduplication + sorting | RecordMatcher |

### Tests Added

- `test_data_mapping.py` - 20+ tests
- `test_record_matching.py` - 15+ tests
- `test_intent_parsing.py` - 20+ tests
- `test_engine_routing.py` - 15+ tests
- `test_correctness.py` - 30+ tests
- `test_integration_phase2.py` - 20+ tests

**Total: 120+ tests**

---

## PHASE 3: AZURE OPENAI INTEGRATION (Week 3)

### Objective
Enhance Copilot with intelligent LLM interaction, MCP grounding, and performance optimization.

### Key Components

#### 1. LLM Service (`planning_intelligence/llm_service.py`)
- `classify_intent(query)` - Classify query type
- `extract_entities(query)` - Extract entities
- `generate_response(mcp_context)` - Generate natural language response
- Guardrails to prevent hallucinations

#### 2. MCP Context Builder (`planning_intelligence/mcp_context_builder.py`)
- Builds MCP context with:
  - Planning health
  - Forecast metrics
  - Trend delta
  - Changed record count
  - Drivers
  - Risk summary
  - Supplier/material/datacenter summaries
  - Detail records
  - SAP field dictionary
  - Semantic mapping

#### 3. Clarification Engine (`planning_intelligence/clarification_engine.py`)
- Detects incomplete queries
- Generates clarification prompts
- Provides guided exploration
- Generates options

#### 4. Cache Layer (`planning_intelligence/cache_layer.py`)
- Prompt caching (key: hash(query + context), TTL: 1 hour)
- Metrics caching (per scope, TTL: 1 hour)
- Cache invalidation on refresh

#### 5. Response Validator (Enhanced)
- Validates no hallucinations
- Validates numbers match source
- Validates consistency

### Performance Targets

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| First response | <200ms | 850-1350ms | 5-10x faster |
| Cached response | <5ms | 850-1350ms | 170x faster |
| Throughput | 50+ prompts/sec | 1-2 prompts/sec | 50x faster |
| Cost | $0.002/prompt | $0.01/prompt | 80% reduction |

### Tests Added

- `test_llm_service.py` - 15+ tests
- `test_mcp_context.py` - 15+ tests
- `test_clarification.py` - 15+ tests
- `test_caching.py` - 15+ tests
- `test_integration_phase3.py` - 20+ tests

**Total: 80+ tests**

---

## IMPLEMENTATION SEQUENCE

### Week 1: Data Mapping & Record Matching
```
Day 1-2: Create DataMapper, RecordMatcher, IntentParser
Day 3-4: Create EngineRouter, ResponseValidator
Day 5: Add tests, validate correctness
```

### Week 2: Engine Fixes & Validation
```
Day 1-2: Fix all engines (Supplier, Design, Forecast, ROJ, Comparison, Record, Contributing)
Day 3-4: Add validation, add tests
Day 5: Integration testing, correctness validation
```

### Week 3: LLM Integration & Performance
```
Day 1-2: Create LLMService, MCPContextBuilder, ClarificationEngine
Day 3-4: Create CacheLayer, add tests
Day 5: Integration testing, performance validation, deployment
```

---

## CORRECTNESS VALIDATION

### Before Phase 2
```
Query: "Which suppliers have design changes?"
Response: "Global summary: 5000 records changed..."
Status: ❌ FAIL (global summary leakage)
```

### After Phase 2
```
Query: "Which suppliers have design changes?"
Response: "Suppliers with design changes: SUP001, SUP002..."
Status: ✅ PASS (scoped response)
```

### Before Phase 3
```
Query: "Why is UPS risky?"
Response: "UPS has 50% change rate..."
Status: ⚠️ PARTIAL (correct but not intelligent)
```

### After Phase 3
```
Query: "Why is UPS risky?"
Response: "UPS is risky because 50% of records changed, primarily due to forecast increases. 
Key drivers: Forecast (60%), Design (30%), Supplier (10%). 
Recommended actions: Review forecast assumptions, validate design changes."
Status: ✅ PASS (intelligent and correct)
```

---

## PERFORMANCE VALIDATION

### Before Optimization
```
Process 40 prompts: 34 seconds
Cost: $0.40
Cache hit rate: 0%
```

### After Optimization
```
Process 40 prompts: 2-4 seconds (10-20x faster)
Cost: $0.08 (80% reduction)
Cache hit rate: 70%+
```

---

## SUCCESS CRITERIA

### Phase 2 Complete When:
- ✅ All 11 requirements implemented
- ✅ 120+ tests passing
- ✅ No zero/null errors when data exists
- ✅ No global summary leakage
- ✅ All prompt types produce correct scoped answers
- ✅ Correct forecast/design/supplier/ROJ values

### Phase 3 Complete When:
- ✅ All 6 requirements implemented
- ✅ 80+ tests passing
- ✅ Azure OpenAI integration working
- ✅ MCP context complete
- ✅ Performance targets met (5-50x faster, 80% cost reduction)
- ✅ System production-ready

---

## RISK MITIGATION

### Risk: Breaking Existing Functionality
**Mitigation:** 
- Comprehensive test coverage (200+ tests)
- Gradual rollout (Phase 2 first, then Phase 3)
- Rollback procedures documented

### Risk: Performance Degradation
**Mitigation:**
- Performance testing before deployment
- Caching implemented to improve performance
- Monitoring in place

### Risk: Hallucinations from LLM
**Mitigation:**
- Guardrails implemented
- Response validation enforced
- Numbers validated against source

---

## DELIVERABLES

### Code
- 10+ new Python modules
- 200+ tests
- Updated existing modules
- Deployment guide

### Documentation
- Requirements document
- Design document
- Implementation guide
- Testing guide
- Deployment guide

### Validation
- 200+ automated tests
- Performance benchmarks
- Correctness validation
- Production readiness checklist

---

## NEXT STEPS

1. **Review & Approve**
   - Review requirements.md
   - Review design.md
   - Review tasks.md
   - Approve implementation plan

2. **Week 1: Phase 2 Implementation**
   - Implement data mapping
   - Implement record matching
   - Implement intent parsing
   - Implement engine routing
   - Add validation
   - Add tests

3. **Week 2: Phase 2 Validation**
   - Fix all engines
   - Add correctness tests
   - Validate no global summary leakage
   - Integration testing

4. **Week 3: Phase 3 Implementation**
   - Implement LLM service
   - Implement MCP context
   - Implement caching
   - Add performance optimization
   - Integration testing

5. **Week 4: Deployment**
   - Final testing
   - Deploy to Azure
   - Monitor performance
   - Gather feedback

---

## ESTIMATED EFFORT

- **Phase 2:** 80 hours (Week 1-2)
- **Phase 3:** 60 hours (Week 3)
- **Total:** 140 hours (2-3 weeks)

---

## PRIORITY

**Correctness > Performance > Intelligence**

Do not proceed to optimization until correctness is fully validated.

---

## SPEC LOCATION

All detailed specifications are in:
- `.kiro/specs/copilot-phase2-phase3-enhancement/requirements.md`
- `.kiro/specs/copilot-phase2-phase3-enhancement/design.md`
- `.kiro/specs/copilot-phase2-phase3-enhancement/tasks.md`

