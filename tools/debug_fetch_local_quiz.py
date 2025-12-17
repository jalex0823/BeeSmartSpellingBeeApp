import re
import sys
from pathlib import Path

import requests


def main() -> int:
    base = 'http://127.0.0.1:5000'
    out = Path('debug_local_quiz.html')

    s = requests.Session()

    # Touch home to establish a session cookie
    s.get(base + '/', timeout=15)

    # Seed sample words into the session
    seed = s.post(
        base + '/api/upload-manual-words',
        json={'words': ['apple', 'bee', 'cat', 'honey', 'buzz']},
        timeout=30,
    )
    print('seed', seed.status_code)
    if seed.status_code >= 400:
        print(seed.text[:500])

    q = s.get(base + '/quiz?resume=1&t=0', timeout=30, allow_redirects=True)
    print('quiz', q.status_code, 'final_url', q.url, 'len', len(q.text))

    out.write_text(q.text, encoding='utf-8', errors='replace')
    print('wrote', out)

    count = len(re.findall(r"\\\\'", q.text))
    print("\\\\' occurrences:", count)

    # Also check for the classic unescaped apostrophe pattern around contractions in single-quoted strings
    # This is a heuristic only.
    suspect = len(re.findall(r"'[^\n']*\\\\\\\\'[^\n']*'", q.text))
    print("suspect single-quoted strings containing \\\\':", suspect)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
