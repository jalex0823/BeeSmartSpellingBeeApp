from __future__ import annotations

import pathlib

HTML_PATH = pathlib.Path(__file__).with_name('debug_quiz_rendered.html')


def main() -> None:
    html = HTML_PATH.read_text(encoding='utf-8', errors='replace')

    marker = "Quiz script loading"
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit(f"Marker not found: {marker!r}")

    # Find the surrounding <script>...</script> (inline) that contains this marker.
    script_open = html.rfind('<script', 0, idx)
    if script_open < 0:
        raise SystemExit('Could not find <script before marker')
    content_start = html.find('>', script_open)
    if content_start < 0:
        raise SystemExit('Could not find end of <script ...> tag')
    content_start += 1

    script_close = html.find('</script>', content_start)
    if script_close < 0:
        raise SystemExit('Could not find </script> after marker')

    content = html[content_start:script_close]
    lines = content.splitlines()

    # Print around the line Node reported (117)
    target = 117
    start = max(1, target - 10)
    end = min(len(lines), target + 10)

    print(f"Extracted script lines: {len(lines)}")
    print(f"Showing script lines {start}-{end} (target {target})")
    print('-' * 60)
    for i in range(start, end + 1):
        print(f"{i:4d}: {lines[i-1]}")


if __name__ == '__main__':
    main()
