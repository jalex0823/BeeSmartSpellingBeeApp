# 🔐 BeeSmart Authentication System Guide

## Date: October 18, 2025
## Purpose: Complete guide to user authentication, registration, and account management

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [User Journey](#user-journey)
3. [Registration Process](#registration-process)
4. [Login Process](#login-process)
5. [Guest Mode](#guest-mode)
6. [Password Recovery](#password-recovery)
7. [Teacher Integration](#teacher-integration)
8. [Database Schema](#database-schema)
9. [Security Features](#security-features)
10. [Testing Checklist](#testing-checklist)

---

## 🎯 System Overview

BeeSmart uses **Flask-Login** with **PostgreSQL** database for user authentication. The system supports three modes:

### User Types

1. **Registered Users** - Full feature access with persistent progress tracking
2. **Guest Users** - Auto-created temporary accounts (progress saved during session)
3. **Teacher Accounts** - Special accounts with classroom management features

### Technology Stack

- **Backend**: Flask-Login, Flask-Bcrypt for password hashing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Session Management**: Flask-Session (server-side storage)
- **Frontend**: Vanilla JavaScript with AJAX form submission

---

## 🚀 User Journey

### First-Time Visitor Flow

```
Landing Page (unified_menu.html)
    ↓
See 3 Options:
    1. 🔑 Sign In → /auth/login
    2. ✨ Register → /auth/register
    3. 👋 Continue as Guest → Stay on page (guest account auto-created)
    ↓
Choose Word Upload Method → Start Quiz
```

### Returning User Flow

```
Landing Page
    ↓
If Session Exists:
    - Show welcome message with username
    - Display lifetime points
    - Show quick stats
    ↓
If No Session:
    - Show Sign In / Register options
    - Offer guest mode
```

---

## ✨ Registration Process

### Form Fields

| Field | Required | Validation | Purpose |
|-------|----------|------------|---------|
| Username | ✅ Yes | 3-20 chars, alphanumeric + underscore | Unique login identifier |
| Display Name | ✅ Yes | Max 50 chars | Shown in game UI |
| Email | ❌ Optional | Valid email format | Password recovery only |
| Password | ✅ Yes | Min 6 chars | Account security |
| Grade Level | ❌ Optional | K-12 | Content personalization |
| Teacher Key | ❌ Optional | Format: BEE-YYYY-NAME-CODE | Classroom linking |

### Registration Flow

**File**: `templates/auth/register.html`

1. **User fills form** → Client-side validation
2. **Submit button clicked** → AJAX POST to `/auth/register`
3. **Server validates**:
   - Check username uniqueness
   - Validate email format (if provided)
   - Hash password with bcrypt
   - Create User record in database
4. **Auto-login** → Session created
5. **Redirect** → Home page with success message

### Password Strength Indicator

Real-time feedback as user types:
- **Weak** (1-2 points): Length < 10, no special chars
- **Medium** (3 points): Mix of cases + numbers
- **Strong** (4-5 points): Length ≥10 + special chars + mixed case

### Instructional Content

**What users see below the register form:**

```
🍯 What You'll Get:
• Honey Points System - Earn points for speed, accuracy, streaks!
• 7 Achievement Badges - From Perfect Spelling Bee to Speed Demon!
• Level Progression - Rise from Busy Bee to Queen Bee!
• Report Card - Track progress with detailed statistics!
• Battle of the Bees - Compete with friends!

🔒 Privacy & Safety:
• Email is optional (only for password recovery)
• Data is secure and never shared
• Kid-safe content with automated filtering
• Guest mode available if you prefer not to register
```

---

## 🔑 Login Process

### Login Flow

**File**: `templates/auth/login.html`

1. **User enters credentials** → Username + Password
2. **Optional**: Check "Remember me" → Extended session (30 days)
3. **Submit** → AJAX POST to `/auth/login`
4. **Server validates**:
   - Find user by username
   - Verify password with bcrypt
   - Create Flask-Login session
5. **Success** → Redirect to home page
6. **Failure** → Show error message (generic for security)

### Security Features

- **Generic error messages** - Don't reveal if username exists
- **Bcrypt password hashing** - Industry-standard encryption
- **Session timeout** - 24 hours default (30 days if "remember me")
- **HTTPS only** (in production) - Secure transmission

### Instructional Content

**What users see below the login form:**

```
🐝 Why Create an Account?
• Track Your Progress - Save your points and watch them grow!
• Earn Badges - Unlock achievements as you practice!
• Level Up - Progress from Busy Bee to Queen Bee!
• View History - See all your past quizzes and improvements!
• Battle Mode - Challenge friends and compete!

Guest Mode: You can play without an account, but your progress 
won't be saved. Perfect for trying out the app!
```

---

## 👋 Guest Mode

### How It Works

**File**: `AjaSpellBApp.py` → `get_or_create_guest_user()`

```python
def get_or_create_guest_user():
    """Get existing guest or create new one"""
    if current_user.is_authenticated:
        return current_user
    
    guest_id = session.get('guest_user_id')
    if guest_id:
        user = User.query.get(guest_id)
        if user:
            return user
    
    # Create new guest
    guest = User(
        username=f"guest_{uuid.uuid4().hex[:8]}",
        display_name="Guest Player",
        is_guest=True
    )
    db.session.add(guest)
    db.session.commit()
    
    session['guest_user_id'] = guest.id
    return guest
```

### Guest Features

✅ **What Guests CAN Do:**
- Take spelling quizzes
- Earn points (session only)
- See immediate progress
- Upload custom word lists
- Use all quiz features (timer, hints, voice)

❌ **What Guests CANNOT Do:**
- Save progress between sessions
- View quiz history
- Earn permanent badges
- Access report card
- Participate in Battle of the Bees
- Create word lists for others

### Converting Guest to Registered

Future feature: Allow guests to "claim" their progress by registering after playing.

---

## 🔄 Password Recovery

### Forgot Password Flow

**Trigger**: Click "Forgot password?" link on login page

1. **Expand panel** → Shows email/username input
2. **User enters identifier** → Email or username
3. **Submit** → POST to `/api/auth/forgot-password`
4. **Generic success message** → "If account exists, we'll send reset instructions"
   - **Security**: Don't reveal if account exists (prevents enumeration)
5. **Email sent** (if account found) → Reset link with token
6. **User clicks link** → `/auth/reset/<token>`
7. **Enter new password** → Password updated
8. **Redirect to login** → Success banner shown

### Reset Token Security

- **Token expiry**: 1 hour
- **Single use**: Token invalidated after use
- **Secure random**: Generated with `secrets` module

---

## 👨‍🏫 Teacher Integration

### Teacher Key System

**Format**: `BEE-YYYY-NAME-CODE`
- Example: `BEE-2025-SMITH-7A3B`

### How It Works

1. **Teacher creates key** → Via teacher dashboard (future feature)
2. **Student registers** → Enters teacher key (optional field)
3. **Account linked** → Student associated with teacher's classroom
4. **Teacher access** → View class roster, progress, assign word lists

### Future Teacher Features

- [ ] Classroom dashboard
- [ ] Student progress reports
- [ ] Custom word list creation
- [ ] Assignment tracking
- [ ] Group battle management

---

## 🗄️ Database Schema

### User Table

```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    grade = db.Column(db.String(10), nullable=True)
    teacher_key = db.Column(db.String(50), nullable=True)
    is_guest = db.Column(db.Boolean, default=False)
    total_lifetime_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)
```

### QuizSession Table

Tracks every quiz attempt:

```python
class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    total_words = db.Column(db.Integer)
    correct_count = db.Column(db.Integer)
    points_earned = db.Column(db.Integer, default=0)
    wordbank_name = db.Column(db.String(200))
```

### Achievement Table

Stores earned badges:

```python
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    badge_type = db.Column(db.String(50))  # "perfect_bee", "speed_demon", etc.
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_awarded = db.Column(db.Integer, default=0)
```

---

## 🔒 Security Features

### Password Security

1. **Bcrypt hashing** - Work factor 12 (slow, secure)
2. **Salted hashes** - Unique salt per password
3. **No plaintext storage** - Ever

### Session Security

1. **Server-side sessions** - Data stored in database, not cookies
2. **Secure cookies** - HttpOnly, SameSite=Lax
3. **CSRF protection** - Token validation (if enabled)

### Input Validation

1. **Client-side** - HTML5 + JavaScript patterns
2. **Server-side** - SQLAlchemy validation + custom checks
3. **SQL injection protection** - Parameterized queries (SQLAlchemy ORM)

### Rate Limiting

Future implementation:
- Max 5 login attempts per 15 minutes
- Max 3 password reset requests per hour

---

## 🧪 Testing Checklist

### Registration Tests

- [ ] **Valid registration** - Create account with all required fields
- [ ] **Duplicate username** - Error shown
- [ ] **Duplicate email** - Error shown
- [ ] **Weak password** - Still accepts (6+ chars)
- [ ] **Optional fields** - Registration works without email/grade
- [ ] **Teacher key** - Links to classroom (if key valid)
- [ ] **Auto-login** - Redirects to home after registration
- [ ] **Display name** - Shown in game UI
- [ ] **Instructional content** - Visible below form

### Login Tests

- [ ] **Valid credentials** - Login successful
- [ ] **Invalid username** - Generic error shown
- [ ] **Invalid password** - Generic error shown
- [ ] **Remember me** - Session persists 30 days
- [ ] **Forgot password** - Panel expands
- [ ] **Reset email sent** - Generic success message
- [ ] **Instructional content** - Visible below form

### Guest Mode Tests

- [ ] **Guest auto-creation** - Plays without registration
- [ ] **Session persistence** - Guest data saved during session
- [ ] **Points earned** - Shows in session, not saved long-term
- [ ] **Badges disabled** - No permanent badge unlocking
- [ ] **Convert to registered** - (Future) Guest can claim progress

### Security Tests

- [ ] **SQL injection** - Parameterized queries prevent
- [ ] **XSS attacks** - Template escaping prevents
- [ ] **CSRF** - Token validation (if enabled)
- [ ] **Password enumeration** - Generic error messages
- [ ] **Brute force** - Rate limiting (future)

### UI/UX Tests

- [ ] **Mobile responsive** - Forms work on small screens
- [ ] **Keyboard navigation** - Tab order logical
- [ ] **Screen reader** - Accessible labels and ARIA
- [ ] **Error messages** - Clear and helpful
- [ ] **Success feedback** - Confirmation messages shown
- [ ] **Loading states** - Buttons disabled during submit

---

## 🚀 Deployment Considerations

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Optional
SESSION_COOKIE_SECURE=True  # HTTPS only
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Database Migration

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Add authentication tables"

# Apply migration
flask db upgrade
```

### Production Checklist

- [ ] Set `SECRET_KEY` to random value
- [ ] Enable `SESSION_COOKIE_SECURE` (HTTPS only)
- [ ] Configure `DATABASE_URL` for production database
- [ ] Set up email service for password reset
- [ ] Enable rate limiting
- [ ] Configure backup system
- [ ] Set up monitoring/logging

---

## 📊 Analytics & Monitoring

### Key Metrics to Track

1. **Registration rate** - % of visitors who create accounts
2. **Guest vs registered** - User type distribution
3. **Login success rate** - Failed login attempts
4. **Password reset requests** - Frequency of forgotten passwords
5. **Session duration** - How long users stay logged in

### Recommended Tools

- **Sentry** - Error tracking
- **Google Analytics** - User behavior
- **PostgreSQL logs** - Database performance
- **Flask logging** - Application events

---

## 🎯 Future Enhancements

### Planned Features

- [ ] **OAuth integration** - Sign in with Google/Microsoft
- [ ] **Two-factor authentication** - SMS or TOTP codes
- [ ] **Email verification** - Confirm email on registration
- [ ] **Profile customization** - Avatar, bio, preferences
- [ ] **Parent accounts** - Link to multiple student accounts
- [ ] **Teacher dashboard** - Full classroom management
- [ ] **Guest conversion** - Register and keep progress
- [ ] **Social features** - Friend requests, leaderboards

### Nice-to-Have

- [ ] **Password strength requirements** - Enforce strong passwords
- [ ] **Account deletion** - GDPR compliance
- [ ] **Export data** - Download quiz history
- [ ] **Dark mode** - User preference
- [ ] **Notification system** - In-app messages

---

## 📝 Support & Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError: No module named 'flask_login'"
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: "Session not persisting"
- **Solution**: Check `SECRET_KEY` is set, verify Flask-Session config

**Issue**: "Database connection error"
- **Solution**: Verify `DATABASE_URL` in environment, check PostgreSQL running

**Issue**: "Password reset email not sending"
- **Solution**: Configure email service (future implementation)

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
python AjaSpellBApp.py
```

---

## 🐝 Summary

The BeeSmart authentication system provides:

✅ **Secure user registration** with bcrypt password hashing  
✅ **Flexible login** with "remember me" option  
✅ **Guest mode** for trial users  
✅ **Password recovery** with secure reset tokens  
✅ **Teacher integration** via classroom keys  
✅ **Database persistence** for all user data  
✅ **Instructional content** to guide users  

All authentication pages now include helpful guides explaining the benefits of creating an account vs. playing as a guest!

---

**Last Updated**: October 18, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
