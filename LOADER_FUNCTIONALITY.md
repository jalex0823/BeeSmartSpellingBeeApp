# 🍯 BeeSmart Loader - Complete Functionality

## Visual Elements (Always Present)

### 1. Black Honeycomb Background ✅
- **Source**: `HoneyCombBg2.png`
- **Element**: `appHoneyLoader` div with background-image
- **Purpose**: Branded, thematic background during system checks

### 2. Matrix Rain Animation ✅
- **Element**: `<canvas id="matrixCanvas">`
- **Animation**: Green falling characters at 30fps
- **Purpose**: Visual engagement while checks run

### 3. BeeSmart Crest Logo ✅
- **Source**: `BeeSmartCrestLogo1.png`
- **Element**: `<img id="loaderLogo">`
- **Position**: Center of loader, above progress text

### 4. Load Percentage ✅
- **Element**: `<div id="loaderPercentText">`
- **Range**: 0% → 100%
- **Updates**: Real-time as each system check completes

### 5. System Status Text ✅
- **Task Name**: `<div id="loaderProcessName">` - Current task (e.g., "Health", "Wordbank")
- **Detail**: `<div id="loaderStatusDetail">` - Specific action (e.g., "Checking system health…")

---

## Real System Checks (Not Just for Show!)

### Check Sequence (5 Tasks)

| # | Task | Endpoint/Action | Timeout | What It Checks |
|---|------|----------------|---------|----------------|
| 1 | **Core Assets** | Preload 2 images | N/A | Logo and honeycomb background accessible |
| 2 | **Health Check** | `GET /health` | 1000ms | Backend server responding, app version |
| 3 | **Wordbank** | `GET /api/wordbank` | 1200ms | Word lists loaded, count > 0 |
| 4 | **Mascot Avatar** | `HEAD /static/assets/.../mascot-bee.obj` | 1200ms | 3D model file exists and accessible |
| 5 | **Dictionary Cache** | Simulated 500ms delay | N/A | Dictionary priming complete |

### Check Results Logged

Each check records:
```javascript
{
  name: "Health Check",
  status: "success" | "warning" | "error" | "timeout",
  timestamp: "2025-11-11T12:34:56.789Z",
  // Additional details:
  version: "1.6",      // from /health
  words: 245,          // from wordbank
  size: "1234567",     // from HEAD check
  error: "timeout"     // if failed
}
```

---

## Diagnostic Logging

### Storage Location
- **sessionStorage**: Key `beeSmartDiagnostics`
- **Persists**: For current browser session only
- **Format**: JSON object

### Diagnostic Structure
```javascript
{
  timestamp: "2025-11-11T12:34:56.789Z",
  completedAt: "2025-11-11T12:34:59.234Z",
  duration: 2445,  // milliseconds
  healthPercentage: 100,  // 0-100%
  
  checks: [
    { name: "Core Assets", status: "success", ... },
    { name: "Health Check", status: "success", ... },
    // ... all 5 checks
  ],
  
  warnings: [
    // Any checks with status: "warning"
  ],
  
  errors: [
    // Any checks with status: "error" or "timeout"
  ],
  
  summary: {
    totalChecks: 5,
    successful: 4,
    warnings: 0,
    errors: 1,
    healthPercentage: 80
  }
}
```

### Viewing Diagnostics

Users can access the log via browser console:

```javascript
// View formatted diagnostics report
SystemChecks.viewDiagnostics()

// Get raw diagnostic object
SystemChecks.getDiagnostics()

// Check sessionStorage directly
JSON.parse(sessionStorage.getItem('beeSmartDiagnostics'))
```

**Output Example:**
```
🍯 BeeSmart System Diagnostics
  Timestamp: 2025-11-11T12:34:56.789Z
  Total Checks: 5
  Warnings: 0
  Errors: 1
  
  ┌─────┬─────────────────┬─────────┬──────────────┐
  │ idx │ name            │ status  │ timestamp    │
  ├─────┼─────────────────┼─────────┼──────────────┤
  │ 0   │ Core Assets     │ success │ ...56.890Z   │
  │ 1   │ Health Check    │ success │ ...57.123Z   │
  │ 2   │ Wordbank        │ timeout │ ...58.456Z   │
  │ 3   │ Mascot Avatar   │ success │ ...58.789Z   │
  │ 4   │ Dictionary Cache│ success │ ...59.234Z   │
  └─────┴─────────────────┴─────────┴──────────────┘
```

---

## 🚨 Critical: 55% Health Threshold

### Minimum System Health Required

Before allowing the page to proceed, the loader calculates:

```
Health % = (Successful Checks / Total Checks) × 100
```

**THRESHOLD: 55% minimum**

### What Happens Below 55%

If system health < 55%:

1. **Loader HALTS** - Does NOT proceed to main page
2. **Visual Feedback**:
   - Progress bar stops at actual health %
   - Task name: `"System Health Critical"`
   - Detail text: `"Only 40% of systems healthy (need 55%)"`
   - Red error message displayed

3. **Console Error**:
   ```
   🚫 System health at 40% - below minimum threshold of 55%
   Critical systems failed. View diagnostics: SystemChecks.viewDiagnostics()
   ```

4. **Diagnostic Log Updated**:
   ```javascript
   {
     criticalFailure: true,
     healthPercentage: 40,
     thresholdRequired: 55,
     // ... rest of log
   }
   ```

5. **User Action Required**:
   - Refresh the page
   - Check network connection
   - Contact support if persists

### Example Scenarios

| Successful Checks | Health % | Result |
|-------------------|----------|--------|
| 5 / 5 | 100% | ✅ Proceed (All healthy) |
| 4 / 5 | 80% | ✅ Proceed (Above threshold) |
| 3 / 5 | 60% | ✅ Proceed (Above threshold) |
| 2 / 5 | 40% | ❌ HALT (Below 55%) |
| 1 / 5 | 20% | ❌ HALT (Critical failure) |
| 0 / 5 | 0% | ❌ HALT (Complete failure) |

---

## Safety Features

### 1. Timeout Protection
- Every network call has timeout (1000-1200ms)
- Prevents infinite hanging
- Failed checks logged but don't crash loader

### 2. 5-Second Safety Ceiling
```javascript
setTimeout(() => { if(!finished) finish(); }, 5000);
```
- Absolute maximum: 5 seconds
- Forces completion even if checks hang
- Ensures page never frozen indefinitely

### 3. Graceful Degradation
- If check fails (timeout/error), loader continues
- Failure logged to diagnostics
- Only halts if health < 55%

### 4. No Double-Execution
```javascript
if (window.honeyLoaderLoaded) return;
window.honeyLoaderLoaded = true;
```
- Prevents multiple loader instances
- Protects against template duplication

---

## Console Feedback

### Healthy Load
```
🍯 BeeSmart loaded in 2445ms - All systems healthy (100%) ✓
```

### Load with Issues (but above 55%)
```
⚠️ BeeSmart loaded in 2801ms (80% healthy) with 1 errors, 0 warnings. 
   View: SystemChecks.viewDiagnostics()
```

### Critical Failure (below 55%)
```
🚫 System health at 40% - below minimum threshold of 55%
Critical systems failed. View diagnostics: SystemChecks.viewDiagnostics()
```

---

## Visual Flow

```
1. Page loads
   ↓
2. Honeycomb background appears
   Matrix rain starts
   Logo displays at 0%
   ↓
3. "Core… 0%" → Preload assets
   ↓
4. "Health… 20%" → Check backend
   ↓
5. "Wordbank… 40%" → Load word lists
   ↓
6. "Avatars… 60%" → Check mascot model
   ↓
7. "Definitions… 80%" → Prime dictionary
   ↓
8. Calculate health percentage
   ↓
   If < 55%: HALT with error message
   If ≥ 55%: Continue ↓
   ↓
9. "Ready 100%" → Fade out loader
   ↓
10. Fire honeyLoaderFinished event
    ↓
11. Main page visible
```

---

## API Exposed

### `window.SystemChecks`

```javascript
SystemChecks.setProgress(percent, label)  // Update progress bar
SystemChecks.setDetail(text)               // Update detail text
SystemChecks.finish()                      // Force completion
SystemChecks.getDiagnostics()              // Get raw log object
SystemChecks.viewDiagnostics()             // Pretty-print to console
```

---

## Summary: What Makes This Real

✅ **Real network calls** to actual endpoints  
✅ **Real timeouts** prevent hanging  
✅ **Real logging** to sessionStorage  
✅ **Real threshold** (55%) enforced  
✅ **Real visual feedback** (progress, status, errors)  
✅ **Real diagnostics** accessible to users  
✅ **Real halting** if systems critical  

**This loader doesn't fake it - it actually checks your app's health before letting users in!** 🍯✨
