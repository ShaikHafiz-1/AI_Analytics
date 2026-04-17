# Deployment Troubleshooting Guide

**Last Updated**: April 15, 2026  
**Status**: Ready for Production

---

## 🔍 Common Issues & Solutions

### 1. Backend Won't Start Locally

#### Issue: "ModuleNotFoundError: No module named 'azure'"

**Symptoms:**
```
Traceback (most recent call last):
  File "planning_intelligence/function_app.py", line 1, in <module>
    import azure.functions as func
ModuleNotFoundError: No module named 'azure'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep azure
```

**Expected output:**
```
azure-functions          1.x.x
azure-storage-blob       12.x.x
```

---

#### Issue: "Python version too old"

**Symptoms:**
```
ERROR: Python 3.7 is not supported. Minimum version is 3.9
```

**Solution:**
```bash
# Check Python version
python --version

# If < 3.9, install Python 3.9+
# Download from https://www.python.org/downloads/

# Verify new version
python3.9 --version

# Create venv with correct version
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

#### Issue: "func command not found"

**Symptoms:**
```
bash: func: command not found
```

**Solution:**
```bash
# Install Azure Functions Core Tools
# macOS
brew tap azure/azure
brew install azure-functions

# Windows (via npm)
npm install -g azure-functions-core-tools@4

# Linux
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4

# Verify installation
func --version
```

---

### 2. Backend Starts But Endpoints Fail

#### Issue: "OPENAI_API_KEY not found"

**Symptoms:**
```
Error: OPENAI_API_KEY environment variable not set
Response: {"error": "API key not configured"}
```

**Solution:**
```bash
# Create .env file in planning_intelligence directory
cd planning_intelligence
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Verify .env file
cat .env

# Restart backend
func start
```

**For Azure deployment:**
```bash
az functionapp config appsettings set \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --settings OPENAI_API_KEY="sk-your-key-here"

# Verify setting
az functionapp config appsettings list \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence | grep OPENAI_API_KEY
```

---

#### Issue: "Blob storage connection failed"

**Symptoms:**
```
Error: Failed to connect to blob storage
Response: {"error": "Connection string invalid"}
```

**Solution:**
```bash
# Get connection string from Azure
az storage account show-connection-string \
  --name stgplanningintel \
  --resource-group rg-planning-intelligence

# Add to .env
echo "AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;..." >> .env

# Verify connection
python -c "
from azure.storage.blob import BlobServiceClient
import os
conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
client = BlobServiceClient.from_connection_string(conn_str)
print('✓ Connection successful')
"
```

---

#### Issue: "Timeout on /api/planning_dashboard_v2"

**Symptoms:**
```
Request timeout after 30 seconds
Response: {"error": "Request timed out"}
```

**Causes & Solutions:**

**Cause 1: Blob storage is slow**
```bash
# Check blob storage performance
az storage blob list \
  --container-name planning-data \
  --account-name stgplanningintel \
  --output table

# If slow, consider:
# - Upgrade storage account tier
# - Use blob caching
# - Implement pagination
```

**Cause 2: Too many records**
```bash
# Check record count
python -c "
from planning_intelligence.blob_service import BlobService
blob = BlobService()
records = blob.load_snapshot()
print(f'Total records: {len(records)}')
"

# If > 50,000, consider:
# - Implement pagination
# - Add caching layer
# - Filter by date range
```

**Cause 3: Network latency**
```bash
# Test network connectivity
ping stgplanningintel.blob.core.windows.net

# If high latency:
# - Use Azure CDN
# - Deploy closer to data
# - Use local caching
```

---

### 3. LLM Integration Issues

#### Issue: "OpenAI API key invalid"

**Symptoms:**
```
Error: Invalid API key provided
Response: {"error": "Authentication failed"}
```

**Solution:**
```bash
# Verify API key format
# Should start with: sk-

# Check API key is active
# Go to: https://platform.openai.com/api-keys
# Verify key is not revoked

# Test API key locally
python -c "
import openai
openai.api_key = 'sk-your-key-here'
try:
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('✓ API key valid')
except Exception as e:
    print(f'✗ API key invalid: {e}')
"

# If invalid, regenerate at https://platform.openai.com/api-keys
```

---

#### Issue: "OpenAI API rate limit exceeded"

**Symptoms:**
```
Error: Rate limit exceeded
Response: {"error": "429 Too Many Requests"}
```

**Solution:**
```bash
# Check API usage
# Go to: https://platform.openai.com/account/usage/overview

# Implement rate limiting
# In llm_service.py:
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

# Apply to LLM calls
@rate_limit(calls_per_minute=60)
def generate_response(self, ...):
    ...
```

---

#### Issue: "LLM returns blank response"

**Symptoms:**
```
Response: {"answer": "", "aiInsight": ""}
```

**Solution:**
```bash
# Check system prompt is being built
python -c "
from planning_intelligence.llm_service import LLMService
from planning_intelligence.business_rules import get_business_rules
llm = LLMService()
rules = get_business_rules()
print(f'Business rules loaded: {len(rules)} rules')
print(f'System prompt size: {len(llm._build_system_prompt())} chars')
"

# Check user prompt is being built
python -c "
from planning_intelligence.llm_service import LLMService
llm = LLMService()
prompt = llm._build_user_prompt('What are the high-risk items?', [])
print(f'User prompt: {prompt[:200]}...')
"

# Check OpenAI response
python -c "
import openai
openai.api_key = 'sk-your-key-here'
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Hello'}
    ]
)
print(f'Response: {response.choices[0].message.content}')
"
```

---

### 4. Frontend Issues

#### Issue: "Frontend shows blank page"

**Symptoms:**
```
Browser shows white page
Console shows: "Cannot GET /"
```

**Solution:**
```bash
# Check if frontend is running
curl http://localhost:3000

# If not running, start it
cd frontend
npm start

# If build error, rebuild
npm run build

# Check for errors
npm run build 2>&1 | tail -20
```

---

#### Issue: "API connection failed"

**Symptoms:**
```
Console error: "Failed to fetch from http://localhost:7071/api/explain"
Copilot shows: "Connection error"
```

**Solution:**
```bash
# Verify backend is running
curl http://localhost:7071/api/planning_dashboard_v2

# If not running, start backend
cd planning_intelligence
func start

# Verify frontend .env has correct URL
cat frontend/.env

# Should show:
# REACT_APP_API_URL=http://localhost:7071/api

# If wrong, update .env
echo "REACT_APP_API_URL=http://localhost:7071/api" > frontend/.env

# Restart frontend
npm start
```

---

#### Issue: "CORS error in browser console"

**Symptoms:**
```
Console error: "Access to XMLHttpRequest at 'http://localhost:7071/api/explain' 
from origin 'http://localhost:3000' has been blocked by CORS policy"
```

**Solution:**
```bash
# Backend already has CORS enabled
# Check function_app.py for CORS headers:

# Should have:
response.headers.add("Access-Control-Allow-Origin", "*")
response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
response.headers.add("Access-Control-Allow-Headers", "Content-Type")

# If missing, add to _cors_response() function:
def _cors_response(data: str, status: int = 200, mimetype: str = "application/json") -> func.HttpResponse:
    response = func.HttpResponse(data, status=status, mimetype=mimetype)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response
```

---

#### Issue: "Timeout error in copilot panel"

**Symptoms:**
```
Copilot shows: "⏱ Request timed out. Your question has been preserved — please try again."
After 35 seconds
```

**Solution:**
```bash
# This is expected for very complex queries
# But if happening for simple queries:

# 1. Check backend is responding
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question":"Hi","context":{"detailRecords":[],"selectedEntity":null}}'

# 2. Check response time
time curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question":"Hi","context":{"detailRecords":[],"selectedEntity":null}}'

# 3. If > 5 seconds for simple query, check:
# - Backend logs for errors
# - OpenAI API status
# - Network latency

# 4. Increase timeout if needed (in CopilotPanel.tsx):
# Change: }, 35000);  to  }, 60000);  for 60 seconds
```

---

### 5. Azure Deployment Issues

#### Issue: "Function app deployment failed"

**Symptoms:**
```
Error: Deployment failed
Details: "Unable to deploy function app"
```

**Solution:**
```bash
# Check Azure CLI is installed
az --version

# Login to Azure
az login

# Check resource group exists
az group list --output table

# If not, create it
az group create --name rg-planning-intelligence --location eastus

# Check function app exists
az functionapp list --output table

# If not, create it
az functionapp create \
  --resource-group rg-planning-intelligence \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name func-planning-intelligence \
  --storage-account stgplanningintel

# Try deployment again
func azure functionapp publish func-planning-intelligence
```

---

#### Issue: "Function app returns 503 Service Unavailable"

**Symptoms:**
```
HTTP 503 Service Unavailable
Error: "The service is temporarily unavailable"
```

**Solution:**
```bash
# Check function app status
az functionapp show \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence \
  --query state

# Should show: "Running"

# If not, start it
az functionapp start \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence

# Check logs
az functionapp log tail \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence

# Look for errors and fix them
```

---

#### Issue: "Function app returns 404 Not Found"

**Symptoms:**
```
HTTP 404 Not Found
Error: "The resource you requested could not be found"
```

**Solution:**
```bash
# Check function endpoints are deployed
az functionapp function list \
  --name func-planning-intelligence \
  --resource-group rg-planning-intelligence

# Should show:
# - explain
# - planning_dashboard_v2
# - planning_intelligence_nlp
# - daily_refresh

# If missing, redeploy
func azure functionapp publish func-planning-intelligence

# Verify endpoint URL
# Should be: https://func-planning-intelligence.azurewebsites.net/api/explain
```

---

### 6. Performance Issues

#### Issue: "Responses are slow (> 15 seconds)"

**Symptoms:**
```
User waits > 15 seconds for response
```

**Solution:**
```bash
# 1. Check backend response time
time curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the high-risk items?","context":{"detailRecords":[],"selectedEntity":null}}'

# 2. If backend is slow:
# - Check OpenAI API status
# - Check network latency
# - Check blob storage performance
# - Check function app CPU/memory

# 3. Optimize:
# - Implement caching
# - Reduce blob data size
# - Use pagination
# - Implement async processing

# 4. Monitor performance
az monitor metrics list \
  --resource /subscriptions/{subscription}/resourceGroups/rg-planning-intelligence/providers/Microsoft.Web/sites/func-planning-intelligence \
  --metric "FunctionExecutionCount,FunctionExecutionUnits"
```

---

#### Issue: "High memory usage"

**Symptoms:**
```
Function app crashes with "Out of memory"
```

**Solution:**
```bash
# Check memory usage
az monitor metrics list \
  --resource /subscriptions/{subscription}/resourceGroups/rg-planning-intelligence/providers/Microsoft.Web/sites/func-planning-intelligence \
  --metric "MemoryWorkingSet"

# Optimize:
# 1. Reduce blob data loaded into memory
# 2. Implement pagination
# 3. Use streaming for large responses
# 4. Upgrade function app plan

# Upgrade to Premium plan
az appservice plan create \
  --name plan-planning-intelligence-premium \
  --resource-group rg-planning-intelligence \
  --sku P1V2 \
  --is-linux

az functionapp plan update \
  --name func-planning-intelligence \
  --plan plan-planning-intelligence-premium
```

---

## 🧪 Diagnostic Commands

### Backend Diagnostics

```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check .env file
cat planning_intelligence/.env

# Check function app structure
ls -la planning_intelligence/

# Test imports
python -c "
import azure.functions
import openai
import azure.storage.blob
print('✓ All imports successful')
"

# Test blob connection
python -c "
from planning_intelligence.blob_service import BlobService
blob = BlobService()
records = blob.load_snapshot()
print(f'✓ Blob connection successful: {len(records)} records loaded')
"

# Test OpenAI connection
python -c "
from planning_intelligence.llm_service import LLMService
llm = LLMService()
print('✓ LLM service initialized')
"
```

### Frontend Diagnostics

```bash
# Check Node version
node --version

# Check npm version
npm --version

# Check dependencies
npm list

# Check .env file
cat frontend/.env

# Check build
npm run build

# Check for errors
npm run build 2>&1 | grep -i error

# Test API connection
curl http://localhost:7071/api/planning_dashboard_v2
```

### Azure Diagnostics

```bash
# Check Azure CLI
az --version

# Check logged in
az account show

# Check resource group
az group show --name rg-planning-intelligence

# Check function app
az functionapp show --name func-planning-intelligence --resource-group rg-planning-intelligence

# Check function app settings
az functionapp config appsettings list --name func-planning-intelligence --resource-group rg-planning-intelligence

# Check function app logs
az functionapp log tail --name func-planning-intelligence --resource-group rg-planning-intelligence

# Check function app metrics
az monitor metrics list --resource /subscriptions/{subscription}/resourceGroups/rg-planning-intelligence/providers/Microsoft.Web/sites/func-planning-intelligence
```

---

## 📞 Getting Help

If you're still stuck:

1. **Check logs**: `az functionapp log tail --name func-planning-intelligence --resource-group rg-planning-intelligence`
2. **Check OpenAI status**: https://status.openai.com
3. **Check Azure status**: https://status.azure.com
4. **Review code**: Check function_app.py and llm_service.py for errors
5. **Test locally**: Run backend and frontend locally to isolate issues

---

**Still need help? Review the DEPLOYMENT_GUIDE_ORG_LAPTOP_COMPLETE.md for detailed setup instructions.**
