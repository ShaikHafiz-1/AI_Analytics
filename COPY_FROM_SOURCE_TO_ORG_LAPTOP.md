# Copy Files from Source to Org Laptop

## Your Setup
- **Source**: `D:\MA_Power_Automate\AI_Analytics\AI_Analytics` (the repo on this machine)
- **Destination**: `C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready` (org laptop)

---

## Quick PowerShell Commands

### Copy All Backend Python Files
```powershell
Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence\*.py" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
```

### Copy Backend Config Files
```powershell
Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence\.env" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force

Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence\local.settings.json" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force

Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence\requirements.txt" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force

Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence\host.json" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence" -Force
```

### Copy All Frontend Files
```powershell
Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\frontend\*" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\frontend" -Recurse -Force
```

### Copy Sample Data
```powershell
Copy-Item -Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\sample_data\*" -Destination "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\sample_data" -Recurse -Force
```

---

## All-in-One Script

Save this as `copy_to_org_laptop.ps1`:

```powershell
# Define paths
$source = "D:\MA_Power_Automate\AI_Analytics\AI_Analytics"
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

Write-Host "Copying from: $source"
Write-Host "Copying to: $dest"
Write-Host ""

# Create destination folders if they don't exist
Write-Host "Creating destination folders..."
New-Item -ItemType Directory -Path "$dest\planning_intelligence" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest\frontend" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest\sample_data" -Force | Out-Null

# Copy backend Python files
Write-Host "Copying backend Python files..."
Copy-Item -Path "$source\planning_intelligence\*.py" -Destination "$dest\planning_intelligence" -Force
$pyCount = (Get-ChildItem "$dest\planning_intelligence\*.py" | Measure-Object).Count
Write-Host "✓ Copied $pyCount Python files"

# Copy backend config files
Write-Host "Copying backend config files..."
Copy-Item -Path "$source\planning_intelligence\.env" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\local.settings.json" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\requirements.txt" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\host.json" -Destination "$dest\planning_intelligence" -Force
Write-Host "✓ Copied config files (.env, local.settings.json, requirements.txt, host.json)"

# Copy frontend files
Write-Host "Copying frontend files..."
Copy-Item -Path "$source\frontend\*" -Destination "$dest\frontend" -Recurse -Force
$feCount = (Get-ChildItem "$dest\frontend\src" -Recurse | Measure-Object).Count
Write-Host "✓ Copied $feCount frontend files"

# Copy sample data
Write-Host "Copying sample data..."
Copy-Item -Path "$source\sample_data\*" -Destination "$dest\sample_data" -Recurse -Force
$sampleCount = (Get-ChildItem "$dest\sample_data\*" | Measure-Object).Count
Write-Host "✓ Copied $sampleCount sample data files"

Write-Host ""
Write-Host "✓ All files copied successfully!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. cd $dest"
Write-Host "2. cd planning_intelligence && pip install -r requirements.txt"
Write-Host "3. cd ../frontend && npm install"
Write-Host "4. cd ../planning_intelligence && func start"
Write-Host "5. In new terminal: cd frontend && npm start"
```

### Run the Script
```powershell
# Navigate to the source directory
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics

# Run the script
.\copy_to_org_laptop.ps1
```

---

## Step-by-Step Manual Copy

If you prefer to copy manually:

### Step 1: Copy Backend Files
```powershell
$source = "D:\MA_Power_Automate\AI_Analytics\AI_Analytics"
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

# Copy all Python files
Copy-Item -Path "$source\planning_intelligence\*.py" -Destination "$dest\planning_intelligence" -Force

# Copy config files
Copy-Item -Path "$source\planning_intelligence\.env" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\local.settings.json" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\requirements.txt" -Destination "$dest\planning_intelligence" -Force
Copy-Item -Path "$source\planning_intelligence\host.json" -Destination "$dest\planning_intelligence" -Force
```

### Step 2: Copy Frontend Files
```powershell
Copy-Item -Path "$source\frontend\*" -Destination "$dest\frontend" -Recurse -Force
```

### Step 3: Copy Sample Data
```powershell
Copy-Item -Path "$source\sample_data\*" -Destination "$dest\sample_data" -Recurse -Force
```

### Step 4: Verify Files
```powershell
# Check backend
Get-ChildItem "$dest\planning_intelligence\*.py" | Measure-Object
Get-ChildItem "$dest\planning_intelligence\*.json"
Get-ChildItem "$dest\planning_intelligence\.env"

# Check frontend
Get-ChildItem "$dest\frontend\src" -Recurse | Measure-Object

# Check sample data
Get-ChildItem "$dest\sample_data\*"
```

---

## Verification Checklist

After copying, verify:

```powershell
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

# Backend files
Write-Host "Backend Python files:"
Get-ChildItem "$dest\planning_intelligence\*.py" | Select-Object Name | Format-Table

Write-Host "Backend config files:"
Get-ChildItem "$dest\planning_intelligence\*.json", "$dest\planning_intelligence\.env", "$dest\planning_intelligence\requirements.txt" | Select-Object Name

# Frontend files
Write-Host "Frontend files:"
Get-ChildItem "$dest\frontend\src" -Recurse | Measure-Object

# Sample data
Write-Host "Sample data files:"
Get-ChildItem "$dest\sample_data\*" | Select-Object Name
```

---

## Expected File Counts

After successful copy:

| Folder | Expected Count |
|--------|-----------------|
| `planning_intelligence\*.py` | 40+ Python files |
| `planning_intelligence\*.json` | 2 files (local.settings.json, host.json) |
| `planning_intelligence\.env` | 1 file |
| `planning_intelligence\requirements.txt` | 1 file |
| `frontend\src\**` | 30+ TypeScript/React files |
| `sample_data\*` | 2 CSV files |

---

## Next Steps After Copying

### 1. Install Backend Dependencies
```powershell
cd "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready\planning_intelligence"
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd "..\frontend"
npm install
```

### 3. Test Blob Connection
```powershell
cd "..\planning_intelligence"
python test_blob_real_data.py
```

Expected output:
```
✅ SUCCESS: Loaded 13148 current rows and 13148 previous rows
```

### 4. Start Backend
```powershell
func start
```

Expected output:
```
Functions:
  planning_intelligence_nlp: [POST,OPTIONS] http://localhost:7071/api/planning_intelligence_nlp
  planning-dashboard-v2: [POST,OPTIONS] http://localhost:7071/api/planning-dashboard-v2
  ...
```

### 5. Start Frontend (in new terminal)
```powershell
cd "..\frontend"
npm start
```

Expected output:
```
Server running on port 3000
```

### 6. Open Browser
```
http://localhost:3000
```

You should see the dashboard with real blob data (13,148 records).

---

## Troubleshooting

### Error: "Path not found"
Make sure the source path exists:
```powershell
Test-Path "D:\MA_Power_Automate\AI_Analytics\AI_Analytics\planning_intelligence"
```

Should return `True`.

### Error: "Access Denied"
Run PowerShell as Administrator:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Run the copy commands

### Error: "Destination path has spaces"
The path with spaces is fine as long as it's in quotes. Make sure you're using:
```powershell
$dest = "C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"
```

Not:
```powershell
$dest = C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready
```

---

## Quick Copy Command (One-Liner)

If you want to copy everything in one command:

```powershell
$s="D:\MA_Power_Automate\AI_Analytics\AI_Analytics"; $d="C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"; Copy-Item "$s\planning_intelligence\*.py" "$d\planning_intelligence" -Force; Copy-Item "$s\planning_intelligence\.env" "$d\planning_intelligence" -Force; Copy-Item "$s\planning_intelligence\local.settings.json" "$d\planning_intelligence" -Force; Copy-Item "$s\planning_intelligence\requirements.txt" "$d\planning_intelligence" -Force; Copy-Item "$s\planning_intelligence\host.json" "$d\planning_intelligence" -Force; Copy-Item "$s\frontend\*" "$d\frontend" -Recurse -Force; Copy-Item "$s\sample_data\*" "$d\sample_data" -Recurse -Force; Write-Host "Done!"
```

---

## Summary

**Source**: `D:\MA_Power_Automate\AI_Analytics\AI_Analytics`  
**Destination**: `C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready`

**Copy command**:
```powershell
$s="D:\MA_Power_Automate\AI_Analytics\AI_Analytics"
$d="C:\Users\v-syedfar\Downloads\AI_Analytics-feature-local-test-ready (3)\AI_Analytics-feature-local-test-ready"

Copy-Item "$s\planning_intelligence\*.py" "$d\planning_intelligence" -Force
Copy-Item "$s\planning_intelligence\.env" "$d\planning_intelligence" -Force
Copy-Item "$s\planning_intelligence\local.settings.json" "$d\planning_intelligence" -Force
Copy-Item "$s\planning_intelligence\requirements.txt" "$d\planning_intelligence" -Force
Copy-Item "$s\planning_intelligence\host.json" "$d\planning_intelligence" -Force
Copy-Item "$s\frontend\*" "$d\frontend" -Recurse -Force
Copy-Item "$s\sample_data\*" "$d\sample_data" -Recurse -Force
```

Done! All files copied to org laptop.

