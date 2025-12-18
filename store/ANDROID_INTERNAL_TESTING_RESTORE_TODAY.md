# Android Internal Testing → Restore Purchases (today checklist)

This is the fastest path to a **real** Play Billing restore test (not a mock).

## 0) Prereqs

- You have a Google Play Console app created for the package name `com.beesmart.spelling`.
- You have at least one test SKU (subscription or one-time) configured in Play Console.
- You have a tester Google account (Gmail) you can use on a real Android device.

## 1) Create signing (upload key)

From `mobile/`:

- Run `setup-keystore.ps1` (generates `mobile/android/upload-keystore.jks`)
- Run `setup-signing.ps1` (creates `mobile/android/keystore.properties`)

Notes:

- These files are intentionally ignored by git. Keep them safe.
- If you already have an upload key from Play Console, reuse it.

## 2) Build the release AAB

From `mobile/`:

- Run `build-release.ps1` (or build in Android Studio)

Expected output:

- `mobile/android/app/build/outputs/bundle/release/app-release.aab`

## 3) Publish to Internal testing

In Play Console:

- Create an **Internal testing** track release and upload the `.aab`.
- Add testers (email list or Google Groups).
- Copy the **opt-in link**.

## 4) Device install (critical)

On the Android device:

- Sign into the **tester Google account** in the Play Store.
- Open the opt-in link, accept, then install from the Play Store listing.

## 5) Validate restore

Follow `store/NATIVE_SANDBOX_RESTORE_RUNBOOK.md`.

Minimum “today” pass criteria:

- Purchase 1 item (subscription or one-time)
- Uninstall
- Reinstall from Play internal track
- Tap **Restore Purchases**
- Premium unlocks / owned content shows as owned

## If something fails

Common causes:

- App installed by sideload (no Play purchase history)
- Wrong Google account on device
- SKU not active / not available to the tester
- Build package name doesn’t match the Play app
