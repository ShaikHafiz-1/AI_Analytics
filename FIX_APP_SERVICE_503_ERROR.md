# Fix App Service 503 Error - Frontend Deployment

## Problem
The App Service is returning 503 errors because:
1. The startup command is not configured correctly
2. The Node.js server (server.js) is not running
3. App Service doesn't know how to start the application

## Solution: Configure App Service Startup Command

### Step 1: Set the Startup Command in Azure Portal

```bash
# Go to Azure Portal → app-scp-mcp-dev → Configuration → General settings
# Set "Startup command" to:
node server.js
```

**Important**: Do NOT include the full path, just `node server.js`

### Step 2: Update App Service Configuration via CLI

Run this command to set the startup command:

```bash
az webapp config set --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --startup-file "node server.js"
```

### Step 3: Verify the Build Folder Exists

The deployment must include the `build` folder. Check:

```bash
# In your frontend directory, verify build exists:
ls -la frontend/build/
# Should show: index.html, static/, favicon.ico, etc.
```

### Step 4: Redeploy Frontend

```bash
# From frontend directory:
cd frontend

# Ensure build is fresh:
npm run build

# Create deployment package:
Compress-Archive -Path "build", "server.js", "package.json", "package-lock.json" -DestinationPath "frontend-deploy.zip" -Force

# Deploy to App Service:
az webapp deployment source config-zip --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --src frontend-deploy.zip
```

### Step 5: Verify Deployment

After deployment, check the logs:

```bash
# Stream live logs:
az webapp log tail --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev

# Should see: "Server running on port 8080"
```

### Step 6: Test the URL

Visit: `https://app-scp-mcp-dev.azurewebsites.net`

Should now load without 503 errors.

## Troubleshooting

If still getting 503:

1. **Check startup command is set**:
   ```bash
   az webapp config show --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --query "appCommandLine"
   ```

2. **Check logs for errors**:
   ```bash
   az webapp log tail --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --lines 50
   ```

3. **Verify Node.js runtime**:
   ```bash
   az webapp config show --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --query "linuxFxVersion"
   # Should show: node|24-lts or similar
   ```

4. **Check if build folder is deployed**:
   - Go to Azure Portal → app-scp-mcp-dev → Advanced Tools (Kudu)
   - Navigate to `/home/site/wwwroot/`
   - Should see: `build/`, `server.js`, `package.json`

## Alternative: Use Azure Static Web Apps (Faster)

If you want to avoid the Node.js complexity, use Static Web Apps:

```bash
# Create Static Web App:
az staticwebapp create \
  --name scp-frontend \
  --resource-group rg-scp-mcp-dev \
  --location eastus \
  --sku Free

# Deploy build folder:
az staticwebapp upload \
  --name scp-frontend \
  --app-location frontend/build
```

This is simpler and faster for React apps.
