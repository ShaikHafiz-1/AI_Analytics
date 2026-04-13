# Windows Copy Commands for File Migration

You're on Windows, so use PowerShell commands instead of `cp` (which is Linux).

## Quick Copy Commands (PowerShell)

### Copy All Python Files
```powershell
Copy-Item -Path "planning_intelligence\*.py" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
```

### Copy All Frontend Files
```powershell
Copy-Item -Path "frontend\*" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend" -Recurse -Force
```

### Copy Configuration Files
```powershell
Copy-Item -Path "planning_intelligence\.env" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\local.settings.json" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\requirements.txt" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\host.json" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
```

---

## Easier Way: Use Git Clone (Recommended)

Since you already have the code in git, just clone it:

```powershell
cd C:\Users\v-syedfar\Downloads
git clone https://github.com/ShaikHafiz-1/AI_Analytics.git planning-intelligence-copilot
cd planning-intelligence-copilot
git checkout feature/local-test-ready
```

This is **much faster** and ensures you get everything correctly.

---

## Step-by-Step: Copy Using PowerShell

### Step 1: Create Destination Folders
```powershell
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

# Create folders if they don't exist
New-Item -ItemType Directory -Path "$dest\planning_intelligence" -Force
New-Item -ItemType Directory -Path "$dest\frontend" -Force
New-Item -ItemType Directory -Path "$dest\sample_data" -Force
```

### Step 2: Copy Backend Files
```powershell
# Copy all Python files
Copy-Item -Path "planning_intelligence\*.py" -Destination "$dest\planning_intelligence" -Force

# Copy config files
Copy-Item -Path "planning_intelligence\.env" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\local.settings.json" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\requirements.txt" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\host.json" -Destination "$dest\planning_intelligence" -Force
```

### Step 3: Copy Frontend Files
```powershell
# Copy entire frontend folder
Copy-Item -Path "frontend\*" -Destination "$dest\frontend" -Recurse -Force
```

### Step 4: Copy Sample Data
```powershell
# Copy sample data
Copy-Item -Path "sample_data\*" -Destination "$dest\sample_data" -Recurse -Force
```

### Step 5: Verify Files Copied
```powershell
# Check backend files
Get-ChildItem "$dest\planning_intelligence\*.py" | Measure-Object

# Check frontend files
Get-ChildItem "$dest\frontend\src" -Recurse | Measure-Object

# Check config files
Get-ChildItem "$dest\planning_intelligence\*.json"
Get-ChildItem "$dest\planning_intelligence\.env"
```

---

## All-in-One Script

Save this as `copy_files.ps1` and run it:

```powershell
# Set destination
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

# Create folders
New-Item -ItemType Directory -Path "$dest\planning_intelligence" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest\frontend" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest\sample_data" -Force | Out-Null

# Copy backend
Write-Host "Copying backend files..."
Copy-Item -Path "planning_intelligence\*.py" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\.env" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\local.settings.json" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\requirements.txt" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "planning_intelligence\host.json" -Destination "$dest\planning_intelligence" -Force

# Copy frontend
Write-Host "Copying frontend files..."
Copy-Item -Path "frontend\*" -Destination "$dest\frontend" -Recurse -Force

# Copy sample data
Write-Host "Copying sample data..."
Copy-Item -Path "sample_data\*" -Destination "$dest\sample_data" -Recurse -Force

# Verify
Write-Host "Verification:"
Write-Host "Backend files: $(Get-ChildItem "$dest\planning_intelligence\*.py" | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Host "Frontend files: $(Get-ChildItem "$dest\frontend\src" -Recurse | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Host "Done!"
```

Run it:
```powershell
.\copy_files.ps1
```

---

## Troubleshooting

### Error: "Path with spaces"
If your path has spaces, wrap it in quotes:
```powershell
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"
Copy-Item -Path "planning_intelligence\*.py" -Destination "$dest\planning_intelligence" -Force
```

### Error: "Access Denied"
Run PowerShell as Administrator:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Run the copy commands

### Error: "Cannot find path"
Make sure you're in the correct directory:
```powershell
# Check current directory
Get-Location

# Should show: D:\MA_Power_Automate\AI_Analytics\AI_Analytics (or similar)

# If not, navigate to it
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics
```

---

## Recommended: Use Git Instead

This is the **easiest and most reliable** way:

```powershell
# Navigate to downloads
cd C:\Users\v-syedfar\Downloads

# Clone the repository
git clone https://github.com/ShaikHafiz-1/AI_Analytics.git planning-intelligence-copilot

# Navigate to the cloned folder
cd planning-intelligence-copilot

# Checkout the feature branch
git checkout feature/local-test-ready

# Verify files
Get-ChildItem planning_intelligence\*.py | Measure-Object
Get-ChildItem frontend\src -Recurse | Measure-Object
```

**Advantages of Git**:
- ✅ Gets all files correctly
- ✅ Gets all subdirectories
- ✅ Gets all configuration files
- ✅ No manual copying needed
- ✅ Easy to update later with `git pull`

---

## Next Steps After Copying

1. **Install dependencies**:
   ```powershell
   cd planning_intelligence
   pip install -r requirements.txt
   
   cd ..\frontend
   npm install
   ```

2. **Test blob connection**:
   ```powershell
   cd ..\planning_intelligence
   python test_blob_real_data.py
   ```

3. **Start backend**:
   ```powershell
   func start
   ```

4. **Start frontend** (in new terminal):
   ```powershell
   cd frontend
   npm start
   ```

---

## Files You Need to Copy

**Backend** (planning_intelligence/):
- ✅ All `.py` files (40+ files)
- ✅ `.env` (has credentials)
- ✅ `local.settings.json` (has credentials)
- ✅ `requirements.txt` (dependencies)
- ✅ `host.json` (Azure config)

**Frontend** (frontend/):
- ✅ All files in `src/` folder
- ✅ `package.json` (dependencies)
- ✅ `.env` (API URL)
- ✅ `public/` folder

**Sample Data** (sample_data/):
- ✅ `current.csv`
- ✅ `previous.csv`

**Don't copy**:
- ❌ `node_modules/` (will be generated by `npm install`)
- ❌ `build/` (will be generated by `npm run build`)
- ❌ `.venv/` (will be generated by `pip install`)
- ❌ `__pycache__/` (will be generated by Python)

