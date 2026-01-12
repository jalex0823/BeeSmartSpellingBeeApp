# Troubleshooting 500 Internal Server Error

**Date**: January 12, 2026  
**Error**: `500 Internal Server Error: The server encountered an internal error...`

---

## 🔍 Quick Diagnosis Steps

### Step 1: Check Server Logs
The error message you received is the generic Flask error handler response. To find the actual error:

**If running locally:**
```bash
# Check the terminal where Flask is running
# Look for Python traceback/error messages
```

**If on Railway/production:**
1. Go to Railway dashboard
2. Click on your service
3. View "Deploy Logs" or "Runtime Logs"
4. Look for Python traceback errors

### Step 2: Identify the Failing Route
The error doesn't specify which route failed. Check:
- What URL were you accessing when the error occurred?
- Was it `/`, `/api/avatars`, `/honeycomb-picker`, or another route?

### Step 3: Check Recent Changes
We just modified:
- `templates/unified_menu.html` - Added Avatars tile
- `mobile/ios/App/App/Info.plist` - Removed background audio

**Template syntax verified**: ✅ Passed Jinja2 validation

---

## 🐛 Common Causes & Fixes

### 1. Template Rendering Error
**Symptoms**: Error when loading home page or menu

**Check**:
```bash
# Verify template syntax
python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('templates')); template = env.get_template('unified_menu.html'); print('OK')"
```

**If this fails**: There's a syntax error in the template

### 2. Missing Route Handler
**Symptoms**: Error when clicking Avatars tile

**Check**: Verify `/honeycomb-picker` route exists:
```python
# In AjaSpellBApp.py, should have:
@app.route('/honeycomb-picker')
def honeycomb_avatar_picker():
    ...
```

### 3. Database Connection Error
**Symptoms**: Error on any route that queries database

**Check**:
- Database credentials in environment variables
- Database server is running/accessible
- Connection string is correct

### 4. Import Error
**Symptoms**: Error on startup or first request

**Check**: All imports are valid:
```bash
python -c "import AjaSpellBApp; print('Imports OK')"
```

### 5. Missing Dependencies
**Symptoms**: Error mentioning missing module

**Check**: Install all requirements:
```bash
pip install -r requirements.txt
```

---

## 🔧 Debugging Steps

### Enable Flask Debug Mode (Local Only)
```python
# In AjaSpellBApp.py, ensure:
if __name__ == '__main__':
    app.run(debug=True)  # Shows detailed error pages
```

**⚠️ WARNING**: Never enable debug mode in production!

### Check Specific Route
Test the route that's failing:
```bash
# If error is on home page:
curl http://localhost:5000/

# If error is on avatars route:
curl http://localhost:5000/honeycomb-picker

# If error is on API:
curl http://localhost:5000/api/avatars
```

### Check Server Console
When running Flask locally, the error traceback should appear in the terminal. Look for:
- `Traceback (most recent call last):`
- `File "...", line X, in function_name`
- `Error: ...`

---

## 🎯 Most Likely Issues After Our Changes

### Issue 1: `/honeycomb-picker` Route Requires Login
**Problem**: The route might have `@login_required` decorator, but guest users are trying to access it.

**Check**:
```python
# In AjaSpellBApp.py, line ~12967
@app.route('/honeycomb-picker')
def honeycomb_avatar_picker():
    if not (hasattr(current_user, 'is_authenticated') and current_user.is_authenticated):
        return redirect(url_for('login', next=request.path))
    ...
```

**Fix**: If you want guests to access it, remove the login check or make it optional.

### Issue 2: Missing Template File
**Problem**: Route references a template that doesn't exist.

**Check**: Verify template exists:
```bash
ls templates/honeycomb_avatar_picker_responsive.html
```

### Issue 3: Template Variable Error
**Problem**: Template expects a variable that isn't being passed.

**Check**: Look at the route handler to see what variables it passes to the template.

---

## 📋 Action Items

1. **Get the actual error traceback**:
   - Check server logs (terminal or Railway)
   - Look for the Python traceback

2. **Identify the failing route**:
   - Note the exact URL when error occurs
   - Check if it's related to our Avatars tile changes

3. **Check route handler**:
   - Verify `/honeycomb-picker` route exists and is correct
   - Check if it requires authentication

4. **Test template rendering**:
   - Try accessing the route directly
   - Check if template file exists

---

## 🚨 If Error Persists

**Please provide**:
1. The full Python traceback from server logs
2. The exact URL/route that's failing
3. Whether it's local or production
4. Any error messages from the browser console (F12 → Console)

This will help identify the exact cause.

---

## ✅ Quick Fixes to Try

### Fix 1: Restart Server
```bash
# Stop Flask server (Ctrl+C)
# Restart it
python AjaSpellBApp.py
```

### Fix 2: Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Or clear cache in browser settings

### Fix 3: Check Route Exists
```bash
# List all routes
python -c "from AjaSpellBApp import app; print([r.rule for r in app.url_map.iter_rules()])"
```

---

**Next Step**: Check your server logs and share the actual Python traceback for more specific help.
