# START HERE - Deployment Instructions

## What You Need to Do

You have a **complete, production-ready** Planning Intelligence Copilot system. Here's exactly what to do next:

---

## STEP 1: Move Files to Org Laptop (5 minutes)

### Option A: Using Git (Recommended)
```bash
# Clone the repository
git clone <your-repo-url> planning-intelligence-copilot
cd planning-intelligence-copilot
```

### Option B: Manual Copy
Use the files listed in `QUICK_MOVE_CHECKLIST.md`:
- Copy all files from `planning_intelligence/` folder
- Copy all files from `frontend/` folder
- Copy configuration files (`.env`, `local.settings.json`, etc.)

**Don't copy**:
- `node_modules/` (will be generated)
- `build/` (will be generated)
- `.venv/` (will be generated)
- Test result files

---

## STEP 2: Install Dependencies (5 minutes)

### Backend
```bash
cd planning_intelligence
pip install -r requirements.txt
```

### Frontend
```bash
cd ../frontend
npm install
```

---

## STEP 3: Test Blob Connection (2 minutes)

```bash
cd planning_intelligence
python test_blob_real_data.py
```

**Expected Output**:
```
✅ SUCCESS: Loaded 13148 current rows and 13148 previous rows
```

If this fails, check:
- `local.settings.json` has `BLOB_CONNECTION_STRING`
- You have internet access to Azure
- Azure Storage account is accessible

---

## STEP 4: Load Real Data (2 minutes)

```bash
python run_daily_refresh.py
```

**Expected Output**:
```
Refresh complete. Health: 37, Changed: 2951/13148
```

This creates a snapshot with real data (13,148 records).

---

## STEP 5: Deploy to Azure Functions (10 minutes)

### 5a. Login to Azure
```bash
az login
```

### 5b. Set Environment Variables in Azure
```bash
az functionapp config appsettings set \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --settings \
    BLOB_CONNECTION_STRING="<YOUR_BLOB_CONNECTION_STRING>" \
    BLOB_CONTAINER_NAME="planning-data" \
    BLOB_CURRENT_FILE="current.csv" \
    BLOB_PREVIOUS_FILE="previous.csv"
```

### 5c. Deploy Backend
```bash
cd planning_intelligence
func azure functionapp publish <your-function-app-name>
```

### 5d. Trigger Daily Refresh
```bash
curl -X POST https://<your-function-app>.azurewebsites.net/api/daily-refresh?code=<your-function-key>
```

---

## STEP 6: Deploy Frontend (5 minutes)

### 6a. Build Frontend
```bash
cd frontend
npm run build
```

### 6b. Deploy Build Folder
Upload the `build/` folder to your hosting:
- Azure App Service
- Azure Static Web Apps
- Any other hosting

---

## STEP 7: Verify Everything Works (5 minutes)

### Test Backend
```bash
# Test dashboard endpoint
curl -X POST https://<your-function-app>.azurewebsites.net/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' \
  -H "x-functions-key: <your-function-key>"
```

**Expected**: Returns dashboard with 13,148 records

### Test Frontend
1. Open frontend URL in browser
2. Should see dashboard with real data
3. Planning health should show 37/100
4. Click "Ask Copilot" button
5. Ask: "How is planning health?"
6. Should get response about 37/100 health

---

## What You Should See

### Dashboard
- Planning Health: **37/100 (Critical)**
- Changed Records: **2,951 of 13,148 (22.4%)**
- Primary Drivers: **Design changes (1926), Supplier changes (1499)**

### Copilot Response
```
Planning health is 37/100 (Critical). 2,951 of 13,148 records have changed (22.4%). 
Primary drivers: Design changes (1926), Supplier changes (1499).
```

---

## Troubleshooting

### Blob Connection Fails
```bash
# Check credentials in local.settings.json
cat planning_intelligence/local.settings.json | grep BLOB_CONNECTION_STRING

# Verify Azure Storage account is accessible
# Verify files exist in blob storage:
#   - Container: planning-data
#   - Files: current.csv, previous.csv
```

### Frontend Can't Reach Backend
```bash
# Check .env file
cat frontend/.env | grep REACT_APP_API_URL

# Should point to your Azure Functions URL
# Example: https://your-function-app.azurewebsites.net/api
```

### npm install Fails
```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules

# Reinstall
npm install
```

### Python Dependencies Fail
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt
```

---

## File Locations

### Backend
```
planning_intelligence/
├── function_app.py              ← Main app
├── local.settings.json          ← Has blob credentials
├── requirements.txt             ← Python packages
└── [40+ other .py files]
```

### Frontend
```
frontend/
├── src/                         ← Source code
├── public/                      ← Public assets
├── .env                         ← Has API URL
├── package.json                 ← npm packages
└── build/                       ← Production build (after npm run build)
```

---

## Key Files to Remember

### Critical (Don't Lose!)
- `planning_intelligence/local.settings.json` - **HAS BLOB CREDENTIALS**
- `frontend/.env` - **HAS API URL**

### Important
- `planning_intelligence/requirements.txt` - Python dependencies
- `frontend/package.json` - npm dependencies
- `planning_intelligence/host.json` - Azure Functions config

---

## Time Estimate

| Step | Time |
|------|------|
| 1. Move files | 5 min |
| 2. Install dependencies | 5 min |
| 3. Test blob connection | 2 min |
| 4. Load real data | 2 min |
| 5. Deploy to Azure | 10 min |
| 6. Deploy frontend | 5 min |
| 7. Verify | 5 min |
| **TOTAL** | **~35 min** |

---

## Success Criteria

✅ You're done when:
1. Backend deployed to Azure Functions
2. Frontend deployed to hosting
3. Dashboard loads with real data (13,148 records)
4. Planning health shows 37/100
5. Copilot responds to questions
6. All 46 test prompts work

---

## Next: Advanced Setup (Optional)

### Add Timer Trigger for Daily Refresh
```bash
# Add to function_app.py:
@app.schedule(schedule="0 0 6 * * *")  # 6 AM daily
def daily_refresh_timer(timer: func.TimerRequest):
    run_daily_refresh()
```

### Add Azure OpenAI Integration
```bash
# Set in Azure Functions:
AZURE_OPENAI_KEY="..."
AZURE_OPENAI_ENDPOINT="..."
AZURE_OPENAI_DEPLOYMENT_NAME="..."
```

### Add Custom Styling
Edit `frontend/tailwind.config.js` and `frontend/src/index.css`

---

## Support

### Quick References
- `QUICK_MOVE_CHECKLIST.md` - Files to move
- `DEPLOYMENT_GUIDE_ORG_LAPTOP.md` - Detailed guide
- `COMPLETE_BUILD_REVIEW.md` - Full system review

### Technical Details
- `FUNCTION_APP_INTEGRATION_GUIDE.md` - Integration details
- `SCOPED_COMPUTATION_ANALYSIS.md` - How fixes work
- `E2E_TEST_FINAL_REPORT.md` - Test results

---

## Questions?

Check these files in order:
1. `QUICK_MOVE_CHECKLIST.md` - For file questions
2. `LOCAL_TESTING_SETUP.md` - For local testing
3. `DEPLOYMENT_GUIDE_ORG_LAPTOP.md` - For deployment
4. `COMPLETE_BUILD_REVIEW.md` - For system overview

---

## You're Ready! 🚀

Everything is built, tested, and ready to deploy. Follow the 7 steps above and you'll have a fully functional Planning Intelligence Copilot system running on Azure Functions with a React frontend.

**Estimated time to production: ~35 minutes**

