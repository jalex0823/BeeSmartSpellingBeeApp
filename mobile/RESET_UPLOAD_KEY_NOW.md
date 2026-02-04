# Fix "Wrong key" — Reset upload key (do in this order)

You're seeing this because:
- **Play expects:** SHA1 `EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13`
- **Your AAB was signed with:** SHA1 `CB:9A:9B:3C:2B:8B:CF:89:3E:39:E4:33:E1:6E:7B:D9:2E:10:B0:3A`

So you're building with a different key than Play has on file. **Do not upload another AAB until you complete the steps below** and then build a new one.

---

## Step 1: Start the reset in Play Console

1. Open [Play Console](https://play.google.com/console) → your app.
2. Go to **Setup** → **App integrity**.
3. Under **Upload key certificate**, click **Reset upload key** (or **Request upload key reset** / **Register new key**).
4. Follow the screen; it will ask you to upload a **new certificate (PEM)**. Leave that tab open — you'll get the file in Step 2.

---

## Step 2: Generate a new key and PEM on your PC

In **PowerShell**, from the `mobile` folder:

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
py reset_or_find_play_upload_key.py --make-new
```

- When prompted, choose a **strong password** and **save it** (you need it for every future release).
- This creates:
  - `android/upload-keystore.jks` (new key)
  - `android/upload_certificate.pem` (file for Play)
  - `android/keystore.properties` (so the next build uses this key)

**If the script says** `upload-keystore.jks already exists` and you want to replace it with a new key, run:

```powershell
py reset_or_find_play_upload_key.py --make-new --force
```

---

## Step 3: Upload the PEM in Play Console

Back in Play Console (the reset flow from Step 1):

- When it asks for the **upload certificate**, upload this file:
  - **`c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile\android\upload_certificate.pem`**
- Complete the reset. After this, Play will **expect** the new key (the one you just created).

---

## Step 4: Build a new AAB

Still in PowerShell from `mobile`:

```powershell
.\build-aab.ps1
```

This signs the bundle with the **new** keystore (the one that matches the PEM you uploaded).

---

## Step 5: Upload the new AAB to Play

- In Play Console go to **Release** → **Create new release** (or your release track).
- Upload: **`mobile\android\app\build\outputs\bundle\release\app-release.aab`**

Play should accept it because the AAB is now signed with the key you registered in Step 3.

---

## Summary

| Step | What to do |
|------|------------|
| 1 | Play Console → Setup → App integrity → **Reset upload key** |
| 2 | Run `py reset_or_find_play_upload_key.py --make-new` (save the password) |
| 3 | In Play Console, upload `android\upload_certificate.pem` |
| 4 | Run `.\build-aab.ps1` |
| 5 | Upload the new `app-release.aab` in Play Console |

After this, keep **the same** `upload-keystore.jks` and password for all future releases; do not overwrite the keystore unless you plan to reset the upload key again.
