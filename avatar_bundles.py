"""
Avatar bundles and redeemable keys (dev-ready)

- BUNDLE_CATALOG: bundle_id -> { name, avatars[] }
- REDEEMABLE_KEYS: UPPERCASE key (no spaces) -> bundle_id

Notes
- Keys here are for development/demo. In production, load from a secure store
  or environment, and consider one-time-use tracking.
- Avatars listed should match catalog slugs; basic aliases exist elsewhere.
"""
from __future__ import annotations

import os
from typing import Dict, List

# Minimal starter bundles (choose fun, kid-friendly sets)
BUNDLE_CATALOG: Dict[str, dict] = {
    "classroom_starter_pack": {
        "name": "Classroom Starter Pack",
        "avatars": [
            "queen-bee",
            "superbee",
            "knight-bee",
            "rocker-bee",
            "doctor-bee",
        ],
    },
    "family_fun_pack": {
        "name": "Family Fun Pack",
        "avatars": [
            "cutie-bee",
            "explorer-bee",
            "singer-bee",
            "astro-bee",   # alias of space-bee
            "biker-bee",   # alias of motor-bee
        ],
    },
    "launch_pack_2025": {
        "name": "Launch Pack",
        "avatars": [
            "bk-bee",
            "gamer-bee",
            "super-bee",
            "techno-bee",
            "knight-bee",
        ],
    },
}

# Default dev/demo keys (case-insensitive; spaces ignored on server)
_DEFAULT_KEYS: Dict[str, str] = {
    "BEE-CLASS-STARTER-1": "classroom_starter_pack",
    "BEE-FAMILY-FUN-1": "family_fun_pack",
}

# Allow runtime override via environment JSON (optional)
# Example: export BUNDLE_KEYS_JSON='{"SCHOOL-ABC-2025":"classroom_starter_pack"}'
import json
_env_json = os.getenv("BUNDLE_KEYS_JSON", "").strip()
if _env_json:
    try:
        _override = json.loads(_env_json)
        if isinstance(_override, dict):
            _DEFAULT_KEYS.update(_override)
    except Exception:
        pass

# Normalize to uppercase, remove spaces for fast lookup
REDEEMABLE_KEYS: Dict[str, str] = {}
for _k, _v in _DEFAULT_KEYS.items():
    if not isinstance(_k, str) or not isinstance(_v, str):
        continue
    key_norm = _k.replace(" ", "").upper()
    REDEEMABLE_KEYS[key_norm] = _v
