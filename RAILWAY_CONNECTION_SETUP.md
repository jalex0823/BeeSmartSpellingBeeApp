# 🔗 Getting Your Railway PostgreSQL Connection String

**Complete step-by-step guide to connect BeeSmart to your Railway database**

---

## Step 1: Log into Railway Dashboard

1. Go to **https://railway.app**
2. Sign in with your account
3. Click on your **BeeSmart Spelling Bee** project

---

## Step 2: Navigate to PostgreSQL Service

From your Railway dashboard:
1. In the left sidebar, locate your **PostgreSQL** service
2. Click on it to open the service details
3. You should see tabs at the top: **Logs**, **Metrics**, **Deployments**, **Variables**, **Connect**

---

## Step 3: Get Your Connection String

Click on the **Connect** tab. You'll see several connection options:

### Option A: Get DATABASE_URL (Easiest)
Look for the **Connection String** section that shows:

```
postgresql://[username]:[password]@[host]:[port]/[database]
```

Example:
```
postgresql://postgres:Abc123Xyz456@containers-us-west-22.railway.app:7089/railway
```

**This is your DATABASE_URL!**

### Option B: Get from Variables Tab
Alternatively, click **Variables** tab at the top:
1. You'll see `DATABASE_URL` already listed
2. Copy the value directly

---

## Step 4: Set the Environment Variable Locally

Open PowerShell and set it for testing:

```powershell
# Replace with YOUR actual URL
$env:DATABASE_URL = "postgresql://postgres:YourPassword@containers-us-west-22.railway.app:7089/railway"

# Verify it's set
Write-Host $env:DATABASE_URL
```

---

## Step 5: Test Connection

Run the initialization script:

```powershell
cd c:\Temp\BeeSmartSpellingBeeApp

python init_railway_db.py
```

**Expected output:**
```
============================================
🚀 RAILWAY DATABASE INITIALIZATION
============================================

📍 Database URL: postgresql://postgres:***@...

1. Testing connection to Railway PostgreSQL...
   ✅ Connection successful!

2. Initializing Flask app with Railway database...
   ✅ Flask app loaded

3. Creating database tables...
   ✅ db.create_all() executed

4. Verifying wordbank_storage table...
   ✅ wordbank_storage table exists with 0 wordbanks

============================================
✅ RAILWAY DATABASE INITIALIZATION COMPLETE
============================================
```

---

## Step 6: Deploy to Railway

### Option A: Deploy via Git Push
```powershell
# Make sure you've set DATABASE_URL in Railway
# Then push your code
git add .
git commit -m "Configure Railway PostgreSQL for wordbank persistence"
git push origin main

# Railway auto-deploys!
```

### Option B: Deploy via Railway CLI
```powershell
# Install Railway CLI (if not already)
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

---

## Step 7: Verify on Railway

1. Go to Railway Dashboard
2. Click on your app service (not PostgreSQL)
3. Click **Logs** tab
4. Upload some test words in your app
5. Look for logs like:
   ```
   ✅ Saved X words to Railway database for storage_id=...
   ```

6. Restart the app
7. Navigate to quiz → verify words are still there!

---

## 🔍 Troubleshooting

### Problem: "could not translate host name"
**Cause**: DATABASE_URL not set or incorrect  
**Fix**: Double-check the URL from Railway Connect tab

### Problem: "FATAL: remaining connection slots are reserved"
**Cause**: Too many connections to database  
**Fix**: Restart the app or check for connection leaks

### Problem: "wordbank_storage table does not exist"
**Cause**: `init_railway_db.py` wasn't run  
**Fix**: Run `python init_railway_db.py` with DATABASE_URL set

### Problem: Words appear in local DB but not Railway
**Cause**: Different DATABASE_URL than where words were saved  
**Fix**: Verify you're using the correct CONNECTION STRING

---

## 📋 Checklist

Before deploying to Railway production:

- [ ] Get PostgreSQL URL from Railway dashboard
- [ ] Set `$env:DATABASE_URL` locally
- [ ] Run `init_railway_db.py` successfully
- [ ] Test word upload with Railway database
- [ ] Verify logs show "Saved to Railway database"
- [ ] Set `DATABASE_URL` in Railway Variables/Config
- [ ] Deploy code to Railway
- [ ] Test upload in production
- [ ] Verify words persist across app restarts

---

## 🚀 Quick Command Reference

```powershell
# Set environment variable
$env:DATABASE_URL = "postgresql://..."

# Test connection
python init_railway_db.py

# Restart Flask app (after setting env var)
python AjaSpellBApp.py

# Test upload
python test_upload.py

# Check database directly (SQLite local)
python check_instance_db.py
```

---

## 📞 Getting Help

If you have your Railway PostgreSQL URL but need help:

1. **Share CONNECTION STRING format** (don't share password):
   ```
   postgresql://[user]:[***]@[host]:xxxx/[database]
   ```

2. **Check logs** from Flask app during upload

3. **Verify table** was created:
   ```sql
   SELECT COUNT(*) FROM wordbank_storage;
   ```

---

## 🎯 What Happens After Setup

```
User Uploads Words
    ↓
Flask saves to WordBankStorage table (Railway PostgreSQL)
    ↓
Session stores storage_id (UUID)
    ↓
Words cached in memory for fast access
    ↓
User goes to quiz
    ↓
Flask loads from in-memory cache OR database
    ↓
Words displayed in quiz
    ↓
App restarts
    ↓
Words still there (loaded from Railway database!)
```

---

**Ready to connect? Get your DATABASE_URL and run `init_railway_db.py`!**

