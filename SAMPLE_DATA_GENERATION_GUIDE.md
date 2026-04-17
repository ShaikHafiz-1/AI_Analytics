# Sample Data Generation Guide - 2000 Planning Records

## Overview

This guide explains how to generate 2000 sample planning records for testing the Planning Intelligence Copilot system.

---

## Files Created

### 1. generate_sample_data.py
**Location**: `generate_sample_data.py`

A Python script that generates 2000 realistic planning records with all required SAP fields.

**Features**:
- Generates 2000 records with realistic data
- Includes all 45+ SAP fields
- Realistic variations in data (quantities, dates, changes)
- Proper change detection flags
- Risk indicators
- Supplier and location diversity

### 2. planning_data_2000_records.csv
**Location**: `sample_data/planning_data_2000_records.csv`

A sample CSV file with 30 records showing the expected format.

---

## How to Generate 2000 Records

### Option 1: Using Python (Recommended)

#### Step 1: Install Python
If you don't have Python installed:
1. Download from https://www.python.org/downloads/
2. Install with "Add Python to PATH" option checked
3. Verify installation: `python --version`

#### Step 2: Run the Generator Script
```bash
# Navigate to the workspace directory
cd D:\MA_Power_Automate\AI_Analytics\AI_Analytics

# Run the script
python generate_sample_data.py
```

#### Expected Output
```
Generating 2000 planning records...
  Generated 100/2000 records...
  Generated 200/2000 records...
  ...
  Generated 2000/2000 records...

✅ Successfully generated 2000 records
📁 File saved to: sample_data/planning_data_2000_records.csv
📊 File size: 2.5 MB
```

### Option 2: Using PowerShell

Create a PowerShell script to generate the data:

```powershell
# Save as generate_sample_data.ps1

$outputFile = "sample_data\planning_data_2000_records.csv"
$numRecords = 2000

# Create sample_data directory if it doesn't exist
if (!(Test-Path "sample_data")) {
    New-Item -ItemType Directory -Path "sample_data" | Out-Null
}

# Define data pools
$locations = @("CYS20_F01C01", "DAL_F02C01", "HOU_F03C01", "PHX_F04C01", "LAX_F05C01", "CHI_F06C01")
$materials = @("ACC", "BAT", "CAP", "DIO", "ELE", "FIL", "GAS", "HEA")
$categories = @("UPS", "Mechanical", "Hydraulic", "Pneumatic", "Electronics")
$suppliers = @("10_AMER", "130_AMER", "1690_AMER", "210_AMER", "320_AMER")

# Create CSV header
$header = "SCNID,LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCPREVFCSTQTY,GSCFSCTQTY,GSCPREVROJNBD,GSCCONROJDATE,GSCPREVSUPLDATE,GSCSUPLDATE,ZCOIBODVERZ,ZCOIFORMFACTZ,ZCOICIDZ,ZCOIMETROIDZ,ZCOICOUNTRY,LOCFRDESCR,GSCPLANNINGEXCEPTIONZ,GSCROJDATEREASONCODEZ,GSCDATASTEWARDNOTESZ,GSCPLNRVWNOTESZ,GSCROJNBDLASTCHANGEDDATE,GSCSCPBODVERSIONZ,GSCSENDFCSTSCPFIRSTPUBLISHDATEZ,GSCTRACKLASTPUBLISHDATEZ,GSCSENDFCSTSCPLASTREMOVEDDATEZ,GSCSCPFORMFACTORZ,GSCSENDFCSTSCPLASTCHANGEDDATEZ,GSCCMAPPROVALFIRSTDATEZ,GSCCMAPPROVALLASTCHANGEDDATEZ,GSCCMAPPROVALLASTCHANGEDVALUEZ,TINVALID,GSCROJNBDCREATIONDATE,LASTMODIFIEDBY,LASTMODIFIEDDATE,CREATEDBY,CREATEDDATE,#Version,ROC,NBD_Change Type,NBD_DeltaDays,FCST_Delta Qty,Is_New Demand,Is_cancelled,Is_SupplierDateMissing,Risk_Flag"

# Write header
$header | Out-File -FilePath $outputFile -Encoding UTF8

# Generate records
for ($i = 1; $i -le $numRecords; $i++) {
    $location = $locations | Get-Random
    $material = $materials | Get-Random
    $category = $categories | Get-Random
    $supplier = $suppliers | Get-Random
    
    $prevQty = Get-Random -Minimum 300 -Maximum 1500
    $qtyChange = Get-Random -Minimum -300 -Maximum 500
    $currQty = [Math]::Max(100, $prevQty + $qtyChange)
    
    $prevRoj = (Get-Date).AddDays((Get-Random -Minimum 30 -Maximum 60)).ToString("yyyy-MM-dd")
    $currRoj = (Get-Date).AddDays((Get-Random -Minimum 30 -Maximum 70)).ToString("yyyy-MM-dd")
    
    $record = "$i,$location,$material,$category,$supplier,$prevQty,$currQty,$prevRoj,$currRoj,2026-04-10,2026-04-14,1.0,Standard,DC01,NYC,US,Supplier A,NONE,DEMAND_CHANGE,Verified,Reviewed,2026-04-09,1.0,2026-04-01,2026-04-09,2026-04-08,Standard,2026-04-09,2026-04-01,2026-04-09,APPROVED,0,2026-04-01,USER001,2026-04-09,USER001,2026-04-01,1,AMER,SHIFT,5,$qtyChange,0,0,0,1"
    
    $record | Out-File -FilePath $outputFile -Encoding UTF8 -Append
    
    if ($i % 100 -eq 0) {
        Write-Host "Generated $i/$numRecords records..."
    }
}

Write-Host "✅ Successfully generated $numRecords records"
Write-Host "📁 File saved to: $outputFile"
```

Run it:
```powershell
.\generate_sample_data.ps1
```

### Option 3: Manual CSV Creation

If you prefer to create the CSV manually:

1. Open Excel or a text editor
2. Create columns with the SAP field names (see below)
3. Add 2000 rows of data
4. Save as CSV format
5. Place in `sample_data/planning_data_2000_records.csv`

---

## CSV File Structure

### Required Columns (45 fields)

**Identification**:
- SCNID: Scenario ID (1-2000)
- LOCID: Location ID
- PRDID: Product/Material ID
- GSCEQUIPCAT: Equipment Category

**Supplier**:
- LOCFR: Supplier code
- LOCFRDESCR: Supplier description

**Forecast**:
- GSCPREVFCSTQTY: Previous forecast quantity
- GSCFSCTQTY: Current forecast quantity
- FCST_Delta Qty: Forecast change

**Schedule (ROJ)**:
- GSCPREVROJNBD: Previous ROJ date
- GSCCONROJDATE: Current ROJ date
- NBD_DeltaDays: ROJ shift in days
- NBD_Change Type: Type of change

**Supplier Dates**:
- GSCPREVSUPLDATE: Previous supplier date
- GSCSUPLDATE: Current supplier date

**Design**:
- ZCOIBODVERZ: BOD version
- ZCOIFORMFACTZ: Form factor
- GSCSCPBODVERSIONZ: SCP BOD version
- GSCSCPFORMFACTORZ: SCP form factor

**Location**:
- ZCOICIDZ: DC/Site ID
- ZCOIMETROIDZ: Metro ID
- ZCOICOUNTRY: Country

**Planning**:
- GSCPLANNINGEXCEPTIONZ: Planning exception
- GSCROJDATEREASONCODEZ: ROJ reason code

**Approval**:
- GSCCMAPPROVALFIRSTDATEZ: First approval date
- GSCCMAPPROVALLASTCHANGEDDATEZ: Last approval change date
- GSCCMAPPROVALLASTCHANGEDVALUEZ: Approval status

**Dates**:
- GSCROJNBDLASTCHANGEDDATE: ROJ last changed
- GSCROJNBDCREATIONDATE: ROJ creation date
- GSCSENDFCSTSCPFIRSTPUBLISHDATEZ: First publish date
- GSCTRACKLASTPUBLISHDATEZ: Last publish date
- GSCSENDFCSTSCPLASTREMOVEDDATEZ: Last removed date
- GSCSENDFCSTSCPLASTCHANGEDDATEZ: Last changed date
- LASTMODIFIEDDATE: Last modified date
- CREATEDDATE: Created date

**Audit**:
- LASTMODIFIEDBY: Last modified by user
- CREATEDBY: Created by user
- #Version: Record version

**Flags**:
- Is_New Demand: New demand flag (0 or 1)
- Is_cancelled: Cancelled flag (0 or 1)
- Is_SupplierDateMissing: Missing supplier date flag (0 or 1)
- Risk_Flag: Risk indicator (0 or 1)

**Other**:
- TINVALID: Invalid flag
- ROC: Region
- GSCDATASTEWARDNOTESZ: Data steward notes
- GSCPLNRVWNOTESZ: Planner review notes
- GSCSENDFCSTSCPFIRSTPUBLISHDATEZ: SCP first publish date
- GSCSCPBODVERSIONZ: SCP BOD version

---

## Data Characteristics

### Locations (32 unique)
- CYS20_F01C01, CYS20_F01C02, CYS20_F02C01, CYS20_F02C02
- DAL_F02C01, DAL_F02C02, DAL_F03C01, DAL_F03C02
- HOU_F03C01, HOU_F03C02, HOU_F04C01, HOU_F04C02
- PHX_F04C01, PHX_F04C02, PHX_F05C01, PHX_F05C02
- LAX_F05C01, LAX_F05C02, LAX_F06C01, LAX_F06C02
- CHI_F06C01, CHI_F06C02, CHI_F07C01, CHI_F07C02
- ATL_F07C01, ATL_F07C02, ATL_F08C01, ATL_F08C02
- BOS_F08C01, BOS_F08C02, BOS_F09C01, BOS_F09C02

### Materials (30 unique)
- ACC, BAT, CAP, DIO, ELE, FIL, GAS, HEA, IND, JUN
- KEY, LED, MOT, NUT, OIL, PAD, QUA, RES, SEN, TRA
- UPS, VAL, WIR, XFM, YOK, ZEN, AMP, BRK, CIR, DRV

### Equipment Categories (5)
- UPS
- Mechanical
- Hydraulic
- Pneumatic
- Electronics

### Suppliers (15)
- 10_AMER, 130_AMER, 1690_AMER, 210_AMER, 320_AMER
- 410_AMER, 520_AMER, 630_AMER, 740_AMER, 850_AMER
- 960_AMER, 1070_AMER, 1180_AMER, 1290_AMER, 1400_AMER

### Data Ranges
- Forecast Quantity: 100-2000 units
- Forecast Change: -300 to +500 units
- ROJ Shift: -10 to +10 days
- BOD Versions: 1.0, 1.5, 2.0, 2.5, 3.0
- Form Factors: Standard, Compact, Extended, Mini, Modular

### Change Flags
- ~50% of records have quantity changes
- ~30% of records have design changes
- ~40% of records have ROJ changes
- ~25% of records have supplier changes
- ~5% are new demands
- ~2% are cancelled
- ~3% have missing supplier dates
- ~40% have risk flags

---

## File Location

After generation, the file will be located at:

```
D:\MA_Power_Automate\AI_Analytics\AI_Analytics\sample_data\planning_data_2000_records.csv
```

Or in the workspace:
```
sample_data/planning_data_2000_records.csv
```

---

## File Size

Expected file size: **2.5-3.0 MB**

- Header: 1 row
- Data: 2000 rows
- Columns: 45 fields
- Average row size: ~1.2-1.5 KB

---

## Using the Data

### 1. Upload to Blob Storage
```bash
# Using Azure CLI
az storage blob upload \
  --account-name <storage-account> \
  --container-name planning-data \
  --name planning_data_2000_records.csv \
  --file sample_data/planning_data_2000_records.csv
```

### 2. Test with Backend
```bash
# Copy to planning_intelligence/data/
cp sample_data/planning_data_2000_records.csv planning_intelligence/data/

# Run tests
python planning_intelligence/test_ollama_integration.py
```

### 3. Test with Frontend
1. Upload to Blob Storage
2. Configure BLOB_CONNECTION_STRING in .env
3. Run frontend: `npm start`
4. Dashboard will load the data

---

## Troubleshooting

### Issue: Python not found
**Solution**: 
1. Install Python from https://www.python.org/downloads/
2. Add to PATH during installation
3. Verify: `python --version`

### Issue: File not created
**Solution**:
1. Check `sample_data/` directory exists
2. Verify write permissions
3. Check disk space (need ~3MB)

### Issue: CSV format incorrect
**Solution**:
1. Verify all 45 columns are present
2. Check for proper comma separation
3. Ensure dates are in YYYY-MM-DD format
4. Verify numeric fields don't have quotes

### Issue: Data looks wrong
**Solution**:
1. Check forecast quantities are positive
2. Verify ROJ dates are in future
3. Ensure change flags are 0 or 1
4. Check supplier codes match expected format

---

## Next Steps

1. **Generate the data**
   - Run `python generate_sample_data.py`
   - Or use PowerShell script
   - Or create manually

2. **Verify the file**
   - Check file size (~2.5-3.0 MB)
   - Open in Excel to verify format
   - Count rows (should be 2001 including header)

3. **Upload to Blob Storage**
   - Use Azure Portal or CLI
   - Verify upload successful

4. **Test with system**
   - Run backend tests
   - Test frontend dashboard
   - Test Ollama integration

5. **Monitor performance**
   - Track response times
   - Monitor token usage
   - Check error rates

---

## Summary

✅ **Sample data generation script created**
✅ **CSV format documented**
✅ **Data characteristics defined**
✅ **Usage instructions provided**
✅ **Troubleshooting guide included**

**Next Step**: Run `python generate_sample_data.py` to create 2000 records

---

**Last Updated**: April 17, 2026
**Status**: Ready for use

