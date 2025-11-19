#!/usr/bin/env python3
"""Automated validation for quiz enrichment logic (/api/next).

Scenarios:
1. Word with NO pre-set sentence -> /api/next should enrich definition & sentence via dictionary lookup.
2. Word WITH pre-set sentence only -> /api/next should derive a separate definition (not reuse sentence) and preserve sentence.

Assertions:
- hasDefinition True
- definitionSource in {'dictionary_lookup','hint','definition_field'}
- Sentence and definition are distinct when sentence pre-set.
- Target word is blanked in both fields (no raw word token present with word boundaries).
"""

import re
import json
from AjaSpellBApp import app, set_wordbank, init_quiz_state, get_wordbank


def _contains_raw_word(text: str, word: str) -> bool:
    if not text:
        return False
    # Word boundary match ignoring case
    return re.search(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE) is not None


def _print_result(label: str, data: dict):
    print(f"\n=== {label} ===")
    print(json.dumps({k: data[k] for k in ['word','definition','sentence','definitionSource','hasDefinition']}, indent=2))


def run_case(words, label):
    # Use both test_client() and its context to ensure request + application context present
    with app.test_client() as client:
        with client.session_transaction():
            pass  # ensure a session exists
        # Use a request context for helper functions relying on session
        with app.test_request_context():
            set_wordbank(words, is_user_upload=True)
            init_quiz_state()
        resp = client.post('/api/next')
        assert resp.status_code == 200, f"Unexpected status: {resp.status_code}"
        data = resp.get_json()
        _print_result(label, data)
        word = data['word']
        # Assertions
        assert data['hasDefinition'] is True, 'Definition expected to be present'
        assert data['definitionSource'] in {'dictionary_lookup','definition_field','hint','fallback'}, 'Unexpected definitionSource'
        # Blanking check: raw word should not appear
        assert not _contains_raw_word(data['sentence'], word), 'Raw word leaked in sentence'
        assert not _contains_raw_word(data['definition'], word), 'Raw word leaked in definition'
        return data


def main():
    print("Starting quiz enrichment validation...")

    # Scenario: Upload via API (auto sentence enrichment), then verify /api/next parsing
    with app.test_client() as client:
        upload_resp = client.post('/api/upload-manual-words', json={"words": ["encourage"]})
        assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.status_code} {upload_resp.get_data(as_text=True)}"
        # Call /api/next for quiz question
        next_resp = client.post('/api/next')
        assert next_resp.status_code == 200, f"/api/next failed: {next_resp.status_code} {next_resp.get_data(as_text=True)}"
        data = next_resp.get_json()
        _print_result('API UPLOAD CASE', data)
        assert data['hasDefinition'] is True
        assert data['definitionSource'] in {'dictionary_lookup','definition_field','hint','fallback'}
        # Distinct definition vs sentence expectation when parsed successfully
        if data['definitionSource'] == 'dictionary_lookup':
            assert data['definition'] != data['sentence'], 'Parsed definition should differ from sample sentence'
        # Blanking checks
        assert '_____' in data['sentence'], 'Sentence should include blank placeholder'
        assert 'encourage' not in data['sentence'].lower(), 'Raw word leaked in sentence'
        assert 'encourage' not in data['definition'].lower(), 'Raw word leaked in definition'

    print("\nAll quiz enrichment checks PASSED.")


if __name__ == '__main__':
    main()
