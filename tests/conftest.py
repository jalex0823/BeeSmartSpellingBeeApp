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


def pytest_configure() -> None:
    """Make Flask app errors visible during tests.

    Several tests use dynamic imports of `AjaSpellBApp.py` via `importlib`,
    but others may import `AjaSpellBApp` directly. Turning on TESTING and
    propagating exceptions helps pytest surface server errors rather than
    returning opaque 500s.
    """

    try:
        import AjaSpellBApp

        AjaSpellBApp.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=True)
    except Exception:
        # Avoid failing test collection/config if the app can't import here.
        pass


from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import pytest  # type: ignore


def _get_pytest():
    # Local import keeps linters calmer in workspaces where pytest isn't in the
    # active type-check environment, while still working at runtime.
    import pytest  # type: ignore

    return pytest


@_get_pytest().fixture
def client():
    """Shared Flask test client fixture.

    Note: some test modules also define their own `client` fixture. That's fine
    (module-local fixtures take precedence), but having this in conftest makes
    it available repo-wide for any tests that don't.
    """
    import AjaSpellBApp

    AjaSpellBApp.app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'PROPAGATE_EXCEPTIONS': True,
    })

    with AjaSpellBApp.app.test_client() as c:
        with AjaSpellBApp.app.app_context():
            yield c
