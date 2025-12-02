🐝 HONEY LOADER SYSTEM - ACTIVE FILE REFERENCE
================================================

ACTIVE LOADER (DO NOT RENAME OR REMOVE):
- honey-loader.unified.safe.js ✅ PRODUCTION - Ultra-safe micro-task loader

DEPRECATED LOADERS (renamed with .DEPRECATED extension):
- honey-loader.full.js.DEPRECATED ❌ Heavy loader with canvas matrix, 55% health gate
- honey-loader.unified.js.DEPRECATED ❌ First unified attempt, replaced by .safe version
- honey-loader.clean.js.DEPRECATED ❌ Basic loader, replaced by safer versions

WHY honey-loader.unified.safe.js IS THE ONLY ONE:
==================================================
1. Micro-task slicing with requestAnimationFrame + nextFrame()
2. Progress moves BEFORE network calls (UI stays responsive)
3. Pure CSS matrix animation (can't freeze even if JS stalls)
4. Hard 1400ms timeout on all fetches
5. Only 3 lightweight checks: /api/avatars/light, /api/quizzes/light, /api/analytics/ping
6. Dispatches BeeSmart:loaderComplete event (matches avatar-display-manager.js)
7. No health threshold blocking (won't trap users)

LOAD SEQUENCE:
==============
1. honey-loader.unified.safe.js runs on page load
2. Matrix animation (pure CSS) starts immediately
3. System checks run (0% → 100%)
4. Dispatches BeeSmart:loaderComplete event
5. avatar-display-manager.js hears event and initializes 3D carousel (deferred)

TEMPLATES USING THIS LOADER:
=============================
- templates/base.html (line 8)
- templates/unified_menu.html (line 33, dynamic load)

NEVER LOAD MULTIPLE LOADERS ON SAME PAGE - CAUSES FREEZING!
