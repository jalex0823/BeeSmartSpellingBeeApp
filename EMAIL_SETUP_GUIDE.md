# 📧 Email System & Password Reset - Complete Guide

## Overview
BeeSmart has a password reset system that uses email to send reset links. However, **email sending is currently in development mode** and requires SMTP configuration to actually send emails.

---

## 🔍 Current Status

### Development Mode (Current State)
- Email configuration variables are **not set** in production
- When a password reset is requested, the system **logs the reset link to console** instead of sending email
- The reset link is printed in Flask logs like this:
  ```
  📧 [DEV] Would send reset email to user@example.com: http://localhost:5000/reset-password?token=abc123...
  ```

### What This Means
- ✅ Password reset system is **fully functional**
- ✅ Reset tokens are generated and stored securely
- ✅ Users can reset passwords if they have the reset link
- ❌ Emails are **not actually sent** (printed to console instead)
- ⚠️ In development, you need to **copy the link from Flask logs**

---

## 📊 User Database Access

### Table: `users`
The user information is stored in the `users` table with these key fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `username` | String(50) | Unique username |
| `display_name` | String(100) | Display name |
| `email` | String(100) | Email address (unique) |
| `password_hash` | String(255) | Hashed password |
| `role` | String(20) | student, teacher, parent, admin |
| `email_verified` | Boolean | Email verification status |
| `created_at` | DateTime | Account creation date |
| `last_login` | DateTime | Last login timestamp |

### How to Access User Data

#### Method 1: Use the Database Access Tool
```powershell
python view_user_data.py
```

This will show all users with their emails, including:
- Username
- Email address
- Role
- Creation date
- Quiz stats

#### Method 2: Python Script
```python
from AjaSpellBApp import app, db
from models import User

with app.app_context():
    # Get all users
    users = User.query.all()
    for user in users:
        print(f"{user.username}: {user.email}")
    
    # Get specific user
    user = User.query.filter_by(username='admin').first()
    print(f"Admin email: {user.email}")
    
    # Find user by email
    user = User.query.filter_by(email='student@example.com').first()
    print(f"User: {user.username}")
```

#### Method 3: SQLite Browser (if using SQLite)
```powershell
# Open database with SQLite browser
sqlite3 beesmart.db

# Query users
SELECT id, username, email, role FROM users;

# Find specific user
SELECT * FROM users WHERE username = 'admin';

# Exit
.quit
```

---

## 🔧 Setting Up Email (To Actually Send Emails)

### Step 1: Choose Email Provider

#### Option A: Gmail (Easiest for Testing)
1. Create a Gmail account or use existing
2. Enable "2-Step Verification" in Google Account settings
3. Go to: https://myaccount.google.com/apppasswords
4. Generate an "App Password" for "Mail"
5. Copy the 16-character password

#### Option B: SendGrid (Best for Production)
1. Sign up at: https://sendgrid.com
2. Create an API key
3. Use `smtp.sendgrid.net` as server

#### Option C: AWS SES
1. Sign up for AWS SES
2. Verify your sender email
3. Get SMTP credentials

### Step 2: Set Environment Variables

Create or edit `.env` file in your project root:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
```

**For Gmail:**
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=youremail@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
```

**For SendGrid:**
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your-api-key-here
```

### Step 3: Restart Application
```powershell
# Stop Flask
Ctrl+C

# Restart
python AjaSpellBApp.py
```

### Step 4: Test Password Reset
1. Go to login page
2. Click "Forgot Password?"
3. Enter email address
4. Check email inbox for reset link
5. Click link and reset password

---

## 🔐 Password Reset Flow

### How It Works:

```
1. User clicks "Forgot Password"
   ↓
2. Enters email address
   ↓
3. Backend checks if user exists
   ↓
4. Generates secure reset token (valid for 1 hour)
   ↓
5. Creates reset URL: http://yoursite.com/reset-password?token=abc123...
   ↓
6. Sends email (or logs to console in dev mode)
   ↓
7. User clicks link in email
   ↓
8. Backend validates token (checks expiry, user exists, etc.)
   ↓
9. User enters new password
   ↓
10. Password updated, token invalidated
   ↓
11. User redirected to login
```

### Security Features:
- ✅ Tokens expire after 1 hour
- ✅ Tokens are single-use only
- ✅ Tokens are cryptographically secure (HMAC-SHA256)
- ✅ Old password is not revealed
- ✅ Rate limiting on reset requests (1 per 15 minutes per user)

---

## 🛠️ Common Tasks

### 1. View All User Emails
```powershell
python view_user_data.py
```

Output:
```
👥 ALL USERS IN DATABASE
═══════════════════════════════════════════════════════
ID    Username             Email                          Role       Created
--------------------------------------------------------------------------------
1     admin                admin@example.com              admin      2025-10-15
2     student1             student1@school.com            student    2025-10-16
3     teacher1             teacher@school.com             teacher    2025-10-17
```

### 2. Add Email to User Without One
```powershell
python view_user_data.py
```

Then in the script, uncomment:
```python
update_user_email('username', 'newemail@example.com')
```

Or use Python directly:
```python
from AjaSpellBApp import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    user.email = 'admin@example.com'
    db.session.commit()
    print(f"✅ Email updated for {user.username}")
```

### 3. Manually Reset Password (If Email Not Working)
```python
from AjaSpellBApp import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    user.password_hash = generate_password_hash('newpassword123')
    db.session.commit()
    print(f"✅ Password reset for {user.username}")
```

### 4. Check Users Without Email
```powershell
python view_user_data.py
```

In script, uncomment:
```python
show_users_without_email()
```

### 5. Get Reset Link from Console (Dev Mode)
1. Request password reset on website
2. Check Flask console output
3. Look for:
   ```
   📧 [DEV] Would send reset email to user@example.com: http://localhost:5000/reset-password?token=...
   ```
4. Copy the full URL
5. Paste in browser
6. Reset password

---

## 📁 File Locations

### Configuration
- **`config.py`** - Email settings (lines 52-57)
- **`.env`** - Environment variables (create if doesn't exist)

### Code
- **`AjaSpellBApp.py:453-495`** - `send_reset_email()` function
- **`AjaSpellBApp.py:3984-4057`** - `/api/auth/forgot-password` route
- **`AjaSpellBApp.py:4064-4110`** - `/reset-password` route

### Database
- **`beesmart.db`** - SQLite database file (if using SQLite)
- **`models.py:17-50`** - User model definition

### Tools
- **`view_user_data.py`** - Database access tool (NEW)
- **`verify_gpa_storage.py`** - User stats verification

---

## 🐛 Troubleshooting

### Problem: "Email not sent"
**Solution:** This is normal in development mode. Check Flask console for reset link.

### Problem: "User not found"
**Solution:** 
1. Check if user has email set: `python view_user_data.py`
2. Add email if missing: `update_user_email('username', 'email@example.com')`

### Problem: "Token expired"
**Solution:** Tokens expire after 1 hour. Request new password reset.

### Problem: "SMTP authentication failed"
**Solution:**
1. Verify MAIL_USERNAME and MAIL_PASSWORD in `.env`
2. For Gmail, use App Password (not regular password)
3. Check MAIL_SERVER and MAIL_PORT are correct

### Problem: "Can't access database"
**Solution:**
```powershell
# Check database exists
ls beesmart.db

# Test database connection
python -c "from AjaSpellBApp import app, db; app.app_context().push(); print(f'Users: {db.session.query(User).count()}')"
```

---

## 🎯 Quick Reference

### View Users
```powershell
python view_user_data.py
```

### Update Email
```python
from AjaSpellBApp import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    user.email = 'admin@example.com'
    db.session.commit()
```

### Reset Password Manually
```python
from AjaSpellBApp import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    user.password_hash = generate_password_hash('newpassword')
    db.session.commit()
```

### Enable Email Sending
1. Edit `.env`
2. Add MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD
3. Restart Flask

---

## ✅ Summary

**Email System Status:**
- ✅ Password reset functionality works
- ✅ Reset tokens are secure
- ⚠️ Email sending is in DEV mode (logs to console)
- 💡 Configure SMTP to send actual emails

**Database Access:**
- ✅ Use `view_user_data.py` to see all users and emails
- ✅ Can update user emails via Python script
- ✅ Can manually reset passwords if needed

**To Enable Real Email:**
1. Set up MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD in `.env`
2. Restart application
3. Test password reset - email will be sent!

---

## 📚 Related Files

1. **view_user_data.py** - Database access tool (NEW)
2. **EMAIL_SETUP_GUIDE.md** - This file
3. **config.py** - Configuration settings
4. **.env** - Environment variables (create if missing)
