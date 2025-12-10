# Railway to DigitalOcean Migration Guide

## 📋 Overview

This guide walks you through migrating your BeeSmart Spelling Bee App from Railway to DigitalOcean, including:
- PostgreSQL database migration
- Static assets (avatars, badges, images)
- Environment configuration
- Testing and verification

**Estimated Time:** 2-4 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Access to both Railway and DigitalOcean accounts

---

## 🚀 Quick Start Checklist

- [ ] DigitalOcean PostgreSQL database created
- [ ] Railway database connection string available
- [ ] DigitalOcean database connection string available
- [ ] Backup of current Railway data
- [ ] Python environment with required packages installed
- [ ] At least 2GB free disk space for backup

---

## 📝 Step-by-Step Migration

### Step 1: Set Up DigitalOcean Database

1. **Create PostgreSQL Database in DigitalOcean:**
   - Log into DigitalOcean Dashboard
   - Go to Databases → Create Database
   - Choose PostgreSQL (version 14 or higher recommended)
   - Select your preferred region and plan
   - Create database named `beesmart` (or your preference)

2. **Get Connection Details:**
   ```
   Host: your-db-name-do-user-123456-0.db.ondigitalocean.com
   Port: 25060
   Database: beesmart
   Username: doadmin
   Password: [your-password]
   ```

3. **Format Connection String:**
   ```
   postgresql://doadmin:PASSWORD@HOST:25060/beesmart?sslmode=require
   ```

### Step 2: Get Railway Database Connection

1. **Access Railway Dashboard:**
   - Go to your Railway project
   - Click on your PostgreSQL service
   - Navigate to "Connect" tab

2. **Copy Connection String:**
   ```
   Railway provides: postgres://user:pass@host:port/database
   ```

### Step 3: Set Environment Variables

Open PowerShell in your project directory:

```powershell
# Set Railway database URL
$env:RAILWAY_DATABASE_URL="postgresql://user:pass@host:port/railway"

# Set DigitalOcean database URL  
$env:DIGITALOCEAN_DATABASE_URL="postgresql://doadmin:pass@host:25060/beesmart?sslmode=require"

# Verify they're set
echo $env:RAILWAY_DATABASE_URL
echo $env:DIGITALOCEAN_DATABASE_URL
```

### Step 4: Install Required Packages

```powershell
pip install psycopg2-binary sqlalchemy python-dotenv
```

### Step 5: Run Pre-Migration Backup

```powershell
# Create manual backup first
python -c "from migrate_railway_to_digitalocean import RailwayToDigitalOceanMigration; m = RailwayToDigitalOceanMigration(); m.validate_connections()"
```

### Step 6: Run the Migration Script

```powershell
python migrate_railway_to_digitalocean.py
```

**What the script does:**
1. ✅ Validates both database connections
2. 📁 Creates timestamped backup directory
3. 📊 Exports database schema (table structure)
4. 💾 Exports all table data to JSON files
5. 🖼️ Backs up static assets (avatars, badges)
6. ⏸️ Pauses for your confirmation
7. 🏗️ Creates tables in DigitalOcean
8. ⬆️ Imports all data to DigitalOcean
9. ✔️ Verifies row counts match
10. 📄 Generates new .env file

### Step 7: Upload Static Assets

The script backs up your assets to `migration_backup/[timestamp]/static_assets/`

**For DigitalOcean App Platform:**
1. Assets are deployed with your code - no extra step needed
2. Ensure `static/` folder is in your Git repository
3. Verify `.gitignore` doesn't exclude asset files

**For DigitalOcean Droplet:**
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Navigate to your app directory
cd /var/www/beesmart

# Upload static assets (from your local machine)
scp -r static/assets root@your-droplet-ip:/var/www/beesmart/static/
```

**For DigitalOcean Spaces (S3-compatible storage):**
- Consider using DO Spaces for large static assets
- Update `AjaSpellBApp.py` to serve avatars from CDN URL
- See section "Using DigitalOcean Spaces" below

### Step 8: Update Environment Configuration

1. **Copy the generated `.env.digitalocean` file:**
   ```powershell
   copy migration_backup\[timestamp]\.env.digitalocean .env
   ```

2. **Edit `.env` and update:**
   ```env
   # Database
   DATABASE_URL=postgresql://doadmin:PASSWORD@HOST:25060/beesmart?sslmode=require
   
   # Email (update with your settings)
   MAIL_SERVER=smtp.hostinger.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@domain.com
   MAIL_PASSWORD=your-password
   
   # Production security
   SECRET_KEY=your-very-secure-random-key-here
   ```

3. **Generate a secure SECRET_KEY:**
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Step 9: Test Locally with DigitalOcean Database

```powershell
# Set environment to use DigitalOcean database
$env:DATABASE_URL=$env:DIGITALOCEAN_DATABASE_URL

# Run the app
python AjaSpellBApp.py
```

**Test Checklist:**
- [ ] Home page loads
- [ ] User login works
- [ ] Avatars display correctly
- [ ] Quiz functionality works
- [ ] Word lists load
- [ ] Admin dashboard accessible

### Step 10: Deploy to DigitalOcean

**Option A: DigitalOcean App Platform (Recommended)**

1. **Connect GitHub Repository:**
   - Go to DigitalOcean → Apps → Create App
   - Select your GitHub repository
   - Choose branch: `main`

2. **Configure Build Settings:**
   ```
   Build Command: pip install -r requirements.txt
   Run Command: gunicorn AjaSpellBApp:app
   ```

3. **Add Environment Variables:**
   - Go to Settings → Environment Variables
   - Add all variables from your `.env` file
   - Especially: `DATABASE_URL`, `SECRET_KEY`, `MAIL_*`

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be available at: `https://your-app-name.ondigitalocean.app`

**Option B: DigitalOcean Droplet (Manual)**

1. **Set up Droplet:**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python and dependencies
   apt install -y python3 python3-pip python3-venv nginx
   
   # Install PostgreSQL client
   apt install -y postgresql-client
   ```

2. **Deploy Application:**
   ```bash
   # Clone repository
   cd /var/www
   git clone https://github.com/yourusername/BeeSmartSpellingBeeApp.git beesmart
   cd beesmart
   
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Configure Nginx:**
   ```nginx
   # /etc/nginx/sites-available/beesmart
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /static {
           alias /var/www/beesmart/static;
       }
   }
   ```

4. **Create Systemd Service:**
   ```ini
   # /etc/systemd/system/beesmart.service
   [Unit]
   Description=BeeSmart Spelling Bee App
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/var/www/beesmart
   Environment="DATABASE_URL=postgresql://..."
   ExecStart=/var/www/beesmart/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 AjaSpellBApp:app
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Services:**
   ```bash
   systemctl enable beesmart
   systemctl start beesmart
   systemctl enable nginx
   systemctl restart nginx
   ```

---

## 🔍 Verification & Testing

### Database Verification

```powershell
# Check row counts
python -c "
from migrate_railway_to_digitalocean import RailwayToDigitalOceanMigration
m = RailwayToDigitalOceanMigration()
m.validate_connections()
m.verify_migration()
"
```

### Functional Testing

**Test User Login:**
1. Go to your app URL
2. Login with existing credentials
3. Verify user data loads correctly

**Test Avatars:**
1. Go to avatar selection
2. Verify all 39 avatars display
3. Select an avatar and save
4. Confirm avatar persists after logout/login

**Test Quiz Flow:**
1. Upload a word list or use existing
2. Start a quiz
3. Complete several words
4. Verify scoring and progress tracking

**Test Admin Dashboard:**
1. Login as admin (BigDaddy2)
2. Check user management
3. Verify word lists
4. Review quiz statistics

### Performance Testing

```bash
# Install Apache Bench
apt install apache2-utils

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 https://your-app.ondigitalocean.app/
```

---

## 📊 Migration Data Reference

### Tables to Migrate

**Core Tables:**
- `users` - User accounts and profiles
- `avatars` - Avatar catalog (39 avatars)
- `wordbank_storage` - User word lists
- `quiz_sessions` - Quiz history
- `quiz_results` - Individual quiz results

**Supporting Tables:**
- `word_lists` - Teacher word lists
- `word_list_items` - Individual words in lists
- `achievements` - User achievements/badges
- `teacher_students` - Teacher-student relationships
- `battle_sessions` - Battle of the Bees data
- `purchase_records` - IAP purchases
- `speed_round_scores` - Speed round history

### Static Assets to Migrate

**Critical Assets:**
- `static/assets/avatars/glb_files/*.glb` (39 GLB files, ~800MB total)
- `static/assets/avatars/glb_files/AvatarThumbnails/*.png` (39 thumbnails)
- `static/assets/badges/*.png` (14 rank badges)
- `static/BeeSmartCrestLogo1.png` (app logo)
- `static/favicon.ico`

**Optional Assets:**
- `static/sounds/` - Audio files for quiz
- `static/images/` - Additional UI images
- `static/android-chrome-*.png` - PWA icons

---

## 🔧 Troubleshooting

### Connection Issues

**Error: "connection refused"**
```
Solution: Check database firewall rules
- DigitalOcean: Add your IP to "Trusted Sources"
- Railway: Verify database is not paused
```

**Error: "SSL connection required"**
```
Solution: Add SSL parameter to connection string
postgresql://...?sslmode=require
```

### Import Issues

**Error: "duplicate key value violates unique constraint"**
```
Solution: This is normal for tables with existing data
The script skips duplicates automatically
```

**Error: "relation does not exist"**
```
Solution: Schema wasn't created properly
Run: python init_db.py
Then retry migration
```

### Performance Issues

**Slow avatar loading**
```
Solution 1: Enable CDN (see DigitalOcean Spaces below)
Solution 2: Compress GLB files
Solution 3: Implement lazy loading
```

**Database connection timeout**
```
Solution: Increase connection pool size in config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 10,
    'pool_pre_ping': True,
}
```

---

## 🚀 Advanced: Using DigitalOcean Spaces for Static Assets

DigitalOcean Spaces is S3-compatible object storage, ideal for serving large files like avatars.

### Setup Spaces

1. **Create Space:**
   - Go to Spaces → Create Space
   - Choose region
   - Enable CDN
   - Name: `beesmart-assets`

2. **Upload Assets:**
   ```powershell
   # Install s3cmd
   pip install s3cmd
   
   # Configure (use DO Spaces API keys)
   s3cmd --configure
   
   # Upload avatars
   s3cmd put -r static/assets/avatars/* s3://beesmart-assets/avatars/
   ```

3. **Update Code:**
   ```python
   # In AjaSpellBApp.py
   SPACES_CDN = "https://beesmart-assets.nyc3.cdn.digitaloceanspaces.com"
   
   # Update avatar URLs
   avatar_url = f"{SPACES_CDN}/avatars/glb_files/{avatar.obj_file}"
   ```

### Benefits

- ✅ Faster global delivery via CDN
- ✅ Reduced app server load
- ✅ Better scalability
- ✅ Automatic backups
- ✅ Cost: ~$5/month for 250GB storage + bandwidth

---

## 📞 Post-Migration Checklist

### Week 1: Monitor Both Systems

- [ ] Keep Railway database running as backup
- [ ] Monitor DigitalOcean database performance
- [ ] Check error logs daily
- [ ] Verify all features work correctly
- [ ] Test from different devices/locations

### Week 2: Validate & Optimize

- [ ] Review database query performance
- [ ] Optimize slow queries if needed
- [ ] Set up automated backups in DigitalOcean
- [ ] Configure database connection pooling
- [ ] Enable database metrics/monitoring

### Week 3-4: Full Cutover

- [ ] Update DNS if using custom domain
- [ ] Pause Railway database (don't delete yet)
- [ ] Update all external integrations
- [ ] Inform users of any API endpoint changes
- [ ] Create final Railway backup

### Month 2: Cleanup

- [ ] Archive Railway backup locally
- [ ] Delete Railway database (after confirming everything works)
- [ ] Remove Railway environment variables
- [ ] Update documentation
- [ ] Celebrate successful migration! 🎉

---

## 📚 Additional Resources

### DigitalOcean Documentation
- [App Platform Guide](https://docs.digitalocean.com/products/app-platform/)
- [Managed Databases](https://docs.digitalocean.com/products/databases/)
- [Spaces Object Storage](https://docs.digitalocean.com/products/spaces/)

### Flask Deployment
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx Flask Proxy](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04)

### Database Management
- [PostgreSQL Backup & Restore](https://www.postgresql.org/docs/current/backup.html)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/14/core/pooling.html)

---

## 🆘 Need Help?

If you encounter issues during migration:

1. **Check Migration Backup:**
   - All data is saved in `migration_backup/[timestamp]/`
   - You can re-run import steps if needed

2. **Rollback Plan:**
   - Keep Railway database active
   - Switch `DATABASE_URL` back to Railway
   - Redeploy previous version

3. **Support Contacts:**
   - Railway Support: https://railway.app/support
   - DigitalOcean Support: https://www.digitalocean.com/support
   - GitHub Issues: [your-repo]/issues

---

## ✅ Success Criteria

Your migration is successful when:

- ✅ All user accounts accessible
- ✅ All avatars (39) display correctly
- ✅ Quiz functionality works end-to-end
- ✅ Word lists save and load properly
- ✅ Admin dashboard fully functional
- ✅ No data loss verified
- ✅ Performance meets or exceeds Railway
- ✅ Automated backups configured
- ✅ Monitoring and alerts set up

---

**Migration Script Version:** 1.0  
**Last Updated:** December 10, 2025  
**Tested With:** Python 3.10, PostgreSQL 14, DigitalOcean App Platform

---

Good luck with your migration! 🚀
