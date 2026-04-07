# GitHub Push Protection - Fix Instructions

## 🔍 Problem
GitHub is blocking your push because documentation files contain Azure Storage Account Access Keys (secrets).

**Error**: `Push cannot contain secrets - Azure Storage Account Access Key`

---

## ✅ Solution: Remove Secrets from Git History

### Step 1: Remove the Problematic File from Git History

GitHub detected secrets in the commit. You need to remove them from git history:

```bash
# Option A: Use git filter-branch (recommended for single file)
git filter-branch --tree-filter 'rm -f BLOB_CONNECTION_STRING_FIX.md' HEAD

# Option B: Use BFG Repo-Cleaner (faster for large repos)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
bfg --delete-files BLOB_CONNECTION_STRING_FIX.md
```

### Step 2: Force Push the Cleaned History

```bash
git push -f origin feature/local-test-ready
```

---

## 🚀 Alternative: Quick Fix (Recommended)

If the above doesn't work, follow these steps:

### Step 1: Undo the Last Commit
```bash
git reset --soft HEAD~1
```

### Step 2: Remove the Problematic File
```bash
git rm BLOB_CONNECTION_STRING_FIX.md
```

### Step 3: Stage Changes
```bash
git add .
```

### Step 4: Commit Again (Without Secrets)
```bash
git commit -m "docs: remove file with secrets, add clean version"
```

### Step 5: Push
```bash
git push origin feature/local-test-ready
```

---

## 📝 Files to Check

Make sure these files do NOT contain secrets:
- ✅ `BLOB_CONNECTION_STRING_SETUP.md` - Clean (no secrets)
- ✅ `SNAPSHOT_FILE_LOCATION_FIX.md` - Clean (no secrets)
- ✅ `WINDOWS_SETUP_FINAL.md` - Clean (no secrets)
- ✅ `WINDOWS_QUICK_FIX.txt` - Clean (no secrets)
- ❌ `BLOB_CONNECTION_STRING_FIX.md` - Contains secrets (DELETE)

---

## 🔐 Best Practices

1. **Never commit secrets to git**
   - Connection strings
   - API keys
   - Access keys
   - Passwords

2. **Use environment variables instead**
   - Store in `local.settings.json` (not committed)
   - Load via `func start`
   - Reference in documentation without values

3. **If you accidentally commit secrets**
   - Remove from git history immediately
   - Rotate the secret in Azure
   - Force push to update remote

---

## ✅ After Fixing

Once you've removed the secrets and pushed:

```bash
# Verify the push succeeded
git log --oneline -5

# Check remote branch
git branch -r
```

---

## 📞 GitHub Secret Scanning

GitHub detected the secret and blocked the push. You can:

1. **Remove the secret** (recommended) - Follow steps above
2. **Unblock the secret** - Click the link in the error message (not recommended)

**Link from error**:
```
https://github.com/ShaikHafiz-1/AI_Analytics/security/secret-scanning/unblock-secret/3C2ZWLGGBI7c42FwZjLP9L5YkiM
```

---

## 🎯 Quick Summary

1. Delete `BLOB_CONNECTION_STRING_FIX.md` from git history
2. Use `BLOB_CONNECTION_STRING_SETUP.md` instead (no secrets)
3. Force push to update remote
4. Verify push succeeded

---

**Status**: ✅ Instructions Provided
**Action**: Remove secrets from git history
**Time to Fix**: ~5 minutes
