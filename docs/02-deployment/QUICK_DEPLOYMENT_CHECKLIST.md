# Quick Deployment Checklist

## The Situation

✓ Code is fixed
✓ Tests pass locally
✗ Azure Function not restarted/redeployed
✗ Old code still running

## What You Need to Do

### Option 1: Quick Restart (Fastest)

- [ ] Go to Azure Portal
- [ ] Find your Function App
- [ ] Click "Restart" button
- [ ] Wait 30-60 seconds
- [ ] Test: "List suppliers for AVC11_F01C01"
- [ ] Should return suppliers (not "No supplier information found")

### Option 2: Redeploy Code (Recommended)

**Using Azure CLI:**
```bash
cd planning_intelligence
func azure functionapp publish <your-function-app-name>
```

**Using VS Code:**
- [ ] Open VS Code
- [ ] Open Azure extension
- [ ] Find your Function App
- [ ] Right-click → "Deploy to Function App"
- [ ] Wait for deployment to complete
- [ ] Test: "List suppliers for AVC11_F01C01"

## Verification

After restart/redeploy:

- [ ] Check logs for DEBUG messages
- [ ] Test supplier query: "List suppliers for AVC11_F01C01"
- [ ] Verify response includes suppliers (not "No supplier information found")
- [ ] Test comparison query: "Compare LOC001 vs LOC002"
- [ ] Test record detail query: "What changed for MAT-001?"
- [ ] Test root cause query: "Why is AVC11_F01C01 risky?"
- [ ] Test traceability query: "Show top contributing records"

## Expected Results

### Before Deployment
```
Query: "List suppliers for AVC11_F01C01"
Response: "No supplier information found for location AVC11_F01C01"
```

### After Deployment
```
Query: "List suppliers for AVC11_F01C01"
Response: 
📊 Suppliers at AVC11_F01C01:

Supplier             Records    Changed    Forecast     Design     Avail  ROJ    Risk
────────────────────────────────────────────────────────────────────────────────
SUP-A                15         8          +450         8 (53%)    2      3      High
SUP-B                12         5          +300         5 (42%)    1      2      Medium
```

## Troubleshooting

### Still Getting "No supplier information found"?

1. [ ] Verify deployment completed
2. [ ] Check Azure Portal → Deployment Center
3. [ ] Look at logs for DEBUG messages
4. [ ] If no DEBUG messages, old code is still running
5. [ ] Try force restart:
   - Stop Function App
   - Wait 10 seconds
   - Start Function App
   - Wait 30 seconds
   - Test again

### Getting different error?

1. [ ] Check error message
2. [ ] Look at logs for exception
3. [ ] Run diagnostic: `python3 planning_intelligence/diagnose_data.py`
4. [ ] Run tests: `python3 -m pytest planning_intelligence/tests/ -v`

## Files Changed

| File | Change |
|------|--------|
| response_builder.py | Line 148: Use `compared` instead of `changed` |
| dashboard_builder.py | Line 139: Use `compared` instead of `changed` |
| function_app.py | Added normalization and logging |

## Success Criteria

✓ Supplier queries return suppliers
✓ All query types work
✓ No "No supplier information found" errors
✓ Response time < 500ms
✓ No errors in logs

## Support

- **Deployment help?** See DEPLOYMENT_VERIFICATION_GUIDE.md
- **Data flow?** See UNDERSTANDING_THE_DATA_FLOW.md
- **Full details?** See CURRENT_STATUS_AND_NEXT_STEPS.md
- **Root cause?** See REAL_ISSUE_FOUND_AND_FIXED.md

---

**Next Action**: Restart or redeploy the Azure Function, then test the supplier query.
