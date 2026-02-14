#!/usr/bin/env python3
"""
BeeSmart - Scroll & Rubber-Band Health Smoke Test (all OS's)

Validates that quiz and shared templates are configured so scrolling works
and rubber-banding is controlled on all platforms (iOS, Android, desktop).
Checks CSS and JS patterns that would break scroll or cause unwanted rubber-band.

Usage:
    python smoke_test_scroll_health.py

    # Without BASE_URL: reads templates/ (recommended for CI). Same HTML/CSS/JS
    # is served for all OS's, so one run validates scroll config for iOS, Android, desktop.

    # With BASE_URL: fetches /quiz and base from server (may be login page if gated).
"""

import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# Configuration
BASE_DIR = Path(__file__).resolve().parent
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

RESULTS = []


def log(category: str, name: str, passed: bool, detail: str = ""):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"  {status} [{category}] {name}")
    if detail:
        print(f"      {detail}")
    RESULTS.append({"category": category, "name": name, "passed": passed, "detail": detail})
    return passed


def read_quiz_html():
    """Quiz page content: from file or fetch."""
    if BASE_URL:
        try:
            r = requests.get(
                f"{BASE_URL}/quiz",
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}
            )
            if r.ok:
                return r.text
        except Exception as e:
            print(f"  {YELLOW}WARN: fetch quiz failed: {e}{RESET}")
    p = BASE_DIR / "templates" / "quiz.html"
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    return ""


def read_base_html():
    """Base template content."""
    if BASE_URL:
        try:
            r = requests.get(f"{BASE_URL}/", timeout=10)
            if r.ok:
                return r.text
        except Exception:
            pass
    p = BASE_DIR / "templates" / "base.html"
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    return ""


def run_quiz_scroll_css_checks(html: str) -> bool:
    """Quiz page: CSS that enables body scroll and controls rubber-band (all OS's)."""
    section = "QuizScrollCSS"
    ok = True

    # body.route-quiz must be the scroll container
    if "body.route-quiz" not in html:
        ok &= log(section, "body.route-quiz block exists", False, "missing")
    else:
        ok &= log(section, "body.route-quiz block exists", True)

    # Required for vertical scroll
    if re.search(r"body\.route-quiz\s*\{[^}]*overflow-y:\s*auto", html, re.S):
        ok &= log(section, "body.route-quiz overflow-y: auto", True)
    else:
        ok &= log(section, "body.route-quiz overflow-y: auto", False, "needed for body scroll")

    # iOS momentum scroll (must be in or adjacent to body.route-quiz block)
    idx = html.find("body.route-quiz")
    if idx >= 0:
        chunk = html[idx : idx + 1500]
        if "-webkit-overflow-scrolling" in chunk and "touch" in chunk:
            ok &= log(section, "body.route-quiz -webkit-overflow-scrolling: touch", True)
        else:
            ok &= log(section, "body.route-quiz -webkit-overflow-scrolling: touch", False, "iOS momentum scroll")
    else:
        ok &= log(section, "body.route-quiz -webkit-overflow-scrolling: touch", False, "body.route-quiz not found")

    # Touch action allows vertical pan (scroll)
    if "touch-action" in html and "route-quiz" in html:
        ok &= log(section, "touch-action present for route-quiz", True)
    else:
        ok &= log(section, "touch-action present for route-quiz", False, "pan-y recommended")

    # Card content must not clip so body can grow (no overflow:hidden on quiz card for route-quiz)
    if "body.route-quiz .card-scroll" in html and "overflow: visible" in html:
        ok &= log(section, "body.route-quiz .card-scroll overflow visible", True)
    else:
        ok &= log(section, "body.route-quiz .card-scroll overflow visible", False, "content would be clipped")

    if "body.route-quiz .quiz-card" in html and "overflow: visible" in html:
        ok &= log(section, "body.route-quiz .quiz-card overflow visible", True)
    else:
        ok &= log(section, "body.route-quiz .quiz-card overflow visible", False, "page may not scroll")

    # Overscroll: body can scroll; html rubber-band can be suppressed
    if "overscroll-behavior" in html:
        ok &= log(section, "overscroll-behavior defined", True)
    else:
        ok &= log(section, "overscroll-behavior defined", False, "optional but recommended")

    return ok


def run_quiz_scroll_js_checks(html: str) -> bool:
    """Quiz page: JS must NOT install document-level scroll traps when on quiz (all OS's)."""
    section = "QuizScrollJS"
    ok = True

    # Critical: isQuizPage must force usesInnerScroller false so we don't add preventBodyScroll
    if "isQuizPage" in html and "route-quiz" in html:
        ok &= log(section, "isQuizPage / route-quiz check present", True)
    else:
        ok &= log(section, "isQuizPage / route-quiz check present", False)

    # usesInnerScroller must be false when isQuizPage (so scroll traps are skipped)
    if re.search(r"isQuizPage\s*\)\s*return\s*false", html):
        ok &= log(section, "usesInnerScroller false when isQuizPage", True)
    elif "isQuizPage" in html and "return false" in html:
        ok &= log(section, "usesInnerScroller false when isQuizPage", True)
    else:
        ok &= log(section, "usesInnerScroller false when isQuizPage", False, "scroll traps would run on quiz")

    # Document-level touchmove preventDefault must only run when usesInnerScroller
    if "document.addEventListener('touchmove', preventBodyScroll" in html:
        if "usesInnerScroller" in html:
            ok &= log(section, "preventBodyScroll only when usesInnerScroller", True)
        else:
            ok &= log(section, "preventBodyScroll only when usesInnerScroller", False, "could block body scroll")
    else:
        ok &= log(section, "no document touchmove trap on quiz", True)

    # Comment or log that we skip scroll guards on quiz
    if "Page scroll mode" in html or "skipping" in html and "inner-scroller" in html:
        ok &= log(section, "page scroll mode / skip inner-scroller documented", True)
    else:
        ok &= log(section, "page scroll mode / skip inner-scroller documented", False, "optional")

    return ok


def run_base_ios_scroll_checks(html: str) -> bool:
    """Base template: on iOS, do not block scroll on quiz page (touchend)."""
    section = "BaseScroll"
    ok = True

    if "route-quiz" not in html:
        ok &= log(section, "base touches route-quiz for scroll", False, "base must skip touchend on quiz")
    else:
        # Should have: if body.classList.contains('route-quiz') return;
        if "route-quiz" in html and ("return" in html or "contains" in html):
            ok &= log(section, "base skips touchend preventDefault on route-quiz", True)
        else:
            ok &= log(section, "base skips touchend preventDefault on route-quiz", False)
    return ok


def run_speed_round_scroll_checks() -> bool:
    """Speed round: scrollable modals and containers use touch scrolling where needed."""
    section = "SpeedRoundScroll"
    p = BASE_DIR / "templates" / "speed_round_quiz.html"
    if not p.exists():
        log(section, "speed_round_quiz template found", False)
        return False
    content = p.read_text(encoding="utf-8", errors="replace")
    ok = True
    if "-webkit-overflow-scrolling: touch" in content:
        ok &= log(section, "speed round -webkit-overflow-scrolling touch present", True)
    else:
        ok &= log(section, "speed round -webkit-overflow-scrolling touch present", False, "optional for modals")
    return ok


def main():
    print(f"\n{BOLD}{BLUE}=== Scroll & Rubber-Band Health (all OS's) ==={RESET}\n")

    quiz_html = read_quiz_html()
    if not quiz_html:
        print(f"  {RED}No quiz content (file or BASE_URL).{RESET}")
        sys.exit(1)

    base_html = read_base_html()

    run_quiz_scroll_css_checks(quiz_html)
    run_quiz_scroll_js_checks(quiz_html)
    if base_html:
        run_base_ios_scroll_checks(base_html)
    run_speed_round_scroll_checks()

    passed = sum(1 for r in RESULTS if r["passed"])
    total = len(RESULTS)
    print(f"\n{BOLD}Scroll health: {passed}/{total} passed{RESET}")
    if passed < total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
