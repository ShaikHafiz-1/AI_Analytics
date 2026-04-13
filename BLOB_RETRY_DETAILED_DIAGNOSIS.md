# Blob Retry Failure - Detailed Diagnosis

## Status
✅ Blob files exist in Azure Blob Storage
❌ Retry is still failing

## Next Steps: Identify the Exact Error

### Step 1: Check Azure Functions Logs
When you click "Retry Blob" from the UI, look at the terminal where `func start` is running.

You should see error messages like:
```
Blob load failed: Missing required columns in current: {'LOCID', 'PRDID', 'GSCEQUIPCAT'}
```

**Copy the exact error message** - this will tell us what's wrong.

### Step 2: Common Issues & Solutions

#### Issue 1: Missing Required Columns
**Error**: `Missing required columns in current: {'LOCID', 'PRDID', 'GSCEQUIPCAT'}`

**Solution**: CSV files must have these exact columns (case-sensitive, UPPERCASE):
- `LOCID` - Location ID
- `PRDID` - Product ID  
- `GSCEQUIPCAT` - Equipment Category

**Fix**:
1. Open CSV file in Excel
2. Check column headers
3. Rename columns to match exactly (UPPERCASE)
4. Re-upload to blob storage
5. Restart Azure Functions: `func start`
6. Retry from UI

#### Issue 2: File Encoding Problem
**Error**: `Failed to parse file (current): ...`

**Solution**: CSV file might have wrong encoding

**Fix**:
1. Open CSV in Notepad++
2. Check encoding (should be UTF-8 or ANSI)
3. If wrong, convert to UTF-8:
   - Encoding → Convert to UTF-8
   - Save file
4. Re-upload to blob storage
5. Restart Azure Functions
6. Retry from UI

#### Issue 3: Empty Rows or Corrupted Data
**Error**: `File is empty: current` or parsing errors

**Solution**: CSV file might have empty rows or corrupted data

**Fix**:
1. Open CSV in Excel
2. Check for empty rows
3. Delete empty rows
4. Verify data looks correct
5. Save as CSV (UTF-8)
6. Re-upload to blob storage
7. Restart Azure Functions
8. Retry from UI

#### Issue 4: Wrong Delimiter
**Error**: `Missing required columns...` but columns exist

**Solution**: CSV might use wrong delimiter (semicolon instead of comma)

**Fix**:
1. Open CSV in text editor
2. Check if using `;` instead of `,`
3. If using semicolon, convert to comma:
   - Find & Replace: `;` → `,`
   - Save file
4. Re-upload to blob storage
5. Restart Azure Functions
6. Retry from UI

### Step 3: Verify CSV Format

Your CSV files should look like this:

**current.csv**:
```
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT
LOC001,MAT001,ELECTRONICS,SUPPLIER1,1000,2026-04-15,BOD1,FF1
LOC001,MAT002,ELECTRONICS,SUPPLIER2,2000,2026-04-20,BOD2,FF2
LOC002,MAT003,MECHANICAL,SUPPLIER1,1500,2026-04-25,BOD3,FF3
```

**previous.csv**:
```
LOCID,PRDID,GSCEQUIPCAT,LOCFR,GSCFSCTQTY,GSCCONROJDATE,ZCOIBODVER,ZCOIFORMFACT
LOC001,MAT001,ELECTRONICS,SUPPLIER1,900,2026-04-10,BOD1,FF1
LOC001,MAT002,ELECTRONICS,SUPPLIER1,2000,2026-04-15,BOD2,FF2
LOC002,MAT003,MECHANICAL,SUPPLIER1,1500,2026-04-20,BOD3,FF3
```

### Step 4: Check File Size

Files should not be empty:
- current.csv: > 100 bytes
- previous.csv: > 100 bytes

If files are very small (< 100 bytes), they might be corrupted or empty.

### Step 5: Improved Error Messages

I've enhanced the blob loader with better logging. When you retry, you'll see:
- File size in bytes
- Encoding used (UTF-8 or latin-1)
- Number of rows and columns
- Exact column names found
- Detailed error messages

## Troubleshooting Workflow

1. **Click "Retry Blob"** from UI
2. **Check Azure Functions logs** for error message
3. **Identify the issue** from the error message
4. **Apply the fix** from the solutions above
5. **Re-upload CSV** to blob storage
6. **Restart Azure Functions**: `func start`
7. **Retry from UI** - should work now ✅

## Quick Checklist

- [ ] CSV files exist in blob storage (planning-data container)
- [ ] Column headers are UPPERCASE: LOCID, PRDID, GSCEQUIPCAT
- [ ] Files use comma delimiter (`,`) not semicolon (`;`)
- [ ] Files are UTF-8 encoded
- [ ] Files have data rows (not just headers)
- [ ] Files are not empty (> 100 bytes)
- [ ] No empty rows in the middle of data
- [ ] Azure Functions restarted after uploading

## Getting the Error Message

To see the exact error:

1. Open terminal where `func start` is running
2. Click "Retry Blob" from UI
3. Look for error message in terminal
4. Copy the exact error message
5. Match it to the solutions above

## Example Error Messages

### ✅ Success
```
Downloaded blob planning-data/current.csv (1234 bytes)
Successfully parsed current with UTF-8 encoding
Loaded current: 100 rows, 8 columns
Columns in current: ['LOCID', 'PRDID', 'GSCEQUIPCAT', 'LOCFR', 'GSCFSCTQTY', 'GSCCONROJDATE', 'ZCOIBODVER', 'ZCOIFORMFACT']
✅ All required columns present in current: ['GSCEQUIPCAT', 'LOCID', 'PRDID']
```

### ❌ Missing Columns
```
Loaded current: 100 rows, 5 columns
Columns in current: ['Location', 'Product', 'Category', 'Supplier', 'Quantity']
Missing required columns in current: ['GSCEQUIPCAT', 'LOCID', 'PRDID']
Found columns: ['Category', 'Location', 'Product', 'Quantity', 'Supplier']
```

### ❌ Encoding Error
```
UTF-8 decode failed for current, trying latin-1
Successfully parsed current with latin-1 encoding
```

### ❌ Empty File
```
Downloaded blob planning-data/current.csv (0 bytes)
Empty file content for current
```

## Next Action

1. Click "Retry Blob" from UI
2. Check the error message in Azure Functions logs
3. Reply with the exact error message
4. I'll provide the specific fix

---

**Status**: Blob files exist, investigating why retry fails
**Next**: Get exact error message from Azure Functions logs
