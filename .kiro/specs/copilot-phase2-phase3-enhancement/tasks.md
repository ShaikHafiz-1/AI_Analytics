# Phase 2 & 3 Enhancement - Implementation Tasks

**Status:** Ready for Implementation  
**Total Tasks:** 25  
**Estimated Duration:** 2-3 weeks

---

## PHASE 2: VALIDATION HARDENING

### Week 1: Data Mapping & Record Matching

- [-] 1.1 Create `planning_intelligence/data_mapper.py`
  - Implement DataMapper class
  - Implement field mappings (forecast, ROJ, supplier, design)
  - Implement delta computation with null handling
  - Implement design change detection
  - Implement risk computation
  - Add unit tests

- [ ] 1.2 Create `planning_intelligence/record_matcher.py`
  - Implement RecordMatcher class
  - Implement composite key matching
  - Implement record deduplication
  - Add unit tests

- [ ] 1.3 Update `planning_intelligence/phase1_core_functions.py`
  - Integrate DataMapper
  - Integrate RecordMatcher
  - Remove old mapping logic
  - Add validation

- [ ] 1.4 Create `planning_intelligence/intent_parser.py`
  - Implement IntentParser class
  - Implement query type classification
  - Implement entity extraction (no prefix contamination)
  - Implement validation
  - Add unit tests

- [ ] 1.5 Create `planning_intelligence/engine_router.py`
  - Implement EngineRouter class
  - Implement routing logic
  - Implement validation (no global summary leakage)
  - Add unit tests

- [ ] 1.6 Create `planning_intelligence/test_data_mapping.py`
  - Test all field mappings
  - Test delta computation
  - Test null handling
  - Test design change detection
  - Test risk computation
  - Ensure no zero-only outputs

- [ ] 1.7 Create `planning_intelligence/test_record_matching.py`
  - Test composite key matching
  - Test record deduplication
  - Test missing rows handling
  - Test sorting

- [ ] 1.8 Create `planning_intelligence/test_intent_parsing.py`
  - Test query type classification
  - Test entity extraction
  - Test prefix contamination fix
  - Test all 40+ prompt types

### Week 2: Engine Fixes & Validation

- [ ] 2.1 Fix `planning_intelligence/phase2_answer_templates.py`
  - Fix design change logic
  - Fix forecast trend logic
  - Fix risk logic
  - Fix filtered responses
  - Fix traceability (unique records, correct sorting)
  - Add validation

- [ ] 2.2 Create `planning_intelligence/response_validator.py`
  - Implement ResponseValidator class
  - Implement hallucination detection
  - Implement global summary leakage detection
  - Implement required fields validation
  - Add unit tests

- [ ] 2.3 Update all engines
  - SupplierEngine: Fix filtering, add validation
  - DesignEngine: Fix design change logic, add validation
  - ForecastEngine: Fix trend logic, add validation
  - ROJEngine: Fix schedule logic, add validation
  - ComparisonEngine: Fix comparison logic, add validation
  - RecordEngine: Fix record matching, add validation
  - ContributingRecordEngine: Fix traceability, add validation

- [ ] 2.4 Create `planning_intelligence/test_engine_routing.py`
  - Test correct routing for all query types
  - Test no global summary leakage
  - Test scoped queries return scoped answers
  - Test validation enforcement

- [ ] 2.5 Create `planning_intelligence/test_correctness.py`
  - Test no zero-only outputs
  - Test correct deltas
  - Test correct routing
  - Test correct record matching
  - Test correct comparisons
  - Test all 40+ prompt types

- [ ] 2.6 Create `planning_intelligence/test_integration_phase2.py`
  - End-to-end tests for Phase 2
  - Real data from blob storage
  - All prompt types
  - Edge cases (missing data, zero values, etc.)

---

## PHASE 3: AZURE OPENAI INTEGRATION

### Week 3: LLM Service & MCP

- [ ] 3.1 Create `planning_intelligence/llm_service.py`
  - Implement LLMService class
  - Implement classify_intent()
  - Implement extract_entities()
  - Implement generate_response()
  - Add guardrails (no hallucinations)
  - Add unit tests

- [ ] 3.2 Create `planning_intelligence/mcp_context_builder.py`
  - Implement MCPContextBuilder class
  - Implement SAP field dictionary
  - Implement semantic mapping
  - Implement MCP context building
  - Add unit tests

- [ ] 3.3 Update `planning_intelligence/azure_openai_integration.py`
  - Fix endpoint configuration
  - Add error handling
  - Add retry logic
  - Add logging

- [ ] 3.4 Create `planning_intelligence/clarification_engine.py`
  - Implement interactive clarification
  - Implement guided exploration
  - Implement option generation
  - Add unit tests

- [ ] 3.5 Create `planning_intelligence/cache_layer.py`
  - Implement CacheLayer class
  - Implement prompt caching
  - Implement metrics caching
  - Implement cache invalidation
  - Add unit tests

- [ ] 3.6 Create `planning_intelligence/test_llm_service.py`
  - Test intent classification
  - Test entity extraction
  - Test response generation
  - Test guardrails
  - Test no hallucinations

- [ ] 3.7 Create `planning_intelligence/test_mcp_context.py`
  - Test MCP context building
  - Test SAP field dictionary
  - Test semantic mapping
  - Test all context fields

- [ ] 3.8 Create `planning_intelligence/test_clarification.py`
  - Test incomplete query detection
  - Test clarification generation
  - Test guided exploration
  - Test option generation

- [ ] 3.9 Create `planning_intelligence/test_caching.py`
  - Test prompt caching
  - Test metrics caching
  - Test cache invalidation
  - Test performance improvement

- [ ] 3.10 Create `planning_intelligence/test_integration_phase3.py`
  - End-to-end tests for Phase 3
  - LLM integration tests
  - MCP context tests
  - Performance tests

---

## INTEGRATION & DEPLOYMENT

- [ ] 4.1 Update `planning_intelligence/nlp_endpoint.py`
  - Integrate IntentParser
  - Integrate EngineRouter
  - Integrate LLMService
  - Integrate CacheLayer
  - Add error handling

- [ ] 4.2 Update `planning_intelligence/function_app.py`
  - Update planning_intelligence_nlp endpoint
  - Integrate new components
  - Add logging
  - Add monitoring

- [ ] 4.3 Create `planning_intelligence/test_end_to_end_phase2_phase3.py`
  - Complete end-to-end tests
  - All 40+ prompt types
  - Real data scenarios
  - Performance validation

- [ ] 4.4 Create deployment guide
  - Document all changes
  - Document configuration
  - Document testing procedures
  - Document rollback procedures

- [ ] 4.5 Deploy to Azure
  - Update local.settings.json
  - Deploy backend
  - Verify in logs
  - Test from UI

---

## VALIDATION & TESTING

- [ ] 5.1 Correctness Validation
  - No zero/null errors when data exists
  - No global summary leakage
  - All prompt types produce correct scoped answers
  - Correct forecast/design/supplier/ROJ values

- [ ] 5.2 Performance Validation
  - First response <200ms
  - Cached response <5ms
  - Throughput 50+ prompts/sec
  - Cache hit rate >70%

- [ ] 5.3 Intelligence Validation
  - Azure OpenAI integration working
  - Intent classification accurate
  - Entity extraction accurate
  - Response generation intelligent

- [ ] 5.4 Production Readiness
  - All tests passing
  - No known issues
  - Documentation complete
  - Monitoring in place

---

## SUCCESS CRITERIA

### Phase 2 Complete When:
- ✅ All 11 requirements implemented
- ✅ All tests passing (100+ tests)
- ✅ No zero/null errors
- ✅ No global summary leakage
- ✅ All prompt types working correctly

### Phase 3 Complete When:
- ✅ All 6 requirements implemented
- ✅ Azure OpenAI integration working
- ✅ MCP context complete
- ✅ Performance targets met
- ✅ System production-ready

---

## PRIORITY ORDER

1. **CRITICAL (Week 1)**
   - 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8

2. **HIGH (Week 2)**
   - 2.1, 2.2, 2.3, 2.4, 2.5, 2.6

3. **MEDIUM (Week 3)**
   - 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10

4. **FINAL (Week 3-4)**
   - 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4

---

## ESTIMATED EFFORT

| Task | Effort | Duration |
|------|--------|----------|
| 1.1-1.8 | 40 hours | Week 1 |
| 2.1-2.6 | 40 hours | Week 2 |
| 3.1-3.10 | 40 hours | Week 3 |
| 4.1-5.4 | 20 hours | Week 3-4 |
| **Total** | **140 hours** | **2-3 weeks** |

---

## NOTES

- Correctness > Performance > Intelligence
- Do not proceed to optimization until correctness is fully validated
- All tests must pass before deployment
- Document all changes
- Monitor performance after deployment

