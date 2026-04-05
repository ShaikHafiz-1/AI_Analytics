# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Azure Storage Account with Blob Storage credentials

### Backend (Terminal 1)

```bash
cd planning_intelligence

# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Blob Storage connection string

# Run
func start
```

**Expected output:**
```
Http Functions:
  planning-intelligence: [POST] http://localhost:7071/api/planning-intelligence
  planning-dashboard-v2: [POST] http://localhost:7071/api/planning-dashboard-v2
  daily-refresh: [POST] http://localhost:7071/api/daily-refresh
  explain: [POST] http://localhost:7071/api/explain
```

### Frontend (Terminal 2)

```bash
cd frontend

# Setup
npm install
cp .env.example .env
# Edit .env:
# REACT_APP_API_URL=http://localhost:7071/api
# REACT_APP_USE_MOCK=false

# Run
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view planning-intelligence-frontend in the browser.
  Local:            http://localhost:3000
```

### Test (Terminal 3)

```bash
# Load data from Blob Storage
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'

# Open browser: http://localhost:3000
# You should see the dashboard with data
```

---

## Common Commands

### Backend

```bash
# Activate environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
func start

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_normalizer.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Deactivate environment
deactivate
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm build

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Clean install (if issues)
rm -rf node_modules package-lock.json
npm install
```

### Git

```bash
# Clone from GitLab
git clone https://gitlab.your-org.com/your-group/planning-intelligence.git

# Create feature branch
git checkout -b feature/your-feature

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitLab
git push origin feature/your-feature

# Create merge request in GitLab UI
```

---

## API Endpoints

### Load Data from Blob Storage
```bash
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'
```

### Get Dashboard Data
```bash
curl -X POST http://localhost:7071/api/planning-dashboard-v2 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Ask a Question (Copilot)
```bash
curl -X POST http://localhost:7071/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What changed most?",
    "context": {
      "planningHealth": 87,
      "changedRecordCount": 45,
      "totalRecords": 1234
    }
  }'
```

### Analyze Two Snapshots
```bash
curl -X POST http://localhost:7071/api/planning-intelligence \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "summary",
    "current_rows": [...],
    "previous_rows": [...]
  }'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `Cannot find module` (frontend) | `rm -rf node_modules && npm install` |
| `Connection refused` (Blob) | Check `.env` connection string |
| `CORS error` | Verify `REACT_APP_API_URL` in `.env` |
| `func start` not found | Install Azure Functions Core Tools |
| `npm start` not found | Install Node.js 18+ |
| `python` not found | Install Python 3.11+ |

---

## File Locations

| File | Purpose |
|------|---------|
| `planning_intelligence/.env` | Backend Blob Storage config |
| `planning_intelligence/local.settings.json` | Azure Functions local config |
| `frontend/.env` | Frontend API endpoint config |
| `README.md` | Full project documentation |
| `GITLAB_SETUP.md` | GitLab & local setup guide |
| `planning_intelligence/DESIGN.md` | Backend architecture |

---

## Environment Variables

### Backend (.env)
```env
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=
REACT_APP_USE_MOCK=false
```

---

## Project Structure

```
planning-intelligence/
├── planning_intelligence/     # Backend (Python)
│   ├── function_app.py       # Entry point
│   ├── requirements.txt       # Dependencies
│   └── tests/                # Unit tests
├── frontend/                 # Frontend (React + TypeScript)
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── .github/workflows/        # CI/CD
├── README.md                 # Full docs
├── GITLAB_SETUP.md          # Setup guide
└── QUICK_START.md           # This file
```

---

## Next Steps

1. ✅ Clone repository
2. ✅ Setup backend with Blob Storage
3. ✅ Setup frontend
4. ✅ Run `func start` and `npm start`
5. ✅ Open http://localhost:3000
6. ✅ Test with `/api/daily-refresh`
7. ✅ Push to GitLab
8. ✅ Configure CI/CD (optional)

---

## Support

- **Backend Issues**: Check `func start` output
- **Frontend Issues**: Check browser console (F12)
- **Blob Storage**: Verify connection string in `.env`
- **Git Issues**: See GITLAB_SETUP.md

---

## Useful Links

- [Azure Functions Documentation](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [GitLab Documentation](https://docs.gitlab.com/)
