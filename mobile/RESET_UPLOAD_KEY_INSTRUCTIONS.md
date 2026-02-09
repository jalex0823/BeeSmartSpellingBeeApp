# Fix "Wrong Key" Error — Reset Upload Key in Play Console

Google Play expects: **SHA1: 02:5E:52:B2:D1:EC:17:06:8A:19:0C:66:88:9E:F9:D1:3A:8A:7D:D5**  
Your current keystore has: **SHA1: F4:7B:09:38:F2:77:ED:CC:51:42:50:0D:D5:B8:62:0F:6C:55:FC:75**

To fix this, **reset the upload key** in Play Console and use the new certificate.

---

## Step 1: Reset upload key in Play Console

1. Go to [Google Play Console](https://play.google.com/console)
2. Select your app (**BeeSmartSpelling** with package `com.beesmart.spellingbee`)
3. Navigate: **Setup** → **App integrity** → **Upload key certificate**
4. Click **Reset upload key** (or "Request upload key reset")
5. Follow the wizard — when it asks for the new certificate, continue to Step 2

---

## Step 2: Upload the certificate

When Play Console asks for the new upload certificate, upload this file:

```
f:\GitHub\BeeSmartSpellingBeeApp\mobile\android\upload_certificate.pem
```

---

## Step 3: Upload the AAB

After the reset is approved, upload your signed AAB:

```
f:\GitHub\BeeSmartSpellingBeeApp\mobile\android\app\build\outputs\bundle\release\app-release.aab
```

This AAB is already signed with the keystore that matches the certificate you uploaded.

---

## If you have the original keystore

If you still have the keystore with SHA1 `02:5E:52:B2:D1:EC:...` (e.g. from a backup or another machine):

1. Copy it to `mobile/android/upload-keystore.jks` (replace the current one)
2. Update `mobile/android/keystore.properties` with the correct password and alias
3. Rebuild the AAB

You would **not** need to reset the upload key in that case.
