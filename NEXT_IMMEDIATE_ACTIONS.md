# Next Immediate Actions - After Storage Account Setup

**Status**: ✅ Storage Account Verified  
**Next**: Create Blob Container & Continue Deployment  
**Time**: ~5 minutes for container, then continue with Function App

---

## ✅ What You've Completed

- ✅ Resource Group: `Rg-pi-copilot-dev` created
- ✅ Storage Account: `stgpicopilotdev` created
- ✅ Configuration: **Fully compliant with SFI zero-trust policies**

---

## 🎯 Immediate Actions (Next 5 Minutes)

### Action 1: Create Blob Container

```bash
# Set variables
$resourceGroup = "Rg-pi-copilot-dev"
$storageAccount = "stgpicopilotdev"
$containerName = "planning-data"

# Create container using Azure AD authentication (no keys)
az storage container create \
  --name $containerName \
  --account-name $storageAccount \
  --resource-group $resourceGroup \
  --auth-mode login

# Verify container was created
az storage container exists \
  --name $containerName \
  --account-name $storageAccount \
  --auth-mode login
```

**Expected output:**
```
{
  "exists": true
}
```

### Action 2: Upload Planning Data (Optional - If You Have Data)

```bash
# If you have a snapshot.json file with planning data:
az storage blob upload \
  --account-name $storageAccount \
  --container-name $containerName \
  --name "snapshot.json" \
  --file ./snapshot.json \
  --auth-mode login

# Verify upload
az storage blob list \
  --account-name $storageAccount \
  --container-name $containerName \
  --auth-mode login
```

---

## 🚀 Continue with Function App Setup

Once the container is created, proceed with the next steps from **COMPLIANCE_QUICK_SETUP.md**:

### Step 4: Create App Service Plan
```bash
$appServicePlan = "plan-pi-copilot-dev"

az appservice plan create \
  --name $appServicePlan \
  --resource-group $resourceGroup \
  --sku B1 \
  --is-linux \
  --subscription $subscription
```

### Step 5: Create Function App
```bash
$functionApp = "func-pi-copilot-dev"

az functionapp create \
  --name $functionApp \
  --resource-group $resourceGroup \
  --plan $appServicePlan \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --storage-account $storageAccount \
  --subscription $subscription
```

### Step 6: Enable Managed Identity
```bash
az functionapp identity assign \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription

$principalId = az functionapp identity show \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query principalId -o tsv

echo "Principal ID: $principalId"
```

### Step 7: Assign RBAC Roles
```bash
# Get storage account ID
$storageAccountId = az storage account show \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query id -o tsv

# Assign Storage Blob Data Reader role
az role assignment create \
  --assignee $principalId \
  --role "Storage Blob Data Reader" \
  --scope $storageAccountId \
  --subscription $subscription
```

---

## 📋 Quick Checklist

- [ ] Blob container "planning-data" created
- [ ] Planning data uploaded (if available)
- [ ] App Service Plan created
- [ ] Function App created
- [ ] Managed Identity enabled
- [ ] RBAC role assigned (Storage Blob Data Reader)
- [ ] Ready for Azure OpenAI setup

---

## 🔐 Verification Commands

```bash
# Verify container exists
az storage container exists \
  --name planning-data \
  --account-name stgpicopilotdev \
  --auth-mode login

# Verify Function App exists
az functionapp show \
  --name func-pi-copilot-dev \
  --resource-group Rg-pi-copilot-dev

# Verify Managed Identity
az functionapp identity show \
  --name func-pi-copilot-dev \
  --resource-group Rg-pi-copilot-dev

# Verify RBAC role
az role assignment list \
  --assignee <principal-id> \
  --scope <storage-account-id>
```

---

## 📚 Full Workflow

```
1. ✅ Create Resource Group (DONE)
2. ✅ Create Storage Account (DONE)
3. ✅ Configure Storage Account (DONE)
4. → Create Blob Container (NOW)
5. → Upload Planning Data (OPTIONAL)
6. → Create App Service Plan (NEXT)
7. → Create Function App (NEXT)
8. → Enable Managed Identity (NEXT)
9. → Assign RBAC Roles (NEXT)
10. → Create Azure OpenAI (NEXT)
11. → Configure Function App Settings (NEXT)
12. → Deploy Backend Code (NEXT)
13. → Test & Verify (NEXT)
```

---

## 🎯 Next Steps After This

Once you complete the immediate actions above:

1. **Create Azure OpenAI Resource** (Step 8 in COMPLIANCE_QUICK_SETUP.md)
2. **Configure Function App Settings** (Step 9)
3. **Deploy Backend Code** (Step 10)
4. **Test & Verify** (Verification section)

---

## 📞 Need Help?

- **Quick Setup Guide**: COMPLIANCE_QUICK_SETUP.md
- **Detailed Guide**: COMPLIANCE_DEPLOYMENT_GUIDE.md
- **Storage Config Verified**: STORAGE_ACCOUNT_CONFIGURATION_VERIFIED.md

---

**Status**: Ready for next steps  
**Time**: ~5 minutes to create container  
**Then**: Continue with Function App setup
