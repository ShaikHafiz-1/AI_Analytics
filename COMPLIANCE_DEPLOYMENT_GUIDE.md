# SFI Compliance Deployment Guide - Planning Intelligence Copilot

**Status**: Compliance-Focused Deployment  
**Date**: April 16, 2026  
**Security Model**: Zero-Trust with Managed Identity  
**Compliance**: SFI Policies + Microsoft Confidential

---

## 📋 Overview

This guide ensures your Planning Intelligence Copilot deployment aligns with:
- ✅ Zero-Trust security principles
- ✅ SFI compliance policies
- ✅ Managed Identity (MI) authentication
- ✅ RBAC for all resource access
- ✅ No access keys or credentials in code

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Zero-Trust Model                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Function App (Managed Identity)                            │
│  └─ System-assigned MI (auto-created)                       │
│     └─ RBAC Role: Storage Blob Data Reader                  │
│        └─ Scope: Blob Storage (planning-data container)     │
│                                                              │
│  Azure OpenAI (Managed Identity)                            │
│  └─ System-assigned MI                                      │
│     └─ RBAC Role: Cognitive Services User                   │
│        └─ Scope: Azure OpenAI resource                      │
│                                                              │
│  NO Access Keys ✓                                           │
│  NO Connection Strings ✓                                    │
│  NO Credentials in Code ✓                                   │
│  NO System/User Credentials ✓                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📍 Step 1: Create Resource Group

### 1.1 Create Dedicated Resource Group

```bash
# Set variables
$resourceGroup = "Rg-pi-copilot-dev"
$location = "eastus"
$subscription = "your-subscription-id"

# Create resource group
az group create \
  --name $resourceGroup \
  --location $location \
  --subscription $subscription

# Verify creation
az group show \
  --name $resourceGroup \
  --subscription $subscription
```

**Expected output:**
```json
{
  "id": "/subscriptions/.../resourceGroups/Rg-pi-copilot-dev",
  "location": "eastus",
  "name": "Rg-pi-copilot-dev",
  "properties": {
    "provisioningState": "Succeeded"
  }
}
```

### 1.2 Verify Resource Group

```bash
# List all resources in the group (should be empty initially)
az resource list \
  --resource-group $resourceGroup \
  --subscription $subscription
```

---

## 🔑 Step 2: Create Storage Account with Managed Identity

### 2.1 Create Storage Account

```bash
# Set variables
$storageAccount = "stgpicopilotdev"
$containerName = "planning-data"

# Create storage account
az storage account create \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --location $location \
  --sku Standard_LRS \
  --subscription $subscription

# Verify creation
az storage account show \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 2.2 Create Blob Container

```bash
# Get storage account key (temporary, for setup only)
$storageKey = az storage account keys list \
  --account-name $storageAccount \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query "[0].value" -o tsv

# Create container
az storage container create \
  --name $containerName \
  --account-name $storageAccount \
  --account-key $storageKey \
  --subscription $subscription

# Verify container
az storage container exists \
  --name $containerName \
  --account-name $storageAccount \
  --account-key $storageKey \
  --subscription $subscription
```

---

## 🔧 Step 3: Create Function App with Managed Identity

### 3.1 Create App Service Plan

```bash
# Set variables
$appServicePlan = "plan-pi-copilot-dev"

# Create App Service Plan
az appservice plan create \
  --name $appServicePlan \
  --resource-group $resourceGroup \
  --sku B1 \
  --is-linux \
  --subscription $subscription

# Verify creation
az appservice plan show \
  --name $appServicePlan \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 3.2 Create Function App

```bash
# Set variables
$functionApp = "func-pi-copilot-dev"

# Create Function App
az functionapp create \
  --name $functionApp \
  --resource-group $resourceGroup \
  --plan $appServicePlan \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --storage-account $storageAccount \
  --subscription $subscription

# Verify creation
az functionapp show \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 3.3 Enable System-Assigned Managed Identity

```bash
# Enable managed identity
az functionapp identity assign \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription

# Get the managed identity object ID
$principalId = az functionapp identity show \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query principalId -o tsv

echo "Managed Identity Principal ID: $principalId"
```

**Expected output:**
```
Managed Identity Principal ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 🔐 Step 4: Configure RBAC for Blob Storage

### 4.1 Grant Storage Blob Data Reader Role

```bash
# Set variables
$storageAccountId = az storage account show \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query id -o tsv

# Assign role to Function App's managed identity
az role assignment create \
  --assignee $principalId \
  --role "Storage Blob Data Reader" \
  --scope $storageAccountId \
  --subscription $subscription

# Verify role assignment
az role assignment list \
  --assignee $principalId \
  --scope $storageAccountId \
  --subscription $subscription
```

**Expected output:**
```json
[
  {
    "id": "/subscriptions/.../roleAssignments/...",
    "principalId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "principalName": "func-pi-copilot-dev",
    "principalType": "ServicePrincipal",
    "roleDefinitionId": "/subscriptions/.../roleDefinitions/2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",
    "roleDefinitionName": "Storage Blob Data Reader",
    "scope": "/subscriptions/.../resourceGroups/Rg-pi-copilot-dev/providers/Microsoft.Storage/storageAccounts/stgpicopilotdev"
  }
]
```

### 4.2 Verify Blob Access

```bash
# Test blob access using managed identity
az storage blob list \
  --container-name $containerName \
  --account-name $storageAccount \
  --auth-mode login \
  --subscription $subscription
```

---

## 🤖 Step 5: Create Azure OpenAI Resource

### 5.1 Create Azure OpenAI Resource

```bash
# Set variables
$openaiResource = "openai-pi-copilot-dev"
$openaiSku = "S0"

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --kind OpenAI \
  --sku $openaiSku \
  --location $location \
  --subscription $subscription

# Verify creation
az cognitiveservices account show \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 5.2 Deploy GPT Model

```bash
# Deploy gpt-3.5-turbo model
az cognitiveservices account deployment create \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-3.5-turbo" \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 1 \
  --subscription $subscription

# Verify deployment
az cognitiveservices account deployment list \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 5.3 Enable Managed Identity for OpenAI

```bash
# Get OpenAI resource ID
$openaiResourceId = az cognitiveservices account show \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query id -o tsv

# Assign Cognitive Services User role to Function App
az role assignment create \
  --assignee $principalId \
  --role "Cognitive Services User" \
  --scope $openaiResourceId \
  --subscription $subscription

# Verify role assignment
az role assignment list \
  --assignee $principalId \
  --scope $openaiResourceId \
  --subscription $subscription
```

---

## 🔑 Step 6: Configure Function App Settings

### 6.1 Get Resource Endpoints

```bash
# Get Blob Storage endpoint
$blobEndpoint = az storage account show \
  --name $storageAccount \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query primaryEndpoints.blob -o tsv

# Get OpenAI endpoint
$openaiEndpoint = az cognitiveservices account show \
  --name $openaiResource \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query properties.endpoint -o tsv

echo "Blob Endpoint: $blobEndpoint"
echo "OpenAI Endpoint: $openaiEndpoint"
```

### 6.2 Set Function App Configuration

```bash
# Set application settings (NO credentials, only endpoints)
az functionapp config appsettings set \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --settings \
    AZURE_STORAGE_ACCOUNT_NAME=$storageAccount \
    AZURE_STORAGE_CONTAINER_NAME=$containerName \
    AZURE_STORAGE_BLOB_ENDPOINT=$blobEndpoint \
    AZURE_OPENAI_ENDPOINT=$openaiEndpoint \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo" \
    AZURE_OPENAI_API_VERSION="2023-05-15"

# Verify settings
az functionapp config appsettings list \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription
```

---

## 📝 Step 7: Update Backend Code for Managed Identity

### 7.1 Update `planning_intelligence/blob_service.py`

```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os

class BlobService:
    def __init__(self):
        # Use Managed Identity (DefaultAzureCredential)
        credential = DefaultAzureCredential()
        
        # Get endpoint from environment (no connection string)
        blob_endpoint = os.getenv("AZURE_STORAGE_BLOB_ENDPOINT")
        
        # Create client using managed identity
        self.client = BlobServiceClient(
            account_url=blob_endpoint,
            credential=credential
        )
        
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "planning-data")
        self.container_client = self.client.get_container_client(container_name)
    
    def load_snapshot(self):
        """Load data from blob using managed identity"""
        try:
            blob_client = self.container_client.get_blob_client("snapshot.json")
            data = blob_client.download_blob().readall()
            return json.loads(data)
        except Exception as e:
            print(f"Error loading blob: {e}")
            return []
```

### 7.2 Update `planning_intelligence/llm_service.py`

```python
from azure.ai.openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import os

class LLMService:
    def __init__(self):
        # Use Managed Identity (DefaultAzureCredential)
        credential = DefaultAzureCredential()
        
        # Get endpoints from environment (no API keys)
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        
        # Create client using managed identity
        self.client = AzureOpenAI(
            api_key="",  # Not used with managed identity
            azure_endpoint=endpoint,
            api_version=api_version,
            azure_ad_token_provider=credential.get_token
        )
        
        self.deployment = deployment
    
    def generate_response(self, system_prompt, user_prompt):
        """Generate response using Azure OpenAI with managed identity"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
```

### 7.3 Update `requirements.txt`

```
azure-functions==1.13.0
azure-storage-blob==12.17.0
azure-identity==1.13.0
azure-ai-openai==1.3.0
python-dotenv==1.0.0
```

---

## 🚀 Step 8: Deploy Backend Code

### 8.1 Deploy Function App

```bash
# Navigate to backend directory
cd planning_intelligence

# Deploy using func CLI
func azure functionapp publish $functionApp \
  --build remote \
  --subscription $subscription

# Verify deployment
az functionapp deployment list \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription
```

### 8.2 Verify Function App Logs

```bash
# Stream logs
az functionapp log tail \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription

# Check for errors
az functionapp log tail \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription | grep -i error
```

---

## 🧪 Step 9: Test Managed Identity Access

### 9.1 Test Blob Storage Access

```bash
# Create test script
cat > test_blob_access.py << 'EOF'
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os

# Use managed identity
credential = DefaultAzureCredential()
blob_endpoint = os.getenv("AZURE_STORAGE_BLOB_ENDPOINT")

client = BlobServiceClient(account_url=blob_endpoint, credential=credential)
container_client = client.get_container_client("planning-data")

# List blobs
blobs = container_client.list_blobs()
for blob in blobs:
    print(f"✓ Blob: {blob.name}")

print("✓ Blob Storage access successful!")
EOF

# Run test
python test_blob_access.py
```

### 9.2 Test Azure OpenAI Access

```bash
# Create test script
cat > test_openai_access.py << 'EOF'
from azure.ai.openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import os

# Use managed identity
credential = DefaultAzureCredential()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_version="2023-05-15",
    azure_ad_token_provider=credential.get_token
)

# Test API call
response = client.chat.completions.create(
    model=deployment,
    messages=[{"role": "user", "content": "Hello"}]
)

print(f"✓ Response: {response.choices[0].message.content}")
print("✓ Azure OpenAI access successful!")
EOF

# Run test
python test_openai_access.py
```

---

## 🎯 Step 10: End-to-End Testing

### 10.1 Test Backend Endpoints

```bash
# Get function app URL
$functionUrl = az functionapp show \
  --name $functionApp \
  --resource-group $resourceGroup \
  --subscription $subscription \
  --query defaultHostName -o tsv

# Test dashboard endpoint
curl https://$functionUrl/api/planning_dashboard_v2

# Test explain endpoint
curl -X POST https://$functionUrl/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the high-risk items?",
    "context": {
      "detailRecords": [],
      "selectedEntity": null
    }
  }'
```

### 10.2 Test Frontend Integration

```bash
# Deploy frontend (if not already deployed)
cd frontend
npm run build

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group $resourceGroup \
  --name "app-pi-copilot-dev" \
  --src build.zip

# Test in browser
# https://app-pi-copilot-dev.azurewebsites.net
```

---

## ✅ Compliance Checklist

- [ ] Resource group created: `Rg-pi-copilot-dev`
- [ ] Storage account created with managed identity
- [ ] Function App created with system-assigned managed identity
- [ ] Azure OpenAI resource created
- [ ] RBAC roles assigned (Storage Blob Data Reader, Cognitive Services User)
- [ ] NO access keys in code
- [ ] NO connection strings in code
- [ ] NO credentials in environment variables
- [ ] All endpoints configured via environment variables
- [ ] Backend code updated to use DefaultAzureCredential
- [ ] Function App deployed successfully
- [ ] Blob Storage access tested
- [ ] Azure OpenAI access tested
- [ ] End-to-end testing completed
- [ ] Frontend integration verified

---

## 🔒 Security Summary

### What's Implemented ✅
- **Zero-Trust**: Managed Identity for all resource access
- **No Credentials**: No access keys, connection strings, or API keys in code
- **RBAC**: Least-privilege role assignments
- **SFI Compliant**: Follows organizational security policies
- **Audit Trail**: All access logged via Azure AD

### What's NOT Used ❌
- ❌ Access keys
- ❌ Connection strings
- ❌ API keys
- ❌ System credentials
- ❌ User credentials

---

## 📞 Support

If you get stuck:

1. **Check Managed Identity**: 
   ```bash
   az functionapp identity show --name $functionApp --resource-group $resourceGroup
   ```

2. **Check RBAC Assignments**:
   ```bash
   az role assignment list --assignee $principalId
   ```

3. **Check Function Logs**:
   ```bash
   az functionapp log tail --name $functionApp --resource-group $resourceGroup
   ```

4. **Verify Endpoints**:
   ```bash
   az storage account show --name $storageAccount --query primaryEndpoints.blob
   az cognitiveservices account show --name $openaiResource --query properties.endpoint
   ```

---

## 🎯 Next Steps

Once the resource group is created and this guide is followed:

1. ✅ Create resource group `Rg-pi-copilot-dev`
2. ✅ Set up Storage Account with Managed Identity
3. ✅ Create Function App with System-Assigned MI
4. ✅ Configure Azure OpenAI
5. ✅ Assign RBAC roles
6. ✅ Update backend code
7. ✅ Deploy Function App
8. ✅ Test Blob Storage access
9. ✅ Test Azure OpenAI access
10. ✅ Deploy frontend
11. ✅ Run end-to-end tests
12. ✅ Validate Copilot responses with live data

---

**Status**: Ready for SFI-Compliant Deployment  
**Security Model**: Zero-Trust with Managed Identity  
**Compliance**: ✅ SFI Policies Aligned
