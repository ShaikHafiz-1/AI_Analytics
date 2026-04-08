# UI Copilot Fix - Action Plan

## Current Status
- ✅ Backend API: 100% pass rate (44/44 prompts)
- ❌ UI Copilot: Failing with "No supplier information found"
- **Diagnosis**: Backend works, frontend context passing is broken

---

## Root Cause

The frontend is not properly passing the dashboard context (including `detailRecords`) to the Copilot API.

**What should happen:**
1. Dashboard loads data from backend
2. `buildDashboardContext()` extracts `detailRecords` from response
3. User asks Copilot a question
4. `CopilotPanel` sends context to `/api/explain` endpoint
5. Backend uses `detailRecords` to answer the question

**What's actually happening:**
1. Dashboard loads (maybe)
2. Context is built (maybe)
3. User asks Copilot
4. Context is NOT being passed or is empty
5. Backend can't find supplier data

---

## Fix Steps

### Step 1: Verify Backend is Running (5 minutes)

**Terminal 1** - Check backend is running:
```bash
cd planning_intelligence
func start
```

**Expected output:**
```
Http Functions:
  explain: [POST] http://localhost:7071/api/explain
  planning-dashboard-v2: [POST] http://localhost:7071/api/planning-dashboard-v2
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
```

If you see errors, stop and fix them first.

---

### Step 2: Verify Data is Loaded (5 minutes)

**Terminal 2** - Load data:
```bash
cd planning_intelligence
set SNAPSHOT_FILE_PATH=%cd%\planning_snapshot.json
python run_daily_refresh.py
```

**Expected output:**
```
✅ Data loaded successfully
✅ Snapshot saved to ...
```

**Verify file exists:**
```bash
dir planning_snapshot.json
```

Should show file size > 5MB.

---

### Step 3: Verify Tests Pass (5 minutes)

**Terminal 3** - Run tests:
```bash
cd planning_intelligence
python test_all_44_prompts_CORRECTED.py
```

**Expected output:**
```
Pass rate: 100.0%
```

If tests fail, backend is broken. If tests pass, backend is working.

---

### Step 4: Hard Refresh Browser (2 minutes)

1. Open browser to http://localhost:3000
2. Press **Ctrl + Shift + Delete** (Windows) or **Cmd + Shift + Delete** (Mac)
3. Select "All time" and clear cache
4. Close browser completely
5. Reopen browser to http://localhost:3000
6. Wait for dashboard to load

---

### Step 5: Check Browser Console (5 minutes)

1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Look for any red error messages
4. Take a screenshot of any errors
5. Go to **Network** tab
6. Refresh page (F5)
7. Look for requests:
   - `planning-dashboard-v2` - Click it, check "Response" tab
   - Should see `detailRecords` field with data
8. Look for `explain` requests - Check if they include `context` parameter

---

### Step 6: Test Copilot (5 minutes)

1. Wait for dashboard to fully load
2. Click "Ask Copilot" button
3. Try this prompt: **"Which suppliers at CYS20_F01C01 have design changes?"**
4. Check if you get a proper response with supplier list
5. If you get "No supplier information found", the context is not being passed

---

### Step 7: If Still Broken - Add Debug Logging (10 minutes)

**Add logging to frontend** - Edit `frontend/src/components/CopilotPanel.tsx`:

Find the `sendMessage` function (around line 470) and add this at the start:

```typescript
const sendMessage = useCallback(async (question: string) => {
  if (!question.trim() || loading) return;
  
  // ADD THESE LINES:
  console.log("=== COPILOT DEBUG ===");
  console.log("Question:", question);
  console.log("Context exists:", !!context);
  console.log("Context.detailRecords:", context?.detailRecords?.length || 0);
  console.log("Context.planningHealth:", context?.planningHealth);
  console.log("Full context:", context);
  console.log("=== END DEBUG ===");
  
  const userMsg: ChatMessage = { role: "user", content: question.trim(), timestamp: Date.now() };
  // ... rest of function
```

Then:
1. Refresh browser (F5)
2. Open DevTools Console (F12)
3. Ask Copilot a question
4. Check console output
5. Screenshot the debug output
6. Share it with the team

---

### Step 8: If Still Broken - Check Backend Logs (5 minutes)

Look at **Terminal 1** output when you ask Copilot a question.

You should see something like:
```
Explain endpoint triggered.
Context received: True
detailRecords count: 1234
```

If you see:
```
Explain endpoint triggered.
Context received: False
```

Then the frontend is NOT sending context.

---

## Checklist

Before asking Copilot, verify ALL of these:

- [ ] Terminal 1: `func start` is running
- [ ] Terminal 1: Shows "Http Functions" with all endpoints
- [ ] Terminal 1: No error messages
- [ ] Terminal 2: `python run_daily_refresh.py` completed
- [ ] Terminal 2: `planning_snapshot.json` file exists (> 5MB)
- [ ] Terminal 3: Tests show 44/44 passing
- [ ] Browser: Dashboard loads without errors
- [ ] Browser: All cards show data (not skeleton loaders)
- [ ] Browser: Console (F12) shows no red errors
- [ ] Browser: Network tab shows `planning-dashboard-v2` response includes `detailRecords`

---

## Expected Behavior When Fixed

1. Dashboard loads with all metrics
2. "Ask Copilot" button is active
3. Type a prompt and see suggestions
4. Ask: "Which suppliers at CYS20_F01C01 have design changes?"
5. Get response like:
   ```
   📊 Suppliers at CYS20_F01C01:
   • UPS: 5 records, Forecast: +100, Design changes: 2
   • MVSXRM: 3 records, Forecast: +50, Design changes: 1
   • FedEx: 2 records, Forecast: +25, Design changes: 0
   ```
6. No "No supplier information found" errors

---

## If You're Still Stuck

1. **Screenshot the browser console** (F12 → Console tab)
2. **Screenshot the Network tab** showing the API responses
3. **Copy the debug output** from the console
4. **Check Terminal 1 logs** for any error messages
5. **Verify all 3 terminals are running** and showing success messages

Then share these with the team for further debugging.

---

## Quick Summary

**The fix is:**
1. Verify backend is running (Terminal 1)
2. Verify data is loaded (Terminal 2)
3. Verify tests pass (Terminal 3)
4. Hard refresh browser (Ctrl+Shift+Delete)
5. Check browser console for errors (F12)
6. Test Copilot with a supplier query
7. If broken, add debug logging and check what's being sent

**Most likely issue:** Browser cache is stale or data didn't load properly.

**Solution:** Hard refresh browser and restart all terminals.

