# Fix Prompts Not Working - Quick Action Guide

## 🎯 The Problem
Some prompts are not working on your organization laptop.

## ✅ The Solution
The data snapshot file is missing. Generate it with one command:

```bash
cd planning_intelligence
python run_daily_refresh.py
```

That's it! This will:
1. Load data from Blob Storage
2. Create `planning_snapshot.json` (the missing file)
3. Enable all 44 prompts to work

---

## 📋 Complete Steps (5 minutes)

### Terminal 1: Start Backend
```bash
cd planning_intelligence
func start
```

### Terminal 2: Generate Data Snapshot
```bash
cd planning_intelligence
python run_daily_refresh.py
```

Expected output:
```
✅ Data loaded successfully
✅ Snapshot created: planning_snapshot.json
```

### Terminal 3: Run Tests
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

Expected output:
```
Total prompts: 44
Passed: 44
Failed: 0
Pass rate: 100.0%
```

---

## ✨ That's All!

After running these commands:
- ✅ All 44 prompts will work
- ✅ Responses will be complete
- ✅ No more "No supplier information found" errors

---

## 🔍 Why This Happened

The `planning_snapshot.json` file:
- Is generated locally (not in git)
- Gets created when you run `python run_daily_refresh.py`
- Was missing when you moved the build to your organization laptop

**Solution**: Always run `python run_daily_refresh.py` after moving/cloning the build.

---

## 📞 If It Still Doesn't Work

1. Verify file was created:
   ```bash
   ls -la planning_intelligence/planning_snapshot.json
   ```

2. Check backend is running (Terminal 1 should show no errors)

3. Run tests again:
   ```bash
   python test_all_44_prompts_CORRECTED.py
   ```

---

**Status**: ✅ Ready to Fix
**Time to Fix**: ~5 minutes
**Expected Result**: 44/44 prompts working
