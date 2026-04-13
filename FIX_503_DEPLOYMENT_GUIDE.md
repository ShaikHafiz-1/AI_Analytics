# Fix 503 Error - Complete Deployment Guide

## Root Cause
The app service is failing because:
1. `server.js` exists but the build files aren't deployed
2. Frontend `.env` points to localhost (doesn't work in Azure)
3. App service needs both the server code AND the built React files

## Solution: Redeploy with Correct Configuration

### Step 1: Update Frontend Environment for Production

Update `frontend/.env`:

```
PORT=3000
REACT_APP_API_URL=https://pi-planning-intelligence.azurewebsites.net/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

### Step 2: Rebuild Frontend

```powershell
cd frontend
npm run build
```

### Step 3: Deploy to App Service

```powershell
# Create deployment package with server.js + build files
Compress-Archive -Path "server.js", "build", "package.json", "package-lock.json" -DestinationPath "frontend-deploy.zip" -Force

# Deploy to app service
az webapp deployment source config-zip --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev --src frontend-deploy.zip
```

### Step 4: Verify Deployment

Wait 2-3 minutes for the app service to restart, then visit:
```
https://app-scp-mcp-dev.azurewebsites.net
```

## What's Happening

- **server.js**: Express server that serves the React build files
- **build/**: Pre-built React application (static files)
- **App Service**: Runs `node server.js` which serves the build files on port 3000
- **Azure Maps**: Port 3000 → 80/443 automatically

## If Still Getting 503

Check logs:
```powershell
az webapp log tail --resource-group rg-scp-mcp-dev --name app-scp-mcp-dev
```

Common issues:
- Missing `node_modules` → Run `npm install` before zipping
- Wrong backend URL → Check REACT_APP_API_URL in .env
- Port binding → App service expects PORT env var (already set to 3000)
