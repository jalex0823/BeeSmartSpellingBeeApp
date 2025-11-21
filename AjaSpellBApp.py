HOME_PREVIEW_ENABLED = True  # feature flag for new honey home page preview
# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import csv
import os
import shutil
import re
import json
import time
import random
import threading
import uuid
import logging
from datetime import datetime, timedelta, timezone
import socket
import secrets
import hashlib
from typing import List, Dict, Optional
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file, Response, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from PIL import Image
from sqlalchemy import inspect, exc as sa_exc, or_, and_, not_, text
from sqlalchemy.exc import DisconnectionError, OperationalError, SQLAlchemyError

# Database imports
from config import get_config
from models import db, User, QuizSession, QuizResult, WordMastery, TeacherStudent, Achievement
from models import WordList, WordListItem
from models import PasswordResetToken
from models import SessionLog
from models import SpeedRoundConfig, SpeedRoundScore
from models import Avatar, BattleSession, PurchaseRecord, BundleKey, DynamicBundle, BundleKeyRedemption
from avatar_skus import AVATAR_SKUS, build_product_entitlements  # Avatar monetization mapping
try:
    from avatar_bundles import BUNDLE_CATALOG, REDEEMABLE_KEYS  # Optional: bundle catalog + redeemable keys
except Exception:
    BUNDLE_CATALOG = {}
    REDEEMABLE_KEYS = {}

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

# Fast-boot mode: skip heavy startup checks/initializers that can delay first load
# Default is OFF to run full system checks prior to entering the home page.
FAST_BOOT = os.getenv('FAST_BOOT', '0').strip().lower() in ('1', 'true', 'yes', 'on')
if FAST_BOOT:
    print("⚡ FAST_BOOT=on → Skipping heavy startup checks to unblock app load")
else:
    print("⚙️ FAST_BOOT=off → Running full startup checks")

# ✅ BUILT-IN DICTIONARY ONLY - External API removed for performance
# No external dictionary_api imports - we use Simple Wiktionary (50K+ words)
print("📚 Using built-in Simple English Wiktionary (50K+ words, kid-friendly)")


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
                    except Exception:
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

# ------------------------------
# Public policy pages
# ------------------------------

# Ensure Flask app object exists before any route decorators are applied
# Some routes are defined early in this module; define `app` up-front to avoid NameError at import time.
print("🔧 Creating Flask app (early)...")
try:
    app  # type: ignore[name-defined]
except NameError:
    app = Flask(__name__)

# Reliable, post-app-creation lightweight routes
@app.route('/')
def home_root_direct():
    """Primary application landing page: shows loader then auto-redirects to app."""
    return render_template('unified_menu.html')

# Optional legacy preview alias retained (can be removed later)
@app.route('/home_preview')
def home_preview():
    return render_template('honey_home.html')


@app.route('/points-buzz-dust-explanation')
def points_buzz_dust_explanation():
    """Show Points vs Buzz Dust explanation screen"""
    try:
        from buzz_dust_helpers import get_all_bee_classes
        bee_classes = get_all_bee_classes()
        return render_template('points_buzz_dust_explanation.html', bee_classes=bee_classes)
    except Exception as e:
        print(f"Error loading explanation page: {e}")
        # Fallback with minimal data
        return render_template('points_buzz_dust_explanation.html', bee_classes=[])


def _safe_template(name):
    """Small helper to render a template if present without crashing the app."""
    try:
        return render_template(name)
    except Exception:
        # Minimal inline fallback so /privacy never 500s even if template missing
        return "<html><head><meta charset='utf-8'><title>Privacy Policy</title></head><body><h1>Privacy Policy</h1><p>BeeSmart Spelling Bee privacy policy.</p></body></html>"


@app.route("/privacy")
def privacy_page():
    """Public privacy policy page required for Play Console disclosures."""
    return _safe_template("privacy.html")

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

# Dictionary cache - loaded on-demand by get_word_info(), not at startup
DICTIONARY_CACHE = {}

# In-memory acceleration structures
from collections import OrderedDict
WORD_INFO_CACHE_MAX = 3000  # soft cap for LRU
WORD_INFO_CACHE = OrderedDict()  # LRU of formatted definition sentences
SIMPLE_WIKTIONARY_INDEX = None  # set of lowercase words for O(1) membership
_WORD_INFO_HITS = 0
_WORD_INFO_MISSES = 0

# Simple English Wiktionary - Lazy load on first use (for Random Word feature)
# This improves Railway startup time by ~2-3 seconds
SIMPLE_WIKTIONARY = None  # Loaded on-demand when random words are requested
SIMPLE_WIKTIONARY_LOADED = False

def ensure_simple_wiktionary_loaded():
    """
    Lazy-load Simple Wiktionary only when needed.
    This prevents blocking Railway app startup with 50K+ word dictionary load.
    """
    global SIMPLE_WIKTIONARY, SIMPLE_WIKTIONARY_LOADED, SIMPLE_WIKTIONARY_INDEX
    
    if SIMPLE_WIKTIONARY_LOADED:
        return SIMPLE_WIKTIONARY
    
    print("📚 Loading Simple English Wiktionary on-demand (first use)...")
    SIMPLE_WIKTIONARY = load_simple_wiktionary()
    SIMPLE_WIKTIONARY_LOADED = True
    # Build fast index (lowercase keys already) for O(1) membership checks
    try:
        SIMPLE_WIKTIONARY_INDEX = set(SIMPLE_WIKTIONARY.keys())
        print(f"✅ Simple Wiktionary loaded: {len(SIMPLE_WIKTIONARY):,} words ready (index built)")
    except Exception as _idx_err:
        SIMPLE_WIKTIONARY_INDEX = None
        print(f"⚠️ Failed building wiktionary index: {_idx_err}")
    return SIMPLE_WIKTIONARY

print("✅ Dictionary resources initialized (on-demand loading enabled)")

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

# ----------------------------------------------------------------------------
# In-App Purchases (Apple/Google) – server-side verification stubs and mapping
# ----------------------------------------------------------------------------

IAP_MOCK_MODE = os.getenv('IAP_MOCK', '1') in ('1', 'true', 'True', 'yes')
IAP_VERIFICATION_MODE = os.getenv('IAP_VERIFICATION_MODE', 'mock' if IAP_MOCK_MODE else 'live_strict').strip().lower()

# Subscription Product IDs (for App Store Connect)
SUBSCRIPTION_PRODUCT_IDS = {
    'monthly': 'beesmart.premium.monthly',      # $4.99/month
    'yearly': 'beesmart.premium.yearly',        # $39.99/year (Save 33%)
    'family': 'beesmart.premium.family.monthly', # $7.99/month (Up to 6 members)
    'legacy': 'beesmart.sub.full_monthly'       # Legacy subscription (backward compatibility)
}

# Product -> entitlement mapping (override via env if needed)
PRODUCT_MAP = {
    # Full unlock (premium membership - one-time purchase)
    os.getenv('PRODUCT_FULL_UNLOCK_ID', 'beesmart.full_unlock'): {
        'type': 'premium'
    },
    # SUBSCRIPTION TIERS (Auto-Renewable)
    # Legacy subscription (kept for backward compatibility)
    os.getenv('PRODUCT_SUBSCRIPTION_FULL_ID', 'beesmart.sub.full_monthly'): {
        'type': 'premium', 'subscription': True, 'price': 4.99, 'duration': '1 month'
    },
    # Monthly Premium Subscription ($4.99/month)
    'beesmart.premium.monthly': {
        'type': 'premium', 'subscription': True, 'price': 4.99, 'duration': '1 month',
        'name': 'Premium Monthly Membership'
    },
    # Yearly Premium Subscription ($39.99/year - Best Value, Save 33%)
    'beesmart.premium.yearly': {
        'type': 'premium', 'subscription': True, 'price': 39.99, 'duration': '1 year',
        'name': 'Premium Yearly Membership'
    },
    # Family Premium Subscription ($7.99/month - Up to 6 members)
    'beesmart.premium.family.monthly': {
        'type': 'premium', 'subscription': True, 'price': 7.99, 'duration': '1 month',
        'name': 'Premium Family Membership', 'family_sharing': True
    },
    # Individual avatar unlocks
    os.getenv('PRODUCT_AVATAR_SUPERBEE_ID', 'beesmart.avatar.superbee'): {
        'type': 'avatar', 'avatar_id': 'superbee'
    },
    os.getenv('PRODUCT_AVATAR_QUEEN_ID', 'beesmart.avatar.queen'): {
        'type': 'avatar', 'avatar_id': 'queen-bee'
    },
    os.getenv('PRODUCT_AVATAR_KNIGHT_ID', 'beesmart.avatar.knight'): {
        'type': 'avatar', 'avatar_id': 'knight-bee'
    },
    os.getenv('PRODUCT_AVATAR_ROCKER_ID', 'beesmart.avatar.rocker'): {
        'type': 'avatar', 'avatar_id': 'rocker-bee'
    },
    # Example bundle
    os.getenv('PRODUCT_BUNDLE_TOP_ID', 'beesmart.bundle.top'): {
        'type': 'bundle', 'bundle_id': 'top_bee_bundle',
        'avatars': ['superbee', 'queen-bee', 'knight-bee', 'rocker-bee']
    },
}

# Extend product map with all avatar SKUs → avatar entitlements
try:
    PRODUCT_MAP.update(build_product_entitlements())
except Exception as _e:
    print(f"WARN: Failed to load avatar product entitlements: {_e}")

# Extend product map with bundle catalog → bundle entitlements
try:
    if BUNDLE_CATALOG:
        for _bundle_id, _cfg in BUNDLE_CATALOG.items():
            pid = f"bundle:{_bundle_id}"
            if pid not in PRODUCT_MAP:
                PRODUCT_MAP[pid] = {
                    'type': 'bundle',
                    'bundle_id': _bundle_id,
                    'avatars': list(_cfg.get('avatars', []) or [])
                }
        try:
            print(f"✅ Bundle catalog loaded: {len(BUNDLE_CATALOG)} bundles; keys available: {len(REDEEMABLE_KEYS) if isinstance(REDEEMABLE_KEYS, dict) else 0}")
        except Exception:
            pass
except Exception as _e:
    print(f"WARN: Failed to load bundle entitlements: {_e}")


def _apply_entitlement(user: User, product_id: str) -> dict:
    """Apply entitlements for a product to the given user. Idempotent.
    Returns a dict summary of changes.
    """
    mapping = PRODUCT_MAP.get(product_id)
    result = {"applied": False, "details": {}}
    if not mapping:
        return result

    if mapping.get('type') == 'premium':
        if not user.premium_member:
            user.premium_member = True
            result["applied"] = True
        result["details"] = {"premium_member": True}
        return result

    if mapping.get('type') == 'avatar':
        avatar_id = mapping.get('avatar_id')
        if avatar_id:
            # Ensure purchased_avatars list
            if not user.purchased_avatars:
                user.purchased_avatars = []
            if avatar_id not in user.purchased_avatars:
                user.purchased_avatars.append(avatar_id)
                result["applied"] = True
            result["details"] = {"unlocked_avatar": avatar_id}
        return result

    if mapping.get('type') == 'bundle':
        bundle_id = mapping.get('bundle_id')
        avatars = mapping.get('avatars', [])
        if not user.purchased_bundles:
            user.purchased_bundles = []
        if bundle_id and bundle_id not in user.purchased_bundles:
            user.purchased_bundles.append(bundle_id)
            # Unlock avatars
            if not user.purchased_avatars:
                user.purchased_avatars = []
            new_ones = 0
            for a in avatars:
                if a not in user.purchased_avatars:
                    user.purchased_avatars.append(a)
                    new_ones += 1
            result["applied"] = True
            result["details"] = {"bundle": bundle_id, "unlocked_count": new_ones}
        else:
            result["details"] = {"bundle": bundle_id, "unlocked_count": 0}
        return result

    return result


# ----------------------------
# IAP verification (scaffolds)
# ----------------------------
def _verify_with_store_apple(data: dict) -> tuple[bool, str, dict]:
    """Scaffold for App Store Server API verification.
    Env (planned):
      - APPLE_ISSUER_ID
      - APPLE_KEY_ID
      - APPLE_PRIVATE_KEY (PEM) or APPLE_PRIVATE_KEY_PATH
      - APPLE_APP_BUNDLE_ID
      - APPLE_ENV ("Sandbox" | "Production")
      - IAP_LIVE_ACCEPT_BASIC (optional: accept basic checks only for dev)
    """
    # Basic presence checks
    product_id = (data or {}).get('product_id')
    payload = (data or {}).get('payload') or {}
    txn = (data or {}).get('transaction_id') or (payload.get('transactionId'))

    # Require product mapping to exist
    if product_id not in PRODUCT_MAP:
        return False, 'unknown_product', {'reason': 'product_id not in PRODUCT_MAP'}

    # Require some form of transaction evidence
    if not (txn or payload):
        return False, 'missing_transaction', {'reason': 'no transaction_id or payload provided'}

    # Check configuration availability
    has_conf = all(os.getenv(k) for k in ('APPLE_ISSUER_ID', 'APPLE_KEY_ID')) and (
        os.getenv('APPLE_PRIVATE_KEY') or os.getenv('APPLE_PRIVATE_KEY_PATH')
    )
    if not has_conf:
        if os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1', 'true', 'True', 'yes'):
            return True, 'basic_accepted_unverified', {'note': 'APPLE_* env not fully configured'}
        return False, 'apple_verification_not_configured', {}

    # Attempt live verification if module available
    try:
        from iap_verification import verify_apple_purchase  # type: ignore
        ok, status, details = verify_apple_purchase(data)
        if ok:
            return True, status, details
        # If strict, propagate failure; if permissive and basic acceptance allowed, accept
        if IAP_VERIFICATION_MODE == 'live_permissive' or os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1','true','True','yes'):
            return True, f'permissive_{status}', details
        return False, status, details
    except Exception as e:
        if IAP_VERIFICATION_MODE == 'live_permissive' or os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1','true','True','yes'):
            return True, f'permissive_exception: {e}', {}
        return False, f'apple_verifier_unavailable: {e}', {}


def _verify_with_store_google(data: dict) -> tuple[bool, str, dict]:
    """Scaffold for Google Play Developer API verification.
    Env (planned):
      - GOOGLE_PLAY_SERVICE_ACCOUNT (JSON string) or GOOGLE_PLAY_SERVICE_ACCOUNT_PATH
      - GOOGLE_PLAY_PACKAGE_NAME
      - IAP_LIVE_ACCEPT_BASIC (optional: accept basic checks only for dev)
    """
    product_id = (data or {}).get('product_id')
    purchase_token = (data or {}).get('purchase_token') or ((data or {}).get('payload') or {}).get('purchaseToken')

    if product_id not in PRODUCT_MAP:
        return False, 'unknown_product', {'reason': 'product_id not in PRODUCT_MAP'}
    if not purchase_token:
        return False, 'missing_purchase_token', {'reason': 'no purchase_token provided'}

    has_conf = bool(os.getenv('GOOGLE_PLAY_PACKAGE_NAME')) and (
        os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT') or os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT_PATH')
    )
    if not has_conf:
        if os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1', 'true', 'True', 'yes'):
            return True, 'basic_accepted_unverified', {'note': 'GOOGLE_* env not fully configured'}
        return False, 'google_verification_not_configured', {}

    # Attempt live verification if module available
    try:
        from iap_verification import verify_google_purchase  # type: ignore
        ok, status, details = verify_google_purchase(data)
        if ok:
            return True, status, details
        if IAP_VERIFICATION_MODE == 'live_permissive' or os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1','true','True','yes'):
            return True, f'permissive_{status}', details
        return False, status, details
    except Exception as e:
        if IAP_VERIFICATION_MODE == 'live_permissive' or os.getenv('IAP_LIVE_ACCEPT_BASIC', '0') in ('1','true','True','yes'):
            return True, f'permissive_exception: {e}', {}
        return False, f'google_verifier_unavailable: {e}', {}


def _verify_with_store(platform: str, payload: dict) -> tuple[bool, str, dict]:
    """Verify purchase with Apple/Google based on env-driven mode.
    Returns (ok, status_message, details)
    Modes:
      - IAP_MOCK=1                 → always succeed with mock
      - IAP_VERIFICATION_MODE=live_strict (default when mock off)
      - IAP_VERIFICATION_MODE=live_permissive (accept if basic checks pass)
    """
    if IAP_MOCK_MODE or IAP_VERIFICATION_MODE == 'mock':
        return True, 'mock_verified', {'mock': True}

    try:
        if platform == 'apple':
            return _verify_with_store_apple(payload)
        elif platform == 'google':
            return _verify_with_store_google(payload)
        else:
            return False, 'unsupported_platform', {}
    except Exception as e:
        return False, f'verification_error: {e}', {}

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

def _filter_definition(definition, word):
    """Filter definition to remove the target word and provide alternative if needed."""
    if not definition or not word:
        return definition or ""
    
    # Remove unhelpful phrases like "American spelling of...", "British spelling of...", etc.
    unhelpful_patterns = [
        r"^American spelling of\s+\w+\.?\s*",
        r"^British spelling of\s+\w+\.?\s*",
        r"^US spelling of\s+\w+\.?\s*",
        r"^UK spelling of\s+\w+\.?\s*",
        r"^Alternative spelling of\s+\w+\.?\s*",
        r"^Alternative form of\s+\w+\.?\s*",
    ]
    
    filtered = definition
    for pattern in unhelpful_patterns:
        filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE).strip()
    
    # If we removed everything, return a generic description
    if not filtered or len(filtered) < 10:
        return f"A word to practice spelling"
    
    # Now blank out the word
    filtered = _blank_word(filtered, word)
    
    # If the definition is mostly blanks now, provide a generic alternative
    blank_count = filtered.count("_____")
    word_count = len(filtered.split())
    
    if blank_count > 0 and (blank_count / max(word_count, 1)) > 0.3:  # More than 30% blanks
        return f"A word to practice spelling"
    
    return filtered

def _get_inappropriate_vocab() -> set:
    """Return the most comprehensive set of inappropriate vocabulary available.
    Prefer the enhanced list from content_filter_guardian if importable; otherwise
    fall back to the base INAPPROPRIATE_WORDS defined in this module.
    """
    try:
        from content_filter_guardian import ALL_INAPPROPRIATE_WORDS as _ALL
        return set(_ALL)
    except Exception:
        return set(INAPPROPRIATE_WORDS)

def sanitize_kid_friendly_text(text: str) -> str:
    """Sanitize definition/example text for kid-friendliness.
    Strategy:
      - Split into sentences and drop any sentence that contains clearly inappropriate
        words (exact-token matches) or the special substring 'sex'.
      - Also drop sentences that contain any longer (len>4) inappropriate word as a substring.
      - If everything is removed or text becomes too short, return a neutral fallback.
    Never modifies the answer blanks ("_____").
    """
    if not text:
        return ""

    original = text
    vocab = _get_inappropriate_vocab()

    # Simple sentence splitter (keep punctuation boundaries)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept: list[str] = []
    for s in sentences:
        s_lower = s.lower()

        # Preserve answer blanks
        if not s.strip():
            continue

        # Special-case: block any sentence containing 'sex'
        if "sex" in s_lower:
            continue

        # Tokenize and check exact matches
        tokens = re.findall(r"[a-z]+", s_lower)
        token_set = set(tokens)
        if any(tok in vocab for tok in token_set):
            continue

        # Substring rule for longer inappropriate words
        if any(len(bad) > 4 and bad in s_lower for bad in vocab):
            continue

        kept.append(s)

    cleaned = " ".join(kept).strip()
    # If nothing left or too short, return a safe generic
    if not cleaned or len(cleaned) < 8:
        # Preserve a friendly, neutral prompt depending on the context of usage
        return "A kid-friendly description is unavailable. Please listen and spell the word you hear."

    return cleaned

def parse_enriched_info(raw: str, word: str) -> tuple[str, str]:
    """Split combined enrichment string into (definition, sentence), then blank + sanitize.
    Expected format contains 'Fill in the blank:'. If missing, treat all as definition.
    Never reveals the answer; idempotent with existing blanks.
    """
    if not raw:
        return "", ""
    try:
        if "Fill in the blank:" in raw:
            before, after = raw.split("Fill in the blank:", 1)
            d = sanitize_kid_friendly_text(_blank_word(before.strip(), word))
            s = sanitize_kid_friendly_text(_blank_word(after.strip(), word))
            return d, s
        else:
            d = sanitize_kid_friendly_text(_blank_word(raw.strip(), word))
            return d, ""
    except Exception:
        return "", ""

def _cache_word_info(word_lower: str, formatted: str):
    """LRU cache helper for formatted word info responses."""
    try:
        if not formatted:
            return
        if word_lower in WORD_INFO_CACHE:
            WORD_INFO_CACHE.move_to_end(word_lower)
            WORD_INFO_CACHE[word_lower] = formatted
        else:
            WORD_INFO_CACHE[word_lower] = formatted
            if len(WORD_INFO_CACHE) > WORD_INFO_CACHE_MAX:
                # Pop oldest
                WORD_INFO_CACHE.popitem(last=False)
    except Exception:
        pass

def get_word_info(word):
    """Fast word enrichment: definition + example sentence with blanks.
    Priority:
      1) Simple Wiktionary (indexed) – kid-friendly
      2) Persistent DICTIONARY_CACHE (previous enrichments)
      3) Smart fallback generator
    All paths blank out the target word safely.
    """
    global DICTIONARY_CACHE, SIMPLE_WIKTIONARY_INDEX

    if not word:
        return "Definition not available for this word. Listen carefully and spell _____ correctly"

    word_lower = word.lower().strip()

    # Fast LRU hit
    if word_lower in WORD_INFO_CACHE:
        global _WORD_INFO_HITS
        _WORD_INFO_HITS += 1
        return WORD_INFO_CACHE[word_lower]
    global _WORD_INFO_MISSES
    _WORD_INFO_MISSES += 1

    # Ensure caches
    if not DICTIONARY_CACHE:
        DICTIONARY_CACHE = load_dictionary_cache()
    wiktionary = ensure_simple_wiktionary_loaded()

    # PRIORITY 1: Simple Wiktionary via index (constant time membership)
    if SIMPLE_WIKTIONARY_INDEX and word_lower in SIMPLE_WIKTIONARY_INDEX:
        word_data = wiktionary.get(word_lower, {})
        definition = word_data.get("definition", "")
        example = word_data.get("example", "")
        if definition:
            if example and len(example) > 10:
                # Sanitize and blank both definition and example for safety
                definition = sanitize_kid_friendly_text(_filter_definition(definition, word))
                example = sanitize_kid_friendly_text(_blank_word(example, word))
                formatted = f"{definition}. Fill in the blank: {example}"
                print(f"📖 (indexed) '{word}' → wiktionary+example")
            else:
                definition = sanitize_kid_friendly_text(_filter_definition(definition, word))
                formatted = f"{definition}. Fill in the blank: Can you spell _____ correctly?"
                print(f"📖 (indexed) '{word}' → wiktionary (no example)")
            _cache_word_info(word_lower, formatted)
            return formatted

    # PRIORITY 2: Persistent DICTIONARY_CACHE
    if word_lower in DICTIONARY_CACHE:
        word_data = DICTIONARY_CACHE[word_lower]
        definition = word_data.get("definition", "")
        example = word_data.get("example", "")
        if definition:
            if example:
                definition = sanitize_kid_friendly_text(_filter_definition(definition, word))
                example = sanitize_kid_friendly_text(_blank_word(example, word))
                formatted = f"{definition}. Fill in the blank: {example}"
            else:
                definition = sanitize_kid_friendly_text(_filter_definition(definition, word))
                formatted = f"{definition}. Fill in the blank: Can you spell _____ correctly?"
            print(f"✅ Cache hit '{word}'")
            _cache_word_info(word_lower, formatted)
            return formatted
    
    # PRIORITY 3: Smart fallback - deterministic enrichment
    try:
        fb = generate_smart_fallback(word)
        definition = sanitize_kid_friendly_text(fb.get("definition", "A word to spell"))
        example = sanitize_kid_friendly_text(_blank_word(fb.get("example", "Can you spell _____ correctly?"), word))
        formatted = f"{definition}. Fill in the blank: {example}"
        print(f"🟨 Fallback '{word}' ({fb.get('source','fallback')})")
        _cache_word_info(word_lower, formatted)
        return formatted
    except Exception as _e:
        formatted = "Definition not available for this word. Listen carefully and spell _____ correctly"
        _cache_word_info(word_lower, formatted)
        print(f"⚠️ Fallback failed for '{word}': {_e}")
        return formatted


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


# ---------------------------------
# Upload helpers used by saved-list
# ---------------------------------
def _normalize_for_compare(word: str) -> str:
    """Normalize a word for deduplication: lowercase and remove non-alphanumerics."""
    if not word:
        return ""
    return re.sub(r"[^0-9a-z]+", "", word.lower())


from typing import Union, Set  # ensure Union and Set available for Python <3.10 compatibility

def deduplicate_words(words: List[Union[Dict, str]]) -> List[Dict]:
    """Dedupe words using normalization rules; preserve first occurrence and existing metadata.
    Accepts a list of strings or dicts with at least a 'word' key; returns a list of dicts.
    """
    seen = set()
    result: List[Dict] = []
    for item in words:
        if isinstance(item, dict):
            w = (item.get("word") or "").strip()
            key = _normalize_for_compare(w)
            if not key or key in seen:
                continue
            seen.add(key)
            result.append({
                "word": w,
                "sentence": (item.get("sentence") or "").strip(),
                "hint": (item.get("hint") or "").strip(),
            })
        else:
            w = (str(item) or "").strip()
            key = _normalize_for_compare(w)
            if not key or key in seen:
                continue
            seen.add(key)
            result.append({"word": w, "sentence": "", "hint": ""})
    return result


def enrich_with_definitions(words: List[Dict]) -> List[Dict]:
    """Batch enrich records with sentences using cached get_word_info.
    Avoid repeated per-record overhead by leveraging LRU/cache.
    """
    unique_words: List[str] = []
    seen: Set[str] = set()
    for rec in words:
        w = (rec.get("word") or "").strip()
        if not w:
            continue
        wl = w.lower()
        if wl in seen:
            continue
        seen.add(wl)
        unique_words.append(w)

    word_info_map = bulk_word_info(unique_words)

    enriched: List[Dict] = []
    for rec in words:
        w = (rec.get("word") or "").strip()
        if not w:
            continue
        hint = (rec.get("hint") or "").strip()
        sentence = (rec.get("sentence") or "").strip()
        if not sentence:
            sentence = word_info_map.get(w.lower()) or "Listen carefully and spell _____ correctly."
        enriched.append({"word": w, "sentence": sentence, "hint": hint})
    return enriched

# ---------------------------
# Bulk Word Info Enrichment
# ---------------------------
def bulk_word_info(words: List[str]) -> Dict[str, str]:
    """Efficiently enrich a list of words, returning a mapping of lowercased word -> formatted sentence.
    Leverages internal LRU & persistent caches. Ensures each word looked up at most once.
    Safe failures fall back to a generic spelling prompt.
    """
    results: Dict[str, str] = {}
    for w in words:
        if not w:
            continue
        wl = w.lower().strip()
        if wl in results:
            continue
        try:
            formatted = get_word_info(w)
        except Exception as ex:
            print(f"⚠️ bulk_word_info failed for '{w}': {ex}")
            formatted = "Listen carefully and spell _____ correctly."
        results[wl] = formatted
    return results


def log_error(message: str):
    """Lightweight error logger used in a few endpoints; safe even if app.logger isn't available."""
    try:
        app.logger.error(message)  # type: ignore[attr-defined]
    except Exception:
        logging.getLogger(__name__).error(message)


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

print("🔧 Creating Flask app (main init)...")
# Preserve existing app if earlier created; do NOT overwrite to keep early routes.
if 'app' not in globals():
    app = Flask(__name__)
# --- Avatar GLB sync helper ---
def _sync_glb_avatars():
    """Copy any new GLB avatars dropped in Avatars/3D Avatar Files into the served static folder.
    This lets newly uploaded .glb files become available at /static/assets/avatars/glb_files/ without manual moves.
    Safe to run on startup; copies only when destination is missing or source is newer.
    """
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(project_root, 'Avatars', '3D Avatar Files')
        dst_dir = os.path.join(project_root, 'static', 'assets', 'avatars', 'glb_files')
        if not os.path.isdir(src_dir):
            return
        os.makedirs(dst_dir, exist_ok=True)
        for name in os.listdir(src_dir):
            if not name.lower().endswith('.glb'):
                continue
            src = os.path.join(src_dir, name)
            dst = os.path.join(dst_dir, name)
            try:
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    print(f"[avatar-sync] Copied GLB: {name}")
            except Exception as e:
                print(f"[avatar-sync] Skip {name}: {e}")
    except Exception as e:
        print(f"[avatar-sync] Error: {e}")

# Run sync at startup (skipped in FAST_BOOT)
if not FAST_BOOT:
    _sync_glb_avatars()
else:
    print("⏭️ Skipping GLB avatar sync at startup (FAST_BOOT)")

# Load configuration from config.py (includes database settings)
print("🔧 Loading configuration...")
app.config.from_object(get_config())
print(f"✅ Config loaded - Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

# Backwards compatibility: keep old secret key if not in config
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ.get("SPELLING_APP_SECRET", "dev-secret-change-me")

# Admin registration key - required to register as admin
ADMIN_REGISTRATION_KEY = os.environ.get("BEESMART_ADMIN_KEY", "BEE-ADMIN-2025-SECURE-KEY")

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
            
            # Migration: Add is_favorite column if missing
            try:
                columns = [col['name'] for col in inspector.get_columns('word_lists')]
                if 'is_favorite' not in columns:
                    print("🔧 Adding is_favorite column to word_lists table...")
                    db.session.execute(text(
                        "ALTER TABLE word_lists ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE"
                    ))
                    db.session.commit()
                    print("✅ Added is_favorite column")
            except Exception as e:
                print(f"⚠️ is_favorite migration: {e}")
                db.session.rollback()
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
    """
    Convert numerical GPA (0-4.0) to letter grade.
    
    Must match the grade_to_gpa mapping in models.py:
    A+: 4.0, A: 4.0, A-: 3.7, B+: 3.3, B: 3.0, B-: 2.7,
    C+: 2.3, C: 2.0, C-: 1.7, D+: 1.3, D: 1.0, D-: 0.7, F: 0.0
    """
    try:
        gpa_value = float(gpa) if gpa else 0.0
    except (ValueError, TypeError):
        return "N/A"
    
    # Exact reverse of grade_to_gpa mapping
    if gpa_value >= 4.0:
        return "A+"  # 4.0 = A+ or A, prefer A+
    elif gpa_value >= 3.7:
        return "A-"
    elif gpa_value >= 3.3:
        return "B+"
    elif gpa_value >= 3.0:
        return "B"
    elif gpa_value >= 2.7:
        return "B-"
    elif gpa_value >= 2.3:
        return "C+"
    elif gpa_value >= 2.0:
        return "C"
    elif gpa_value >= 1.7:
        return "C-"
    elif gpa_value >= 1.3:
        return "D+"
    elif gpa_value >= 1.0:
        return "D"
    elif gpa_value >= 0.7:
        return "D-"
    elif gpa_value > 0:
        return "F"
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
    """Ensure every request has a session with unique ID and permanent flag
    Skip for static files, health checks, and other non-interactive endpoints to improve performance"""
    # Skip session creation for static files and health/utility endpoints
    if request.path.startswith(('/static/', '/health', '/favicon.ico', '/.well-known/')):
        return
    
    if not session.get("session_id"):
        session["session_id"] = str(uuid.uuid4())
        session.permanent = True  # Use PERMANENT_SESSION_LIFETIME
    elif not session.permanent:
        session.permanent = True  # Ensure existing sessions are permanent


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
        # Prefer configured default sender (e.g., Contact@beesmartspelling.app)
        default_sender = app.config.get('MAIL_DEFAULT_SENDER') or username
        from_name = app.config.get('MAIL_FROM_NAME')
        msg['From'] = f"{from_name} <{default_sender}>" if from_name and default_sender else (default_sender or '')
        msg['To'] = recipient_email
        # Ensure reply goes to the branded address
        if default_sender:
            msg['Reply-To'] = default_sender
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
        # Envelope sender should match the default sender when available
        envelope_from = default_sender or username
        smtp.sendmail(envelope_from, [recipient_email], msg.as_string())
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
        # Prefer configured default sender (e.g., Contact@beesmartspelling.app)
        default_sender = app.config.get('MAIL_DEFAULT_SENDER') or smtp_username
        from_name = app.config.get('MAIL_FROM_NAME')
        msg['From'] = f"{from_name} <{default_sender}>" if from_name and default_sender else (default_sender or '')
        msg['To'] = recipient_email
        if default_sender:
            msg['Reply-To'] = default_sender
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
        envelope_from = default_sender or smtp_username
        smtp.sendmail(envelope_from, [recipient_email], msg.as_string())
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
            email_verified=False,
            avatar_id="mascot-bee",  # Always use free mascot for guests
            avatar_variant="default"
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
    # Sexual/adult content - CRITICAL: Block all adult/child abuse terms
    "sex", "sexy", "porn", "orgasm", "penis", "vagina", "breast", "breasts",
    "ejaculation", "ejaculations", "erection", "masturbate", "prostitute",
    "pedophile", "pedophiles", "pedophilia", "pedophilic", "paedophile", "paedophilia",
    "molest", "molestation", "molester", "molesting", "molesters",
    "rape", "rapist", "raping", "rapes", "raped",
    "incest", "incestuous", "abuse", "abuser", "abusive", "abusing",
    "predator", "predators", "groom", "grooming", "groomer", "groomers",
    "statutory", "underage", "preteen", "preteens", "tweener", "tweeners",
    "victim", "victims", "exploit", "exploitation", "exploiting",
    "assault", "assaulting", "assaults", "assaulted",
    "harass", "harassment", "harassing",
    "nude", "naked", "horny", "arousal", "climax", "intercourse",
    "erotic", "sexuality", "genitals", "genital",
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

    # Special rule: block any word containing the substring "sex"
    # This is stricter than the general partial-match rule and reflects
    # the app's kid-safety policy requested by stakeholders.
    if "sex" in word_lower:
        return False, f"Word '{word}' contains restricted substring 'sex'"
    
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

# Helper: filter out any records whose sentence/hint contains profanity or inappropriate text
def _filter_records_excluding_inappropriate_text(records: List[Dict[str, str]]):
    """Return (filtered, blocked) where blocked is list of {'word','reason'} dicts.
    Policy: if sentence or hint contains profanity or other inappropriate content, remove it.
    Rules:
      - Block if 'sex' appears anywhere (substring, case-insensitive)
      - Block if any token matches an inappropriate word exactly (case-insensitive)
      - Block if any inappropriate word of length > 4 appears as a substring
    """
    # Acquire inappropriate vocabulary from enhanced filter if available, else fallback
    try:
        from content_filter_guardian import ALL_INAPPROPRIATE_WORDS as _ALL
        inappropriate_words = set(_ALL)
    except Exception:
        # Fallback to base set already in this module
        inappropriate_words = set(INAPPROPRIATE_WORDS)

    filtered: List[Dict[str, str]] = []
    blocked: List[Dict[str, str]] = []

    for r in records:
        sentence = (r.get("sentence") or "")
        hint = (r.get("hint") or "")
        combined = f"{sentence} {hint}".lower()

        # Rule 1: special-case substring 'sex'
        if "sex" in combined:
            blocked.append({"word": r.get("word", ""), "reason": "definition/hint contains restricted substring 'sex'"})
            continue

        # Tokenize to check exact matches (avoid false positives like 'class')
        tokens = re.findall(r"[a-z]+", combined)
        token_set = set(tokens)
        if any(tok in inappropriate_words for tok in token_set):
            blocked.append({"word": r.get("word", ""), "reason": "definition/hint contains profanity or inappropriate words"})
            continue

        # Substring rule for longer inappropriate words (>4 chars)
        if any(len(bad) > 4 and bad in combined for bad in inappropriate_words):
            blocked.append({"word": r.get("word", ""), "reason": "definition/hint contains inappropriate content"})
            continue

        filtered.append(r)

    return filtered, blocked

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
    """Read wordbank from WORD_STORAGE using session's storage_id pointer.
    
    Avoids cookie size limits by keeping full word list server-side.
    Session only stores small UUID pointer (~36 bytes).
    """
    storage_id = session.get("wordbank_storage_id")
    wb = []

    # Try to load from WORD_STORAGE using storage_id pointer
    if storage_id:
        with WORD_STORAGE_LOCK:
            wb = WORD_STORAGE.get(storage_id, [])
        if wb:
            print(f"DEBUG get_wordbank: Loaded {len(wb)} words from WORD_STORAGE[{storage_id}]")
        else:
            print(f"⚠️ WARNING get_wordbank: storage_id={storage_id} exists but WORD_STORAGE is empty (server restart?)")
    
    # Fallback: try legacy direct session storage (migrate to WORD_STORAGE)
    # BUT respect explicit clear operation - don't restore if user cleared intentionally
    if not wb:
        legacy = session.get(DATA_KEY)
        was_cleared = session.get("wordbank_cleared", False)
        
        if was_cleared:
            print("DEBUG get_wordbank: Wordbank was intentionally cleared - not restoring from fallback")
        elif isinstance(legacy, list) and legacy:
            wb = legacy
            print(f"DEBUG get_wordbank: Migrating {len(wb)} words from session to WORD_STORAGE")
            set_wordbank(wb, is_user_upload=session.get("has_uploaded_once", False))

    # NO DEFAULT LOADING - Users must upload or type their own words
    # Wordbank starts empty until user provides words
    if not wb:
        print("DEBUG get_wordbank: Wordbank is empty - user needs to upload or add words")
    
    session["wordbank_count"] = len(wb)
    return wb

def set_wordbank(rows: List[Dict[str, str]], is_user_upload: bool = False):
    """Store wordbank in WORD_STORAGE to avoid cookie size limits.
    
    Cookie-based sessions have ~4KB limit - large word lists cause data loss.
    WORD_STORAGE is server-side in-memory, session only stores UUID pointer.
    """
    import uuid
    
    # Get or create storage_id for this session
    storage_id = session.get("wordbank_storage_id")
    if not storage_id:
        storage_id = str(uuid.uuid4())
        session["wordbank_storage_id"] = storage_id
        print(f"DEBUG set_wordbank: Created new storage_id={storage_id}")
    
    # Store full word list in server-side WORD_STORAGE (not in cookies!)
    with WORD_STORAGE_LOCK:
        WORD_STORAGE[storage_id] = rows
    
    # Only store lightweight metadata in session
    session["wordbank_count"] = len(rows)
    # Provide a tiny durability fallback for very small lists (survive dev reloads)
    # We avoid bloating cookies: only persist if JSON size <= ~2KB
    try:
        payload = json.dumps(rows, ensure_ascii=False)
        if len(payload.encode('utf-8')) <= 2048:
            session[DATA_KEY] = rows  # allows get_wordbank() to migrate after reload
            print(f"DEBUG set_wordbank: Stored compact fallback list in session (len={len(rows)})")
        else:
            session.pop(DATA_KEY, None)
    except Exception as _e:
        # On any failure, ensure legacy key is cleared
        session.pop(DATA_KEY, None)
    session.modified = True
    session.permanent = True  # Strengthen persistence on mobile browsers

    if is_user_upload:
        session["has_uploaded_once"] = True
        session.pop("using_default_words", None)
        print(f"DEBUG set_wordbank: User uploaded {len(rows)} words → WORD_STORAGE[{storage_id}]")
    else:
        session["using_default_words"] = True
        print(f"DEBUG set_wordbank: System words {len(rows)} → WORD_STORAGE[{storage_id}]")

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
    "started_at": datetime.now(timezone.utc).isoformat(),
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

# Register Battle of the Bees API Blueprint
print("🔧 Registering Battle API...")
try:
    from battles_api import battles_bp
    app.register_blueprint(battles_bp, url_prefix='/api')
    print("✅ Battle API registered successfully - Routes at /api/battles/*")
except Exception as e:
    print(f"⚠️ Battle API registration failed: {e}")

# --- Routes: Saved Word Lists (Persistent) -----------------------------------
@app.route("/api/saved-lists", methods=["GET"])
def list_saved_wordlists():
    """Return the current user's saved word lists (persisted; not cleared by /api/clear)."""
    try:
        # Guests are not allowed to use Saved Lists API
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required to use Saved Lists", "auth_required": True}), 403
        
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
                "is_favorite": getattr(wl, 'is_favorite', False),  # Include favorite status
            })

        return jsonify({"ok": True, "lists": data})
    except Exception as e:
        print(f"ERROR /api/saved-lists GET: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to retrieve saved lists"}), 500


@app.route("/api/saved-lists/<int:list_id>", methods=["GET"])
def get_saved_wordlist(list_id):
    """Get details of a specific saved word list."""
    try:
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required"}), 403
        
        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400
        
        # Find the list
        wl = WordList.query.filter_by(id=list_id, created_by_user_id=user.id).first()
        
        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404
        
        # Get all words in the list
        items = WordListItem.query.filter_by(word_list_id=wl.id).order_by(WordListItem.position).all()
        words = [item.word_data.get('word', '') for item in items if item.word_data]
        
        return jsonify({
            "ok": True,
            "list": {
                "id": wl.id,
                "name": wl.list_name,
                "word_count": len(items),
                "words": words,
                "created_at": wl.created_at.isoformat() if wl.created_at else None,
                "updated_at": wl.updated_at.isoformat() if wl.updated_at else None
            }
        })
    except Exception as e:
        print(f"ERROR /api/saved-lists/{list_id} GET: {e}")
        return jsonify({"ok": False, "error": "Failed to load list"}), 500


@app.route("/api/saved-lists/save", methods=["POST"])
def save_current_wordlist():
    """Persist the current in-session wordbank to the database with a user-provided name."""
    try:
        # Guests are not allowed to save lists
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required to save lists", "auth_required": True}), 403
        payload = request.get_json(silent=True) or {}
        list_name = (payload.get("list_name") or "").strip()
        description = (payload.get("description") or "").strip()

        if not list_name:
            return jsonify({"ok": False, "error": "List name is required"}), 400

        storage_id = session.get("wordbank_storage_id")
        print(f"DEBUG /api/saved-lists/save: storage_id={storage_id}, session_keys={list(session.keys())}")
        
        words = get_wordbank()
        print(f"DEBUG /api/saved-lists/save: Retrieved {len(words)} words from get_wordbank()")
        
        if not words:
            return jsonify({"ok": False, "error": "No words available to save. Please upload or paste words first."}), 400

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
        # Guests are not allowed to load lists
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required to load saved lists", "auth_required": True}), 403
        payload = request.get_json(silent=True) or {}
        list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")
        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        print(f"DEBUG /api/saved-lists/load: Loading list_id={list_id}")

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

        # Explicitly clear any previous quiz state BEFORE loading new words to avoid stale stats
        if session.get(QUIZ_STATE_KEY):
            print(f"DEBUG /api/saved-lists/load: Clearing previous quiz state for session_id={session.get('session_id')}")
            session.pop(QUIZ_STATE_KEY, None)
            session.modified = True

        # Load into session for quiz use (mark as user_upload to prevent defaults from appearing)
        print(f"DEBUG /api/saved-lists/load: Loading {len(rows)} words into session via set_wordbank")
        set_wordbank(rows, is_user_upload=True)  # Changed to True - saved lists are user content
        # Re-initialize quiz state with fresh order & counters
        init_quiz_state()
        # Safety: ensure new quiz state reflects new word count
        fresh_state = get_quiz_state()
        if fresh_state and len(fresh_state.get("order", [])) != len(rows):
            print("WARNING /api/saved-lists/load: Fresh quiz state length mismatch, reinitializing once more")
            init_quiz_state()

        print(f"DEBUG /api/saved-lists/load: Successfully loaded {len(rows)} words, storage_id={session.get('wordbank_storage_id')}")

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


@app.route("/api/saved-lists/delete", methods=["POST"])
@app.route("/api/saved-lists/<int:list_id>", methods=["DELETE"])
def delete_saved_wordlist(list_id=None):
    try:
        # Guests are not allowed to delete lists
        if not current_user.is_authenticated:
            print(f"DEBUG /api/saved-lists/delete: User not authenticated")
            return jsonify({"ok": False, "error": "Login required to delete saved lists", "auth_required": True}), 403
        
        # Get list_id from URL parameter or POST body
        if list_id is None:
            payload = request.get_json(silent=True) or {}
            list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")
        
        print(f"DEBUG /api/saved-lists/delete: Received payload={payload}, list_id={list_id}")
        
        if not list_id:
            print(f"DEBUG /api/saved-lists/delete: Missing list ID in payload")
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        print(f"DEBUG /api/saved-lists/delete: Attempting to delete list_id={list_id}")

        user = get_or_create_guest_user()
        if not user:
            print(f"DEBUG /api/saved-lists/delete: Unable to resolve user")
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        print(f"DEBUG /api/saved-lists/delete: User resolved: id={user.id}, username={user.username}")

        wl = None
        try:
            # Try numeric ID first
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
            print(f"DEBUG /api/saved-lists/delete: Tried numeric lookup id={numeric_id}, found={wl is not None}")
        except Exception as e:
            # Fallback to UUID
            print(f"DEBUG /api/saved-lists/delete: Numeric lookup failed ({e}), trying UUID")
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()
            print(f"DEBUG /api/saved-lists/delete: UUID lookup uuid={list_id}, found={wl is not None}")

        if not wl:
            # List all user's lists for debugging
            all_lists = WordList.query.filter_by(created_by_user_id=user.id).all()
            list_info = [(l.id, l.uuid, l.list_name) for l in all_lists]
            print(f"DEBUG /api/saved-lists/delete: List not found for user {user.id}")
            print(f"DEBUG /api/saved-lists/delete: User has {len(all_lists)} lists: {list_info}")
            return jsonify({"ok": False, "error": "List not found or you don't have permission to delete it"}), 404

        # Count items before deletion
        item_count = WordListItem.query.filter_by(word_list_id=wl.id).count()
        print(f"DEBUG /api/saved-lists/delete: Deleting list '{wl.list_name}' (id={wl.id}, uuid={wl.uuid}) with {item_count} items")
        
        db.session.delete(wl)
        db.session.commit()
        
        print(f"✅ /api/saved-lists/delete: Successfully deleted list and its {item_count} items (cascade)")
        return jsonify({"ok": True, "deleted": {"id": wl.id, "name": wl.list_name, "item_count": item_count}})
    except Exception as e:
        print(f"ERROR /api/saved-lists/delete: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to delete list"}), 500


@app.route("/api/saved-lists/favorite", methods=["POST"])
def favorite_saved_wordlist():
    """Toggle favorite/pin status for a saved word list."""
    try:
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required", "auth_required": True}), 403
        
        data = request.get_json() or {}
        list_id = data.get("id")
        is_fav = bool(data.get("is_favorite", False))

        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Try numeric ID first, fallback to UUID
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404

        wl.is_favorite = is_fav
        wl.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"ok": True, "id": wl.id, "is_favorite": wl.is_favorite})

    except Exception as e:
        print(f"ERROR /api/saved-lists/favorite: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/rename", methods=["POST"])
def rename_saved_wordlist():
    """Rename a saved word list."""
    try:
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required", "auth_required": True}), 403
        
        data = request.get_json() or {}
        list_id = data.get("id")
        new_name = (data.get("new_name") or "").strip()

        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        if not new_name:
            return jsonify({"ok": False, "error": "Name cannot be empty"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Try numeric ID first, fallback to UUID
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404

        wl.list_name = new_name
        wl.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"ok": True, "id": wl.id, "name": wl.list_name})

    except Exception as e:
        print(f"ERROR /api/saved-lists/rename: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>", methods=["PUT"])
def update_saved_wordlist(list_id):
    """Update a saved word list (name and words)."""
    try:
        if not current_user.is_authenticated:
            return jsonify({"ok": False, "error": "Login required", "auth_required": True}), 403
        
        data = request.get_json() or {}
        new_name = (data.get("name") or "").strip()
        words = data.get("words") or []

        if not new_name:
            return jsonify({"ok": False, "error": "Name cannot be empty"}), 400
        
        if not isinstance(words, list):
            return jsonify({"ok": False, "error": "Words must be a list"}), 400

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        wl = WordList.query.filter_by(id=list_id, created_by_user_id=user.id).first()
        if not wl:
            return jsonify({"ok": False, "error": "List not found"}), 404

        # Update list name
        wl.list_name = new_name
        
        # Parse words - handle both string and dict formats
        parsed_words = []
        for item in words:
            if isinstance(item, dict):
                word = item.get('word', '').strip()
                sentence = item.get('sentence', '').strip()
                hint = item.get('hint', '').strip()
                if word:
                    parsed_words.append({
                        'word': word,
                        'sentence': sentence or word,
                        'hint': hint or ''
                    })
            elif isinstance(item, str):
                word = item.strip()
                if word:
                    parsed_words.append({
                        'word': word,
                        'sentence': word,
                        'hint': ''
                    })
        
        # Update words and count
        wl.words_json = json.dumps(parsed_words)
        wl.word_count = len(parsed_words)
        wl.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "ok": True,
            "list": {
                "id": wl.id,
                "name": wl.list_name,
                "word_count": wl.word_count,
                "words": parsed_words
            }
        })

    except Exception as e:
        print(f"ERROR /api/saved-lists/{list_id} PUT: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


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
        wl.updated_at = datetime.now(timezone.utc)

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
    """Ultra-light shell for root path that immediately forwards to /app.

    This avoids any unexpected middleware or template interactions tied to the root
    and guarantees a quick render with a 200, then a client redirect to the app.
    """
    from flask import make_response
    body = """<!doctype html><html><head><meta charset='utf-8'>
    <title>BeeSmart</title><meta http-equiv='refresh' content='0;url=/app'>
    <meta name='robots' content='noindex'>
    <style>body{font-family:Arial,sans-serif;padding:2rem;text-align:center}
    img{max-width:260px;margin:1rem auto;display:block}</style></head>
    <body>
    <img src='/static/BeeSmartCrestLogo1.png' alt='BeeSmart Logo'>
      <p>Loading BeeSmart… If not redirected, <a href='/app'>click here</a>.</p>
      <script>try{window.location.replace('/app')}catch(e){}</script>
    </body></html>"""
    resp = make_response(body)
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    return resp

@app.route("/app")
def app_home():
    import time
    timestamp = str(int(time.time()))
    from flask import make_response
    # Pass subscription messaging to home for guest upsell
    billing_mode = os.environ.get('REGISTRATION_BILLING_MODE', 'subscription').strip().lower()
    try:
        monthly_fee = float(os.environ.get('SUBSCRIPTION_MONTHLY_USD', '4.49'))
    except Exception:
        monthly_fee = 4.49
    try:
        trial_days = int(os.environ.get('SUBSCRIPTION_TRIAL_DAYS', '7'))
    except Exception:
        trial_days = 7
    try:
        intro_price = os.environ.get('SUBSCRIPTION_INTRO_PRICE_USD')
        intro_price = float(intro_price) if intro_price is not None and intro_price != '' else None
    except Exception:
        intro_price = None
    try:
        intro_months = int(os.environ.get('SUBSCRIPTION_INTRO_MONTHS', '0'))
    except Exception:
        intro_months = 0
    try:
        subscription_product_id = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID', 'beesmart.sub.full_monthly')
    except Exception:
        subscription_product_id = 'beesmart.sub.full_monthly'
    # Determine premium state for signed-in users (for trial banner logic)
    try:
        from flask_login import current_user as _cu
        is_premium = bool(getattr(_cu, 'is_authenticated', False) and getattr(_cu, 'premium_member', False))
    except Exception:
        is_premium = False
    # Expose avatar SKUs to client (native wrappers / UI can use this list)
    try:
        avatar_product_ids = AVATAR_SKUS
    except Exception:
        avatar_product_ids = {}
    
    # Expose subscription product IDs to client
    subscription_products = {
        'monthly': {
            'id': SUBSCRIPTION_PRODUCT_IDS['monthly'],
            'price': 4.99,
            'duration': '1 month',
            'name': 'Premium Monthly Membership'
        },
        'yearly': {
            'id': SUBSCRIPTION_PRODUCT_IDS['yearly'],
            'price': 39.99,
            'duration': '1 year',
            'name': 'Premium Yearly Membership',
            'savings': '33%'
        },
        'family': {
            'id': SUBSCRIPTION_PRODUCT_IDS['family'],
            'price': 7.99,
            'duration': '1 month',
            'name': 'Premium Family Membership',
            'family_sharing': True
        }
    }

    html = render_template(
        "unified_menu.html",
        timestamp=timestamp,
        registration_billing_mode=billing_mode,
        subscription_monthly_usd=monthly_fee,
        subscription_trial_days=trial_days,
        subscription_intro_price_usd=intro_price,
        subscription_intro_months=intro_months,
        subscription_product_id=subscription_product_id,
        subscription_products=subscription_products,
        is_premium=is_premium,
        avatar_product_ids=avatar_product_ids
    )
    resp = make_response(html)
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    return resp

@app.route("/__test_home")
def __test_home():
    """Ultra-minimal home variant for debugging blank/403 issues.

    Returns plain HTML without template logic to isolate external middleware / WAF
    interference. If this returns 200 while `/` returns 403, the blockage is not
    in Flask route code but an upstream rule targeting the root path specifically.
    """
    try:
        from flask import make_response
        body = """<!doctype html><html><head><title>BeeSmart Test Home</title></head>
        <body style='font-family:Arial,sans-serif;padding:2rem;'>
        <h1>BeeSmart Test Home ✅</h1>
        <p>If you can see this, Flask routing works. Root path blockage likely external.</p>
        <p>Timestamp: %s</p>
    <img src='/static/BeeSmartCrestLogo1.png' alt='Logo' style='max-width:300px;'>
        </body></html>""" % (int(time.time()))
        resp = make_response(body)
        resp.headers["Cache-Control"] = "no-store, max-age=0"
        return resp
    except Exception as e:
        return f"Test home error: {e}", 500

@app.after_request
def _debug_root_status(resp):
    """Log status codes for root path to aid 403 diagnostics without altering response."""
    try:
        if request.path == '/':
            print(f"DEBUG AFTER_REQUEST / status={resp.status_code}")
        # Apply aggressive no-cache headers for all API endpoints to prevent stale wordbank / quiz state.
        # This consolidates front-end cache busting with server guarantees (see manual upload race condition notes).
        if request.path.startswith('/api/'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, max-age=0, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
    except Exception:
        pass
    return resp

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
        # Check if quiz is completed - reset if so
        idx = state.get('idx', 0)
        order = state.get('order', [])
        if idx >= len(order):
            print(f"DEBUG /quiz: Quiz completed (idx={idx}, total={len(order)}) - resetting for new attempt")
            init_quiz_state()
        else:
            print(f"DEBUG /quiz: Using existing quiz state - idx={idx}, total={len(order)}")
        
    print(f"DEBUG /quiz: Rendering quiz.html with {len(wordbank)} words")
    
    # Cache busting timestamp
    timestamp = int(time.time() * 1000)
    
    # Pass user information if logged in
    user_name = None
    if current_user.is_authenticated:
        user_name = current_user.display_name
        print(f"DEBUG /quiz: User logged in as {user_name}")
    
    return render_template("quiz.html", user_name=user_name, timestamp=timestamp)

@app.route("/battle/<battle_code>")
@login_required
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
@login_required
def battles_list():
    """Battle of the Bees - Live battles listing page"""
    timestamp = int(time.time())
    return render_template("battles.html", timestamp=timestamp)

@app.route("/upload")
def upload_page():
    """Upload word lists page"""
    return render_template("upload.html")

@app.route("/word-lists")
def word_lists_page():
    """Dedicated word lists management page - robust and dynamic!"""
    return render_template("word_lists.html")

@app.route("/debug/word-lists-version")
def debug_word_lists_version():
    """Debug endpoint to verify which version of word_lists.html is deployed"""
    import os
    import hashlib
    
    try:
        template_path = os.path.join(app.template_folder, 'word_lists.html')
        if os.path.exists(template_path):
            with open(template_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                file_size = len(content)
                line_count = content.count(b'\n') + 1
            
            # Check for new design markers
            has_hive_stats = b'Hive Stats Bar' in content
            has_floating_bee = b'floating-bee' in content
            has_honey_gradient = b'linear-gradient(135deg, #FFE5B4' in content
            has_bounce_animation = b'@keyframes bounce' in content
            
            return jsonify({
                'status': 'NEW VERSION ✅' if (has_hive_stats and has_floating_bee) else 'OLD VERSION ❌',
                'file_hash': file_hash,
                'file_size_bytes': file_size,
                'line_count': line_count,
                'expected_lines': '~1620',
                'features_detected': {
                    'hive_stats_bar': has_hive_stats,
                    'floating_bee_animation': has_floating_bee,
                    'honey_gradient_background': has_honey_gradient,
                    'bounce_animation': has_bounce_animation
                },
                'deployment_check': 'PASS' if all([has_hive_stats, has_floating_bee, has_honey_gradient, has_bounce_animation]) else 'FAIL',
                'recommendation': 'Hard refresh browser (Ctrl+Shift+R)' if file_size > 30000 else 'Redeploy from Git'
            })
        else:
            return jsonify({
                'status': 'ERROR',
                'error': 'Template file not found',
                'template_path': template_path
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500

@app.route("/magical_quiz")
def magical_quiz_page():
    """Legacy route - redirects to main quiz"""
    return redirect("/quiz")

@app.route("/health")
def health_check():
    """Ultra-simple health check for Railway - always returns 200"""
    return jsonify({"status": "ok", "version": "1.6"}), 200

@app.route("/health/iap")
def health_iap():
    """IAP health and configuration status for ops visibility."""
    try:
        mock = IAP_MOCK_MODE
        mode = (os.getenv('IAP_VERIFICATION_MODE') or ('mock' if mock else 'live_strict')).strip().lower()

        # Apple config
        apple_missing = []
        apple_keys = {
            'APPLE_ISSUER_ID': os.getenv('APPLE_ISSUER_ID'),
            'APPLE_KEY_ID': os.getenv('APPLE_KEY_ID'),
            'APPLE_APP_BUNDLE_ID': os.getenv('APPLE_APP_BUNDLE_ID'),
        }
        for k, v in apple_keys.items():
            if not v:
                apple_missing.append(k)
        has_priv = bool(os.getenv('APPLE_PRIVATE_KEY') or os.getenv('APPLE_PRIVATE_KEY_PATH'))
        if not has_priv:
            apple_missing.append('APPLE_PRIVATE_KEY or APPLE_PRIVATE_KEY_PATH')
        apple_configured = (len(apple_missing) == 0)
        try:
            import jwt  # noqa: F401
            import requests  # noqa: F401
            import cryptography  # noqa: F401
            apple_deps_ok = True
        except Exception:
            apple_deps_ok = False

        # Google config
        google_missing = []
        if not os.getenv('GOOGLE_PLAY_PACKAGE_NAME'):
            google_missing.append('GOOGLE_PLAY_PACKAGE_NAME')
        if not (os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT') or os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT_PATH')):
            google_missing.append('GOOGLE_PLAY_SERVICE_ACCOUNT or GOOGLE_PLAY_SERVICE_ACCOUNT_PATH')
        google_configured = (len(google_missing) == 0)
        try:
            from google.oauth2 import service_account  # noqa: F401
            from googleapiclient.discovery import build  # noqa: F401
            google_deps_ok = True
        except Exception:
            google_deps_ok = False

        return jsonify({
            "status": "ok",
            "version": "1.6",
            "iap": {
                "mock": bool(mock),
                "verification_mode": mode,
                "apple": {
                    "configured": apple_configured,
                    "missing": apple_missing,
                    "deps_ok": apple_deps_ok,
                    "env": (os.getenv('APPLE_ENV') or 'Production')
                },
                "google": {
                    "configured": google_configured,
                    "missing": google_missing,
                    "deps_ok": google_deps_ok
                }
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# PWA service worker - serve from root scope so it controls the whole app
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

# Well-known endpoints for app links / universal links
@app.route('/.well-known/apple-app-site-association')
def aasa_file():
    # Served without .json extension and with JSON content
    return send_from_directory('static/.well-known', 'apple-app-site-association', mimetype='application/json')

@app.route('/.well-known/assetlinks.json')
def assetlinks_file():
    return send_from_directory('static/.well-known', 'assetlinks.json', mimetype='application/json')

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

# ✅ TEST ENDPOINT REMOVED - No external dictionary API
# The app now uses only Simple English Wiktionary (50K+ words built-in)
# For testing definitions, use /api/wordbank or Random Words feature

# --- Random Play Helper Functions -------------------------------------------
def calculate_word_difficulty(word: str) -> int:
    """
    Calculate difficulty level (1-5) for a word based on multiple factors.
    Enhanced algorithm for unique and challenging spelling experience.
    
    1 = Easy (3-4 letters, common patterns, phonetic)
    2 = Medium-Easy (5-6 letters, mostly phonetic)
    3 = Medium (7-8 letters, some tricky patterns)
    4 = Medium-Hard (9-11 letters, complex patterns, silent letters)
    5 = Hard (12+ letters, very complex, multiple tricks)
    """
    word_lower = word.lower()
    length = len(word_lower)
    
    # Base difficulty from length (revised scale)
    if length <= 4:
        base_difficulty = 1.0
    elif length <= 6:
        base_difficulty = 2.0
    elif length <= 8:
        base_difficulty = 3.0
    elif length <= 11:
        base_difficulty = 4.0
    else:
        base_difficulty = 5.0
    
    # Complexity scoring system
    complexity_score = 0.0
    
    # ══════════════════════════════════════════════════════════════
    # VERY DIFFICULT PATTERNS (+1.5 each)
    # ══════════════════════════════════════════════════════════════
    very_hard_patterns = [
        'ough',    # tough, through, bough (multiple pronunciations)
        'eigh',    # eight, weigh, neighbor
        'queue',   # unique spelling
        'pneum',   # pneumonia, pneumatic
        'psych',   # psychology, psychic
        'rrhea',   # diarrhea
        'rrh',     # hemorrhage, catarrh
        'phth',    # ophthalmology
        'chth',    # chthonic
    ]
    for pattern in very_hard_patterns:
        if pattern in word_lower:
            complexity_score += 1.5
    
    # ══════════════════════════════════════════════════════════════
    # HARD PATTERNS (+1.0 each)
    # ══════════════════════════════════════════════════════════════
    hard_patterns = [
        'tion',    # nation, station
        'sion',    # mansion, tension
        'ious',    # various, curious
        'eous',    # gorgeous, courteous
        'ough',    # though, thought
        'augh',    # laugh, taught
        'eigh',    # sleigh, freight
        'ign',     # sign, design, foreign
        'sce',     # scene, science
        'tch',     # match, watch
        'dge',     # bridge, edge
        'ance',    # dance,rance
        'ence',    # fence, science
    ]
    for pattern in hard_patterns:
        if pattern in word_lower:
            complexity_score += 1.0
    
    # ══════════════════════════════════════════════════════════════
    # SILENT LETTERS (+0.7 each)
    # ══════════════════════════════════════════════════════════════
    silent_patterns = [
        'kn',      # knife, know
        'gn',      # gnome, sign
        'wr',      # write, wrong
        'mb',      # climb, comb
        'gh',      # night, thought (silent or /f/)
        'ph',      # phone, elephant
        'pn',      # pneumonia
        'ps',      # psychology
        'pt',      # pterodactyl, receipt
        'rh',      # rhythm, rhyme
        'wh',      # who, whole (sometimes)
    ]
    for pattern in silent_patterns:
        if pattern in word_lower:
            complexity_score += 0.7
    
    # ══════════════════════════════════════════════════════════════
    # VOWEL COMBINATIONS (+0.5 each)
    # ══════════════════════════════════════════════════════════════
    vowel_combos = [
        'ea',      # bread vs bead (different sounds)
        'ie',      # field vs friend
        'ei',      # receive, weird
        'ou',      # through, tough, cough (many sounds)
        'oo',      # book vs boot
        'au',      # autumn, laugh
        'ai',      # rain, said
        'ay',      # way, says
    ]
    for pattern in vowel_combos:
        if pattern in word_lower:
            complexity_score += 0.5
    
    # ══════════════════════════════════════════════════════════════
    # STRUCTURAL COMPLEXITY
    # ══════════════════════════════════════════════════════════════
    
    # Double letters (+0.3 each occurrence)
    import re
    double_count = len(re.findall(r'(.)\1', word_lower))
    complexity_score += double_count * 0.3
    
    # Triple letters (rare but very tricky, +0.8)
    if re.search(r'(.)\1\1', word_lower):
        complexity_score += 0.8
    
    # Uncommon letters (+0.4 each)
    uncommon_letters = set('qxzj')
    uncommon_count = sum(1 for letter in word_lower if letter in uncommon_letters)
    complexity_score += uncommon_count * 0.4
    
    # Consonant clusters (3+ consonants together, +0.5)
    consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{3,}', word_lower)
    complexity_score += len(consonant_clusters) * 0.5
    
    # ══════════════════════════════════════════════════════════════
    # FINAL DIFFICULTY CALCULATION
    # ══════════════════════════════════════════════════════════════
    
    # Apply complexity adjustments
    final_difficulty = base_difficulty
    
    if complexity_score >= 3.0:
        final_difficulty += 2.0
    elif complexity_score >= 2.0:
        final_difficulty += 1.5
    elif complexity_score >= 1.0:
        final_difficulty += 1.0
    elif complexity_score >= 0.5:
        final_difficulty += 0.5
    
    # Cap at 1-5 range
    final_difficulty = max(1.0, min(5.0, final_difficulty))
    
    # Round to nearest integer
    return int(round(final_difficulty))


def get_random_words_by_difficulty(difficulty: int, count: int = 10) -> List[Dict[str, str]]:
    """
    Get random words from Simple Wiktionary filtered by difficulty level.
    Enhanced with quality filters for unique, challenging spelling experience.
    
    Args:
        difficulty: Level 1-5 (1=easy, 5=hard)
        count: Number of words to return (default 10)
    
    Returns:
        List of word dictionaries with word, sentence, and hint fields
    """
    # ✅ Lazy-load Simple Wiktionary on first use (improves Railway startup time)
    wiktionary = ensure_simple_wiktionary_loaded()
    
    if not wiktionary:
        raise ValueError("Simple Wiktionary not loaded - cannot generate random words")
    
    # ══════════════════════════════════════════════════════════════
    # QUALITY FILTERS - Skip overly simple/common words
    # ══════════════════════════════════════════════════════════════
    overly_common_words = {
        'the', 'and', 'or', 'but', 'if', 'for', 'of', 'to', 'in', 'on', 'at', 'is', 'it',
        'be', 'was', 'are', 'as', 'by', 'he', 'she', 'we', 'you', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'his', 'our', 'your', 'their', 'this', 'that', 'these', 'those',
        'a', 'an', 'am', 'i', 'do', 'go', 'so', 'no', 'up', 'out', 'get', 'got', 'see', 'saw',
        'cat', 'dog', 'boy', 'girl', 'man', 'can', 'run', 'big', 'red', 'hot', 'cold', 'yes'
    }
    
    # Filter words by difficulty with quality checks
    words_at_difficulty = []
    
    print(f"🎲 Searching for {count} words at difficulty level {difficulty}...")
    
    for word, data in wiktionary.items():
        word_lower = word.lower()
        
        # ══════════════════════════════════════════════════════════════
        # SKIP CONDITIONS (quality filters)
        # ══════════════════════════════════════════════════════════════
        
        # Skip very short words unless difficulty is 1
        if len(word) < 3 and difficulty > 1:
            continue
        
        # Skip words with non-alphabetic characters
        if not word.isalpha():
            continue
        
        # Skip overly common words (except for difficulty 1)
        if difficulty > 1 and word_lower in overly_common_words:
            continue
        
        # Skip proper nouns (capitalized words from dictionary, basic check)
        if word[0].isupper() and len(word) > 1:
            continue
        
        # Skip extremely long words (over 18 letters - likely compound/technical)
        if len(word) > 18:
            continue
        
        # Must have a meaningful definition
        if not data.get("definition") or len(data.get("definition", "")) < 10:
            continue
        
        # ══════════════════════════════════════════════════════════════
        # DIFFICULTY MATCHING
        # ══════════════════════════════════════════════════════════════
        word_difficulty = calculate_word_difficulty(word)
        
        # For difficulty 1-2: Accept exact match only (keep it simple)
        # For difficulty 3-5: Accept ±1 level for variety
        tolerance = 1 if difficulty >= 3 else 0
        
        if abs(word_difficulty - difficulty) <= tolerance:
            # Calculate uniqueness score (words with interesting patterns get priority)
            uniqueness = 0
            if any(p in word_lower for p in ['ough', 'eigh', 'queue', 'pneum', 'psych']):
                uniqueness += 3
            if any(p in word_lower for p in ['tion', 'sion', 'ious', 'eous', 'ign', 'sce']):
                uniqueness += 2
            if any(p in word_lower for p in ['kn', 'gn', 'wr', 'mb', 'ph', 'gh']):
                uniqueness += 1
            
            words_at_difficulty.append({
                "word": word,
                "data": data,
                "exact_match": word_difficulty == difficulty,
                "uniqueness": uniqueness
            })
    
    # ══════════════════════════════════════════════════════════════
    # PRIORITIZED SELECTION
    # ══════════════════════════════════════════════════════════════
    
    # Sort by: exact match first, then by uniqueness, then random
    exact_matches = [w for w in words_at_difficulty if w["exact_match"]]
    close_matches = [w for w in words_at_difficulty if not w["exact_match"]]
    
    # Sort each group by uniqueness (descending)
    exact_matches.sort(key=lambda x: x["uniqueness"], reverse=True)
    close_matches.sort(key=lambda x: x["uniqueness"], reverse=True)
    
    print(f"📊 Found {len(exact_matches)} exact matches, {len(close_matches)} close matches")
    
    # Randomly select words (prefer exact matches, but add randomness to top candidates)
    selected = []
    
    # From exact matches: take top 50% by uniqueness, then shuffle those
    if exact_matches:
        top_exact = exact_matches[:max(len(exact_matches) // 2, count * 2)]
        random.shuffle(top_exact)
        selected = top_exact[:count]
    
    # If not enough, add from close matches
    if len(selected) < count and close_matches:
        top_close = close_matches[:max(len(close_matches) // 2, count * 2)]
        random.shuffle(top_close)
        remaining_needed = count - len(selected)
        selected.extend(top_close[:remaining_needed])
    
    # ══════════════════════════════════════════════════════════════
    # FORMAT RESULTS
    # ══════════════════════════════════════════════════════════════
    result = []
    for item in selected[:count]:
        word = item["word"]
        data = item["data"]
        
        definition = data.get("definition", "")
        example = data.get("example", "")
        
        # Create kid-friendly sentence from definition and example
        if example and len(example) > 10:
            # Blank out the word in the example
            sentence = f"{definition}. Example: {_blank_word(example, word)}"
        else:
            # Use definition with creative prompt
            sentence = f"{definition}. Can you spell this {len(word)}-letter word?"
        
        # Create informative hint
        hint_parts = [f"Level {difficulty} word"]
        if len(word) >= 8:
            hint_parts.append(f"{len(word)} letters")
        if item["uniqueness"] >= 2:
            hint_parts.append("has tricky spelling patterns")
        
        result.append({
            "word": word,
            "sentence": sentence,
            "hint": " - ".join(hint_parts) + "."
        })
    
    print(f"✅ Selected {len(result)} quality words at difficulty {difficulty}")
    return result

# --- Routes: API -------------------------------------------------------------
@app.route("/api/random-words", methods=["POST"])
@login_required
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
        
        # Generate random words (authenticated users only)
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

# DEPRECATED ROUTE - Moved to battles_api.py blueprint
# @app.route("/api/battles/join", methods=["POST"])
def api_join_battle_DEPRECATED():
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

# DEPRECATED ROUTE - Moved to battles_api.py blueprint
# @app.route("/api/battles/<battle_code>/leaderboard", methods=["GET"])
def api_battle_leaderboard_DEPRECATED(battle_code):
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

# DEPRECATED ROUTE - Moved to battles_api.py blueprint
# @app.route("/api/battles/live", methods=["GET"])
def api_battles_live_DEPRECATED():
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

# DEPRECATED ROUTE - Moved to battles_api.py blueprint
# @app.route("/api/battles/<battle_code>/progress", methods=["POST"])
def api_battle_progress_DEPRECATED(battle_code):
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

# DEPRECATED ROUTE - Moved to battles_api.py blueprint
# @app.route("/api/battles/<battle_code>/export", methods=["GET"])
def api_battle_export_DEPRECATED(battle_code):
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
    """
    Returns the ACTUAL current wordbank from session storage.
    NEVER returns defaults - only what user has uploaded/entered.
    If empty, returns [] (empty list) - user must upload their own words.
    """
    # Enhanced debugging for mobile troubleshooting
    storage_id = session.get("wordbank_storage_id")
    words = get_wordbank()
    was_cleared = session.get("wordbank_cleared", False)
    has_uploaded = session.get("has_uploaded_once", False)
    
    print(f"DEBUG /api/wordbank: session_id={session.get('session_id', 'NONE')}, "
          f"storage_id={storage_id}, word_count={len(words)}, "
          f"was_cleared={was_cleared}, has_uploaded={has_uploaded}, "
          f"session_keys={list(session.keys())}, "
          f"user_agent={request.headers.get('User-Agent', 'UNKNOWN')[:50]}")
    
    # Check if storage exists in WORD_STORAGE (this is NOT a default - it's real user data)
    if storage_id:
        with WORD_STORAGE_LOCK:
            stored_words = WORD_STORAGE.get(storage_id, [])
            print(f"DEBUG /api/wordbank: WORD_STORAGE contains {len(stored_words)} words for storage_id={storage_id}")
            if len(stored_words) > 0:
                print(f"ℹ️ /api/wordbank: Returning {len(stored_words)} REAL words from user's session (NOT defaults)")
            else:
                print(f"ℹ️ /api/wordbank: Returning 0 words - wordbank is empty (no defaults loaded)")
    else:
        print(f"ℹ️ /api/wordbank: No storage_id - fresh session with no words uploaded yet")
    
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
        
        update_upload_progress(session_id, "enriching", "Bees are pre-loading definitions from internal dictionary...", "bees_fetching_definitions", 55)
        
        # Enhanced enrichment with progress tracking and VALIDATION
        enriched = []
        enrichment_errors = []
        
        for i, r in enumerate(deduped):
            word = r["word"]
            sentence = r.get("sentence", "").strip()
            hint = r.get("hint", "").strip()
            
            progress = 55 + int((i + 1) / len(deduped) * 35)  # 55-90%
            update_upload_progress(session_id, "enriching", f"📖 Pre-loading definition: {word}", "bees_fetching_definitions", progress, word)
            
            # ✅ ALWAYS enrich with internal dictionary for consistency
            # This ensures all words have complete definitions BEFORE quiz starts
            auto_definition = get_word_info(word)
            
            # Use user-provided sentence if available, otherwise use auto-generated
            final_sentence = sentence if sentence else auto_definition
            
            # VALIDATE: Check if definition is real (not placeholder or empty)
            if not final_sentence or final_sentence.strip() == "":
                enrichment_errors.append(f"No definition found for '{word}'")
                print(f"ERROR: Failed to get definition for '{word}'")
                final_sentence = f"Practice spelling this word: {word}"  # Emergency fallback
            
            enriched.append({
                "word": word,
                "sentence": final_sentence,
                "hint": hint if hint else ""  # Preserve user hint or use empty string
            })
            
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
        
        # EXTRA FILTER: Remove any items whose definition/hint contains inappropriate content
        filtered_enriched, blocked_defs = _filter_records_excluding_inappropriate_text(enriched)
        if blocked_defs:
            print(f"⚠️ Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

        # CRITICAL VALIDATION: Check all definitions before quiz can start
        print("DEBUG: Validating wordbank definitions before storing...")
        is_valid, validation_error = validate_wordbank_definitions(filtered_enriched)
        
        if not is_valid:
            print(f"ERROR: Wordbank validation failed: {validation_error}")
            complete_upload_session(session_id, False, f"Definition Check Failed: {validation_error}")
            return
        
        update_upload_progress(session_id, "finalizing", "Bees are storing words in the hive...", "bees_storing", 95)
        
        # Store the wordbank and initialize quiz (USER UPLOAD)
        set_wordbank(filtered_enriched, is_user_upload=True)
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
        
        update_upload_progress(session_id, "completed", f"✅ {len(filtered_enriched)} words with pre-loaded definitions ready!", "bees_celebrating", 100)
        complete_upload_session(session_id, True, f"🐝 Amazing! {len(filtered_enriched)} words enriched with definitions - quiz starts instantly!")
        
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
                    # Guests cannot use OCR-based image upload
                    if not current_user.is_authenticated:
                        return jsonify({"error": "Login required for image uploads (OCR)", "auth_required": True}), 403
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

    # Auto-enrich words with definitions (INTERNAL ONLY - NO EXTERNAL API CALLS)
    # Uses: 1) Simple Wiktionary (50K+ words), 2) Dictionary cache, 3) Smart fallback
    print(f"📚 Enriching {len(deduped)} words using built-in dictionary...")
    import time
    enrichment_start = time.time()
    
    # PRE-LOAD dictionary ONCE to avoid repeated lazy-loading
    global DICTIONARY_CACHE
    if not DICTIONARY_CACHE:
        DICTIONARY_CACHE = load_dictionary_cache()
    ensure_simple_wiktionary_loaded()  # Pre-load Wiktionary once
    
    enriched = []
    for r in deduped:
        word = r["word"]
        sentence = r.get("sentence", "").strip()
        hint = r.get("hint", "").strip()
        
        # If no sentence/definition provided, use built-in dictionary
        if not sentence and not hint:
            auto_definition = get_word_info(word)
            enriched.append({
                "word": word,
                "sentence": auto_definition,
                "hint": ""
            })
        else:
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
    print(f"✅ Enrichment completed in {enrichment_time:.2f}s for {len(enriched)} words")
    
    # EXTRA FILTER: Remove any items whose definition/hint contains inappropriate content
    enriched, blocked_defs = _filter_records_excluding_inappropriate_text(enriched)
    if blocked_defs:
        print(f"⚠️ /api/upload: Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

    deduped = enriched

    if len(deduped) > MAX_RECORDS:
        deduped = deduped[:MAX_RECORDS]

    # CRITICAL VALIDATION: Check all definitions before quiz can start
    is_valid, validation_error = validate_wordbank_definitions(deduped)
    
    if not is_valid:
        print(f"❌ Wordbank validation failed: {validation_error}")
        return jsonify({"error": validation_error}), 400
    
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
        print("⚠️ Quiz state failed to persist! Retrying init...")
        init_quiz_state()
        session.modified = True
        time.sleep(0.2)
    
    # Verify wordbank was set correctly
    verify_wb = get_wordbank()
    if len(verify_wb) != len(deduped):
        print(f"⚠️ Wordbank size mismatch! Set {len(deduped)}, got {len(verify_wb)}")
    else:
        print(f"✅ Successfully uploaded {len(deduped)} words")
    
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
        
        # Auto-enrich words with definitions (INTERNAL ONLY - NO EXTERNAL API CALLS)
        # Uses: 1) Simple Wiktionary (50K+ words), 2) Dictionary cache, 3) Smart fallback
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

        # EXTRA FILTER: Remove any items whose definition/hint contains inappropriate content
        enriched, blocked_defs = _filter_records_excluding_inappropriate_text(enriched)
        if blocked_defs:
            print(f"⚠️ /api/upload-manual-words: Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

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
    has_uploaded = session.get("has_uploaded_once", False)
    using_defaults = session.get("using_default_words", False)
    
    print(f"DEBUG /api/next: session_id={session.get('session_id')}, storage_id={storage_id}, "
          f"wordbank_len={len(wb)}, quiz_idx={state['idx'] if state else 'NO_STATE'}, "
          f"has_uploaded_once={has_uploaded}, using_default_words={using_defaults}")
    
    # 🔧 CRITICAL CHECK: Warn if using default words when user has uploaded before
    if using_defaults and has_uploaded:
        print("⚠️⚠️⚠️ CRITICAL WARNING /api/next: Using DEFAULT words but has_uploaded_once=True!")
        print("⚠️⚠️⚠️ This indicates session loss - user's uploaded words were lost!")
        print(f"⚠️⚠️⚠️ Session keys: {list(session.keys())}")
    
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
            # finished - extract incorrect words for study review
            incorrect_words = []
            for entry in state.get("history", []):
                if not entry.get("correct") and not entry.get("skipped"):
                    incorrect_words.append({
                        "word": entry.get("word", ""),
                        "user_answer": entry.get("user_input", "")
                    })
            
            return jsonify({
                "done": True,
                "summary": {
                    "total": len(order),
                    "correct": state["correct"],
                    "incorrect": state["incorrect"],
                    "streak": state["streak"],
                    "history": state["history"],
                    "incorrect_words": incorrect_words
                }
            })

    word_rec = wb[order[idx]]
    word = word_rec.get("word", "")
    
    # ---------------- Quiz content assembly & enrichment ----------------
    # Separate definition vs. sample sentence; never substitute sentence for definition.
    def _parse_enriched(raw: str) -> tuple[str, str]:
        """Split combined enrichment into (definition, sentence).
        Expected format contains 'Fill in the blank:'; if missing, treat entire string as definition.
        Returned values are blanked for safety.
        """
        if not raw:
            return "", ""
        if "Fill in the blank:" in raw:
            before, after = raw.split("Fill in the blank:", 1)
            return before.strip(), after.strip()
        return raw.strip(), ""

    sentence = (word_rec.get("sentence") or "").strip()
    hint = (word_rec.get("hint") or "").strip()
    existing_def = (word_rec.get("definition") or "").strip()

    # Blanking + sanitization safety for existing fields
    sentence = sanitize_kid_friendly_text(_blank_word(sentence, word))
    hint = sanitize_kid_friendly_text(_blank_word(hint, word))
    existing_def = sanitize_kid_friendly_text(_blank_word(existing_def, word))

    definition = existing_def
    definition_source = "definition_field" if existing_def else "none"
    has_definition = bool(definition)

    # If we lack a definition, attempt live dictionary enrichment (even if we already have a sentence).
    if not has_definition:
        try:
            enriched = get_word_info(word)  # returns combined formatted string
            parsed_def, parsed_sentence = _parse_enriched(enriched)
            parsed_def = sanitize_kid_friendly_text(_blank_word(parsed_def, word))
            parsed_sentence = sanitize_kid_friendly_text(_blank_word(parsed_sentence, word))

            # Adopt parsed definition if non-empty
            if parsed_def:
                definition = parsed_def
                definition_source = "dictionary_lookup"
                has_definition = True
            # Adopt sentence if we didn't already have one
            if parsed_sentence and not sentence:
                sentence = parsed_sentence
            # Persist enriched fields back to word record for future reuse in session
            updated = False
            if sentence and not word_rec.get("sentence"):
                word_rec["sentence"] = sentence
                updated = True
            if definition and not word_rec.get("definition"):
                word_rec["definition"] = definition
                updated = True
            if updated:
                try:
                    set_wordbank(wb, is_user_upload=session.get("has_uploaded_once", False))
                except Exception as _persist_err:
                    print(f"⚠️ Failed to persist enrichment for '{word}': {_persist_err}")
        except Exception as ex:
            print(f"⚠️ Dictionary enrichment failed for '{word}': {ex}")
            if not definition:
                definition = "Listen carefully and spell the word you hear."
                definition_source = "fallback"
                has_definition = False

    # If still no definition but we have a hint, use hint as gentle contextual prompt.
    if not has_definition and hint:
        definition = f"Hint: {hint}"
        definition_source = "hint"
        has_definition = True

    # Final blanking + sanitization pass (idempotent)
    definition = sanitize_kid_friendly_text(_blank_word(definition or "", word))
    sentence = sanitize_kid_friendly_text(_blank_word(sentence or "", word))

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

    # ✅ OPTIMIZED: Use pre-enriched definitions from word_rec (enriched during upload)
    # Only call get_word_info() if sentence is completely missing (rare edge case)
    definition = word_rec.get("sentence", "").strip()
    
    if not definition:
        # Fallback: Try to get definition from internal dictionary (fast, cached)
        try:
            definition = get_word_info(current_word)
        except:
            definition = "Please spell the word you hear."
    
    # Ensure word is blanked and content sanitized
    if current_word:
        definition = sanitize_kid_friendly_text(_blank_word(definition, current_word))
    
    # Fallback to hint if definition is still empty
    if not definition or definition.startswith("Definition not available"):
        if word_rec.get("hint"):
            definition = f"Hint: {word_rec['hint']}"
        else:
            definition = "Please spell the word you hear."

    word_lower = current_word.lower()
    cached_entry = DICTIONARY_CACHE.get(word_lower, {}) if current_word else {}
    phonetic_lookup = cached_entry.get("phonetic", "")
    spelled_out = build_phonetic_spelling(current_word)

    # Also sanitize sentence and hint for safety
    safe_sentence = sanitize_kid_friendly_text(_blank_word(word_rec.get("sentence", ""), current_word))
    safe_hint = sanitize_kid_friendly_text(_blank_word(word_rec.get("hint", ""), current_word))

    return jsonify({
        "word": current_word,
        "definition": definition,
        "sentence": safe_sentence,
        "hint": safe_hint,
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
    current_word = word_rec.get("word", "")
    return jsonify({
        "hint": sanitize_kid_friendly_text(_blank_word(word_rec.get("hint", ""), current_word)),
        "sentence": sanitize_kid_friendly_text(_blank_word(word_rec.get("sentence", ""), current_word))
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

def check_newly_unlocked_avatars(old_honey_points, new_honey_points):
    """
    Check if user unlocked any new avatars by comparing old vs new honey points.
    Returns list of newly unlocked avatar objects with name, slug, description, thumbnail.
    """
    try:
        from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked
        from models import Avatar

        newly_unlocked = []

        # Use AVATAR_CATALOG directly (AVATARS_CATALOG alias may not yet be set here)
        for avatar_config in AVATAR_CATALOG:
            avatar_slug = avatar_config.get('id')
            if not avatar_slug:
                continue

            # Check if avatar was locked before but unlocked now
            old_status = check_avatar_unlocked(avatar_slug, old_honey_points, [])
            new_status = check_avatar_unlocked(avatar_slug, new_honey_points, [])

            # Skip if was already unlocked or still locked
            if old_status.get('unlocked') or not new_status.get('unlocked'):
                continue

            # Get avatar details from database
            avatar = Avatar.query.filter_by(slug=avatar_slug, is_active=True).first()
            if not avatar:
                continue

            # Build thumbnail URL
            base_path = f"/static/assets/avatars/{avatar.folder_path}"
            thumbnail_url = f"{base_path}/{avatar.thumbnail_file}" if avatar.thumbnail_file else None

            newly_unlocked.append({
                'slug': avatar.slug,
                'name': avatar.name,
                'description': avatar.description or f'{avatar.name} is now available!',
                'thumbnail': thumbnail_url
            })

        return newly_unlocked

    except Exception as e:
        print(f"⚠️ Error checking newly unlocked avatars: {e}")
        return []

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
    "ts": datetime.now(timezone.utc).isoformat(),
        "skipped": skip_requested
    })
    session[QUIZ_STATE_KEY] = state

    # Save to database for ALL users (authenticated + guests)
    user_obj = get_or_create_guest_user()
    if user_obj and state.get("db_session_id"):
        try:
            # Save individual word result with detailed points breakdown
            quiz_result = QuizResult(
                session_id=state["db_session_id"],
                user_id=user_obj.id,
                word=correct_spelling,
                is_correct=is_correct,
                user_answer=user_input,
                correct_spelling=correct_spelling,
                time_taken_seconds=(elapsed_ms / 1000.0) if elapsed_ms else None,
                input_method=method,
                points_earned=points_earned if is_correct else 0,
                base_points=points_breakdown.get("base", 0) if is_correct else 0,
                time_bonus=points_breakdown.get("time_bonus", 0) if is_correct else 0,
                streak_bonus=points_breakdown.get("streak_bonus", 0) if is_correct else 0,
                first_attempt_bonus=points_breakdown.get("first_attempt", 0) if is_correct else 0,
                no_hints_bonus=points_breakdown.get("no_hints", 0) if is_correct else 0,
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
                
                # 🍯 Calculate total points from all sources
                word_points = state.get("session_points", 0)  # Points from answering words correctly
                badge_points = sum(b["points"] for b in badges_unlocked)  # Badge bonus points
                extra_bonus = state.get("extra_points", 0)  # Any additional bonus points
                
                # Store detailed breakdown
                quiz_session.points_earned = word_points  # Word answer points (already includes time/streak bonuses)
                quiz_session.badge_bonus_points = badge_points  # Badge achievement points
                quiz_session.extra_points = extra_bonus  # Any extra/special bonus points
                
                # Calculate cumulative total (all points combined)
                total_points = word_points + badge_points + extra_bonus
                quiz_session.total_points = total_points  # Store cumulative total
                
                print(f"📊 POINTS BREAKDOWN: Words={word_points}, Badges={badge_points}, Extra={extra_bonus}, TOTAL={total_points}")
                
                quiz_session.complete_session()
                
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
                newly_unlocked_avatars = []
                if current_user.is_authenticated:
                    # 🎯 Check for level up BEFORE updating points
                    old_lifetime_points = current_user.total_lifetime_points or 0
                    new_lifetime_points = old_lifetime_points + total_points
                    level_up_data = check_level_up(old_lifetime_points, new_lifetime_points)
                    
                    # 🐝 Check for newly unlocked avatars based on honey points
                    from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked
                    old_honey_points = current_user.honey_points or 0
                    new_honey_points = old_honey_points + total_points
                    current_user.honey_points = new_honey_points
                    
                    purchased_avatars = current_user.purchased_avatars or []
                    
                    # Find avatars that were locked before but are now unlocked
                    # Iterate the catalog directly; alias may not be available yet
                    for avatar_data in AVATAR_CATALOG:
                        avatar_id = avatar_data.get('id')
                        # Check if avatar was locked with old points but unlocked with new points
                        old_unlock_result = check_avatar_unlocked(avatar_id, old_honey_points, purchased_avatars)
                        new_unlock_result = check_avatar_unlocked(avatar_id, new_honey_points, purchased_avatars)
                        
                        was_locked = not old_unlock_result.get('unlocked', False)
                        is_now_unlocked = new_unlock_result.get('unlocked', False)
                        
                        if was_locked and is_now_unlocked:
                            newly_unlocked_avatars.append({
                                'id': avatar_id,
                                'name': avatar_data.get('name', avatar_id),
                                'thumbnail': avatar_data.get('thumbnail', ''),
                                'unlock_points': avatar_data.get('unlock_points', 0),
                                'backstory': avatar_data.get('backstory', ''),
                                'message': f"Congratulations! You've unlocked {avatar_data.get('name')}! 🎉"
                            })
                    
                    if newly_unlocked_avatars:
                        print(f"🐝 User unlocked {len(newly_unlocked_avatars)} new avatar(s): {[a['name'] for a in newly_unlocked_avatars]}")
                    
                    # Update stats
                    current_user.total_quizzes_completed = (current_user.total_quizzes_completed or 0) + 1
                    current_user.total_lifetime_points = new_lifetime_points
                    if quiz_session.best_streak > (current_user.best_streak or 0):
                        current_user.best_streak = quiz_session.best_streak
                    
                    # 📊 Update GPA and average accuracy
                    current_user.update_gpa_and_accuracy()
                    
                    print(f"📈 STATS UPDATE: User={current_user.username}, Quizzes={current_user.total_quizzes_completed}, Points={current_user.total_lifetime_points}, Honey Points={current_user.honey_points}, GPA={current_user.cumulative_gpa}, Avg Accuracy={current_user.average_accuracy}%")
                    
                    if level_up_data:
                        print(f"🎉 LEVEL UP! {level_up_data['old_level']['tier']} → {level_up_data['new_level']['tier']}")
                    
                    print(f"✅ Quiz completed! Grade: {quiz_session.grade}, Session Points: {quiz_session.points_earned}, Total Points: {total_points}, User Lifetime: {current_user.total_lifetime_points}")
                else:
                    print(f"✅ Guest quiz completed! Grade: {quiz_session.grade}, Points: {total_points}")
                
                # Save level up data to session for frontend
                if level_up_data:
                    state["level_up"] = level_up_data
                    session[QUIZ_STATE_KEY] = state
                
                # Save newly unlocked avatars to session
                if newly_unlocked_avatars:
                    state["newly_unlocked_avatars"] = newly_unlocked_avatars
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
        "level_up": state.get("level_up") if quiz_complete else None,
        "newly_unlocked_avatars": state.get("newly_unlocked_avatars", []) if quiz_complete else []
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
        quiz_session.session_end = datetime.now(timezone.utc)
        
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

@app.route("/api/add-bonus-points", methods=["POST"])
def api_add_bonus_points():
    """
    Add extra/bonus points to the current quiz session
    Useful for special achievements, milestones, events, etc.
    
    Body JSON: {
        "points": <int>,           # Amount of bonus points to add
        "reason": "<string>",      # Description of why points were awarded
        "category": "<string>"     # Optional: "achievement", "milestone", "event", "special"
    }
    """
    try:
        session.permanent = True
        session.modified = True
        
        payload = request.get_json(force=True)
        bonus_points = int(payload.get("points", 0))
        reason = payload.get("reason", "Bonus points")
        category = payload.get("category", "bonus")
        
        if bonus_points <= 0:
            return jsonify({"error": "Bonus points must be positive"}), 400
        
        state = get_quiz_state()
        if not state:
            return jsonify({"error": "No active quiz session"}), 400
        
        # Add bonus points to session extra_points tracker
        current_extra = state.get("extra_points", 0)
        state["extra_points"] = current_extra + bonus_points
        
        # Also add to session_points for immediate cumulative total
        state["session_points"] = state.get("session_points", 0) + bonus_points
        
        # Track bonus point awards in history
        if "bonus_awards" not in state:
            state["bonus_awards"] = []
        
        state["bonus_awards"].append({
            "points": bonus_points,
            "reason": reason,
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        session[QUIZ_STATE_KEY] = state
        session.modified = True
        
        print(f"🎁 BONUS POINTS AWARDED: +{bonus_points} points for '{reason}' (category: {category})")
        print(f"   New session total: {state['session_points']} points (extra_points: {state['extra_points']})")
        
        return jsonify({
            "success": True,
            "bonus_points_added": bonus_points,
            "reason": reason,
            "category": category,
            "new_session_total": state["session_points"],
            "total_extra_points": state["extra_points"]
        })
        
    except Exception as e:
        print(f"❌ Error adding bonus points: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
    Look up a word using INTERNAL DICTIONARY ONLY (Simple English Wiktionary → Cache → Smart Fallback).
    ✅ NO EXTERNAL API CALLS - All definitions from built-in resources.
    
    Body JSON: { "word": "example" }
    Returns: { "word": "example", "definition": "...", "phonetic": "E X A M P L E", "found": true/false }
    """
    payload = request.get_json(force=True)
    word = (payload.get("word") or "").strip()
    
    if not word:
        return jsonify({"error": "No word provided"}), 400

    # Guest quota: small free allowance per day
    try:
        if not current_user.is_authenticated:
            QUOTA_KEY = "guest_dict_quota_v1"
            quota = session.get(QUOTA_KEY) or {}
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if quota.get("date") != today:
                quota = {"date": today, "count": 0, "limit": 5}
            limit = int(quota.get("limit", 5))
            count = int(quota.get("count", 0))
            if count >= limit:
                reset_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
                return jsonify({
                    "ok": False,
                    "error": "Guest dictionary lookups limit reached. Please register to continue.",
                    "auth_required": True,
                    "limit": limit,
                    "reset_date": reset_at
                }), 403
            else:
                quota["count"] = count + 1
                quota["date"] = today
                session[QUOTA_KEY] = quota
                session.modified = True
    except Exception:
        # Non-fatal if quota logic fails
        pass
    
    # ✅ All lookups use INTERNAL DICTIONARY ONLY (get_word_info uses Simple Wiktionary → Cache → Smart Fallback)
    definition = get_word_info(word)
    phonetic_spelling = build_phonetic_spelling(word)
    word_lower = word.lower()
    
    # Check which internal source provided the definition
    wiktionary = ensure_simple_wiktionary_loaded()
    found_in_wiktionary = wiktionary and word_lower in wiktionary
    found_in_cache = word_lower in DICTIONARY_CACHE
    
    # Determine source (all internal)
    if found_in_wiktionary:
        source = "simple_wiktionary"
    elif found_in_cache:
        source = "internal_cache"
    else:
        source = "smart_fallback"

    return jsonify({
        "word": word,
        "definition": definition,
        "phonetic": phonetic_spelling,
        "found": found_in_wiktionary or found_in_cache,
        "source": source  # ✅ All sources are internal (simple_wiktionary, internal_cache, or smart_fallback)
    })

@app.route("/api/word-info/preload", methods=["POST"])
def api_word_info_preload():
    """
    Preload the built-in dictionary during loading screen.
    This forces Simple Wiktionary to load into memory so word processing is faster.
    Accepts a list of common words to cache definitions for.
    """
    try:
        data = request.get_json() or {}
        words = data.get('words', ['hello', 'world', 'test', 'example', 'dictionary'])
        
        # Force-load Simple Wiktionary into memory
        wiktionary = ensure_simple_wiktionary_loaded()
        preloaded_count = 0
        
        # Pre-cache definitions for common words
        for word in words:
            try:
                # This will cache the definition in DICTIONARY_CACHE
                definition = get_word_info(word)
                if definition:
                    preloaded_count += 1
            except Exception as e:
                print(f"⚠️ Failed to preload '{word}': {e}")
                continue
        
        print(f"✅ Dictionary preloaded: {preloaded_count}/{len(words)} words cached")
        
        return jsonify({
            "success": True,
            "preloaded": preloaded_count,
            "total_requested": len(words),
            "wiktionary_loaded": wiktionary is not None,
            "cache_size": len(DICTIONARY_CACHE)
        })
        
    except Exception as e:
        print(f"❌ Dictionary preload failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "preloaded": 0
        }), 500

@app.route("/api/dictionary/stats", methods=["GET"])
def api_dictionary_stats():
    """Expose internal dictionary/cache performance statistics."""
    try:
        ensure_simple_wiktionary_loaded()
        prefetch_snapshot = {}
        try:
            if 'PREFETCH_METRICS_LOCK' in globals() and 'PREFETCH_METRICS' in globals():
                lock_obj = globals().get('PREFETCH_METRICS_LOCK')
                metrics_obj = globals().get('PREFETCH_METRICS')
                if lock_obj and metrics_obj:
                    with lock_obj:
                        prefetch_snapshot = dict(metrics_obj)
        except Exception as ex:
            print(f"⚠️ Failed snapshotting prefetch metrics: {ex}")
        return jsonify({
            "ok": True,
            "wiktionary_loaded": SIMPLE_WIKTIONARY_LOADED,
            "wiktionary_size": len(SIMPLE_WIKTIONARY) if SIMPLE_WIKTIONARY_LOADED else 0,
            "persistent_cache_size": len(DICTIONARY_CACHE),
            "lru_size": len(WORD_INFO_CACHE),
            "lru_capacity": WORD_INFO_CACHE_MAX,
            "lru_hits": _WORD_INFO_HITS,
            "lru_misses": _WORD_INFO_MISSES,
            "index_built": SIMPLE_WIKTIONARY_INDEX is not None,
            "prefetch_metrics": prefetch_snapshot
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ===============================
# Word Info Prefetch (Progress)
# ===============================
from threading import Thread, Lock
import uuid as _uuid

PREFETCH_JOBS = {}
PREFETCH_JOBS_LOCK = Lock()

# Prefetch performance metrics (aggregate across jobs)
PREFETCH_METRICS_LOCK = Lock()
PREFETCH_METRICS = {
    "total_batches": 0,
    "total_words_processed": 0,
    "last_batch_ms": 0.0,
    "avg_batch_ms": 0.0,
    "total_batch_ms": 0.0,
    "last_prefetch_total_ms": 0.0,
}

def _start_prefetch_job(words, mode='both', storage_id: Optional[str] = None):
    """Create and start a background job to warm up definitions/sentences.
    Returns a job_id string.
    """
    job_id = str(_uuid.uuid4())
    job = {
        'id': job_id,
        'total': len(words),
        'current': 0,
        'done': False,
        'cancelled': False,
        'errors': 0,
        'mode': mode,
        'last_word': None,
    }
    with PREFETCH_JOBS_LOCK:
        PREFETCH_JOBS[job_id] = job

    def worker():
        try:
            start_total = time.time()
            # Use bulk enrichment pattern in small batches to reduce lock churn
            BATCH_SIZE = 25
            total_words = len(words)
            for i in range(0, total_words, BATCH_SIZE):
                with PREFETCH_JOBS_LOCK:
                    if job.get('cancelled'):
                        break
                batch_start = time.time()
                batch = words[i:i+BATCH_SIZE]
                _bulk_map = bulk_word_info(batch)
                for w in batch:
                    with PREFETCH_JOBS_LOCK:
                        if job.get('cancelled'):
                            break
                    try:
                        formatted = _bulk_map.get(w.lower()) or get_word_info(w)
                        # If requested, persist enriched definition/sentence back to current wordbank
                        if storage_id and mode in ('persist', 'both'):
                            try:
                                d, s = parse_enriched_info(formatted, w)
                                if d or s:
                                    with WORD_STORAGE_LOCK:
                                        rows = WORD_STORAGE.get(storage_id)
                                        if isinstance(rows, list):
                                            for rec in rows:
                                                rw = (rec.get('word') or '').strip()
                                                if rw and rw.lower() == w.lower():
                                                    # Only set if empty to avoid clobbering user-provided content
                                                    if d and not (rec.get('definition') or '').strip():
                                                        rec['definition'] = d
                                                    if s and not (rec.get('sentence') or '').strip():
                                                        rec['sentence'] = s
                                    # no session writes here; safe in background
                            except Exception as _persist_ex:
                                print(f"⚠️ Prefetch persist failed for '{w}': {_persist_ex}")
                    except Exception as ex:
                        print(f"⚠️ Prefetch error for '{w}': {ex}")
                        with PREFETCH_JOBS_LOCK:
                            job['errors'] += 1
                    finally:
                        with PREFETCH_JOBS_LOCK:
                            job['current'] += 1
                            job['last_word'] = w
                batch_ms = (time.time() - batch_start) * 1000.0
                with PREFETCH_METRICS_LOCK:
                    PREFETCH_METRICS['total_batches'] += 1
                    PREFETCH_METRICS['total_words_processed'] += len(batch)
                    PREFETCH_METRICS['last_batch_ms'] = batch_ms
                    PREFETCH_METRICS['total_batch_ms'] += batch_ms
                    PREFETCH_METRICS['avg_batch_ms'] = PREFETCH_METRICS['total_batch_ms'] / max(PREFETCH_METRICS['total_batches'], 1)
                # Optional micro-sleep to yield CPU (avoid long tight loop on large lists)
                time.sleep(0.001)
            with PREFETCH_JOBS_LOCK:
                if not job.get('cancelled'):
                    job['done'] = True
            total_ms = (time.time() - start_total) * 1000.0
            with PREFETCH_METRICS_LOCK:
                PREFETCH_METRICS['last_prefetch_total_ms'] = total_ms
        except Exception as e:
            print(f"❌ Prefetch job crashed: {e}")
            with PREFETCH_JOBS_LOCK:
                job['errors'] += 1
                job['done'] = True

    Thread(target=worker, daemon=True).start()
    return job_id

@app.route('/api/word-info/prefetch/start', methods=['POST'])
def api_word_info_prefetch_start():
    """Start prefetching word info for the current wordbank.
    Returns a job_id to poll for progress.
    """
    try:
        data = request.get_json() or {}
        mode = data.get('mode', 'both')  # 'warm' | 'persist' | 'both'
        # Get current wordbank words
        rows = get_wordbank() or []
        words = [r.get('word') for r in rows if isinstance(r, dict) and r.get('word')]
        if not words:
            return jsonify({'success': False, 'error': 'No words to prefetch', 'total': 0}), 400

        # Pass current storage_id for persistence when requested
        storage_id = session.get('wordbank_storage_id')
        job_id = _start_prefetch_job(words, mode=mode, storage_id=storage_id)
        with PREFETCH_JOBS_LOCK:
            total = PREFETCH_JOBS[job_id]['total']
        return jsonify({'success': True, 'job_id': job_id, 'total': total})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/word-info/prefetch/status', methods=['GET'])
def api_word_info_prefetch_status():
    job_id = request.args.get('id')
    if not job_id:
        return jsonify({'success': False, 'error': 'Missing id'}), 400
    with PREFETCH_JOBS_LOCK:
        job = PREFETCH_JOBS.get(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        total = max(job.get('total') or 0, 1)
        current = min(job.get('current') or 0, total)
        done = bool(job.get('done'))
        cancelled = bool(job.get('cancelled'))
        last_word = job.get('last_word')
        errors = job.get('errors')
        progress = current / float(total)
    return jsonify({'success': True, 'job_id': job_id, 'total': total, 'current': current, 'progress': progress, 'done': done, 'cancelled': cancelled, 'last_word': last_word, 'errors': errors})

@app.route('/api/word-info/prefetch/cancel', methods=['POST'])
def api_word_info_prefetch_cancel():
    data = request.get_json() or {}
    job_id = data.get('id')
    if not job_id:
        return jsonify({'success': False, 'error': 'Missing id'}), 400
    with PREFETCH_JOBS_LOCK:
        job = PREFETCH_JOBS.get(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        job['cancelled'] = True
    return jsonify({'success': True})

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

@app.route("/api/wordbank/verify", methods=["GET"])
def api_verify_wordbank():
    """
    Verify the current wordbank state before starting quiz.
    Returns detailed information about the loaded word list.
    Frontend can call this before navigating to /quiz to ensure correct list is loaded.
    """
    wb = get_wordbank()
    has_uploaded = session.get("has_uploaded_once", False)
    using_defaults = session.get("using_default_words", False)
    skip_defaults = session.get("skip_default_load", False)
    
    # Detect potential issues
    issues = []
    if len(wb) == 0:
        issues.append("No words loaded - wordbank is empty")
    if using_defaults and has_uploaded:
        issues.append("WARNING: Using default words but user previously uploaded custom list (possible session loss)")
    if not wb and has_uploaded:
        issues.append("CRITICAL: User uploaded words but wordbank is empty (session lost)")
    
    return jsonify({
        "ok": len(wb) > 0,
        "wordbank_count": len(wb),
        "wordbank_preview": wb[:5] if wb else [],  # Show first 5 words
        "has_uploaded_once": has_uploaded,
        "using_default_words": using_defaults,
        "skip_default_load": skip_defaults,
        "issues": issues,
        "recommendation": "Ready to start quiz" if len(wb) > 0 and not issues else "Please upload a word list before starting"
    })

@app.route("/api/dictionary-status", methods=["GET"])
def api_dictionary_status():
    """
    Report internal dictionary system status.
    Shows how many words are cached and ready for instant definition lookup.
    """
    global DICTIONARY_CACHE
    
    # Lazy load dictionary cache if not loaded
    if not DICTIONARY_CACHE:
        DICTIONARY_CACHE = load_dictionary_cache()
    
    # Check Simple Wiktionary status
    wiktionary = ensure_simple_wiktionary_loaded()
    wiktionary_count = len(wiktionary) if wiktionary else 0
    
    # Check DICTIONARY_CACHE status
    cache_count = len(DICTIONARY_CACHE)
    
    # Total unique words available
    total_words = wiktionary_count + cache_count
    
    return jsonify({
        "available": True,  # Dictionary is always available (has fallback)
        "word_count": total_words,
        "sources": {
            "simple_wiktionary": wiktionary_count,
            "dictionary_cache": cache_count
        },
        "status": "ready",
        "message": f"Internal dictionary ready with {total_words:,} pre-loaded definitions",
        "optimization": "All quiz definitions pre-enriched during upload for instant quiz performance"
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
        
        # Clear all session data thoroughly
        session.pop("wordbank_storage_id", None)
        session.pop(DATA_KEY, None)
        session.pop(QUIZ_STATE_KEY, None)
        session.pop("wordbank_count", None)
        session.pop("using_default_words", None)  # Clear default flag
        
        # 🔧 TOTAL RESET: Clear flags so user gets fresh start (NO default words auto-load)
        # This ensures refresh button truly clears EVERYTHING including default word list
        session.pop("skip_default_load", None)  # Remove flag
        session.pop("has_uploaded_once", None)  # Remove flag
        
        # CRITICAL: Explicitly set empty word list to prevent restoration from fallback
        # This prevents get_wordbank() from finding session fallback data after reload
        session[DATA_KEY] = []  # Set explicit empty list instead of removing key
        session["wordbank_count"] = 0
        session["wordbank_cleared"] = True  # Flag that clear was intentional
        
        # Clear from WORD_STORAGE again to be absolutely certain
        if storage_id:
            with WORD_STORAGE_LOCK:
                WORD_STORAGE[storage_id] = []  # Ensure it's empty, not deleted
                print(f"DEBUG /api/clear: Set WORD_STORAGE[{storage_id}] to empty list []")
        
        # Set flag to explicitly prevent auto-loading defaults after clear
        # User must manually upload or select "Random Words" to get any words
        session["skip_default_load"] = True  # Don't auto-load defaults after clear
        
        # Force session modification
        session.modified = True
        
        print(f"DEBUG /api/clear: Session cleared. Remaining keys: {list(session.keys())}")
        print(f"DEBUG /api/clear: User must manually upload words or use Random Words feature")
        
        return jsonify({
            "ok": True, 
            "message": "All word lists and quiz progress cleared successfully! Word list is now completely empty.",
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
    Build dictionary cache for all words in current wordbank using built-in Simple Wiktionary
    ✅ NO EXTERNAL API - Uses only 50K+ word built-in dictionary
    """
    wordbank = get_wordbank()
    if not wordbank:
        return jsonify({"error": "No wordbank loaded"}), 400
    
    results = {
        "total_words": len(wordbank),
        "api_lookups": 0,  # Now means Wiktionary lookups
        "cache_hits": 0,
        "fallbacks": 0,
        "errors": []
    }
    
    print(f"Building dictionary cache for {len(wordbank)} words using built-in Wiktionary...")
    
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
            # Try built-in Wiktionary lookup first (50K+ words)
            wiktionary = ensure_simple_wiktionary_loaded()
            
            if wiktionary and word_lower in wiktionary:
                word_data = wiktionary[word_lower]
                # Sanitize before caching to prevent storing inappropriate content
                try:
                    safe_def = sanitize_kid_friendly_text(_filter_definition(word_data.get("definition", ""), word))
                    safe_ex = sanitize_kid_friendly_text(_blank_word(word_data.get("example", ""), word))
                except Exception:
                    safe_def = word_data.get("definition", "")
                    safe_ex = _blank_word(word_data.get("example", ""), word)

                sanitized = dict(word_data)
                if safe_def:
                    sanitized["definition"] = safe_def
                if safe_ex:
                    sanitized["example"] = safe_ex

                # Cache the sanitized Wiktionary entry
                cache_entry = {word_lower: sanitized}
                save_dictionary_cache(cache_entry)
                DICTIONARY_CACHE.update(cache_entry)
                results["api_lookups"] += 1
                print(f"📖 Wiktionary lookup successful for '{word}'")
            else:
                # Generate fallback for words not in Wiktionary
                fallback_data = generate_smart_fallback(word)
                fallback_data["created"] = datetime.now().isoformat()
                # Sanitize fallback data before caching (belt-and-suspenders)
                try:
                    fallback_data["definition"] = sanitize_kid_friendly_text(fallback_data.get("definition", ""))
                    fallback_data["example"] = sanitize_kid_friendly_text(_blank_word(fallback_data.get("example", ""), word))
                except Exception:
                    pass

                cache_entry = {word_lower: fallback_data}
                save_dictionary_cache(cache_entry)
                DICTIONARY_CACHE.update(cache_entry)
                results["fallbacks"] += 1
                print(f"🟨 Using fallback for '{word}'")
                
        except Exception as e:
            error_msg = f"Error processing '{word}': {str(e)}"
            results["errors"].append(error_msg)
            print(f"Γ£ù {error_msg}")
    
    return jsonify({
        "success": True,
        "message": f"Dictionary cache built for {results['total_words']} words using built-in Wiktionary (50K+ words)",
        "results": results
    })


# ============================================================================
# IAP ROUTES (Apple / Google) — verification + restore
# ============================================================================

def _entitlements_summary(user: User) -> dict:
    try:
        unlocked = user.get_unlocked_avatars()
    except Exception:
        unlocked = []
    return {
        "premium_member": bool(getattr(user, 'premium_member', False)),
        "purchased_avatars": list(getattr(user, 'purchased_avatars', []) or []),
        "purchased_bundles": list(getattr(user, 'purchased_bundles', []) or []),
        "unlocked_avatars": unlocked,
    }


@app.route('/api/iap/verify/<platform>', methods=['POST'])
@login_required
def api_iap_verify(platform):
    """Verify a purchase from App Store / Play Billing and apply entitlements.
    Request JSON:
      { product_id, transaction_id, purchase_token, payload }
    """
    platform = (platform or '').lower().strip()
    if platform not in ('apple', 'google', 'web'):
        return jsonify({"success": False, "error": "Unsupported platform"}), 400

    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    transaction_id = data.get('transaction_id')
    purchase_token = data.get('purchase_token')
    payload = data.get('payload', {})

    if not product_id:
        return jsonify({"success": False, "error": "Missing product_id"}), 400

    # Create purchase record (pending)
    rec = PurchaseRecord(
        user_id=current_user.id,
        platform=platform,
        product_id=product_id,
        status='pending',
        transaction_id=transaction_id,
        purchase_token=purchase_token,
        raw_payload=payload or {}
    )
    db.session.add(rec)
    db.session.flush()  # get rec.id

    ok, status_msg, details = _verify_with_store(platform, data)
    if not ok:
        rec.status = 'failed'
        rec.raw_payload = {**(rec.raw_payload or {}), 'verify_status': status_msg, 'store_details': details}
        db.session.commit()
        return jsonify({"success": False, "error": status_msg, "record_id": rec.id}), 400

    # Apply entitlements idempotently
    apply_res = _apply_entitlement(current_user, product_id)
    rec.status = 'verified'
    rec.raw_payload = {**(rec.raw_payload or {}), 'verify_status': status_msg, 'store_details': details, 'apply_result': apply_res}
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"db_commit_failed: {e}"}), 500

    return jsonify({
        "success": True,
        "message": "Purchase verified",
        "record_id": rec.id,
        "entitlements": _entitlements_summary(current_user)
    })


@app.route('/api/iap/restore', methods=['POST'])
@login_required
def api_iap_restore():
    """Restore entitlements from a list of product IDs (client-side provenience).
    This is helpful when a user reinstalls or switches devices; the platform
    client should pre-validate owned purchases and send the product IDs here.
    """
    data = request.get_json(silent=True) or {}
    product_ids = data.get('product_ids') or []
    platform = (data.get('platform') or 'apple').lower()
    if not isinstance(product_ids, list) or not product_ids:
        return jsonify({"success": False, "error": "product_ids must be a non-empty list"}), 400

    applied = []
    for pid in product_ids:
        res = _apply_entitlement(current_user, pid)
        if res.get('applied'):
            applied.append({"product_id": pid, **res})
        # Log a record for traceability (status verified via restore)
        rec = PurchaseRecord(
            user_id=current_user.id,
            platform=platform,
            product_id=pid,
            status='verified',
            transaction_id=None,
            purchase_token=None,
            raw_payload={'restore': True}
        )
        db.session.add(rec)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"db_commit_failed: {e}"}), 500

    return jsonify({
        "success": True,
        "applied": applied,
        "entitlements": _entitlements_summary(current_user)
    })


# ----------------------------------------------------------------------------
# Bundle Key Redemption (Teacher/Parent distributed keys)
# ----------------------------------------------------------------------------
@app.route('/api/bundles/redeem', methods=['POST'])
@login_required
def api_bundles_redeem():
    """Redeem a special bundle key to unlock a set of avatars.
    Request JSON: { key: string }
    Response: { success, bundle_id, bundle_name, unlocked_count, entitlements }
    Notes:
      - Idempotent: re-redeeming an already applied bundle won't duplicate unlocks
      - Keys are matched case-insensitively and with whitespace trimmed
    """
    data = request.get_json(silent=True) or {}
    raw_key = (data.get('key') or '').strip()
    if not raw_key:
        return jsonify({"success": False, "error": "Missing key"}), 400

    if not isinstance(REDEEMABLE_KEYS, dict) or not REDEEMABLE_KEYS:
        return jsonify({"success": False, "error": "Redemption unavailable"}), 503

    norm_key = re.sub(r"\s+", "", raw_key).upper()
    bundle_id = None
    bundle_name = None
    avatars = []
    source = 'legacy'
    bundle_key_row = None

    # 1) Prefer DB-managed bundle key if exists
    try:
        bundle_key_row = BundleKey.query.filter_by(key_norm=norm_key).first()
    except Exception:
        bundle_key_row = None

    if bundle_key_row:
        source = 'db'
        can, reason = bundle_key_row.can_redeem()
        if not can:
            return jsonify({"success": False, "error": reason}), 400
        bundle_id = bundle_key_row.bundle_id
    else:
        # 2) Fallback to legacy in-memory map
        bundle_id = REDEEMABLE_KEYS.get(norm_key)
        if not bundle_id:
            return jsonify({"success": False, "error": "Invalid key"}), 400

    # Resolve bundle config: prefer dynamic bundle when present
    bundle_cfg = (BUNDLE_CATALOG or {}).get(bundle_id) or {}
    if not bundle_cfg:
        try:
            dyn = DynamicBundle.query.filter_by(bundle_id=bundle_id).first()
            if dyn:
                bundle_cfg = { 'name': dyn.name, 'avatars': list(dyn.avatars or []) }
        except Exception:
            pass
    avatars = list(bundle_cfg.get('avatars', []) or [])
    bundle_name = bundle_cfg.get('name') or bundle_id

    product_id = f"bundle:{bundle_id}"
    if product_id not in PRODUCT_MAP:
        PRODUCT_MAP[product_id] = { 'type': 'bundle', 'bundle_id': bundle_id, 'avatars': avatars }

    res = _apply_entitlement(current_user, product_id)

    # If DB key, record usage now (after successful entitlement attempt)
    if bundle_key_row:
        try:
            bundle_key_row.apply_use(current_user.id)
            db.session.add(bundle_key_row)
            # trace redemption
            trace = BundleKeyRedemption(
                bundle_key_id=bundle_key_row.id,
                user_id=current_user.id,
                bundle_id=bundle_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:300]
            )
            db.session.add(trace)
        except Exception:
            pass

    # Log a record for traceability
    try:
        rec = PurchaseRecord(
            user_id=current_user.id,
            platform='web',
            product_id=product_id,
            status='verified',
            transaction_id=None,
            purchase_token=None,
            raw_payload={'redeemed_key': norm_key, 'bundle_id': bundle_id, 'apply_result': res}
        )
        db.session.add(rec)
    except Exception:
        pass

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"db_commit_failed: {e}"}), 500

    return jsonify({
        "success": True,
        "bundle_id": bundle_id,
        "bundle_name": bundle_name,
        "source": source,
        "unlocked_count": int((res or {}).get('details', {}).get('unlocked_count') or 0),
        "entitlements": _entitlements_summary(current_user)
    })



# ----------------------------------------------------------------------------
# BeeKey Redemption for Linked Users (Admin/Parent/Teacher)
# ----------------------------------------------------------------------------
@app.route('/api/beekey/redeem-for-linked', methods=['POST'])
@login_required
def api_beekey_redeem_for_linked():
    """Redeem a BeeKey and unlock avatars for all users linked to the redeemer's admin/teacher key.
    
    This endpoint allows Admin, Parent, and Teacher users to redeem a BeeKey code and automatically
    unlock the avatars in that BeeKey pack for all students/children linked to their account via
    admin_key or teacher_key.
    
    Request JSON: { beekey: string }
    Response: { success, bundle_id, avatars_count, users_unlocked, message }
    """
    data = request.get_json(silent=True) or {}
    raw_key = (data.get('beekey') or '').strip()
    
    if not raw_key:
        return jsonify({"success": False, "error": "Missing BeeKey code"}), 400
    
    # Normalize the key
    norm_key = re.sub(r"\s+", "", raw_key).upper()
    
    # Find the BeeKey in database
    try:
        _ensure_db_initialized()
        bundle_key_row = BundleKey.query.filter_by(key_norm=norm_key).first()
    except Exception as e:
        app.logger.error(f"BeeKey lookup error: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500
    
    if not bundle_key_row:
        return jsonify({"success": False, "error": "Invalid BeeKey code"}), 400
    
    # Check if the BeeKey can be redeemed
    can_redeem, reason = bundle_key_row.can_redeem()
    if not can_redeem:
        error_messages = {
            'status_not_active': 'This BeeKey has been revoked or is no longer active',
            'expired': 'This BeeKey has expired',
            'key_exhausted': 'This BeeKey has reached its maximum number of uses'
        }
        return jsonify({"success": False, "error": error_messages.get(reason, reason)}), 400
    
    bundle_id = bundle_key_row.bundle_id
    
    # Get the avatars from the bundle (check DynamicBundle first, then BUNDLE_CATALOG)
    avatars = []
    bundle_name = bundle_id
    
    try:
        dyn_bundle = DynamicBundle.query.filter_by(bundle_id=bundle_id).first()
        if dyn_bundle:
            avatars = list(dyn_bundle.avatars or [])
            bundle_name = dyn_bundle.name or bundle_id
        else:
            # Fallback to BUNDLE_CATALOG
            bundle_cfg = (BUNDLE_CATALOG or {}).get(bundle_id, {})
            avatars = list(bundle_cfg.get('avatars', []) or [])
            bundle_name = bundle_cfg.get('name') or bundle_id
    except Exception as e:
        app.logger.error(f"Bundle lookup error: {e}")
        return jsonify({"success": False, "error": "Bundle not found"}), 404
    
    if not avatars:
        return jsonify({"success": False, "error": "No avatars found in this BeeKey pack"}), 400
    
    # Find all linked users based on the current user's role
    linked_users = []
    
    try:
        if current_user.role == 'admin':
            # For admins, find all users linked via their teacher_key (admins have a teacher_key too)
            if current_user.teacher_key:
                # Find via TeacherStudent relationship
                links = TeacherStudent.query.filter_by(teacher_key=current_user.teacher_key).all()
                student_ids = [link.student_id for link in links]
                linked_users = User.query.filter(User.id.in_(student_ids)).all() if student_ids else []
        
        elif current_user.role == 'parent':
            # For parents, find all users linked via their teacher_key (parents also use teacher_key)
            if current_user.teacher_key:
                links = TeacherStudent.query.filter_by(teacher_key=current_user.teacher_key).all()
                student_ids = [link.student_id for link in links]
                linked_users = User.query.filter(User.id.in_(student_ids)).all() if student_ids else []
        
        elif current_user.role == 'teacher':
            # For teachers, find all students linked via their teacher_key
            if current_user.teacher_key:
                links = TeacherStudent.query.filter_by(teacher_key=current_user.teacher_key).all()
                student_ids = [link.student_id for link in links]
                linked_users = User.query.filter(User.id.in_(student_ids)).all() if student_ids else []
        
        else:
            return jsonify({"success": False, "error": "Only Admin, Parent, and Teacher accounts can redeem BeeKeys for linked users"}), 403
    
    except Exception as e:
        app.logger.error(f"Error finding linked users: {e}")
        return jsonify({"success": False, "error": "Error finding linked users"}), 500
    
    if not linked_users:
        return jsonify({"success": False, "error": "No students/children are linked to your account"}), 400
    
    # Unlock avatars for all linked users
    unlocked_count = 0
    
    for user in linked_users:
        try:
            # Get user's current purchased avatars list
            purchased = user.purchased_avatars or []
            if not isinstance(purchased, list):
                purchased = []
            
            # Add new avatars (avoiding duplicates)
            initial_count = len(purchased)
            for avatar_id in avatars:
                if avatar_id not in purchased:
                    purchased.append(avatar_id)
            
            # Update user's purchased avatars
            user.purchased_avatars = purchased
            
            # If avatars were added, count this user
            if len(purchased) > initial_count:
                unlocked_count += 1
        
        except Exception as e:
            app.logger.error(f"Error unlocking avatars for user {user.id}: {e}")
            continue
    
    # Record the BeeKey usage
    try:
        bundle_key_row.apply_use(current_user.id)
        db.session.add(bundle_key_row)
        
        # Create redemption trace
        trace = BundleKeyRedemption(
            bundle_key_id=bundle_key_row.id,
            user_id=current_user.id,
            bundle_id=bundle_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:300]
        )
        db.session.add(trace)
        
        # Log purchase record for the redeemer
        rec = PurchaseRecord(
            user_id=current_user.id,
            platform='web',
            product_id=f"beekey:{bundle_id}",
            status='verified',
            transaction_id=None,
            purchase_token=None,
            raw_payload={
                'redeemed_key': norm_key,
                'bundle_id': bundle_id,
                'redemption_type': 'for_linked_users',
                'users_unlocked': unlocked_count,
                'total_linked_users': len(linked_users)
            }
        )
        db.session.add(rec)
        
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving BeeKey redemption: {e}")
        return jsonify({"success": False, "error": "Failed to save redemption"}), 500
    
    return jsonify({
        "success": True,
        "bundle_id": bundle_id,
        "bundle_name": bundle_name,
        "avatars_count": len(avatars),
        "users_unlocked": unlocked_count,
        "total_linked_users": len(linked_users),
        "message": f"Successfully unlocked {len(avatars)} avatar(s) for {unlocked_count} user(s)"
    })


# ----------------------------------------------------------------------------
# Buzz Dust & Ranking System API
# ----------------------------------------------------------------------------
@app.route('/api/buzz-dust/info', methods=['GET'])
@login_required
def api_buzz_dust_info():
    """Get current user's Buzz Dust and rank information"""
    try:
        from buzz_dust_helpers import get_rank_progress, get_all_bee_classes
        
        rank_progress = get_rank_progress(current_user.total_buzz_dust or 0)
        
        return jsonify({
            'success': True,
            'total_buzz_dust': current_user.total_buzz_dust or 0,
            'current_class': rank_progress['current_class'],
            'next_class': rank_progress['next_class'],
            'progress_percent': rank_progress['progress_percent'],
            'dust_needed': rank_progress['dust_needed'],
            'at_max_rank': rank_progress['at_max_rank'],
            'all_classes': get_all_bee_classes()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/buzz-dust/leaderboard', methods=['GET'])
def api_buzz_dust_leaderboard():
    """Get Buzz Dust leaderboard (public or filtered by role)"""
    try:
        from buzz_dust_helpers import get_leaderboard_data
        
        limit = min(int(request.args.get('limit', 50)), 100)
        role_filter = request.args.get('role')  # Optional: 'student', 'teacher', etc.
        
        leaderboard = get_leaderboard_data(limit=limit, role_filter=role_filter)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check-rank-up', methods=['GET'])
@login_required
def api_check_rank_up():
    """Check if user has ranked up (called after quiz completion)"""
    try:
        from buzz_dust_helpers import get_bee_class
        
        # Check if there's a recent rank-up in session
        ranked_up = session.pop('ranked_up', False)
        
        if ranked_up:
            old_class_id = session.pop('old_class_id', 'novice')
            new_class_id = current_user.bee_class or 'novice'
            
            from buzz_dust_helpers import get_all_bee_classes
            all_classes = get_all_bee_classes()
            
            old_class = next((c for c in all_classes if c['id'] == old_class_id), all_classes[0])
            new_class = next((c for c in all_classes if c['id'] == new_class_id), all_classes[0])
            
            return jsonify({
                'success': True,
                'ranked_up': True,
                'old_class': old_class,
                'new_class': new_class,
                'total_buzz_dust': current_user.total_buzz_dust or 0
            })
        
        return jsonify({
            'success': True,
            'ranked_up': False
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------------------------------------------------------------------
# Admin: Bundle Key Management (DB-managed keys)
# ----------------------------------------------------------------------------
@app.route('/api/admin/bundle-keys', methods=['GET'])
@login_required
def api_admin_bundle_keys_list():
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Forbidden"}), 403
    try:
        _ensure_db_initialized()
        rows = BundleKey.query.order_by(BundleKey.created_at.desc()).limit(250).all()
        return jsonify({
            "success": True,
            "bundle_keys": [r.to_dict() for r in rows]
        })
    except Exception as e:
        app.logger.error(f"bundle key list error: {e}")
        return jsonify({"success": False, "error": "list_failed"}), 500


@app.route('/api/admin/bundle-keys', methods=['POST'])
@login_required
def api_admin_bundle_keys_create():
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    bundle_id = (data.get('bundle_id') or '').strip()
    max_uses = int(data.get('max_uses') or 1)
    expires_days = int(data.get('expires_days') or 0)
    if not bundle_id:
        return jsonify({"success": False, "error": "missing_bundle_id"}), 400
    if max_uses < 1:
        max_uses = 1
    if bundle_id not in (BUNDLE_CATALOG or {}):
        return jsonify({"success": False, "error": "unknown_bundle"}), 400
    key_raw, key_norm = BundleKey.generate(bundle_id)
    expires_at = None
    if expires_days > 0:
        try:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        except Exception:
            expires_at = None
    row = BundleKey(
        key_raw=key_raw,
        key_norm=key_norm,
        bundle_id=bundle_id,
        max_uses=max_uses,
        expires_at=expires_at,
        issued_by=current_user.id
    )
    try:
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "bundle_key": row.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"create_failed: {e}"}), 500


@app.route('/api/admin/bee-keys/generate', methods=['POST'])
@login_required
def api_admin_bee_keys_generate():
    """Generate a dynamic 4-avatar BeeKey pack and associated bundle key.

    Body JSON: { avatar_ids?: [str,...], max_uses?: int, expires_days?: int, name?: str }
    - If avatar_ids omitted: pick 4 random active avatars (distinct)
    - Creates DynamicBundle then BundleKey
    Response: { success, bundle, bundle_key }
    """
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    avatar_ids = data.get('avatar_ids') or []
    max_uses = int(data.get('max_uses') or 1)
    expires_days = int(data.get('expires_days') or 0)
    name = (data.get('name') or '').strip() or 'BeeKey Pack'

    # Collect active avatars (exclude defaults if desired)
    try:
        active_avatars = [a.slug for a in Avatar.get_all_active()]
    except Exception:
        active_avatars = []

    if not avatar_ids:
        # Choose 4 random distinct avatars
        import random
        random.shuffle(active_avatars)
        avatar_ids = active_avatars[:4]
    else:
        # Validate requested avatar ids exist
        avatar_ids = [aid for aid in avatar_ids if aid in active_avatars]
    avatar_ids = avatar_ids[:4]
    if len(avatar_ids) < 1:
        return jsonify({"success": False, "error": "no_valid_avatars"}), 400

    # Generate bundle_id
    import uuid
    bundle_uuid = str(uuid.uuid4())[:8]
    bundle_id = f"beekey_{bundle_uuid}".lower()

    dyn = DynamicBundle(
        bundle_id=bundle_id,
        name=name,
        avatars=avatar_ids,
        created_by=current_user.id
    )

    key_raw, key_norm = BundleKey.generate(bundle_id, prefix='BEEKEY')
    expires_at = None
    if expires_days > 0:
        try:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        except Exception:
            expires_at = None
    bkey = BundleKey(
        key_raw=key_raw,
        key_norm=key_norm,
        bundle_id=bundle_id,
        max_uses=max_uses,
        expires_at=expires_at,
        issued_by=current_user.id
    )
    try:
        db.session.add(dyn)
        db.session.add(bkey)
        db.session.commit()
        return jsonify({
            "success": True,
            "bundle": dyn.to_dict(),
            "bundle_key": bkey.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"generate_failed: {e}"}), 500


@app.route('/api/admin/bundle-keys/<int:key_id>/redemptions', methods=['GET'])
@login_required
def api_admin_bundle_key_redemptions(key_id: int):
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Forbidden"}), 403
    try:
        _ensure_db_initialized()
        rows = BundleKeyRedemption.query.filter_by(bundle_key_id=key_id).order_by(BundleKeyRedemption.redeemed_at.desc()).limit(200).all()
        return jsonify({"success": True, "redemptions": [r.to_dict() for r in rows]})
    except Exception as e:
        return jsonify({"success": False, "error": f"list_failed: {e}"}), 500


@app.route('/api/admin/bundle-keys/<int:key_id>/revoke', methods=['POST'])
@login_required
def api_admin_bundle_key_revoke(key_id: int):
    if current_user.role != 'admin':
        return jsonify({"success": False, "error": "Forbidden"}), 403
    try:
        row = BundleKey.query.filter_by(id=key_id).first()
        if not row:
            return jsonify({"success": False, "error": "not_found"}), 404
        if row.status != 'active':
            return jsonify({"success": False, "error": "already_inactive"}), 400
        row.status = 'revoked'
        db.session.commit()
        return jsonify({"success": True, "bundle_key": row.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"revoke_failed: {e}"}), 500


# ============================================================================
# AUTHENTICATION ROUTES (User Login/Registration)
# ============================================================================

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'GET':
        # Expose configurable registration pricing to template
        billing_mode = os.environ.get('REGISTRATION_BILLING_MODE', 'subscription').strip().lower()
        # Legacy one-time fee support (fallback)
        try:
            one_time_fee = float(os.environ.get('REGISTRATION_FEE_USD', '4.99'))
        except Exception:
            one_time_fee = 4.99
        # Monthly subscription fee (default lower than typical $4.99)
        try:
            monthly_fee = float(os.environ.get('SUBSCRIPTION_MONTHLY_USD', '4.49'))
        except Exception:
            monthly_fee = 4.49
        # Optional: free trial days and intro pricing
        try:
            trial_days = int(os.environ.get('SUBSCRIPTION_TRIAL_DAYS', '7'))
        except Exception:
            trial_days = 7
        try:
            intro_price = os.environ.get('SUBSCRIPTION_INTRO_PRICE_USD')
            intro_price = float(intro_price) if intro_price is not None and intro_price != '' else None
        except Exception:
            intro_price = None
        try:
            intro_months = int(os.environ.get('SUBSCRIPTION_INTRO_MONTHS', '0'))
        except Exception:
            intro_months = 0
        try:
            subscription_product_id = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID', 'beesmart.sub.full_monthly')
        except Exception:
            subscription_product_id = 'beesmart.sub.full_monthly'
        return render_template(
            'auth/register.html',
            registration_fee_usd=one_time_fee,
            subscription_monthly_usd=monthly_fee,
            registration_billing_mode=billing_mode,
            subscription_trial_days=trial_days,
            subscription_intro_price_usd=intro_price,
            subscription_intro_months=intro_months,
            subscription_product_id=subscription_product_id
        )

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
        if role not in ['student', 'teacher', 'parent', 'admin']:
            role = 'student'  # Default to student if invalid
        
        # Admin registration requires secret key
        admin_all_access = False
        if role == 'admin':
            admin_key = data.get('admin_key', '').strip()
            if admin_key != ADMIN_REGISTRATION_KEY:
                return jsonify({
                    "success": False, 
                    "error": "Invalid admin registration key. Contact system administrator for admin access."
                }), 403
            admin_all_access = True  # Grant admin bypass privileges

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
            avatar_variant='default',
            admin_all_access=admin_all_access  # Grant admin bypass if key was validated
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
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)

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


# Generic confirmation page after requesting a password reset
@app.route('/auth/forgot-confirmation', methods=['GET'])
def forgot_confirmation_page():
    try:
        return render_template('auth/forgot_confirmation.html')
    except Exception as e:
        app.logger.warning(f"render forgot-confirmation error: {e}")
        # Render a minimal inline message if template missing
        return (
            "<html><body><h1>Check your email</h1>"
            "<p>If an account exists for the info you entered, we'll send reset instructions.</p>"
            f"<p><a href='{url_for('login')}'>Back to Sign In</a></p>"
            "</body></html>",
            200,
            {"Content-Type": "text/html; charset=utf-8"}
        )

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

    # Get current user's avatar data for immediate display (no fetch needed)
    try:
        user_avatar_data = current_user.get_avatar_data()
        use_mascot = current_user.has_selected_avatar() == False
    except Exception as e:
        print(f"⚠️ Could not load user avatar data: {e}")
        user_avatar_data = None
        use_mascot = True

    return render_template('auth/student_dashboard.html',
                         recent_sessions=recent_sessions,
                         total_sessions=total_sessions,
                         avg_accuracy=round(avg_accuracy, 1),
                         struggling_words=struggling_words,
                         badge_collection=badge_collection_sorted,
                         recent_badges=recent_badges,
                         total_badges=len(achievements),
                         total_badge_points=total_badge_points,
                         linked_students=linked_students,
                         user_avatar=user_avatar_data,
                         use_mascot=use_mascot)


@app.route('/api/user/avatar', methods=['POST'], endpoint='api_update_own_avatar')
@login_required
def api_update_user_avatar_legacy():
    """API endpoint for a user to update their own avatar. (Legacy)"""
    data = request.get_json()
    if not data or 'avatar_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing avatar_id in request.'}), 400

    avatar_id = data['avatar_id']
    
    # The update_avatar method on the User model handles validation and saving.
    success, message = current_user.update_avatar(avatar_id)
    
    if success:
        try:
            db.session.commit()
            return jsonify({'status': 'success', 'message': message})
        except Exception as e:
            db.session.rollback()
            log_error(f"Database error after updating avatar for user {current_user.id}: {e}")
            return jsonify({'status': 'error', 'message': 'Database error. Could not save avatar.'}), 500
    else:
        return jsonify({'status': 'error', 'message': message}), 400


@app.route('/avatar-picker')
@login_required
def avatar_picker_page():
    """Avatar picker page with 3D viewer for choosing your bee character"""
    return render_template('test_avatar_picker.html')

@app.route('/honeycomb-picker')
@login_required
def honeycomb_avatar_picker():
    """NEW: Honeycomb-style avatar picker with hexagonal grid layout (responsive version)"""
    timestamp = int(time.time())
    # Optional background override via query param `bg`.
    # Accepts values like '/static/images/my-bg.jpg' or 'images/my-bg.jpg'.
    bg = request.args.get('bg')
    if not bg:
        # Default to the new background image
        picker_bg_url = url_for('static', filename='images/AvatarPickBg.png')
    else:
        if bg.startswith('/static/'):
            picker_bg_url = bg
        else:
            # Normalize to a static-relative path
            picker_bg_url = url_for('static', filename=bg.lstrip('/'))

    return render_template(
        'honeycomb_avatar_picker_responsive.html',
        timestamp=timestamp,
        picker_bg_url=picker_bg_url
    )

@app.route('/honeycomb-picker-old')
@login_required
def honeycomb_avatar_picker_old():
    """OLD: Original honeycomb picker with absolute positioning"""
    return render_template('honeycomb_avatar_picker.html')

@app.route('/test/api')
def test_api():
    """Test page for API debugging"""
    return render_template('test_api.html')

@app.route('/test/avatar-loading')
def test_avatar_loading():
    """Test page for avatar 3D loading diagnostics"""
    return render_template('test_avatar_loading.html')


@app.route('/test/single-avatar')
def test_single_avatar():
    """Test page for single avatar loading with detailed diagnostics"""
    return render_template('test_single_avatar.html')


@app.route('/test/glb-avatars')
def test_glb_avatars():
    """Test page for GLB avatar display and verification"""
    return render_template('test_glb_avatars.html')


@app.route('/visualizer')
def bee_swarm_visualizer():
    """Bee swarm voice visualizer - interactive audio visualization"""
    return render_template('bee_swarm_visualizer.html')


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
    
    # Get current user's avatar data for immediate display
    try:
        user_avatar_data = current_user.get_avatar_data()
        use_mascot = current_user.has_selected_avatar() == False
    except Exception as e:
        print(f"⚠️ Could not load user avatar data: {e}")
        user_avatar_data = None
        use_mascot = True
    
    from datetime import datetime
    return render_template('parent/dashboard.html',
                         students=students,
                         family_stats=family_stats,
                         now=datetime.now(),
                         user_avatar=user_avatar_data,
                          use_mascot=use_mascot)


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
    c.drawString(1 * inch, y, f"Owner: {current_user.display_name} • Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
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
    c.drawString(1*inch, y, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} • Owner: {current_user.display_name}")
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
    cutoff = datetime.now(timezone.utc) - timedelta(days=60)
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

    # Aggregate stats - count both completed and in-progress quizzes with attempts
    total_quizzes = QuizSession.query.filter(
        QuizSession.user_id == student.id,
        or_(
            QuizSession.completed == True,
            and_(
                QuizSession.completed == False,
                (QuizSession.correct_count + QuizSession.incorrect_count) > 0
            )
        )
    ).count()
    
    avg_accuracy = db.session.query(db.func.avg(QuizSession.accuracy_percentage)).filter(
        QuizSession.user_id == student.id,
        or_(
            QuizSession.completed == True,
            and_(
                QuizSession.completed == False,
                (QuizSession.correct_count + QuizSession.incorrect_count) > 0
            )
        )
    ).scalar() or 0

    # Recent quiz sessions - include in-progress with attempts
    recent_sessions = QuizSession.query.filter(
        QuizSession.user_id == student.id,
        or_(
            QuizSession.completed == True,
            and_(
                QuizSession.completed == False,
                (QuizSession.correct_count + QuizSession.incorrect_count) > 0
            )
        )
    ).order_by(
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
    cutoff = datetime.now(timezone.utc) - timedelta(days=60)
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
    return f"BEE-{datetime.now(timezone.utc).year}-AUTO-{str(uuid.uuid4())[:8].upper()}"


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
    try:
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
        
        # Get current user's avatar data for immediate display
        try:
            user_avatar_data = current_user.get_avatar_data()
            use_mascot = current_user.has_selected_avatar() == False
        except Exception as e:
            print(f"⚠️ Could not load user avatar data: {e}")
            user_avatar_data = None
            use_mascot = True
        
        return render_template('admin/dashboard.html', 
                             user=current_user, 
                             stats=stats,
                             battle_stats=battle_stats,
                             leaderboard=leaderboard,
                             my_students=my_students,
                             admin_key=my_key,
                             BUNDLE_CATALOG=BUNDLE_CATALOG or {},
                             user_avatar=user_avatar_data,
                             use_mascot=use_mascot)  # Pass teacher_key as admin_key for template
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ADMIN DASHBOARD ERROR: {str(e)}")
        print(error_details)
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('error.html', 
                             error_message=f"Admin Dashboard Error: {str(e)}",
                             error_details=error_details if app.debug else None), 500


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


@app.route('/admin/sync-avatar-names', methods=['POST'])
@login_required
def admin_sync_avatar_names():
    """Sync DB avatar names with catalog (Apple Store compliance - add ' Avatar' suffix)"""
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    
    try:
        from models import Avatar
        from avatar_catalog import AVATAR_CATALOG
        
        # Build catalog lookup
        catalog_map = {a['id']: a for a in AVATAR_CATALOG}
        
        updated_count = 0
        updated_avatars = []
        
        # Update DB avatars to match catalog names
        db_avatars = Avatar.query.filter_by(is_active=True).all()
        
        for avatar in db_avatars:
            catalog_entry = catalog_map.get(avatar.slug)
            if catalog_entry:
                catalog_name = catalog_entry['name']
                if avatar.name != catalog_name:
                    old_name = avatar.name
                    avatar.name = catalog_name
                    updated_count += 1
                    updated_avatars.append({
                        'slug': avatar.slug,
                        'old_name': old_name,
                        'new_name': catalog_name
                    })
        
        if updated_count > 0:
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "updated_count": updated_count,
            "updated_avatars": updated_avatars
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


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
            headers={'Content-Disposition': f'attachment; filename=users_export_{datetime.now(timezone.utc).strftime("%Y%m%d")}.csv'}
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
                    'created_at': datetime.now(timezone.utc)
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


def update_user_stats_railway(user_id, points_to_add, words_correct, words_attempted):
    """
    Railway-safe comprehensive user stats update for speed rounds
    Updates: quizzes completed, lifetime points, and average accuracy
    """
    try:
        engine = db.get_engine()
        
        accuracy = (words_correct / words_attempted * 100) if words_attempted > 0 else 0
        
        with engine.begin() as conn:
            # First, get current stats
            result = conn.execute(
                text("""
                    SELECT total_quizzes_completed, average_accuracy 
                    FROM users 
                    WHERE id = :user_id
                """),
                {'user_id': user_id}
            ).fetchone()
            
            if result:
                current_quizzes = result[0] or 0
                current_avg_accuracy = result[1] or 0.0
                
                # Calculate new average accuracy (cumulative)
                total_quizzes_after = current_quizzes + 1
                new_avg_accuracy = ((current_avg_accuracy * current_quizzes) + accuracy) / total_quizzes_after
                
                # Update all stats in one query
                conn.execute(
                    text("""
                        UPDATE users 
                        SET total_lifetime_points = COALESCE(total_lifetime_points, 0) + :points,
                            total_quizzes_completed = COALESCE(total_quizzes_completed, 0) + 1,
                            average_accuracy = :new_avg_accuracy
                        WHERE id = :user_id
                    """),
                    {
                        'user_id': user_id, 
                        'points': points_to_add,
                        'new_avg_accuracy': round(new_avg_accuracy, 2)
                    }
                )
                
                speed_logger.info(f"Updated user {user_id} stats: Quizzes={total_quizzes_after}, Points=+{points_to_add}, Accuracy={new_avg_accuracy:.1f}%")
                return True
            else:
                speed_logger.error(f"User {user_id} not found for stats update")
                return False
            
    except Exception as e:
        speed_logger.error(f"Failed to update user stats: {e}")
        import traceback
        traceback.print_exc()
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
    # Pass user information if logged in
    user_name = None
    if current_user.is_authenticated:
        user_name = current_user.display_name
        try:
            print(f"DEBUG /speed-round/quiz: User logged in as {user_name}")
        except Exception:
            pass

    return render_template('speed_round_quiz.html', timestamp=timestamp, user_name=user_name)


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
            'remaining': max(0, len(words) - (current_index + 1)),
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
        
        # Map difficulty names to 1-5 scale for internal dictionary
        difficulty_map = {
            'grade_1_2': 1,
            'grade_3_4': 2,
            'grade_5_6': 3,
            'grade_7_8': 4,
            'grade_9_12': 5,
            'easy': 1,
            'medium': 3,
            'hard': 5
        }
        
        # Generate or fetch words
        if word_source == 'auto':
            # ✅ Use internal dictionary (50K+ Simple Wiktionary) with enhanced difficulty system
            difficulty_level = difficulty_map.get(difficulty, 2)  # Default to grade 3-4
            print(f"🎯 Speed Round: Generating {word_count} words at difficulty level {difficulty_level} from internal dictionary")
            
            word_records = get_random_words_by_difficulty(difficulty_level, count=word_count)
            
            # Extract just word strings for speed round
            words = [record['word'] for record in word_records]
            
            print(f"✅ Generated {len(words)} kid-friendly words from internal dictionary")
            
        elif word_source == 'uploaded':
            # Get user's uploaded word list
            wordbank = get_wordbank()
            if not wordbank or len(wordbank) == 0:
                # ✅ FALLBACK: If no uploaded words, use internal dictionary instead of erroring
                print("⚠️ No uploaded words found, falling back to internal dictionary")
                difficulty_level = difficulty_map.get(difficulty, 2)
                word_records = get_random_words_by_difficulty(difficulty_level, count=word_count)
                words = [record['word'] for record in word_records]
            else:
                # Extract just the word strings
                words = [item['word'] for item in wordbank]
                random.shuffle(words)
                words = words[:word_count]  # Take only requested count
                
        elif word_source == 'mixed':
            # Use internal dictionary with mixed difficulty levels
            print("🎲 Speed Round: Generating mixed difficulty words from internal dictionary")
            mixed_words = []
            words_per_level = max(1, word_count // 5)  # Distribute across all 5 levels
            
            for level in range(1, 6):
                level_words = get_random_words_by_difficulty(level, count=words_per_level)
                mixed_words.extend([record['word'] for record in level_words])
            
            # Shuffle and trim to exact count
            random.shuffle(mixed_words)
            words = mixed_words[:word_count]
            print(f"✅ Generated {len(words)} mixed difficulty words")
            
        else:
            # Default: Use internal dictionary at medium difficulty
            print("⚠️ Unknown word source, using internal dictionary at medium difficulty")
            word_records = get_random_words_by_difficulty(3, count=word_count)
            words = [record['word'] for record in word_records]
        
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

        # Harden persistence (mirrors quiz endpoints)
        session.permanent = True
        session.modified = True
        
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
        
        # Move to next word (guard against overshoot)
        if speed_round['current_index'] < len(words):
            speed_round['current_index'] += 1
        
        # Check if round is complete
        is_complete = speed_round['current_index'] >= len(words)

        # Update session (keep inside try block)
        session['speed_round'] = speed_round
        session.permanent = True
        session.modified = True

        return jsonify({
            'is_correct': is_correct,
            'correct_spelling': correct_spelling,
            'points_earned': points_earned,
            'speed_bonus': speed_bonus,
            'total_points': speed_round['total_points'],
            'current_streak': speed_round['current_streak'],
            'time_taken': round(time_taken, 2),
            'complete': is_complete,
            'next_index': (speed_round['current_index'] + 1) if not is_complete else None,
            'remaining': max(0, len(words) - speed_round['current_index'])
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
            # Update user's comprehensive stats (quizzes, points, accuracy) using Railway-safe method
            stats_updated = update_user_stats_railway(
                current_user.id, 
                speed_round['total_points'],
                words_correct,
                words_attempted
            )
            
            speed_logger.info(f"Speed Round saved: {words_correct}/{words_attempted} correct, {speed_round['total_points']} pts, stats_updated={stats_updated}")
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
# Simple in-memory cache for avatar list (invalidates on app restart)
_AVATAR_CACHE = {"data": None, "timestamp": 0, "ttl": 300}  # 5 minute TTL
# Cache for GLB file scanning (expensive filesystem operation)
_GLB_SCAN_CACHE = {"data": None, "timestamp": 0, "ttl": 600}  # 10 minute TTL

@app.route("/api/avatars", methods=["GET"])
def api_get_avatars():
    """Get the complete avatar catalog with optional filtering, plus canonical asset URLs.

    Improvements:
    - Dedupe GLB avatars by canonical slug and choose the most recent file ("latest one")
    - Generate robust thumbnail URLs by probing common naming variants server-side
    - Alphabetize the final hive list for stable ordering
    - Include unlock status based on user's honey points and purchases
    """
    # Check cache first
    global _AVATAR_CACHE
    current_time = time.time()
    
    # Use cache for both authenticated and unauthenticated users
    # Cache key includes user ID to separate per-user unlock status
    cache_key = f"user_{current_user.id if current_user.is_authenticated else 'guest'}"
    
    # Allow cache bypass for immediate troubleshooting (e.g., force=1)
    if request.args.get('force') != '1':
        if _AVATAR_CACHE.get(cache_key) and (current_time - _AVATAR_CACHE.get(f"{cache_key}_timestamp", 0)) < _AVATAR_CACHE["ttl"]:
            print(f"⚡ Returning cached avatar list for {cache_key}")
            return jsonify(_AVATAR_CACHE[cache_key])
    
    try:
        # Be resilient: if DB or catalog imports fail, fall back to filesystem avatars
        try:
            from models import Avatar, User
        except Exception as _imp_err:
            print(f"⚠️ Avatar model import failed, falling back to filesystem-only avatars: {_imp_err}")
            Avatar = None  # type: ignore
        try:
            from avatar_catalog import check_avatar_unlocked, AVATAR_CATALOG
            AVATARS_CATALOG = AVATAR_CATALOG  # Alias for backward compatibility
        except Exception as _cat_err:
            print(f"⚠️ Avatar catalog import failed, disabling unlock checks: {_cat_err}")
            AVATARS_CATALOG = []  # type: ignore
            def check_avatar_unlocked(*_args, **_kwargs):
                # Return dict format to match avatar_catalog.check_avatar_unlocked
                return {"unlocked": True, "reason": "Catalog unavailable", "required_points": 0, "price": 0}
        import re as _re
        
        # Helper: append a simple cache-busting query (use app start time instead of checking each file)
        # This avoids expensive os.path.getmtime() calls for every asset
        _APP_VERSION = str(int(time.time()))  # Changes on each app restart
        def _cachebust_url(url: str) -> str:
            if not url:
                return url
            sep = '&' if '?' in url else '?'
            return f"{url}{sep}v={_APP_VERSION}"

    # Get current user's unlock status
        user_honey_points = 0
        purchased_avatars = []
        is_admin_or_premium = False
        
        if current_user.is_authenticated:
            # Safe access with fallbacks for newly migrated fields
            user_honey_points = getattr(current_user, 'honey_points', 0) or 0
            purchased_avatars = getattr(current_user, 'purchased_avatars', []) or []
            
            # Check if user has admin_all_access method
            if hasattr(current_user, 'is_admin_or_premium'):
                try:
                    is_admin_or_premium = current_user.is_admin_or_premium()
                except Exception:
                    # Fallback to role check
                    is_admin_or_premium = getattr(current_user, 'role', '') == 'admin'
            else:
                is_admin_or_premium = getattr(current_user, 'role', '') == 'admin'

        # Request filters
        category = request.args.get('category')
        search_query = request.args.get('search')

        # Kid-safe exclusions
        excluded_slugs = {'anxious-bee', 'monster-bee'}

        # Base query (optional - skip if Avatar model unavailable)
        enriched_avatars = []
        if Avatar is not None:
            try:
                query = Avatar.query.filter_by(is_active=True)
                if excluded_slugs:
                    query = query.filter(~Avatar.slug.in_(list(excluded_slugs)))
                if category:
                    query = query.filter_by(category=category)
                if search_query:
                    pattern = f"%{search_query}%"
                    query = query.filter(
                        db.or_(
                            Avatar.name.ilike(pattern),
                            Avatar.description.ilike(pattern),
                            Avatar.slug.ilike(pattern)
                        )
                    )

                avatars = query.order_by(Avatar.sort_order, Avatar.name).all()

                # Enrichment
                for avatar in avatars:
                    base_path = f"/static/assets/avatars/{avatar.folder_path}"
                    # NOTE: avatar.obj_file is a LEGACY field name. Some records still have .obj from legacy era.
                    raw_name = avatar.obj_file or ''
                    is_glb = raw_name.lower().endswith('.glb')
                    desc = avatar.description

                    # HARD OVERRIDE (UNCONDITIONAL): Any legacy .obj gets remapped to glb_files/<Name>.glb
                    # We no longer skip if the file is missing; we assume all canonical GLBs exist.
                    if raw_name.lower().endswith('.obj'):
                        stem = raw_name.rsplit('.', 1)[0]
                        base_path = "/static/assets/avatars/glb_files"
                        avatar.folder_path = 'glb_files'
                        raw_name = f"{stem}.glb"
                        is_glb = True
                        print(f"🔁 Remapped legacy OBJ to GLB for avatar: {avatar.slug} -> {raw_name}")
                    if (avatar.slug or '').lower() in ('obee', 'o-bee'):
                        desc = "A wise Jedi Master of the hive. May the buzz be with you. 🐝✨"

                    # Check unlock status from avatar_catalog
                    avatar_slug = avatar.slug
                    catalog_avatar = next((a for a in AVATARS_CATALOG if a['id'] == avatar_slug), None)

                    is_locked = True
                    unlock_message = ""
                    unlock_points_val = None
                    tier_val = None
                    price_val = None

                    if is_admin_or_premium:
                        # Admins and premium members have access to all avatars
                        is_locked = False
                    elif catalog_avatar:
                        # Check unlock status using avatar_catalog helper (returns dict)
                        unlock_result = check_avatar_unlocked(
                            avatar_slug,
                            user_honey_points,
                            purchased_avatars
                        )
                        is_locked = not unlock_result.get('unlocked', False)

                        if is_locked:
                            # Generate unlock message based on tier
                            tier = catalog_avatar.get('tier', 'premium')
                            unlock_points = catalog_avatar.get('unlock_points', 0)
                            price = catalog_avatar.get('price', 0)

                            # expose raw values for frontend computation
                            unlock_points_val = unlock_points
                            tier_val = tier
                            price_val = price

                            if tier == 'earn_or_buy':
                                points_needed = unlock_points - user_honey_points
                                unlock_message = f"Earn {points_needed:,} more Honey Points or purchase for ${price:.2f}"
                            elif tier == 'premium':
                                unlock_message = f"Purchase for ${price:.2f}"
                            else:
                                unlock_message = "Complete more quizzes to unlock!"

                    # Build thumb/preview with cache-busting
                    thumb_url = f"{base_path}/{avatar.thumbnail_file}" if avatar.thumbnail_file else None
                    thumb_cb = _cachebust_url(thumb_url) if thumb_url else None

                    # Build URLs object - GLB-only (all avatars are GLB format)
                    glb_url = f"{base_path}/{raw_name}"  # Always a .glb after override above
                    urls_obj = {
                        'glb': glb_url,  # Primary GLB file path (GLTFLoader uses this)
                        'model_obj': glb_url,  # DEPRECATED: Backward compatibility alias
                        'thumbnail': thumb_cb,
                        'preview': thumb_cb,
                    }

                    enriched_avatars.append({
                        'id': avatar.slug,
                        'name': avatar.name,
                        'description': desc,
                        'category': avatar.category,
                        'folder': avatar.folder_path,
                        'is_glb': is_glb,
                        'thumbnail': thumb_cb,
                        'preview': thumb_cb,
                        'urls': urls_obj,
                        'unlock_level': avatar.unlock_level,
                        'points_required': avatar.points_required,
                        'is_premium': avatar.is_premium,
                        'is_locked': is_locked,
                        'unlock_message': unlock_message,
                        # expose numeric unlock info when available
                        'unlock_points': unlock_points_val,
                        'tier': tier_val,
                        'price': price_val,
                    })
            except Exception as _db_err:
                print(f"⚠️ Avatar DB query failed, continuing with filesystem-only avatars: {_db_err}")

    # Filesystem fallback (e.g., BudaBee.glb, JRockBee.glb)
        static_root = os.path.join(app.root_path, 'static', 'assets', 'avatars')
        glb_dir = os.path.join(static_root, 'glb_files')
        thumb_dir = os.path.join(glb_dir, 'AvatarThumbnails')
        existing_slugs = { item['id'] for item in enriched_avatars }

        def _slug_from_base(base: str) -> str:
            name_with_spaces = _re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
            return _re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-'), name_with_spaces

        def _thumbnail_for_base(base: str):
            """Prefer exact {base}!.png; for known legacy names, try an alias before giving up."""
            base_path = "/static/assets/avatars/glb_files"
            # 1) strict
            candidate = f"{base_path}/AvatarThumbnails/{base}!.png"
            cand_fs = os.path.join(thumb_dir, f"{base}!.png")
            if os.path.exists(cand_fs):
                return candidate
            # 2) known aliases (e.g., DoctorBee -> DocBee thumbnail)
            # Support multiple alias candidates per base to handle spacing/hyphenation variants
            # Python 3.9 compatibility: use typing.Union instead of PEP 604 (|) unions
            aliases: Dict[str, Union[List[str], str]] = {
                'DoctorBee': ['DocBee'],
                'FrankenBee': ['Franken Bee', 'Franken-Bee'],
            }
            alias_val = aliases.get(base)
            if alias_val:
                alias_list = alias_val if isinstance(alias_val, (list, tuple)) else [alias_val]
                for alias in alias_list:
                    alias_candidate = f"{base_path}/AvatarThumbnails/{alias}!.png"
                    alias_fs = os.path.join(thumb_dir, f"{alias}!.png")
                    if os.path.exists(alias_fs):
                        return alias_candidate
            return None

        # Build a map of slug -> latest GLB file info so duplicates resolve to the newest
        # Use cache to avoid expensive filesystem scanning on every request
        global _GLB_SCAN_CACHE
        glb_latest: dict = {}
        
        if _GLB_SCAN_CACHE["data"] and (time.time() - _GLB_SCAN_CACHE["timestamp"]) < _GLB_SCAN_CACHE["ttl"]:
            print("⚡ Using cached GLB scan results")
            glb_latest = _GLB_SCAN_CACHE["data"]
        elif os.path.isdir(glb_dir):
            print("🔍 Scanning GLB files...")
            for fname in os.listdir(glb_dir):
                if not fname.lower().endswith('.glb'):
                    continue
                base = fname[:-4]
                slug, name_with_spaces = _slug_from_base(base)
                if slug in excluded_slugs or slug in existing_slugs:
                    continue

                file_path = os.path.join(glb_dir, fname)
                try:
                    mtime = os.path.getmtime(file_path)
                except Exception:
                    mtime = 0

                prev = glb_latest.get(slug)
                if not prev or mtime > prev['mtime']:
                    glb_latest[slug] = {
                        'fname': fname,
                        'base': base,
                        'name': name_with_spaces,
                        'mtime': mtime,
                    }
            
            # Cache the results
            _GLB_SCAN_CACHE["data"] = glb_latest
            _GLB_SCAN_CACHE["timestamp"] = time.time()
            print(f"💾 Cached {len(glb_latest)} GLB files")

        # If certain GLB slugs exist, prefer them over older OBJ variants with different slugs
        # Example: if 'j-rock-bee' (from JRockBee.glb) exists, drop legacy 'rocker-bee' DB entry
        glb_slugs = set(glb_latest.keys())
        replacement_rules = {
            'j-rock-bee': ['rocker-bee'],
            # Prefer concise GLB slug 'doc-bee' over legacy DB slug 'doctor-bee'
            'doc-bee': ['doctor-bee'],
            # Prefer 'robo-bee' over legacy 'buzzbot-bee'
            'robo-bee': ['buzzbot-bee'],
        }
        if glb_slugs:
            pruned = []
            to_drop = set()
            for glb_slug in glb_slugs:
                for legacy in replacement_rules.get(glb_slug, []):
                    to_drop.add(legacy)
            if to_drop:
                for item in enriched_avatars:
                    if item.get('id') in to_drop:
                        continue
                    pruned.append(item)
                enriched_avatars = pruned

    # Append latest GLB entries
        base_path = "/static/assets/avatars/glb_files"
        for slug, info in glb_latest.items():
            model_url = f"{base_path}/{info['fname']}"
            thumb_url = _thumbnail_for_base(info['base'])
            thumb_cb = _cachebust_url(thumb_url)

            auto_desc = f"{info['name']} is ready to spell! 🐝"
            if slug in ('obee', 'o-bee'):
                auto_desc = "A wise Jedi Master of the hive. May the buzz be with you. 🐝✨"
            
            # Check unlock status for GLB avatars
            catalog_avatar = next((a for a in AVATARS_CATALOG if a['id'] == slug), None)
            
            is_locked = True
            unlock_message = ""
            unlock_points_val = None
            tier_val = None
            price_val = None
            
            # Use catalog name if available (Apple Store compliant with " Avatar" suffix)
            display_name = catalog_avatar.get('name') if catalog_avatar else info['name']
            catalog_desc = catalog_avatar.get('description') if catalog_avatar else auto_desc
            
            if is_admin_or_premium:
                is_locked = False
            elif catalog_avatar:
                # Check unlock status using avatar_catalog helper (returns dict)
                unlock_result = check_avatar_unlocked(
                    slug, 
                    user_honey_points, 
                    purchased_avatars
                )
                is_locked = not unlock_result.get('unlocked', False)
                
                if is_locked:
                    tier = catalog_avatar.get('tier', 'premium')
                    unlock_points = catalog_avatar.get('unlock_points', 0)
                    price = catalog_avatar.get('price', 0)
                    # expose raw values for frontend computation
                    unlock_points_val = unlock_points
                    tier_val = tier
                    price_val = price
                    
                    if tier == 'earn_or_buy':
                        points_needed = unlock_points - user_honey_points
                        unlock_message = f"Earn {points_needed:,} more Honey Points or purchase for ${price:.2f}"
                    elif tier == 'premium':
                        unlock_message = f"Purchase for ${price:.2f}"
                    else:
                        unlock_message = "Complete more quizzes to unlock!"
            else:
                # Not in catalog, assume it's a free avatar
                is_locked = False

            enriched_avatars.append({
                'id': slug,
                'name': display_name,
                'description': catalog_desc,
                'category': 'classic',
                'folder': 'glb_files',
                'is_glb': True,
                'thumbnail': thumb_cb,
                'preview': thumb_cb,
                'urls': {
                    'glb': model_url,  # PRIMARY: GLB file path for GLTFLoader
                    'model_obj': model_url,  # BACKUP: For compatibility with code checking model_obj
                    'model_mtl': None,
                    'texture': None,
                    'thumbnail': thumb_cb,
                    'preview': thumb_cb,
                },
                'unlock_level': 1,
                'points_required': 0,
                'is_premium': False,
                'is_locked': is_locked,
                'unlock_message': unlock_message,
                # expose numeric unlock info when available
                'unlock_points': unlock_points_val,
                'tier': tier_val,
                'price': price_val,
            })

        # Post-process: fix any DB-provided thumbnails that point to the generic HoneyComb
        # by probing for a better match on disk using the slug or GLB base.
        def _maybe_fix_thumbnail(av: dict) -> None:
            try:
                url = av.get('thumbnail') or ''
                fname = os.path.basename(url)
                is_generic = fname.lower().startswith('honeycomb')
                exists = os.path.exists(os.path.join(thumb_dir, fname)) if fname else False
                if exists and not is_generic:
                    return
                # Derive a base name from the GLB filename if available, else from slug
                model_url = (av.get('urls') or {}).get('model_obj') or ''
                base_guess = ''
                if model_url.lower().endswith('.glb'):
                    base_guess = os.path.splitext(os.path.basename(model_url))[0]
                if not base_guess:
                    slug_val = av.get('id') or ''
                    parts = [p for p in _re.split(r'[^a-zA-Z0-9]+', slug_val) if p]
                    base_guess = ''.join(s.capitalize() for s in parts)
                if base_guess:
                    fixed = _thumbnail_for_base(base_guess)
                    av['thumbnail'] = fixed
                    av['preview'] = fixed
                    if 'urls' in av:
                        av['urls']['thumbnail'] = fixed
                        av['urls']['preview'] = fixed
            except Exception:
                pass

        for _av in enriched_avatars:
            _maybe_fix_thumbnail(_av)

        # Post-clean: ensure no .obj URLs survived (safety net)
        for av in enriched_avatars:
            urls = av.get('urls') or {}
            for k in ('glb','model_obj','preview','thumbnail'):
                v = urls.get(k)
                if isinstance(v, str) and v.lower().endswith('.obj'):
                    urls[k] = v[:-4] + '.glb'
            av['urls'] = urls
            if av.get('folder') != 'glb_files':
                av['folder'] = 'glb_files'
        # Final dedupe by slug (in case) and alphabetize for stable hive order
        seen = set()
        deduped = []
        for av in enriched_avatars:
            if av['id'] in seen:
                continue
            seen.add(av['id'])
            deduped.append(av)
        deduped.sort(key=lambda a: (a.get('name') or '').lower())

        enriched_avatars = deduped

        response_data = {
            'status': 'success',
            'avatars': enriched_avatars,
            'total': len(enriched_avatars),
            # include current user honey points for client-side computations
            'user_honey_points': user_honey_points
        }
        
        # Cache for all users (with per-user cache key)
        cache_key = f"user_{current_user.id if current_user.is_authenticated else 'guest'}"
        _AVATAR_CACHE[cache_key] = response_data
        _AVATAR_CACHE[f"{cache_key}_timestamp"] = time.time()
        print(f"💾 Cached {len(enriched_avatars)} avatars for {cache_key}")
        
        return jsonify(response_data)

    except Exception as e:
        import traceback
        print(f"❌ Error fetching avatars: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        }), 500

@app.route("/api/subscriptions", methods=["GET"])
def api_get_subscriptions():
    """Get available subscription products with pricing and details.
    
    Returns subscription tiers for App Store Connect integration:
    - Monthly Premium ($4.99/month)
    - Yearly Premium ($39.99/year - Save 33%)
    - Family Premium ($7.99/month - Up to 6 members)
    """
    try:
        subscriptions = {
            'status': 'success',
            'products': [
                {
                    'id': SUBSCRIPTION_PRODUCT_IDS['monthly'],
                    'type': 'monthly',
                    'name': 'Premium Monthly Membership',
                    'displayName': 'Premium Monthly',
                    'price': 4.99,
                    'currency': 'USD',
                    'duration': '1 month',
                    'subscription': True,
                    'familySharing': False,
                    'description': 'Unlock unlimited spelling practice with Premium Monthly Membership!',
                    'benefits': [
                        'Unlimited word lists and quizzes',
                        'All 39 premium bee avatars unlocked',
                        'Ad-free experience',
                        'Speed Round mode access',
                        'Offline mode for practice anywhere',
                        'Priority customer support',
                        'Monthly content updates'
                    ]
                },
                {
                    'id': SUBSCRIPTION_PRODUCT_IDS['yearly'],
                    'type': 'yearly',
                    'name': 'Premium Yearly Membership',
                    'displayName': 'Premium Yearly',
                    'price': 39.99,
                    'currency': 'USD',
                    'duration': '1 year',
                    'subscription': True,
                    'familySharing': False,
                    'savings': '33%',
                    'savingsAmount': 20.00,
                    'monthlyEquivalent': 3.33,
                    'recommended': True,
                    'badge': 'Best Value',
                    'description': 'Best Value! Unlock unlimited spelling practice for a full year!',
                    'benefits': [
                        'Everything in Monthly Premium',
                        'Save 33% compared to monthly billing',
                        'All 39 premium bee avatars unlocked forever',
                        'Ad-free experience for the entire year',
                        'Speed Round mode access',
                        'Offline mode for practice anywhere',
                        'Priority customer support',
                        'All future content updates included'
                    ]
                },
                {
                    'id': SUBSCRIPTION_PRODUCT_IDS['family'],
                    'type': 'family',
                    'name': 'Premium Family Membership',
                    'displayName': 'Premium Family',
                    'price': 7.99,
                    'currency': 'USD',
                    'duration': '1 month',
                    'subscription': True,
                    'familySharing': True,
                    'maxMembers': 6,
                    'description': 'Perfect for families! Share Premium access with up to 6 family members!',
                    'benefits': [
                        'Premium access for up to 6 family members',
                        'Each member gets their own progress tracking',
                        'All 39 premium bee avatars unlocked',
                        'Ad-free experience for everyone',
                        'Speed Round mode access',
                        'Offline mode for practice anywhere',
                        'Priority customer support',
                        'Individual leaderboards and achievements'
                    ]
                }
            ],
            'subscriptionGroup': 'BeeSmart Premium Membership',
            'freeTrial': {
                'available': True,
                'duration': 7,
                'durationUnit': 'days'
            }
        }
        
        # Include user's current subscription status if authenticated
        if current_user.is_authenticated:
            subscriptions['user'] = {
                'isPremium': getattr(current_user, 'premium_member', False),
                'activeSubscription': None  # TODO: Track active subscription type
            }
        
        return jsonify(subscriptions)
        
    except Exception as e:
        import traceback
        print(f"❌ Error fetching subscriptions: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        }), 500

@app.route("/subscription")
@app.route("/premium")
def subscription_page():
    """
    Subscription landing page for BeeSmart Premium
    Shows all 3 tiers (Monthly, Yearly, Family) with pricing comparison
    """
    try:
        # Check if user is authenticated
        user_authenticated = 'user_id' in session
        current_user = None
        
        if user_authenticated:
            user_id = session.get('user_id')
            current_user = User.query.get(user_id)
        
        return render_template(
            'subscription.html',
            user_authenticated=user_authenticated,
            current_user=current_user
        )
    
    except Exception as e:
        print(f"❌ Error loading subscription page: {e}")
        import traceback
        traceback.print_exc()
        return render_template(
            'subscription.html',
            user_authenticated=False,
            current_user=None
        )

@app.route("/api/validate-receipt", methods=["POST"])
def validate_receipt():
    """
    Validate App Store receipt and update user's subscription status.
    
    iOS app sends receipt data after purchase/restore.
    We validate with Apple's servers and update database.
    
    TEMPORARILY DISABLED: Database migration required.
    """
    return jsonify({
        'status': 'error',
        'message': 'Subscription system temporarily disabled for database migration',
        'migration_needed': True
    }), 503
    

@app.route("/apple-webhook", methods=["POST"])
def apple_subscription_webhook():
    """
    Apple App Store Server-to-Server Notifications webhook.
    
    Apple automatically POSTs to this endpoint for subscription events:
    - DID_RENEW: Subscription renewed successfully
    - DID_FAIL_TO_RENEW: Billing failed (enters grace period)
    - DID_CHANGE_RENEWAL_STATUS: User canceled or re-enabled auto-renew
    - REFUND: User received refund
    - CANCEL: Subscription canceled by Apple support
    
    TEMPORARILY DISABLED: Database migration required.
    """
    return jsonify({'status': 'received', 'migration_needed': True}), 200
    

@app.route("/api/speed-round/health")
def speed_round_health_railway():
    """Speed Round system health check for Railway"""
    health = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
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
        # NOTE: avatar.obj_file is a LEGACY field name - it actually contains the GLB filename
        is_glb = avatar.obj_file.lower().endswith('.glb') if avatar.obj_file else False
        
        avatar_info = {
            'id': avatar.slug,
            'name': avatar.name,
            'description': avatar.description,
            'variant': 'default',
            'category': avatar.category,
            'thumbnail_url': f"{base_path}/{avatar.thumbnail_file}",
            'preview_url': f"{base_path}/{avatar.thumbnail_file}",
            'glb_url': f"{base_path}/{avatar.obj_file}" if is_glb else None,  # GLB files stored in obj_file field
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


@app.route("/api/users/<int:user_id>/avatar", methods=["PUT"], endpoint='api_admin_or_user_update_avatar')
@login_required
def api_admin_or_user_update_avatar(user_id):
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


@app.route("/api/avatar/select", methods=["POST"])
@login_required
def api_select_avatar():
    """
    Simple avatar selection endpoint for the avatar picker
    Accepts avatar_slug and updates current user's avatar
    """
    try:
        from models import Avatar
        
        data = request.get_json()
        avatar_slug = data.get('avatar_slug')
        
        if not avatar_slug:
            return jsonify({
                'success': False,
                'error': 'avatar_slug is required'
            }), 400
        
        # Look up avatar by slug; if missing, attempt auto-install from GLB folder
        avatar = Avatar.query.filter_by(slug=avatar_slug, is_active=True).first()
        if not avatar:
            # Auto-install: search glb_files for a matching slug
            import re as _re
            static_root = os.path.join(app.root_path, 'static', 'assets', 'avatars')
            glb_dir = os.path.join(static_root, 'glb_files')
            thumb_dir = os.path.join(glb_dir, 'AvatarThumbnails')

            def _slug_from_base(base: str) -> str:
                name_with_spaces = _re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
                return _re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-'), name_with_spaces

            def _thumbnail_for_base(base: str):
                base_path = "/static/assets/avatars/glb_files"
                cand_fs = os.path.join(thumb_dir, f"{base}!.png")
                return f"{base_path}/AvatarThumbnails/{base}!.png" if os.path.exists(cand_fs) else None

            installed = False
            if os.path.isdir(glb_dir):
                for fname in os.listdir(glb_dir):
                    if not fname.lower().endswith('.glb'):
                        continue
                    base = fname[:-4]
                    slug, name_with_spaces = _slug_from_base(base)
                    if slug != avatar_slug:
                        continue
                    # Create DB record
                    thumb_url = _thumbnail_for_base(base)
                    # Store relative paths inside folder_path
                    try:
                        avatar = Avatar(
                            slug=avatar_slug,
                            name=name_with_spaces,
                            description=f"{name_with_spaces} is ready to spell! 🐝",
                            category='classic',
                            folder_path='glb_files',
                            obj_file=fname,
                            mtl_file=None,
                            texture_file=None,
                            thumbnail_file=os.path.join('AvatarThumbnails', os.path.basename(thumb_url)),
                            sort_order=Avatar.query.count() + 100,
                            is_active=True,
                        )
                        db.session.add(avatar)
                        db.session.commit()
                        installed = True
                        break
                    except Exception as _e:
                        db.session.rollback()
                        print(f"❌ Failed to auto-install avatar '{avatar_slug}': {_e}")
                        break
            if not installed or not avatar:
                return jsonify({
                    'success': False,
                    'error': f'Avatar not found: {avatar_slug}'
                }), 404
        
        # Update current user's avatar
        success, message = current_user.update_avatar(avatar.slug, variant='default')
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Mark avatar as explicitly selected
        try:
            prefs = current_user.preferences or {}
            prefs['avatar_selected'] = True
            current_user.preferences = prefs
        except Exception as e:
            print(f"⚠️ Could not update preferences: {e}")
        
        db.session.commit()
        
        print(f"✅ User {current_user.username} selected avatar: {avatar_slug}")
        
        return jsonify({
            'success': True,
            'message': f'Avatar updated to {avatar.name}!',
            'avatar': {
                'slug': avatar.slug,
                'name': avatar.name
            },
            'redirect': url_for('student_dashboard')  # Or wherever you want to redirect
        })
    
    except Exception as e:
        print(f"❌ Error selecting avatar: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# --- Avatar File Serving from Database -------------------------------------------
@app.route("/static/assets/avatars/<slug>/<filename>")
def serve_avatar_file_from_db(slug, filename):
    """Serve avatar 3D files from database binary data"""
    try:
        from models import Avatar
        from io import BytesIO
        
        # Get avatar from database
        avatar = Avatar.query.filter_by(slug=slug).first()
        if not avatar:
            # Try from filesystem as fallback
            try:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            except:
                return "Avatar not found", 404
        
        # Determine which binary field to serve based on file extension
        ext = filename.lower().split('.')[-1]
        
        if ext == 'obj':
            if not avatar.obj_data:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            return Response(avatar.obj_data, mimetype='application/octet-stream')
        
        elif ext == 'mtl':
            if not avatar.mtl_data:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            return Response(avatar.mtl_data, mimetype='text/plain')
        
        elif ext == 'png' and '!' in filename:
            # Thumbnail
            if not avatar.thumbnail_data:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            return Response(avatar.thumbnail_data, mimetype='image/png')
        
        elif ext == 'png':
            # Texture
            if not avatar.texture_data:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            return Response(avatar.texture_data, mimetype='image/png')
        
        else:
            # Unknown file type, try filesystem
            return send_from_directory(f'static/assets/avatars/{slug}', filename)
    
    except Exception as e:
        print(f"❌ Error serving avatar file {slug}/{filename}: {e}")
        # Fallback to filesystem
        try:
            return send_from_directory(f'static/assets/avatars/{slug}', filename)
        except:
            return "File not found", 404


@app.route("/api/users/me", methods=["GET"])
def api_get_current_user():
    """Get current user's basic information (name, auth status, etc.)"""
    try:
        # Check if user is authenticated
        if current_user.is_authenticated:
            # Live stats may have been updated by the latest quiz completion; ensure we have most recent GPA/accuracy
            try:
                # Lightweight refresh (won't recalc heavy aggregates but ensures derived fields are present)
                if hasattr(current_user, 'update_gpa_and_accuracy'):
                    current_user.update_gpa_and_accuracy()
            except Exception as _e:
                print(f"WARNING /api/users/me: Failed to auto-refresh GPA/accuracy: {_e}")

            resp = jsonify({
                'status': 'success',
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'display_name': getattr(current_user, 'display_name', current_user.username),
                    'email': getattr(current_user, 'email', None),
                    'role': getattr(current_user, 'role', 'student'),
                    # ✅ Extended real-time progress fields
                    'total_quizzes_completed': getattr(current_user, 'total_quizzes_completed', 0),
                    'total_lifetime_points': getattr(current_user, 'total_lifetime_points', 0),
                    'honey_points': getattr(current_user, 'honey_points', 0),
                    'cumulative_gpa': getattr(current_user, 'cumulative_gpa', 0.0),
                    'average_accuracy': getattr(current_user, 'average_accuracy', 0.0),
                    'best_grade': getattr(current_user, 'best_grade', None),
                    'best_streak': getattr(current_user, 'best_streak', 0)
                }
            })
            try:
                resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            except Exception:
                pass
            return resp
        else:
            # Guest user
            resp = jsonify({
                'status': 'success',
                'authenticated': False,
                'user': {
                    'display_name': 'NewBee',
                    'role': 'guest',
                    # Provide consistent shape for frontend consumption
                    'total_quizzes_completed': 0,
                    'total_lifetime_points': 0,
                    'honey_points': 0,
                    'cumulative_gpa': 0.0,
                    'average_accuracy': 0.0,
                    'best_grade': None,
                    'best_streak': 0
                }
            })
            try:
                resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            except Exception:
                pass
            return resp
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


@app.route("/api/users/stats", methods=["GET"])
def api_get_user_stats():
    """Lightweight endpoint for polling cumulative stats (GPA, accuracy, points, streaks)."""
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'status': 'success',
                'authenticated': False,
                'stats': {
                    'cumulative_gpa': 0.0,
                    'average_accuracy': 0.0,
                    'total_lifetime_points': 0,
                    'total_quizzes_completed': 0,
                    'best_streak': 0,
                    'best_grade': None,
                    'current_speed_round_streak': 0
                }
            })

        # Refresh GPA & accuracy including speed rounds
        try:
            if hasattr(current_user, 'update_gpa_and_accuracy'):
                current_user.update_gpa_and_accuracy()
                db.session.commit()
        except Exception as _e:
            print(f"WARNING /api/users/stats: refresh failed: {_e}")

        sr = session.get('speed_round') or {}
        current_sr_streak = sr.get('current_streak', 0) if sr.get('active') else 0

        resp = jsonify({
            'status': 'success',
            'authenticated': True,
            'stats': {
                'cumulative_gpa': float(getattr(current_user, 'cumulative_gpa', 0.0) or 0.0),
                'average_accuracy': float(getattr(current_user, 'average_accuracy', 0.0) or 0.0),
                'total_lifetime_points': int(getattr(current_user, 'total_lifetime_points', 0) or 0),
                'total_quizzes_completed': int(getattr(current_user, 'total_quizzes_completed', 0) or 0),
                'best_streak': int(getattr(current_user, 'best_streak', 0) or 0),
                'best_grade': getattr(current_user, 'best_grade', None),
                'current_speed_round_streak': int(current_sr_streak or 0),
                # 🐝 Buzz Dust Gamification Fields
                'total_buzz_dust': int(getattr(current_user, 'total_buzz_dust', 0) or 0),
                'bee_class': getattr(current_user, 'bee_class', 'Novice Bee'),
                'current_streak': int(getattr(current_user, 'current_streak', 0) or 0),
                'longest_streak': int(getattr(current_user, 'longest_streak', 0) or 0)
            }
        })
        try:
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        except Exception:
            pass
        return resp
    except Exception as e:
        print(f"❌ Error /api/users/stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ---------------------------------------------------------------------------
# Cross-role stats endpoints for viewing other users (teacher/parent/admin)
# ---------------------------------------------------------------------------
def _build_stats_payload_for_user(u: User) -> Dict[str, object]:
    """Internal helper to build a stats payload identical to /api/users/stats for any user.
    Performs a lightweight GPA/accuracy refresh before reading fields.
    """
    try:
        if hasattr(u, 'update_gpa_and_accuracy'):
            u.update_gpa_and_accuracy()
    except Exception as _e:
        print(f"WARNING _build_stats_payload_for_user: refresh failed for user_id={u.id}: {_e}")
    return {
        'cumulative_gpa': float(getattr(u, 'cumulative_gpa', 0.0) or 0.0),
        'average_accuracy': float(getattr(u, 'average_accuracy', 0.0) or 0.0),
        'total_lifetime_points': int(getattr(u, 'total_lifetime_points', 0) or 0),
        'total_quizzes_completed': int(getattr(u, 'total_quizzes_completed', 0) or 0),
        'best_streak': int(getattr(u, 'best_streak', 0) or 0),
        'best_grade': getattr(u, 'best_grade', None),
        # 🐝 Buzz Dust Gamification Fields
        'total_buzz_dust': int(getattr(u, 'total_buzz_dust', 0) or 0),
        'bee_class': getattr(u, 'bee_class', 'Novice Bee'),
        'current_streak': int(getattr(u, 'current_streak', 0) or 0),
        'longest_streak': int(getattr(u, 'longest_streak', 0) or 0)
    }

def _is_authorized_to_view_user(target: User) -> bool:
    """Return True if current_user is allowed to view target user's stats.
    Rules:
      * Admins can view everyone
      * The user themselves can view their own stats
      * Teachers/Parents can view students they are linked to via TeacherStudent
    """
    if not current_user.is_authenticated:
        return False
    if current_user.role == 'admin':
        return True
    if current_user.id == target.id:
        return True
    if current_user.role in ('teacher', 'parent'):
        try:
            link = TeacherStudent.query.filter_by(
                teacher_user_id=current_user.id,
                student_id=target.id,
                is_active=True
            ).first()
            if link:
                return True
        except Exception as _e:
            print(f"WARNING _is_authorized_to_view_user: link check failed: {_e}")
    return False

@app.route("/api/users/<int:user_id>/stats", methods=["GET"])
def api_get_specific_user_stats(user_id: int):
    """Return stats for a specific user (used by teacher/parent/admin dashboards for polling)."""
    try:
        target = User.query.get(user_id)
        if not target:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        if not _is_authorized_to_view_user(target):
            return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
        payload = _build_stats_payload_for_user(target)
        resp = jsonify({'status': 'success', 'user_id': user_id, 'stats': payload})
        try:
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        except Exception:
            pass
        return resp
    except Exception as e:
        print(f"❌ Error /api/users/<id>/stats: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to build stats'}), 500

@app.route("/api/users/stats/batch", methods=["GET"])
def api_get_batch_user_stats():
    """Batch stats endpoint: /api/users/stats/batch?ids=1,2,3
    Returns a dict keyed by user id for authorized targets.
    Unauthorized targets are omitted (or optionally reported)."""
    try:
        ids_param = request.args.get('ids', '')
        if not ids_param.strip():
            return jsonify({'status': 'error', 'message': 'No ids provided'}), 400
        raw_ids = [p.strip() for p in ids_param.split(',') if p.strip()]
        # Coerce to ints, ignore invalid
        id_list = []
        for r in raw_ids:
            try:
                id_list.append(int(r))
            except ValueError:
                continue
        if not id_list:
            return jsonify({'status': 'error', 'message': 'No valid ids'}), 400
        users = User.query.filter(User.id.in_(id_list)).all()
        response_map = {}
        unauthorized = []
        for u in users:
            if _is_authorized_to_view_user(u):
                response_map[u.id] = _build_stats_payload_for_user(u)
            else:
                unauthorized.append(u.id)
        result = {
            'status': 'success',
            'results': response_map
        }
        if unauthorized:
            result['unauthorized'] = unauthorized
        resp = jsonify(result)
        try:
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        except Exception:
            pass
        return resp
    except Exception as e:
        print(f"❌ Error /api/users/stats/batch: {e}")
        return jsonify({'status': 'error', 'message': 'Batch stats failed'}), 500


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
            # No user found, return default mascot (GLB-only)
            return jsonify({
                'status': 'success',
                'avatar': {
                    'avatar_id': 'mascot-bee',
                    'variant': 'default',
                    'name': 'Mascot Bee Avatar',
                    'urls': {
                        'glb': '/static/assets/avatars/glb_files/MascotBee.glb',
                        'thumbnail': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png'
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
                    'name': 'Mascot Bee Avatar',
                    'urls': {
                        'glb': '/static/assets/avatars/glb_files/MascotBee.glb',
                        'thumbnail': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png'
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
        # Return default mascot on error (GLB-only)
        return jsonify({
            'status': 'success',
            'avatar': {
                'avatar_id': 'mascot-bee',
                'variant': 'default',
                'name': 'Mascot Bee Avatar',
                'urls': {
                    'glb': '/static/assets/avatars/glb_files/MascotBee.glb',
                    'thumbnail': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png'
                }
            },
            'use_mascot': True
        })


@app.route("/api/users/me/avatar", methods=["PUT"])
@login_required
def api_update_my_avatar():
    """Update current user's avatar (convenience endpoint)"""
    return api_admin_or_user_update_avatar(current_user.id)


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

# Initialize GLB avatars on startup (idempotent)
if not FAST_BOOT:
    try:
        from init_glb_avatars import init_glb_avatars
        init_glb_avatars()
    except Exception as e:
        print(f"⚠️ GLB avatar initialization warning: {e}")
else:
    print("⏭️ Skipping init_glb_avatars() at startup (FAST_BOOT)")

# Validate and fix avatar thumbnail paths on EVERY startup (skipped in FAST_BOOT)
if not FAST_BOOT:
    try:
        with app.app_context():
            all_avatars = Avatar.query.filter_by(is_active=True).all()
            fixed_count = 0
            
            for avatar in all_avatars:
                if not avatar.thumbnail_file:
                    continue
                    
                current_thumb = avatar.thumbnail_file
                expected_thumb = None
                
                # GLB avatars MUST have AvatarThumbnails/ prefix
                if avatar.folder_path == 'glb_files':
                    filename = os.path.basename(current_thumb)
                    if not current_thumb.startswith('AvatarThumbnails/'):
                        expected_thumb = f'AvatarThumbnails/{filename}'
                
                # OBJ avatars MUST NOT have AvatarThumbnails/ prefix
                elif current_thumb.startswith('AvatarThumbnails/'):
                    expected_thumb = os.path.basename(current_thumb)
                
                # Fix if needed
                if expected_thumb and expected_thumb != current_thumb:
                    avatar.thumbnail_file = expected_thumb
                    fixed_count += 1
            
            if fixed_count > 0:
                db.session.commit()
                print(f"✅ [STARTUP] Fixed {fixed_count} avatar thumbnail paths")
            else:
                print(f"✅ [STARTUP] All {len(all_avatars)} avatar thumbnails validated - no fixes needed")
                
    except Exception as e:
        print(f"⚠️ [STARTUP] Avatar thumbnail validation warning: {e}")
        try:
            db.session.rollback()
        except:
            pass
else:
    print("⏭️ Skipping avatar thumbnail validation at startup (FAST_BOOT)")

def _is_port_free(p: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", p))
            return True
    except OSError:
        return False

def _pick_port(default_port: int) -> int:
    candidates = [default_port, 5051, 8080, 5500]
    for p in candidates:
        if _is_port_free(p):
            return p
    # As last resort, ask OS for an ephemeral free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    env_port = int(os.environ.get("PORT", 5000))
    port = _pick_port(env_port)
    # Respect FLASK_DEBUG env (0/1, true/false) and disable reloader for stable runs in terminals/CI
    debug_env = os.environ.get("FLASK_DEBUG", "0").strip().lower()
    debug = debug_env in ("1", "true", "yes", "on")
    if port != env_port:
        print(f"⚠️ Port {env_port} in use or unavailable; switching to {port}.")
    print(f"🚀 Starting development server on port {port} with Socket.IO support (debug={'on' if debug else 'off'})...")
    try:
        from app_socketio import socketio
        # Disable reloader to avoid parent-process exit that can confuse task runners
        socketio.run(app, host="0.0.0.0", port=port, debug=debug, use_reloader=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"⚠️ Failed to start with Socket.IO: {e}")
        print("🔄 Falling back to standard Flask server...")
        try:
            app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
        except OSError as oe:
            if getattr(oe, 'errno', None) == 48 or 'Address already in use' in str(oe):
                # Try another port automatically
                new_port = _pick_port(port + 1)
                print(f"⚠️ Port {port} busy; retrying on {new_port}...")
                app.run(host="0.0.0.0", port=new_port, debug=debug, use_reloader=False)
            else:
                raise
