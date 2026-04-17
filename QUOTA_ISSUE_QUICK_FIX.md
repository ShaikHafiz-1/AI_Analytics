# Quick Fix - Azure Quota Issue

**Problem**: Basic VM quota is 0 in East US  
**Solution**: Use West US region instead  
**Time**: 5 minutes  
**Cost**: Same

---

## 🚀 Fastest Solution: Use West US

### Step 1: Delete Failed App Service Plan (1 min)

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"**
3. Find **"plan-pi-copilot-dev"** (if it exists)
4. Click **"Delete"**
5. Confirm deletion

### Step 2: Create New App Service Plan with West US (5 min)

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"App Service Plans"**
3. Click **"Create"**

**Fill in:**
```
Subscription: CO+I GSC Supplier Management Preprod
Resource Group: Rg-pi-copilot-dev
Name: plan-pi-copilot-dev
Operating System: Linux
Region: West US ← IMPORTANT: CHANGE THIS
Sku and size: B1 (Basic)
```

4. Click **"Review + create"**
5. Click **"Create"**
6. Wait for deployment (2-3 min)

### Step 3: Continue with Function App Setup

Now continue with the rest of the setup:
- Create Function App (use West US region)
- Enable Managed Identity
- Assign RBAC roles
- Create Azure OpenAI (use West US region)
- Deploy model
- Configure settings

---

## ✅ Alternative: Request Quota Increase

If you prefer to keep East US:

1. Go to **Azure Portal** → https://portal.azure.com
2. Search for **"Quotas"**
3. Click **"Compute"**
4. Filter: Region = East US
5. Search for **"Standard B1"**
6. Click **"Request quota increase"**
7. Set new limit to **1**
8. Click **"Submit"**
9. Wait 5-15 minutes for approval
10. Then create App Service Plan in East US

---

## 🎯 Recommendation

**Use West US** - It's faster and no waiting!

The only difference is the region. Everything else works the same.

---

## 📊 Region Comparison

| Aspect | East US | West US |
|--------|---------|---------|
| Quota | 0 (need request) | Usually available |
| Latency | Lower | Slightly higher |
| Cost | Same | Same |
| Setup Time | 5-15 min wait | Immediate |

---

## ✨ Summary

**Problem**: ✅ Identified  
**Solution**: ✅ Use West US  
**Time**: ✅ 5 minutes  
**Cost**: ✅ Same  

**Next**: Delete failed plan and create new one in West US

---

**Ready?** Follow the 3 steps above!
