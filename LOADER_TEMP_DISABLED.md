# Loader Temporarily Disabled

The previous loading screen has been disabled because it was causing a broken/blocked experience.

## What Was Done
- Added `static/js/loader-disable.js` which hides common loader element IDs/classes and provides no-op `showLoader` / `hideLoader` functions.
- Added `static/css/loader-disable.css` which force-hides loader elements.
- Did NOT remove existing `static/js/loading-screen.js` (file delete attempt kept existing file; override script should neutralize behavior) — you can fully remove or restore later.

## How To Re-Enable Later
1. Remove the includes for `loader-disable.js` and `loader-disable.css` from the base template.
2. Restore original loader JS/CSS (or checkout previous commit).
3. Test via a cold load and ensure assets complete before quiz interactions.

## Recommended Template Changes
In `templates/base.html` (or whichever layout first loads), ensure you:
```html
<!-- After other scripts -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/loader-disable.css') }}">
<script src="{{ url_for('static', filename='js/loader-disable.js') }}" defer></script>
```
Remove any blocking logic that waits for 3D assets before showing the menu.

## Direct Home Route
If the root route is not pointing to the menu yet, add to `AjaSpellBApp.py`:
```python
from flask import render_template

@app.route('/')
def home_redirect():
    return render_template('unified_menu.html')
```
(Adjust the `app` name if different.)

## Rollback
To rollback, simply delete the two new files and remove their includes.
