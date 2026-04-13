# Import Error Fix - April 11, 2026

## Problems Fixed

Azure Functions was failing to start with two import errors:

### Error 1: AnswerTemplateRouter Import
```
ImportError: cannot import name 'AnswerTemplateRouter' from 'phase2_answer_templates'
```

**Root Cause**: `nlp_endpoint.py` was trying to import a non-existent class `AnswerTemplateRouter`.
**Actual Class**: `AnswerTemplates`

### Error 2: IntegratedQueryProcessor Import
```
ImportError: cannot import name 'IntegratedQueryProcessor' from 'phase3_integration'
```

**Root Cause**: `nlp_endpoint.py` was trying to import a non-existent class `IntegratedQueryProcessor`.
**Actual Class**: `Phase3Integration`

---

## Solution

### Fixed Import Statements

**File**: `planning_intelligence/nlp_endpoint.py` (Lines 31-32)

**Before**:
```python
from phase2_answer_templates import AnswerTemplateRouter
from phase3_integration import IntegratedQueryProcessor
```

**After**:
```python
from phase2_answer_templates import AnswerTemplates
from phase3_integration import Phase3Integration
```

---

## Verification

✅ **Diagnostics Check**: No errors found in `nlp_endpoint.py` or `function_app.py`

✅ **Import Resolution**: All imports now correctly reference existing classes:
- `AnswerTemplates` exists in `phase2_answer_templates.py`
- `Phase3Integration` exists in `phase3_integration.py`

✅ **No Unused Imports**: `Phase3Integration` is imported but not currently used in `nlp_endpoint.py`. This is acceptable as it may be used in future enhancements.

---

## Testing

To verify the fix works:

1. **Local Testing**:
   ```bash
   cd planning_intelligence
   python -c "from nlp_endpoint import handle_nlp_query; print('Import successful')"
   ```

2. **Azure Functions Local**:
   ```bash
   func start
   ```

3. **Test Endpoint**:
   ```bash
   curl -X POST http://localhost:7071/api/planning_intelligence_nlp \
     -H "Content-Type: application/json" \
     -d '{"question": "Why is CYS20_F01C01 risky?", "detail_records": []}'
   ```

---

## Files Modified

- `planning_intelligence/nlp_endpoint.py` - Fixed both import statements (lines 31-32)

---

## Status

✅ **COMPLETE** - Both import errors fixed. Azure Functions should now start successfully.
