# Quick Move Checklist - Org Laptop

## Backend Files to Move

### Core Production Files (MUST MOVE)

```
✅ planning_intelligence/function_app.py
✅ planning_intelligence/llm_service.py
✅ planning_intelligence/generative_responses.py
✅ planning_intelligence/business_rules.py
✅ planning_intelligence/sap_schema.py
✅ planning_intelligence/scoped_metrics.py
✅ planning_intelligence/answer_engine.py
✅ planning_intelligence/response_builder.py
✅ planning_intelligence/copilot_helpers.py
✅ planning_intelligence/nlp_endpoint.py
✅ planning_intelligence/diagnostic_copilot.py
✅ planning_intelligence/phase1_core_functions.py
✅ planning_intelligence/phase2_answer_templates.py
✅ planning_intelligence/phase3_integration.py
```

### Configuration Files (MUST MOVE)

```
✅ planning_intelligence/.env (with OPENAI_API_KEY)
✅ planning_intelligence/requirements.txt
✅ planning_intelligence/host.json
✅ planning_intelligence/local.settings.json
✅ planning_intelligence/proxies.json
```

### Test Files (OPTIONAL)

```
⚠️ planning_intelligence/test_*.py (all test files)
```

---

## Frontend Files to Move

### Core Production Files (MUST MOVE)

```
✅ frontend/src/components/CopilotPanel.tsx (MODIFIED - has timeout & detailRecords fixes)
✅ frontend/src/pages/DashboardPage.tsx
✅ frontend/src/services/api.ts
✅ frontend/src/utils/answerGenerator.ts
✅ frontend/src/utils/promptGenerator.ts
✅ frontend/src/types/dashboard.ts
✅ frontend/src/App.tsx
✅ frontend/src/index.tsx
```

### Public Files (MUST MOVE)

```
✅ frontend/public/index.html
✅ frontend/public/favicon.ico
```

### Configuration Files (MUST MOVE)

```
✅ frontend/.env (with REACT_APP_API_URL)
✅ frontend/.env.example
✅ frontend/package.json
✅ frontend/package-lock.json
✅ frontend/tsconfig.json
✅ frontend/tailwind.config.js
✅ frontend/server.js
```

---

## Copy Commands

### Option 1: Copy Entire Folders (Easiest)

```bash
# Backend
scp -r planning_intelligence/ user@org-laptop:~/projects/planning-intelligence/

# Frontend
scp -r frontend/ user@org-laptop:~/projects/planning-frontend/
```

### Option 2: Copy Individual Files

#### Backend

```bash
# Core files
scp planning_intelligence/function_app.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/llm_service.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/generative_responses.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/business_rules.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/.env user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/requirements.txt user@org-laptop:~/projects/planning-intelligence/
```

#### Frontend

```bash
# Core files
scp -r frontend/src user@org-laptop:~/projects/planning-frontend/
scp -r frontend/public user@org-laptop:~/projects/planning-frontend/
scp frontend/.env user@org-laptop:~/projects/planning-frontend/
scp frontend/package.json user@org-laptop:~/projects/planning-frontend/
scp frontend/tsconfig.json user@org-laptop:~/projects/planning-frontend/
```

---

## Setup on Org Laptop

### Backend Setup

```bash
# 1. Navigate to backend
cd ~/projects/planning-intelligence

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Edit .env file
nano .env
# Add: OPENAI_API_KEY=sk-...

# 6. Test backend
func start
# Should see: "Azure Functions Core Tools started on port 7071"
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd ~/projects/planning-frontend

# 2. Install dependencies
npm install

# 3. Edit .env file
nano .env
# Add: REACT_APP_API_URL=http://localhost:7071

# 4. Test frontend
npm start
# Should see: "Compiled successfully!"
# Browser opens at http://localhost:3000
```

---

## Verification Checklist

### Backend ✅

- [ ] function_app.py exists
- [ ] llm_service.py exists
- [ ] generative_responses.py exists
- [ ] business_rules.py exists
- [ ] .env file exists with OPENAI_API_KEY
- [ ] requirements.txt exists
- [ ] host.json exists
- [ ] local.settings.json exists
- [ ] `func start` works without errors
- [ ] Backend runs on http://localhost:7071

### Frontend ✅

- [ ] CopilotPanel.tsx exists (check for timeout=35000)
- [ ] DashboardPage.tsx exists
- [ ] api.ts exists
- [ ] answerGenerator.ts exists
- [ ] promptGenerator.ts exists
- [ ] .env file exists with REACT_APP_API_URL
- [ ] package.json exists
- [ ] tsconfig.json exists
- [ ] `npm install` completes without errors
- [ ] `npm start` works without errors
- [ ] Frontend runs on http://localhost:3000

### Integration ✅

- [ ] Frontend can connect to backend
- [ ] Test "Hi" - should respond in <2 seconds
- [ ] Test "What are the risks?" - should respond in <10 seconds
- [ ] No timeout errors
- [ ] No API errors

---

## Critical Files (Minimum to Move)

### Backend (Minimum)

```
planning_intelligence/
├── function_app.py          ✅ CRITICAL
├── llm_service.py           ✅ CRITICAL
├── generative_responses.py  ✅ CRITICAL
├── business_rules.py        ✅ CRITICAL
├── .env                     ✅ CRITICAL
└── requirements.txt         ✅ CRITICAL
```

### Frontend (Minimum)

```
frontend/
├── src/
│   ├── components/CopilotPanel.tsx    ✅ CRITICAL (MODIFIED)
│   ├── pages/DashboardPage.tsx        ✅ CRITICAL
│   ├── services/api.ts                ✅ CRITICAL
│   └── utils/                         ✅ CRITICAL
├── .env                               ✅ CRITICAL
└── package.json                       ✅ CRITICAL
```

---

## Environment Variables

### Backend .env

```
OPENAI_API_KEY=sk-...
AZURE_STORAGE_CONNECTION_STRING=...
```

### Frontend .env

```
REACT_APP_API_URL=http://localhost:7071
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check Azure Functions
func --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check .env file
cat .env  # Should have OPENAI_API_KEY
```

### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 14+

# Check npm version
npm --version  # Should be 6+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check .env file
cat .env  # Should have REACT_APP_API_URL
```

### Connection Issues

```bash
# Test backend is running
curl http://localhost:7071/api/health

# Test frontend can reach backend
# Open browser console and check Network tab
# Should see requests to http://localhost:7071
```

---

## Summary

### Files to Move
- Backend: 19 files (~200 KB)
- Frontend: 15+ files (~500 KB)
- Total: ~700 KB

### Time Required
- Copy files: 5 min
- Setup backend: 10 min
- Setup frontend: 10 min
- Test: 10 min
- **Total: ~35 minutes**

### Key Points
- ✅ CopilotPanel.tsx has the critical fixes
- ✅ .env files must have API keys
- ✅ Test locally before deploying
- ✅ Backend must run on port 7071
- ✅ Frontend must run on port 3000

---

## Next Steps

1. Copy backend files
2. Copy frontend files
3. Setup backend environment
4. Setup frontend environment
5. Test locally
6. Deploy to production

---

**Status**: ✅ READY TO MOVE
**Recommendation**: Move files now, test locally, then deploy
