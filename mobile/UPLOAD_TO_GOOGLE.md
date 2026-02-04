# Upload BeeSmart to Google Play (short path)

Get a signed AAB, then upload it in [Play Console](https://play.google.com/console) → your app → **Release** → **Create new release** → upload the `.aab` file.

---

## Reset upload key (lost key / new key)

Do these in order:

1. **Play Console** → your app → **Setup** → **App integrity** → **Upload key certificate** → **Reset upload key** (or “Request upload key reset”). Start the process; they’ll ask for a new certificate in step 3.

2. **Generate new keystore + certificate** (in PowerShell from `mobile`):
   ```powershell
   cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
   py reset_or_find_play_upload_key.py --make-new
   ```
   - Pick a **strong password** and save it (you need it for every future release).
   - This creates `android/upload-keystore.jks`, `android/upload_certificate.pem`, and `android/keystore.properties`.

3. **Back in Play Console**, when it asks for the new upload certificate, upload:
   - **`mobile\android\upload_certificate.pem`**

4. **Build the AAB**:
   ```powershell
   .\build-aab.ps1
   ```

5. **Upload** `android\app\build\outputs\bundle\release\app-release.aab` in Play Console → Release → Create new release.

---

## Do you have the right signing key?

Play expects this **upload key** SHA1:  
`EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13`

- **Yes, I have that keystore** (or I’m not sure) → [Path A](#path-a-use-your-existing-keystore)  
- **No, I lost it / I want a new key** → [Path B](#path-b-reset-upload-key-in-play-then-use-new-keystore)

---

## Path A: Use your existing keystore

1. Put your `.jks` (or `.keystore`) in **`mobile/android/`** and name it `upload-keystore.jks` (or set `storeFile` in step 2 to match the filename).
2. Create **`mobile/android/keystore.properties`** (copy from `keystore.properties.example` and fill in):
   - `storeFile=upload-keystore.jks`
   - `storePassword=YOUR_KEYSTORE_PASSWORD`
   - `keyPassword=YOUR_KEY_PASSWORD`
   - `keyAlias=upload` (or whatever alias your key uses)
3. Check the fingerprint (optional):
   ```powershell
   cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
   .\show-keystore-fingerprint.ps1
   ```
   SHA1 should be `EF:B0:34:20:...` (same as above).
4. Build the AAB:
   ```powershell
   .\build-aab.ps1
   ```
5. Upload **`mobile\android\app\build\outputs\bundle\release\app-release.aab`** in Play Console.

---

## Path B: Reset upload key in Play, then use new keystore

Use this if you don’t have the original keystore or want to start fresh.

1. **In Play Console:** your app → **Setup** → **App integrity** → **Upload key certificate** → **Reset upload key** (or request a new upload key). Follow the prompts.
2. **On your PC**, generate a new keystore and PEM (for the reset):
   ```powershell
   cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
   py reset_or_find_play_upload_key.py --make-new
   ```
   - Choose and save a **strong keystore password**.
   - This creates `android/upload-keystore.jks`, `android/upload_certificate.pem`, and `android/keystore.properties`.
3. **Back in Play Console**, when it asks for the new upload certificate, upload **`android/upload_certificate.pem`**.
4. Build the AAB:
   ```powershell
   .\build-aab.ps1
   ```
5. Upload **`mobile\android\app\build\outputs\bundle\release\app-release.aab`** in Play Console.

---

## If something fails

| Problem | What to do |
|--------|------------|
| **“Wrong key” when uploading AAB** | You’re signing with a different key than Play expects. Use Path A with the keystore that has SHA1 `EF:B0:34:20:...`, or do Path B to reset the upload key. |
| **keytool not found** | Install JDK 17 (e.g. [Eclipse Temurin](https://adoptium.net/)) and ensure `JAVA_HOME` is set, or run `.\set-java.ps1` / see SIGNING_QUICKSTART.md. |
| **No keystore.properties** | Path A: create it from `keystore.properties.example`. Path B: `reset_or_find_play_upload_key.py --make-new` creates it. |
| **Gradle / build errors** | From `mobile/`: `npm run build` then `npx cap sync android`, then run `.\build-aab.ps1` again. |

---

**One-liner (after you have a valid keystore + keystore.properties):**

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
.\build-aab.ps1
```

Then upload **`android\app\build\outputs\bundle\release\app-release.aab`** in Google Play Console.
