# 🗄️ BeeSmart Database Architecture & Implementation Plan

## Overview
A production-ready database system that powers the BeeSmart app while providing secure external access for teachers, administrators, and data analysts to run custom queries and generate reports.

---

## Database Selection: PostgreSQL

### Why PostgreSQL?
✅ **Free & Open Source**: No licensing costs
✅ **Production-Ready**: Used by major companies (Instagram, Spotify, Netflix)
✅ **Excellent Railway Support**: Native PostgreSQL add-on
✅ **Advanced Features**: JSON columns, full-text search, window functions
✅ **External Access**: Supports remote connections with SSL
✅ **Query Tools**: Compatible with pgAdmin, DBeaver, TablePlus, DataGrip
✅ **Python Integration**: Excellent SQLAlchemy + psycopg2 support
✅ **Backup & Export**: Built-in tools for CSV/JSON export
✅ **Performance**: Handles millions of records efficiently

### Development vs. Production:
- **Development**: SQLite (file-based, no setup, easy testing)
- **Production**: PostgreSQL (Railway-hosted, scalable, secure remote access)

---

## Complete Database Schema

### **1. Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'parent', 'admin')),
    teacher_key VARCHAR(50) UNIQUE, -- Only populated for teacher/parent accounts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    last_login_ip VARCHAR(45),
    profile_picture TEXT, -- Base64 or cloud storage URL
    grade_level VARCHAR(20),
    school_name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    preferences JSONB DEFAULT '{}', -- Stores user settings as JSON
    total_lifetime_points INTEGER DEFAULT 0,
    total_quizzes_completed INTEGER DEFAULT 0,
    account_level INTEGER DEFAULT 1, -- Gamification level
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_teacher_key ON users(teacher_key);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

### **2. Quiz Sessions Table**
```sql
CREATE TABLE quiz_sessions (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
    user_id INTEGER NOT NULL,
    teacher_key VARCHAR(50), -- Links student to teacher for reporting
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    total_words INTEGER NOT NULL,
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2),
    difficulty_level VARCHAR(20) DEFAULT 'normal', -- 'easy', 'normal', 'challenge', 'mixed'
    word_list_name VARCHAR(200),
    word_list_source VARCHAR(50) DEFAULT 'upload', -- 'upload', 'default', 'teacher_assigned'
    time_spent_seconds INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    grade VARCHAR(5), -- 'A+', 'A', 'A-', 'B+', etc.
    quiz_mode VARCHAR(20) DEFAULT 'standard', -- 'standard', 'battle', 'timed_challenge'
    device_type VARCHAR(20), -- 'desktop', 'tablet', 'mobile'
    browser_info VARCHAR(100),
    ip_address VARCHAR(45),
    notes TEXT, -- Student's self-notes or teacher comments
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_accuracy CHECK (accuracy_percentage >= 0 AND accuracy_percentage <= 100)
);

CREATE INDEX idx_quiz_sessions_user_id ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_teacher_key ON quiz_sessions(teacher_key);
CREATE INDEX idx_quiz_sessions_date ON quiz_sessions(session_start DESC);
CREATE INDEX idx_quiz_sessions_completed ON quiz_sessions(completed);
CREATE INDEX idx_quiz_sessions_grade ON quiz_sessions(grade);
```

### **3. Quiz Results Table** (Word-level details)
```sql
CREATE TABLE quiz_results (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    word VARCHAR(100) NOT NULL,
    word_length INTEGER,
    word_difficulty VARCHAR(20), -- 'short', 'medium', 'long', 'very_long'
    is_correct BOOLEAN NOT NULL,
    user_answer TEXT,
    correct_spelling VARCHAR(100),
    time_taken_seconds DECIMAL(6,2),
    time_remaining_seconds DECIMAL(6,2), -- For time bonus calculation
    points_earned INTEGER DEFAULT 0,
    base_points INTEGER DEFAULT 100,
    time_bonus INTEGER DEFAULT 0,
    difficulty_multiplier DECIMAL(3,2) DEFAULT 1.00,
    streak_bonus INTEGER DEFAULT 0,
    first_attempt_bonus INTEGER DEFAULT 0,
    no_hints_bonus INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,
    hint_type VARCHAR(50), -- 'definition', 'phonetic', 'sentence'
    attempts INTEGER DEFAULT 1,
    input_method VARCHAR(20), -- 'keyboard', 'voice'
    voice_confidence DECIMAL(5,4), -- For voice input accuracy tracking
    question_number INTEGER, -- Position in quiz (1, 2, 3...)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_quiz_results_session_id ON quiz_results(session_id);
CREATE INDEX idx_quiz_results_user_id ON quiz_results(user_id);
CREATE INDEX idx_quiz_results_word ON quiz_results(word);
CREATE INDEX idx_quiz_results_is_correct ON quiz_results(is_correct);
CREATE INDEX idx_quiz_results_timestamp ON quiz_results(timestamp DESC);
```

### **4. Teacher Student Links Table**
```sql
CREATE TABLE teacher_students (
    id SERIAL PRIMARY KEY,
    teacher_key VARCHAR(50) NOT NULL,
    teacher_user_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    relationship_type VARCHAR(20) DEFAULT 'teacher', -- 'teacher', 'parent', 'tutor'
    notes TEXT, -- Teacher's notes about student
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (teacher_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(teacher_key, student_id)
);

CREATE INDEX idx_teacher_students_teacher_key ON teacher_students(teacher_key);
CREATE INDEX idx_teacher_students_student_id ON teacher_students(student_id);
```

### **5. Word Lists Table** (Teacher-created lists)
```sql
CREATE TABLE word_lists (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
    created_by_user_id INTEGER NOT NULL,
    list_name VARCHAR(200) NOT NULL,
    description TEXT,
    grade_level VARCHAR(20),
    difficulty_level VARCHAR(20),
    word_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE, -- Can other teachers use it?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_used INTEGER DEFAULT 0,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_word_lists_created_by ON word_lists(created_by_user_id);
CREATE INDEX idx_word_lists_public ON word_lists(is_public);
```

### **6. Word List Items Table**
```sql
CREATE TABLE word_list_items (
    id SERIAL PRIMARY KEY,
    word_list_id INTEGER NOT NULL,
    word VARCHAR(100) NOT NULL,
    sentence TEXT, -- Example sentence
    hint TEXT, -- Custom hint
    difficulty_override VARCHAR(20), -- Manual difficulty setting
    position INTEGER, -- Order in list
    FOREIGN KEY (word_list_id) REFERENCES word_lists(id) ON DELETE CASCADE
);

CREATE INDEX idx_word_list_items_list_id ON word_list_items(word_list_id);
CREATE INDEX idx_word_list_items_word ON word_list_items(word);
```

### **7. Achievements Table**
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    achievement_type VARCHAR(50) NOT NULL, 
    -- Types: 'perfect_quiz', 'streak_10', 'streak_25', 'streak_50',
    --        'points_1000', 'points_5000', 'points_10000',
    --        'speed_demon', 'word_master', '100_quizzes', etc.
    achievement_name VARCHAR(100),
    achievement_description TEXT,
    earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    points_bonus INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}', -- Additional context (e.g., which word, what score)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_achievements_user_id ON achievements(user_id);
CREATE INDEX idx_achievements_type ON achievements(achievement_type);
CREATE INDEX idx_achievements_date ON achievements(earned_date DESC);
```

### **8. Word Mastery Tracking Table**
```sql
CREATE TABLE word_mastery (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    word VARCHAR(100) NOT NULL,
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    times_incorrect INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    mastery_level VARCHAR(20) DEFAULT 'learning', 
    -- Levels: 'learning' (0-50%), 'practicing' (50-80%), 'proficient' (80-95%), 'mastered' (95-100%)
    first_attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    average_time_seconds DECIMAL(6,2),
    fastest_time_seconds DECIMAL(6,2),
    needs_review BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, word)
);

CREATE INDEX idx_word_mastery_user_id ON word_mastery(user_id);
CREATE INDEX idx_word_mastery_word ON word_mastery(word);
CREATE INDEX idx_word_mastery_level ON word_mastery(mastery_level);
CREATE INDEX idx_word_mastery_needs_review ON word_mastery(needs_review);
```

### **9. Session Logs Table** (Audit trail)
```sql
CREATE TABLE session_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL, -- 'login', 'logout', 'quiz_start', 'quiz_complete', etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    additional_data JSONB DEFAULT '{}'
);

CREATE INDEX idx_session_logs_user_id ON session_logs(user_id);
CREATE INDEX idx_session_logs_action ON session_logs(action);
CREATE INDEX idx_session_logs_timestamp ON session_logs(timestamp DESC);
```

### **10. Export Requests Table** (Track report generation)
```sql
CREATE TABLE export_requests (
    id SERIAL PRIMARY KEY,
    requested_by_user_id INTEGER NOT NULL,
    export_type VARCHAR(50), -- 'student_report', 'class_report', 'csv_export', 'pdf_report'
    target_user_id INTEGER, -- If exporting specific student
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    file_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (requested_by_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_export_requests_user_id ON export_requests(requested_by_user_id);
CREATE INDEX idx_export_requests_status ON export_requests(status);
```

---

## Database Views (Pre-computed Reports)

### **View: Student Performance Summary**
```sql
CREATE VIEW student_performance_summary AS
SELECT 
    u.id AS user_id,
    u.username,
    u.display_name,
    u.grade_level,
    COUNT(DISTINCT qs.id) AS total_quizzes,
    SUM(qs.total_words) AS total_words_attempted,
    SUM(qs.correct_count) AS total_correct,
    SUM(qs.incorrect_count) AS total_incorrect,
    ROUND(AVG(qs.accuracy_percentage), 2) AS average_accuracy,
    SUM(qs.total_points) AS lifetime_points,
    MAX(qs.max_streak) AS best_streak_ever,
    MAX(qs.session_start) AS last_quiz_date,
    COUNT(DISTINCT DATE(qs.session_start)) AS days_active
FROM users u
LEFT JOIN quiz_sessions qs ON u.id = qs.user_id AND qs.completed = TRUE
WHERE u.role = 'student'
GROUP BY u.id, u.username, u.display_name, u.grade_level;
```

### **View: Teacher Class Summary**
```sql
CREATE VIEW teacher_class_summary AS
SELECT 
    ts.teacher_key,
    t.display_name AS teacher_name,
    COUNT(DISTINCT ts.student_id) AS total_students,
    COUNT(DISTINCT qs.id) AS total_quizzes_by_class,
    ROUND(AVG(qs.accuracy_percentage), 2) AS class_average_accuracy,
    SUM(qs.total_points) AS total_class_points,
    COUNT(DISTINCT DATE(qs.session_start)) AS class_active_days
FROM teacher_students ts
JOIN users t ON ts.teacher_user_id = t.id
LEFT JOIN quiz_sessions qs ON ts.student_id = qs.user_id AND qs.completed = TRUE
GROUP BY ts.teacher_key, t.display_name;
```

### **View: Words Needing Practice** (Class-wide)
```sql
CREATE VIEW words_needing_practice AS
SELECT 
    qr.word,
    COUNT(DISTINCT qr.user_id) AS students_attempted,
    COUNT(*) AS total_attempts,
    SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) AS correct_attempts,
    ROUND(AVG(CASE WHEN qr.is_correct THEN 100.0 ELSE 0.0 END), 2) AS success_rate,
    ROUND(AVG(qr.time_taken_seconds), 2) AS avg_time_seconds
FROM quiz_results qr
GROUP BY qr.word
HAVING success_rate < 70.0
ORDER BY success_rate ASC, students_attempted DESC;
```

---

## External Database Access Setup

### **1. PostgreSQL Connection Details**
When deployed on Railway, you'll get connection info like:
```
Host: containers-us-west-xyz.railway.app
Port: 5432
Database: railway
Username: postgres
Password: <generated_password>
Connection String: postgresql://postgres:<password>@containers-us-west-xyz.railway.app:5432/railway
```

### **2. Database Clients for External Access**

#### **A. pgAdmin (Free, GUI)**
- Download: https://www.pgadmin.org/
- Create new server connection
- Use Railway PostgreSQL credentials
- Full GUI for queries, exports, table management

#### **B. DBeaver (Free, Multi-DB)**
- Download: https://dbeaver.io/
- Supports PostgreSQL + 80+ databases
- Great for data visualization and exports
- Built-in ER diagram generator

#### **C. TablePlus (Paid, Beautiful UI)**
- Download: https://tableplus.com/
- Native macOS/Windows/Linux apps
- Fast, modern interface
- Excellent for teachers (non-technical users)

#### **D. DataGrip (Paid, JetBrains)**
- Download: https://www.jetbrains.com/datagrip/
- Most powerful IDE for databases
- AI-powered query suggestions
- Best for advanced users

### **3. SQL Client Setup Example (pgAdmin)**
```
1. Open pgAdmin
2. Right-click "Servers" → Create → Server
3. General Tab:
   - Name: BeeSmart Production
4. Connection Tab:
   - Host: containers-us-west-xyz.railway.app
   - Port: 5432
   - Database: railway
   - Username: postgres
   - Password: <Railway password>
5. SSL Tab:
   - SSL Mode: Require
6. Save → Connected! ✅
```

### **4. Security: Read-Only User for Teachers**
```sql
-- Create read-only role for teachers who want direct DB access
CREATE ROLE teacher_readonly WITH LOGIN PASSWORD 'secure_password_here';

-- Grant read access to all tables
GRANT CONNECT ON DATABASE railway TO teacher_readonly;
GRANT USAGE ON SCHEMA public TO teacher_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO teacher_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO teacher_readonly;

-- Teachers can query but NOT modify data
-- Example: Allow viewing students but not editing
GRANT SELECT ON users, quiz_sessions, quiz_results, word_mastery TO teacher_readonly;
```

---

## Useful SQL Queries for Teachers

### **Query 1: Get All Students in My Class**
```sql
SELECT 
    u.display_name AS student_name,
    u.grade_level,
    u.total_lifetime_points AS points,
    u.total_quizzes_completed AS quizzes,
    u.last_login AS last_active
FROM users u
JOIN teacher_students ts ON u.id = ts.student_id
WHERE ts.teacher_key = 'YOUR_TEACHER_KEY_HERE'
    AND ts.is_active = TRUE
ORDER BY u.display_name;
```

### **Query 2: Top 10 Students by Points (Leaderboard)**
```sql
SELECT 
    u.display_name,
    u.total_lifetime_points AS points,
    u.total_quizzes_completed AS quizzes,
    ROUND(AVG(qs.accuracy_percentage), 1) AS avg_accuracy
FROM users u
LEFT JOIN quiz_sessions qs ON u.id = qs.user_id AND qs.completed = TRUE
WHERE u.role = 'student'
GROUP BY u.id, u.display_name, u.total_lifetime_points, u.total_quizzes_completed
ORDER BY u.total_lifetime_points DESC
LIMIT 10;
```

### **Query 3: Student Performance This Week**
```sql
SELECT 
    u.display_name AS student,
    COUNT(qs.id) AS quizzes_this_week,
    SUM(qs.total_points) AS points_earned,
    ROUND(AVG(qs.accuracy_percentage), 1) AS avg_accuracy
FROM quiz_sessions qs
JOIN users u ON qs.user_id = u.id
WHERE qs.session_start >= CURRENT_DATE - INTERVAL '7 days'
    AND qs.completed = TRUE
GROUP BY u.display_name
ORDER BY points_earned DESC;
```

### **Query 4: Words a Specific Student Struggles With**
```sql
SELECT 
    wm.word,
    wm.times_seen,
    wm.times_correct,
    wm.times_incorrect,
    wm.success_rate,
    wm.mastery_level,
    wm.last_attempt_date
FROM word_mastery wm
JOIN users u ON wm.user_id = u.id
WHERE u.username = 'alex_student'
    AND wm.success_rate < 70.0
ORDER BY wm.times_seen DESC, wm.success_rate ASC
LIMIT 20;
```

### **Query 5: Class Performance on Recent Quiz**
```sql
SELECT 
    qs.word_list_name,
    qs.session_start AS date,
    COUNT(DISTINCT qs.user_id) AS students_took_quiz,
    ROUND(AVG(qs.accuracy_percentage), 1) AS class_avg_accuracy,
    SUM(qs.total_points) AS total_class_points,
    MAX(qs.total_points) AS highest_score,
    MIN(qs.total_points) AS lowest_score
FROM quiz_sessions qs
WHERE qs.session_start >= CURRENT_DATE - INTERVAL '7 days'
    AND qs.completed = TRUE
GROUP BY qs.word_list_name, qs.session_start
ORDER BY qs.session_start DESC;
```

### **Query 6: Export Student Data to CSV (Copy result)**
```sql
COPY (
    SELECT 
        qs.session_start AS date,
        u.display_name AS student,
        qs.word_list_name,
        qs.total_words,
        qs.correct_count,
        qs.incorrect_count,
        qs.accuracy_percentage,
        qs.total_points,
        qs.grade,
        qs.time_spent_seconds
    FROM quiz_sessions qs
    JOIN users u ON qs.user_id = u.id
    WHERE qs.completed = TRUE
    ORDER BY qs.session_start DESC
) TO '/tmp/quiz_results.csv' WITH CSV HEADER;
```

---

## Python Backend Integration

### **1. Install Required Packages**
```bash
pip install Flask-SQLAlchemy psycopg2-binary Flask-Migrate Flask-Login
```

### **2. Update `requirements.txt`**
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
psycopg2-binary==2.9.7
Flask-Migrate==4.0.5
Flask-Login==0.6.2
Flask-Bcrypt==1.0.1
python-dotenv==1.0.0
```

### **3. Environment Variables (`.env` file)**
```env
# Development (SQLite)
DATABASE_URL=sqlite:///beesmart.db

# Production (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:<password>@containers-us-west-xyz.railway.app:5432/railway

# Security
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=production
```

### **4. Database Configuration (`config.py`)**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    
    # Auto-detect database URL (Railway provides DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///beesmart.db'
    
    # Fix for Railway's postgres:// vs postgresql:// 
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for query debugging
```

### **5. Database Models (`models.py`)**
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    teacher_key = db.Column(db.String(50), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    profile_picture = db.Column(db.Text)
    grade_level = db.Column(db.String(20))
    school_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    total_lifetime_points = db.Column(db.Integer, default=0)
    total_quizzes_completed = db.Column(db.Integer, default=0)
    
    # Relationships
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_teacher_key(self):
        """Generate unique teacher key like BEE-2024-SMITH-7A3B"""
        import random, string
        year = datetime.now().year
        name_part = self.display_name.split()[0].upper()[:5]
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.teacher_key = f"BEE-{year}-{name_part}-{random_part}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    teacher_key = db.Column(db.String(50), index=True)
    session_start = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_end = db.Column(db.DateTime)
    total_words = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Numeric(5, 2))
    difficulty_level = db.Column(db.String(20), default='normal')
    word_list_name = db.Column(db.String(200))
    time_spent_seconds = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False, index=True)
    grade = db.Column(db.String(5))
    
    # Relationships
    results = db.relationship('QuizResult', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<QuizSession {self.id} - User {self.user_id}>'

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.Integer, db.ForeignKey('quiz_sessions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    word_difficulty = db.Column(db.String(20))
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    user_answer = db.Column(db.Text)
    time_taken_seconds = db.Column(db.Numeric(6, 2))
    points_earned = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    input_method = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<QuizResult {self.word} - {"✓" if self.is_correct else "✗"}>'

class WordMastery(db.Model):
    __tablename__ = 'word_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    times_seen = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    times_incorrect = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Numeric(5, 2))
    mastery_level = db.Column(db.String(20), default='learning', index=True)
    last_attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'word'),)
    
    def update_stats(self, is_correct):
        """Update mastery stats after attempt"""
        self.times_seen += 1
        if is_correct:
            self.times_correct += 1
        else:
            self.times_incorrect += 1
        
        self.success_rate = (self.times_correct / self.times_seen) * 100
        
        # Update mastery level
        if self.success_rate >= 95:
            self.mastery_level = 'mastered'
        elif self.success_rate >= 80:
            self.mastery_level = 'proficient'
        elif self.success_rate >= 50:
            self.mastery_level = 'practicing'
        else:
            self.mastery_level = 'learning'
        
        self.last_attempt_date = datetime.utcnow()
    
    def __repr__(self):
        return f'<WordMastery {self.word} - {self.mastery_level}>'
```

### **6. Database Initialization (`init_db.py`)**
```python
from AjaSpellBApp import app, db
from models import User, QuizSession, QuizResult, WordMastery

def init_database():
    """Initialize database with tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database initialized successfully!")
        
        # Create test admin user
        admin = User(
            username='admin',
            display_name='Administrator',
            email='admin@beesmart.app',
            role='admin'
        )
        admin.set_password('admin123')  # Change in production!
        admin.generate_teacher_key()
        
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin user created: {admin.username}")
        print(f"   Teacher Key: {admin.teacher_key}")

if __name__ == '__main__':
    init_database()
```

### **7. Database Migrations Setup**
```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial database schema"

# Apply migration
flask db upgrade

# Future changes: just run migrate + upgrade again
```

---

## Railway Deployment with PostgreSQL

### **Step 1: Add PostgreSQL Plugin**
```
1. Open Railway project dashboard
2. Click "+ New" → "Database" → "PostgreSQL"
3. Railway auto-generates DATABASE_URL
4. No manual configuration needed!
```

### **Step 2: Update `railway.toml`**
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 AjaSpellBApp:app"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### **Step 3: Environment Variables in Railway**
```
SECRET_KEY = <generate secure random string>
FLASK_ENV = production
DATABASE_URL = <auto-populated by Railway PostgreSQL plugin>
```

---

## Data Export & Backup

### **1. Automated Daily Backups (Railway)**
Railway automatically backs up PostgreSQL databases daily.

### **2. Manual Export via pgAdmin**
```
1. Right-click database → Backup
2. Choose format: Custom, Tar, Plain SQL
3. Select tables or full database
4. Save to local file
```

### **3. CSV Export from Python**
```python
import csv
from models import QuizSession, User

def export_to_csv(filename='quiz_export.csv'):
    """Export all quiz sessions to CSV"""
    sessions = QuizSession.query.join(User).all()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Student', 'Word List', 'Score', 'Points', 'Grade'])
        
        for session in sessions:
            writer.writerow([
                session.session_start,
                session.user.display_name,
                session.word_list_name,
                f"{session.correct_count}/{session.total_words}",
                session.total_points,
                session.grade
            ])
    
    print(f"✅ Exported {len(sessions)} sessions to {filename}")
```

---

## Security Best Practices

### **1. Connection Security**
- ✅ Always use SSL for PostgreSQL connections
- ✅ Railway enforces SSL automatically
- ✅ Never commit `.env` file to Git (add to `.gitignore`)

### **2. Access Control**
```python
# Different access levels
ROLES = {
    'student': ['view_own_data'],
    'teacher': ['view_own_data', 'view_student_data', 'create_word_lists'],
    'parent': ['view_own_data', 'view_child_data'],
    'admin': ['full_access']
}
```

### **3. SQL Injection Prevention**
```python
# ✅ GOOD: Use SQLAlchemy ORM (automatic escaping)
user = User.query.filter_by(username=username).first()

# ❌ BAD: Raw SQL with string formatting
cursor.execute(f"SELECT * FROM users WHERE username='{username}'")

# ✅ ACCEPTABLE: Raw SQL with parameterization
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

---

## Next Steps

1. **Implement models.py** with SQLAlchemy classes
2. **Update AjaSpellBApp.py** to use database instead of session storage
3. **Create migration scripts** for existing data (if any)
4. **Test locally** with SQLite
5. **Deploy to Railway** with PostgreSQL
6. **Set up read-only access** for teachers
7. **Create SQL query templates** for common reports
8. **Document connection instructions** for teachers

---

## Teacher Quick Start Guide (External Access)

**How to Access the Database:**
1. Download **pgAdmin** (free): https://www.pgadmin.org/
2. Open pgAdmin and create new server
3. Use credentials from teacher dashboard (provided by admin)
4. Run pre-made queries or create custom reports
5. Export results to CSV for Excel/Google Sheets

**Common Teacher Queries:**
- See all my students' progress
- Find words students struggle with
- Generate weekly performance reports
- Track individual student improvement over time

---

Ready to start implementing the database? We can begin with Phase 1 (database models + basic integration) right now! 🚀
