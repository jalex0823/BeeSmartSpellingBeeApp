"""DB smoke test for BeeSmart Spelling Bee App.

Goal: Provide a quick PASS/FAIL signal that the configured database is reachable
and basic ORM operations work.

This runs *in-process* (no HTTP server) to avoid port conflicts and flaky shell
tools. It should be safe against production DBs because it only creates a
single uniquely-named user and then deletes it (or rolls back on error).

Exit code:
  0 = PASS
  2 = FAIL

Usage:
  python3 scripts/smoke_test_db.py

Optional:
  SMOKE_DB_KEEP=1   # don't delete the created user (for debugging)
"""

from __future__ import annotations

import os
import sys
import time
import uuid
import socket


# Ensure repo root is importable when running from scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _print(msg: str) -> None:
    print(msg, flush=True)


def _tcp_check(host: str, port: int, timeout_s: float = 5.0) -> tuple[bool, str]:
    """Return (ok, message) for a TCP connect check."""
    try:
        ip = socket.gethostbyname(host)
    except Exception as e:
        return False, f"DNS failed for {host}: {e}"

    s = socket.socket()
    s.settimeout(timeout_s)
    try:
        s.connect((host, port))
    except Exception as e:
        return False, f"TCP connect failed to {host}:{port} ({ip}): {e}"
    finally:
        try:
            s.close()
        except Exception:
            pass
    return True, f"TCP connect ok to {host}:{port} ({ip})"


def main() -> int:
    os.environ.setdefault("FAST_BOOT", "1")

    t0 = time.time()
    try:
        import AjaSpellBApp as app_module  # noqa: E402
    except Exception as e:
        _print(f"FAIL: import AjaSpellBApp failed: {e}")
        return 2

    app = getattr(app_module, "app", None)
    if app is None:
        _print("FAIL: Flask app not found as AjaSpellBApp.app")
        return 2

    try:
        from models import db, User  # noqa: E402
    except Exception as e:
        _print(f"FAIL: import models/db failed: {e}")
        return 2

    keep = os.environ.get("SMOKE_DB_KEEP") == "1"

    _print("\n🐝 DB smoke test starting...")

    with app.app_context():
        # 1) Engine / connection sanity
        try:
            uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            safe_uri = uri
            if isinstance(uri, str) and "://" in uri:
                # best-effort: avoid printing creds
                scheme, rest = uri.split("://", 1)
                if "@" in rest:
                    safe_uri = scheme + "://" + "***:***@" + rest.split("@", 1)[1]
            _print(f"DB URI: {safe_uri}")

            # 1a) Explicit DigitalOcean DB network reachability check (DNS + TCP)
            # This makes it crystal-clear when failures are due to firewall/VPN/network.
            try:
                host = db.engine.url.host
                port = int(db.engine.url.port or 5432)
                ok, msg = _tcp_check(host, port, timeout_s=5.0)
                if ok:
                    _print(f"PASS: network reachability: {msg}")
                else:
                    _print(f"FAIL: network reachability: {msg}")
                    return 2
            except Exception as e:
                _print(f"WARN: could not run TCP reachability check: {e}")

            conn = db.engine.connect()
            try:
                conn.exec_driver_sql("SELECT 1")
            finally:
                conn.close()
            _print("PASS: DB connection (SELECT 1)")
        except Exception as e:
            _print(f"FAIL: DB connection failed: {e}")
            return 2

        # 2) Schema sanity (users table exists)
        try:
            # Cheap query that will fail if table missing
            count = User.query.count()
            _print(f"PASS: users table query (count={count})")
        except Exception as e:
            _print(f"FAIL: users table query failed: {e}")
            return 2

        # 3) Create + read + delete a temp row
        created_user_id = None
        username = f"smoke_{uuid.uuid4().hex[:12]}"
        email = f"{username}@example.invalid"

        try:
            u = User(
                username=username,
                display_name="DB Smoke Test",
                email=email,
                role="student",
                password_hash="smoke-test",  # not used
            )

            # Prefer model helper if available
            if hasattr(u, "set_password"):
                try:
                    u.set_password("SmokeTest!123")
                except Exception:
                    # fallback is fine
                    pass

            db.session.add(u)
            db.session.commit()
            created_user_id = u.id
            _print(f"PASS: created user id={created_user_id} username={username}")

            got = User.query.filter_by(username=username).first()
            if not got:
                _print("FAIL: could not re-read created user")
                return 2
            _print("PASS: re-read created user")

        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            _print(f"FAIL: create/read transaction failed: {e}")
            return 2
        finally:
            if created_user_id is not None and not keep:
                try:
                    # delete via loaded instance if available
                    victim = User.query.get(created_user_id)  # type: ignore[attr-defined]
                    if victim is not None:
                        db.session.delete(victim)
                        db.session.commit()
                        _print("PASS: deleted temp user")
                except Exception as e:
                    try:
                        db.session.rollback()
                    except Exception:
                        pass
                    _print(f"WARN: could not delete temp user: {e}")

    dt = time.time() - t0
    _print(f"\n✅ DB smoke test PASS ({dt:.2f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
