# Corrected Function App Setup - Flex Consumption Plan

**Issue**: You're on "Create Function App (Flex Consumption)" page  
**Solution**: Use System-assigned Managed Identity (not User-assigned)  
**Status**: Easy fix ✅

---

## 🔴 What You're Seeing

```
Create Function App (Flex Consumption)
├─ Host storage: stgpicopilotdev ✓
├─ Deployment storage: app-package-func-pi-copilot-dev-e5a4548 ✓
├─ Azure OpenAI: openai-pi-copilot-dev ✓
├─ Managed identity: [DROPDOWN]
│  ├─ System-assigned managed identity ← SELECT THIS
│  ├─ User-assigned managed identity (grayed out)
│  └─ Error: "You don't have permission to create user-assigned..."
└─ [Review + create] button
```

---

## ✅ Fix: Select System-Assigned Managed Identity

### Step 1: Click the Managed Identity Dropdown

1. Look for **"Managed identity"** section
2. Click the dropdown that says **"System-assigned managed identity"**
3. It should already be selected (blue highlight)

### Step 2: Verify Selection

**You should see:**
```
✓ System-assigned managed identity (SELECTED)
  Enable (Not enough permissions)
```

**This is correct!** The "Not enough permissions" message is just informational - you don't need to enable it here.

### Step 3: Click "Review + create"

1. Scroll down
2. Click **"Review + create"** button (blue button)
3. Review all settings
4. Click **"Create"**

---

## 📋 What Should Be Filled In

**Before clicking "Review + create", verify:**

```
Resource
├─ Host storage (Azure WebJobs Storage): stgpicopilotdev ✓
├─ Deployment storage: app-package-func-pi-copilot-dev-e5a4548 ✓
├─ Azure OpenAI: openai-pi-copilot-dev ✓
├─ Azure AI Search: (optional, can be empty)
├─ Application Insights: func-pi-copilot-dev ✓
└─ Managed identity: System-assigned managed identity ✓

Authentication type
├─ Host storage: Managed identity ✓
├─ Deployment storage: Managed identity ✓
├─ Azure OpenAI: Managed identity ✓
└─ Azure AI Search: (if used) Managed identity ✓

Minimum roles required
├─ Host storage: Storage Blob Data Owner ✓
├─ Deployment storage: Storage Blob Data Contributor ✓
├─ Azure OpenAI: Cognitive Services OpenAI User ✓
└─ Azure AI Search: (if used) Search Index Data Contributor ✓
```

---

## 🚀 Next Steps After Creation

### Step 1: Wait for Deployment

1. Click **"Create"**
2. Wait for deployment (3-5 minutes)
3. You'll see: **"Deployment succeeded"** ✓

### Step 2: Enable System-Assigned Managed Identity

After Function App is created:

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"func-pi-copilot-dev"**
3. Click on the Function App
4. In left menu, click **"Identity"**
5. Under **"System assigned"** tab:
   - Toggle **"Status"** to **"On"**
   - Click **"Save"**
6. Click **"Yes"** to confirm

### Step 3: Copy Object ID

1. After enabling, copy the **"Object ID"**
2. Save it (you'll need it for RBAC)

---

## ✅ Verification

**After Function App is created, verify:**

```
☐ Function App exists: func-pi-copilot-dev
☐ Region: Central US
☐ Plan: Flex Consumption
☐ Storage: stgpicopilotdev
☐ Managed Identity: System-assigned (enabled)
☐ Object ID: Present
```

---

## 🎯 Current Status

✅ **Storage Account**: Created (stgpicopilotdev)  
🔄 **Function App**: Creating (Flex Consumption)  
⏳ **Next**: Enable Managed Identity after creation  

---

## 📝 Important Notes

### About Flex Consumption Plan

- ✅ Serverless (pay-per-execution)
- ✅ Auto-scales
- ✅ Good for variable workloads
- ✅ Lower cost than App Service Plan
- ✅ Supports Managed Identity

### About System-Assigned Managed Identity

- ✅ Automatically created with Function App
- ✅ Automatically deleted when Function App is deleted
- ✅ No need to manage lifecycle
- ✅ Perfect for this use case

### About the Error Message

The error "You don't have permission to create user-assigned managed identity" is **normal and expected**. You don't need user-assigned identity - system-assigned is better for this scenario.

---

## 🚀 Quick Summary

1. **Current page**: Create Function App (Flex Consumption) ✓
2. **Managed identity**: System-assigned managed identity ✓
3. **Next action**: Click "Review + create"
4. **Then**: Click "Create"
5. **Wait**: 3-5 minutes for deployment
6. **After**: Enable Managed Identity in Function App settings

---

## ✨ You're Almost There!

Just click **"Review + create"** and then **"Create"**!

The system-assigned managed identity is already selected and correct.

---

**Status**: ✅ Ready to Create Function App  
**Next**: Click "Review + create" button
