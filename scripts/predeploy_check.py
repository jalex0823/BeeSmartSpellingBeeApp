import os
import sys
import subprocess

def run(cmd: list) -> int:
    try:
        print(f"$ {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ Failed running command {' '.join(cmd)}: {e}")
        return 1

def main() -> int:
    """Run pre-deploy checks but NEVER fail deployment.

    Any error encountered here must be logged and ignored so that the actual
    app can still deploy. Railway treats a non-zero exit from the pre-deploy
    command as a deployment failure, so we always return 0.
    """
    try:
        print("🚀 Railway pre-deploy diagnostics starting...")
        print(f"Python: {sys.version}")
        print(f"Working dir: {os.getcwd()}")
        print(f"ENV: PORT={os.getenv('PORT')} RAILWAY_ENVIRONMENT={os.getenv('RAILWAY_ENVIRONMENT')} DATABASE_URL set={bool(os.getenv('DATABASE_URL'))}")

        # Show installed packages (top few) to confirm build layer
        try:
            import pkg_resources
            dists = sorted([(d.project_name, d.version) for d in pkg_resources.working_set])
            print("📦 Installed packages (sample):", ", ".join([f"{n}=={v}" for n, v in dists[:15]]), "...")
        except Exception as e:
            print(f"⚠️ Could not enumerate installed packages: {e}")

        # Try schema ensure (non-fatal)
        schema_script = os.path.join("scripts", "ensure_db_schema.py")
        if os.path.exists(schema_script):
            try:
                print(f"🔧 Running schema migration: {schema_script}")
                rc = run([sys.executable, schema_script]) 
                if rc != 0:
                    print(f"⚠️ ensure_db_schema exited with code {rc} (continuing anyway)")
            except Exception as e:
                print(f"⚠️ ensure_db_schema failed: {e} (continuing anyway)")
        else:
            print(f"⚠️ Schema script not found at {schema_script} (skipping)")

        # Run wordbank persistence migration (non-fatal)
        wordbank_migration = "add_wordbank_columns.py"
        if os.path.exists(wordbank_migration):
            try:
                print(f"🔧 Running wordbank persistence migration: {wordbank_migration}")
                rc = run([sys.executable, wordbank_migration])
                if rc != 0:
                    print(f"⚠️ wordbank migration exited with code {rc} (continuing anyway)")
            except Exception as e:
                print(f"⚠️ wordbank migration failed: {e} (continuing anyway)")
        else:
            print(f"⚠️ Wordbank migration not found at {wordbank_migration} (skipping)")

        # School Edition: schools + school_keys tables and users.school_id (non-fatal)
        school_migration = os.path.join("scripts", "migrate_school_tables.py")
        if os.path.exists(school_migration):
            try:
                print(f"🔧 Running school tables migration: {school_migration}")
                rc = run([sys.executable, school_migration])
                if rc != 0:
                    print(f"⚠️ school migration exited with code {rc} (continuing anyway)")
            except Exception as e:
                print(f"⚠️ school migration failed: {e} (continuing anyway)")

        print("✅ Pre-deploy diagnostics complete. Proceeding to deploy.")
        return 0
    except Exception as e:
        # Absolute last-resort guard: never fail deployment due to pre-deploy script
        print(f"⚠️ Pre-deploy script encountered a fatal error but will not block deployment: {e}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
