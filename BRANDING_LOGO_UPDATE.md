# BeeSmart Branding Logo Update

This repository has been switched to use a new global logo asset.

- Canonical path: `static/images/BeeSmartSpellingBeeApplication.png`
- Version param in templates: `?v=20251108` to help bust caches
- Runtime brand script reads `window.BeeSmartBrand.logoPath`

What you need to do
1) Save the provided new logo image file as:
   `static/images/BeeSmartSpellingBeeApplication.png`
2) (Optional) If you prefer a different filename, update all references of `BeeSmartSpellingBeeApplication.png` accordingly and keep the version param.

Fail-safe
- Until the new file exists, pages will fall back at runtime to the previously committed logo `LogoBee&WordingTM.png` for inline images via `static/js/brand-logo-replacer.js`.
- Favicons and email previews reference the new path directly; add the file to ensure they render the new artwork.

Verification
- Start the app and visit `/app`. Inspect `<img>` and favicon requests in the Network tab to confirm the new asset is served from `/static/images/BeeSmartSpellingBeeApplication.png`.
