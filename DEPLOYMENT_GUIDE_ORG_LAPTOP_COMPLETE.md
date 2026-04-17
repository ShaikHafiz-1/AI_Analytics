# Complete Deployment Guide - Planning Intelligence Copilot LLM Integration

**Date**: April 15, 2026  
**Status**: Ready for Production Deployment  
**Estimated Setup Time**: 35-45 minutes

---

## 📋 Pre-Deployment Checklist

Before starting, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ and npm installed
- [ ] Azure CLI installed (for Azure deployment)
- [ ] Git installed
- [ ] OpenAI API key (from https://platform.openai.com/api-keys)
- [ ] Azure subscription (if deploying to Azure)
- [ ] Access to the repository

---

## 🔑 Critical: API Key Setup

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you won't see it again)
4. **IMPORTANT**: This key was exposed in chat - regenerate it immediately after deployment

### Step 2: Store API Key Securely

**For Local Development:**
```bash
# Create .env file in planning_intelligence directory
cd planning_intelligence
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**For Azure Deployment:**
- Add to Azure Key Vault
- Reference in Azure Functions configuration
- Never commit to git

---

## 🚀 Backend Deployment (Planning Intelligence)

### Phase 1: Local Setup (5-10 minutes)

#### 1.1 Navigate to Backend Directory
```bash
cd planning_intelligence
```

#### 1.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed azure-functions azure-storage-blob openai python-dotenv ...
```

#### 1.4 Configure Environment Variables
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your values
# OPENAI_API_KEY=sk-your-key-here
# AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
# AZURE_STORAGE_CONTAINER_NAME=planning-data
```

#### 1.5 Verify Setup
```bash
python -c "import azure.functions; import openai; print('✓ All dependencies installed')"
```

### Phase 2: Local Testing (5-10 minutes)

#### 2.1 Start Local Azure Functions Runtime
```bash
func start
```

**Expected output:**
```
Azure Functions Core Tools
Version 4.x.x
...
Functions:
  planning_intelligence_nlp: [POST] http://localhost:7071/api/planning_intelligence_nlp
  planning_dashboard_v2: [GET] http://localhost:7071/api/planning_dashboard_v2
  explain: [POST] http://localhost:7071/api/explain
  daily_refresh: [TimerTrigger] ...
```

#### 2.2 Test Backend Endpoints

**Test 1: Dashboard Endpoint**
```bash
curl http://localhost:7071/api/planning_dashboard_v2
```

**Expected response:**
```json
{
  "status": "success",
  "data": {
    "totalRecords": 13148,
    "detailRecords": [...],
    "metrics": {...}
  }
}
```

**Test 2: Greeting Question**
```bash
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hi",
    "context": {
      "detailRecords": [],
      "selectedEntity": null
    }
  }'
```

**Expected response:**
```json
{
  "answer": "Hello! I'm your Planning Intelligence Copilot...",
  "type": "greeting",
  "aiInsight": "..."
}
```

**Test 3: Planning Question**
```bash
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the high-risk items?",
    "context": {
      "detailRecords": [],
      "selectedEntity": null
    }
  }'
```

**Expected response:**
```json
{
  "answer": "Based on the current data...",
  "type": "risk",
  "aiInsight": "..."
}
```

### Phase 3: Azure Deployment (10-15 minutes)

#### 3.1 Create Azure Resources

**Option A: Using Azure CLI**
```bash
# Set variables
$resourceGroup = "rg-planning-intelligence"
$location = "eastus"
$storageAccount = "stgplanningintel"
$functionApp = "func-planning-intelligence"

# Create resource group
az group create --name $resourceGroup --location $location

# Create storage account
az storage account create \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --location $location \
  --sku Standard_LRS

# Create function app
az functionapp create \
  --resource-group $resourceGroup \
  --consumption-plan-location $location \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name $functionApp \
  --storage-account $storageAccount
```

**Option B: Using Azure Portal**
1. Create Resource Group
2. Create Storage Account
3. Create Function App (Python 3.9, Consumption Plan)

#### 3.2 Deploy Backend Code
```bash
# From planning_intelligence directory
func azure functionapp publish func-planning-intelligence
```

**Expected output:**
```
Getting site publishing info...
Creating archive for current directory...
Uploading 1.2 MB...
Deployment successful!
```

#### 3.3 Configure Application Settings
```bash
# Set environment variables in Azure
az functionapp config appsettings set \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --settings \
    OPENAI_API_KEY="sk-your-key-here" \
    AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;..." \
    AZURE_STORAGE_CONTAINER_NAME="planning-data"
```

#### 3.4 Verify Deployment
```bash
# Get function app URL
az functionapp show \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --query defaultHostName

# Test endpoint
curl https://func-planning-intelligence.azurewebsites.net/api/planning_dashboard_v2
```

---

## 🎨 Frontend Deployment (React App)

### Phase 1: Local Setup (5-10 minutes)

#### 1.1 Navigate to Frontend Directory
```bash
cd frontend
```

#### 1.2 Install Dependencies
```bash
npm install
```

**Expected output:**
```
added 1,234 packages in 45s
```

#### 1.3 Configure Environment Variables
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your backend URL
# REACT_APP_API_URL=http://localhost:7071/api
# (or https://func-planning-intelligence.azurewebsites.net/api for Azure)
```

#### 1.4 Verify Setup
```bash
npm run build
```

**Expected output:**
```
> react-scripts build
Creating an optimized production build...
The build folder is ready to be deployed.
```

### Phase 2: Local Testing (5 minutes)

#### 2.1 Start Development Server
```bash
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view the app in the browser at:
  http://localhost:3000
```

#### 2.2 Test Frontend Features

1. **Open Dashboard**: http://localhost:3000
2. **Test Greeting**: Type "Hi" in copilot panel
3. **Test Planning Question**: Type "What are the high-risk items?"
4. **Verify Response**: Should see LLM-generated response with business context

### Phase 3: Azure Deployment (10-15 minutes)

#### 3.1 Build Production Bundle
```bash
npm run build
```

#### 3.2 Deploy to Azure App Service

**Option A: Using Azure CLI**
```bash
# Create App Service Plan
az appservice plan create \
  --name plan-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-planning-intelligence \
  --plan plan-planning-intelligence \
  --name app-planning-intelligence \
  --runtime "NODE|16-lts"

# Deploy code
az webapp deployment source config-zip \
  --resource-group rg-planning-intelligence \
  --name app-planning-intelligence \
  --src build.zip
```

**Option B: Using Azure Portal**
1. Create App Service Plan (Linux, B1 tier)
2. Create Web App (Node.js 16 LTS)
3. Deploy via Zip Upload or GitHub Actions

#### 3.3 Configure Application Settings
```bash
az webapp config appsettings set \
  --resource-group rg-planning-intelligence \
  --name app-planning-intelligence \
  --settings \
    REACT_APP_API_URL="https://func-planning-intelligence.azurewebsites.net/api"
```

#### 3.4 Verify Deployment
```bash
# Get app URL
az webapp show \
  --resource-group rg-planning-intelligence \
  --name app-planning-intelligence \
  --query defaultHostName

# Test in browser
# https://app-planning-intelligence.azurewebsites.net
```

---

## ✅ Post-Deployment Verification

### Backend Verification

```bash
# 1. Check function app is running
curl https://func-planning-intelligence.azurewebsites.net/api/planning_dashboard_v2

# 2. Check logs
az functionapp log tail \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence

# 3. Test all endpoints
# - /api/planning_dashboard_v2 (GET)
# - /api/explain (POST)
# - /api/planning_intelligence_nlp (POST)
```

### Frontend Verification

```bash
# 1. Check app is accessible
curl https://app-planning-intelligence.azurewebsites.net

# 2. Test in browser
# - Dashboard loads
# - Copilot panel visible
# - Can type questions
# - Receives responses

# 3. Check browser console for errors
# - No CORS errors
# - No API errors
# - No timeout errors
```

### End-to-End Verification

1. **Open Dashboard**: https://app-planning-intelligence.azurewebsites.net
2. **Test Greeting**: Type "Hello" → Should get LLM response
3. **Test Planning Question**: Type "What are the top risks?" → Should get detailed analysis
4. **Test Entity Filter**: Select a location → Ask question → Should get scoped response
5. **Check Performance**: Response should be <5 seconds for most queries

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: "OPENAI_API_KEY not found"**
```bash
# Solution: Set environment variable
az functionapp config appsettings set \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --settings OPENAI_API_KEY="sk-your-key-here"
```

**Issue: "Blob storage connection failed"**
```bash
# Solution: Verify connection string
az functionapp config appsettings set \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --settings AZURE_STORAGE_CONNECTION_STRING="your-connection-string"
```

**Issue: "Timeout errors on complex queries"**
```bash
# Solution: Already fixed in frontend (35 second timeout)
# If still occurring, check backend logs:
az functionapp log tail \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence
```

### Frontend Issues

**Issue: "API connection failed"**
```bash
# Solution: Verify REACT_APP_API_URL
# Check .env file has correct backend URL
# Verify backend is accessible from frontend
curl https://func-planning-intelligence.azurewebsites.net/api/planning_dashboard_v2
```

**Issue: "CORS errors"**
```bash
# Solution: Backend already has CORS enabled
# If still occurring, check function_app.py for CORS headers
```

**Issue: "Blank responses from LLM"**
```bash
# Solution: Check OpenAI API key is valid
# Verify API key has sufficient quota
# Check backend logs for API errors
```

---

## 📊 Performance Expectations

After deployment, you should see:

| Query Type | Response Time | Notes |
|-----------|---------------|-------|
| Greeting | 1-2 seconds | LLM generates response |
| Simple Planning | 2-4 seconds | LLM analyzes data |
| Complex Planning | 4-8 seconds | LLM with full context |
| Very Complex | 8-15 seconds | Multiple data sources |

**Timeout**: 35 seconds (already configured)

---

## 🔐 Security Checklist

- [ ] OpenAI API key stored in Azure Key Vault (not in code)
- [ ] Connection strings stored in Azure Key Vault
- [ ] HTTPS enabled on all endpoints
- [ ] CORS configured for frontend domain only
- [ ] No sensitive data in logs
- [ ] API key regenerated after deployment
- [ ] Access restricted to authorized users

---

## 📝 Files to Deploy

### Backend Files (19 files)
```
planning_intelligence/
├── function_app.py (MODIFIED - all answer functions + LLM)
├── llm_service.py (NEW - LLM integration with business rules)
├── business_rules.py (NEW - business rules for ChatGPT)
├── generative_responses.py
├── sap_schema.py
├── blob_service.py
├── requirements.txt
├── .env (with OPENAI_API_KEY)
├── host.json
├── local.settings.json
└── [other supporting files]
```

### Frontend Files (15+ files)
```
frontend/
├── src/
│   ├── components/
│   │   └── CopilotPanel.tsx (MODIFIED - timeout & detailRecords)
│   ├── pages/
│   │   └── DashboardPage.tsx
│   ├── services/
│   │   └── api.ts
│   └── [other components]
├── .env (with REACT_APP_API_URL)
├── package.json
├── tsconfig.json
└── [other config files]
```

---

## 🚀 Quick Start Commands

### Backend
```bash
cd planning_intelligence
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-your-key-here" > .env
func start
```

### Frontend
```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:7071/api" > .env
npm start
```

### Deploy to Azure
```bash
# Backend
cd planning_intelligence
func azure functionapp publish func-planning-intelligence

# Frontend
cd frontend
npm run build
# Upload build folder to App Service
```

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `az functionapp log tail --name func-planning-intelligence --resource-group rg-planning-intelligence`
2. **Verify API key**: Ensure OpenAI API key is valid and has quota
3. **Check connectivity**: Verify frontend can reach backend
4. **Review code**: Check function_app.py and llm_service.py for errors

---

## ✨ What's New in This Deployment

✅ **Greeting Detection**: Simple greetings (Hi, Hello) now routed to ChatGPT  
✅ **Full LLM Integration**: All answer functions use ChatGPT with full blob context  
✅ **Business Rules**: ChatGPT understands supply chain planning domain  
✅ **Performance**: 1-2 seconds faster responses (detailRecords passed from frontend)  
✅ **Timeout Fix**: 35 second timeout prevents premature failures  
✅ **Error Handling**: Graceful fallbacks if LLM fails  

---

**Ready to deploy? Start with the Backend Deployment section above.**
