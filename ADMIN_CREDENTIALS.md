# 🔐 BeeSmart Admin Credentials

**Date Created:** November 13, 2025  
**Status:** ✅ Active

---

## 🏠 LOCAL DEVELOPMENT (Offline)

### Admin Account

**Username:** `BigDaddy`  
**Password:** `Aja121514!`  
**Email:** bigdaddy@beesmart.app  
**Role:** admin  
**User ID:** 25

### How to Login (Local)

1. Start the app:
   ```bash
   python AjaSpellBApp.py
   ```

2. Open browser:
   ```
   http://localhost:5000/auth/login
   ```

3. Enter credentials:
   - Username: `BigDaddy`
   - Password: `Aja121514!`

4. ✅ Access admin dashboard

---

## 🌐 PRODUCTION/RAILWAY (Online)

### Admin Account

**Username:** `BigDaddy`  
**Password:** `Aja121514!`  
**Email:** bigdaddy@beesmart.app  
**Role:** admin

### How to Login (Railway)

1. Navigate to your Railway app:
   ```
   https://[your-railway-app].up.railway.app/auth/login
   ```

2. Enter credentials:
   - Username: `BigDaddy`
   - Password: `Aja121514!`

3. ✅ Access admin dashboard

### ⚠️ If Login Fails on Railway

If you get "Invalid credentials" on Railway, the admin account may not exist in the production database yet. Here's how to create it:

#### Option 1: Railway Shell (Recommended)

```bash
# Connect to Railway
railway shell

# Run the admin creation script
python3 create_admin_bigdaddy.py
```

#### Option 2: Direct Database Script

```bash
railway run python3 create_admin_bigdaddy.py
```

#### Option 3: Manual Creation via Railway Shell

```bash
railway shell

python3 << 'EOF'
from AjaSpellBApp import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if exists
    existing = User.query.filter_by(username='BigDaddy').first()
    if existing:
        print(f"✅ BigDaddy already exists (ID: {existing.id})")
    else:
        # Create admin
        admin = User(
            username='BigDaddy',
            display_name='Big Daddy',
            email='bigdaddy@beesmart.app',
            password_hash=generate_password_hash('Aja121514!'),
            role='admin',
            is_active=True,
            email_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created! ID: {admin.id}")
EOF
```

---

## 🎯 Admin Capabilities

With the BigDaddy admin account, you have access to:

### User Management
- ✅ View all users
- ✅ Create/edit/delete user accounts
- ✅ Reset user passwords
- ✅ Change user roles (student → teacher → admin)
- ✅ Verify email addresses
- ✅ Activate/deactivate accounts

### Content Management
- ✅ View all quiz sessions
- ✅ Access all quiz results
- ✅ Monitor user activity
- ✅ Generate reports

### Teacher Tools
- ✅ Generate teacher keys
- ✅ View teacher-student relationships
- ✅ Manage classroom groups
- ✅ Monitor student progress

### System Administration
- ✅ Access admin dashboard
- ✅ View system statistics
- ✅ Manage application settings
- ✅ Database operations
- ✅ Avatar management
- ✅ IAP product management

### Avatar & Store
- ✅ Unlock all avatars for testing
- ✅ Manage avatar catalog
- ✅ Configure pricing tiers
- ✅ Monitor purchases
- ✅ Grant honey points

---

## 📍 Access URLs

### Local Development
- **Login:** http://localhost:5000/auth/login
- **Dashboard:** http://localhost:5000/admin/dashboard
- **User List:** http://localhost:5000/admin/users
- **Stats:** http://localhost:5000/admin/stats

### Railway Production
- **Login:** https://[your-app].up.railway.app/auth/login
- **Dashboard:** https://[your-app].up.railway.app/admin/dashboard
- **User List:** https://[your-app].up.railway.app/admin/users
- **Stats:** https://[your-app].up.railway.app/admin/stats

---

## 🔧 Admin Tools & Scripts

### Check if Admin Exists
```bash
python3 << 'EOF'
from AjaSpellBApp import app, db, User

with app.app_context():
    admin = User.query.filter_by(username='BigDaddy').first()
    if admin:
        print(f"✅ BigDaddy exists - ID: {admin.id}, Role: {admin.role}")
    else:
        print("❌ BigDaddy not found")
EOF
```

### List All Admin Accounts
```bash
python3 << 'EOF'
from AjaSpellBApp import app, db, User

with app.app_context():
    admins = User.query.filter_by(role='admin').all()
    print(f"Found {len(admins)} admin(s):")
    for admin in admins:
        print(f"  • {admin.username} (ID: {admin.id}, Email: {admin.email})")
EOF
```

### Reset Admin Password
```bash
python3 << 'EOF'
from AjaSpellBApp import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(username='BigDaddy').first()
    if admin:
        admin.password_hash = generate_password_hash('Aja121514!')
        db.session.commit()
        print("✅ Password reset to: Aja121514!")
    else:
        print("❌ Admin not found")
EOF
```

### Promote Existing User to Admin
```bash
python3 << 'EOF'
from AjaSpellBApp import app, db, User

with app.app_context():
    user = User.query.filter_by(username='[USERNAME]').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print(f"✅ {user.username} promoted to admin")
    else:
        print("❌ User not found")
EOF
```

---

## 🔒 Security Notes

### Password Policy
- Current password: `Aja121514!`
- **Recommendation:** Change after first login
- Use strong, unique password for production

### Access Control
- Only admins can access `/admin/*` routes
- User sessions expire after inactivity
- Password hashes use `scrypt` (secure)

### Production Best Practices
1. ✅ Change default password
2. ✅ Use HTTPS (Railway provides this)
3. ✅ Enable 2FA if available
4. ✅ Monitor admin login activity
5. ✅ Regular password rotation

---

## 📞 Troubleshooting

### Can't Login Locally?

**Verify admin exists:**
```bash
python view_user_data.py
```
Look for `BigDaddy` in the user list.

**Recreate admin:**
```bash
python create_admin_bigdaddy.py
```

### Can't Login on Railway?

**Check if database is fresh:**
- Railway may use ephemeral storage
- Database resets on redeploy
- Need to recreate admin account

**Fix:**
```bash
railway run python3 create_admin_bigdaddy.py
```

### Wrong Password?

**Reset to default:**
```bash
python3 create_admin_bigdaddy.py
```
(Script will prompt to update password if user exists)

---

## 📋 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║         BeeSmart Admin Credentials               ║
╠══════════════════════════════════════════════════╣
║ Username:  BigDaddy                              ║
║ Password:  Aja121514!                            ║
║ Email:     bigdaddy@beesmart.app                 ║
║ Role:      admin                                 ║
╠══════════════════════════════════════════════════╣
║ LOCAL:                                           ║
║   http://localhost:5000/auth/login               ║
║                                                  ║
║ RAILWAY:                                         ║
║   https://[your-app].up.railway.app/auth/login   ║
╚══════════════════════════════════════════════════╝
```

---

## ✅ Verification Checklist

- [x] Admin account created locally (ID: 25)
- [x] Password: Aja121514!
- [x] Role: admin
- [x] Email verified: Yes
- [x] Can login to local app
- [ ] Admin account created on Railway
- [ ] Can login to Railway app
- [ ] Admin dashboard accessible
- [ ] All admin features working

---

## 🎯 Next Steps

1. **Test Local Login:**
   - Start app: `python AjaSpellBApp.py`
   - Login at: http://localhost:5000/auth/login
   - Verify admin dashboard works

2. **Setup Railway Admin:**
   - Connect to Railway: `railway shell`
   - Create admin: `python3 create_admin_bigdaddy.py`
   - Test login on Railway URL

3. **Change Password (Optional):**
   - Login to admin dashboard
   - Navigate to profile settings
   - Update password to something more secure

4. **Explore Admin Features:**
   - User management
   - System statistics
   - Teacher key generation
   - Avatar catalog management

---

**Last Updated:** November 13, 2025  
**Database:** SQLite (beesmart.db)  
**App Version:** 1.6
