"""
Quick startup profiling helper.
Measures import times for the main app and key modules without changing runtime behavior.
Usage:
  python scripts/profile_startup.py
Optional:
  PYTHONPROFILEIMPORTTIME=1 python -X importtime scripts/profile_startup.py
"""
from __future__ import annotations
import importlib
import time
import sys

MODULES = [
    "AjaSpellBApp",
    "dictionary_api",
    "avatar_catalog",
    "avatar_manager",
    "models",
]


def time_import(module_name: str) -> float:
    start = time.perf_counter()
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
        dur = (time.perf_counter() - start) * 1000
        print(f"✅ import {module_name:<20} {dur:8.2f} ms")
        return dur
    except Exception as e:
        dur = (time.perf_counter() - start) * 1000
        print(f"❌ import {module_name:<20} {dur:8.2f} ms  (error: {e})")
        return dur


def main() -> None:
    print("\n🐝 BeeSmart Startup Import Profile\n" + "-" * 40)
    totals = []
    for mod in MODULES:
        totals.append(time_import(mod))
    total_ms = sum(totals)
    print("-" * 40)
    print(f"Total (sum of above): {total_ms:.2f} ms")
    print("Note: This is an approximation; wall clock cold start differs.\n")


if __name__ == "__main__":
    main()
