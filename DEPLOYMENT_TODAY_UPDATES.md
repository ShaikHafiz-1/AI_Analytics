# Deployment Guide - Today's Updates (April 14, 2026)

## Quick Summary

**Frontend**: ✅ NO CHANGES NEEDED - Already deployed
**Backend**: ⚠️ NEEDS REDEPLOYMENT - New LLM integration files

---

## What Changed Today

### New Files Created
1. `planning_intelligence/llm_service.py` - LLM service with ChatGPT integration
2. `planning_intelligence/generative_responses.py` - Updated with LLM support
3. `planning_intelligence/test_llm_integration.py` - Test suite for LLM

### Updated Files
1. `planning_intelligence/generative_responses.py` - Added LLM fallback logic
2. `planning_intelligence/sap_schema.py` - Already exists (no changes)

### Documentation (No deployment needed)
- `CHATGPT_INTEGRATION_PLAN.md`
- `REQUEST_RESPONSE_FLOW_ANALYSIS.md`
- `LLM_SCHEMA_INTEGRATION.md`

---

## Deployment Steps from Organization Laptop

### Step 1: Verify Current Deployment Status

```powershell
# Check if backend is running
$url = "https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2?code=<YOUR_FUNCTION_KEY>"
$response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}" -UseBasicParsing
Write-Host "Backend Status: $($response.StatusCode)"

# Check if frontend is accessible
$frontendUrl = "https://planningdatapi.z5.web.core.windows.net/"
$frontendResponse = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing
Write-Host "Frontend Status: $($frontendResponse.StatusCode)"
```

### Step 2: Prepare Backend for Deployment

```powershell
# Navigate to project directory
cd "D:\a\_work\1\s\AI_Analytics"  # Your project path

# Verify new files exist
Test-Path "planning_intelligence/llm_service.py"
Test-Path "planning_intelligence/test_llm_integration.py"

# Check Python dependencies
pip list | grep openai
# If not installed: pip install openai
```

### Step 3: Test Locally Before Deployment

```powershell
# Run LLM integration tests
cd planning_intelligence
python test_llm_integration.py

# Expected output:
# ✓ LLM Service initialized
# ✓ Mock Response Generation: PASS
# ✓ Template Response Generation: PASS
# ✓ LLM Response Generation (with Fallback): PASS
# ✓ All 46 Prompts (Sample): PASS
```

### Step 4: Deploy Backend to Azure

#### Option A: Using Azure CLI (Recommended)

```powershell
# Login to Azure
az login

# Set subscription
az account set --subscription "ae07c9b8-a459-4d4b-bd97-2ea38db97067"

# Deploy to Function App
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence --build remote

# Expected output:
# Getting site publishing info...
# Creating archive for current directory...
# Uploading 1234 bytes...
# Deployment successful!
```

#### Option B: Using VS Code

1. Open VS Code
2. Install "Azure Functions" extension
3. Right-click on `planning_intelligence` folder
4. Select "Deploy to Function App"
5. Choose `pi-planning-intelligence`
6. Confirm deployment

#### Option C: Using PowerShell Script

```powershell
# Create deployment script
$deployScript = @"
# Build
cd planning_intelligence
pip install -r requirements.txt

# Deploy
func azure functionapp publish pi-planning-intelligence --build remote
"@

# Run deployment
Invoke-Expression $deployScript
```

### Step 5: Verify Deployment

```powershell
# Test backend endpoint
$url = "https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2?code=<YOUR_FUNCTION_KEY>"
$body = @{
    mode = "blob"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri $url `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body `
    -UseBasicParsing

Write-Host "Response Status: $($response.StatusCode)"
Write-Host "Response Body: $($response.Content | ConvertFrom-Json | ConvertTo-Json)"
```

### Step 6: Test Copilot with New LLM Integration

```powershell
# Test explain endpoint (used by copilot)
$explainUrl = "https://pi-planning-intelligence.azurewebsites.net/api/explain?code=<YOUR_FUNCTION_KEY>"
$explainBody = @{
    question = "What's the planning health?"
    context = @{
        detailRecords = @()
    }
} | ConvertTo-Json

$explainResponse = Invoke-WebRequest -Uri $explainUrl `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $explainBody `
    -UseBasicParsing

Write-Host "Explain Response: $($explainResponse.Content | ConvertFrom-Json | ConvertTo-Json)"
```

---

## Files to Deploy

### Backend Files (Copy to Azure)

```
planning_intelligence/
├── llm_service.py                    ← NEW
├── generative_responses.py           ← UPDATED
├── test_llm_integration.py           ← NEW
├── function_app.py                   (no changes)
├── sap_schema.py                     (no changes)
├── scoped_metrics.py                 (no changes)
├── phase1_core_functions.py          (no changes)
├── phase2_answer_templates.py        (no changes)
├── phase3_integration.py             (no changes)
└── requirements.txt                  (check if openai needed)
```

### Frontend Files

```
frontend/
├── src/
│   ├── pages/DashboardPage.tsx       (no changes)
│   ├── services/api.ts               (no changes)
│   └── components/CopilotPanel.tsx   (no changes)
└── build/                            (already deployed)
```

**✅ NO FRONTEND REDEPLOYMENT NEEDED**

---

## Deployment Checklist

- [ ] Verify backend is currently running
- [ ] Verify frontend is currently accessible
- [ ] Check new files exist locally
- [ ] Run local tests: `python test_llm_integration.py`
- [ ] All tests pass
- [ ] Deploy backend using `func azure functionapp publish`
- [ ] Verify deployment: Check Azure Portal
- [ ] Test explain endpoint
- [ ] Test copilot in dashboard
- [ ] Verify responses are working

---

## Testing After Deployment

### Test 1: Backend Health

```powershell
$url = "https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2?code=<KEY>"
$response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}" -UseBasicParsing
Write-Host "Status: $($response.StatusCode)"
```

### Test 2: Copilot Endpoint

```powershell
$url = "https://pi-planning-intelligence.azurewebsites.net/api/explain?code=<KEY>"
$body = @{
    question = "What's the planning health?"
    context = @{ detailRecords = @() }
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Content-Type"="application/json"} -Body $body -UseBasicParsing
$result = $response.Content | ConvertFrom-Json
Write-Host "Answer: $($result.answer)"
```

### Test 3: Dashboard Copilot

1. Open: `https://planningdatapi.z5.web.core.windows.net/`
2. Click "Ask Copilot" button
3. Type: "What's the planning health?"
4. Verify response appears

---

## Troubleshooting

### Issue: Deployment Fails

**Solution:**
```powershell
# Check logs
func azure functionapp logstream pi-planning-intelligence

# Redeploy with verbose output
func azure functionapp publish pi-planning-intelligence --build remote --verbose
```

### Issue: LLM Service Not Found

**Solution:**
```powershell
# Verify file was deployed
az functionapp deployment source show --resource-group rg-scp-mcp-dev --name pi-planning-intelligence

# Check if llm_service.py exists in deployment
# If not, redeploy
```

### Issue: Copilot Returns Error

**Solution:**
```powershell
# Check if schema is loaded
# Test with mock responses first (no API key needed)

# Verify in Azure Portal:
# 1. Go to Function App
# 2. Check Application Insights logs
# 3. Look for "LLM Service initialized"
```

### Issue: Timeout on Copilot

**Solution:**
- LLM service starts with mock mode (no API key)
- Responses should be instant
- If timeout, check Azure Function logs

---

## Environment Variables (No Changes Needed Yet)

Current settings in Azure Function App:

```
OPENAI_API_KEY=<NOT SET YET>
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
```

**Note**: LLM service works without API key (uses mock responses)
When you get API key, add to Azure Portal:
1. Go to Function App → Configuration
2. Add new Application Setting: `OPENAI_API_KEY`
3. Value: `sk-...`
4. Save and restart function app

---

## Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Verify current deployment | 2 min | ✓ |
| Run local tests | 3 min | ✓ |
| Deploy backend | 5 min | ⏳ |
| Verify deployment | 2 min | ⏳ |
| Test copilot | 3 min | ⏳ |
| **Total** | **~15 min** | |

---

## What's New in This Deployment

### LLM Service (`llm_service.py`)
- ChatGPT integration ready
- Mock responses for testing (no API key needed)
- SAP schema integration for data interpretation
- Automatic fallback to templates if LLM fails
- Error handling and logging

### Updated Response Builder (`generative_responses.py`)
- LLM-first approach with template fallback
- Each response type tries LLM first
- Falls back to templates on error
- Maintains backward compatibility

### Test Suite (`test_llm_integration.py`)
- Tests LLM initialization
- Tests mock responses
- Tests template responses
- Tests all 46 prompts
- Tests error handling

---

## Next Steps After Deployment

1. **Get OpenAI API Key**
   - Visit: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy key

2. **Add API Key to Azure**
   - Azure Portal → Function App → Configuration
   - Add `OPENAI_API_KEY` setting
   - Paste key value
   - Save and restart

3. **Test with Real ChatGPT**
   - Open dashboard copilot
   - Ask a question
   - Verify ChatGPT response (not mock)

4. **Monitor Costs**
   - Track API usage in OpenAI dashboard
   - Monitor response times
   - Adjust model if needed (gpt-3.5-turbo vs gpt-4)

---

## Rollback Plan (If Needed)

If deployment causes issues:

```powershell
# Revert to previous version
az functionapp deployment slot swap --resource-group rg-scp-mcp-dev --name pi-planning-intelligence --slot staging

# Or redeploy previous version
git checkout HEAD~1 planning_intelligence/
func azure functionapp publish pi-planning-intelligence --build remote
```

---

## Support

If you encounter issues:

1. Check Azure Portal logs
2. Review `LLM_SCHEMA_INTEGRATION.md`
3. Review `REQUEST_RESPONSE_FLOW_ANALYSIS.md`
4. Run local tests to isolate issue
5. Check function app configuration

---

## Summary

✅ **Frontend**: No changes, no redeployment needed
⚠️ **Backend**: Deploy 3 new/updated files
⏱️ **Time**: ~15 minutes total
🎯 **Result**: LLM integration ready (mock mode active, real ChatGPT ready when API key added)
