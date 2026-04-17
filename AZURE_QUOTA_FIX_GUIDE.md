# Azure Quota Fix Guide - Basic VM Quota Issue

**Error**: InternalSubscriptionIsOverQuotaForSku  
**Issue**: Basic VM quota is 0 in East US  
**Solution**: Request quota increase OR use different region/SKU  
**Time to Fix**: 5-15 minutes

---

## 🔴 The Problem

```
Error: Operation cannot be completed without additional quota
Location: East US
Current Limit (Basic VMs): 0
Current Usage: 0
Amount required: 1
```

**What this means**: Your subscription doesn't have permission to create Basic tier VMs in East US.

---

## ✅ Solution 1: Request Quota Increase (Recommended)

### Step 1.1: Go to Quotas Page

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"Quotas"** in the search bar
3. Click on **"Quotas"**

### Step 1.2: Filter for Compute

1. Click **"Compute"** (left menu)
2. Select **"Subscription**: CO+I GSC Supplier Management Preprod
3. Select **"Region"**: East US
4. Search for **"Standard B"** (Basic tier)

### Step 1.3: Request Increase

1. Find **"Standard B1s"** or **"Standard B1"**
2. Click on it
3. Click **"Request quota increase"**

### Step 1.4: Fill Request

**Quota increase request:**
- **New limit**: 1 (or higher, e.g., 5)
- **Description**: "Planning Intelligence Copilot Function App"
- Click **"Submit"**

### Step 1.5: Wait for Approval

- **Typical time**: 5-15 minutes
- **Max time**: 24 hours
- You'll get an email notification

---

## ⚡ Solution 2: Use Different Region (Faster)

If you don't want to wait for quota approval, use a different region:

### Available Regions (Usually Have Quota)

Try these regions in order:
1. **West US** (usually available)
2. **West US 2** (usually available)
3. **Central US** (usually available)
4. **South Central US** (usually available)

### How to Change Region

**When creating App Service Plan:**
- Instead of **East US**
- Select **West US** or **West US 2**

**When creating Azure OpenAI:**
- Instead of **East US**
- Select **West US** or **West US 2**

---

## 🚀 Solution 3: Use Premium Tier (Alternative)

If Basic tier quota is unavailable, try Premium tier:

### Change SKU in App Service Plan

**Instead of:**
- Sku and size: B1 (Basic)

**Use:**
- Sku and size: P1V2 (Premium)

**Note**: Premium tier costs more but usually has available quota

---

## 📋 Recommended Path

### Option A: Request Quota (Best Long-Term)
1. Request quota increase for Basic VMs in East US
2. Wait 5-15 minutes for approval
3. Continue with original setup
4. **Benefit**: Quota available for future deployments

### Option B: Use Different Region (Fastest)
1. Change region to West US or West US 2
2. Continue with setup immediately
3. **Benefit**: No waiting, immediate deployment

### Option C: Use Premium Tier (Alternative)
1. Change SKU to P1V2
2. Continue with setup immediately
3. **Benefit**: No waiting, but higher cost

---

## 🔧 Step-by-Step: Request Quota Increase

### Step 1: Navigate to Quotas

```
Azure Portal
  ↓
Search: "Quotas"
  ↓
Click: "Quotas"
```

### Step 2: Filter

```
Left Menu: "Compute"
  ↓
Subscription: CO+I GSC Supplier Management Preprod
  ↓
Region: East US
  ↓
Search: "Standard B"
```

### Step 3: Find and Request

```
Find: "Standard B1s" or "Standard B1"
  ↓
Click: "Request quota increase"
  ↓
New limit: 1 (or higher)
  ↓
Description: "Planning Intelligence Copilot Function App"
  ↓
Click: "Submit"
```

### Step 4: Wait

```
Email notification when approved
  ↓
Typically 5-15 minutes
  ↓
Then continue with setup
```

---

## 🔧 Step-by-Step: Use Different Region

### Step 1: Go Back to App Service Plan

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"**
3. Click **"Create"** again

### Step 2: Change Region

**Basics Tab:**
- **Subscription**: CO+I GSC Supplier Management Preprod
- **Resource Group**: Rg-pi-copilot-dev
- **Name**: plan-pi-copilot-dev
- **Operating System**: Linux
- **Region**: **West US** ← CHANGE THIS
- **Sku and size**: B1 (Basic)

### Step 3: Continue

1. Click **"Review + create"**
2. Click **"Create"**
3. Wait for deployment

### Step 4: Update Other Resources

When creating Azure OpenAI:
- **Region**: West US (same as App Service Plan)

---

## 📊 Comparison of Solutions

| Solution | Time | Cost | Effort | Recommended |
|----------|------|------|--------|-------------|
| Request Quota | 5-15 min | Same | Low | ✅ YES |
| Different Region | Immediate | Same | Low | ✅ YES |
| Premium Tier | Immediate | Higher | Low | ⚠️ Maybe |

---

## ✅ Recommended: Use West US

**Fastest solution:**

1. **Delete** the failed App Service Plan (if created)
2. **Create new** App Service Plan with:
   - Region: **West US**
   - Everything else same
3. **Create** Function App with:
   - Region: **East US** (can be different)
   - Plan: plan-pi-copilot-dev (from West US)
4. **Create** Azure OpenAI with:
   - Region: **West US** (same as App Service Plan)

---

## 🎯 Quick Fix (5 minutes)

### Option 1: Request Quota (Recommended)

```bash
1. Go to Azure Portal → Quotas
2. Search for "Standard B1"
3. Click "Request quota increase"
4. Set new limit to 1
5. Submit
6. Wait 5-15 minutes
7. Continue with setup
```

### Option 2: Use West US (Fastest)

```bash
1. Go to Azure Portal → App Service Plans
2. Click "Create"
3. Change Region to "West US"
4. Continue with setup
5. Done immediately
```

---

## 📝 Important Notes

### About Quota Requests
- ✅ Usually approved within 5-15 minutes
- ✅ No cost to request
- ✅ Permanent quota increase
- ✅ Available for future deployments

### About Region Change
- ✅ No waiting
- ✅ Same cost
- ✅ Immediate deployment
- ⚠️ May have slightly higher latency

### About Premium Tier
- ✅ No waiting
- ✅ Immediate deployment
- ❌ Higher cost (~$100+/month vs ~$10/month)
- ✅ Better performance

---

## 🚀 Next Steps

### Choose One:

**Path 1: Request Quota (Recommended)**
1. Request quota increase (5 min)
2. Wait for approval (5-15 min)
3. Continue with original setup
4. Total time: 10-20 min

**Path 2: Use West US (Fastest)**
1. Delete failed App Service Plan (1 min)
2. Create new with West US region (5 min)
3. Continue with setup (40 min)
4. Total time: 45 min

**Path 3: Use Premium Tier (Alternative)**
1. Delete failed App Service Plan (1 min)
2. Create new with P1V2 tier (5 min)
3. Continue with setup (40 min)
4. Total time: 45 min (but higher cost)

---

## ✨ Summary

**Problem**: Basic VM quota is 0 in East US  
**Solution**: Request quota OR use different region  
**Time**: 5-15 minutes (quota) or immediate (region change)  
**Recommendation**: Use West US for immediate deployment  

---

## 📞 Need Help?

### If quota request is stuck:
1. Check email for approval notification
2. Go to Quotas page and check status
3. Try different region as backup

### If region change doesn't work:
1. Try different region (West US 2, Central US)
2. Check subscription limits
3. Contact Azure support

---

**Ready to fix?**

Choose Path 1 (Request Quota) or Path 2 (Use West US) above and proceed!

---

**Status**: Quota Issue Identified ✅  
**Solution**: Available ✅  
**Time to Fix**: 5-15 minutes ✅
