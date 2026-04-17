# Deployment Architecture - Visual Guide

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Dashboard (Frontend)                              │   │
│  │  - DashboardPage.tsx                                     │   │
│  │  - CopilotPanel.tsx (MODIFIED - timeout & detailRecords)│   │
│  │  - API Service                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓ HTTPS                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      AZURE APP SERVICE                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Node.js Server (frontend/server.js)                     │   │
│  │  - Serves React build                                    │   │
│  │  - Handles static assets                                 │   │
│  │  - Proxies API calls to backend                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓ HTTPS                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   AZURE FUNCTIONS (Backend)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Function App (planning_intelligence)                    │   │
│  │                                                           │   │
│  │  Endpoints:                                              │   │
│  │  - /api/planning_dashboard_v2 (GET)                      │   │
│  │  - /api/explain (POST) ← Main endpoint                   │   │
│  │  - /api/planning_intelligence_nlp (POST)                 │   │
│  │  - /api/daily_refresh (Timer)                            │   │
│  │                                                           │   │
│  │  Core Functions:                                         │   │
│  │  - classify_question() → Determines question type        │   │
│  │  - generate_*_answer() → 12 answer functions             │   │
│  │  - explain() → Main orchestrator                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LLM Service (llm_service.py)                            │   │
│  │  - Builds system prompt with business rules             │   │
│  │  - Calls OpenAI ChatGPT API                              │   │
│  │  - Handles errors & retries                              │   │
│  │  - Returns intelligent responses                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Business Rules (business_rules.py)                      │   │
│  │  - Composite key rules (LOCID + GSCEQUIPCAT + PRDID)    │   │
│  │  - Design change detection                               │   │
│  │  - Forecast trend analysis                               │   │
│  │  - Supplier analysis                                     │   │
│  │  - ROJ schedule analysis                                 │   │
│  │  - Exclusion rules                                       │   │
│  │  - Field definitions (30+ SAP fields)                    │   │
│  │  - Response guidelines                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  OpenAI API (ChatGPT)                                    │   │
│  │  - Receives system prompt with business rules            │   │
│  │  - Receives user question + full blob context            │   │
│  │  - Generates intelligent response                        │   │
│  │  - Returns to backend                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Azure Blob Storage                                      │   │
│  │  - Stores 13,148 planning records                        │   │
│  │  - Daily refresh via timer trigger                       │   │
│  │  - Loaded into memory for fast access                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow: User Question to Response

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER TYPES QUESTION IN COPILOT PANEL                         │
│    Example: "What are the high-risk items?"                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND SENDS REQUEST                                       │
│    POST /api/explain                                            │
│    {                                                            │
│      "question": "What are the high-risk items?",              │
│      "context": {                                              │
│        "detailRecords": [...13,148 records...],  ← MODIFIED   │
│        "selectedEntity": null                                  │
│      }                                                          │
│    }                                                            │
│    Timeout: 35 seconds  ← MODIFIED                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. BACKEND RECEIVES REQUEST                                     │
│    explain() endpoint in function_app.py                        │
│    - Extracts question & context                               │
│    - Receives detailRecords from frontend (no load needed)     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. CLASSIFY QUESTION                                            │
│    classify_question() function                                 │
│    - Detects: greeting, risk, forecast, design, etc.           │
│    - Returns: question type                                    │
│    Example: "risk" for "What are the high-risk items?"        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. ROUTE TO APPROPRIATE ANSWER FUNCTION                         │
│    explain() endpoint routes to:                               │
│    - generate_greeting_answer() for greetings                  │
│    - generate_risk_answer() for risk questions                 │
│    - generate_forecast_answer() for forecast questions         │
│    - generate_design_answer() for design questions             │
│    - etc. (12 total answer functions)                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. ANSWER FUNCTION PROCESSES DATA                               │
│    Example: generate_risk_answer()                              │
│    - Filters detailRecords for high-risk items                 │
│    - Calculates metrics (count, percentage, etc.)              │
│    - Prepares context for LLM                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. CALL LLM SERVICE                                             │
│    llm_service.generate_response()                              │
│    - Builds system prompt with business rules                  │
│    - Includes: composite keys, design changes, forecasts, etc. │
│    - Adds: field definitions, response guidelines              │
│    - Passes: full blob context (detailRecords)                 │
│    - Sends: user question                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. OPENAI CHATGPT PROCESSES REQUEST                             │
│    - Reads system prompt (business rules)                      │
│    - Understands supply chain planning domain                  │
│    - Analyzes user question                                    │
│    - Interprets data with business context                     │
│    - Generates intelligent response                            │
│    - Returns response to backend                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. BACKEND RETURNS RESPONSE                                     │
│    {                                                            │
│      "answer": "Based on current data, we have 3,208 high-risk │
│                 items (24.4% of total). The primary concern is │
│                 Design + Supplier Change Risk...",              │
│      "type": "risk",                                            │
│      "aiInsight": "..."                                         │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. FRONTEND DISPLAYS RESPONSE                                  │
│     - Shows LLM-generated answer in copilot panel              │
│     - Displays supporting metrics                              │
│     - Shows follow-up questions                                │
│     - User sees intelligent response within 4-8 seconds        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request/Response Timeline

```
Time    Component           Action
────────────────────────────────────────────────────────────────
0ms     User                Types question in copilot panel
50ms    Frontend            Sends POST request to backend
100ms   Backend             Receives request
150ms   Backend             Classifies question type
200ms   Backend             Routes to answer function
250ms   Backend             Processes data (filters, calculates)
300ms   Backend             Calls LLM service
350ms   LLM Service         Builds system prompt with business rules
400ms   LLM Service         Calls OpenAI API
1000ms  OpenAI              Processes request
2000ms  OpenAI              Generates response
2050ms  LLM Service         Receives response from OpenAI
2100ms  Backend             Formats response
2150ms  Backend             Returns response to frontend
2200ms  Frontend            Receives response
2250ms  Frontend            Displays in copilot panel
────────────────────────────────────────────────────────────────
Total: ~2.2 seconds for simple queries
       ~4-8 seconds for complex queries
       ~8-15 seconds for very complex queries
```

---

## 🗂️ File Structure After Deployment

### Backend (Azure Functions)
```
planning_intelligence/
├── function_app.py              ← Main backend (MODIFIED)
│   ├── classify_question()
│   ├── generate_greeting_answer()
│   ├── generate_risk_answer()
│   ├── generate_forecast_answer()
│   ├── generate_design_answer()
│   ├── generate_schedule_answer()
│   ├── generate_location_answer()
│   ├── generate_material_answer()
│   ├── generate_entity_answer()
│   ├── generate_comparison_answer()
│   ├── generate_impact_answer()
│   ├── generate_health_answer()
│   ├── generate_change_answer()
│   ├── generate_general_answer()
│   └── explain() ← Main endpoint
│
├── llm_service.py               ← LLM integration (NEW)
│   ├── LLMService class
│   ├── generate_response()
│   ├── _build_system_prompt()
│   ├── _build_user_prompt()
│   └── Error handling
│
├── business_rules.py            ← Business rules (NEW)
│   ├── Composite key rules
│   ├── Design change detection
│   ├── Forecast trend analysis
│   ├── Supplier analysis
│   ├── ROJ schedule analysis
│   ├── Exclusion rules
│   ├── Field definitions
│   └── Response guidelines
│
├── generative_responses.py
├── sap_schema.py
├── blob_service.py
├── requirements.txt
├── .env                         ← API keys (SECURE)
├── host.json
└── local.settings.json
```

### Frontend (React App)
```
frontend/
├── src/
│   ├── components/
│   │   ├── CopilotPanel.tsx     ← Main copilot (MODIFIED)
│   │   │   ├── sendMessage()    ← Timeout: 35s, detailRecords passed
│   │   │   ├── useEffect()
│   │   │   └── Chat UI
│   │   └── [other components]
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx    ← Dashboard
│   │   │   └── buildDashboardContext()
│   │   └── [other pages]
│   │
│   ├── services/
│   │   └── api.ts               ← API calls
│   │       └── fetchExplain()
│   │
│   └── [other files]
│
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── .env                         ← API URL (SECURE)
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── server.js                    ← Node.js server
└── build/                       ← Production build
```

---

## 🔐 Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-your-key-here
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=planning-data
```

### Frontend (.env)
```
REACT_APP_API_URL=https://func-planning-intelligence.azurewebsites.net/api
```

---

## 📈 Deployment Checklist

```
BACKEND DEPLOYMENT
├── [ ] Create Azure Function App
├── [ ] Create Storage Account
├── [ ] Deploy code via func publish
├── [ ] Set environment variables
├── [ ] Test endpoints
└── [ ] Verify logs

FRONTEND DEPLOYMENT
├── [ ] Build React app (npm run build)
├── [ ] Create App Service
├── [ ] Deploy build folder
├── [ ] Set environment variables
├── [ ] Test in browser
└── [ ] Verify no errors

SECURITY
├── [ ] Store API keys in Key Vault
├── [ ] Enable HTTPS
├── [ ] Configure CORS
├── [ ] Regenerate API key after deployment
└── [ ] Remove keys from .env files

VERIFICATION
├── [ ] Test greeting endpoint
├── [ ] Test planning question endpoint
├── [ ] Test frontend dashboard
├── [ ] Test copilot panel
├── [ ] Verify response times
└── [ ] Check error handling
```

---

## 🎯 Key Improvements in This Deployment

| Aspect | Before | After | Impact |
|--------|--------|-------|--------|
| Greeting Support | ❌ Not routed to LLM | ✅ Routed to ChatGPT | Better UX |
| LLM Context | ⚠️ Partial context | ✅ Full blob context | Better insights |
| Frontend Timeout | ⚠️ 6 seconds | ✅ 35 seconds | No premature failures |
| detailRecords | ⚠️ Loaded from snapshot | ✅ Passed from frontend | 1-2s faster |
| Business Rules | ❌ Not used | ✅ Injected in system prompt | Domain understanding |
| Response Quality | ⚠️ Template-based | ✅ LLM-generated | Much better |

---

**Ready to deploy? Follow the DEPLOYMENT_QUICK_CHECKLIST.md for step-by-step instructions.**
