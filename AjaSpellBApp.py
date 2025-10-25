# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import csv
import os
import re
import json
import time
import random
import threading
import uuid
import logging
from datetime import datetime, timedelta
import secrets
import hashlib
from typing import List, Dict, Optional
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file, Response, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from PIL import Image
from sqlalchemy import inspect, exc as sa_exc, or_, and_, not_

# Database imports
from config import get_config
from models import db, User, QuizSession, QuizResult, WordMastery, TeacherStudent, Achievement
from models import WordList, WordListItem
from models import PasswordResetToken
from models import SessionLog
from models import SpeedRoundConfig, SpeedRoundScore
from models import Avatar, BattleSession

# Word generation for speed rounds
from word_generator import generate_words_by_difficulty, get_difficulty_multiplier, generate_mixed_words

# Optional OCR support - graceful degradation if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR available")
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
    print("⚠️ Tesseract OCR not available - image upload will show error message")

# Backwards-compatibility alias for test suites
OCR_AVAILABLE = TESSERACT_AVAILABLE

print("="*70)
print("🐝 BeeSmart Spelling Bee App - Starting Up")
print("="*70)
print(f"📍 Python version: {sys.version}")
print(f"📍 Platform: {sys.platform}")
print(f"📍 Working directory: {os.getcwd()}")
print("="*70)

# Dictionary API with robust error handling
try:
    from dictionary_api import dictionary_api
    def DICT_LOOKUP(word: str):
        return dictionary_api.lookup_word(word)
    print("✅ Dictionary API loaded successfully")
except Exception as e:
    print(f"⚠️ Dictionary API not available: {e}")
    # Safe fallback when dictionary API isn't available
    def DICT_LOOKUP(word: str):
        return {
            "definition": f"A placeholder definition for '{word}'.",
            "example": f"The _____ is spelled '{word}'.",
            "phonetic": ""
        }

# Content Filter and Guardian Reporting System
try:
    from content_filter_guardian import (
        filter_content_with_tracking, 
        get_content_filter_status, 
        violation_tracker,
        ContentViolationTracker
    )
    print("✅ Content Filter with Guardian Reporting loaded successfully")
    CONTENT_FILTER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Content Filter not available: {e}")
    # Fallback functions if content filter isn't available
    def filter_content_with_tracking(words, session_context):
        # Simple fallback - just return words as-is when content filter unavailable
        # The original filtering will still happen in the upload processing functions
        return words, [], []
    
    def get_content_filter_status(session_context):
        return {'session_id': 'fallback', 'violation_count_24h': 0, 'warning_level': 'green', 'guardian_notification_triggered': False}
    
    CONTENT_FILTER_AVAILABLE = False

# Dictionary Cache Functions
DICTIONARY_CACHE_FILE = "data/dictionary.json"
SIMPLE_WIKTIONARY_FILE = "data/simple-wiktionary.jsonl"

def load_simple_wiktionary():
    """Load Simple English Wiktionary from JSONL file - 50K+ words!"""
    words = {}
    try:
        if os.path.exists(SIMPLE_WIKTIONARY_FILE):
            print(f"📚 Loading Simple English Wiktionary...")
            with open(SIMPLE_WIKTIONARY_FILE, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        word = entry.get('word', '').lower().strip()
                        
                        # Extract definition and example
                        senses = entry.get('senses', [])
                        if senses and word:
                            first_sense = senses[0]
                            glosses = first_sense.get('glosses', [])
                            examples = first_sense.get('examples', [])
                            
                            definition = glosses[0] if glosses else ""
                            example_obj = examples[0] if examples else {}
                            example = example_obj.get('text', '') if isinstance(example_obj, dict) else ""
                            
                            if definition:  # Only store words with definitions
                                words[word] = {
                                    "definition": definition,
                                    "example": example,
                                    "source": "simple-wiktionary"
                                }
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
                    except Exception as e:
                        continue  # Skip problematic entries
                        
            print(f"✅ Loaded {len(words):,} words from Simple English Wiktionary")
            return words
        else:
            print(f"⚠️ Simple Wiktionary not found: {SIMPLE_WIKTIONARY_FILE}")
    except Exception as e:
        print(f"❌ Failed to load Simple Wiktionary: {e}")
    return {}

# 🏆 Badge metadata for display
BADGE_METADATA = {
    'perfect_game': {
        'icon': '🌟',
        'name': 'Perfect Game',
        'description': '100% accuracy, no hints, no mistakes',
        'rarity': 'epic',
        'points': 500
    },
    'speed_demon': {
        'icon': '⚡',
        'name': 'Speed Demon',
        'description': 'Average answer time < 10 seconds',
        'rarity': 'rare',
        'points': 200
    },
    'persistent_learner': {
        'icon': '📚',
        'name': 'Persistent Learner',
        'description': 'Complete 50+ words in one session',
        'rarity': 'rare',
        'points': 150
    },
    'hot_streak': {
        'icon': '🔥',
        'name': 'Hot Streak',
        'description': '10+ correct answers in a row',
        'rarity': 'common',
        'points': 100
    },
    'comeback_kid': {
        'icon': '🎯',
        'name': 'Comeback Kid',
        'description': 'Succeed after multiple wrong attempts',
        'rarity': 'rare',
        'points': 100
    },
    'honey_hunter': {
        'icon': '🍯',
        'name': 'Honey Hunter',
        'description': 'Use hints wisely (< 20% of words)',
        'rarity': 'common',
        'points': 75
    },
    'early_bird': {
        'icon': '🐝',
        'name': 'Early Bird',
        'description': 'Complete quiz in under 5 minutes',
        'rarity': 'common',
        'points': 50
    }
}

def load_dictionary_cache():
    """Load cached dictionary entries from JSON file"""
    try:
        if os.path.exists(DICTIONARY_CACHE_FILE):
            with open(DICTIONARY_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                words = data.get('words', {})
                print(f"✅ Loaded dictionary cache with {len(words)} words from {DICTIONARY_CACHE_FILE}")
                return words
        else:
            print(f"⚠️ Dictionary cache file not found: {DICTIONARY_CACHE_FILE}")
    except Exception as e:
        print(f"❌ Failed to load dictionary cache: {e}")
    return {}

def save_dictionary_cache(cache_data):
    """Save dictionary cache to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DICTIONARY_CACHE_FILE), exist_ok=True)
        
        # Load existing data or create new
        if os.path.exists(DICTIONARY_CACHE_FILE):
            with open(DICTIONARY_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "_metadata": {
                    "version": "1.6",
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "description": "BeeSmart dictionary cache - API fetched definitions only"
                },
                "words": {},
                "stats": {
                    "total_words": 0,
                    "api_calls": 0,
                    "cache_hits": 0
                }
            }
        
        # Update words cache and stats
        data['words'].update(cache_data)
        data['last_updated'] = datetime.now().isoformat()
        data['stats']['total_words'] = len(data['words'])
        
        # Save to file
        with open(DICTIONARY_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Dictionary cache updated with {len(cache_data)} entries")
        
    except Exception as e:
        print(f"Warning: Failed to save dictionary cache: {e}")

# Load cache at startup
print("🔧 Loading dictionary cache...")
DICTIONARY_CACHE = load_dictionary_cache()

# Load Simple English Wiktionary (50K+ words with definitions)
# DISABLED for Railway - this takes too long and blocks startup
# Load it in background after app starts
print("🔧 Simple English Wiktionary loading scheduled for background...")
SIMPLE_WIKTIONARY = {}  # Start with empty dict, will load async

def load_wiktionary_background():
    """Load wiktionary in background thread after app starts"""
    global SIMPLE_WIKTIONARY
    print("🔧 Background: Loading Simple English Wiktionary (this may take 30-60 seconds)...")
    SIMPLE_WIKTIONARY = load_simple_wiktionary()
    print(f"✅ Background: Wiktionary loaded with {len(SIMPLE_WIKTIONARY)} words")

# Start background loading
import threading
wiktionary_thread = threading.Thread(target=load_wiktionary_background, daemon=True)
wiktionary_thread.start()

print("✅ Dictionary resources initialized (Wiktionary loading in background)")

# Speed Round logging configuration for Railway
speed_logger = logging.getLogger('SpeedRound_Railway')
if not speed_logger.handlers:
    speed_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - SpeedRound - %(levelname)s - %(message)s'))
    speed_logger.addHandler(handler)

def get_railway_speed_round_engine_options():
    """Get Railway-optimized engine options for Speed Round"""
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
        return {
            'pool_timeout': 5,          # Shorter timeout for Railway
            'pool_recycle': 300,        # 5 minutes
            'pool_pre_ping': True,      # Test connections
            'pool_size': 3,             # Smaller pool for Speed Round
            'max_overflow': 2,          # Limited overflow
            'connect_args': {
                'connect_timeout': 5,
                'application_name': 'BeeSmart_SpeedRound',
                'options': '-c statement_timeout=10000'  # 10 second query timeout
            }
        }
    return {}

def generate_smart_fallback(word):
    """Generate an educational challenge for words not found via API."""
    word_len = len(word)
    word_lower = word.lower()
    
    # Pattern-based fallbacks for common word types
    if word_lower.endswith('ing'):
        return {
            "definition": f"Action word ending in 'ing'",
            "example": f"The children are _____ at the playground",
            "source": "pattern_fallback"
        }
    elif word_lower.endswith('ed'):
        return {
            "definition": f"Past tense word ending in 'ed'", 
            "example": f"Yesterday, she _____ her homework carefully",
            "source": "pattern_fallback"
        }
    elif word_lower.endswith('ly'):
        return {
            "definition": f"Descriptive word ending in 'ly'",
            "example": f"The student worked very _____ on the project",
            "source": "pattern_fallback"
        }
    elif word_lower.endswith('tion') or word_lower.endswith('sion'):
        return {
            "definition": f"Noun ending in 'tion' or 'sion'",
            "example": f"The _____ was announced at the school assembly",
            "source": "pattern_fallback"
        }
    else:
        # Generic fallback with more helpful context
        return {
            "definition": f"Practice spelling this {word_len}-letter word",
            "example": f"Listen carefully and spell _____ correctly",
            "source": "generic_fallback",
            "note": "Definition not available - focus on correct spelling"
        }

def _blank_word(text, word):
    """Backend safety blanker - replace target word AND variations with blanks in text.
    Handles: admire → admired, admiring, admires, etc.
    Also handles capitalized forms, plural, and common morphological changes."""
    if not text or not word:
        return text or ""
    
    word_lower = word.lower()
    
    # Build comprehensive list of variations
    variations = [
        word,              # Original case
        word_lower,        # Lowercase
        word.capitalize(), # Capitalized
        word.upper(),      # Uppercase
    ]
    
    # Add common suffixes
    suffixes = ["s", "es", "ed", "d", "ing", "er", "est", "ly", "ness", "ment", "tion", "sion"]
    
    for suffix in suffixes:
        variations.append(word_lower + suffix)
    
    # For words ending in 'e', try without the 'e' + suffix
    if word_lower.endswith('e'):
        base = word_lower[:-1]
        for suffix in ["ing", "ed", "er", "est"]:
            variations.append(base + suffix)
    
    # For words ending in 'y', try 'i' + suffix
    if word_lower.endswith('y') and len(word_lower) > 1:
        base = word_lower[:-1] + 'i'
        for suffix in ["es", "ed", "er", "est", "ness"]:
            variations.append(base + suffix)
    
    # For words ending in consonant, try doubling + suffix
    if len(word_lower) >= 3 and word_lower[-1] not in 'aeiouy':
        double_base = word_lower + word_lower[-1]
        for suffix in ["ing", "ed", "er", "est"]:
            variations.append(double_base + suffix)
    
    # Remove duplicates and sort by length (longest first to avoid partial replacements)
    variations = sorted(set(variations), key=len, reverse=True)
    
    # Replace all variations with blanks
    result = text
    for variation in variations:
        result = re.sub(rf"\b{re.escape(variation)}\b", "_____", result, flags=re.IGNORECASE)
    
    return result

def get_word_info(word):
    """Get definition and example sentence for a word. 
    Priority: 1) Simple Wiktionary (50K words), 2) API cache, 3) API lookup
    Returns: Formatted definition string OR "Definition not available" for spelling-only quiz."""
    word_lower = word.lower()
    
    # PRIORITY 1: Check Simple English Wiktionary FIRST (50K+ words, kid-friendly)
    if word_lower in SIMPLE_WIKTIONARY:
        word_data = SIMPLE_WIKTIONARY[word_lower]
        definition = word_data.get("definition", "")
        example = word_data.get("example", "")
        
        if definition:
            # If we have an example, use it; otherwise create generic sentence
            if example and len(example) > 10:
                example = _blank_word(example, word)
                print(f"📖 Found '{word}' in Simple Wiktionary with example")
                return f"{definition}. Fill in the blank: {example}"
            else:
                # Have definition but no example
                print(f"� Found '{word}' in Simple Wiktionary (no example)")
                return f"{definition}. Fill in the blank: Can you spell _____ correctly?"
    
    # PRIORITY 2: Check API cache
    if word_lower in DICTIONARY_CACHE:
        word_data = DICTIONARY_CACHE[word_lower]
        definition = word_data.get("definition", "")
        example = word_data.get("example", "")
        if definition and example:
            example = _blank_word(example, word)
            print(f"✅ Found '{word}' in API cache")
            return f"{definition}. Fill in the blank: {example}"
    
    # PRIORITY 3: Try API lookup (rarely needed with 50K Wiktionary!)
    print(f"🔍 Word '{word}' not in Wiktionary, trying API...")
    api_result = DICT_LOOKUP(word)
    print(f"DEBUG get_word_info: API returned for '{word}': {api_result}")
    
    # Check if API returned real data (not placeholder)
    if api_result and not api_result.get("definition", "").startswith("A placeholder"):
        # Cache successful API result
        cache_entry = {word_lower: api_result}
        save_dictionary_cache(cache_entry)
        DICTIONARY_CACHE.update(cache_entry)
        
        definition = api_result.get("definition", "")
        example = api_result.get("example", "")
        example = _blank_word(example, word)
        print(f"✅ API returned definition for '{word}'")
        return f"{definition}. Fill in the blank: {example}"
    
    # PRIORITY 4: Smart fallback to guarantee a helpful prompt
    try:
        fb = generate_smart_fallback(word)
        definition = fb.get("definition", "A word to spell")
        example = fb.get("example", "Can you spell _____ correctly?")
        example = _blank_word(example, word)
        print(f"🟨 Fallback used for '{word}' ({fb.get('source','fallback')})")
        return f"{definition}. Fill in the blank: {example}"
    except Exception as _e:
        # Absolute last resort
        print(f"⚠️ Fallback failed for '{word}': {_e}")
        return "Definition not available for this word. Listen carefully and spell _____ correctly"


def validate_wordbank_definitions(wordbank: List[Dict]) -> tuple[bool, str]:
    """
    Validate that all words in the wordbank have valid sentences/hints.
    Returns (is_valid, error_message)
    """
    missing_definitions = []
    
    for word_rec in wordbank:
        word = word_rec.get("word", "")
        sentence = word_rec.get("sentence", "").strip()
        hint = word_rec.get("hint", "").strip()
        
        # Check if word has neither sentence nor hint
        if not sentence and not hint:
            missing_definitions.append(word)
        # Check if sentence is placeholder (failed enrichment)
        elif sentence and sentence.startswith("A placeholder"):
            missing_definitions.append(f"{word} (placeholder definition)")
    
    if missing_definitions:
        words_list = ", ".join(missing_definitions[:5])
        if len(missing_definitions) > 5:
            words_list += f", ... and {len(missing_definitions) - 5} more"
        
        error_msg = f"Definition issues found for {len(missing_definitions)} word(s): {words_list}. Please check your word list and try again."
        return False, error_msg
    
    return True, ""


def build_phonetic_spelling(word: str) -> str:
    """Create a friendly spelled-out version of a word (e.g., B E E)."""
    if not word:
        return ""
    letters = []
    for ch in word:
        if ch.isalpha():
            letters.append(ch.upper())
        elif ch.isdigit():
            letters.append(ch)
        elif ch in {"'", "-"}:
            # use simple descriptors for punctuation inside words
            letters.append("dash" if ch == '-' else "apostrophe")
    if not letters:
        letters = list(word.upper())
    return " ".join(letters)

# Optional imports guarded so the app still runs if you only do TXT/CSV
try:
    import docx  # python-docx
except Exception:  # pragma: no cover
    docx = None

try:
    from pdfminer.high_level import extract_text  # pdfminer.six
except Exception:  # pragma: no cover
    extract_text = None

# ============================================================================
# FLASK APP INITIALIZATION WITH DATABASE & AUTHENTICATION
# ============================================================================

print("🔧 Creating Flask app...")
app = Flask(__name__)

# Load configuration from config.py (includes database settings)
print("🔧 Loading configuration...")
app.config.from_object(get_config())
print(f"✅ Config loaded - Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

# Backwards compatibility: keep old secret key if not in config
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ.get("SPELLING_APP_SECRET", "dev-secret-change-me")

# Railway Speed Round optimization
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    # Configure Flask session for Railway Speed Round
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    
    # Update SQLAlchemy configuration for Railway Speed Round optimization
    railway_engine_options = get_railway_speed_round_engine_options()
    if railway_engine_options and hasattr(app.config, 'SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'].update(railway_engine_options)
        
    speed_logger.info("Speed Round Railway configuration applied")


# Enhanced session configuration for mobile compatibility
# Detect if running on HTTPS (production) or HTTP (local dev)
is_production = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("PORT")
print(f"🔧 Environment: {'PRODUCTION (Railway)' if is_production else 'DEVELOPMENT (Local)'}")

app.config.update(
    SESSION_COOKIE_SECURE=bool(is_production),  # True in production (HTTPS), False locally
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # Better mobile compatibility than 'Strict'
    PERMANENT_SESSION_LIFETIME=3600 * 24 * 7,  # 7 days (increased from 1 day)
    SESSION_COOKIE_NAME='beesmart_session',
    SESSION_REFRESH_EACH_REQUEST=True,  # Keep session alive on activity
    SESSION_COOKIE_PATH='/',  # Ensure cookie works across all paths
    SESSION_COOKIE_DOMAIN=None,  # Let Flask auto-detect domain
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max upload
)

# Initialize database
print("🔧 Initializing database...")
db.init_app(app)
print("✅ Database initialized")

# Initialize Socket.IO for Battle of the Bees
try:
    from app_socketio import socketio
    socketio.init_app(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    print("✅ Socket.IO initialized for Battle of the Bees")
except Exception as e:
    print(f"⚠️ Socket.IO initialization failed: {e}")
    print("⚠️ Battles will work without real-time updates")

# --- Safety net: ensure DB tables exist in deployed environments (e.g., Railway) ---
def _ensure_db_initialized() -> None:
    """Create tables on first boot if they don't exist.

    This avoids 500s like 'no such table: users' or 'relation "users" does not exist'
    when the database hasn't been initialized yet in ephemeral deployments.
    """
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            # Use one canonical table to check overall schema readiness
            has_users = inspector.has_table('users')
            if not has_users:
                print("🐝 Initializing database schema (create_all)")
                db.create_all()
                print("✅ Database tables created")
    except Exception as e:
        # Never crash app startup; just log. Auth routes will still surface a friendly error.
        print(f"⚠️ DB initialization check failed: {e}")

# Run DB initialization in a background thread to avoid blocking app startup/healthcheck
def _schedule_db_init_background():
    def _runner():
        try:
            # Small delay to ensure the server is up before any heavy DB checks
            time.sleep(0.2)
        except Exception:
            pass
        _ensure_db_initialized()

    try:
        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        print("🔧 DB initialization scheduled in background")
    except Exception as e:
        print(f"⚠️ Failed to schedule DB initialization: {e}")

_schedule_db_init_background()

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated
login_manager.login_message = '🐝 Please log in to save your progress!'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

# TEMPORARY: Disable database sessions to fix Railway deployment
# Using default Flask sessions until we can diagnose the hanging issue
SESSION_INIT_SUCCESS = False
print("⚠️ Database sessions temporarily disabled for Railway deployment")
print("⚠️ Using default Flask sessions (data may be lost on redeploy)")

# TODO: Re-enable once Railway database connection is stable
# try:
#     from flask_session import Session
#     app.config.update(
#         SESSION_TYPE="sqlalchemy",
#         SESSION_SQLALCHEMY=db,
#         SESSION_SQLALCHEMY_TABLE='sessions',
#         SESSION_PERMANENT=True,
#         SESSION_USE_SIGNER=True,
#         SESSION_KEY_PREFIX='beesmart_',
#     )
#     sess = Session(app)
#     SESSION_INIT_SUCCESS = True
#     print("✅ Flask-Session configured (database sessions enabled)")
# except Exception as _e:
#     print(f"⚠️ Flask-Session failed: {_e}")
#     SESSION_INIT_SUCCESS = False

print(f"🔧 Session config: SECURE={app.config['SESSION_COOKIE_SECURE']}, SAMESITE={app.config['SESSION_COOKIE_SAMESITE']}, PRODUCTION={is_production}")

# Dev/test toggle for exposing reset token peek endpoint
ALLOW_DEV_RESET_PEEK = os.getenv('ALLOW_DEV_RESET_PEEK') == '1'

# 🏆 Template filters for badge display
@app.template_filter('badge_icon')
def get_badge_icon_filter(badge_type):
    """Get emoji icon for badge type"""
    return BADGE_METADATA.get(badge_type, {}).get('icon', '🏆')

@app.template_filter('badge_name')
def get_badge_name_filter(badge_type):
    """Get display name for badge type"""
    return BADGE_METADATA.get(badge_type, {}).get('name', 'Achievement')

@app.template_filter('badge_rarity')
def get_badge_rarity_filter(badge_type):
    """Get rarity tier for badge type"""
    return BADGE_METADATA.get(badge_type, {}).get('rarity', 'common')

@app.template_filter('badge_description')
def get_badge_description_filter(badge_type):
    """Get description for badge type"""
    return BADGE_METADATA.get(badge_type, {}).get('description', 'Special achievement')

@app.template_filter('gpa_to_grade')
def gpa_to_grade_filter(gpa):
    """Convert numerical GPA (0-4.0) to letter grade"""
    try:
        gpa_value = float(gpa) if gpa else 0.0
    except (ValueError, TypeError):
        return "N/A"
    
    if gpa_value >= 3.85:
        return "A+"
    elif gpa_value >= 3.50:
        return "A"
    elif gpa_value >= 3.15:
        return "A-"
    elif gpa_value >= 2.85:
        return "B+"
    elif gpa_value >= 2.50:
        return "B"
    elif gpa_value >= 2.15:
        return "B-"
    elif gpa_value >= 1.85:
        return "C+"
    elif gpa_value >= 1.50:
        return "C"
    elif gpa_value >= 1.15:
        return "C-"
    elif gpa_value >= 0.85:
        return "D+"
    elif gpa_value >= 0.50:
        return "D"
    elif gpa_value > 0:
        return "D-"
    else:
        return "N/A"

@app.template_filter('format_number')
def format_number_filter(number):
    """Format number with comma separators (e.g., 23746 -> 23,746)"""
    try:
        if number is None:
            return "0"
        
        # Convert to int if it's a float with no decimal part
        if isinstance(number, float) and number.is_integer():
            number = int(number)
        
        # Format with comma separators
        if isinstance(number, (int, float)):
            return f"{number:,}"
        
        # Handle string numbers
        if isinstance(number, str):
            try:
                num = float(number)
                if num.is_integer():
                    return f"{int(num):,}"
                else:
                    return f"{num:,.1f}"
            except ValueError:
                return str(number)
        
        return str(number)
        
    except Exception as e:
        print(f"Error formatting number {number}: {e}")
        return str(number) if number is not None else "0"

@app.template_filter('format_honey_points')
def format_honey_points_filter(points):
    """Format honey points with commas and bee emoji"""
    try:
        formatted = format_number_filter(points)
        return f"🍯 {formatted}"
    except Exception:
        return f"🍯 {points or 0}"

@app.template_filter('format_percentage')
def format_percentage_filter(value):
    """Format percentage with proper decimal places"""
    try:
        if value is None:
            return "0%"
        
        num = float(value)
        if num == int(num):
            return f"{int(num)}%"
        else:
            return f"{num:.1f}%"
            
    except Exception:
        return f"{value or 0}%"


# Ensure sessions are persistent and trackable
@app.before_request
def ensure_session():
    """Ensure every request has a session with unique ID and permanent flag"""
    if not session.get("session_id"):
        session["session_id"] = str(uuid.uuid4())
        session.permanent = True  # Use PERMANENT_SESSION_LIFETIME
        print(f"DEBUG: New session created - id={session['session_id']}")
    elif not session.permanent:
        session.permanent = True  # Ensure existing sessions are permanent
        print(f"DEBUG: Made existing session permanent - id={session.get('session_id')}")


# --- Session Logging Helper --------------------------------------------------
def log_session_action(action: str, user_id: Optional[int] = None, data: Optional[Dict] = None):
    """Best-effort audit log that won't break flow on failure."""
    try:
        entry = SessionLog(
            user_id=user_id,
            action=action,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            additional_data=data or {}
        )
        db.session.add(entry)
    except Exception as e:
        app.logger.debug(f"SessionLog failed for {action}: {e}")


# --- Public URL helpers (for emails) ----------------------------------------
def _public_base_url() -> str:
    """Resolve a public base URL for building absolute links in emails."""
    try:
        if request and request.url_root:
            return request.url_root.rstrip('/')
    except Exception:
        pass
    base = app.config.get('APP_BASE_URL')
    if base:
        return str(base).rstrip('/')
    # Default production base (Railway)
    return 'https://beesmartspellingbee.up.railway.app'


def _static_url(path: str) -> str:
    base = _public_base_url()
    return f"{base}/static/{path.lstrip('/')}"


# --- Simple Email Sender (best-effort) --------------------------------------
def send_reset_email(recipient_email: str, reset_url: str) -> bool:
    """Password reset email (multipart text+html) with BeeSmart logo."""
    server = app.config.get('MAIL_SERVER')
    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    port = app.config.get('MAIL_PORT') or 587
    use_tls = app.config.get('MAIL_USE_TLS', True)
    use_ssl = app.config.get('MAIL_USE_SSL', False)

    subject = "BeeSmart Password Reset"
    # Render HTML/text bodies
    try:
        with app.app_context():
            base = _public_base_url()
            logo_url = _static_url('BeeSmartLogoTransparent.png')
            html_body = render_template('emails/reset.html', reset_url=reset_url, base=base, logo_url=logo_url)
            text_body = render_template('emails/reset.txt', reset_url=reset_url)
    except Exception:
        html_body = None
        text_body = (
            "Hello!\n\n"
            "We received a request to reset your BeeSmart password.\n"
            "If you made this request, click the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            "If you did not request a reset, you can ignore this email.\n\n— BeeSmart Team"
        )

    if not server or not username or not password:
        preview = text_body or (html_body or '').replace('\n', ' ')
        print(f"📧 [DEV] Would send reset email to {recipient_email}:\nSubject: {subject}\n{preview}")
        return True

    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = recipient_email
        msg.attach(MIMEText((text_body or ''), 'plain', 'utf-8'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        if use_ssl:
            smtp = smtplib.SMTP_SSL(server, port)
        else:
            smtp = smtplib.SMTP(server, port)
            if use_tls:
                smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.sendmail(username, [recipient_email], msg.as_string())
        smtp.quit()
        print(f"📧 Reset email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send reset email: {e}")
        return False


def send_welcome_email(recipient_email: str, account_username: str, role: str, teacher_key: Optional[str]) -> bool:
    """Send a post-registration welcome email (multipart text+html).

    Includes Teacher/Parent key and guidance when applicable.
    Returns True if queued/sent; logs and returns True in dev fallback.
    """
    server = app.config.get('MAIL_SERVER')
    smtp_username = app.config.get('MAIL_USERNAME')
    smtp_password = app.config.get('MAIL_PASSWORD')
    port = app.config.get('MAIL_PORT') or 587
    use_tls = app.config.get('MAIL_USE_TLS', True)
    use_ssl = app.config.get('MAIL_USE_SSL', False)

    subject = "Welcome to BeeSmart 🐝"

    # Render templates inside app context
    try:
        with app.app_context():
            base = _public_base_url()
            logo_url = _static_url('BeeSmartLogoTransparent.png')
            html_body = render_template(
                'emails/welcome.html',
                username=account_username,
                role=role,
                teacher_key=teacher_key,
                base=base,
                logo_url=logo_url
            )
            text_body = render_template(
                'emails/welcome.txt',
                username=account_username,
                role=role,
                teacher_key=teacher_key
            )
    except Exception as _rt_e:
        # Fallback to simple text if templates unavailable
        html_body = None
        text_body = (
            f"Hello {account_username},\n\n"
            "Thank you for registering for BeeSmart! We're excited to help you practice and track spelling progress.\n\n"
            + (f"Your {role.capitalize()} Key: {teacher_key}\nKeep this key private and share it only with learners you manage. You can rotate it from your dashboard.\n\n" if role in ['teacher','parent'] and teacher_key else "")
            + "Tips:\n- Teachers/Parents: Use your dashboard to see linked learners and export class or individual reports.\n- Students: Start a quiz or speed round and watch your bee come to life!\n\n— BeeSmart Team"
        )

    # Dev fallback: log to console without SMTP
    if not server or not smtp_username or not smtp_password:
        preview = text_body or (html_body or '').replace('\n', ' ')
        print(f"📧 [DEV] Would send welcome email to {recipient_email}:\nSubject: {subject}\n{preview}")
        return True

    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        # Always include text part
        msg.attach(MIMEText((text_body or ''), 'plain', 'utf-8'))
        # Include html if available
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        if use_ssl:
            smtp = smtplib.SMTP_SSL(server, port)
        else:
            smtp = smtplib.SMTP(server, port)
            if use_tls:
                smtp.starttls()
        if smtp_username and smtp_password:
            smtp.login(smtp_username, smtp_password)
        smtp.sendmail(smtp_username, [recipient_email], msg.as_string())
        smtp.quit()
        print(f"📧 Welcome email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send welcome email: {e}")
        return False


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


def _rate_limit_key(identifier: str, ip: str) -> str:
    return f"reset_req:{normalize(identifier)}:{ip}"


# In-memory minimal rate limiter (per process)
_RL: Dict[str, List[float]] = {}
_RL_WINDOW_SECONDS = 15 * 60  # 15 minutes
_RL_MAX_REQUESTS = 3

# Optional Redis client for shared rate limiting across processes
_REDIS = None
try:
    _REDIS_URL = os.getenv('REDIS_URL') or os.getenv('REDIS_CONNECTION_STRING')
    if _REDIS_URL:
        import redis  # type: ignore
        _REDIS = redis.from_url(_REDIS_URL)
        app.logger.info("Rate limiting: using Redis backend")
except Exception as _re:
    _REDIS = None
    app.logger.info(f"Rate limiting: Redis not available ({_re}); using in-memory fallback")

def _is_rate_limited(identifier: str, ip: str) -> bool:
    key = _rate_limit_key(identifier, ip)
    if _REDIS is not None:
        try:
            pipe = _REDIS.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, _RL_WINDOW_SECONDS)
            count, _ = pipe.execute()
            return int(count) > _RL_MAX_REQUESTS
        except Exception:
            pass  # fall back
    # in-memory fallback (sliding window)
    now = time.time()
    window = _RL.get(key, [])
    window = [t for t in window if now - t <= _RL_WINDOW_SECONDS]
    _RL[key] = window
    return len(window) >= _RL_MAX_REQUESTS

def _add_rate_hit(identifier: str, ip: str):
    key = _rate_limit_key(identifier, ip)
    if _REDIS is not None:
        try:
            pipe = _REDIS.pipeline()
            pipe.incr(key, 1)
            pipe.expire(key, _RL_WINDOW_SECONDS)
            pipe.execute()
            return
        except Exception:
            pass  # fall back to in-memory
    _RL.setdefault(key, []).append(time.time())

# --- Dev-only reset token capture -------------------------------------------
DEV_RESET_TOKEN_CACHE: Dict[int, str] = {}  # user_id -> last raw token


# --- Config ------------------------------------------------------------------
DATA_KEY = "wordbank_v1"
QUIZ_STATE_KEY = "quiz_state_v1"
ALLOWED_EXTENSIONS = {".csv", ".txt", ".docx", ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
MAX_RECORDS = 500  # safety cap; your typical lists are ~50

# Progress tracking for upload processing with bee theme
UPLOAD_PROGRESS = {}
UPLOAD_PROGRESS_LOCK = threading.Lock()

# In-memory word storage keyed by session-bound identifiers to avoid oversized cookies
WORD_STORAGE: Dict[str, List[Dict[str, str]]] = {}
WORD_STORAGE_LOCK = threading.Lock()

# --- Database Helpers --------------------------------------------------------

def get_or_create_guest_user():
    """
    Get or create a guest user for anonymous sessions.
    Allows progress tracking without requiring signup.
    Returns User object (guest or authenticated).
    """
    if current_user.is_authenticated:
        return current_user
    
    # Check if this session has a guest user ID
    guest_user_id = session.get("guest_user_id")
    
    if guest_user_id:
        # Try to retrieve existing guest user
        guest_user = User.query.get(guest_user_id)
        if guest_user:
            return guest_user
    
    # Create new guest user
    try:
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"
        guest_user = User(
            username=guest_username,
            display_name="NewBee",
            email=f"{guest_username}@beesmart.guest",
            role="guest",
            is_active=True,
            email_verified=False
        )
        guest_user.set_password(str(uuid.uuid4()))  # Random password (user can't login)
        
        db.session.add(guest_user)
        db.session.commit()
        
        # Store guest user ID in session
        session["guest_user_id"] = guest_user.id
        session["is_guest"] = True
        
        print(f"✅ Created guest user: {guest_username} (ID: {guest_user.id})")
        return guest_user
        
    except Exception as e:
        print(f"⚠️ Failed to create guest user: {e}")
        db.session.rollback()
        return None

# ============================================================================
# GUEST USER FILTERING UTILITIES
# ============================================================================

def is_guest_user(user):
    """
    Check if a user is a guest user
    Returns True if user is guest, False otherwise
    """
    if not user:
        return False
    
    # Check username pattern (guest users have usernames starting with 'guest_')
    if user.username and user.username.startswith('guest_'):
        return True
    
    # Check if user has no password hash (guests don't have passwords)
    if not hasattr(user, 'password_hash') or not user.password_hash:
        return True
    
    # Check if display name indicates guest
    if user.display_name and user.display_name.startswith('Guest '):
        return True
    
    return False

def filter_non_guest_users(query):
    """
    Add filter to exclude guest users from a User query
    Returns modified query that excludes guests
    """
    from sqlalchemy import and_, not_
    
    return query.filter(
        and_(
            # Exclude usernames starting with 'guest_'
            not_(User.username.like('guest_%')),
            # Ensure user has a password hash (guests don't)
            User.password_hash.isnot(None),
            User.password_hash != '',
            # Exclude display names starting with 'Guest '
            not_(User.display_name.like('Guest %'))
        )
    )

def get_non_guest_users_query():
    """
    Get a base User query that excludes all guest users
    """
    return filter_non_guest_users(User.query)

def get_students_no_guests():
    """
    Get all student users excluding guests
    """
    return filter_non_guest_users(
        User.query.filter_by(role='student')
    ).order_by(User.created_at.desc()).all()

def get_leaderboard_no_guests(limit=10):
    """
    Get leaderboard excluding guest users - includes avatar information
    """
    try:
        # Get users with their avatar data
        users = filter_non_guest_users(
            User.query.filter(
                User.role.in_(['student', 'teacher', 'parent', 'admin'])
            )
        ).order_by(
            User.total_lifetime_points.desc(),
            User.total_quizzes_completed.desc(),
            User.created_at.asc()
        ).limit(limit).all()
        
        # Enrich each user with their avatar object for easier template access
        for user in users:
            try:
                if user.avatar_id:
                    user.avatar_obj = Avatar.query.filter_by(slug=user.avatar_id).first()
                else:
                    user.avatar_obj = None
            except Exception as e:
                print(f"Error loading avatar for user {user.id}: {e}")
                user.avatar_obj = None
        
        return users
    except Exception as e:
        print(f"Error in get_leaderboard_no_guests: {e}")
        return []

# --- Helpers -----------------------------------------------------------------
NORMALIZE_PATTERN = re.compile(r"[^a-z0-9]", re.IGNORECASE)

def normalize(s: str) -> str:
    """Normalize a spelling for comparison: strip non-alnum, lowercase."""
    if s is None:
        return ""
    return re.sub(NORMALIZE_PATTERN, "", s).lower()

# Kid-Friendly Word Filter - Blocks inappropriate content for children
INAPPROPRIATE_WORDS = {
    # Profanity and vulgar terms
    "damn", "damned", "hell", "hells", "crap", "sucks", "piss", "pissed",
    # Sexual/adult content
    "sex", "sexy", "porn", "orgasm", "penis", "vagina", "breast", "breasts",
    "ejaculation", "ejaculations", "erection", "masturbate", "prostitute",
    # Violence/weapons
    "kill", "killing", "killer", "murder", "murderer", "suicide", "weapon", 
    "gun", "shoot", "shooting", "bomb", "explosive",
    # Drugs/alcohol
    "drug", "drugs", "cocaine", "marijuana", "heroin", "meth", "drunk", "alcohol",
    # Hate speech
    "racist", "sexist", "nazi", "hate",
    # Other inappropriate
    "death", "die", "dying", "blood", "bloody", "torture"
}

def is_kid_friendly(word: str) -> tuple[bool, str]:
    """
    Check if a word is appropriate for children (ages 6-14).
    Filters out inappropriate words, acronyms, and spam.
    Returns: (is_safe, reason)
    """
    if not word:
        return False, "Empty word"
    
    word_lower = word.lower().strip()
    
    # Check against inappropriate words list
    if word_lower in INAPPROPRIATE_WORDS:
        return False, f"Word '{word}' is not appropriate for children"
    
    # Check for partial matches (e.g., "ejaculation" contains "ejaculate")
    for inappropriate in INAPPROPRIATE_WORDS:
        if inappropriate in word_lower and len(inappropriate) > 4:
            return False, f"Word '{word}' contains inappropriate content"
    
    # Additional pattern checks
    # Block words with numbers mixed in (likely spam/codes)
    if re.search(r'\d', word):
        return False, f"Word '{word}' contains numbers"
    
    # Must be at least 2 letters
    if len(word_lower) < 2:
        return False, f"Word '{word}' is too short"
    
    # Must be only letters
    if not word_lower.isalpha():
        return False, f"Word '{word}' contains non-letter characters"
    
    # Block excessively long "words" (likely spam)
    if len(word) > 25:
        return False, f"Word '{word}' is too long (max 25 letters)"
    
    # ACRONYM FILTER: Block words that are likely acronyms
    # An acronym typically:
    # 1. Is short (2-6 letters)
    # 2. All uppercase or mixed case (not all lowercase)
    # 3. Has few/no vowels
    # 4. Is not a common word
    
    original_word = word.strip()  # Keep original casing
    
    # Check if word is ALL CAPS (strong acronym indicator)
    if original_word.isupper() and len(original_word) >= 2:
        # Allow common all-caps words that are real words
        allowed_caps_words = {'TV', 'OK', 'US', 'AM', 'PM', 'AD', 'BC'}
        if original_word not in allowed_caps_words:
            return False, f"Word '{word}' appears to be an acronym (all capitals)"
    
    # Check for vowel ratio (acronyms usually have few vowels)
    # Only apply this check to very short words (2-4 letters) where it's more reliable
    if len(word_lower) >= 2 and len(word_lower) <= 4:
        vowels = sum(1 for c in word_lower if c in 'aeiou')
        
        # If word has NO vowels and is 2-4 letters, likely an acronym
        if vowels == 0:
            # Common short words with no vowels that should be allowed
            allowed_no_vowel = {
                'by', 'my', 'try', 'cry', 'dry', 'fly', 'fry', 'pry', 'shy', 'sky', 'sly', 'spy', 'why',
                'gym', 'hymn', 'lynx', 'myth', 'sync', 'nth', 'tv', 'pm'
            }
            if word_lower not in allowed_no_vowel:
                return False, f"Word '{word}' appears to be an acronym (no vowels)"
    
    # Check for mixed case in middle of word (e.g., "iPhone", "YouTube")
    # These are often brand names or acronyms
    if len(original_word) > 2:
        # Check if there's an uppercase letter after the first character
        if any(c.isupper() for c in original_word[1:]):
            return False, f"Word '{word}' has unusual capitalization (possibly acronym or brand name)"
    
    return True, "OK"

# Progress tracking functions for bee-themed upload processing
def create_upload_session(session_id: str, total_words: int):
    """Create a new upload progress session"""
    with UPLOAD_PROGRESS_LOCK:
        UPLOAD_PROGRESS[session_id] = {
            "status": "initializing",
            "message": "Getting ready to collect spelling words...",
            "bee_action": "bees_gathering",
            "progress": 0,
            "total_words": total_words,
            "processed_words": 0,
            "current_word": "",
            "errors": [],
            "start_time": time.time(),
            "bee_messages": [
                "🐝 Bees are getting ready to collect words...",
                "🐝 Preparing the hive for new spelling words...",
                "🐝 Worker bees are warming up their wings..."
            ]
        }

def update_upload_progress(session_id: str, status: str, message: str, bee_action: str, 
                          progress: Optional[int] = None, current_word: str = "", error: Optional[str] = None):
    """Update upload progress with bee-themed messages"""
    with UPLOAD_PROGRESS_LOCK:
        if session_id in UPLOAD_PROGRESS:
            UPLOAD_PROGRESS[session_id]["status"] = status
            UPLOAD_PROGRESS[session_id]["message"] = message
            UPLOAD_PROGRESS[session_id]["bee_action"] = bee_action
            UPLOAD_PROGRESS[session_id]["current_word"] = current_word
            
            if progress is not None:
                UPLOAD_PROGRESS[session_id]["progress"] = progress
                UPLOAD_PROGRESS[session_id]["processed_words"] = (
                    progress * UPLOAD_PROGRESS[session_id]["total_words"] // 100
                )
            
            if error:
                UPLOAD_PROGRESS[session_id]["errors"].append(error)
            
            # Add bee-themed messages based on progress
            if progress is not None:
                if progress < 25:
                    bee_msg = f"🐝 Bees are flying to collect '{current_word}'..."
                elif progress < 50:
                    bee_msg = f"🐝 Worker bees are gathering definitions for '{current_word}'..."
                elif progress < 75:
                    bee_msg = f"🐝 Bees are creating quiz sentences for '{current_word}'..."
                else:
                    bee_msg = f"🐝 Almost done! Bees are organizing '{current_word}' in the hive..."
                
                UPLOAD_PROGRESS[session_id]["bee_messages"].append(bee_msg)
                # Keep only last 5 messages
                if len(UPLOAD_PROGRESS[session_id]["bee_messages"]) > 5:
                    UPLOAD_PROGRESS[session_id]["bee_messages"] = UPLOAD_PROGRESS[session_id]["bee_messages"][-5:]

def get_upload_progress(session_id: str):
    """Get current upload progress"""
    with UPLOAD_PROGRESS_LOCK:
        return UPLOAD_PROGRESS.get(session_id, None)

def complete_upload_session(session_id: str, success: bool, final_message: str):
    """Complete upload session with final status"""
    with UPLOAD_PROGRESS_LOCK:
        if session_id in UPLOAD_PROGRESS:
            UPLOAD_PROGRESS[session_id]["status"] = "completed" if success else "error"
            UPLOAD_PROGRESS[session_id]["message"] = final_message
            UPLOAD_PROGRESS[session_id]["bee_action"] = "bees_celebrating" if success else "bees_confused"
            UPLOAD_PROGRESS[session_id]["progress"] = 100 if success else UPLOAD_PROGRESS[session_id]["progress"]
            UPLOAD_PROGRESS[session_id]["end_time"] = time.time()
            
            if success:
                UPLOAD_PROGRESS[session_id]["bee_messages"].append("🐝 Success! All bees have returned to the hive with spelling words!")
            else:
                UPLOAD_PROGRESS[session_id]["bee_messages"].append("🐝 Oh no! Some bees got confused... Let's try again!")

def _records_from_lines(lines: List[str]) -> List[Dict[str, str]]:
    """
    Given plain lines where each line is:
        word
        word|sentence
        word|sentence|hint
    Produce a list of dicts with keys: word, sentence, hint.
    Blank lines are skipped.
    """
    out = []
    for raw in lines:
        line = (raw or "").strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        word = parts[0] if parts else ""
        if not word:
            continue
        sentence = parts[1] if len(parts) > 1 else ""
        hint = parts[2] if len(parts) > 2 else ""
        out.append({"word": word, "sentence": sentence, "hint": hint})
    return out

def parse_txt(file_bytes: bytes) -> List[Dict[str, str]]:
    text = file_bytes.decode("utf-8", errors="replace")
    return _records_from_lines(text.splitlines())

def parse_csv(file_bytes: bytes, filename: str) -> List[Dict[str, str]]:
    """
    CSV with optional headers (word, sentence, hint). If no header or 'word'
    missing, treat first column as 'word'; col2 = sentence; col3 = hint.
    """
    text = file_bytes.decode("utf-8-sig", errors="replace")
    sio = io.StringIO(text)
    reader = csv.reader(sio)
    peek = next(reader, None)
    if peek is None:
        return []

    # Detect header if it contains 'word'
    def _is_header(row):
        return any(cell.strip().lower() == "word" for cell in row)

    records: List[Dict[str, str]] = []
    if _is_header(peek):
        # Use DictReader starting from the top again
        sio.seek(0)
        dreader = csv.DictReader(io.StringIO(text))
        for rec in dreader:
            word = (rec.get("word") or rec.get("Word") or rec.get("WORD") or "").strip()
            if not word:
                continue
            sentence = (rec.get("sentence") or rec.get("Sentence") or "").strip()
            hint = (rec.get("hint") or rec.get("Hint") or "").strip()
            records.append({"word": word, "sentence": sentence, "hint": hint})
    else:
        # No headerΓÇötreat columns positionally
        row0 = peek
        if row0:
            records.append({
                "word": row0[0].strip() if len(row0) > 0 else "",
                "sentence": row0[1].strip() if len(row0) > 1 else "",
                "hint": row0[2].strip() if len(row0) > 2 else "",
            })
        for row in reader:
            if not row:
                continue
            records.append({
                "word": row[0].strip() if len(row) > 0 else "",
                "sentence": row[1].strip() if len(row) > 1 else "",
                "hint": row[2].strip() if len(row) > 2 else "",
            })
    return records

def parse_docx(file_bytes: bytes) -> List[Dict[str, str]]:
    if docx is None:
        raise RuntimeError("DOCX support not installed. Please install python-docx.")
    # Load from in-memory bytes
    bio = io.BytesIO(file_bytes)
    document = docx.Document(bio)
    lines: List[str] = []
    for p in document.paragraphs:
        t = (p.text or "").strip()
        if t:
            lines.append(t)
    # Also consider single-column tables (optional)
    for tbl in getattr(document, "tables", []):
        for row in tbl.rows:
            cells = [c.text.strip() for c in row.cells if c and c.text]
            if cells:
                lines.append("|".join(cells))  # allow word|sentence|hint in table
    return _records_from_lines(lines)

def parse_pdf(file_bytes: bytes) -> List[Dict[str, str]]:
    if extract_text is None:
        raise RuntimeError("PDF support not installed. Please install pdfminer.six.")
    bio = io.BytesIO(file_bytes)
    text = extract_text(bio) or ""
    # Split on lines; PDFs often have hyphenation and odd spacing,
    # but for typical lists (one word per line or word|sentence|hint), this works well.
    # You can pre-clean some hyphenated artifacts:
    text = text.replace("\u00ad", "")  # soft hyphen
    raw_lines = [ln.strip() for ln in text.splitlines()]
    # Remove obvious page header/footer noise if needed (optional heuristic)
    lines = [ln for ln in raw_lines if ln]
    return _records_from_lines(lines)

def parse_image_ocr(file_bytes: bytes) -> List[Dict[str, str]]:
    """Extract text from image using OCR and parse as word list"""
    if not TESSERACT_AVAILABLE:
        raise RuntimeError("Image processing requires Tesseract OCR. Please install pytesseract and tesseract-ocr.")
    
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(file_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        
        # Process OCR text into word list
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Clean up OCR artifacts
        cleaned_lines = []
        for line in lines:
            # Remove common OCR artifacts
            cleaned = re.sub(r'[^\w\s|,-]', '', line)  # Keep word chars, spaces, pipes, commas, hyphens
            if cleaned.strip() and len(cleaned.strip()) > 1:  # Avoid single character OCR errors
                cleaned_lines.append(cleaned.strip())
        
        return _records_from_lines(cleaned_lines)
        
    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {str(e)}")

def load_default_wordbank() -> List[Dict[str, str]]:
    """Load default word list from 50Words_kidfriendly.txt"""
    try:
        import os
        file_path = os.path.join(os.path.dirname(__file__), "50Words_kidfriendly.txt")
        
        if not os.path.exists(file_path):
            print(f"DEBUG: Default word file not found at {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        words = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                word = parts[0].strip()
                definition_and_example = parts[1].strip()
                
                # Split definition and example if "Example:" is present
                if "Example:" in definition_and_example:
                    def_parts = definition_and_example.split("Example:", 1)
                    definition = def_parts[0].strip().rstrip('.')  # Remove trailing period
                    sentence = def_parts[1].strip()
                    
                    # Ensure sentence has blank
                    if "_____" not in sentence:
                        sentence = f"Definition: {definition}. Fill in the blank: The word is _____."
                else:
                    # No example provided
                    definition = definition_and_example
                    sentence = f"Definition: {definition}. Fill in the blank: The word is _____."
                
                words.append({
                    "word": word,
                    "sentence": sentence,  # Use sentence as primary field
                    "hint": ""  # No hint field in defaults
                })
                
            elif len(parts) == 1:
                # Plain word format fallback
                word = parts[0].strip()
                words.append({
                    "word": word,
                    "sentence": f"Practice spelling this word: _____",
                    "hint": ""
                })
            
            if len(words) >= 50:  # Limit to 50 words
                break
        
        print(f"DEBUG load_default_wordbank: Successfully loaded {len(words)} default words from {file_path}")
        return words
        
    except Exception as e:
        print(f"ERROR load_default_wordbank: Error loading default words: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_wordbank() -> List[Dict[str, str]]:
    """Read the active wordbank directly from the server-side session.

    We persist the full list in the session store (filesystem/Redis), so
    it is shared across workers and survives process restarts.
    """
    wb = session.get(DATA_KEY)

    # Migrate legacy payload (dict with storage_id) to direct list if possible
    if isinstance(wb, dict):
        storage_id = wb.get("storage_id")
        migrated = []
        if storage_id:
            with WORD_STORAGE_LOCK:
                migrated = WORD_STORAGE.get(storage_id, [])
        if migrated:
            session[DATA_KEY] = migrated
            session.pop("wordbank_storage_id", None)
            wb = migrated
            print(f"DEBUG get_wordbank: Migrated {len(migrated)} words from legacy storage_id to server-side session")
        else:
            wb = []

    # New shape: list of word dicts
    if not isinstance(wb, list):
        wb = []

    # Smart default load for brand-new sessions with nothing uploaded yet
    if not wb and not session.get("skip_default_load", False) and not session.get("has_uploaded_once", False):
        print("DEBUG get_wordbank: New/empty session detected, loading default demo words")
        default_words = load_default_wordbank()
        if default_words:
            set_wordbank(default_words, is_user_upload=False)
            wb = default_words
            session["using_default_words"] = True
            print(f"DEBUG get_wordbank: Loaded {len(wb)} default demo words for new session")

    session["wordbank_count"] = len(wb)
    print(f"DEBUG get_wordbank: Retrieved {len(wb)} words from server-side session, session keys: {list(session.keys())}")
    return wb

def set_wordbank(rows: List[Dict[str, str]], is_user_upload: bool = False):
    """Persist the full wordbank in the server-side session store."""
    print(f"DEBUG set_wordbank: Storing {len(rows)} words directly in server-side session (is_user_upload={is_user_upload})")
    
    session[DATA_KEY] = rows
    session["wordbank_count"] = len(rows)
    # Clear any legacy indirection
    session.pop("wordbank_storage_id", None)
    session.modified = True

    if is_user_upload:
        session["has_uploaded_once"] = True
        session.pop("using_default_words", None)
        print("DEBUG set_wordbank: Marked as user upload - has_uploaded_once=True")

    # Always clear skip flag when new words are loaded
    session.pop("skip_default_load", None)
    
    print(f"DEBUG set_wordbank: Server-side session updated, keys={list(session.keys())}")

def init_quiz_state():
    wordbank = get_wordbank()
    order = list(range(len(wordbank)))
    random.shuffle(order)  # Randomize word order for each quiz session!
    
    # Create database session for ALL users (authenticated + guests)
    db_session_id = None
    user_obj = get_or_create_guest_user()  # Returns current_user or creates guest
    
    if user_obj:
        try:
            # Create new QuizSession in database
            quiz_session = QuizSession(
                user_id=user_obj.id,
                total_words=len(wordbank)
            )
            # If this user is linked to a teacher/parent, stamp teacher_key for reporting
            try:
                link = TeacherStudent.query.filter_by(student_id=user_obj.id, is_active=True).first()
                if link and not quiz_session.teacher_key:
                    quiz_session.teacher_key = link.teacher_key
            except Exception as _e:
                # Non-fatal; proceed without teacher_key if lookup fails
                print(f"⚠️ Could not associate teacher_key to QuizSession: {_e}")
            db.session.add(quiz_session)
            db.session.commit()
            db_session_id = quiz_session.id
            
            user_type = "guest" if session.get("is_guest") else "authenticated"
            print(f"✅ Created database QuizSession ID: {db_session_id} for {user_type} user {user_obj.username}")
        except Exception as e:
            print(f"⚠️ Failed to create database session: {e}")
            db.session.rollback()
    
    session[QUIZ_STATE_KEY] = {
        "idx": 0,
        "order": order,
        "started_at": datetime.utcnow().isoformat(),
        "correct": 0,
        "incorrect": 0,
        "streak": 0,
        "max_streak": 0,  # 🍯 Track best streak for badges
        "session_points": 0,  # 🍯 Total honey points earned this session
        "hints_used_current_word": 0,  # 🍯 Track hints for no-hints bonus
        "history": [],  # list of {word, user_input, correct, method, elapsed_ms, ts}
        "db_session_id": db_session_id  # Link to database session
    }
    session.modified = True  # Critical for mobile session persistence

def get_quiz_state():
    return session.get(QUIZ_STATE_KEY)

# Register Battle of the Bees API Blueprint (temporarily disabled)
print("🔧 Battle API temporarily disabled until Flask-SocketIO is installed")
# TODO: Uncomment once Flask-SocketIO is properly installed
# from battles_api import battles_bp
# app.register_blueprint(battles_bp, url_prefix='/api')
print("⚠️ Battle API not registered - will be enabled after Socket.IO setup")

# --- Routes: Saved Word Lists (Persistent) -----------------------------------
@app.route("/api/saved-lists", methods=["GET"])
def list_saved_wordlists():
    """Return the current user's saved word lists (persisted; not cleared by /api/clear)."""
    try:
        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        lists = (
            WordList.query
            .filter(WordList.created_by_user_id == user.id)
            .order_by(WordList.updated_at.desc())
            .all()
        )

        data = []
        for wl in lists:
            data.append({
                "id": wl.id,
                "uuid": wl.uuid,
                "name": wl.list_name,
                "description": wl.description or "",
                "word_count": wl.word_count or 0,
                "created_at": wl.created_at.isoformat() if wl.created_at else None,
                "updated_at": wl.updated_at.isoformat() if wl.updated_at else None,
            })

        return jsonify({"ok": True, "lists": data})
    except Exception as e:
        print(f"ERROR /api/saved-lists GET: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to retrieve saved lists"}), 500


@app.route("/api/saved-lists/save", methods=["POST"])
def save_current_wordlist():
    """Persist the current in-session wordbank to the database with a user-provided name."""
    try:
        payload = request.get_json(silent=True) or {}
        list_name = (payload.get("list_name") or "").strip()
        description = (payload.get("description") or "").strip()

        if not list_name:
            return jsonify({"ok": False, "error": "List name is required"}), 400

        words = get_wordbank()
        if not words:
            return jsonify({"ok": False, "error": "No words available to save"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Create WordList record
        wl = WordList(
            created_by_user_id=user.id,
            list_name=list_name,
            description=description,
            word_count=len(words),
            is_public=False
        )
        db.session.add(wl)
        db.session.flush()  # get wl.id

        # Insert items
        position = 1
        for rec in words:
            item = WordListItem(
                word_list_id=wl.id,
                word=(rec.get("word") or "").strip(),
                sentence=(rec.get("sentence") or "").strip(),
                hint=(rec.get("hint") or "").strip(),
                position=position
            )
            db.session.add(item)
            position += 1

        db.session.commit()

        return jsonify({
            "ok": True,
            "saved": {
                "id": wl.id,
                "uuid": wl.uuid,
                "name": wl.list_name,
                "word_count": wl.word_count
            }
        })
    except Exception as e:
        print(f"ERROR /api/saved-lists/save: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to save list"}), 500


@app.route("/api/saved-lists/load", methods=["POST"])
def load_saved_wordlist():
    """Load a saved list into the current session and initialize quiz state."""
    try:
        payload = request.get_json(silent=True) or {}
        list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")
        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Lookup by uuid if non-numeric, else by id
        wl = None
        try:
            # numeric id path
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except Exception:
            # uuid path
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404

        items = WordListItem.query.filter_by(word_list_id=wl.id).order_by(WordListItem.position.asc()).all()
        rows = []
        for it in items:
            if it.word:
                rows.append({"word": it.word, "sentence": it.sentence or "", "hint": it.hint or ""})

        if not rows:
            return jsonify({"ok": False, "error": "This list has no items"}), 400

        # Load into session for quiz use
        set_wordbank(rows, is_user_upload=False)
        init_quiz_state()

        return jsonify({
            "ok": True,
            "loaded": {
                "id": wl.id,
                "uuid": wl.uuid,
                "name": wl.list_name,
                "word_count": len(rows)
            }
        })
    except Exception as e:
        print(f"ERROR /api/saved-lists/load: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to load list"}), 500


@app.route("/api/saved-lists/delete", methods=["POST"])  # small, optional helper
def delete_saved_wordlist():
    try:
        payload = request.get_json(silent=True) or {}
        list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")
        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        wl = None
        try:
            wl = WordList.query.filter_by(id=int(str(list_id)), created_by_user_id=user.id).first()
        except Exception:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404

        db.session.delete(wl)
        db.session.commit()
        return jsonify({"ok": True})
    except Exception as e:
        print(f"ERROR /api/saved-lists/delete: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to delete list"}), 500

@app.route("/api/upload-to-saved-list", methods=["POST"])
def upload_to_saved_list():
    """Upload a file to update an existing saved word list."""
    try:
        # Get the saved list ID from form data
        saved_list_id = request.form.get('savedListId')
        if not saved_list_id:
            return jsonify({"ok": False, "error": "Missing saved list ID"}), 400

        # Get current user
        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Find the saved list
        try:
            wl = WordList.query.filter_by(id=int(saved_list_id), created_by_user_id=user.id).first()
        except (ValueError, TypeError):
            wl = WordList.query.filter_by(uuid=str(saved_list_id), created_by_user_id=user.id).first()

        if not wl:
            return jsonify({"ok": False, "error": "Saved list not found"}), 404

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"ok": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"ok": False, "error": "No file selected"}), 400

        # Process the uploaded file (reuse existing upload logic)
        words = []
        filename = file.filename.lower()

        if filename.endswith('.csv'):
            words = parse_csv(file)
        elif filename.endswith('.txt'):
            words = parse_txt(file)
        elif filename.endswith('.docx'):
            words = parse_docx(file)
        elif filename.endswith('.pdf'):
            words = parse_pdf(file)
        elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            if not TESSERACT_AVAILABLE:
                return jsonify({"ok": False, "error": "Image processing requires Tesseract OCR installation"}), 400
            words = parse_image_ocr(file)
        else:
            return jsonify({"ok": False, "error": "Unsupported file format"}), 400

        if not words:
            return jsonify({"ok": False, "error": "No words found in the uploaded file"}), 400

        # Deduplicate and enrich words
        words = deduplicate_words(words)
        words = enrich_with_definitions(words)

        # Delete existing items for this list
        WordListItem.query.filter_by(word_list_id=wl.id).delete()

        # Add new items
        position = 1
        for word_data in words:
            item = WordListItem(
                word_list_id=wl.id,
                word=(word_data.get("word") or "").strip(),
                sentence=(word_data.get("sentence") or "").strip(),
                hint=(word_data.get("hint") or "").strip(),
                position=position
            )
            db.session.add(item)
            position += 1

        # Update the word count and timestamp
        wl.word_count = len(words)
        wl.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "ok": True,
            "updated": {
                "id": wl.id,
                "uuid": wl.uuid,
                "name": wl.list_name,
                "word_count": wl.word_count
            },
            "word_count": len(words)
        })

    except Exception as e:
        print(f"ERROR /api/upload-to-saved-list: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to update list"}), 500

# --- Routes: UI --------------------------------------------------------------
@app.route("/")
def home():
    import time
    timestamp = str(int(time.time()))
    return render_template("unified_menu.html", timestamp=timestamp)

@app.route("/test")
def test_page():
    """Test page to verify Flask is working"""
    return render_template("test_page.html")

@app.route("/avatar-diagnostic")
def avatar_diagnostic():
    """Diagnostic page for troubleshooting avatar rendering issues"""
    import time
    timestamp = str(int(time.time()))
    return render_template("avatar_diagnostic.html", timestamp=timestamp)

@app.route("/minimal")
def minimal_main():
    """Minimal version of main page for testing"""
    import time
    timestamp = str(int(time.time()))
    return render_template("unified_menu.html", timestamp=timestamp)

@app.route("/quiz")
def quiz_page():
    """Interactive quiz page"""
    # Enhanced debugging for mobile session issues
    session_id = session.get("session_id", "NONE")
    storage_id = session.get("wordbank_storage_id", "NONE")
    
    print(f"DEBUG /quiz: session_id={session_id}, storage_id={storage_id}")
    print(f"DEBUG /quiz: session keys={list(session.keys())}")
    print(f"DEBUG /quiz: cookies={request.cookies.keys()}")
    
    # Check WORD_STORAGE
    with WORD_STORAGE_LOCK:
        storage_keys = list(WORD_STORAGE.keys())
        print(f"DEBUG /quiz: WORD_STORAGE has {len(storage_keys)} entries: {storage_keys}")
        if storage_id and storage_id != "NONE":
            words_in_storage = len(WORD_STORAGE.get(storage_id, []))
            print(f"DEBUG /quiz: storage_id {storage_id} has {words_in_storage} words")
    
    # Ensure wordbank is loaded before showing quiz
    wordbank = get_wordbank()
    if not wordbank or len(wordbank) == 0:
        print("WARNING /quiz: No wordbank found, redirecting to menu")
        # Redirect back to menu with error message
        return redirect("/?error=no_words")
    
    # Initialize quiz state for this wordbank (only if not already initialized)
    state = get_quiz_state()
    if state is None or len(state.get("order", [])) != len(wordbank):
        print(f"DEBUG /quiz: Initializing quiz state for {len(wordbank)} words")
        init_quiz_state()
    else:
        print(f"DEBUG /quiz: Using existing quiz state - idx={state.get('idx')}, total={len(state.get('order', []))}")
        
    print(f"DEBUG /quiz: Rendering quiz.html with {len(wordbank)} words")
    
    # Pass user information if logged in
    user_name = None
    if current_user.is_authenticated:
        user_name = current_user.display_name
        print(f"DEBUG /quiz: User logged in as {user_name}")
    
    return render_template("quiz.html", user_name=user_name)

@app.route("/battle/<battle_code>")
def battle_page(battle_code):
    """
    Individual battle page for Battle of the Bees.
    Live multiplayer spelling battle with real-time updates.
    """
    battle_code = battle_code.upper()
    timestamp = int(time.time())
    
    # Check if battle exists via API
    try:
        from models import BattleSession
        battle = BattleSession.query.filter_by(code=battle_code).first()
        if not battle:
            return render_template("error.html", 
                                 error_title="Battle Not Found",
                                 error_message=f"Battle code {battle_code} does not exist."), 404
    except Exception as e:
        print(f"Error checking battle: {e}")
        return render_template("error.html", 
                             error_title="Error Loading Battle",
                             error_message="Failed to load battle data."), 500
    
    # Battle exists, render the battle page
    return render_template("battle.html", 
                         battle_code=battle_code, 
                         timestamp=timestamp)

@app.route("/help")
def help_page():
    """Helpful tips and onboarding guidance"""
    return render_template("help.html")

@app.route("/guide")
def user_guide():
    """Comprehensive user guide"""
    try:
        import markdown
        with open('BEESMART_USER_GUIDE.md', 'r', encoding='utf-8') as f:
            guide_content = f.read()
        html_content = markdown.markdown(guide_content, extensions=['toc', 'tables'])
        return render_template("guide.html", content=html_content, title="BeeSmart User Guide")
    except FileNotFoundError:
        return render_template("guide.html", 
                             content="<p>User guide not found. Please contact support.</p>", 
                             title="Guide Not Available")
    except ImportError:
        # Fallback if markdown isn't installed
        with open('BEESMART_USER_GUIDE.md', 'r', encoding='utf-8') as f:
            guide_content = f.read()
        # Simple conversion for display
        html_content = guide_content.replace('\n', '<br>').replace('#', '<h3>').replace('**', '<b>').replace('**', '</b>')
        return render_template("guide.html", content=html_content, title="BeeSmart User Guide")

@app.route("/admin-guide")
def admin_guide():
    """Technical administrator guide"""
    try:
        import markdown
        with open('BEESMART_ADMIN_GUIDE.md', 'r', encoding='utf-8') as f:
            guide_content = f.read()
        html_content = markdown.markdown(guide_content, extensions=['toc', 'tables'])
        return render_template("guide.html", content=html_content, title="BeeSmart Administrator Guide")
    except FileNotFoundError:
        return render_template("guide.html", 
                             content="<p>Administrator guide not found. Please contact support.</p>", 
                             title="Admin Guide Not Available")
    except ImportError:
        # Fallback if markdown isn't installed
        with open('BEESMART_ADMIN_GUIDE.md', 'r', encoding='utf-8') as f:
            guide_content = f.read()
        # Simple conversion for display
        html_content = guide_content.replace('\n', '<br>').replace('#', '<h3>').replace('**', '<b>').replace('**', '</b>')
        return render_template("guide.html", content=html_content, title="BeeSmart Administrator Guide")

@app.route("/battles")
def battles_list():
    """Battle of the Bees - Live battles listing page"""
    timestamp = int(time.time())
    return render_template("battles.html", timestamp=timestamp)

@app.route("/upload")
def upload_page():
    """Upload word lists page"""
    return render_template("upload.html")

@app.route("/magical_quiz")
def magical_quiz_page():
    """Legacy magical quiz experience (kept for backwards compatibility)"""
    return render_template("magical_quiz.html")

@app.route("/health")
def health_check():
    """Ultra-simple health check for Railway - always returns 200"""
    return jsonify({"status": "ok", "version": "1.6"}), 200

@app.route("/db/migrate-avatar-columns")
def migrate_avatar_columns():
    """Migration endpoint to add avatar columns to existing users table"""
    try:
        from sqlalchemy import text
        
        # Check if columns already exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        migrations_needed = []
        migrations_run = []
        
        # Define the columns to add
        avatar_columns = {
            'avatar_id': "VARCHAR(50) DEFAULT 'mascot-bee'",
            'avatar_variant': "VARCHAR(10) DEFAULT 'default'",
            'avatar_locked': "BOOLEAN DEFAULT FALSE",
            'avatar_last_updated': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        # Add any missing columns
        with db.engine.connect() as conn:
            for col_name, col_def in avatar_columns.items():
                if col_name not in columns:
                    migrations_needed.append(col_name)
                    try:
                        # PostgreSQL syntax
                        sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"
                        conn.execute(text(sql))
                        conn.commit()
                        migrations_run.append(col_name)
                        print(f"✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"❌ Failed to add column {col_name}: {e}")
                        return jsonify({
                            "status": "error",
                            "message": f"Failed to add column {col_name}",
                            "error": str(e)
                        }), 500
        
        if migrations_run:
            return jsonify({
                "status": "success",
                "message": f"Added {len(migrations_run)} columns to users table",
                "columns_added": migrations_run
            }), 200
        else:
            return jsonify({
                "status": "success",
                "message": "All avatar columns already exist",
                "columns_checked": list(avatar_columns.keys())
            }), 200
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Migration failed",
            "error": str(e)
        }), 500

@app.route("/api/test-dictionary")
def test_dictionary():
    """Test dictionary API with a simple word"""
    try:
        # Reset circuit breaker first
        from dictionary_api import dictionary_api
        dictionary_api.reset_circuit_breaker()
        
        # Test with a simple word
        test_word = "test"
        print(f"🧪 Testing dictionary API with word: '{test_word}'")
        
        result = dictionary_api.lookup_word(test_word)
        
        if result:
            return jsonify({
                "status": "success",
                "message": "Dictionary API is working",
                "test_word": test_word,
                "result": result,
                "circuit_breaker_failures": dictionary_api.circuit_breaker_failures
            })
        else:
            return jsonify({
                "status": "failed", 
                "message": "Dictionary API returned no result",
                "test_word": test_word,
                "circuit_breaker_failures": dictionary_api.circuit_breaker_failures
            }), 500
            
    except Exception as e:
        try:
            from dictionary_api import dictionary_api
            failures = dictionary_api.circuit_breaker_failures
        except:
            failures = 'unknown'
            
        return jsonify({
            "status": "error",
            "message": f"Dictionary API test failed: {str(e)}",
            "circuit_breaker_failures": failures
        }), 500

# --- Random Play Helper Functions -------------------------------------------
def calculate_word_difficulty(word: str) -> int:
    """
    Calculate difficulty level (1-5) for a word based on multiple factors.
    1 = Easy (3-4 letters, common patterns)
    2 = Medium-Easy (5-6 letters, simple patterns)
    3 = Medium (7-8 letters, some complexity)
    4 = Medium-Hard (9-10 letters, complex patterns)
    5 = Hard (11+ letters, very complex)
    """
    word_lower = word.lower()
    length = len(word_lower)
    
    # Base difficulty from length
    if length <= 4:
        base_difficulty = 1
    elif length <= 6:
        base_difficulty = 2
    elif length <= 8:
        base_difficulty = 3
    elif length <= 10:
        base_difficulty = 4
    else:
        base_difficulty = 5
    
    # Adjust for complexity factors
    complexity_score = 0
    
    # Check for difficult letter combinations
    difficult_patterns = ['ough', 'eigh', 'tion', 'sion', 'ious', 'eous', 'queue', 'pneum', 'psych', 'rrhea']
    for pattern in difficult_patterns:
        if pattern in word_lower:
            complexity_score += 1
    
    # Check for silent letters (common patterns)
    silent_patterns = ['kn', 'gn', 'wr', 'mb', 'gh', 'ph']
    for pattern in silent_patterns:
        if pattern in word_lower:
            complexity_score += 0.5
    
    # Check for double letters (slightly harder)
    import re
    if re.search(r'(.)\1', word_lower):
        complexity_score += 0.5
    
    # Check for uncommon letters
    uncommon_letters = set('qxzj')
    if any(letter in word_lower for letter in uncommon_letters):
        complexity_score += 0.5
    
    # Adjust base difficulty
    if complexity_score >= 2:
        base_difficulty = min(5, base_difficulty + 1)
    elif complexity_score >= 1:
        base_difficulty = min(5, base_difficulty + 0.5)
    
    # Round to nearest integer
    return int(round(base_difficulty))

def get_random_words_by_difficulty(difficulty: int, count: int = 10) -> List[Dict[str, str]]:
    """
    Get random words from Simple Wiktionary filtered by difficulty level.
    
    Args:
        difficulty: Level 1-5 (1=easy, 5=hard)
        count: Number of words to return (default 10)
    
    Returns:
        List of word dictionaries with word, sentence, and hint fields
    """
    if not SIMPLE_WIKTIONARY:
        raise ValueError("Simple Wiktionary not loaded - cannot generate random words")
    
    # Filter words by difficulty
    words_at_difficulty = []
    
    print(f"🎲 Searching for {count} words at difficulty level {difficulty}...")
    
    for word, data in SIMPLE_WIKTIONARY.items():
        # Skip very short words (likely abbreviations) or words with special characters
        if len(word) < 3 or not word.isalpha():
            continue
        
        word_difficulty = calculate_word_difficulty(word)
        
        # Accept words at exact difficulty or ±1 level (for variety)
        if abs(word_difficulty - difficulty) <= 1:
            words_at_difficulty.append({
                "word": word,
                "data": data,
                "exact_match": word_difficulty == difficulty
            })
    
    # Prioritize exact matches, then close matches
    exact_matches = [w for w in words_at_difficulty if w["exact_match"]]
    close_matches = [w for w in words_at_difficulty if not w["exact_match"]]
    
    print(f"📊 Found {len(exact_matches)} exact matches and {len(close_matches)} close matches")
    
    # Randomly select words (prefer exact matches)
    selected = []
    
    # First, try to get from exact matches
    if exact_matches:
        random.shuffle(exact_matches)
        selected = exact_matches[:count]
    
    # If not enough exact matches, add from close matches
    if len(selected) < count and close_matches:
        random.shuffle(close_matches)
        remaining_needed = count - len(selected)
        selected.extend(close_matches[:remaining_needed])
    
    # Format as word records
    result = []
    for item in selected[:count]:
        word = item["word"]
        data = item["data"]
        
        definition = data.get("definition", "")
        example = data.get("example", "")
        
        # Create sentence from definition and example
        if example and len(example) > 10:
            sentence = f"{definition}. {_blank_word(example, word)}"
        else:
            sentence = f"{definition}. Fill in the blank: Can you spell _____ correctly?"
        
        result.append({
            "word": word,
            "sentence": sentence,
            "hint": f"This is a level {difficulty} word with {len(word)} letters."
        })
    
    print(f"✅ Selected {len(result)} random words at difficulty {difficulty}")
    return result

# --- Routes: API -------------------------------------------------------------
@app.route("/api/random-words", methods=["POST"])
def api_random_words():
    """
    Generate a random word list based on difficulty level.
    Expects JSON: {"difficulty": 1-5, "count": 10}
    """
    try:
        data = request.get_json()
        difficulty = data.get("difficulty", 3)
        count = data.get("count", 10)
        
        # Validate inputs
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            return jsonify({
                "status": "error",
                "message": "Difficulty must be between 1 and 5"
            }), 400
        
        if not isinstance(count, int) or count < 1 or count > 50:
            return jsonify({
                "status": "error",
                "message": "Count must be between 1 and 50"
            }), 400
        
        # Generate random words
        try:
            random_words = get_random_words_by_difficulty(difficulty, count)
            
            if not random_words:
                return jsonify({
                    "status": "error",
                    "message": f"Could not find enough words at difficulty level {difficulty}"
                }), 404
            
            # Store in session (same as file upload)
            set_wordbank(random_words)
            init_quiz_state()
            
            print(f"✅ Generated {len(random_words)} random words at difficulty {difficulty}")
            
            return jsonify({
                "status": "success",
                "count": len(random_words),
                "difficulty": difficulty,
                "message": f"🎲 Generated {len(random_words)} random words at difficulty level {difficulty}!",
                "words": random_words  # For preview
            })
            
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Error generating random words: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to generate random words: {str(e)}"
        }), 500

# --- Battle of the Bees: Helper Functions ------------------------------------

BATTLES_DIR = "data/groups"

def generate_battle_code() -> str:
    """Generate a unique 6-digit battle code like BATTLE123"""
    while True:
        # Generate random 3-digit number
        number = random.randint(100, 999)
        code = f"BATTLE{number}"
        
        # Check if code already exists
        battle_file = os.path.join(BATTLES_DIR, f"{code}.json")
        if not os.path.exists(battle_file):
            return code

def save_battle(battle_data: Dict) -> bool:
    """Save battle data to JSON file"""
    try:
        code = battle_data.get("battle_code")
        if not code:
            print("❌ No battle code provided")
            return False
        
        # Ensure directory exists
        os.makedirs(BATTLES_DIR, exist_ok=True)
        
        # Save to file
        battle_file = os.path.join(BATTLES_DIR, f"{code}.json")
        with open(battle_file, 'w', encoding='utf-8') as f:
            json.dump(battle_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Battle saved: {code}")
        return True
    except Exception as e:
        print(f"❌ Failed to save battle: {e}")
        return False

def load_battle(battle_code: str) -> Optional[Dict]:
    """Load battle data from JSON file"""
    try:
        battle_file = os.path.join(BATTLES_DIR, f"{battle_code}.json")
        if not os.path.exists(battle_file):
            print(f"⚠️ Battle not found: {battle_code}")
            return None
        
        with open(battle_file, 'r', encoding='utf-8') as f:
            battle_data = json.load(f)
        
        print(f"✅ Battle loaded: {battle_code}")
        return battle_data
    except Exception as e:
        print(f"❌ Failed to load battle {battle_code}: {e}")
        return None

def get_all_active_battles() -> List[Dict]:
    """Get list of all active (non-expired) battles"""
    battles = []
    try:
        if not os.path.exists(BATTLES_DIR):
            return battles
        
        now = datetime.now().timestamp()
        
        for filename in os.listdir(BATTLES_DIR):
            if filename.endswith(".json"):
                battle_file = os.path.join(BATTLES_DIR, filename)
                try:
                    with open(battle_file, 'r', encoding='utf-8') as f:
                        battle_data = json.load(f)
                    
                    # Check if expired (24 hours)
                    created_at = battle_data.get("created_at", 0)
                    expires_at = battle_data.get("expires_at", 0)
                    
                    if now < expires_at:
                        battles.append(battle_data)
                    else:
                        print(f"🗑️ Battle expired: {filename}")
                        # Optional: delete expired battle
                        # os.remove(battle_file)
                except Exception as e:
                    print(f"⚠️ Error reading battle file {filename}: {e}")
                    continue
        
        print(f"✅ Found {len(battles)} active battles")
        return battles
    except Exception as e:
        print(f"❌ Failed to get active battles: {e}")
        return []

def cleanup_expired_battles() -> int:
    """Delete expired battle files (24+ hours old)"""
    deleted_count = 0
    try:
        if not os.path.exists(BATTLES_DIR):
            return 0
        
        now = datetime.now().timestamp()
        
        for filename in os.listdir(BATTLES_DIR):
            if filename.endswith(".json"):
                battle_file = os.path.join(BATTLES_DIR, filename)
                try:
                    with open(battle_file, 'r', encoding='utf-8') as f:
                        battle_data = json.load(f)
                    
                    expires_at = battle_data.get("expires_at", 0)
                    
                    if now >= expires_at:
                        os.remove(battle_file)
                        deleted_count += 1
                        print(f"🗑️ Deleted expired battle: {filename}")
                except Exception as e:
                    print(f"⚠️ Error cleaning battle file {filename}: {e}")
                    continue
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} expired battles")
        return deleted_count
    except Exception as e:
        print(f"❌ Failed to cleanup battles: {e}")
        return 0

# --- Battle of the Bees: API Routes -------------------------------------------

@app.route("/api/battles/create", methods=["POST"])
def api_create_battle():
    """
    Create a new Battle of the Bees.
    Expects JSON or FormData:
    - battle_name: str (e.g., "Mrs. Smith's Vocabulary Test")
    - creator_name: str (e.g., "Mrs. Smith")
    - word_list: optional array of word objects OR use session wordbank
    - use_current_words: bool (if true, use current session wordbank)
    """
    try:
        # Handle both JSON and FormData
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()

        # Support both legacy and new frontend payloads
        # New frontend (battles.html) sends: { name, max_players }
        # Legacy API expects: { battle_name, creator_name, use_current_words, word_list }
        battle_name = (data.get("battle_name") or data.get("name") or "").strip()
        creator_name = (data.get("creator_name") or session.get("battle_creator_name") or "").strip()
        use_current_words = data.get("use_current_words", False)
        max_players = int(data.get("max_players", 50))
        
        # Validation
        if not battle_name:
            return jsonify({
                "status": "error",
                "message": "Battle name is required"
            }), 400
        
        if not creator_name:
            # Try to infer from logged-in user or fallback to generic host
            try:
                if current_user.is_authenticated:
                    creator_name = current_user.display_name or "Host"
                else:
                    creator_name = "Host"
            except Exception:
                creator_name = "Host"
        
        # Get word list
        word_list = None
        
        if use_current_words or "use_current_words" in data:
            # Use current session wordbank
            word_list = get_wordbank()
            if not word_list:
                return jsonify({
                    "status": "error",
                    "message": "No words in session. Please upload or generate words first."
                }), 400
        elif "word_list" in data:
            # Use provided word list
            word_list = data.get("word_list")
            if not isinstance(word_list, list) or len(word_list) == 0:
                return jsonify({
                    "status": "error",
                    "message": "Word list must be a non-empty array"
                }), 400
        else:
            return jsonify({
                "status": "error",
                "message": "Either provide a word_list or set use_current_words=true"
            }), 400
        
        # Generate unique battle code
        battle_code = generate_battle_code()
        
        # Create battle data structure
        now = datetime.now()
        battle_data = {
            "battle_code": battle_code,
            "battle_name": battle_name,
            "creator_name": creator_name,
            "created_at": now.timestamp(),
            "expires_at": (now.timestamp() + 86400),  # 24 hours from now
            "word_list": word_list,
            "shuffle_seed": random.randint(1000, 9999),  # For synchronized shuffle
            "players": {},  # Will be populated as players join
            "status": "active",
            "max_players": max_players
        }
        
        # Save battle
        if not save_battle(battle_data):
            return jsonify({
                "status": "error",
                "message": "Failed to save battle data"
            }), 500
        
        print(f"⚔️ Battle created: {battle_code} - {battle_name} by {creator_name}")
        
        # Return both legacy and new-frontend friendly shapes
        return jsonify({
            "status": "success",
            "battle_code": battle_code,
            "battle_name": battle_name,
            "word_count": len(word_list),
            "expires_at": battle_data["expires_at"],
            "message": f"⚔️ Battle of the Bees created! Code: {battle_code}",
            # New frontend expects ok + battle with .code
            "ok": True,
            "battle": {
                "code": battle_code,
                "status": "waiting",  # map 'active' -> 'waiting' for UI
                "is_public": True,
                "allow_guests": True,
                "current_players": 0,
                "max_players": max_players,
                "grade_range": "",
                "mode": "standard",
                "wordset": "Session Words",
                "created_at": datetime.fromtimestamp(battle_data["created_at"]).isoformat(),
                "started_at": None,
                "player_names": []
            }
        })
    
    except Exception as e:
        print(f"❌ Error creating battle: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to create battle: {str(e)}"
        }), 500

@app.route("/api/battles/join", methods=["POST"])
def api_join_battle():
    """
    Join an existing Battle of the Bees.
    Expects JSON:
    - battle_code: str (e.g., "BATTLE123")
    - player_name: str (e.g., "Alice")
    """
    try:
        data = request.get_json()
        battle_code = data.get("battle_code", "").strip().upper()
        player_name = data.get("player_name", "").strip()
        
        # Validation
        if not battle_code:
            return jsonify({
                "status": "error",
                "message": "Battle code is required"
            }), 400
        
        if not player_name:
            return jsonify({
                "status": "error",
                "message": "Player name is required"
            }), 400
        
        # Load battle
        battle_data = load_battle(battle_code)
        if not battle_data:
            return jsonify({
                "status": "error",
                "message": f"Battle not found: {battle_code}"
            }), 404
        
        # Check if expired
        now = datetime.now().timestamp()
        if now >= battle_data.get("expires_at", 0):
            return jsonify({
                "status": "error",
                "message": "This battle has expired"
            }), 410
        
        # Check player limit (max 50 players)
        players = battle_data.get("players", {})
        if len(players) >= 50:
            return jsonify({
                "status": "error",
                "message": "Battle is full (maximum 50 players)"
            }), 403
        
        # Generate unique player ID
        player_id = f"{normalize(player_name)}_{uuid.uuid4().hex[:8]}"
        
        # Check for duplicate names (case-insensitive)
        existing_names = [p.get("name", "").lower() for p in players.values()]
        if player_name.lower() in existing_names:
            return jsonify({
                "status": "error",
                "message": f"A player named '{player_name}' has already joined. Please use a different name."
            }), 409
        
        # Add player to battle
        players[player_id] = {
            "player_id": player_id,
            "name": player_name,
            "joined_at": now,
            "current_word_index": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "total_time_ms": 0,
            "score": 0,
            "streak": 0,
            "max_streak": 0,
            "completed": False,
            "answers": []  # Array of {word, user_input, correct, time_ms, timestamp}
        }
        
        battle_data["players"] = players
        
        # Save updated battle
        if not save_battle(battle_data):
            return jsonify({
                "status": "error",
                "message": "Failed to join battle"
            }), 500
        
        # Get word list (same for all players)
        word_list = battle_data.get("word_list", [])
        
        # Shuffle with same seed for all players
        shuffle_seed = battle_data.get("shuffle_seed", 1234)
        random.seed(shuffle_seed)
        shuffled_list = word_list.copy()
        random.shuffle(shuffled_list)
        random.seed()  # Reset to random seed
        
        # Store battle context in session
        session["battle_mode"] = True
        session["battle_code"] = battle_code
        session["battle_player_id"] = player_id
        session["battle_player_name"] = player_name
        
        # Load word list into session (same as upload flow)
        set_wordbank(shuffled_list)
        init_quiz_state()
        
        print(f"⚔️ {player_name} joined battle {battle_code}")
        
        return jsonify({
            "status": "success",
            "battle_code": battle_code,
            "battle_name": battle_data.get("battle_name"),
            "player_id": player_id,
            "player_name": player_name,
            "word_count": len(word_list),
            "player_count": len(players),
            "expires_at": battle_data.get("expires_at"),
            "message": f"⚔️ Welcome to the Battle, {player_name}!"
        })
    
    except Exception as e:
        print(f"❌ Error joining battle: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to join battle: {str(e)}"
        }), 500

@app.route("/api/battles/<battle_code>/leaderboard", methods=["GET"])
def api_battle_leaderboard(battle_code):
    """
    Get real-time leaderboard for a battle.
    Returns sorted list of players with scores, progress, accuracy.
    """
    try:
        battle_code = battle_code.upper()
        
        # Load battle
        battle_data = load_battle(battle_code)
        if not battle_data:
            return jsonify({
                "status": "error",
                "message": f"Battle not found: {battle_code}"
            }), 404
        
        players = battle_data.get("players", {})
        word_count = len(battle_data.get("word_list", []))
        
        # Calculate leaderboard
        leaderboard = []
        for player_id, player_data in players.items():
            correct = player_data.get("correct_count", 0)
            incorrect = player_data.get("incorrect_count", 0)
            total_answered = correct + incorrect
            accuracy = (correct / total_answered * 100) if total_answered > 0 else 0
            
            leaderboard.append({
                "player_id": player_id,
                "name": player_data.get("name"),
                "score": player_data.get("score", 0),
                "correct_count": correct,
                "incorrect_count": incorrect,
                "accuracy": round(accuracy, 1),
                "progress": f"{total_answered}/{word_count}",
                "completed": player_data.get("completed", False),
                "total_time_ms": player_data.get("total_time_ms", 0),
                "max_streak": player_data.get("max_streak", 0)
            })
        
        # Sort by score (descending), then by time (ascending)
        leaderboard.sort(key=lambda x: (-x["score"], x["total_time_ms"]))
        
        # Add rankings
        for i, player in enumerate(leaderboard, 1):
            player["rank"] = i
        
        return jsonify({
            "status": "success",
            "battle_code": battle_code,
            "battle_name": battle_data.get("battle_name"),
            "word_count": word_count,
            "player_count": len(players),
            "leaderboard": leaderboard
        })
    
    except Exception as e:
        print(f"❌ Error getting leaderboard: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get leaderboard: {str(e)}"
        }), 500

@app.route("/api/battles/live", methods=["GET"])
def api_battles_live():
    """Lightweight battles listing for Battles page without DB/Socket.IO.
    Returns shape expected by templates/battles.html: { ok, battles: [...], stats: {...} }
    """
    try:
        # Use file-backed battles list; tolerate missing directory by returning empty
        battles = get_all_active_battles()  # file-backed active battles
        mapped = []
        total_players = 0
        for b in battles:
            players_dict = b.get("players", {}) or {}
            player_names = [p.get("name") for p in players_dict.values() if isinstance(p, dict)]
            current_players = len(players_dict)
            total_players += current_players
            created_ts = b.get("created_at") or time.time()
            # Map status to UI-friendly values
            status = b.get("status", "active")
            if status == "active":
                status = "waiting"
            mapped.append({
                "id": b.get("battle_code"),
                "code": b.get("battle_code"),
                "status": status,
                "is_public": True,
                "allow_guests": True,
                "current_players": current_players,
                "max_players": int(b.get("max_players", 50)),
                "grade_range": "",
                "mode": "standard",
                "wordset": "Session Words",
                "created_at": datetime.fromtimestamp(created_ts).isoformat(),
                "started_at": None,
                "player_names": player_names
            })

        stats = {
            "active_battles": len(mapped),
            "total_players": total_players,
            "battles_waiting": sum(1 for m in mapped if m.get("status") in ("waiting",))
        }

        return jsonify({"ok": True, "battles": mapped, "stats": stats})
    except Exception as e:
        print(f"❌ Failed to list live battles: {e}")
        return jsonify({"ok": False, "error": "Failed to load battles"}), 500

@app.route("/api/battles/<battle_code>/progress", methods=["POST"])
def api_battle_progress(battle_code):
    """
    Update player progress after answering a word.
    Expects JSON:
    - player_id: str
    - word: str (the word that was answered)
    - user_input: str (what the user typed)
    - correct: bool
    - time_ms: int (time taken to answer)
    """
    try:
        battle_code = battle_code.upper()
        data = request.get_json()
        
        player_id = data.get("player_id")
        word = data.get("word")
        user_input = data.get("user_input")
        correct = data.get("correct", False)
        time_ms = data.get("time_ms", 0)
        
        # Load battle
        battle_data = load_battle(battle_code)
        if not battle_data:
            return jsonify({
                "status": "error",
                "message": "Battle not found"
            }), 404
        
        # Get player
        players = battle_data.get("players", {})
        if player_id not in players:
            return jsonify({
                "status": "error",
                "message": "Player not found in battle"
            }), 404
        
        player_data = players[player_id]
        
        # Update player stats
        if correct:
            player_data["correct_count"] += 1
            player_data["streak"] += 1
            player_data["max_streak"] = max(player_data["max_streak"], player_data["streak"])
            
            # Calculate score with bonuses
            base_score = 100
            
            # Speed bonus (under 5s = 50pts, under 10s = 25pts, under 15s = 10pts)
            time_seconds = time_ms / 1000
            if time_seconds < 5:
                speed_bonus = 50
            elif time_seconds < 10:
                speed_bonus = 25
            elif time_seconds < 15:
                speed_bonus = 10
            else:
                speed_bonus = 0
            
            # Streak multiplier (3+ = 1.5x, 5+ = 2x, 10+ = 3x)
            streak = player_data["streak"]
            if streak >= 10:
                multiplier = 3.0
            elif streak >= 5:
                multiplier = 2.0
            elif streak >= 3:
                multiplier = 1.5
            else:
                multiplier = 1.0
            
            word_score = int((base_score + speed_bonus) * multiplier)
            player_data["score"] += word_score
            
        else:
            player_data["incorrect_count"] += 1
            player_data["streak"] = 0  # Reset streak
        
        # Update time and progress
        player_data["total_time_ms"] += time_ms
        player_data["current_word_index"] += 1
        
        # Record answer
        player_data["answers"].append({
            "word": word,
            "user_input": user_input,
            "correct": correct,
            "time_ms": time_ms,
            "timestamp": datetime.now().timestamp()
        })
        
        # Check if completed
        word_count = len(battle_data.get("word_list", []))
        if player_data["current_word_index"] >= word_count:
            player_data["completed"] = True
        
        # Save updated battle
        if not save_battle(battle_data):
            return jsonify({
                "status": "error",
                "message": "Failed to save progress"
            }), 500
        
        return jsonify({
            "status": "success",
            "player_data": {
                "score": player_data["score"],
                "correct_count": player_data["correct_count"],
                "incorrect_count": player_data["incorrect_count"],
                "streak": player_data["streak"],
                "completed": player_data["completed"]
            }
        })
    
    except Exception as e:
        print(f"❌ Error updating battle progress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to update progress: {str(e)}"
        }), 500

@app.route("/api/battles/<battle_code>/export", methods=["GET"])
def api_battle_export(battle_code):
    """
    Export battle results as CSV for teachers to download.
    Returns CSV file with student names, scores, accuracy, time, etc.
    """
    try:
        battle_code = battle_code.upper()
        
        # Load battle
        battle_data = load_battle(battle_code)
        if not battle_data:
            return jsonify({
                "status": "error",
                "message": "Battle not found"
            }), 404
        
        # Create CSV
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Header row
        csv_writer.writerow([
            "Rank",
            "Player Name",
            "Score",
            "Correct",
            "Incorrect",
            "Accuracy (%)",
            "Total Time",
            "Max Streak",
            "Completed",
            "Status"
        ])
        
        # Get leaderboard data
        players = battle_data.get("players", {})
        word_count = len(battle_data.get("word_list", []))
        
        leaderboard = []
        for player_id, player_data in players.items():
            correct = player_data.get("correct_count", 0)
            incorrect = player_data.get("incorrect_count", 0)
            total_answered = correct + incorrect
            accuracy = (correct / total_answered * 100) if total_answered > 0 else 0
            
            # Format time as MM:SS
            total_seconds = player_data.get("total_time_ms", 0) / 1000
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            time_str = f"{minutes}:{seconds:02d}"
            
            leaderboard.append({
                "name": player_data.get("name"),
                "score": player_data.get("score", 0),
                "correct": correct,
                "incorrect": incorrect,
                "accuracy": accuracy,
                "time": time_str,
                "time_ms": player_data.get("total_time_ms", 0),
                "max_streak": player_data.get("max_streak", 0),
                "completed": player_data.get("completed", False),
                "progress": f"{total_answered}/{word_count}"
            })
        
        # Sort by score (descending), then by time (ascending)
        leaderboard.sort(key=lambda x: (-x["score"], x["time_ms"]))
        
        # Write data rows
        for i, player in enumerate(leaderboard, 1):
            status = "✅ Completed" if player["completed"] else f"🏃 In Progress ({player['progress']})"
            
            csv_writer.writerow([
                i,  # Rank
                player["name"],
                player["score"],
                player["correct"],
                player["incorrect"],
                f"{player['accuracy']:.1f}",
                player["time"],
                player["max_streak"],
                "Yes" if player["completed"] else "No",
                status
            ])
        
        # Create response
        from flask import make_response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = f"attachment; filename=battle_{battle_code}_results.csv"
        
        print(f"📊 Exported results for battle {battle_code}")
        return response
    
    except Exception as e:
        print(f"❌ Error exporting battle results: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to export results: {str(e)}"
        }), 500

@app.route("/api/wordbank", methods=["GET"])
def api_get_wordbank():
    # Enhanced debugging for mobile troubleshooting
    storage_id = session.get("wordbank_storage_id")
    words = get_wordbank()
    
    print(f"DEBUG /api/wordbank: session_id={session.get('session_id', 'NONE')}, "
          f"storage_id={storage_id}, word_count={len(words)}, "
          f"session_keys={list(session.keys())}, "
          f"user_agent={request.headers.get('User-Agent', 'UNKNOWN')[:50]}")
    
    # Check if storage exists in WORD_STORAGE
    if storage_id:
        with WORD_STORAGE_LOCK:
            stored_words = WORD_STORAGE.get(storage_id, [])
            print(f"DEBUG /api/wordbank: WORD_STORAGE contains {len(stored_words)} words for storage_id={storage_id}")
    
    # Return both 'words' (for backward compatibility) and 'success'/'count' (for LoadingSystem)
    response = jsonify({
        "words": words,
        "success": len(words) > 0,
        "count": len(words)
    })
    # Add cache-control headers to prevent Safari caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/api/content-filter-status", methods=["GET"])
def api_content_filter_status():
    """Get content filter status for current session with violation tracking"""
    try:
        status = get_content_filter_status(request)
        
        # Add helpful frontend information
        response_data = {
            "ok": True,
            "status": status,
            "messages": {
                "green": "🐝 Welcome to BeeSmart! Our bees keep the hive safe and educational.",
                "yellow": "⚠️ Please remember to use appropriate, educational words only.",
                "red": "🚫 Multiple inappropriate attempts detected. A report may be sent to your guardian."
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"⚠️ Content filter status error: {e}")
        # Provide safe fallback
        return jsonify({
            "ok": True,
            "status": {
                'session_id': 'error',
                'violation_count_24h': 0,
                'warning_level': 'green',
                'guardian_notification_triggered': False
            },
            "messages": {
                "green": "🐝 Welcome to BeeSmart! Our bees keep the hive safe and educational."
            }
        })

@app.route("/api/upload-enhanced", methods=["POST"])
def api_upload_enhanced():
    """
    Enhanced upload with progress tracking and bee-themed animations.
    Starts background processing and returns session ID for progress tracking.
    """
    import uuid
    session_id = str(uuid.uuid4())
    
    try:
        # Start processing in background thread
        thread = threading.Thread(target=process_upload_with_progress, args=(session_id, request))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "ok": True,
            "session_id": session_id,
            "message": "Upload started! Bees are getting ready to work..."
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to start upload: {e}"}), 500

@app.route("/api/upload-progress/<session_id>", methods=["GET"])
def api_upload_progress(session_id):
    """Get progress for an ongoing upload"""
    progress = get_upload_progress(session_id)
    if progress is None:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(progress)

def process_upload_with_progress(session_id, request_obj):
    """Background function to process upload with progress updates"""
    try:
        # Parse the request to get initial data
        rows: List[Dict[str, str]] = []
        
        # Handle the request similar to original upload but with progress tracking
        with request_obj.environ['werkzeug.request'].application_context():
            # Copy form data and files from original request
            content_type = request_obj.content_type
            
            if content_type and "application/json" in content_type:
                # JSON payload path
                payload = request_obj.get_json(silent=True) or {}
                words_json = payload.get("words", [])
                
                create_upload_session(session_id, len(words_json))
                update_upload_progress(session_id, "parsing", "Bees are examining the word list...", "bees_inspecting", 5)
                
                for i, w in enumerate(words_json):
                    word = (w.get("word") or "").strip()
                    sentence = (w.get("sentence") or "").strip()
                    hint = (w.get("hint") or "").strip()
                    if word:
                        rows.append({"word": word, "sentence": sentence, "hint": hint})
                        progress = int((i + 1) / len(words_json) * 20) + 5  # 5-25%
                        update_upload_progress(session_id, "parsing", f"Parsing word: {word}", "bees_collecting", progress, word)
                        time.sleep(0.1)  # Small delay for visual effect
            else:
                # File upload path  
                f = request_obj.files.get("file")
                if not f or f.filename == "":
                    complete_upload_session(session_id, False, "No file provided")
                    return
                
                create_upload_session(session_id, 50)  # Estimate, we'll update later
                update_upload_progress(session_id, "reading", "Bees are reading the uploaded file...", "bees_reading", 10)
                
                from werkzeug.utils import secure_filename
                filename = secure_filename(f.filename or "upload")
                content = f.read()
                ext = os.path.splitext(filename.lower())[1]
                
                update_upload_progress(session_id, "parsing", f"Bees are parsing {ext} file...", "bees_processing", 20)
                
                # Parse based on file type (similar to original logic)
                if ext == ".csv":
                    rows = parse_csv(content, filename)
                elif ext == ".txt":
                    rows = parse_txt(content)
                elif ext == ".docx":
                    rows = parse_docx(content)
                elif ext == ".pdf":
                    rows = parse_pdf(content)
                elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                    update_upload_progress(session_id, "ocr", "Bees are reading text from image...", "bees_reading_image", 25)
                    rows = parse_image_ocr(content)
                
                # Update session with actual word count
                UPLOAD_PROGRESS[session_id]["total_words"] = len(rows)
        
        if not rows:
            complete_upload_session(session_id, False, "No words found in uploaded file")
            return
        
        update_upload_progress(session_id, "deduplicating", "Bees are organizing and removing duplicates...", "bees_organizing", 30)
        
        # Deduplicate (similar to original logic)
        seen = set()
        deduped = []
        for i, r in enumerate(rows):
            word = (r.get("word") or "").strip()
            if not word:
                continue
            key = normalize(word)
            if key and key not in seen:
                seen.add(key)
                deduped.append({
                    "word": word,
                    "sentence": (r.get("sentence") or "").strip(),
                    "hint": (r.get("hint") or "").strip()
                })
            
            if i % 5 == 0:  # Update progress every 5 words
                progress = 30 + int((i + 1) / len(rows) * 20)  # 30-50%
                update_upload_progress(session_id, "deduplicating", f"Organizing: {word}", "bees_organizing", progress, word)
        
        if not deduped:
            complete_upload_session(session_id, False, "No valid words found after cleanup")
            return
        
        # ENHANCED KID-FRIENDLY FILTER: Block inappropriate words with guardian tracking
        update_upload_progress(session_id, "filtering", "Bees are checking words for kid-friendliness...", "bees_checking", 50)
        print(f"🛡️ Running enhanced kid-friendly filter on {len(deduped)} words...")
        
        # Extract just the words for filtering
        word_list = [r["word"] for r in deduped]
        
        # Use enhanced content filter with guardian reporting
        try:
            safe_words, blocked_words, violation_messages = filter_content_with_tracking(word_list, request)
            
            # Rebuild filtered list with only safe words
            filtered = []
            blocked = []
            
            for r in deduped:
                if r["word"] in safe_words:
                    filtered.append(r)
                elif r["word"] in blocked_words:
                    blocked.append({"word": r["word"], "reason": "inappropriate content detected"})
            
            # Log violation details
            if violation_messages:
                print(f"🚨 Content violations detected: {len(violation_messages)}")
                for vm in violation_messages:
                    print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                    if vm['should_report']:
                        print(f"   📧 Guardian report triggered for repeated violations")
            
        except Exception as e:
            # Fallback to original filtering if enhanced system fails
            print(f"⚠️ Enhanced filter failed, using fallback: {e}")
            filtered = []
            blocked = []
            for r in deduped:
                word = r["word"]
                is_safe, reason = is_kid_friendly(word)
                if is_safe:
                    filtered.append(r)
                else:
                    blocked.append({"word": word, "reason": reason})
        
        if blocked:
            print(f"⚠️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
        
        if not filtered:
            blocked_words = ", ".join([b["word"] for b in blocked[:5]])
            if len(blocked) > 5:
                blocked_words += f" and {len(blocked) - 5} more"
            complete_upload_session(session_id, False, 
                f"All {len(blocked)} words were blocked as inappropriate for children. Examples: {blocked_words}")
            return
        
        deduped = filtered
        print(f"✅ {len(deduped)} words passed kid-friendly filter")
        
        update_upload_progress(session_id, "enriching", "Bees are flying to collect definitions...", "bees_fetching_definitions", 55)
        
        # Enhanced enrichment with progress tracking and VALIDATION
        enriched = []
        enrichment_errors = []
        
        for i, r in enumerate(deduped):
            word = r["word"]
            sentence = r.get("sentence", "").strip()
            hint = r.get("hint", "").strip()
            
            progress = 55 + int((i + 1) / len(deduped) * 35)  # 55-90%
            update_upload_progress(session_id, "enriching", f"Getting definition for: {word}", "bees_fetching_definitions", progress, word)
            
            # If no sentence/definition provided, use enhanced dictionary lookup
            if not sentence and not hint:
                auto_definition = get_word_info(word)
                
                # VALIDATE: Check if definition is real (not placeholder or empty)
                if not auto_definition or auto_definition.strip() == "":
                    enrichment_errors.append(f"No definition found for '{word}'")
                    print(f"ERROR: Failed to get definition for '{word}'")
                
                enriched.append({
                    "word": word,
                    "sentence": auto_definition if auto_definition else f"Practice spelling this word: {word}",
                    "hint": ""
                })
            else:
                # VALIDATE: If user provided sentence/hint, make sure it's not empty after stripping
                if not sentence and not hint:
                    enrichment_errors.append(f"No definition or hint provided for '{word}'")
                enriched.append(r)
            
            time.sleep(0.05)  # Small delay for animation effect
        
        # CHECK: If we have enrichment errors, report them but continue with what we have
        if enrichment_errors:
            error_summary = "\n".join(enrichment_errors[:5])  # Show first 5 errors
            if len(enrichment_errors) > 5:
                error_summary += f"\n... and {len(enrichment_errors) - 5} more words"
            print(f"WARNING: Enrichment completed with {len(enrichment_errors)} warnings:\n{error_summary}")
            # Don't abort - we still have partial definitions from fallback
        
        # Limit records if needed
        if len(enriched) > MAX_RECORDS:
            enriched = enriched[:MAX_RECORDS]
        
        # CRITICAL VALIDATION: Check all definitions before quiz can start
        print("DEBUG: Validating wordbank definitions before storing...")
        is_valid, validation_error = validate_wordbank_definitions(enriched)
        
        if not is_valid:
            print(f"ERROR: Wordbank validation failed: {validation_error}")
            complete_upload_session(session_id, False, f"Definition Check Failed: {validation_error}")
            return
        
        update_upload_progress(session_id, "finalizing", "Bees are storing words in the hive...", "bees_storing", 95)
        
        # Store the wordbank and initialize quiz (USER UPLOAD)
        set_wordbank(enriched, is_user_upload=True)
        init_quiz_state()
        
        # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
        session.permanent = True
        session.modified = True
        time.sleep(0.25)
        
        # Double-check quiz state was saved
        saved_state = get_quiz_state()
        if not saved_state:
            print("ERROR /process_upload_with_progress: Quiz state failed to persist! Retrying init...")
            init_quiz_state()
            session.modified = True
            time.sleep(0.2)
        
        update_upload_progress(session_id, "completed", f"Success! {len(enriched)} words ready for spelling practice!", "bees_celebrating", 100)
        complete_upload_session(session_id, True, f"🐝 Amazing! The bees collected {len(enriched)} spelling words and are ready for the quiz!")
        
    except Exception as e:
        complete_upload_session(session_id, False, f"Oops! The bees encountered an error: {str(e)}")

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Accepts:
      - file upload (.csv, .txt, .docx, .pdf)
      - OR raw JSON body: { "words": [ {"word": "...", "sentence":"", "hint":""}, ... ] }
    """
    rows: List[Dict[str, str]] = []

    # JSON payload path
    if request.content_type and "application/json" in request.content_type:
        payload = request.get_json(silent=True) or {}
        words_json = payload.get("words", [])
        for w in words_json:
            word = (w.get("word") or "").strip()
            sentence = (w.get("sentence") or "").strip()
            hint = (w.get("hint") or "").strip()
            if word:
                rows.append({"word": word, "sentence": sentence, "hint": hint})

    # File upload path
    else:
        f = request.files.get("file")
        if not f or f.filename == "":
            return jsonify({"error": "No file provided"}), 400

        filename = secure_filename(f.filename or "upload")
        content = f.read()
        ext = os.path.splitext(filename.lower())[1]

        # Try by extension if known, else smart fallback
        try:
            if ext in ALLOWED_EXTENSIONS:
                if ext == ".csv":
                    rows = parse_csv(content, filename)
                elif ext == ".txt":
                    rows = parse_txt(content)
                elif ext == ".docx":
                    rows = parse_docx(content)
                elif ext == ".pdf":
                    rows = parse_pdf(content)
                elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                    rows = parse_image_ocr(content)
            else:
                # Fallback: attempt CSV, then TXT, then DOCX, then PDF
                tried = []
                try:
                    rows = parse_csv(content, filename)
                except Exception as e:
                    tried.append(f"csv:{e}")
                if not rows:
                    try:
                        rows = parse_txt(content)
                    except Exception as e:
                        tried.append(f"txt:{e}")
                if not rows and docx is not None:
                    try:
                        rows = parse_docx(content)
                    except Exception as e:
                        tried.append(f"docx:{e}")
                if not rows and extract_text is not None:
                    try:
                        rows = parse_pdf(content)
                    except Exception as e:
                        tried.append(f"pdf:{e}")
                if not rows and tried:
                    return jsonify({"error": f"Unable to parse file. Tried: {', '.join(tried)}"}), 400
        except RuntimeError as e:
            # e.g., missing dependency for docx/pdf
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to parse file: {e}"}), 400

    if not rows:
        return jsonify({"error": "No words parsed"}), 400

    # Trim and deduplicate
    seen = set()
    deduped = []
    for r in rows:
        word = (r.get("word") or "").strip()
        if not word:
            continue
        key = normalize(word)
        if key and key not in seen:
            seen.add(key)
            deduped.append({
                "word": word,
                "sentence": (r.get("sentence") or "").strip(),
                "hint": (r.get("hint") or "").strip()
            })

    if not deduped:
        return jsonify({"error": "No valid 'word' entries found"}), 400

    # ENHANCED KID-FRIENDLY FILTER: Block inappropriate words with guardian tracking
    print(f"🛡️ Running enhanced kid-friendly filter on {len(deduped)} words...")
    
    # Extract just the words for filtering
    word_list = [r["word"] for r in deduped]
    
    # Use enhanced content filter with guardian reporting
    try:
        safe_words, blocked_words, violation_messages = filter_content_with_tracking(word_list, request)
        
        # Rebuild filtered list with only safe words
        filtered = []
        blocked = []
        
        for r in deduped:
            if r["word"] in safe_words:
                filtered.append(r)
            elif r["word"] in blocked_words:
                blocked.append({"word": r["word"], "reason": "inappropriate content detected"})
        
        # Log violation details and show user-friendly messages
        violation_response_message = None
        if violation_messages:
            print(f"🚨 Content violations detected: {len(violation_messages)}")
            for vm in violation_messages:
                print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                if vm['should_report']:
                    print(f"   📧 Guardian report triggered for repeated violations")
            
            # Use the kid-friendly message from the most severe violation
            most_severe = max(violation_messages, key=lambda x: x['violation_count'])
            violation_response_message = most_severe['message']
        
    except Exception as e:
        # Fallback to original filtering if enhanced system fails
        print(f"⚠️ Enhanced filter failed, using fallback: {e}")
        filtered = []
        blocked = []
        violation_response_message = None
        for r in deduped:
            word = r["word"]
            is_safe, reason = is_kid_friendly(word)
            if is_safe:
                filtered.append(r)
            else:
                blocked.append({"word": word, "reason": reason})
    
    # Log results
    if blocked:
        print(f"⚠️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
    
    if not filtered:
        if violation_response_message:
            # Return the kid-friendly violation message instead of generic error
            return jsonify({"error": violation_response_message}), 400
        else:
            blocked_words = ", ".join([b["word"] for b in blocked[:5]])
            if len(blocked) > 5:
                blocked_words += f" and {len(blocked) - 5} more"
            return jsonify({
                "error": f"All {len(blocked)} words were blocked as inappropriate for children. Examples: {blocked_words}"
        }), 400
    
    # Use filtered list for enrichment
    deduped = filtered
    print(f"✅ {len(deduped)} words passed kid-friendly filter")

    # Auto-enrich words with definitions from built-in dictionary
    print(f"DEBUG /api/upload: Starting enrichment for {len(deduped)} words...")
    import time
    enrichment_start = time.time()
    
    enriched = []
    for idx, r in enumerate(deduped):
        word = r["word"]
        sentence = r.get("sentence", "").strip()
        hint = r.get("hint", "").strip()
        
        if idx % 10 == 0 and idx > 0:
            print(f"DEBUG /api/upload: Enriched {idx}/{len(deduped)} words...")
        
        # If no sentence/definition provided, use built-in dictionary
        if not sentence and not hint:
            print(f"DEBUG /api/upload: Enriching '{word}' (no sentence/hint provided)...")
            auto_definition = get_word_info(word)
            print(f"DEBUG /api/upload: Got definition for '{word}': {auto_definition[:100]}...")
            enriched.append({
                "word": word,
                "sentence": auto_definition,
                "hint": ""
            })
        else:
            print(f"DEBUG /api/upload: Skipping enrichment for '{word}' (sentence='{sentence[:50] if sentence else ''}', hint='{hint[:50] if hint else ''}')")
            # If user provided a sentence, ensure it has a blank for the word
            if sentence and "_____" not in sentence:
                # Try to replace the word with blank (case-insensitive)
                import re
                sentence_with_blank = re.sub(
                    r'\b' + re.escape(word) + r'\b',
                    '_____',
                    sentence,
                    flags=re.IGNORECASE,
                    count=1  # Only replace first occurrence
                )
                
                # If replacement worked, use it; otherwise keep original
                if '_____' in sentence_with_blank:
                    sentence = sentence_with_blank
                else:
                    # Word not found in sentence - wrap in proper format
                    sentence = f"Definition: {sentence}. Fill in the blank: The word is _____."
            
            enriched.append({
                "word": word,
                "sentence": sentence,
                "hint": hint
            })
    
    enrichment_time = time.time() - enrichment_start
    print(f"DEBUG /api/upload: Enrichment completed in {enrichment_time:.2f} seconds for {len(enriched)} words")
    
    deduped = enriched

    if len(deduped) > MAX_RECORDS:
        deduped = deduped[:MAX_RECORDS]

    # CRITICAL VALIDATION: Check all definitions before quiz can start
    print("DEBUG /api/upload: Validating wordbank definitions before storing...")
    is_valid, validation_error = validate_wordbank_definitions(deduped)
    
    if not is_valid:
        print(f"ERROR /api/upload: Wordbank validation failed: {validation_error}")
        return jsonify({"error": validation_error}), 400

    print(f"DEBUG /api/upload: Processing {len(deduped)} words. Session before: {list(session.keys())}")
    
    # CRITICAL: Set flag to prevent default word loading (same as manual upload)
    session["skip_default_load"] = True
    
    # Set wordbank (USER UPLOAD - marks has_uploaded_once)
    set_wordbank(deduped, is_user_upload=True)
    init_quiz_state()
    
    # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
    session.permanent = True
    session.modified = True
    
    # Increased delay to ensure quiz state persists BEFORE response
    time.sleep(0.25)
    
    # Double-check quiz state was saved (Railway can drop session between requests)
    saved_state = get_quiz_state()
    if not saved_state:
        print("ERROR /api/upload: Quiz state failed to persist! Retrying init...")
        init_quiz_state()
        session.modified = True
        time.sleep(0.2)
    
    # Verify wordbank was set correctly
    verify_wb = get_wordbank()
    print(f"DEBUG /api/upload: After upload - set {len(deduped)} words, verified {len(verify_wb)} words in session")
    print(f"DEBUG /api/upload: Session after: {list(session.keys())}")
    print(f"DEBUG /api/upload: Session storage_id: {session.get('wordbank_storage_id')}")
    print(f"DEBUG /api/upload: Session cookie will be: {session.sid if hasattr(session, 'sid') else 'N/A'}")
    
    # Debug: Print first word to verify format
    if deduped:
        print(f"DEBUG /api/upload: First word example: {deduped[0]}")
    
    if len(verify_wb) != len(deduped):
        print(f"WARNING /api/upload: Wordbank size mismatch! Set {len(deduped)}, got {len(verify_wb)}")
    
    return jsonify({"ok": True, "count": len(deduped)})

@app.route("/api/import", methods=["POST"])
def api_import():
    """
    Import endpoint - alias for /api/upload to handle JSON/CSV imports.
    Accepts file uploads (.json, .csv, .txt, .docx, .pdf)
    """
    # Simply delegate to the main upload endpoint
    return api_upload()

@app.route("/api/upload-manual-words", methods=["POST"])
def api_upload_manual_words():
    """
    Accepts manually typed/pasted words via JSON:
    { "words": ["cat", "dog", "bird", ...] }
    Enriches each word with definitions from dictionary.
    """
    try:
        data = request.get_json(silent=True) or {}
        words_list = data.get('words', [])
        
        if not words_list or not isinstance(words_list, list):
            return jsonify({"ok": False, "error": "Invalid words array"}), 400
        
        if not words_list:
            return jsonify({"ok": False, "error": "No words provided"}), 400
        
        # Convert to word records
        rows = []
        for word in words_list:
            word = word.strip()
            if word:  # Skip empty strings
                rows.append({
                    "word": word,
                    "sentence": "",
                    "hint": ""
                })
        
        if not rows:
            return jsonify({"ok": False, "error": "No valid words found"}), 400
        
        # Deduplicate using same logic as file upload
        seen = set()
        deduped = []
        for r in rows:
            word = r.get("word", "").strip()
            if not word:
                continue
            norm = normalize(word)
            if norm not in seen:
                seen.add(norm)
                deduped.append(r)
        
        if not deduped:
            return jsonify({"ok": False, "error": "No valid words after deduplication"}), 400
        
        # ENHANCED KID-FRIENDLY FILTER: Block inappropriate words with guardian tracking  
        print(f"🛡️ Running enhanced kid-friendly filter on {len(deduped)} manually entered words...")
        
        # Extract just the words for filtering
        word_list = [r["word"] for r in deduped]
        
        # Use enhanced content filter with guardian reporting
        try:
            safe_words, blocked_words, violation_messages = filter_content_with_tracking(word_list, request)
            
            # Rebuild filtered list with only safe words
            filtered = []
            blocked = []
            
            for r in deduped:
                if r["word"] in safe_words:
                    filtered.append(r)
                elif r["word"] in blocked_words:
                    blocked.append({"word": r["word"], "reason": "inappropriate content detected"})
            
            # Handle violation messages for manual entry (this is most likely paste abuse)
            violation_response_message = None
            if violation_messages:
                print(f"🚨 Manual entry violations detected: {len(violation_messages)}")
                for vm in violation_messages:
                    print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                    if vm['should_report']:
                        print(f"   📧 Guardian report triggered for repeated manual entry violations")
                
                # For manual entry, always show the warning message from the most severe violation
                most_severe = max(violation_messages, key=lambda x: x['violation_count'])
                violation_response_message = most_severe['message']
        
        except Exception as e:
            # Fallback to original filtering if enhanced system fails
            print(f"⚠️ Enhanced filter failed, using fallback: {e}")
            filtered = []
            blocked = []
            violation_response_message = None
            for r in deduped:
                word = r["word"]
                is_safe, reason = is_kid_friendly(word)
                if is_safe:
                    filtered.append(r)
                else:
                    blocked.append({"word": word, "reason": reason})
        
        if blocked:
            print(f"⚠️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
        
        if not filtered:
            if violation_response_message:
                # Return the kid-friendly violation message for manual entry abuse
                return jsonify({
                    "ok": False,
                    "error": violation_response_message,
                    "violation_warning": True
                }), 400
            else:
                blocked_words = ", ".join([b["word"] for b in blocked[:5]])
                if len(blocked) > 5:
                    blocked_words += f" and {len(blocked) - 5} more"
                return jsonify({
                    "ok": False, 
                    "error": f"All {len(blocked)} words were blocked as inappropriate for children. Examples: {blocked_words}"
                }), 400
        
        deduped = filtered
        print(f"✅ {len(deduped)} words passed kid-friendly filter")
        
        # Auto-enrich words with definitions (same logic as file upload)
        print(f"DEBUG /api/upload-manual-words: Starting enrichment for {len(deduped)} words...")
        import time
        enrichment_start = time.time()
        
        enriched = []
        for idx, r in enumerate(deduped):
            word = r["word"]
            
            if idx % 10 == 0 and idx > 0:
                print(f"DEBUG /api/upload-manual-words: Enriched {idx}/{len(deduped)} words...")
            
            # Get definition from dictionary
            auto_definition = get_word_info(word)
            enriched.append({
                "word": word,
                "sentence": auto_definition,
                "hint": ""
            })
        
        enrichment_time = time.time() - enrichment_start
        print(f"DEBUG /api/upload-manual-words: Enrichment completed in {enrichment_time:.2f} seconds for {len(enriched)} words")
        
        if len(enriched) > MAX_RECORDS:
            enriched = enriched[:MAX_RECORDS]
        
        print(f"DEBUG /api/upload-manual-words: Processing {len(enriched)} words. Session before: {list(session.keys())}")
        
        # CRITICAL: Set flag to prevent default word loading
        session["skip_default_load"] = True
        
        # Store and initialize quiz (USER UPLOAD - manual words)
        set_wordbank(enriched, is_user_upload=True)
        init_quiz_state()
        
        # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
        session.permanent = True
        session.modified = True
        
        # Increased delay to ensure quiz state persists BEFORE response
        time.sleep(0.25)
        
        # Double-check quiz state was saved
        saved_state = get_quiz_state()
        if not saved_state:
            print("ERROR /api/upload-manual-words: Quiz state failed to persist! Retrying init...")
            init_quiz_state()
            session.modified = True
            time.sleep(0.2)
        
        # Small delay to ensure session is persisted
        time.sleep(0.1)
        
        # Verify wordbank was set correctly
        verify_wb = get_wordbank()
        print(f"DEBUG /api/upload-manual-words: After upload - set {len(enriched)} words, verified {len(verify_wb)} words in session")
        print(f"DEBUG /api/upload-manual-words: Session after: {list(session.keys())}")
        print(f"DEBUG /api/upload-manual-words: Session storage_id: {session.get('wordbank_storage_id')}")
        
        # Debug: Print first word to verify format
        if enriched:
            print(f"DEBUG /api/upload-manual-words: First word example: {enriched[0]}")
        
        if len(verify_wb) != len(enriched):
            print(f"WARNING /api/upload-manual-words: Wordbank size mismatch! Set {len(enriched)}, got {len(verify_wb)}")
        
        return jsonify({"ok": True, "count": len(enriched)})
        
    except Exception as e:
        return jsonify({"ok": False, "error": f"Processing error: {str(e)}"}), 500

@app.route("/api/next", methods=["POST"])
def api_next():
    # Ensure session persists
    session.permanent = True
    session.modified = True
    
    state = get_quiz_state()
    wb = get_wordbank()
    
    # Enhanced debugging for session loss
    storage_id = session.get("wordbank_storage_id")
    print(f"DEBUG /api/next: session_id={session.get('session_id')}, storage_id={storage_id}, "
          f"wordbank_len={len(wb)}, quiz_idx={state['idx'] if state else 'NO_STATE'}")
    
    # Enhanced validation with detailed error messages
    if not wb:
        print(f"ERROR /api/next: No wordbank! storage_id={storage_id}, session_keys={list(session.keys())}")
        with WORD_STORAGE_LOCK:
            print(f"ERROR /api/next: WORD_STORAGE contains {len(WORD_STORAGE)} storage_ids: {list(WORD_STORAGE.keys())}")
            if storage_id:
                if storage_id in WORD_STORAGE:
                    print(f"ERROR /api/next: WORD_STORAGE has {len(WORD_STORAGE[storage_id])} words but get_wordbank() returned empty!")
                else:
                    print(f"ERROR /api/next: storage_id {storage_id} not found in WORD_STORAGE!")
        
        return jsonify({
            "error": "No word list loaded", 
            "message": "Please upload a word list (text file, CSV, or image) before starting the quiz.",
            "action_required": "upload_words"
        }), 400
    
    if len(wb) < 1:
        return jsonify({
            "error": "Word list is empty",
            "message": "The uploaded word list contains no valid words. Please check your file and try again.",
            "action_required": "upload_words"
        }), 400
    
    if state is None:
        print("WARNING /api/next: No quiz state found! This should have been initialized during upload.")
        print("WARNING /api/next: Attempting emergency quiz state initialization...")
        init_quiz_state()
        session.modified = True
        session.permanent = True
        time.sleep(0.2)  # Give session time to persist
        
        # Retry getting state
        state = get_quiz_state()
        if state is None:
            print("ERROR /api/next: Quiz state STILL missing after init! Session may be corrupted.")
            return jsonify({
                "error": "Quiz initialization failed",
                "message": "Unable to start quiz. Please refresh the page and try uploading your word list again.",
                "action_required": "reload_page"
            }), 500

    idx = state["idx"]
    original_question_index = idx  # preserve before we advance
    order = state["order"]
    
    # CRITICAL FIX: If quiz state order doesn't match current wordbank length, reset it
    # This happens when user uploads a new word list after completing a previous quiz
    if len(order) != len(wb):
        print(f"DEBUG /api/next: Quiz state mismatch - order={len(order)}, wordbank={len(wb)}, reinitializing")
        init_quiz_state()
        state = get_quiz_state()
        idx = state["idx"]
        order = state["order"]

    if idx >= len(order):
        # SAFETY CHECK: Don't show completion if no questions were answered
        if state["correct"] == 0 and state["incorrect"] == 0:
            print(f"WARNING /api/next: Quiz appears complete but no questions answered! Resetting.")
            print(f"WARNING /api/next: idx={idx}, len(order)={len(order)}, correct={state['correct']}, incorrect={state['incorrect']}")
            init_quiz_state()
            state = get_quiz_state()
            idx = state["idx"]
            order = state["order"]
            # Fall through to return first question
        else:
            # finished
            return jsonify({
                "done": True,
                "summary": {
                    "total": len(order),
                    "correct": state["correct"],
                    "incorrect": state["incorrect"],
                    "streak": state["streak"],
                    "history": state["history"]
                }
            })

    word_rec = wb[order[idx]]
    word = word_rec.get("word", "")
    
    # Get definition/sentence/hint - prioritize sentence, then hint, then definition
    sentence = (word_rec.get("sentence") or "").strip()
    hint = (word_rec.get("hint") or "").strip()

    # Apply backend blanker to ensure target word is hidden
    sentence = _blank_word(sentence, word)
    hint = _blank_word(hint, word)

    if sentence:
        definition = sentence
        has_definition = True
        definition_source = "sentence"
    elif hint:
        definition = f"Hint: {hint}"
        has_definition = True
        definition_source = "hint"
    elif word_rec.get("definition"):
        definition = _blank_word((word_rec.get("definition") or "").strip(), word)
        has_definition = bool(definition)
        definition_source = "definition_field"
    else:
        definition = "Listen carefully and spell the word you hear."
        has_definition = False
        definition_source = "fallback"

    return jsonify({
        "done": False,
        "index": idx + 1,
        "total": len(order),

        # Back-compat (UI already uses this)
        "definition": definition,

        # ✅ New explicit fields (use these in UI going forward)
        "sentence": sentence,
        "hint": hint,
        "definitionSource": definition_source,
        "hasDefinition": has_definition,

        # Word for TTS/pronunciation
        "word": word,
        "wordMeta": {
            "hasSentence": bool(sentence),
            "hasHint": bool(hint),
        },
        "progress": {
            "correct": state.get("correct", 0),
            "incorrect": state.get("incorrect", 0),
            "streak": state.get("streak", 0)
        }
    })

@app.route("/api/pronounce", methods=["POST"])
def api_pronounce():
    """Provide pronunciation helpers for the current quiz word."""
    state = get_quiz_state()
    wb = get_wordbank()
    if not wb or state is None:
        return jsonify({"error": "No active session"}), 400

    idx = state["idx"]
    order = state["order"]
    if idx >= len(order):
        return jsonify({"error": "Quiz finished"}), 400

    # Track hint usage for points calculation
    state["hints_used_current_word"] = state.get("hints_used_current_word", 0) + 1
    state["hints_used_total"] = state.get("hints_used_total", 0) + 1
    session[QUIZ_STATE_KEY] = state

    word_rec = wb[order[idx]]
    current_word = word_rec.get("word", "")

    # Get properly formatted definition + fill-in-the-blank sentence
    # This function already blanks out the word and formats nicely
    definition = get_word_info(current_word)
    
    # If get_word_info fails, fall back to sentence/hint from word_rec
    if not definition or definition.startswith("Definition not available"):
        if word_rec.get("sentence"):
            # Make sure to blank out the word in the sentence
            sentence_blanked = _blank_word(word_rec["sentence"], current_word)
            definition = sentence_blanked
        elif word_rec.get("hint"):
            definition = f"Hint: {word_rec['hint']}"
        else:
            definition = "Please spell the word you hear."

    word_lower = current_word.lower()
    cached_entry = DICTIONARY_CACHE.get(word_lower, {}) if current_word else {}
    phonetic_lookup = cached_entry.get("phonetic", "")
    spelled_out = build_phonetic_spelling(current_word)

    return jsonify({
        "word": current_word,
        "definition": definition,
        "sentence": word_rec.get("sentence", ""),
        "hint": word_rec.get("hint", ""),
        "phonetic": phonetic_lookup,
        "phonetic_spelling": spelled_out
    })

@app.route("/api/hint", methods=["POST"])
def api_hint():
    state = get_quiz_state()
    wb = get_wordbank()
    if not wb or state is None:
        return jsonify({"error": "No active session"}), 400

    idx = state["idx"]
    order = state["order"]
    if idx >= len(order):
        return jsonify({"error": "Quiz finished"}), 400

    # Track hint usage for points calculation
    state["hints_used_current_word"] = state.get("hints_used_current_word", 0) + 1
    state["hints_used_total"] = state.get("hints_used_total", 0) + 1
    session[QUIZ_STATE_KEY] = state

    word_rec = wb[order[idx]]
    return jsonify({
        "hint": word_rec.get("hint", ""),
        "sentence": word_rec.get("sentence", "")
    })

# --- 🎯 LEVEL PROGRESSION SYSTEM ------------------------------------------

def get_user_level(total_lifetime_points):
    """
    Calculate user's level tier based on lifetime points.
    Returns dict with tier, icon, level number, and progress info.
    
    Tier Progression:
    - Busy Bee: 0-499 pts
    - Flower Flyer: 500-1499 pts
    - Honey Collector: 1500-2999 pts
    - Spelling Star: 3000-4999 pts
    - Word Wizard: 5000-9999 pts
    - Queen Bee: 10000+ pts
    """
    points = total_lifetime_points or 0
    
    if points >= 10000:
        return {
            "tier": "Queen Bee",
            "icon": "👑",
            "level": 6,
            "points_current": points,
            "points_required": 10000,
            "points_to_next": 0,  # Max level reached!
            "progress_percent": 100,
            "is_max_level": True
        }
    elif points >= 5000:
        return {
            "tier": "Word Wizard",
            "icon": "🧙",
            "level": 5,
            "points_current": points,
            "points_required": 5000,
            "points_to_next": 10000 - points,
            "progress_percent": int(((points - 5000) / 5000) * 100),
            "is_max_level": False
        }
    elif points >= 3000:
        return {
            "tier": "Spelling Star",
            "icon": "⭐",
            "level": 4,
            "points_current": points,
            "points_required": 3000,
            "points_to_next": 5000 - points,
            "progress_percent": int(((points - 3000) / 2000) * 100),
            "is_max_level": False
        }
    elif points >= 1500:
        return {
            "tier": "Honey Collector",
            "icon": "🍯",
            "level": 3,
            "points_current": points,
            "points_required": 1500,
            "points_to_next": 3000 - points,
            "progress_percent": int(((points - 1500) / 1500) * 100),
            "is_max_level": False
        }
    elif points >= 500:
        return {
            "tier": "Flower Flyer",
            "icon": "🌸",
            "level": 2,
            "points_current": points,
            "points_required": 500,
            "points_to_next": 1500 - points,
            "progress_percent": int(((points - 500) / 1000) * 100),
            "is_max_level": False
        }
    else:  # 0-499 points
        return {
            "tier": "Busy Bee",
            "icon": "🐝",
            "level": 1,
            "points_current": points,
            "points_required": 0,
            "points_to_next": 500 - points,
            "progress_percent": int((points / 500) * 100),
            "is_max_level": False
        }

def check_level_up(old_points, new_points):
    """
    Check if user leveled up after earning new points.
    Returns level_up_data if leveled up, None otherwise.
    """
    old_level = get_user_level(old_points)
    new_level = get_user_level(new_points)
    
    if new_level["level"] > old_level["level"]:
        return {
            "leveled_up": True,
            "old_level": old_level,
            "new_level": new_level,
            "message": f"🎉 Level Up! You're now a {new_level['tier']}!"
        }
    
    return None

# --- 🏆 BADGE ACHIEVEMENT SYSTEM ------------------------------------------

# 🏆 BADGE ACHIEVEMENT SYSTEM
def check_badges(state, wb):
    """
    Check if any badges should be awarded based on quiz session performance.
    Returns list of badge objects: [{"type": "perfect_game", "name": "Perfect Game", "points": 500, "message": "..."}]
    """
    badges_earned = []
    
    correct = state.get("correct", 0)
    incorrect = state.get("incorrect", 0)
    total = correct + incorrect
    max_streak = state.get("max_streak", 0)
    hints_used_total = state.get("hints_used_total", 0)
    session_points = state.get("session_points", 0)
    history = state.get("history", [])
    
    # Calculate total elapsed time and average time per word
    total_time_ms = sum(h.get("elapsed_ms", 0) for h in history if h.get("correct"))
    correct_answers = [h for h in history if h.get("correct")]
    avg_time_ms = (total_time_ms / len(correct_answers)) if correct_answers else 0
    
    # 🌟 Perfect Game (+500 points)
    # Complete quiz with 100% accuracy, no hints, no wrong attempts
    if total >= 10 and incorrect == 0 and hints_used_total == 0:
        badges_earned.append({
            "type": "perfect_game",
            "name": "Perfect Game",
            "icon": "🌟",
            "points": 500,
            "message": "PERFECT GAME! You're a spelling champion!"
        })
    
    # ⚡ Speed Demon (+200 points)
    # Average answer time < 10 seconds per word (minimum 10 words)
    if correct >= 10 and avg_time_ms > 0 and (avg_time_ms / 1000) < 10:
        badges_earned.append({
            "type": "speed_demon",
            "name": "Speed Demon",
            "icon": "⚡",
            "points": 200,
            "message": "SPEED DEMON! Lightning-fast spelling!"
        })
    
    # 📚 Persistent Learner (+150 points)
    # Complete 50+ words in a single session
    if total >= 50:
        badges_earned.append({
            "type": "persistent_learner",
            "name": "Persistent Learner",
            "icon": "📚",
            "points": 150,
            "message": "PERSISTENT LEARNER! You love to learn!"
        })
    
    # 🔥 Hot Streak (+100 points)
    # Achieve 10+ correct answers in a row
    if max_streak >= 10:
        badges_earned.append({
            "type": "hot_streak",
            "name": "Hot Streak",
            "icon": "🔥",
            "points": 100,
            "message": "HOT STREAK! You're on fire!"
        })
    
    # 🎯 Comeback Kid (+100 points)
    # Get correct answer after 2+ wrong attempts on same word
    word_attempts = {}
    for h in history:
        word = h.get("word")
        if word:
            if word not in word_attempts:
                word_attempts[word] = {"attempts": 0, "got_correct": False}
            word_attempts[word]["attempts"] += 1
            if h.get("correct"):
                word_attempts[word]["got_correct"] = True
    
    comeback_words = [w for w, data in word_attempts.items() 
                     if data["attempts"] >= 3 and data["got_correct"]]
    if comeback_words:
        badges_earned.append({
            "type": "comeback_kid",
            "name": "Comeback Kid",
            "icon": "🎯",
            "points": 100,
            "message": "COMEBACK KID! Never give up!"
        })
    
    # 🍯 Honey Hunter (+75 points)
    # Use hints wisely (< 20% of words, minimum 10 words)
    if total >= 10 and hints_used_total > 0:
        hint_percentage = (hints_used_total / total) * 100
        if hint_percentage < 20:
            badges_earned.append({
                "type": "honey_hunter",
                "name": "Honey Hunter",
                "icon": "🍯",
                "points": 75,
                "message": "HONEY HUNTER! Smart use of help!"
            })
    
    # 🐝 Early Bird (+50 points)
    # Complete quiz quickly (within 5 minutes for 10+ words)
    if total >= 10 and total_time_ms > 0 and (total_time_ms / 1000 / 60) < 5:
        badges_earned.append({
            "type": "early_bird",
            "name": "Early Bird",
            "icon": "🐝",
            "points": 50,
            "message": "EARLY BIRD! Quick learner!"
        })
    
    return badges_earned

@app.route("/api/answer", methods=["POST"])
def api_answer():
    """
    Body JSON: { "user_input": "...", "method": "voice"|"keyboard", "elapsed_ms": <int> }
    Validates correctness, updates quiz state, advances index if correct.
    """
    # Ensure session persists
    session.permanent = True
    session.modified = True
    
    payload = request.get_json(force=True)
    user_input = (payload.get("user_input") or "").strip()
    method = (payload.get("method") or "keyboard").lower()
    elapsed_ms = int(payload.get("elapsed_ms") or 0)

    state = get_quiz_state()
    wb = get_wordbank()
    
    # Enhanced debugging
    print(f"DEBUG /api/answer: session_id={session.get('session_id')}, wordbank_len={len(wb)}, "
          f"quiz_idx={state['idx'] if state else 'NO_STATE'}, user_input='{user_input}'")
    
    # Check wordbank first
    if not wb:
        print(f"ERROR /api/answer: No wordbank! wb={len(wb) if wb else 0}")
        return jsonify({"error": "No active session"}), 400
    
    # Initialize quiz state if missing (same protection as /api/next)
    if state is None:
        print("WARNING /api/answer: No quiz state found! Attempting emergency initialization...")
        init_quiz_state()
        session.modified = True
        session.permanent = True
        time.sleep(0.2)  # Give session time to persist
        
        # Retry getting state
        state = get_quiz_state()
        if state is None:
            print("ERROR /api/answer: Quiz state STILL missing after init! Session corrupted.")
            return jsonify({"error": "Quiz initialization failed"}), 500

    idx = state["idx"]
    order = state["order"]
    if idx >= len(order):
        return jsonify({"error": "Quiz finished"}), 400

    word_rec = wb[order[idx]]
    correct_spelling = word_rec["word"]

    skip_requested = bool(payload.get("skip")) or method == "skip"

    if skip_requested:
        user_input = user_input or "[skipped]"

    is_correct = False if skip_requested else normalize(user_input) == normalize(correct_spelling)

    # 🍯 HONEY POINTS CALCULATION
    points_earned = 0
    points_breakdown = {}
    
    if is_correct and not skip_requested:
        # Base points for correct answer
        base_points = 100
        points_breakdown["base"] = base_points
        points_earned += base_points
        
        # Time bonus: 5 points per second remaining (based on 60s default timer)
        # Frontend should send elapsed_ms from when word was displayed
        timer_duration_ms = 60000  # Default 60 seconds
        if elapsed_ms > 0 and elapsed_ms < timer_duration_ms:
            time_remaining_seconds = (timer_duration_ms - elapsed_ms) / 1000
            time_bonus = int(5 * time_remaining_seconds)
            if time_bonus > 0:
                points_breakdown["time_bonus"] = time_bonus
                points_earned += time_bonus
        
        # Streak bonus: 10 points × current streak (before incrementing)
        current_streak = state.get("streak", 0)
        if current_streak > 0:
            streak_bonus = 10 * current_streak
            points_breakdown["streak_bonus"] = streak_bonus
            points_earned += streak_bonus
        
        # First attempt bonus: +50 points if no previous incorrect attempts on this word
        # Check if this word already in history with incorrect answer
        word_already_attempted_wrong = any(
            h.get("word") == correct_spelling and not h.get("correct") 
            for h in state.get("history", [])
        )
        if not word_already_attempted_wrong:
            points_breakdown["first_attempt"] = 50
            points_earned += 50
        
        # No hints bonus: +25 points if no hints used this session
        # Track hints_used in state (updated when /api/hint, /api/pronounce called)
        hints_used_this_word = state.get("hints_used_current_word", 0)
        
        # 💡 Apply hint penalty BEFORE adding no-hints bonus
        hint_penalty = 0
        if hints_used_this_word > 0:
            # 30% penalty for using hints
            hint_penalty = int(points_earned * 0.30)
            points_earned -= hint_penalty
            points_breakdown["hint_penalty"] = hint_penalty
            print(f"💡 Hint penalty applied: -{hint_penalty} points (30% reduction)")
        else:
            # No hints bonus
            points_breakdown["no_hints"] = 25
            points_earned += 25
        
        print(f"🍯 Points earned: {points_earned} (breakdown: {points_breakdown})")

    # Update stats and advance index for any completed attempt
    if is_correct:
        state["correct"] += 1
        state["streak"] += 1
        # Track session points
        state["session_points"] = state.get("session_points", 0) + points_earned
        if state["streak"] > state.get("max_streak", 0):
            state["max_streak"] = state["streak"]
    else:
        state["incorrect"] += 1
        state["streak"] = 0

    state["idx"] += 1
    
    # Reset hints counter for next word
    state["hints_used_current_word"] = 0

    state["history"].append({
        "word": correct_spelling,
        "user_input": user_input,
        "correct": is_correct,
        "method": method,
        "elapsed_ms": elapsed_ms,
        "ts": datetime.utcnow().isoformat(),
        "skipped": skip_requested
    })
    session[QUIZ_STATE_KEY] = state

    # Save to database for ALL users (authenticated + guests)
    user_obj = get_or_create_guest_user()
    if user_obj and state.get("db_session_id"):
        try:
            # Save individual word result
            quiz_result = QuizResult(
                session_id=state["db_session_id"],
                user_id=user_obj.id,
                word=correct_spelling,
                is_correct=is_correct,
                user_answer=user_input,
                correct_spelling=correct_spelling,
                time_taken_seconds=(elapsed_ms / 1000.0) if elapsed_ms else None,
                input_method=method,
                points_earned=int(state.get("session_points", 0) and (points_earned if is_correct else 0)),
                hints_used=state.get("hints_used_current_word", 0),
                # Use the 1-based question sequence; idx was incremented above after processing this answer
                question_number=state.get("idx", 0)
            )
            # Derive difficulty metadata
            try:
                quiz_result.calculate_difficulty()
            except Exception:
                pass
            db.session.add(quiz_result)
            
            # Update or create WordMastery record
            word_mastery = WordMastery.query.filter_by(
                user_id=user_obj.id,
                word=correct_spelling
            ).first()
            
            if word_mastery:
                word_mastery.update_stats(is_correct, time_taken=(elapsed_ms / 1000.0) if elapsed_ms else None)
            else:
                word_mastery = WordMastery(user_id=user_obj.id, word=correct_spelling)
                # Initialize stats via helper
                word_mastery.update_stats(is_correct, time_taken=(elapsed_ms / 1000.0) if elapsed_ms else None)
                db.session.add(word_mastery)
            
            db.session.commit()
            print(f"✅ Saved QuizResult for word '{correct_spelling}' (correct={is_correct}) to session {state['db_session_id']}")
        except Exception as e:
            print(f"⚠️ Failed to save quiz result: {e}")
            db.session.rollback()

    # Get phonetic information for incorrect answers
    phonetic_help = ""
    phonetic_spelling = ""
    if not is_correct or skip_requested:
        word_lower = correct_spelling.lower()
        if word_lower in DICTIONARY_CACHE:
            cached_data = DICTIONARY_CACHE[word_lower]
            phonetic_help = cached_data.get("phonetic", "")

        phonetic_spelling = build_phonetic_spelling(correct_spelling)

    feedback_message = "Great job!" if is_correct else (
        "Skipping this word. Let's try a new one!" if skip_requested else f"Try again! The word is spelled: {correct_spelling}"
    )

    next_index_position = min(state["idx"] + 1, len(order))
    
    # 🏆 Check for badge achievements
    badges_unlocked = []
    quiz_complete = state["idx"] >= len(order)
    
    # 🔍 DEBUG: Log quiz completion status
    print(f"� QUIZ STATUS DEBUG:")
    print(f"   Current index: {state['idx']}")
    print(f"   Total words: {len(order)}")
    print(f"   Quiz complete: {quiz_complete}")
    print(f"   Words correct: {state['correct']}")
    print(f"   Words incorrect: {state['incorrect']}")
    print(f"   Progress: {state['idx']}/{len(order)}")
    
    if quiz_complete:
        # Track total hints used across all words
        state["hints_used_total"] = state.get("hints_used_total", 0)
        
        # Check for badges
        badges_unlocked = check_badges(state, wb)
        
        # Add badge points to session total
        badge_points = sum(b["points"] for b in badges_unlocked)
        if badge_points > 0:
            state["session_points"] = state.get("session_points", 0) + badge_points
            print(f"🏆 Badges earned: {len(badges_unlocked)}, bonus points: {badge_points}")
        
        # Save badges to state for report card display
        state["badges_earned"] = badges_unlocked
        session[QUIZ_STATE_KEY] = state
    
    # Finalize database session for logged-in users OR guest accounts
    if quiz_complete and state.get("db_session_id"):
        print(f"🔍 Finalizing quiz session ID: {state.get('db_session_id')}")
        try:
            # Finalize the quiz session
            quiz_session = QuizSession.query.get(state["db_session_id"])
            if not quiz_session:
                print(f"⚠️ WARNING: QuizSession ID {state.get('db_session_id')} not found in database!")
            if quiz_session:
                quiz_session.correct_count = state["correct"]
                quiz_session.incorrect_count = state["incorrect"]
                quiz_session.best_streak = max(state.get("max_streak", 0), state.get("streak", 0))
                
                # 🍯 Save session points earned (from gamification system)
                quiz_session.points_earned = state.get("session_points", 0)
                
                quiz_session.complete_session()
                
                # Calculate points (includes points_earned + any database bonus)
                total_points = quiz_session.total_points
                
                # 🏆 Save badges to Achievement table
                if badges_unlocked and current_user.is_authenticated:
                    for badge in badges_unlocked:
                        achievement = Achievement(
                            user_id=current_user.id,
                            achievement_type=badge["type"],
                            achievement_name=badge["name"],
                            achievement_description=badge["message"],
                            points_bonus=badge["points"],
                            achievement_metadata={
                                "icon": badge["icon"],
                                "earned_in_session": state["db_session_id"],
                                "quiz_accuracy": quiz_session.accuracy_percentage
                            }
                        )
                        db.session.add(achievement)
                    print(f"🏆 Saved {len(badges_unlocked)} badge(s) to Achievement table")
                
                # Update user stats (if authenticated)
                level_up_data = None
                if current_user.is_authenticated:
                    # 🎯 Check for level up BEFORE updating points
                    old_lifetime_points = current_user.total_lifetime_points or 0
                    new_lifetime_points = old_lifetime_points + total_points
                    level_up_data = check_level_up(old_lifetime_points, new_lifetime_points)
                    
                    # Update stats
                    current_user.total_quizzes_completed = (current_user.total_quizzes_completed or 0) + 1
                    current_user.total_lifetime_points = new_lifetime_points
                    if quiz_session.best_streak > (current_user.best_streak or 0):
                        current_user.best_streak = quiz_session.best_streak
                    
                    # 📊 Update GPA and average accuracy
                    current_user.update_gpa_and_accuracy()
                    
                    print(f"📈 STATS UPDATE: User={current_user.username}, Quizzes={current_user.total_quizzes_completed}, Points={current_user.total_lifetime_points}, GPA={current_user.cumulative_gpa}, Avg Accuracy={current_user.average_accuracy}%")
                    
                    if level_up_data:
                        print(f"🎉 LEVEL UP! {level_up_data['old_level']['tier']} → {level_up_data['new_level']['tier']}")
                    
                    print(f"✅ Quiz completed! Grade: {quiz_session.grade}, Session Points: {quiz_session.points_earned}, Total Points: {total_points}, User Lifetime: {current_user.total_lifetime_points}")
                else:
                    print(f"✅ Guest quiz completed! Grade: {quiz_session.grade}, Points: {total_points}")
                
                # Save level up data to session for frontend
                if level_up_data:
                    state["level_up"] = level_up_data
                    session[QUIZ_STATE_KEY] = state
                
                # 🔥 CRITICAL: Commit all changes to database
                db.session.commit()
                print(f"💾 DATABASE COMMITTED: QuizSession.completed={quiz_session.completed}, User.total_quizzes={current_user.total_quizzes_completed if current_user.is_authenticated else 'N/A'}")
                
        except Exception as e:
            print(f"⚠️ Failed to finalize quiz session: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
    elif quiz_complete and not state.get("db_session_id"):
        print(f"⚠️ WARNING: Quiz complete but no db_session_id in state! Cannot save to database.")

    return jsonify({
        "correct": is_correct,
        "expected": correct_spelling,
        "skipped": skip_requested,
        "phonetic": phonetic_help if (phonetic_help and (not is_correct or skip_requested)) else "",
        "phonetic_spelling": phonetic_spelling if (not is_correct or skip_requested) else "",
        "feedback_message": feedback_message,
        "progress": {
            "index": next_index_position,
            "total": len(order),
            "correct": state["correct"],
            "incorrect": state["incorrect"],
            "streak": state["streak"]
        },
        "points": {
            "earned": points_earned,
            "breakdown": points_breakdown,
            "session_total": state.get("session_points", 0),
            "max_streak": state.get("max_streak", 0)
        },
        "quiz_complete": quiz_complete,
        "badges": badges_unlocked if quiz_complete else [],
        "level_up": state.get("level_up") if quiz_complete else None
    })

@app.route("/api/save-partial-progress", methods=["POST"])
def api_save_partial_progress():
    """
    Save quiz progress even if quiz is incomplete
    This ensures points, achievements, and progress are saved when users exit early
    """
    try:
        state = session.get(QUIZ_STATE_KEY)
        if not state:
            return jsonify({"status": "no_quiz", "message": "No active quiz session"}), 400
        
        # Only save if there's a database session and user has answered at least one question
        if not state.get("db_session_id"):
            return jsonify({"status": "no_db_session", "message": "No database session to save"}), 400
        
        if state.get("index", 0) == 0 and state.get("correct", 0) == 0 and state.get("incorrect", 0) == 0:
            return jsonify({"status": "no_progress", "message": "No progress to save yet"}), 400
        
        # Get the quiz session from database
        quiz_session = QuizSession.query.get(state["db_session_id"])
        if not quiz_session:
            return jsonify({"status": "error", "message": "Quiz session not found"}), 404
        
        # Update session with current progress (even if incomplete)
        quiz_session.correct_count = state.get("correct", 0)
        quiz_session.incorrect_count = state.get("incorrect", 0)
        quiz_session.best_streak = max(state.get("max_streak", 0), state.get("streak", 0))
        quiz_session.points_earned = state.get("session_points", 0)
        
        # Mark as incomplete (don't call complete_session())
        # But update the end time to show when they last accessed it
        from datetime import datetime
        quiz_session.session_end = datetime.utcnow()
        
        # Calculate partial accuracy
        total_answered = quiz_session.correct_count + quiz_session.incorrect_count
        if total_answered > 0:
            quiz_session.accuracy_percentage = (quiz_session.correct_count / total_answered) * 100
        
        # Save badges earned so far (if any)
        badges_unlocked = state.get("badges_earned", [])
        if badges_unlocked and current_user.is_authenticated:
            for badge in badges_unlocked:
                # Check if badge already exists to avoid duplicates
                existing = Achievement.query.filter_by(
                    user_id=current_user.id,
                    achievement_type=badge["type"],
                    achievement_name=badge["name"]
                ).first()
                
                if not existing:
                    achievement = Achievement(
                        user_id=current_user.id,
                        achievement_type=badge["type"],
                        achievement_name=badge["name"],
                        achievement_description=badge["message"],
                        points_bonus=badge["points"],
                        achievement_metadata={
                            "icon": badge["icon"],
                            "earned_in_session": state["db_session_id"],
                            "partial_save": True
                        }
                    )
                    db.session.add(achievement)
        
        # Update user's partial progress (for authenticated users)
        if current_user.is_authenticated:
            # Add partial points to lifetime total
            points_to_add = quiz_session.points_earned
            if points_to_add > 0:
                current_user.total_lifetime_points = (current_user.total_lifetime_points or 0) + points_to_add
            
            # Update best streak if current is higher
            if quiz_session.best_streak > (current_user.best_streak or 0):
                current_user.best_streak = quiz_session.best_streak
            
            # Update average accuracy and GPA (includes incomplete sessions)
            current_user.update_gpa_and_accuracy()
        
        # Commit to database
        db.session.commit()
        
        print(f"💾 Saved partial progress: Session {quiz_session.id}, Correct: {quiz_session.correct_count}, "
              f"Incorrect: {quiz_session.incorrect_count}, Points: {quiz_session.points_earned}, "
              f"Completed: {quiz_session.completed}")
        
        return jsonify({
            "status": "success",
            "message": "Progress saved successfully",
            "progress": {
                "correct": quiz_session.correct_count,
                "incorrect": quiz_session.incorrect_count,
                "points": quiz_session.points_earned,
                "streak": quiz_session.best_streak,
                "accuracy": round(quiz_session.accuracy_percentage, 1) if quiz_session.accuracy_percentage else 0
            }
        })
        
    except Exception as e:
        print(f"❌ Error saving partial progress: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/user/level", methods=["GET"])
def api_user_level():
    """
    Get current user's level information
    Returns: level tier, icon, progress to next level
    """
    try:
        # Get or create guest user to track progress
        user = get_or_create_guest_user()
        
        # Get level data based on lifetime points
        level_data = get_user_level(user.total_lifetime_points or 0)
        
        return jsonify({
            "success": True,
            "level": level_data
        })
    except Exception as e:
        print(f"ERROR /api/user/level: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "level": {
                "tier": "Busy Bee",
                "icon": "🐝",
                "level": 1,
                "points_current": 0,
                "points_next": 500,
                "points_to_next": 500,
                "progress_percent": 0,
                "is_max_level": False
            }
        })

@app.route("/api/dictionary-lookup", methods=["POST"])
def api_dictionary_lookup():
    """
    Look up a word in the built-in dictionary.
    Body JSON: { "word": "example" }
    Returns: { "word": "example", "definition": "...", "phonetic": "E X A M P L E", "found": true/false }
    """
    payload = request.get_json(force=True)
    word = (payload.get("word") or "").strip()
    
    if not word:
        return jsonify({"error": "No word provided"}), 400
    
    definition = get_word_info(word)
    phonetic_spelling = build_phonetic_spelling(word)
    word_lower = word.lower()
    found_in_cache = word_lower in DICTIONARY_CACHE

    return jsonify({
        "word": word,
        "definition": definition,
        "phonetic": phonetic_spelling,
        "found": found_in_cache,
        "source": "cached" if found_in_cache else "api_lookup"
    })

@app.route("/api/session_debug", methods=["GET"])
def api_session_debug():
    """Debug endpoint to check session state"""
    wb = get_wordbank()
    return jsonify({
        "wordbank_count": len(wb),
        "wordbank_preview": wb[:3] if wb else [],
        "session_keys": list(session.keys()),
        "data_key": DATA_KEY,
        "quiz_key": QUIZ_STATE_KEY
    })

@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear wordbank and quiz state with authorization check"""
    try:
        # Check for authorization parameter
        data = request.get_json() or {}
        confirmed = data.get('confirmed', False)
        
        if not confirmed:
            return jsonify({
                "error": "Authorization required", 
                "message": "Please confirm you want to clear all word lists"
            }), 400
        
        print(f"DEBUG /api/clear: Clearing session - session_id={session.get('session_id')}")
        
        # Get current storage_id before clearing
        storage_id = session.get("wordbank_storage_id")
        print(f"DEBUG /api/clear: Current storage_id={storage_id}")
        
        # Clear from storage first
        if storage_id:
            with WORD_STORAGE_LOCK:
                removed = WORD_STORAGE.pop(storage_id, None)
                print(f"DEBUG /api/clear: Removed {len(removed) if removed else 0} words from WORD_STORAGE")
        
        # Clear all session data
        session.pop("wordbank_storage_id", None)
        session.pop(DATA_KEY, None)
        session.pop(QUIZ_STATE_KEY, None)
        session.pop("wordbank_count", None)
        session.pop("using_default_words", None)  # Clear default flag
        
        # CRITICAL: Prevent auto-loading defaults after explicit clear
        # User explicitly cleared everything, so don't auto-load defaults
        session["skip_default_load"] = True
        session["has_uploaded_once"] = True  # Treat as if user has used the app before
        
        # Force session modification
        session.modified = True
        
        print(f"DEBUG /api/clear: Session cleared. Remaining keys: {list(session.keys())}")
        
        return jsonify({
            "ok": True, 
            "message": "All word lists and quiz progress cleared successfully! Ready for new words.",
            "cleared": {
                "wordbank": True,
                "quiz_state": True,
                "session_data": True
            }
        })
        
    except Exception as e:
        print(f"ERROR /api/clear: {str(e)}")
        return jsonify({"error": f"Failed to clear data: {str(e)}"}), 500

@app.route("/api/reset", methods=["POST"])
def api_reset():
    wb = get_wordbank()
    if not wb:
        return jsonify({"error": f"No wordbank loaded. Session keys: {list(session.keys())}"}), 400
    init_quiz_state()
    return jsonify({"ok": True})

@app.route("/api/build_dictionary", methods=["POST"])
def api_build_dictionary():
    """
    Build dictionary cache for all words in current wordbank
    P0 Feature: Batch dictionary builder for imported word lists
    """
    wordbank = get_wordbank()
    if not wordbank:
        return jsonify({"error": "No wordbank loaded"}), 400
    
    results = {
        "total_words": len(wordbank),
        "api_lookups": 0,
        "cache_hits": 0,
        "fallbacks": 0,
        "errors": []
    }
    
    print(f"Building dictionary cache for {len(wordbank)} words...")
    
    for record in wordbank:
        word = record.get("word", "").strip()
        if not word:
            continue
            
        word_lower = word.lower()
        
        # Skip if already cached
        if word_lower in DICTIONARY_CACHE:
            results["cache_hits"] += 1
            continue
        
        try:
            # Try API lookup using safe wrapper function
            api_result = DICT_LOOKUP(word)
            
            if api_result:
                # Cache successful API result
                cache_entry = {word_lower: api_result}
                save_dictionary_cache(cache_entry)
                DICTIONARY_CACHE.update(cache_entry)
                results["api_lookups"] += 1
                print(f"Γ£ô API lookup successful for '{word}'")
            else:
                # Generate fallback
                fallback_data = generate_smart_fallback(word)
                fallback_data["created"] = datetime.now().isoformat()
                
                cache_entry = {word_lower: fallback_data}
                save_dictionary_cache(cache_entry)
                DICTIONARY_CACHE.update(cache_entry)
                results["fallbacks"] += 1
                print(f"ΓÜá Using fallback for '{word}'")
                
        except Exception as e:
            error_msg = f"Error processing '{word}': {str(e)}"
            results["errors"].append(error_msg)
            print(f"Γ£ù {error_msg}")
    
    return jsonify({
        "success": True,
        "message": f"Dictionary cache built for {results['total_words']} words",
        "results": results
    })


# ============================================================================
# AUTHENTICATION ROUTES (User Login/Registration)
# ============================================================================

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'GET':
        return render_template('auth/register.html')

    # Handle registration form submission
    data = request.get_json() if request.is_json else request.form

    username = data.get('username', '').strip()
    display_name = data.get('display_name', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    grade_level = data.get('grade_level', '')
    teacher_key = data.get('teacher_key', '').strip()
    avatar_id = data.get('avatar_id', 'mascot-bee').strip()  # Default to mascot-bee
    role = data.get('role', 'student').strip().lower()  # Get role from form (student, teacher, parent)

    try:
        # Quick readiness check each request is cheap and prevents opaque 500s
        _ensure_db_initialized()

        # Validation
        if not username or not display_name or not password:
            return jsonify({"success": False, "error": "Username, display name, and password are required"}), 400

        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

        # Validate role
        if role not in ['student', 'teacher', 'parent']:
            role = 'student'  # Default to student if invalid

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"success": False, "error": "Username already taken"}), 400

        # Check if email already exists (if provided)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({"success": False, "error": "Email already registered"}), 400

        # Create new user
        new_user = User(
            username=username,
            display_name=display_name,
            email=email if email else None,
            role=role,
            grade_level=grade_level if grade_level else None,
            avatar_id=avatar_id,
            avatar_variant='default'
            # NOTE: Do NOT set teacher_key for students - it has UNIQUE constraint
            # Students are linked via TeacherStudent table instead (see below)
        )
        new_user.set_password(password)

        # Mark that user selected an avatar during registration
        # This ensures their choice overrides the default mascot
        try:
            prefs = new_user.preferences or {}
            # Set avatar_selected=True if an avatar_id was provided in the form
            # This allows ANY avatar choice to override the mascot
            prefs['avatar_selected'] = bool(avatar_id and 'avatar_id' in data)
            new_user.preferences = prefs
        except Exception:
            pass

        # Generate unique key for teachers and parents
        generated_key = None
        if role in ['teacher', 'parent']:
            generated_key = new_user.generate_teacher_key()

        db.session.add(new_user)
        db.session.commit()
        
        # Link to teacher/parent if teacher_key provided (for students)
        linked_to_admin = False
        admin_name = None
        if teacher_key and role == 'student':
            teacher = User.query.filter_by(teacher_key=teacher_key).first()
            if teacher:
                try:
                    # Check if link already exists
                    existing_link = TeacherStudent.query.filter_by(
                        teacher_key=teacher_key,
                        student_id=new_user.id
                    ).first()
                    
                    if not existing_link:
                        link = TeacherStudent(
                            teacher_key=teacher_key,
                            teacher_user_id=teacher.id,
                            student_id=new_user.id,
                            relationship_type='parent' if teacher.role == 'parent' else 'teacher'
                        )
                        db.session.add(link)
                        db.session.commit()
                        linked_to_admin = True
                        admin_name = teacher.display_name
                        print(f"✅ Linked {new_user.username} to {teacher.username}'s dashboard")
                    else:
                        linked_to_admin = True
                        admin_name = teacher.display_name
                        print(f"ℹ️ Link already exists for {new_user.username} → {teacher.username}")
                except Exception as link_error:
                    print(f"⚠️ Failed to create TeacherStudent link: {link_error}")
                    # Non-fatal - user registration still succeeds
            else:
                print(f"⚠️ Teacher key '{teacher_key}' not found - student not linked")
        
        # Auto-login after registration
        login_user(new_user, remember=True)

        # Send welcome email asynchronously (best-effort) if email provided
        if new_user.email:
            def _send_async():
                try:
                    send_welcome_email(new_user.email, new_user.username, new_user.role, new_user.teacher_key if new_user.role in ['teacher', 'parent'] else None)
                except Exception as _e:
                    print(f"⚠️ Welcome email async failed: {_e}")
            threading.Thread(target=_send_async, daemon=True).start()
        
        # Build response message
        message = f"🎉 Welcome to the hive, {display_name}! Your account has been created successfully! 🐝✨"
        
        # Add confirmation message if student was linked to admin
        if linked_to_admin and admin_name:
            message += f"\n\n✅ You've been linked to {admin_name}'s dashboard for progress tracking!"
        
        # Determine redirect based on role
        if role == 'teacher':
            redirect_url = url_for('teacher_dashboard')
        elif role == 'parent':
            redirect_url = url_for('parent_dashboard')
        else:
            redirect_url = url_for('student_dashboard')
        
        response_data = {
            "success": True,
            "message": message,
            "redirect": redirect_url,
            "linked_to_admin": linked_to_admin,
            "admin_name": admin_name if linked_to_admin else None
        }
        
        # Include the generated key in response for teachers/parents
        if generated_key:
            response_data["teacher_key"] = generated_key
            response_data["show_key_modal"] = True
        
        return jsonify(response_data)
    
    except sa_exc.ProgrammingError as e:
        # Likely missing tables on first boot
        db.session.rollback()
        return jsonify({"success": False, "error": "Server database not initialized. Please try again in a moment."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 500


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'GET':
        # Pop and show a one-time success banner if set by reset
        show_banner = bool(session.pop('reset_success_banner', False))
        return render_template('auth/login.html', show_reset_banner=show_banner)
    
    # Handle login form submission
    data = request.get_json() if request.is_json else request.form

    try:
        _ensure_db_initialized()

        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400

        # Find user (case-insensitive username match)
        try:
            user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        except Exception:
            # Fallback to exact match if db.func.lower not available (shouldn't happen)
            user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({"success": False, "error": "Invalid username or password"}), 401

        if not user.is_active:
            return jsonify({"success": False, "error": "Account is disabled. Please contact support."}), 403

        # Log the user in
        login_user(user, remember=bool(remember))

        # Update last login
        user.update_last_login(ip_address=request.remote_addr)
        db.session.commit()

        # Redirect based on role
        if user.role == 'teacher' or user.role == 'parent':
            redirect_url = url_for('teacher_dashboard') if user.role == 'teacher' else url_for('parent_dashboard')
        elif user.role == 'admin':
            redirect_url = url_for('admin_dashboard')
        else:
            redirect_url = url_for('student_dashboard')

        return jsonify({
            "success": True,
            "message": f"Welcome back, {user.display_name}! 🐝",
            "redirect": redirect_url
        })
    except sa_exc.ProgrammingError as e:
        db.session.rollback()
        app.logger.error(f"Login failed due to missing tables: {e}")
        return jsonify({"success": False, "error": "Server database is initializing. Please try again shortly."}), 500
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Login unexpected error: {e}")
        return jsonify({"success": False, "error": "An unexpected server error occurred. Please try again."}), 500


@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    """Initiate password reset. Always return generic success to avoid enumeration."""
    try:
        data = request.get_json(silent=True) or {}
        identifier = (data.get('identifier') or '').strip()

        # Always respond generically
        generic = {
            "success": True,
            "message": "If an account exists for that email or username, we'll send reset instructions."
        }
        if not identifier:
            return jsonify(generic)

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if _is_rate_limited(identifier, ip):
            return jsonify(generic)

        # Look up user by email or username (case-insensitive)
        user = None
        try:
            if '@' in identifier:
                user = User.query.filter(db.func.lower(User.email) == identifier.lower()).first()
            else:
                user = User.query.filter(db.func.lower(User.username) == identifier.lower()).first()
        except Exception:
            user = None

        # Count towards rate limit regardless
        _add_rate_hit(identifier, ip)

        if not user or not user.email:
            return jsonify(generic)

        # Create a reset token valid for 30 minutes
        raw = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw)
        expires = datetime.utcnow() + timedelta(minutes=30)

        prt = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires,
            request_ip=ip,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(prt)
        db.session.commit()

        # Build reset URL and send email
        reset_url = url_for('reset_password_page', token=raw, _external=True)
        send_reset_email(user.email, reset_url)

        # Audit (best-effort)
        log_session_action(
            'password_reset_requested',
            user_id=user.id,
            data={'expires_at': expires.isoformat()}
        )
        db.session.commit()

        # Dev-only: capture last raw token for automated tests
        if ALLOW_DEV_RESET_PEEK:
            try:
                DEV_RESET_TOKEN_CACHE[user.id] = raw
            except Exception:
                pass

        return jsonify(generic)
    except Exception as e:
        app.logger.warning(f"forgot-password handler error: {e}")
        db.session.rollback()
        return jsonify({
            "success": True,
            "message": "If an account exists for that email or username, we'll send reset instructions."
        })


@app.route('/auth/reset', methods=['GET', 'POST'])
def reset_password_page():
    """Render reset page on GET; on POST, validate token and set new password."""
    if request.method == 'GET':
        token = request.args.get('token', '')
        return render_template('auth/reset.html', token=token)

    # POST: accept JSON or form
    data = request.get_json(silent=True) or request.form
    token = (data.get('token') or '').strip()
    new_password = (data.get('password') or '').strip()

    generic = {"success": True, "message": "If the link is valid, your password has been updated."}

    if not token or len(new_password) < 8:
        return jsonify(generic)

    try:
        token_hash = _hash_token(token)
        prt = PasswordResetToken.query.filter_by(token_hash=token_hash).first()
        if not prt or prt.is_used or prt.is_expired:
            # Audit invalid or expired attempts without revealing to client
            uid = prt.user_id if prt else None
            log_session_action('password_reset_attempt_invalid', user_id=uid)
            return jsonify(generic)

        user = User.query.get(prt.user_id)
        if not user:
            return jsonify(generic)

        # Simple password checks: length and not equal to username/email
        if len(new_password) < 8 or new_password.lower() in {user.username.lower(), (user.email or '').lower()}:
            return jsonify(generic)

        user.set_password(new_password)
        prt.mark_used()
        # Audit success
        log_session_action('password_reset_completed', user_id=user.id)
        # Set session banner to show on next login page render
        try:
            session['reset_success_banner'] = True
        except Exception:
            pass
        db.session.commit()
        return jsonify(generic)
    except Exception as e:
        app.logger.warning(f"reset-password error: {e}")
        db.session.rollback()
        return jsonify(generic)


# Dev-only endpoint: fetch last raw reset token for a user (by username/email)
@app.route('/dev/peek-reset-token')
def dev_peek_reset_token():
    if not ALLOW_DEV_RESET_PEEK:
        return jsonify({"error": "not available"}), 404
    ident = (request.args.get('identifier') or '').strip().lower()
    if not ident:
        return jsonify({"error": "missing identifier"}), 400
    user = None
    if '@' in ident:
        user = User.query.filter(db.func.lower(User.email) == ident).first()
    else:
        user = User.query.filter(db.func.lower(User.username) == ident).first()
    if not user:
        return jsonify({"error": "not found"}), 404
    raw = DEV_RESET_TOKEN_CACHE.get(user.id)
    return jsonify({"token": raw})


@app.route('/auth/logout')
@login_required
def logout():
    """Log out current user"""
    logout_user()
    flash('You have been logged out. See you next time! 🐝', 'success')
    return redirect(url_for('home'))


# Temporary, token-gated admin bootstrap endpoint
# Usage: POST /dev/bootstrap-admin with JSON {"token": "<secret>", "username": "BigDaddy", "password": "<newpass>", "email": "..."}
# Only enabled if env BOOTSTRAP_ADMIN_TOKEN is set. Returns 404 otherwise.
@app.route('/dev/bootstrap-admin', methods=['POST'])
def dev_bootstrap_admin():
    secret = os.environ.get('BOOTSTRAP_ADMIN_TOKEN')
    if not secret:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    token = (data.get('token') or '').strip()
    if token != secret:
        return jsonify({"error": "unauthorized"}), 401
    username = (data.get('username') or 'BigDaddy').strip()
    password = (data.get('password') or '').strip()
    email = (data.get('email') or 'admin@example.com').strip()
    display_name = (data.get('display_name') or 'Administrator').strip()
    if len(password) < 8:
        return jsonify({"error": "password too short"}), 400
    try:
        _ensure_db_initialized()
        # find by username (case-insensitive)
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if not user:
            user = User(
                username=username,
                email=email,
                display_name=display_name,
                role='admin',
                is_active=True,
            )
            user.set_password(password)
            db.session.add(user)
        else:
            user.email = email or user.email
            user.display_name = display_name or user.display_name
            user.role = 'admin'
            user.is_active = True
            user.set_password(password)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Admin '{user.username}' is ready.",
            "id": user.id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"bootstrap-admin error: {e}")
        return jsonify({"error": "server error"}), 500


# Quick list users endpoint (no token required, use for debugging then remove)
# Usage: GET /dev/list-users
@app.route('/dev/list-users', methods=['GET'])
def dev_list_users():
    try:
        _ensure_db_initialized()
        users = User.query.all()
        # Also show which database is being used
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')
        # Mask password in postgres URI for security
        if 'postgresql://' in db_uri:
            import re
            db_uri_safe = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_uri)
        else:
            db_uri_safe = db_uri
        return jsonify({
            "count": len(users),
            "users": [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users],
            "database": db_uri_safe
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Quick promote-to-admin endpoint (no token required, use once and remove)
# Usage: POST /dev/promote-admin with JSON {"username": "BigDaddy2"}
@app.route('/dev/promote-admin', methods=['POST'])
def dev_promote_admin():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username:
        return jsonify({"error": "username required"}), 400
    try:
        _ensure_db_initialized()
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if not user:
            return jsonify({"error": "user not found"}), 404
        user.role = 'admin'
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"User '{user.username}' promoted to admin.",
            "id": user.id,
            "role": user.role
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"promote-admin error: {e}")
        return jsonify({"error": "server error"}), 500


# Database migration endpoint - adds missing columns to users table
@app.route('/dev/migrate-db', methods=['POST'])
def dev_migrate_database():
    """Run database migration to add avatar and GPA columns"""
    try:
        from sqlalchemy import inspect as sql_inspect, text
        
        inspector = sql_inspect(db.engine)
        if not inspector.has_table('users'):
            return jsonify({"error": "Users table doesn't exist"}), 500
        
        existing_columns = {col['name'] for col in inspector.get_columns('users')}
        
        migrations = [
            ("avatar_id", "VARCHAR(50) DEFAULT 'mascot-bee'"),
            ("avatar_variant", "VARCHAR(10) DEFAULT 'default'"),
            ("avatar_locked", "BOOLEAN DEFAULT FALSE"),
            ("avatar_last_updated", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("cumulative_gpa", "NUMERIC(3, 2) DEFAULT 0.0"),
            ("average_accuracy", "NUMERIC(5, 2) DEFAULT 0.0"),
            ("best_grade", "VARCHAR(5)"),
            ("best_streak", "INTEGER DEFAULT 0"),
        ]
        
        results = []
        for col_name, col_def in migrations:
            if col_name in existing_columns:
                results.append(f"⏭️  {col_name} - already exists")
            else:
                try:
                    sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"
                    db.session.execute(text(sql))
                    db.session.commit()
                    results.append(f"✅ {col_name} - added")
                except Exception as e:
                    db.session.rollback()
                    results.append(f"❌ {col_name} - failed: {str(e)}")
        
        # Create index
        try:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_avatar_id ON users(avatar_id)"))
            db.session.commit()
            results.append("✅ Avatar index created")
        except Exception as e:
            results.append(f"⚠️  Index: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": "Migration completed",
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Temporary, token-gated user deletion endpoint (for ops/cleanup)
# Usage: POST /dev/delete-user with JSON {"token": "<secret>", "username": "..."} OR {"email": "..."} OR {"user_id": 123}
# Only enabled if env BOOTSTRAP_ADMIN_TOKEN is set. Returns 404 otherwise.
@app.route('/dev/delete-user', methods=['POST'])
def dev_delete_user():
    secret = os.environ.get('BOOTSTRAP_ADMIN_TOKEN')
    if not secret:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    token = (data.get('token') or '').strip()
    if token != secret:
        return jsonify({"error": "unauthorized"}), 401

    identifier = {
        'username': (data.get('username') or '').strip(),
        'email': (data.get('email') or '').strip(),
        'user_id': data.get('user_id')
    }

    if not identifier['username'] and not identifier['email'] and not identifier['user_id']:
        return jsonify({"error": "Provide username, email, or user_id"}), 400

    try:
        _ensure_db_initialized()

        user = None
        if identifier['user_id']:
            try:
                user = User.query.get(int(identifier['user_id']))
            except Exception:
                user = None
        if user is None and identifier['email']:
            try:
                user = User.query.filter(db.func.lower(User.email) == identifier['email'].lower()).first()
            except Exception:
                user = None
        if user is None and identifier['username']:
            try:
                user = User.query.filter(db.func.lower(User.username) == identifier['username'].lower()).first()
            except Exception:
                user = None

        if not user:
            return jsonify({"error": "user not found"}), 404

        uname = user.username
        uid = user.id

        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": f"User '{uname}' (id={uid}) deleted."})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"delete-user error: {e}")
        return jsonify({"error": "server error"}), 500


@app.route('/auth/dashboard')
@login_required
def student_dashboard():
    """Student personal dashboard with badge showcase"""
    # Redirect non-student roles to their respective dashboards
    try:
        role = getattr(current_user, 'role', 'student')
        if role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        if role == 'parent':
            return redirect(url_for('parent_dashboard'))
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
    except Exception:
        # If anything goes wrong determining role, fall back to student view
        pass
    # Get student's quiz history
    recent_sessions = QuizSession.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(QuizSession.session_start.desc()).limit(10).all()
    
    # Calculate stats
    total_sessions = QuizSession.query.filter_by(user_id=current_user.id, completed=True).count()
    avg_accuracy = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter_by(
        user_id=current_user.id,
        completed=True
    ).scalar() or 0.0
    
    # Get words needing practice (below 70% success rate)
    struggling_words = WordMastery.query.filter_by(
        user_id=current_user.id
    ).filter(WordMastery.success_rate < 70).order_by(WordMastery.success_rate).limit(12).all()
    
    # 🏆 NEW: Get badge collection
    achievements = Achievement.query.filter_by(
        user_id=current_user.id
    ).order_by(Achievement.earned_date.desc()).all()
    
    # Group badges by type and calculate stats
    badge_collection = {}
    total_badge_points = 0
    
    for achievement in achievements:
        badge_type = achievement.achievement_type
        points = achievement.points_bonus or 0
        total_badge_points += points
        
        if badge_type not in badge_collection:
            badge_collection[badge_type] = {
                'count': 0,
                'total_points': 0,
                'first_earned': achievement.earned_date,
                'latest_earned': achievement.earned_date,
                'rarity': BADGE_METADATA.get(badge_type, {}).get('rarity', 'common'),
                'icon': BADGE_METADATA.get(badge_type, {}).get('icon', '🏆'),
                'name': BADGE_METADATA.get(badge_type, {}).get('name', badge_type.replace('_', ' ').title()),
                'description': BADGE_METADATA.get(badge_type, {}).get('description', '')
            }
        
        badge_collection[badge_type]['count'] += 1
        badge_collection[badge_type]['total_points'] += points
        
        # Update latest earned date if this is more recent
        if achievement.earned_date > badge_collection[badge_type]['latest_earned']:
            badge_collection[badge_type]['latest_earned'] = achievement.earned_date
    
    # Get recent badges (last 5)
    recent_badges = []
    for achievement in achievements[:5]:
        badge_type = achievement.achievement_type
        recent_badges.append({
            'type': badge_type,
            'icon': BADGE_METADATA.get(badge_type, {}).get('icon', '🏆'),
            'name': BADGE_METADATA.get(badge_type, {}).get('name', badge_type.replace('_', ' ').title()),
            'points': achievement.points_bonus or 0,
            'earned_date': achievement.earned_date
        })
    
    # Sort badge collection by rarity (legendary → epic → rare → common)
    rarity_order = {'legendary': 0, 'epic': 1, 'rare': 2, 'common': 3}
    badge_collection_sorted = dict(sorted(
        badge_collection.items(),
        key=lambda x: (rarity_order.get(x[1]['rarity'], 4), -x[1]['count'])
    ))
    
    # If teacher/parent/admin, also gather linked students for quick actions/cards
    linked_students = []
    if getattr(current_user, 'role', None) in ['teacher', 'parent', 'admin']:
        try:
            # Helper is defined below; safe to call at runtime
            students = _get_linked_students_for_current()
        except Exception:
            students = []
        # Attach quick stats and avatar thumbnail
        for s in students:
            try:
                avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
                    QuizSession.user_id == s.id,
                    QuizSession.completed == True
                ).scalar()
                s.avg_accuracy = round(float(avg_acc or 0.0), 1)
            except Exception:
                s.avg_accuracy = 0.0
            try:
                avatar = s.get_avatar_data()
                s.avatar_thumb_url = (avatar.get('urls') or {}).get('thumbnail') or avatar.get('thumbnail_url')
            except Exception:
                s.avatar_thumb_url = None
        linked_students = students

    return render_template('auth/student_dashboard.html',
                         recent_sessions=recent_sessions,
                         total_sessions=total_sessions,
                         avg_accuracy=round(avg_accuracy, 1),
                         struggling_words=struggling_words,
                         badge_collection=badge_collection_sorted,
                         recent_badges=recent_badges,
                         total_badges=len(achievements),
                         total_badge_points=total_badge_points,
                         linked_students=linked_students)


@app.route('/test/avatar-picker')
@login_required
def test_avatar_picker():
    """Test page for avatar picker with 3D viewer"""
    return render_template('test_avatar_picker.html')

@app.route('/test/api')
def test_api():
    """Test page for API debugging"""
    return render_template('test_api.html')

@app.route('/test/avatar-loading')
def test_avatar_loading():
    """Test page for avatar 3D loading diagnostics"""
    return render_template('test_avatar_loading.html')


@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard with student overview"""
    if current_user.role not in ['teacher', 'parent', 'admin']:
        flash('Access denied: Teachers only', 'error')
        return redirect(url_for('home'))
    
    # Get all students linked to this teacher
    students_query = db.session.query(User).join(
        TeacherStudent,
        TeacherStudent.student_id == User.id
    ).filter(
        TeacherStudent.teacher_key == current_user.teacher_key,
        TeacherStudent.is_active == True
    )
    
    students = students_query.all()
    
    # Add individual stats to each student
    for student in students:
        # Get average accuracy for this student (both completed AND incomplete with progress)
        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id == student.id,
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).scalar()
        student.avg_accuracy = round(avg_acc, 1) if avg_acc else 0.0
        # Attach avatar thumbnail for quick identification
        try:
            avatar = student.get_avatar_data()
            student.avatar_thumb_url = (avatar.get('urls') or {}).get('thumbnail') or avatar.get('thumbnail_url')
        except Exception:
            student.avatar_thumb_url = None
    
    # Get class statistics
    class_stats = {
        'total_students': len(students),
        'total_quizzes': 0,
        'avg_accuracy': 0.0,
        'total_points': 0
    }
    
    if students:
        student_ids = [s.id for s in students]
        
        # Total quizzes (include both completed and in-progress with answers)
        class_stats['total_quizzes'] = QuizSession.query.filter(
            QuizSession.user_id.in_(student_ids),
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).count()
        
        # Average accuracy (include incomplete sessions)
        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id.in_(student_ids),
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).scalar()
        class_stats['avg_accuracy'] = round(avg_acc, 1) if avg_acc else 0.0
        
        # Total points
        total_points = db.session.query(db.func.sum(User.total_lifetime_points)).filter(
            User.id.in_(student_ids)
        ).scalar()
        class_stats['total_points'] = total_points if total_points else 0
    
    from datetime import datetime
    return render_template('teacher/dashboard.html',
                         students=students,
                         class_stats=class_stats,
                         now=datetime.now())


@app.route('/parent/dashboard')
@login_required
def parent_dashboard():
    """Parent dashboard with child overview (same functionality as teacher)"""
    if current_user.role not in ['parent', 'admin']:
        flash('Access denied: Parents only', 'error')
        return redirect(url_for('home'))
    
    # Get all students linked to this parent
    students_query = db.session.query(User).join(
        TeacherStudent,
        TeacherStudent.student_id == User.id
    ).filter(
        TeacherStudent.teacher_key == current_user.teacher_key,
        TeacherStudent.is_active == True
    )
    
    students = students_query.all()
    
    # Add individual stats to each student
    for student in students:
        # Get average accuracy for this student (include incomplete sessions)
        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id == student.id,
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).scalar()
        student.avg_accuracy = round(avg_acc, 1) if avg_acc else 0.0
        # Attach avatar thumbnail for quick identification
        try:
            avatar = student.get_avatar_data()
            student.avatar_thumb_url = (avatar.get('urls') or {}).get('thumbnail') or avatar.get('thumbnail_url')
        except Exception:
            student.avatar_thumb_url = None
    
    # Get family statistics
    family_stats = {
        'total_students': len(students),
        'total_quizzes': 0,
        'avg_accuracy': 0.0,
        'total_points': 0
    }
    
    if students:
        student_ids = [s.id for s in students]
        
        # Total quizzes (include both completed and in-progress)
        family_stats['total_quizzes'] = QuizSession.query.filter(
            QuizSession.user_id.in_(student_ids),
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).count()
        
        # Average accuracy (include incomplete sessions)
        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id.in_(student_ids),
            or_(
                QuizSession.completed == True,
                and_(
                    QuizSession.completed == False,
                    (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                )
            )
        ).scalar()
        family_stats['avg_accuracy'] = round(avg_acc, 1) if avg_acc else 0.0
        
        # Total points
        total_points = db.session.query(db.func.sum(User.total_lifetime_points)).filter(
            User.id.in_(student_ids)
        ).scalar()
        family_stats['total_points'] = total_points if total_points else 0
    
    from datetime import datetime
    return render_template('parent/dashboard.html',
                         students=students,
                         family_stats=family_stats,
                         now=datetime.now())


# =============================
# Teacher/Parent Exports
# =============================

def _require_teacher_parent_admin():
    return current_user.role in ['teacher', 'parent', 'admin']

def _get_linked_students_for_current():
    if current_user.role == 'admin':
        return User.query.filter_by(role='student', is_active=True).all()
    return db.session.query(User).join(
        TeacherStudent, TeacherStudent.student_id == User.id
    ).filter(
        TeacherStudent.teacher_key == current_user.teacher_key,
        TeacherStudent.is_active == True
    ).all()

@app.route('/teacher/export/class.csv')
@login_required
def export_class_csv():
    if not _require_teacher_parent_admin():
        flash('Access denied', 'error')
        return redirect(url_for('home'))

    students = _get_linked_students_for_current()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name','Grade','Quizzes','Avg Accuracy %','Points','Best Grade','Best Streak','Last Active'])
    for s in students:
        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id == s.id,
            QuizSession.completed == True
        ).scalar()
        avg_acc_val = round(float(avg_acc), 1) if avg_acc else 0.0
        last_active = s.last_login.strftime('%Y-%m-%d') if s.last_login else ''
        writer.writerow([
            s.display_name,
            s.grade_level or '',
            s.total_quizzes_completed or 0,
            avg_acc_val,
            s.total_lifetime_points or 0,
            s.best_grade or '',
            s.best_streak or 0,
            last_active
        ])
    output.seek(0)
    return Response(
        output.read(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename="class_report.csv"'}
    )

@app.route('/teacher/export/class.pdf')
@login_required
def export_class_pdf():
    if not _require_teacher_parent_admin():
        flash('Access denied', 'error')
        return redirect(url_for('home'))
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib import colors
    except Exception:
        flash('PDF engine not available on server', 'error')
        return redirect(url_for('teacher_dashboard'))

    students = _get_linked_students_for_current()
    # Optional filtering by selected IDs via query parameter (?ids=1,2,3)
    ids_param = request.args.get('ids')
    if ids_param:
        try:
            requested_ids = {int(x) for x in ids_param.split(',') if x.strip().isdigit()}
            if requested_ids:
                # Keep only students that are both linked and requested
                students = [s for s in students if s.id in requested_ids]
        except Exception:
            pass

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 1 * inch

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, y, "BeeSmart Class Report")
    y -= 0.3 * inch
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, y, f"Owner: {current_user.display_name} • Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    y -= 0.4 * inch

    headers = ['Name','Grade','Quizzes','Avg %','Points','Best Grade','Best Streak','Last Active']
    col_x = [1*inch, 2.6*inch, 3.4*inch, 4.0*inch, 4.6*inch, 5.2*inch, 6.1*inch, 6.9*inch]

    c.setFont("Helvetica-Bold", 9)
    for hx, htxt in zip(col_x, headers):
        c.drawString(hx, y, htxt)
    y -= 0.2 * inch
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.lightgrey)
    c.line(1*inch, y, 7.8*inch, y)
    y -= 0.15 * inch
    c.setFont("Helvetica", 9)

    for s in students:
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch
            c.setFont("Helvetica-Bold", 9)
            for hx, htxt in zip(col_x, headers):
                c.drawString(hx, y, htxt)
            y -= 0.2 * inch
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.lightgrey)
            c.line(1*inch, y, 7.8*inch, y)
            y -= 0.15 * inch
            c.setFont("Helvetica", 9)

        avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
            QuizSession.user_id == s.id,
            QuizSession.completed == True
        ).scalar()
        avg_acc_val = round(float(avg_acc), 1) if avg_acc else 0.0
        last_active = s.last_login.strftime('%Y-%m-%d') if s.last_login else ''
        row = [
            s.display_name,
            s.grade_level or '',
            str(s.total_quizzes_completed or 0),
            f"{avg_acc_val}",
            str(s.total_lifetime_points or 0),
            s.best_grade or '',
            str(s.best_streak or 0),
            last_active
        ]
        for hx, cell in zip(col_x, row):
            c.drawString(hx, y, str(cell))
        y -= 0.18 * inch

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='class_report.pdf')

@app.route('/teacher/student/<int:student_id>/export.pdf')
@login_required
def export_student_pdf(student_id: int):
    if not _require_teacher_parent_admin():
        flash('Access denied', 'error')
        return redirect(url_for('home'))
    student = User.query.get_or_404(student_id)
    if current_user.role in ['teacher', 'parent']:
        link = TeacherStudent.query.filter_by(
            teacher_key=current_user.teacher_key,
            student_id=student.id,
            is_active=True
        ).first()
        if not link:
            flash('This student is not linked to your key.', 'error')
            return redirect(url_for('teacher_dashboard'))
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib import colors
    except Exception:
        flash('PDF engine not available on server', 'error')
        return redirect(url_for('teacher_student_detail', student_id=student.id))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 1 * inch

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, y, f"Student Report – {student.display_name}")
    y -= 0.3*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d')} • Owner: {current_user.display_name}")
    y -= 0.35*inch

    avg_acc = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
        QuizSession.user_id == student.id,
        QuizSession.completed == True
    ).scalar()
    avg_acc_val = round(float(avg_acc), 1) if avg_acc else 0.0
    overview = [
        f"Quizzes: {QuizSession.query.filter_by(user_id=student.id, completed=True).count()}",
        f"Avg %: {avg_acc_val}",
        f"GPA: {student.cumulative_gpa or 0}",
        f"Best Grade: {student.best_grade or '—'}",
        f"Best Streak: {student.best_streak or 0}",
        f"Points: {student.total_lifetime_points or 0}",
    ]
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y, "  •  ".join(overview))
    y -= 0.4*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Recent Quiz Sessions")
    y -= 0.22*inch
    c.setFont("Helvetica", 9)
    sessions = QuizSession.query.filter_by(user_id=student.id, completed=True).order_by(QuizSession.session_end.desc()).limit(10).all()
    if sessions:
        for s in sessions:
            if y < 1*inch:
                c.showPage(); y = height - 1*inch; c.setFont("Helvetica", 9)
            line = f"{(s.session_end or s.session_start).strftime('%Y-%m-%d')}  •  {s.accuracy_percentage or 0}%  •  {s.grade or '—'}  •  {s.total_points or 0} pts"
            c.drawString(1*inch, y, line)
            y -= 0.18*inch
    else:
        c.drawString(1*inch, y, "No sessions yet.")
        y -= 0.18*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Speed Round Scores")
    y -= 0.22*inch
    c.setFont("Helvetica", 9)
    srs = SpeedRoundScore.query.filter_by(user_id=student.id).order_by(SpeedRoundScore.completed_at.desc()).limit(10).all()
    if srs:
        for r in srs:
            if y < 1*inch:
                c.showPage(); y = height - 1*inch; c.setFont("Helvetica", 9)
            line = f"{r.completed_at.strftime('%Y-%m-%d')}  •  {r.honey_points_earned} pts  •  {r.words_correct}/{r.words_attempted}  •  {r.accuracy_percentage}%"
            c.drawString(1*inch, y, line)
            y -= 0.18*inch
    else:
        c.drawString(1*inch, y, "No speed scores yet.")
        y -= 0.18*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Recent Achievements")
    y -= 0.22*inch
    c.setFont("Helvetica", 9)
    achs = Achievement.query.filter_by(user_id=student.id).order_by(Achievement.earned_date.desc()).limit(10).all()
    if achs:
        for a in achs:
            if y < 1*inch:
                c.showPage(); y = height - 1*inch; c.setFont("Helvetica", 9)
            line = f"{a.earned_date.strftime('%Y-%m-%d')}  •  {a.achievement_name or a.achievement_type}"
            c.drawString(1*inch, y, line)
            y -= 0.18*inch
    else:
        c.drawString(1*inch, y, "No achievements yet.")
        y -= 0.18*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, "Struggling Words (60 days)")
    y -= 0.22*inch
    cutoff = datetime.utcnow() - timedelta(days=60)
    rows = db.session.query(
        QuizResult.word,
        db.func.count(QuizResult.id).label('misses')
    ).filter(
        QuizResult.user_id == student.id,
        QuizResult.is_correct == False,
        QuizResult.timestamp >= cutoff
    ).group_by(QuizResult.word).order_by(db.desc('misses')).limit(10).all()
    c.setFont("Helvetica", 9)
    if rows:
        for w, misses in rows:
            if y < 1*inch:
                c.showPage(); y = height - 1*inch; c.setFont("Helvetica", 9)
            c.drawString(1*inch, y, f"{w}: {int(misses)} misses")
            y -= 0.18*inch
    else:
        c.drawString(1*inch, y, "No struggling words in the last 60 days.")
        y -= 0.18*inch

    c.showPage()
    c.save()
    buffer.seek(0)
    safe_name = re.sub(r'[^A-Za-z0-9_\-]+', '_', student.display_name)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'{safe_name}_report.pdf')


@app.route('/teacher/student/<int:student_id>')
@login_required
def teacher_student_detail(student_id: int):
    """Detailed profile view for a linked student (teachers/parents/admin only)."""
    # AuthZ: Only teachers/parents/admins
    if current_user.role not in ['teacher', 'parent', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('home'))

    student = User.query.get_or_404(student_id)

    # If teacher/parent, enforce link via TeacherStudent
    if current_user.role in ['teacher', 'parent']:
        link = TeacherStudent.query.filter_by(
            teacher_key=current_user.teacher_key,
            student_id=student.id,
            is_active=True
        ).first()
        if not link:
            flash('This student is not linked to your key.', 'error')
            return redirect(url_for('teacher_dashboard'))

    # Avatar data
    try:
        avatar_data = student.get_avatar_data()
    except Exception:
        avatar_data = None

    # Aggregate stats
    total_quizzes = QuizSession.query.filter_by(user_id=student.id, completed=True).count()
    avg_accuracy = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
        QuizSession.user_id == student.id,
        QuizSession.completed == True
    ).scalar() or 0

    # Recent quiz sessions
    recent_sessions = QuizSession.query.filter_by(user_id=student.id, completed=True).order_by(
        QuizSession.session_end.desc().nullslast()
    ).limit(10).all()

    # Recent speed round scores
    recent_speed = SpeedRoundScore.query.filter_by(user_id=student.id).order_by(
        SpeedRoundScore.completed_at.desc()
    ).limit(10).all()

    # Recent achievements
    recent_achievements = Achievement.query.filter_by(user_id=student.id).order_by(
        Achievement.earned_date.desc()
    ).limit(10).all()

    # Struggling words: most-missed in last 60 days
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=60)
    struggling_rows = db.session.query(
        QuizResult.word,
        db.func.count(QuizResult.id).label('misses')
    ).filter(
        QuizResult.user_id == student.id,
        QuizResult.is_correct == False,
        QuizResult.timestamp >= cutoff
    ).group_by(QuizResult.word).order_by(db.desc('misses')).limit(10).all()

    struggling_words = [{'word': r[0], 'misses': int(r[1])} for r in struggling_rows]

    return render_template(
        'teacher/student_detail.html',
        student=student,
        avatar=avatar_data,
        total_quizzes=total_quizzes,
        avg_accuracy=round(float(avg_accuracy), 1) if avg_accuracy else 0.0,
        recent_sessions=recent_sessions,
        recent_speed=recent_speed,
        recent_achievements=recent_achievements,
        struggling_words=struggling_words
    )


# =============================
# Teacher Key Management API
# =============================

def _generate_unique_teacher_key(display_name: str) -> str:
    """Generate a unique teacher key and ensure no collision in DB."""
    # Reuse model's generator for consistency
    tmp_user = User(display_name=display_name or 'Teacher', username=f'_tmp_{uuid.uuid4()}', role='teacher')
    for _ in range(10):
        key = tmp_user.generate_teacher_key()
        # Collision check
        if not User.query.filter_by(teacher_key=key).first():
            return key
    # Worst-case: fall back to UUID segment
    return f"BEE-{datetime.utcnow().year}-AUTO-{str(uuid.uuid4())[:8].upper()}"


@app.route('/api/teacher/key', methods=['GET'])
@login_required
def api_get_teacher_key():
    """Return current user's teacher key (teachers/admins only)."""
    if current_user.role not in ['teacher', 'admin']:
        return jsonify({"success": False, "error": "Forbidden"}), 403
    return jsonify({
        "success": True,
        "teacher_key": current_user.teacher_key or ""
    })


@app.route('/api/teacher/key', methods=['POST'])
@login_required
def api_generate_teacher_key():
    """Create or regenerate a teacher key for the current user.

    - Teachers can generate their own key
    - Admins can optionally regenerate for a target teacher by username
    Body JSON: { target_username?: str, rotate?: bool }
    """
    if current_user.role not in ['teacher', 'admin']:
        return jsonify({"success": False, "error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    target_username = (data.get('target_username') or '').strip()

    try:
        _ensure_db_initialized()

        # Determine target user
        target_user = current_user
        if current_user.role == 'admin' and target_username:
            candidate = User.query.filter_by(username=target_username).first()
            if not candidate or candidate.role not in ['teacher', 'admin']:
                return jsonify({"success": False, "error": "Target must be a teacher or admin"}), 400
            target_user = candidate

        # Generate if missing or rotate on demand
        new_key = _generate_unique_teacher_key(target_user.display_name or 'Teacher')
        target_user.teacher_key = new_key
        db.session.commit()

        return jsonify({
            "success": True,
            "teacher_key": new_key,
            "owner": target_user.username
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"teacher key generation error: {e}")
        return jsonify({"success": False, "error": "Could not generate key. Try again."}), 500


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    # Get MY teacher key to find students/family under my supervision
    # (Admins use teacher_key field for tracking their students)
    my_key = current_user.teacher_key
    
    # Find all students who registered with MY teacher key
    # Use TeacherStudent link table to find students linked to this admin
    my_students = []
    if my_key:
        # Get student IDs from TeacherStudent link table
        student_links = TeacherStudent.query.filter_by(
            teacher_key=my_key,
            is_active=True
        ).all()
        
        # Get the actual user objects for these students (exclude guests)
        student_ids = [link.student_id for link in student_links]
        if student_ids:
            my_students = filter_non_guest_users(
                User.query.filter(User.id.in_(student_ids))
            ).order_by(User.created_at.desc()).all()
        
        # Double-check to filter out any remaining guests
        my_students = [student for student in my_students if not is_guest_user(student)]
        
        # Enrich student data with their stats
        for student in my_students:
            # Build a reusable query for sessions with actual activity
            session_q = QuizSession.query.filter_by(
                user_id=student.id
            ).filter(
                or_(
                    QuizSession.completed == True,
                    and_(
                        QuizSession.completed == False,
                        (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                    )
                )
            )

            # Count quizzes with activity (completed or in-progress with attempts)
            student.quiz_count = session_q.count()

            # Prefer robust counts from QuizSession aggregates to avoid gaps when QuizResult rows are missing
            from sqlalchemy import func
            total_correct = session_q.with_entities(func.coalesce(func.sum(QuizSession.correct_count), 0)).scalar() or 0
            total_incorrect = session_q.with_entities(func.coalesce(func.sum(QuizSession.incorrect_count), 0)).scalar() or 0

            student.correct_count = int(total_correct)
            student.words_practiced = int(total_correct + total_incorrect)

            # Accuracy for parent view should mirror the student's dashboard value
            # Use the stored per-session average_accuracy field for exact consistency
            try:
                student.accuracy = round(float(student.average_accuracy or 0.0), 1)
            except Exception:
                student.accuracy = round((student.correct_count / student.words_practiced) * 100, 1) if student.words_practiced > 0 else 0

            # Get latest quiz date (including incomplete sessions)
            latest_quiz = session_q.order_by(
                QuizSession.session_end.desc().nullslast(),
                QuizSession.session_start.desc()
            ).first()
            
            student.last_active = (
                latest_quiz.session_end if (latest_quiz and latest_quiz.session_end)
                else latest_quiz.session_start if (latest_quiz and latest_quiz.session_start)
                else student.created_at
            )
    
    # System-wide statistics (exclude guest users)
    stats = {
        'total_users': get_non_guest_users_query().count(),
        'total_students': filter_non_guest_users(User.query.filter_by(role='student')).count(),
        'total_teachers': filter_non_guest_users(User.query.filter_by(role='teacher')).count(),
        'total_quizzes': QuizSession.query.join(User).filter(
            and_(
                or_(
                    QuizSession.completed == True,
                    and_(
                        QuizSession.completed == False,
                        (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                    )
                ),
                # Exclude guest users from quiz counts
                not_(User.username.like('guest_%')),
                User.password_hash.isnot(None)
            )
        ).count(),
        'total_words_attempted': QuizResult.query.join(User).filter(
            and_(
                not_(User.username.like('guest_%')),
                User.password_hash.isnot(None)
            )
        ).count(),
        'my_students_count': len(my_students)
    }
    
    # Battle Bee Statistics - Query actual battle sessions
    try:
        total_battles = BattleSession.query.count()
        active_battles = BattleSession.query.filter(
            BattleSession.status.in_(['waiting', 'in_progress'])
        ).count()
        completed_battles = BattleSession.query.filter_by(status='completed').count()
    except Exception as e:
        print(f"Error loading battle stats: {e}")
        total_battles = 0
        active_battles = 0
        completed_battles = 0
    
    # Get top 10 players on the leaderboard (exclude guests)
    try:
        leaderboard = get_leaderboard_no_guests(10)
    except Exception as e:
        print(f"Error loading leaderboard: {e}")
        leaderboard = []
    
    # Enrich leaderboard with stats (battle stats placeholders until Battle models implemented)
    for idx, player in enumerate(leaderboard, start=1):
        player.rank = idx
        # Placeholder: battle stats not yet implemented
        player.total_battles_played = getattr(player, 'total_battles_played', 0)
        player.total_battles_won = getattr(player, 'total_battles_won', 0)
        player.win_rate = round((player.total_battles_won / player.total_battles_played * 100), 1) if player.total_battles_played > 0 else 0
        # Use total_lifetime_points as honey_points for now
        player.honey_points = getattr(player, 'honey_points', player.total_lifetime_points)
    
    battle_stats = {
        'total_battles': total_battles,
        'active_battles': active_battles,
        'completed_battles': completed_battles,
        'total_battle_participants': 0  # Placeholder until Battle models implemented
    }
    
    return render_template('admin/dashboard.html', 
                         user=current_user, 
                         stats=stats,
                         battle_stats=battle_stats,
                         leaderboard=leaderboard,
                         my_students=my_students,
                         admin_key=my_key)  # Pass teacher_key as admin_key for template


@app.route('/admin/battle-bees')
@login_required
def admin_battle_bees():
    """Admin Battle of the Bees detailed page"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    # Placeholder - Battle models not yet implemented
    all_battles = []
    
    # Get all potential battle participants (using quiz activity as proxy)
    # Note: Battle fields don't exist yet, using safe fallbacks
    battle_participants = User.query.filter(
        User.total_quizzes_completed > 0
    ).order_by(
        User.total_lifetime_points.desc()
    ).all()
    
    # Add placeholder battle stats to each participant
    for participant in battle_participants:
        participant.total_battles_played = getattr(participant, 'total_battles_played', 0)
        participant.total_battles_won = getattr(participant, 'total_battles_won', 0)
        participant.honey_points = getattr(participant, 'honey_points', participant.total_lifetime_points)
    
    # Get top 20 leaderboard (using lifetime points as proxy for honey points)
    leaderboard = User.query.filter(
        User.total_quizzes_completed > 0
    ).order_by(
        User.total_lifetime_points.desc(),
        User.total_quizzes_completed.desc(),
        User.created_at.asc()
    ).limit(20).all()
    
    # Enrich leaderboard with stats
    for idx, player in enumerate(leaderboard, start=1):
        player.rank = idx
        player.total_battles_played = getattr(player, 'total_battles_played', 0)
        player.total_battles_won = getattr(player, 'total_battles_won', 0)
        player.win_rate = round((player.total_battles_won / player.total_battles_played * 100), 1) if player.total_battles_played > 0 else 0
        player.honey_points = getattr(player, 'honey_points', player.total_lifetime_points)
    
    # Battle statistics (placeholder)
    battle_stats = {
        'total_battles': 0,
        'active_battles': 0,
        'completed_battles': 0,
        'total_participants': len(battle_participants),
        'total_honey_earned': sum(p.honey_points for p in battle_participants),
        'avg_battle_score': 0
    }
    
    # Get active battle codes (placeholder)
    active_battle_codes = []
    
    return render_template('admin/battle_bees.html',
                         user=current_user,
                         battles=all_battles,
                         battle_participants=battle_participants,
                         leaderboard=leaderboard,
                         battle_stats=battle_stats,
                         active_battle_codes=active_battle_codes)


@app.route('/admin/users')
@login_required
def admin_users():
    """Admin user management page"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin/users.html', user=current_user)


@app.route('/admin/user/<int:user_id>')
@login_required
def admin_user_detail(user_id):
    """Admin user detail page"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    # Get user details
    target_user = User.query.get_or_404(user_id)
    
    # Get user statistics (placeholder - UserStats model not yet implemented)
    stats = None
    
    # Get battle participation (placeholder - BattleParticipant model not yet implemented)
    battle_participations = []
    
    # Get recent quiz attempts (if we track them)
    # For now, we'll just show basic info
    
    return render_template('admin/user_detail.html', 
                         user=current_user,
                         target_user=target_user,
                         stats=stats,
                         battle_participations=battle_participations)


@app.route('/api/admin/users', methods=['GET'])
@login_required
def api_admin_get_users():
    """Get all users for admin management"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        users_data = []
        for user in users:
            # For students, check if they're linked to a teacher
            linked_teacher = None
            if user.role == 'student':
                teacher_link = TeacherStudent.query.filter_by(student_id=user.id).first()
                if teacher_link:
                    teacher = User.query.get(teacher_link.teacher_user_id)
                    if teacher:
                        linked_teacher = {
                            'id': teacher.id,
                            'username': teacher.username,
                            'display_name': teacher.display_name,
                            'teacher_key': teacher_link.teacher_key
                        }
            
            users_data.append({
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'role': user.role,
                'teacher_key': user.teacher_key,
                'linked_teacher': linked_teacher,  # New field for students
                'total_quizzes': user.total_quizzes_completed or 0,
                'total_lifetime_points': user.total_lifetime_points or 0,
                'average_accuracy': round(user.average_accuracy or 0, 1),
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return jsonify({
            "status": "success",
            "users": users_data,
            "total": len(users_data)
        })
    
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/fix-avatars', methods=['POST'])
@login_required
def api_admin_fix_avatars():
    """Admin endpoint to fix all avatar file references in database"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        from models import Avatar
        
        # Complete mapping for the 9 working avatars
        AVATAR_FIXES = {
            'al-bee': {'obj_file': 'AlBee.obj', 'mtl_file': 'AlBee.mtl', 'texture_file': 'AlBee.png', 'thumbnail_file': 'AlBee!.png'},
            'anxious-bee': {'obj_file': 'AnxiousBee.obj', 'mtl_file': 'AnxiousBee.mtl', 'texture_file': 'AnxiousBee.png', 'thumbnail_file': 'AnxiousBee!.png'},
            'mascot-bee': {'obj_file': 'MascotBee.obj', 'mtl_file': 'MascotBee.mtl', 'texture_file': 'MascotBee.png', 'thumbnail_file': 'MascotBee!.png'},
            'monster-bee': {'obj_file': 'MonsterBee.obj', 'mtl_file': 'MonsterBee.mtl', 'texture_file': 'MonsterBee.png', 'thumbnail_file': 'MonsterBee!.png'},
            'professor-bee': {'obj_file': 'ProfessorBee.obj', 'mtl_file': 'ProfessorBee.mtl', 'texture_file': 'ProfessorBee.png', 'thumbnail_file': 'ProfessorBee!.png'},
            'rocker-bee': {'obj_file': 'RockerBee.obj', 'mtl_file': 'RockerBee.mtl', 'texture_file': 'RockerBee.png', 'thumbnail_file': 'RockerBee!.png'},
            'vamp-bee': {'obj_file': 'VampBee.obj', 'mtl_file': 'VampBee.mtl', 'texture_file': 'VampBee.png', 'thumbnail_file': 'VampBee!.png'},
            'ware-bee': {'obj_file': 'WareBee.obj', 'mtl_file': 'WareBee.mtl', 'texture_file': 'WareBee.png', 'thumbnail_file': 'WareBee!.png'},
            'zom-bee': {'obj_file': 'ZomBee.obj', 'mtl_file': 'ZomBee.mtl', 'texture_file': 'ZomBee.png', 'thumbnail_file': 'ZomBee!.png'}
        }
        
        updated_avatars = []
        for slug, fixes in AVATAR_FIXES.items():
            avatar = Avatar.query.filter_by(slug=slug).first()
            if not avatar:
                continue
            
            # Update all file fields
            avatar.obj_file = fixes['obj_file']
            avatar.mtl_file = fixes['mtl_file']
            avatar.texture_file = fixes['texture_file']
            avatar.thumbnail_file = fixes['thumbnail_file']
            
            updated_avatars.append({
                'slug': slug,
                'name': avatar.name,
                'thumbnail': fixes['thumbnail_file']
            })
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"Successfully updated {len(updated_avatars)} avatars",
            "updated": updated_avatars
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error fixing avatars: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def api_admin_update_user(user_id):
    """Update user information"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'email' in data:
            user.email = data['email'] if data['email'] else None
        if 'role' in data and data['role'] in ['student', 'teacher', 'parent', 'admin', 'guest']:
            user.role = data['role']
        if 'teacher_key' in data:
            user.teacher_key = data['teacher_key'] if data['teacher_key'] else None
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "User updated successfully",
            "user": {
                'id': user.id,
                'display_name': user.display_name,
                'email': user.email,
                'role': user.role
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating user: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_admin_delete_user(user_id):
    """Delete a user and all associated data"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        return jsonify({"status": "error", "message": "Cannot delete your own account"}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        username = user.username
        
        # Delete associated data
        QuizSession.query.filter_by(user_id=user_id).delete()
        QuizResult.query.filter_by(user_id=user_id).delete()
        WordMastery.query.filter_by(user_id=user_id).delete()
        Achievement.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        print(f"🗑️ Admin {current_user.username} deleted user: {username} (ID: {user_id})")
        
        return jsonify({
            "status": "success",
            "message": f"User {username} deleted successfully"
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting user: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/bulk-delete', methods=['POST'])
@login_required
def api_admin_bulk_delete():
    """Delete multiple users at once"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        # Remove current user from list if present
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        
        if not user_ids:
            return jsonify({"status": "error", "message": "No valid users to delete"}), 400
        
        # Delete associated data for all users
        QuizSession.query.filter(QuizSession.user_id.in_(user_ids)).delete(synchronize_session=False)
        QuizResult.query.filter(QuizResult.user_id.in_(user_ids)).delete(synchronize_session=False)
        WordMastery.query.filter(WordMastery.user_id.in_(user_ids)).delete(synchronize_session=False)
        Achievement.query.filter(Achievement.user_id.in_(user_ids)).delete(synchronize_session=False)
        
        # Delete users
        deleted = User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        print(f"🗑️ Admin {current_user.username} bulk deleted {deleted} users")
        
        return jsonify({
            "status": "success",
            "message": f"Deleted {deleted} user(s)",
            "deleted_count": deleted
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error bulk deleting users: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/bulk-update-role', methods=['POST'])
@login_required
def api_admin_bulk_update_role():
    """Update role for multiple users"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        new_role = data.get('role')
        
        if not new_role or new_role not in ['student', 'teacher', 'parent', 'admin', 'guest']:
            return jsonify({"status": "error", "message": "Invalid role"}), 400
        
        # Remove current user from list
        user_ids = [uid for uid in user_ids if uid != current_user.id]
        
        if not user_ids:
            return jsonify({"status": "error", "message": "No valid users to update"}), 400
        
        # Update roles
        updated = User.query.filter(User.id.in_(user_ids)).update(
            {User.role: new_role},
            synchronize_session=False
        )
        db.session.commit()
        
        print(f"✏️ Admin {current_user.username} updated {updated} users to role: {new_role}")
        
        return jsonify({
            "status": "success",
            "message": f"Updated {updated} user(s) to {new_role}",
            "updated_count": updated
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error bulk updating roles: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/export', methods=['POST'])
@login_required
def api_admin_export_users():
    """Export selected users to CSV"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        import csv
        from io import StringIO
        
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else User.query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Username', 'Display Name', 'Email', 'Role', 'Teacher Key', 
                        'Total Quizzes', 'Lifetime Points', 'Avg Accuracy', 'Created At', 'Last Login'])
        
        # Data rows
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.display_name or '',
                user.email or '',
                user.role,
                user.teacher_key or '',
                user.total_quizzes_completed or 0,
                user.total_lifetime_points or 0,
                round(user.average_accuracy or 0, 1),
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=users_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'}
        )
    
    except Exception as e:
        print(f"❌ Error exporting users: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================

# ==============================================================================
# SPEED ROUND RAILWAY FIXES
# ==============================================================================

def railway_db_safe_speed_round(max_retries=3, backoff_factor=0.5):
    """
    Railway-safe database decorator for Speed Round operations
    Handles connection timeouts, recycling, and rollbacks
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Use fresh connection with shorter timeout
                    result = func(*args, **kwargs)
                    speed_logger.info(f"Speed Round DB operation successful: {func.__name__}")
                    return result
                    
                except (DisconnectionError, TimeoutError, OperationalError) as e:
                    retry_count += 1
                    wait_time = backoff_factor * (2 ** retry_count)
                    
                    speed_logger.warning(
                        f"Speed Round DB retry {retry_count}/{max_retries} for {func.__name__}: {e}"
                    )
                    
                    if retry_count >= max_retries:
                        speed_logger.error(
                            f"Speed Round DB failed after {max_retries} retries: {func.__name__}"
                        )
                        return None
                    
                    # Progressive backoff
                    time.sleep(wait_time)
                    
                except SQLAlchemyError as e:
                    speed_logger.error(f"Speed Round SQL Error in {func.__name__}: {e}")
                    return None
                    
                except Exception as e:
                    speed_logger.error(f"Speed Round Unexpected Error in {func.__name__}: {e}")
                    return None
            
            return None
        return wrapper
    return decorator

@railway_db_safe_speed_round()
def save_speed_round_score_railway(user_id, score_data):
    """
    Railway-safe speed round score saving with connection management
    """
    try:
        # Use direct SQL with explicit transaction management
        engine = db.get_engine()
        
        with engine.begin() as conn:  # Auto-commit transaction
            result = conn.execute(
                text("""
                    INSERT INTO speed_round_scores 
                    (user_id, words_attempted, words_correct, total_time, honey_points_earned, 
                     longest_streak, average_time_per_word, fastest_word_time, speed_bonuses_earned,
                     word_details, difficulty_level, created_at)
                    VALUES (:user_id, :words_attempted, :words_correct, :total_time, :honey_points_earned,
                            :longest_streak, :avg_time, :fastest_time, :speed_bonuses,
                            :word_details, :difficulty_level, :created_at)
                    RETURNING id
                """),
                {
                    'user_id': user_id,
                    'words_attempted': score_data.get('words_attempted', 0),
                    'words_correct': score_data.get('words_correct', 0),
                    'total_time': score_data.get('total_time', 0),
                    'honey_points_earned': score_data.get('honey_points_earned', 0),
                    'longest_streak': score_data.get('longest_streak', 0),
                    'avg_time': score_data.get('average_time_per_word', 0),
                    'fastest_time': score_data.get('fastest_word_time'),
                    'speed_bonuses': score_data.get('speed_bonuses_earned', 0),
                    'word_details': __import__('json').dumps(score_data.get('word_details', [])),
                    'difficulty_level': score_data.get('difficulty_level', 'unknown'),
                    'created_at': datetime.utcnow()
                }
            )
            
            score_id = result.fetchone()[0]
            speed_logger.info(f"Speed Round score saved: user_id={user_id}, score_id={score_id}")
            return score_id
            
    except Exception as e:
        speed_logger.error(f"Failed to save speed round score: {e}")
        return None

@railway_db_safe_speed_round()
def update_user_lifetime_points_railway(user_id, points_to_add):
    """
    Railway-safe user lifetime points update
    """
    try:
        engine = db.get_engine()
        
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE users 
                    SET total_lifetime_points = COALESCE(total_lifetime_points, 0) + :points
                    WHERE id = :user_id
                """),
                {'user_id': user_id, 'points': points_to_add}
            )
            
            speed_logger.info(f"Updated user {user_id} lifetime points: +{points_to_add}")
            return True
            
    except Exception as e:
        speed_logger.error(f"Failed to update user lifetime points: {e}")
        return False

# ==============================================================================
# END SPEED ROUND RAILWAY FIXES
# ==============================================================================


# SPEED ROUND API ENDPOINTS
# ============================================================================

@app.route("/speed-round/setup")
def speed_round_setup():
    """Speed round configuration page"""
    timestamp = int(time.time())
    return render_template('speed_round_setup.html', timestamp=timestamp)


@app.route("/speed-round/quiz")
def speed_round_quiz():
    """Speed round quiz page with timer"""
    # Check if round is active
    if 'speed_round' not in session or not session.get('speed_round', {}).get('active'):
        flash('Please start a speed round first!', 'warning')
        return redirect(url_for('speed_round_setup'))
    
    timestamp = int(time.time())
    return render_template('speed_round_quiz.html', timestamp=timestamp)


@app.route("/api/speed-round/next", methods=["GET"])
def api_speed_round_next():
    """Get the next word in the speed round"""
    try:
        if 'speed_round' not in session:
            return jsonify({'error': 'No active speed round'}), 400
        
        round_data = session['speed_round']
        
        if not round_data.get('active'):
            return jsonify({'error': 'Speed round not active'}), 400
        
        current_index = round_data.get('current_index', 0)
        words = round_data.get('words', [])
        
        # Check if round is complete
        if current_index >= len(words):
            return jsonify({'complete': True})
        
        # Get current word (can be string or dict)
        word_data = words[current_index]

        # Handle both string and dict formats
        if isinstance(word_data, dict):
            word_spelling = word_data.get('word', '')
            sentence_text = (word_data.get('sentence') or '').strip()
            hint_text = (word_data.get('hint') or '').strip()
            # Prefer sentence, then hint; otherwise generate a smart fallback
            if sentence_text:
                definition = _blank_word(sentence_text, word_spelling)
            elif hint_text:
                definition = f"Hint: {_blank_word(hint_text, word_spelling)}"
            else:
                # Use dictionary pipeline smart fallback
                definition = get_word_info(word_spelling)
        else:
            # word_data is a string
            word_spelling = word_data
            # No metadata; use dictionary pipeline to get a kid-friendly, blanked definition
            definition = get_word_info(word_spelling)
            sentence_text = ''
            hint_text = ''
        
        # Return word info (without revealing the spelling)
        return jsonify({
            'complete': False,
            'word': word_spelling,  # spelling string for TTS only; UI must not reveal
            'definition': definition,
            'sentence': sentence_text if 'sentence_text' in locals() else '',
            'hint': hint_text if 'hint_text' in locals() else '',
            'current_index': current_index + 1,  # 1-based for display
            'total_words': len(words),
            'time_per_word': round_data.get('config', {}).get('time_per_word', 10),
            'current_streak': round_data.get('current_streak', 0),
            'total_points': round_data.get('total_points', 0)
        })
    
    except Exception as e:
        print(f"Error in api_speed_round_next: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route("/api/speed-round/start", methods=["POST"])
def api_speed_round_start():
    """Initialize a speed round with configuration"""
    try:
        data = request.get_json()
        
        # Extract configuration
        time_per_word = data.get('time_per_word', 15)
        difficulty = data.get('difficulty', 'grade_3_4')
        word_count = data.get('word_count', 20)
        word_source = data.get('word_source', 'auto')
        
        # Generate or fetch words
        if word_source == 'auto':
            words = generate_words_by_difficulty(difficulty, count=word_count)
        elif word_source == 'uploaded':
            # Get user's uploaded word list
            wordbank = get_wordbank()
            if not wordbank or len(wordbank) == 0:
                return jsonify({
                    'status': 'error',
                    'message': 'No uploaded word list found. Please upload words first or use auto-generate.'
                }), 400
            
            # Extract just the word strings
            words = [item['word'] for item in wordbank]
            random.shuffle(words)
            words = words[:word_count]  # Take only requested count
        elif word_source == 'mixed':
            words = generate_mixed_words(count=word_count)
        else:
            words = generate_words_by_difficulty('grade_3_4', count=word_count)
        
        # Store speed round state in session
        session['speed_round'] = {
            'active': True,  # Mark round as active
            'words': words,
            'config': {
                'time_per_word': time_per_word,
                'difficulty': difficulty,
                'word_count': word_count,
                'word_source': word_source,
                'multiplier': get_difficulty_multiplier(difficulty)
            },
            'start_time': time.time(),
            'current_index': 0,
            'correct_count': 0,
            'current_streak': 0,  # Use current_streak for consistency
            'max_streak': 0,
            'total_points': 0,
            'speed_bonuses': 0,
            'word_history': []  # Track each word's performance
        }
        
        print(f"🎯 Speed Round started: {len(words)} words, {difficulty}, {time_per_word}s/word")
        
        return jsonify({
            'status': 'success',
            'word_count': len(words),
            'first_word': words[0] if words else None
        })
        
    except Exception as e:
        print(f"❌ Error starting speed round: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/speed-round/answer", methods=["POST"])
def api_speed_round_answer():
    """Process speed round answer with timing and scoring"""
    try:
        data = request.get_json()
        speed_round = session.get('speed_round')
        
        if not speed_round:
            return jsonify({'error': 'No active speed round found'}), 400
        
        # Get current word and user answer
        current_index = speed_round['current_index']
        words = speed_round['words']
        
        if current_index >= len(words):
            return jsonify({'complete': True})
        
        current_word_data = words[current_index]
        correct_spelling = current_word_data.get('word', current_word_data) if isinstance(current_word_data, dict) else current_word_data
        user_input = data.get('user_input', '').strip()
        elapsed_ms = data.get('elapsed_ms', 0)
        is_skipped = data.get('skipped', False)
        
        time_taken = elapsed_ms / 1000.0  # Convert to seconds
        time_limit = speed_round['config']['time_per_word']
        
        # Check if correct (normalize for comparison)
        is_correct = normalize(user_input) == normalize(correct_spelling) if not is_skipped else False
        
        # Calculate points
        points_earned = 0
        speed_bonus = False
        
        if is_correct:
            base_points = 10
            multiplier = speed_round['config']['multiplier']
            
            # Speed bonus (answered in < 50% of time limit)
            if time_taken < (time_limit * 0.5):
                base_points += 5
                speed_bonus = True
                speed_round['speed_bonuses'] += 1
            
            # Streak bonus
            speed_round['current_streak'] += 1
            streak_bonus = speed_round['current_streak'] * 2
            
            # Update max streak
            if speed_round['current_streak'] > speed_round['max_streak']:
                speed_round['max_streak'] = speed_round['current_streak']
            
            # Calculate total points with multiplier
            points_earned = int((base_points + streak_bonus) * multiplier)
            speed_round['total_points'] += points_earned
            speed_round['correct_count'] += 1
            
            print(f"✅ Correct! '{correct_spelling}' - {points_earned} pts (streak: {speed_round['current_streak']})")
        else:
            # Reset streak on wrong answer
            speed_round['current_streak'] = 0
            print(f"❌ Wrong! '{user_input}' != '{correct_spelling}'")
        
        # Record this word's performance
        word_record = {
            'word': correct_spelling,
            'user_answer': user_input,
            'correct': is_correct,
            'skipped': is_skipped,
            'time_taken': round(time_taken, 2),
            'points_earned': points_earned,
            'speed_bonus': speed_bonus,
            'streak_at_time': speed_round['current_streak']
        }
        speed_round['word_history'].append(word_record)
        
        # Move to next word
        speed_round['current_index'] += 1
        
        # Check if round is complete
        is_complete = speed_round['current_index'] >= len(words)
        
        # Update session
        session['speed_round'] = speed_round
        session.modified = True
        
        return jsonify({
            'is_correct': is_correct,
            'correct_spelling': correct_spelling,
            'points_earned': points_earned,
            'speed_bonus': speed_bonus,
            'total_points': speed_round['total_points'],
            'current_streak': speed_round['current_streak'],
            'time_taken': round(time_taken, 2),
            'complete': is_complete
        })
        
    except Exception as e:
        print(f"❌ Error processing answer: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route("/api/speed-round/complete", methods=["POST"])
@login_required
def api_speed_round_complete():
    """Save speed round results to database - Railway-safe version"""
    try:
        speed_round = session.get('speed_round')
        
        if not speed_round:
            return jsonify({
                'status': 'error',
                'message': 'No speed round data found'
            }), 400
        
        # Mark round as inactive
        speed_round['active'] = False
        
        # Calculate statistics
        total_time = time.time() - speed_round['start_time']
        words_attempted = speed_round['current_index']
        words_correct = speed_round['correct_count']
        
        # Find fastest correct word time
        fastest_time = None
        for record in speed_round['word_history']:
            if record['correct'] and record['time_taken'] > 0:
                if fastest_time is None or record['time_taken'] < fastest_time:
                    fastest_time = record['time_taken']
        
        avg_time = total_time / words_attempted if words_attempted > 0 else 0
        accuracy = (words_correct / words_attempted * 100) if words_attempted > 0 else 0
        
        # Prepare score data for Railway-safe saving
        score_data = {
            'words_attempted': words_attempted,
            'words_correct': words_correct,
            'total_time': round(total_time, 2),
            'honey_points_earned': speed_round['total_points'],
            'longest_streak': speed_round['max_streak'],
            'average_time_per_word': round(avg_time, 2),
            'fastest_word_time': round(fastest_time, 2) if fastest_time else None,
            'speed_bonuses_earned': speed_round['speed_bonuses'],
            'word_details': speed_round['word_history'],
            'difficulty_level': speed_round['config']['difficulty']
        }
        
        # Use Railway-safe database operations
        score_id = save_speed_round_score_railway(current_user.id, score_data)
        
        if score_id:
            # Update user's total points using Railway-safe method
            points_updated = update_user_lifetime_points_railway(current_user.id, speed_round['total_points'])
            
            speed_logger.info(f"Speed Round saved: {words_correct}/{words_attempted} correct, {speed_round['total_points']} pts, points_updated={points_updated}")
        else:
            speed_logger.error("Failed to save Speed Round score")
        
        # Collect incorrect words for review
        incorrect_words = []
        for record in speed_round['word_history']:
            if not record['correct'] and not record.get('skipped', False):
                incorrect_words.append({
                    'word': record['word'],
                    'user_answer': record.get('user_answer', ''),
                    'correct_spelling': record['word']
                })
        
        # Store results in session for results page
        session['speed_round_results'] = {
            'score_id': score_id,
            'total_points': speed_round['total_points'],
            'words_attempted': words_attempted,
            'words_correct': words_correct,
            'accuracy': round(accuracy, 1),
            'longest_streak': speed_round['max_streak'],
            'fastest_time': round(fastest_time, 2) if fastest_time else None,
            'total_time': round(total_time, 2),
            'speed_bonuses': speed_round['speed_bonuses'],
            'difficulty': speed_round['config']['difficulty'],
            'config': speed_round['config'],
            'incorrect_words': incorrect_words
        }
        
        # Clear speed round from session
        session.pop('speed_round', None)
        
        return jsonify({
            'status': 'success',
            'score_id': score_id,
            'statistics': session['speed_round_results'],
            'railway_optimized': True
        })
        
    except Exception as e:
        speed_logger.error(f"Error saving speed round: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'railway_error': True
        }), 500


@app.route("/speed-round/results")
@login_required
def speed_round_results():
    """Speed round results page"""
    results = session.get('speed_round_results')
    
    if not results:
        flash('No results found. Please complete a speed round first!', 'warning')
        return redirect(url_for('speed_round_setup'))
    
    timestamp = int(time.time())
    return render_template('speed_round_results.html', results=results, timestamp=timestamp)


# --- 3D Avatar API Routes ----------------------------------------------------
@app.route("/api/avatars", methods=["GET"])
def api_get_avatars():
    """Get the complete avatar catalog with optional filtering, plus canonical asset URLs"""
    try:
        from models import Avatar
        
        # Check if Avatar table exists and is populated
        try:
            # Test query to check if table exists
            avatar_count = Avatar.query.count()
            
            # If table is empty, populate it from filesystem
            if avatar_count == 0:
                print("📦 Avatar table is empty, populating from filesystem...")
                from migrate_avatars_to_db import populate_avatars_from_filesystem
                # We're already in app context since this is a route handler
                populated_count = populate_avatars_from_filesystem()
                print(f"✅ Populated {populated_count} avatars from filesystem")
                
        except Exception as table_error:
            print(f"⚠️ Avatar table doesn't exist, creating now: {table_error}")
            # Create all tables (safe operation - won't affect existing tables)
            db.create_all()
            print("✅ Database tables created")
            
            # Populate avatars
            print("📦 Populating avatar database from filesystem...")
            from migrate_avatars_to_db import populate_avatars_from_filesystem
            # We're already in app context since this is a route handler
            populated_count = populate_avatars_from_filesystem()
            print(f"✅ Populated {populated_count} avatars")
        
        # Check if filtering by category or search
        category = request.args.get('category')
        search_query = request.args.get('search')

        # Query database for avatars
        query = Avatar.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    Avatar.name.ilike(search_pattern),
                    Avatar.description.ilike(search_pattern),
                    Avatar.slug.ilike(search_pattern)
                )
            )
        
        avatars = query.order_by(Avatar.sort_order, Avatar.name).all()

        # Enrich each avatar with thumbnail/preview and canonical 3D asset URLs
        enriched_avatars = []
        for avatar in avatars:
            avatar_id = avatar.slug
            base_path = f"/static/assets/avatars/{avatar.folder_path}"
            
            # Build enriched avatar dict with all URLs
            enriched = {
                'id': avatar_id,
                'name': avatar.name,
                'description': avatar.description,
                'category': avatar.category,
                'folder': avatar.folder_path,
                
                # Legacy flat fields for thumbnails (kept for backward compatibility)
                'thumbnail': f"{base_path}/{avatar.thumbnail_file}",
                'preview': f"{base_path}/{avatar.thumbnail_file}",
                
                # Canonical URLs bundle expected by front-end picker and validation scripts
                'urls': {
                    'model_obj': f"{base_path}/{avatar.obj_file}",
                    'model_mtl': f"{base_path}/{avatar.mtl_file}" if avatar.mtl_file else None,
                    'texture': f"{base_path}/{avatar.texture_file}" if avatar.texture_file else None,
                    'thumbnail': f"{base_path}/{avatar.thumbnail_file}",
                    'preview': f"{base_path}/{avatar.thumbnail_file}",
                },
                
                # Additional metadata
                'unlock_level': avatar.unlock_level,
                'points_required': avatar.points_required,
                'is_premium': avatar.is_premium,
            }

            enriched_avatars.append(enriched)

        return jsonify({
            'status': 'success',
            'avatars': enriched_avatars,
            'total': len(enriched_avatars)
        })

    except Exception as e:
        import traceback
        print(f"❌ Error fetching avatars: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        }), 500

@app.route("/api/speed-round/health")
def speed_round_health_railway():
    """Speed Round system health check for Railway"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'Railway' if (os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL')) else 'Local',
        'speed_round_status': 'checking',
        'database_status': 'checking',
        'session_status': 'checking'
    }
    
    try:
        # Test database connection with timeout
        engine = db.get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                health['database_status'] = 'operational'
            else:
                health['database_status'] = 'degraded'
        
        # Test session functionality
        health['session_status'] = 'operational'
        
        # Test Speed Round table access
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM speed_round_scores LIMIT 1"))
                health['speed_round_table'] = 'accessible'
        except:
            health['speed_round_table'] = 'inaccessible'
        
        # Overall status
        if (health['database_status'] == 'operational' and 
            health['session_status'] == 'operational' and
            health['speed_round_table'] == 'accessible'):
            health['speed_round_status'] = 'operational'
        else:
            health['speed_round_status'] = 'degraded'
        
        speed_logger.info(f"Speed Round health check: {health['speed_round_status']}")
        
    except Exception as e:
        health['speed_round_status'] = 'failed'
        health['database_status'] = 'failed'
        health['error'] = str(e)
        speed_logger.error(f"Speed Round health check failed: {e}")
    
    return jsonify(health)


@app.route("/api/avatar/<avatar_id>", methods=["GET"])
def api_get_avatar(avatar_id):
    """Get information for a specific avatar"""
    try:
        from models import Avatar
        
        # Query database for avatar
        avatar = Avatar.get_by_slug(avatar_id)
        
        if not avatar:
            return jsonify({
                'status': 'error',
                'message': f'Avatar not found: {avatar_id}'
            }), 404
        
        # Build avatar info dict with all URLs
        base_path = f"/static/assets/avatars/{avatar.folder_path}"
        avatar_info = {
            'id': avatar.slug,
            'name': avatar.name,
            'description': avatar.description,
            'variant': 'default',
            'category': avatar.category,
            'thumbnail_url': f"{base_path}/{avatar.thumbnail_file}",
            'preview_url': f"{base_path}/{avatar.thumbnail_file}",
            'model_obj_url': f"{base_path}/{avatar.obj_file}",
            'model_mtl_url': f"{base_path}/{avatar.mtl_file}" if avatar.mtl_file else None,
            'texture_url': f"{base_path}/{avatar.texture_file}" if avatar.texture_file else None,
            'fallback_url': "/static/assets/avatars/fallback.png",
            'unlock_level': avatar.unlock_level,
            'points_required': avatar.points_required,
            'is_premium': avatar.is_premium
        }
        
        return jsonify({
            'status': 'success',
            'avatar': avatar_info
        })
    
    except Exception as e:
        print(f"❌ Error fetching avatar {avatar_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/avatars/categories", methods=["GET"])
def api_get_avatar_categories():
    """Get avatars grouped by category"""
    try:
        from models import Avatar
        
        # Query all active avatars
        avatars = Avatar.query.filter_by(is_active=True).order_by(Avatar.sort_order, Avatar.name).all()
        
        # Group by category
        categories = {}
        for avatar in avatars:
            cat = avatar.category
            if cat not in categories:
                categories[cat] = []
            
            base_path = f"/static/assets/avatars/{avatar.folder_path}"
            categories[cat].append({
                'id': avatar.slug,
                'name': avatar.name,
                'description': avatar.description,
                'category': avatar.category,
                'folder': avatar.folder_path,
                'thumbnail': f"{base_path}/{avatar.thumbnail_file}",
                'unlock_level': avatar.unlock_level,
                'points_required': avatar.points_required,
                'is_premium': avatar.is_premium
            })
        
        return jsonify({
            'status': 'success',
            'categories': categories
        })
    
    except Exception as e:
        print(f"❌ Error fetching avatar categories: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/users/<int:user_id>/avatar", methods=["GET"])
@login_required
def api_get_user_avatar(user_id):
    """Get a user's current avatar"""
    try:
        # Check permission - users can only view their own avatar unless admin
        if current_user.id != user_id and current_user.role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        avatar_data = user.get_avatar_data()
        # Decide whether UI should render mascot (default) or the user's 3D avatar
        use_mascot = not user.has_selected_avatar()
        
        return jsonify({
            'status': 'success',
            'avatar': avatar_data,
            'use_mascot': use_mascot
        })
    
    except Exception as e:
        print(f"❌ Error fetching user avatar: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/users/<int:user_id>/avatar", methods=["PUT"])
@login_required
def api_update_user_avatar(user_id):
    """Update a user's avatar"""
    try:
        # Check permission - users can only update their own avatar
        if current_user.id != user_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        avatar_id = data.get('avatar_id')
        variant = data.get('variant', 'male')
        
        if not avatar_id:
            return jsonify({
                'status': 'error',
                'message': 'avatar_id is required'
            }), 400
        
        # Update avatar
        success, message = user.update_avatar(avatar_id, variant)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        # Mark avatar as explicitly selected after update
        try:
            prefs = user.preferences or {}
            prefs['avatar_selected'] = True
            user.preferences = prefs
        except Exception:
            pass

        db.session.commit()

        # Get updated avatar data
        avatar_data = user.get_avatar_data()
        use_mascot = not user.has_selected_avatar()

        print(f"🐝 User {user.username} updated avatar to {avatar_id} ({variant})")

        return jsonify({
            'status': 'success',
            'message': message,
            'avatar': avatar_data,
            'use_mascot': use_mascot
        })
    
    except Exception as e:
        print(f"❌ Error updating user avatar: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/users/me", methods=["GET"])
def api_get_current_user():
    """Get current user's basic information (name, auth status, etc.)"""
    try:
        # Check if user is authenticated
        if current_user.is_authenticated:
            return jsonify({
                'status': 'success',
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'display_name': current_user.display_name,
                    'email': current_user.email if hasattr(current_user, 'email') else None,
                    'role': current_user.role if hasattr(current_user, 'role') else 'student'
                }
            })
        else:
            # Guest user
            return jsonify({
                'status': 'success',
                'authenticated': False,
                'user': {
                    'display_name': 'NewBee',
                    'role': 'guest'
                }
            })
    except Exception as e:
        print(f"❌ Error fetching current user: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user information',
            'authenticated': False,
            'user': {
                'display_name': 'NewBee',
                'role': 'guest'
            }
        }), 500


@app.route("/api/users/me/avatar", methods=["GET"])
def api_get_my_avatar():
    """Get current user's avatar (works for both authenticated and guest users)"""
    try:
        # Try to get authenticated user first
        if current_user.is_authenticated:
            user = current_user
        else:
            # Fall back to guest user
            user = get_or_create_guest_user()
        
        if not user:
            # No user found, return default mascot
            return jsonify({
                'status': 'success',
                'avatar': {
                    'avatar_id': 'mascot-bee',
                    'variant': 'default',
                    'name': 'MascotBee',
                    'urls': {
                        'model_obj': '/static/assets/avatars/mascot-bee/MascotBee.obj',
                        'model_mtl': '/static/assets/avatars/mascot-bee/MascotBee.mtl',
                        'texture': '/static/assets/avatars/mascot-bee/MascotBee.png',
                        'thumbnail': '/static/assets/avatars/mascot-bee/MascotBee!.png'
                    }
                },
                'use_mascot': True
            })
        
        # Check if user has explicitly selected an avatar
        use_mascot = not user.has_selected_avatar()
        
        # If user hasn't selected an avatar, return MascotBee as default
        if use_mascot:
            return jsonify({
                'status': 'success',
                'avatar': {
                    'avatar_id': 'mascot-bee',
                    'variant': 'default',
                    'name': 'MascotBee',
                    'urls': {
                        'model_obj': '/static/assets/avatars/mascot-bee/MascotBee.obj',
                        'model_mtl': '/static/assets/avatars/mascot-bee/MascotBee.mtl',
                        'texture': '/static/assets/avatars/mascot-bee/MascotBee.png',
                        'thumbnail': '/static/assets/avatars/mascot-bee/MascotBee!.png'
                    }
                },
                'use_mascot': True
            })
        
        # User has selected an avatar, return their choice
        avatar_data = user.get_avatar_data()
        return jsonify({
            'status': 'success',
            'avatar': avatar_data,
            'use_mascot': False
        })
    
    except Exception as e:
        print(f"❌ Error fetching user avatar: {e}")
        # Return default mascot on error
        return jsonify({
            'status': 'success',
            'avatar': {
                'avatar_id': 'mascot-bee',
                'variant': 'default',
                'name': 'MascotBee',
                'urls': {
                    'model_obj': '/static/assets/avatars/mascot-bee/MascotBee.obj',
                    'model_mtl': '/static/assets/avatars/mascot-bee/MascotBee.mtl',
                    'texture': '/static/assets/avatars/mascot-bee/MascotBee.png',
                    'thumbnail': '/static/assets/avatars/mascot-bee/MascotBee!.png'
                }
            },
            'use_mascot': True
        })


@app.route("/api/users/me/avatar", methods=["PUT"])
@login_required
def api_update_my_avatar():
    """Update current user's avatar (convenience endpoint)"""
    return api_update_user_avatar(current_user.id)


@app.route("/api/users/<int:user_id>/avatar/lock", methods=["POST"])
@login_required
def api_lock_avatar(user_id):
    """Lock avatar changes (parental control)"""
    try:
        # Only parents/teachers/admins can lock avatars
        if current_user.role not in ['parent', 'teacher', 'admin']:
            return jsonify({
                'status': 'error',
                'message': 'Only parents, teachers, or admins can lock avatars'
            }), 403
        
        # Parents/teachers can only lock their linked students
        if current_user.role in ['parent', 'teacher']:
            link = TeacherStudent.query.filter_by(
                teacher_key=current_user.teacher_key,
                student_id=user_id
            ).first()
            
            if not link:
                return jsonify({
                    'status': 'error',
                    'message': 'You can only lock avatars for your linked students'
                }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user.avatar_locked = True
        db.session.commit()
        
        print(f"🔒 Avatar locked for user {user.username} by {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'Avatar locked successfully'
        })
    
    except Exception as e:
        print(f"❌ Error locking avatar: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/users/<int:user_id>/avatar/unlock", methods=["POST"])
@login_required
def api_unlock_avatar(user_id):
    """Unlock avatar changes (parental control)"""
    try:
        # Only parents/teachers/admins can unlock avatars
        if current_user.role not in ['parent', 'teacher', 'admin']:
            return jsonify({
                'status': 'error',
                'message': 'Only parents, teachers, or admins can unlock avatars'
            }), 403
        
        # Parents/teachers can only unlock their linked students
        if current_user.role in ['parent', 'teacher']:
            link = TeacherStudent.query.filter_by(
                teacher_key=current_user.teacher_key,
                student_id=user_id
            ).first()
            
            if not link:
                return jsonify({
                    'status': 'error',
                    'message': 'You can only unlock avatars for your linked students'
                }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user.avatar_locked = False
        db.session.commit()
        
        print(f"🔓 Avatar unlocked for user {user.username} by {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'Avatar unlocked successfully'
        })
    
    except Exception as e:
        print(f"❌ Error unlocking avatar: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Startup confirmation logging
print("=" * 60)
print("🐝 BeeSmart Spelling Bee App - Initialization Complete")
print("=" * 60)
print(f"✅ App version: 1.6")
print(f"✅ Environment: {os.environ.get('FLASK_ENV', 'development')}")
print(f"✅ Database: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
print(f"✅ Sessions: {'Database (persistent)' if SESSION_INIT_SUCCESS else 'Filesystem (temporary)'}")
print(f"✅ Dictionary cache: {len(DICTIONARY_CACHE.get('words', {}))} words loaded")
print(f"✅ Health check endpoint: /health")
print(f"✅ Ready to serve requests on port ${os.environ.get('PORT', '5000')}")
print("=" * 60)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting development server on port {port} with Socket.IO support...")
    try:
        from app_socketio import socketio
        socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"⚠️ Failed to start with Socket.IO: {e}")
        print("🔄 Falling back to standard Flask server...")
        app.run(host="0.0.0.0", port=port, debug=True)
