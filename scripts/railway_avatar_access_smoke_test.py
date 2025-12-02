"""Railway Avatar Access Smoke Test

Purpose:
    Lightweight HTTP-based verification that deployed Railway instance enforces
    strict guest restriction and proper role-based unlocking of avatars.

Usage:
    python3 scripts/railway_avatar_access_smoke_test.py \
        --base https://beesmart-production.up.railway.app \
        --student stud1 --student-pass Password123! \
        --admin admin --admin-pass ChangeMeNow!42

Environment Variables (alternative):
    RAILWAY_BASE_URL, RAILWAY_STUDENT_USER, RAILWAY_STUDENT_PASS,
    RAILWAY_ADMIN_USER, RAILWAY_ADMIN_PASS

Exit Codes:
    0 -> all checks passed
    1 -> failure detected

Checks Performed:
    1. Guest request returns exactly 1 mascot avatar and guest_limited flag true.
    2. Student login then /api/avatars returns > 1 avatar with mixture of locked/unlocked.
    3. Admin login then /api/avatars returns all avatars unlocked (locked count == 0).

Notes:
    - Assumes cookies (session) based auth. We persist a 'requests.Session' per role.
    - Does not mutate state (read-only). Add delegated unlock test separately if needed.
"""
from __future__ import annotations
import os, sys, argparse, json
import requests

MASCOT_IDS = {"mascot-bee", "honey-comb", "honeycomb"}

def fetch_avatars(session: requests.Session, base: str) -> dict:
    r = session.get(f"{base}/api/avatars?force=1", timeout=20)
    r.raise_for_status()
    return r.json()

def login(session: requests.Session, base: str, username: str, password: str) -> bool:
    r = session.post(f"{base}/auth/login", data={"username": username, "password": password}, timeout=20, allow_redirects=True)
    # Some deployments redirect -> status 200 expected afterwards
    return r.status_code in (200, 302)

def check_guest(base: str) -> list[str]:
    s = requests.Session()
    data = fetch_avatars(s, base)
    problems = []
    avatars = data.get("avatars", [])
    if not data.get("guest_limited"):
        problems.append("guest_limited flag missing/false")
    if len(avatars) != 1:
        problems.append(f"guest should see exactly 1 avatar, saw {len(avatars)}")
    else:
        if avatars[0].get("id") not in MASCOT_IDS:
            problems.append(f"guest single avatar id unexpected: {avatars[0].get('id')}")
    return problems

def check_student(base: str, user: str, passwd: str) -> list[str]:
    s = requests.Session()
    problems = []
    if not login(s, base, user, passwd):
        return [f"student login failed for {user}"]
    data = fetch_avatars(s, base)
    avatars = data.get("avatars", [])
    if len(avatars) <= 1:
        problems.append("student should see full catalog (>1 avatar)")
    locked = [a for a in avatars if a.get("is_locked")]
    unlocked = [a for a in avatars if not a.get("is_locked")]
    if not locked:
        problems.append("student expected some locked avatars, none found")
    if not unlocked:
        problems.append("student expected some unlocked avatars, none found")
    # Ensure no guest-only reasons
    bad_reasons = {"guest_restriction", "guest_mascot"}
    for a in avatars:
        if a.get("locked_reason") in bad_reasons:
            problems.append(f"student received guest-only locked_reason on avatar {a.get('id')}")
            break
    return problems

def check_admin(base: str, user: str, passwd: str) -> list[str]:
    s = requests.Session()
    problems = []
    if not login(s, base, user, passwd):
        return [f"admin login failed for {user}"]
    data = fetch_avatars(s, base)
    avatars = data.get("avatars", [])
    locked = [a for a in avatars if a.get("is_locked")]
    if locked:
        sample = [(a.get("id"), a.get("locked_reason")) for a in locked[:5]]
        problems.append(f"admin saw locked avatars: sample={sample}")
    # Sanity: ensure reasons reflect admin unlock
    admin_reason_ok = {"admin_unlocked", "unlocked", "free"}
    mismatch = [a.get("id") for a in avatars if a.get("locked_reason") not in admin_reason_ok]
    if mismatch:
        problems.append(f"admin unexpected locked_reason values for avatars: {mismatch[:5]}")
    return problems

def main():
    parser = argparse.ArgumentParser(description="Railway avatar access smoke test")
    parser.add_argument("--base", default=os.environ.get("RAILWAY_BASE_URL"), help="Base URL of deployed app (e.g. https://your-app.up.railway.app)")
    parser.add_argument("--student", default=os.environ.get("RAILWAY_STUDENT_USER"))
    parser.add_argument("--student-pass", default=os.environ.get("RAILWAY_STUDENT_PASS"))
    parser.add_argument("--admin", default=os.environ.get("RAILWAY_ADMIN_USER"))
    parser.add_argument("--admin-pass", default=os.environ.get("RAILWAY_ADMIN_PASS"))
    args = parser.parse_args()

    if not args.base:
        print("ERROR: --base (or RAILWAY_BASE_URL) required")
        return 1
    problems = []
    problems += [f"guest: {p}" for p in check_guest(args.base)]
    if args.student and args.student_pass:
        problems += [f"student: {p}" for p in check_student(args.base, args.student, args.student_pass)]
    else:
        problems.append("student credentials not provided; skipping student checks")
    if args.admin and args.admin_pass:
        problems += [f"admin: {p}" for p in check_admin(args.base, args.admin, args.admin_pass)]
    else:
        problems.append("admin credentials not provided; skipping admin checks")

    if problems:
        print("\nFAILURES DETECTED:")
        for p in problems:
            print(f" - {p}")
        return 1
    print("All avatar access smoke tests passed ✅")
    return 0

if __name__ == "__main__":
    sys.exit(main())
