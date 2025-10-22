# iOS Voice Fixes - BeeSmart Spelling Bee App

## Issues Identified
1. **Intro voice not playing on iOS** - Speech synthesis requires user interaction
2. **Male vs Female voice inconsistency** - Voice selection not optimized for iOS

## Root Causes

### iOS Speech Synthesis Limitations
- iOS requires **user interaction** before `speechSynthesis` can play audio (auto-play policy)
- iOS has different voice names than desktop browsers
- Voice loading is asynchronous and needs explicit handling

### Voice Consistency Issues
- Voice caching happened once but iOS-specific voices weren't prioritized
- Desktop optimized for British English, but iOS doesn't always have those voices
- Need platform-specific voice selection

## Fixes Applied

### 1. iOS-Specific Voice Selection
```javascript
// iOS Priority: Samantha (US English Female) - clearest on iOS
// Fallback: Karen (Australian English Female)
// Desktop Priority: British English Female voices
```

**Location**: `templates/quiz.html` line ~1990 in `speakAnnouncement()` function

**Changes**:
- Detect iOS device: `/iPhone|iPad|iPod/i.test(navigator.userAgent)`
- iOS uses: Samantha → Karen → Any female English voice
- Desktop uses: British English female → British English → Any female English
- Ensures consistent **female voice** across all platforms

### 2. Voice Preloading for iOS
```javascript
// iOS fix: Force voice loading by creating dummy utterance first
const dummyUtterance = new SpeechSynthesisUtterance('');
speechSynthesis.speak(dummyUtterance);
speechSynthesis.cancel();
```

**Location**: `templates/quiz.html` line ~2280 (desktop intro) and line ~2210 (mobile intro)

**Purpose**:
- iOS requires a "dummy" utterance to activate speech synthesis
- This unlocks the speech API so voices can load properly
- Must happen before any actual speech

### 3. Voice Loading Timeout
```javascript
// Wait for voices with 2-second timeout
await new Promise(resolve => {
    const timeout = setTimeout(() => {
        console.warn('⏰ Voice loading timeout after 2 seconds');
        resolve();
    }, 2000);
    
    speechSynthesis.addEventListener('voiceschanged', () => {
        clearTimeout(timeout);
        resolve();
    }, { once: true });
});
```

**Location**: `templates/quiz.html` line ~2225 (mobile intro)

**Benefits**:
- Prevents infinite waiting if voices fail to load
- Still allows quiz to start even without voice
- Logs helpful debugging info

### 4. Enhanced Console Logging
```javascript
console.log('🍎 iOS device detected - selecting optimal voice');
console.log('🍎 iOS voice locked for consistency');
console.log('🎤 Initial voices loaded:', voices.length);
```

**Purpose**:
- Easy debugging on iOS Safari (connect via Mac)
- Track voice selection process
- Identify voice loading issues

## Testing Checklist

### Desktop (Chrome/Edge/Firefox)
- ✅ Intro voice plays automatically (British English female)
- ✅ Quiz announcements use same voice throughout
- ✅ Definition sentences use same voice

### iOS Safari
- ✅ Mobile intro requires "Start Quiz" button tap (user interaction)
- ✅ Voice plays after button tap (Samantha or Karen)
- ✅ All announcements use same female voice
- ✅ No voice switching between intro and quiz

### Android Chrome
- ✅ Mobile intro with voice after "Start Quiz" tap
- ✅ Female voice selection (British English preferred)
- ✅ Consistent voice throughout quiz

## Voice Selection Priority

### iOS Devices
1. **Samantha** (en-US Female) - Most natural on iOS
2. **Karen** (en-AU Female) - Clear Australian accent
3. **Any female English voice**

### Desktop/Android
1. **British English Female** (Kate, Serena, Susan, etc.)
2. **Any British English voice**
3. **Any female English voice** (Samantha, Victoria, Joanna, etc.)

## Expected User Experience

### iOS Users
1. Land on quiz page
2. See "🐝 Tap to Start!" message (mobile intro required)
3. Tap "Start Quiz" button
4. Hear Buzzy (female voice): "Hello! I'm Buzzy, your announcer bee! Let's start spelling!"
5. Quiz loads with same female voice for all words

### Desktop Users
1. Land on quiz page
2. Automatically hear intro (no button tap needed)
3. Voice plays: "Hello! I'm Buzzy, your announcer bee! Welcome to BeeSmart Spelling!"
4. Quiz auto-advances after 7 seconds
5. Same voice throughout quiz

## Known Limitations

### iOS Restrictions
- **User interaction required**: iOS auto-play policy blocks speech without user gesture
- **Voice names vary**: iOS voice names differ from desktop browsers
- **No British voices**: iOS may not have British English voices installed

### Workarounds Implemented
- ✅ Mobile intro requires button tap (satisfies user interaction requirement)
- ✅ iOS-specific voice selection (Samantha/Karen)
- ✅ Voice preloading with dummy utterance
- ✅ Graceful fallback if voices unavailable

## Debugging on iOS

### Connect iOS Device to Mac
1. Connect iPhone/iPad via USB
2. Open Safari on Mac
3. Safari → Develop → [Your Device] → [Page Name]
4. Check Console for voice logs:
   - `🍎 iOS device detected`
   - `🎤 Selected voice for session: Samantha (en-US)`
   - `🍎 iOS voice locked for consistency`

### Common Issues
- **No sound**: Check iOS device is not in silent mode
- **Wrong voice**: Check console for selected voice name
- **Voice not loading**: Check for timeout message after 2 seconds

## Files Modified
- `templates/quiz.html` - Voice selection logic, iOS detection, voice preloading

## Commit Details
- **Branch**: main
- **Files changed**: 1 (quiz.html)
- **Changes**: ~50 lines modified in voice selection and initialization
