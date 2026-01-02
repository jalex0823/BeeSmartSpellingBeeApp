"""Pytest configuration for BeeSmartSpellingBeeApp.

This repo is not packaged as an installable Python distribution, and several
tests import modules (e.g., `AjaSpellBApp`, `config`) from the repository root.

When pytest is executed from a different working directory or via certain IDE
test runners, the repo root may not be on `sys.path`, causing import errors
during test collection.

We explicitly add the repo root to `sys.path` so tests can import the app
module consistently.
"""

from __future__ import annotations

import sys
from pathlib import Path


# Ensure repository root is importable.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
