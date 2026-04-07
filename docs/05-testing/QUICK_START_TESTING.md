# Quick Start Testing Guide

## What Was Done

✅ **Fixed 2 Critical Bugs**:
1. Comparison query AttributeError - "Compare LOC001 vs LOC002" now works
2. Design/Form Factor query filtering - "Which materials have Form Factor changes?" now filters correctly

✅ **Added Enhancements**:
1. Detail level support - responses can show summary/detailed/full information
2. Response tips - guides users to ask follow-up questions
3. Automated testing - Python script to test all 44 prompts

---

## How to Test

### Option 1: Manual Testing (5-10 minutes)
1. Restart backend: `func start`
2. Restart frontend: `npm start`
3. Open Copilot in UI
4. Test a few key prompts:
   - "Compare AVC11_F01C01 vs LOC001" (Comparison)
   - "Which materials have Form Factor changes?" (Design filter)
   - "List suppliers for AVC11_F01C01" (Supplier)
   - "Why is AVC11_F01C01 risky?" (Root cause)

### Option 2: Automated Testing (2-3 minutes)
```bash
cd planning_intelligence
python test_all_44_prompts.py
```

This will:
- Test all 44 prompts automatically
- Show pass/fail for each
- Calculate pass rate
- Save results to JSON file

---

## Expected Results

### Manual Testing
- Responses should include relevant data/metrics
- No errors in console
- Response time < 500ms

### Automated Testing
- Pass rate >= 90% (40+ out of 44)
- All critical query types work
- No errors in logs

---

## Key Prompts to Test

### Supplier Queries
```
List suppliers for AVC11_F01C01
Which suppliers at AVC11_F01C01 have design changes?
```

### Comparison Queries
```
Compare AVC11_F01C01 vs LOC001
Compare PUMP vs VALVE
```

### Design/BOD Queries
```
Which materials have Form Factor changes?
Which materials have BOD changes?
Any design changes at AVC11_F01C01?
```

### Root Cause Queries
```
Why is AVC11_F01C01 risky?
Why is LOC001 not risky?
```

### Traceability Queries
```
Show top contributing records
Which records are highest risk?
```

---

## Detail Level Options

After getting a response, you can ask for more details:

**Summary** (default):
```
List suppliers for AVC11_F01C01
→ Shows basic metrics
```

**Detailed**:
```
Show more details
→ Adds Location ID, Equipment Category, Supplier info
```

**Full**:
```
Show all details
→ Complete record details with all fields
```

---

## Troubleshooting

### If a prompt fails:
1. Check backend logs for errors
2. Verify data is loaded in blob storage
3. Try a similar prompt
4. Check `test_results_44_prompts.json` for details

### If pass rate < 90%:
1. Identify which prompts failed
2. Check the error messages
3. Fix the issue in `function_app.py`
4. Re-run tests

### If response is slow (> 500ms):
1. Check backend performance
2. Verify data size
3. Check network latency
4. Optimize query if needed

---

## Files to Review

- `COMPREHENSIVE_TESTING_PLAN.md` - Complete testing guide with all 44 prompts
- `TESTING_AND_ENHANCEMENT_SUMMARY.md` - Detailed summary of changes
- `planning_intelligence/test_all_44_prompts.py` - Automated test script
- `planning_intelligence/function_app.py` - Implementation

---

## Success Criteria

✓ **SUCCESS** if:
- Pass rate >= 90% (40+ out of 44)
- All critical query types work
- No major errors in logs
- Response times < 500ms

---

## Next Steps

1. **Run Tests**
   - Manual: Test key prompts in UI
   - Automated: Run `python test_all_44_prompts.py`

2. **Review Results**
   - Check pass/fail for each prompt
   - Identify any failures

3. **Fix Issues**
   - For each failure, identify root cause
   - Implement fix
   - Re-test

4. **Deploy**
   - Once pass rate >= 90%
   - Deploy to production

---

## Questions?

Refer to:
- `COMPREHENSIVE_TESTING_PLAN.md` for detailed testing guide
- `TESTING_AND_ENHANCEMENT_SUMMARY.md` for technical details
- Backend logs for error messages

