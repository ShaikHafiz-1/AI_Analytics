# Deploy Frontend to Azure Blob Storage (Static Website)

This is the correct approach for your org laptop setup. You're deploying the React build to blob storage's `$web` container.

## Prerequisites

- Azure Storage Account: `planningdatapi`
- Container: `$web` (for static website hosting)
- Backend: `https://pi-planning-intelligence.azurewebsites.net/api`

## Deployment Steps

### Step 1: Update Frontend Environment

Edit `frontend/.env`:

```
PORT=3000
REACT_APP_API_URL=https://pi-planning-intelligence.azurewebsites.net/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

### Step 2: Build Frontend

```powershell
cd frontend
npm run build
```

### Step 3: Deploy to Blob Storage

```powershell
# Upload build files to $web container
az storage blob upload-batch -d '$web' -s build --account-name planningdatapi
```

### Step 4: Get Static Website URL

```powershell
# Get the static website endpoint
az storage account show --name planningdatapi --query "primaryEndpoints.web" -o tsv
```

This will output something like:
```
https://planningdatapi.z5.web.core.windows.net/
```

## CORS Configuration (If Needed)

If you get CORS errors, configure CORS on the storage account:

```powershell
az storage cors add --methods GET POST PUT --origins "*" --allowed-headers "*" --exposed-headers "*" --max-age 3600 --services b --account-name planningdatapi
```

## Verify Deployment

1. Visit the static website URL
2. Dashboard should load
3. Check browser console for any errors
4. Verify backend connection works

## Troubleshooting

**404 on refresh**: Blob storage doesn't support SPA routing. Add `index.html` as default document:

```powershell
az storage blob service-properties update --account-name planningdatapi --static-website --index-document index.html --404-document index.html
```

**CORS errors**: Backend needs CORS headers. Check if backend has CORS enabled:

```powershell
# Test backend CORS
$url = "https://pi-planning-intelligence.azurewebsites.net/api/planning-dashboard-v2?code=<YOUR_FUNCTION_KEY>"
$response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
$response.Headers["Access-Control-Allow-Origin"]
```

## Advantages of Blob Storage Approach

✅ Cheaper than App Service  
✅ No server to manage  
✅ Automatic scaling  
✅ CDN-ready  
✅ Perfect for static React apps  

## Disadvantages

❌ No server-side rendering  
❌ No environment variables at runtime  
❌ Must rebuild for config changes  
❌ SPA routing needs special config  
