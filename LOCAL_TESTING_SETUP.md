# Local Testing Setup Guide

## Environment Files Created ✅

I've created `.env` files for both backend and frontend to enable local testing.

### Backend: `planning_intelligence/.env`
```
BLOB_CONNECTION_STRING=...
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.2-chat
AZURE_OPENAI_API_VERSION=2024-02-15-preview
FUNCTIONS_WORKER_RUNTIME=python
AzureWebJobsStorage=...
CORS_ORIGIN=http://localhost:3000
```

### Frontend: `frontend/.env`
```
PORT=3000
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

## Local Testing Setup

### Step 1: Start Backend (Azure Functions)
```bash
cd planning_intelligence
func start
```

Expected output:
```
Functions:
  planning_intelligence_nlp: [POST,OPTIONS] http://localhost:7071/api/planning_intelligence_nlp
  planning-dashboard-v2: [POST,OPTIONS] http://localhost:7071/api/planning-dashboard-v2
  daily-refresh: [POST,OPTIONS] http://localhost:7071/api/daily-refresh
  explain: [POST,OPTIONS] http://localhost:7071/api/explain
  debug-snapshot: [POST,OPTIONS] http://localhost:7071/api/debug-snapshot
```

### Step 2: Start Frontend (React)
In a new terminal:
```bash
cd frontend
npm start
```

Expected output:
```
Server running on port 3000
```

### Step 3: Access Application
Open browser: **http://localhost:3000**

## Testing Checklist

### Backend Testing
- [ ] Azure Functions running on port 7071
- [ ] All 5 endpoints accessible
- [ ] Blob data loading works
- [ ] No errors in Azure Functions logs

### Frontend Testing
- [ ] React app running on port 3000
- [ ] Dashboard loads with data
- [ ] Copilot panel works
- [ ] "Retry Blob" button works
- [ ] Filters work (location, material group)

### Integration Testing
- [ ] Frontend connects to backend
- [ ] Data displays correctly
- [ ] No CORS errors
- [ ] Error handling works

## Troubleshooting

### Issue: "Cannot connect to backend"
**Solution**: 
1. Verify Azure Functions running: `func start`
2. Check port 7071 is not blocked
3. Verify REACT_APP_API_URL=http://localhost:7071/api in frontend/.env
4. Rebuild frontend: `npm run build`

### Issue: "Port 3000 already in use"
**Solution**:
1. Change PORT in frontend/.env to 3001
2. Rebuild frontend: `npm run build`
3. Restart: `npm start`

### Issue: "Port 7071 already in use"
**Solution**:
1. Kill process using port 7071
2. Restart Azure Functions: `func start`

### Issue: "Blob data unavailable"
**Solution**:
1. Verify blob files exist in Azure Storage
2. Check BLOB_CONNECTION_STRING in planning_intelligence/.env
3. Verify BLOB_CONTAINER_NAME=planning-data
4. Restart Azure Functions: `func start`

## Environment Variables

### Backend (.env)
| Variable | Purpose | Example |
|----------|---------|---------|
| BLOB_CONNECTION_STRING | Azure Blob Storage connection | DefaultEndpointsProtocol=https;... |
| BLOB_CONTAINER_NAME | Blob container name | planning-data |
| BLOB_CURRENT_FILE | Current data file | current.csv |
| BLOB_PREVIOUS_FILE | Previous data file | previous.csv |
| AZURE_OPENAI_KEY | OpenAI API key | <YOUR_AZURE_OPENAI_KEY> |
| AZURE_OPENAI_ENDPOINT | OpenAI endpoint | <YOUR_AZURE_OPENAI_ENDPOINT> |
| AZURE_OPENAI_DEPLOYMENT_NAME | OpenAI deployment | gpt-5.2-chat |
| AZURE_OPENAI_API_VERSION | OpenAI API version | 2024-02-15-preview |
| FUNCTIONS_WORKER_RUNTIME | Functions runtime | python |
| AzureWebJobsStorage | Azure Storage for functions | <YOUR_AZURE_WEBJOBS_STORAGE> |
| CORS_ORIGIN | CORS origin for local dev | http://localhost:3000 |

### Frontend (.env)
| Variable | Purpose | Example |
|----------|---------|---------|
| PORT | Frontend port | 3000 |
| REACT_APP_API_URL | Backend API URL | http://localhost:7071/api |
| REACT_APP_API_KEY | API key (if needed) | (empty for local) |
| REACT_APP_USE_MOCK | Use mock data | false |

## Quick Start Commands

### Terminal 1: Backend
```bash
cd planning_intelligence
func start
```

### Terminal 2: Frontend
```bash
cd frontend
npm start
```

### Terminal 3: Testing (Optional)
```bash
# Test backend endpoint
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

# Test daily refresh
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'
```

## File Structure

```
project/
├── planning_intelligence/
│   ├── .env                    ✅ Created
│   ├── local.settings.json     ✅ Existing
│   ├── function_app.py
│   ├── blob_loader.py
│   └── ...
├── frontend/
│   ├── .env                    ✅ Updated
│   ├── .env.example
│   ├── package.json
│   └── src/
└── ...
```

## Notes

- `.env` files are for local development only
- Never commit `.env` files with secrets to version control
- Use `local.settings.json` for Azure Functions (already configured)
- Use `.env` for local testing with `func start`
- Rebuild frontend after changing `.env`: `npm run build`

## Next Steps

1. ✅ Create `.env` files (DONE)
2. Start backend: `func start`
3. Start frontend: `npm start`
4. Open http://localhost:3000
5. Test "Retry Blob" button
6. Check Azure Functions logs for errors
7. Share error message if retry fails

---

**Status**: Environment files created and configured for local testing
**Ready**: Yes, start backend and frontend
**Next**: Run local testing and verify blob retry works
