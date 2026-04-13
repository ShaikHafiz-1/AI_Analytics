# Quick Move Checklist - Files to Transfer to Org Laptop

## TL;DR - Essential Files Only

### Backend (planning_intelligence/) - 40+ Python files
```
✅ MUST MOVE (Core Application):
  - function_app.py
  - nlp_endpoint.py
  - blob_loader.py
  - run_daily_refresh.py
  - snapshot_store.py
  - local.settings.json (HAS CREDENTIALS)
  - host.json
  - requirements.txt
  - All other *.py files in planning_intelligence/

❌ DON'T MOVE:
  - __pycache__/
  - .venv/
  - .pytest_cache/
  - test_results*.json
  - *.txt (test output)
```

### Frontend (frontend/) - React/TypeScript
```
✅ MUST MOVE (Source Code):
  - src/ (entire directory)
  - public/ (entire directory)
  - package.json
  - package-lock.json
  - .env (HAS API URL)
  - tsconfig.json
  - tailwind.config.js
  - postcss.config.js
  - web.config

❌ DON'T MOVE:
  - node_modules/ (run: npm install)
  - build/ (run: npm run build)
```

### Documentation (Optional but Recommended)
```
📖 RECOMMENDED:
  - FUNCTION_APP_INTEGRATION_GUIDE.md
  - SCOPED_COMPUTATION_ANALYSIS.md
  - E2E_TEST_FINAL_REPORT.md
  - LOCAL_TESTING_SETUP.md
  - DEPLOYMENT_GUIDE_ORG_LAPTOP.md (this file)
```

---

## Copy Commands (Windows PowerShell)

### Backend
```powershell
# Copy all Python files
Copy-Item -Path "planning_intelligence\*.py" -Destination "C:\YourPath\planning_intelligence\" -Force
Copy-Item -Path "planning_intelligence\local.settings.json" -Destination "C:\YourPath\planning_intelligence\" -Force
Copy-Item -Path "planning_intelligence\host.json" -Destination "C:\YourPath\planning_intelligence\" -Force
Copy-Item -Path "planning_intelligence\requirements.txt" -Destination "C:\YourPath\planning_intelligence\" -Force
```

### Frontend
```powershell
# Copy source
Copy-Item -Path "frontend\src" -Destination "C:\YourPath\frontend\" -Recurse -Force
Copy-Item -Path "frontend\public" -Destination "C:\YourPath\frontend\" -Recurse -Force
Copy-Item -Path "frontend\package.json" -Destination "C:\YourPath\frontend\" -Force
Copy-Item -Path "frontend\package-lock.json" -Destination "C:\YourPath\frontend\" -Force
Copy-Item -Path "frontend\.env" -Destination "C:\YourPath\frontend\" -Force
Copy-Item -Path "frontend\tsconfig.json" -Destination "C:\YourPath\frontend\" -Force
Copy-Item -Path "frontend\tailwind.config.js" -Destination "C:\YourPath\frontend\" -Force
Copy-Item -Path "frontend\postcss.config.js" -Destination "C:\YourPath\frontend\" -Force
```

---

## Copy Commands (Linux/Mac)

### Backend
```bash
# Copy all Python files
cp planning_intelligence/*.py /path/to/destination/planning_intelligence/
cp planning_intelligence/local.settings.json /path/to/destination/planning_intelligence/
cp planning_intelligence/host.json /path/to/destination/planning_intelligence/
cp planning_intelligence/requirements.txt /path/to/destination/planning_intelligence/
```

### Frontend
```bash
# Copy source
cp -r frontend/src /path/to/destination/frontend/
cp -r frontend/public /path/to/destination/frontend/
cp frontend/package.json /path/to/destination/frontend/
cp frontend/package-lock.json /path/to/destination/frontend/
cp frontend/.env /path/to/destination/frontend/
cp frontend/tsconfig.json /path/to/destination/frontend/
cp frontend/tailwind.config.js /path/to/destination/frontend/
cp frontend/postcss.config.js /path/to/destination/frontend/
```

---

## After Moving Files - Setup Steps

### 1. Install Python Dependencies
```bash
cd planning_intelligence
pip install -r requirements.txt
```

### 2. Install Node Dependencies
```bash
cd frontend
npm install
```

### 3. Test Blob Connection
```bash
cd planning_intelligence
python test_blob_real_data.py
```

### 4. Run Daily Refresh (Load Real Data)
```bash
python run_daily_refresh.py
```

### 5. Deploy to Azure Functions
```bash
az login
func azure functionapp publish <your-function-app-name>
```

### 6. Build Frontend
```bash
cd frontend
npm run build
```

---

## File Count Summary

| Component | Files | Size |
|-----------|-------|------|
| Backend Python | 40+ | ~2-3 MB |
| Frontend Source | 30+ | ~500 KB |
| Config Files | 8 | ~50 KB |
| **TOTAL TO MOVE** | **80+** | **~3 MB** |

---

## Critical Files (Don't Forget!)

### These have credentials/config:
- ✅ `planning_intelligence/local.settings.json` - **BLOB_CONNECTION_STRING**
- ✅ `frontend/.env` - **REACT_APP_API_URL**

### These are required for deployment:
- ✅ `planning_intelligence/requirements.txt` - Python packages
- ✅ `frontend/package.json` - npm packages
- ✅ `planning_intelligence/host.json` - Azure Functions config

---

## Verification After Move

```bash
# Backend
cd planning_intelligence
ls -la *.py | wc -l  # Should show 40+ files
cat local.settings.json | grep BLOB_CONNECTION_STRING  # Should show connection string

# Frontend
cd ../frontend
cat package.json | grep "name"  # Should show package name
cat .env | grep REACT_APP_API_URL  # Should show API URL
```

---

## Next: Deploy to Azure

Once files are on org laptop:

1. **Set Azure Functions Environment Variables**
   ```bash
   az functionapp config appsettings set \
     --name <function-app-name> \
     --resource-group <resource-group> \
     --settings BLOB_CONNECTION_STRING="..." BLOB_CONTAINER_NAME="planning-data"
   ```

2. **Deploy Backend**
   ```bash
   cd planning_intelligence
   func azure functionapp publish <function-app-name>
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend
   npm run build
   # Upload build/ folder to your hosting
   ```

4. **Trigger Daily Refresh**
   ```bash
   curl -X POST https://<function-app>.azurewebsites.net/api/daily-refresh?code=<function-key>
   ```

---

## Support

- See `DEPLOYMENT_GUIDE_ORG_LAPTOP.md` for detailed guide
- See `LOCAL_TESTING_SETUP.md` for local testing
- See `FUNCTION_APP_INTEGRATION_GUIDE.md` for integration details

