# Deployment & Migration Checklist

Use this checklist to ensure everything is ready for GitLab migration and local testing.

## Pre-Migration Checklist

### Code Consolidation
- [x] Removed `dashboard_ui/` folder
- [x] Updated `.gitignore` to remove dashboard_ui references
- [x] Verified no references to dashboard_ui in codebase
- [x] Confirmed `frontend/` is the only UI version

### Documentation
- [x] Created `README.md` with full project documentation
- [x] Created `GITLAB_SETUP.md` with setup instructions
- [x] Created `QUICK_START.md` with quick reference
- [x] Created `CONSOLIDATION_SUMMARY.md` with consolidation details
- [x] Created `DEPLOYMENT_CHECKLIST.md` (this file)

### Backend Verification
- [x] `planning_intelligence/requirements.txt` is complete
- [x] `planning_intelligence/.env.example` has all required variables
- [x] `planning_intelligence/local.settings.json` template exists
- [x] All Python modules are present
- [x] Tests are in `planning_intelligence/tests/`

### Frontend Verification
- [x] `frontend/package.json` has all dependencies
- [x] `frontend/tsconfig.json` is configured
- [x] `frontend/.env.example` has all required variables
- [x] All React components are present
- [x] TypeScript types are defined

### Git Configuration
- [x] `.gitignore` excludes sensitive files
- [x] `.gitignore` excludes node_modules
- [x] `.gitignore` excludes .venv
- [x] `.gitignore` excludes local.settings.json
- [x] `.gitignore` excludes .env files

---

## GitLab Migration Checklist

### Repository Setup
- [ ] Create GitLab project in organization
- [ ] Set project visibility to Private/Internal
- [ ] Add remote: `git remote add gitlab <gitlab-url>`
- [ ] Push all branches: `git push -u gitlab main`
- [ ] Verify all files are in GitLab
- [ ] Verify no sensitive files are committed

### Branch Protection (Optional)
- [ ] Protect `main` branch
- [ ] Require merge request reviews
- [ ] Require status checks to pass
- [ ] Dismiss stale reviews

### CI/CD Setup (Optional)
- [ ] Create `.gitlab-ci.yml` (see GITLAB_SETUP.md)
- [ ] Add CI/CD variables:
  - [ ] `AZURE_STORAGE_CONNECTION_STRING`
  - [ ] `REACT_APP_API_URL`
  - [ ] `REACT_APP_API_KEY`
  - [ ] `AZUREAPPSERVICE_PUBLISHPROFILE`
- [ ] Test CI/CD pipeline
- [ ] Verify build succeeds
- [ ] Verify tests pass

### Documentation
- [ ] Add link to README.md in GitLab project description
- [ ] Create wiki page with setup instructions
- [ ] Add GITLAB_SETUP.md to wiki
- [ ] Add QUICK_START.md to wiki

---

## Local Development Setup Checklist

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] Azure Functions Core Tools installed
- [ ] Azure Storage Account created
- [ ] Blob Storage container created

### Backend Setup
- [ ] Clone repository from GitLab
- [ ] Navigate to `planning_intelligence/`
- [ ] Create virtual environment: `python -m venv .venv`
- [ ] Activate virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Add Blob Storage connection string to `.env`
- [ ] Create `local.settings.json`
- [ ] Run backend: `func start`
- [ ] Verify endpoints are accessible

### Frontend Setup
- [ ] Navigate to `frontend/`
- [ ] Install dependencies: `npm install`
- [ ] Copy `.env.example` to `.env`
- [ ] Set `REACT_APP_API_URL=http://localhost:7071/api`
- [ ] Set `REACT_APP_USE_MOCK=false`
- [ ] Run frontend: `npm start`
- [ ] Verify dashboard loads

### Testing
- [ ] Backend tests pass: `pytest tests/ -v`
- [ ] Frontend builds: `npm run build`
- [ ] Dashboard displays data from Blob Storage
- [ ] Copilot panel works
- [ ] Drill-down panels work
- [ ] All cards display correctly

---

## Blob Storage Configuration Checklist

### Azure Portal Setup
- [ ] Storage Account created
- [ ] Blob Storage container created (name: `planning-data`)
- [ ] Access keys generated
- [ ] Connection string copied

### Data Files
- [ ] `current.csv` uploaded to Blob Storage
- [ ] `previous.csv` uploaded to Blob Storage
- [ ] Files contain valid planning data
- [ ] CSV format matches expected schema

### Environment Configuration
- [ ] `BLOB_CONNECTION_STRING` set in `.env`
- [ ] `BLOB_CONTAINER_NAME` set to `planning-data`
- [ ] `BLOB_CURRENT_FILE` set to `current.csv`
- [ ] `BLOB_PREVIOUS_FILE` set to `previous.csv`
- [ ] Connection tested successfully

---

## Testing Checklist

### Backend Tests
- [ ] Run: `cd planning_intelligence && pytest tests/ -v`
- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No warnings or errors

### Frontend Tests
- [ ] Run: `cd frontend && npm test`
- [ ] All tests pass
- [ ] No console errors
- [ ] No TypeScript errors

### Integration Tests
- [ ] Backend running: `func start`
- [ ] Frontend running: `npm start`
- [ ] Dashboard loads at `http://localhost:3000`
- [ ] Data loads from Blob Storage
- [ ] All cards display correctly
- [ ] Copilot panel responds to questions
- [ ] Drill-down panels open correctly

### API Tests
- [ ] Test `/api/daily-refresh` endpoint
- [ ] Test `/api/planning-dashboard-v2` endpoint
- [ ] Test `/api/explain` endpoint
- [ ] All endpoints return valid JSON
- [ ] Error handling works correctly

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests pass locally
- [ ] No console errors or warnings
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Version number updated (if applicable)

### Azure Functions Deployment
- [ ] Publish profile configured
- [ ] GitHub Secrets added:
  - [ ] `AZUREAPPSERVICE_PUBLISHPROFILE`
  - [ ] `REACT_APP_API_URL`
  - [ ] `REACT_APP_API_KEY`
- [ ] CI/CD pipeline configured
- [ ] Backend deployment successful
- [ ] Endpoints accessible in Azure

### Frontend Deployment
- [ ] Storage account configured
- [ ] GitHub Secrets added:
  - [ ] `AZURE_STORAGE_CONNECTION_STRING`
- [ ] CI/CD pipeline configured
- [ ] Frontend deployment successful
- [ ] Dashboard accessible at production URL

### Post-Deployment
- [ ] Test production endpoints
- [ ] Verify data loads correctly
- [ ] Check error handling
- [ ] Monitor logs for errors
- [ ] Notify team of deployment

---

## Team Onboarding Checklist

### Documentation
- [ ] Share README.md with team
- [ ] Share QUICK_START.md with team
- [ ] Share GITLAB_SETUP.md with team
- [ ] Add links to GitLab wiki
- [ ] Create team documentation

### Access
- [ ] Team members have GitLab access
- [ ] Team members have Azure access
- [ ] Team members have Blob Storage access
- [ ] SSH keys configured (if using SSH)

### Local Setup
- [ ] Each team member clones repository
- [ ] Each team member completes local setup
- [ ] Each team member runs tests successfully
- [ ] Each team member can start backend and frontend

### Training
- [ ] Explain project structure
- [ ] Explain data flow
- [ ] Explain API endpoints
- [ ] Explain deployment process
- [ ] Answer questions

---

## Troubleshooting Checklist

### If Backend Won't Start
- [ ] Check Python version: `python --version`
- [ ] Check virtual environment is activated
- [ ] Check dependencies installed: `pip list`
- [ ] Check `.env` file exists and is valid
- [ ] Check `local.settings.json` exists
- [ ] Check Blob Storage connection string
- [ ] Check Azure Functions Core Tools installed

### If Frontend Won't Start
- [ ] Check Node.js version: `node --version`
- [ ] Check npm version: `npm --version`
- [ ] Check dependencies installed: `npm list`
- [ ] Check `.env` file exists and is valid
- [ ] Check `REACT_APP_API_URL` is correct
- [ ] Check backend is running
- [ ] Clear cache: `rm -rf node_modules && npm install`

### If Tests Fail
- [ ] Check all dependencies installed
- [ ] Check Python/Node versions
- [ ] Run tests with verbose output: `pytest -v` or `npm test -- --verbose`
- [ ] Check test data files exist
- [ ] Check environment variables set

### If Deployment Fails
- [ ] Check GitHub Secrets are set correctly
- [ ] Check CI/CD logs for errors
- [ ] Check Azure credentials are valid
- [ ] Check storage account is accessible
- [ ] Check function app exists in Azure

---

## Sign-Off

- [ ] All checklist items completed
- [ ] Project ready for GitLab migration
- [ ] Team ready for local development
- [ ] Documentation complete and reviewed
- [ ] Deployment process tested

**Completed by**: ________________  
**Date**: ________________  
**Notes**: ________________________________________________

---

## Quick Links

- **README.md** - Full project documentation
- **GITLAB_SETUP.md** - GitLab setup guide
- **QUICK_START.md** - Quick reference
- **CONSOLIDATION_SUMMARY.md** - What was changed
- **planning_intelligence/DESIGN.md** - Backend architecture
- **frontend/tsconfig.json** - TypeScript configuration

---

## Support

For issues or questions:
1. Check QUICK_START.md troubleshooting section
2. Check GITLAB_SETUP.md troubleshooting section
3. Review backend logs: `func start` output
4. Review frontend logs: browser console (F12)
5. Check Azure Portal for function app logs
