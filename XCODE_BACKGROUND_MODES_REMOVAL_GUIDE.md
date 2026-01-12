# Remove Required Background Modes from Xcode Project

## Issue
The Xcode project has "Required Background Modes" capability enabled, but the app does not use background audio. This needs to be removed.

## Solution: Remove Background Modes in Xcode

### Step-by-Step Instructions

1. **Open Xcode Project**
   - Navigate to: `mobile/ios/App/App.xcodeproj`
   - Open in Xcode

2. **Select the App Target**
   - In the Project Navigator (left sidebar), click on the **"App"** project (blue icon)
   - Select the **"App"** target under "TARGETS" (not "PROJECT")

3. **Open Capabilities Tab**
   - Click on the **"Signing & Capabilities"** tab at the top
   - Scroll down to find **"Background Modes"** section

4. **Remove Background Modes**
   - If "Background Modes" is listed, click the **"-"** (minus) button to remove it
   - OR uncheck all boxes if it's enabled:
     - ❌ Uncheck "Audio, AirPlay, and Picture in Picture"
     - ❌ Uncheck any other background mode options

5. **Verify Removal**
   - The "Background Modes" section should no longer appear in the Capabilities list
   - If it's still there, click the **"X"** button next to "Background Modes" to completely remove it

6. **Clean Build**
   - Product → Clean Build Folder (Shift+Cmd+K)
   - This ensures the change is applied

### Visual Guide

```
Xcode → Select App Target → Signing & Capabilities Tab
↓
Find "Background Modes" section
↓
Click "-" button or uncheck all options
↓
Background Modes should disappear from list
```

### Verification

After removal, verify:
- ✅ "Background Modes" no longer appears in Capabilities
- ✅ Info.plist does not contain `UIBackgroundModes` key (already verified - it's commented out)
- ✅ App builds successfully without background mode warnings

### Why This Matters

- **Apple Guideline 2.5.4**: Apps must not declare capabilities they don't use
- **App Review**: Reviewers check for unnecessary capabilities
- **User Privacy**: Declaring unused capabilities can raise privacy concerns

### Current Status

- ✅ **Info.plist**: UIBackgroundModes is commented out (not active)
- ⚠️ **Xcode Project**: May still have Background Modes enabled in Capabilities (needs manual removal in Xcode)

---

## Alternative: Check via Command Line

If you want to verify the current state without opening Xcode:

```bash
# Check if Background Modes is in the entitlements
grep -r "UIBackgroundModes" mobile/ios/App/App.xcodeproj/

# Check Info.plist (already verified - commented out)
grep "UIBackgroundModes" mobile/ios/App/App/Info.plist
```

The Xcode project file (`.pbxproj`) may contain references that need to be removed through the Xcode UI, as manual editing can corrupt the project file.

---

## Notes

- **Do NOT manually edit** `project.pbxproj` file - always use Xcode UI
- Removing Background Modes in Xcode will automatically update the project file
- The app does not require background audio - all audio is in-app only
- This change will not affect app functionality
