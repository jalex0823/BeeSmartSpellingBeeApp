import json
import os
import subprocess
from pathlib import Path

# ----------------------------
# CONFIG (edit if needed)
# ----------------------------
MOBILE_ROOT = Path(r"F:\mobile")  # <-- your mobile folder root

CAP_MODULES = [
    "android",          # already patched, but safe to include (will skip if already fixed)
    "app",
    "browser",
    "camera",
    "filesystem",
    "haptics",
    "keyboard",
    "splash-screen",
    "status-bar",
]

# The exact string we want to replace (covers both single and double quotes)
NEEDLE_1 = "getDefaultProguardFile('proguard-android.txt')"
NEEDLE_2 = 'getDefaultProguardFile("proguard-android.txt")'

REPLACE_1 = "getDefaultProguardFile('proguard-android-optimize.txt')"
REPLACE_2 = 'getDefaultProguardFile("proguard-android-optimize.txt")'

# Files we patch per module (Capacitor plugins)
# For @capacitor/android, the failing file you showed is ...\capacitor\build.gradle
def candidate_gradle_files(module: str) -> list[Path]:
    base = MOBILE_ROOT / "node_modules" / "@capacitor" / module
    if module == "android":
        return [base / "capacitor" / "build.gradle"]
    else:
        return [base / "android" / "build.gradle"]


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"\n>> Running: {' '.join(cmd)}   (cwd={cwd})")
    # Use shell=True on Windows so npx.cmd is found
    proc = subprocess.run(
        " ".join(cmd) if os.name == "nt" else cmd,
        cwd=str(cwd),
        shell=(os.name == "nt"),
        capture_output=True,
        text=True,
    )
    if proc.stdout.strip():
        print(proc.stdout)
    if proc.returncode != 0:
        if proc.stderr.strip():
            print(proc.stderr)
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"!! Missing: {path}")
        return False

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Replace both quote styles
    text = text.replace(NEEDLE_1, REPLACE_1)
    text = text.replace(NEEDLE_2, REPLACE_2)

    if text == original:
        print(f"-- No change needed: {path}")
        return False

    path.write_text(text, encoding="utf-8")
    print(f"** Patched: {path}")
    return True


def ensure_postinstall_patch_package(package_json_path: Path) -> None:
    if not package_json_path.exists():
        raise FileNotFoundError(f"package.json not found at: {package_json_path}")

    data = json.loads(package_json_path.read_text(encoding="utf-8"))
    scripts = data.get("scripts", {})
    if scripts is None:
        scripts = {}

    if scripts.get("postinstall") == "patch-package":
        print("-- package.json already has postinstall=patch-package")
        return

    # If a postinstall exists, we'll chain it safely
    if "postinstall" in scripts and scripts["postinstall"]:
        scripts["postinstall"] = f"{scripts['postinstall']} && patch-package"
        print("** Updated package.json postinstall to chain existing script + patch-package")
    else:
        scripts["postinstall"] = "patch-package"
        print("** Added package.json postinstall=patch-package")

    data["scripts"] = scripts
    package_json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    print("=== BeeSmart Capacitor Gradle Proguard Fix + patch-package Automation ===")
    print(f"Mobile root: {MOBILE_ROOT}")

    if not MOBILE_ROOT.exists():
        raise FileNotFoundError(f"MOBILE_ROOT does not exist: {MOBILE_ROOT}")

    # 1) Patch all module gradle files
    changed_any = False
    for module in CAP_MODULES:
        files = candidate_gradle_files(module)
        for f in files:
            try:
                changed = patch_file(f)
                changed_any = changed_any or changed
            except Exception as e:
                print(f"!! Error patching {f}: {e}")
                raise

    # 2) Ensure package.json has postinstall patch-package
    pkg = MOBILE_ROOT / "package.json"
    ensure_postinstall_patch_package(pkg)

    # 3) Create patch files for modules (even if no change, patch-package will create none or error)
    # We only run patch-package for modules that exist in node_modules.
    for module in CAP_MODULES:
        pkg_dir = MOBILE_ROOT / "node_modules" / "@capacitor" / module
        if not pkg_dir.exists():
            print(f"!! Skipping patch-package for @capacitor/{module} (not installed)")
            continue

        # patch-package expects package name, not path
        package_name = f"@capacitor/{module}"
        # Run npx patch-package @capacitor/module
        run_cmd(["npx", "patch-package", package_name], cwd=MOBILE_ROOT)

    print("\n=== DONE ===")
    print("Next steps:")
    print("1) In Android Studio: File -> Sync Project with Gradle Files")
    print("2) Build -> Clean Project")
    print("3) Build -> Generate Signed Bundle / APK -> Android App Bundle (release)")
    if changed_any:
        print("\n[OK] Proguard references were updated and patches created under F:\\mobile\\patches\\")
    else:
        print("\n[INFO] No file content changes detected, but patch-package was still run for installed modules.")


if __name__ == "__main__":
    main()
