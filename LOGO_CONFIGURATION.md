# BeeSmart Logo Configuration

## How to Change the Logo Across the Entire Application

All logo references in the BeeSmart Spelling Bee Application are now centralized. To change the logo everywhere, you only need to update **ONE** file.

### Quick Guide

1. **Replace the logo file:**
   - Place your new logo at: `/static/images/BeeSmartSpellingBeeApplication.png`
   - The file MUST be named exactly: `BeeSmartSpellingBeeApplication.png`

2. **Update the version number:**
   - Open: `/static/js/logo-config.js`
   - Find the line: `const LOGO_VERSION = '20251112';`
   - Change to a new date or number: `const LOGO_VERSION = '20251113';`
   - This ensures browsers reload the new logo (cache busting)

That's it! The logo will update everywhere automatically.

### Where the Logo Appears

The centralized logo appears in:
- ✅ Honey pot loading screen
- ✅ Main menu welcome screen
- ✅ System loading overlay (pink subloader)
- ✅ Base template loader
- ✅ All pages using the brand logo
- ✅ Email templates
- ✅ PWA icons and favicons

### Advanced: Changing the Logo Path

If you want to use a different filename or location:

1. Open: `/static/js/logo-config.js`
2. Edit the MASTER_LOGO_PATH:
   ```javascript
   const MASTER_LOGO_PATH = '/static/images/YOUR_NEW_LOGO.png';
   ```
3. Update the version number
4. Restart the Flask server

### Technical Details

The centralized logo system works through:

- **Master Config:** `/static/js/logo-config.js` - Central configuration
- **Global Object:** `window.BeeSmartLogo` - JavaScript API
- **Auto-Replace:** Automatically finds and updates all logo images on page load
- **Backward Compatible:** Works with legacy `window.BeeSmartBrand.logoPath`

### JavaScript API

You can programmatically access the logo in JavaScript:

```javascript
// Get the logo URL (with cache busting)
const logoUrl = window.BeeSmartLogo.getUrl();

// Get the logo path (without version)
const logoPath = window.BeeSmartLogo.getPath();

// Apply logo to a specific image element
const img = document.getElementById('myLogo');
window.BeeSmartLogo.applyToImage(img);

// Replace all logos on the page
window.BeeSmartLogo.replaceAll();
```

### Troubleshooting

**Logo not updating?**
1. Clear your browser cache (Cmd+Shift+R or Ctrl+Shift+R)
2. Make sure you updated the LOGO_VERSION in logo-config.js
3. Restart the Flask server

**Logo appears broken?**
1. Check the file exists at `/static/images/BeeSmartSpellingBeeApplication.png`
2. Verify the filename matches exactly (case-sensitive)
3. Check browser console for 404 errors

### Files Modified for Centralization

The following files now use the centralized logo:
- `/templates/base.html`
- `/templates/unified_menu.html`
- `/static/js/logo-config.js` (NEW - master configuration)

All other files will automatically inherit the logo through these templates.
