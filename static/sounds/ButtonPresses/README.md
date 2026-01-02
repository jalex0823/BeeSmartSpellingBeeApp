# ButtonPresses SFX (optional)

This folder is an **optional** pack of short button-press sound effects.

- The app will request an available playlist from `GET /api/button-press-sfx` and randomly choose from whatever `.mp3` files exist in this folder.
- If this folder is empty or missing, the UI falls back to `/static/sounds/button-click.mp3`.

## Licensing note

Only place sound files here if you have the **right to distribute** them (e.g., original recordings, properly licensed royalty-free assets, or assets you created).

To prevent accidental commits of unvetted audio, the repo ignores `static/sounds/ButtonPresses/*.(mp3|wav|ogg)` by default (see `.gitignore`). If you intentionally want to version-control licensed sounds, update `.gitignore` accordingly.
