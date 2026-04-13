# Deployment Guide: Files to Move to Org Laptop

## Overview
This guide lists all files needed to deploy the Planning Intelligence Copilot system to your org laptop for testing and deployment to Azure Functions.

---

## CRITICAL: Environment Setup First

Before moving files, ensure your org laptop has:
1. **Python 3.9+** installed
2. **Azure CLI** installed (`az login` configured)
3. **Node.js 16+** installed (for frontend)
4. **Git** installed

---

## PART 1: BACKEND FILES (planning_intelligence/)

### Core Production Files (MUST MOVE)
These are the main application files:

```
planning_intelligence/
├── function_app.py                    ✅ CRITICAL - Main Azure Functions app
├── nlp_endpoint.py                    ✅ CRITICAL - NLP query handler
├── blob_loader.py                     ✅ CRITICAL - Azure Blob Storage loader
├── run_daily_refresh.py               ✅ CRITICAL - Daily refresh job
├── snapshot_store.py                  ✅ CRITICAL - Snapshot persistence
├── local.settings.json                ✅ CRITICAL - Environment variables
├── host.json                          ✅ CRITICAL - Azure Functions config
├── requirements.txt                   ✅ CRITICAL - Python dependencies
│
├── normalizer.py                      ✅ Core pipeline
├── filters.py                         ✅ Core pipeline
├── comparator.py                      ✅ Core pipeline
├── analytics.py                       ✅ Core pipeline
├── response_builder.py                ✅ Core pipeline
├── dashboard_builder.py               ✅ Core pipeline
│
├── phase1_core_functions.py           ✅ NLP Phase 1
├── phase2_answer_templates.py         ✅ NLP Phase 2
├── phase3_integration.py              ✅ NLP Phase 3
├── copilot_helpers.py                 ✅ Copilot utilities
│
├── scoped_metrics.py                  ✅ Scoped computation (NEW)
├── generative_responses.py            ✅ Generative responses (NEW)
│
├── azure_openai_integration.py        ✅ Azure OpenAI integration
├── answer_engine.py                   ✅ Answer generation
├── trend_analyzer.py                  ✅ Trend analysis
├── models.py                          ✅ Data models
├── sap_schema.py                      ✅ SAP field definitions
└── mcp_context_builder.py             ✅ MCP context building
```

### Testing Files (OPTIONAL - for local testing)
```
planning_intelligence/
├── test_blob_real_data.py             ⚠️ Test blob connection
├── test_e2e_all_prompts.py            ⚠️ End-to-end test (46 prompts)
├── validate_scoped_fixes.py           ⚠️ Validate scoped computation
├── test_all_prompts_with_blob.py      ⚠️ Test with real blob data
└── [other test_*.py files]            ⚠️ Optional for debugging
```

### Configuration Files (MUST MOVE)
```
planning_intelligence/
├── local.settings.json                ✅ CRITICAL - Has blob credentials
├── host.json                          ✅ CRITICAL - Azure Functions config
├── requirements.txt                   ✅ CRITICAL - Python packages
└── .funcignore                        ✅ Azure Functions ignore file
```

### Sample/Mock Files (OPTIONAL)
```
planning_intelligence/
├── samples/                           ⚠️ Sample data (optional)
└── [*.json test result files]         ⚠️ Test results (optional)
```

---

## PART 2: FRONTEND FILES (frontend/)

### Core Production Files (MUST MOVE)
```
frontend/
├── package.json                       ✅ CRITICAL - Dependencies
├── package-lock.json                  ✅ CRITICAL - Lock file
├── tsconfig.json                      ✅ CRITICAL - TypeScript config
├── tailwind.config.js                 ✅ CRITICAL - Tailwind config
├── postcss.config.js                  ✅ CRITICAL - PostCSS config
├── .env                               ✅ CRITICAL - Environment variables
├── .env.example                       ✅ Reference
│
├── src/
│   ├── App.tsx                        ✅ Main app component
│   ├── index.tsx                      ✅ Entry point
│   ├── index.css                      ✅ Global styles
│   │
│   ├── pages/
│   │   └── DashboardPage.tsx          ✅ Main dashboard
│   │
│   ├── components/
│   │   ├── CopilotPanel.tsx           ✅ Copilot UI
│   │   ├── DashboardPage.tsx          ✅ Dashboard layout
│   │   ├── TopRiskTable.tsx           ✅ Risk table
│   │   ├── PlanningHealthCard.tsx     ✅ Health card
│   │   ├── ForecastCard.tsx           ✅ Forecast card
│   │   ├── TrendCard.tsx              ✅ Trend card
│   │   ├── RiskCard.tsx               ✅ Risk card
│   │   ├── AlertBanner.tsx            ✅ Alert banner
│   │   ├── DrillDownPanel.tsx         ✅ Drill-down panel
│   │   └── [other components]         ✅ UI components
│   │
│   ├── services/
│   │   └── api.ts                     ✅ API client
│   │
│   ├── types/
│   │   └── dashboard.ts               ✅ TypeScript types
│   │
│   ├── utils/
│   │   ├── answerGenerator.ts         ✅ Answer generation
│   │   └── promptGenerator.ts         ✅ Prompt generation
│   │
│   └── mock/
│       └── sample_payload.json        ⚠️ Mock data (optional)
│
├── public/
│   └── index.html                     ✅ HTML template
│
├── build/                             ⚠️ Build output (optional)
└── node_modules/                      ⚠️ Will be generated by npm install
```

### Configuration Files (MUST MOVE)
```
frontend/
├── .env                               ✅ CRITICAL - API URL and key
├── .env.example                       ✅ Reference
├── package.json                       ✅ CRITICAL - Dependencies
├── package-lock.json                  ✅ CRITICAL - Lock file
├── tsconfig.json                      ✅ TypeScript config
├── tailwind.config.js                 ✅ Tailwind config
├── postcss.config.js                  ✅ PostCSS config
└── web.config                         ✅ IIS config (if deploying to IIS)
```

---

## PART 3: DOCUMENTATION FILES (OPTIONAL but RECOMMENDED)

### Integration Guides
```
FUNCTION_APP_INTEGRATION_GUIDE.md      📖 How to integrate fixes
SCOPED_COMPUTATION_ANALYSIS.md         📖 Root cause analysis
SCOPED_COMPUTATION_FIXES_SUMMARY.md    📖 Summary of fixes
E2E_TEST_FINAL_REPORT.md               📖 Test results (100% pass)
```

### Deployment Guides
```
DEPLOYMENT_VERIFICATION_GUIDE.md       📖 Verify deployment
LOCAL_TESTING_SETUP.md                 📖 Local testing setup
BLOB_DATA_TESTING_GUIDE.md             📖 Blob data testing
```

### Reference
```
README_SCOPED_FIXES.md                 📖 Quick start
COMPLETION_SUMMARY.md                  📖 What was completed
```

---

## STEP-BY-STEP: What to Move

### Step 1: Create Project Structure on Org Laptop
```bash
# Create project directory
mkdir planning-intelligence-copilot
cd planning-intelligence-copilot

# Create subdirectories
mkdir planning_intelligence
mkdir frontend
```

### Step 2: Copy Backend Files
```bash
# Copy all Python files from planning_intelligence/
cp planning_intelligence/*.py planning_intelligence/
cp planning_intelligence/local.settings.json planning_intelligence/
cp planning_intelligence/host.json planning_intelligence/
cp planning_intelligence/requirements.txt planning_intelligence/
cp planning_intelligence/.funcignore planning_intelligence/
```

### Step 3: Copy Frontend Files
```bash
# Copy frontend source
cp -r frontend/src frontend/
cp -r frontend/public frontend/
cp frontend/package.json frontend/
cp frontend/package-lock.json frontend/
cp frontend/.env frontend/
cp frontend/tsconfig.json frontend/
cp frontend/tailwind.config.js frontend/
cp frontend/postcss.config.js frontend/
cp frontend/web.config frontend/
```

### Step 4: Copy Documentation
```bash
# Copy key documentation
cp FUNCTION_APP_INTEGRATION_GUIDE.md .
cp SCOPED_COMPUTATION_ANALYSIS.md .
cp E2E_TEST_FINAL_REPORT.md .
cp LOCAL_TESTING_SETUP.md .
```

---

## CRITICAL FILES CHECKLIST

### Backend (planning_intelligence/)
- [ ] `function_app.py` - Main app
- [ ] `nlp_endpoint.py` - NLP handler
- [ ] `blob_loader.py` - Blob loader
- [ ] `run_daily_refresh.py` - Daily refresh
- [ ] `snapshot_store.py` - Snapshot storage
- [ ] `local.settings.json` - **HAS BLOB CREDENTIALS**
- [ ] `host.json` - Azure Functions config
- [ ] `requirements.txt` - Python dependencies
- [ ] All `*.py` files in planning_intelligence/

### Frontend (frontend/)
- [ ] `package.json` - Dependencies
- [ ] `.env` - **HAS API URL AND KEY**
- [ ] `src/` - All source files
- [ ] `public/` - Public assets
- [ ] `tsconfig.json` - TypeScript config
- [ ] `tailwind.config.js` - Tailwind config

---

## WHAT NOT TO MOVE

### Don't Move (Generated/Large)
```
❌ frontend/node_modules/          (will be generated by npm install)
❌ frontend/build/                 (will be generated by npm run build)
❌ planning_intelligence/.venv/    (will be generated by pip install)
❌ planning_intelligence/__pycache__/
❌ planning_intelligence/.pytest_cache/
❌ .git/                           (if using git, clone instead)
```

### Don't Move (Test Results)
```
❌ planning_intelligence/test_results*.json
❌ planning_intelligence/test_output.txt
❌ planning_intelligence/PROMPT_REVIEW_REPORT.txt
```

---

## NEXT STEPS ON ORG LAPTOP

### 1. Install Dependencies
```bash
# Backend
cd planning_intelligence
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment
```bash
# Backend - local.settings.json already has credentials
# Just verify BLOB_CONNECTION_STRING is set

# Frontend - .env already has API URL
# Just verify REACT_APP_API_URL is correct
```

### 3. Test Blob Connection
```bash
cd planning_intelligence
python test_blob_real_data.py
```

### 4. Run Daily Refresh
```bash
python run_daily_refresh.py
```

### 5. Deploy to Azure Functions
```bash
# Login to Azure
az login

# Deploy
func azure functionapp publish <your-function-app-name>
```

### 6. Build and Deploy Frontend
```bash
cd ../frontend
npm run build
# Deploy build/ folder to your hosting (Azure App Service, etc.)
```

---

## File Size Summary

| Component | Size | Notes |
|-----------|------|-------|
| Backend (planning_intelligence/) | ~2-3 MB | All .py files |
| Frontend (src/) | ~500 KB | TypeScript/React |
| Frontend (node_modules/) | ~500 MB | Generated by npm install |
| Frontend (build/) | ~2-3 MB | Generated by npm run build |
| **Total to Move** | **~3 MB** | Just source files |

---

## Verification Checklist

After moving files to org laptop:

- [ ] All Python files present in `planning_intelligence/`
- [ ] `local.settings.json` has blob credentials
- [ ] All TypeScript files present in `frontend/src/`
- [ ] `.env` file has correct API URL
- [ ] `requirements.txt` lists all dependencies
- [ ] `package.json` lists all npm dependencies
- [ ] Can run `python test_blob_real_data.py` successfully
- [ ] Can run `npm install` in frontend/ successfully
- [ ] Can run `npm run build` in frontend/ successfully

---

## Troubleshooting

### Python not found
```bash
# Install Python 3.9+
# Add to PATH
```

### Azure CLI not found
```bash
# Install Azure CLI
# Run: az login
```

### Blob connection fails
```bash
# Verify BLOB_CONNECTION_STRING in local.settings.json
# Verify Azure Storage account is accessible
# Run: python test_blob_real_data.py
```

### npm install fails
```bash
# Clear cache: npm cache clean --force
# Delete node_modules: rm -rf node_modules
# Reinstall: npm install
```

---

## Support

For issues, check:
1. `LOCAL_TESTING_SETUP.md` - Local testing guide
2. `BLOB_DATA_TESTING_GUIDE.md` - Blob data testing
3. `FUNCTION_APP_INTEGRATION_GUIDE.md` - Integration details
4. `E2E_TEST_FINAL_REPORT.md` - Test results and validation

