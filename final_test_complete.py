import os
import sys
import time
import socket
import subprocess
from urllib.parse import urlparse, urlunparse

import requests


def _is_tcp_port_free(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
        return True
    except OSError:
        return False


def _pick_free_tcp_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


def _with_port(base_url: str, port: int) -> str:
    parsed = urlparse(base_url)
    netloc_host = parsed.hostname or "127.0.0.1"
    # Preserve any username/password if ever present (unlikely here)
    if parsed.username or parsed.password:
        userinfo = ""
        if parsed.username:
            userinfo += parsed.username
        if parsed.password:
            userinfo += f":{parsed.password}"
        netloc = f"{userinfo}@{netloc_host}:{port}"
    else:
        netloc = f"{netloc_host}:{port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def _wait_for_health(base_url: str, timeout_s: float = 20.0) -> bool:
    url = f"{base_url.rstrip('/')}/health"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False

repo_root = os.path.dirname(os.path.abspath(__file__))

# Create a session to maintain cookies
session = requests.Session()

print("🔄 Testing PlainWordList50.txt complete workflow with sessions...")

base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5051').rstrip('/')

# If we're pointing at localhost and nothing is listening, auto-start the app.
server_proc = None
parsed = urlparse(base_url)
host = (parsed.hostname or "127.0.0.1").lower()
is_localhost = host in ("127.0.0.1", "localhost")

port = parsed.port
if port is None:
    port = 443 if parsed.scheme == "https" else 80

if is_localhost and not _wait_for_health(base_url, timeout_s=1.0):
    # Ensure we pick a port we can actually bind to.
    bind_host = "127.0.0.1"
    chosen_port = port if _is_tcp_port_free(bind_host, port) else _pick_free_tcp_port(bind_host)
    if chosen_port != port:
        base_url = _with_port(base_url, chosen_port).rstrip('/')
        port = chosen_port

    print(f"ℹ️ No server detected at {base_url} — starting local BeeSmart server on port {port}...")
    env = os.environ.copy()
    env.setdefault("PORT", str(port))
    env.setdefault("FAST_BOOT", "1")
    env.setdefault("BYPASS_AVATAR_DB_SYNC", "1")
    env.setdefault("ENABLE_STARTUP_AVATAR_THUMBNAIL_VALIDATION", "0")
    env.setdefault("FORCE_DEBUG", "0")
    stdout_path = os.path.join(repo_root, "_final_test_server_stdout.log")
    stderr_path = os.path.join(repo_root, "_final_test_server_stderr.log")
    server_proc = subprocess.Popen(
        [sys.executable, os.path.join(repo_root, "AjaSpellBApp.py")],
        cwd=repo_root,
        env=env,
        stdout=open(stdout_path, "w", encoding="utf-8"),
        stderr=open(stderr_path, "w", encoding="utf-8"),
    )

    if not _wait_for_health(base_url, timeout_s=25.0):
        print("❌ Server failed to start (health check never became ready).")
        print(f"   See logs: {stdout_path} and {stderr_path}")
        try:
            server_proc.terminate()
        except Exception:
            pass
        raise SystemExit(1)

print("1️⃣ Uploading PlainWordList50.txt...")
try:
    with open('PlainWordList50.txt', 'rb') as f:
        files = {'file': ('PlainWordList50.txt', f, 'text/plain')}
        response = session.post(f'{base_url}/api/upload', files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload success: {result}")
    else:
        print(f"❌ Upload failed: {response.text}")
        exit(1)

except Exception as e:
    print(f"❌ Upload error: {e}")
    exit(1)

print("\n2️⃣ Checking wordbank...")
try:
    response = session.get(f'{base_url}/api/wordbank')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Wordbank contains {len(data['words'])} words")
        
        # Display first few words with their full data
        for i, word in enumerate(data['words'][:3]):
            print(f"   {i+1}. Word: '{word['word']}'")
            print(f"      Sentence: '{word.get('sentence', 'MISSING')}'")
            print(f"      Hint: '{word.get('hint', 'MISSING')}'")
            print()
    else:
        print(f"❌ Failed to get wordbank: {response.text}")
        exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("3️⃣ Testing current word (should work after upload)...")
try:
    response = session.post(f'{base_url}/api/next', json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    if response.status_code == 200:
        data = response.json()
        if data.get('done') is True:
            print("✅ Quiz is already complete (server returned done=true)")
            summary = data.get('summary') or {}
            print(f"   Summary: {summary.get('correct', 0)}/{summary.get('total', 0)} correct")
        else:
            print(f"✅ Current challenge: {data.get('sentence', 'MISSING')}")
            print(f"   Hint: {data.get('hint', 'MISSING')}")
            word_len = (
                data.get('word_length')
                or data.get('wordLength')
                or (len(data.get('word', '')) if data.get('word') else None)
            )
            print(f"   Word length: {word_len if word_len is not None else 'MISSING'}")
    else:
        print("❌ Failed to fetch next quiz word via /api/next")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 The issue was session management!")
print("   When you upload via browser, make sure to use the same session/tab")
print("   The Flask app uses sessions to store your word list")
print(f"\n🔗 Test in browser: {base_url.rstrip('/')}/simple-quiz")

if server_proc is not None:
    try:
        server_proc.terminate()
        server_proc.wait(timeout=5)
    except Exception:
        try:
            server_proc.kill()
        except Exception:
            pass