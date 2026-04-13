# Deploy to Azure Using rg-scp-mcp-dev

Your resource group: **rg-scp-mcp-dev**

---

## STEP 1: Deploy Backend to Azure Functions

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

---

## STEP 2: Configure Backend Environment Variables

Set the blob connection string and other settings:

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"

# Set blob storage settings
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
    BLOB_CONNECTION_STRING="<YOUR_BLOB_CONNECTION_STRING>" `
    BLOB_CONTAINER_NAME="planning-data" `
    BLOB_CURRENT_FILE="current.csv" `
    BLOB_PREVIOUS_FILE="previous.csv"

# Set Azure OpenAI settings (if using LLM)
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
    AZURE_OPENAI_KEY="<YOUR_AZURE_OPENAI_KEY>" `
    AZURE_OPENAI_ENDPOINT="<YOUR_AZURE_OPENAI_ENDPOINT>" `
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-5.2-chat" `
    AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

**Get your blob connection string**:
```powershell
# Find storage account in your resource group
az storage account list --resource-group rg-scp-mcp-dev --query "[].name" -o tsv

# Get connection string (replace with your storage account name)
az storage account show-connection-string --name <storage-account-name> --resource-group rg-scp-mcp-dev
```

---

## STEP 3: Test Backend Deployment

```powershell
$functionApp = "pi-planning-intelligence"
$resourceGroup = "rg-scp-mcp-dev"

# Get function app URL
$functionUrl = az functionapp show `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

Write-Host "Function App URL: https://$functionUrl/api"

# Get function key
$functionKey = az functionapp keys list `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query "functionKeys.default" `
  -o tsv

Write-Host "Function Key: $functionKey"

# Test dashboard endpoint
$response = Invoke-WebRequest `
  -Uri "https://$functionUrl/api/planning-dashboard-v2?code=$functionKey" `
  -Method POST `
  -ContentType "application/json" `
  -Body "{}"

Write-Host "Response Status: $($response.StatusCode)"
Write-Host "Response Body: $($response.Content | ConvertFrom-Json | ConvertTo-Json)"
```

**Expected response**:
```json
{
  "planningHealth": 37,
  "changedRecordCount": 2951,
  "totalRecords": 13148,
  "status": "Critical",
  "dataMode": "blob"
}
```

---

## STEP 4: Create App Service for Frontend (if not exists)

Check if app service exists:

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Check if app service exists
$appServiceExists = az webapp show `
  --name $appService `
  --resource-group $resourceGroup `
  --query "name" `
  -o tsv 2>$null

if ($appServiceExists) {
  Write-Host "✓ App Service already exists: $appService"
} else {
  Write-Host "Creating App Service..."
  
  # Create app service plan if needed
  $planName = "asp-planning-intelligence"
  $planExists = az appservice plan show `
    --name $planName `
    --resource-group $resourceGroup `
    --query "name" `
    -o tsv 2>$null
  
  if (-not $planExists) {
    Write-Host "Creating App Service Plan..."
    az appservice plan create `
      --name $planName `
      --resource-group $resourceGroup `
      --sku B1 `
      --is-linux
  }
  
  # Create app service
  az webapp create `
    --name $appService `
    --resource-group $resourceGroup `
    --plan $planName
  
  Write-Host "✓ App Service created: $appService"
}
```

---

## STEP 5: Build Frontend

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

---

## STEP 6: Deploy Frontend to App Service

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Create zip of build folder
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend

Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# Deploy using new command (recommended)
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip

Write-Host "✓ Frontend deployed successfully!"
```

---

## STEP 7: Configure Frontend Environment

Set the backend API URL:

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$functionApp = "pi-planning-intelligence"

# Get function app URL
$functionUrl = az functionapp show `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

# Get function key
$functionKey = az functionapp keys list `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query "functionKeys.default" `
  -o tsv

# Set app settings
az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"

Write-Host "✓ Frontend configured with backend URL: https://$functionUrl/api"
```

---

## STEP 8: Test Frontend Deployment

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Get frontend URL
$frontendUrl = az webapp show `
  --name $appService `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

Write-Host "Frontend URL: https://$frontendUrl"
Write-Host ""
Write-Host "Open in browser: https://$frontendUrl"
```

Open the URL in your browser. You should see:
- Dashboard loading with real data (13,148 records)
- Planning health: 37/100
- Changed records: 2,951/13,148
- Copilot panel working

---

## COMPLETE DEPLOYMENT SCRIPT

Save this as `deploy-all.ps1`:

```powershell
# Configuration
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"
$appService = "pi-planning-copilot"
$appServicePlan = "asp-planning-intelligence"
$basePath = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Planning Intelligence Copilot Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Deploy Backend
Write-Host "STEP 1: Deploying Backend..." -ForegroundColor Yellow
cd "$basePath\planning_intelligence"
func azure functionapp publish $functionApp
Write-Host "✓ Backend deployed" -ForegroundColor Green
Write-Host ""

# Step 2: Create App Service if needed
Write-Host "STEP 2: Checking App Service..." -ForegroundColor Yellow
$appServiceExists = az webapp show --name $appService --resource-group $resourceGroup --query "name" -o tsv 2>$null
if (-not $appServiceExists) {
  Write-Host "Creating App Service Plan..."
  az appservice plan create --name $appServicePlan --resource-group $resourceGroup --sku B1 --is-linux
  Write-Host "Creating App Service..."
  az webapp create --name $appService --resource-group $resourceGroup --plan $appServicePlan
}
Write-Host "✓ App Service ready" -ForegroundColor Green
Write-Host ""

# Step 3: Build Frontend
Write-Host "STEP 3: Building Frontend..." -ForegroundColor Yellow
cd "$basePath\frontend"
npm run build
Write-Host "✓ Frontend built" -ForegroundColor Green
Write-Host ""

# Step 4: Deploy Frontend
Write-Host "STEP 4: Deploying Frontend..." -ForegroundColor Yellow
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deploy --resource-group $resourceGroup --name $appService --src-path "build.zip" --type zip
Write-Host "✓ Frontend deployed" -ForegroundColor Green
Write-Host ""

# Step 5: Configure Frontend
Write-Host "STEP 5: Configuring Frontend..." -ForegroundColor Yellow
$functionUrl = az functionapp show --name $functionApp --resource-group $resourceGroup --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name $functionApp --resource-group $resourceGroup --query "functionKeys.default" -o tsv
az webapp config appsettings set --name $appService --resource-group $resourceGroup --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"
Write-Host "✓ Frontend configured" -ForegroundColor Green
Write-Host ""

# Step 6: Get URLs
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
$frontendUrl = az webapp show --name $appService --resource-group $resourceGroup --query defaultHostName -o tsv
Write-Host "Frontend URL: https://$frontendUrl" -ForegroundColor Cyan
Write-Host "Backend URL: https://$functionUrl/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open in browser: https://$frontendUrl" -ForegroundColor Green
```

Run it:
```powershell
.\deploy-all.ps1
```

---

## VERIFICATION CHECKLIST

After deployment:

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"
$appService = "pi-planning-copilot"

# Check backend
Write-Host "Backend Status:"
az functionapp show --name $functionApp --resource-group $resourceGroup --query "state" -o tsv

# Check frontend
Write-Host "Frontend Status:"
az webapp show --name $appService --resource-group $resourceGroup --query "state" -o tsv

# Get URLs
Write-Host ""
Write-Host "Backend URL:"
az functionapp show --name $functionApp --resource-group $resourceGroup --query defaultHostName -o tsv

Write-Host "Frontend URL:"
az webapp show --name $appService --resource-group $resourceGroup --query defaultHostName -o tsv
```

---

## TROUBLESHOOTING

### Backend deployment fails
```powershell
# Check if function app exists
az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev

# If not, create it
az functionapp create `
  --resource-group rg-scp-mcp-dev `
  --consumption-plan-location eastus `
  --runtime python `
  --runtime-version 3.9 `
  --functions-version 4 `
  --name pi-planning-intelligence `
  --storage-account <storage-account-name>
```

### Frontend deployment fails
```powershell
# Check if app service exists
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev

# If not, create it
az appservice plan create --name asp-planning-intelligence --resource-group rg-scp-mcp-dev --sku B1 --is-linux
az webapp create --name pi-planning-copilot --resource-group rg-scp-mcp-dev --plan asp-planning-intelligence
```

### CORS error
```powershell
# Enable CORS
az functionapp cors add --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --allowed-origins "*"
```

---

## QUICK COMMANDS

```powershell
# Deploy backend
cd planning_intelligence
func azure functionapp publish pi-planning-intelligence

# Deploy frontend
cd frontend
npm run build
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip

# Get URLs
az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

