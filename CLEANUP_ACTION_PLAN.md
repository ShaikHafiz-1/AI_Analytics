# Cleanup Action Plan

## Overview

This document provides a concrete action plan for cleaning up the codebase by removing irrelevant files and functions.

---

## PHASE 1: BACKEND CLEANUP (High Priority)

### Step 1: Delete Legacy Modules (8 files)

These are completely superseded by Phases 1-4:

```bash
# Delete legacy reasoning/NLP modules
rm planning_intelligence/reasoning_engine.py
rm planning_intelligence/clarification_engine.py
rm planning_intelligence/enhanced_intent_parser.py
rm planning_intelligence/generative_response_engine.py
rm planning_intelligence/insight_generator.py
rm planning_intelligence/ai_insight_engine.py
rm planning_intelligence/alert_rules.py
rm planning_intelligence/validation_guardrails.py
```

**Impact**: 
- Removes ~1,500 lines of dead code
- No functional impact (not imported anywhere)
- Reduces confusion about which NLP system to use

---

### Step 2: Delete Debugging Scripts (9 files)

These are one-off development utilities:

```bash
# Delete debugging scripts
rm planning_intelligence/check_snapshot_content.py
rm planning_intelligence/debug_blob.py
rm planning_intelligence/diagnose_data.py
rm planning_intelligence/discover_real_data.py
rm planning_intelligence/verify_fix_locally.py
rm planning_intelligence/run_daily_refresh.py
rm planning_intelligence/run_reasoning_tests.py
rm planning_intelligence/run_tests.py
rm planning_intelligence/performance_validation.py
```

**Impact**:
- Removes ~500 lines of debug code
- No functional impact (not used in production)
- Cleaner directory structure

---

### Step 3: Delete Alternative Data Loaders (2 files)

These are not used (system uses blob_loader):

```bash
# Delete alternative loaders
rm planning_intelligence/sharepoint_loader.py
rm planning_intelligence/data_mapper.py
```

**Impact**:
- Removes ~300 lines
- No functional impact (not imported)
- Clarifies data loading strategy

---

### Step 4: Delete Experimental Code (2 files)

These are demo/experimental:

```bash
# Delete experimental code
rm planning_intelligence/ui_app.py
rm planning_intelligence/demo_phase0.py
```

**Impact**:
- Removes ~200 lines
- No functional impact
- Reduces confusion

---

### Step 5: Delete Test Artifacts (15+ files)

These are build outputs, not source code:

```bash
# Delete test output files
rm planning_intelligence/test_output.txt
rm planning_intelligence/test_results.txt
rm planning_intelligence/test_results_*.json
rm planning_intelligence/test_report_*.txt
rm planning_intelligence/test_report_*.md
rm planning_intelligence/TEST_OUTPUT_44_PROMPTS.txt
rm planning_intelligence/PROMPT_REVIEW_REPORT.txt
rm planning_intelligence/REAL_DATA_PROMPT_REVIEW_REPORT.txt
rm planning_intelligence/discovered_data.json
```

**Impact**:
- Removes build artifacts
- No functional impact
- Cleaner repository

---

### Step 6: Clean Up function_app.py

Remove legacy endpoints and helper functions:

**Current file**: ~2,000 lines
**After cleanup**: ~400 lines

**Keep these endpoints**:
- ✅ `planning_intelligence_nlp()` - NLP endpoint
- ✅ `planning_dashboard_v2()` - Dashboard endpoint

**Remove these endpoints**:
- ❌ `planning_intelligence()` - Old trend analysis
- ❌ `reasoning_query()` - Old reasoning
- ❌ `planning_dashboard()` - Old dashboard v1
- ❌ `daily_refresh()` - Background refresh
- ❌ `explain()` - Old explain endpoint
- ❌ `debug_snapshot()` - Debug endpoint

**Remove these helper functions** (lines 522-1971):
- ❌ `_extract_scope()`
- ❌ `_determine_answer_mode()`
- ❌ `_compute_scoped_metrics()`
- ❌ `_generate_*_answer()` (all variants)
- ❌ `_build_*()` (all variants)
- ❌ `_handle_*()` (all variants)
- ❌ `_classify_question()`
- ❌ `_build_explainability()`
- ❌ `_build_suggested_actions()`
- ❌ `_build_follow_ups()`
- ❌ `_filter_snapshot()`

**Action**:
```python
# Keep only:
# - Imports
# - _normalize_detail_records()
# - _error()
# - _cors_response()
# - planning_intelligence_nlp()
# - planning_dashboard_v2()
# - app definition
```

**Impact**:
- Removes ~1,600 lines of legacy code
- Keeps only 2 active endpoints
- Much clearer codebase

---

### Step 7: Delete Outdated Documentation (4 files)

```bash
# Delete old documentation
rm planning_intelligence/DESIGN.md
rm planning_intelligence/API_DOCUMENTATION_COPILOT.md
rm planning_intelligence/INTEGRATION_WITH_ASK_COPILOT.md
rm planning_intelligence/local.settings.json
```

**Impact**:
- Removes outdated docs
- Use spec files instead
- Use .env for configuration

---

### Step 8: Archive Directories (2 directories)

```bash
# Archive non-core directories
mkdir -p planning_intelligence/archive
mv planning_intelligence/mcp planning_intelligence/archive/
mv planning_intelligence/samples planning_intelligence/archive/
```

**Impact**:
- Keeps for reference but out of main view
- Reduces clutter

---

## PHASE 2: FRONTEND CLEANUP (Medium Priority)

### Step 1: No Component Deletions

**All 18 components are relevant and actively used.**

No deletions needed.

---

### Step 2: Extract Large Component Logic

**DashboardPage.tsx** (600+ lines):
- Extract tooltip components to separate file
- Extract debug panel to separate file
- Extract skeleton components to separate file

**CopilotPanel.tsx** (546 lines):
- Extract `buildSmartPrompts()` to `promptGenerator.ts`
- Extract `buildFallbackAnswer()` to `answerGenerator.ts`
- Extract `buildFollowUps()` to `followUpGenerator.ts`
- Extract `filterDetailsByEntity()` to `entityFilter.ts`

**Impact**:
- Reduces component size
- Improves maintainability
- Enables reuse

---

## PHASE 3: DOCUMENTATION CLEANUP (Low Priority)

### Step 1: Archive Old Documentation

```bash
# Create archive directory
mkdir -p docs/archive

# Move old documentation
mv ARCHITECTURE.md docs/archive/
mv ARCHITECTURE_REVIEW_AND_IMPROVEMENTS.md docs/archive/
mv ARCHITECTURE_SUMMARY_VISUAL.md docs/archive/
mv COMPLETE_BUILD_REVIEW_SUMMARY.md docs/archive/
mv FINAL_DELIVERY_SUMMARY.md docs/archive/
mv IMMEDIATE_ACTION_PLAN.md docs/archive/
mv IMPLEMENTATION_CODE_EXAMPLES.md docs/archive/
mv IMPLEMENTATION_SUMMARY.md docs/archive/
mv INTEGRATION_GUIDE_PHASE3.md docs/archive/
mv PHASE2_PHASE3_IMPLEMENTATION_PLAN.md docs/archive/
mv PHASE2_PHASE3_QUICK_START.md docs/archive/
mv PHASE2_PHASE3_SPECIFICATION_INDEX.md docs/archive/
mv PHASE2_PHASE3_SUMMARY.md docs/archive/
mv PHASES_1_2_3_IMPLEMENTATION_COMPLETE.md docs/archive/
mv PHASES_1_3_COMPLETE_INDEX.md docs/archive/
mv PHASES_1_4_COMPLETE_SUMMARY.md docs/archive/
mv PHASES_4_5_NEXT_STEPS.md docs/archive/
mv PHASE_4_COMPREHENSIVE_TESTING_COMPLETE.md docs/archive/
mv QUICK_REFERENCE_CARD.md docs/archive/
mv QUICK_START_PHASES_1_3.md docs/archive/
mv README_PHASE2_PHASE3.md docs/archive/
```

**Impact**:
- Keeps historical documentation
- Reduces root directory clutter
- Easier to find current docs

---

### Step 2: Keep Current Documentation

**Keep in root**:
- ✅ `.kiro/specs/` - Current spec files
- ✅ `IRRELEVANT_FILES_AND_FUNCTIONS_ANALYSIS.md` - Cleanup guide
- ✅ `COPILOT_DATA_FLOW_ARCHITECTURE.md` - Architecture reference
- ✅ `FRONTEND_CODE_REVIEW_AND_ANALYSIS.md` - Frontend guide
- ✅ `COMPLETE_SYSTEM_REVIEW_SUMMARY.md` - System overview
- ✅ `CLEANUP_ACTION_PLAN.md` - This file

---

## CLEANUP SUMMARY

### Backend Cleanup

| Category | Files | Lines | Action |
|----------|-------|-------|--------|
| Legacy Modules | 8 | 1,500 | Delete |
| Debug Scripts | 9 | 500 | Delete |
| Alternative Loaders | 2 | 300 | Delete |
| Experimental | 2 | 200 | Delete |
| Test Artifacts | 15+ | - | Delete |
| Old Docs | 4 | - | Delete |
| function_app.py | 1 | 1,600 | Remove legacy code |
| **Total** | **41** | **~4,100** | **Delete/Clean** |

### Frontend Cleanup

| Category | Files | Action |
|----------|-------|--------|
| Components | 18 | Keep all |
| Large Components | 2 | Refactor (extract logic) |
| **Total** | **18** | **Keep, refactor 2** |

### Documentation Cleanup

| Category | Files | Action |
|----------|-------|--------|
| Old Docs | 21 | Archive |
| Current Docs | 5 | Keep |
| Spec Files | 5 | Keep |
| **Total** | **31** | **Archive 21, Keep 26** |

---

## EXECUTION STEPS

### Step 1: Backup (5 minutes)
```bash
git commit -m "Backup before cleanup"
git branch backup/pre-cleanup
```

### Step 2: Delete Backend Files (10 minutes)
```bash
# Run all delete commands from Phase 1
```

### Step 3: Clean function_app.py (30 minutes)
```bash
# Manually edit to keep only 2 endpoints
# Test with: pytest test_nlp_endpoint.py test_end_to_end.py
```

### Step 4: Refactor Frontend (1-2 hours)
```bash
# Extract CopilotPanel logic
# Extract DashboardPage components
# Test with: npm run build
```

### Step 5: Archive Documentation (10 minutes)
```bash
# Move old docs to archive
# Verify current docs are accessible
```

### Step 6: Verify (30 minutes)
```bash
# Run all tests
pytest planning_intelligence/test_*.py

# Build frontend
npm run build

# Check for import errors
grep -r "reasoning_engine\|clarification_engine" planning_intelligence/
```

### Step 7: Commit (5 minutes)
```bash
git add -A
git commit -m "Cleanup: Remove legacy code and documentation"
git push
```

---

## ROLLBACK PLAN

If anything breaks:

```bash
# Rollback to backup
git checkout backup/pre-cleanup

# Or rollback specific file
git checkout HEAD~1 planning_intelligence/function_app.py
```

---

## VERIFICATION CHECKLIST

After cleanup, verify:

- ✅ All tests pass: `pytest planning_intelligence/test_*.py`
- ✅ Frontend builds: `npm run build`
- ✅ No import errors: `grep -r "reasoning_engine\|clarification_engine" planning_intelligence/`
- ✅ No broken references: `grep -r "planning_intelligence()\|reasoning_query()" frontend/`
- ✅ API endpoints work: Test with Postman/curl
- ✅ Dashboard loads: Open in browser
- ✅ Copilot works: Send test question

---

## EXPECTED RESULTS

### Before Cleanup
- 80+ files in planning_intelligence/
- ~2,500 lines active code + ~3,000 lines legacy
- 2,000 lines in function_app.py
- 21 old documentation files in root

### After Cleanup
- 30 files in planning_intelligence/
- ~2,500 lines active code only
- 400 lines in function_app.py
- 5 current documentation files in root
- 21 archived documentation files

### Benefits
- ✅ 50% fewer files
- ✅ 60% less legacy code
- ✅ Clearer codebase
- ✅ Easier to navigate
- ✅ Reduced confusion
- ✅ Faster development

---

## TIMELINE

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Backend Cleanup | 1-2 hours | High |
| Phase 2: Frontend Refactor | 2-4 hours | Medium |
| Phase 3: Documentation | 30 minutes | Low |
| **Total** | **3-7 hours** | - |

---

## RECOMMENDATION

**Execute immediately after deployment to production.**

This cleanup will:
- Reduce technical debt
- Improve code clarity
- Accelerate future development
- Reduce onboarding time for new developers
- Make the codebase more maintainable

