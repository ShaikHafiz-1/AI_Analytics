# Copilot Classification Fix Applied

## Problem Identified

The Copilot was returning generic health answers for entity, impact, and comparison questions because:

1. **Entity questions were being misclassified** - Questions like "Which materials are affected?" were matching the "impact" classification (because of the "affected" keyword) instead of "entity"
2. **Classification priority was wrong** - Entity questions need to be checked BEFORE impact questions
3. **Keyword matching was too broad** - The "affected" keyword was matching impact instead of entity context

## Solution Applied

Updated the `classify_question()` function in `planning_intelligence/function_app.py` with improved classification logic:

### Classification Priority (New Order)

1. **Comparison** - "compare", "vs", "versus", "difference", "between"
2. **Entity** - "list", "supplier", "suppliers", "material", "materials", "which" (with entity context)
3. **Impact** - "impact", "most impact", "most affected", "most changed", "consequence"
4. **Design** - "design", "BOD", "form factor", "FF"
5. **Schedule** - "ROJ", "schedule", "date"
6. **Forecast** - "forecast", "trend", "delta", "increase", "decrease", "units", "quantity"
7. **Location** - "location", "locations", "datacenter", "site"
8. **Risk** - "risk", "risks", "risky", "danger", "dangerous", "high-risk"
9. **Health** - "health", "status", "score", "critical", "stable", "planning"
10. **Change** - "change", "changed", "changes"
11. **General** - fallback

### Key Changes

1. **Entity questions checked BEFORE impact** - Prevents "affected" keyword from matching impact
2. **Separate check for "material"** - Catches "Which materials are affected?" as entity, not impact
3. **Context-aware "which" matching** - "which" only matches entity if followed by entity keywords
4. **Risk checked BEFORE health** - Prevents "status" keyword from matching health when it's part of a risk question

## Expected Results After Fix

### Entity Questions

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "List suppliers for CYS20_F01C01" | entity | "Location CYS20_F01C01: X records. Suppliers: A, B, C. Materials: M1, M2. Changed: Y." |
| "Which materials are affected?" | entity | "Top affected materials: MAT001 (X changes), MAT002 (Y changes)..." |
| "Which suppliers at CYS20_F01C01 have design changes?" | entity | "Location CYS20_F01C01: X records. Suppliers: A, B. Materials: M1. Changed: Y." |
| "What suppliers are involved?" | entity | "Top affected suppliers: Supplier A (X changes), Supplier B (Y changes)..." |
| "What materials are involved?" | entity | "Top affected materials: MAT001 (X changes), MAT002 (Y changes)..." |
| "List materials for DSM18_F01C01" | entity | "Location DSM18_F01C01: X records. Suppliers: A, B. Materials: M1, M2. Changed: Y." |
| "Which locations are affected?" | entity | "Top affected locations: LOC1 (X changes), LOC2 (Y changes)..." |
| "What groups are affected?" | entity | "Top affected materials: MAT001 (X changes), MAT002 (Y changes)..." |

### Comparison Questions

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "Compare CYS20_F01C01 vs DSM18_F01C01" | comparison | "Comparison: CYS20_F01C01 vs DSM18_F01C01. CYS20_F01C01: X records, Y changed. DSM18_F01C01: Z records, W changed." |
| "What's the difference between CYS20_F01C01 and DSM18_F01C01?" | comparison | "Comparison: CYS20_F01C01 vs DSM18_F01C01. CYS20_F01C01: X records, Y changed. DSM18_F01C01: Z records, W changed." |

### Impact Questions

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "Which supplier has the most impact?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes)..." |
| "What is the impact?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes)..." |
| "Which materials are most affected?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes)... Top materials affected: MAT001 (X changes)..." |
| "What's the impact on suppliers?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes)..." |
| "Which supplier has the most changes?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes)..." |
| "What's the consequence of changes?" | impact | "Impact analysis: Top suppliers affected: Supplier A (X changes), Supplier B (Y changes)..." |

### Health Questions (Should Still Work)

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "What's the current planning health status?" | health | "Planning health is 37/100 (Critical). 5,927 of 13,148 records have changed (45.1%). Primary drivers: Design changes (1926), Supplier changes (1499)." |
| "What's the planning health?" | health | "Planning health is 37/100 (Critical). 5,927 of 13,148 records have changed (45.1%). Primary drivers: Design changes (1926), Supplier changes (1499)." |

### Risk Questions (Should Still Work)

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "What are the top risks?" | risk | "Risk level is High. Highest risk type: Design + Supplier. 1200 high-risk records out of 13,148 total (9.1%). Breakdown: Design (1926), Supplier (1499), Quantity (4725)." |
| "What are the risks?" | risk | "Risk level is High. Highest risk type: Design + Supplier. 1200 high-risk records out of 13,148 total (9.1%). Breakdown: Design (1926), Supplier (1499), Quantity (4725)." |

### Change Questions (Should Still Work)

| Question | Expected Classification | Expected Answer |
|----------|------------------------|-----------------|
| "How many records have changed?" | change | "5,927 records have changed out of 13,148 total (45.1%). Breakdown: Design (1926), Supplier (1499), Quantity (4725)." |
| "What changes have occurred?" | change | "5,927 records have changed out of 13,148 total (45.1%). Breakdown: Design (1926), Supplier (1499), Quantity (4725)." |

## Files Modified

- `planning_intelligence/function_app.py` - Updated `classify_question()` function with improved classification logic

## Testing

To verify the fix works:

1. **Restart the backend**:
   ```bash
   cd planning_intelligence
   func start
   ```

2. **Test entity questions** in the Copilot panel:
   - "List suppliers for CYS20_F01C01" → Should return location-specific suppliers
   - "Which materials are affected?" → Should return top affected materials
   - "Which suppliers at CYS20_F01C01 have design changes?" → Should return location-specific suppliers

3. **Test comparison questions**:
   - "Compare CYS20_F01C01 vs DSM18_F01C01" → Should return side-by-side comparison

4. **Test impact questions**:
   - "Which supplier has the most impact?" → Should return impact analysis
   - "What is the impact?" → Should return impact analysis

5. **Verify existing questions still work**:
   - "What's the planning health?" → Should return health answer
   - "What are the top risks?" → Should return risk answer
   - "How many records have changed?" → Should return change answer

## Next Steps

1. Restart the backend with the updated code
2. Test all 40+ prompts to verify they return correct answers
3. Monitor logs for any classification errors
4. If any prompts still return wrong answers, check:
   - Question classification (logs show "Question type: X")
   - Answer generator function (logs show "Generated answer: ...")
   - Data availability (logs show "Processing question with N records")

## Troubleshooting

### Issue: Still Getting Generic Health Answers

**Check**:
1. Backend restarted with new code? `func start`
2. Question classification correct? Check logs for "Question type: X"
3. Answer generator called? Check logs for "Generated answer: ..."

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

## Success Criteria

✅ All entity questions return location-specific or impact-ranked answers
✅ All comparison questions return side-by-side comparisons
✅ All impact questions return ranked suppliers/materials
✅ All existing questions (health, risk, change) still work
✅ No generic fallback answers for specific questions
✅ All answers include supporting metrics
