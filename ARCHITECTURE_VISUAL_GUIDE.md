# Planning Intelligence Copilot - Architecture Visual Guide

**Purpose**: Visual representation of system architecture for business stakeholders  
**Audience**: Technical and non-technical stakeholders  
**Status**: ✅ Complete

---

## 🏗️ System Architecture Layers

### Layer 1: User Interface (Frontend)
```
┌─────────────────────────────────────────────────────────┐
│                   REACT DASHBOARD                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Planning Dashboard                              │   │
│  │  • Health Status Cards                           │   │
│  │  • Forecast Trends                               │   │
│  │  • Risk Indicators                               │   │
│  │  • AI Insights Panel                             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Copilot Chat Panel                              │   │
│  │  • Question input box                            │   │
│  │  • Chat history                                  │   │
│  │  • Response display                              │   │
│  │  • Drill-down options                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Data Visualization                              │   │
│  │  • Charts and graphs                             │   │
│  │  • Metrics and KPIs                              │   │
│  │  • Drill-down tables                             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Layer 2: API Gateway (Backend)
```
┌─────────────────────────────────────────────────────────┐
│              AZURE FUNCTIONS (Backend)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Endpoints                                   │   │
│  │  • POST /api/planning_intelligence_nlp           │   │
│  │  • GET /api/planning_dashboard_v2                │   │
│  │  • POST /api/daily_refresh                       │   │
│  │  • GET /api/explain                              │   │
│  │  • GET /api/debug_snapshot                       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Request Processing                              │   │
│  │  • CORS handling                                 │   │
│  │  • Request validation                            │   │
│  │  • Error handling                                │   │
│  │  • Response formatting                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Layer 3: Business Logic (Processing)
```
┌─────────────────────────────────────────────────────────┐
│           BUSINESS LOGIC LAYER                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Question Classification                         │   │
│  │  • Identifies question type (12 types)           │   │
│  │  • Extracts parameters                           │   │
│  │  • Routes to appropriate handler                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Answer Generation (12 Functions)                │   │
│  │  • Health Status Analysis                        │   │
│  │  • Forecast Prediction                           │   │
│  │  • Risk Assessment                               │   │
│  │  • Design Change Impact                          │   │
│  │  • General Planning                              │   │
│  │  • Greeting Response                             │   │
│  │  • Design Specification                          │   │
│  │  • Schedule Analysis                             │   │
│  │  • Location Analysis                             │   │
│  │  • Material Analysis                             │   │
│  │  • Entity Analysis                               │   │
│  │  • Comparison Analysis                           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Data Processing                                 │   │
│  │  • Data filtering                                │   │
│  │  • Metric calculation                            │   │
│  │  • Aggregation                                   │   │
│  │  • Normalization                                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Layer 4: AI & Intelligence (ChatGPT)
```
┌─────────────────────────────────────────────────────────┐
│              AZURE OPENAI (ChatGPT)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  LLM Service                                     │   │
│  │  • System prompt (business rules)                │   │
│  │  • User prompt (question + context)              │   │
│  │  • Context injection (planning data)             │   │
│  │  • Response generation                           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Business Rules Engine                           │   │
│  │  • Planning health rules                         │   │
│  │  • Forecast rules                                │   │
│  │  • Risk assessment rules                         │   │
│  │  • Equipment category rules                      │   │
│  │  • Location rules                                │   │
│  │  • Supplier rules                                │   │
│  │  • Material group rules                          │   │
│  │  • Compliance rules                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Response Validation                             │   │
│  │  • Fact checking                                 │   │
│  │  • Rule compliance                               │   │
│  │  • Quality assurance                             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Layer 5: Data Storage (Blob Storage)
```
┌─────────────────────────────────────────────────────────┐
│           AZURE BLOB STORAGE                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Planning Data Container                         │   │
│  │  ├── current.csv (13,000+ records)               │   │
│  │  │   • Location ID                               │   │
│  │  │   • Material ID                               │   │
│  │  │   • Equipment Category                        │   │
│  │  │   • Health Status                             │   │
│  │  │   • Forecast Metrics                          │   │
│  │  │   • Risk Indicators                           │   │
│  │  │   • Timestamps                                │   │
│  │  │                                               │   │
│  │  ├── previous.csv (previous day)                 │   │
│  │  │   • Used for trend analysis                   │   │
│  │  │   • Day-over-day comparison                   │   │
│  │  │                                               │   │
│  │  └── historical/ (archive)                       │   │
│  │      • Long-term trends                          │   │
│  │      • Seasonal patterns                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### User Question to Response Flow

```
1. USER ASKS QUESTION
   ┌─────────────────────────────────────────┐
   │ "What's the health status in Dallas?"   │
   └────────────────┬────────────────────────┘
                    │
                    ↓
2. FRONTEND SENDS REQUEST
   ┌─────────────────────────────────────────┐
   │ POST /api/planning_intelligence_nlp     │
   │ {                                       │
   │   "question": "What's the health...",   │
   │   "location": "Dallas",                 │
   │   "detailRecords": [...]                │
   │ }                                       │
   └────────────────┬────────────────────────┘
                    │ HTTPS
                    ↓
3. BACKEND RECEIVES REQUEST
   ┌─────────────────────────────────────────┐
   │ Azure Function App                      │
   │ • Validates request                     │
   │ • Extracts parameters                   │
   └────────────────┬────────────────────────┘
                    │
                    ↓
4. CLASSIFY QUESTION
   ┌─────────────────────────────────────────┐
   │ Question Type: LOCATION_ANALYSIS        │
   │ Parameters: location="Dallas"           │
   └────────────────┬────────────────────────┘
                    │
                    ↓
5. LOAD DATA FROM BLOB
   ┌─────────────────────────────────────────┐
   │ Azure Blob Storage                      │
   │ • Read current.csv                      │
   │ • Load 13,000+ records                  │
   │ • Filter for Dallas (500 records)       │
   └────────────────┬────────────────────────┘
                    │
                    ↓
6. CALCULATE METRICS
   ┌─────────────────────────────────────────┐
   │ • Health score: 78/100                  │
   │ • Forecast: Stable                      │
   │ • Risk level: Medium                    │
   │ • Equipment breakdown                   │
   └────────────────┬────────────────────────┘
                    │
                    ↓
7. BUILD CONTEXT FOR CHATGPT
   ┌─────────────────────────────────────────┐
   │ System Prompt:                          │
   │ • Business rules (8 categories)         │
   │ • Domain knowledge                      │
   │ • Response guidelines                   │
   │                                         │
   │ User Prompt:                            │
   │ • Question                              │
   │ • Planning data (500 records)           │
   │ • Calculated metrics                    │
   │ • Context information                   │
   └────────────────┬────────────────────────┘
                    │
                    ↓
8. SEND TO CHATGPT
   ┌─────────────────────────────────────────┐
   │ Azure OpenAI (GPT-3.5-turbo)            │
   │ • Receives system + user prompt         │
   │ • Analyzes planning data                │
   │ • Applies business rules                │
   │ • Generates response                    │
   └────────────────┬────────────────────────┘
                    │
                    ↓
9. CHATGPT GENERATES RESPONSE
   ┌─────────────────────────────────────────┐
   │ "Dallas location shows YELLOW health    │
   │  status (78/100). While overall         │
   │  performance is acceptable, the         │
   │  Mechanical and Hydraulic equipment     │
   │  categories need attention..."          │
   └────────────────┬────────────────────────┘
                    │
                    ↓
10. BACKEND FORMATS RESPONSE
    ┌─────────────────────────────────────────┐
    │ {                                       │
    │   "answer": "Dallas location shows...", │
    │   "metrics": {...},                     │
    │   "recommendations": [...],             │
    │   "timestamp": "2026-04-17T10:30:00Z"   │
    │ }                                       │
    └────────────────┬────────────────────────┘
                     │ HTTPS
                     ↓
11. FRONTEND RECEIVES RESPONSE
    ┌─────────────────────────────────────────┐
    │ React Dashboard                         │
    │ • Displays response in chat panel       │
    │ • Shows metrics                         │
    │ • Offers drill-down options             │
    └────────────────┬────────────────────────┘
                     │
                     ↓
12. USER SEES ANSWER
    ┌─────────────────────────────────────────┐
    │ Copilot Chat Panel                      │
    │ "Dallas location shows YELLOW health    │
    │  status (78/100)..."                    │
    │                                         │
    │ [Drill Down] [Get Details] [Export]     │
    └─────────────────────────────────────────┘
```

---

## 📊 Daily Refresh Data Flow

```
SAP Planning System
    │
    ├─ Exports planning snapshot
    │  (13,000+ records)
    │
    ↓
CSV File
    │
    ├─ Location, Material, Equipment
    ├─ Health Status, Forecast, Risk
    ├─ Timestamps, Metrics
    │
    ↓
Azure Blob Storage
    │
    ├─ Upload to "planning-data" container
    ├─ File: "current.csv"
    ├─ Backup previous: "previous.csv"
    │
    ↓
Backend Loads Data
    │
    ├─ Azure Function App
    ├─ Reads from Blob Storage
    ├─ Loads 13,000+ records
    ├─ Caches in memory
    │
    ↓
Copilot Ready
    │
    ├─ User asks question
    ├─ Backend loads latest data
    ├─ Filters by parameters
    ├─ Sends to ChatGPT
    │
    ↓
User Gets Fresh Insights
    │
    └─ Response based on today's data
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                        │
└─────────────────────────────────────────────────────────┘

Layer 1: Network Security
├─ HTTPS encryption (TLS 1.2+)
├─ Azure Firewall
├─ DDoS protection
└─ Network isolation

Layer 2: Authentication
├─ Azure AD (Microsoft Entra)
├─ Managed Identity (no API keys)
├─ Role-based access control (RBAC)
└─ Multi-factor authentication (MFA)

Layer 3: Data Security
├─ Encryption at rest (AES-256)
├─ Encryption in transit (TLS 1.2+)
├─ Key Vault for secrets
└─ Secure key rotation

Layer 4: Application Security
├─ Input validation
├─ SQL injection prevention
├─ XSS protection
├─ CSRF tokens
└─ Rate limiting

Layer 5: Compliance
├─ SFI zero-trust policies
├─ Audit logging
├─ Data governance
├─ Regulatory compliance
└─ Compliance monitoring
```

---

## 📈 Scalability Architecture

```
┌─────────────────────────────────────────────────────────┐
│              SCALABILITY DESIGN                         │
└─────────────────────────────────────────────────────────┘

Horizontal Scaling
├─ Azure Functions: Auto-scale (0-1000+ instances)
├─ Blob Storage: Unlimited capacity
├─ OpenAI API: Unlimited requests
└─ Database: Partitioned by location/material

Vertical Scaling
├─ Function memory: Configurable
├─ Blob throughput: Configurable
├─ OpenAI tokens: Configurable
└─ Cache size: Configurable

Performance Optimization
├─ Data caching (in-memory)
├─ Query optimization
├─ Response compression
├─ CDN for static assets
└─ Lazy loading for UI

Load Balancing
├─ Azure Load Balancer
├─ Geographic distribution
├─ Request routing
└─ Failover handling
```

---

## 🎯 Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    USER BROWSER                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  React Dashboard (Frontend)                        │  │
│  │  • CopilotPanel.tsx                                │  │
│  │  • DashboardPage.tsx                               │  │
│  │  • API service client                              │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS API
                         ↓
┌──────────────────────────────────────────────────────────┐
│              AZURE CLOUD PLATFORM                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Azure Functions (Backend)                         │  │
│  │  • function_app.py                                 │  │
│  │  • 12 answer functions                             │  │
│  │  • Question classification                         │  │
│  │  • Response formatting                             │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                 │
│         ┌───────────────┼───────────────┐                │
│         ↓               ↓               ↓                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │   Blob     │  │  ChatGPT   │  │  Business  │         │
│  │  Storage   │  │  (OpenAI)  │  │   Rules    │         │
│  │            │  │            │  │   Engine   │         │
│  │ • current  │  │ • LLM      │  │ • 8 rule   │         │
│  │   .csv     │  │   service  │  │   categories         │
│  │ • previous │  │ • System   │  │ • Validation         │
│  │   .csv     │  │   prompt   │  │ • Compliance         │
│  │ • historical│ │ • Response │  │                      │
│  │            │  │   generation│ │                      │
│  └────────────┘  └────────────┘  └────────────┘         │
│         ↑               ↑               ↑                │
│         └───────────────┼───────────────┘                │
│                         │                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Azure Key Vault                                   │  │
│  │  • API keys                                        │  │
│  │  • Connection strings                              │  │
│  │  • Secrets                                         │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Azure Monitor                                     │  │
│  │  • Logging                                         │  │
│  │  • Monitoring                                      │  │
│  │  • Alerting                                        │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ Architecture Summary

**Frontend**: React dashboard with Copilot chat panel  
**Backend**: Azure Functions with 12 specialized answer functions  
**AI**: Azure OpenAI (ChatGPT) with business rules injection  
**Data**: Azure Blob Storage with daily refresh  
**Security**: Zero-trust with Managed Identity and RBAC  
**Scalability**: Auto-scaling to handle 1,000+ concurrent users  
**Performance**: 2-8 second response times for most queries  

---

**Document Status**: ✅ Complete  
**Last Updated**: April 17, 2026
