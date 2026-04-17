# Azure Portal Manual Setup Guide - Planning Intelligence Copilot

**Status**: Storage Account ✅ Complete  
**Next**: Function App + Azure OpenAI Setup  
**Security Model**: Zero-Trust with Managed Identity  
**Compliance**: SFI Policies

---

## ✅ Storage Account Configuration - VERIFIED

Your storage account configuration is **perfect** and fully compliant:

### What You Did Right ✅
- ✅ **Secure transfer enabled** - All data encrypted in transit
- ✅ **Blob anonymous access disabled** - No public access
- ✅ **Storage account key access disabled** - No key-based access
- ✅ **Microsoft Entra authorization enabled** - Uses Azure AD (Managed Identity)
- ✅ **TLS 1.2 minimum** - Strong encryption
- ✅ **Public network access disabled** - Private access only
- ✅ **Soft delete enabled** - Data recovery capability
- ✅ **Managed Identity for SMB enabled** - Zero-trust for file shares

### Security Summary
```
Storage Account: stgpicopilotdev
├─ Authentication: Microsoft Entra ID (Managed Identity) ✓
├─ Encryption: TLS 1.2+ ✓
├─ Access: Private network only ✓
├─ Keys: Disabled ✓
└─ Compliance: SFI Zero-Trust ✓
```

---

## 🚀 Step 1: Create App Service Plan (Azure Portal)

### 1.1 Navigate to App Service Plans

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"** in the search bar
3. Click **"Create"** or **"+ Create"**

### 1.2 Fill in Basic Information

**Basics Tab:**
- **Subscription**: CO+I GSC Supplier Management Preprod
- **Resource Group**: Rg-pi-copilot-dev
- **Name**: plan-pi-copilot-dev
- **Operating System**: Linux
- **Region**: East US
- **Sku and size**: 
  - Click **"Change size"**
  - Select **"B1"** (Basic tier)
  - Click **"Apply"**

### 1.3 Review and Create

1. Click **"Review + create"**
2. Verify all settings
3. Click **"Create"**
4. Wait for deployment (2-3 minutes)

**Expected Result:**
```
✓ App Service Plan created
  Name: plan-pi-copilot-dev
  Tier: Basic (B1)
  OS: Linux
```

---

## 🔧 Step 2: Create Function App (Azure Portal)

### 2.1 Navigate to Function Apps

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"Function App"** in the search bar
3. Click **"Create"** or **"+ Create"**

### 2.2 Fill in Basic Information

**Basics Tab:**
- **Subscription**: CO+I GSC Supplier Management Preprod
- **Resource Group**: Rg-pi-copilot-dev
- **Function App name**: func-pi-copilot-dev
- **Publish**: Code
- **Runtime stack**: Python
- **Version**: 3.9
- **Region**: East US

### 2.3 Configure Hosting

**Hosting Tab:**
- **Storage account**: stgpicopilotdev (select from dropdown)
- **Operating system**: Linux
- **Plan type**: App Service Plan
- **App Service Plan**: plan-pi-copilot-dev (select from dropdown)

### 2.4 Configure Networking

**Networking Tab:**
- **Enable network injection**: No (for now)
- Keep defaults

### 2.5 Configure Monitoring

**Monitoring Tab:**
- **Enable Application Insights**: Yes
- **Application Insights**: Create new
  - **Name**: appi-pi-copilot-dev
  - **Location**: East US

### 2.6 Review and Create

1. Click **"Review + create"**
2. Verify all settings
3. Click **"Create"**
4. Wait for deployment (3-5 minutes)

**Expected Result:**
```
✓ Function App created
  Name: func-pi-copilot-dev
  Runtime: Python 3.9
  Plan: plan-pi-copilot-dev
  Storage: stgpicopilotdev
```

---

## 🔐 Step 3: Enable Managed Identity (Azure Portal)

### 3.1 Navigate to Function App

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App

### 3.2 Enable System-Assigned Managed Identity

1. In the left menu, click **"Identity"**
2. Under **"System assigned"** tab:
   - Toggle **"Status"** to **"On"**
   - Click **"Save"**
3. Click **"Yes"** to confirm

**Expected Result:**
```
✓ System-assigned Managed Identity enabled
  Status: On
  Object ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 3.3 Copy the Object ID

1. Copy the **"Object ID"** (you'll need this for RBAC)
2. Save it somewhere safe

---

## 🔑 Step 4: Configure RBAC - Storage Blob Data Reader (Azure Portal)

### 4.1 Navigate to Storage Account

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account

### 4.2 Assign Role

1. In the left menu, click **"Access Control (IAM)"**
2. Click **"+ Add"** → **"Add role assignment"**

### 4.3 Fill in Role Assignment

**Add role assignment panel:**
- **Role**: Search for **"Storage Blob Data Reader"**
  - Click on it to select
- **Assign access to**: Azure AD user, group, or service principal
- **Select members**: 
  - Click **"+ Select members"**
  - Search for **"func-pi-copilot-dev"**
  - Click on it to select
  - Click **"Select"**

### 4.4 Review and Assign

1. Click **"Review + assign"**
2. Verify:
   - Role: Storage Blob Data Reader
   - Member: func-pi-copilot-dev
3. Click **"Assign"**

**Expected Result:**
```
✓ Role assignment created
  Role: Storage Blob Data Reader
  Assigned to: func-pi-copilot-dev
  Scope: stgpicopilotdev
```

---

## 🤖 Step 5: Create Azure OpenAI Resource (Azure Portal)

### 5.1 Navigate to Create Resource

1. Go to **Azure Portal** → https://portal.azure.com
2. Click **"+ Create a resource"**
3. Search for **"Azure OpenAI"**
4. Click on **"Azure OpenAI"** (by Microsoft)
5. Click **"Create"**

### 5.2 Fill in Basic Information

**Basics Tab:**
- **Subscription**: CO+I GSC Supplier Management Preprod
- **Resource Group**: Rg-pi-copilot-dev
- **Region**: East US (or available region)
- **Name**: openai-pi-copilot-dev
- **Pricing tier**: Standard S0

### 5.3 Configure Network

**Network Tab:**
- **Connectivity method**: Public endpoint
- **Firewall**: Disabled (for now, can be enabled later)

### 5.4 Review and Create

1. Click **"Review + create"**
2. Verify all settings
3. Click **"Create"**
4. Wait for deployment (5-10 minutes)

**Expected Result:**
```
✓ Azure OpenAI resource created
  Name: openai-pi-copilot-dev
  Region: East US
  Tier: Standard S0
```

---

## 🧠 Step 6: Deploy GPT Model (Azure Portal)

### 6.1 Navigate to Azure OpenAI Studio

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. Click **"Go to Azure OpenAI Studio"** (or click **"Deployments"** in left menu)

### 6.2 Create Model Deployment

1. In Azure OpenAI Studio:
   - Click **"Deployments"** (left menu)
   - Click **"+ Create new deployment"**

2. **Deployment configuration:**
   - **Select a model**: gpt-3.5-turbo
   - **Model version**: 0613 (or latest available)
   - **Deployment name**: gpt-35-turbo
   - **Tokens per minute rate limit**: 90,000 (or default)

3. Click **"Create"**

**Expected Result:**
```
✓ Model deployment created
  Model: gpt-3.5-turbo
  Deployment name: gpt-35-turbo
  Status: Succeeded
```

---

## 🔐 Step 7: Configure RBAC - Cognitive Services User (Azure Portal)

### 7.1 Navigate to Azure OpenAI Resource

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource

### 7.2 Assign Role

1. In the left menu, click **"Access Control (IAM)"**
2. Click **"+ Add"** → **"Add role assignment"**

### 7.3 Fill in Role Assignment

**Add role assignment panel:**
- **Role**: Search for **"Cognitive Services User"**
  - Click on it to select
- **Assign access to**: Azure AD user, group, or service principal
- **Select members**: 
  - Click **"+ Select members"**
  - Search for **"func-pi-copilot-dev"**
  - Click on it to select
  - Click **"Select"**

### 7.4 Review and Assign

1. Click **"Review + assign"**
2. Verify:
   - Role: Cognitive Services User
   - Member: func-pi-copilot-dev
3. Click **"Assign"**

**Expected Result:**
```
✓ Role assignment created
  Role: Cognitive Services User
  Assigned to: func-pi-copilot-dev
  Scope: openai-pi-copilot-dev
```

---

## 📝 Step 8: Get Resource Endpoints (Azure Portal)

### 8.1 Get Blob Storage Endpoint

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account
4. In the left menu, click **"Endpoints"**
5. Copy the **"Blob service"** endpoint
   - Example: `https://stgpicopilotdev.blob.core.windows.net/`

### 8.2 Get Azure OpenAI Endpoint

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. In the left menu, click **"Keys and Endpoint"**
5. Copy the **"Endpoint"**
   - Example: `https://openai-pi-copilot-dev.openai.azure.com/`

### 8.3 Save Endpoints

Save these endpoints (you'll need them for Function App configuration):
```
AZURE_STORAGE_BLOB_ENDPOINT=https://stgpicopilotdev.blob.core.windows.net/
AZURE_OPENAI_ENDPOINT=https://openai-pi-copilot-dev.openai.azure.com/
```

---

## ⚙️ Step 9: Configure Function App Settings (Azure Portal)

### 9.1 Navigate to Function App

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App

### 9.2 Add Application Settings

1. In the left menu, click **"Configuration"**
2. Click **"+ New application setting"** for each setting:

**Add these settings:**

| Name | Value |
|------|-------|
| AZURE_STORAGE_ACCOUNT_NAME | stgpicopilotdev |
| AZURE_STORAGE_CONTAINER_NAME | planning-data |
| AZURE_STORAGE_BLOB_ENDPOINT | https://stgpicopilotdev.blob.core.windows.net/ |
| AZURE_OPENAI_ENDPOINT | https://openai-pi-copilot-dev.openai.azure.com/ |
| AZURE_OPENAI_DEPLOYMENT_NAME | gpt-35-turbo |
| AZURE_OPENAI_API_VERSION | 2023-05-15 |

### 9.3 Save Settings

1. After adding all settings, click **"Save"**
2. Click **"Continue"** when prompted to restart

**Expected Result:**
```
✓ Application settings configured
  6 settings added
  Function App restarted
```

---

## 📦 Step 10: Create Blob Container (Azure Portal)

### 10.1 Navigate to Storage Account

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account

### 10.2 Create Container

1. In the left menu, click **"Containers"**
2. Click **"+ Container"**

**Container details:**
- **Name**: planning-data
- **Public access level**: Private (no anonymous access)

3. Click **"Create"**

**Expected Result:**
```
✓ Container created
  Name: planning-data
  Access level: Private
```

---

## 🧪 Step 11: Verify Managed Identity Access (Azure Portal)

### 11.1 Check Function App Identity

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App
4. In the left menu, click **"Identity"**

**Verify:**
- ✓ System assigned: On
- ✓ Object ID: Present
- ✓ Tenant ID: Present

### 11.2 Check RBAC Assignments

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"stgpicopilotdev"**
3. Click on the Storage Account
4. In the left menu, click **"Access Control (IAM)"**

**Verify:**
- ✓ func-pi-copilot-dev has "Storage Blob Data Reader" role

### 11.3 Check Azure OpenAI RBAC

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"openai-pi-copilot-dev"**
3. Click on the Azure OpenAI resource
4. In the left menu, click **"Access Control (IAM)"**

**Verify:**
- ✓ func-pi-copilot-dev has "Cognitive Services User" role

---

## ✅ Verification Checklist

### Infrastructure
- [ ] App Service Plan created: plan-pi-copilot-dev
- [ ] Function App created: func-pi-copilot-dev
- [ ] Managed Identity enabled on Function App
- [ ] Azure OpenAI resource created: openai-pi-copilot-dev
- [ ] GPT-3.5-turbo model deployed

### RBAC & Security
- [ ] Storage Blob Data Reader role assigned to Function App
- [ ] Cognitive Services User role assigned to Function App
- [ ] NO access keys used
- [ ] NO connection strings used
- [ ] Managed Identity used for all access

### Configuration
- [ ] Blob Storage endpoint configured
- [ ] Azure OpenAI endpoint configured
- [ ] Deployment name configured (gpt-35-turbo)
- [ ] API version configured (2023-05-15)
- [ ] Container created: planning-data

### Security
- [ ] Storage account: Secure transfer enabled
- [ ] Storage account: Key access disabled
- [ ] Storage account: Microsoft Entra authorization enabled
- [ ] Azure OpenAI: Public endpoint (can restrict later)
- [ ] Function App: Managed Identity enabled

---

## 🎯 Next Steps

### Step 12: Deploy Backend Code

Once all Azure resources are configured:

1. Update backend code to use DefaultAzureCredential:
   - `blob_service.py` - Use Managed Identity
   - `llm_service.py` - Use Managed Identity
   - `requirements.txt` - Add azure-identity

2. Deploy Function App:
   ```bash
   cd planning_intelligence
   func azure functionapp publish func-pi-copilot-dev --build remote
   ```

3. Verify deployment:
   ```bash
   az functionapp log tail --name func-pi-copilot-dev --resource-group Rg-pi-copilot-dev
   ```

### Step 13: Test Managed Identity Access

1. Test Blob Storage access
2. Test Azure OpenAI access
3. Verify no credentials are used

### Step 14: Deploy Frontend

1. Build React app
2. Deploy to App Service
3. Configure API URL

### Step 15: End-to-End Testing

1. Test dashboard endpoint
2. Test explain endpoint
3. Test Copilot responses
4. Validate with live data

---

## 🔒 Security Summary

### What's Implemented ✅
- **Zero-Trust**: Managed Identity for all resource access
- **No Credentials**: No access keys, connection strings, or API keys
- **RBAC**: Least-privilege role assignments
- **Encryption**: TLS 1.2+ for all data in transit
- **Audit Trail**: All access logged via Azure AD

### What's NOT Used ❌
- ❌ Access keys
- ❌ Connection strings
- ❌ API keys
- ❌ System credentials
- ❌ User credentials

---

## 📞 Troubleshooting

### Issue: "Managed Identity not found"
- Go to Function App → Identity
- Verify "System assigned" is "On"
- If not, toggle it on and save

### Issue: "Access denied to Blob Storage"
- Go to Storage Account → Access Control (IAM)
- Verify func-pi-copilot-dev has "Storage Blob Data Reader" role
- If not, add the role assignment

### Issue: "Access denied to Azure OpenAI"
- Go to Azure OpenAI → Access Control (IAM)
- Verify func-pi-copilot-dev has "Cognitive Services User" role
- If not, add the role assignment

### Issue: "Function App won't start"
- Go to Function App → Configuration
- Verify all settings are correct
- Check Application Insights logs

---

## 📊 Resource Summary

```
Resource Group: Rg-pi-copilot-dev
├─ Storage Account: stgpicopilotdev
│  ├─ Container: planning-data
│  └─ Security: Managed Identity + RBAC
├─ App Service Plan: plan-pi-copilot-dev
│  └─ Tier: Basic (B1)
├─ Function App: func-pi-copilot-dev
│  ├─ Runtime: Python 3.9
│  ├─ Managed Identity: Enabled
│  └─ RBAC: Storage Blob Data Reader
├─ Azure OpenAI: openai-pi-copilot-dev
│  ├─ Model: gpt-3.5-turbo
│  ├─ Deployment: gpt-35-turbo
│  └─ RBAC: Cognitive Services User
└─ Application Insights: appi-pi-copilot-dev
```

---

**Status**: ✅ Ready for Backend Code Deployment  
**Security Model**: Zero-Trust with Managed Identity  
**Compliance**: ✅ SFI Policies Aligned  
**Next Step**: Deploy backend code with DefaultAzureCredential
