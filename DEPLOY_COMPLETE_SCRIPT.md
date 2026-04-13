# Complete Deployment Script - Corrected Format

## Full Deployment Commands

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
az appservice plan create --name $appServicePlan --resource-group $resourceGroup --sku B1 --is-linux
Write-Host "✓ App Service Plan created" -ForegroundColor Green
Write-Host ""

# Step 2: Create App Service (CORRECTED FORMAT)
Write-Host "STEP 2: Creating App Service..." -ForegroundColor Yellow
az webapp create --name $appService --resource-group $resourceGroup --plan $appServicePlan --runtime node --runtime-version 18-lts
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
az webapp deploy --resource-group $resourceGroup --name $appService --src-path "build.zip" --type zip
Write-Host "✓ Frontend deployed" -ForegroundColor Green
Write-Host ""

# Step 6: Get Backend Details
Write-Host "STEP 6: Getting backend details..." -ForegroundColor Yellow
$functionUrl = az functionapp show --name $functionApp --resource-group $resourceGroup --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name $functionApp --resource-group $resourceGroup --query "functionKeys.default" -o tsv
Write-Host "Backend URL: https://$functionUrl/api" -ForegroundColor Cyan
Write-Host "✓ Backend details retrieved" -ForegroundColor Green
Write-Host ""

# Step 7: Configure Frontend
Write-Host "STEP 7: Configuring frontend..." -ForegroundColor Yellow
az webapp config appsettings set --name $appService --resource-group $resourceGroup --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"
Write-Host "✓ Frontend configured" -ForegroundColor Green
Write-Host ""

# Step 8: Get Frontend URL
Write-Host "STEP 8: Getting frontend URL..." -ForegroundColor Yellow
$frontendUrl = az webapp show --name $appService --resource-group $resourceGroup --query defaultHostName -o tsv
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

---

## Quick Copy-Paste Commands

### Step 1: Create App Service Plan
```powershell
az appservice plan create --name asp-planning-intelligence --resource-group rg-scp-mcp-dev --sku B1 --is-linux
```

### Step 2: Create App Service (CORRECTED)
```powershell
az webapp create --name pi-planning-copilot --resource-group rg-scp-mcp-dev --plan asp-planning-intelligence --runtime node --runtime-version 18-lts
```

### Step 3: Build Frontend
```powershell
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend
npm run build
```

### Step 4: Package
```powershell
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
```

### Step 5: Deploy
```powershell
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip
```

### Step 6: Get Backend Details
```powershell
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv
Write-Host "Backend URL: https://$functionUrl/api"
Write-Host "Function Key: $functionKey"
```

### Step 7: Configure Frontend
```powershell
az webapp config appsettings set --name pi-planning-copilot --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://pi-planning-intelligence.azurewebsites.net/api" REACT_APP_API_KEY="<YOUR_FUNCTION_KEY>"
```

Replace `<YOUR_FUNCTION_KEY>` with the actual key from Step 6.

### Step 8: Get Frontend URL
```powershell
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

---

## Key Change

**Old (broken)**:
```powershell
az webapp create --name $appService --resource-group $resourceGroup --plan $appServicePlan --runtime "node|18-lts"
```

**New (correct)**:
```powershell
az webapp create --name $appService --resource-group $resourceGroup --plan $appServicePlan --runtime node --runtime-version 18-lts
```

The pipe character issue is resolved by using separate `--runtime` and `--runtime-version` parameters.

---

## Run the Complete Script

Save as `deploy.ps1` and run:
```powershell
.\deploy.ps1
```

Or run the commands one by one from the "Quick Copy-Paste Commands" section above.
