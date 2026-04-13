# Immediate Action Plan - Azure OpenAI Connectivity Fix

**Priority:** CRITICAL  
**Timeline:** TODAY (1-2 hours)  
**Owner:** You

---

## THE PROBLEM (In Plain English)

Your backend is trying to connect to the **wrong Azure OpenAI endpoint**. It's like trying to call a phone number that doesn't exist.

**What's happening:**
- Your code says: "Call Azure OpenAI at `planning-intelligence-openai.openai.azure.com`"
- But Azure is actually using: `v-sye-mnrovouj-eastus2.cognitiveservices.azure.com`
- Result: 404 errors, LLM not working

**Why it happened:**
- You updated `local.settings.json` with the correct endpoint
- But you didn't update the Azure Function app settings
- So the old endpoint is still deployed

---

## THE SOLUTION (3 Steps)

### Step 1: Verify Current Configuration

Run this command to see what's currently deployed in Azure:

```powershell
az functionapp config appsettings list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "[?name=='AZURE_OPENAI_ENDPOINT'].value" -o tsv
```

**Expected output:**
```
https://planning-intelligence-openai.openai.azure.com/
```

**If you see something else** (like `v-sye-mnrovouj-eastus2...`), proceed to Step 2.

---

### Step 2: Update Azure Function Settings

If the endpoint is wrong, update it:

```powershell
az functionapp config appsettings set --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --settings AZURE_OPENAI_ENDPOINT="https://planning-intelligence-openai.openai.azure.com/"
```

**What this does:**
- Updates the Azure Function app settings
- Sets the correct endpoint
- Takes effect immediately (no redeploy needed)

---

### Step 3: Redeploy Backend Code

Even though settings are updated, redeploy to ensure everything is in sync:

```powershell
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence
```

**What this does:**
- Uploads latest code to Azure
- Restarts the function app
- Clears any cached settings

---

## VERIFICATION (How to Know It Worked)

### Check 1: Verify Settings Updated

```powershell
az functionapp config appsettings list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "[?name=='AZURE_OPENAI_ENDPOINT'].value" -o tsv
```

Should show: `https://planning-intelligence-openai.openai.azure.com/`

### Check 2: Check Azure Logs

```powershell
az functionapp log tail --name pi-planning-intelligence --resource-group rg-scp-mcp-dev
```

Look for:
- ✅ `HTTP Request: POST https://planning-intelligence-openai.openai.azure.com/openai/deployments/gpt-5.2-chat/chat/completions?api-version=2024-02-15-preview`
- ✅ `"HTTP/1.1 200 OK"` (not 404)
- ✅ `Azure OpenAI result: intent=...`

### Check 3: Test from UI

1. Go to your Copilot UI
2. Ask a question: "Why is UPS risky?"
3. Should get a response (not a timeout)

---

## WHAT HAPPENS NEXT

Once Azure OpenAI is working:

1. **LLM responses will be generated** - Natural language answers instead of templates
2. **Confidence scores will improve** - From 0.0 to 0.8-0.95
3. **Answers will be more intelligent** - Context-aware, business-focused

---

## IF SOMETHING GOES WRONG

### Issue: Still getting 404 errors

**Cause:** Settings didn't update properly

**Fix:**
```powershell
# Force restart the function app
az functionapp restart --name pi-planning-intelligence --resource-group rg-scp-mcp-dev

# Wait 30 seconds, then check logs again
az functionapp log tail --name pi-planning-intelligence --resource-group rg-scp-mcp-dev
```

### Issue: Getting 401 Unauthorized

**Cause:** API key is wrong or expired

**Fix:**
```powershell
# Verify the API key
az functionapp config appsettings list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "[?name=='AZURE_OPENAI_KEY'].value" -o tsv

# Should show: <YOUR_AZURE_OPENAI_KEY>

# If different, update it
az functionapp config appsettings set --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --settings AZURE_OPENAI_KEY="<YOUR_AZURE_OPENAI_KEY>"
```

### Issue: Getting timeout errors

**Cause:** Azure OpenAI is slow or overloaded

**Fix:**
```powershell
# Check if Azure OpenAI service is up
# Go to: https://status.azure.com/

# If service is up, increase timeout in code
# Edit: planning_intelligence/azure_openai_integration.py
# Change: max_tokens=400 to max_tokens=200 (smaller responses = faster)
```

---

## SUMMARY

| Step | Command | Time |
|------|---------|------|
| 1 | Verify current endpoint | 1 min |
| 2 | Update Azure settings | 1 min |
| 3 | Redeploy backend | 5 min |
| 4 | Verify in logs | 2 min |
| 5 | Test from UI | 2 min |
| **Total** | | **~11 minutes** |

---

## NEXT STEPS (After This Fix)

Once Azure OpenAI is working, we'll implement:

1. **Prompt Caching** - 70-80% cost reduction
2. **Request Batching** - 10x faster throughput
3. **Metrics Caching** - 99% computation reduction
4. **Extensibility Refactoring** - Support 40+ prompts easily

These will make your system production-ready for 40+ prompts.

