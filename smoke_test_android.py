#!/usr/bin/env python3
"""
BeeSmart Spelling Bee App - Android Smoke Test

Comprehensive smoke test for the entire app when accessed from Android.
Uses Android User-Agent for all HTTP requests to simulate Android WebView.
Verifies Android build config, critical pages, APIs, and Android-specific flows.

Usage:
    # Against local server (default http://localhost:5051)
    python smoke_test_android.py

    # Against production
    BASE_URL=https://beesmartspelling.app python smoke_test_android.py

    # Against custom URL
    BASE_URL=http://192.168.1.100:5000 python smoke_test_android.py

Optional env:
    BASE_URL - Target base URL (default: http://localhost:5051)
    SKIP_BUILD_CHECKS - Set to 1 to skip Android project file checks
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Run: pip install requests")
    sys.exit(1)

# Configuration
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5051").rstrip("/")
SKIP_BUILD_CHECKS = os.environ.get("SKIP_BUILD_CHECKS", "").lower() in ("1", "true", "yes")

# Android WebView User-Agent (Chrome on Android 13)
ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Build/TD1A.220804.031) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

TEST_RESULTS = []


def log_test(category: str, test_name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} [{category}] {test_name}")
    if details:
        print(f"   {details}")
    TEST_RESULTS.append({
        "category": category,
        "test": test_name,
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    })
    return passed


def session_with_android_ua():
    """Create requests session with Android User-Agent"""
    s = requests.Session()
    s.headers.update({"User-Agent": ANDROID_UA})
    return s


# ---------------------------------------------------------------------------
# 1. Android Build Config
# ---------------------------------------------------------------------------
def test_android_build_config():
    """Verify Android project structure and config"""
    print(f"\n{BOLD}{BLUE}=== Android Build Config ==={RESET}")

    if SKIP_BUILD_CHECKS:
        log_test("Build", "Build checks skipped (SKIP_BUILD_CHECKS=1)", True)
        return

    base = Path(__file__).parent

    # build.gradle
    build_gradle = base / "mobile" / "android" / "app" / "build.gradle"
    if build_gradle.exists():
        content = build_gradle.read_text(encoding="utf-8", errors="replace")
        has_version = "versionCode" in content and "versionName" in content
        has_app_id = "com.beesmart.spellingbee" in content or "com.beesmart.spelling" in content
        has_billing = "billing" in content or "BILLING" in content
        log_test("Build", "build.gradle exists", True, f"versionCode/versionName: {has_version}")
        log_test("Build", "Application ID configured", has_app_id)
        log_test("Build", "Billing dependency present", has_billing)
    else:
        log_test("Build", "build.gradle exists", False, f"Not found: {build_gradle}")

    # AndroidManifest.xml
    manifest = base / "mobile" / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    if manifest.exists():
        content = manifest.read_text(encoding="utf-8", errors="replace")
        has_internet = "INTERNET" in content
        has_billing = "BILLING" in content
        log_test("Build", "AndroidManifest exists", True)
        log_test("Build", "INTERNET permission", has_internet)
        log_test("Build", "BILLING permission", has_billing)
    else:
        log_test("Build", "AndroidManifest exists", False, f"Not found: {manifest}")

    # Capacitor config
    cap_config = base / "capacitor.config.json"
    if cap_config.exists():
        try:
            data = json.loads(cap_config.read_text(encoding="utf-8"))
            has_android = "android" in data
            log_test("Build", "Capacitor config exists", True)
            log_test("Build", "Android config in Capacitor", has_android)
        except Exception as e:
            log_test("Build", "Capacitor config parse", False, str(e))
    else:
        log_test("Build", "Capacitor config exists", False)


# ---------------------------------------------------------------------------
# 2. Android-Specific Code Paths (static analysis)
# ---------------------------------------------------------------------------
def test_android_code_paths():
    """Verify Android-specific handling exists in codebase"""
    print(f"\n{BOLD}{BLUE}=== Android Code Paths ==={RESET}")

    app_file = Path(__file__).parent / "AjaSpellBApp.py"
    if not app_file.exists():
        log_test("Code", "AjaSpellBApp.py exists", False)
        return

    content = app_file.read_text(encoding="utf-8", errors="replace")

    checks = [
        ("Android IAP verify endpoint", r"/api/iap/verify.*google|platform.*android"),
        ("Android subscription verify", r"/api/android/subscription/verify"),
        ("Android RTDN endpoint", r"/api/android/rtdn"),
        ("Google Play product IDs", r"use_google_play_ids|platform.*android"),
    ]
    for name, pattern in checks:
        found = bool(re.search(pattern, content))
        log_test("Code", name, found)

    # Check honeycomb picker has Android redirect handling
    picker_js = Path(__file__).parent / "static" / "js" / "honeycomb-avatar-picker-responsive.js"
    if picker_js.exists():
        js_content = picker_js.read_text(encoding="utf-8", errors="replace")
        has_android_redirect = "isAndroid" in js_content and "location.replace" in js_content
        log_test("Code", "Avatar picker Android redirect", has_android_redirect)

    # Check speed round has Android handling
    speed_setup = Path(__file__).parent / "templates" / "speed_round_setup.html"
    if speed_setup.exists():
        html = speed_setup.read_text(encoding="utf-8", errors="replace")
        has_android_speed = "Android" in html or "redirect" in html
        log_test("Code", "Speed round Android handling", has_android_speed)


# ---------------------------------------------------------------------------
# 3. Health & Core Endpoints
# ---------------------------------------------------------------------------
def test_health_endpoints():
    """Test health endpoints with Android UA"""
    print(f"\n{BOLD}{BLUE}=== Health Endpoints ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/health", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and data.get("status") == "ok"
        log_test("Health", "Main health", passed, f"Status: {r.status_code}, version: {data.get('version', 'N/A')}")
    except Exception as e:
        log_test("Health", "Main health", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/health/iap", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200
        log_test("Health", "IAP health", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Health", "IAP health", False, str(e))


# ---------------------------------------------------------------------------
# 4. Core Pages (must load with Android UA)
# ---------------------------------------------------------------------------
def test_core_pages():
    """Test all critical pages load with Android User-Agent"""
    print(f"\n{BOLD}{BLUE}=== Core Pages ==={RESET}")

    session = session_with_android_ua()
    pages = [
        ("/", "Home / Main menu"),
        ("/quiz", "Quiz page"),
        ("/auth/login", "Login page"),
        ("/auth/register", "Registration page"),
        ("/auth/dashboard", "Student dashboard"),
        ("/honeycomb-picker", "Avatar picker"),
        ("/speed-round/setup", "Speed round setup"),
        ("/word-lists", "Word lists"),
        ("/privacy", "Privacy policy"),
        ("/points-buzz-dust-explanation", "Points explanation"),
    ]

    for path, name in pages:
        try:
            r = session.get(f"{BASE_URL}{path}", timeout=10, allow_redirects=True)
            passed = r.status_code == 200 and len(r.text) > 200
            log_test("Pages", name, passed, f"Status: {r.status_code}, Size: {len(r.text)} bytes")
        except Exception as e:
            log_test("Pages", name, False, str(e))


# ---------------------------------------------------------------------------
# 5. Menu Tile Functions (every tile's backend API)
# ---------------------------------------------------------------------------
def test_tile_type_manually():
    """Tile: Type Words Manually -> POST /api/upload-manual-words"""
    print(f"\n{BOLD}{BLUE}=== Tile: Type Manually ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/upload-manual-words",
            json={"words": ["bee", "hive", "honey"]},
            timeout=15,
        )
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and (data.get("ok") is True or data.get("count", 0) > 0)
        log_test("Tile:Manual", "Upload manual words", passed, f"Status: {r.status_code}, count: {data.get('count', 'N/A')}")
    except Exception as e:
        log_test("Tile:Manual", "Upload manual words", False, str(e))


def test_tile_text_upload():
    """Tile: Upload Word List -> POST /api/wordbank/import-text"""
    print(f"\n{BOLD}{BLUE}=== Tile: Text Upload ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/wordbank/import-text",
            json={"text": "spell\nquiz\nword"},
            timeout=15,
        )
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and data.get("status") == "success"
        log_test("Tile:Text", "Import text words", passed, f"Stored: {data.get('stored', 'N/A')}")
    except Exception as e:
        log_test("Tile:Text", "Import text words", False, str(e))


def test_tile_dictionary():
    """Tile: Dictionary Search -> POST /api/dictionary-lookup"""
    print(f"\n{BOLD}{BLUE}=== Tile: Dictionary ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/dictionary-lookup",
            json={"word": "bee"},
            timeout=15,
        )
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and ("definition" in data or "found" in data or "word" in data)
        log_test("Tile:Dictionary", "Lookup word", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Tile:Dictionary", "Lookup word", False, str(e))


def test_tile_image_upload():
    """Tile: Extract from Image -> GET/POST /api/upload/image (premium)"""
    print(f"\n{BOLD}{BLUE}=== Tile: Image Upload ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/upload/image", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        # 200=ready, 401/403=auth/premium gate (endpoint works)
        passed = r.status_code in (200, 401, 403) or (r.status_code == 501 and "OCR" in str(data))
        log_test("Tile:Image", "Image upload endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Tile:Image", "Image upload endpoint", False, str(e))


def test_tile_random_play():
    """Tile: Random Play -> POST /api/random-words (requires auth)"""
    print(f"\n{BOLD}{BLUE}=== Tile: Random Play ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/random-words",
            json={"difficulty": 3, "count": 5},
            timeout=15,
        )
        data = r.json() if r.status_code in (200, 401) else {}
        passed = r.status_code == 200 or (r.status_code == 401 and data.get("error"))
        log_test("Tile:Random", "Random words API", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Tile:Random", "Random words API", False, str(e))


def test_tile_saved_lists():
    """Tile: Saved Lists -> GET /api/saved-lists (requires auth)"""
    print(f"\n{BOLD}{BLUE}=== Tile: Saved Lists ==={RESET}")
    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/saved-lists", timeout=10)
        data = r.json() if r.status_code in (200, 401) else {}
        passed = r.status_code == 200 or r.status_code == 401
        log_test("Tile:Saved", "Saved lists API", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Tile:Saved", "Saved lists API", False, str(e))


def test_tile_navigation_pages():
    """Tiles that navigate: avatars, groups, join, battles"""
    print(f"\n{BOLD}{BLUE}=== Tile: Navigation Pages ==={RESET}")
    session = session_with_android_ua()
    nav_pages = [
        ("/honeycomb-picker", "Avatars tile"),
        ("/groups", "Groups tile"),
        ("/join", "Join teacher tile"),
        ("/battles", "Battles tile"),
    ]
    for path, name in nav_pages:
        try:
            r = session.get(f"{BASE_URL}{path}", timeout=10, allow_redirects=True)
            passed = r.status_code == 200 and len(r.text) > 200
            log_test("Tile:Nav", name, passed, f"Status: {r.status_code}")
        except Exception as e:
            log_test("Tile:Nav", name, False, str(e))


# ---------------------------------------------------------------------------
# 6. Wordbank API (full)
# ---------------------------------------------------------------------------
def test_wordbank_api():
    """Test wordbank API with Android UA"""
    print(f"\n{BOLD}{BLUE}=== Wordbank API ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/wordbank/count", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and "count" in data
        log_test("Wordbank", "Get count", passed, f"Count: {data.get('count', 'N/A')}")
    except Exception as e:
        log_test("Wordbank", "Get count", False, str(e))

    try:
        r = session.post(
            f"{BASE_URL}/api/wordbank",
            json={"rows": [{"word": "test", "sentence": "Test sentence", "hint": ""}]},
            timeout=10,
        )
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and data.get("status") in ("success", "ok")
        log_test("Wordbank", "Add words", passed, f"Status: {data.get('status', 'N/A')}")
    except Exception as e:
        log_test("Wordbank", "Add words", False, str(e))

    try:
        r = session.post(f"{BASE_URL}/api/wordbank/clear", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and data.get("status") in ("success", "ok")
        log_test("Wordbank", "Clear wordbank", passed)
    except Exception as e:
        log_test("Wordbank", "Clear wordbank", False, str(e))


# ---------------------------------------------------------------------------
# 7. Full Quiz Flow (all functions)
# ---------------------------------------------------------------------------
def test_quiz_api():
    """Test full quiz flow: setup, next, answer (correct/incorrect), hint, pronounce"""
    print(f"\n{BOLD}{BLUE}=== Quiz API (Full Flow) ==={RESET}")

    session = session_with_android_ua()
    try:
        # Setup wordbank
        r = session.post(
            f"{BASE_URL}/api/wordbank",
            json={
                "rows": [
                    {"word": "cat", "sentence": "The cat sat.", "hint": "pet"},
                    {"word": "dog", "sentence": "A dog barks.", "hint": "pet"},
                    {"word": "bee", "sentence": "The bee buzzes.", "hint": "insect"},
                ]
            },
            timeout=10,
        )
        if r.status_code != 200:
            log_test("Quiz", "Setup wordbank", False, f"Status: {r.status_code}")
            return

        log_test("Quiz", "Setup wordbank", True)

        # Get next word
        r = session.post(f"{BASE_URL}/api/next", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and isinstance(data, dict) and "word" in data
        log_test("Quiz", "Get next word", passed, f"Word: {data.get('word', 'N/A')}")

        if not passed:
            return

        word = data.get("word", "")
        # Submit correct answer
        r = session.post(
            f"{BASE_URL}/api/answer",
            json={"user_input": word.lower(), "method": "keyboard", "elapsed_ms": 1000},
            timeout=10,
        )
        ans = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200 and ans.get("correct") is True
        log_test("Quiz", "Submit correct answer", passed, f"Correct: {ans.get('correct', 'N/A')}")

        # Get next word and submit wrong answer
        r = session.post(f"{BASE_URL}/api/next", timeout=10)
        data2 = r.json() if r.status_code == 200 else {}
        if r.status_code == 200 and "word" in data2:
            r = session.post(
                f"{BASE_URL}/api/answer",
                json={"user_input": "wronganswer", "method": "keyboard", "elapsed_ms": 500},
                timeout=10,
            )
            ans2 = r.json() if r.status_code == 200 else {}
            passed = r.status_code == 200 and ans2.get("correct") is False
            log_test("Quiz", "Submit incorrect answer", passed, f"Correct: {ans2.get('correct', 'N/A')}")

        # Test hint endpoint
        r = session.post(f"{BASE_URL}/api/hint", json={}, timeout=10)
        passed = r.status_code == 200
        log_test("Quiz", "Hint endpoint", passed, f"Status: {r.status_code}")

        # Test pronounce endpoint
        r = session.post(f"{BASE_URL}/api/pronounce", json={"word": "bee"}, timeout=10)
        passed = r.status_code in (200, 204, 400)
        log_test("Quiz", "Pronounce endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Quiz", "Quiz flow", False, str(e))


def test_avatar_api():
    """Test avatar picker APIs with Android UA"""
    print(f"\n{BOLD}{BLUE}=== Avatar Picker API ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/avatars", timeout=10)
        payload = r.json() if r.status_code == 200 else {}
        avatars = payload.get("avatars", payload) if isinstance(payload, dict) else payload
        avatars = avatars or []
        passed = r.status_code == 200 and len(avatars) > 0
        log_test("Avatar", "Get avatar list", passed, f"Avatars: {len(avatars)}")
    except Exception as e:
        log_test("Avatar", "Get avatar list", False, str(e))

    try:
        r = session.post(
            f"{BASE_URL}/api/avatar/select",
            json={"avatar_slug": "honey-comb"},
            timeout=10,
        )
        data = r.json() if r.status_code in (200, 401, 403) else {}
        passed = r.status_code in (200, 401, 403)
        log_test("Avatar", "Select avatar endpoint", passed, f"Status: {r.status_code} (auth required)")
    except Exception as e:
        log_test("Avatar", "Select avatar endpoint", False, str(e))


# ---------------------------------------------------------------------------
# 8. Full Speed Round Flow
# ---------------------------------------------------------------------------
def test_speed_round_full():
    """Test speed round API flow: start, next, answer, complete"""
    print(f"\n{BOLD}{BLUE}=== Speed Round (Full Flow) ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/speed-round/start",
            json={"time_per_word": 15, "difficulty": "grade_3_4", "word_count": 5, "word_source": "auto"},
            timeout=15,
            allow_redirects=True,
        )
        if r.status_code == 200:
            log_test("SpeedRound", "Start speed round", True, "Started (302->200)")
            r = session.get(f"{BASE_URL}/api/speed-round/next", timeout=10)
            data = r.json() if r.status_code == 200 else {}
            passed = r.status_code == 200 and ("word" in data or data.get("complete"))
            log_test("SpeedRound", "Get next word", passed, f"Status: {r.status_code}")

            if passed and "word" in data:
                word = data.get("word", "")
                r = session.post(
                    f"{BASE_URL}/api/speed-round/answer",
                    json={"user_input": word, "elapsed_ms": 2000},
                    timeout=10,
                )
                ans = r.json() if r.status_code == 200 else {}
                passed = r.status_code == 200 and "correct" in ans
                log_test("SpeedRound", "Submit answer", passed, f"Status: {r.status_code}")

            r = session.post(f"{BASE_URL}/api/speed-round/complete", timeout=10)
            log_test("SpeedRound", "Complete round", r.status_code == 200, f"Status: {r.status_code}")
        elif r.status_code in (401, 403):
            log_test("SpeedRound", "Start speed round", True, f"Status: {r.status_code} (auth/premium gate)")
        else:
            log_test("SpeedRound", "Start speed round", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test("SpeedRound", "Speed round flow", False, str(e))


# ---------------------------------------------------------------------------
# 9. Other Quiz/App Functions
# ---------------------------------------------------------------------------
def test_quiz_auxiliary():
    """Quiz state, status, clear, live-status, etc."""
    print(f"\n{BOLD}{BLUE}=== Quiz Auxiliary APIs ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/quiz/state", timeout=10)
        passed = r.status_code == 200
        log_test("QuizAux", "Quiz state", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("QuizAux", "Quiz state", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/api/quiz/status", timeout=10)
        passed = r.status_code == 200
        log_test("QuizAux", "Quiz status", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("QuizAux", "Quiz status", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/api/live-status", timeout=10)
        passed = r.status_code == 200
        log_test("QuizAux", "Live status", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("QuizAux", "Live status", False, str(e))

    try:
        r = session.post(f"{BASE_URL}/api/clear", json={"confirmed": True}, timeout=10)
        data = r.json() if r.status_code in (200, 400) else {}
        passed = r.status_code == 200 or (r.status_code == 400 and data.get("error"))
        log_test("QuizAux", "Clear session", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("QuizAux", "Clear session", False, str(e))


def test_buzz_dust_and_misc():
    """Buzz dust, bundles, auth status"""
    print(f"\n{BOLD}{BLUE}=== Buzz Dust & Misc ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/api/buzz-dust/info", timeout=10)
        passed = r.status_code in (200, 401)
        log_test("Misc", "Buzz dust info", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Misc", "Buzz dust info", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/api/bundles", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200
        log_test("Misc", "Bundles list", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Misc", "Bundles list", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/api/auth/status", timeout=10)
        passed = r.status_code == 200
        log_test("Misc", "Auth status", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Misc", "Auth status", False, str(e))


# ---------------------------------------------------------------------------
# 10. Android-Specific APIs
# ---------------------------------------------------------------------------
def test_android_iap_endpoints():
    """Test Android/Google IAP endpoints"""
    print(f"\n{BOLD}{BLUE}=== Android IAP Endpoints ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.post(
            f"{BASE_URL}/api/iap/verify/google",
            json={"product_id": "test.product", "purchase_token": "test_token"},
            timeout=10,
        )
        # 200, 400, 401 acceptable (invalid token in test)
        passed = r.status_code in (200, 400, 401)
        log_test("IAP", "Google verify endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("IAP", "Google verify endpoint", False, str(e))

    try:
        r = session.post(
            f"{BASE_URL}/api/iap/restore",
            json={"platform": "google", "product_ids": ["test.product"]},
            timeout=10,
        )
        passed = r.status_code in (200, 400, 401)
        log_test("IAP", "Restore (Google)", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("IAP", "Restore (Google)", False, str(e))


# ---------------------------------------------------------------------------
# 11. Speed Round Pages
# ---------------------------------------------------------------------------
def test_speed_round():
    """Test speed round pages and API with Android UA"""
    print(f"\n{BOLD}{BLUE}=== Speed Round ==={RESET}")

    session = session_with_android_ua()
    try:
        r = session.get(f"{BASE_URL}/speed-round/setup", timeout=10, allow_redirects=True)
        passed = r.status_code == 200
        log_test("SpeedRound", "Setup page loads", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("SpeedRound", "Setup page loads", False, str(e))

    try:
        r = session.get(f"{BASE_URL}/api/speed-round/health", timeout=10)
        data = r.json() if r.status_code == 200 else {}
        passed = r.status_code == 200
        log_test("SpeedRound", "Health endpoint", passed, f"Status: {data.get('speed_round_status', 'N/A')}")
    except Exception as e:
        log_test("SpeedRound", "Health endpoint", False, str(e))


# ---------------------------------------------------------------------------
# 12. Static Assets (PWA, manifest)
# ---------------------------------------------------------------------------
def test_static_assets():
    """Test critical static assets with Android UA"""
    print(f"\n{BOLD}{BLUE}=== Static Assets ==={RESET}")

    session = session_with_android_ua()
    assets = [
        ("/static/css/BeeSmart.css", "Main CSS"),
        ("/static/js/smarty-bee-3d.js", "3D Avatar loader"),
        ("/static/js/user-avatar-loader.js", "User avatar loader"),
        ("/static/js/honeycomb-avatar-picker-responsive.js", "Avatar picker JS"),
        ("/static/service-worker.js", "Service worker"),
        ("/static/manifest.webmanifest", "Web manifest"),
        ("/.well-known/assetlinks.json", "Android App Links"),
    ]

    for path, name in assets:
        try:
            r = session.get(f"{BASE_URL}{path}", timeout=10)
            passed = r.status_code == 200
            log_test("Assets", name, passed, f"Status: {r.status_code}, Size: {len(r.content)} bytes")
        except Exception as e:
            log_test("Assets", name, False, str(e))


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def generate_report():
    """Generate test summary report"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}ANDROID SMOKE TEST SUMMARY{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")

    total = len(TEST_RESULTS)
    passed = sum(1 for t in TEST_RESULTS if t["passed"])
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%" if total else "N/A")

    if failed > 0:
        print(f"\n{RED}Failed Tests:{RESET}")
        for t in TEST_RESULTS:
            if not t["passed"]:
                print(f"  ❌ [{t['category']}] {t['test']}")
                if t.get("details"):
                    print(f"     {t['details']}")

    report_file = f"smoke_test_android_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "base_url": BASE_URL,
                "user_agent": "Android WebView (Chrome 120)",
                "summary": {"total": total, "passed": passed, "failed": failed},
                "tests": TEST_RESULTS,
            },
            f,
            indent=2,
        )
    print(f"\n📄 Report saved to: {report_file}")
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    return failed == 0


def main():
    """Run all Android smoke tests"""
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}BeeSmart - Android Smoke Test{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"Target: {BASE_URL}")
    print(f"User-Agent: Android WebView (Chrome 120)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check server reachability
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5, headers={"User-Agent": ANDROID_UA})
        if r.status_code != 200:
            print(f"\n{RED}ERROR: Server not responding at {BASE_URL}{RESET}")
            print("Start the app: python AjaSpellBApp.py")
            sys.exit(1)
    except Exception as e:
        print(f"\n{RED}ERROR: Cannot connect to {BASE_URL}{RESET}")
        print(f"Error: {e}")
        print("\nStart the app: python AjaSpellBApp.py")
        sys.exit(1)

    print(f"{GREEN}✅ Server reachable{RESET}\n")

    # Run all test suites
    test_android_build_config()
    test_android_code_paths()
    test_health_endpoints()
    test_core_pages()
    test_tile_type_manually()
    test_tile_text_upload()
    test_tile_dictionary()
    test_tile_image_upload()
    test_tile_random_play()
    test_tile_saved_lists()
    test_tile_navigation_pages()
    test_wordbank_api()
    test_quiz_api()
    test_avatar_api()
    test_speed_round_full()
    test_quiz_auxiliary()
    test_buzz_dust_and_misc()
    test_android_iap_endpoints()
    test_speed_round()
    test_static_assets()

    all_passed = generate_report()

    if all_passed:
        print(f"\n{GREEN}✅ ALL ANDROID SMOKE TESTS PASSED{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}❌ SOME TESTS FAILED - Review before Android release{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
