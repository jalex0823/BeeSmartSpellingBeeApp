# BeeSmart — Quiz Pipeline Smoke Test Checklist (Web + iOS)

**Purpose:** Final stabilization validation before release approval.

**Rule:** Any failure in a MUST-PASS item is a **blocking defect**.

---

## Quick setup

- Test environments:
  - **Web (localhost)**
  - **iOS WebView (Capacitor)**

- Test word lists (repo root examples):
  - `10WordList.txt`
  - `50Words_kidfriendly.txt`

- Run types:
  - **External wordbank** (imported)
  - **Internal/default wordbank**

---

## MUST-PASS gates (release sign-off)

Release is **PASS** only if all are true in both **Web** and **iOS WebView**:

1. **Totals match everywhere**
   - Import UI total
   - Menu/wordbank total
   - Quiz start total (`0/N`)
   - Report card total (`N`)

2. **Replace import is not cumulative**
   - Replacing a list results in **exactly** the new list size.

3. **Clear truly clears**
   - After clear + reload, **no old external words** appear.

4. **Randomization integrity**
   - 10-word full run: no repeats before exhausting the set; no missing words.

5. **Normalization + scoring integrity**
   - Case/whitespace behave consistently.
   - Score counters match expected math.

6. **Buzz Points award exactly once per completion**
   - No duplication on refresh/reload/revisit results.

---

## Environment A — Web (localhost) smoke flow

### A0) Baseline reset
- Clear wordbank.
- Reload menu and quiz pages (fresh).

**Expect:** totals show **0** for external bank.

### A1) Import 10 words (external)
1. Import `10WordList.txt`.
2. Verify total = **10** on import success UI.
3. Verify menu/wordbank view total = **10**.
4. Start quiz.

**Expect:** quiz shows **0/10**.

### A2) Randomization integrity (10 word full run)
- Complete the entire 10-word quiz.

**Expect:**
- Each word appears once (unless app intentionally allows repeats).
- Final report: total = 10; correct+incorrect = 10.

### A3) Replace-only import behavior
1. Import a different list (e.g., `20Wordlist.txt`) using **replace** behavior.
2. Verify total becomes **20** (not 30).
3. Start quiz.

**Expect:** quiz shows **0/20**, never an older stale total.

### A4) Clear between runs
1. Clear external wordbank.
2. Reload quiz.

**Expect:** quiz does not use prior external words; external total is **0**.

### A5) Refresh/Resync + Restart/Reshuffle recovery
On an active quiz session:
- Click **↻ Refresh/Resync**.
  - **Expect:** totals sync to live wordbank count; polling continues.
- Click **⟲ Restart**, confirm modal.
  - **Expect:** progress resets to **0/N** and order changes.

### A6) Import 50 words (external)
1. Import `50Words_kidfriendly.txt`.
2. Verify totals = **50** everywhere.
3. Start quiz.

**Expect:** quiz shows **0/50**.

### A7) Scoring & normalization spot checks
Pick a known word and validate:
- Case variants: `bee`, `BEE`, ` Bee `
- (If intended) punctuation tolerance: `bee!`, `bee.`

**Expect:** outcomes match intended normalization rules.

---

## Environment B — iOS WebView (Capacitor) smoke flow

Repeat the Web flow (A0–A7) with these extra iOS-specific checks:

### B0) iOS-specific preflight
- Confirm the app is pointing at the correct backend/base URL (dev vs prod as configured).
- Confirm the quiz page loads without layout regressions (header buttons visible and tappable).

### B1) Touch + modal behavior
- Tap **⟲ Restart**.

**Expect:** modal is centered, buttons usable, backdrop dismiss works, and it does not freeze the UI.

### B2) Network resilience (basic)
- Toggle airplane mode briefly during an active quiz.
- Restore network.
- Tap **↻ Refresh/Resync**.

**Expect:** recovery occurs and quiz is usable; no hard lock.

---

## Defect logging template (blocking)

- **ID:** DEFECT-YYYYMMDD-###
- **Title:**
- **Severity:** Blocker / Major / Minor
- **Environment:** Web localhost / iOS WebView (device + iOS version)
- **Build/Commit:**
- **Preconditions:** (guest/auth, internal/external mode, wordbank size)
- **Steps to Reproduce:**
  1.
  2.
  3.
- **Expected Result:**
- **Actual Result:**
- **Artifacts:** screenshot/video, console logs, server logs
- **Notes:** suspected area (`/api/wordbank`, `/api/live-status`, import parsing, report calc)
