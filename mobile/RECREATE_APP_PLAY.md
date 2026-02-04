# Recreate the app on Play (new listing, new key)

If you're done fighting the upload key and are okay starting a **new** Play Store listing (new page, no old installs/reviews), this is the path.

**Tradeoff:** New app = new store listing. You lose the current app’s installs, ratings, and reviews. The old listing can stay as-is or you can unpublish it later.

---

## 1. Create the new app in Play Console

1. Go to [Play Console](https://play.google.com/console).
2. Click **Create app** (or **Add app**).
3. Fill in app name (e.g. "BeeSmart Spelling" again or "BeeSmart Spelling Bee"), default language, app or game, etc.
4. Create the app. You’ll get a **new** app with no upload key registered yet.

---

## 2. Use a new package name (required for a new app)

Play treats each **applicationId** as a different app. So we need a new one.

Pick a new package name, e.g.:

- `com.beesmart.spellingbee`
- `com.altech.beesmart.spelling`

Then change it in the project (see step 3). You only need to do this once.

---

## 3. Change applicationId in the project

In **`mobile/android/app/build.gradle`**, set the new package name:

- `applicationId "com.beesmart.spellingbee"` (or whatever you chose)
- Optionally set `namespace` to the same value (e.g. `namespace "com.beesmart.spellingbee"`) so it stays consistent.

If you have other places that reference the package (e.g. deep links, Firebase), update those too.

---

## 4. New keystore + build (no key reset)

From the **mobile** folder:

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
py reset_or_find_play_upload_key.py --make-new --force
```

Use a strong password and save it. Then:

```powershell
.\build-aab.ps1
```

You do **not** upload any PEM to Play for a brand‑new app. The first AAB you upload **is** the one that registers your upload key.

---

## 5. Upload to the new app

1. In Play Console, open the **new** app you created.
2. Go to **Release** → **Production** (or **Testing**) → **Create new release**.
3. Upload: **`mobile\android\app\build\outputs\bundle\release\app-release.aab`**

Play will accept it and register the key you used. No “wrong key” flow.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Play Console → Create app (new listing) |
| 2 | Pick new package name (e.g. `com.beesmart.spellingbee`) |
| 3 | In `android/app/build.gradle`: set `applicationId` (and optionally `namespace`) to that package |
| 4 | Run `py reset_or_find_play_upload_key.py --make-new --force` then `.\build-aab.ps1` |
| 5 | In the **new** app, upload the new `app-release.aab` |

After this, use the **same** keystore and password for all future releases of this new app.
