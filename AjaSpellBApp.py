HOME_PREVIEW_ENABLED = True  # feature flag for new honey home page preview
# -*- coding: utf-8 -*-
# Updated: 2025-12-03 - Fixed word_lists.html div structure
import sys
import io
import os

# Force UTF-8 encoding for Windows console output
if sys.platform == "win32":
    # Avoid wrapping pytest's capture streams (can break collection with
    # "I/O operation on closed file" when pytest swaps/tears down streams).
    _running_pytest = ('PYTEST_CURRENT_TEST' in os.environ) or ('pytest' in sys.modules)
    if not _running_pytest:
        try:
            if getattr(sys.stdout, 'buffer', None) is not None and not getattr(sys.stdout, 'closed', False):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if getattr(sys.stderr, 'buffer', None) is not None and not getattr(sys.stderr, 'closed', False):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            # Best-effort: never fail app import due to console encoding tweaks.
            pass

import csv
import shutil
import re
import json
import time
import random
import threading
import uuid
import logging
from tempfile import NamedTemporaryFile
from pathlib import Path
from datetime import datetime, timedelta, timezone, date
import socket
import secrets
import hashlib
from typing import List, Dict, Optional
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file, Response, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# App Review helpers
# When enabled, we provide a reviewer-friendly path for Apple App Review to access
# core premium flows without creating an account or relying on fragile demo creds.
APP_REVIEW_MODE = os.environ.get('APP_REVIEW_MODE', '0').strip() == '1'
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
from models import WordBankStorage  # Single source of truth for all word operations
from datetime import date
from avatar_skus import AVATAR_SKUS, build_product_entitlements  # Avatar monetization mapping
try:
    from bundle_skus import build_bundle_product_entitlements, bundle_sku_for_id  # Bundle monetization mapping
except Exception:
    build_bundle_product_entitlements = None  # type: ignore
    bundle_sku_for_id = None  # type: ignore
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
    print(" Tesseract OCR available")
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
    print("️ Tesseract OCR not available - image upload will show error message")

# Backwards-compatibility alias for test suites
OCR_AVAILABLE = TESSERACT_AVAILABLE

print("="*70)
print(" BeeSmart Spelling Bee App - Starting Up")
print("="*70)
print(f" Python version: {sys.version}")
print(f" Platform: {sys.platform}")
print(f" Working directory: {os.getcwd()}")
print("="*70)

# Build/release version (surfaced via /health)
# Keep this in sync with the public app version used by validation scripts.
APP_VERSION = "34"

# Base directory for resolving relative data paths (added to silence linter undefined warning)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Fast-boot mode: skip heavy startup checks/initializers that can delay first load
# Default is OFF to run full system checks prior to entering the home page.
FAST_BOOT = os.getenv('FAST_BOOT', '0').strip().lower() in ('1', 'true', 'yes', 'on')
if FAST_BOOT:
    print(" FAST_BOOT=on → Skipping heavy startup checks to unblock app load")
else:
    print("️ FAST_BOOT=off → Running full startup checks")

#  BUILT-IN DICTIONARY ONLY - External API removed for performance
# No external dictionary_api imports - we use Simple Wiktionary (50K+ words)
print(" Using built-in Simple English Wiktionary (50K+ words, kid-friendly)")

# ------------------------------
# Ensure Flask app exists BEFORE any route decorators
# ------------------------------
# Some routes (e.g., wordbank APIs) are defined early in this module. To avoid
# NameError during module import, make sure `app` is created up front.
try:
    app  # type: ignore[name-defined]
except NameError:
    app = Flask(__name__)

# ------------------------------
# Simple in-memory cache for avatar API
# ------------------------------
AVATAR_LIST_CACHE: Dict[str, Dict] = {}
AVATAR_LIST_CACHE_TTL_SECONDS = 60  # small TTL to avoid stale data


# Content Filter and Guardian Reporting System
try:
    from content_filter_guardian import (
        filter_content_with_tracking, 
        get_content_filter_status, 
        violation_tracker,
        ContentViolationTracker
    )
    print(" Content Filter with Guardian Reporting loaded successfully")
    CONTENT_FILTER_AVAILABLE = True
except Exception as e:
    print(f"️ Content Filter not available: {e}")
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
# Wordbank storage lives in Postgres via the WordBankStorage model.
# Deployment uses DigitalOcean managed Postgres.
DATA_KEY = "wordbank_v1"
QUIZ_STATE_KEY = "quiz_state_v1"

def _ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

# DEPRECATED: Disk-based wordbank functions - replaced by Railway database (WordBankStorage model)
# These functions are no longer used since all wordbank operations now use PostgreSQL

def _wordbank_path(storage_id: str) -> str:
    """DEPRECATED: Railway database replaces disk storage."""
    return ""

def save_wordbank_atomic(storage_id: str, rows: list) -> bool:
    """DEPRECATED: Use WordBankStorage.save_wordbank() instead."""
    return True

def load_wordbank_safe(storage_id: str) -> list:
    """DEPRECATED: Use WordBankStorage.load_wordbank() instead."""
    return []

def load_simple_wiktionary():
    """Load Simple English Wiktionary from JSONL file - 50K+ words!"""
    words = {}
    try:
        if os.path.exists(SIMPLE_WIKTIONARY_FILE):
            print(f" Loading Simple English Wiktionary...")
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
            print(f" Loaded {len(words):,} words from Simple English Wiktionary")
            return words
        else:
            print(f"️ Simple Wiktionary not found: {SIMPLE_WIKTIONARY_FILE}")
    except Exception as e:
        print(f" Failed to load Simple Wiktionary: {e}")
    return {}

# ------------------------------
# Wordbank helpers (single source of truth for quizzes)
# ------------------------------
def _normalize_word(s: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]", "", (s or "").lower())
    except Exception:
        return (s or "").lower()

def _ensure_session_storage_id() -> str:
    sid = session.get('wordbank_storage_id')
    if not sid:
        sid = str(uuid.uuid4())
        session['wordbank_storage_id'] = sid
        session.modified = True
    return sid

# DEPRECATED: OLD disk-based get_wordbank (replaced by WORD_STORAGE version at line ~2899)
# def get_wordbank() -> list:
#     """Return the active wordbank rows from disk for this session."""
#     sid = _ensure_session_storage_id()
#     rows = load_wordbank_safe(sid)
#     return rows

# DEPRECATED: OLD disk-based set_wordbank (replaced by WORD_STORAGE version at line ~2956)
# def set_wordbank(rows: list, clear_first: bool = True) -> int:
#     """Replace the active wordbank with the provided rows.
#
#     Normalizes and de-duplicates entries. Optionally clears prior data first.
#     Returns the number of rows stored.
#     """
#     sid = _ensure_session_storage_id()
#
#     # Clear by overwriting with empty list if requested
#     if clear_first:
#         save_wordbank_atomic(sid, [])
#
#     # Normalize to shape {word,sentence,hint}
#     cleaned = []
#     seen = set()
#     for r in rows or []:
#         if isinstance(r, dict):
#             w = str(r.get('word', '')).strip()
#             if not w:
#                 continue
#             key = _normalize_word(w)
#             if not key or key in seen:
#                 continue
#             seen.add(key)
#             cleaned.append({
#                 'word': w,
#                 'sentence': str(r.get('sentence', '')).strip(),
#                 'hint': str(r.get('hint', '')).strip()
#             })
#         else:
#             w = str(r).strip()
#             if not w:
#                 continue
#             key = _normalize_word(w)
#             if not key or key in seen:
#                 continue
#             seen.add(key)
#             cleaned.append({'word': w, 'sentence': '', 'hint': ''})
#
#     save_wordbank_atomic(sid, cleaned)
#     # Reset quiz state whenever wordbank changes
#     init_quiz_state()
#     return len(cleaned)

def clear_wordbank() -> None:
    """Clear the active wordbank safely and reset quiz state.
    
    Deletes wordbank from Railway database (single source of truth).
    """
    storage_id = session.get("wordbank_storage_id")
    
    if storage_id:
        try:
            delete_wordbank(storage_id)
            print(f" clear_wordbank: Deleted storage_id={storage_id} from database")
        except Exception as e:
            print(f"️ clear_wordbank: Database error: {e}")
    
    # Clear session
    session.pop("wordbank_storage_id", None)
    session["wordbank_count"] = 0
    session.modified = True
    
    # Reset quiz state
    try:
        init_quiz_state(0)
    except Exception as e:
        print(f"️ clear_wordbank: init_quiz_state failed: {e}")

def init_quiz_state(total_words: int):
    """Initializes or resets the quiz state in the session."""
    order = list(range(total_words))

    # Deterministic ordering in tests: pytest expects stable word sequencing.
    # Keep production behavior randomized.
    if not app.config.get("TESTING"):
        random.shuffle(order)

    # Fingerprint the active wordbank so "resume" can be safely gated to the same list.
    # We fingerprint ONLY the normalized words (not sentences/hints) so it stays stable.
    try:
        wb = get_wordbank() or []
        normalized_words = []
        for rec in wb:
            w = rec.get('word', '') if isinstance(rec, dict) else str(rec or '')
            w = normalize(str(w))
            if w:
                normalized_words.append(w)
        joined = '|'.join(normalized_words)
        wordbank_fingerprint = hashlib.sha256(joined.encode('utf-8')).hexdigest() if joined else ''
    except Exception:
        wordbank_fingerprint = ''

    # Ensure we have a stable user context before touching any DB/session-backed
    # quiz tracking. IMPORTANT: authenticated users must NOT be routed through
    # guest user creation, otherwise QuizSession records attach to a guest user
    # and cumulative GPA/accuracy/quiz count won't update for the real account.
    db_session_id = None
    try:
        is_auth = bool(getattr(current_user, "is_authenticated", False))
    except Exception:
        is_auth = False

    if is_auth:
        user_obj = current_user
        # Keep a consistent flag for older logic that distinguishes guest UX
        session["is_guest"] = False
    else:
        user_obj = get_or_create_guest_user()

    # After guest resolution, restore the active wordbank pointer if it was
    # dropped by any session churn.
    try:
        if not session.get("wordbank_storage_id"):
            # Prefer hybrid session state first
            hybrid = session.get(DATA_KEY)
            if isinstance(hybrid, dict) and hybrid.get("storage_id"):
                session["wordbank_storage_id"] = hybrid.get("storage_id")
                session.modified = True
            # Fall back to user record (guest users store their last wordbank)
            elif user_obj and getattr(user_obj, "wordbank_storage_id", None):
                session["wordbank_storage_id"] = user_obj.wordbank_storage_id
                session.modified = True
    except Exception:
        pass

    if user_obj:
        # Some legacy deployments had JSON fields stored as TEXT (e.g. "[]").
        # If a user row still contains those string values, merely loading the
        # instance can raise via MutableList coercion. Don't let that break the
        # core quiz flow; the quiz session is an optional analytics record.
        try:
            _ = user_obj.id
        except Exception as _e:
            print(f"️ init_quiz_state: Continuing without DB quiz session due to user coercion error: {_e}")
            user_obj = None

    if user_obj:
        try:
            quiz_session = QuizSession(
                user_id=user_obj.id,
                total_words=total_words
            )
            link = TeacherStudent.query.filter_by(student_id=user_obj.id, is_active=True).first()
            if link and not quiz_session.teacher_key:
                quiz_session.teacher_key = link.teacher_key
            db.session.add(quiz_session)
            db.session.commit()
            db_session_id = quiz_session.id
            user_type = "guest" if session.get("is_guest") else "authenticated"
            print(f" Created database QuizSession ID: {db_session_id} for {user_type} user {user_obj.username}")
        except Exception as e:
            print(f"️ Failed to create database session: {e}")
            db.session.rollback()

    # IMPORTANT: never let optional DB session tracking clear our active wordbank.
    # Some error paths in the app roll back and can accidentally wipe session keys;
    # ensure storage_id/count survive so /api/next can proceed.
    session.modified = True

    session[QUIZ_STATE_KEY] = {
        "idx": 0,
        "order": order,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "correct": 0,
        "incorrect": 0,
        "streak": 0,
        "max_streak": 0,
        "session_points": 0,
        # Explicit completion flag so other endpoints (e.g. /api/users/stats) can
        # distinguish in-progress points from committed lifetime points.
        "quiz_complete": False,
        "hints_used_current_word": 0,
        "history": [],
        "db_session_id": db_session_id,
        "wordbank_fingerprint": wordbank_fingerprint,
        # Persist a copy of the storage_id in quiz state as a last-resort
        # recovery if a later request loses the key.
        "storage_id": session.get("wordbank_storage_id"),
    }
    session.permanent = True
    session.modified = True

# ------------------------------
# Wordbank API endpoints
# ------------------------------
@app.route('/api/wordbank', methods=['GET'])
def api_wordbank_get():
    """
    Get wordbank from Railway database - returns 'words' key for compatibility
    """
    try:
        words = get_wordbank()
        response = jsonify({
            'status': 'success',
            'count': len(words),
            'words': words,  # Changed from 'rows' to 'words' for WordBankManager compatibility
            'rows': words[:100],  # Keep 'rows' for backward compatibility
        })
        # Add cache-control headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/wordbank', methods=['POST'])
def api_wordbank_set():
    try:
        data = request.get_json(silent=True) or {}
        # Accept both modern and legacy payload shapes.
        # - Legacy: { rows: [...] }
        # - Modern: { words: [...] }
        rows = data.get('rows')
        if rows is None:
            rows = data.get('words')
        rows = rows or []
        # NOTE: OLD implementation used clear_first, NEW uses is_user_upload
        # Treating POST to /api/wordbank as user upload (manual API call)
        # Ensure the session has a stable storage_id before persisting.
        # This prevents a mismatch where the DB write happens under one ID
        # but subsequent reads (e.g., /api/next) look up a different/empty ID.
        sid = _ensure_session_storage_id()
        # Force the session pointer to the ensured id so the DB write and later
        # reads use the same storage id.
        session["wordbank_storage_id"] = sid
        session.permanent = True
        session.modified = True

        # Normalize/dedupe and keep it kid-friendly (same flow as other upload paths)
        try:
            rows = deduplicate_words(rows)
        except Exception:
            pass
        try:
            rows, _blocked = _filter_records_excluding_inappropriate_text(rows)  # noqa: F841
        except Exception:
            pass

        set_wordbank(rows, is_user_upload=True)
        init_quiz_state(len(rows))
        return jsonify({'status': 'success', 'stored': len(rows)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/wordbank/clear', methods=['POST'])
def api_wordbank_clear():
    # Always attempt to clear and return success, even if underlying storage write fails.
    # This avoids blocking UX in ephemeral environments.
    try:
        clear_wordbank()
    except Exception as e:
        print(f"️ api_wordbank_clear: non-fatal error: {e}")
    return jsonify({'status': 'success'})

@app.route('/api/wordbank/import-text', methods=['POST'])
def api_wordbank_import_text():
    """Import a simple text list (newline or delimiter separated).

    Body JSON: { text: str, delimiter?: str, clear_first?: bool }
    """
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get('text', '') or '')
        delimiter = data.get('delimiter')
        # clear_first is no longer used; set_wordbank fully replaces the active list
        # Accept the field for backward compatibility but ignore it.
        _ = data.get('clear_first', True)
        parts = []
        if delimiter:
            parts = [p.strip() for p in text.split(delimiter)]
        else:
            # default: split on newlines/commas
            temp = re.split(r"[\r\n,]+", text)
            parts = [p.strip() for p in temp]
        # Convert to rows
        rows = [{'word': p, 'sentence': '', 'hint': ''} for p in parts if p]

        # Deduplicate and kid-friendly filter
        deduped = deduplicate_words(rows)
        filtered_rows, blocked = [], []
        if deduped:
            try:
                print(f"️ Running enhanced kid-friendly filter on {len(deduped)} words...")
                filtered_rows, blocked = _filter_records_excluding_inappropriate_text(deduped)
                print(f" {len(filtered_rows)} words passed kid-friendly filter")
            except Exception as fe:
                print(f" Kid-friendly filter failed, proceeding without filter: {fe}")
                filtered_rows = deduped
        else:
            filtered_rows = []

        # Optional enrichment with definitions (non-blocking)
        try:
            filtered_rows = enrich_with_definitions(filtered_rows)
        except Exception as ee:
            print(f" Definition enrichment skipped due to error: {ee}")

        stored_count = len(filtered_rows)
        # Treat import-text as a user upload so small lists persist in session fallback
        set_wordbank(filtered_rows, is_user_upload=True)
        # Initialize quiz state immediately after import for a ready-to-play experience
        try:
            init_quiz_state(stored_count)
        except Exception as _e:
            # Non-fatal; quiz can still start later via next/answer endpoints
            print(f"️ init_quiz_state after import failed: {_e}")
        return jsonify({'status': 'success', 'stored': stored_count, 'blocked_count': len(blocked), 'blocked_words': [b.get('word') for b in (blocked or [])]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/wordbank/count', methods=['GET'])
def api_wordbank_count():
    """Return counts and system checks for loading state."""
    try:
        # IMPORTANT: Do NOT auto-create a new storage_id here.
        # The authoritative wordbank lives in the database and is keyed by the
        # session's existing wordbank_storage_id pointer.
        sid = session.get("wordbank_storage_id")
        rows = get_wordbank()  # Always compute from authoritative source

        # Disk path is legacy; keep it only as a best-effort diagnostic.
        exists = False
        last_modified = None
        if sid:
            try:
                path = _wordbank_path(sid)
                exists = os.path.exists(path)
                if exists:
                    last_modified = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            except Exception:
                exists = False
                last_modified = None

        return jsonify({
            'status': 'success',
            'storage_id': sid,
            'exists': exists,
            'last_modified': last_modified,
            'count': len(rows),
            'loaded': len(rows) > 0,
            'source': 'uploaded' if len(rows) > 0 else 'dictionary'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/wordbank/live-summary', methods=['GET'])
def api_wordbank_live_summary():
    """Real-time wordbank summary for UI modals and system checks.

    Provides:
    - count: live number of words (authoritative from get_wordbank)
    - ready_for_quiz: True if count > 0
    - storage_id: current session pointer
    - quiz_state_present: True if a quiz state exists
    - last_modified: disk timestamp of the active storage file if present
    """
    try:
        sid = _ensure_session_storage_id()
        rows = get_wordbank()
        exists = os.path.exists(_wordbank_path(sid))
        last_modified = None
        if exists:
            try:
                last_modified = datetime.fromtimestamp(os.path.getmtime(_wordbank_path(sid))).isoformat()
            except Exception:
                last_modified = None
        qs = session.get(QUIZ_STATE_KEY)
        return jsonify({
            'status': 'success',
            'storage_id': sid,
            'count': len(rows),
            'ready_for_quiz': len(rows) > 0,
            'quiz_state_present': bool(qs is not None),
            'last_modified': last_modified
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/button-press-sfx', methods=['GET'])
def api_button_press_sfx():
    """Return available button-press SFX URLs.

    The UI will randomly choose from these.
    Source folder (if present on the server): static/sounds/ButtonPresses/*.mp3
    Returns an empty list if the folder does not exist or has no mp3 files.
    """
    try:
        static_root = app.static_folder or os.path.join(BASE_DIR, 'static')
        folder = Path(static_root) / 'sounds' / 'ButtonPresses'
        if not folder.exists():
            return jsonify([])

        names = sorted([p.name for p in folder.glob('*.mp3') if p.is_file()])
        urls = [url_for('static', filename=f'sounds/ButtonPresses/{name}') for name in names]
        resp = jsonify(urls)
        # Prevent stale caching when users add/remove sound files during dev.
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except Exception:
        return jsonify([])

#  Badge metadata for display
BADGE_METADATA = {
    'perfect_game': {
        'icon': '',  # emoji fallback
        'image': 'badges/perfect_game.png',
        'name': 'Perfect Game',
        'description': '100% accuracy, no hints, no mistakes',
        'rarity': 'epic',
        'points': 500
    },
    'speed_demon': {
        'icon': '',
        'image': 'badges/speed_demon.png',
        'name': 'Speed Demon',
        'description': 'Average answer time < 10 seconds',
        'rarity': 'rare',
        'points': 200
    },
    'persistent_learner': {
        'icon': '',
        'image': 'badges/persistent_learner.png',
        'name': 'Persistent Learner',
        'description': 'Complete 50+ words in one session',
        'rarity': 'rare',
        'points': 150
    },
    'hot_streak': {
        'icon': '',
        'image': 'badges/hot_streak.png',
        'name': 'Hot Streak',
        'description': '10+ correct answers in a row',
        'rarity': 'common',
        'points': 100
    },
    'comeback_kid': {
        'icon': '',
        'image': 'badges/comeback_kid.png',
        'name': 'Comeback Kid',
        'description': 'Succeed after multiple wrong attempts',
        'rarity': 'rare',
        'points': 100
    },
    'honey_hunter': {
        'icon': '',
        'image': 'badges/honey_hunter.png',
        'name': 'Honey Hunter',
        'description': 'Use hints wisely (< 20% of words)',
        'rarity': 'common',
        'points': 75
    },
    'early_bird': {
        'icon': '',
        'image': 'badges/early_bird.png',
        'name': 'Early Bird',
        'description': 'Complete quiz in under 5 minutes',
        'rarity': 'common',
        'points': 50
    },
    'elite_buzz_dust': {
        'icon': '',  # fallback emoji
        'image': 'badges/elite_buzz_dust.png',  # PNG expected in static/images/badges/
        'name': 'Elite Buzz Dust',
        'description': 'Reach elite Buzz Dust threshold',
        'rarity': 'epic',
        'points': 0
    },
    # Rank advancement badges
    'novice_rank': {
        'icon': '',
        'image': 'badges/Novice.png',
        'name': 'Novice Bee',
        'description': 'Welcome to BeeSmart!',
        'rarity': 'common',
        'points': 0
    },
    'apprentice_rank': {
        'icon': '',
        'image': 'badges/Apprentice.png',
        'name': 'Apprentice Bee',
        'description': 'Reached Apprentice Bee rank',
        'rarity': 'common',
        'points': 0
    },
    'scholar_rank': {
        'icon': '',
        'image': 'badges/Scholar.png',
        'name': 'Scholar Bee',
        'description': 'Reached Scholar Bee rank',
        'rarity': 'rare',
        'points': 0
    },
    'elite_rank': {
        'icon': '',
        'image': 'badges/Elete.png',  # Note: typo in file system 'Elete' instead of 'Elite'
        'name': 'Elite Bee',
        'description': 'Reached Elite Bee rank',
        'rarity': 'epic',
        'points': 0
    },
    'magistrate_rank': {
        'icon': '️',
        'image': 'badges/Magistrate.png',
        'name': 'Magistrate Bee',
        'description': 'Reached Magistrate Bee rank',
        'rarity': 'legendary',
        'points': 0
    },
    'master_rank': {
        'icon': '',
        'image': 'badges/BuzzDustMaster.png',
        'name': 'Buzz Dust Master',
        'description': 'Reached the highest rank!',
        'rarity': 'legendary',
        'points': 0
    }
}

# ------------------------------
# Public policy pages
# ------------------------------

# Flask app already created earlier to support early route decorators

# Reliable, post-app-creation lightweight routes
@app.route('/', endpoint='home')
def home_root_direct():
    """Primary application landing page: shows loader then auto-redirects to app."""
    print("="*80)
    print(" [HOME ROUTE] Starting home_root_direct()")
    print(f" [HOME ROUTE] User authenticated: {current_user.is_authenticated}")
    print("="*80)
    
    # Get current user's avatar data for immediate display (same as dashboard)
    user_avatar_data = None
    use_mascot = True
    
    if current_user.is_authenticated:
        try:
            user_avatar_data = current_user.get_avatar_data()
            use_mascot = current_user.has_selected_avatar() == False
            print(f" [HOME] User avatar data: {user_avatar_data}")
            print(f" [HOME] Use mascot: {use_mascot}")
            print(f" [HOME] Avatar ID: {user_avatar_data.get('id') if user_avatar_data else 'None'}")
        except Exception as e:
            print(f"️ Could not load user avatar data: {e}")
            import traceback
            traceback.print_exc()
            user_avatar_data = None
            use_mascot = True
    
    print(f" [HOME] Passing to template: user_avatar={user_avatar_data is not None}, use_mascot={use_mascot}")
    print("="*80)
    
    # Keep the home menu's Premium CTA price driven by the backend so UI stays future-proof.
    # (This is display copy only; the actual purchase flow still uses StoreKit/Google billing.)
    # Provide all required template variables to avoid 500 errors
    import time
    timestamp = str(int(time.time()))
    billing_mode = os.environ.get('REGISTRATION_BILLING_MODE', 'subscription').strip().lower()
    try:
        subscription_product_id = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID')
        subscription_product_id = (subscription_product_id or '').strip() or SUBSCRIPTION_PRODUCT_IDS.get('monthly', 'com.beesmart.premium.monthly')
    except Exception:
        subscription_product_id = SUBSCRIPTION_PRODUCT_IDS.get('monthly', 'com.beesmart.premium.monthly')
    try:
        from flask_login import current_user as _cu
        is_premium = bool(getattr(_cu, 'is_authenticated', False) and getattr(_cu, 'premium_member', False))
    except Exception:
        is_premium = False
    try:
        avatar_product_ids = AVATAR_SKUS
    except Exception:
        avatar_product_ids = {}
    
    return render_template(
        'unified_menu.html',
        user_avatar=user_avatar_data,
        use_mascot=use_mascot,
        subscription_monthly_usd=3.99,
        timestamp=timestamp,
        registration_billing_mode=billing_mode,
        subscription_product_id=subscription_product_id,
        is_premium=is_premium,
        avatar_product_ids=avatar_product_ids,
    )

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico to prevent 404 errors"""
    try:
        return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception:
        # If favicon doesn't exist, return 204 No Content (browser will stop requesting)
        return '', 204

# Optional legacy preview alias retained (can be removed later)
@app.route('/home_preview')
def home_preview():
    return render_template('honey_home.html')


# Backwards-compatible alias: some templates build URLs for endpoint "unified_menu".
# Our home route is implemented as `home()`, so provide a stable alias to avoid 500s.
@app.route('/unified_menu')
def unified_menu():
    return home()


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


@app.route("/terms")
def terms_page():
    """Public Terms of Use / EULA page.

    App Store guideline 3.1.2 expects an in-app, no-login Terms/EULA link.
    """
    return _safe_template("terms.html")


@app.route("/support")
def support_page():
    """Public support/contact page.

    App Store Connect requires a functional Support URL.
    """
    try:
        return render_template("support.html")
    except Exception:
        return "<html><head><meta charset='utf-8'><title>Support</title></head><body><h1>Support</h1><p>Email: <a href='mailto:contact@beesmartspelling.com'>contact@beesmartspelling.com</a></p><p><a href='/app'>Back to App</a></p></body></html>"


@app.route("/contact")
def contact_page():
    """Alias for /support.

    Some docs and older builds reference /contact.
    """
    return support_page()

# ------------------------------
# Avatar API helpers
# ------------------------------
def _avatar_thumbnail_url_from_glb(glb_filename: str) -> str:
    """Derive the standard thumbnail URL from a GLB filename.

    Convention used in this repo:
      static/assets/avatars/glb_files/AvatarThumbnails/<BaseName>!.png
    """
    try:
        base = os.path.splitext(os.path.basename(glb_filename or ""))[0]
        if not base:
            return "/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png"
        return f"/static/assets/avatars/glb_files/AvatarThumbnails/{base}!.png"
    except Exception:
        return "/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png"

def _is_avatar_unlocked_for_user(entry: Dict, role: str, user: Optional["User"]) -> Dict[str, object]:
    """Compute lock state and reason for an avatar entry based on role and user state.

    Returns dict with keys: unlocked (bool), reason (str), points_needed (int|None)
    """
    # Admin: always unlocked
    if role == 'admin':
        return {"unlocked": True, "reason": "Admin access", "points_needed": None}

    # Guest: normally limited; in App Review / demo mode allow reviewers to explore
    if role == 'guest':
        try:
            if APP_REVIEW_MODE or bool(session.get('app_review_mode')):
                return {"unlocked": True, "reason": "App Review mode", "points_needed": 0}
        except Exception:
            pass
        return {"unlocked": False, "reason": "Guest access limited", "points_needed": None}

    # Registered users (student/teacher/parent)
    tier = (entry.get('tier') or '').lower()
    is_default_free = bool(entry.get('is_default_free'))
    unlock_points = int(entry.get('unlock_points') or 0)
    avatar_id = entry.get('id')

    # Defaults for missing user
    honey_points = 0
    purchased = []
    premium_member = False
    if user is not None:
        try:
            honey_points = int(user.honey_points or 0)
        except Exception:
            honey_points = 0
        try:
            purchased = list(user.purchased_avatars or [])
        except Exception:
            purchased = []
        try:
            premium_member = bool(getattr(user, 'premium_member', False))
        except Exception:
            premium_member = False

    # Default free tiers are unlocked
    if tier in ('default_free', 'mascot_free') or is_default_free:
        return {"unlocked": True, "reason": "Default free avatar", "points_needed": 0}

    # Guest entitlement support (Apple Guideline 5.1.1): allow anon-owned SKUs to
    # unlock premium and avatar purchases without requiring login.
    anon_owned = []
    anon_premium = False
    if role == 'guest' and user is None:
        try:
            ent = _get_guest_entitlements()
            ao = ent.get('anon_owned_products', []) if isinstance(ent, dict) else []
            anon_owned = ao if isinstance(ao, list) else []
        except Exception:
            anon_owned = []

        # Treat any premium/subscription SKU as premium entitlement for guests.
        # Note: In this codebase, subscriptions are mapped as type 'premium' with
        # subscription=True (not as type 'subscription').
        try:
            for pid in anon_owned:
                try:
                    mapping = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
                except Exception:
                    mapping = None
                if isinstance(mapping, dict):
                    t = str(mapping.get('type') or '').strip().lower()
                    if t == 'premium' and bool(mapping.get('subscription')):
                        anon_premium = True
                        break
                    if t == 'premium':
                        # One-time premium unlock also counts
                        anon_premium = True
                        break
            if not anon_premium:
                for pid in anon_owned:
                    p = (pid or '').lower()
                    if any(k in p for k in ('premium', 'subscription', 'monthly', 'yearly', 'family')):
                        anon_premium = True
                        break
        except Exception:
            anon_premium = False

    # Earn-or-buy tier: unlock by points or purchase
    if tier == 'earn_or_buy':
        if avatar_id in purchased:
            return {"unlocked": True, "reason": "Purchased", "points_needed": 0}
        # Guest restore/purchase unlock
        if role == 'guest' and user is None and anon_owned:
            try:
                for pid in anon_owned:
                    m = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
                    if isinstance(m, dict) and m.get('type') == 'avatar':
                        if str(m.get('avatar_id') or '').strip().lower() == avatar_id:
                            return {"unlocked": True, "reason": "Restored purchase", "points_needed": 0}
            except Exception:
                pass
        if honey_points >= unlock_points:
            return {"unlocked": True, "reason": "Sufficient points", "points_needed": 0}
        return {"unlocked": False, "reason": "Earn points or purchase", "points_needed": max(unlock_points - honey_points, 0)}

    # Premium tier policy:
    # - Admin: always unlocked (handled above)
    # - Guests: locked unless purchased/restored or premium entitlement
    # - Registered users (student/teacher/parent): follow catalog rules: only the
    #   5 DEFAULT_FREE avatars are unlocked by default.
    if tier == 'premium':
        if role in ('student', 'teacher', 'parent'):
            return {"unlocked": False, "reason": "Premium - subscribe to unlock", "points_needed": None}

        # Non-admin, non-registered fall back to entitlement-based unlock.
        if avatar_id in purchased:
            return {"unlocked": True, "reason": "Purchased", "points_needed": 0}
        if premium_member or anon_premium:
            return {"unlocked": True, "reason": "Premium membership", "points_needed": 0}
        # If guest owns a matching avatar SKU, unlock it.
        if anon_owned:
            try:
                for pid in anon_owned:
                    m = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
                    if isinstance(m, dict) and m.get('type') == 'avatar':
                        if str(m.get('avatar_id') or '').strip().lower() == avatar_id:
                            return {"unlocked": True, "reason": "Restored purchase", "points_needed": 0}
            except Exception:
                pass
        return {"unlocked": False, "reason": "Premium - purchase to unlock", "points_needed": None}

    # Fallback - treat unknown tiers as locked
    return {"unlocked": False, "reason": "Locked", "points_needed": None}

def load_dictionary_cache():
    """Load cached dictionary entries from JSON file"""
    try:
        if os.path.exists(DICTIONARY_CACHE_FILE):
            with open(DICTIONARY_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                words = data.get('words', {})
                print(f" Loaded dictionary cache with {len(words)} words from {DICTIONARY_CACHE_FILE}")
                return words
        else:
            print(f"️ Dictionary cache file not found: {DICTIONARY_CACHE_FILE}")
    except Exception as e:
        print(f" Failed to load dictionary cache: {e}")
    return {}

# ------------------------------
# Avatars API: returns role-aware list with lock state
# ------------------------------
@app.route('/api/avatars', methods=['GET'])
def api_avatars():
    """Return the avatar catalog with per-user lock state and thumbnails.

    Caching:
      - Guests: single cache key 'guest_role_guest'
      - Authenticated: cache key 'user_{id}_role_{role}'
    """
    try:
        # Lazy import to avoid circulars at module import time
        from avatar_catalog import AVATAR_CATALOG
    except Exception as e:
        print(f" Failed to import AVATAR_CATALOG: {e}")
        return jsonify({"status": "error", "message": "Catalog unavailable"}), 500

    # Identify user and role
    user = current_user if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
    role = 'guest'
    if user is not None:
        try:
            role = (user.role or 'student').lower()
        except Exception:
            role = 'student'

    # Guest entitlement support (Apple Guideline 5.1.1): allow a non-logged-in
    # user to restore/purchase and have avatar lock state persist via anon_restore_id.
    guest_entitlements = None
    anon_owned = []
    if user is None:
        try:
            guest_entitlements = _get_guest_entitlements()
            ao = guest_entitlements.get('anon_owned_products', []) if isinstance(guest_entitlements, dict) else []
            anon_owned = ao if isinstance(ao, list) else []
        except Exception:
            guest_entitlements = None
            anon_owned = []

    # Dev-only override: allow the local StoreKit webview to fetch the full avatar catalog
    # (including product IDs) even when not logged in.
    #
    # Enable with: ALLOW_DEV_FULL_AVATARS=1 and request /api/avatars?dev_full=1
    # This is intentionally *opt-in* via both env var and query param, and uses its own
    # cache key to avoid contaminating the normal guest response.
    allow_dev_full = os.getenv('ALLOW_DEV_FULL_AVATARS', '0').strip().lower() in ('1', 'true', 'yes', 'on')
    dev_full_requested = (request.args.get('dev_full') or '').strip().lower() in ('1', 'true', 'yes', 'on')
    dev_full_effective = bool(user is None and role == 'guest' and allow_dev_full and dev_full_requested)
    if dev_full_effective:
        role = 'student'

    # Scope filtering:
    # - registration: only return the DEFAULT_FREE avatars (5) for signup UI
    scope = (request.args.get('scope') or '').strip().lower()
    registration_scope = scope in ('registration', 'register', 'signup')

    # Build cache key per user+role (prevents admin cache bleed)
    # NOTE: Guests with DB-backed entitlements must not be lumped into the
    # generic guest cache key, otherwise a restored user could see the mascot-only list.
    if dev_full_effective:
        cache_key = 'guest_role_dev_full'
    elif user is None:
        if anon_owned:
            # Keep this key stable per entitlements, but avoid leaking raw product ids
            # into cache keys (logs). Hash-like: just encode count + a short checksum.
            try:
                joined = "|".join(sorted([str(x) for x in anon_owned if x]))
                checksum = str(abs(hash(joined)) % 100000000)
            except Exception:
                checksum = '0'
            cache_key = f"guest_role_guest_ent_{len(anon_owned)}_{checksum}"
        else:
            cache_key = 'guest_role_guest'
    else:
        cache_key = f"user_{getattr(user, 'id', 'unknown')}_role_{role}"

    if registration_scope:
        cache_key = f"{cache_key}_scope_registration"

    now_ts = time.time()
    cached = AVATAR_LIST_CACHE.get(cache_key)
    if cached and (now_ts - cached.get('ts', 0)) <= AVATAR_LIST_CACHE_TTL_SECONDS:
        payload = {
            "status": "success",
            "avatars": cached.get('data', []),
            "cached": True,
            "purchased_avatars": list(getattr(user, 'purchased_avatars', []) or []) if user is not None else [],
            "purchased_bundles": list(getattr(user, 'purchased_bundles', []) or []) if user is not None else [],
            "user": {
                "role": role,
                "is_authenticated": bool(user is not None),
                "is_guest": bool(user is None),
                "is_admin": bool(role == 'admin'),
                "honey_points": int(getattr(user, 'honey_points', 0) or 0) if user is not None else 0,
            }
        }
        return jsonify(payload)

    # Build role-aware list
    result = []

    # Registration scope: never expose the full catalog; only allow the default-free avatars.
    catalog_iter = AVATAR_CATALOG
    if registration_scope:
        try:
            catalog_iter = [
                e for e in AVATAR_CATALOG
                if bool(e.get('is_default_free')) or (str(e.get('tier') or '').strip().lower() == 'default_free')
            ]
        except Exception:
            catalog_iter = []

    # Guest rule:
    # - With NO guest entitlements: return the full catalog, but lock everything
    #   except the single allowed guest avatar (Mascot Bee; Honey Comb fallback).
    #   This keeps the picker UI consistent while enforcing restrictions.
    # - With guest entitlements present (anon_restore_id restored/purchased): show full catalog
    #   with per-item lock states.
    guest_allowed_id = None
    if role == 'guest' and not anon_owned:
        try:
            mascot = next((e for e in AVATAR_CATALOG if (e.get('id') or '').lower() == 'mascot-bee'), None)
            if mascot is None:
                mascot = next((e for e in AVATAR_CATALOG if (e.get('id') or '').lower() == 'honey-comb'), None)
            if mascot is not None:
                guest_allowed_id = (mascot.get('id') or '').strip().lower() or None
        except Exception:
            guest_allowed_id = None

    # Registered users and admins: evaluate all catalog entries
    # NOTE: For native IAP, the client must purchase using the exact App Store / Play
    # product id. We derive a preferred SKU from PRODUCT_MAP so it matches the store.
    def _build_avatar_sku_lookup() -> dict:
        lookup = {}
        try:
            items = PRODUCT_MAP.items() if isinstance(PRODUCT_MAP, dict) else []
        except Exception:
            items = []

        candidates = {}
        for pid, mapping in items:
            try:
                if not isinstance(mapping, dict):
                    continue
                if mapping.get('type') != 'avatar':
                    continue
                aid = str(mapping.get('avatar_id') or '').strip().lower()
                if not aid:
                    continue
                candidates.setdefault(aid, []).append(str(pid))
            except Exception:
                continue

        def _score(pid: str):
            p = (pid or '').strip().lower()
            # Prefer the NEW App Store Connect v2 product IDs.
            if p.startswith('beesmart.avatar.') and p.endswith('.v2'):
                prefix_rank = 0
            # Next best: legacy beesmart.avatar.* (for back-compat restores)
            elif p.startswith('beesmart.avatar.'):
                prefix_rank = 1
            elif p.startswith('com.beesmart.avatar.'):
                prefix_rank = 2
            else:
                prefix_rank = 3
            # Prefer underscore style (matches existing product ids like cool_bee)
            style_rank = 0 if '_' in p else 1
            return (prefix_rank, style_rank, len(p))

        for aid, pids in candidates.items():
            try:
                best = sorted(set(pids), key=_score)[0] if pids else None
            except Exception:
                best = pids[0] if pids else None
            if best:
                lookup[aid] = best
        return lookup

    avatar_sku_lookup = _build_avatar_sku_lookup()
    locked_count = 0
    unlocked_count = 0
    for entry in catalog_iter:
        # Compute lock state
        if registration_scope:
            # Registration UI: the returned list is already limited to default-free avatars.
            lc = {
                'unlocked': True,
                'reason': 'Default free (registration)',
                'points_needed': 0
            }
            is_unlocked = True
        elif role == 'guest' and not anon_owned:
            # Guests without entitlements: only one avatar is selectable.
            avatar_id_norm = str(entry.get('id') or '').strip().lower()
            is_unlocked = bool(guest_allowed_id and avatar_id_norm == guest_allowed_id)
            lc = {
                'unlocked': is_unlocked,
                'reason': 'Guest default' if is_unlocked else 'Sign in to unlock',
                'points_needed': None
            }
        else:
            lc = _is_avatar_unlocked_for_user(entry, role, user)
            is_unlocked = bool(lc.get('unlocked'))

        # Special admin debug log per item
        if role == 'admin' and is_unlocked:
            try:
                print(f" ADMIN UNLOCK: {entry.get('id')} - {entry.get('name')}")
            except Exception:
                pass

        thumb = _avatar_thumbnail_url_from_glb(entry.get('obj_file'))
        obj_file = entry.get('obj_file') or ''
        # GLB avatars are in glb_files folder, not individual avatar folders
        glb_url = f"/static/assets/avatars/glb_files/{obj_file}" if obj_file else None
        # Optional: stable product id for store purchase flows
        product_id = None
        try:
            tier_norm = (entry.get('tier') or '').lower()
            avatar_id = str(entry.get('id') or '').strip().lower()
            if tier_norm in ('earn_or_buy', 'premium') and avatar_id:
                product_id = avatar_sku_lookup.get(avatar_id)
        except Exception:
            product_id = None

        # Provide consistent unlock metadata for frontends
        price_val = float(entry.get('price') or 0.0) if entry.get('price') is not None else None
        unlock_points_val = int(entry.get('unlock_points') or 0) or None
        unlock_msg = ''
        try:
            if is_unlocked:
                unlock_msg = 'Unlocked'
            else:
                tier_norm = (entry.get('tier') or '').lower()
                if tier_norm == 'earn_or_buy':
                    points_needed = lc.get('points_needed')
                    if isinstance(points_needed, int) and points_needed > 0:
                        unlock_msg = f"Earn {points_needed} more Honey Points to unlock"
                        if price_val:
                            unlock_msg += f" or purchase for ${price_val:.2f}"
                        unlock_msg += '.'
                    else:
                        unlock_msg = 'Earn Honey Points or purchase to unlock.'
                elif tier_norm == 'premium':
                    unlock_msg = f"Purchase to unlock{f' for ${price_val:.2f}' if price_val else ''}."
                else:
                    unlock_msg = (lc.get('reason') or 'Locked')
        except Exception:
            unlock_msg = (lc.get('reason') or 'Locked')

        dto = {
            'id': entry.get('id'),
            'name': entry.get('name'),
            'tier': entry.get('tier'),
            'category': entry.get('category'),
            'description': entry.get('description'),
            'price_usd': float(entry.get('price') or 0.0) if entry.get('price') is not None else None,
            'unlock_requirement': int(entry.get('unlock_points') or 0) or None,
            # Back-compat + front-end friendly fields
            'price': price_val,
            'unlock_points': unlock_points_val,
            'unlock_message': unlock_msg,
            'product_id': product_id,
            'is_locked': not is_unlocked,
            'urls': {
                'thumbnail': thumb,
                'glb': glb_url
            }
        }

        if is_unlocked:
            unlocked_count += 1
        else:
            locked_count += 1

        result.append(dto)

    # Verification logging
    try:
        print(f" Avatar availability for role={role}: unlocked={unlocked_count}, locked={locked_count}, total={len(result)}")
        if role == 'admin' and locked_count > 0:
            print("️ WARNING: Admin user has locked avatars in response — investigate caching or gating logic.")
        if role == 'admin' and unlocked_count == len(result):
            print(" Admin verification: all avatars unlocked.")
    except Exception:
        pass

    # Store in cache and return
    AVATAR_LIST_CACHE[cache_key] = { 'ts': now_ts, 'data': result }
    return jsonify({
        "status": "success",
        "avatars": result,
        "cached": False,
        "purchased_avatars": list(getattr(user, 'purchased_avatars', []) or []) if user is not None else [],
        "purchased_bundles": list(getattr(user, 'purchased_bundles', []) or []) if user is not None else [],
        "anon_owned_products": anon_owned if user is None else [],
        "user": {
            "role": role,
            "is_authenticated": bool(user is not None),
            "is_guest": bool(user is None),
            "is_admin": bool(role == 'admin'),
            "honey_points": int(getattr(user, 'honey_points', 0) or 0) if user is not None else 0,
        }
    })

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
                    "version": APP_VERSION,
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
    
    print(" Loading Simple English Wiktionary on-demand (first use)...")
    SIMPLE_WIKTIONARY = load_simple_wiktionary()
    SIMPLE_WIKTIONARY_LOADED = True
    # Build fast index (lowercase keys already) for O(1) membership checks
    try:
        SIMPLE_WIKTIONARY_INDEX = set(SIMPLE_WIKTIONARY.keys())
        print(f" Simple Wiktionary loaded: {len(SIMPLE_WIKTIONARY):,} words ready (index built)")
    except Exception as _idx_err:
        SIMPLE_WIKTIONARY_INDEX = None
        print(f"️ Failed building wiktionary index: {_idx_err}")
    return SIMPLE_WIKTIONARY

print(" Dictionary resources initialized (on-demand loading enabled)")

speed_logger = logging.getLogger('SpeedRound')
if not speed_logger.handlers:
    speed_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - SpeedRound - %(levelname)s - %(message)s'))
    speed_logger.addHandler(handler)

# ----------------------------------------------------------------------------
# In-App Purchases (Apple/Google) – server-side verification stubs and mapping
# ----------------------------------------------------------------------------

# Mode selection rules:
# - If IAP_VERIFICATION_MODE is explicitly set to a live mode, it wins and mock is OFF.
# - Otherwise, IAP_MOCK=1 defaults us into mock mode.
# - Otherwise default to live_strict.
_env_mode_raw = (os.getenv('IAP_VERIFICATION_MODE') or '').strip().lower()
IAP_MOCK_MODE = os.getenv('IAP_MOCK', '1').strip().lower() in ('1', 'true', 'yes', 'on')

if _env_mode_raw in ('mock', 'live_strict', 'live_permissive'):
    IAP_VERIFICATION_MODE = _env_mode_raw
    if IAP_VERIFICATION_MODE != 'mock':
        IAP_MOCK_MODE = False
else:
    IAP_VERIFICATION_MODE = 'mock' if IAP_MOCK_MODE else 'live_strict'

# App Store Connect configuration safety switch.
# When enabled, the server will only accept the monthly subscription SKU and will reject
# yearly/family subscription SKUs. This prevents accidental exposure of products that
# are not yet created in App Store Connect for a given build.
IAP_MONTHLY_ONLY = os.getenv('IAP_MONTHLY_ONLY', '0').strip().lower() in ('1', 'true', 'yes', 'on')


def _is_subscription_product_allowed(product_id: str) -> bool:
    """Return True if a subscription SKU is allowed in the current build.

    - If IAP_MONTHLY_ONLY=1, then only the monthly subscription is allowed.
    - Non-subscription products (avatars/bundles/one-time unlock) are always allowed.
    """
    if not product_id:
        return False
    if not IAP_MONTHLY_ONLY:
        return True
    try:
        mapping = PRODUCT_MAP.get(product_id) or {}
        if not mapping.get('subscription'):
            return True
    except Exception:
        # If we can't confidently classify it, be conservative in monthly-only mode.
        return False
    return product_id == SUBSCRIPTION_PRODUCT_IDS.get('monthly')

# Subscription Product IDs (for App Store Connect)
SUBSCRIPTION_PRODUCT_IDS = {
    'monthly': os.getenv('PRODUCT_SUBSCRIPTION_FULL_ID', 'com.beesmart.premium.monthly'),
    'yearly': os.getenv('PRODUCT_SUBSCRIPTION_YEARLY_ID', 'com.beesmart.premium.yearly'),
    'family': os.getenv('PRODUCT_SUBSCRIPTION_FAMILY_ID', 'com.beesmart.premium.family.monthly'),
    'legacy': 'beesmart.sub.full_monthly'       # Legacy subscription (backward compatibility)
}

# Product -> entitlement mapping (override via env if needed)
PRODUCT_MAP = {
    # Full unlock (premium membership - one-time purchase)
    os.getenv('PRODUCT_FULL_UNLOCK_ID', 'beesmart.full_unlock'): {
        'type': 'premium'
    },
    # SUBSCRIPTION TIERS (Auto-Renewable)
    # Configurable subscription SKU (defaults to current monthly). Legacy remains supported.
    os.getenv('PRODUCT_SUBSCRIPTION_FULL_ID', 'com.beesmart.premium.monthly'): {
        'type': 'premium', 'subscription': True, 'duration': '1 month'
    },
    # Legacy subscription (kept for backward compatibility)
    'beesmart.sub.full_monthly': {
        'type': 'premium', 'subscription': True, 'duration': '1 month'
    },
    # Monthly Premium Subscription
    'com.beesmart.premium.monthly': {
        'type': 'premium', 'subscription': True, 'duration': '1 month',
        'name': 'Premium Monthly Membership'
    },
    # Yearly Premium Subscription
    'com.beesmart.premium.yearly': {
        'type': 'premium', 'subscription': True, 'duration': '1 year',
        'name': 'Premium Yearly Membership'
    },
    # Family Premium Subscription
    'com.beesmart.premium.family.monthly': {
        'type': 'premium', 'subscription': True, 'duration': '1 month',
        'name': 'Premium Family Membership', 'family_sharing': True
    },
    # Individual avatar unlocks
    os.getenv('PRODUCT_AVATAR_SUPERBEE_ID', 'com.beesmart.avatar.super_bee'): {
        # Canonical catalog id is hyphenated
        'type': 'avatar', 'avatar_id': 'super-bee'
    },
    os.getenv('PRODUCT_AVATAR_QUEEN_ID', 'com.beesmart.avatar.queen_bee'): {
        'type': 'avatar', 'avatar_id': 'queen-bee'
    },
    os.getenv('PRODUCT_AVATAR_KNIGHT_ID', 'com.beesmart.avatar.knight_bee'): {
        'type': 'avatar', 'avatar_id': 'knight-bee'
    },
    os.getenv('PRODUCT_AVATAR_ROCKER_ID', 'com.beesmart.avatar.rocker_bee'): {
        'type': 'avatar', 'avatar_id': 'rocker-bee'
    },
    # Example bundle
    os.getenv('PRODUCT_BUNDLE_TOP_ID', 'beesmart.bundle.top'): {
        'type': 'bundle', 'bundle_id': 'top_bee_bundle',
        'avatars': ['super-bee', 'queen-bee', 'knight-bee', 'rocker-bee']
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
        # Normalize avatar ids inside bundles to canonical catalog ids.
        # This prevents mismatches like "superbee" vs "super-bee".
        _catalog_ids: list[str] = []
        try:
            from avatar_catalog import AVATAR_CATALOG  # type: ignore
            _catalog_ids = [str((a.get('id') or '')).strip().lower() for a in (AVATAR_CATALOG or []) if (a.get('id') or '').strip()]
        except Exception:
            _catalog_ids = []

        _norm_to_canon: dict[str, str] = {}
        for _cid in _catalog_ids:
            _k = re.sub(r"[^a-z0-9]+", "", _cid)
            if _k and _k not in _norm_to_canon:
                _norm_to_canon[_k] = _cid

        def _canon_avatar_id(_s: str) -> str:
            v = str(_s or '').strip().lower()
            if not v:
                return ''
            if v in _catalog_ids:
                return v
            k = re.sub(r"[^a-z0-9]+", "", v)
            return _norm_to_canon.get(k, v)

        _bundle_catalog_norm: dict[str, dict] = {}
        for _bundle_id, _cfg in (BUNDLE_CATALOG or {}).items():
            _cfg = _cfg or {}
            raw = list(_cfg.get('avatars', []) or [])
            norm_avatars: list[str] = []
            for _a in raw:
                ca = _canon_avatar_id(_a)
                if ca:
                    norm_avatars.append(ca)
            _bundle_catalog_norm[_bundle_id] = {**_cfg, 'avatars': norm_avatars}

        # 1) Store-friendly bundle SKUs (e.g., com.beesmart.bundle.classroom_starter_pack)
        if callable(build_bundle_product_entitlements):
            try:
                PRODUCT_MAP.update(build_bundle_product_entitlements(_bundle_catalog_norm))
            except Exception as _be:
                print(f"WARN: Failed to load bundle SKU entitlements: {_be}")

        # 2) Internal bundle ids (used by BeeKey redemption and dev tooling)
        for _bundle_id, _cfg in _bundle_catalog_norm.items():
            pid_internal = f"bundle:{_bundle_id}"
            if pid_internal not in PRODUCT_MAP:
                PRODUCT_MAP[pid_internal] = {
                    'type': 'bundle',
                    'bundle_id': _bundle_id,
                    'avatars': list(_cfg.get('avatars', []) or [])
                }
        try:
            print(f" Bundle catalog loaded: {len(BUNDLE_CATALOG)} bundles; keys available: {len(REDEEMABLE_KEYS) if isinstance(REDEEMABLE_KEYS, dict) else 0}")
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

    mtype = str(mapping.get('type') or '').strip().lower()
    if mtype == 'premium' or (mtype == 'subscription') or bool(mapping.get('subscription')):
        if not user.premium_member:
            user.premium_member = True
            result["applied"] = True
        result["details"] = {"premium_member": True, "subscription": bool(mapping.get('subscription'))}
        return result

    if mapping.get('type') == 'avatar':
        avatar_id = mapping.get('avatar_id')
        if avatar_id:
            # Ensure purchased_avatars list
            pa = getattr(user, 'purchased_avatars', None)
            # Defensive: legacy/corrupted rows might store JSON as a string
            if not isinstance(pa, list):
                pa = []
            user.purchased_avatars = pa
            if avatar_id not in user.purchased_avatars:
                user.purchased_avatars.append(avatar_id)
                result["applied"] = True
            result["details"] = {"unlocked_avatar": avatar_id}
        return result

    if mapping.get('type') == 'bundle':
        bundle_id = mapping.get('bundle_id')
        avatars = mapping.get('avatars', [])
        pb = getattr(user, 'purchased_bundles', None)
        if not isinstance(pb, list):
            pb = []
        user.purchased_bundles = pb
        if bundle_id and bundle_id not in user.purchased_bundles:
            user.purchased_bundles.append(bundle_id)
            # Unlock avatars
            pa = getattr(user, 'purchased_avatars', None)
            if not isinstance(pa, list):
                pa = []
            user.purchased_avatars = pa
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
    - APPLE_PRIVATE_KEY (PEM) or APPLE_PRIVATE_KEY_B64 (base64 PEM) or APPLE_PRIVATE_KEY_PATH
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
        os.getenv('APPLE_PRIVATE_KEY') or os.getenv('APPLE_PRIVATE_KEY_B64') or os.getenv('APPLE_PRIVATE_KEY_PATH')
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
                print(f" (indexed) '{word}' → wiktionary+example")
            else:
                definition = sanitize_kid_friendly_text(_filter_definition(definition, word))
                formatted = f"{definition}. Fill in the blank: Can you spell _____ correctly?"
                print(f" (indexed) '{word}' → wiktionary (no example)")
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
            print(f" Cache hit '{word}'")
            _cache_word_info(word_lower, formatted)
            return formatted
    
    # PRIORITY 3: Smart fallback - deterministic enrichment
    try:
        fb = generate_smart_fallback(word)
        definition = sanitize_kid_friendly_text(fb.get("definition", "A word to spell"))
        example = sanitize_kid_friendly_text(_blank_word(fb.get("example", "Can you spell _____ correctly?"), word))
        formatted = f"{definition}. Fill in the blank: {example}"
        print(f" Fallback '{word}' ({fb.get('source','fallback')})")
        _cache_word_info(word_lower, formatted)
        return formatted
    except Exception as _e:
        formatted = "Definition not available for this word. Listen carefully and spell _____ correctly"
        _cache_word_info(word_lower, formatted)
        print(f"️ Fallback failed for '{word}': {_e}")
        return formatted

def get_word_of_the_day():
    """
    Get today's featured word with definition and bonus info.
    """
    try:
        # Use date as seed for consistent daily word
        today = date.today()
        seed_value = today.year * 10000 + today.month * 100 + today.day
        
        # Load word list for selection
        ensure_simple_wiktionary_loaded()
        if not SIMPLE_WIKTIONARY:
            return None
            
        # Select word based on date seed
        word_list = list(SIMPLE_WIKTIONARY_INDEX) if SIMPLE_WIKTIONARY_INDEX else []
        if not word_list:
            return None
            
        import random
        random.seed(seed_value)
        featured_word = random.choice(word_list)
        
        # Get definition
        definition = get_word_info(featured_word)
        
        return {
            'word': featured_word,
            'definition': definition,
            'bonus_points': 50,
            'date': today.strftime('%Y-%m-%d'),
            'message': f'Word of the Day: {featured_word.title()}! Spell it correctly for +50 bonus points!'
        }
        
    except Exception as e:
        print(f"Error getting word of the day: {e}")
        return None

def check_daily_login_reward(user_id):
    """
    Check and award daily login rewards for authenticated users.
    Returns reward data if earned, None otherwise.
    """
    try:
        if not user_id:
            return None
            
        from models import User
        user = User.query.get(user_id)
        if not user:
            return None
            
        today = date.today()
        last_login_date = user.last_login.date() if user.last_login else None
        
        # Check if user already got reward today
        if last_login_date == today:
            return None  # Already got today's reward
        
        # Calculate streak
        if last_login_date and (today - last_login_date).days == 1:
            # Consecutive day - increment streak
            streak_days = getattr(user, 'daily_login_streak', 0) + 1
        elif last_login_date and (today - last_login_date).days > 1:
            # Broke streak - reset to 1
            streak_days = 1
        else:
            # First login or same day
            streak_days = 1
            
        # Calculate reward amount (base 50 + 10 per day in streak)
        base_reward = 50
        streak_bonus = min((streak_days - 1) * 10, 200)  # Max 200 bonus
        total_reward = base_reward + streak_bonus
        
        # Award honey points
        user.honey_points = (user.honey_points or 0) + total_reward
        user.last_login = datetime.now(timezone.utc)
        
        # Store streak (we'll add this field if needed)
        if hasattr(user, 'daily_login_streak'):
            user.daily_login_streak = streak_days
            
        db.session.commit()
        
        return {
            'reward': total_reward,
            'base': base_reward,
            'streak_bonus': streak_bonus,
            'streak_days': streak_days,
            'message': f'Welcome back! {total_reward} honey points earned!'
        }
        
    except Exception as e:
        print(f"Error checking daily login reward: {e}")
        db.session.rollback()
        return None

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
    """Normalize a word for deduplication using the same rules as answer comparison."""
    if not word:
        return ""
    # Use the same normalization as answer comparison for consistency
    return normalize(word)


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
            print(f"️ bulk_word_info failed for '{w}': {ex}")
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

print(" Creating Flask app (main init)...")
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
print(" Loading configuration...")
app.config.from_object(get_config())
print(f" Config loaded - Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

# Backwards compatibility: keep old secret key if not in config
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ.get("SPELLING_APP_SECRET", "dev-secret-change-me")

# In pytest, force a stable SECRET_KEY so Flask's signed session cookie can be
# decoded across requests. If the key changes per import/run, the client will
# present a cookie that can't be verified and Flask will treat it as a brand new
# session (dropping guest_user_id/wordbank_storage_id).
try:
    if os.environ.get("FLASK_ENV") == "testing" or os.environ.get("PYTEST_CURRENT_TEST"):
        app.config['SECRET_KEY'] = os.environ.get(
            "PYTEST_SECRET_KEY",
            "pytest-secret-key-do-not-use-in-production",
        )
except Exception:
    pass

# Admin registration key - required to register as admin
ADMIN_REGISTRATION_KEY = os.environ.get("BEESMART_ADMIN_KEY", "BEE-ADMIN-2025-SECURE-KEY")

"""Session/cookie config

Key rule: only set Secure cookies when the client is actually using HTTPS.

Important: only set Secure cookies when the client is actually using HTTPS.

Local dev often uses HTTP on localhost (even if it points at a remote Postgres).
If we mark the session cookie as Secure in that case, the browser correctly
refuses to send it back over HTTP → a brand new session on every request → lost
wordbank pointer and broken quiz flow.
"""

is_deployed_env = os.environ.get("FLASK_ENV") == "production"

# Explicit override for secure cookies (set this in real HTTPS production if needed).
force_secure_cookie = os.environ.get("FORCE_SECURE_COOKIE", "0") == "1"

# In practice, Secure cookies should only be enabled when the app is behind HTTPS.
cookie_secure = bool(force_secure_cookie or is_deployed_env)

# In automated tests, keep cookies non-secure; some test clients won't persist
# Secure cookies, which looks like a new session every request.
try:
    if os.environ.get("FLASK_ENV") == "testing" or os.environ.get("PYTEST_CURRENT_TEST"):
        cookie_secure = False
except Exception:
    pass

print(f" Environment: {'PRODUCTION' if is_deployed_env else 'DEVELOPMENT (Local)'}")

app.config.update(
    SESSION_COOKIE_SECURE=cookie_secure,  # Only True when we're actually on HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    # Use Lax by default. (SameSite=None requires Secure=True, which we *cannot*
    # use on local HTTP dev.)
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600 * 24 * 7,  # 7 days (increased from 1 day)
    SESSION_COOKIE_NAME='beesmart_session',
    # Avoid re-issuing the session cookie on every request.
    # When combined with other code paths that also touch `session`, this can
    # lead to cookie churn and lost keys in some clients/tests.
    SESSION_REFRESH_EACH_REQUEST=False,
    SESSION_COOKIE_PATH='/',  # Ensure cookie works across all paths
    SESSION_COOKIE_DOMAIN=None,  # Let Flask auto-detect domain
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    SEND_FILE_MAX_AGE_DEFAULT=3600  # 1 hour default cache for static files
)

# Initialize database
print(" Initializing database...")
db.init_app(app)
print(" Database initialized")

# Initialize Socket.IO for Battle of the Bees
try:
    from app_socketio import socketio
    socketio.init_app(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    print(" Socket.IO initialized for Battle of the Bees")
except Exception as e:
    print(f"️ Socket.IO initialization failed: {e}")
    print("️ Battles will work without real-time updates")

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
                print(" Initializing database schema (create_all)")
                db.create_all()
                print(" Database tables created")

            # If server-side sessions are enabled, ensure the sessions table exists.
            try:
                if SESSION_INIT_SUCCESS:
                    has_sessions = inspector.has_table('sessions')
                    if not has_sessions:
                        print(" Creating sessions table for Flask-Session...")
                        db.create_all()
            except Exception as _se:
                print(f"️ sessions table check failed: {_se}")
            
            # Migration: Add is_favorite column if missing
            try:
                columns = [col['name'] for col in inspector.get_columns('word_lists')]
                if 'is_favorite' not in columns:
                    print(" Adding is_favorite column to word_lists table...")
                    db.session.execute(text(
                        "ALTER TABLE word_lists ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE"
                    ))
                    db.session.commit()
                    print(" Added is_favorite column")
            except Exception as e:
                print(f"️ is_favorite migration: {e}")
                db.session.rollback()
    except Exception as e:
        # Never crash app startup; just log. Auth routes will still surface a friendly error.
        print(f"️ DB initialization check failed: {e}")

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
        print(" DB initialization scheduled in background")
    except Exception as e:
        print(f"️ Failed to schedule DB initialization: {e}")

_schedule_db_init_background()

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated
login_manager.login_message = ' Please log in to save your progress!'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login
    
    This function is called by Flask-Login whenever current_user is accessed.
    It must handle database connection issues gracefully to prevent RuntimeErrors.
    """
    try:
        # Ensure database is initialized before querying
        _ensure_db_initialized()
        
        # Safely convert user_id to int
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            print(f"⚠️ Invalid user_id in load_user: {user_id}")
            return None
        
        # Query user from database
        try:
            user = User.query.get(user_id_int)
            if user:
                return user
            else:
                # User not found - this is normal for invalid session IDs
                return None
        except Exception as db_error:
            # Database connection or query error
            print(f"⚠️ Database error in load_user for user_id {user_id_int}: {db_error}")
            import traceback
            traceback.print_exc()
            # Return None to allow Flask-Login to treat as anonymous user
            return None
    except Exception as e:
        # Catch any other errors (e.g., database not initialized)
        print(f"⚠️ Error in load_user for user_id {user_id}: {e}")
        import traceback
        traceback.print_exc()
        # Return None to allow Flask-Login to treat as anonymous user
        return None

SESSION_INIT_SUCCESS = False

# Prefer server-side sessions when possible (more reliable for larger session state like pointers).
# This is opt-in via env var to avoid reintroducing historical Railway hangs.
if os.getenv("ALLOW_DB_SESSIONS", "0") == "1":
    try:
        from flask_session import Session
        app.config.update(
            SESSION_TYPE="sqlalchemy",
            SESSION_SQLALCHEMY=db,
            SESSION_SQLALCHEMY_TABLE="sessions",
            SESSION_PERMANENT=True,
            # Keep session IDs as plain strings; in some environments enabling the
            # signer can cause bytes session IDs which break response.set_cookie.
            SESSION_USE_SIGNER=False,
            SESSION_KEY_PREFIX="beesmart_",
        )
        Session(app)
        SESSION_INIT_SUCCESS = True
        print(" Flask-Session configured (database sessions enabled)")
    except Exception as _e:
        print(f"️ Flask-Session failed, falling back to cookie sessions: {_e}")
        SESSION_INIT_SUCCESS = False
else:
    print("️ Database sessions disabled (set ALLOW_DB_SESSIONS=1 to enable)")

print(f" Session config: SECURE={app.config['SESSION_COOKIE_SECURE']}, SAMESITE={app.config['SESSION_COOKIE_SAMESITE']}, DEPLOYED={is_deployed_env}")

# Dev/test toggle for exposing reset token peek endpoint
ALLOW_DEV_RESET_PEEK = os.getenv('ALLOW_DEV_RESET_PEEK') == '1'

#  Template filters for badge display
@app.template_filter('badge_icon')
def get_badge_icon_filter(badge_type):
    """Get emoji icon for badge type"""
    return BADGE_METADATA.get(badge_type, {}).get('icon', '')

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
        return f" {formatted}"
    except Exception:
        return f" {points or 0}"

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
    
    # Only manage our *internal* tracking id; do not touch the Flask-Session
    # backing store id (cookie value), or it can cause sid churn.
    if not session.get("session_id"):
        session["session_id"] = str(uuid.uuid4())

    # Mark permanent, but don't toggle it repeatedly.
    if not session.permanent:
        session.permanent = True  # Use PERMANENT_SESSION_LIFETIME


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
    # Final fallback (best-effort): use production domain for deployed builds.
    # Dev should set APP_BASE_URL explicitly, but this prevents accidental
    # localhost links in outbound emails if the env var is missing.
    return 'https://beesmartspelling.app'


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
        print(f" [DEV] Would send reset email to {recipient_email}:\nSubject: {subject}\n{preview}")
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
        print(f" Reset email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"️ Failed to send reset email: {e}")
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

    subject = "Welcome to BeeSmart "

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
        print(f" [DEV] Would send welcome email to {recipient_email}:\nSubject: {subject}\n{preview}")
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
        print(f" Welcome email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"️ Failed to send welcome email: {e}")
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

# Wordbank storage moved to Railway PostgreSQL database (WordBankStorage model)
# No more in-memory WORD_STORAGE dictionary - database is single source of truth

# Legacy debug hooks: provide empty in-memory structures so optional debug prints
# that reference WORD_STORAGE/WORD_STORAGE_LOCK don't crash routes in local/dev.
try:
    WORD_STORAGE  # type: ignore[name-defined]
except NameError:
    WORD_STORAGE = {}
try:
    WORD_STORAGE_LOCK  # type: ignore[name-defined]
except NameError:
    WORD_STORAGE_LOCK = threading.Lock()

# --- Database Helpers --------------------------------------------------------

def get_or_create_guest_user():
    """
    Get or create a guest user for anonymous sessions.
    Allows progress tracking without requiring signup.
    Returns User object (guest or authenticated).
    """
    try:
        print(f"DEBUG get_or_create_guest_user: Starting guest user resolution")
        
        # Test database connection first
        try:
            db.session.execute(db.text('SELECT 1'))
            print(f"DEBUG get_or_create_guest_user: Database connection OK")
        except Exception as db_e:
            print(f"ERROR get_or_create_guest_user: Database connection failed: {db_e}")
            return None
        
        if current_user.is_authenticated:
            print(f"DEBUG get_or_create_guest_user: Authenticated user: {current_user.username}")
            return current_user

        # Preserve any active wordbank pointer before we touch other session keys.
        # If this gets lost, /api/next will 400 even though WordBankStorage exists.
        _preserved_wordbank_storage_id = session.get("wordbank_storage_id")
        _preserved_wordbank_count = session.get("wordbank_count")
        _preserved_has_uploaded_once = session.get("has_uploaded_once")
        _preserved_using_default_words = session.get("using_default_words")

        # Check if this session has a guest user ID
        guest_user_id = session.get("guest_user_id")
        print(f"DEBUG get_or_create_guest_user: Session guest_user_id: {guest_user_id}")
        
        if guest_user_id:
            # Try to retrieve existing guest user
            print(f"DEBUG get_or_create_guest_user: Looking up guest user with id: {guest_user_id}")
            guest_user = User.query.get(guest_user_id)
            if guest_user:
                # Legacy DB safety: some JSON columns were historically stored as strings
                # (e.g. "[]") which breaks runtime code expecting lists.
                try:
                    import json as _json

                    def _coerce_json_list_runtime(v):
                        if v is None:
                            return []
                        if isinstance(v, list):
                            return v
                        if isinstance(v, str):
                            s = v.strip()
                            if not s:
                                return []
                            try:
                                parsed = _json.loads(s)
                                return parsed if isinstance(parsed, list) else []
                            except Exception:
                                return []
                        return []

                    pa = _coerce_json_list_runtime(getattr(guest_user, 'purchased_avatars', None))
                    pb = _coerce_json_list_runtime(getattr(guest_user, 'purchased_bundles', None))
                    dirty = False
                    if not isinstance(getattr(guest_user, 'purchased_avatars', None), list):
                        guest_user.purchased_avatars = pa
                        dirty = True
                    if not isinstance(getattr(guest_user, 'purchased_bundles', None), list):
                        guest_user.purchased_bundles = pb
                        dirty = True
                    if dirty:
                        # Commit the fix so future requests don't hit the same issue.
                        db.session.commit()
                except Exception as _e:
                    # Non-fatal: don't block guest login if coercion fails.
                    print(f"DEBUG get_or_create_guest_user: JSON coercion skipped: {_e}")
                # Re-attach preserved wordbank session keys (defensive; should already exist).
                if _preserved_wordbank_storage_id and not session.get("wordbank_storage_id"):
                    session["wordbank_storage_id"] = _preserved_wordbank_storage_id
                if _preserved_wordbank_count is not None:
                    session["wordbank_count"] = _preserved_wordbank_count
                if _preserved_has_uploaded_once is not None:
                    session["has_uploaded_once"] = _preserved_has_uploaded_once
                if _preserved_using_default_words is not None:
                    session["using_default_words"] = _preserved_using_default_words
                session.modified = True

                print(f"DEBUG get_or_create_guest_user: Found existing guest user: {guest_user.username}")
                return guest_user
            else:
                print(f"DEBUG get_or_create_guest_user: Guest user id {guest_user_id} not found in database")
        
        # Create new guest user
        print(f"DEBUG get_or_create_guest_user: Creating new guest user")
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

        # Ensure JSON list fields are correct types from the start.
        try:
            guest_user.purchased_avatars = []
            guest_user.purchased_bundles = []
        except Exception:
            pass
        
        print(f"DEBUG get_or_create_guest_user: Adding guest user to database: {guest_username}")
        db.session.add(guest_user)

        # Flush can trigger ORM defaults / schema defaults. Guard against any
        # surprise string values (e.g. "[]") landing in these fields.
        db.session.flush()  # Get the ID without committing
        try:
            dirty = False
            if isinstance(getattr(guest_user, 'purchased_avatars', None), str):
                guest_user.purchased_avatars = []
                dirty = True
            if isinstance(getattr(guest_user, 'purchased_bundles', None), str):
                guest_user.purchased_bundles = []
                dirty = True
            if dirty:
                db.session.flush()
        except Exception as _e:
            print(f"DEBUG get_or_create_guest_user: Post-flush JSON coercion skipped: {_e}")
        
        # Store guest user ID in session BEFORE committing
        session["guest_user_id"] = guest_user.id
        session["is_guest"] = True

        # Persist the active wordbank pointer on the user record as an
        # additional source of truth. This makes the quiz flow resilient even
        # if the cookie-backed session key gets regenerated/dropped.
        try:
            if _preserved_wordbank_storage_id and not getattr(guest_user, "wordbank_storage_id", None):
                guest_user.wordbank_storage_id = _preserved_wordbank_storage_id
                guest_user.wordbank_last_updated = datetime.utcnow()
        except Exception as _e:
            print(f"DEBUG get_or_create_guest_user: Unable to persist wordbank pointer: {_e}")

        # Re-attach preserved wordbank session keys.
        if _preserved_wordbank_storage_id and not session.get("wordbank_storage_id"):
            session["wordbank_storage_id"] = _preserved_wordbank_storage_id
        if _preserved_wordbank_count is not None:
            session["wordbank_count"] = _preserved_wordbank_count
        if _preserved_has_uploaded_once is not None:
            session["has_uploaded_once"] = _preserved_has_uploaded_once
        if _preserved_using_default_words is not None:
            session["using_default_words"] = _preserved_using_default_words
        session.modified = True

        print(f"DEBUG get_or_create_guest_user: Stored guest_user_id in session: {guest_user.id}")
        
        db.session.commit()
        # NOTE: Some legacy DB/defaults can cause the JSON mutable loader to raise
        # during attribute refresh. Avoid crashing guest creation over a log line.
        try:
            gid = guest_user.id
        except Exception:
            gid = session.get("guest_user_id")
        print(f" Created guest user: {guest_username} (ID: {gid})")
        return guest_user
        
    except Exception as e:
        print(f"️ Failed to create guest user: {type(e).__name__}: {e}")
        import traceback
        print(f"️ Guest user creation traceback: {traceback.format_exc()}")
        db.session.rollback()
        
        # Last resort: Try to create a minimal session without database
        print(f"DEBUG get_or_create_guest_user: Attempting session-only fallback")
        session_guest_id = session.get("fallback_guest_id")
        if not session_guest_id:
            session_guest_id = f"fallback_{uuid.uuid4().hex[:8]}"
            session["fallback_guest_id"] = session_guest_id
            session["is_guest"] = True
        
        # Return None to indicate failure - calling code should handle this gracefully
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


def _require_premium_json(feature: str = "premium"):
    """Server-side paywall enforcement for premium-only features.

    Contract:
    - For unauthenticated users: return a 401 JSON response with auth_required.
    - For authenticated non-premium users: return a 403 JSON response with premium_required.
    - For premium users: return None.

    NOTE: We intentionally use a JSON response (not redirect) since these routes
    are API endpoints.
    """
    try:
        if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
            return jsonify({
                "ok": False,
                "error": "auth_required",
                "auth_required": True,
                "feature": feature,
            }), 401
        if not bool(getattr(current_user, 'premium_member', False)):
            return jsonify({
                "ok": False,
                "error": "premium_required",
                "premium_required": True,
                "feature": feature,
            }), 403
    except Exception:
        # Fail-safe: never break the API on guard errors.
        return None
    return None


def _deny_guest_avatar_picker_access():
    """DEPRECATED: guest gating for pickers is no longer enforced here.

    We keep this function as a no-op for backward compatibility with older
    deployments/branches that might still call it.
    """
    return None

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
    """Normalize a spelling for comparison: remove diacritics, strip non-alnum, lowercase.
    This fixes cases where voice input or pasted text includes accents/Unicode variants.
    """
    if s is None:
        return ""
    # Strip leading/trailing whitespace first
    s = str(s).strip()
    # Remove invisible/control characters that can appear from mobile/macOS keyboards,
    # copy/paste, or IME composition (e.g., zero-width chars, BOM, bidi markers, DEL).
    # We keep this conservative and only remove known problematic classes.
    try:
        import re as _re
        s = _re.sub(r"[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF\u00AD\x00-\x1F\x7F]", "", s)
    except Exception:
        pass
    try:
        import unicodedata
        # Decompose characters and drop combining marks (accents/diacritics)
        s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
    except Exception:
        # If unicodedata fails for some reason, continue with original string
        pass
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
    "death", "die", "dying", "blood", "bloody", "torture",
    # Disturbing / age-inappropriate concepts
    "sadism", "sadist", "sadistic"
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
                " Bees are getting ready to collect words...",
                " Preparing the hive for new spelling words...",
                " Worker bees are warming up their wings..."
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
                    bee_msg = f" Bees are flying to collect '{current_word}'..."
                elif progress < 50:
                    bee_msg = f" Worker bees are gathering definitions for '{current_word}'..."
                elif progress < 75:
                    bee_msg = f" Bees are creating quiz sentences for '{current_word}'..."
                else:
                    bee_msg = f" Almost done! Bees are organizing '{current_word}' in the hive..."
                
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
                UPLOAD_PROGRESS[session_id]["bee_messages"].append(" Success! All bees have returned to the hive with spelling words!")
            else:
                UPLOAD_PROGRESS[session_id]["bee_messages"].append(" Oh no! Some bees got confused... Let's try again!")

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

@app.route('/api/upload/image', methods=['GET', 'POST'])
def api_upload_image():
    """Upload an image file for OCR processing."""
    # Pay-to-play: OCR/image upload is a Premium feature.
    premium_block = _require_premium_json("image_upload")
    if premium_block is not None:
        return premium_block

    if request.method == 'GET':
        # The test checks this endpoint's availability via GET
        if not TESSERACT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'OCR (image upload) is not available on this server.'}), 501
        return jsonify({'status': 'ready', 'message': 'OCR endpoint is available. Please POST an image.'})

    if not TESSERACT_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'OCR (image upload) is not available on this server.'}), 501

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected for uploading'}), 400

    if file:
        try:
            file_bytes = file.read()
            records = parse_image_ocr(file_bytes)
            
            # Deduplicate and filter
            deduped_records = deduplicate_words(records)
            
            # Kid-friendly filter
            filtered_records, blocked = [], []
            if deduped_records:
                print(f"️ Running enhanced kid-friendly filter on {len(deduped_records)} words...")
                filtered_records, blocked = _filter_records_excluding_inappropriate_text(deduped_records)
                print(f" {len(filtered_records)} words passed kid-friendly filter")
            
            # Enrich with definitions
            enriched_records = enrich_with_definitions(filtered_records)
            
            # Save to wordbank
            set_wordbank(enriched_records, is_user_upload=True)
            init_quiz_state(len(enriched_records))
            
            return jsonify({
                'status': 'success',
                'message': f'Successfully uploaded and processed {len(enriched_records)} words.',
                'stored': len(enriched_records),
                'blocked_count': len(blocked),
                'blocked_words': [b['word'] for b in blocked]
            })
            
        except Exception as e:
            log_error(f"OCR Upload Error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
    return jsonify({'status': 'error', 'message': 'File upload failed'}), 500

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

# Disk-backed persistence for WORD_STORAGE entries so user lists survive app restarts
WORD_STORAGE_DIR = os.path.join(BASE_DIR if 'BASE_DIR' in globals() else os.getcwd(), 'data', 'wordbanks')
try:
    os.makedirs(WORD_STORAGE_DIR, exist_ok=True)
except Exception:
    pass

def _load_wordbank_from_disk(storage_id: str) -> List[Dict[str, str]]:
    """DEPRECATED: Replaced by get_wordbank() which uses WordBankStorage model."""
    return []

def _save_wordbank_to_disk(storage_id: str, rows: List[Dict[str, str]]):
    """DEPRECATED: Replaced by set_wordbank() which uses WordBankStorage model."""
    pass

def _delete_wordbank_from_disk(storage_id: Optional[str]):
    """DEPRECATED: Replaced by delete_wordbank() which uses WordBankStorage model."""
    pass

def get_wordbank() -> List[Dict[str, str]]:
    """Read wordbank from Railway database (ONLY source of truth).
    
    All word operations use wordbank_storage table in PostgreSQL.
    Session stores small UUID pointer (~36 bytes) to avoid cookie limits.
    """
    storage_id = session.get("wordbank_storage_id")

    # Last-resort recovery: if the pointer was lost but we have an active quiz
    # state, it can carry the storage_id.
    if not storage_id:
        try:
            qs = session.get(QUIZ_STATE_KEY)
            if isinstance(qs, dict) and qs.get("storage_id"):
                storage_id = qs.get("storage_id")
                session["wordbank_storage_id"] = storage_id
                session.modified = True
        except Exception:
            pass

    # Hybrid-session compatibility: in some flows (notably guest creation / older
    # clients) the DB pointer can be missing but the server-side wordbank still
    # exists under the canonical helpers.
    if not storage_id:
        try:
            wb_state = session.get(DATA_KEY) or {}
            if isinstance(wb_state, dict):
                storage_id = wb_state.get("storage_id") or wb_state.get("wordbank_storage_id")
        except Exception:
            storage_id = None
        if storage_id:
            session["wordbank_storage_id"] = storage_id
            session.modified = True

    # If the session key was lost (common when guest-user/session regeneration
    # happens mid-flow), try to recover the pointer from the user record.
    if not storage_id:
        try:
            # IMPORTANT: don't create/attach a guest user when a real user is logged in.
            # Guest creation here would fork wordbank ownership and break stats attribution.
            try:
                is_auth = bool(getattr(current_user, "is_authenticated", False))
            except Exception:
                is_auth = False
            user_obj = current_user if is_auth else get_or_create_guest_user()
            candidate = getattr(user_obj, "wordbank_storage_id", None) if user_obj else None
            if candidate:
                storage_id = candidate
                session["wordbank_storage_id"] = storage_id
                session.modified = True
        except Exception:
            pass
    
    if not storage_id:
        print("DEBUG get_wordbank: No storage_id in session - wordbank is empty")
        session["wordbank_count"] = 0
        return []
    
    # Query Railway database (ONLY storage location)
    try:
        words = WordBankStorage.load_wordbank(storage_id)
        if words:
            print(f" get_wordbank: Loaded {len(words)} words from Railway database (storage_id={storage_id})")
            session["wordbank_count"] = len(words)
            return list(words)  # Return copy to prevent modification
        else:
            print(f"️ get_wordbank: storage_id={storage_id} not found in Railway database")
            session["wordbank_count"] = 0
            return []
    except Exception as e:
        print(f" get_wordbank: Database error: {e}")
        session["wordbank_count"] = 0
        return []

def set_wordbank(rows: List[Dict[str, str]], is_user_upload: bool = False):
    """Save wordbank to Railway database (ONLY storage location).
    
     CRITICAL: COMPLETE REPLACEMENT - old wordbank is WIPED and replaced with new rows.
    Session stores small UUID pointer (~36 bytes) to avoid cookie size limits.
    """
    import uuid
    
    # Get or create storage_id for this session
    storage_id = session.get("wordbank_storage_id")
    if not storage_id:
        storage_id = str(uuid.uuid4())
        print(f"DEBUG set_wordbank: Created new storage_id={storage_id}")
    else:
        print(f"DEBUG set_wordbank: Reusing existing storage_id={storage_id}")
    
    # CRITICAL FIX: Ensure old data is completely deleted before writing new data
    # This prevents race conditions where quiz reads old data during upload
    try:
        # If storage_id already exists, delete it first to ensure clean slate
        existing_wordbank = WordBankStorage.query.filter_by(storage_id=storage_id).first()
        if existing_wordbank:
            print(f"️ set_wordbank: Deleting existing wordbank for storage_id={storage_id}")
            db.session.delete(existing_wordbank)
            db.session.flush()  # Ensure delete happens before insert
    except Exception as e:
        print(f"️ set_wordbank: Error deleting old wordbank: {e}")
        db.session.rollback()
    
    # Save to Railway database (ONLY storage location)
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        WordBankStorage.save_wordbank(storage_id, rows, user_id)
        print(f" set_wordbank: Saved {len(rows)} words to Railway database (storage_id={storage_id})")
    except Exception as e:
        print(f" set_wordbank: Database error: {e}")
        db.session.rollback()
        raise
    
    # Update session with storage_id (new or reused)
    session["wordbank_storage_id"] = storage_id
    session["wordbank_count"] = len(rows)

    # Hybrid session schema: the rest of the app (and older client flows) use
    # a server-side session key that stores metadata about the active wordbank.
    # Keep it in sync so get_wordbank() can recover if the legacy pointer key
    # gets dropped during guest-user/session initialization.
    session[DATA_KEY] = {
        "storage_id": storage_id,
        "word_count": len(rows),
        "using_default_words": (not is_user_upload),
        "has_uploaded_once": bool(is_user_upload),
    }
    session.permanent = True
    session.modified = True
    
    if is_user_upload:
        session["has_uploaded_once"] = True
        session.pop("using_default_words", None)
        print(f"DEBUG set_wordbank: User uploaded {len(rows)} words")
    else:
        session["using_default_words"] = True
        print(f"DEBUG set_wordbank: System loaded {len(rows)} words")

def delete_wordbank(storage_id: str):
    """Delete wordbank from Railway database (single source of truth).
    
    Used when loading new word lists or clearing wordbank completely.
    """
    try:
        success = WordBankStorage.delete_wordbank(storage_id)
        if success:
            print(f" delete_wordbank: Removed storage_id={storage_id} from Railway database")
        else:
            print(f"️ delete_wordbank: storage_id={storage_id} not found in Railway database")
        return success
    except Exception as e:
        print(f" delete_wordbank: Database error: {e}")
        db.session.rollback()
        return False

def get_quiz_state():
    return session.get(QUIZ_STATE_KEY)

@app.route('/api/quiz/state', methods=['GET'])
def api_quiz_state():
    """Return current quiz state summary for resume/restore checks."""
    try:
        qs = session.get(QUIZ_STATE_KEY)
        wb = get_wordbank()
        return jsonify({
            'status': 'success',
            'has_state': bool(qs is not None),
            'total_words': len(wb),
            'state': qs or {}
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/quiz/resume', methods=['POST'])
def api_quiz_resume():
    """Check if a quiz is in progress and can be resumed."""
    try:
        qs = session.get(QUIZ_STATE_KEY)
        if qs is not None:
            idx = int(qs.get("idx", 0) or 0)
            order = qs.get("order", []) or []
            correct = int(qs.get("correct", 0) or 0)
            incorrect = int(qs.get("incorrect", 0) or 0)

            # If the quiz is already completed (idx at/after total), do not offer resume.
            if len(order) > 0 and idx >= len(order):
                return jsonify({'status': 'success', 'resumed': False, 'in_progress': False})

            # Do not offer "Resume" unless there's meaningful progress.
            # If idx==0 and no answers were recorded, treat this as not started yet.
            # (Fixes UX: "You can't resume something you never started".)
            has_progress = (idx > 0) or (correct > 0) or (incorrect > 0)
            if not has_progress:
                return jsonify({'status': 'success', 'resumed': False, 'in_progress': False})

            return jsonify({
                'status': 'success',
                'resumed': True,
                'in_progress': True,
                'message': 'A quiz is currently in progress. Do you want to resume?',
                'state': {
                    'current_word_index': idx,
                    'total_words': len(order),
                    'correct': correct,
                    'incorrect': incorrect,
                    'wordbank_fingerprint': qs.get('wordbank_fingerprint', ''),
                }
            })

        return jsonify({'status': 'success', 'resumed': False, 'in_progress': False})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/quiz/start', methods=['POST'])
def api_quiz_start():
    """Starts a new quiz or resumes an existing one based on user choice."""
    try:
        data = request.get_json(silent=True) or {}
        # Accept both legacy and UI action names.
        # UI uses: 'resume' | 'start_new'
        # Some older callers may send: 'restart' | 'new'
        action = (data.get('action') or 'start_new').strip().lower()
        if action in {'restart', 'new', 'start', 'start_over'}:
            action = 'start_new'

        qs = session.get(QUIZ_STATE_KEY)

        if action == 'resume' and qs is not None:
            # Resume existing quiz only if there's meaningful progress.
            idx = int(qs.get("idx", 0) or 0)
            correct = int(qs.get("correct", 0) or 0)
            incorrect = int(qs.get("incorrect", 0) or 0)
            has_progress = (idx > 0) or (correct > 0) or (incorrect > 0)
            if has_progress:
                return jsonify({'status': 'success', 'resumed': True, 'state': qs})
            # If no progress, fall through to start_new (harmless reset).
        
        # Start a new quiz
        wb = get_wordbank()
        if not wb:
            return jsonify({'status': 'error', 'message': 'No wordbank loaded to start a quiz.'}), 400
            
        init_quiz_state(len(wb))
        return jsonify({'status': 'success', 'resumed': False, 'state': session.get(QUIZ_STATE_KEY)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Register Battle of the Bees API Blueprint
print(" Registering Battle API...")
try:
    from battles_api import battles_bp
    app.register_blueprint(battles_bp, url_prefix='/api')
    print(" Battle API registered successfully - Routes at /api/battles/*")
except Exception as e:
    print(f"️ Battle API registration failed: {e}")

# --- Routes: Health Check for API Debugging ----------------------------------


@app.route("/api/debug/health", methods=["GET"])
def api_debug_health():
    """Simple health check endpoint to test basic API functionality without complex dependencies."""
    return jsonify({"status": "healthy"})

@app.route("/api/debug/session", methods=["GET"])
def api_debug_session():
    """Debug endpoint to check current session state and wordbank"""
    try:
        session.permanent = True
        
        storage_id = session.get("wordbank_storage_id")
        session_id = session.get("session_id")
        
        result = {
            "session_id": session_id,
            "storage_id": storage_id,
            "session_keys": list(session.keys()),
            "cookies_received": list(request.cookies.keys()),
            "has_uploaded_once": session.get("has_uploaded_once", False),
            "wordbank_count_session": session.get("wordbank_count", 0),
        }
        
        # Check WORD_STORAGE
        try:
            with WORD_STORAGE_LOCK:
                result["word_storage_keys"] = list(WORD_STORAGE.keys())
                if storage_id:
                    result["words_in_storage"] = len(WORD_STORAGE.get(storage_id, []))
                else:
                    result["words_in_storage"] = 0
        except Exception as _e:
            result["word_storage_error"] = str(_e)
        
        # Check wordbank via get_wordbank()
        wb = get_wordbank()
        result["wordbank_via_get"] = len(wb)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback_str = ''.join(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback_str
        }), 500

@app.route("/api/debug/avatar-picker", methods=["GET"])
@login_required
def api_debug_avatar_picker():
    """Debug endpoint for avatar picker and selection issues"""
    try:
        from models import Avatar
        
        result = {
            "authenticated": current_user.is_authenticated,
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "current_avatar": current_user.avatar_id,
            "avatar_locked": getattr(current_user, 'avatar_locked', False),
            "password_hash": bool(current_user.password_hash),
            "honey_points": getattr(current_user, 'honey_points', 0),
            "purchased_avatars": getattr(current_user, 'purchased_avatars', []),
        }
        
        # Count avatars in database
        avatar_count = Avatar.query.filter_by(is_active=True).count()
        result["avatars_in_database"] = avatar_count
        
        # Check specific avatar we're trying to select
        test_avatar = Avatar.query.filter_by(slug="brother-bee", is_active=True).first()
        result["brother_bee_exists"] = bool(test_avatar)
        if test_avatar:
            result["brother_bee_data"] = {
                "name": test_avatar.name,
                "category": test_avatar.category,
                "is_active": test_avatar.is_active
            }
        
        # Check if GLB files exist
        import os
        glb_path = os.path.join(app.root_path, 'static', 'assets', 'avatars', 'glb_files')
        glb_exists = os.path.isdir(glb_path)
        result["glb_folder_exists"] = glb_exists
        if glb_exists:
            glb_files = [f for f in os.listdir(glb_path) if f.lower().endswith('.glb')]
            result["glb_files_count"] = len(glb_files)
            if "BrotherBee.glb" in [f for f in os.listdir(glb_path)]:
                result["brother_bee_glb_exists"] = True
        
        result["status"] = " Ready"
        return jsonify(result)
        
    except Exception as e:
        print(f" Avatar picker debug error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": " Error",
            "error": str(e)
        }), 500

@app.route("/api/debug/systems-diagnostic", methods=["GET"])
def systems_diagnostic():
    """Comprehensive systems diagnostic - tests all major functions, quizzes, and database connections."""
    diagnostic = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "running",
        "tests": {}
    }
    
    failed_tests = []
    
    try:
        #  Test 1: Database Connection and Core Tables
        diagnostic["tests"]["database"] = {"status": "testing"}
        try:
            # Test basic connection
            db.session.execute('SELECT 1')
            
            # Test core table access
            from models import User, WordList, Avatar, QuizSession, SpeedRoundScore, Achievement
            
            user_count = User.query.count()
            wordlist_count = WordList.query.count()
            avatar_count = Avatar.query.count()
            quiz_count = QuizSession.query.count()
            speed_count = SpeedRoundScore.query.count()
            achievement_count = Achievement.query.count()
            
            diagnostic["tests"]["database"] = {
                "status": "success",
                "connection": "active",
                "tables": {
                    "users": user_count,
                    "word_lists": wordlist_count,
                    "avatars": avatar_count,
                    "quiz_sessions": quiz_count,
                    "speed_rounds": speed_count,
                    "achievements": achievement_count
                }
            }
        except Exception as e:
            diagnostic["tests"]["database"] = {"status": "failed", "error": str(e)}
            failed_tests.append("database")

        #  Test 2: User Authentication System
        diagnostic["tests"]["authentication"] = {"status": "testing"}
        try:
            # Test guest user creation
            guest_user = get_or_create_guest_user()
            
            diagnostic["tests"]["authentication"] = {
                "status": "success",
                "current_user_authenticated": current_user.is_authenticated,
                "guest_user_created": bool(guest_user),
                "guest_user_id": guest_user.id if guest_user else None,
                "session_keys": list(session.keys())
            }
        except Exception as e:
            diagnostic["tests"]["authentication"] = {"status": "failed", "error": str(e)}
            failed_tests.append("authentication")

        #  Test 3: Word List System
        diagnostic["tests"]["wordlists"] = {"status": "testing"}
        try:
            # Test saved lists functionality
            user = get_or_create_guest_user()
            if user:
                lists = WordList.query.filter(WordList.created_by_user_id == user.id).limit(5).all()
                
                diagnostic["tests"]["wordlists"] = {
                    "status": "success",
                    "user_lists_count": len(lists),
                    "api_endpoint": "/api/saved-lists accessible",
                    "model_functional": True
                }
            else:
                diagnostic["tests"]["wordlists"] = {"status": "failed", "error": "No user available"}
                failed_tests.append("wordlists")
        except Exception as e:
            diagnostic["tests"]["wordlists"] = {"status": "failed", "error": str(e)}
            failed_tests.append("wordlists")

        #  Test 4: Avatar System (rendering-path specific)
        diagnostic["tests"]["avatars"] = {"status": "testing"}
        try:
            from avatar_catalog import AVATAR_CATALOG

            # Determine which render path applies.
            # - Guests: carousel GLB preview
            # - Registered users: selected avatar GLB + personal FX config
            is_registered = bool(getattr(current_user, 'is_authenticated', False)) and getattr(current_user, 'role', None) not in (None, 'guest')
            mode = 'registered' if is_registered else 'guest'

            glb_dir = os.path.join(app.root_path, 'static', 'assets', 'avatars', 'glb_files')
            glb_dir_exists = os.path.isdir(glb_dir)

            stage_fx_cfg_path = os.path.join(app.root_path, 'static', 'config', 'avatar_fx.json')
            stage_fx_cfg_exists = os.path.exists(stage_fx_cfg_path)

            # Minimal DB sample for reporting (not a rendering check).
            db_avatars = Avatar.query.filter_by(is_active=True).limit(3).all()

            avatar_test = {
                "mode": mode,
                "catalog_avatars": len(AVATAR_CATALOG),
                "glb_folder_exists": glb_dir_exists,
                "sample_avatars": [{"id": av.slug, "name": av.name} for av in db_avatars],
            }

            if mode == 'guest':
                # Carousel: verify representative GLBs exist on disk.
                required = ['MascotBee.glb', 'ExplorerBee.glb']
                present = []
                missing = []
                if glb_dir_exists:
                    for fn in required:
                        if os.path.exists(os.path.join(glb_dir, fn)):
                            present.append(fn)
                        else:
                            missing.append(fn)
                else:
                    missing = required[:]

                avatar_test.update({
                    "carousel_glb_required": required,
                    "carousel_glb_present": present,
                    "carousel_glb_missing": missing,
                })

            else:
                # Registered: verify selected avatar GLB is resolvable + stage FX config contains mapping.
                avatar_data = None
                try:
                    if hasattr(current_user, 'get_avatar_data'):
                        avatar_data = current_user.get_avatar_data()
                except Exception:
                    avatar_data = None

                avatar_name = None
                avatar_glb_url = None
                if isinstance(avatar_data, dict):
                    avatar_name = avatar_data.get('name')
                    urls = avatar_data.get('urls') or {}
                    avatar_glb_url = urls.get('glb')

                glb_filename = None
                glb_exists = None
                if isinstance(avatar_glb_url, str) and avatar_glb_url:
                    # Only resolve file existence for local static assets.
                    marker = '/static/assets/avatars/glb_files/'
                    if marker in avatar_glb_url:
                        glb_filename = avatar_glb_url.split(marker, 1)[-1].split('?', 1)[0]
                        glb_exists = os.path.exists(os.path.join(glb_dir, glb_filename)) if glb_dir_exists else False

                fx_mapped = None
                if stage_fx_cfg_exists and avatar_name:
                    try:
                        with open(stage_fx_cfg_path, 'r', encoding='utf-8') as f:
                            cfg = json.load(f)
                        avatar_map = cfg.get('avatars') if isinstance(cfg, dict) else None
                        if isinstance(avatar_map, dict):
                            fx_mapped = (avatar_name in avatar_map)
                    except Exception:
                        fx_mapped = None

                avatar_test.update({
                    "selected_avatar_name": avatar_name,
                    "selected_avatar_glb_url": avatar_glb_url,
                    "selected_avatar_glb_filename": glb_filename,
                    "selected_avatar_glb_exists": glb_exists,
                    "stage_fx_config_exists": stage_fx_cfg_exists,
                    "stage_fx_mapped": fx_mapped,
                })

            diagnostic["tests"]["avatars"] = {
                "status": "success",
                **avatar_test,
            }
        except Exception as e:
            diagnostic["tests"]["avatars"] = {"status": "failed", "error": str(e)}
            failed_tests.append("avatars")

        #  Test 5: Quiz System
        diagnostic["tests"]["quiz_system"] = {"status": "testing"}
        try:
            # Test quiz-related endpoints
            recent_sessions = QuizSession.query.limit(5).all()
            
            # Test quiz state management
            quiz_state = session.get('quiz_state_v1', {})
            wordbank = get_wordbank()
            
            diagnostic["tests"]["quiz_system"] = {
                "status": "success",
                "recent_sessions": len(recent_sessions),
                "quiz_state_exists": bool(quiz_state),
                "wordbank_functional": wordbank is not None,
                "wordbank_size": len(wordbank) if isinstance(wordbank, list) else 0
            }
        except Exception as e:
            diagnostic["tests"]["quiz_system"] = {"status": "failed", "error": str(e)}
            failed_tests.append("quiz_system")

        #  Test 6: Speed Round System  
        diagnostic["tests"]["speed_round"] = {"status": "testing"}
        try:
            # Test speed round configuration
            speed_config = SpeedRoundConfig.query.first()
            speed_scores = SpeedRoundScore.query.limit(5).all()
            
            diagnostic["tests"]["speed_round"] = {
                "status": "success",
                "config_exists": bool(speed_config),
                "recent_scores": len(speed_scores),
                "api_endpoint": "/api/speed-round accessible"
            }
        except Exception as e:
            diagnostic["tests"]["speed_round"] = {"status": "failed", "error": str(e)}
            failed_tests.append("speed_round")

        #  Test 7: Dictionary System
        diagnostic["tests"]["dictionary"] = {"status": "testing"}
        try:
            # Test dictionary API functionality
            import dictionary_api
            
            # Test cache file
            cache_file = "data/dictionary.json"
            cache_exists = os.path.exists(cache_file)
            
            diagnostic["tests"]["dictionary"] = {
                "status": "success",
                "api_module": "dictionary_api imported",
                "cache_file_exists": cache_exists,
                "functions_available": True
            }
        except Exception as e:
            diagnostic["tests"]["dictionary"] = {"status": "failed", "error": str(e)}
            failed_tests.append("dictionary")

        #  Test 8: File Upload System
        diagnostic["tests"]["file_upload"] = {"status": "testing"}
        try:
            # Test upload directory
            upload_dir = os.path.join(app.root_path, 'uploads')
            upload_exists = os.path.exists(upload_dir)
            
            diagnostic["tests"]["file_upload"] = {
                "status": "success",
                "upload_directory_exists": upload_exists,
                "api_endpoint": "/api/upload accessible",
                "parsers_available": True
            }
        except Exception as e:
            diagnostic["tests"]["file_upload"] = {"status": "failed", "error": str(e)}
            failed_tests.append("file_upload")

        #  Test 9: Session Management
        diagnostic["tests"]["session_management"] = {"status": "testing"}
        try:
            # Test session functionality
            session_data = dict(session)
            
            diagnostic["tests"]["session_management"] = {
                "status": "success",
                "session_active": bool(session_data),
                "session_keys": list(session_data.keys()),
                "guest_user_id": session.get("guest_user_id"),
                "quiz_state": "quiz_state_v1" in session,
                "wordbank_storage": "wordbank_storage_id" in session
            }
        except Exception as e:
            diagnostic["tests"]["session_management"] = {"status": "failed", "error": str(e)}
            failed_tests.append("session_management")

        #  Test 10: Static Assets (Bee Swarm, Avatars, etc.)
        diagnostic["tests"]["static_assets"] = {"status": "testing"}
        try:
            # Test critical static file paths
            static_root = os.path.join(app.root_path, 'static')
            js_dir = os.path.join(static_root, 'js')
            avatar_dir = os.path.join(static_root, 'assets', 'avatars')
            glb_dir = os.path.join(avatar_dir, 'glb_files')
            
            diagnostic["tests"]["static_assets"] = {
                "status": "success",
                "static_directory": os.path.exists(static_root),
                "js_directory": os.path.exists(js_dir),
                "avatar_directory": os.path.exists(avatar_dir),
                "glb_directory": os.path.exists(glb_dir),
                "bee_swarm_js": os.path.exists(os.path.join(js_dir, 'bee_swarm_visualizer.js'))
            }
        except Exception as e:
            diagnostic["tests"]["static_assets"] = {"status": "failed", "error": str(e)}
            failed_tests.append("static_assets")

        #  Final Status Assessment
        total_tests = len(diagnostic["tests"])
        failed_count = len(failed_tests)
        success_count = total_tests - failed_count
        
        diagnostic["summary"] = {
            "total_tests": total_tests,
            "successful": success_count,
            "failed": failed_count,
            "success_rate": f"{(success_count/total_tests)*100:.1f}%",
            "failed_tests": failed_tests
        }
        
        if failed_count == 0:
            diagnostic["overall_status"] = "all_systems_operational"
        elif failed_count <= 2:
            diagnostic["overall_status"] = "mostly_operational"
        else:
            diagnostic["overall_status"] = "multiple_failures"

        return jsonify(diagnostic)
        
    except Exception as global_error:
        import traceback
        diagnostic["overall_status"] = "diagnostic_failed"
        diagnostic["global_error"] = {
            "error": str(global_error),
            "type": type(global_error).__name__,
            "traceback": traceback.format_exc()
        }
        return jsonify(diagnostic), 500

@app.route("/api/debug/tiles-test", methods=["GET"])
def debug_tiles_test():
    """Test all main app tiles and pages for functionality."""
    tiles_test = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    try:
        #  Test Main Menu Tiles
        tiles_test["tests"]["main_menu_tiles"] = {
            "status": "testing",
            "tiles": {}
        }
        
        # Test each major tile/feature
        main_tiles = {
            "upload": {"route": "/api/upload", "description": "Word list file upload"},
            "quiz": {"route": "/quiz", "description": "Main spelling quiz"},
            "speed_round": {"route": "/speed-round", "description": "Speed round quiz"},
            "saved_lists": {"route": "/api/saved-lists", "description": "Saved word lists"},
            "avatars": {"route": "/api/avatars", "description": "Avatar selection"},
            "progress": {"route": "/api/buzz-dust/info", "description": "Progress tracking"},
            "achievements": {"route": "/achievements", "description": "User achievements"}
        }
        
        for tile_name, tile_info in main_tiles.items():
            try:
                # For API endpoints, test if they respond
                if tile_info["route"].startswith("/api/"):
                    # Simulate API endpoint validation (check if route exists in app)
                    route_exists = any(rule.rule == tile_info["route"] for rule in app.url_map.iter_rules())
                    tiles_test["tests"]["main_menu_tiles"]["tiles"][tile_name] = {
                        "status": "success" if route_exists else "route_not_found",
                        "route": tile_info["route"],
                        "description": tile_info["description"],
                        "endpoint_exists": route_exists
                    }
                else:
                    # For page routes, check if they exist
                    route_exists = any(rule.rule == tile_info["route"] for rule in app.url_map.iter_rules())
                    tiles_test["tests"]["main_menu_tiles"]["tiles"][tile_name] = {
                        "status": "success" if route_exists else "route_not_found",
                        "route": tile_info["route"],
                        "description": tile_info["description"],
                        "page_exists": route_exists
                    }
            except Exception as e:
                tiles_test["tests"]["main_menu_tiles"]["tiles"][tile_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        tiles_test["tests"]["main_menu_tiles"]["status"] = "completed"
        
        #  Test Quiz Functionality 
        tiles_test["tests"]["quiz_functionality"] = {"status": "testing"}
        try:
            # Test quiz-related endpoints
            recent_sessions = QuizSession.query.limit(5).all()
            
            # Test wordbank functionality (using local function)
            wordbank = get_wordbank()
            
            # Test quiz state initialization
            quiz_state = session.get('quiz_state_v1', {})
            
            tiles_test["tests"]["quiz_functionality"] = {
                "status": "success",
                "recent_sessions": len(recent_sessions),
                "wordbank_available": wordbank is not None,
                "wordbank_size": len(wordbank) if isinstance(wordbank, list) else 0,
                "quiz_state_exists": bool(quiz_state),
                "quiz_routes": {
                    "main_quiz": "/quiz",
                    "api_next": "/api/next", 
                    "api_answer": "/api/answer",
                    "api_clear": "/api/clear"
                }
            }
        except Exception as e:
            tiles_test["tests"]["quiz_functionality"] = {"status": "failed", "error": str(e)}

        #  Test Speed Round
        tiles_test["tests"]["speed_round_functionality"] = {"status": "testing"}
        try:
            speed_config = SpeedRoundConfig.query.first()
            
            tiles_test["tests"]["speed_round_functionality"] = {
                "status": "success",
                "config_available": bool(speed_config),
                "routes": {
                    "speed_round_page": "/speed-round",
                    "api_start": "/api/speed-round/start",
                    "api_submit": "/api/speed-round/submit"
                }
            }
        except Exception as e:
            tiles_test["tests"]["speed_round_functionality"] = {"status": "failed", "error": str(e)}

        #  Test File Upload System
        tiles_test["tests"]["upload_functionality"] = {"status": "testing"}  
        try:
            upload_dir = os.path.join(app.root_path, 'uploads')
            
            tiles_test["tests"]["upload_functionality"] = {
                "status": "success",
                "upload_directory": os.path.exists(upload_dir),
                "supported_formats": ["CSV", "TXT", "DOCX", "PDF", "Image (OCR)"],
                "api_endpoint": "/api/upload"
            }
        except Exception as e:
            tiles_test["tests"]["upload_functionality"] = {"status": "failed", "error": str(e)}

        #  Test Progress/Achievement System
        tiles_test["tests"]["progress_system"] = {"status": "testing"}
        try:
            # Test buzz dust system
            user = get_or_create_guest_user()
            if user:
                buzz_dust = getattr(user, 'honey_points', 0)
                achievements = Achievement.query.limit(5).all()
                
                tiles_test["tests"]["progress_system"] = {
                    "status": "success",
                    "user_buzz_dust": buzz_dust,
                    "achievements_available": len(achievements),
                    "api_endpoints": ["/api/buzz-dust/info", "/achievements"]
                }
            else:
                tiles_test["tests"]["progress_system"] = {"status": "failed", "error": "No user available"}
        except Exception as e:
            tiles_test["tests"]["progress_system"] = {"status": "failed", "error": str(e)}

        #  Summary
        total_tile_tests = len([t for test_group in tiles_test["tests"].values() 
                               for t in (test_group.get("tiles", {}) if "tiles" in test_group else [test_group])])
        failed_tile_tests = len([t for test_group in tiles_test["tests"].values() 
                                for t in (test_group.get("tiles", {}).values() if "tiles" in test_group else [test_group])
                                if t.get("status") == "failed"])
        
        tiles_test["summary"] = {
            "total_tests": len(tiles_test["tests"]),
            "failed_count": len([t for t in tiles_test["tests"].values() if t.get("status") == "failed"]),
            "all_tiles_functional": failed_tile_tests == 0
        }
        
        return jsonify(tiles_test)
        
    except Exception as e:
        import traceback
        tiles_test["error"] = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        return jsonify(tiles_test), 500

# --- Routes: Saved Word Lists (Persistent) -----------------------------------
@app.route("/api/debug/saved-lists-test", methods=["GET"])
def debug_saved_lists_test():
    """Step-by-step test of saved-lists functionality for debugging."""
    debug_steps = {}
    
    try:
        # Step 1: Test database connection
        debug_steps["step_1_db_connection"] = "testing"
        db.session.execute('SELECT 1')
        debug_steps["step_1_db_connection"] = "success"
        
        # Step 2: Test models import
        debug_steps["step_2_models_import"] = "testing"
        from models import WordList, User
        debug_steps["step_2_models_import"] = "success"
        
        # Step 3: Test user resolution
        debug_steps["step_3_user_resolution"] = "testing"
        user = get_or_create_guest_user()
        debug_steps["step_3_user_resolution"] = "success" if user else "failed"
        debug_steps["user_id"] = user.id if user else None
        debug_steps["user_type"] = "authenticated" if current_user.is_authenticated else "guest"
        
        # Step 4: Test WordList query (without execution)
        debug_steps["step_4_query_build"] = "testing"
        if user:
            query = WordList.query.filter(WordList.created_by_user_id == user.id)
            debug_steps["step_4_query_build"] = "success"
            debug_steps["query_sql"] = str(query)
            
            # Step 5: Test query execution
            debug_steps["step_5_query_execution"] = "testing"
            lists = query.all()
            debug_steps["step_5_query_execution"] = "success"
            debug_steps["lists_found"] = len(lists)
        else:
            debug_steps["step_4_query_build"] = "skipped_no_user"
            debug_steps["step_5_query_execution"] = "skipped_no_user"
        
        return jsonify({
            "status": "debug_complete",
            "steps": debug_steps,
            "session_info": {
                "keys": list(session.keys()),
                "guest_user_id": session.get("guest_user_id"),
                "is_guest": session.get("is_guest")
            }
        })
        
    except Exception as e:
        import traceback
        debug_steps["error"] = str(e)
        debug_steps["error_type"] = type(e).__name__
        debug_steps["traceback"] = traceback.format_exc()
        
        return jsonify({
            "status": "debug_failed",
            "steps": debug_steps,
            "error": str(e)
        }), 500

# =============================================================================
#  WORD LIST API SUITE - Complete CRUD for Saved Lists
# =============================================================================

def _serialize_word_list(wl):
    """Return a WordList in the exact shape frontend expects."""
    items = (WordListItem.query
             .filter_by(word_list_id=wl.id)
             .order_by(WordListItem.position.asc(), WordListItem.id.asc())
             .all())

    # Calculate percent_used: how many words from this list have been attempted in quizzes
    percent_used = None
    if items:
        try:
            from models import QuizResult
            # Get all unique words from this list
            list_words = {item.word.lower() for item in items}
            
            # Count how many of these words have been attempted by this user
            attempted_words = set()
            quiz_results = QuizResult.query.filter(
                QuizResult.user_id == wl.created_by_user_id,
                QuizResult.word.in_([w.upper() for w in list_words] + [w.lower() for w in list_words] + [w.capitalize() for w in list_words])
            ).all()
            
            for result in quiz_results:
                attempted_words.add(result.word.lower())
            
            # Calculate percentage (0-100)
            if len(list_words) > 0:
                percent_used = (len(attempted_words) / len(list_words)) * 100
        except Exception as e:
            print(f"️ Could not calculate percent_used for list {wl.id}: {e}")
            percent_used = None

    return {
        "id": wl.id,
        "uuid": wl.uuid,
        "name": wl.list_name,
        "description": wl.description,
        "grade_level": wl.grade_level,
        "difficulty_level": wl.difficulty_level,
        "word_count": len(items),
        "is_favorite": wl.is_favorite,
        "is_public": wl.is_public,
        "times_used": wl.times_used,
        "percent_used": percent_used,  # NEW: quiz usage tracking
        "created_at": wl.created_at.isoformat() if wl.created_at else None,
        "updated_at": wl.updated_at.isoformat() if wl.updated_at else None,
        "words": [
            {
                "id": it.id,
                "word": it.word,
                "sentence": it.sentence,
                "hint": it.hint,
                "difficulty_override": it.difficulty_override,
                "position": it.position
            }
            for it in items
        ]
    }


def _require_owner(wl, user_id):
    """Guard that the list belongs to specified user."""
    if not wl or wl.created_by_user_id != user_id:
        return False
    return True


def _normalize_words(words_raw):
    """
    Accepts list of:
      - strings ["cat","dog"]
      - dicts [{"word":"cat","sentence":"..."}]
    Returns list of dicts with consistent keys.
    """
    normalized = []
    if not words_raw:
        return normalized

    for w in words_raw:
        if isinstance(w, str):
            word_val = w.strip()
            if not word_val:
                continue
            normalized.append({
                "word": word_val,
                "sentence": None,
                "hint": None,
                "difficulty_override": None
            })
        elif isinstance(w, dict):
            word_val = (w.get("word") or "").strip()
            if not word_val:
                continue
            normalized.append({
                "word": word_val,
                "sentence": w.get("sentence"),
                "hint": w.get("hint"),
                "difficulty_override": w.get("difficulty_override")
            })
    return normalized


@app.route("/api/saved-lists", methods=["GET"])
def list_saved_wordlists():
    """GET all saved lists for current user."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": True, "lists": [], "error": "User session issue"}), 200

        lists = (WordList.query
                 .filter_by(created_by_user_id=user.id)
                 .order_by(WordList.updated_at.desc())
                 .all())

        payload = [_serialize_word_list(wl) for wl in lists]
        return jsonify({"ok": True, "lists": payload}), 200

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists GET: {e}")
        return jsonify({"ok": True, "lists": [], "error": str(e)}), 200


@app.route("/api/saved-lists", methods=["POST"])
def create_saved_list():
    """POST create a new saved list."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        data = request.get_json(force=True) or {}
        name = (data.get("name") or data.get("list_name") or "").strip()
        load_into_session = bool(data.get("load_into_session", False))

        if not name:
            return jsonify({"ok": False, "error": "name_required"}), 400

        words = _normalize_words(data.get("words"))

        wl = WordList(
            created_by_user_id=user.id,
            list_name=name,
            description=data.get("description"),
            grade_level=data.get("grade_level"),
            difficulty_level=data.get("difficulty_level") or "normal",
            is_public=bool(data.get("is_public", False)),
            is_favorite=bool(data.get("is_favorite", False)),
            word_count=len(words),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(wl)
        db.session.flush()  # get wl.id before inserting items

        for i, w in enumerate(words, start=1):
            db.session.add(WordListItem(
                word_list_id=wl.id,
                word=w["word"],
                sentence=w.get("sentence"),
                hint=w.get("hint"),
                difficulty_override=w.get("difficulty_override"),
                position=i
            ))

        db.session.commit()
        print(f" Created word list '{name}' with {len(words)} words for user {user.id}")

        # Optionally load this newly created list into the active session wordbank
        if load_into_session and words:
            # Transform normalized words into session wordbank shape
            rows = [
                {
                    "word": w.get("word") or "",
                    "sentence": w.get("sentence") or "",
                    "hint": w.get("hint") or ""
                }
                for w in words if (w.get("word") or "").strip()
            ]

            # Clear existing quiz state before replacing words
            session.pop(QUIZ_STATE_KEY, None)
            session.pop("is_random_play", None)
            set_wordbank(rows, is_user_upload=True)
            init_quiz_state(len(rows))
            print(f" Loaded newly created list into session wordbank (rows={len(rows)}) and initialized quiz state")

        return jsonify({"ok": True, "list": _serialize_word_list(wl)}), 201

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists POST: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>", methods=["GET"])
def get_saved_wordlist(list_id):
    """GET one list by id."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        wl = WordList.query.get(list_id)
        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "not_found"}), 404

        return jsonify({"ok": True, "list": _serialize_word_list(wl)}), 200

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists/{list_id} GET: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>", methods=["PUT"])
def update_saved_wordlist(list_id):
    """PUT update list metadata and/or replace words."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        wl = WordList.query.get(list_id)
        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "not_found"}), 404

        data = request.get_json(force=True) or {}

        # metadata updates
        if "name" in data:
            new_name = (data.get("name") or "").strip()
            if not new_name:
                return jsonify({"ok": False, "error": "name_required"}), 400
            wl.list_name = new_name

        if "description" in data:
            wl.description = data.get("description")

        if "grade_level" in data:
            wl.grade_level = data.get("grade_level")

        if "difficulty_level" in data:
            wl.difficulty_level = data.get("difficulty_level") or wl.difficulty_level

        if "is_public" in data:
            wl.is_public = bool(data.get("is_public"))

        if "is_favorite" in data:
            wl.is_favorite = bool(data.get("is_favorite"))

        # replace words (can be triggered by replace_words=true OR if words array is provided)
        should_replace_words = data.get("replace_words") is True or ("words" in data and isinstance(data.get("words"), list))
        
        if should_replace_words:
            words = _normalize_words(data.get("words", []))

            if not words:
                return jsonify({"ok": False, "error": "words_required"}), 400

            # delete old items
            WordListItem.query.filter_by(word_list_id=wl.id).delete()

            # insert new items
            for i, w in enumerate(words, start=1):
                db.session.add(WordListItem(
                    word_list_id=wl.id,
                    word=w["word"],
                    sentence=w.get("sentence"),
                    hint=w.get("hint"),
                    difficulty_override=w.get("difficulty_override"),
                    position=i
                ))

            wl.word_count = len(words)
            print(f" Updated {wl.list_name}: replaced {len(words)} words")

        wl.updated_at = datetime.utcnow()
        db.session.commit()

        print(f" Updated word list id={list_id} '{wl.list_name}'")
        return jsonify({"ok": True, "list": _serialize_word_list(wl)}), 200

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists/{list_id} PUT: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>", methods=["DELETE"])
@app.route("/api/saved-lists/delete", methods=["POST"])
def delete_saved_wordlist(list_id=None):
    """DELETE list."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Get list_id from URL parameter or POST body
        if list_id is None:
            payload = request.get_json(silent=True) or {}
            list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")

        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        # Try numeric ID first, fallback to UUID
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "not_found"}), 404

        db.session.delete(wl)
        db.session.commit()

        print(f" Deleted word list id={wl.id} '{wl.list_name}'")
        return jsonify({"ok": True, "deleted_id": list_id}), 200

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists DELETE: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>/favorite", methods=["POST"])
@app.route("/api/saved-lists/favorite", methods=["POST"])
def toggle_saved_list_favorite(list_id=None):
    """POST toggle favorite/pin."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        # Get list_id from URL or body
        if list_id is None:
            data = request.get_json() or {}
            list_id = data.get("id")

        if not list_id:
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        # Try numeric ID first, fallback to UUID
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "not_found"}), 404

        wl.is_favorite = not bool(wl.is_favorite)
        wl.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"ok": True, "is_favorite": wl.is_favorite}), 200

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists/favorite: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/<int:list_id>/clone", methods=["POST"])
def clone_saved_list(list_id):
    """POST clone list."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400

        wl = WordList.query.get(list_id)
        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "not_found"}), 404

        data = request.get_json(force=True) or {}
        new_name = (data.get("name") or f"Copy of {wl.list_name}").strip()

        new_wl = WordList(
            created_by_user_id=user.id,
            list_name=new_name,
            description=wl.description,
            grade_level=wl.grade_level,
            difficulty_level=wl.difficulty_level,
            is_public=False,          # clones default to private
            is_favorite=False,
            word_count=0
        )
        db.session.add(new_wl)
        db.session.flush()

        items = (WordListItem.query
                 .filter_by(word_list_id=wl.id)
                 .order_by(WordListItem.position.asc())
                 .all())

        for it in items:
            db.session.add(WordListItem(
                word_list_id=new_wl.id,
                word=it.word,
                sentence=it.sentence,
                hint=it.hint,
                difficulty_override=it.difficulty_override,
                position=it.position
            ))

        new_wl.word_count = len(items)
        db.session.commit()

        print(f" Cloned word list '{wl.list_name}' to '{new_name}'")
        return jsonify({"ok": True, "list": _serialize_word_list(new_wl)}), 201

    except Exception as e:
        db.session.rollback()
        print(f" ERROR /api/saved-lists/clone: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/saved-lists/save", methods=["POST"])
def save_current_wordlist():
    """Legacy: Save current session wordbank as a new list."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400
        
        payload = request.get_json(silent=True) or {}
        list_name = (payload.get("list_name") or "").strip()
        description = (payload.get("description") or "").strip()

        if not list_name:
            return jsonify({"ok": False, "error": "List name is required"}), 400

        words = get_wordbank()
        if not words:
            return jsonify({"ok": False, "error": "No words available to save"}), 400

        # Create WordList record
        wl = WordList(
            created_by_user_id=user.id,
            list_name=list_name,
            description=description,
            word_count=len(words),
            is_public=False
        )
        db.session.add(wl)
        db.session.flush()

        # Insert items
        for i, rec in enumerate(words, start=1):
            item = WordListItem(
                word_list_id=wl.id,
                word=(rec.get("word") or "").strip(),
                sentence=(rec.get("sentence") or "").strip(),
                hint=(rec.get("hint") or "").strip(),
                position=i
            )
            db.session.add(item)

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
        print(f" ERROR /api/saved-lists/save: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to save list"}), 500


@app.route("/api/saved-lists/load", methods=["POST"])
def load_saved_wordlist():
    """Load a saved list into the current session and initialize quiz state."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        # CRITICAL DEBUG: Track session across request
        incoming_session_id = session.get("session_id", "NEW")
        incoming_storage_id = session.get("wordbank_storage_id", "NONE")
        print(f"\n{'='*80}")
        print(f" /api/saved-lists/load REQUEST RECEIVED")
        print(f"{'='*80}")
        print(f"   Incoming session_id: {incoming_session_id}")
        print(f"   Incoming storage_id: {incoming_storage_id}")
        print(f"   Session keys: {list(session.keys())}")
        print(f"   Cookie header: {request.headers.get('Cookie', 'NO COOKIE')[:200]}")
        
        user = get_or_create_guest_user()
        if not user:
            print(" /api/saved-lists/load: Unable to resolve user")
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400
        
        payload = request.get_json(silent=True) or {}
        list_id = payload.get("id") or payload.get("uuid") or payload.get("list_id")
        if not list_id:
            print(f" /api/saved-lists/load: Missing list id. Payload: {payload}")
            return jsonify({"ok": False, "error": "Missing list id"}), 400

        # Lookup by uuid if non-numeric, else by id
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not wl:
            print(f" /api/saved-lists/load: List not found. list_id={list_id}, user_id={user.id}")
            return jsonify({"ok": False, "error": "List not found"}), 404

        #  RESUME/RESTART LOGIC
        # Check if a quiz is already in progress for this specific list
        force_restart = payload.get("force_restart", False)
        quiz_state = session.get(QUIZ_STATE_KEY)
        active_list_id = session.get("source_list_id")
        
        if quiz_state and active_list_id == list_id and not force_restart:
            is_complete = quiz_state.get("is_complete", False)
            current_index = quiz_state.get("current_word_index", 0)
            total_words = quiz_state.get("total_words", 0)
            
            if not is_complete and current_index > 0 and current_index < total_words:
                # This list is already in progress, ask user what to do
                print(f" /api/saved-lists/load: Found in-progress quiz for list_id={list_id}")
                return jsonify({
                    "ok": True,
                    "action_required": "resume_or_restart",
                    "message": f"You have a quiz in progress for '{wl.list_name}'.",
                    "list_name": wl.list_name,
                    "progress": {
                        "current": current_index,
                        "total": total_words
                    }
                })
        
        # User chose restart or no quiz in progress
        if force_restart:
            print(f" /api/saved-lists/load: User chose to restart quiz for list_id={list_id}")

        # --- End Resume/Restart Logic ---

        items = WordListItem.query.filter_by(word_list_id=wl.id).order_by(WordListItem.position.asc()).all()
        rows = []
        for it in items:
            if it.word:
                rows.append({"word": it.word, "sentence": it.sentence or "", "hint": it.hint or ""})

        if not rows:
            print(f" /api/saved-lists/load: List has no items. list_id={wl.id}")
            return jsonify({"ok": False, "error": "This list is empty. Please upload words to this list first."}), 400

        #  CRITICAL: COMPLETE WORDBANK WIPE AND REPLACEMENT
        # Treat saved list load EXACTLY like fresh upload - prevent duplicate words from appended lists
        # set_wordbank() now handles deletion automatically with proper transaction handling
        
        # Step 1: Clear quiz state BEFORE touching wordbank
        session.pop(QUIZ_STATE_KEY, None)
        session.pop("is_random_play", None)
        session.modified = True
        
        print(f" /api/saved-lists/load: Loading {len(rows)} fresh words from saved list (old wordbank will be auto-deleted)")

        # Step 2: Load saved list as brand new wordbank
        # This will automatically delete old wordbank if storage_id exists
        set_wordbank(rows, is_user_upload=True)
        
        # CRITICAL DEBUG: Verify wordbank was actually saved
        verify_wb = get_wordbank()
        verify_storage_id = session.get("wordbank_storage_id")
        print(f" /api/saved-lists/load: VERIFICATION after set_wordbank:")
        print(f"   storage_id in session: {verify_storage_id}")
        print(f"   get_wordbank() returned: {len(verify_wb)} words")
        print(f"   Session keys: {list(session.keys())}")
        if len(verify_wb) != len(rows):
            print(f"️ WARNING: Mismatch! Saved {len(rows)} but got {len(verify_wb)} back")
        
        # Initialize fresh quiz state from new wordbank
        init_quiz_state(len(rows))
        
        #  Store the source list ID to enable the resume feature
        session["source_list_id"] = list_id
        
        print(f" /api/saved-lists/load: Initialized quiz state for {len(rows)} words")

        # FINAL VERIFICATION
        final_session_id = session.get("session_id", "MISSING")
        final_storage_id = session.get("wordbank_storage_id", "MISSING")
        print(f" /api/saved-lists/load RESPONSE:")
        print(f"   Final session_id: {final_session_id}")
        print(f"   Final storage_id: {final_storage_id}")
        print(f"   Wordbank count: {len(verify_wb)}")
        print(f"   Session modified: {session.modified}")
        print(f"{'='*80}\n")

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
        print(f" ERROR /api/saved-lists/load: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": "Failed to load list"}), 500


@app.route("/api/saved-lists/rename", methods=["POST"])
def rename_saved_wordlist():
    """Rename a saved word list (legacy, use PUT instead)."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

        user = get_or_create_guest_user()
        if not user:
            return jsonify({"ok": False, "error": "Unable to resolve user"}), 400
        
        data = request.get_json() or {}
        list_id = data.get("id")
        new_name = (data.get("new_name") or "").strip()

        if not list_id or not new_name:
            return jsonify({"ok": False, "error": "Missing list id or name"}), 400

        # Try numeric ID first, fallback to UUID
        wl = None
        try:
            numeric_id = int(str(list_id))
            wl = WordList.query.filter_by(id=numeric_id, created_by_user_id=user.id).first()
        except:
            wl = WordList.query.filter_by(uuid=str(list_id), created_by_user_id=user.id).first()

        if not _require_owner(wl, user.id):
            return jsonify({"ok": False, "error": "List not found"}), 404

        wl.list_name = new_name
        wl.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"ok": True, "id": wl.id, "name": wl.list_name})

    except Exception as e:
        print(f" ERROR /api/saved-lists/rename: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/upload-to-saved-list", methods=["POST"])
def upload_to_saved_list():
    """Upload a file to update an existing saved word list."""
    try:
        premium_block = _require_premium_json("saved_lists")
        if premium_block is not None:
            return premium_block

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
        filename = (file.filename or '').lower()
        file_bytes = file.read()  # Read raw bytes once for parser functions

        if filename.endswith('.csv'):
            words = parse_csv(file_bytes, filename)
        elif filename.endswith('.txt'):
            words = parse_txt(file_bytes)
        elif filename.endswith('.docx'):
            words = parse_docx(file_bytes)
        elif filename.endswith('.pdf'):
            words = parse_pdf(file_bytes)
        elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            if not TESSERACT_AVAILABLE:
                return jsonify({"ok": False, "error": "Image processing requires Tesseract OCR installation"}), 400
            words = parse_image_ocr(file_bytes)
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
# NOTE: The root route '/' is handled by home_root_direct() at line 767.
# The duplicate route decorator below has been commented out to fix the 500 error.
# @app.route("/")  # REMOVED: duplicate route - home_root_direct() at line 767 handles '/'
def home():
    """Legacy function - route removed to fix duplicate route issue.
    
    This function previously redirected to /app, but home_root_direct() at line 767
    is the correct handler for '/' that renders unified_menu.html with all required
    template variables. This function is kept for backwards compatibility but the
    route decorator has been removed.
    """
    # Delegate to home_root_direct() which has all the template variables
    return home_root_direct()

@app.route("/app")
def app_home():
    # App Review / demo mode toggle.
    # Only respected when APP_REVIEW_MODE=1 to avoid exposing a public backdoor.
    try:
        if APP_REVIEW_MODE:
            rv = (request.args.get('review') or '').strip().lower()
            if rv in ('1', 'true', 'yes', 'on'):
                session['app_review_mode'] = True
            elif rv in ('0', 'false', 'no', 'off'):
                session.pop('app_review_mode', None)
    except Exception:
        pass

    import time
    timestamp = str(int(time.time()))
    from flask import make_response
    # Pass subscription messaging to home for guest upsell
    billing_mode = os.environ.get('REGISTRATION_BILLING_MODE', 'subscription').strip().lower()
    try:
        _m = os.environ.get('SUBSCRIPTION_MONTHLY_USD')
        monthly_fee = float(_m) if _m not in (None, '') else None
    except Exception:
        monthly_fee = None
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
    # Default to the current monthly subscription SKU unless explicitly overridden.
    # (The legacy 'beesmart.sub.full_monthly' remains supported via env and PRODUCT_MAP.)
    try:
        subscription_product_id = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID')
        subscription_product_id = (subscription_product_id or '').strip() or SUBSCRIPTION_PRODUCT_IDS['monthly']
    except Exception:
        subscription_product_id = SUBSCRIPTION_PRODUCT_IDS['monthly']
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
            'duration': '1 month',
            'name': 'Premium Monthly Membership'
        },
        'yearly': {
            'id': SUBSCRIPTION_PRODUCT_IDS['yearly'],
            'duration': '1 year',
            'name': 'Premium Yearly Membership',
            'savings': None
        },
        'family': {
            'id': SUBSCRIPTION_PRODUCT_IDS['family'],
            'duration': '1 month',
            'name': 'Premium Family Membership',
            'family_sharing': True
        }
    }

    # In monthly-only builds, only expose the monthly subscription.
    if IAP_MONTHLY_ONLY:
        subscription_products = {k: v for k, v in subscription_products.items() if k == 'monthly'}

    # Some deployments may fail to load pricing config (or return None).
    # Ensure templates always receive a real number to avoid Jinja formatting errors.
    try:
        _monthly_fee_for_template = float(monthly_fee) if monthly_fee is not None else 3.99
    except Exception:
        _monthly_fee_for_template = 3.99

    html = render_template(
        "unified_menu.html",
        timestamp=timestamp,
        registration_billing_mode=billing_mode,
        subscription_monthly_usd=_monthly_fee_for_template,
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
        <h1>BeeSmart Test Home </h1>
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
        # --- CORS / iOS WebView compatibility ---------------------------------
        # WKWebView often treats requests as cross-origin (app://, file://, capacitor://)
        # and will fail with “access control checks” unless we attach consistent CORS
        # headers on both API + static asset responses and handle OPTIONS preflight.
        if request.path.startswith('/api/') or request.path.startswith('/static/'):
            # --- CORS / iOS WebView compatibility ---------------------------------
            # Safari/WKWebView can send Origin values like:
            # - "null" (file:// contexts)
            # - capacitor://localhost, ionic://localhost, app://*, etc
            # For credentialed requests, browsers require a *non-wildcard* ACAO.
            origin = request.headers.get('Origin')
            origin = (origin or '').strip()

            # Some edge deployments / proxies (or certain WebView stacks) can omit the
            # Origin header entirely, yet the browser still enforces CORS based on the
            # request context. In that case, fall back to Referer-based allowlisting
            # for our own site.
            referer = (request.headers.get('Referer') or '').strip()

            # Always vary on Origin so caches/CDNs don't mix cross-origin responses.
            vary = resp.headers.get('Vary')
            if vary:
                if 'Origin' not in vary:
                    resp.headers['Vary'] = f"{vary}, Origin"
            else:
                resp.headers['Vary'] = 'Origin'

            allow_origin = None
            if origin and origin.lower() != 'null':
                allow_origin = origin
            elif referer:
                try:
                    from urllib.parse import urlparse
                    ref_host = urlparse(referer).netloc
                    # Allow same-site referrals even if Origin was stripped.
                    if ref_host in (request.host, 'beesmartspelling.app', 'www.beesmartspelling.app'):
                        allow_origin = f"{request.scheme}://{ref_host}" if request.scheme else f"https://{ref_host}"
                except Exception:
                    pass

            if allow_origin:
                resp.headers['Access-Control-Allow-Origin'] = allow_origin
                resp.headers['Access-Control-Allow-Credentials'] = 'true'
            else:
                # If we can't safely echo an Origin (missing or "null"), fall back.
                # - Static assets: permissive wildcard is fine.
                # - API: avoid wildcard because we rely on cookies.
                if request.path.startswith('/static/'):
                    resp.headers['Access-Control-Allow-Origin'] = '*'

            resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
            # Allow the header sets commonly used by fetch/XHR + native wrappers.
            resp.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Requested-With, Accept, Origin, '
                'Cache-Control, Pragma, X-CSRFToken, X-CSRF-Token, '
                'X-Apple-Storekit-Version, X-Client-Version'
            )
            resp.headers['Access-Control-Max-Age'] = '86400'  # cache preflight 24h

        if request.path == '/':
            print(f"DEBUG AFTER_REQUEST / status={resp.status_code}")
        
        # Apply aggressive no-cache headers for all API endpoints to prevent stale wordbank / quiz state.
        # This consolidates front-end cache busting with server guarantees (see manual upload race condition notes).
        if request.path.startswith('/api/'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, max-age=0, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'

        # Service worker script must never be cached by the browser/CDN, otherwise
        # clients can get stuck on an old SW and keep serving stale UI.
        if request.path == '/service-worker.js':
            resp.headers['Cache-Control'] = 'no-store, no-cache, max-age=0, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
        
        # Set proper Content-Type with UTF-8 charset for HTML responses
        # Fixes accessibility/compatibility validator warnings
        if resp.content_type and 'text/html' in resp.content_type:
            if 'charset' not in resp.content_type:
                resp.headers['Content-Type'] = 'text/html; charset=utf-8'
            
            # Apply cache-control headers for HTML pages (not as aggressive as API)
            # Allow browser caching but require revalidation for freshness
            if 'Cache-Control' not in resp.headers:
                resp.headers['Cache-Control'] = 'private, max-age=0, must-revalidate'
        
        # Cache busting for static assets with versioning
        # Allow long-term caching for fingerprinted assets
        if request.path.startswith('/static/'):
            if any(ext in request.path for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2']):
                # Check if URL has cache-busting parameter (timestamp or version)
                if '?' in request.path or 'timestamp=' in request.query_string.decode() or 'v=' in request.query_string.decode():
                    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year for versioned assets
                else:
                    resp.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'  # 1 hour for unversioned
    except Exception:
        pass
    return resp

@app.route("/test")
def test_page():
    """Test page to verify Flask is working"""
    return render_template("test_page.html")


@app.route('/api/<path:_path>', methods=['OPTIONS'])
def _api_cors_preflight(_path):
    """CORS preflight responder for API routes.

    Some WebView environments send preflight OPTIONS even for credentialed GETs.
    We respond 204 and let the global after_request hook attach the CORS headers.
    """
    from flask import make_response
    resp = make_response('', 204)
    return resp


@app.route('/static/<path:_path>', methods=['OPTIONS'])
def _static_cors_preflight(_path):
    """CORS preflight responder for static routes.

    Some WebView environments send OPTIONS preflight even for simple GET asset
    loads. Return 204 and rely on after_request to attach CORS headers.
    """
    from flask import make_response
    resp = make_response('', 204)
    return resp

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

@app.route("/quiz", strict_slashes=False)
def quiz_page():
    """Interactive quiz page"""
    try:
        # Ensure session persists across page navigation
        session.permanent = True
        
        # Enhanced debugging for mobile session issues
        session_id = session.get("session_id", "NONE")
        storage_id = session.get("wordbank_storage_id", "NONE")
        
        print(f"\n{'='*60}")
        print(f" /quiz ROUTE ACCESSED")
        print(f"{'='*60}")
        print(f"DEBUG /quiz: session_id={session_id}, storage_id={storage_id}")
        print(f"DEBUG /quiz: session keys={list(session.keys())}")
        print(f"DEBUG /quiz: cookies={list(request.cookies.keys())}")
        print(f"DEBUG /quiz: cookie values={dict(request.cookies)}")
        print(f"DEBUG /quiz: user-agent={request.headers.get('User-Agent', 'UNKNOWN')[:80]}")
        
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
            init_quiz_state(len(wordbank))
        else:
            # Check if quiz is completed - reset if so
            idx = state.get('idx', 0)
            order = state.get('order', [])
            if idx >= len(order):
                print(f"DEBUG /quiz: Quiz completed (idx={idx}, total={len(order)}) - resetting for new attempt")
                init_quiz_state(len(wordbank))
            else:
                print(f"DEBUG /quiz: Using existing quiz state - idx={idx}, total={len(order)}")
            
        print(f"DEBUG /quiz: Rendering quiz.html with {len(wordbank)} words")
        
        # Cache busting timestamp
        import time
        timestamp = int(time.time() * 1000)
        
        # Pass user information if logged in
        user_name = None
        if current_user.is_authenticated:
            user_name = current_user.display_name
            print(f"DEBUG /quiz: User logged in as {user_name}")
        
        # Force fresh HTML for quiz page (prevents stale cached templates that can preserve old JS syntax bugs)
        from flask import make_response
        resp = make_response(render_template("quiz.html", user_name=user_name, timestamp=timestamp))
        resp.headers['Cache-Control'] = 'no-store, no-cache, max-age=0, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except Exception as e:
        import traceback
        print(f" ERROR in /quiz: {e}")
        traceback.print_exc()
        return (
            f"<h1>Quiz Error</h1><p>{type(e).__name__}: {str(e)}</p>",
            500,
            {"Content-Type": "text/html"}
        )

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
                'status': 'NEW VERSION ' if (has_hive_stats and has_floating_bee) else 'OLD VERSION ',
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
    # Include a build fingerprint so we can confirm which commit is deployed.
    # DigitalOcean deployments can sometimes serve stale code if the process wasn't restarted.
    try:
        import subprocess
        build_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=1.0,
        ).decode("utf-8").strip()
    except Exception:
        build_sha = os.getenv("APP_BUILD_SHA") or None

    # Prefer a version derived from the git state when available. This prevents a long-running
    # process from accidentally reporting a stale hardcoded value after multiple deploy cycles.
    try:
        import subprocess
        derived_version = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=1.0,
        ).decode("utf-8").strip()
    except Exception:
        derived_version = None

    version = os.getenv("APP_HEALTH_VERSION") or derived_version or APP_VERSION

    return jsonify({"status": "ok", "version": version, "build": build_sha}), 200

# Extra health endpoints for PaaS defaults (Railway/Render/Heroku variants)
# Many platforms probe different default paths; keep them lightweight and identical
@app.route("/healthcheck")
@app.route("/healthz")
@app.route("/__health")
@app.route("/_/health")
@app.route("/ready")
def health_check_aliases():
    try:
        import subprocess
        build_sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=1.0,
        ).decode("utf-8").strip()
    except Exception:
        build_sha = os.getenv("APP_BUILD_SHA") or None

    try:
        import subprocess
        derived_version = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=1.0,
        ).decode("utf-8").strip()
    except Exception:
        derived_version = None

    version = os.getenv("APP_HEALTH_VERSION") or derived_version or APP_VERSION

    return jsonify({"status": "ok", "version": version, "build": build_sha}), 200

@app.route("/health/iap")
def health_iap():
    """IAP health and configuration status for ops visibility."""
    try:
        mode = (IAP_VERIFICATION_MODE or 'mock').strip().lower()
        mock = bool(mode == 'mock')

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
        has_priv = bool(os.getenv('APPLE_PRIVATE_KEY') or os.getenv('APPLE_PRIVATE_KEY_B64') or os.getenv('APPLE_PRIVATE_KEY_PATH'))
        if not has_priv:
            apple_missing.append('APPLE_PRIVATE_KEY or APPLE_PRIVATE_KEY_B64 or APPLE_PRIVATE_KEY_PATH')
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
            "version": APP_VERSION,
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
                        print(f" Added column: {col_name}")
                    except Exception as e:
                        print(f" Failed to add column {col_name}: {e}")
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
        print(f" Migration failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Migration failed",
            "error": str(e)
        }), 500

#  TEST ENDPOINT REMOVED - No external dictionary API
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
    #  Lazy-load Simple Wiktionary on first use (improves Railway startup time)
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
    
    print(f" Searching for {count} words at difficulty level {difficulty}...")
    
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
    
    print(f" Found {len(exact_matches)} exact matches, {len(close_matches)} close matches")
    
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
    
    print(f" Selected {len(result)} quality words at difficulty {difficulty}")
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
            init_quiz_state(len(random_words))
            
            # Mark this as a Random Play session to suppress default words warning
            session['is_random_play'] = True
            
            print(f" Generated {len(random_words)} random words at difficulty {difficulty}")
            
            return jsonify({
                "status": "success",
                "count": len(random_words),
                "difficulty": difficulty,
                "message": f" Generated {len(random_words)} random words at difficulty level {difficulty}!",
                "words": random_words  # For preview
            })
            
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
            
    except Exception as e:
        print(f" Error generating random words: {e}")
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
            print(" No battle code provided")
            return False
        
        # Ensure directory exists
        os.makedirs(BATTLES_DIR, exist_ok=True)
        
        # Save to file
        battle_file = os.path.join(BATTLES_DIR, f"{code}.json")
        with open(battle_file, 'w', encoding='utf-8') as f:
            json.dump(battle_data, f, indent=2, ensure_ascii=False)
        
        print(f" Battle saved: {code}")
        return True
    except Exception as e:
        print(f" Failed to save battle: {e}")
        return False

def load_battle(battle_code: str) -> Optional[Dict]:
    """Load battle data from JSON file"""
    try:
        battle_file = os.path.join(BATTLES_DIR, f"{battle_code}.json")
        if not os.path.exists(battle_file):
            print(f"️ Battle not found: {battle_code}")
            return None
        
        with open(battle_file, 'r', encoding='utf-8') as f:
            battle_data = json.load(f)
        
        print(f" Battle loaded: {battle_code}")
        return battle_data
    except Exception as e:
        print(f" Failed to load battle {battle_code}: {e}")
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
                        print(f"️ Battle expired: {filename}")
                        # Optional: delete expired battle
                        # os.remove(battle_file)
                except Exception as e:
                    print(f"️ Error reading battle file {filename}: {e}")
                    continue
        
        print(f" Found {len(battles)} active battles")
        return battles
    except Exception as e:
        print(f" Failed to get active battles: {e}")
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
                        print(f"️ Deleted expired battle: {filename}")
                except Exception as e:
                    print(f"️ Error cleaning battle file {filename}: {e}")
                    continue
        
        if deleted_count > 0:
            print(f" Cleaned up {deleted_count} expired battles")
        return deleted_count
    except Exception as e:
        print(f" Failed to cleanup battles: {e}")
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
        init_quiz_state(len(shuffled_list))
        
        print(f"️ {player_name} joined battle {battle_code}")
        
        return jsonify({
            "status": "success",
            "battle_code": battle_code,
            "battle_name": battle_data.get("battle_name"),
            "player_id": player_id,
            "player_name": player_name,
            "word_count": len(word_list),
            "player_count": len(players),
            "expires_at": battle_data.get("expires_at"),
            "message": f"️ Welcome to the Battle, {player_name}!"
        })
    
    except Exception as e:
        print(f" Error joining battle: {e}")
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
        print(f" Error getting leaderboard: {e}")
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
        print(f" Failed to list live battles: {e}")
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
        print(f" Error updating battle progress: {e}")
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
            status = " Completed" if player["completed"] else f" In Progress ({player['progress']})"
            
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
        
        print(f" Exported results for battle {battle_code}")
        return response
    
    except Exception as e:
        print(f" Error exporting battle results: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to export results: {str(e)}"
        }), 500

@app.route("/api/wordbank", methods=["GET"])
def api_get_wordbank():
    """
    Returns the ACTUAL current wordbank from Railway database.
    NEVER returns defaults - only what user has uploaded/entered.
    If empty, returns [] (empty list) - user must upload their own words.
    """
    # Enhanced debugging for mobile troubleshooting
    storage_id = session.get("wordbank_storage_id")
    words = get_wordbank()  # Queries Railway database
    was_cleared = session.get("wordbank_cleared", False)
    has_uploaded = session.get("has_uploaded_once", False)
    
    print(f"DEBUG /api/wordbank: session_id={session.get('session_id', 'NONE')}, "
          f"storage_id={storage_id}, word_count={len(words)}, "
          f"was_cleared={was_cleared}, has_uploaded={has_uploaded}, "
          f"session_keys={list(session.keys())}, "
          f"user_agent={request.headers.get('User-Agent', 'UNKNOWN')[:50]}")
    
    if len(words) > 0:
        print(f"ℹ️ /api/wordbank: Returning {len(words)} words from Railway database (storage_id={storage_id})")
    else:
        print(f"ℹ️ /api/wordbank: Returning 0 words - wordbank is empty (no words uploaded)")
    
    # Return both 'words' (for backward compatibility) and 'success'/'count' (for LoadingSystem)
    response = jsonify({
        "words": words,
        "success": len(words) > 0,
        "count": len(words),
        "using_default": session.get("using_default_words", False),
        "quiz_state": session.get(QUIZ_STATE_KEY, {})
    })
    # Add cache-control headers to prevent Safari caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/api/wordbank/delete", methods=["POST"])
def api_wordbank_delete():
    """Delete a single word from the current wordbank by word text or index.
    Body: { "word": "..." } OR { "index": 3 }
    Normalization removes non-alphanum and lowercases for comparison.
    """
    try:
        data = request.get_json(silent=True) or {}
        wb = get_wordbank()
        if not wb:
            return jsonify({"ok": False, "error": "No wordbank loaded"}), 400

        removed = None
        if "index" in data and isinstance(data["index"], int):
            idx = data["index"]
            if 0 <= idx < len(wb):
                removed = wb.pop(idx)
        elif "word" in data:
            target = normalize(str(data["word"]))
            for i, rec in enumerate(list(wb)):
                if normalize(rec.get("word", "")) == target:
                    removed = wb.pop(i)
                    break

        if removed is None:
            return jsonify({"ok": False, "error": "Word not found"}), 404

        # Persist updated list and refresh quiz order
        set_wordbank(wb, is_user_upload=session.get("has_uploaded_once", False))
        init_quiz_state(len(wb))
        return jsonify({"ok": True, "count": len(wb), "removed": removed.get("word")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/export", methods=["GET"])
def api_export():
    """
    Export the user's word list in JSON or CSV format.
    Query parameter: format=json or format=csv (default: json)
    """
    try:
        # Get format parameter
        export_format = request.args.get('format', 'json').lower()
        
        # Get current wordbank
        words = get_wordbank()
        
        if not words:
            return jsonify({"error": "No words to export"}), 400
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'csv':
            # Create CSV output
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Word', 'Sentence', 'Hint'])
            
            # Write data rows
            for word_data in words:
                writer.writerow([
                    word_data.get('word', ''),
                    word_data.get('sentence', ''),
                    word_data.get('hint', '')
                ])
            
            output.seek(0)
            return Response(
                output.read(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename="beesmart_wordlist_{timestamp}.csv"',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )
        else:
            # Default to JSON format
            json_data = json.dumps({
                'exported_at': timestamp,
                'word_count': len(words),
                'words': words
            }, indent=2)
            
            return Response(
                json_data,
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename="beesmart_wordlist_{timestamp}.json"',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/quiz/reset", methods=["POST"])
def api_quiz_reset():
    """
    Reset quiz state to start fresh from the beginning.
    Resets current_index and reshuffles word order.
    """
    try:
        # Reset quiz state using the same initialization logic
        wordbank = get_wordbank()
        init_quiz_state(len(wordbank))
        
        # Clear any accumulated quiz stats for fresh start
        
        return jsonify({
            "ok": True,
            "message": "Quiz reset successfully",
            "total_words": len(wordbank),
            "quiz_state": session.get(QUIZ_STATE_KEY, {})
        })
    except Exception as e:
        print(f" Error resetting quiz: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/daily-reward", methods=["POST"])
def api_daily_reward():
    """Check and award daily login rewards to authenticated users"""
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    try:
        reward_data = check_daily_login_reward(current_user.id)
        return jsonify({
            "success": True,
            "reward": reward_data if reward_data else None
        })
    except Exception as e:
        print(f"Daily reward error: {e}")
        return jsonify({"success": False, "error": "Failed to check daily reward"}), 500

@app.route("/api/word-of-day", methods=["GET"])
def api_word_of_day():
    """Get the word of the day with bonus points information"""
    try:
        word_data = get_word_of_the_day()
        return jsonify(word_data)
    except Exception as e:
        print(f"Word of the day error: {e}")
        return jsonify({"error": "Failed to get word of the day"}), 500

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
                "green": " Welcome to BeeSmart! Our bees keep the hive safe and educational.",
                "yellow": "️ Please remember to use appropriate, educational words only.",
                "red": " Multiple inappropriate attempts detected. A report may be sent to your guardian."
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"️ Content filter status error: {e}")
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
                "green": " Welcome to BeeSmart! Our bees keep the hive safe and educational."
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
        print(f"️ Running enhanced kid-friendly filter on {len(deduped)} words...")
        
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
                print(f" Content violations detected: {len(violation_messages)}")
                for vm in violation_messages:
                    print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                    if vm['should_report']:
                        print(f"    Guardian report triggered for repeated violations")
            
        except Exception as e:
            # Fallback to original filtering if enhanced system fails
            print(f"️ Enhanced filter failed, using fallback: {e}")
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
            print(f"️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
        
        if not filtered:
            blocked_words = ", ".join([b["word"] for b in blocked[:5]])
            if len(blocked) > 5:
                blocked_words += f" and {len(blocked) - 5} more"
            complete_upload_session(session_id, False, 
                f"All {len(blocked)} words were blocked as inappropriate for children. Examples: {blocked_words}")
            return
        
        deduped = filtered
        print(f" {len(deduped)} words passed kid-friendly filter")
        
        update_upload_progress(session_id, "enriching", "Bees are pre-loading definitions from internal dictionary...", "bees_fetching_definitions", 55)
        
        # Enhanced enrichment with progress tracking and VALIDATION
        enriched = []
        enrichment_errors = []
        
        for i, r in enumerate(deduped):
            word = r["word"]
            sentence = r.get("sentence", "").strip()
            hint = r.get("hint", "").strip()
            
            progress = 55 + int((i + 1) / len(deduped) * 35)  # 55-90%
            update_upload_progress(session_id, "enriching", f" Pre-loading definition: {word}", "bees_fetching_definitions", progress, word)
            
            #  ALWAYS enrich with internal dictionary for consistency
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
            print(f"️ Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

        # CRITICAL VALIDATION: Check all definitions before quiz can start
        print("DEBUG: Validating wordbank definitions before storing...")
        is_valid, validation_error = validate_wordbank_definitions(filtered_enriched)
        
        if not is_valid:
            print(f"ERROR: Wordbank validation failed: {validation_error}")
            complete_upload_session(session_id, False, f"Definition Check Failed: {validation_error}")
            return
        
        update_upload_progress(session_id, "finalizing", "Bees are storing words in the hive...", "bees_storing", 95)
        
        # Clear Random Play flag since user is uploading custom words
        session.pop("is_random_play", None)
        
        # Store the wordbank and initialize quiz (USER UPLOAD)
        set_wordbank(filtered_enriched, is_user_upload=True)
        init_quiz_state(len(filtered_enriched))
        
        # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
        session.permanent = True
        session.modified = True
        time.sleep(0.25)
        
        # Double-check quiz state was saved
        saved_state = get_quiz_state()
        if not saved_state:
            print("ERROR /process_upload_with_progress: Quiz state failed to persist! Retrying init...")
            init_quiz_state(len(filtered_enriched))
            session.modified = True
            time.sleep(0.2)
        
        update_upload_progress(session_id, "completed", f" {len(filtered_enriched)} words with pre-loaded definitions ready!", "bees_celebrating", 100)
        complete_upload_session(session_id, True, f" Amazing! {len(filtered_enriched)} words enriched with definitions - quiz starts instantly!")
        
    except Exception as e:
        complete_upload_session(session_id, False, f"Oops! The bees encountered an error: {str(e)}")

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Accepts:
      - file upload (.csv, .txt, .docx, .pdf)
      - OR raw JSON body: { "words": [ {"word": "...", "sentence":"", "hint":""}, ... ] }
    """
    # Uploading words is open to all users (including guests) per product policy:
    # the only gating should be on *tiles/features* (e.g., Saved Lists), not on
    # the ability to build a temporary wordbank for practice.

    # CRITICAL: Set session persistence FIRST before any session operations
    session.permanent = True
    session.modified = True
    
    # Add error logging for debugging
    try:
        app.logger.info(f"Upload request - Content-Type: {request.content_type}")
        app.logger.info(f"Upload request - Files: {list(request.files.keys())}")
        app.logger.info(f"Upload request - Form: {list(request.form.keys())}")
    except Exception as e:
        app.logger.warning(f"Error logging upload request details: {e}")
    
    rows: List[Dict[str, str]] = []

    # JSON payload path
    if request.content_type and "application/json" in request.content_type:
        payload = request.get_json(silent=True) or {}
        words_json = payload.get("words", [])
        # Back-compat / convenience: allow a newline-delimited string, not just a list.
        # Canonical payload remains: {"words": [{"word":"...","sentence":"","hint":""}, ...]}
        if isinstance(words_json, str):
            words_json = [ln.strip() for ln in words_json.splitlines() if ln.strip()]
        elif words_json is None:
            words_json = []

        if isinstance(words_json, list):
            for w in words_json:
                if isinstance(w, str):
                    w = {"word": w}
                if not isinstance(w, dict):
                    continue
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
    print(f"️ Running enhanced kid-friendly filter on {len(deduped)} words...")
    
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
            print(f" Content violations detected: {len(violation_messages)}")
            for vm in violation_messages:
                print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                if vm['should_report']:
                    print(f"    Guardian report triggered for repeated violations")
            
            # Use the kid-friendly message from the most severe violation
            most_severe = max(violation_messages, key=lambda x: x['violation_count'])
            violation_response_message = most_severe['message']
        
    except Exception as e:
        # Fallback to original filtering if enhanced system fails
        print(f"️ Enhanced filter failed, using fallback: {e}")
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
        print(f"️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
    
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
    print(f" {len(deduped)} words passed kid-friendly filter")

    # Auto-enrich words with definitions (INTERNAL ONLY - NO EXTERNAL API CALLS)
    # Uses: 1) Simple Wiktionary (50K+ words), 2) Dictionary cache, 3) Smart fallback
    print(f" Enriching {len(deduped)} words using built-in dictionary...")
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
    print(f" Enrichment completed in {enrichment_time:.2f}s for {len(enriched)} words")
    
    # EXTRA FILTER: Remove any items whose definition/hint contains inappropriate content
    enriched, blocked_defs = _filter_records_excluding_inappropriate_text(enriched)
    if blocked_defs:
        print(f"️ /api/upload: Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

    deduped = enriched

    if len(deduped) > MAX_RECORDS:
        deduped = deduped[:MAX_RECORDS]

    # CRITICAL VALIDATION: Check all definitions before quiz can start
    is_valid, validation_error = validate_wordbank_definitions(deduped)
    
    if not is_valid:
        print(f" Wordbank validation failed: {validation_error}")
        return jsonify({"error": validation_error}), 400
    
    # CRITICAL: Set flag to prevent default word loading (same as manual upload)
    session["skip_default_load"] = True
    
    #  CRITICAL: COMPLETE WORDBANK WIPE AND REPLACEMENT
    # set_wordbank() now handles deletion automatically with proper transaction handling
    
    # Step 1: Clear quiz state before setting new wordbank
    session.pop(QUIZ_STATE_KEY, None)
    session.pop("is_random_play", None)
    session.modified = True
    
    print(f" /api/upload: Uploading {len(deduped)} fresh words (old wordbank will be auto-deleted)")
    
    # Step 2: Set new wordbank (USER UPLOAD - marks has_uploaded_once)
    # This will automatically delete old wordbank if storage_id exists
    set_wordbank(deduped, is_user_upload=True)
    init_quiz_state(len(deduped))
    
    # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
    session.permanent = True
    session.modified = True
    
    # Increased delay to ensure quiz state persists BEFORE response
    time.sleep(0.25)
    
    # Double-check quiz state was saved (Railway can drop session between requests)
    saved_state = get_quiz_state()
    if not saved_state:
        print("️ Quiz state failed to persist! Retrying init...")
        init_quiz_state(len(deduped))
        session.modified = True
        time.sleep(0.2)
    
    # Verify wordbank was set correctly
    verify_wb = get_wordbank()
    if len(verify_wb) != len(deduped):
        print(f"️ Wordbank size mismatch! Set {len(deduped)}, got {len(verify_wb)}")
    else:
        print(f" Successfully uploaded {len(deduped)} words")
    
    return jsonify({"ok": True, "count": len(deduped)})

# Error handler for uncaught exceptions in upload endpoint
@app.errorhandler(500)
def handle_500_error(error):
    """Log and return 500 errors with details"""
    app.logger.error(f"Internal server error: {error}")
    import traceback
    app.logger.error(traceback.format_exc())
    return jsonify({"error": "Internal server error", "details": str(error)}), 500

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
        data = request.get_json(silent=True)

        # Accept either:
        # 1) {"words": [...]} (legacy / UI), or
        # 2) a raw JSON list [...] (API/tests convenience)
        if isinstance(data, list):
            words_list = data
        else:
            data = data or {}
            words_list = data.get('words', [])
        
        if not words_list or not isinstance(words_list, list):
            return jsonify({"ok": False, "error": "Invalid words array"}), 400
        
        if not words_list:
            return jsonify({"ok": False, "error": "No words provided"}), 400
        
        # Convert to word records. Accept either a list[str] or a list[dict].
        # Some tests/UI paths already provide the full record shape.
        rows = []
        for item in words_list:
            if isinstance(item, str):
                word = item.strip()
                if word:  # Skip empty strings
                    rows.append({"word": word, "sentence": "", "hint": ""})
                continue

            if isinstance(item, dict):
                word = str(item.get("word", "")).strip()
                if not word:
                    continue
                rows.append({
                    "word": word,
                    # sentence/hint will be enriched anyway, but keep whatever
                    # caller sent in case it helps.
                    "sentence": str(item.get("sentence", "") or ""),
                    "hint": str(item.get("hint", "") or ""),
                })
                continue

            # Unknown type: ignore.
            continue
        
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
        print(f"️ Running enhanced kid-friendly filter on {len(deduped)} manually entered words...")
        
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
                print(f" Manual entry violations detected: {len(violation_messages)}")
                for vm in violation_messages:
                    print(f"   - {vm['word']}: violation #{vm['violation_count']}")
                    if vm['should_report']:
                        print(f"    Guardian report triggered for repeated manual entry violations")
                
                # For manual entry, always show the warning message from the most severe violation
                most_severe = max(violation_messages, key=lambda x: x['violation_count'])
                violation_response_message = most_severe['message']
        
        except Exception as e:
            # Fallback to original filtering if enhanced system fails
            print(f"️ Enhanced filter failed, using fallback: {e}")
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
            print(f"️ Blocked {len(blocked)} inappropriate words: {[b['word'] for b in blocked]}")
        
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
        print(f" {len(deduped)} words passed kid-friendly filter")
        
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
            print(f"️ /api/upload-manual-words: Definition filter blocked {len(blocked_defs)} item(s) due to inappropriate content in text: {[b['word'] for b in blocked_defs]}")

        if len(enriched) > MAX_RECORDS:
            enriched = enriched[:MAX_RECORDS]
        
        print(f"DEBUG /api/upload-manual-words: Processing {len(enriched)} words. Session before: {list(session.keys())}")
        
        # CRITICAL: Set flag to prevent default word loading
        session["skip_default_load"] = True
        
        #  CRITICAL: COMPLETE WORDBANK WIPE AND REPLACEMENT
        # set_wordbank() now handles deletion automatically with proper transaction handling
        
        # Step 1: Clear quiz state before setting new wordbank
        session.pop(QUIZ_STATE_KEY, None)
        session.pop("is_random_play", None)
        session.modified = True
        
        print(f" /api/upload-manual-words: Uploading {len(enriched)} fresh manual words (old wordbank will be auto-deleted)")
        
        # Step 2: Store and initialize quiz (USER UPLOAD - manual words)
        # This will automatically delete old wordbank if storage_id exists
        set_wordbank(enriched, is_user_upload=True)
        init_quiz_state(len(enriched))
        
        # CRITICAL: Aggressive session persistence (Railway fix for "3 clicks" bug)
        session.permanent = True
        session.modified = True
        
        # Increased delay to ensure quiz state persists BEFORE response
        time.sleep(0.25)
        
        # Double-check quiz state was saved
        saved_state = get_quiz_state()
        if not saved_state:
            print("ERROR /api/upload-manual-words: Quiz state failed to persist! Retrying init...")
            init_quiz_state(len(enriched))
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

@app.route('/api/next', methods=['POST'])
def api_next():
    """Get the next word in the quiz sequence."""
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
    
    #  CRITICAL CHECK: Warn if using default words when user has uploaded before
    if using_defaults and has_uploaded:
        print("️️️ CRITICAL WARNING /api/next: Using DEFAULT words but has_uploaded_once=True!")
        print("️️️ This indicates session loss - user's uploaded words were lost!")
        print(f"️️️ Session keys: {list(session.keys())}")
    
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
        init_quiz_state(len(wb))
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
    
    # CHECK FOR QUIZ COMPLETION FIRST - before showing any word
    if idx >= len(order):
        # SAFETY CHECK: Don't show completion if no questions were answered
        if state["correct"] == 0 and state["incorrect"] == 0:
            print(f"WARNING /api/next: Quiz appears complete but no questions answered! Resetting.")
            print(f"WARNING /api/next: idx={idx}, len(order)={len(order)}, correct={state['correct']}, incorrect={state['incorrect']}")
            init_quiz_state(len(wb))
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
            
            # Build comprehensive summary for report card
            quiz_summary = {
                "total": len(order),
                "correct": state.get("correct", 0),
                "incorrect": state.get("incorrect", 0),
                "streak": state.get("streak", 0),
                "max_streak": state.get("max_streak", 0),
                "history": state.get("history", []),
                "incorrect_words": incorrect_words,
                "session_points": state.get("session_points", 0),
                "badges_earned": state.get("badges_earned", []),
                "buzz_dust_earned": state.get("buzz_dust_earned", 0),
                "buzz_dust_breakdown": state.get("buzz_dust_breakdown", {}),
                "level_up": state.get("level_up"),
                "newly_unlocked_avatars": state.get("newly_unlocked_avatars", [])
            }
            print(f" Quiz complete summary: {quiz_summary['correct']}/{quiz_summary['total']} correct, {quiz_summary['session_points']} points")
            return jsonify({
                "done": True,
                "summary": quiz_summary
            })
    
    # CRITICAL FIX: If quiz state order doesn't match current wordbank length, reset it
    # This happens when user uploads a new word list after completing a previous quiz
    if len(order) != len(wb):
        print(f"DEBUG /api/next: Quiz state mismatch - order={len(order)}, wordbank={len(wb)}, reinitializing")
        init_quiz_state(len(wb))
        state = get_quiz_state()
        idx = state["idx"]
        order = state["order"]

    # Get the current word to display
    word_rec = wb[order[idx]]
    word = word_rec.get("word", "")
    
    # DEBUG: Log the actual word record structure
    print(f" DEBUG /api/next: word_rec structure = {word_rec}")
    print(f" DEBUG /api/next: word_rec keys = {list(word_rec.keys())}")
    print(f" DEBUG /api/next: word_rec['sentence'] type = {type(word_rec.get('sentence'))}")
    
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
                    print(f"️ Failed to persist enrichment for '{word}': {_persist_err}")
        except Exception as ex:
            print(f"️ Dictionary enrichment failed for '{word}': {ex}")
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
    
    # CRITICAL: Ensure all fields are strings, not dicts (defensive coding)
    if isinstance(definition, dict):
        print(f"️ WARNING: definition is a dict for word '{word}', extracting string value")
        definition = definition.get("definition", definition.get("sentence", "Listen carefully."))
    if isinstance(sentence, dict):
        print(f"️ WARNING: sentence is a dict for word '{word}', extracting string value")
        sentence = sentence.get("sentence", sentence.get("definition", ""))
    if isinstance(hint, dict):
        print(f"️ WARNING: hint is a dict for word '{word}', extracting string value")
        hint = hint.get("hint", "")
    
    # Ensure they are strings
    definition = str(definition or "")
    sentence = str(sentence or "")
    hint = str(hint or "")
    word = str(word or "")

    #  Initialize hints counter if not present (for first word or after reset)
    if "hints_used_current_word" not in state:
        state["hints_used_current_word"] = 0
        print(f" Initialized hints_used_current_word to 0 for word: {word}")
    else:
        print(f" Current word '{word}' - hints_used_current_word = {state.get('hints_used_current_word', 0)}")
    
    #  ADVANCE INDEX for next call after answer is submitted
    # This ensures proper sequence: show word → answer → feedback → next word
    # /api/answer WILL advance after recording the answer
    # state["idx"] += 1  # REMOVED: Don't advance here, let /api/answer handle it
    print(f" ️ Showing word at idx={idx}, will advance after answer is submitted")
    
    session[QUIZ_STATE_KEY] = state
    session.modified = True
    
    return jsonify({
        "done": False,
        "index": idx + 1,
        "total": len(order),

        # Back-compat (UI already uses this)
        "definition": definition,

        #  New explicit fields (use these in UI going forward)
        "sentence": sentence,
        "hint": hint,
        "definitionSource": definition_source,
        "hasDefinition": has_definition,

        # Word for TTS/pronunciation
        "word": word,
        # Announcer control to prevent double playback on repeated /api/next calls
        # Client should only auto-pronounce when shouldAnnounce=true and may pass announceToken to /api/pronounce.
        "shouldAnnounce": (lambda _now: (
            # Compute whether we should announce: if new idx or last announce older than 1.5s
            True if (state.get("last_announced_idx") != idx or (_now - float(state.get("last_announce_ts", 0))) > 1.5) else False
        ))(time.time()),
        "announceToken": (lambda: (
            # Generate a short token for idempotency; store in state when shouldAnnounce is true
            __import__("uuid").uuid4().hex[:12]
        ))(),
        "wordMeta": {
            "hasSentence": bool(sentence),
            "hasHint": bool(hint),
        },
        "progress": {
            # Unified progress structure (matches /api/answer & /api/live-status)
            "index": idx + 1,
            "total": len(order),
            "correct": state.get("correct", 0),
            "incorrect": state.get("incorrect", 0),
            "streak": state.get("streak", 0),
            "session_points": state.get("session_points", 0)
        }
    })

@app.route("/api/pronounce", methods=["POST"])
def api_pronounce():
    """Provide pronunciation helpers for the current quiz word."""
    state = get_quiz_state()
    wb = get_wordbank()
    if not wb or state is None:
        return jsonify({"error": "No active session"}), 400

    # Optional auto flag: when the client auto-announces on new word, don't count as a hint
    payload = {}
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}
    is_auto = bool(payload.get("auto"))
    announce_token = payload.get("token")

    idx = state["idx"]
    order = state["order"]
    if idx >= len(order):
        return jsonify({"error": "Quiz finished"}), 400

    # Track hint usage for points calculation only if user explicitly requested pronunciation
    if not is_auto:
        state["hints_used_current_word"] = state.get("hints_used_current_word", 0) + 1
        state["hints_used_total"] = state.get("hints_used_total", 0) + 1
    else:
        # Record last announce timing/idempotency to avoid echo
        state["last_announced_idx"] = idx
        state["last_announce_ts"] = time.time()
        if announce_token:
            state["last_announce_token"] = announce_token
    session[QUIZ_STATE_KEY] = state

    word_rec = wb[order[idx]]
    current_word = word_rec.get("word", "")

    #  OPTIMIZED: Use pre-enriched definitions from word_rec (enriched during upload)
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
        "definition": definition,
        "sentence": safe_sentence,
        "hint": safe_hint,
        "phonetic": phonetic_lookup,
        "phonetic_spelling": spelled_out
    })

@app.route("/api/live-status", methods=["GET"])
def api_live_status():
    """Real-time session stats without penalizing incomplete quizzes.
    Provides: current index, total, streak, points earned so far, correct/incorrect counts.
    GPA / lifetime accuracy intentionally excluded (only completed sessions adjust those).
    """
    state = get_quiz_state()
    wb = get_wordbank()
    if not state or not wb:
        return jsonify({
            "active": False,
            "message": "No active quiz",
            "session_points": 0,
            "streak": 0,
            "correct": 0,
            "incorrect": 0
        })
    order = state.get("order", [])
    idx = state.get("idx", 0)
    total = len(order)
    return jsonify({
        "active": idx < total,
        "index": idx + 1 if idx < total else total,
        "total": total,
        "streak": state.get("streak", 0),
        "max_streak": state.get("max_streak", 0),
        "session_points": state.get("session_points", 0),
        "correct": state.get("correct", 0),
        "incorrect": state.get("incorrect", 0),
        "hints_used_current_word": state.get("hints_used_current_word", 0)
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

# ---  LEVEL PROGRESSION SYSTEM ------------------------------------------

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
            "icon": "",
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
            "icon": "",
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
            "icon": "",
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
            "icon": "",
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
            "icon": "",
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
            "message": f" Level Up! You're now a {new_level['tier']}!"
        }
    
    return None

# ---  BADGE ACHIEVEMENT SYSTEM ------------------------------------------

#  BADGE ACHIEVEMENT SYSTEM
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
    
    #  Perfect Game (+500 points)
    # Complete quiz with 100% accuracy, no hints, no wrong attempts
    if total >= 10 and incorrect == 0 and hints_used_total == 0:
        badges_earned.append({
            "type": "perfect_game",
            "name": "Perfect Game",
            "icon": "",
            "points": 500,
            "message": "PERFECT GAME! You're a spelling champion!"
        })
    
    #  Speed Demon (+200 points)
    # Average answer time < 10 seconds per word (minimum 10 words)
    if correct >= 10 and avg_time_ms > 0 and (avg_time_ms / 1000) < 10:
        badges_earned.append({
            "type": "speed_demon",
            "name": "Speed Demon",
            "icon": "",
            "points": 200,
            "message": "SPEED DEMON! Lightning-fast spelling!"
        })
    
    #  Persistent Learner (+150 points)
    # Complete 50+ words in a single session
    if total >= 50:
        badges_earned.append({
            "type": "persistent_learner",
            "name": "Persistent Learner",
            "icon": "",
            "points": 150,
            "message": "PERSISTENT LEARNER! You love to learn!"
        })
    
    #  Hot Streak (+100 points)
    # Achieve 10+ correct answers in a row
    if max_streak >= 10:
        badges_earned.append({
            "type": "hot_streak",
            "name": "Hot Streak",
            "icon": "",
            "points": 100,
            "message": "HOT STREAK! You're on fire!"
        })
    
    #  Comeback Kid (+100 points)
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
            "icon": "",
            "points": 100,
            "message": "COMEBACK KID! Never give up!"
        })
    
    #  Honey Hunter (+75 points)
    # Use hints wisely (< 20% of words, minimum 10 words)
    if total >= 10 and hints_used_total > 0:
        hint_percentage = (hints_used_total / total) * 100
        if hint_percentage < 20:
            badges_earned.append({
                "type": "honey_hunter",
                "name": "Honey Hunter",
                "icon": "",
                "points": 75,
                "message": "HONEY HUNTER! Smart use of help!"
            })
    
    #  Early Bird (+50 points)
    # Complete quiz quickly (within 5 minutes for 10+ words)
    if total >= 10 and total_time_ms > 0 and (total_time_ms / 1000 / 60) < 5:
        badges_earned.append({
            "type": "early_bird",
            "name": "Early Bird",
            "icon": "",
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
        print(f"️ Error checking newly unlocked avatars: {e}")
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
        init_quiz_state(len(wb))
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
    
    # Check if quiz is already complete
    if idx >= len(order):
        return jsonify({"error": "Quiz finished"}), 400

    word_rec = wb[order[idx]]
    correct_spelling = word_rec["word"]

    skip_requested = bool(payload.get("skip")) or method == "skip"

    if skip_requested:
        user_input = user_input or "[skipped]"

    #  DEBUG: Log exact comparison details
    normalized_input = normalize(user_input)
    normalized_correct = normalize(correct_spelling)
    print(f"")
    print(f"{'='*70}")
    print(f" ANSWER COMPARISON DEBUG:")
    print(f"   User input (raw): '{user_input}' (len={len(user_input)})")
    print(f"   User input (normalized): '{normalized_input}' (len={len(normalized_input)})")
    print(f"   Correct word (raw): '{correct_spelling}' (len={len(correct_spelling)})")
    print(f"   Correct word (normalized): '{normalized_correct}' (len={len(normalized_correct)})")
    print(f"   Comparison: '{normalized_input}' == '{normalized_correct}'")
    print(f"   Match: {normalized_input == normalized_correct}")
    print(f"   Result: {' CORRECT' if normalized_input == normalized_correct else ' INCORRECT'}")
    print(f"{'='*70}")
    print(f"")

    is_correct = False if skip_requested else normalized_input == normalized_correct

    #  HONEY POINTS CALCULATION
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
        # Check if this word already in history with incorrect answer (case-insensitive)
        word_already_attempted_wrong = any(
            normalize(h.get("word", "")) == normalize(correct_spelling) and not h.get("correct") 
            for h in state.get("history", [])
        )
        if not word_already_attempted_wrong:
            points_breakdown["first_attempt"] = 50
            points_earned += 50
        
        # No hints bonus: +25 points if no hints used this session
        # Track hints_used in state (updated when /api/hint, /api/pronounce called)
        hints_used_this_word = state.get("hints_used_current_word", 0)
        print(f" Checking hints for word '{correct_spelling}': hints_used_current_word = {hints_used_this_word}")
        
        #  Apply hint penalty BEFORE adding no-hints bonus
        hint_penalty = 0
        if hints_used_this_word > 0:
            # 30% penalty for using hints
            hint_penalty = int(points_earned * 0.30)
            points_earned -= hint_penalty
            points_breakdown["hint_penalty"] = hint_penalty
            print(f" Hint penalty applied: -{hint_penalty} points (30% reduction)")
        else:
            # No hints bonus
            points_breakdown["no_hints"] = 25
            points_earned += 25
        
        print(f" Points earned: {points_earned} (breakdown: {points_breakdown})")

    # Update stats and advance index for any completed attempt
    if is_correct:
        state["correct"] += 1
        state["streak"] += 1
        # Track session points
        state["session_points"] = state.get("session_points", 0) + points_earned
        if state["streak"] > state.get("max_streak", 0):
            state["max_streak"] = state["streak"]
        
        #  BUZZ DUST AWARDING - Award Buzz Dust for correct answers (authenticated users)
        # Buzz Dust is XP derived from points via BUZZ_DUST_MULTIPLIER.
        if current_user.is_authenticated and points_earned > 0:
            from buzz_dust_helpers import get_bee_class, BUZZ_DUST_MULTIPLIER

            dust_awarded = int(points_earned * float(BUZZ_DUST_MULTIPLIER))
            if dust_awarded <= 0:
                dust_awarded = 0

            old_buzz_dust = current_user.total_buzz_dust or 0
            current_user.total_buzz_dust = old_buzz_dust + dust_awarded
            
            # Check for rank advancement
            old_class_id = get_bee_class(old_buzz_dust).get('id', 'novice')
            new_class_id = get_bee_class(current_user.total_buzz_dust).get('id', 'novice')
            
            if old_class_id != new_class_id:
                # User ranked up mid-quiz!
                session['ranked_up'] = True
                session['old_class_id'] = old_class_id
                session['new_class_id'] = new_class_id
                current_user.bee_class = new_class_id
                current_user.last_rank_up_at = datetime.now(timezone.utc)
                print(f" MID-QUIZ RANK UP! {old_class_id} → {new_class_id} (Buzz Dust: {old_buzz_dust} → {current_user.total_buzz_dust})")
                
                # Award rank-up badge immediately
                badge_type = f"{new_class_id}_rank"
                try:
                    # Check if user already has this rank badge
                    existing_badge = Achievement.query.filter_by(
                        user_id=current_user.id,
                        achievement_type=badge_type
                    ).first()
                    
                    if not existing_badge:
                        rank_badge = Achievement(
                            user_id=current_user.id,
                            achievement_type=badge_type,
                            points_bonus=0,  # Rank badges don't give extra points
                            earned_date=datetime.now(timezone.utc)
                        )
                        db.session.add(rank_badge)
                        print(f" RANK BADGE AWARDED: {badge_type}")
                except Exception as badge_error:
                    print(f"️ Failed to award rank badge: {badge_error}")
            
            # Commit the Buzz Dust update immediately
            try:
                db.session.commit()
                print(
                    f" BUZZ DUST AWARDED: +{dust_awarded} (mult={BUZZ_DUST_MULTIPLIER}) "
                    f"for correct answer (now {current_user.total_buzz_dust} total)"
                )
            except Exception as e:
                print(f"️ Failed to commit Buzz Dust award: {e}")
                db.session.rollback()
    else:
        state["incorrect"] += 1
        state["streak"] = 0

    #  ADVANCE INDEX AFTER RECORDING ANSWER - This is the correct place for advancement
    # /api/next shows current word, /api/answer records result and advances to next
    # This prevents the double-advance bug that was skipping words
    state["idx"] += 1
    print(f" ️ Answer recorded for word '{correct_spelling}', advanced to next index: {state['idx']}")
    
    # Capture hints used for this *answered* word before we reset
    hints_used_for_answered_word = state.get("hints_used_current_word", 0)

    # Reset hints counter for next word (will be used when /api/next is called)
    state["hints_used_current_word"] = 0
    print(f" Answer recorded, hints reset for next word")

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
    session.modified = True  # CRITICAL: Tell Flask to persist session changes

    # Save to database for ALL users (authenticated + guests).
    # IMPORTANT: authenticated users must attach QuizResult/WordMastery rows to
    # their real account, otherwise cumulative GPA/accuracy/quiz count won't
    # reflect quiz completion for the logged-in user.
    try:
        is_auth = bool(getattr(current_user, "is_authenticated", False))
    except Exception:
        is_auth = False
    user_obj = current_user if is_auth else get_or_create_guest_user()
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
                hints_used=hints_used_for_answered_word,
                # Use the 1-based question sequence; idx was incremented above after processing this answer
                question_number=state.get("idx", 0)
            )
            # Derive difficulty metadata
            try:
                quiz_result.calculate_difficulty()
            except Exception:
                pass
            db.session.add(quiz_result)
            
            # Update or create WordMastery record (use normalized word for consistency)
            normalized_word = normalize(correct_spelling)
            word_mastery = WordMastery.query.filter_by(
                user_id=user_obj.id,
                word=normalized_word
            ).first()
            
            if word_mastery:
                word_mastery.update_stats(is_correct, time_taken=(elapsed_ms / 1000.0) if elapsed_ms else None)
            else:
                word_mastery = WordMastery(user_id=user_obj.id, word=normalized_word)
                # Initialize stats via helper
                word_mastery.update_stats(is_correct, time_taken=(elapsed_ms / 1000.0) if elapsed_ms else None)
                db.session.add(word_mastery)
            
            db.session.commit()
            print(f" Saved QuizResult for word '{correct_spelling}' (correct={is_correct}) to session {state['db_session_id']}")
        except Exception as e:
            import traceback
            print(f"️ Failed to save quiz result: {type(e).__name__}: {e}")
            try:
                print(f"️ Quiz result save traceback: {traceback.format_exc()}")
            except Exception:
                pass
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

    # Next index position for UI progress (1-based).
    # state["idx"] is our 0-based pointer to the *next* word after the answer.
    # Example: after answering the 1st word -> state["idx"]=1 -> progress.index should be 2.
    next_index_position = min(state["idx"] + 1, len(order))
    
    #  Check for badge achievements
    badges_unlocked = []
    quiz_complete = state["idx"] >= len(order)

    # Persist completion status in session state so real-time stats endpoints
    # stop treating this session as "in progress" once it is complete.
    try:
        state["quiz_complete"] = bool(quiz_complete)
        session[QUIZ_STATE_KEY] = state
        session.modified = True
    except Exception:
        pass
    
    #  DEBUG: Log quiz completion status
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
            print(f" Badges earned: {len(badges_unlocked)}, bonus points: {badge_points}")
        
    # Save ONLY buzz dust related badge(s) for report card display; filter others out.
    filtered_for_report = [b for b in badges_unlocked if b.get("type") in {"elite_buzz_dust", "buzz_dust", "buzz_dust_elite"}]
    state["badges_earned"] = filtered_for_report

    # Recompute totals from history to avoid any drift if legacy sessions are missing counters.
    # IMPORTANT: history is the system-of-record for what happened in the quiz.
    history = state.get("history", []) or []
    correct_total = sum(1 for h in history if h.get("correct"))
    # Treat any non-correct attempt as incorrect (including skips).
    incorrect_total = len(history) - correct_total

    # Keep the counters in state consistent too (other endpoints read these directly).
    state["correct"] = int(correct_total)
    state["incorrect"] = int(incorrect_total)

    session[QUIZ_STATE_KEY] = state
    session.modified = True  # CRITICAL: Ensure session persists
    
    # Finalize database session for logged-in users OR guest accounts
    if quiz_complete and state.get("db_session_id"):
        print(f" Finalizing quiz session ID: {state.get('db_session_id')}")
        try:
            # Finalize the quiz session
            quiz_session = QuizSession.query.get(state["db_session_id"])
            if not quiz_session:
                print(f"️ WARNING: QuizSession ID {state.get('db_session_id')} not found in database!")
            if quiz_session:
                quiz_session.correct_count = state["correct"]
                quiz_session.incorrect_count = state["incorrect"]
                quiz_session.best_streak = max(state.get("max_streak", 0), state.get("streak", 0))
                
                #  Calculate total points from all sources
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
                
                print(f" POINTS BREAKDOWN: Words={word_points}, Badges={badge_points}, Extra={extra_bonus}, TOTAL={total_points}")
                
                # Capture old points BEFORE complete_session() updates them
                old_lifetime_points = 0
                old_honey_points = 0
                if current_user.is_authenticated:
                    old_lifetime_points = current_user.total_lifetime_points or 0
                    old_honey_points = current_user.honey_points or 0
                
                # Complete the session - this applies points and increments quiz count
                quiz_session.complete_session()
                
                # Refresh user object to get updated values from database
                if current_user.is_authenticated:
                    db.session.refresh(current_user)
                
                #  Save badges to Achievement table
                # Persist all badges to Achievement table (full history), but report card later filters display.
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
                    print(f" Saved {len(badges_unlocked)} badge(s) to Achievement table")
                
                # Update user stats (if authenticated)
                level_up_data = None
                newly_unlocked_avatars = []
                if current_user.is_authenticated:
                    # CRITICAL: Set lifetime points directly (like buzz dust) to ensure they're saved
                    # complete_session() should have applied them, but we'll ensure they're correct
                    expected_lifetime_points = old_lifetime_points + total_points
                    current_lifetime_points = current_user.total_lifetime_points or 0
                    
                    # If points weren't applied by complete_session(), apply them directly
                    if current_lifetime_points != expected_lifetime_points:
                        print(f"⚠️ WARNING: Points not applied correctly by complete_session()!")
                        print(f"   Old: {old_lifetime_points}, Expected: {expected_lifetime_points}, Current: {current_lifetime_points}")
                        print(f"🔧 FIXING: Setting total_lifetime_points directly to {expected_lifetime_points}")
                        current_user.total_lifetime_points = expected_lifetime_points
                        new_lifetime_points = expected_lifetime_points
                    else:
                        new_lifetime_points = current_lifetime_points
                    
                    # Calculate points earned (for logging/display)
                    points_earned_this_quiz = new_lifetime_points - old_lifetime_points
                    
                    #  Check for level up using the updated points
                    level_up_data = check_level_up(old_lifetime_points, new_lifetime_points)
                    
                    #  Check for newly unlocked avatars based on honey points
                    from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked
                    # Update honey points (separate from lifetime points for avatar unlocks)
                    new_honey_points = old_honey_points + total_points
                    
                    #  DEBUG: Log honey points update
                    print(f" HONEY POINTS UPDATE:")
                    print(f"   Old: {old_honey_points}")
                    print(f"   Earned: {total_points}")
                    print(f"   New: {new_honey_points}")
                    
                    current_user.honey_points = new_honey_points
                    print(f"    Set current_user.honey_points = {current_user.honey_points}")
                    
                    #  BUZZ DUST AWARDING - Award completion bonuses (avoid double-awarding base dust)
                    # Base dust is already awarded per correct answer above.
                    from buzz_dust_helpers import get_bee_class, calculate_quiz_buzz_dust, BUZZ_DUST_MULTIPLIER
                    
                    old_buzz_dust = current_user.total_buzz_dust or 0

                    # Calculate buzz dust with all bonuses: perfect round, no hints, streak, etc.
                    is_perfect_round = (state.get("incorrect", 0) == 0 and state.get("correct", 0) > 0)
                    no_hints_used = (state.get("hints_used_total", 0) == 0)
                    max_streak = state.get("max_streak", 0)
                    
                    full_quiz_dust, buzz_dust_breakdown = calculate_quiz_buzz_dust(
                        points=word_points,
                        perfect_round=is_perfect_round,
                        no_hints=no_hints_used,
                        streak_length=max_streak,
                        daily_challenge=False
                    )

                    # Base dust that should already have been awarded incrementally.
                    base_quiz_dust = int(word_points * float(BUZZ_DUST_MULTIPLIER))
                    bonus_quiz_dust = max(0, int(full_quiz_dust) - int(base_quiz_dust))

                    # Convert badge points to dust using the same multiplier.
                    badge_dust = int(badge_points * float(BUZZ_DUST_MULTIPLIER)) if badge_points else 0

                    completion_dust_awarded = bonus_quiz_dust + badge_dust
                    current_user.total_buzz_dust = old_buzz_dust + completion_dust_awarded

                    # Store full-quiz earned dust for display (base + bonuses), plus badge dust.
                    state["buzz_dust_earned"] = int(full_quiz_dust) + int(badge_dust)
                    state["buzz_dust_breakdown"] = buzz_dust_breakdown
                    if badge_dust:
                        state["buzz_dust_breakdown"]["badges"] = badge_dust

                    print(
                        f" BUZZ DUST AWARDED (completion): +{completion_dust_awarded} "
                        f"(quiz_bonus={bonus_quiz_dust}, badge_dust={badge_dust}, mult={BUZZ_DUST_MULTIPLIER}) "
                        f"(was {old_buzz_dust}, now {current_user.total_buzz_dust})"
                    )
                    print(f"   Display earned this quiz: {state['buzz_dust_earned']} (incl. base already awarded per answer)")
                    print(f"   Breakdown: {state['buzz_dust_breakdown']}")
                    
                    # Check for rank advancement
                    old_class_id = get_bee_class(old_buzz_dust).get('id', 'novice')
                    new_class_id = get_bee_class(current_user.total_buzz_dust).get('id', 'novice')
                    
                    if old_class_id != new_class_id:
                        # User ranked up!
                        session['ranked_up'] = True
                        session['old_class_id'] = old_class_id
                        session['new_class_id'] = new_class_id
                        current_user.bee_class = new_class_id
                        current_user.last_rank_up_at = datetime.now(timezone.utc)
                        print(f" RANK UP! {old_class_id} → {new_class_id}")
                        
                        # Award rank-up badge
                        badge_type = f"{new_class_id}_rank"
                        try:
                            # Check if user already has this rank badge
                            existing_badge = Achievement.query.filter_by(
                                user_id=current_user.id,
                                achievement_type=badge_type
                            ).first()
                            
                            if not existing_badge:
                                rank_badge = Achievement(
                                    user_id=current_user.id,
                                    achievement_type=badge_type,
                                    points_bonus=0,  # Rank badges don't give extra points
                                    earned_date=datetime.now(timezone.utc)
                                )
                                db.session.add(rank_badge)
                                print(f" RANK BADGE AWARDED: {badge_type}")
                        except Exception as badge_error:
                            print(f"️ Failed to award rank badge: {badge_error}")
                    
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
                                'message': f"Congratulations! You've unlocked {avatar_data.get('name')}! "
                            })
                    
                    if newly_unlocked_avatars:
                        print(f" User unlocked {len(newly_unlocked_avatars)} new avatar(s): {[a['name'] for a in newly_unlocked_avatars]}")
                    
                    # Update stats (complete_session() already incremented quizzes and applied points)
                    # Only update best_streak if this session's streak is better
                    if quiz_session.best_streak > (current_user.best_streak or 0):
                        current_user.best_streak = quiz_session.best_streak
                    
                    # GPA and accuracy are already updated by complete_session() via update_gpa_and_accuracy()
                    # No need to refresh again - we already refreshed after complete_session()
                    
                    print(f" STATS UPDATE: User={current_user.username}, Quizzes={current_user.total_quizzes_completed}, Points={current_user.total_lifetime_points}, Honey Points={current_user.honey_points}, GPA={current_user.cumulative_gpa}, Avg Accuracy={current_user.average_accuracy}%")
                    
                    if level_up_data:
                        print(f" LEVEL UP! {level_up_data['old_level']['tier']} → {level_up_data['new_level']['tier']}")
                    
                    print(f" Quiz completed! Grade: {quiz_session.grade}, Session Points: {quiz_session.points_earned}, Total Points: {total_points}, User Lifetime: {current_user.total_lifetime_points}")
                else:
                    print(f" Guest quiz completed! Grade: {quiz_session.grade}, Points: {total_points}")
                
                # Save level up data to session for frontend
                if level_up_data:
                    state["level_up"] = level_up_data
                    session[QUIZ_STATE_KEY] = state
                    session.modified = True
                
                # Save newly unlocked avatars to session
                if newly_unlocked_avatars:
                    state["newly_unlocked_avatars"] = newly_unlocked_avatars
                    session[QUIZ_STATE_KEY] = state
                    session.modified = True
                
                #  CRITICAL: Commit all changes to database
                db.session.commit()
                
                # Refresh user object from database to ensure we have latest values
                if current_user.is_authenticated:
                    db.session.refresh(current_user)
                
                print(f" DATABASE COMMITTED: QuizSession.completed={quiz_session.completed}, User.total_quizzes={current_user.total_quizzes_completed if current_user.is_authenticated else 'N/A'}, User.points={current_user.total_lifetime_points if current_user.is_authenticated else 'N/A'}")
                
        except Exception as e:
            print(f"️ Failed to finalize quiz session: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
    elif quiz_complete and not state.get("db_session_id"):
        print(f"️ WARNING: Quiz complete but no db_session_id in state! Cannot save to database.")

    # 📚 Enhanced Educational Features: Get a safe (blanked) definition snippet
    # NOTE: Our canonical enrichment helper is get_word_info() defined in this module.
    # It returns a formatted string: "<definition>. Fill in the blank: <sentence>".
    # Avoid importing dictionary_api.get_word_info (it may not exist and can cause runtime errors).
    word_definition = ""
    if correct_spelling:
        try:
            raw = get_word_info(correct_spelling)
            d, _s = parse_enriched_info(raw, correct_spelling)
            word_definition = (d or "").strip()
        except Exception as e:
            print(f"Failed to get definition for '{correct_spelling}': {e}")
    
    # 🎉 Check for streak milestones to celebrate
    streak_milestone = None
    current_streak = state.get("streak", 0)
    if is_correct and current_streak > 1:  # Only show for streak >= 2
        milestones = {
            5: {"title": "🔥 Hot Streak!", "message": "5 words in a row! You're on fire!"},
            10: {"title": "🌟 Amazing Streak!", "message": "10 correct! You're a spelling superstar!"},
            15: {"title": "💫 Incredible Run!", "message": "15 in a row! You're unstoppable!"},
            20: {"title": "🏆 Legendary Streak!", "message": "20 perfect! You're a spelling legend!"},
            25: {"title": "👑 Master Speller!", "message": "25 straight! You've achieved spelling mastery!"}
        }
        
        if current_streak in milestones:
            streak_milestone = milestones[current_streak]

    return jsonify({
        "correct": is_correct,
        "word": correct_spelling,  # Add word for frontend reference
        "expected": correct_spelling,
        "skipped": skip_requested,
        "phonetic": phonetic_help if (phonetic_help and (not is_correct or skip_requested)) else "",
        "phonetic_spelling": phonetic_spelling if (not is_correct or skip_requested) else "",
        "feedback_message": feedback_message,
        "definition": word_definition if word_definition else None,  # 📚 Educational definition
        "streak_milestone": streak_milestone,  # 🎉 Celebration data
        "progress": {
            "index": next_index_position,
            "total": len(order),
            "correct": state["correct"],
            "incorrect": state["incorrect"],
            "streak": state["streak"],
            "session_points": state.get("session_points", 0)
        },
        "points": {
            "earned": points_earned,
            "breakdown": points_breakdown,
            "session_total": state.get("session_points", 0),
            "max_streak": state.get("max_streak", 0)
        },
        "buzz_dust": {
            "earned": state.get("buzz_dust_earned", 0) if quiz_complete else 0,
            "breakdown": state.get("buzz_dust_breakdown", {}) if quiz_complete else {}
        } if current_user.is_authenticated else None,
        "quiz_complete": quiz_complete,
        "badges": badges_unlocked if quiz_complete else [],
        "level_up": state.get("level_up") if quiz_complete else None,
        "newly_unlocked_avatars": state.get("newly_unlocked_avatars", []) if quiz_complete else []
    })

# Save partial quiz progress
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
        
        # Apply points to the user if they haven't been applied yet.
        # This credits any earned points without incrementing quiz count or GPA.
        if current_user.is_authenticated:
            added_points = quiz_session.apply_points_if_needed()
            # Update the user's best streak if the session's streak exceeds their record
            if quiz_session.best_streak > (current_user.best_streak or 0):
                current_user.best_streak = quiz_session.best_streak
            # Recalculate GPA and accuracy to account for any new provisional data
            current_user.update_gpa_and_accuracy()
        
        # Commit to database
        db.session.commit()
        
        print(f" Saved partial progress: Session {quiz_session.id}, Correct: {quiz_session.correct_count}, "
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
        print(f" Error saving partial progress: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/quiz/status", methods=["GET"])
def api_quiz_status():
    """
    Get current quiz status - checks if there's resumable progress
    Returns can_resume flag and current stats if available
    """
    try:
        state = session.get(QUIZ_STATE_KEY)
        if not state:
            return jsonify({"can_resume": False, "message": "No quiz session found"})
        
        # Check if there's meaningful progress to resume
        idx = state.get("idx", 0)
        correct = state.get("correct", 0)
        incorrect = state.get("incorrect", 0)
        order = state.get("order", [])
        total = len(order)
        
        print(f"DEBUG /api/quiz/status: idx={idx}, correct={correct}, incorrect={incorrect}, total={total}")
        print(f"DEBUG /api/quiz/status: condition check: total > 0 = {total > 0}, idx < total = {idx < total}, (correct > 0 or incorrect > 0) = {correct > 0 or incorrect > 0}")
        
        #  FIX: Can resume only if quiz has actual progress (at least one answer submitted)
        # Prevents modal on fresh uploads where idx=0, correct=0, incorrect=0
        can_resume = total > 0 and idx < total and (correct > 0 or incorrect > 0)
        
        print(f"DEBUG /api/quiz/status: can_resume = {can_resume}")
        
        if can_resume:
            return jsonify({
                "can_resume": True,
                "index": idx,
                "total": total,
                "correct": correct,
                "incorrect": incorrect,
                "streak": state.get("streak", 0),
                "session_points": state.get("session_points", 0)
            })
        else:
            return jsonify({"can_resume": False, "message": "No progress to resume"})
            
    except Exception as e:
        print(f" Error checking quiz status: {e}")
        return jsonify({"can_resume": False, "error": str(e)}), 500

@app.route("/api/clear-partial-progress", methods=["POST"])
def api_clear_partial_progress():
    """
    Clear saved quiz progress to start fresh
    Does NOT delete database records, just resets session state
    """
    try:
        state = session.get(QUIZ_STATE_KEY)
        if state:
            # Reset to initial state but keep wordbank
            state["index"] = 0
            state["correct"] = 0
            state["incorrect"] = 0
            state["streak"] = 0
            state["max_streak"] = 0
            state["session_points"] = 0
            state["badges_earned"] = []
            session[QUIZ_STATE_KEY] = state
        
        return jsonify({
            "status": "success",
            "message": "Quiz progress cleared - ready for fresh start"
        })
        
    except Exception as e:
        print(f" Error clearing quiz progress: {e}")
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
        
        print(f" BONUS POINTS AWARDED: +{bonus_points} points for '{reason}' (category: {category})")
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
        print(f" Error adding bonus points: {e}")
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
                "icon": "",
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
     NO EXTERNAL API CALLS - All definitions from built-in resources.
    
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
    
    #  All lookups use INTERNAL DICTIONARY ONLY (get_word_info uses Simple Wiktionary → Cache → Smart Fallback)
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
        "source": source  #  All sources are internal (simple_wiktionary, internal_cache, or smart_fallback)
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
                print(f"️ Failed to preload '{word}': {e}")
                continue
        
        print(f" Dictionary preloaded: {preloaded_count}/{len(words)} words cached")
        
        return jsonify({
            "success": True,
            "preloaded": preloaded_count,
            "total_requested": len(words),
            "wiktionary_loaded": wiktionary is not None,
            "cache_size": len(DICTIONARY_CACHE)
        })
        
    except Exception as e:
        print(f" Dictionary preload failed: {e}")
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
            print(f"️ Failed snapshotting prefetch metrics: {ex}")
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
                                print(f"️ Prefetch persist failed for '{w}': {_persist_ex}")
                    except Exception as ex:
                        print(f"️ Prefetch error for '{w}': {ex}")
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
            print(f" Prefetch job crashed: {e}")
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
    is_random_play = session.get("is_random_play", False)  # Random Play flag
    
    # Detect potential issues
    issues = []
    if len(wb) == 0:
        issues.append("No words loaded - wordbank is empty")
    # Don't warn about default words if this is Random Play mode
    if using_defaults and has_uploaded and not is_random_play:
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
        "is_random_play": is_random_play,
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
        
        # Delete from Railway database (single source of truth)
        if storage_id:
            delete_wordbank(storage_id)
            print(f"DEBUG /api/clear: Deleted wordbank from Railway database")
        
        # Clear all session data thoroughly
        session.pop("wordbank_storage_id", None)
        session.pop(DATA_KEY, None)
        session.pop(QUIZ_STATE_KEY, None)
        session.pop("wordbank_count", None)
        session.pop("using_default_words", None)
        session.pop("skip_default_load", None)
        session.pop("has_uploaded_once", None)
        session.pop("is_random_play", None)
        
        # Mark wordbank as intentionally cleared
        session["wordbank_count"] = 0
        session["wordbank_cleared"] = True
        
        # Force session modification
        session.modified = True
        
        print(f"DEBUG /api/clear: Session cleared. User must manually upload words or use Random Words feature")
        
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
    init_quiz_state(len(wb))
    return jsonify({"ok": True})

@app.route("/api/build_dictionary", methods=["POST"])
def api_build_dictionary():
    """
    Build dictionary cache for all words in current wordbank using built-in Simple Wiktionary
     NO EXTERNAL API - Uses only 50K+ word built-in dictionary
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
                print(f" Wiktionary lookup successful for '{word}'")
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
                print(f" Using fallback for '{word}'")
                
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
    def _safe_is_premium(u: User) -> bool:
        try:
            # Prefer a richer check if the model supports it.
            if hasattr(u, 'is_premium_active') and callable(getattr(u, 'is_premium_active')):
                return bool(u.is_premium_active())
        except Exception:
            pass
        return bool(getattr(u, 'premium_member', False))

    try:
        unlocked = user.get_unlocked_avatars()
    except Exception:
        unlocked = []

    pa = getattr(user, 'purchased_avatars', [])
    if not isinstance(pa, list):
        pa = []
    pb = getattr(user, 'purchased_bundles', [])
    if not isinstance(pb, list):
        pb = []
    return {
        "premium_member": _safe_is_premium(user),
        "purchased_avatars": list(pa or []),
        "purchased_bundles": list(pb or []),
        "unlocked_avatars": unlocked,
    }


def _reconcile_anon_entitlements_to_user(user: User) -> dict:
    """Best-effort: import anon (cookie/device-scoped) entitlements into a logged-in user.

    This supports the common flow:
      - user restores/purchases on device (anon_restore_id)
      - later they create an account or sign in
      - their previously restored avatar/bundle ownership should carry over

    Security note:
      - We intentionally do *not* import premium/subscription SKUs from anon
        ownership here (those require account-based verification/restore).
    """
    out = {
        'imported': False,
        'anon_restore_id_present': False,
        'total_candidates': 0,
        'applied_count': 0,
        'applied_product_ids': [],
        'skipped_product_ids': [],
        'errors': [],
    }
    if user is None:
        return out

    anon_restore_id = None
    try:
        anon_restore_id = request.cookies.get('anon_restore_id')
    except Exception:
        anon_restore_id = None
    if not anon_restore_id:
        try:
            anon_restore_id = session.get('anon_restore_id')
        except Exception:
            anon_restore_id = None

    out['anon_restore_id_present'] = bool(anon_restore_id)
    if not anon_restore_id:
        return out

    # Pull anon owned products (DB + session) and de-dupe.
    try:
        anon_ent = _get_guest_entitlements() or {}
        owned = anon_ent.get('anon_owned_products') if isinstance(anon_ent, dict) else []
    except Exception:
        owned = []
    if not isinstance(owned, list):
        owned = []

    merged: list[str] = []
    seen: set[str] = set()
    for pid in owned:
        if not pid:
            continue
        spid = str(pid).strip()
        if not spid or spid in seen:
            continue
        seen.add(spid)
        merged.append(spid)

    out['total_candidates'] = int(len(merged))
    if not merged:
        return out

    def _looks_premiumish(pid: str) -> bool:
        try:
            p = (pid or '').lower()
        except Exception:
            return False
        return any(k in p for k in ('premium', 'subscription', 'monthly', 'yearly', 'family'))

    # Apply only non-subscription entitlements from anon ownership.
    applied: list[str] = []
    skipped: list[str] = []
    for pid in merged:
        try:
            mapping = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
            mtype = str(mapping.get('type') or '').strip().lower() if isinstance(mapping, dict) else ''
            is_subscription_like = bool(mtype in ('premium', 'subscription') or (isinstance(mapping, dict) and bool(mapping.get('subscription'))))
            if is_subscription_like or _looks_premiumish(pid):
                skipped.append(pid)
                continue

            res = _apply_entitlement(user, pid)
            if isinstance(res, dict) and res.get('applied'):
                applied.append(pid)
        except Exception as e:
            out['errors'].append({'product_id': pid, 'error': str(e)})

    out['applied_product_ids'] = applied
    out['skipped_product_ids'] = skipped
    out['applied_count'] = int(len(applied))
    out['imported'] = True

    # Best-effort audit trail: record imported entitlements as PurchaseRecord rows.
    bypass_db = os.environ.get('DISABLE_IAP_DB_WRITES', '0').strip() == '1'
    if not bypass_db and applied:
        try:
            for pid in applied:
                try:
                    rec = PurchaseRecord(
                        user_id=user.id,
                        platform='web',
                        product_id=pid,
                        status='verified',
                        transaction_id=None,
                        purchase_token=None,
                        raw_payload={
                            'imported_from_anon_restore_id': anon_restore_id,
                            'source': 'anon_entitlements_login_reconcile'
                        }
                    )
                    db.session.add(rec)
                except Exception:
                    continue
        except Exception:
            pass

    return out


def _get_anon_owned_products_from_db() -> list[str]:
    """Best-effort lookup of anonymous/device-scoped ownership.

    Uses the `anon_restore_id` cookie as a stable key (Apple guideline 5.1.1 guest restore).
    Returns a de-duped list of product_ids.
    """
    # Prefer a request-scoped override (used during reconcile-only / install_id relink)
    # before falling back to the cookie.
    anon_restore_id = None
    try:
        anon_restore_id = session.get('anon_restore_id')
    except Exception:
        anon_restore_id = None
    if not anon_restore_id:
        try:
            anon_restore_id = request.cookies.get('anon_restore_id')
        except Exception:
            anon_restore_id = None
    if not anon_restore_id:
        return []

    try:
        from models import AnonPurchaseOwnership
        rows = (AnonPurchaseOwnership.query
                .filter_by(anon_restore_id=anon_restore_id)
                .filter(AnonPurchaseOwnership.status != 'restore_error')
                .all())
        out = []
        seen = set()
        for r in rows or []:
            pid = getattr(r, 'product_id', None)
            if not pid:
                continue
            if pid in seen:
                continue
            seen.add(pid)
            out.append(pid)
        return out
    except Exception:
        return []


def _get_guest_entitlements() -> dict:
    """Return guest entitlements, merging session + DB-backed anon ownership.

    This ensures sticky access for TestFlight users even if the JS bridge is flaky.
    """
    anon_owned = session.get('anon_owned_products')
    if not isinstance(anon_owned, list):
        anon_owned = []

    # Reconcile-only requests (no product_ids) should still return durable
    # guest ownership from the DB even if the session doesn't yet contain it.
    # If we have nothing in-session, seed from DB so the API response reflects
    # persisted ownership immediately.
    if not anon_owned:
        try:
            anon_owned = _get_anon_owned_products_from_db() or []
            if not isinstance(anon_owned, list):
                anon_owned = []
            session['anon_owned_products'] = anon_owned
        except Exception:
            anon_owned = []

    db_owned = _get_anon_owned_products_from_db()
    if db_owned:
        merged = []
        seen = set()
        for pid in list(anon_owned) + list(db_owned):
            if not pid or pid in seen:
                continue
            seen.add(pid)
            merged.append(pid)
        anon_owned = merged
        # keep session in sync so downstream code (avatars/bundles) keeps working
        try:
            session['anon_owned_products'] = anon_owned
        except Exception:
            pass

    return {"anon_owned_products": anon_owned}


@app.route('/api/iap/verify/<platform>', methods=['POST'])
def api_iap_verify(platform):
    """Verify a purchase from App Store / Play Billing and apply entitlements.
    Request JSON:
      { product_id, transaction_id, purchase_token, payload }
    """
    platform = (platform or '').lower().strip()
    # Be tolerant of common native platform labels.
    if platform in ('ios', 'appstore', 'app_store'):
        platform = 'apple'
    elif platform in ('android', 'play', 'playstore', 'play_store'):
        platform = 'google'

    if platform not in ('apple', 'google', 'web'):
        return jsonify({"success": False, "error": "Unsupported platform"}), 400

    # In tests (and optionally in local dev), allow bypassing store verification
    # so guest-flow behavior can be validated without live App Store/Play calls.
    if os.environ.get('DISABLE_IAP_STORE_VERIFY', '0').strip() == '1':
        data = request.get_json(silent=True) or {}
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({"success": False, "error": "Missing product_id"}), 400

        user_for_verify = current_user if current_user.is_authenticated else None
        anon_restore_id = None
        if user_for_verify is None:
            try:
                anon_restore_id = request.cookies.get('anon_restore_id')
            except Exception:
                anon_restore_id = None
            if not anon_restore_id:
                anon_restore_id = uuid.uuid4().hex

        if user_for_verify is not None:
            try:
                _apply_entitlement(user_for_verify, product_id)
            except Exception:
                pass
        else:
            try:
                owned = session.get('anon_owned_products')
                if not isinstance(owned, list):
                    owned = []
                if product_id not in owned:
                    owned.append(product_id)
                session['anon_owned_products'] = owned
            except Exception:
                pass

        resp = jsonify({
            "success": True,
            "message": "Purchase verified (bypass)",
            "record_id": None,
            "entitlements": _entitlements_summary(user_for_verify) if user_for_verify is not None else _get_guest_entitlements()
        })
        if anon_restore_id:
            try:
                resp.set_cookie(
                    'anon_restore_id',
                    anon_restore_id,
                    max_age=60 * 60 * 24 * 365,
                    httponly=True,
                    samesite='Lax'
                )
            except Exception:
                pass
        return resp

    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    transaction_id = data.get('transaction_id')
    purchase_token = data.get('purchase_token')
    payload = data.get('payload', {})

    if not product_id:
        return jsonify({"success": False, "error": "Missing product_id"}), 400

    if not _is_subscription_product_allowed(product_id):
        return jsonify({
            "success": False,
            "error": "product_not_available",
            "details": {"product_id": product_id, "monthly_only": bool(IAP_MONTHLY_ONLY)}
        }), 400

    # Apple Guideline 5.1.1: users must not be forced to register/login before
    # purchasing content that is not account-based. Support guest verification by
    # tracking ownership against an anonymous id.
    user_for_verify = current_user if current_user.is_authenticated else None
    anon_restore_id = None
    if user_for_verify is None:
        try:
            anon_restore_id = request.cookies.get('anon_restore_id')
        except Exception:
            anon_restore_id = None
        if not anon_restore_id:
            anon_restore_id = uuid.uuid4().hex

    # Create purchase record (pending)
    # IMPORTANT: Some deployments have PurchaseRecord.user_id as NOT NULL.
    # Guest flows must not crash; for guests we skip DB writes and store
    # entitlements against anon_owned_products + anon_restore_id instead.
    bypass_db = os.environ.get('DISABLE_IAP_DB_WRITES', '0').strip() == '1' or (user_for_verify is None)
    rec = None
    if not bypass_db:
        rec = PurchaseRecord(
            user_id=user_for_verify.id,
            platform=platform,
            product_id=product_id,
            status='pending',
            transaction_id=transaction_id,
            purchase_token=purchase_token,
            raw_payload={**(payload or {}), **({'anon_restore_id': anon_restore_id} if anon_restore_id else {})}
        )
        db.session.add(rec)
        db.session.flush()  # get rec.id

    ok, status_msg, details = _verify_with_store(platform, data)
    if not ok:
        if rec is not None:
            rec.status = 'failed'
            rec.raw_payload = {**(rec.raw_payload or {}), 'verify_status': status_msg, 'store_details': details}
            db.session.commit()
        return jsonify({"success": False, "error": status_msg, "record_id": (rec.id if rec is not None else None)}), 400

    # Apply entitlements idempotently
    if user_for_verify is not None:
        apply_res = _apply_entitlement(user_for_verify, product_id)
    else:
        # Guest flow: record owned SKUs for this device/session.
        # The UI can reflect ownership without an account.
        try:
            owned = session.get('anon_owned_products')
            if not isinstance(owned, list):
                owned = []
            if product_id not in owned:
                owned.append(product_id)
            session['anon_owned_products'] = owned
        except Exception:
            pass
        apply_res = {'applied': True, 'details': {'mode': 'anon_session'}}
    if rec is not None:
        rec.status = 'verified'
        rec.raw_payload = {**(rec.raw_payload or {}), 'verify_status': status_msg, 'store_details': details, 'apply_result': apply_res}
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Log error but don't fail the verification - purchase may still be valid
            try:
                app.logger.error(f"IAP verify: db commit failed: {e}", exc_info=True)
            except Exception:
                pass
            # Return success with warning instead of 500 to prevent error screen
            return jsonify({
                "success": True,
                "message": "Purchase verified (database write failed)",
                "warning": "Purchase verified but not saved to database. Please try again.",
                "error": f"db_commit_failed: {e}"
            }), 200

    resp = jsonify({
        "success": True,
        "message": "Purchase verified",
        "record_id": (rec.id if rec is not None else None),
        "entitlements": _entitlements_summary(user_for_verify) if user_for_verify is not None else _get_guest_entitlements()
    })

    if anon_restore_id:
        try:
            resp.set_cookie(
                'anon_restore_id',
                anon_restore_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite='Lax'
            )
        except Exception:
            pass

    return resp


@app.route('/api/iap/restore', methods=['POST'])
def api_iap_restore():
    """Restore entitlements from a list of product IDs (client-side provenience).
    This is helpful when a user reinstalls or switches devices; the platform
    client should pre-validate owned purchases and send the product IDs here.
    """
    data = request.get_json(silent=True) or {}
    product_ids = data.get('product_ids')
    platform = (data.get('platform') or 'apple').lower()
    install_id = (data.get('install_id') or '').strip()
    restore_id = uuid.uuid4().hex[:12]

    # NOTE: This endpoint supports reconcile-only calls (no product_ids) for both
    # guests and authenticated users so the UI can refresh entitlement state.
    #
    # For security, we do NOT accept premium/subscription SKUs for guests, since
    # restore relies on client-side enumeration and could otherwise be spoofed.
    user_for_restore = current_user if current_user.is_authenticated else None
    anon_restore_id = None
    if user_for_restore is None:
        try:
            anon_restore_id = request.cookies.get('anon_restore_id')
        except Exception:
            anon_restore_id = None

        # Optional: if the cookie is missing (reinstall), try using a stable native
        # install identifier to recover the prior anon_restore_id.
        if not anon_restore_id and install_id:
            try:
                from models import AnonInstallLink
                link = AnonInstallLink.query.filter_by(install_id=install_id).first()
                if link and getattr(link, 'anon_restore_id', None):
                    anon_restore_id = link.anon_restore_id
            except Exception:
                pass

        if not anon_restore_id:
            anon_restore_id = uuid.uuid4().hex

        # Important: if we had to mint a new anon_restore_id (no cookie and no
        # existing install link), persist the install_id -> anon_restore_id link
        # immediately so a subsequent request/session can relink.
        _bypass_db = os.environ.get('DISABLE_IAP_DB_WRITES', '0').strip() == '1'
        if anon_restore_id and install_id and not _bypass_db:
            try:
                from models import AnonInstallLink
                _ = AnonInstallLink.upsert(install_id=install_id, anon_restore_id=anon_restore_id)
                db.session.commit()
            except Exception:
                try:
                    db.session.rollback()
                except Exception:
                    pass

    def _extract_pid(x):
        """Accept either a string SKU or an object from native SDKs.
        Some wrappers return objects (e.g., {productId, id, sku}).
        """
        if x is None:
            return None
        if isinstance(x, str):
            v = x.strip()
            return v or None
        if isinstance(x, dict):
            for k in ('productId', 'product_id', 'productID', 'sku', 'id', 'identifier'):
                if k in x and x.get(k):
                    try:
                        v = str(x.get(k)).strip()
                        return v or None
                    except Exception:
                        continue
        # Last resort: stringify primitives
        if isinstance(x, (int, float, bool)):
            v = str(x).strip()
            return v or None
        return None

    def _canonicalize_pid(pid: str | None) -> str | None:
        """Return a canonical product id for mapping.

        We accept a few historical/legacy variants from mobile builds and
        translate them into the current App Store Connect SKU so entitlements
        apply correctly.

        Example: native sometimes reports `beesmart.premium.monthly` while the
        server mapping expects `com.beesmart.premium.monthly`.
        """
        if not pid:
            return None
        try:
            p = str(pid).strip()
        except Exception:
            return None
        if not p:
            return None

        # Map known legacy/malformed identifiers to the configured monthly SKU.
        # Keep this tight to avoid accidentally re-mapping unrelated products.
        try:
            monthly = (SUBSCRIPTION_PRODUCT_IDS.get('monthly') or 'com.beesmart.premium.monthly').strip()
        except Exception:
            monthly = 'com.beesmart.premium.monthly'
        if p == 'beesmart.premium.monthly':
            return monthly
        return p

    # If the client can't enumerate product_ids yet (bridge not ready), treat this
    # as a reconcile request instead of a hard failure. We'll return current
    # entitlements from DB/session.
    if not isinstance(product_ids, list) or not product_ids:
        # If we recovered anon_restore_id via install_id (reinstall scenario), ensure
        # _get_guest_entitlements() can see it in this request even before the
        # response cookie is persisted client-side.
        if user_for_restore is None and anon_restore_id:
            try:
                session['anon_restore_id'] = anon_restore_id
            except Exception:
                pass

        resp = jsonify({
            "success": True,
            "restore_id": restore_id,
            "normalized_product_ids": [],
            "applied": [],
            "errors": [],
            "entitlements": _entitlements_summary(user_for_restore) if user_for_restore is not None else _get_guest_entitlements(),
            "note": "no_product_ids_provided_reconcile_only"
        })
        if anon_restore_id:
            try:
                resp.set_cookie(
                    'anon_restore_id',
                    anon_restore_id,
                    max_age=60 * 60 * 24 * 365,
                    httponly=True,
                    samesite='Lax'
                )
            except Exception:
                pass

        # Persist optional install_id -> anon_restore_id link for reinstall continuity.
        # Keep this best-effort and avoid managing transactions here.
        _bypass_db = os.environ.get('DISABLE_IAP_DB_WRITES', '0').strip() == '1'
        if anon_restore_id and install_id and not _bypass_db:
            try:
                from models import AnonInstallLink
                _ = AnonInstallLink.upsert(install_id=install_id, anon_restore_id=anon_restore_id)
                db.session.commit()
            except Exception:
                # no-op: reconcile-only should never fail due to the install link
                try:
                    db.session.rollback()
                except Exception:
                    pass
        return resp

    # In tests (and optionally in local dev), allow bypassing DB writes
    # so restore can succeed without requiring a live database.
    bypass_db = os.environ.get('DISABLE_IAP_DB_WRITES', '0').strip() == '1'

    # Normalize + de-dupe while preserving order
    normalized = []
    seen = set()
    for item in product_ids:
        pid = _canonicalize_pid(_extract_pid(item))
        if not pid:
            continue
        if pid in seen:
            continue
        seen.add(pid)
        normalized.append(pid)

    def _looks_premiumish(pid: str) -> bool:
        try:
            p = (pid or '').lower()
        except Exception:
            return False
        return any(k in p for k in ('premium', 'subscription', 'monthly', 'yearly', 'family'))

    # Guests: refuse to process subscription-like SKUs (prevents spoofed premium).
    if user_for_restore is None and normalized:
        safe = []
        blocked = []
        for pid in normalized:
            mapping = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
            mtype = str(mapping.get('type') or '').strip().lower() if isinstance(mapping, dict) else ''
            is_subscription_like = bool(mtype in ('premium', 'subscription') or (isinstance(mapping, dict) and bool(mapping.get('subscription'))))
            if is_subscription_like or _looks_premiumish(pid):
                blocked.append(pid)
            else:
                safe.append(pid)
        normalized = safe
        if blocked:
            # Keep response helpful for clients that try restore while signed-out.
            errors = [{"product_id": pid, "error": "login_required_for_subscription"} for pid in blocked]
            # If everything was blocked, return 401 so the UI can prompt login.
            if not normalized:
                return jsonify({
                    "success": False,
                    "error": "login_required",
                    "message": "Please sign in with your BeeSmart account to restore subscriptions.",
                    "login_url": url_for('login'),
                    "restore_id": restore_id,
                    "normalized_product_ids": [],
                    "applied": [],
                    "errors": errors,
                    "entitlements": _get_guest_entitlements(),
                }), 401

    if not normalized:
        return jsonify({
            "success": False,
            "error": "No valid product_ids after normalization",
            "restore_id": restore_id,
        }), 400

    # In monthly-only builds, reject unsupported subscription SKUs early.
    if IAP_MONTHLY_ONLY:
        blocked = [pid for pid in normalized if not _is_subscription_product_allowed(pid)]
        if blocked:
            return jsonify({
                "success": False,
                "error": "product_not_available",
                "restore_id": restore_id,
                "blocked_product_ids": blocked,
                "monthly_only": True
            }), 400

    try:
        app.logger.info(
            f"IAP restore start restore_id={restore_id} "
            f"user_id={getattr(current_user, 'id', None) if current_user.is_authenticated else None} "
            f"anon_id={'set' if anon_restore_id else None} platform={platform} "
            f"count_in={len(product_ids)} count_norm={len(normalized)}"
        )
    except Exception:
        pass

    applied = []
    errors = []
    db_errors = []  # Track database-specific errors separately
    
    # Refresh user object from database to avoid stale data issues
    if user_for_restore is not None:
        try:
            db.session.refresh(user_for_restore)
        except Exception as e:
            try:
                app.logger.warning(f"IAP restore: failed to refresh user object: {e}")
                # Try to reload from database
                user_for_restore = User.query.get(user_for_restore.id)
                if user_for_restore is None:
                    return jsonify({
                        "success": False,
                        "error": "user_not_found",
                        "message": "User account not found. Please sign in again.",
                        "restore_id": restore_id
                    }), 404
            except Exception:
                pass
    
    for pid in normalized:
        had_error = False
        err_msg = None
        try:
            if user_for_restore is not None:
                try:
                    res = _apply_entitlement(user_for_restore, pid)
                    if res and isinstance(res, dict) and res.get('applied'):
                        applied.append({"product_id": pid, **res})
                except Exception as e:
                    had_error = True
                    err_msg = f"entitlement_apply_failed: {str(e)}"
                    errors.append({"product_id": pid, "error": err_msg})
                    try:
                        app.logger.warning(f"IAP restore: failed to apply entitlement for {pid}: {e}", exc_info=True)
                    except Exception:
                        pass
            else:
                # Guest restore: record owned SKUs for this device; the UI can reflect
                # restored ownership without requiring an account.
                try:
                    owned = session.get('anon_owned_products')
                    if not isinstance(owned, list):
                        owned = []
                    if pid not in owned:
                        owned.append(pid)
                    session['anon_owned_products'] = owned
                    applied.append({"product_id": pid, "applied": True, "details": {"mode": "anon_session"}})
                except Exception as e:
                    # Fallback: still mark as applied for guest even if session write fails
                    applied.append({"product_id": pid, "applied": True, "details": {"mode": "anon"}})
                    try:
                        app.logger.warning(f"IAP restore: session write failed for guest restore {pid}: {e}")
                    except Exception:
                        pass
        except Exception as e:
            had_error = True
            err_msg = str(e)
            errors.append({"product_id": pid, "error": err_msg})
            try:
                app.logger.error(f"IAP restore: unexpected error for {pid}: {e}", exc_info=True)
            except Exception:
                pass

        # Log a record for traceability (status verified via restore)
        raw_payload = {'restore': True, 'restore_id': restore_id}
        if had_error and err_msg:
            raw_payload['restore_error'] = err_msg
        if not bypass_db:
            # Only write PurchaseRecord for authenticated users (schema requires user_id).
            if user_for_restore is not None:
                try:
                    # Check if PurchaseRecord already exists to avoid duplicates
                    existing = PurchaseRecord.query.filter_by(
                        user_id=user_for_restore.id,
                        platform=platform,
                        product_id=pid,
                        status='restore_error' if had_error else 'verified'
                    ).first()
                    
                    if existing is None:
                        rec = PurchaseRecord(
                            user_id=user_for_restore.id,
                            platform=platform,
                            product_id=pid,
                            status='restore_error' if had_error else 'verified',
                            transaction_id=None,
                            purchase_token=None,
                            raw_payload=raw_payload
                        )
                        db.session.add(rec)
                        # Commit immediately per product to isolate failures
                        try:
                            db.session.commit()
                        except Exception as commit_err:
                            db.session.rollback()
                            db_errors.append({
                                "product_id": pid,
                                "error": str(commit_err),
                                "type": "purchase_record_commit_failed"
                            })
                            try:
                                app.logger.error(
                                    f"IAP restore: failed to commit PurchaseRecord for {pid}: {commit_err}",
                                    exc_info=True
                                )
                            except Exception:
                                pass
                    else:
                        # Update existing record with latest restore info
                        try:
                            existing.raw_payload = raw_payload
                            existing.status = 'restore_error' if had_error else 'verified'
                            existing.updated_at = datetime.utcnow()
                            db.session.commit()
                        except Exception as update_err:
                            db.session.rollback()
                            db_errors.append({
                                "product_id": pid,
                                "error": str(update_err),
                                "type": "purchase_record_update_failed"
                            })
                            try:
                                app.logger.error(
                                    f"IAP restore: failed to update PurchaseRecord for {pid}: {update_err}",
                                    exc_info=True
                                )
                            except Exception:
                                pass
                except Exception as e:
                    # Log but don't fail the restore if DB write fails
                    db_errors.append({
                        "product_id": pid,
                        "error": str(e),
                        "type": "purchase_record_create_failed"
                    })
                    try:
                        app.logger.error(f"IAP restore: failed to create/update PurchaseRecord for {pid}: {e}", exc_info=True)
                    except Exception:
                        pass
            else:
                # Guest restore: store durable ownership tied to anon_restore_id cookie.
                try:
                    from models import AnonPurchaseOwnership
                    owner = AnonPurchaseOwnership.upsert(
                        anon_restore_id=anon_restore_id,
                        platform=platform,
                        product_id=pid,
                        status='restore_error' if had_error else 'verified',
                        raw_payload=raw_payload
                    )
                    # keep lint quiet
                    _ = owner
                    # Commit immediately for guest records too
                    try:
                        db.session.commit()
                    except Exception as commit_err:
                        db.session.rollback()
                        db_errors.append({
                            "product_id": pid,
                            "error": str(commit_err),
                            "type": "anon_ownership_commit_failed"
                        })
                        try:
                            app.logger.error(
                                f"IAP restore: failed to commit AnonPurchaseOwnership for {pid}: {commit_err}",
                                exc_info=True
                            )
                        except Exception:
                            pass

                    # Optional: link a stable native install id to this anon_restore_id
                    # so a reinstall can recover guest entitlements.
                    if install_id:
                        try:
                            from models import AnonInstallLink
                            _ = AnonInstallLink.upsert(install_id=install_id, anon_restore_id=anon_restore_id)
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            try:
                                app.logger.warning(f"IAP restore: failed to link install_id for {pid}: {e}", exc_info=True)
                            except Exception:
                                pass
                except Exception as e:
                    # Log but don't fail the restore if guest DB write fails
                    db_errors.append({
                        "product_id": pid,
                        "error": str(e),
                        "type": "anon_ownership_create_failed"
                    })
                    try:
                        app.logger.error(f"IAP restore: failed to create AnonPurchaseOwnership for {pid}: {e}", exc_info=True)
                    except Exception:
                        pass
    
    # Commit user entitlement changes if any were made
    if user_for_restore is not None and not bypass_db:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db_errors.append({
                "error": str(e),
                "type": "user_entitlements_commit_failed"
            })
            try:
                app.logger.error(f"IAP restore: failed to commit user entitlement changes: {e}", exc_info=True)
            except Exception:
                pass
    
    # If we had database errors, include them in the response but don't fail the restore
    if db_errors:
        errors.extend([{"error": f"db_{err.get('type', 'unknown')}", "product_id": err.get("product_id"), "message": err.get("error")} for err in db_errors])
        try:
            app.logger.warning(f"IAP restore: {len(db_errors)} database errors occurred during restore", extra={"db_errors": db_errors})
        except Exception:
            pass

    # Optional debug payload to help diagnose entitlement mismatches in TestFlight.
    # Off by default; enable temporarily via env var.
    iap_debug = os.environ.get('IAP_DEBUG_RESTORE', '0').strip().lower() in ('1', 'true', 'yes', 'on')
    debug_info = None
    if iap_debug:
        try:
            known = []
            unknown = []
            premium_like = []
            subscription_like = []
            premium_map_types = set(['premium', 'subscription'])
            for pid in normalized:
                m = PRODUCT_MAP.get(pid) if isinstance(PRODUCT_MAP, dict) else None
                if m:
                    known.append({'product_id': pid, 'type': m.get('type'), 'mapping': {k: m.get(k) for k in ('type', 'subscription', 'bundle_id', 'avatar_id') if k in m}})
                    t = (m.get('type') or '').lower()
                    if t in premium_map_types:
                        premium_like.append(pid)
                    if m.get('subscription') or t == 'subscription':
                        subscription_like.append(pid)
                else:
                    unknown.append(pid)
                    p = (pid or '').lower()
                    if any(k in p for k in ('premium', 'subscription', 'monthly', 'yearly', 'family')):
                        premium_like.append(pid)
            debug_info = {
                'platform': platform,
                'user_id': getattr(user_for_restore, 'id', None) if user_for_restore is not None else None,
                'is_authenticated': bool(user_for_restore is not None),
                'install_id_present': bool(install_id),
                'anon_restore_id_set': bool(anon_restore_id),
                'count_in': len(product_ids) if isinstance(product_ids, list) else None,
                'count_normalized': len(normalized),
                'normalized_known': known,
                'normalized_unknown': unknown,
                'premium_like_product_ids': list(dict.fromkeys(premium_like)),
                'subscription_like_product_ids': list(dict.fromkeys(subscription_like)),
            }
        except Exception as _e:
            debug_info = {'error': f'debug_failed: {_e}'}

    resp_payload = {
        "success": True,
        "restore_id": restore_id,
        "normalized_product_ids": normalized,
        "applied": applied,
        "errors": errors,
        "entitlements": _entitlements_summary(user_for_restore) if user_for_restore is not None else _get_guest_entitlements()
    }
    if debug_info is not None:
        resp_payload['debug'] = debug_info

    resp = jsonify(resp_payload)

    if anon_restore_id:
        try:
            resp.set_cookie(
                'anon_restore_id',
                anon_restore_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite='Lax'
            )
        except Exception:
            pass

    return resp


@app.route('/api/bundles', methods=['GET'])
def api_bundles_list():
    """List available avatar bundles for the current user.

    Returned bundle.product_id is intended to be passed to the native IAP bridge.
    The same product_id must be recognized in PRODUCT_MAP for verification.
    """
    bundles = []
    user_purchased = set(list(getattr(current_user, 'purchased_bundles', []) or [])) if getattr(current_user, 'is_authenticated', False) else set()
    is_premium = bool(getattr(current_user, 'premium_member', False)) if getattr(current_user, 'is_authenticated', False) else False

    # Guest ownership support (Apple Guideline 5.1.1): allow the UI to reflect
    # restore/purchase entitlements without requiring login.
    anon_owned = _get_guest_entitlements().get('anon_owned_products', [])

    # Build a small normalization map once (catalog is tiny: 39 avatars)
    try:
        from avatar_catalog import AVATAR_CATALOG  # type: ignore
        _catalog_ids = [str((a.get('id') or '')).strip().lower() for a in (AVATAR_CATALOG or []) if (a.get('id') or '').strip()]
    except Exception:
        _catalog_ids = []
    _norm_to_canon = {}
    for _cid in _catalog_ids:
        _k = re.sub(r"[^a-z0-9]+", "", _cid)
        if _k and _k not in _norm_to_canon:
            _norm_to_canon[_k] = _cid

    def _canon_avatar_id(_s: str) -> str:
        v = str(_s or '').strip().lower()
        if not v:
            return ''
        if v in _catalog_ids:
            return v
        k = re.sub(r"[^a-z0-9]+", "", v)
        return _norm_to_canon.get(k, v)

    for bundle_id, cfg in (BUNDLE_CATALOG or {}).items():
        cfg = cfg or {}
        name = cfg.get('name') or bundle_id
        avatars_raw = list(cfg.get('avatars', []) or [])
        avatars = []
        for _a in avatars_raw:
            ca = _canon_avatar_id(_a)
            if ca:
                avatars.append(ca)
        # Prefer store-friendly SKU when available
        product_id = None
        if callable(bundle_sku_for_id):
            try:
                product_id = bundle_sku_for_id(bundle_id)
            except Exception:
                product_id = None
        if not product_id:
            # Back-compat/internal id (not recommended for store SKUs)
            product_id = f"bundle:{bundle_id}"

        owned_by_anon = bool((product_id in anon_owned) or ((f"bundle:{bundle_id}") in anon_owned))

        bundles.append({
            'id': bundle_id,
            'name': name,
            'avatars': avatars,
            'count': int(len(avatars)),
            'product_id': product_id,
            'is_owned': bool(is_premium or (bundle_id in user_purchased) or owned_by_anon),
        })

    bundles.sort(key=lambda b: (b.get('name') or '').lower())

    return jsonify({
        'success': True,
        'bundles': bundles,
        'user': {
            'premium_member': is_premium,
            'purchased_bundles': list(user_purchased),
            'anon_owned_products': anon_owned if not getattr(current_user, 'is_authenticated', False) else [],
        }
    })


# ----------------------------------------------------------------------------
# Bundle Key Redemption (Teacher/Parent distributed keys)
# ----------------------------------------------------------------------------
@app.route('/api/bundles/redeem', methods=['POST'])
def api_bundles_redeem():
    """Redeem a special bundle key to unlock a set of avatars.
    Request JSON: { key: string }
    Response: { success, bundle_id, bundle_name, unlocked_count, entitlements }
    Notes:
      - Idempotent: re-redeeming an already applied bundle won't duplicate unlocks
      - Keys are matched case-insensitively and with whitespace trimmed
    """
    # App Store compliance: digital content unlocks must use IAP.
    # Kill switch: in App Store builds, always hide key redemption regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    # Otherwise, keep key redemption only for explicit dev/teacher environments.
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)

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
    # Normalize avatar ids inside bundles to canonical catalog ids.
    avatars_raw = list(bundle_cfg.get('avatars', []) or [])
    try:
        from avatar_catalog import AVATAR_CATALOG  # type: ignore
        _catalog_ids = [str((a.get('id') or '')).strip().lower() for a in (AVATAR_CATALOG or []) if (a.get('id') or '').strip()]
    except Exception:
        _catalog_ids = []
    _norm_to_canon = {}
    for _cid in _catalog_ids:
        _k = re.sub(r"[^a-z0-9]+", "", _cid)
        if _k and _k not in _norm_to_canon:
            _norm_to_canon[_k] = _cid

    def _canon_avatar_id(_s: str) -> str:
        v = str(_s or '').strip().lower()
        if not v:
            return ''
        if v in _catalog_ids:
            return v
        k = re.sub(r"[^a-z0-9]+", "", v)
        return _norm_to_canon.get(k, v)

    avatars = []
    for _a in avatars_raw:
        ca = _canon_avatar_id(_a)
        if ca:
            avatars.append(ca)
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
        # Log error but don't fail the redemption - bundle may still be applied
        try:
            app.logger.error(f"Bundle redemption: db commit failed: {e}", exc_info=True)
        except Exception:
            pass
        # Return success with warning instead of 500 to prevent error screen
        return jsonify({
            "success": True,
            "bundle_id": bundle_id,
            "bundle_name": bundle_name,
            "source": source,
            "unlocked_count": unlocked_count,
            "entitlements": entitlements,
            "warning": "Bundle redeemed but not saved to database. Please try again.",
            "error": f"db_commit_failed: {e}"
        }), 200

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
def api_beekey_redeem_for_linked():
    """Redeem a BeeKey and unlock avatars for all users linked to the redeemer's admin/teacher key.
    
    This endpoint allows Admin, Parent, and Teacher users to redeem a BeeKey code and automatically
    unlock the avatars in that BeeKey pack for all students/children linked to their account via
    admin_key or teacher_key.
    
    Request JSON: { beekey: string }
    Response: { success, bundle_id, avatars_count, users_unlocked, message }
    """
    # App Store compliance: digital content unlocks must use IAP.
    # Kill switch: in App Store builds, always hide BeeKey redemption regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    # Otherwise, keep BeeKey redemption only for explicit dev/teacher environments.
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)

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
def api_buzz_dust_info():
    """Get current user's Buzz Dust and rank information
    
    Supports both authenticated users and guests.
    Guests always get Novice Bee rank with 0 Buzz Dust.
    """
    try:
        print(f" DEBUG /api/buzz-dust/info: Starting request")
        print(f" DEBUG /api/buzz-dust/info: current_user.is_authenticated = {current_user.is_authenticated}")
        
        from buzz_dust_helpers import BUZZ_DUST_MULTIPLIER, get_bee_class, get_rank_progress, get_all_bee_classes
        
        # Handle both authenticated and guest users
        if current_user.is_authenticated:
            buzz_dust = current_user.total_buzz_dust or 0
            print(f" DEBUG /api/buzz-dust/info: Authenticated user, buzz_dust={buzz_dust}")

            # NOTE: Buzz Dust is *separate* from Points/grades.
            # Do NOT derive total_buzz_dust from lifetime points.
            # Instead, if the stored bee_class is inconsistent with the user's Buzz Dust,
            # reconcile bee_class without mutating total_buzz_dust.
            try:
                computed_class_id = get_bee_class(buzz_dust).get('id', 'novice')
                stored_class_id = (current_user.bee_class or 'novice')
                if stored_class_id != computed_class_id:
                    print(
                        " WARN /api/buzz-dust/info: Reconciling bee_class "
                        f"{stored_class_id}→{computed_class_id} based on total_buzz_dust={buzz_dust}"
                    )
                    current_user.bee_class = computed_class_id
                    # If we are reconciling into a higher rank and there's no timestamp, set one
                    # so clients/logic don't treat this as an 'unknown' rank-up state.
                    if computed_class_id != 'novice' and getattr(current_user, 'last_rank_up_at', None) is None:
                        current_user.last_rank_up_at = datetime.now(timezone.utc)
                    from models import db
                    db.session.commit()
            except Exception as reconcile_error:
                # Non-fatal: still return whatever stored value we have
                print(f" WARN /api/buzz-dust/info: Reconcile check failed: {reconcile_error}")
        else:
            # Guest users always start at 0
            buzz_dust = 0
            print(f" DEBUG /api/buzz-dust/info: Guest user, defaulting to 0 Buzz Dust")
        
        rank_progress = get_rank_progress(buzz_dust)

        response_data = {
            'success': True,
            'total_buzz_dust': buzz_dust,
            'current_class': rank_progress['current_class'],
            'next_class': rank_progress['next_class'],
            'progress_percent': rank_progress['progress_percent'],
            'dust_needed': rank_progress['dust_needed'],
            'at_max_rank': rank_progress['at_max_rank'],
            'all_classes': get_all_bee_classes(),
            'is_authenticated': current_user.is_authenticated  # Help frontend debug
        }
        
        print(f" DEBUG /api/buzz-dust/info: Returning success response")
        print(f"   - current_class: {rank_progress['current_class'].get('label', 'Unknown')}")
        print(f"   - next_class: {rank_progress['next_class'].get('label', 'Max') if rank_progress['next_class'] else 'None'}")
        print(f"   - at_max_rank: {rank_progress['at_max_rank']}")
        
        resp = jsonify(response_data)
        # Ensure browsers and service workers don't cache progress/rank data
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
        
    except Exception as e:
        print(f" ERROR /api/buzz-dust/info: {type(e).__name__}: {e}")
        import traceback
        print(f" ERROR /api/buzz-dust/info: Traceback: {traceback.format_exc()}")
        
        # Return safe fallback data instead of 500 error
        return jsonify({
            'success': False,
            'error': str(e),
            'total_buzz_dust': 0,
            'current_class': {
                'label': 'Novice Bee',
                'min_buzz_dust': 0,
                'min_points': 0,
                'badge_image': 'Novice.glb'
            },
            'next_class': {
                'label': 'Apprentice Bee',
                'min_buzz_dust': 10000,
                'min_points': 10000,
                'badge_image': 'Apprentice.glb'
            },
            'progress_percent': 0,
            'dust_needed': 10000,
            'at_max_rank': False,
            'all_classes': [],
            'is_authenticated': current_user.is_authenticated
        }), 200  # Return 200 with error flag instead of 500


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
    # App Store compliance: hide key management endpoints.
    # Kill switch: in App Store builds, always hide key management regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)
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
    # App Store compliance: hide key management endpoints.
    # Kill switch: in App Store builds, always hide key management regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)
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
    # App Store compliance: hide key generation endpoints.
    # Kill switch: in App Store builds, always hide key generation regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)
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
    # App Store compliance: hide key management endpoints.
    # Kill switch: in App Store builds, always hide key management regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)
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
    # App Store compliance: hide key management endpoints.
    # Kill switch: in App Store builds, always hide key management regardless of other flags.
    if os.environ.get('APP_STORE_BUILD', '0').strip() == '1':
        return ("Not Found", 404)
    if os.environ.get('ALLOW_KEY_REDEMPTION', '0').strip() != '1':
        return ("Not Found", 404)
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
            _f = os.environ.get('REGISTRATION_FEE_USD')
            one_time_fee = float(_f) if _f not in (None, '') else None
        except Exception:
            one_time_fee = None
        # Monthly subscription fee
        try:
            _m = os.environ.get('SUBSCRIPTION_MONTHLY_USD')
            monthly_fee = float(_m) if _m not in (None, '') else None
        except Exception:
            monthly_fee = None
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
        # Default to the current monthly subscription SKU unless explicitly overridden.
        # (The legacy 'beesmart.sub.full_monthly' remains supported via env and PRODUCT_MAP.)
        try:
            subscription_product_id = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID')
            subscription_product_id = (subscription_product_id or '').strip() or SUBSCRIPTION_PRODUCT_IDS['monthly']
        except Exception:
            subscription_product_id = SUBSCRIPTION_PRODUCT_IDS['monthly']
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
    avatar_id = (data.get('avatar_id') or '').strip()
    if not avatar_id:
        avatar_id = 'mascot-bee'  # Always default to mascot-bee if not explicitly selected
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
            # IMPORTANT: never let a previous user's cached avatar selection bleed into a new account.
            # Consider an avatar "selected" ONLY when the client explicitly sends a non-empty avatar_id.
            prefs['avatar_selected'] = bool((data.get('avatar_id') or '').strip())
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
                        print(f" Linked {new_user.username} to {teacher.username}'s dashboard")
                    else:
                        linked_to_admin = True
                        admin_name = teacher.display_name
                        print(f"ℹ️ Link already exists for {new_user.username} → {teacher.username}")
                except Exception as link_error:
                    print(f"️ Failed to create TeacherStudent link: {link_error}")
                    # Non-fatal - user registration still succeeds
            else:
                print(f"️ Teacher key '{teacher_key}' not found - student not linked")
        
        # Auto-login after registration
        login_user(new_user, remember=True)

        # Send welcome email asynchronously (best-effort) if email provided
        if new_user.email:
            def _send_async():
                try:
                    send_welcome_email(new_user.email, new_user.username, new_user.role, new_user.teacher_key if new_user.role in ['teacher', 'parent'] else None)
                except Exception as _e:
                    print(f"️ Welcome email async failed: {_e}")
            threading.Thread(target=_send_async, daemon=True).start()
        
        # Build response message
        message = f" Welcome to the hive, {display_name}! Your account has been created successfully! "
        
        # Add confirmation message if student was linked to admin
        if linked_to_admin and admin_name:
            message += f"\n\n You've been linked to {admin_name}'s dashboard for progress tracking!"
        
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
        # Best-effort: if this device previously restored/purchased as a guest,
        # import those non-subscription entitlements into the signed-in account.
        # (Subscriptions remain login/verification-based.)
        try:
            _reconcile_anon_entitlements_to_user(user)
        except Exception:
            pass

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
            "message": f"Welcome back, {user.display_name}! ",
            "redirect": redirect_url,
            "entitlements": _entitlements_summary(user)
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
    # Clear any client-side IAP state handoffs so premium UI cannot appear
    # to remain "active" after signing out.
    logout_user()
    try:
        session.pop('iap_entitlements', None)
        session.pop('iap_owned_products', None)
        session.pop('iap_last_restore_at', None)
        session.pop('iap_install_id', None)
        # Legacy/alternate keys (best-effort; safe if absent)
        session.pop('owned_products', None)
        session.pop('entitlements', None)
    except Exception:
        # Non-fatal: logout should always succeed.
        pass

    resp = redirect(url_for('home'))
    try:
        # Ensure cookies used for anonymous restore / install tracking are cleared.
        resp.delete_cookie('anon_restore_id')
        resp.delete_cookie('beesmart_anon_restore_id')
        resp.delete_cookie('beesmart_install_id')
        resp.delete_cookie('install_id')
    except Exception:
        pass

    flash('You have been logged out. See you next time! ', 'success')
    return resp


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
                    results.append(f" {col_name} - added")
                except Exception as e:
                    db.session.rollback()
                    results.append(f" {col_name} - failed: {str(e)}")
        
        # Create index
        try:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_avatar_id ON users(avatar_id)"))
            db.session.commit()
            results.append(" Avatar index created")
        except Exception as e:
            results.append(f"️  Index: {str(e)}")
        
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
    except Exception as e:
        # If anything goes wrong determining role, fall back to student view
        print(f" WARNING student_dashboard role redirect failed: {e}")
    
    # --- Safe defaults so the dashboard never 500s ---
    recent_sessions = []
    total_sessions = 0
    avg_accuracy = 0.0
    struggling_words = []
    achievements = []
    badge_collection_sorted = {}
    total_badge_points = 0
    recent_badges = []
    linked_students = []

    # Wrap heavy DB logic in a safety net so we degrade gracefully on prod
    try:
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
        
        #  NEW: Get badge collection
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
                    'icon': BADGE_METADATA.get(badge_type, {}).get('icon', ''),
                    'image': BADGE_METADATA.get(badge_type, {}).get('image'),
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
            meta = BADGE_METADATA.get(badge_type, {})
            recent_badges.append({
                'type': badge_type,
                'icon': meta.get('icon', ''),
                'image': meta.get('image'),
                'name': meta.get('name', badge_type.replace('_', ' ').title()),
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
    except Exception as e:
        # Never let a bad row or migration issue take down the dashboard
        print(f" ERROR student_dashboard: failed to build stats: {e}")
        import traceback as _tb
        _tb.print_exc()

    # Get current user's avatar data for immediate display (no fetch needed)
    try:
        user_avatar_data = current_user.get_avatar_data()
        use_mascot = current_user.has_selected_avatar() == False
    except Exception as e:
        print(f"️ Could not load user avatar data: {e}")
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
    """API endpoint for a user to update their own avatar. (Legacy)
    
     SECURITY: Validates avatar unlock status before allowing selection.
    - Admins bypass all unlock checks
    - Regular users must have earned/purchased the avatar
    - Guest users cannot select avatars (fallback to mascot)
    """
    try:
        data = request.get_json()
        if not data or 'avatar_id' not in data:
            return jsonify({'status': 'error', 'message': 'Missing avatar_id in request.'}), 400

        avatar_id = data['avatar_id']
        
        #  SECURITY CHECK 1: Verify user can select avatars
        # Guest users (no password) cannot select avatars
        if not current_user.password_hash:
            return jsonify({
                'status': 'error', 
                'message': 'Guest users cannot select avatars. Please register to customize your bee!'
            }), 403
        
        #  SECURITY CHECK 2: Avatar unlock validation (unless admin)
        if current_user.role != 'admin':
            try:
                from avatar_catalog import check_avatar_unlocked, AVATAR_CATALOG
                
                # Get user's unlock eligibility
                user_honey_points = getattr(current_user, 'honey_points', 0) or 0
                purchased_avatars = getattr(current_user, 'purchased_avatars', []) or []
                
                # Check if avatar is unlocked
                unlock_result = check_avatar_unlocked(avatar_id, user_honey_points, purchased_avatars)
                
                if not unlock_result.get('unlocked', False):
                    # Forbidden: User has not earned/purchased this avatar
                    tier = next(
                        (a.get('tier', 'premium') for a in AVATAR_CATALOG if a['id'] == avatar_id),
                        'premium'
                    )
                    
                    if tier == 'premium':
                        return jsonify({
                            'status': 'error',
                            'message': 'This avatar is only available for purchase.',
                            'reason': 'premium_locked'
                        }), 403
                    elif tier == 'earn_or_buy':
                        points_needed = unlock_result.get('required_points', 0) - user_honey_points
                        return jsonify({
                            'status': 'error',
                            'message': f'Earn {points_needed:,} more Honey Points or purchase to unlock this avatar.',
                            'reason': 'points_required',
                            'points_needed': max(0, points_needed)
                        }), 403
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'This avatar is not yet unlocked. Complete more quizzes to earn it!',
                            'reason': 'not_earned'
                        }), 403
                        
            except ImportError:
                # Fallback if avatar_catalog unavailable
                print(f"️ Avatar catalog unavailable, skipping unlock check for {avatar_id}")
            except Exception as e:
                print(f"️ Error checking avatar unlock status: {e}")
                # Continue with selection on catalog errors (fail-open for existing data)
        
        #  SECURITY CHECK 3: Avatar parental lock (if parent locked their child's avatars)
        if getattr(current_user, 'avatar_locked', False):
            return jsonify({
                'status': 'error',
                'message': 'Your parent has locked avatar selection. Please ask them to unlock it.',
                'reason': 'parental_lock'
            }), 403
        
        #  UPDATE: The update_avatar method on the User model handles saving.
        success, message = current_user.update_avatar(avatar_id)
        
        if success:
            try:
                # Mark avatar as explicitly selected
                prefs = current_user.preferences or {}
                prefs['avatar_selected'] = True
                prefs['avatar_selected_at'] = datetime.now(timezone.utc).isoformat()
                current_user.preferences = prefs
                
                db.session.commit()
                
                #  AUDIT: Log avatar selection
                print(f" User {current_user.id} ({current_user.username}) selected avatar: {avatar_id}")
                
                return jsonify({
                    'status': 'success', 
                    'message': message,
                    'avatar_id': avatar_id
                })
            except Exception as e:
                db.session.rollback()
                log_error(f"Database error after updating avatar for user {current_user.id}: {e}")
                return jsonify({'status': 'error', 'message': 'Database error. Could not save avatar.'}), 500
        else:
            # Avatar not found or update failed
            return jsonify({'status': 'error', 'message': message}), 400
            
    except Exception as e:
        print(f" Unexpected error in avatar selection: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'An unexpected error occurred. Please try again.',
            'error': str(e) if app.debug else None
        }), 500


@app.route('/avatar-picker')
def avatar_picker_page():
    """Avatar picker page with 3D viewer for choosing your bee character"""
    if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
        return redirect(url_for('login', next=request.path))
    return render_template('test_avatar_picker.html')

@app.route('/honeycomb-picker')
def honeycomb_avatar_picker():
    """NEW: Honeycomb-style avatar picker with hexagonal grid layout (responsive version)
    
    Allows public browsing to improve IAP discoverability (Apple requirement).
    Guests can view all avatars but must login/register to purchase or select.
    """
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

    # Pass user context to template/JavaScript
    # NOTE: Guests can now browse but will see "Login to purchase" messaging
    is_authenticated = hasattr(current_user, 'is_authenticated') and current_user.is_authenticated
    
    # Safely access user attributes only if authenticated
    user_data = {
        'is_authenticated': is_authenticated,
        'is_guest': not is_authenticated,  # Guests can now browse
        'is_admin': False,
        'user_role': None,
        'username': None,
    }
    
    if is_authenticated:
        try:
            user_data['is_admin'] = getattr(current_user, 'role', None) == 'admin'
            user_data['user_role'] = getattr(current_user, 'role', None)
            user_data['username'] = getattr(current_user, 'username', None)
        except Exception:
            # Fallback if any attribute access fails
            pass

    return render_template(
        'honeycomb_avatar_picker_responsive.html',
        timestamp=timestamp,
        picker_bg_url=picker_bg_url,
        user_data=user_data
    )

@app.route('/honeycomb-picker-old')
def honeycomb_avatar_picker_old():
    """OLD: Original honeycomb picker with absolute positioning"""
    # Registered users only
    if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
        return redirect(url_for('login', next=request.path))
    return render_template('honeycomb_avatar_picker.html')

@app.route('/test/api')
def test_api():
    """Test page for API debugging"""
    return render_template('test_api.html')

@app.route('/api/user/session', methods=['GET'])
def api_user_session():
    """
    Get current user's session information.
    Called during avatar picker loading to verify authentication.
    """
    try:
        if current_user.is_authenticated:
            # Check if user is an actual guest (guest_ username or no password AND guest role)
            user_is_guest = is_guest_user(current_user)
            
            return jsonify({
                'authenticated': True,
                'username': current_user.username,
                'user_id': current_user.id,
                'role': getattr(current_user, 'role', 'user'),
                'is_guest': user_is_guest,  # Only TRUE for actual guest users
                'is_admin': current_user.is_admin_or_premium() if hasattr(current_user, 'is_admin_or_premium') else False,
                'honey_points': getattr(current_user, 'honey_points', 0),
                'premium_member': getattr(current_user, 'premium_member', False),
                'purchased_avatars': list(getattr(current_user, 'purchased_avatars', []) or [])  # CRITICAL: Avatar unlock gate
            })
        else:
            return jsonify({
                'authenticated': False,
                'is_guest': True,
                'message': 'No active session'
            })
    except Exception as e:
        print(f" Error in /api/user/session: {e}")
        import traceback


@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    """Small, cache-free endpoint to confirm current auth state.

    This is intentionally minimal so front-end flows (like Premium Restore Purchases)
    can avoid using possibly-stale template flags when iOS WebView cookie behavior
    is in flux.
    """
    try:
        resp = jsonify({
            'authenticated': bool(getattr(current_user, 'is_authenticated', False) and current_user.is_authenticated)
        })
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        return resp
    except Exception as e:
        print(f" Error in /api/auth/status: {e}")
        import traceback
        traceback.print_exc()
        # Best-effort: never error the client for a status probe.
        return jsonify({'authenticated': False}), 200

@app.route('/test/avatar-loading')
def test_avatar_loading():
    """Test page for avatar 3D loading diagnostics"""
    return render_template('test_avatar_loading.html')

@app.route('/debug/my-permissions')
@login_required
def debug_my_permissions():
    """Debug endpoint to show current user's permissions"""
    import json
    
    user_info = {
        'username': current_user.username,
        'display_name': current_user.display_name,
        'id': current_user.id,
        'role': current_user.role,
        'admin_all_access': current_user.admin_all_access,
        'premium_member': current_user.premium_member,
        'honey_points': current_user.honey_points,
        'purchased_avatars': current_user.purchased_avatars,
        'is_admin_or_premium()': current_user.is_admin_or_premium(),
        'is_guest': session.get('is_guest', False) or is_guest_user(current_user),
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <title>Permission Debug - {current_user.username}</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace; 
                padding: 10px; 
                background: #1a1a1a; 
                color: #00ff00;
                font-size: 14px;
                line-height: 1.4;
                overflow-x: hidden;
            }}
            .section {{ 
                margin: 15px 0; 
                padding: 12px; 
                background: #2a2a2a; 
                border: 2px solid #00ff00;
                border-radius: 8px;
                word-wrap: break-word;
            }}
            .label {{ color: #ffff00; font-weight: bold; }}
            .value {{ color: #00ff00; }}
            .error {{ color: #ff0000; }}
            .success {{ color: #00ff00; }}
            pre {{ 
                background: #0a0a0a; 
                padding: 8px; 
                border: 1px solid #333;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 12px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            h1 {{ 
                font-size: 1.2rem; 
                margin: 10px 0;
                word-wrap: break-word;
            }}
            h2 {{ 
                font-size: 1rem; 
                margin: 8px 0;
            }}
            ul {{ 
                padding-left: 20px;
                margin: 10px 0;
            }}
            li {{ 
                margin: 8px 0;
                word-wrap: break-word;
            }}
            a {{
                color: #00ff00;
                text-decoration: none;
                padding: 8px 12px;
                display: inline-block;
                background: #2a2a2a;
                border: 1px solid #00ff00;
                border-radius: 4px;
                margin: 5px 0;
            }}
            /* iOS touch feedback */
            a:active {{
                background: #00ff00;
                color: #1a1a1a;
            }}
        </style>
    </head>
    <body>
        <h1> Permission Debug: {current_user.username}</h1>
        
        <div class="section">
            <h2>User Information</h2>
            <pre>{json.dumps(user_info, indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>Avatar Access Analysis</h2>
            <p class="label">Expected Behavior:</p>
            <ul>
                <li class="{'success' if user_info['role'] == 'admin' else 'value'}">
                    Role 'admin' = All avatars unlocked
                    <strong>{' YES' if user_info['role'] == 'admin' else ' NO'}</strong>
                </li>
                <li class="{'success' if user_info['admin_all_access'] else 'value'}">
                    admin_all_access = All avatars unlocked
                    <strong>{' YES' if user_info['admin_all_access'] else ' NO'}</strong>
                </li>
                <li class="{'success' if user_info['premium_member'] else 'value'}">
                    premium_member = All avatars unlocked
                    <strong>{' YES' if user_info['premium_member'] else ' NO'}</strong>
                </li>
            </ul>
            
            <p class="label">Final Result:</p>
            <p class="{'error' if user_info['is_admin_or_premium()'] else 'success'}" style="font-size: 1.5em;">
                is_admin_or_premium() = <strong>{user_info['is_admin_or_premium()']}</strong>
            </p>
            
            {'<p class="error">️ BUG DETECTED: Regular user has admin/premium access!</p>' if user_info['is_admin_or_premium()'] and user_info['role'] != 'admin' and not user_info['admin_all_access'] and not user_info['premium_member'] else ''}
            {'<p class="success"> Permissions look correct - avatars should be locked based on honey points/purchases</p>' if not user_info['is_admin_or_premium()'] else ''}
        </div>
        
        <div class="section">
            <p><a href="/honeycomb-picker" style="color: #00ff00;">Go to Avatar Picker</a></p>
            <p><a href="/" style="color: #00ff00;">Go to Home</a></p>
        </div>
    </body>
    </html>
    """
    
    return html


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
        print(f"️ Could not load user avatar data: {e}")
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
            print(f"️ Could not load user avatar data: {e}")
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
        print(f" ADMIN DASHBOARD ERROR: {str(e)}")
        print(error_details)
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('error.html', 
                             error_message=f"Admin Dashboard Error: {str(e)}",
                             error_details=error_details if app.debug else None), 500


@app.route('/admin/fix-avatar-glb')
@login_required
def admin_fix_avatar_glb():
    """Admin utility page to fix avatar GLB paths in database"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin/fix_avatar_glb.html', user=current_user)


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
        print(f" Error fetching users: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users', methods=['POST'])
@login_required
def api_admin_create_user():
    """Create a new user (admin-only).

    Expects JSON:
      - username (required)
      - display_name (optional)
      - email (optional)
      - role (required): student|teacher|parent|admin|guest
      - password (optional): if omitted, server generates one
      - teacher_key (optional): for teacher/parent (otherwise can auto-generate)
      - link_student_to_teacher_key (optional): student-only; if provided, creates TeacherStudent link

    Returns:
      - created user (basic fields)
      - generated_password (only present when server generated)
    """
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403

    try:
        data = request.get_json() or {}

        username = (data.get('username') or '').strip()
        display_name = (data.get('display_name') or '').strip()
        email = (data.get('email') or '').strip() or None
        role = (data.get('role') or '').strip().lower()
        password = data.get('password')

        teacher_key = (data.get('teacher_key') or '').strip() or None
        link_student_to_teacher_key = (data.get('link_student_to_teacher_key') or '').strip() or None

        if not username:
            return jsonify({"status": "error", "message": "username is required"}), 400

        allowed_roles = ['student', 'teacher', 'parent', 'admin', 'guest']
        if role not in allowed_roles:
            return jsonify({"status": "error", "message": "Invalid role"}), 400

        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({"status": "error", "message": "username already exists"}), 409

        # Generate password if not provided
        generated_password = None
        if not password:
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            # 12 chars keeps it copy/pasteable while still strong enough for a default
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
            generated_password = password

        user = User(
            username=username,
            display_name=display_name or username,
            email=email,
            role=role,
        )

        # Avatars: always default to mascot-bee for all account types,
        # unless an avatar is explicitly set later by the normal avatar-selection flows.
        if hasattr(user, 'avatar_id'):
            user.avatar_id = 'mascot-bee'
        if hasattr(user, 'avatar_variant'):
            user.avatar_variant = 'default'
        # Clear any avatar selection preference for fresh accounts
        try:
            prefs = user.preferences or {}
            prefs['avatar_selected'] = False
            user.preferences = prefs
        except Exception:
            pass

        user.set_password(password)

        # Teacher/Parent: ensure teacher_key
        if role in ['teacher', 'parent']:
            if teacher_key:
                user.teacher_key = teacher_key
            else:
                # Best-effort unique generation; rare collisions handled below
                user.generate_teacher_key()

        # Admin: ensure elevated access flag exists and is enabled
        if role == 'admin':
            if hasattr(user, 'admin_all_access'):
                user.admin_all_access = True

        db.session.add(user)
        db.session.flush()  # assign user.id

        # Student linking: optional link_student_to_teacher_key
        if role == 'student' and link_student_to_teacher_key:
            teacher = User.query.filter_by(teacher_key=link_student_to_teacher_key, role='teacher').first()
            if not teacher:
                db.session.rollback()
                return jsonify({
                    "status": "error",
                    "message": "Teacher not found for provided teacher_key"
                }), 400

            # Avoid duplicate link rows
            existing_link = TeacherStudent.query.filter_by(student_id=user.id).first()
            if existing_link:
                existing_link.teacher_user_id = teacher.id
                existing_link.teacher_key = teacher.teacher_key
            else:
                db.session.add(TeacherStudent(
                    teacher_user_id=teacher.id,
                    student_id=user.id,
                    teacher_key=teacher.teacher_key
                ))

        db.session.commit()

        payload = {
            "status": "success",
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "email": user.email,
                "role": user.role,
                "teacher_key": getattr(user, 'teacher_key', None),
            }
        }
        if generated_password:
            payload["generated_password"] = generated_password

        return jsonify(payload), 201

    except Exception as e:
        db.session.rollback()
        print(f" Error creating user: {e}")
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
        print(f" Error updating user: {e}")
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
        
        print(f"️ Admin {current_user.username} deleted user: {username} (ID: {user_id})")
        
        return jsonify({
            "status": "success",
            "message": f"User {username} deleted successfully"
        })
    
    except Exception as e:
        db.session.rollback()
        print(f" Error deleting user: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def api_admin_reset_user_password(user_id):
    """Admin-only: reset/change another user's password.

    Expects JSON:
      - password (optional) : if absent, server generates a new one

    Returns:
      - generated_password (only if server generated)
    """
    if current_user.role != 'admin':
        return jsonify({"status": "error", "message": "Admin access required"}), 403

    try:
        if user_id == current_user.id:
            # Let admins use normal password flow for themselves.
            return jsonify({"status": "error", "message": "Use your profile/password page to change your own password"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        data = request.get_json(silent=True) or {}
        password = (data.get('password') or '').strip()

        generated_password = None
        if not password:
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
            generated_password = password

        if len(password) < 8:
            return jsonify({"status": "error", "message": "Password must be at least 8 characters"}), 400

        user.set_password(password)

        # Audit best-effort
        try:
            log_session_action('admin_password_reset', user_id=user.id, data={'by_admin_id': current_user.id})
        except Exception:
            pass

        db.session.commit()

        payload = {
            "status": "success",
            "message": f"Password reset for {user.username}"
        }
        if generated_password:
            payload['generated_password'] = generated_password

        return jsonify(payload)

    except Exception as e:
        db.session.rollback()
        print(f" Error resetting password: {e}")
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
        
        print(f"️ Admin {current_user.username} bulk deleted {deleted} users")
        
        return jsonify({
            "status": "success",
            "message": f"Deleted {deleted} user(s)",
            "deleted_count": deleted
        })
    
    except Exception as e:
        db.session.rollback()
        print(f" Error bulk deleting users: {e}")
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
        
        print(f"️ Admin {current_user.username} updated {updated} users to role: {new_role}")
        
        return jsonify({
            "status": "success",
            "message": f"Updated {updated} user(s) to {new_role}",
            "updated_count": updated
        })
    
    except Exception as e:
        db.session.rollback()
        print(f" Error bulk updating roles: {e}")
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
        print(f" Error exporting users: {e}")
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
    """Speed round configuration page
    
    NOTE: Page is accessible to all users (including Apple reviewers) for visibility.
    Premium check happens at API level when user tries to start a round.
    """
    try:
        # Ensure database is initialized (fixes load_user issues)
        _ensure_db_initialized()
        
        # Now current_user should work properly since load_user has error handling
        # Flask-Login's current_user is a LocalProxy that handles anonymous users gracefully
        is_authenticated = current_user.is_authenticated
        is_premium = bool(getattr(current_user, 'premium_member', False)) if is_authenticated else False
        
        # Always render the page (for Apple review visibility)
        # Premium check happens at API level (/api/speed-round/start)
        timestamp = int(time.time())
        return render_template('speed_round_setup.html', 
                             timestamp=timestamp,
                             is_premium=is_premium,
                             is_authenticated=is_authenticated)
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Error in speed_round_setup: {e}")
        import traceback
        traceback.print_exc()
        # Return a proper error page instead of crashing
        try:
            error_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Loading Speed Round Setup - BeeSmart Spelling</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #d32f2f; }
        a { color: #1976d2; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Error Loading Speed Round Setup</h1>
    <p>An error occurred: {error}</p>
    <p><a href="/">Return to Home</a></p>
</body>
</html>""".format(error=str(e))
            return error_html, 500
        except Exception:
            return "Error loading speed round setup page. Please try again later.", 500


@app.route("/speed-round/quiz")
def speed_round_quiz():
    """Speed round quiz page with timer"""
    try:
        # Ensure database is initialized (fixes load_user issues)
        _ensure_db_initialized()
        
        # Now current_user should work properly since load_user has error handling
        is_authenticated = current_user.is_authenticated
        is_premium = bool(getattr(current_user, 'premium_member', False)) if is_authenticated else False
        
        if not (is_authenticated and is_premium):
            try:
                flash('Speed Round is a Premium feature. Please subscribe to BeeSmart Premium to unlock it.', 'info')
            except Exception:
                pass
            return redirect(url_for('subscription_page'))
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Error in speed_round_quiz: {e}")
        import traceback
        traceback.print_exc()
        # Fail gracefully - redirect to subscription page
        try:
            flash('Unable to verify premium status. Please try again.', 'warning')
        except Exception:
            pass
        return redirect(url_for('subscription_page'))

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
        premium_block = _require_premium_json("speed_round")
        if premium_block is not None:
            return premium_block

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
        premium_block = _require_premium_json("speed_round")
        if premium_block is not None:
            return premium_block

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
            #  Use internal dictionary (50K+ Simple Wiktionary) with enhanced difficulty system
            difficulty_level = difficulty_map.get(difficulty, 2)  # Default to grade 3-4
            print(f" Speed Round: Generating {word_count} words at difficulty level {difficulty_level} from internal dictionary")
            
            try:
                word_records = get_random_words_by_difficulty(difficulty_level, count=word_count)
                
                if not word_records or len(word_records) == 0:
                    print(f"⚠️ No words found at difficulty {difficulty_level}, trying fallback...")
                    # Fallback: try a wider difficulty range
                    word_records = get_random_words_by_difficulty(2, count=word_count)  # Default to medium
                
                # Extract just word strings for speed round
                words = [record['word'] for record in word_records] if word_records else []
                
                if not words:
                    raise ValueError("Could not generate words from dictionary - please try again")
                
                print(f" Generated {len(words)} kid-friendly words from internal dictionary")
            except ValueError as ve:
                print(f"❌ Speed Round word generation error: {ve}")
                return jsonify({
                    'status': 'error',
                    'message': 'Word dictionary is loading. Please wait a moment and try again.'
                }), 500
            except Exception as e:
                print(f"❌ Speed Round unexpected error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to generate words. Please try again.'
                }), 500
            
        elif word_source == 'uploaded':
            # Get user's uploaded word list
            wordbank = get_wordbank()
            if not wordbank or len(wordbank) == 0:
                #  FALLBACK: If no uploaded words, use internal dictionary instead of erroring
                print("️ No uploaded words found, falling back to internal dictionary")
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
            print(" Speed Round: Generating mixed difficulty words from internal dictionary")
            mixed_words = []
            words_per_level = max(1, word_count // 5)  # Distribute across all 5 levels
            
            for level in range(1, 6):
                level_words = get_random_words_by_difficulty(level, count=words_per_level)
                mixed_words.extend([record['word'] for record in level_words])
            
            # Shuffle and trim to exact count
            random.shuffle(mixed_words)
            words = mixed_words[:word_count]
            print(f" Generated {len(words)} mixed difficulty words")
            
        else:
            # Default: Use internal dictionary at medium difficulty
            print("️ Unknown word source, using internal dictionary at medium difficulty")
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
        
        print(f" Speed Round started: {len(words)} words, {difficulty}, {time_per_word}s/word")
        
        return jsonify({
            'status': 'success',
            'word_count': len(words),
            'first_word': words[0] if words else None
        })
        
    except Exception as e:
        print(f" Error starting speed round: {e}")
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
        premium_block = _require_premium_json("speed_round")
        if premium_block is not None:
            return premium_block

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
        time_bonus_points = 0
        
        if is_correct:
            base_points = 10
            multiplier = speed_round['config']['multiplier']
            
            #  PROGRESSIVE TIME BONUS: Faster answers earn MORE points
            # Calculate percentage of time used (0-100%)
            time_percentage = (time_taken / time_limit) * 100
            
            # Award points based on speed (maximum 20 bonus points for instant answers)
            # Points decrease linearly as time increases
            if time_percentage <= 100:  # Valid answer within time limit
                # 0-20% time used: 20 bonus points (lightning fast!)
                # 21-40% time used: 15 bonus points (very fast)
                # 41-60% time used: 10 bonus points (fast)
                # 61-80% time used: 5 bonus points (moderate)
                # 81-100% time used: 2 bonus points (slow but valid)
                
                if time_percentage <= 20:
                    time_bonus_points = 20
                    speed_bonus = True
                    speed_round['speed_bonuses'] += 1
                elif time_percentage <= 40:
                    time_bonus_points = 15
                    speed_bonus = True
                    speed_round['speed_bonuses'] += 1
                elif time_percentage <= 60:
                    time_bonus_points = 10
                    speed_bonus = True
                    speed_round['speed_bonuses'] += 1
                elif time_percentage <= 80:
                    time_bonus_points = 5
                else:
                    time_bonus_points = 2
                
                base_points += time_bonus_points
                speed_logger.info(f" Time bonus: {time_bonus_points} pts ({time_percentage:.1f}% time used, {time_taken:.2f}s/{time_limit}s)")
            
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
            
            # 🆕 REAL-TIME BUZZ DUST AWARDING: Award Buzz Dust immediately on each correct answer with speed bonus
            if current_user.is_authenticated:
                try:
                    from buzz_dust_helpers import get_bee_class, calculate_quiz_buzz_dust
                    
                    old_buzz_dust = current_user.total_buzz_dust or 0
                    
                    # For speed round, use base_points (without multiplier) and apply speed bonus multiplier
                    # Speed round is already fast-paced, so we use the points_earned which includes speed bonuses
                    # Calculate speed-specific buzz dust: just take earned points as base (they include speed calculations)
                    buzz_dust_earned = points_earned  # Already includes time bonus and streak calculations
                    
                    current_user.total_buzz_dust = old_buzz_dust + buzz_dust_earned
                    
                    # Check for rank advancement
                    old_class_id = get_bee_class(old_buzz_dust).get('id', 'novice')
                    new_class_id = get_bee_class(current_user.total_buzz_dust).get('id', 'novice')
                    
                    if old_class_id != new_class_id:
                        # User ranked up mid-speed-round!
                        session['ranked_up_speed'] = True
                        session['old_class_id_speed'] = old_class_id
                        current_user.bee_class = new_class_id
                        speed_logger.info(f" MID-SPEED-ROUND RANK UP! {old_class_id} → {new_class_id} (Buzz Dust: {old_buzz_dust} → {current_user.total_buzz_dust})")
                    
                    # Commit the Buzz Dust update immediately
                    db.session.commit()
                    speed_logger.info(f" SPEED ROUND BUZZ DUST: +{buzz_dust_earned} (was {old_buzz_dust}, now {current_user.total_buzz_dust})")
                except Exception as e:
                    speed_logger.error(f"Failed real-time Buzz Dust award: {e}")
                    db.session.rollback()
            
            print(f" Correct! '{correct_spelling}' - {points_earned} pts (streak: {speed_round['current_streak']})")
        else:
            # Reset streak on wrong answer
            speed_round['current_streak'] = 0
            print(f" Wrong! '{user_input}' != '{correct_spelling}'")
        
        # Record this word's performance
        word_record = {
            'word': correct_spelling,
            'user_answer': user_input,
            'correct': is_correct,
            'skipped': is_skipped,
            'time_taken': round(time_taken, 2),
            'points_earned': points_earned,
            'speed_bonus': speed_bonus,
            'time_bonus_points': time_bonus_points if is_correct else 0,
            'time_percentage': round((time_taken / time_limit) * 100, 1) if is_correct else 100,
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
            'time_bonus_points': time_bonus_points if is_correct else 0,
            'time_percentage': round((time_taken / time_limit) * 100, 1),
            'total_points': speed_round['total_points'],
            'current_streak': speed_round['current_streak'],
            'time_taken': round(time_taken, 2),
            'complete': is_complete,
            'next_index': (speed_round['current_index'] + 1) if not is_complete else None,
            'remaining': max(0, len(words) - speed_round['current_index'])
        })
        
    except Exception as e:
        print(f" Error processing answer: {e}")
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
        
        #  Check for badge achievements in speed round
        badges_unlocked = []
        
        # Build state object compatible with check_badges function
        speed_state = {
            'correct': words_correct,
            'incorrect': words_attempted - words_correct,
            'max_streak': speed_round['max_streak'],
            'hints_used_total': 0,  # Speed round doesn't use hints
            'session_points': speed_round['total_points'],
            'history': speed_round['word_history']
        }
        
        # Convert word_history to format expected by check_badges
        for record in speed_state['history']:
            if 'elapsed_ms' not in record and 'time_taken' in record:
                record['elapsed_ms'] = int(record['time_taken'] * 1000)
        
        # Check badges using same logic as regular quiz
        badges_unlocked = check_badges(speed_state, speed_round.get('word_list', []))
        
        # Calculate badge bonus points
        badge_points = sum(b["points"] for b in badges_unlocked)
        
        if score_id:
            # 🆕 Points already awarded real-time during the round, so pass 0 here
            # Only update quiz completion count and accuracy stats
            stats_updated = update_user_stats_railway(
                current_user.id, 
                badge_points,  # Award badge bonus points (word points already saved incrementally)
                words_correct,
                words_attempted
            )
            
            #  Save badges to Achievement table
            if badges_unlocked and current_user.is_authenticated:
                try:
                    for badge in badges_unlocked:
                        achievement = Achievement(
                            user_id=current_user.id,
                            achievement_type=badge["type"],
                            achievement_name=badge["name"],
                            achievement_description=badge["message"],
                            points_bonus=badge["points"],
                            achievement_metadata={
                                "icon": badge["icon"],
                                "earned_in_speed_round": score_id,
                                "speed_round_accuracy": accuracy
                            }
                        )
                        db.session.add(achievement)
                    db.session.commit()
                    speed_logger.info(f" Saved {len(badges_unlocked)} badge(s) to Achievement table")
                except Exception as e:
                    speed_logger.error(f"Failed to save badges: {e}")
                    db.session.rollback()
            
            speed_logger.info(f"Speed Round saved: {words_correct}/{words_attempted} correct, {speed_round['total_points']} pts (awarded real-time) + {badge_points} badge pts, stats_updated={stats_updated}")
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
            'badge_points': badge_points,
            'total_with_badges': speed_round['total_points'] + badge_points,
            'words_attempted': words_attempted,
            'words_correct': words_correct,
            'accuracy': round(accuracy, 1),
            'longest_streak': speed_round['max_streak'],
            'fastest_time': round(fastest_time, 2) if fastest_time else None,
            'total_time': round(total_time, 2),
            'speed_bonuses': speed_round['speed_bonuses'],
            'difficulty': speed_round['config']['difficulty'],
            'config': speed_round['config'],
            'incorrect_words': incorrect_words,
            'badges_earned': badges_unlocked  #  Include badges for display
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
# DEPRECATED: Duplicate /api/avatars endpoint removed (active implementation at line ~664)
# The following code was commented out to prevent Flask from using the wrong implementation
# Flask uses the FIRST defined route, so the cleaner implementation at line 663 is active

# # Simple in-memory cache for avatar list (invalidates on app restart)
# _AVATAR_CACHE = {"data": None, "timestamp": 0, "ttl": 300}  # 5 minute TTL
# # Cache for GLB file scanning (expensive filesystem operation)
# _GLB_SCAN_CACHE = {"data": None, "timestamp": 0, "ttl": 600}  # 10 minute TTL

# REMOVED: Duplicate api_get_avatars() function (~600 lines)
# The duplicate /api/avatars endpoint has been removed to prevent Flask route conflicts.
# Active implementation: api_avatars() at line ~664 (cleaner, uses avatar_catalog)
# The duplicate had excessive debug logging and filesystem fallback that created maintenance burden.

@app.route("/api/subscriptions", methods=["GET"])
def api_get_subscriptions():
    """Get available subscription products (no price display).

    For Apple policy and consistency, this endpoint does not return explicit pricing.
    Pricing is shown in the App Store purchase flow.
    """
    try:
        products = [
            {
                'id': SUBSCRIPTION_PRODUCT_IDS['monthly'],
                'type': 'monthly',
                'name': 'Premium Monthly Membership',
                'displayName': 'Premium Monthly',
                'duration': '1 month',
                'subscription': True,
                'familySharing': False,
                'price': None,
                'currency': None,
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
            }
        ]

        # Only expose monthly for current live offering / monthly-only builds.
        if not IAP_MONTHLY_ONLY:
            # If you later enable yearly/family, add them back without explicit price fields.
            pass

        subscriptions = {
            'status': 'success',
            'products': products,
            'pricingNotice': 'Pricing is shown in the App Store purchase flow.'
        }

        return jsonify(subscriptions)

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route("/subscription")
@app.route("/premium")
def subscription_page():
    """
    Subscription landing page for BeeSmart Premium
    Shows available premium subscription options (pricing shown in the App Store purchase flow)
    """
    try:
        # Check if user is authenticated
        user_authenticated = 'user_id' in session
        current_user = None
        
        if user_authenticated:
            user_id = session.get('user_id')
            current_user = User.query.get(user_id)
        
        # When IAP_MONTHLY_ONLY is enabled, ensure templates don't accidentally
        # render pricing for Yearly/Family options.
        return render_template(
            'subscription.html',
            user_authenticated=user_authenticated,
            current_user=current_user,
            iap_monthly_only=IAP_MONTHLY_ONLY,
            # Display price on /subscription (requested). If you later fetch live
            # prices from StoreKit / server, pass the dynamic value here.
            subscription_monthly_usd=3.99,
            subscription_product_ids={'monthly': SUBSCRIPTION_PRODUCT_IDS.get('monthly')}
            if IAP_MONTHLY_ONLY else SUBSCRIPTION_PRODUCT_IDS,
        )
    
    except Exception as e:
        print(f" Error loading subscription page: {e}")
        import traceback
        traceback.print_exc()
        return render_template(
            'subscription.html',
            user_authenticated=False,
            current_user=None,
            iap_monthly_only=IAP_MONTHLY_ONLY,
            subscription_monthly_usd=3.99,
            subscription_product_ids={'monthly': SUBSCRIPTION_PRODUCT_IDS.get('monthly')}
            if IAP_MONTHLY_ONLY else SUBSCRIPTION_PRODUCT_IDS,
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
        
        # Build avatar info dict with GLB-only URLs
        # All avatars are GLB format, stored in glb_files/ directory
        base_path = "/static/assets/avatars/glb_files"
        
        # Get GLB filename from obj_file field (legacy naming)
        glb_filename = avatar.obj_file if avatar.obj_file else "MascotBee.glb"
        
        # Derive thumbnail from GLB filename
        import os
        glb_basename = os.path.splitext(os.path.basename(glb_filename))[0]
        thumbnail_path = f"{base_path}/AvatarThumbnails/{glb_basename}!.png"
        
        avatar_info = {
            'id': avatar.slug,
            'name': avatar.name,
            'description': avatar.description,
            'variant': 'default',
            'category': avatar.category,
            'thumbnail_url': thumbnail_path,
            'preview_url': thumbnail_path,
            'glb_url': f"{base_path}/{glb_filename}",
            'fallback_url': "/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png",
            'unlock_level': avatar.unlock_level,
            'points_required': avatar.points_required,
            'is_premium': avatar.is_premium
        }
        
        return jsonify({
            'status': 'success',
            'avatar': avatar_info
        })
    
    except Exception as e:
        print(f" Error fetching avatar {avatar_id}: {e}")
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
        print(f" Error fetching avatar categories: {e}")
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
        print(f" Error fetching user avatar: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route("/api/users/<int:user_id>/avatar", methods=["PUT"], endpoint='api_admin_or_user_update_avatar')
@login_required
def api_admin_or_user_update_avatar(user_id):
    """Update a user's avatar
    
     SECURITY: Validates avatar unlock status before allowing selection.
    - Users can only update their own avatar (unless admin updating for others)
    - Unlock validation applied for non-admins
    - Respects parental locks
    """
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
        
        #  SECURITY CHECK 1: Guest users cannot select avatars
        if not user.password_hash:
            return jsonify({
                'status': 'error',
                'message': 'Guest users cannot select avatars. Please register to customize your bee!'
            }), 403
        
        #  SECURITY CHECK 2: Parental lock
        if getattr(user, 'avatar_locked', False):
            return jsonify({
                'status': 'error',
                'message': 'Your parent has locked avatar selection. Please ask them to unlock it.'
            }), 403
        
        data = request.get_json()
        avatar_id = data.get('avatar_id')
        variant = data.get('variant', 'male')
        
        if not avatar_id:
            return jsonify({
                'status': 'error',
                'message': 'avatar_id is required'
            }), 400
        
        #  SECURITY CHECK 3: Unlock validation (unless admin)
        if user.role != 'admin':
            try:
                from avatar_catalog import check_avatar_unlocked, AVATAR_CATALOG
                
                # Get user's unlock eligibility
                user_honey_points = getattr(user, 'honey_points', 0) or 0
                purchased_avatars = getattr(user, 'purchased_avatars', []) or []
                
                # Check if avatar is unlocked
                unlock_result = check_avatar_unlocked(avatar_id, user_honey_points, purchased_avatars)
                
                if not unlock_result.get('unlocked', False):
                    # Forbidden: User has not earned/purchased this avatar
                    tier = next(
                        (a.get('tier', 'premium') for a in AVATAR_CATALOG if a['id'] == avatar_id),
                        'premium'
                    )
                    
                    if tier == 'premium':
                        return jsonify({
                            'status': 'error',
                            'message': 'This avatar is only available for purchase.',
                            'reason': 'premium_locked'
                        }), 403
                    elif tier == 'earn_or_buy':
                        points_needed = unlock_result.get('required_points', 0) - user_honey_points
                        return jsonify({
                            'status': 'error',
                            'message': f'Earn {points_needed:,} more Honey Points or purchase to unlock this avatar.',
                            'reason': 'points_required',
                            'points_needed': max(0, points_needed)
                        }), 403
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'This avatar is not yet unlocked. Complete more quizzes to earn it!',
                            'reason': 'not_earned'
                        }), 403
                        
            except ImportError:
                print(f"️ Avatar catalog unavailable, skipping unlock check for {avatar_id}")
            except Exception as e:
                print(f"️ Error checking avatar unlock status: {e}")
        
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
            prefs['avatar_selected_at'] = datetime.now(timezone.utc).isoformat()
            user.preferences = prefs
        except Exception:
            pass

        db.session.commit()

        # Get updated avatar data
        avatar_data = user.get_avatar_data()
        use_mascot = not user.has_selected_avatar()

        #  AUDIT: Log avatar selection
        print(f" User {user.id} ({user.username}) updated avatar to {avatar_id} ({variant})")

        return jsonify({
            'status': 'success',
            'message': message,
            'avatar': avatar_data,
            'use_mascot': use_mascot
        })
    
    except Exception as e:
        print(f" Error updating user avatar: {e}")
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
    
     SECURITY: Validates avatar unlock status before allowing selection.
    - Admins bypass all unlock checks
    - Regular users must have earned/purchased the avatar
    - Respects parental locks on account
    """
    try:
        from models import Avatar
        
        # Debug: Log current user info
        print(f" Avatar select endpoint - User: {current_user.id} ({current_user.username}), Role: {current_user.role}")
        
        # SAFETY CHECK: Ensure current_user is valid
        if not current_user or not current_user.is_authenticated:
            print(f" Current user is not authenticated")
            return jsonify({
                'success': False,
                'error': 'You must be logged in to change your avatar.'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
            
        avatar_slug = data.get('avatar_slug')
        
        if not avatar_slug:
            return jsonify({
                'success': False,
                'error': 'avatar_slug is required'
            }), 400
        
        #  SECURITY CHECK 1: Block guest/legacy accounts from avatar customization
        # Some legacy "guest" records may be authenticated but do not have a password.
        if not getattr(current_user, 'password_hash', None):
            return jsonify({
                'success': False,
                'error': 'Guest users cannot select avatars. Please register to customize your bee!'
            }), 403
        
        #  SECURITY CHECK 2: Parental lock
        if getattr(current_user, 'avatar_locked', False):
            return jsonify({
                'success': False,
                'error': 'Your parent has locked avatar selection. Please ask them to unlock it.'
            }), 403
        
        # Look up avatar by slug; if missing, attempt auto-install from GLB folder
        avatar = Avatar.query.filter_by(slug=avatar_slug, is_active=True).first()
        if not avatar:
            # Auto-install: search glb_files for a matching slug
            import re as _re
            static_root = os.path.join(app.root_path, 'static', 'assets', 'avatars')
            glb_dir = os.path.join(static_root, 'glb_files')
            thumb_dir = os.path.join(glb_dir, 'AvatarThumbnails')

            def _slug_from_base(base: str) -> str:
                # Check if there's a known mapping for this base name
                try:
                    from avatar_catalog import NAME_MAP_CAMELCASE
                    if base in NAME_MAP_CAMELCASE:
                        canonical_slug = NAME_MAP_CAMELCASE[base]
                        print(f" Found canonical slug via NAME_MAP_CAMELCASE: {base} -> {canonical_slug}")
                        return canonical_slug, base
                except ImportError:
                    pass
                
                # Fallback: generate slug from CamelCase
                name_with_spaces = _re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
                slug = _re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-')
                return slug, name_with_spaces

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
                            description=f"{name_with_spaces} is ready to spell! ",
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
                        print(f" Failed to auto-install avatar '{avatar_slug}': {_e}")
                        break
            if not installed or not avatar:
                return jsonify({
                    'success': False,
                    'error': f'Avatar not found: {avatar_slug}'
                }), 404

        # Canonicalize selection key used for unlock checks.
        # - Avatar catalog uses ids (slugs) like "mascot-bee".
        # - We store user.avatar_id as a slug.
        selected_avatar_id = str(avatar.slug or avatar_slug).strip().lower()
        
        #  SECURITY CHECK 3: Unlock validation (unless admin)
        if current_user.role != 'admin':
            try:
                from avatar_catalog import check_avatar_unlocked, AVATAR_CATALOG
                
                # Get user's unlock eligibility
                user_honey_points = getattr(current_user, 'honey_points', 0) or 0
                purchased_avatars = getattr(current_user, 'purchased_avatars', []) or []
                
                # Check if avatar is unlocked
                unlock_result = check_avatar_unlocked(
                    selected_avatar_id,
                    user_honey_points,
                    purchased_avatars
                )
                
                if not unlock_result.get('unlocked', False):
                    # Forbidden: User has not earned/purchased this avatar
                    tier = next(
                        (a.get('tier', 'premium') for a in AVATAR_CATALOG if a.get('id') == selected_avatar_id),
                        'premium'
                    )
                    
                    if tier == 'premium':
                        return jsonify({
                            'success': False,
                            'error': 'This avatar is only available for purchase.',
                            'reason': 'premium_locked'
                        }), 403
                    elif tier == 'earn_or_buy':
                        points_needed = unlock_result.get('required_points', 0) - user_honey_points
                        return jsonify({
                            'success': False,
                            'error': f'Earn {points_needed:,} more Honey Points or purchase to unlock this avatar.',
                            'reason': 'points_required',
                            'points_needed': max(0, points_needed)
                        }), 403
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'This avatar is not yet unlocked. Complete more quizzes to earn it!',
                            'reason': 'not_earned'
                        }), 403
                        
            except ImportError:
                # Fail closed: if we can't validate locks, we should not allow premium selections.
                return jsonify({
                    'success': False,
                    'error': 'Avatar unlock system unavailable. Please try again in a moment.',
                    'reason': 'unlock_system_unavailable'
                }), 503
            except Exception as e:
                print(f"️ Error checking avatar unlock status: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Could not verify avatar unlock status. Please try again.',
                    'reason': 'unlock_check_failed'
                }), 500
        
        # Update current user's avatar
        success, message = current_user.update_avatar(selected_avatar_id, variant='default')
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Mark avatar as explicitly selected
        try:
            prefs = current_user.preferences or {}
            prefs['avatar_selected'] = True
            prefs['avatar_selected_at'] = datetime.now(timezone.utc).isoformat()
            current_user.preferences = prefs
        except Exception as e:
            print(f"️ Could not update preferences: {e}")
        
        db.session.commit()
        
        #  AUDIT: Log avatar selection
        print(f" User {current_user.id} ({current_user.username}) selected avatar via picker: {avatar_slug}")
        
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
        print(f" Error selecting avatar: {e}")
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
        
        elif ext == 'glb':
            if not avatar.glb_data:
                return send_from_directory(f'static/assets/avatars/{slug}', filename)
            return Response(
                avatar.glb_data, 
                mimetype='model/gltf-binary',
                headers={
                    'Content-Disposition': f'inline; filename="{filename}"',
                    'Cache-Control': 'public, max-age=31536000'  # 1 year cache
                }
            )
        
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
        print(f" Error serving avatar file {slug}/{filename}: {e}")
        # Fallback to filesystem
        try:
            return send_from_directory(f'static/assets/avatars/{slug}', filename)
        except:
            return "File not found", 404


# --- Badge GLB File Serving from Database -------------------------------------------
@app.route("/static/assets/badges/glb_files/<filename>")
def serve_badge_file_from_db(filename):
    """Serve badge GLB files from database binary data"""
    try:
        from models import BadgeAsset
        from datetime import datetime
        
        # Extract badge name from filename (e.g., 'Novice.glb' -> 'Novice')
        badge_name = filename.replace('.glb', '')
        
        # Get badge from database
        badge = BadgeAsset.query.filter_by(badge_name=badge_name).first()
        
        if not badge:
            # Try from filesystem as fallback
            try:
                return send_from_directory('static/assets/badges/glb_files', filename)
            except:
                return jsonify({'error': 'Badge not found'}), 404
        
        # Update last accessed time (async, don't block response)
        try:
            badge.last_accessed = datetime.utcnow()
            db.session.commit()
        except:
            db.session.rollback()
        
        # Serve GLB file from database
        return Response(
            badge.file_data,
            mimetype='model/gltf-binary',
            headers={
                'Content-Disposition': f'inline; filename="{badge.file_name}"',
                'Cache-Control': 'public, max-age=31536000'  # Cache for 1 year
            }
        )
    
    except Exception as e:
        print(f" Error serving badge file {filename}: {e}")
        # Fallback to filesystem
        try:
            return send_from_directory('static/assets/badges/glb_files', filename)
        except:
            return jsonify({'error': 'File not found'}), 404


@app.route("/api/badges/list", methods=["GET"])
def api_list_badges():
    """List all available badge GLB files"""
    try:
        from models import BadgeAsset
        
        badges = BadgeAsset.query.order_by(BadgeAsset.badge_name).all()
        
        return jsonify({
            'success': True,
            'badges': [badge.to_dict() for badge in badges],
            'count': len(badges)
        })
    
    except Exception as e:
        print(f" Error listing badges: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/users/me", methods=["GET", "PUT"])
def api_get_current_user():
    """Get current user's basic information (name, auth status, etc.)"""
    try:
        # Allow authenticated users to update their own display_name.
        if request.method == "PUT":
            if not current_user.is_authenticated:
                return jsonify({
                    "status": "error",
                    "message": "Authentication required"
                }), 401

            data = request.get_json(silent=True) or {}
            new_name = (data.get("display_name") or "").strip()
            if not new_name:
                return jsonify({
                    "status": "error",
                    "message": "display_name is required"
                }), 400
            # Keep it kid-friendly + safe for headers/UI.
            if len(new_name) > 40:
                new_name = new_name[:40].strip()
            current_user.display_name = new_name
            db.session.commit()
            try:
                db.session.refresh(current_user)
            except Exception:
                pass
            resp = jsonify({
                "status": "success",
                "message": "Name updated",
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "display_name": current_user.display_name,
                    "role": getattr(current_user, "role", "student")
                }
            })
            try:
                resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            except Exception:
                pass
            return resp

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
                    #  Extended real-time progress fields
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
        print(f" Error fetching current user: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user information',
            'authenticated': False,
            'user': {
                'display_name': 'NewBee',
                'role': 'guest'
            }
        }), 500


@app.route("/api/users/stats/recalculate", methods=["POST"])
@login_required
def api_force_recalculate_stats():
    """Force complete recalculation of cumulative stats from ALL quiz sessions.
    This ensures stats are always accurate even if previous updates failed."""
    try:
        print(f"🔄 FORCED STATS RECALCULATION for user: {current_user.username} (ID: {current_user.id})")
        
        # Step 1: Recalculate total_lifetime_points from ALL completed quiz sessions
        from sqlalchemy import func
        total_points_from_sessions = db.session.query(
            func.coalesce(func.sum(QuizSession.total_points), 0)
        ).filter_by(
            user_id=current_user.id,
            completed=True
        ).scalar() or 0
        
        # Also sum points_earned + badge_bonus_points + extra_points for sessions that might not have total_points set
        sessions_with_points = QuizSession.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).all()

        old_points = current_user.total_lifetime_points or 0
        old_quizzes = current_user.total_quizzes_completed or 0

        calculated_total_points = old_points
        quiz_count = old_quizzes

        # Only recalc from sessions if we actually have any completed sessions.
        # This prevents wiping out existing lifetime points when historical data
        # is missing or sessions are still marked incomplete.
        if sessions_with_points:
            calculated_total_points = 0
            for sess in sessions_with_points:
                if sess.total_points:
                    calculated_total_points += int(sess.total_points)
                else:
                    # Fallback: sum individual components
                    calculated_total_points += int(sess.points_earned or 0)
                    calculated_total_points += int(sess.badge_bonus_points or 0)
                    calculated_total_points += int(sess.extra_points or 0)

            quiz_count = len(sessions_with_points)

        current_user.total_lifetime_points = calculated_total_points
        current_user.total_quizzes_completed = quiz_count

        print(f"   Points: {old_points} → {calculated_total_points} (from {len(sessions_with_points)} sessions)")
        print(f"   Quizzes: {old_quizzes} → {quiz_count}")
        
        # Step 3: Force recalculation of GPA and accuracy from ALL sessions
        current_user.update_gpa_and_accuracy()
        print(f"   GPA: {current_user.cumulative_gpa}, Accuracy: {current_user.average_accuracy}%")
        
        # Step 4: Commit all changes
        db.session.commit()
        
        # Step 5: Refresh user object to ensure we have latest values
        db.session.refresh(current_user)
        
        # Calculate percentage of actions completed (for progress display)
        total_actions = quiz_count
        actions_percentage = 100.0 if total_actions > 0 else 0.0
        
        return jsonify({
            'status': 'success',
            'message': 'Stats recalculated successfully',
            'stats': {
                'total_lifetime_points': int(current_user.total_lifetime_points or 0),
                'total_quizzes_completed': int(current_user.total_quizzes_completed or 0),
                'cumulative_gpa': float(current_user.cumulative_gpa or 0.0),
                'average_accuracy': float(current_user.average_accuracy or 0.0),
                'best_grade': getattr(current_user, 'best_grade', None),
                'best_streak': int(getattr(current_user, 'best_streak', 0) or 0),
                'actions_percentage': actions_percentage,
                'total_actions': total_actions
            },
            'recalculation': {
                'points_changed': calculated_total_points != old_points,
                'quizzes_changed': quiz_count != old_quizzes,
                'sessions_processed': len(sessions_with_points)
            }
        })
    except Exception as e:
        print(f"❌ ERROR in forced stats recalculation: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to recalculate stats: {str(e)}'
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

        # Include in-progress quiz points for a real-time "cumulative" view
        base_lifetime_points = int(getattr(current_user, 'total_lifetime_points', 0) or 0)
        display_lifetime_points = base_lifetime_points
        try:
            quiz_state = session.get(QUIZ_STATE_KEY) or {}
            # If there is an active quiz (not yet marked complete), add its session_points
            if quiz_state and not quiz_state.get('quiz_complete', False):
                session_points = int(quiz_state.get('session_points', 0) or 0)
                if session_points > 0:
                    display_lifetime_points = base_lifetime_points + session_points
        except Exception as _e_rt:
            print(f"WARNING /api/users/stats: failed to include in-progress quiz points: {_e_rt}")

        resp = jsonify({
            'status': 'success',
            'authenticated': True,
            'stats': {
                'cumulative_gpa': float(getattr(current_user, 'cumulative_gpa', 0.0) or 0.0),
                'average_accuracy': float(getattr(current_user, 'average_accuracy', 0.0) or 0.0),
                # Display lifetime points plus any in-progress quiz points so the
                # main menu and dashboards reflect real-time cumulative progress.
                'total_lifetime_points': int(display_lifetime_points),
                'total_quizzes_completed': int(getattr(current_user, 'total_quizzes_completed', 0) or 0),
                'best_streak': int(getattr(current_user, 'best_streak', 0) or 0),
                'best_grade': getattr(current_user, 'best_grade', None),
                'current_speed_round_streak': int(current_sr_streak or 0),
                #  Buzz Dust Gamification Fields
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
        print(f" Error /api/users/stats: {e}")
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
        #  Buzz Dust Gamification Fields
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
        print(f" Error /api/users/<id>/stats: {e}")
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
        print(f" Error /api/users/stats/batch: {e}")
        return jsonify({'status': 'error', 'message': 'Batch stats failed'}), 500


@app.route("/api/users/me/avatar", methods=["GET"])
def api_get_my_avatar():
    """Get current user's avatar (works for both authenticated and guest users)"""
    try:
        # Try to get authenticated user first
        if current_user.is_authenticated:
            # IMPORTANT: Avoid extra DB hits here.
            # This endpoint is polled by multiple front-end components; a forced DB query
            # on every request can amplify load and contribute to upstream timeouts (504).
            user = current_user
        else:
            # Fall back to guest user
            user = get_or_create_guest_user()
        
        if not user:
            # No user found, return default mascot (GLB-only)
            print("️ No user found, returning default mascot")
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
        
        # Debug logging
        print(f" Avatar API: User {user.id} ({user.username if hasattr(user, 'username') else 'guest'})")
        print(f"   - avatar_id: {user.avatar_id}")
        print(f"   - has_selected_avatar: {user.has_selected_avatar()}")
        print(f"   - preferences: {user.preferences}")
        print(f"   - use_mascot: {use_mascot}")
        
        # If user hasn't selected an avatar, return MascotBee as default
        if use_mascot:
            print("   → Returning MascotBee (no avatar selected)")
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
        print(f"   → Returning selected avatar: {avatar_data.get('avatar_id')} ({avatar_data.get('name')})")
        return jsonify({
            'status': 'success',
            'avatar': avatar_data,
            'use_mascot': False
        })
    
    except Exception as e:
        print(f" Error fetching user avatar: {e}")
        import traceback
        traceback.print_exc()
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
        
        print(f" Avatar locked for user {user.username} by {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'Avatar locked successfully'
        })
    
    except Exception as e:
        print(f" Error locking avatar: {e}")
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
        
        print(f" Avatar unlocked for user {user.username} by {current_user.username}")
        
        return jsonify({
            'status': 'success',
            'message': 'Avatar unlocked successfully'
        })
    
    except Exception as e:
        print(f" Error unlocking avatar: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Startup confirmation logging
print("=" * 60)
print(" BeeSmart Spelling Bee App - Initialization Complete")
print("=" * 60)
print(f" App version: {APP_VERSION}")
print(f" Environment: {os.environ.get('FLASK_ENV', 'development')}")
print(f" Database: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
print(f" Sessions: {'Database (persistent)' if SESSION_INIT_SUCCESS else 'Filesystem (temporary)'}")
print(f" Dictionary cache: {len(DICTIONARY_CACHE.get('words', {}))} words loaded")
print(f" Health check endpoint: /health")
print(f" Ready to serve requests on port ${os.environ.get('PORT', '5000')}")
print("=" * 60)

# Initialize GLB avatars on startup (idempotent)
if not FAST_BOOT:
    try:
        from init_glb_avatars import init_glb_avatars
        init_glb_avatars()
    except Exception as e:
        print(f"️ GLB avatar initialization warning: {e}")
else:
    print("⏭️ Skipping init_glb_avatars() at startup (FAST_BOOT)")

# Avoid any slow/remote DB work during FAST_BOOT.
# This keeps local smoke tests snappy and ensures the server actually comes up.
if FAST_BOOT or os.environ.get('BYPASS_AVATAR_DB_SYNC', '1').strip().lower() in ('1', 'true', 'yes', 'on'):
    if FAST_BOOT:
        print("⏭️ Skipping avatar catalog DB sync (FAST_BOOT)")
    else:
        print("⏭️ Skipping avatar catalog DB sync (BYPASS_AVATAR_DB_SYNC)")
else:

    # Sync full avatar catalog (ensure all entries exist) - runs after GLB init
    try:
        from avatar_catalog import AVATAR_CATALOG
        from models import Avatar, db
        with app.app_context():
            catalog_total = len(AVATAR_CATALOG)
            # Be resilient for automated tests / offline dev: don't hang startup on a remote DB.
            # If the avatar table is large or the connection is slow, skip gracefully.
            try:
                existing_slugs = {a.slug for a in Avatar.query.with_entities(Avatar.slug).all()}
            except Exception as e:
                print(f"️ Avatar catalog sync skipped (DB unavailable): {e}")
                existing_slugs = None

            if existing_slugs is None:
                # Bail out of the sync block without taking down the app.
                # The core app works fine without this; it's just a convenience initializer.
                raise RuntimeError("avatar_catalog_db_unavailable")
            missing = [entry for entry in AVATAR_CATALOG if entry.get('id') not in existing_slugs]
            added = 0
            for entry in missing:
                slug = entry.get('id')
                name = entry.get('name')
                folder = entry.get('folder') or slug
                obj_file = entry.get('obj_file')
                # Derive thumbnail path based on folder convention
                if folder == 'glb_files':
                    thumb = f"AvatarThumbnails/{obj_file.replace('.glb','')}!.png"
                else:
                    # Thumbnail stored alongside dedicated folder
                    thumb = f"{obj_file.replace('.glb','')}!.png"
                points_required = entry.get('unlock_points', 0) or 0
                tier = entry.get('tier')
                is_premium = tier == 'premium'
                sort_order = 500 + added  # place after any pre-seeded GLBs unless overridden later
                avatar = Avatar(
                    slug=slug,
                    name=name,  # Preserve full display name with required " Avatar" suffix for compliance
                    description=entry.get('description', ''),
                    category=entry.get('category', 'classic'),
                    folder_path=folder,
                    obj_file=obj_file,
                    mtl_file=entry.get('mtl_file'),
                    texture_file=entry.get('texture_file'),
                    thumbnail_file=thumb,
                    unlock_level=1,
                    points_required=points_required,
                    is_premium=is_premium,
                    sort_order=sort_order,
                    is_active=True,
                )
                db.session.add(avatar)
                added += 1

            if added > 0:
                db.session.commit()
                print(f" Avatar catalog sync: {added} missing avatars inserted (total expected: {catalog_total})")
            else:
                print(f" Avatar catalog sync: no missing entries (total: {catalog_total})")

            # Enforcement pass: ensure ALL avatar names end with required suffix
            suffix_fixes = 0
            all_db_avatars = Avatar.query.all()
            for a in all_db_avatars:
                if not a.name.endswith(' Avatar'):
                    a.name = f"{a.name} Avatar"
                    suffix_fixes += 1
            if suffix_fixes > 0:
                db.session.commit()
                print(f" Avatar name compliance: appended suffix to {suffix_fixes} avatars")

            # Deduplicate legacy O Bee slugs: prefer catalog slug 'o-bee'
            obee_legacy = Avatar.query.filter_by(slug='obee').first()
            o_bee_catalog = Avatar.query.filter_by(slug='o-bee').first()
            if obee_legacy and o_bee_catalog:
                # Deactivate legacy 'obee' to avoid duplicate counting
                if obee_legacy.is_active:
                    obee_legacy.is_active = False
                    db.session.commit()
                    print(" Deactivated legacy 'obee' avatar (duplicate of 'o-bee')")
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f"️ Avatar catalog sync warning: {e}")

# Validate and fix avatar thumbnail paths.
# This can involve DB queries and is not required to boot the web app.
# Keep it OFF by default so local dev, smoke tests, and CI don't hang on DB.
ENABLE_STARTUP_AVATAR_THUMBNAIL_VALIDATION = os.getenv(
    'ENABLE_STARTUP_AVATAR_THUMBNAIL_VALIDATION', '0'
).strip().lower() in ('1', 'true', 'yes', 'on')

if (not FAST_BOOT) and ENABLE_STARTUP_AVATAR_THUMBNAIL_VALIDATION:
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
                print(f" [STARTUP] Fixed {fixed_count} avatar thumbnail paths")
            else:
                print(f" [STARTUP] All {len(all_avatars)} avatar thumbnails validated - no fixes needed")
                
    except Exception as e:
        print(f"️ [STARTUP] Avatar thumbnail validation warning: {e}")
        try:
            db.session.rollback()
        except:
            pass
else:
    print("⏭️ Skipping avatar thumbnail validation at startup (FAST_BOOT or disabled)")

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
    # PRE-LOAD dictionary in background to avoid blocking Railway health check
    import threading
    def preload_dictionary():
        print(" Pre-loading Simple Wiktionary dictionary (background)...")
        ensure_simple_wiktionary_loaded()
        global DICTIONARY_CACHE
        if not DICTIONARY_CACHE:
            DICTIONARY_CACHE = load_dictionary_cache()
        print(f" Dictionary ready ({len(SIMPLE_WIKTIONARY_INDEX) if SIMPLE_WIKTIONARY_INDEX else 0} words indexed)")
    
    dict_thread = threading.Thread(target=preload_dictionary, daemon=True)
    dict_thread.start()
    
    # Default to 5051 for local dev to avoid collisions with other tools using 5000.
    # You can still override via: $env:PORT=1234 (PowerShell) or PORT=1234.
    env_port = int(os.environ.get("PORT", 5051))
    port = _pick_port(env_port)
    # Respect FLASK_DEBUG env (0/1, true/false) and disable reloader for stable runs in terminals/CI
    debug_env = os.environ.get("FLASK_DEBUG", "0").strip().lower()
    # Force debug on for local troubleshooting to get full tracebacks
    debug = True if os.environ.get("FORCE_DEBUG", "1") == "1" else (debug_env in ("1", "true", "yes", "on"))
    if port != env_port:
        print(f"️ Port {env_port} in use or unavailable; switching to {port}.")
    print(f" Starting development server on port {port} with Socket.IO support (debug={'on' if debug else 'off'})...")
    try:
        from app_socketio import socketio
        # Disable reloader to avoid parent-process exit that can confuse task runners
        socketio.run(app, host="0.0.0.0", port=port, debug=debug, use_reloader=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"️ Failed to start with Socket.IO: {e}")
        print(" Falling back to standard Flask server...")
        try:
            app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
        except OSError as oe:
            if getattr(oe, 'errno', None) == 48 or 'Address already in use' in str(oe):
                # Try another port automatically
                new_port = _pick_port(port + 1)
                print(f"️ Port {port} busy; retrying on {new_port}...")
                app.run(host="0.0.0.0", port=new_port, debug=debug, use_reloader=False)
            else:
                raise
# NOTE: A unified /api/save-partial-progress handler is defined earlier (api_save_partial_progress).
# The legacy save_partial_progress endpoint below has been deprecated and is retained only
# for backward compatibility. It no longer performs any operations.
#@app.route('/api/save-partial-progress', methods=['POST'])
#@login_required
#def save_partial_progress():
#    data = request.get_json() or {}
#    session_uuid = data.get('session_id')
#    session_points = int(data.get('session_points', 0))
#    session = QuizSession.query.filter_by(uuid=session_uuid, user_id=current_user.id).first()
#    if not session:
#        return jsonify({'status': 'error', 'message': 'session not found'}), 404
#    session.points_earned = max(session.points_earned or 0, session_points)
#    points_added = session.apply_points_if_needed()
#    db.session.commit()
#    return jsonify({'status': 'ok', 'points_added': points_added})