# Deploy Frontend to App Service - Complete Guide

## Current Status

✅ **App Service**: `pi-planning-copilot` (already exists)
✅ **Resource Group**: `rg-scp-mcp-dev`
✅ **Backend**: `pi-planning-intelligence` (running)
✅ **Frontend Build**: Ready to deploy

---

## STEP 1: Build Frontend

```powershell
# Navigate to frontend directory
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend

# Build for production
npm run build

# Verify build folder created
Get-ChildItem build | Select-Object Name
```

**Expected output**:
```
Directory: C:\...\frontend\build

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         4/13/2026   2:30 PM                css
d-----         4/13/2026   2:30 PM                js
d-----         4/13/2026   2:30 PM                static
-a----         4/13/2026   2:30 PM          1234 index.html
-a----         4/13/2026   2:30 PM          5678 favicon.ico
```

---

## STEP 2: Create Deployment Package

```powershell
# Still in frontend directory
# Create zip file of build folder
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# Verify zip created
Get-Item build.zip | Select-Object Name, Length
```

**Expected output**:
```
Name     Length
----     ------
build.zip 2345678
```

---

## STEP 3: Deploy to App Service

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Deploy the zip file
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip

Write-Host "✓ Frontend deployed successfully!"
```

**Expected output**:
```
Getting scm site credentials for zip deployment
Deploying and building...
Deployment successful.
```

---

## STEP 4: Get Backend URL and Key

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$functionApp = "pi-planning-intelligence"

# Get function app URL
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

**Save these values - you'll need them in the next step.**

---

## STEP 5: Configure Frontend Environment Variables

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$functionUrl = "pi-planning-intelligence.azurewebsites.net"  # Replace with actual URL from Step 4
$functionKey = "<YOUR_FUNCTION_KEY>"  # Replace with actual key from Step 4

# Set app settings
az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"

Write-Host "✓ Frontend configured with backend URL"
```

---

## STEP 6: Get Frontend URL

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

---

## STEP 7: Test Deployment

```powershell
# Wait 2-3 minutes for app to start
Write-Host "Waiting for app to start..."
Start-Sleep -Seconds 120

# Get frontend URL
$frontendUrl = az webapp show `
  --name pi-planning-copilot `
  --resource-group rg-scp-mcp-dev `
  --query defaultHostName `
  -o tsv

# Test the URL
$response = Invoke-WebRequest -Uri "https://$frontendUrl" -UseBasicParsing

Write-Host "Status Code: $($response.StatusCode)"
Write-Host "Frontend is running!"
```

---

## COMPLETE DEPLOYMENT SCRIPT

Save this as `deploy-frontend.ps1`:

```powershell
# Configuration
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$functionApp = "pi-planning-intelligence"
$basePath = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Deployment to App Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build Frontend
Write-Host "STEP 1: Building Frontend..." -ForegroundColor Yellow
cd "$basePath\frontend"
npm run build
Write-Host "✓ Frontend built" -ForegroundColor Green
Write-Host ""

# Step 2: Create Deployment Package
Write-Host "STEP 2: Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
Write-Host "✓ Deployment package created" -ForegroundColor Green
Write-Host ""

# Step 3: Deploy to App Service
Write-Host "STEP 3: Deploying to App Service..." -ForegroundColor Yellow
az webapp deploy `
  --resource-group $resourceGroup `
  --name $appService `
  --src-path "build.zip" `
  --type zip
Write-Host "✓ Frontend deployed" -ForegroundColor Green
Write-Host ""

# Step 4: Get Backend Details
Write-Host "STEP 4: Getting backend details..." -ForegroundColor Yellow
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

# Step 5: Configure Frontend
Write-Host "STEP 5: Configuring frontend..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $appService `
  --resource-group $resourceGroup `
  --settings `
    REACT_APP_API_URL="https://$functionUrl/api" `
    REACT_APP_API_KEY="$functionKey"
Write-Host "✓ Frontend configured" -ForegroundColor Green
Write-Host ""

# Step 6: Get Frontend URL
Write-Host "STEP 6: Getting frontend URL..." -ForegroundColor Yellow
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
Write-Host "If you see errors:" -ForegroundColor Yellow
Write-Host "- Check browser console (F12) for errors" -ForegroundColor Yellow
Write-Host "- Check app logs: az webapp log tail --name $appService --resource-group $resourceGroup" -ForegroundColor Yellow
```

Run it:
```powershell
.\deploy-frontend.ps1
```

---

## QUICK COMMANDS (Copy & Paste)

### Build
```powershell
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend
npm run build
```

### Package
```powershell
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
```

### Deploy
```powershell
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip
```

### Configure
```powershell
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv
az webapp config appsettings set --name pi-planning-copilot --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"
```

### Get URL
```powershell
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

---

## VERIFICATION

### Check Deployment Status
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
- Check app logs: `az webapp log tail --name pi-planning-copilot --resource-group rg-scp-mcp-dev`

### API Connection Error
- Verify `REACT_APP_API_URL` is set correctly
- Check backend is running: `az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "state" -o tsv`
- Check CORS is enabled on backend

### Deployment Failed
- Check if app service exists: `az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev`
- Check build folder exists: `Get-ChildItem build`
- Try redeploying: `az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip`

---

## NEXT STEPS

1. ✅ Build frontend
2. ✅ Create deployment package
3. ✅ Deploy to App Service
4. ✅ Configure environment variables
5. ✅ Get frontend URL
6. Open URL in browser
7. Test dashboard and copilot

Ready to deploy? Run the complete script or follow the steps above.
