# Create App Service and Deploy Frontend

## Current Status
✅ Backend: `pi-planning-intelligence` (Function App, running)
❌ Frontend: `pi-planning-copilot` (App Service, needs to be created)

---

## STEP 1: Create App Service Plan

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appServicePlan = "asp-planning-intelligence"

# Create app service plan
az appservice plan create `
  --name $appServicePlan `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux

Write-Host "✓ App Service Plan created: $appServicePlan"
```

---

## STEP 2: Create App Service

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$appServicePlan = "asp-planning-intelligence"

# Create app service
az webapp create `
  --name $appService `
  --resource-group $resourceGroup `
  --plan $appServicePlan `
  --runtime "node|18-lts"

Write-Host "✓ App Service created: $appService"
```

---

## STEP 3: Build Frontend

```powershell
# Navigate to frontend
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend

# Build for production
npm run build

Write-Host "✓ Frontend built"
```

---

## STEP 4: Create Deployment Package

```powershell
# Still in frontend directory
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

Write-Host "✓ Deployment package created"
```

---

## STEP 5: Deploy to App Service

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Deploy
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip

Write-Host "✓ Frontend deployed"
```

---

## STEP 6: Get Backend URL and Key

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"

# Get backend URL
$functionUrl = az functionapp show `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

Write-Host "Backend URL: https://$functionUrl/api"

# Get function key
$functionKey = az functionapp keys list `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query "functionKeys.default" `
  -o tsv

Write-Host "Function Key: $functionKey"
```

---

## STEP 7: Configure Frontend Environment

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$functionUrl = "pi-planning-intelligence.azurewebsites.net"  # Replace with actual from Step 6
$functionKey = "<YOUR_FUNCTION_KEY>"  # Replace with actual from Step 6

# Set environment variables
az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"

Write-Host "✓ Frontend configured"
```

---

## STEP 8: Get Frontend URL

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
```

---

## COMPLETE SCRIPT (Copy & Run)

Save as `create-and-deploy.ps1`:

```powershell
# Configuration
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"
$appService = "pi-planning-copilot"
$appServicePlan = "asp-planning-intelligence"
$basePath = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating App Service and Deploying Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create App Service Plan
Write-Host "STEP 1: Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
  --name $appServicePlan `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux
Write-Host "✓ App Service Plan created" -ForegroundColor Green
Write-Host ""

# Step 2: Create App Service
Write-Host "STEP 2: Creating App Service..." -ForegroundColor Yellow
az webapp create `
  --name $appService `
  --resource-group $resourceGroup `
  --plan $appServicePlan `
  --runtime "node|18-lts"
Write-Host "✓ App Service created" -ForegroundColor Green
Write-Host ""

# Step 3: Build Frontend
Write-Host "STEP 3: Building Frontend..." -ForegroundColor Yellow
cd "$basePath\frontend"
npm run build
Write-Host "✓ Frontend built" -ForegroundColor Green
Write-Host ""

# Step 4: Create Deployment Package
Write-Host "STEP 4: Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
Write-Host "✓ Deployment package created" -ForegroundColor Green
Write-Host ""

# Step 5: Deploy to App Service
Write-Host "STEP 5: Deploying to App Service..." -ForegroundColor Yellow
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip
Write-Host "✓ Frontend deployed" -ForegroundColor Green
Write-Host ""

# Step 6: Get Backend Details
Write-Host "STEP 6: Getting backend details..." -ForegroundColor Yellow
$functionUrl = az functionapp show `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

$functionKey = az functionapp keys list `
  --name $functionApp `
  --resource-group $resourceGroup `
  --query "functionKeys.default" `
  -o tsv

Write-Host "Backend URL: https://$functionUrl/api" -ForegroundColor Cyan
Write-Host "✓ Backend details retrieved" -ForegroundColor Green
Write-Host ""

# Step 7: Configure Frontend
Write-Host "STEP 7: Configuring frontend..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"
Write-Host "✓ Frontend configured" -ForegroundColor Green
Write-Host ""

# Step 8: Get Frontend URL
Write-Host "STEP 8: Getting frontend URL..." -ForegroundColor Yellow
$frontendUrl = az webapp show `
  --name $appService `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv
Write-Host "✓ Frontend URL retrieved" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL: https://$frontendUrl" -ForegroundColor Cyan
Write-Host "Backend URL: https://$functionUrl/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Wait 2-3 minutes for the app to fully start" -ForegroundColor Yellow
Write-Host "2. Open https://$frontendUrl in your browser" -ForegroundColor Yellow
Write-Host "3. Refresh the page if you see a blank screen" -ForegroundColor Yellow
Write-Host ""
```

Run it:
```powershell
.\create-and-deploy.ps1
```

---

## QUICK COMMANDS (If you want to run step by step)

### 1. Create App Service Plan
```powershell
az appservice plan create --name asp-planning-intelligence --resource-group rg-scp-mcp-dev --sku B1 --is-linux
```

### 2. Create App Service
```powershell
az webapp create --name pi-planning-copilot --resource-group rg-scp-mcp-dev --plan asp-planning-intelligence --runtime "node|18-lts"
```

### 3. Build Frontend
```powershell
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend
npm run build
```

### 4. Package
```powershell
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
```

### 5. Deploy
```powershell
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip
```

### 6. Get Backend URL and Key
```powershell
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv
Write-Host "Backend URL: https://$functionUrl/api"
Write-Host "Function Key: $functionKey"
```

### 7. Configure Frontend
```powershell
az webapp config appsettings set --name pi-planning-copilot --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://pi-planning-intelligence.azurewebsites.net/api" REACT_APP_API_KEY="<YOUR_FUNCTION_KEY>"
```

### 8. Get Frontend URL
```powershell
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

---

## VERIFICATION

### Check App Service Status
```powershell
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query "state" -o tsv
```

### View Logs
```powershell
az webapp log tail --name pi-planning-copilot --resource-group rg-scp-mcp-dev
```

### Check App Settings
```powershell
az webapp config appsettings list --name pi-planning-copilot --resource-group rg-scp-mcp-dev
```

---

## TROUBLESHOOTING

### Blank Page
- Wait 2-3 minutes for app to start
- Refresh the page
- Check browser console (F12) for errors

### API Connection Error
- Verify `REACT_APP_API_URL` is set correctly
- Check backend is running: `az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "state" -o tsv`

### Deployment Failed
- Check if app service exists: `az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev`
- Check build folder: `Get-ChildItem build`
- Redeploy: `az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip`

---

## WHAT HAPPENS NEXT

1. ✅ App Service Plan created
2. ✅ App Service created
3. ✅ Frontend built
4. ✅ Frontend deployed
5. ✅ Frontend configured with backend URL
6. Open URL in browser
7. Dashboard loads with real data from blob storage
8. Copilot works with backend API

Ready to run the script?
