# Azure Setup Visual Checklist - Planning Intelligence Copilot

**Status**: Storage Account ✅ | Function App 🔄 | Azure OpenAI 🔄  
**Time**: ~45 minutes for all steps

---

## 📋 Quick Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Azure Portal Setup                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ DONE                                                    │
│  └─ Storage Account: stgpicopilotdev                        │
│     └─ Container: planning-data (to create)                 │
│                                                              │
│  🔄 TODO                                                    │
│  ├─ App Service Plan: plan-pi-copilot-dev                   │
│  ├─ Function App: func-pi-copilot-dev                       │
│  ├─ Managed Identity: Enable on Function App                │
│  ├─ RBAC: Storage Blob Data Reader                          │
│  ├─ Azure OpenAI: openai-pi-copilot-dev                     │
│  ├─ Model: Deploy gpt-3.5-turbo                             │
│  ├─ RBAC: Cognitive Services User                           │
│  └─ Configuration: Add app settings                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Step-by-Step Checklist

### STEP 1: Create App Service Plan ⏱️ 5 min

**Location**: Azure Portal → App Service Plans → Create

```
☐ Subscription: CO+I GSC Supplier Management Preprod
☐ Resource Group: Rg-pi-copilot-dev
☐ Name: plan-pi-copilot-dev
☐ Operating System: Linux
☐ Region: East US
☐ Sku: B1 (Basic)
☐ Click "Create"
☐ Wait for deployment (2-3 min)
```

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

### STEP 2: Create Function App ⏱️ 5 min

**Location**: Azure Portal → Function App → Create

```
☐ Subscription: CO+I GSC Supplier Management Preprod
☐ Resource Group: Rg-pi-copilot-dev
☐ Function App name: func-pi-copilot-dev
☐ Publish: Code
☐ Runtime stack: Python
☐ Version: 3.9
☐ Region: East US
☐ Storage account: stgpicopilotdev
☐ Plan type: App Service Plan
☐ App Service Plan: plan-pi-copilot-dev
☐ Enable Application Insights: Yes
☐ Application Insights name: appi-pi-copilot-dev
☐ Click "Create"
☐ Wait for deployment (3-5 min)
```

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

### STEP 3: Enable Managed Identity ⏱️ 2 min

**Location**: Azure Portal → func-pi-copilot-dev → Identity

```
☐ Go to Function App: func-pi-copilot-dev
☐ Click "Identity" (left menu)
☐ System assigned tab
☐ Toggle "Status" to "On"
☐ Click "Save"
☐ Click "Yes" to confirm
☐ Copy "Object ID" (save for later)
```

**Expected**: 
```
Status: On
Object ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### STEP 4: Assign RBAC - Storage Blob Data Reader ⏱️ 3 min

**Location**: Azure Portal → stgpicopilotdev → Access Control (IAM)

```
☐ Go to Storage Account: stgpicopilotdev
☐ Click "Access Control (IAM)" (left menu)
☐ Click "+ Add" → "Add role assignment"
☐ Role: Search "Storage Blob Data Reader"
☐ Assign access to: Azure AD user, group, or service principal
☐ Select members: Search "func-pi-copilot-dev"
☐ Click "Select"
☐ Click "Review + assign"
☐ Click "Assign"
```

**Expected**: 
```
Role: Storage Blob Data Reader
Assigned to: func-pi-copilot-dev
Scope: stgpicopilotdev
```

---

### STEP 5: Create Azure OpenAI Resource ⏱️ 10 min

**Location**: Azure Portal → Create a resource → Azure OpenAI

```
☐ Click "+ Create a resource"
☐ Search "Azure OpenAI"
☐ Click "Azure OpenAI" (by Microsoft)
☐ Click "Create"
☐ Subscription: CO+I GSC Supplier Management Preprod
☐ Resource Group: Rg-pi-copilot-dev
☐ Region: East US
☐ Name: openai-pi-copilot-dev
☐ Pricing tier: Standard S0
☐ Connectivity method: Public endpoint
☐ Firewall: Disabled
☐ Click "Review + create"
☐ Click "Create"
☐ Wait for deployment (5-10 min)
```

**Expected**: Green checkmark ✓ "Deployment succeeded"

---

### STEP 6: Deploy GPT Model ⏱️ 5 min

**Location**: Azure Portal → openai-pi-copilot-dev → Deployments

```
☐ Go to Azure OpenAI: openai-pi-copilot-dev
☐ Click "Go to Azure OpenAI Studio" (or Deployments in left menu)
☐ Click "Deployments" (left menu)
☐ Click "+ Create new deployment"
☐ Select a model: gpt-3.5-turbo
☐ Model version: 0613 (or latest)
☐ Deployment name: gpt-35-turbo
☐ Tokens per minute: 90,000 (or default)
☐ Click "Create"
☐ Wait for deployment (2-3 min)
```

**Expected**: 
```
Model: gpt-3.5-turbo
Deployment name: gpt-35-turbo
Status: Succeeded
```

---

### STEP 7: Assign RBAC - Cognitive Services User ⏱️ 3 min

**Location**: Azure Portal → openai-pi-copilot-dev → Access Control (IAM)

```
☐ Go to Azure OpenAI: openai-pi-copilot-dev
☐ Click "Access Control (IAM)" (left menu)
☐ Click "+ Add" → "Add role assignment"
☐ Role: Search "Cognitive Services User"
☐ Assign access to: Azure AD user, group, or service principal
☐ Select members: Search "func-pi-copilot-dev"
☐ Click "Select"
☐ Click "Review + assign"
☐ Click "Assign"
```

**Expected**: 
```
Role: Cognitive Services User
Assigned to: func-pi-copilot-dev
Scope: openai-pi-copilot-dev
```

---

### STEP 8: Get Resource Endpoints ⏱️ 3 min

**Location**: Azure Portal → Resources → Endpoints

```
☐ Go to Storage Account: stgpicopilotdev
☐ Click "Endpoints" (left menu)
☐ Copy "Blob service" endpoint
   Save: AZURE_STORAGE_BLOB_ENDPOINT=https://stgpicopilotdev.blob.core.windows.net/

☐ Go to Azure OpenAI: openai-pi-copilot-dev
☐ Click "Keys and Endpoint" (left menu)
☐ Copy "Endpoint"
   Save: AZURE_OPENAI_ENDPOINT=https://openai-pi-copilot-dev.openai.azure.com/
```

**Expected**: Two endpoints saved

---

### STEP 9: Configure Function App Settings ⏱️ 5 min

**Location**: Azure Portal → func-pi-copilot-dev → Configuration

```
☐ Go to Function App: func-pi-copilot-dev
☐ Click "Configuration" (left menu)
☐ Click "+ New application setting" for each:

   ☐ AZURE_STORAGE_ACCOUNT_NAME = stgpicopilotdev
   ☐ AZURE_STORAGE_CONTAINER_NAME = planning-data
   ☐ AZURE_STORAGE_BLOB_ENDPOINT = https://stgpicopilotdev.blob.core.windows.net/
   ☐ AZURE_OPENAI_ENDPOINT = https://openai-pi-copilot-dev.openai.azure.com/
   ☐ AZURE_OPENAI_DEPLOYMENT_NAME = gpt-35-turbo
   ☐ AZURE_OPENAI_API_VERSION = 2023-05-15

☐ Click "Save"
☐ Click "Continue" (to restart)
```

**Expected**: All 6 settings added and saved

---

### STEP 10: Create Blob Container ⏱️ 2 min

**Location**: Azure Portal → stgpicopilotdev → Containers

```
☐ Go to Storage Account: stgpicopilotdev
☐ Click "Containers" (left menu)
☐ Click "+ Container"
☐ Name: planning-data
☐ Public access level: Private
☐ Click "Create"
```

**Expected**: Container "planning-data" created

---

### STEP 11: Verify Everything ⏱️ 5 min

**Verification Checklist:**

```
INFRASTRUCTURE
☐ App Service Plan: plan-pi-copilot-dev (exists)
☐ Function App: func-pi-copilot-dev (exists)
☐ Azure OpenAI: openai-pi-copilot-dev (exists)
☐ Container: planning-data (exists)

MANAGED IDENTITY
☐ Function App Identity: Enabled
☐ Object ID: Present
☐ Tenant ID: Present

RBAC ROLES
☐ Storage Blob Data Reader: Assigned to func-pi-copilot-dev
☐ Cognitive Services User: Assigned to func-pi-copilot-dev

CONFIGURATION
☐ 6 app settings configured
☐ Endpoints correct
☐ Deployment name: gpt-35-turbo

SECURITY
☐ Storage: Secure transfer enabled
☐ Storage: Key access disabled
☐ Storage: Microsoft Entra authorization enabled
☐ NO credentials in settings
```

---

## 🎯 Time Breakdown

| Step | Task | Time |
|------|------|------|
| 1 | Create App Service Plan | 5 min |
| 2 | Create Function App | 5 min |
| 3 | Enable Managed Identity | 2 min |
| 4 | Assign RBAC (Storage) | 3 min |
| 5 | Create Azure OpenAI | 10 min |
| 6 | Deploy GPT Model | 5 min |
| 7 | Assign RBAC (OpenAI) | 3 min |
| 8 | Get Endpoints | 3 min |
| 9 | Configure Settings | 5 min |
| 10 | Create Container | 2 min |
| 11 | Verify | 5 min |
| **Total** | | **~48 min** |

---

## ✅ Final Verification

After completing all steps, verify:

```bash
# Check Function App exists
az functionapp show --name func-pi-copilot-dev --resource-group Rg-pi-copilot-dev

# Check Managed Identity
az functionapp identity show --name func-pi-copilot-dev --resource-group Rg-pi-copilot-dev

# Check RBAC assignments
az role assignment list --assignee <object-id>

# Check settings
az functionapp config appsettings list --name func-pi-copilot-dev --resource-group Rg-pi-copilot-dev
```

---

## 🎓 Key Points

### ✅ What You're Doing Right
- Using Managed Identity (zero-trust)
- No access keys or credentials
- RBAC for least-privilege access
- Secure storage configuration
- Microsoft Entra authorization

### ❌ What NOT to Do
- ❌ Don't use access keys
- ❌ Don't use connection strings
- ❌ Don't store credentials in code
- ❌ Don't use system/user credentials
- ❌ Don't enable public access

---

## 📞 Need Help?

**If stuck on any step:**
1. Check the detailed guide: `AZURE_PORTAL_MANUAL_SETUP_GUIDE.md`
2. Verify all prerequisites are met
3. Check Azure Portal notifications for errors
4. Review the troubleshooting section

---

**Status**: Ready to Start Azure Setup  
**Estimated Time**: ~48 minutes  
**Compliance**: ✅ SFI Zero-Trust  
**Next**: Follow the checklist above step-by-step
