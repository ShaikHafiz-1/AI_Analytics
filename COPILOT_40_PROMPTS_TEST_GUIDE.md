# Copilot 40+ Prompts Test Guide

## Overview

This guide provides all the test prompts organized by category to verify the Copilot fix works correctly for all question types.

---

## Health Questions (5 prompts)

These should return health score, status, changed records, and primary drivers.

1. ✅ "What's the current planning health status?"
2. ✅ "What's the planning health?"
3. ✅ "Is planning healthy?"
4. ✅ "What's the health score?"
5. ✅ "How is planning health?"

**Expected Answer Pattern**: "Planning health is X/100 (Status). Y of Z records have changed. Primary drivers: Design changes (X), Supplier changes (Y)."

---

## Forecast Questions (5 prompts)

These should return forecast data, trends, and deltas.

1. ✅ "What's the forecast?"
2. ✅ "What's the trend?"
3. ✅ "What's the delta?"
4. ✅ "What's the forecast trend?"
5. ✅ "What units are forecasted?"

**Expected Answer Pattern**: "Forecast data with trend information..."

---

## Risk Questions (8 prompts)

These should return risk level, highest risk type, high-risk count, and breakdown.

1. ✅ "What are the top risks?"
2. ✅ "What are the risks?"
3. ✅ "What's the main issue?"
4. ✅ "What's the biggest risk?"
5. ✅ "Are there any risks?"
6. ✅ "What's risky?"
7. ✅ "What's dangerous?"
8. ✅ "What's the high-risk situation?"

**Expected Answer Pattern**: "Risk level is X. Highest risk type: Y. Z high-risk records out of W total (P%). Breakdown: Design (X), Supplier (Y), Quantity (Z)."

---

## Change Questions (8 prompts)

These should return changed count and breakdown by type.

1. ✅ "How many records have changed?"
2. ✅ "What changes have occurred?"
3. ✅ "What's changed?"
4. ✅ "How many changes?"
5. ✅ "What quantity changes?"
6. ✅ "What design changes?"
7. ✅ "What supplier changes?"
8. ✅ "What's the ROJ?"

**Expected Answer Pattern**: "X records have changed out of Y total (P%). Breakdown: Design (X), Supplier (Y), Quantity (Z)."

---

## Entity Questions (8 prompts) - NEW

These should return suppliers, materials, or locations affected.

1. ✅ "List suppliers for CYS20_F01C01"
2. ✅ "Which materials are affected?"
3. ✅ "Which suppliers at CYS20_F01C01 have design changes?"
4. ✅ "What suppliers are involved?"
5. ✅ "What materials are involved?"
6. ✅ "List materials for DSM18_F01C01"
7. ✅ "Which locations are affected?"
8. ✅ "What groups are affected?"

**Expected Answer Pattern**: 
- With location: "Location CYS20_F01C01: X records. Suppliers: A, B, C. Materials: M1, M2. Changed: Y."
- Without location: "Top affected suppliers: Supplier A (X changes), Supplier B (Y changes). Top affected materials: MAT001 (X changes), MAT002 (Y changes)."

---

## Comparison Questions (6 prompts) - NEW

These should return side-by-side comparison of two locations.

1. ✅ "Compare CYS20_F01C01 vs DSM18_F01C01"
2. ✅ "What's the difference between CYS20_F01C01 and DSM18_F01C01?"
3. ✅ "Compare DSM18_F01C01 versus CYS20_F01C01"
4. ✅ "CYS20_F01C01 vs DSM18_F01C01"
5. ✅ "Difference between CYS20_F01C01 and DSM18_F01C01"
6. ✅ "Compare locations CYS20_F01C01 and DSM18_F01C01"

**Expected Answer Pattern**: "Comparison: CYS20_F01C01 vs DSM18_F01C01. CYS20_F01C01: X records, Y changed. DSM18_F01C01: Z records, W changed."

---

## Impact Questions (6 prompts) - NEW

These should return suppliers/materials ranked by impact (changes).

1. ✅ "Which supplier has the most impact?"
2. ✅ "What is the impact?"
3. ✅ "Which materials are most affected?"
4. ✅ "What's the impact on suppliers?"
5. ✅ "Which supplier has the most changes?"
6. ✅ "What's the consequence of changes?"

**Expected Answer Pattern**: "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes), Supplier C (Z changes). Top materials affected: MAT001 (X changes), MAT002 (Y changes), MAT003 (Z changes)."

---

## General Questions (Fallback)

These should return generic planning health summary.

1. ✅ "Hello"
2. ✅ "What?"
3. ✅ "Tell me something"
4. ✅ "Random question"

**Expected Answer Pattern**: "Planning health is X/100. Y of Z records have changed. Ask about health, forecast, risks, or changes for more details."

---

## Test Execution Steps

### Step 1: Restart Backend
```bash
cd planning_intelligence
func start
```

### Step 2: Open Copilot Panel
- Open the dashboard in browser
- Click on Copilot panel

### Step 3: Test Each Category

For each category:
1. Ask the first prompt
2. Verify the answer matches the expected pattern
3. Ask the next prompt
4. Repeat for all prompts in category

### Step 4: Document Results

For each prompt, record:
- ✅ PASS - Answer is relevant and specific
- ❌ FAIL - Answer is generic or irrelevant
- ⚠️ PARTIAL - Answer is partially correct

### Step 5: Verify No Regressions

Ensure existing questions still work:
- Health questions return health-specific answers
- Risk questions return risk-specific answers
- Change questions return change-specific answers

---

## Quick Test (5 minutes)

If you only have 5 minutes, test these key prompts:

1. "What's the current planning health status?" → Health answer
2. "What are the top risks?" → Risk answer
3. "How many records have changed?" → Change answer
4. "List suppliers for CYS20_F01C01" → Entity answer (NEW)
5. "Compare CYS20_F01C01 vs DSM18_F01C01" → Comparison answer (NEW)

---

## Medium Test (15 minutes)

Test one prompt from each category:

1. "What's the planning health?" → Health
2. "What's the forecast?" → Forecast
3. "What are the risks?" → Risk
4. "What changes have occurred?" → Change
5. "Which materials are affected?" → Entity (NEW)
6. "Compare CYS20_F01C01 vs DSM18_F01C01" → Comparison (NEW)
7. "Which supplier has the most impact?" → Impact (NEW)

---

## Full Test (30 minutes)

Test all 40+ prompts as listed above.

---

## Troubleshooting

### Issue: Still Getting Generic Answers

**Check**:
1. Backend restarted? `func start`
2. Code changes applied? Check `function_app.py` has new functions
3. Question classification correct? Check logs for "Question type: X"

**Solution**:
1. Restart backend: `func start`
2. Check backend logs for errors
3. Verify question keywords match classification

### Issue: Location ID Not Extracted

**Check**:
1. Location ID format correct? Should be like "CYS20_F01C01"
2. Question includes location ID? "List suppliers for CYS20_F01C01"

**Solution**:
1. Use correct location ID format
2. Include location ID in question

### Issue: Comparison Not Working

**Check**:
1. Two location IDs in question? "Compare X vs Y"
2. Location IDs in correct format?

**Solution**:
1. Include two location IDs
2. Use "vs", "versus", or "compare" keyword

---

## Success Criteria

✅ All entity questions return location-specific or impact-ranked answers
✅ All comparison questions return side-by-side comparisons
✅ All impact questions return ranked suppliers/materials
✅ All existing questions (health, risk, change) still work
✅ No generic fallback answers for specific questions
✅ All answers include supporting metrics

---

## Next Steps After Testing

1. If all tests pass: Deploy to production
2. If some tests fail: Check logs and adjust keywords/logic
3. If new question types needed: Add to classification and handlers
4. Monitor production for user feedback

