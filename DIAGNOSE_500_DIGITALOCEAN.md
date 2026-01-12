# Diagnosing 500 Error on DigitalOcean

## ✅ Configuration Status

Your app is already configured for DigitalOcean:
- `config.py` prioritizes `DIGITALOCEAN_DATABASE_URL` over `DATABASE_URL`
- SSL mode is automatically set to `require` for DigitalOcean Postgres
- Database connection uses DigitalOcean Managed Postgres

## 🔍 Step-by-Step Diagnosis

### Step 1: Check DigitalOcean Logs

1. **Access DigitalOcean Dashboard:**
   - Go to your DigitalOcean project
   - Click on your App or Droplet
   - Navigate to **"Runtime Logs"** or **"Deploy Logs"**

2. **Look for Python Traceback:**
   - The 500 error handler logs full exceptions
   - Search for "Internal server error" or "Traceback"
   - The traceback will show the exact failing code

### Step 2: Verify Database Connection

**Check Environment Variables:**
```bash
# Should be set in DigitalOcean App Platform or Droplet
DIGITALOCEAN_DATABASE_URL=postgresql://doadmin:PASSWORD@HOST:25060/beesmart?sslmode=require
```

**Test Connection Locally:**
```python
# Quick test script
import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DIGITALOCEAN_DATABASE_URL')
if db_url:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"Connected: {result.fetchone()[0]}")
else:
    print("DIGITALOCEAN_DATABASE_URL not set")
```

### Step 3: Check Browser Network Tab

1. **Open Developer Tools** (F12)
2. **Go to Network tab**
3. **Reload page** (Ctrl+Shift+R)
4. **Find request with Status 500**
5. **Click it to see:**
   - Request URL (the failing resource)
   - Response body (error message)

## 🐛 Common DigitalOcean-Specific Issues

### Issue 1: SSL Connection Required
**Symptom:** Database connection errors in logs
**Fix:** Ensure `sslmode=require` is in connection string
**Check:** `config.py` automatically adds this if missing

### Issue 2: Database Connection Pool Exhausted
**Symptom:** Intermittent 500 errors, especially under load
**Fix:** Check `SQLALCHEMY_ENGINE_OPTIONS` in `config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,  # Verify connections before using
    'pool_recycle': 300,    # Recycle connections after 5 minutes
}
```

### Issue 3: Missing Environment Variables
**Symptom:** 500 errors on startup or specific features
**Check Required Variables:**
- `DIGITALOCEAN_DATABASE_URL` or `DO_DATABASE_URL`
- `SECRET_KEY`
- `MAIL_*` variables (if using email features)

### Issue 4: Static Asset Serving
**Symptom:** 500 error on images/CSS/JS files
**Check:** 
- Files exist in `static/` directory
- DigitalOcean App Platform serves static files correctly
- Check file permissions

### Issue 5: Avatar File Serving
**Symptom:** 500 error on `/static/assets/avatars/<slug>/<filename>`
**Check:**
- Database has avatar records
- Files exist in filesystem or database (`glb_data`, `thumbnail_data` columns)
- Route handler at `AjaSpellBApp.py` line 16192-16256

## 📋 What to Check in DigitalOcean

### App Platform:
1. **Settings → Environment Variables**
   - Verify `DIGITALOCEAN_DATABASE_URL` is set
   - Check `SECRET_KEY` is set
   - Verify all required variables

2. **Runtime Logs**
   - View real-time logs
   - Look for Python exceptions

3. **Metrics**
   - Check CPU/Memory usage
   - Check database connection count

### Managed Database:
1. **Settings → Connection Details**
   - Verify connection string format
   - Check SSL is enabled
   - Verify firewall rules allow your app

2. **Metrics**
   - Check connection count
   - Check query performance

## 🔧 Quick Fixes

### Fix 1: Restart App
In DigitalOcean App Platform:
1. Go to your app
2. Click "Actions" → "Restart"
3. Wait for deployment to complete

### Fix 2: Verify Database Connection
```python
# Test script
python -c "from config import Config; from sqlalchemy import create_engine, text; engine = create_engine(Config.SQLALCHEMY_DATABASE_URI); conn = engine.connect(); print('Connected:', conn.execute(text('SELECT 1')).fetchone())"
```

### Fix 3: Check Health Endpoint
```bash
curl https://beesmartspelling.app/health
# Should return: {"status": "ok", "version": "22"}
```

### Fix 4: Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

## 📝 Information to Gather

If error persists, please provide:

1. **The exact failing URL** (from browser Network tab)
2. **Python traceback** (from DigitalOcean logs)
3. **When it occurs:**
   - On page load?
   - After clicking something?
   - When logged in vs guest?
4. **Environment:**
   - DigitalOcean App Platform or Droplet?
   - Which region?
5. **Database status:**
   - Can you connect to the database?
   - Are there any connection errors in database logs?

## 🚨 Most Likely Causes

Based on DigitalOcean setup:

1. **Database Connection Issues** (most common)
   - SSL mode not set correctly
   - Firewall blocking connections
   - Connection pool exhausted

2. **Missing Environment Variables**
   - `DIGITALOCEAN_DATABASE_URL` not set
   - `SECRET_KEY` not set

3. **Static Asset Issues**
   - Files not deployed
   - Incorrect file paths
   - Permission issues

4. **Avatar File Serving**
   - Database query failing
   - Missing avatar files in database/filesystem

## 📞 Next Steps

1. **Check DigitalOcean Runtime Logs** for the Python traceback
2. **Use Network tab** to identify the exact failing URL
3. **Verify environment variables** are set correctly
4. **Test database connection** separately

Once you have the traceback and failing URL, I can provide a targeted fix!
