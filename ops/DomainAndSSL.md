# Domain, DNS, and SSL Setup — beesmartspelling.app

This guide ensures both apex (beesmartspelling.app) and www work over HTTPS, with a single canonical URL used in store listings.

## Summary
- Canonical domain: https://beesmartspelling.app (apex)
- Alternate: https://www.beesmartspelling.app → 301 redirect to apex
- Server IP (A record): 88.223.85.168
- SSL: one certificate covering both beesmartspelling.app and www.beesmartspelling.app

## DNS (Hostinger)
Create/verify the following records in your Hostinger DNS Zone:

- A @ → 88.223.85.168
- CNAME www → beesmartspelling.app

Notes
- TTL: 300–3600 seconds is fine
- If you must use A for www, point A www → 88.223.85.168 (CNAME is preferred)
- If you later get IPv6, add AAAA @ and AAAA www accordingly

## SSL (HTTPS)
Use Hostinger’s built‑in SSL (Let’s Encrypt) or your preferred certificate:
- Include both domains: beesmartspelling.app and www.beesmartspelling.app
- Enable auto‑renew
- Confirm the full chain is served (no intermediate missing)

Validation
- Visit: https://beesmartspelling.app and https://www.beesmartspelling.app
- Use SSL Labs (optional) to verify trust and chain

## Redirects (force one canonical URL)
Choose apex (recommended; matches store docs). Implement 301 redirects from www → apex.

Apache (.htaccess):
```
RewriteEngine On
RewriteCond %{HTTPS} !=on [OR]
RewriteCond %{HTTP_HOST} ^www\.beesmartspelling\.app$ [NC]
RewriteRule ^(.*)$ https://beesmartspelling.app/$1 [L,R=301]
```

NGINX (server block):
```
server {
  listen 80;
  listen 443 ssl;
  server_name www.beesmartspelling.app;
  return 301 https://beesmartspelling.app$request_uri;
}
```

Hostinger hPanel Redirects
- Add a Permanent (301) redirect from https://www.beesmartspelling.app/* → https://beesmartspelling.app/$1

## Force HTTPS
If your stack supports it, force all HTTP → HTTPS:

Apache (.htaccess):
```
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [L,R=301]
```

NGINX:
```
server {
  listen 80;
  server_name beesmartspelling.app;
  return 301 https://beesmartspelling.app$request_uri;
}
```

## HSTS (optional, advanced)
Only enable if you’re certain HTTPS works everywhere (including www):
- Header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
- Consider preloading later; it’s hard to roll back

## Health endpoint
Ensure the app responds at:
- https://beesmartspelling.app/health → HTTP 200 and version v1.6
- If a reverse proxy is used, pass /health through without auth or caching

## Store and policy URLs
Use the apex (canonical) version everywhere:
- Privacy: https://beesmartspelling.app/privacy
- Terms: https://beesmartspelling.app/terms
- Support: https://beesmartspelling.app/support
- Marketing/Home: https://beesmartspelling.app

## SEO basics (optional)
- Add <link rel="canonical" href="https://beesmartspelling.app/..."> on pages
- Create /sitemap.xml and /robots.txt allowing crawling of policy pages

## Review checklist
- [ ] Apex loads with valid SSL
- [ ] www redirects (301) to apex
- [ ] /privacy, /terms, /support return HTTP 200
- [ ] /health returns 200 with v1.6 body
- [ ] URLs pasted into App Store Connect and Play Console
