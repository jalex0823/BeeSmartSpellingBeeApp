#!/usr/bin/env python3
import time
import requests
import os

BASE = os.environ.get("BASE_URL", "http://localhost:5000").rstrip("/")
ENDPOINTS = ["/auth/login", "/auth/register"]


def wait_for_server(timeout=15):
    start = time.time()
    last_err = None
    while time.time() - start < timeout:
        try:
            r = requests.get(BASE + "/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception as e:
            last_err = e
        time.sleep(0.5)
    if last_err:
        print(f"Server not ready: {last_err}")
    return False


def main():
    ok = wait_for_server()
    if not ok:
        print("❌ Server did not become ready in time")
        return 1

    sess = requests.Session()
    all_good = True
    for ep in ENDPOINTS:
        url = BASE + ep
        try:
            resp = sess.get(url, timeout=5)
            print(f"GET {ep} -> {resp.status_code}")
            if resp.status_code != 200:
                print(f"❌ Unexpected status for {ep}: {resp.status_code}")
                all_good = False
        except Exception as e:
            print(f"❌ Request failed for {ep}: {e}")
            all_good = False
    if all_good:
        print("✅ Auth pages responded with 200 OK")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
