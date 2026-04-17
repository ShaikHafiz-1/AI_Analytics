# Deployment Quick Checklist - 5 Steps to Production

**Total Time**: 35-45 minutes  
**Status**: Ready to Deploy

---

## ✅ Step 1: Get API Key (2 minutes)

- [ ] Go to https://platform.openai.com/api-keys
- [ ] Create new secret key
- [ ] Copy key (save securely)
- [ ] **IMPORTANT**: Regenerate this key after deployment (it was exposed in chat)

---

## ✅ Step 2: Backend Setup (10 minutes)

```bash
# Navigate to backend
cd planning_intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "AZURE_STORAGE_CONNECTION_STRING=your-connection-string" >> .env
echo "AZURE_STORAGE_CONTAINER_NAME=planning-data" >> .env

# Test locally
func start
```

**Verify**: Open http://localhost:7071/api/planning_dashboard_v2 in browser

---

## ✅ Step 3: Frontend Setup (10 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:7071/api" > .env

# Test locally
npm start
```

**Verify**: Open http://localhost:3000 in browser, test copilot panel

---

## ✅ Step 4: Deploy Backend to Azure (10 minutes)

```bash
# From planning_intelligence directory
func azure functionapp publish func-planning-intelligence

# Set environment variables
az functionapp config appsettings set \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --settings \
    OPENAI_API_KEY="sk-your-key-here" \
    AZURE_STORAGE_CONNECTION_STRING="your-connection-string" \
    AZURE_STORAGE_CONTAINER_NAME="planning-data"
```

**Verify**: Test endpoint at https://func-planning-intelligence.azurewebsites.net/api/planning_dashboard_v2

---

## ✅ Step 5: Deploy Frontend to Azure (10 minutes)

```bash
# From frontend directory
npm run build

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group rg-planning-intelligence \
  --name app-planning-intelligence \
  --src build.zip

# Set environment variable
az webapp config appsettings set \
  --resource-group rg-planning-intelligence \
  --name app-planning-intelligence \
  --settings REACT_APP_API_URL="https://func-planning-intelligence.azurewebsites.net/api"
```

**Verify**: Open https://app-planning-intelligence.azurewebsites.net in browser

---

## 🧪 Final Verification (5 minutes)

### Test Backend
```bash
# Test greeting
curl -X POST https://func-planning-intelligence.azurewebsites.net/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question":"Hi","context":{"detailRecords":[],"selectedEntity":null}}'

# Expected: LLM-generated greeting response
```

### Test Frontend
1. Open https://app-planning-intelligence.azurewebsites.net
2. Type "Hello" in copilot panel
3. Should see LLM response within 2-3 seconds
4. Type "What are the high-risk items?"
5. Should see detailed analysis within 4-8 seconds

---

## 🔐 Security: Post-Deployment

- [ ] Regenerate OpenAI API key at https://platform.openai.com/api-keys
- [ ] Store new key in Azure Key Vault
- [ ] Remove old key from .env files
- [ ] Verify no API keys in git history
- [ ] Enable HTTPS on all endpoints
- [ ] Configure CORS for frontend domain only

---

## 📊 Expected Performance

| Query | Time | Status |
|-------|------|--------|
| Greeting | 1-2s | ✅ Fast |
| Simple Question | 2-4s | ✅ Fast |
| Complex Question | 4-8s | ✅ Normal |
| Very Complex | 8-15s | ✅ Normal |
| Timeout | 35s | ✅ Fixed |

---

## 🆘 If Something Goes Wrong

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep azure

# Check .env file
cat .env
```

**Frontend shows blank:**
```bash
# Check API URL
cat frontend/.env

# Test backend connectivity
curl https://func-planning-intelligence.azurewebsites.net/api/planning_dashboard_v2

# Check browser console for errors
```

**LLM not responding:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Check Azure logs
az functionapp log tail --name func-planning-intelligence --resource-group rg-planning-intelligence

# Verify API key is valid at https://platform.openai.com/api-keys
```

---

## 📚 Full Documentation

For detailed information, see: `DEPLOYMENT_GUIDE_ORG_LAPTOP_COMPLETE.md`

---

**You're ready to deploy! Start with Step 1 above.**
