# Azure Deployment: Step-by-Step Guide

## Current Status
✅ Files copied to org laptop  
✅ Backend running locally (`func start`)  
✅ Frontend running locally (`npm start`)  
✅ Blob data loading successfully  

**Next**: Deploy to Azure Functions and Azure App Service

---

## PART 1: DEPLOY BACKEND TO AZURE FUNCTIONS

### Step 1: Login to Azure
```powershell
az login
```

This opens a browser. Sign in with your org account.

**Verify login**:
```powershell
az account show
```

Should show your subscription details.

---

### Step 2: Create Azure Resources (if not already created)

#### Option A: Using Azure Portal (Recommended for first time)
1. Go to https://portal.azure.com
2. Create Resource Group: `rg-planning-intelligence`
3. Create Storage Account: `stplanningintel` (for blob data)
4. Create Function App: `pi-planning-intelligence` (Python 3.9+)
5. Create App Service Plan: `asp-planning-intelligence` (Standard tier)

#### Option B: Using Azure CLI
```powershell
# Set variables
$resourceGroup = "rg-planning-intelligence"
$location = "eastus"
$storageAccount = "stplanningintel"
$functionApp = "pi-planning-intelligence"
$appServicePlan = "asp-planning-intelligence"

# Create resource group
az group create --name $resourceGroup --location $location

# Create storage account
az storage account create --name $storageAccount --resource-group $resourceGroup --location $location --sku Standard_LRS

# Create app service plan
az appservice plan create --name $appServicePlan --resource-group $resourceGroup --sku B1 --is-linux

# Create function app
az functionapp create --resource-group $resourceGroup --consumption-plan-location $location --runtime python --runtime-version 3.9 --functions-version 4 --name $functionApp --storage-account $storageAccount
```

---

### Step 3: Configure Function App Settings

Set environment variables in Azure:

```powershell
$functionApp = "pi-planning-intelligence"
$resourceGroup = "rg-planning-intelligence"

# Set blob storage connection string
az functionapp config appsettings set \
  --name $functionApp \
  --resource-group $resourceGroup \
  --settings \
    BLOB_CONNECTION_STRING="<YOUR_BLOB_CONNECTION_STRING>" \
    BLOB_CONTAINER_NAME="planning-data" \
    BLOB_CURRENT_FILE="current.csv" \
    BLOB_PREVIOUS_FILE="previous.csv"

# Set Azure OpenAI settings (if using LLM)
az functionapp config appsettings set \
  --name $functionApp \
  --resource-group $resourceGroup \
  --settings \
    AZURE_OPENAI_KEY="<YOUR_AZURE_OPENAI_KEY>" \
    AZURE_OPENAI_ENDPOINT="<YOUR_AZURE_OPENAI_ENDPOINT>" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-5.2-chat" \
    AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Set CORS for frontend
az functionapp config appsettings set \
  --name $functionApp \
  --resource-group $resourceGroup \
  --settings \
    CORS_ORIGIN="https://<your-frontend-url>"
```

**Get your blob connection string**:
```powershell
az storage account show-connection-string --name stplanningintel --resource-group rg-planning-intelligence
```

---

### Step 4: Deploy Backend Code

From your org laptop, in the `planning_intelligence` folder:

```powershell
# Navigate to backend
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence

# Deploy to Azure Functions
func azure functionapp publish pi-planning-intelligence
```

**Expected output**:
```
Getting site publishing info...
Creating archive for current directory...
Uploading 1.23 MB [#####################] 100%
Upload completed successfully.
Deployment completed successfully.
Syncing triggers...
Functions in pi-planning-intelligence:
    planning_intelligence_nlp - [POST,OPTIONS]
    planning-dashboard-v2 - [POST,OPTIONS]
    daily-refresh - [POST,OPTIONS]
    explain - [POST,OPTIONS]
    debug-snapshot - [POST,OPTIONS]
```

**Verify deployment**:
```powershell
# Get function app URL
az functionapp show --name pi-planning-intelligence --resource-group rg-planning-intelligence --query defaultHostName
```

Should return: `pi-planning-intelligence.azurewebsites.net`

---

### Step 5: Test Backend Deployment

Test the dashboard endpoint:

```powershell
$functionApp = "pi-planning-intelligence"
$functionKey = "<YOUR_FUNCTION_KEY>"  # Get from Azure Portal

# Test dashboard endpoint
curl -X POST "https://$functionApp.azurewebsites.net/api/planning-dashboard-v2?code=$functionKey" `
  -H "Content-Type: application/json" `
  -d '{}'
```

**Expected response**:
```json
{
  "planningHealth": 37,
  "changedRecordCount": 2951,
  "totalRecords": 13148,
  "status": "Critical",
  "dataMode": "blob",
  ...
}
```

---

## PART 2: DEPLOY FRONTEND TO AZURE APP SERVICE

### Step 1: Build Frontend

From your org laptop, in the `frontend` folder:

```powershell
# Navigate to frontend
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend

# Build for production
npm run build
```

**Expected output**:
```
> react-scripts build

Creating an optimized production build...
Compiled successfully.

Build folder ready to be deployed.
Size of build folder: 2.3 MB
```

This creates a `build/` folder with all production files.

---

### Step 2: Create App Service (if not already created)

```powershell
$resourceGroup = "rg-planning-intelligence"
$appServicePlan = "asp-planning-intelligence"
$appService = "pi-planning-copilot"
$location = "eastus"

# Create app service
az appservice create \
  --name $appService \
  --resource-group $resourceGroup \
  --plan $appServicePlan
```

---

### Step 3: Deploy Frontend Build

#### Option A: Using Azure CLI (Recommended)

```powershell
$resourceGroup = "rg-planning-intelligence"
$appService = "pi-planning-copilot"

# Deploy build folder
az webapp deployment source config-zip \
  --resource-group $resourceGroup \
  --name $appService \
  --src "build.zip"
```

First, create a zip file:
```powershell
# Navigate to frontend folder
cd frontend

# Create zip of build folder
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# Deploy
az webapp deployment source config-zip \
  --resource-group rg-planning-intelligence \
  --name pi-planning-copilot \
  --src "build.zip"
```

#### Option B: Using Git Deployment

```powershell
# Configure git deployment
az webapp deployment source config-local-git \
  --name pi-planning-copilot \
  --resource-group rg-planning-intelligence

# Add remote
git remote add azure <deployment-url>

# Deploy
git push azure main
```

---

### Step 4: Configure Frontend Environment

Set the backend API URL in App Service:

```powershell
$resourceGroup = "rg-planning-intelligence"
$appService = "pi-planning-copilot"
$functionAppUrl = "https://pi-planning-intelligence.azurewebsites.net/api"

# Set app settings
az webapp config appsettings set \
  --name $appService \
  --resource-group $resourceGroup \
  --settings \
    REACT_APP_API_URL="$functionAppUrl" \
    REACT_APP_API_KEY="<YOUR_FUNCTION_KEY>"
```

---

### Step 5: Test Frontend Deployment

Get the frontend URL:

```powershell
az webapp show --name pi-planning-copilot --resource-group rg-planning-intelligence --query defaultHostName
```

Should return: `pi-planning-copilot.azurewebsites.net`

Open in browser: `https://pi-planning-copilot.azurewebsites.net`

**Expected**:
- Dashboard loads with real data (13,148 records)
- Planning health shows 37/100
- Copilot panel works
- Can ask questions

---

## PART 3: CONFIGURE DAILY REFRESH

### Option A: Using Azure Timer Trigger

Edit `planning_intelligence/function_app.py` and add:

```python
@app.schedule(schedule="0 0 6 * * *")  # 6 AM daily
def daily_refresh_timer(timer: func.TimerRequest):
    """Daily refresh from blob storage."""
    logging.info("Daily refresh timer triggered")
    try:
        from run_daily_refresh import run_daily_refresh
        result = run_daily_refresh()
        logging.info(f"Daily refresh completed: {result}")
    except Exception as e:
        logging.error(f"Daily refresh failed: {str(e)}")
```

Redeploy:
```powershell
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence
```

### Option B: Using Azure Logic App

1. Go to Azure Portal
2. Create Logic App
3. Set trigger: Recurrence (Daily at 6 AM)
4. Set action: HTTP POST to `https://pi-planning-intelligence.azurewebsites.net/api/daily-refresh?code=<KEY>`

---

## PART 4: VERIFICATION CHECKLIST

### Backend Verification
```powershell
# Check function app is running
az functionapp show --name pi-planning-intelligence --resource-group rg-planning-intelligence

# Check app settings
az functionapp config appsettings list --name pi-planning-intelligence --resource-group rg-planning-intelligence

# Check logs
az webapp log tail --name pi-planning-intelligence --resource-group rg-planning-intelligence
```

### Frontend Verification
```powershell
# Check app service is running
az webapp show --name pi-planning-copilot --resource-group rg-planning-intelligence

# Check app settings
az webapp config appsettings list --name pi-planning-copilot --resource-group rg-planning-intelligence

# Check logs
az webapp log tail --name pi-planning-copilot --resource-group rg-planning-intelligence
```

### End-to-End Test
1. Open `https://pi-planning-copilot.azurewebsites.net`
2. Dashboard should load with data
3. Click "Ask Copilot"
4. Ask: "How is planning health?"
5. Should get response: "Planning health is 37/100 (Critical)..."

---

## PART 5: TROUBLESHOOTING

### Backend Issues

#### Error: "Blob connection failed"
```powershell
# Verify blob connection string
az functionapp config appsettings list --name pi-planning-intelligence --resource-group rg-planning-intelligence --query "[?name=='BLOB_CONNECTION_STRING']"

# Verify blob storage account is accessible
az storage account show --name stplanningintel --resource-group rg-planning-intelligence
```

#### Error: "Function not found"
```powershell
# Check deployed functions
az functionapp function list --name pi-planning-intelligence --resource-group rg-planning-intelligence

# Redeploy
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence --force
```

#### Error: "CORS error"
```powershell
# Set CORS
az functionapp cors add --name pi-planning-intelligence --resource-group rg-planning-intelligence --allowed-origins "*"
```

### Frontend Issues

#### Error: "Cannot reach backend"
```powershell
# Verify API URL in app settings
az webapp config appsettings list --name pi-planning-copilot --resource-group rg-planning-intelligence --query "[?name=='REACT_APP_API_URL']"

# Should be: https://pi-planning-intelligence.azurewebsites.net/api
```

#### Error: "Blank page"
```powershell
# Check logs
az webapp log tail --name pi-planning-copilot --resource-group rg-planning-intelligence

# Redeploy
cd frontend
npm run build
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deployment source config-zip --resource-group rg-planning-intelligence --name pi-planning-copilot --src "build.zip"
```

---

## PART 6: MONITORING & MAINTENANCE

### Monitor Backend
```powershell
# View logs
az webapp log tail --name pi-planning-intelligence --resource-group rg-planning-intelligence

# View metrics
az monitor metrics list --resource /subscriptions/<subscription-id>/resourceGroups/rg-planning-intelligence/providers/Microsoft.Web/sites/pi-planning-intelligence
```

### Monitor Frontend
```powershell
# View logs
az webapp log tail --name pi-planning-copilot --resource-group rg-planning-intelligence

# View metrics
az monitor metrics list --resource /subscriptions/<subscription-id>/resourceGroups/rg-planning-intelligence/providers/Microsoft.Web/sites/pi-planning-copilot
```

### Update Code
```powershell
# Backend
cd planning_intelligence
# Make changes
func azure functionapp publish pi-planning-intelligence

# Frontend
cd frontend
# Make changes
npm run build
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deployment source config-zip --resource-group rg-planning-intelligence --name pi-planning-copilot --src "build.zip"
```

---

## PART 7: COST OPTIMIZATION

### Reduce Costs
1. **Function App**: Use Consumption plan (pay per execution)
2. **App Service**: Use B1 tier for frontend (~$10/month)
3. **Storage**: Use Standard LRS for blob storage (~$20/month)
4. **Total**: ~$30-50/month

### Monitor Costs
```powershell
# Get cost estimate
az costmanagement query --timeframe MonthToDate --type "Usage" --dataset granularity=daily
```

---

## QUICK REFERENCE

### Deployment Commands
```powershell
# Backend
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence

# Frontend
cd frontend
npm run build
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deployment source config-zip --resource-group rg-planning-intelligence --name pi-planning-copilot --src "build.zip"
```

### URLs
- **Backend**: `https://pi-planning-intelligence.azurewebsites.net/api`
- **Frontend**: `https://pi-planning-copilot.azurewebsites.net`
- **Portal**: `https://portal.azure.com`

### Resource Names
- **Resource Group**: `rg-planning-intelligence`
- **Function App**: `pi-planning-intelligence`
- **App Service**: `pi-planning-copilot`
- **Storage Account**: `stplanningintel`

---

## NEXT STEPS

1. ✅ Deploy backend: `func azure functionapp publish pi-planning-intelligence`
2. ✅ Deploy frontend: Build and upload to App Service
3. ✅ Configure settings: Set environment variables
4. ✅ Test end-to-end: Open frontend URL and test
5. ✅ Monitor: Check logs and metrics
6. ✅ Optimize: Reduce costs and improve performance

---

## Support

For issues:
1. Check Azure Portal logs
2. Run `az webapp log tail` for frontend
3. Run `az functionapp log tail` for backend
4. Check `REACT_APP_API_URL` in frontend settings
5. Check `BLOB_CONNECTION_STRING` in backend settings

