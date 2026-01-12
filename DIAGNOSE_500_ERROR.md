# Diagnosing 500 Internal Server Error

## Quick Steps to Identify the Failing Resource

### Step 1: Check Browser Console
1. Open your browser's Developer Tools (F12)
2. Go to the **Network** tab
3. Look for any requests with status **500** (red)
4. Click on the failed request to see:
   - **Request URL** - Which endpoint is failing
   - **Response** - The error message from the server

### Step 2: Check Server Logs

**If running locally:**
- Check the terminal where Flask is running
- Look for Python traceback errors

**If on Railway/production:**
1. Go to Railway dashboard
2. Click on your service
3. View "Deploy Logs" or "Runtime Logs"
4. Look for Python traceback errors

### Step 3: Common Endpoints That Return 500 Errors

Based on the codebase, these endpoints have error handling that might return 500:

1. **`/api/upload`** - File upload endpoint
2. **`/api/avatars`** - Avatar catalog API
3. **`/api/avatar/<avatar_id>`** - Individual avatar API
4. **`/api/buzz-dust/info`** - Buzz dust ranking API (now returns 200 with error flag)
5. **`/api/wordbank`** - Wordbank API
6. **`/api/next`** - Next word API
7. **`/api/answer`** - Answer submission API

### Step 4: Check Error Handler

The app has a 500 error handler at line 8095-8101 in `AjaSpellBApp.py`:

```python
@app.errorhandler(500)
def handle_500_error(error):
    """Log and return 500 errors with details"""
    app.logger.error(f"Internal server error: {error}")
    import traceback
    app.logger.error(traceback.format_exc())
    return jsonify({"error": "Internal server error", "details": str(error)}), 500
```

This should log the full traceback to the server logs.

## Quick Fixes to Try

### Fix 1: Restart Server
```bash
# Stop Flask server (Ctrl+C)
# Restart it
python AjaSpellBApp.py
```

### Fix 2: Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Or clear cache in browser settings

### Fix 3: Check Database Connection
If the error is on a database-related endpoint:
- Verify database credentials in environment variables
- Check if database server is running/accessible
- Verify connection string is correct

## What Information to Provide

If the error persists, please provide:

1. **The exact URL/endpoint** that's failing (from browser Network tab)
2. **The full Python traceback** from server logs
3. **Whether it's local or production** (Railway)
4. **Any error messages** from the browser console (F12 → Console)
5. **When the error occurs** (on page load, after clicking something, etc.)

This will help identify the exact cause of the 500 error.
