# Create App Service and Deploy Frontend

## Problem
```
The Resource 'Microsoft.Web/sites/pi-planning-copilot' under resource group 'rg-scp-mcp-dev' was not found.
```

The App Service doesn't exist. You need to create it first.

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

**Expected output**:
```
{
  "id": "/subscriptions/.../resourceGroups/rg-scp-mcp-dev/providers/Microsoft.Web/serverfarms/asp-planning-intelligence",
  "name": "asp-planning-intelligence",
  "sku": {
    "name": "B1",
    "tier": "Basic"
  },
  "status": "Ready"
}
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
  --plan $appServicePlan

Write-Host "✓ App Service created: $appService"
```

**Expected output**:
```
{
  "id": "/subscriptions/.../resourceGroups/rg-scp-mcp-dev/providers/Microsoft.Web/sites/pi-planning-copilot",
  "name": "pi-planning-copilot",
  "type": "Microsoft.Web/sites",
  "defaultHostName": "pi-planning-copilot.azurewebsites.net",
  "state": "Running"
}
```

---

## STEP 3: Build Frontend

```powershell
# Navigate to frontend
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend

# Build for production
npm run build

Write-Host "✓ Frontend built successfully"
```

---

## STEP 4: Deploy Frontend

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Create zip of build folder
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# Deploy using new command
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip

Write-Host "✓ Frontend deployed successfully"
```

---

## STEP 5: Configure Frontend Environment

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

Write-Host "✓ Frontend configured"
Write-Host "Backend URL: https://$functionUrl/api"
```

---

## COMPLETE SCRIPT: Create and Deploy Everything

Save this as `create-and-deploy.ps1`:

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
  --plan $appServicePlan
Write-Host "✓ App Service created" -ForegroundColor Green
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
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip
Write-Host "✓ Frontend deployed" -ForegroundColor Green
Write-Host ""

# Step 5: Configure Frontend
Write-Host "STEP 5: Configuring Frontend..." -ForegroundColor Yellow
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

az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"

Write-Host "✓ Frontend configured" -ForegroundColor Green
Write-Host ""

# Step 6: Get URLs
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$frontendUrl = az webapp show `
  --name $appService `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv

Write-Host "Frontend URL: https://$frontendUrl" -ForegroundColor Cyan
Write-Host "Backend URL: https://$functionUrl/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open in browser: https://$frontendUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Wait 2-3 minutes for the app to fully start, then refresh the page." -ForegroundColor Yellow
```

Run it:
```powershell
.\create-and-deploy.ps1
```

---

## QUICK COMMANDS

### Create App Service Plan
```powershell
az appservice plan create --name asp-planning-intelligence --resource-group rg-scp-mcp-dev --sku B1 --is-linux
```

### Create App Service
```powershell
az webapp create --name pi-planning-copilot --resource-group rg-scp-mcp-dev --plan asp-planning-intelligence
```

### Build Frontend
```powershell
cd frontend
npm run build
```

### Deploy Frontend
```powershell
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip
```

### Configure Frontend
```powershell
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv

az webapp config appsettings set --name pi-planning-copilot --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"
```

### Get Frontend URL
```powershell
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

---

## VERIFICATION

After deployment:

```powershell
# Check app service status
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query "state" -o tsv

# Get frontend URL
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv

# Check logs
az webapp log tail --name pi-planning-copilot --resource-group rg-scp-mcp-dev
```

---

## TROUBLESHOOTING

### Error: "App Service Plan not found"
```powershell
# Create it
az appservice plan create --name asp-planning-intelligence --resource-group rg-scp-mcp-dev --sku B1 --is-linux
```

### Error: "Deployment failed"
```powershell
# Check logs
az webapp log tail --name pi-planning-copilot --resource-group rg-scp-mcp-dev

# Redeploy
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip
```

### Error: "Blank page"
```powershell
# Check app settings
az webapp config appsettings list --name pi-planning-copilot --resource-group rg-scp-mcp-dev

# Verify REACT_APP_API_URL is set correctly
# Should be: https://pi-planning-intelligence.azurewebsites.net/api
```

---

## NEXT STEPS

1. ✅ Create App Service Plan
2. ✅ Create App Service
3. ✅ Build Frontend
4. ✅ Deploy Frontend
5. ✅ Configure Frontend
6. Open `https://pi-planning-copilot.azurewebsites.net` in browser
7. Wait 2-3 minutes for app to start
8. Refresh page and test

