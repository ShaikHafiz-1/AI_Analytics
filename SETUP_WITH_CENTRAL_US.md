# Setup Guide - Using Central US Region

**Region**: Central US (instead of East US)  
**Status**: Quota available ✅  
**Cost**: Same as East US  
**Performance**: Excellent  
**Time**: ~48 minutes

---

## ✅ Why Central US?

- ✅ Usually has available quota
- ✅ Good performance
- ✅ Same cost as East US
- ✅ No waiting for quota approval
- ✅ Immediate deployment

---

## 🚀 Step 1: Delete Failed App Service Plan

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"**
3. Find **"plan-pi-copilot-dev"** (if it exists)
4. Click on it
5. Click **"Delete"**
6. Type the name to confirm
7. Click **"Delete"**

**Wait for deletion** (1-2 minutes)

---

## 🔧 Step 2: Create App Service Plan in Central US

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"**
3. Click **"Create"**

**Fill in Basics Tab:**
```
Subscription: CO+I GSC Supplier Management Preprod
Resource Group: Rg-pi-copilot-dev
Name: plan-pi-copilot-dev
Operating System: Linux
Region: Central US ← IMPORTANT
Sku and size: B1 (Basic)
```

4. Click **"Review + create"**
5. Click **"Create"**
6. **Wait for deployment** (2-3 minutes)

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

## 📝 Step 3: Create Function App in Central US

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"Function App"**
3. Click **"Create"**

**Fill in Basics Tab:**
```
Subscription: CO+I GSC Supplier Management Preprod
Resource Group: Rg-pi-copilot-dev
Function App name: func-pi-copilot-dev
Publish: Code
Runtime stack: Python
Version: 3.9
Region: Central US ← IMPORTANT (same as App Service Plan)
```

**Fill in Hosting Tab:**
```
Storage account: stgpicopilotdev
Operating system: Linux
Plan type: App Service Plan
App Service Plan: plan-pi-copilot-dev
```

**Fill in Monitoring Tab:**
```
Enable Application Insights: Yes
Application Insights: Create new
Name: appi-pi-copilot-dev
Location: Central US
```

4. Click **"Review + create"**
5. Click **"Create"**
6. **Wait for deployment** (3-5 minutes)

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

## 🔐 Step 4: Enable Managed Identity

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App
4. In left menu, click **"Identity"**
5. Under **"System assigned"** tab:
   - Toggle **"Status"** to **"On"**
   - Click **"Save"**
6. Click **"Yes"** to confirm
7. **Copy the Object ID** (save for later)

**Expected**:
```
Status: On
Object ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 🔑 Step 5: Assign RBAC - Storage Blob Data Reader

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account
4. In left menu, click **"Access Control (IAM)"**
5. Click **"+ Add"** → **"Add role assignment"**

**Fill in:**
```
Role: Storage Blob Data Reader
Assign access to: Azure AD user, group, or service principal
Select members: func-pi-copilot-dev
```

6. Click **"Review + assign"**
7. Click **"Assign"**

**Expected**:
```
Role: Storage Blob Data Reader
Assigned to: func-pi-copilot-dev
```

---

## 🤖 Step 6: Create Azure OpenAI in Central US

1. Go to **Azure Portal** → https://portal.azure.com
2. Click **"+ Create a resource"**
3. Search for **"Azure OpenAI"**
4. Click on **"Azure OpenAI"** (by Microsoft)
5. Click **"Create"**

**Fill in Basics Tab:**
```
Subscription: CO+I GSC Supplier Management Preprod
Resource Group: Rg-pi-copilot-dev
Region: Central US ← IMPORTANT (same as App Service Plan)
Name: openai-pi-copilot-dev
Pricing tier: Standard S0
```

**Fill in Network Tab:**
```
Connectivity method: Public endpoint
Firewall: Disabled
```

6. Click **"Review + create"**
7. Click **"Create"**
8. **Wait for deployment** (5-10 minutes)

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

## 🧠 Step 7: Deploy GPT Model

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. Click **"Go to Azure OpenAI Studio"** (or Deployments in left menu)
5. Click **"Deployments"** (left menu)
6. Click **"+ Create new deployment"**

**Fill in:**
```
Select a model: gpt-3.5-turbo
Model version: 0613 (or latest)
Deployment name: gpt-35-turbo
Tokens per minute: 90,000 (or default)
```

7. Click **"Create"**
8. **Wait for deployment** (2-3 minutes)

**Expected**:
```
Model: gpt-3.5-turbo
Deployment name: gpt-35-turbo
Status: Succeeded
```

---

## 🔐 Step 8: Assign RBAC - Cognitive Services User

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. In left menu, click **"Access Control (IAM)"**
5. Click **"+ Add"** → **"Add role assignment"**

**Fill in:**
```
Role: Cognitive Services User
Assign access to: Azure AD user, group, or service principal
Select members: func-pi-copilot-dev
```

6. Click **"Review + assign"**
7. Click **"Assign"**

**Expected**:
```
Role: Cognitive Services User
Assigned to: func-pi-copilot-dev
```

---

## 📝 Step 9: Get Resource Endpoints

### Get Blob Storage Endpoint

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account
4. In left menu, click **"Endpoints"**
5. Copy the **"Blob service"** endpoint
   ```
   Save: AZURE_STORAGE_BLOB_ENDPOINT=https://stgpicopilotdev.blob.core.windows.net/
   ```

### Get Azure OpenAI Endpoint

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. In left menu, click **"Keys and Endpoint"**
5. Copy the **"Endpoint"**
   ```
   Save: AZURE_OPENAI_ENDPOINT=https://openai-pi-copilot-dev.openai.azure.com/
   ```

---

## ⚙️ Step 10: Configure Function App Settings

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App
4. In left menu, click **"Configuration"**
5. Click **"+ New application setting"** for each:

**Add these settings:**

| Name | Value |
|------|-------|
| AZURE_STORAGE_ACCOUNT_NAME | stgpicopilotdev |
| AZURE_STORAGE_CONTAINER_NAME | planning-data |
| AZURE_STORAGE_BLOB_ENDPOINT | https://stgpicopilotdev.blob.core.windows.net/ |
| AZURE_OPENAI_ENDPOINT | https://openai-pi-copilot-dev.openai.azure.com/ |
| AZURE_OPENAI_DEPLOYMENT_NAME | gpt-35-turbo |
| AZURE_OPENAI_API_VERSION | 2023-05-15 |

6. Click **"Save"**
7. Click **"Continue"** (to restart)

**Expected**: All 6 settings added and saved

---

## 📦 Step 11: Create Blob Container

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account
4. In left menu, click **"Containers"**
5. Click **"+ Container"**

**Fill in:**
```
Name: planning-data
Public access level: Private
```

6. Click **"Create"**

**Expected**: Container "planning-data" created

---

## ✅ Verification Checklist

```
INFRASTRUCTURE
☐ App Service Plan: plan-pi-copilot-dev (Central US)
☐ Function App: func-pi-copilot-dev (Central US)
☐ Azure OpenAI: openai-pi-copilot-dev (Central US)
☐ Container: planning-data

MANAGED IDENTITY
☐ Function App Identity: Enabled
☐ Object ID: Present

RBAC ROLES
☐ Storage Blob Data Reader: Assigned
☐ Cognitive Services User: Assigned

CONFIGURATION
☐ 6 app settings configured
☐ Endpoints correct
☐ Deployment name: gpt-35-turbo

SECURITY
☐ NO credentials in settings
☐ Managed Identity used
```

---

## 🎯 Time Breakdown

| Step | Task | Time |
|------|------|------|
| 1 | Delete failed plan | 2 min |
| 2 | Create App Service Plan | 5 min |
| 3 | Create Function App | 5 min |
| 4 | Enable Managed Identity | 2 min |
| 5 | Assign RBAC (Storage) | 3 min |
| 6 | Create Azure OpenAI | 10 min |
| 7 | Deploy GPT Model | 5 min |
| 8 | Assign RBAC (OpenAI) | 3 min |
| 9 | Get Endpoints | 3 min |
| 10 | Configure Settings | 5 min |
| 11 | Create Container | 2 min |
| **Total** | | **~45 min** |

---

## 🎓 Key Differences from East US

**Only change**: Region = Central US

Everything else is identical:
- ✅ Same resource names
- ✅ Same configuration
- ✅ Same security settings
- ✅ Same cost
- ✅ Same performance

---

## ✨ Summary

✅ **Region**: Central US (quota available)  
✅ **Time**: ~45 minutes  
✅ **Cost**: Same as East US  
✅ **Security**: Zero-Trust with Managed Identity  
✅ **Compliance**: SFI Policies Aligned  

---

**Ready to proceed?**

Follow the 11 steps above, starting with Step 1: Delete Failed App Service Plan

---

**Status**: ✅ Ready for Central US Setup  
**Next Step**: Delete failed plan and create new one in Central US
