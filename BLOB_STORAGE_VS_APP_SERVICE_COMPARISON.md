# Frontend Deployment: Blob Storage vs App Service

## Quick Answer
**Recommendation: Use App Service** ✅

You already have `pi-planning-copilot` App Service ready. It's the better choice for your use case.

---

## Detailed Comparison

### Option 1: Azure Blob Storage Static Website Hosting

**What it is**: Host static HTML/CSS/JS files directly from blob storage

**Pros**:
- ✅ Cheapest option (~$0.50/month for storage)
- ✅ Simplest setup (upload files to `$web` container)
- ✅ No server management
- ✅ Built-in CDN support
- ✅ Good for pure static sites

**Cons**:
- ❌ No server-side rendering
- ❌ No environment variable management (must hardcode API URLs)
- ❌ No authentication/authorization
- ❌ No SSL certificate management
- ❌ Limited logging and monitoring
- ❌ CORS configuration is complex
- ❌ No request routing or rewriting
- ❌ Cannot run backend code

**Cost**: ~$0.50/month

**Setup Time**: 15 minutes

---

### Option 2: Azure App Service (RECOMMENDED)

**What it is**: Managed web hosting with Node.js runtime

**Pros**:
- ✅ Environment variable management (REACT_APP_API_URL, etc.)
- ✅ Automatic SSL/TLS certificates
- ✅ Built-in authentication support
- ✅ Better logging and monitoring
- ✅ Request routing and rewriting
- ✅ Easy CORS configuration
- ✅ Staging slots for testing
- ✅ Auto-scaling available
- ✅ You already have it created (`pi-planning-copilot`)
- ✅ Better for production apps

**Cons**:
- ❌ Slightly higher cost (~$10-50/month depending on tier)
- ❌ Requires app service plan

**Cost**: ~$10-50/month (B1 tier = ~$10/month)

**Setup Time**: 5 minutes (already created)

---

## Your Current Situation

```
✅ App Service: pi-planning-copilot (READY)
✅ App Service Plan: asp-planning-intelligence (READY)
✅ Resource Group: rg-scp-mcp-dev (READY)
✅ Frontend Build: build.zip (READY)
✅ Backend: pi-planning-intelligence (RUNNING)
```

**Everything is ready for App Service deployment.**

---

## Why App Service is Better for Your Use Case

1. **Environment Variables**: Your frontend needs `REACT_APP_API_URL` to point to the backend
   - App Service: ✅ Automatic environment variable injection
   - Blob Storage: ❌ Must hardcode URL in build

2. **CORS Configuration**: Frontend calls backend API
   - App Service: ✅ Easy CORS setup
   - Blob Storage: ❌ Complex CORS configuration

3. **Future Features**: You might need:
   - Authentication/authorization
   - Server-side rendering
   - API proxying
   - Request logging
   - App Service: ✅ All supported
   - Blob Storage: ❌ Not supported

4. **Cost**: For a production app, the difference is minimal
   - App Service B1: ~$10/month
   - Blob Storage: ~$0.50/month
   - **Difference: $9.50/month** (worth it for features)

---

## Deployment Comparison

### Blob Storage Deployment (if you wanted to)

```powershell
# 1. Enable static website hosting
$storageAccount = "your-storage-account"
$resourceGroup = "rg-scp-mcp-dev"

az storage blob service-properties update `
  --account-name $storageAccount `
  --static-website `
  --index-document index.html `
  --404-document index.html

# 2. Upload build files
az storage blob upload-batch `
  -d '$web' `
  -s "frontend/build" `
  --account-name $storageAccount

# 3. Get URL
az storage account show `
  --name $storageAccount `
  --query "primaryEndpoints.web" `
  -o tsv

# Result: https://yourstorageaccount.z5.web.core.windows.net/
```

**Problem**: Frontend can't reach backend API due to CORS and hardcoded URLs

---

### App Service Deployment (RECOMMENDED)

```powershell
# 1. Build frontend
cd frontend
npm run build

# 2. Create deployment package
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# 3. Deploy to App Service
az webapp deploy `
  --resource-group rg-scp-mcp-dev `
  --name pi-planning-copilot `
  --src-path "build.zip" `
  --type zip

# 4. Configure environment
az webapp config appsettings set `
  --name pi-planning-copilot `
  --resource-group rg-scp-mcp-dev `
  --settings `
    REACT_APP_API_URL="https://pi-planning-intelligence.azurewebsites.net/api" `
    REACT_APP_API_KEY="<your-function-key>"

# Result: https://pi-planning-copilot.azurewebsites.net/
```

**Benefit**: Frontend automatically gets backend URL from environment variables

---

## Decision Matrix

| Feature | Blob Storage | App Service |
|---------|--------------|-------------|
| Cost | $0.50/mo | $10/mo |
| Setup Time | 15 min | 5 min (already done) |
| Environment Variables | ❌ No | ✅ Yes |
| CORS Support | ⚠️ Complex | ✅ Easy |
| SSL/TLS | ✅ Yes | ✅ Yes |
| Logging | ⚠️ Limited | ✅ Full |
| Authentication | ❌ No | ✅ Yes |
| Staging Slots | ❌ No | ✅ Yes |
| Auto-scaling | ❌ No | ✅ Yes |
| Production Ready | ⚠️ For static sites | ✅ Yes |

---

## My Recommendation

**Use App Service** because:

1. ✅ Already created and ready
2. ✅ Supports environment variables (critical for your setup)
3. ✅ Better CORS handling
4. ✅ Production-ready features
5. ✅ Only 5 minutes to deploy
6. ✅ Cost difference is minimal ($9.50/month)
7. ✅ Future-proof for enhancements

---

## Next Steps

**Option A: Deploy to App Service (RECOMMENDED)**
```powershell
# 1. Build frontend
cd frontend
npm run build

# 2. Deploy
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force
az webapp deploy --resource-group rg-scp-mcp-dev --name pi-planning-copilot --src-path "build.zip" --type zip

# 3. Configure
$functionUrl = az functionapp show --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
$functionKey = az functionapp keys list --name pi-planning-intelligence --resource-group rg-scp-mcp-dev --query "functionKeys.default" -o tsv

az webapp config appsettings set --name pi-planning-copilot --resource-group rg-scp-mcp-dev --settings REACT_APP_API_URL="https://$functionUrl/api" REACT_APP_API_KEY="$functionKey"

# 4. Get URL
az webapp show --name pi-planning-copilot --resource-group rg-scp-mcp-dev --query defaultHostName -o tsv
```

**Option B: Deploy to Blob Storage (if you prefer)**
- See "Blob Storage Deployment" section above
- Note: You'll need to handle CORS and hardcode API URLs

---

## Questions?

- **Q: Will the frontend work with the backend?**
  - A: Yes, App Service handles CORS and environment variables automatically

- **Q: Can I switch later?**
  - A: Yes, you can always migrate from one to the other

- **Q: What about costs?**
  - A: App Service B1 tier is ~$10/month. Blob Storage is ~$0.50/month. The difference is worth the features.

- **Q: Is App Service production-ready?**
  - A: Yes, it's designed for production workloads

---

## Summary

| Aspect | Recommendation |
|--------|-----------------|
| **Deployment Target** | App Service (`pi-planning-copilot`) |
| **Cost** | $10/month (B1 tier) |
| **Setup Time** | 5 minutes |
| **Production Ready** | ✅ Yes |
| **Recommended** | ✅ Yes |

**Ready to deploy? Let me know and I'll provide the exact commands.**
