# Sign the AAB for Google Play Console

You need a **signed** Android App Bundle (.aab) before uploading to Google Play. Do this once (or if you lost your keystore).

---

## One-time setup (about 2 minutes)

### 1. Create the keystore

In PowerShell, from the **mobile** folder:

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
.\setup-keystore.ps1
```

- When asked **"Ready to generate keystore? (yes/no)"** type **yes**
- **keytool** will prompt for:
  - **Keystore password** – choose one and **save it**
  - **Key password** – can be the same; **save it**
  - Name, Organization, City, State, Country (e.g. BeeSmart, US)

**Important:** Store both passwords somewhere safe (e.g. password manager). You need them for every future release.

---

### 2. Create keystore.properties

Still in the **mobile** folder:

```powershell
.\setup-signing.ps1
```

- Enter the **same** keystore password and key password you used in step 1  
- This creates `android/keystore.properties` so Gradle can sign the build

---

### 3. Build a signed AAB

```powershell
.\build-aab.ps1
```

The AAB at  
`mobile\android\app\build\outputs\bundle\release\app-release.aab`  
will be **signed** and ready to upload in Google Play Console.

---

## If keytool is not found

Make sure Java (JDK 17) is on your PATH. You can use the JDK that the AAB build uses:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path
keytool -help
```

Then run `.\setup-keystore.ps1` again.

---

## Summary

| Step | Command | Result |
|------|--------|--------|
| 1 | `.\setup-keystore.ps1` | Creates `android/upload-keystore.jks` |
| 2 | `.\setup-signing.ps1` | Creates `android/keystore.properties` |
| 3 | `.\build-aab.ps1` | Builds **signed** `app-release.aab` |

Do **not** commit `upload-keystore.jks` or `keystore.properties` to git (they are in `.gitignore`).
