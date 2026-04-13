# Visual Guide - Files to Move to Org Laptop

## Backend Files Structure

```
planning_intelligence/
│
├── 📄 CORE PRODUCTION FILES (MUST MOVE)
│   ├── function_app.py                    ✅ Main backend
│   ├── llm_service.py                     ✅ ChatGPT integration
│   ├── generative_responses.py            ✅ Response generation
│   ├── business_rules.py                  ✅ Business rules
│   ├── sap_schema.py                      ✅ Data schema
│   ├── scoped_metrics.py                  ✅ Metrics
│   ├── answer_engine.py                   ✅ Answer engine
│   ├── response_builder.py                ✅ Response builder
│   ├── copilot_helpers.py                 ✅ Helpers
│   ├── nlp_endpoint.py                    ✅ NLP endpoint
│   ├── diagnostic_copilot.py              ✅ Diagnostics
│   ├── phase1_core_functions.py           ✅ Core functions
│   ├── phase2_answer_templates.py         ✅ Answer templates
│   └── phase3_integration.py              ✅ Integration
│
├── 📋 CONFIGURATION FILES (MUST MOVE)
│   ├── .env                               ✅ API keys
│   ├── requirements.txt                   ✅ Dependencies
│   ├── host.json                          ✅ Azure config
│   ├── local.settings.json                ✅ Local settings
│   └── proxies.json                       ✅ Proxy config
│
└── 🧪 TEST FILES (OPTIONAL)
    ├── test_greeting_fix.py               ⚠️ Tests
    ├── test_business_rules_llm.py         ⚠️ Tests
    ├── test_llm_integration.py            ⚠️ Tests
    └── ... (other test files)
```

---

## Frontend Files Structure

```
frontend/
│
├── 📁 src/
│   │
│   ├── 📁 components/ (MUST MOVE)
│   │   └── CopilotPanel.tsx               ✅ MODIFIED (timeout & detailRecords)
│   │
│   ├── 📁 pages/ (MUST MOVE)
│   │   └── DashboardPage.tsx              ✅ Dashboard
│   │
│   ├── 📁 services/ (MUST MOVE)
│   │   └── api.ts                         ✅ API service
│   │
│   ├── 📁 utils/ (MUST MOVE)
│   │   ├── answerGenerator.ts             ✅ Answer utils
│   │   └── promptGenerator.ts             ✅ Prompt utils
│   │
│   ├── 📁 types/ (MUST MOVE)
│   │   └── dashboard.ts                   ✅ Types
│   │
│   ├── App.tsx                            ✅ Main app
│   └── index.tsx                          ✅ Entry point
│
├── 📁 public/ (MUST MOVE)
│   ├── index.html                         ✅ HTML
│   └── favicon.ico                        ✅ Icon
│
├── 📋 CONFIGURATION FILES (MUST MOVE)
│   ├── .env                               ✅ API URL
│   ├── .env.example                       ✅ Example
│   ├── package.json                       ✅ Dependencies
│   ├── package-lock.json                  ✅ Lock file
│   ├── tsconfig.json                      ✅ TypeScript
│   ├── tailwind.config.js                 ✅ Tailwind
│   └── server.js                          ✅ Server
│
└── 📁 build/ (OPTIONAL - Generated)
    └── ... (generated files)
```

---

## Copy Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT LOCATION                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ planning_intelligence/                                   │   │
│  │ ├── function_app.py                                      │   │
│  │ ├── llm_service.py                                       │   │
│  │ ├── generative_responses.py                              │   │
│  │ ├── business_rules.py                                    │   │
│  │ ├── .env (OPENAI_API_KEY)                                │   │
│  │ ├── requirements.txt                                     │   │
│  │ └── ... (14 more files)                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ frontend/                                                │   │
│  │ ├── src/                                                 │   │
│  │ │   ├── components/CopilotPanel.tsx (MODIFIED)          │   │
│  │ │   ├── pages/DashboardPage.tsx                         │   │
│  │ │   ├── services/api.ts                                 │   │
│  │ │   └── utils/                                          │   │
│  │ ├── public/                                              │   │
│  │ ├── .env (REACT_APP_API_URL)                             │   │
│  │ ├── package.json                                         │   │
│  │ └── ... (12 more files)                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    (SCP COPY)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ORG LAPTOP                                    │
│                                                                   │
│  ~/projects/                                                     │
│  ├── planning-intelligence/                                      │
│  │   ├── function_app.py                                         │
│  │   ├── llm_service.py                                          │
│  │   ├── generative_responses.py                                 │
│  │   ├── business_rules.py                                       │
│  │   ├── .env (OPENAI_API_KEY)                                   │
│  │   ├── requirements.txt                                        │
│  │   └── ... (14 more files)                                     │
│  │                                                                │
│  └── planning-frontend/                                          │
│      ├── src/                                                    │
│      │   ├── components/CopilotPanel.tsx (MODIFIED)             │
│      │   ├── pages/DashboardPage.tsx                            │
│      │   ├── services/api.ts                                    │
│      │   └── utils/                                             │
│      ├── public/                                                 │
│      ├── .env (REACT_APP_API_URL)                                │
│      ├── package.json                                            │
│      └── ... (12 more files)                                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Setup Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORG LAPTOP SETUP                              │
│                                                                   │
│  BACKEND SETUP                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. cd ~/projects/planning-intelligence                   │   │
│  │ 2. python -m venv venv                                   │   │
│  │ 3. source venv/bin/activate                              │   │
│  │ 4. pip install -r requirements.txt                       │   │
│  │ 5. nano .env (add OPENAI_API_KEY)                        │   │
│  │ 6. func start                                            │   │
│  │    ↓                                                      │   │
│  │    Backend running on http://localhost:7071              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  FRONTEND SETUP                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. cd ~/projects/planning-frontend                       │   │
│  │ 2. npm install                                           │   │
│  │ 3. nano .env (add REACT_APP_API_URL)                     │   │
│  │ 4. npm start                                             │   │
│  │    ↓                                                      │   │
│  │    Frontend running on http://localhost:3000             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  TESTING                                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Open http://localhost:3000 in browser                │   │
│  │ 2. Test "Hi" - should respond in <2 seconds             │   │
│  │ 3. Test "What are the risks?" - should respond in <10s  │   │
│  │ 4. Verify no timeout errors                             │   │
│  │ 5. Verify no API errors                                 │   │
│  │    ↓                                                      │   │
│  │    Ready for production deployment                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Count Summary

```
BACKEND FILES
├── Core Production: 14 files
├── Configuration: 5 files
├── Test Files: 10+ files
└── Total: 19+ files

FRONTEND FILES
├── Source Code: 8 files
├── Public Assets: 2 files
├── Configuration: 7 files
└── Total: 15+ files

GRAND TOTAL: 34+ files
```

---

## Size Summary

```
Backend
├── Core files: ~150 KB
├── Config files: ~10 KB
└── Total: ~160 KB

Frontend
├── Source code: ~100 KB
├── Public assets: ~50 KB
├── Config files: ~20 KB
└── Total: ~170 KB

GRAND TOTAL: ~330 KB (without node_modules)
```

---

## Timeline

```
COPY PHASE (5 minutes)
├── Copy backend files: 2 min
└── Copy frontend files: 3 min

BACKEND SETUP (10 minutes)
├── Create venv: 2 min
├── Install dependencies: 5 min
├── Configure .env: 2 min
└── Test start: 1 min

FRONTEND SETUP (10 minutes)
├── Install dependencies: 5 min
├── Configure .env: 2 min
├── Build: 2 min
└── Test start: 1 min

TESTING (10 minutes)
├── Test backend: 3 min
├── Test frontend: 3 min
├── Test integration: 4 min

TOTAL: ~35 minutes
```

---

## Critical Modifications

```
CopilotPanel.tsx (MODIFIED)
│
├── Line 88: Timeout
│   FROM: }, 6000);
│   TO:   }, 35000);
│
└── Line 96: detailRecords
    FROM: const res = await fetchExplain({ question: question.trim(), context });
    TO:   const res = await fetchExplain({ 
            question: question.trim(), 
            context: { 
              ...context, 
              detailRecords: context.detailRecords || [] 
            } 
          });
```

---

## Verification Checklist

```
BACKEND ✅
├── [ ] function_app.py exists
├── [ ] llm_service.py exists
├── [ ] generative_responses.py exists
├── [ ] business_rules.py exists
├── [ ] .env has OPENAI_API_KEY
├── [ ] requirements.txt exists
├── [ ] func start works
└── [ ] Backend on http://localhost:7071

FRONTEND ✅
├── [ ] CopilotPanel.tsx exists (check timeout=35000)
├── [ ] DashboardPage.tsx exists
├── [ ] api.ts exists
├── [ ] answerGenerator.ts exists
├── [ ] promptGenerator.ts exists
├── [ ] .env has REACT_APP_API_URL
├── [ ] npm install works
├── [ ] npm start works
└── [ ] Frontend on http://localhost:3000

INTEGRATION ✅
├── [ ] Frontend connects to backend
├── [ ] Test "Hi" works
├── [ ] Test complex query works
└── [ ] No errors in console
```

---

## Summary

### What to Move
- ✅ 19+ backend files
- ✅ 15+ frontend files
- ✅ Total: 34+ files

### Size
- ✅ ~330 KB (without node_modules)

### Time
- ✅ ~35 minutes total

### Key Points
- ✅ CopilotPanel.tsx has critical fixes
- ✅ .env files need API keys
- ✅ Test locally before deploying
- ✅ Backend on port 7071
- ✅ Frontend on port 3000

---

**Status**: ✅ READY TO MOVE
**Recommendation**: Move files now, test locally, then deploy
