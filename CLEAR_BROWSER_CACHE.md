# 🔄 Clear Browser Cache for BeeSmart App

## Why Clear Cache?

When you update 3D avatar files (OBJ, MTL, PNG), your browser may still show the **old cached version** instead of your new fixed files. This causes avatars to appear broken even though the files are correct.

---

## ✅ Quick Fix: Hard Refresh

### Windows/Linux:
- **Chrome/Edge**: Press `Ctrl + Shift + R` or `Ctrl + F5`
- **Firefox**: Press `Ctrl + Shift + R` or `Ctrl + F5`

### Mac:
- **Chrome/Edge**: Press `Cmd + Shift + R`
- **Firefox**: Press `Cmd + Shift + R`
- **Safari**: Press `Cmd + Option + E` (empty caches), then `Cmd + R` (reload)

---

## 🧹 Full Cache Clear (If Hard Refresh Doesn't Work)

### Google Chrome / Microsoft Edge

1. **Open Developer Tools**:
   - Press `F12` or `Ctrl + Shift + I` (Windows/Linux)
   - Press `Cmd + Option + I` (Mac)

2. **Right-click the refresh button** (next to the address bar)

3. **Select "Empty Cache and Hard Reload"**

**OR**

1. Click the **3 dots menu** (⋮) → **More Tools** → **Clear Browsing Data**
2. Select **Time Range**: "All time"
3. Check **only**:
   - ✅ Cached images and files
4. Click **Clear data**

---

### Mozilla Firefox

1. Press `Ctrl + Shift + Delete` (Windows/Linux) or `Cmd + Shift + Delete` (Mac)
2. Select **Time Range**: "Everything"
3. Check **only**:
   - ✅ Cache
4. Click **Clear Now**

---

### Safari (Mac)

1. Go to **Safari** → **Preferences** → **Advanced**
2. Enable **"Show Develop menu in menu bar"**
3. Click **Develop** → **Empty Caches**
4. Press `Cmd + R` to reload

---

## 🎯 For Developers: Testing Without Cache

### Chrome DevTools Method

1. Open **DevTools** (`F12`)
2. Go to **Network** tab
3. Check **"Disable cache"** checkbox
4. Keep DevTools **open** while testing

This ensures you always see the latest files without manually clearing cache.

---

## 🚀 Automatic Cache-Busting (Already Implemented!)

The app now adds timestamps to 3D model URLs automatically:
```javascript
// Example: ?v=1729612345678
/static/assets/avatars/diva-bee/DivaBee.obj?v=1729612345678
```

This forces the browser to reload files whenever the page loads, so cache issues should be rare after this update.

---

## 🐝 Which Avatars Need Cache Clearing?

If you recently fixed:
- ✅ **Diva Bee** (new optimized version uploaded)
- ✅ **Detective Bee** (MTL references fixed)
- ✅ **Queen Bee** (MTL references fixed)
- ✅ **Brother Bee** (MTL references fixed)

**Clear your cache** to see the fixes!

---

## 📋 Verification Checklist

After clearing cache:

1. ✅ Open the avatar picker
2. ✅ Select one of the fixed avatars
3. ✅ Check the **browser console** (`F12` → Console tab)
4. ✅ Look for:
   - `✅ MTL materials loaded successfully`
   - `✅ Texture loaded successfully`
   - **NO errors** about missing files

If you still see errors, the files may not be correctly uploaded to the server.

---

## 🆘 Still Not Working?

If cache clearing doesn't fix the issue:

1. **Check browser console** for actual error messages
2. **Verify files exist** on the server:
   ```
   https://yoursite.com/static/assets/avatars/diva-bee/DivaBee.obj
   https://yoursite.com/static/assets/avatars/diva-bee/DivaBee.mtl
   https://yoursite.com/static/assets/avatars/diva-bee/DivaBee.png
   ```
3. **Check MTL file** references the correct PNG filename
4. **Check OBJ file** references the correct MTL filename

---

## 💡 Pro Tip: Incognito/Private Mode

For quick testing without affecting your main browser cache:

- **Chrome**: `Ctrl + Shift + N`
- **Firefox**: `Ctrl + Shift + P`
- **Safari**: `Cmd + Shift + N`

This opens a clean browser window with **no cached files**.
