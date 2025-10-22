"""
Smoke tests for the possessive formatting used in the quiz report card header.

This does not drive the browser. It only validates the name → possessive logic
we rely on in the UI (e.g., Alex → Alex's, James → James').

Run with: pytest -q tests/test_personalization_smoke.py
"""

import re


def format_possessive(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return "Your Report Card!"
    ends_with_s = re.search(r"s$", n, flags=re.IGNORECASE) is not None
    suffix = "'" if ends_with_s else "'s"
    return f"{n}{suffix} Report Card!"


def test_possessive_for_regular_name():
    assert format_possessive("Alex") == "Alex's Report Card!"


def test_possessive_for_name_ending_with_s_lower():
    assert format_possessive("james") == "james' Report Card!"


def test_possessive_for_name_ending_with_s_upper():
    assert format_possessive("JAMES") == "JAMES' Report Card!"


def test_possessive_for_empty_name():
    assert format_possessive("") == "Your Report Card!"


def test_possessive_trims_whitespace():
    assert format_possessive("  Boss  ") == "Boss' Report Card!"
