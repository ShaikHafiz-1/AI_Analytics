# Move Files to Org Laptop - Summary

## Quick Answer

### Backend Files (19 files)

**MUST MOVE**:
```
planning_intelligence/function_app.py
planning_intelligence/llm_service.py
planning_intelligence/generative_responses.py
planning_intelligence/business_rules.py
planning_intelligence/sap_schema.py
planning_intelligence/scoped_metrics.py
planning_intelligence/answer_engine.py
planning_intelligence/response_builder.py
planning_intelligence/copilot_helpers.py
planning_intelligence/nlp_endpoint.py
planning_intelligence/diagnostic_copilot.py
planning_intelligence/phase1_core_functions.py
planning_intelligence/phase2_answer_templates.py
planning_intelligence/phase3_integration.py
planning_intelligence/.env (with OPENAI_API_KEY)
planning_intelligence/requirements.txt
planning_intelligence/host.json
planning_intelligence/local.settings.json
planning_intelligence/proxies.json
```

### Frontend Files (15+ files)

**MUST MOVE**:
```
frontend/src/components/CopilotPanel.tsx (MODIFIED - has fixes)
frontend/src/pages/DashboardPage.tsx
frontend/src/services/api.ts
frontend/src/utils/answerGenerator.ts
frontend/src/utils/promptGenerator.ts
frontend/src/types/dashboard.ts
frontend/src/App.tsx
frontend/src/index.tsx
frontend/public/index.html
frontend/public/favicon.ico
frontend/.env (with REACT_APP_API_URL)
frontend/.env.example
frontend/package.json
frontend/package-lock.json
frontend/tsconfig.json
frontend/tailwind.config.js
frontend/server.js
```

---

## Copy Commands

### Easiest Way (Copy Entire Folders)

```bash
# Backend
scp -r planning_intelligence/ user@org-laptop:~/projects/planning-intelligence/

# Frontend
scp -r frontend/ user@org-laptop:~/projects/planning-frontend/
```

### Alternative (Copy Specific Folders)

```bash
# Backend core files
scp planning_intelligence/*.py user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/.env user@org-laptop:~/projects/planning-intelligence/
scp planning_intelligence/requirements.txt user@org-laptop:~/projects/planning-intelligence/

# Frontend source
scp -r frontend/src user@org-laptop:~/projects/planning-frontend/
scp -r frontend/public user@org-laptop:~/projects/planning-frontend/
scp frontend/.env user@org-laptop:~/projects/planning-frontend/
scp frontend/package.json user@org-laptop:~/projects/planning-frontend/
```

---

## Setup on Org Laptop

### Backend

```bash
cd ~/projects/planning-intelligence
python -m venv venv
source venv/bin/activate  # Mac/Linux or venv\Scripts\activate on Windows
pip install -r requirements.txt
nano .env  # Add OPENAI_API_KEY=sk-...
func start
```

### Frontend

```bash
cd ~/projects/planning-frontend
npm install
nano .env  # Add REACT_APP_API_URL=http://localhost:7071
npm start
```

---

## What's Modified

### CopilotPanel.tsx (Line 88 & 96)

**Line 88**: Timeout changed
```typescript
// FROM: }, 6000);
// TO:   }, 35000);
```

**Line 96**: detailRecords added
```typescript
// FROM: const res = await fetchExplain({ question: question.trim(), context });
// TO:   const res = await fetchExplain({ question: question.trim(), context: { ...context, detailRecords: context.detailRecords || [] } });
```

---

## Verification

### Backend
- [ ] All .py files present
- [ ] .env has OPENAI_API_KEY
- [ ] requirements.txt present
- [ ] `func start` works
- [ ] Backend on http://localhost:7071

### Frontend
- [ ] CopilotPanel.tsx has timeout=35000
- [ ] CopilotPanel.tsx has detailRecords
- [ ] .env has REACT_APP_API_URL
- [ ] package.json present
- [ ] `npm start` works
- [ ] Frontend on http://localhost:3000

### Integration
- [ ] Frontend connects to backend
- [ ] Test "Hi" works
- [ ] Test complex query works
- [ ] No timeout errors

---

## Files Summary

| Category | Backend | Frontend | Total |
|----------|---------|----------|-------|
| Core Files | 14 | 8 | 22 |
| Config Files | 5 | 7 | 12 |
| Test Files | 10+ | 0 | 10+ |
| **Total** | **19+** | **15+** | **34+** |

---

## Size & Time

| Task | Time |
|------|------|
| Copy files | 5 min |
| Setup backend | 10 min |
| Setup frontend | 10 min |
| Test locally | 10 min |
| **Total** | **35 min** |

---

## Critical Points

✅ **CopilotPanel.tsx** has the 2 critical fixes
✅ **.env files** must have API keys
✅ **Backend** must run on port 7071
✅ **Frontend** must run on port 3000
✅ **Test locally** before deploying

---

## Next Steps

1. Copy backend files
2. Copy frontend files
3. Setup backend
4. Setup frontend
5. Test locally
6. Deploy to production

---

**Status**: ✅ READY TO MOVE
**Time**: ~35 minutes
**Recommendation**: Move files now
