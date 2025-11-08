# Reviewer Notes & Test Access — BeeSmart Spelling Bee

## Test Accounts (placeholders)
- Student: student_demo / Password: REVIEW‑ONLY
- Teacher (optional): teacher_demo / Password: REVIEW‑ONLY

Add final credentials in the App Store Connect and Play Console private notes. If your app provisions test users via a backend, pre‑seed these accounts and ensure the passwords match.

## Test Data
- Include `50Words_kidfriendly.txt` accessible from the app’s Upload page and/or ship a sample in the bundle.

## Review Walkthrough
1) Upload the sample list and start a quiz
2) Answer one word via voice (allow microphone permission)
3) Tap “Hint” to show a clue that does not reveal the word
4) Try OCR: import a sample worksheet image and confirm words are added

## Networking and Availability
- Health endpoint: https://beesmartspelling.app/health (returns version v1.7)
- Please ensure the server is reachable during review hours.

## Permissions Rationale
- Microphone: learners can speak answers
- Camera/Photos: scan word lists with OCR; pick files for upload

## Known Limitations
- No third‑party ads or tracking; no social features.
- If accounts are enabled, only teacher/parent/admin accounts are available—kids use without sign‑in.
