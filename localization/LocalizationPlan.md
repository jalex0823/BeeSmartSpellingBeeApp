# Localization Plan — BeeSmart Spelling Bee

## Phases
- Phase 1: en‑US (baseline)
- Phase 2: es‑US, en‑GB (store listings, screenshots, and key UI strings)

## Scope
- Store text: titles, short/long descriptions, captions
- In‑app UI: menu labels (Upload / OCR / Quiz), hints, buttons, error messages, privacy/terms links

## Extraction Strategy
- Centralize display strings in a JSON or PO catalog (e.g., `localization/strings_en.json`)
- Template engine: If staying server‑rendered Flask, consider Flask‑Babel for pluralization and locale selection
- Avoid hard‑coded text in templates; replace with keys

## Keys (starter set)
- app.title: "BeeSmart Spelling Bee"
- menu.upload: "Upload"
- menu.ocr: "Scan (OCR)"
- menu.quiz: "Start Quiz"
- action.hint: "Hint"
- action.pronounce: "Hear phonetic spelling"
- status.streak: "Streak"
- msg.no_reveal: "Hints don’t reveal the answer"

## Workflow
1) Create `strings_en.json` using the keys above
2) Duplicate to `strings_es.json` and localize
3) Add locale switch (query param or cookie) and fallbacks
4) Localize screenshots and captions; generate separate asset sets per locale

## QA Checklist
- Right locale strings appear; fallback to English if missing
- Text fits in buttons at 120% font size
- VoiceOver/TalkBack read localized labels
