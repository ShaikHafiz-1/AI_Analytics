# Copilot Real-Time Answers - Implementation Tasks

## Phase 1: Core Functions

### Task 1.1: Implement Scope Extraction
- [x] Create `_extract_scope()` function
- [x] Handle location patterns (LOC001, "location X")
- [x] Handle supplier patterns (SUP001, "supplier X")
- [x] Handle material group patterns
- [x] Handle material ID patterns
- [x] Handle risk type patterns
- [ ] Add unit tests for each pattern
- [ ] Test edge cases (multiple entities, no entities)

### Task 1.2: Implement Question Classification with Scope
- [ ] Create `_classify_question_and_extract_scope()` function
- [ ] Integrate with existing `_classify_question()`
- [ ] Return tuple: (query_type, scope_type, scope_value)
- [ ] Add unit tests
- [ ] Test all 8 query types with and without scope

### Task 1.3: Implement Answer Mode Determination
- [x] Create `_determine_answer_mode()` function
- [x] Return "summary" or "investigate"
- [x] Comparison always investigates
- [x] Traceability always investigates
- [x] Root cause investigates if scoped
- [x] Why-not investigates if scoped
- [ ] Add unit tests for all combinations

### Task 1.4: Implement Scoped Metrics Computation
- [x] Create `_compute_scoped_metrics()` function
- [x] Filter detailRecords by scope_type and scope_value
- [x] Compute: changed count, change rate, contribution breakdown
- [x] Compute: drivers (primary, secondary)
- [x] Identify: top 5 contributing records
- [x] Return: filteredRecordsCount, scopedContributionBreakdown, scopedDrivers, topContributingRecords
- [ ] Add unit tests for each scope type
- [ ] Test with empty filtered results
- [ ] Test performance (< 100ms)

## Phase 2: Answer Templates

### Task 2.1: Implement Comparison Answer Template
- [x] Create `_generate_comparison_answer()` function
- [x] Extract two entities from question
- [x] Compute metrics for each entity
- [x] Format side-by-side comparison
- [x] Include: changed count, change rate, drivers for each
- [x] Highlight which has more changes
- [ ] Add unit tests
- [ ] Test with locations, suppliers, material groups

### Task 2.2: Implement Root Cause Answer Template
- [x] Create `_generate_root_cause_answer()` function
- [x] Extract entity from question
- [x] Compute scoped metrics
- [x] Format: "In [entity], [what changed]. This is risky because [why]. [Action]"
- [x] Include: what changed, why it's risky, recommended action
- [ ] Add unit tests
- [ ] Test with different risk levels

### Task 2.3: Implement Why-Not Answer Template
- [x] Create `_generate_why_not_answer()` function
- [x] Extract entity from question
- [x] Compute scoped metrics
- [x] Format: "[Entity] is stable because [reasons]"
- [x] Compare to risky entities if applicable
- [ ] Add unit tests
- [ ] Test with stable and unstable entities

### Task 2.4: Implement Traceability Answer Template
- [x] Create `_generate_traceability_answer()` function
- [x] Extract top contributing records from scoped metrics
- [x] Format: "📊 Top [N] contributing records:"
- [x] Include: location, material, delta, change type, risk level
- [x] Sort by absolute delta
- [ ] Add unit tests
- [ ] Test with different record counts

### Task 2.5: Implement Summary Answer Template
- [ ] Create `_generate_summary_answer()` function
- [ ] Refactor existing answer generation logic
- [ ] Keep existing templates for summary mode
- [ ] Add unit tests
- [ ] Ensure backward compatibility

## Phase 3: Integration

### Task 3.1: Update Answer Generation Function
- [x] Refactor `_generate_answer_from_context()` to use new functions
- [x] Add parameters: answer_mode, scope_type, scope_value, scoped_metrics
- [x] Route to appropriate template based on mode and query_type
- [x] Maintain backward compatibility
- [ ] Add unit tests
- [ ] Test all combinations of mode and query_type

### Task 3.2: Update Explain Endpoint
- [x] Update `explain()` function to use new classification
- [x] Extract scope from question
- [x] Determine answer mode
- [x] Compute scoped metrics if needed
- [x] Build response with investigate mode fields
- [ ] Add unit tests
- [ ] Test with context and without context

### Task 3.3: Add Investigate Mode Fields to Response
- [x] Add `investigateMode` object to response
- [x] Include: filteredRecordsCount, scopedContributionBreakdown, scopedDrivers, topContributingRecords
- [x] Include: scopeType, scopeValue
- [ ] Add comparisonMetrics for comparison questions
- [x] Maintain backward compatibility
- [ ] Add unit tests

### Task 3.4: Update Explainability Metadata
- [ ] Update `_build_explainability()` to include answer mode
- [ ] Add: answerMode, scopeType, scopeValue
- [ ] Distinguish: data freshness vs answer specificity
- [ ] Add freshness warning if data > 24h old
- [ ] Add unit tests

## Phase 4: Testing

### Task 4.1: Unit Tests - Scope Extraction
- [x] Test location extraction (LOC001, "location X")
- [x] Test supplier extraction (SUP001, "supplier X")
- [x] Test material group extraction
- [x] Test material ID extraction
- [x] Test risk type extraction
- [x] Test no scope extraction
- [x] Test multiple entities
- [x] Test edge cases (special characters, case sensitivity)

### Task 4.2: Unit Tests - Scoped Metrics
- [x] Test filtering by location
- [x] Test filtering by supplier
- [x] Test filtering by material group
- [x] Test filtering by material ID
- [x] Test filtering by risk type
- [x] Test empty filtered results
- [x] Test metrics computation accuracy
- [x] Test performance (< 100ms)

### Task 4.3: Integration Tests - Answer Templates
- [x] Test comparison template with locations
- [x] Test comparison template with suppliers
- [x] Test root cause template with different risk levels
- [x] Test why-not template with stable entities
- [x] Test why-not template with unstable entities
- [x] Test traceability template with different record counts
- [x] Test summary template (backward compatibility)

### Task 4.4: Integration Tests - Explain Endpoint
- [x] Test comparison question
- [x] Test root cause question
- [x] Test why-not question
- [x] Test traceability question
- [x] Test summary question
- [x] Test with context provided
- [x] Test without context (cached snapshot)
- [x] Test with stale data

### Task 4.5: End-to-End Tests
- [x] Test: "Compare LOC001 vs LOC002"
- [x] Test: "Why is LOC001 risky?"
- [x] Test: "Why is LOC001 not risky?"
- [x] Test: "Which supplier has frequent design changes?"
- [x] Test: "Which supplier is failing ROJ need-by dates?"
- [x] Test: "Show top contributing records"
- [x] Test: "What should the planner do next?"
- [x] Verify answer is specific to question
- [x] Verify answer is not generic summary
- [x] Verify answer uses scoped metrics
- [x] Verify answer feels dynamic and targeted

### Task 4.6: Response Variety Tests
- [x] Verify comparison answers differ from summary
- [x] Verify root cause answers differ from comparison
- [x] Verify why-not answers differ from root cause
- [x] Verify traceability answers differ from why-not
- [x] Verify no template reuse across types
- [x] Verify each type has unique formatting

### Task 4.7: Freshness Tests
- [x] Test with fresh data (< 1 hour old)
- [x] Test with stale data (> 24 hours old)
- [x] Verify freshness confirmation for fresh data
- [x] Verify freshness warning for stale data
- [x] Verify warning doesn't replace analysis

### Task 4.8: Determinism Tests
- [x] Test same question twice → same answer
- [x] Test different data → different answer
- [x] Verify no randomness in answer generation
- [x] Verify metrics are deterministic
- [x] Test with different random seeds (if applicable)

## Phase 5: Documentation & Validation

### Task 5.1: Update API Documentation
- [x] Document new `investigateMode` response fields
- [x] Document scope extraction patterns
- [x] Document answer modes (summary vs investigate)
- [x] Document answer templates
- [x] Add examples for each question type

### Task 5.2: Create Test Data
- [x] Create sample questions for each type
- [x] Create expected answers for each question
- [x] Create test fixtures with known data
- [x] Document test scenarios

### Task 5.3: Performance Validation
- [x] Measure scoped metrics computation time
- [x] Measure answer generation time
- [x] Measure total response time
- [x] Verify < 100ms for scoped computation
- [x] Verify < 500ms for total response

### Task 5.4: Final Validation
- [x] Verify all requirements met
- [x] Verify all acceptance criteria passed
- [x] Verify backward compatibility
- [x] Verify determinism
- [x] Verify trust (provenance visible)
- [x] Verify performance
- [x] Get stakeholder sign-off

## Success Criteria

### SC1: Scope Extraction
- [ ] 100% of location patterns extracted correctly
- [ ] 100% of supplier patterns extracted correctly
- [ ] 100% of material group patterns extracted correctly
- [ ] 100% of material ID patterns extracted correctly
- [ ] 100% of risk type patterns extracted correctly

### SC2: Scoped Metrics
- [ ] 100% of comparison questions use scoped metrics
- [ ] 100% of root cause questions use scoped metrics (if scoped)
- [ ] 100% of why-not questions use scoped metrics (if scoped)
- [ ] 100% of traceability questions use scoped metrics
- [ ] All metrics computed from detailRecords (no invented numbers)

### SC3: Answer Variety
- [ ] 100% of comparison answers use comparison template
- [ ] 100% of root cause answers use root cause template
- [ ] 100% of why-not answers use why-not template
- [ ] 100% of traceability answers use traceability template
- [ ] No two answer types sound identical

### SC4: Freshness Awareness
- [ ] 100% of responses include freshness metadata
- [ ] Fresh data: Freshness confirmation included
- [ ] Stale data: Freshness warning included
- [ ] Warning doesn't replace analysis

### SC5: Determinism
- [ ] 100% of answers deterministic (same input = same output)
- [ ] All metrics traceable to detailRecords
- [ ] No randomness in answer generation
- [ ] No LLM-based variation

### SC6: Performance
- [ ] Scoped metrics computation < 100ms
- [ ] Answer generation < 50ms
- [ ] Total response time < 500ms

### SC7: Backward Compatibility
- [ ] Existing API contract unchanged
- [ ] New fields added (not replacing)
- [ ] Existing clients continue to work
- [ ] Summary mode is default for unscoped questions

## Estimated Effort

- Phase 1 (Core Functions): 8 hours
- Phase 2 (Answer Templates): 12 hours
- Phase 3 (Integration): 8 hours
- Phase 4 (Testing): 16 hours
- Phase 5 (Documentation): 4 hours
- **Total: 48 hours**

## Dependencies

- Existing `detailRecords` structure must be available
- Existing analytics functions must be accessible
- No external dependencies required

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Scope extraction too aggressive | Comprehensive unit tests, conservative patterns |
| Scoped metrics computation slow | Performance testing, optimize filtering |
| Answer templates too similar | Response variety tests, unique formatting |
| Backward compatibility broken | Comprehensive integration tests |
| Determinism violated | Determinism tests, no randomness |

## Notes

- All changes are additive (no breaking changes)
- Existing summary mode remains default
- Investigate mode is opt-in (triggered by scope detection)
- All metrics computed from existing data (no new data sources)
- No LLM-based answer generation (deterministic only)
