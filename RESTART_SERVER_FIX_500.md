# How to Restart Server to Fix 500 Error

**Issue**: 500 error persists because server is running old code  
**Solution**: Restart Flask server to load the fix

---

## 🔄 Restart Steps

### Option 1: Stop and Restart (Recommended)

1. **Find the terminal/window where Flask is running**
   - Look for output like "Running on http://127.0.0.1:5000"
   - Or check for Python process in Task Manager

2. **Stop the server**:
   - Press `Ctrl+C` in that terminal
   - Or close the terminal window

3. **Restart the server**:
   ```powershell
   cd C:\Temp\BeeSmartSpellingBeeApp
   python AjaSpellBApp.py
   ```

4. **Wait for startup**:
   - Look for "Ready to serve requests on port 5000"
   - Should see initialization messages

5. **Test the home page**:
   - Open browser: `http://localhost:5000/`
   - Should load without 500 error

---

### Option 2: Kill Process and Restart

If `Ctrl+C` doesn't work:

1. **Kill Python process**:
   ```powershell
   taskkill /F /PID 26900
   ```
   (Replace 26900 with actual process ID if different)

2. **Or kill all Python processes** (use with caution):
   ```powershell
   taskkill /F /IM python.exe
   ```

3. **Restart server**:
   ```powershell
   python AjaSpellBApp.py
   ```

---

## ✅ Verification

After restart, you should see:
- ✅ Home page loads (`http://localhost:5000/`)
- ✅ No 500 error
- ✅ Avatars tile visible
- ✅ Favicon 404 resolved (or returns 204)

---

## 🐛 If Still Getting 500 Error

If error persists after restart:

1. **Check server console** for Python traceback
2. **Look for error messages** in the terminal
3. **Share the full error** for diagnosis

The fix is in the code - restart is required to apply it.
