# Files to Move to Org Laptop - Complete Guide

## Overview

This guide shows exactly which files you need to move to your org laptop for both frontend and backend to deploy the Planning Intelligence Copilot system.

---

## Backend Files to Move

### Location: `planning_intelligence/` folder

#### Core Files (MUST MOVE - Production Code)

```
planning_intelligence/
├── function_app.py                    ✅ CRITICAL - Main backend with all answer functions
├── llm_service.py                     ✅ CRITICAL - ChatGPT integration
├── generative_responses.py            ✅ CRITICAL - Response generation
├── business_rules.py                  ✅ IMPORTANT - Business rules for LLM
├── sap_schema.py                      ✅ IMPORTANT - Data schema definitions
├── scoped_metrics.py                  ✅ IMPORTANT - Metrics calculations
├── answer_engine.py                   ✅ IMPORTANT - Answer generation engine
├── response_builder.py                ✅ IMPORTANT - Response building
├── copilot_helpers.py                 ✅ IMPORTANT - Helper functions
├── nlp_endpoint.py                    ✅ IMPORTANT - NLP endpoint
├── diagnostic_copilot.py              ✅ IMPORTANT - Diagnostics
├── phase1_core_functions.py           ✅ IMPORTANT - Core functions
├── phase2_answer_templates.py         ✅ IMPORTANT - Answer templates
├── phase3_integration.py              ✅ IMPORTANT - Integration logic
├── .env                               ✅ CRITICAL - Environment variables (OPENAI_API_KEY)
└── requirements.txt                   ✅ CRITICAL - Python dependencies
```

#### Test Files (OPTIONAL - For Local Testing)

```
planning_intelligence/
├── test_greeting_fix.py               ⚠️ OPTIONAL - Test greeting detection
├── test_business_rules_llm.py         ⚠️ OPTIONAL - Test business rules
├── test_llm_integration.py            ⚠️ OPTIONAL - Test LLM integration
├── test_backend_local.py              ⚠️ OPTIONAL - Local backend tests
├── test_end_to_end.py                 ⚠️ OPTIONAL - End-to-end tests
├── test_classification_fix.py         ⚠️ OPTIONAL - Classification tests
├── test_response_content.py           ⚠️ OPTIONAL - Response content tests
├── test_all_prompts_with_blob.py      ⚠️ OPTIONAL - Prompt tests
└── test_e2e_all_prompts.py            ⚠️ OPTIONAL - E2E prompt tests
```

#### Configuration Files (MUST MOVE)

```
planning_intelligence/
├── host.json                          ✅ CRITICAL - Azure Functions config
├── local.settings.json                ✅ CRITICAL - Local settings
└── proxies.json                       ✅ CRITICAL - Proxy settings
```

---

## Frontend Files to Move

### Location: `frontend/` folder

#### Core Files (MUST MOVE - Production Code)

```
frontend/
├── src/
│   ├── components/
│   │   └── CopilotPanel.tsx           ✅ CRITICAL - Main copilot component (MODIFIED)
│   ├── pages/
│   │   └── DashboardPage.tsx          ✅ CRITICAL - Dashboard page
│   ├── services/
│   │   └── api.ts                     ✅ CRITICAL - API service
│   ├── utils/
│   │   ├── answerGenerator.ts         ✅ CRITICAL - Answer generation utilities
│   │   └── promptGenerator.ts         ✅ CRITICAL - Prompt generation utilities
│   ├── types/
│   │   └── dashboard.ts               ✅ CRITICAL - Type definitions
│   ├── App.tsx                        ✅ CRITICAL - Main app component
│   └── index.tsx                      ✅ CRITICAL - Entry point
├── public/
│   ├── index.html                     ✅ CRITICAL - HTML template
│   └── favicon.ico                    ✅ CRITICAL - Favicon
├── .env                               ✅ CRITICAL - Environment variables
├── .env.example                       ✅ CRITICAL - Example env file
├── package.json                       ✅ CRITICAL - Dependencies
├── package-lock.json                  ✅ CRITICAL - Dependency lock
├── tsconfig.json                      ✅ CRITICAL - TypeScript config
├── tailwind.config.js                 ✅ CRITICAL - Tailwind config
└── server.js                          ✅ CRITICAL - Express server (if using)
```

#### Build Output (OPTIONAL - Generated)

```
frontend/
└── build/                             ⚠️ OPTIONAL - Generated build folder
    ├── index.html
    ├── static/
    │   ├── js/
    │   ├── css/
    │   └── media/
    └── manifest.json
```

---

## Step-by-Step Move Instructions

### For Backend

#### Step 1: Create Backend Directory on Org Laptop

```bash
# On org laptop
mkdir -p ~/projects/planning-intelligence
cd ~/projects/planning-intelligence
```

#### Step 2: Copy Core Backend Files

```bash
# Copy from current location to org laptop
# Using SCP or file transfer

# Core production files
scp -r planning_intelligence/*.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/.env user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/requirements.txt user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/host.json user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/local.settings.json user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/proxies.json user@org-laptop:~/projects/planning-intelligence/
```

#### Step 3: Verify Backend Files

```bash
# On org laptop, verify files are present
ls -la ~/projects/planning-intelligence/

# Should see:
# function_app.py
# llm_service.py
# generative_responses.py
# business_rules.py
# .env
# requirements.txt
# ... and other files
```

---

### For Frontend

#### Step 1: Create Frontend Directory on Org Laptop

```bash
# On org laptop
mkdir -p ~/projects/planning-frontend
cd ~/projects/planning-frontend
```

#### Step 2: Copy Core Frontend Files

```bash
# Copy from current location to org laptop
# Using SCP or file transfer

# Copy entire frontend folder
scp -r frontend/ user@org-laptop:~/projects/planning-frontend/

# Or copy specific files
scp -r frontend/src user@org-laptop:~/projects/planning-frontend/
scp -r frontend/public user@org-laptop:~/projects/planning-frontend/
scp frontend/.env user@org-laptop:~/projects/planning-frontend/
scp frontend/.env.example user@org-laptop:~/projects/planning-frontend/
scp frontend/package.json user@org-laptop:~/projects/planning-frontend/
scp frontend/package-lock.json user@org-laptop:~/projects/planning-frontend/
scp frontend/tsconfig.json user@org-laptop:~/projects/planning-frontend/
scp frontend/tailwind.config.js user@org-laptop:~/projects/planning-frontend/
scp frontend/server.js user@org-laptop:~/projects/planning-frontend/
```

#### Step 3: Verify Frontend Files

```bash
# On org laptop, verify files are present
ls -la ~/projects/planning-frontend/

# Should see:
# src/
# public/
# .env
# package.json
# tsconfig.json
# ... and other files
```

---

## Critical Files Summary

### Backend - MUST MOVE (Minimum)

| File | Purpose | Size | Priority |
|------|---------|------|----------|
| function_app.py | Main backend logic | ~50 KB | ✅ CRITICAL |
| llm_service.py | ChatGPT integration | ~20 KB | ✅ CRITICAL |
| generative_responses.py | Response generation | ~30 KB | ✅ CRITICAL |
| business_rules.py | Business rules | ~15 KB | ✅ CRITICAL |
| .env | API keys & config | ~1 KB | ✅ CRITICAL |
| requirements.txt | Python dependencies | ~2 KB | ✅ CRITICAL |

### Frontend - MUST MOVE (Minimum)

| File | Purpose | Size | Priority |
|------|---------|------|----------|
| src/components/CopilotPanel.tsx | Main copilot (MODIFIED) | ~15 KB | ✅ CRITICAL |
| src/pages/DashboardPage.tsx | Dashboard page | ~20 KB | ✅ CRITICAL |
| src/services/api.ts | API service | ~10 KB | ✅ CRITICAL |
| src/utils/answerGenerator.ts | Answer utilities | ~15 KB | ✅ CRITICAL |
| src/utils/promptGenerator.ts | Prompt utilities | ~15 KB | ✅ CRITICAL |
| .env | Environment config | ~1 KB | ✅ CRITICAL |
| package.json | Dependencies | ~2 KB | ✅ CRITICAL |

---

## What Changed (Modified Files)

### Frontend - Modified File

**File**: `frontend/src/components/CopilotPanel.tsx`

**Changes**:
1. Line 88: Timeout changed from `6000` to `35000`
2. Line 96: Added `detailRecords: context.detailRecords || []` to context

**Why**: These are the critical fixes for timeout and detailRecords passing.

### Backend - No Changes Needed

All backend files are already updated with:
- ✅ Greeting detection
- ✅ LLM integration
- ✅ All answer functions using ChatGPT
- ✅ Full blob context support

---

## Setup Instructions on Org Laptop

### Backend Setup

```bash
# 1. Navigate to backend directory
cd ~/projects/planning-intelligence

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables
# Edit .env file with your OPENAI_API_KEY
nano .env
# Add: OPENAI_API_KEY=sk-...

# 6. Test backend locally
func start
# Should start on http://localhost:7071
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd ~/projects/planning-frontend

# 2. Install dependencies
npm install

# 3. Set environment variables
# Edit .env file with your API endpoint
nano .env
# Add: REACT_APP_API_URL=http://localhost:7071

# 4. Start frontend locally
npm start
# Should start on http://localhost:3000
```

---

## Directory Structure on Org Laptop

### After Moving Files

```
~/projects/
├── planning-intelligence/          (Backend)
│   ├── function_app.py
│   ├── llm_service.py
│   ├── generative_responses.py
│   ├── business_rules.py
│   ├── .env
│   ├── requirements.txt
│   ├── host.json
│   ├── local.settings.json
│   └── ... (other files)
│
└── planning-frontend/              (Frontend)
    ├── src/
    │   ├── components/
    │   │   └── CopilotPanel.tsx    (MODIFIED)
    │   ├── pages/
    │   ├── services/
    │   ├── utils/
    │   └── types/
    ├── public/
    ├── .env
    ├── package.json
    ├── tsconfig.json
    └── ... (other files)
```

---

## Verification Checklist

### Backend Files ✅

- [ ] function_app.py present
- [ ] llm_service.py present
- [ ] generative_responses.py present
- [ ] business_rules.py present
- [ ] .env file present with OPENAI_API_KEY
- [ ] requirements.txt present
- [ ] host.json present
- [ ] local.settings.json present

### Frontend Files ✅

- [ ] CopilotPanel.tsx present (with modifications)
- [ ] DashboardPage.tsx present
- [ ] api.ts present
- [ ] answerGenerator.ts present
- [ ] promptGenerator.ts present
- [ ] .env file present
- [ ] package.json present
- [ ] tsconfig.json present

### Environment Variables ✅

- [ ] Backend .env has OPENAI_API_KEY
- [ ] Frontend .env has REACT_APP_API_URL
- [ ] Both .env files are NOT committed to git

---

## Quick Copy Commands

### All-in-One Backend Copy

```bash
# Copy entire backend folder
scp -r planning_intelligence/ user@org-laptop:~/projects/planning-intelligence/
```

### All-in-One Frontend Copy

```bash
# Copy entire frontend folder
scp -r frontend/ user@org-laptop:~/projects/planning-frontend/
```

---

## Important Notes

### Security

⚠️ **IMPORTANT**: 
- Never commit `.env` files to git
- Keep OPENAI_API_KEY secret
- Don't share .env files
- Use .env.example as template

### Dependencies

- Backend requires: Python 3.8+, Azure Functions Core Tools
- Frontend requires: Node.js 14+, npm 6+

### Testing

After moving files:
1. Test backend locally: `func start`
2. Test frontend locally: `npm start`
3. Test API connection
4. Test greeting detection
5. Test LLM integration

---

## Troubleshooting

### Backend Issues

```bash
# If dependencies fail
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# If Azure Functions fails
npm install -g azure-functions-core-tools@4

# If .env not found
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### Frontend Issues

```bash
# If dependencies fail
rm -rf node_modules package-lock.json
npm install

# If TypeScript errors
npm run build

# If port 3000 in use
PORT=3001 npm start
```

---

## Summary

### Backend Files to Move
- ✅ 14 core Python files
- ✅ 1 .env file (with OPENAI_API_KEY)
- ✅ 1 requirements.txt
- ✅ 3 config files (host.json, local.settings.json, proxies.json)

### Frontend Files to Move
- ✅ Entire src/ folder
- ✅ Entire public/ folder
- ✅ 1 .env file
- ✅ 5 config files (package.json, tsconfig.json, tailwind.config.js, server.js, etc.)

### Total Size
- Backend: ~200 KB
- Frontend: ~500 KB (without node_modules)
- Total: ~700 KB

### Time to Move
- Copy files: 5 minutes
- Setup backend: 10 minutes
- Setup frontend: 10 minutes
- Test locally: 10 minutes
- **Total: ~35 minutes**

---

## Next Steps

1. ✅ Copy backend files to org laptop
2. ✅ Copy frontend files to org laptop
3. ✅ Setup backend environment
4. ✅ Setup frontend environment
5. ✅ Test locally
6. ✅ Deploy to production

---

**Status**: ✅ READY TO MOVE
**Files**: 20+ core files
**Size**: ~700 KB
**Time**: ~35 minutes
**Recommendation**: Move files now, test locally, then deploy
