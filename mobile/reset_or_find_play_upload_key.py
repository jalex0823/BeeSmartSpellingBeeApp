# reset_or_find_play_upload_key.py
# Purpose:
# 1) Search for existing keystore files and print their SHA1 fingerprints.
# 2) If you don't have the expected SHA1, generate a NEW upload keystore + export PEM
#    (for Play Console -> App integrity -> Reset upload key).
#
# Usage (Windows CMD/PowerShell):
#   py reset_or_find_play_upload_key.py --project .
#   py reset_or_find_play_upload_key.py --project "c:\...\BeeSmartSpellingBeeApp\mobile" --expected "EF:B0:34:..."
#   py reset_or_find_play_upload_key.py --project . --make-new
#
# Notes:
# - Requires JDK installed and keytool available on PATH.
# - Will NOT upload anything to Google; it only generates files you upload in Play Console.
# - It will NOT delete or overwrite an existing upload-keystore.jks unless you pass --force.

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Default --project is the directory containing this script (mobile/)
_SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_SEARCH_DIRS = [
    str(_SCRIPT_DIR),
    str(Path.home()),
]

KEYSTORE_EXTS = {".jks", ".keystore", ".p12"}


def run(cmd, input_text=None):
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        shell=False,
    )


def find_keytool():
    # keytool is typically on PATH if JDK installed
    keytool = shutil.which("keytool")
    if keytool:
        return keytool

    # Try JAVA_HOME
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home) / "bin" / "keytool.exe"
        if candidate.exists():
            return str(candidate)

    return None


def is_keystore_file(p: Path) -> bool:
    if not p.is_file():
        return False
    ext = p.suffix.lower()
    if ext in KEYSTORE_EXTS:
        return True
    # some keystores have no extension (rare)
    name = p.name.lower()
    if "keystore" in name and p.stat().st_size > 0:
        return True
    return False


def list_keystore_sha1(keytool, keystore_path: Path, storepass: str = None):
    cmd = [keytool, "-list", "-v", "-keystore", str(keystore_path)]
    if storepass is not None:
        cmd += ["-storepass", storepass]

    cp = run(cmd)
    out = (cp.stdout or "") + "\n" + (cp.stderr or "")
    if cp.returncode != 0:
        # likely needs password or not a valid keystore
        return None, out.strip()

    sha1_lines = []
    for line in out.splitlines():
        line = line.strip()
        if line.upper().startswith("SHA1:"):
            sha1_lines.append(line.split("SHA1:", 1)[1].strip())
    return sha1_lines, out.strip()


def normalize_sha1(s: str) -> str:
    return s.strip().upper().replace(" ", "")


def walk_for_keystores(root: Path):
    results = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                if is_keystore_file(p):
                    results.append(p)
            except Exception:
                continue
    return results


def create_new_upload_keystore(keytool, out_dir: Path, force: bool):
    out_dir.mkdir(parents=True, exist_ok=True)
    ks_path = out_dir / "upload-keystore.jks"
    pem_path = out_dir / "upload_certificate.pem"

    if ks_path.exists() and not force:
        raise RuntimeError(
            f"{ks_path} already exists. Use --force to overwrite, or delete it manually."
        )

    # Prompt for password safely
    print("\nCreate NEW upload keystore (for Google Play 'Reset upload key').")
    print("Choose a STRONG password and SAVE IT somewhere safe.\n")

    import getpass

    pw1 = getpass.getpass("Enter keystore password: ")
    pw2 = getpass.getpass("Re-enter keystore password: ")
    if pw1 != pw2 or not pw1:
        raise RuntimeError("Passwords did not match or were empty.")

    # Minimal required identity fields for keytool
    dname = "CN=BeeSmart Spelling, OU=Altech, O=Altech Computer Services LLC, L=Missouri City, S=TX, C=US"

    if ks_path.exists():
        ks_path.unlink()

    # Generate keypair
    gen_cmd = [
        keytool,
        "-genkeypair",
        "-keystore",
        str(ks_path),
        "-alias",
        "upload",
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "10000",
        "-dname",
        dname,
        "-storepass",
        pw1,
        "-keypass",
        pw1,
    ]
    cp = run(gen_cmd)
    if cp.returncode != 0:
        raise RuntimeError("keytool -genkeypair failed:\n" + (cp.stderr or cp.stdout or ""))

    # Export PEM (public cert)
    if pem_path.exists():
        pem_path.unlink()

    exp_cmd = [
        keytool,
        "-export",
        "-rfc",
        "-keystore",
        str(ks_path),
        "-alias",
        "upload",
        "-file",
        str(pem_path),
        "-storepass",
        pw1,
    ]
    cp = run(exp_cmd)
    if cp.returncode != 0:
        raise RuntimeError("keytool -export failed:\n" + (cp.stderr or cp.stdout or ""))

    # Print SHA1 for confirmation
    sha1s, _ = list_keystore_sha1(keytool, ks_path, storepass=pw1)
    sha1 = sha1s[0] if sha1s else "(unknown)"

    # Write keystore.properties template
    props_path = out_dir / "keystore.properties"
    props_path.write_text(
        "storeFile=upload-keystore.jks\n"
        f"storePassword={pw1}\n"
        "keyAlias=upload\n"
        f"keyPassword={pw1}\n",
        encoding="utf-8",
    )

    return ks_path, pem_path, props_path, sha1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--project",
        default=str(_SCRIPT_DIR),
        help=f"Project root (default: script dir = {_SCRIPT_DIR})",
    )
    ap.add_argument("--expected", default="", help="Expected SHA1 from Play Console (optional)")
    ap.add_argument(
        "--search",
        action="store_true",
        help="Search for keystores and print SHA1s (default True)",
    )
    ap.add_argument("--no-search", dest="search", action="store_false")
    ap.set_defaults(search=True)
    ap.add_argument(
        "--make-new",
        action="store_true",
        help="Generate new upload-keystore.jks + upload_certificate.pem",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated upload-keystore.jks",
    )
    args = ap.parse_args()

    project_root = Path(args.project).resolve()
    if not project_root.exists():
        print(f"ERROR: project path does not exist: {project_root}")
        sys.exit(1)

    keytool = find_keytool()
    if not keytool:
        print("ERROR: keytool not found. Install a JDK (17 recommended) or set JAVA_HOME.")
        sys.exit(1)

    expected = normalize_sha1(args.expected) if args.expected else ""

    # 1) Search for existing keystores and list SHA1s (passwordless only)
    found_match = False
    if args.search:
        print(f"\nSearching for keystores under: {project_root}")
        keystores = walk_for_keystores(project_root)

        # Also search in common dirs if project search finds nothing
        if not keystores:
            for d in DEFAULT_SEARCH_DIRS:
                p = Path(d)
                if p.exists() and p != project_root:
                    print(f"Also searching: {p}")
                    keystores.extend(walk_for_keystores(p))

        if not keystores:
            print("No keystore-like files found.")
        else:
            print(f"Found {len(keystores)} candidate keystore files.")
            print("Attempting to read SHA1 fingerprints (will fail for password-protected files).")
            for ks in sorted(set(keystores)):
                sha1s, raw = list_keystore_sha1(keytool, ks, storepass=None)
                if sha1s is None:
                    continue
                for sha1 in sha1s:
                    ns = normalize_sha1(sha1)
                    marker = ""
                    if expected and ns == expected:
                        marker = "  <<< MATCHES EXPECTED (Play upload key)"
                        found_match = True
                    print(f"SHA1 {sha1}  |  {ks}{marker}")

            if expected and not found_match:
                print("\nNo passwordless keystore matched the expected SHA1.")
                print(
                    "That usually means your keystore is password protected (normal) OR you don't have it locally.\n"
                )

    # 2) Generate new upload key (for Play Console reset upload key)
    if args.make_new:
        out_dir = project_root / "android"
        try:
            ks_path, pem_path, props_path, sha1 = create_new_upload_keystore(
                keytool, out_dir, force=args.force
            )
        except Exception as e:
            print("\nERROR creating new upload keystore:\n", str(e))
            sys.exit(1)

        print("\nSUCCESS. Files created:")
        print(f"  Keystore:   {ks_path}")
        print(f"  PEM cert:   {pem_path}")
        print(f"  Properties: {props_path}")
        print(f"  New SHA1:   {sha1}")

        print("\nNEXT STEPS (Google Play Console):")
        print("  1) Play Console -> Setup -> App integrity")
        print("  2) Under 'Upload key certificate' choose 'Reset upload key'")
        print("  3) Upload this file when asked: android\\upload_certificate.pem")
        print("\nNEXT STEPS (Project signing):")
        print("  - android/keystore.properties was created; ensure app/build.gradle")
        print("    reads it and uses signingConfig release for release builds.")
        print("  - Rebuild: Build -> Generate Signed Bundle -> Android App Bundle (release)")
        print("  - Upload the new app-release.aab")

    if not args.make_new:
        print("\nTip: If you need to generate a NEW upload key for Play reset, run:")
        print(f'  py {Path(__file__).name} --project "{project_root}" --make-new')


if __name__ == "__main__":
    main()
