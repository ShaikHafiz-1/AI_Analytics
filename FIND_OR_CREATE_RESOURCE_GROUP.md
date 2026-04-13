# Find or Create Azure Resource Group

## Problem
```
(ResourceGroupNotFound) Resource group 'rg-planning-intelligence' could not be found.
```

This means the resource group doesn't exist in your Azure subscription.

---

## SOLUTION 1: Find Existing Resource Groups

First, check what resource groups you already have:

```powershell
# List all resource groups
az group list --output table
```

**Expected output**:
```
Name                                    Location       Status
--------------------------------------  ---------------  ---------
rg-scp-mcp-dev                          eastus         Succeeded
rg-data-analytics                       eastus2        Succeeded
rg-planning-intelligence                eastus         Succeeded
```

**Look for one of these**:
- `rg-scp-mcp-dev` (most likely - from previous setup)
- `rg-planning-intelligence` (if already created)
- `rg-data-analytics` (if using existing)
- Any other resource group you have access to

---

## SOLUTION 2: Use Existing Resource Group

If you found an existing resource group, use it instead:

```powershell
# Use existing resource group
$resourceGroup = "rg-scp-mcp-dev"  # Replace with your actual resource group name

# Deploy frontend
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name pi-planning-copilot `
  --src "build.zip"
```

---

## SOLUTION 3: Create New Resource Group

If you don't have a resource group, create one:

```powershell
# Create new resource group
az group create `
  --name rg-planning-intelligence `
  --location eastus

# Verify it was created
az group show --name rg-planning-intelligence
```

**Expected output**:
```
{
  "id": "/subscriptions/.../resourceGroups/rg-planning-intelligence",
  "location": "eastus",
  "managedBy": null,
  "name": "rg-planning-intelligence",
  "properties": {
    "provisioningState": "Succeeded"
  },
  "tags": {}
}
```

---

## SOLUTION 4: Create All Azure Resources

If you need to create everything from scratch:

```powershell
# Set variables
$resourceGroup = "rg-planning-intelligence"
$location = "eastus"
$storageAccount = "stplanningintel"
$functionApp = "pi-planning-intelligence"
$appService = "pi-planning-copilot"
$appServicePlan = "asp-planning-intelligence"

# 1. Create resource group
Write-Host "Creating resource group..."
az group create --name $resourceGroup --location $location

# 2. Create storage account (for blob data)
Write-Host "Creating storage account..."
az storage account create `
  --name $storageAccount `
  --resource-group $resourceGroup `
  --location $location `
  --sku Standard_LRS

# 3. Create app service plan
Write-Host "Creating app service plan..."
az appservice plan create `
  --name $appServicePlan `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux

# 4. Create function app (backend)
Write-Host "Creating function app..."
az functionapp create `
  --resource-group $resourceGroup `
  --consumption-plan-location $location `
  --runtime python `
  --runtime-version 3.9 `
  --functions-version 4 `
  --name $functionApp `
  --storage-account $storageAccount

# 5. Create app service (frontend)
Write-Host "Creating app service..."
az webapp create `
  --name $appService `
  --resource-group $resourceGroup `
  --plan $appServicePlan

Write-Host "✓ All resources created successfully!"
```

---

## QUICK FIX: Use Your Existing Resource Group

Most likely, you already have a resource group. Find it:

```powershell
# List all resource groups
az group list --query "[].name" -o tsv
```

Pick one and use it:

```powershell
$resourceGroup = "rg-scp-mcp-dev"  # Replace with your actual group

# Deploy frontend
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name pi-planning-copilot `
  --src "build.zip"
```

---

## STEP-BY-STEP: Deploy with Correct Resource Group

### Step 1: Find Your Resource Group
```powershell
az group list --query "[].name" -o tsv
```

Copy the name (e.g., `rg-scp-mcp-dev`)

### Step 2: Check if App Service Exists
```powershell
$resourceGroup = "rg-scp-mcp-dev"  # Your resource group

# List all app services in this group
az webapp list --resource-group $resourceGroup --query "[].name" -o tsv
```

### Step 3: Create App Service if Needed
```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"
$appServicePlan = "asp-planning-intelligence"

# Create app service plan
az appservice plan create `
  --name $appServicePlan `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux

# Create app service
az webapp create `
  --name $appService `
  --resource-group $resourceGroup `
  --plan $appServicePlan
```

### Step 4: Deploy Frontend
```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Build
cd frontend
npm run build

# Create zip
Compress-Archive -Path "build\*" -DestinationPath "build.zip" -Force

# Deploy
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $appService `
  --src "build.zip"
```

---

## VERIFY DEPLOYMENT

```powershell
$resourceGroup = "rg-scp-mcp-dev"
$appService = "pi-planning-copilot"

# Get app service URL
az webapp show `
  --name $appService `
  --resource-group $resourceGroup `
  --query defaultHostName `
  -o tsv
```

Should return: `pi-planning-copilot.azurewebsites.net`

Open in browser: `https://pi-planning-copilot.azurewebsites.net`

---

## TROUBLESHOOTING

### Error: "App service not found"
```powershell
# Create it
az webapp create `
  --name pi-planning-copilot `
  --resource-group rg-scp-mcp-dev `
  --plan asp-planning-intelligence
```

### Error: "App service plan not found"
```powershell
# Create it
az appservice plan create `
  --name asp-planning-intelligence `
  --resource-group rg-scp-mcp-dev `
  --sku B1 `
  --is-linux
```

### Error: "Subscription not found"
```powershell
# Check your subscription
az account show

# If wrong subscription, switch
az account set --subscription "<subscription-id>"
```

---

## QUICK REFERENCE

**Find resource group**:
```powershell
az group list --query "[].name" -o tsv
```

**Create resource group**:
```powershell
az group create --name rg-planning-intelligence --location eastus
```

**Deploy frontend**:
```powershell
az webapp deployment source config-zip `
  --resource-group <YOUR_RESOURCE_GROUP> `
  --name pi-planning-copilot `
  --src "build.zip"
```

**Get frontend URL**:
```powershell
az webapp show --name pi-planning-copilot --resource-group <YOUR_RESOURCE_GROUP> --query defaultHostName -o tsv
```

