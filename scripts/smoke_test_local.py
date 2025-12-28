"""Local smoke test for BeeSmart Spelling Bee App.

Why this exists:
- Some environments (including certain VS Code terminals) can have broken shell PATHs,
  making curl/grep/head unreliable.
- This script uses only Python stdlib to start the app and hit a few endpoints.

What it checks (basic contract):
- Starts `AjaSpellBApp.py` on a free port with FAST_BOOT=1.
- Polls `/health` until it returns HTTP 200.
- Fetches a small set of key pages and asserts HTTP 200.

Usage:
    python3 scripts/smoke_test_local.py

Optional env:
- SMOKE_TIMEOUT_S: total seconds to wait for server health (default 25)
- SMOKE_PORT: fixed port (otherwise chooses a free port)
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


APP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AjaSpellBApp.py"))


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _http_get(url: str, timeout_s: float = 5.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "beesmart-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        return int(e.code), body
    except urllib.error.URLError as e:
        # Common during startup before the server socket is accepting.
        # Treat as retryable by surfacing a sentinel status.
        return 0, str(e).encode("utf-8", errors="replace")


def _start_app(port: int) -> subprocess.Popen[bytes]:
    env = os.environ.copy()
    env.setdefault("FAST_BOOT", "1")
    env["PORT"] = str(port)

    # Use the same python interpreter that is running this script.
    cmd = [sys.executable, "-u", APP_FILE]

    # Capture output so it doesn't pollute test results; we only print it on failure.
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=os.path.dirname(APP_FILE),
    )


def _tail(proc: subprocess.Popen[bytes], max_bytes: int = 12_000) -> str:
    if proc.stdout is None:
        return ""
    try:
        data = proc.stdout.read(max_bytes)  # type: ignore[arg-type]
    except Exception:
        return ""
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return repr(data)


def main() -> int:
    timeout_s = float(os.environ.get("SMOKE_TIMEOUT_S", "25"))
    port = int(os.environ.get("SMOKE_PORT", "0")) or _free_port()

    base = f"http://127.0.0.1:{port}"
    proc = _start_app(port)

    results: list[CheckResult] = []

    try:
        # Poll /health
        deadline = time.time() + timeout_s
        last_status: int | None = None
        last_body: bytes = b""
        while time.time() < deadline:
            # If the process died, stop early.
            rc = proc.poll()
            if rc is not None:
                out = _tail(proc)
                results.append(
                    CheckResult(
                        name="server_start",
                        ok=False,
                        detail=f"Server exited early (code={rc}). Output tail:\n{out}",
                    )
                )
                break

            status, body = _http_get(f"{base}/health", timeout_s=2.5)
            last_status, last_body = status, body
            if status == 200:
                # Try to parse JSON but don't fail the smoke if format changes.
                try:
                    parsed = json.loads(body.decode("utf-8", errors="replace"))
                    detail = f"HTTP 200, JSON keys: {sorted(parsed.keys())}" if isinstance(parsed, dict) else "HTTP 200"
                except Exception:
                    detail = "HTTP 200"
                results.append(CheckResult(name="/health", ok=True, detail=detail))
                break
            # status==0 is a retryable connection error during startup.

            time.sleep(0.35)

        if not any(r.name == "/health" and r.ok for r in results):
            body_preview = last_body[:300].decode("utf-8", errors="replace")
            results.append(
                CheckResult(
                    name="/health",
                    ok=False,
                    detail=f"Did not reach HTTP 200 within {timeout_s}s. Last status={last_status}. Body preview: {body_preview!r}",
                )
            )

        # Key pages (only if server is up)
        if any(r.name == "/health" and r.ok for r in results):
            for path in ["/", "/support", "/privacy", "/terms"]:
                status, body = _http_get(f"{base}{path}", timeout_s=5.0)
                ok = status == 200
                snippet = body[:120].decode("utf-8", errors="replace").replace("\n", " ")
                results.append(
                    CheckResult(name=path, ok=ok, detail=f"HTTP {status}; body starts: {snippet!r}")
                )

    finally:
        # Always stop the server.
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # Report
    print("\nBeeSmart local smoke test")
    print(f"Base URL: {base}")

    exit_code = 0
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"- {status}: {r.name} — {r.detail}")
        if not r.ok:
            exit_code = 2

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
