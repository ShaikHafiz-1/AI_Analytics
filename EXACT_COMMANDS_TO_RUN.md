# Exact Commands to Run - Copy & Paste

## Step 1: Stop the Function

In the terminal where `func start` is running:
```
Press Ctrl+C
```

---

## Step 2: Verify Code Changes

### Windows PowerShell:
```powershell
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
Select-String -Path response_builder.py -Pattern "detailRecords.*compared"
Select-String -Path dashboard_builder.py -Pattern "detailRecords.*compared"
```

### Windows CMD:
```cmd
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
findstr "detailRecords.*compared" response_builder.py
findstr "detailRecords.*compared" dashboard_builder.py
```

### Git Bash / Linux:
```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
grep "detailRecords.*compared" response_builder.py
grep "detailRecords.*compared" dashboard_builder.py
```

**Expected Output:**
```
"detailRecords": [_slim_record(r) for r in compared],
```

---

## Step 3: Clear Python Cache

### Windows PowerShell:
```powershell
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mcp/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force tests/__pycache__ -ErrorAction SilentlyContinue
```

### Windows CMD:
```cmd
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
rmdir /s /q __pycache__
rmdir /s /q mcp\__pycache__
rmdir /s /q tests\__pycache__
```

### Git Bash / Linux:
```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
rm -r __pycache__
rm -r mcp/__pycache__
rm -r tests/__pycache__
```

---

## Step 4: Restart the Function

### Windows PowerShell:
```powershell
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
func start
```

### Windows CMD:
```cmd
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
func start
```

### Git Bash / Linux:
```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
func start
```

**Wait for output:**
```
Listening on 'http://localhost:7071'
```

---

## Step 5: Test the Query

Open the UI and test:
```
Query: "List suppliers for AVC11_F01C01"
```

**Expected Result:**
```
📊 Suppliers at AVC11_F01C01:

Supplier             Records    Changed    Forecast     Design     Avail  ROJ    Risk
────────────────────────────────────────────────────────────────────────────────
SUP-A                15         8          +450         8 (53%)    2      3      High
SUP-B                12         5          +300         5 (42%)    1      2      Medium
```

---

## Troubleshooting Commands

### Check for Syntax Errors

```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
python3 -m py_compile response_builder.py
python3 -m py_compile dashboard_builder.py
python3 -m py_compile function_app.py
```

No output = OK

### Run Diagnostics

```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
python3 diagnose_data.py
```

### Run Tests

```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
python3 -m pytest tests/ -v
```

### Test Locally (Without UI)

```bash
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
python3 verify_fix_locally.py
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Stop function | Ctrl+C |
| Verify changes | `grep "detailRecords.*compared" response_builder.py` |
| Clear cache | `rm -r __pycache__ mcp/__pycache__ tests/__pycache__` |
| Restart function | `func start` |
| Check syntax | `python3 -m py_compile response_builder.py` |
| Run diagnostics | `python3 diagnose_data.py` |
| Run tests | `python3 -m pytest tests/ -v` |
| Test locally | `python3 verify_fix_locally.py` |

---

## Complete Workflow (Copy & Paste)

### Windows PowerShell:
```powershell
# Stop function (Ctrl+C in the terminal)

# Verify changes
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
Select-String -Path response_builder.py -Pattern "detailRecords.*compared"
Select-String -Path dashboard_builder.py -Pattern "detailRecords.*compared"

# Clear cache
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force mcp/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force tests/__pycache__ -ErrorAction SilentlyContinue

# Restart function
func start

# Wait for "Listening on 'http://localhost:7071'"
# Then test in UI: "List suppliers for AVC11_F01C01"
```

### Git Bash:
```bash
# Stop function (Ctrl+C in the terminal)

# Verify changes
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence
grep "detailRecords.*compared" response_builder.py
grep "detailRecords.*compared" dashboard_builder.py

# Clear cache
rm -r __pycache__ mcp/__pycache__ tests/__pycache__

# Restart function
func start

# Wait for "Listening on 'http://localhost:7071'"
# Then test in UI: "List suppliers for AVC11_F01C01"
```

---

## Expected Timeline

- Stop function: 30 seconds
- Verify changes: 1 minute
- Clear cache: 30 seconds
- Restart function: 1 minute
- Test query: 1 minute

**Total: ~5 minutes**

---

## Success Indicators

After running these commands:

✓ Supplier query returns suppliers (not "No supplier information found")
✓ DEBUG logs show detailRecords count > 0
✓ Response includes supplier table with metrics
✓ All query types work correctly

---

## If Something Goes Wrong

1. **Check syntax**: `python3 -m py_compile response_builder.py`
2. **Run diagnostics**: `python3 diagnose_data.py`
3. **Run tests**: `python3 -m pytest tests/ -v`
4. **Check logs**: Look at the output from `func start`

---

**Ready? Start with Step 1: Stop the function (Ctrl+C)**
