"""
Apply Railway migration to add wordbank persistence columns to the users table.

Usage:
  - Ensure DATABASE_URL is set (e.g., Railway Postgres URL)
  - Run: python scripts/apply_railway_migration.py

This script is idempotent; running it multiple times is safe.
"""
import os
import sys
import psycopg2

SQL_PATH = os.path.join(os.path.dirname(__file__), 'sql', 'railway_add_wordbank_columns.sql')


def main():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL environment variable is not set. Set it to your Railway Postgres URL.')
        sys.exit(1)

    if not os.path.exists(SQL_PATH):
        print(f'❌ Migration SQL not found at {SQL_PATH}')
        sys.exit(1)

    sql_text = open(SQL_PATH, 'r', encoding='utf-8').read()

    try:
        print('🔌 Connecting to database...')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        print('🚀 Applying migration...')
        cur.execute(sql_text)
        conn.commit()
        print('✅ Migration applied successfully.')
        cur.close()
        conn.close()
    except Exception as e:
        print(f'❌ Error applying migration: {e}')
        sys.exit(2)


if __name__ == '__main__':
    main()
