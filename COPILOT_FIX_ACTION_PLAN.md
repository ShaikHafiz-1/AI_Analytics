# Copilot Fix - Quick Action Plan

## What Was Fixed

The question classification logic in the backend was prioritizing keywords incorrectly, causing:
- "Which materials are affected?" → Classified as "impact" instead of "entity"
- "List suppliers for CYS20_F01C01" → Classified correctly but answer generator wasn't being called

**Fix Applied**: Reordered classification priority to check Entity questions BEFORE Impact questions.

---

## Files Changed

**`planning_intelligence/function_app.py`** - Line 394
- Updated `classify_question()` function
- Moved Entity classification before Impact classification
- Added explicit "material" keyword check
- Reordered Risk before Health to avoid conflicts

---

## How to Verify the Fix

### Step 1: Restart Backend
```bash
cd planning_intelligence
func start
```

### Step 2: Test Classification
```bash
cd planning_intelligence
python test_classification_fix.py
```

Expected output: All 44 prompts classified correctly (100% pass rate)

### Step 3: Test in Copilot UI

Open the dashboard and test these key prompts:

1. **Entity Question**
   - Q: "List suppliers for CYS20_F01C01"
   - Expected: Location-specific supplier list
   - ✓ Should NOT return generic health summary

2. **Entity Question**
   - Q: "Which materials are affected?"
   - Expected: List of affected materials
   - ✓ Should NOT return generic health summary

3. **Comparison Question**
   - Q: "Compare CYS20_F01C01 vs DSM18_F01C01"
   - Expected: Side-by-side comparison
   - ✓ Should show metrics for both locations

4. **Impact Question**
   - Q: "Which supplier has the most impact?"
   - Expected: Ranked suppliers by impact
   - ✓ Should show top suppliers with change counts

5. **Health Question**
   - Q: "What's the planning health?"
   - Expected: Health score and status
   - ✓ Should show health/100 and change percentage

---

## Expected Results

### Before Fix
```
Q: "Which materials are affected?"
A: "Planning health is 37/100. 5,927 of 13,148 records have changed..."
   ✗ WRONG - Generic health answer instead of material list
```

### After Fix
```
Q: "Which materials are affected?"
A: "Top affected materials: UPS (1200 changes), POWER (950 changes), COOLING (750 changes)."
   ✓ CORRECT - Specific material impact answer
```

---

## Rollback Plan

If something goes wrong, revert the changes:

```bash
git checkout planning_intelligence/function_app.py
cd planning_intelligence
func start
```

---

## Monitoring

After deploying, monitor these logs:

1. **Backend logs** - Look for "Question type: X" messages
   - Should see correct classification for each question
   - Example: "Question type: entity" for "List suppliers..."

2. **Frontend console** - Check for API errors
   - Should see 200 responses from `/api/explain`
   - Should see correct answer in response

3. **Copilot responses** - Verify answers are specific
   - Entity questions → Location/supplier/material specific
   - Comparison questions → Side-by-side metrics
   - Impact questions → Ranked data
   - Health questions → Health score and status

---

## Success Criteria

✅ Classification test passes (44/44 prompts)
✅ Entity questions return specific answers
✅ Comparison questions return comparisons
✅ Impact questions return rankings
✅ No generic fallback answers
✅ All supporting metrics included
✅ Backend logs show correct classification

---

## Support

If you encounter issues:

1. **Check backend logs** for error messages
2. **Verify location ID format** - Should be like "CYS20_F01C01"
3. **Restart backend** - `func start`
4. **Clear browser cache** - Ctrl+Shift+Delete
5. **Test with simple prompts first** - "What's the health?" before complex ones

---

## Timeline

- **Immediate**: Restart backend and run classification test
- **5 minutes**: Test key prompts in Copilot UI
- **10 minutes**: Verify all 40+ prompts working
- **Ongoing**: Monitor logs for any issues

