# Irrelevant Files and Functions Analysis

## Executive Summary

After analyzing the codebase, we've identified **files and functions that are NOT relevant** to the core Copilot Real-Time Answers system (Phases 1-4). These are legacy, debugging, or experimental code that can be safely ignored or removed.

---

## IRRELEVANT FILES (Can be deleted or archived)

### 1. **Debugging & Diagnostic Scripts**
These are one-off scripts used for development/debugging:

- `check_snapshot_content.py` - Debug script to inspect snapshot content
- `debug_blob.py` - Debug script for blob storage issues
- `diagnose_data.py` - Data diagnosis utility
- `discover_real_data.py` - Script to discover real data structure
- `discovered_data.json` - Output from data discovery
- `verify_fix_locally.py` - Local verification script
- `run_daily_refresh.py` - Manual refresh runner
- `run_reasoning_tests.py` - Manual test runner
- `run_tests.py` - Manual test runner

**Status**: Not used in production. Safe to delete.

---

### 2. **Legacy/Experimental Modules**
These are older implementations that have been superseded:

- `reasoning_engine.py` - **LEGACY**: Replaced by Phase 1-3 pipeline
  - Contains old `ReasoningEngine`, `EntityExtractor`, `IntentClassifier`
  - Not imported by any active endpoint
  - Superseded by `phase1_core_functions.py`, `phase2_answer_templates.py`, `phase3_integration.py`

- `clarification_engine.py` - **LEGACY**: Old clarification logic
  - Not used in current NLP pipeline
  - Replaced by Azure OpenAI integration in `nlp_endpoint.py`

- `enhanced_intent_parser.py` - **LEGACY**: Old intent parsing
  - Not imported by active code
  - Replaced by `phase1_core_functions.QuestionClassifier`

- `generative_response_engine.py` - **LEGACY**: Old response generation
  - Not used in current pipeline
  - Replaced by `phase2_answer_templates.py`

- `insight_generator.py` - **LEGACY**: Old insight generation
  - Not used in current system
  - Functionality absorbed into Phase 2-3

- `ai_insight_engine.py` - **LEGACY**: Old AI insight engine
  - Not imported anywhere
  - Replaced by Azure OpenAI integration

- `alert_rules.py` - **LEGACY**: Old alert system
  - Not used in current Copilot
  - Not imported by any active code

- `validation_guardrails.py` - **LEGACY**: Old validation logic
  - Not used in current pipeline
  - Replaced by validation in `azure_openai_integration.py`

**Status**: Superseded by Phases 1-4. Safe to delete.

---

### 3. **Data Loading Alternatives**
These are alternative data sources that are not used:

- `sharepoint_loader.py` - **UNUSED**: SharePoint data loading
  - Not imported by any active code
  - System uses `blob_loader.py` instead

- `data_mapper.py` - **UNUSED**: Old data mapping logic
  - Not imported by active code
  - Functionality in `normalizer.py`

**Status**: Not used. Safe to delete.

---

### 4. **UI/Demo Code**
These are experimental UI or demo code:

- `ui_app.py` - **EXPERIMENTAL**: Standalone UI app
  - Not part of the main system
  - Frontend is in `frontend/` directory

- `demo_phase0.py` - **DEMO**: Phase 0 demonstration
  - Not used in production
  - Superseded by Phases 1-4

**Status**: Demo/experimental. Safe to delete.

---

### 5. **Test Output & Reports**
These are test artifacts and reports:

- `test_output.txt` - Test output artifact
- `test_results.txt` - Test results artifact
- `test_results_*.json` - Various test result files
- `test_report_*.txt` - Test report artifacts
- `test_report_*.md` - Test report artifacts
- `TEST_OUTPUT_44_PROMPTS.txt` - Test output artifact
- `PROMPT_REVIEW_REPORT.txt` - Prompt review artifact
- `REAL_DATA_PROMPT_REVIEW_REPORT.txt` - Prompt review artifact
- `performance_validation.py` - Performance validation script (not used in tests)

**Status**: Build artifacts. Safe to delete.

---

### 6. **Configuration & Documentation**
These are configuration files that may be outdated:

- `local.settings.json` - Local development settings (should use .env)
- `DESIGN.md` - Old design document (superseded by spec files)
- `API_DOCUMENTATION_COPILOT.md` - Old API docs
- `INTEGRATION_WITH_ASK_COPILOT.md` - Old integration guide

**Status**: Outdated documentation. Can be archived.

---

### 7. **Directories**
- `mcp/` - MCP-related code (not part of core Copilot)
- `samples/` - Sample data/code (not used in production)

**Status**: Not part of core system. Can be archived.

---

## IRRELEVANT FUNCTIONS (In active files)

### In `function_app.py`:

These functions are NOT used by the Copilot Real-Time Answers system:

1. **`planning_intelligence()`** (Line 143)
   - Old endpoint for trend analysis
   - Not called by Copilot UI
   - Uses legacy analytics pipeline

2. **`reasoning_query()`** (Line 305)
   - Old reasoning endpoint
   - Not called by Copilot UI
   - Superseded by NLP endpoint

3. **`planning_dashboard()`** (Line 402)
   - Old dashboard endpoint (v1)
   - Replaced by `planning_dashboard_v2()`

4. **`daily_refresh()`** (Line 495)
   - Scheduled refresh function
   - Not called by Copilot UI
   - Used for background snapshot updates

5. **`explain()`** (Line 1282)
   - Old explain endpoint
   - Not called by Copilot UI
   - Superseded by NLP endpoint

6. **`debug_snapshot()`** (Line 1986)
   - Debug endpoint
   - Not called by Copilot UI
   - Used only for debugging

7. **Helper functions** (Lines 522-1971)
   - `_extract_scope()`, `_determine_answer_mode()`, `_compute_scoped_metrics()`
   - `_generate_*_answer()` functions
   - `_build_*()` functions
   - These are all part of the old pipeline
   - Replaced by Phase 1-3 functions

**Status**: Legacy endpoints. Not used by Copilot. Can be removed.

---

### In `reasoning_engine.py`:

All functions in this file are LEGACY:

- `EntityExtractor` class - Replaced by Phase 1
- `IntentClassifier` class - Replaced by Phase 1
- `ScopedComputation` class - Replaced by Phase 1
- `ResponseGenerator` class - Replaced by Phase 2
- `ReasoningEngine` class - Replaced by Phase 3

**Status**: Entire file is legacy. Can be deleted.

---

### In `clarification_engine.py`:

All functions are LEGACY and not used:

- `ClarificationEngine` class - Replaced by Azure OpenAI integration

**Status**: Entire file is legacy. Can be deleted.

---

## ACTIVE/RELEVANT FILES (Keep these)

### Core Copilot Pipeline:
- ✅ `phase1_core_functions.py` - Question classification, scope extraction
- ✅ `phase2_answer_templates.py` - Answer generation templates
- ✅ `phase3_integration.py` - Integrated query processor
- ✅ `azure_openai_integration.py` - LLM integration
- ✅ `nlp_endpoint.py` - NLP endpoint handler

### Data Processing:
- ✅ `blob_loader.py` - Load data from Azure Blob
- ✅ `normalizer.py` - Normalize data format
- ✅ `filters.py` - Filter records
- ✅ `comparator.py` - Compare current vs previous
- ✅ `snapshot_store.py` - Cache snapshots

### Dashboard/Response Building:
- ✅ `dashboard_builder.py` - Build dashboard response
- ✅ `response_builder.py` - Build response objects
- ✅ `analytics.py` - Analytics computations
- ✅ `trend_analyzer.py` - Trend analysis

### Tests:
- ✅ `test_phase1_core_functions.py` - Phase 1 tests
- ✅ `test_phase2_answer_templates.py` - Phase 2 tests
- ✅ `test_phase3_integration.py` - Phase 3 tests
- ✅ `test_phase4_comprehensive.py` - Phase 4 tests
- ✅ `test_nlp_endpoint.py` - NLP endpoint tests
- ✅ `test_end_to_end.py` - E2E tests

### Configuration:
- ✅ `function_app.py` - Main entry point (keep, but remove legacy endpoints)
- ✅ `host.json` - Azure Functions config
- ✅ `requirements.txt` - Dependencies
- ✅ `.env.example` - Environment template
- ✅ `sap_schema.py` - SAP schema definitions
- ✅ `models.py` - Data models

---

## ACTIVE ENDPOINTS (Keep these)

Only these endpoints are used by Copilot UI:

1. **`planning_intelligence_nlp`** (Line 271)
   - Handles natural language questions
   - Routes to `nlp_endpoint.handle_nlp_query()`
   - **KEEP**

2. **`planning_dashboard_v2`** (Line 446)
   - Returns dashboard data
   - Uses cached snapshot or loads from blob
   - **KEEP**

---

## RECOMMENDATION

### Immediate Actions:

1. **Delete these files** (safe to remove):
   - All debugging scripts (check_snapshot_content.py, debug_blob.py, etc.)
   - All legacy modules (reasoning_engine.py, clarification_engine.py, etc.)
   - All test artifacts (test_output.txt, test_results_*.json, etc.)
   - Experimental code (ui_app.py, demo_phase0.py)
   - Alternative loaders (sharepoint_loader.py, data_mapper.py)

2. **Archive these directories**:
   - `mcp/` - Not part of core Copilot
   - `samples/` - Not used in production

3. **Clean up function_app.py**:
   - Remove legacy endpoints: `planning_intelligence()`, `reasoning_query()`, `planning_dashboard()`, `daily_refresh()`, `explain()`, `debug_snapshot()`
   - Remove helper functions (lines 522-1971) that support legacy endpoints
   - Keep only: `planning_intelligence_nlp()`, `planning_dashboard_v2()`, and their helpers

4. **Update documentation**:
   - Archive old docs (DESIGN.md, API_DOCUMENTATION_COPILOT.md, INTEGRATION_WITH_ASK_COPILOT.md)
   - Keep only current spec files in `.kiro/specs/`

---

## CODEBASE CLEANUP IMPACT

**Before cleanup**: ~80 files, ~2,500 lines of active code + ~3,000 lines of legacy code

**After cleanup**: ~30 files, ~2,500 lines of active code

**Benefit**: 
- Easier to understand and maintain
- Faster to navigate codebase
- Clearer separation of concerns
- Reduced confusion about what's actually used

---

## SUMMARY TABLE

| Category | Files | Status | Action |
|----------|-------|--------|--------|
| Core Pipeline | 5 | Active | Keep |
| Data Processing | 5 | Active | Keep |
| Dashboard/Response | 3 | Active | Keep |
| Tests | 6 | Active | Keep |
| Configuration | 4 | Active | Keep |
| **Debugging Scripts** | **9** | **Unused** | **Delete** |
| **Legacy Modules** | **8** | **Superseded** | **Delete** |
| **Alternative Loaders** | **2** | **Unused** | **Delete** |
| **Experimental UI** | **2** | **Demo** | **Delete** |
| **Test Artifacts** | **15+** | **Build Output** | **Delete** |
| **Old Docs** | **4** | **Outdated** | **Archive** |
| **Directories** | **2** | **Not Core** | **Archive** |

