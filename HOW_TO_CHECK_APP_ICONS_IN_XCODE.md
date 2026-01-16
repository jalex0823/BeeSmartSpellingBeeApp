# How to Check App Icons in Xcode

**Purpose:** Verify that app icons are BeeSmart-branded (not Flutter placeholders)

---

## Method 1: Using Xcode Project Navigator (Easiest)

### Step-by-Step Instructions

1. **Open Xcode**
   - Open the project: `mobile/ios/App/App.xcworkspace` (if using CocoaPods)
   - OR: `mobile/ios/App/App.xcodeproj` (if not using CocoaPods)

2. **Navigate to Assets**
   - In the **Project Navigator** (left sidebar), expand:
     ```
     App
       └── Assets.xcassets
         └── AppIcon.appiconset
     ```

3. **Select AppIcon**
   - Click on `AppIcon` in the Project Navigator
   - The **Asset Catalog Editor** will open in the main editor area

4. **View Icons**
   - You'll see a grid showing all required icon sizes
   - Each slot shows a preview of the icon
   - **Look for:**
     - ✅ BeeSmart logo/bee theme = Good
     - ❌ Flutter logo (blue "F" on white) = Needs replacement

5. **Check Specific Sizes**
   - **1024×1024** (App Store) - Most important!
   - iPhone sizes (60×60, 120×120, 180×180)
   - iPad sizes (76×76, 83.5×83.5)
   - Notification sizes (20×20, 29×29, 40×40)

---

## Method 2: Using Finder (Quick Visual Check)

### Step-by-Step Instructions

1. **Open Finder**
   - Navigate to: `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/`

2. **View Icon Files**
   - You'll see files like:
     - `Icon-App-1024x1024@1x.png`
     - `Icon-App-60x60@2x.png`
     - etc.

3. **Preview Icons**
   - **Double-click** any icon file to preview it
   - **Look for:**
     - ✅ BeeSmart logo/bee = Good
     - ❌ Flutter logo = Needs replacement

4. **Check the 1024×1024 Icon**
   - This is the **most important** one (App Store requirement)
   - Open `Icon-App-1024x1024@1x.png`
   - Verify it shows BeeSmart branding

---

## Method 3: Using Xcode Asset Catalog Editor (Detailed)

### Step-by-Step Instructions

1. **Open Xcode Project**
   - Open: `mobile/ios/App/App.xcworkspace` or `.xcodeproj`

2. **Open Asset Catalog**
   - In Project Navigator, click: `Assets.xcassets`
   - The asset catalog opens in the main editor

3. **Select AppIcon**
   - In the asset catalog list (left side), click: `AppIcon`
   - The icon editor appears on the right

4. **View Icon Grid**
   - You'll see a grid with all required icon sizes
   - Each slot shows:
     - Icon preview (if set)
     - Size label (e.g., "1024pt")
     - Platform label (iPhone, iPad, etc.)

5. **Check Each Icon**
   - **Hover over** each icon slot to see a larger preview
   - **Click** an icon slot to see details
   - **Look for:**
     - ✅ BeeSmart logo = Correct
     - ❌ Flutter logo = Wrong (needs replacement)

6. **Check for Missing Icons**
   - Empty slots show a "+" button
   - All slots should be filled (no empty slots)

---

## What to Look For

### ✅ Good Icons (BeeSmart Branding)
- Bee/beehive theme
- Yellow/gold colors
- BeeSmart logo
- Professional appearance
- No Flutter branding

### ❌ Bad Icons (Flutter Placeholders)
- Blue "F" logo on white background
- Flutter text/logo
- Default/generic appearance
- White/blue color scheme

---

## If Icons Are Flutter Placeholders

### How to Replace Icons

1. **Prepare Your Icon**
   - Create a 1024×1024 PNG master icon
   - Must be BeeSmart-branded
   - No transparency (opaque)
   - Square format

2. **Replace in Xcode**
   - In Asset Catalog Editor, click the 1024×1024 slot
   - Drag your new icon file into the slot
   - Xcode will auto-generate other sizes (or you can manually set each)

3. **OR Replace Manually**
   - Replace files in Finder:
     - `mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/`
   - Replace each size with your BeeSmart icon
   - Keep the same filenames

4. **Verify in Xcode**
   - Return to Xcode
   - Select AppIcon in Asset Catalog
   - Verify all slots show your BeeSmart icon

---

## Quick Terminal Check (Command Line)

You can also check from terminal:

```bash
# Navigate to icon directory
cd mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/

# List all icon files
ls -la *.png

# Preview the 1024×1024 icon (macOS)
open Icon-App-1024x1024@1x.png

# Or use Quick Look
qlmanage -p Icon-App-1024x1024@1x.png
```

---

## Verification Checklist

- [ ] Open Xcode project
- [ ] Navigate to Assets.xcassets → AppIcon
- [ ] Check 1024×1024 icon (App Store requirement)
- [ ] Verify all icons show BeeSmart branding
- [ ] Confirm no Flutter logos present
- [ ] Verify all icon slots are filled
- [ ] Check both iPhone and iPad sizes

---

## Common Issues

### Issue: Icons look correct in Finder but wrong in Xcode
**Solution:** Clean build folder in Xcode (Product → Clean Build Folder)

### Issue: Some icon sizes are missing
**Solution:** Xcode can auto-generate from 1024×1024 master, or manually add each size

### Issue: Icons appear stretched or distorted
**Solution:** Ensure source icon is square (1024×1024) and properly formatted

---

## After Verification

If icons are **correct** (BeeSmart branding):
- ✅ No action needed
- Proceed with build and submission

If icons are **incorrect** (Flutter placeholders):
- ⚠️ Replace all icons with BeeSmart-branded versions
- Clean build folder
- Rebuild app
- Verify icons in simulator before archiving

---

**Quick Tip:** The easiest way is **Method 1** - just open Xcode, navigate to `AppIcon` in the Project Navigator, and visually check the icon previews in the Asset Catalog Editor.
