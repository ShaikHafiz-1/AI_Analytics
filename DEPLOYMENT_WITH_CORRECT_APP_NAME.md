# Deployment with Correct App Service Name

## Issue Found
The App Service was created with the name: `app-scp-mcp-dev` (not `pi-planning-copilot`)

## Corrected Commands

### Step 3: Build Frontend
```powershell
cd C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend
npm run build
```

### Step 4: Package
```powershell
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
```

### Step 5: Deploy (CORRECTED - using app-scp-mcp-dev)
```powershell
az webapp deploy --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --src-path "build.zip" --type zip
```

### Step 6: Get Backend Details
```powershell
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv
Write-Host "Backend URL: https://$functionUrl/api"
Write-Host "Function Key: $functionKey"
```

### Step 7: Configure Frontend (CORRECTED - using app-scp-mcp-dev)
```powershell
az webapp config appsettings set --name app-scp-mcp-dev --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"
```

### Step 8: Get Frontend URL (CORRECTED - using app-scp-mcp-dev)
```powershell
az webapp show --name app-scp-mcp-dev --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

---

## Summary of Changes

| Step | Old Name | New Name |
|------|----------|----------|
| Deploy | pi-planning-copilot | app-scp-mcp-dev |
| Configure | pi-planning-copilot | app-scp-mcp-dev |
| Get URL | pi-planning-copilot | app-scp-mcp-dev |

---

## Current Status

✅ Backend: `pi-planning-intelligence` (Function App, running)
✅ Frontend: `app-scp-mcp-dev` (App Service, created)

Now run Steps 3-8 with the corrected app name.
