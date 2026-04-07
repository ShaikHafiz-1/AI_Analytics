# GitLab Setup & Local Development Guide

This guide walks you through setting up the Planning Intelligence project on your organization's GitLab and testing locally with Blob Storage data.

## Step 1: GitLab Repository Setup

### 1.1 Create GitLab Project

1. Go to your organization's GitLab instance
2. Click **New project**
3. Choose **Create blank project**
4. Fill in:
   - **Project name**: `planning-intelligence`
   - **Project slug**: `planning-intelligence`
   - **Visibility**: Private (or Internal)
   - **Initialize with README**: No (we have one)
5. Click **Create project**

### 1.2 Add Remote and Push Code

```bash
# Clone the current repo (if not already done)
git clone <current-repo-url>
cd planning-intelligence

# Add GitLab as new remote
git remote add gitlab https://gitlab.your-org.com/your-group/planning-intelligence.git

# Push all branches to GitLab
git push -u gitlab main
git push -u gitlab --all
git push -u gitlab --tags
```

### 1.3 Verify Push

Go to your GitLab project and verify:
- ✅ All branches are visible
- ✅ README.md is displayed
- ✅ File structure is correct
- ✅ No sensitive files (`.env`, `local.settings.json`)

## Step 2: Clone on Organization Laptop

### 2.1 Clone Repository

```bash
# Clone from GitLab
git clone https://gitlab.your-org.com/your-group/planning-intelligence.git
cd planning-intelligence
```

### 2.2 Verify Structure

```bash
# Check directory structure
ls -la

# Should see:
# - planning_intelligence/
# - frontend/
# - .github/
# - README.md
# - GITLAB_SETUP.md
```

## Step 3: Backend Setup (Local Testing)

### 3.1 Install Prerequisites

**Windows:**
```powershell
# Install Python 3.11+ (if not already installed)
# Download from https://www.python.org/downloads/

# Verify installation
python --version  # Should be 3.11+

# Install Azure Functions Core Tools
# Download from https://github.com/Azure/azure-functions-core-tools/releases
# Or use Chocolatey:
choco install azure-functions-core-tools-4
```

**macOS:**
```bash
# Install Python 3.11+
brew install python@3.11

# Install Azure Functions Core Tools
brew tap azure/tap
brew install azure-functions-core-tools@4
```

**Linux:**
```bash
# Install Python 3.11+
sudo apt-get install python3.11 python3.11-venv

# Install Azure Functions Core Tools
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### 3.2 Setup Python Environment

```bash
cd planning_intelligence

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3.3 Configure Blob Storage Connection

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Blob Storage credentials
# Open .env and update:
# BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
# BLOB_CONTAINER_NAME=planning-data
# BLOB_CURRENT_FILE=current.csv
# BLOB_PREVIOUS_FILE=previous.csv
```

**Getting Blob Storage Connection String:**
1. Go to Azure Portal
2. Navigate to your Storage Account
3. Click **Access keys** (left sidebar)
4. Copy **Connection string** from Key 1
5. Paste into `.env`

### 3.4 Create local.settings.json

```bash
# Create local.settings.json for Azure Functions
cat > local.settings.json << 'EOF'
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_WORKER_RUNTIME_VERSION": "3.11"
  },
  "Host": {
    "CORS": "http://localhost:3000",
    "CORSCredentials": true
  }
}
EOF
```

### 3.5 Run Backend Locally

```bash
# Start Azure Functions
func start

# You should see:
# Azure Functions Core Tools
# Worker process started and initialized.
# Http Functions:
#   planning-intelligence: [POST] http://localhost:7071/api/planning-intelligence
#   planning-dashboard: [POST] http://localhost:7071/api/planning-dashboard
#   planning-dashboard-v2: [POST] http://localhost:7071/api/planning-dashboard-v2
#   daily-refresh: [POST] http://localhost:7071/api/daily-refresh
#   explain: [POST] http://localhost:7071/api/explain
```

### 3.6 Test Backend with Blob Data

```bash
# In a new terminal, test the daily-refresh endpoint
curl -X POST http://localhost:7071/api/daily-refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "blob"}'

# Expected response:
# {
#   "status": "ok",
#   "lastRefreshedAt": "2026-04-05T10:30:00Z",
#   "totalRecords": 1234,
#   "changedRecordCount": 45,
#   "planningHealth": 87
# }
```

## Step 4: Frontend Setup (Local Testing)

### 4.1 Install Node.js

**Windows/macOS:**
- Download from https://nodejs.org/ (LTS version 18+)
- Run installer

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4.2 Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env:
# REACT_APP_API_URL=http://localhost:7071/api
# REACT_APP_API_KEY=  (leave empty for local testing)
# REACT_APP_USE_MOCK=false
```

### 4.3 Run Frontend Locally

```bash
# Start development server
npm start

# Browser will open at http://localhost:3000
# You should see the Planning Intelligence Dashboard
```

## Step 5: End-to-End Testing

### 5.1 Test Data Flow

1. **Backend running**: `func start` in `planning_intelligence/`
2. **Frontend running**: `npm start` in `frontend/`
3. **Open browser**: http://localhost:3000

### 5.2 Verify Dashboard

You should see:
- ✅ Planning Health Card with score
- ✅ Forecast Card with trend data
- ✅ Risk Card with high-risk records
- ✅ AI Insight Card with analysis
- ✅ Datacenter and Material Group breakdowns
- ✅ All data loaded from Blob Storage

### 5.3 Test Copilot Panel

1. Click **Ask Copilot** button
2. Ask a question: "What changed most?"
3. Verify response is grounded in dashboard data

### 5.4 Test Drill-Down

1. Click on a location in Datacenter Card
2. Verify drill-down panel opens with details
3. Check material group breakdown

## Step 6: Running Tests

### 6.1 Backend Tests

```bash
cd planning_intelligence

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_normalizer.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### 6.2 Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## Step 7: GitLab CI/CD Setup (Optional)

### 7.1 Add CI/CD Variables

1. Go to GitLab project
2. Click **Settings** → **CI/CD** → **Variables**
3. Add these variables:

| Variable | Value | Protected |
|----------|-------|-----------|
| `AZURE_STORAGE_CONNECTION_STRING` | Your Blob Storage connection string | ✅ Yes |
| `REACT_APP_API_URL` | Your Azure Functions URL | ✅ Yes |
| `REACT_APP_API_KEY` | Your Azure Function key | ✅ Yes |
| `AZUREAPPSERVICE_PUBLISHPROFILE` | Your publish profile XML | ✅ Yes |

### 7.2 Create .gitlab-ci.yml

```yaml
stages:
  - test
  - build
  - deploy

# Backend tests
backend_test:
  stage: test
  image: python:3.11
  script:
    - cd planning_intelligence
    - pip install -r requirements.txt
    - pytest tests/ -v
  only:
    - main
    - merge_requests

# Frontend tests
frontend_test:
  stage: test
  image: node:18
  script:
    - cd frontend
    - npm install
    - npm test -- --coverage
  only:
    - main
    - merge_requests

# Build backend
backend_build:
  stage: build
  image: python:3.11
  script:
    - cd planning_intelligence
    - pip install -r requirements.txt --target=".python_packages/lib/site-packages"
    - zip -r ../release.zip . --exclude "tests/*" "__pycache__/*" "*.pyc"
  artifacts:
    paths:
      - release.zip
  only:
    - main

# Build frontend
frontend_build:
  stage: build
  image: node:18
  script:
    - cd frontend
    - npm install
    - npm run build
  artifacts:
    paths:
      - frontend/build
  only:
    - main
```

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'azure'"**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**"Connection refused" when accessing Blob Storage**
- Verify `BLOB_CONNECTION_STRING` in `.env`
- Check Blob Storage account is accessible
- Verify firewall rules allow your IP

**"Function not found" error**
```bash
# Restart Azure Functions
func start
```

### Frontend Issues

**"Cannot find module" errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**"API error 404"**
- Verify backend is running: `func start`
- Check `REACT_APP_API_URL` in `.env`
- Verify endpoint path is correct

**"CORS error"**
- Check `Host.CORS` in `local.settings.json`
- Should be: `"http://localhost:3000"`

### Git Issues

**"Permission denied" when pushing to GitLab**
```bash
# Setup SSH key (recommended)
ssh-keygen -t ed25519 -C "your-email@org.com"
# Add public key to GitLab: Settings → SSH Keys

# Or use personal access token
git remote set-url gitlab https://oauth2:YOUR_TOKEN@gitlab.your-org.com/your-group/planning-intelligence.git
```

## Next Steps

1. ✅ Clone repository on organization laptop
2. ✅ Setup backend with Blob Storage connection
3. ✅ Setup frontend and verify dashboard
4. ✅ Run tests locally
5. ✅ Configure GitLab CI/CD (optional)
6. ✅ Deploy to Azure (see main README.md)

## Support

For issues:
1. Check troubleshooting section above
2. Review Azure Functions logs: `func start` output
3. Check browser console (F12) for frontend errors
4. Review GitLab CI/CD logs in project

## Quick Reference

```bash
# Backend
cd planning_intelligence
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
func start

# Frontend (new terminal)
cd frontend
npm start

# Tests
cd planning_intelligence && pytest tests/ -v
cd ../frontend && npm test

# Git
git add .
git commit -m "Your message"
git push gitlab main
```
