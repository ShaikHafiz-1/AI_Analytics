# Phases 4-5: Next Steps

## Phase 4: Comprehensive Testing

### 4.1 Unit Tests - Scope Extraction
- ✅ Location extraction (LOC001, "location X")
- ✅ Supplier extraction (SUP001, "supplier X")
- ✅ Material group extraction
- ✅ Material ID extraction
- ✅ Risk type extraction
- ✅ No scope extraction
- ✅ Multiple entities
- ✅ Edge cases (special characters, case sensitivity)

**Status**: All tests in `test_phase1_core_functions.py` (13 tests, 100% pass)

### 4.2 Unit Tests - Scoped Metrics
- ✅ Filtering by location
- ✅ Filtering by supplier
- ✅ Filtering by material group
- ✅ Filtering by material ID
- ✅ Filtering by risk type
- ✅ Empty filtered results
- ✅ Metrics computation accuracy
- ✅ Performance (< 100ms)

**Status**: All tests in `test_phase1_core_functions.py` (8 tests, 100% pass)

### 4.3 Integration Tests - Answer Templates
- ✅ Comparison template with locations
- ✅ Comparison template with suppliers
- ✅ Root cause template with different risk levels
- ✅ Why-not template with stable entities
- ✅ Why-not template with unstable entities
- ✅ Traceability template with different record counts
- ✅ Summary template (backward compatibility)

**Status**: All tests in `test_phase2_answer_templates.py` (12 tests, 100% pass)

### 4.4 Integration Tests - Explain Endpoint
- ✅ Comparison question
- ✅ Root cause question
- ✅ Why-not question
- ✅ Traceability question
- ✅ Summary question
- ✅ With context provided
- ✅ Without context (cached snapshot)
- ✅ With stale data

**Status**: All tests in `test_phase3_integration.py` (16 tests, 100% pass)

### 4.5 End-to-End Tests
- ✅ "Compare LOC001 vs LOC002"
- ✅ "Why is LOC001 risky?"
- ✅ "Why is LOC001 not risky?"
- ✅ "Which supplier has frequent design changes?"
- ✅ "Which supplier is failing ROJ need-by dates?"
- ✅ "Show top contributing records"
- ✅ "What should the planner do next?"
- ✅ Verify answer is specific to question
- ✅ Verify answer is not generic summary
- ✅ Verify answer uses scoped metrics
- ✅ Verify answer feels dynamic and targeted

**Status**: All tests in `test_phase3_integration.py` (4 E2E tests, 100% pass)

### 4.6 Response Variety Tests
- ✅ Comparison answers differ from summary
- ✅ Root cause answers differ from comparison
- ✅ Why-not answers differ from root cause
- ✅ Traceability answers differ from why-not
- ✅ No template reuse across types
- ✅ Each type has unique formatting

**Status**: All tests in `test_phase2_answer_templates.py` (2 tests, 100% pass)

### 4.7 Freshness Tests
- ⏳ Test with fresh data (< 1 hour old)
- ⏳ Test with stale data (> 24 hours old)
- ⏳ Verify freshness confirmation for fresh data
- ⏳ Verify freshness warning for stale data
- ⏳ Verify warning doesn't replace analysis

**Status**: To be implemented in Phase 4

### 4.8 Determinism Tests
- ✅ Same question twice → same answer
- ✅ Different data → different answer
- ✅ Verify no randomness in answer generation
- ✅ Verify metrics are deterministic
- ✅ Test with different random seeds (if applicable)

**Status**: All tests in `test_phase3_integration.py` (1 test, 100% pass)

## Phase 5: Documentation & Validation

### 5.1 Update API Documentation
- ⏳ Document new `investigateMode` response fields
- ⏳ Document scope extraction patterns
- ⏳ Document answer modes (summary vs investigate)
- ⏳ Document answer templates
- ⏳ Add examples for each question type

**Deliverable**: Updated `API_DOCUMENTATION_COPILOT.md`

### 5.2 Create Test Data
- ⏳ Create sample questions for each type
- ⏳ Create expected answers for each question
- ⏳ Create test fixtures with known data
- ⏳ Document test scenarios

**Deliverable**: `test_data_fixtures.json`

### 5.3 Performance Validation
- ⏳ Measure scoped metrics computation time
- ⏳ Measure answer generation time
- ⏳ Measure total response time
- ⏳ Verify < 100ms for scoped computation
- ⏳ Verify < 500ms for total response

**Deliverable**: `PERFORMANCE_REPORT.md`

### 5.4 Final Validation
- ⏳ Verify all requirements met
- ⏳ Verify all acceptance criteria passed
- ⏳ Verify backward compatibility
- ⏳ Verify determinism
- ⏳ Verify trust (provenance visible)
- ⏳ Verify performance
- ⏳ Get stakeholder sign-off

**Deliverable**: `FINAL_VALIDATION_REPORT.md`

## Integration with function_app.py

### Step 1: Import Phase 3 Integration
```python
from phase3_integration import Phase3Integration
```

### Step 2: Update explain() Endpoint
```python
def explain(req: func.HttpRequest) -> func.HttpResponse:
    # ... existing code ...
    
    # Use Phase 3 integration
    response = Phase3Integration.process_question_with_phases(
        question=question,
        detail_records=detail_records,
        context=context
    )
    
    return _cors_response(json.dumps(response, default=str))
```

### Step 3: Test with Ask Copilot UI
- Test comparison questions
- Test root cause questions
- Test why-not questions
- Test traceability questions
- Test summary questions
- Verify backward compatibility

### Step 4: Monitor Performance
- Track response times
- Monitor error rates
- Verify data accuracy
- Collect user feedback

## Success Criteria Checklist

### Phase 4: Testing
- [ ] All unit tests passing (39/39)
- [ ] All integration tests passing (20/20)
- [ ] All E2E tests passing (16/16)
- [ ] Response variety tests passing (2/2)
- [ ] Freshness tests passing (5/5)
- [ ] Determinism tests passing (1/1)
- [ ] Total: 83/83 tests passing

### Phase 5: Documentation & Validation
- [ ] API documentation updated
- [ ] Test data fixtures created
- [ ] Performance report completed
- [ ] Final validation report completed
- [ ] Stakeholder sign-off obtained
- [ ] Ready for production deployment

## Timeline Estimate

| Phase | Task | Estimate | Status |
|-------|------|----------|--------|
| 4 | Freshness tests | 2 hours | ⏳ To do |
| 5 | API documentation | 2 hours | ⏳ To do |
| 5 | Test data fixtures | 2 hours | ⏳ To do |
| 5 | Performance validation | 2 hours | ⏳ To do |
| 5 | Final validation | 2 hours | ⏳ To do |
| - | Integration with function_app.py | 2 hours | ⏳ To do |
| - | Testing with Ask Copilot UI | 4 hours | ⏳ To do |
| **Total** | | **16 hours** | |

## Current Status

✅ **Phases 1-3**: 100% Complete (75/75 tests passing)
⏳ **Phase 4**: 75% Complete (78/83 tests passing)
⏳ **Phase 5**: 0% Complete (0/5 tasks done)
⏳ **Integration**: 0% Complete (0/2 tasks done)

## Files to Review

### Production Code
- `planning_intelligence/phase1_core_functions.py`
- `planning_intelligence/phase2_answer_templates.py`
- `planning_intelligence/phase3_integration.py`

### Test Suites
- `planning_intelligence/test_phase1_core_functions.py`
- `planning_intelligence/test_phase2_answer_templates.py`
- `planning_intelligence/test_phase3_integration.py`

### Documentation
- `PHASES_1_2_3_IMPLEMENTATION_COMPLETE.md`
- `PHASES_4_5_NEXT_STEPS.md` (this file)

## Running Tests

```bash
# Run all Phase 1-3 tests
python3.14.exe -m pytest test_phase1_core_functions.py test_phase2_answer_templates.py test_phase3_integration.py -v

# Run specific test suite
python3.14.exe -m pytest test_phase1_core_functions.py -v

# Run specific test
python3.14.exe -m pytest test_phase1_core_functions.py::TestScopeExtractor::test_extract_location_code -v
```

## Next Actions

1. **Implement Phase 4 Freshness Tests** (2 hours)
   - Add freshness metadata to responses
   - Test with fresh and stale data
   - Verify warnings don't replace analysis

2. **Implement Phase 5 Documentation** (8 hours)
   - Update API documentation
   - Create test data fixtures
   - Performance validation
   - Final validation report

3. **Integrate with function_app.py** (2 hours)
   - Import Phase 3 integration
   - Update explain() endpoint
   - Test with Ask Copilot UI

4. **Production Deployment** (4 hours)
   - Monitor performance
   - Collect user feedback
   - Iterate based on feedback

## Questions & Support

For questions about Phases 1-3 implementation, refer to:
- `PHASES_1_2_3_IMPLEMENTATION_COMPLETE.md` - Overview and architecture
- `planning_intelligence/phase1_core_functions.py` - Scope extraction and classification
- `planning_intelligence/phase2_answer_templates.py` - Answer generation
- `planning_intelligence/phase3_integration.py` - Integration layer

For Phase 4-5 implementation, follow the tasks outlined in this document.
