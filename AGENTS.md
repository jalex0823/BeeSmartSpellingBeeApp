# Agent and workflow rules

## Deployment: DigitalOcean only

**School app and production deploy use DigitalOcean only.** Do not assume or document Railway, Heroku, or other platforms for this project. References to pre-deploy, migrations, or run commands should target DigitalOcean (e.g. App Platform run commands, one-off run, or similar). Ignore or treat as legacy any Railway-specific steps (e.g. `predeploy_check.py` calling migrations is for Railway; on DigitalOcean you run migrations manually or via a DO run command if configured).

## Branch policy: main vs release/school

Two **independent** products; two branches. Updating one must not change the other.

| Branch | Product | Update freely? |
|--------|--------|----------------|
| **main** | Mobile app (production) | Yes. Update main whenever needed. Changes here do **not** affect the school version. |
| **release/school** | School Google Chrome version | Yes. Update release/school whenever needed. Changes here do **not** affect the mobile app / main. |

**Rules:**

1. **Never merge `release/school` into `main`.** The school Chrome version must not overwrite or alter the mobile app.
2. **Never merge `main` into `release/school`** unless the user explicitly asks (e.g. to bring a specific fix into school). The mobile app and school version can diverge.
3. **Updates to main** – Work on `main`, commit and push `main` only. Do not apply those changes to `release/school` unless the user requests it.
4. **Updates to release/school** – Work on `release/school`, commit and push `release/school` only. Do not apply those changes to `main`.
5. Before making or committing changes, confirm the correct branch; do not assume.

Result: you can update the mobile app (main) without affecting the school Chrome version, and update the school version (release/school) without affecting the mobile app.
