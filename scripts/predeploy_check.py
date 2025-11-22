import os
import sys
import subprocess

def run(cmd: list[str]) -> int:
    try:
        print(f"$ {' '.join(cmd)}")
        return subprocess.call(cmd)
    except Exception as e:
        print(f"❌ Failed running command {' '.join(cmd)}: {e}")
        return 1

def main() -> int:
    print("🚀 Railway pre-deploy diagnostics starting...")
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    print(f"ENV: PORT={os.getenv('PORT')} RAILWAY_ENVIRONMENT={os.getenv('RAILWAY_ENVIRONMENT')} DATABASE_URL set={bool(os.getenv('DATABASE_URL'))}")

    # Show installed packages (top few) to confirm build layer
    try:
        import pkg_resources  # type: ignore
        dists = sorted([(d.project_name, d.version) for d in pkg_resources.working_set])
        print("📦 Installed packages (sample):", ", ".join([f"{n}=={v}" for n, v in dists[:15]]), "...")
    except Exception as e:
        print(f"⚠️ Could not enumerate installed packages: {e}")

    # Try schema ensure (non-fatal)
    try:
        rc = run([sys.executable, "scripts/ensure_db_schema.py"]) 
        if rc != 0:
            print(f"⚠️ ensure_db_schema exited with code {rc} (continuing)")
    except Exception as e:
        print(f"⚠️ ensure_db_schema failed: {e}")

    print("✅ Pre-deploy diagnostics complete. Proceeding to deploy.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
