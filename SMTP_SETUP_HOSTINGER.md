# Outgoing Email Setup (Hostinger SMTP)

Use these settings to send emails from Contact@beesmartspelling.app via Hostinger.

## 1) Hostinger SMTP values
- SMTP server: smtp.hostinger.com
- Port (recommended): 587 (TLS)
- TLS: true
- SSL: false
- Username: Contact@beesmartspelling.app
- Password: Your mailbox password or an app-specific password

Alternatively, SSL on port 465 is supported:
- Port: 465
- TLS: false
- SSL: true

## 2) Required environment variables
Set these in your environment (Railway, local .env, etc.).

- MAIL_SERVER=smtp.hostinger.com
- MAIL_PORT=587
- MAIL_USE_TLS=true
- MAIL_USE_SSL=false
- MAIL_USERNAME=Contact@beesmartspelling.app
- MAIL_PASSWORD=<secure-password>
- MAIL_DEFAULT_SENDER=Contact@beesmartspelling.app
- MAIL_FROM_NAME=BeeSmart Spelling Bee
- APP_BASE_URL=https://beesmartspellingbee.up.railway.app  # or your custom domain

Tip (Railway): Add these under Variables. For local dev, put them in a `.env` file at the repository root.

## 3) What this config does
- All emails (welcome, password reset) will now be sent From: "BeeSmart Spelling Bee <Contact@beesmartspelling.app>".
- The envelope sender (SMTP MAIL FROM) also uses Contact@, matching Hostinger policy.
- Reply-To is set to Contact@ so replies land in the right mailbox.

## 4) Testing
- Forgot Password flow: POST /api/auth/forgot-password (use an existing user email). Check logs and mailbox.
- Registration flow: After registering, a welcome email is sent.
- Dev fallback: If MAIL_* env vars are missing, the app logs a preview instead of sending.

## 5) Troubleshooting
- Authentication error: Verify username/password. Hostinger requires the full email address as the username.
- TLS/SSL mismatch: If using port 587, set MAIL_USE_TLS=true and MAIL_USE_SSL=false. For 465, do the opposite.
- Spam/Deliverability: Set SPF/DKIM/DMARC records on your domain for Contact@beesmartspelling.app.
- From/Reply-To mismatch: Ensure MAIL_DEFAULT_SENDER matches MAIL_USERNAME for strict SMTP policies.
