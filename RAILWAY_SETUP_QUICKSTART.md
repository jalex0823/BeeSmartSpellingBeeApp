# 🚀 Railway Wordbank Setup - Quick Start

## ✅ What's Already Working (Local)
- Database: `instance/beesmart.db` (SQLite) - 979 MB, fully functional
- WordBankStorage table: Created, 66+ wordbanks stored
- Upload API: `/api/upload` working, words persist
- Session system: UUID-based, no data loss on server restart
- All 4 word upload tests pass ✅

---

## 🔧 Next Steps: Configure Railway PostgreSQL

### Step 1: Check Your Railway Database URL
```powershell
# Get DATABASE_URL from your Railway project
# Go to: Railway Dashboard → Your Project → PostgreSQL → Connection
# You should see something like:
# postgresql://user:password@host:5432/railway
```

### Step 2: Set Environment Variable Locally (for testing)
```powershell
# Test connecting to Railway database locally first
$env:DATABASE_URL = "postgresql://user:password@host:5432/railway"

# Verify it's set
Write-Host $env:DATABASE_URL
```

### Step 3: Initialize Railway Database Tables
```powershell
# Run this script to create wordbank_storage table in Railway
cd c:\Temp\BeeSmartSpellingBeeApp
python init_railway_db.py
```

**Output should show:**
```
Tables in Railway PostgreSQL:
  - wordbank_storage (0 rows)
  - [other existing tables...]
✓ Database initialization complete
```

### Step 4: Restart Flask App
```powershell
# Kill the current Flask task
# Start it again:
python AjaSpellBApp.py
```

### Step 5: Test Upload to Railway
```powershell
# Run the upload test
python test_upload_railway.py
```

**Expected result:**
```
✓ Uploaded 4 words to Railway
✓ Words persisted in database
```

---

## 📊 Database Comparison

| Feature | SQLite (Local) | PostgreSQL (Railway) |
|---------|---|---|
| **Location** | `instance/beesmart.db` | Cloud (Railway) |
| **File Size** | 979 MB | Automatic (cloud) |
| **Survives Restart** | ✅ Yes | ✅ Yes |
| **Survives Redeploy** | ❌ No (ephemeral) | ✅ Yes (persistent) |
| **Multi-Instance** | ❌ No | ✅ Yes |
| **Current Status** | ✅ Working | ⏳ To be configured |

---

## 🎯 Configuration Checklist

- [ ] Get PostgreSQL URL from Railway
- [ ] Set `DATABASE_URL` environment variable
- [ ] Run `init_railway_db.py` (creates table)
- [ ] Restart Flask app
- [ ] Test with `test_upload_railway.py`
- [ ] Verify wordbanks in Railway database
- [ ] Deploy to Railway production
- [ ] Monitor logs: "✅ Saved X words to database"

---

## ❓ Troubleshooting

### Problem: Can't connect to Railway database
```
Error: could not translate host name "..." to address
```
**Solution**: Check DATABASE_URL format and network connectivity

### Problem: Table already exists
```
Error: relation "wordbank_storage" already exists
```
**Solution**: Table already created, just start uploading words

### Problem: Words not persisting after upload
```
Check logs for: "✅ Saved X words to Railway database"
If missing: Database connection failed silently
```
**Solution**: Check DATABASE_URL and database logs

---

## 📁 Files to Review

1. **WORDBANK_ONLINE_DB_REVIEW.md** ← You are here (comprehensive overview)
2. **RAILWAY_WORDBANK_FIX.md** (deployment guide)
3. **WORDBANK_SINGLE_SOURCE_FIX.md** (architecture details)
4. **WORDBANK_PERSISTENCE_FIX.md** (problem analysis & solution)

---

## 🔐 Security Notes

- [ ] `DATABASE_URL` never in code (use environment variable)
- [ ] Use strong password for Railway PostgreSQL
- [ ] Restrict IP access in Railway settings
- [ ] Enable SSL for PostgreSQL connection
- [ ] Regular backups (Railway handles automatically)

---

## 📞 Quick Reference

**Current Local Database:**
```
Type: SQLite
Path: c:\Temp\BeeSmartSpellingBeeApp\instance\beesmart.db
Wordbanks: 66+
Status: ✅ Working
```

**Target Railway Database:**
```
Type: PostgreSQL
Provider: Railway
Wordbanks: To be synced from local
Status: ⏳ Pending configuration
```

**Key Environment Variable:**
```
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
```

