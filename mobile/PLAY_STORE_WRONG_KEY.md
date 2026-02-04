# Play Console: "Your Android App Bundle is signed with the wrong key"

## What the error means

Google Play requires that **every update** to your app be signed with the **same key** that was used for the **first** upload. The fingerprints you see are:

| Role | SHA1 fingerprint |
|------|-------------------|
| **Expected by Play** (original upload key) | `EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13` |
| **What you signed with** (current keystore) | `CB:9A:9B:3C:2B:8B:CF:89:3E:39:E4:33:E1:6E:7B:D9:2E:10:B0:3A` |

So the AAB you uploaded was signed with a **different** keystore than the one Play has on file.

---

## What to do

### 1. Use the correct keystore

You must build the AAB with the keystore whose **SHA1 is**  
`EF:B0:34:20:AD:97:54:1B:C8:52:1C:13:4F:1B:08:68:11:CC:9B:13`.

- That keystore might be:
  - On another machine (old laptop, previous dev setup)
  - In a backup (Dropbox, OneDrive, USB, etc.)
  - From the first time you ran `setup-keystore.ps1` or created the app’s upload key
- Put that `.jks` (or `.keystore`) file in `android/` (e.g. `android/upload-keystore.jks`).
- Point `android/keystore.properties` at it (`storeFile=upload-keystore.jks`, correct `keyAlias`, passwords).
- Rebuild the AAB and upload again.

**Check which key you’re using:**

```powershell
.\show-keystore-fingerprint.ps1
```

You will be prompted for the keystore password. The script prints the keystore’s SHA1 and whether it matches what Play expects.

---

### 2. If you no longer have that keystore (lost key)

If you **cannot** find the keystore with SHA1 `EF:B0:34:20:...`:

- You **cannot** sign updates with a new key unless Google allows a **key reset** for your app.
- In [Play Console](https://play.google.com/console) go to your app → **Setup** → **App signing** and check whether **Play App Signing** is enabled and what options you have.
- Google’s docs: [Request a key reset](https://support.google.com/googleplay/android-developer/answer/9842756) (only in certain situations; you may need to contact support).

---

## Summary

| Your situation | Action |
|----------------|--------|
| You have the original upload keystore (SHA1 `EF:B0:34:20:...`) | Put it in `android/`, set `keystore.properties`, run `.\build-aab.ps1`, upload the new AAB. |
| You’re not sure which keystore you have | Run `.\show-keystore-fingerprint.ps1` and compare the printed SHA1 to the table above. |
| You lost the original keystore | Use Play Console → App signing and Google’s key reset / support process. |
