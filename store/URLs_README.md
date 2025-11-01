# Finalize Privacy Policy and Terms URLs

Publish these pages and paste the final URLs into both Apple App Store Connect and Google Play Console.

## Option A — Host on your domain
- Privacy Policy: https://beesmartspelling.app/privacy
- Terms: https://beesmartspelling.app/terms
- Support: https://beesmartspelling.app/support

Canonical domain note:
- Use https://beesmartspelling.app as the canonical URL in store listings.
- Ensure https://www.beesmartspelling.app redirects (301) to https://beesmartspelling.app.

## Option B — GitHub Pages (quick)
1) Create a `gh-pages` branch or `docs/` folder in your repo
2) Add `privacy.html` and `terms.html` (you can adapt `store/PrivacyPolicy.md` and `store/TermsOfUse.md`)
3) Enable GitHub Pages and obtain URLs like:
   - https://YOUR-USERNAME.github.io/BeeSmartSpellingBeeApp/privacy
   - https://YOUR-USERNAME.github.io/BeeSmartSpellingBeeApp/terms

## Option C — Serve from the app (Flask)
- Add routes `/privacy` and `/terms` that render static templates from `templates/`
- Be sure these routes are reachable publicly for reviewers

After publishing, update:
- `store/AppStoreListing.md`
- `store/PlayStoreListing.md`
- `store/ReviewerNotes.md`
