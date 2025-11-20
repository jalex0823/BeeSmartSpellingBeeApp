"""
Direct Railway PostgreSQL Migration - Add Buzz Dust Fields
Connects to Railway database and adds the 5 missing columns
"""
import psycopg2
from psycopg2 import sql
import sys

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def run_migration():
    """Add Buzz Dust columns to Railway PostgreSQL users table"""
    print("🔧 Connecting to Railway PostgreSQL...")
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway PostgreSQL database")
        print("\n" + "="*60)
        print("🐝 Adding Buzz Dust Columns to Users Table")
        print("="*60 + "\n")
        
        # Check which columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
              AND column_name IN ('total_buzz_dust', 'bee_class', 'last_rank_up_at', 'current_streak', 'longest_streak')
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        migrations = []
        
        # 1. Add total_buzz_dust column
        if 'total_buzz_dust' not in existing_columns:
            print("📝 Adding total_buzz_dust column...")
            cursor.execute("""
                ALTER TABLE users ADD COLUMN total_buzz_dust INTEGER DEFAULT 0
            """)
            cursor.execute("""
                CREATE INDEX ix_users_total_buzz_dust ON users(total_buzz_dust)
            """)
            migrations.append("✅ Added total_buzz_dust (INTEGER, default 0, indexed)")
        else:
            print("⏭️  total_buzz_dust already exists")
        
        # 2. Add bee_class column
        if 'bee_class' not in existing_columns:
            print("📝 Adding bee_class column...")
            cursor.execute("""
                ALTER TABLE users ADD COLUMN bee_class VARCHAR(20) DEFAULT 'Novice Bee'
            """)
            cursor.execute("""
                CREATE INDEX ix_users_bee_class ON users(bee_class)
            """)
            migrations.append("✅ Added bee_class (VARCHAR(20), default 'Novice Bee', indexed)")
        else:
            print("⏭️  bee_class already exists")
        
        # 3. Add last_rank_up_at column
        if 'last_rank_up_at' not in existing_columns:
            print("📝 Adding last_rank_up_at column...")
            cursor.execute("""
                ALTER TABLE users ADD COLUMN last_rank_up_at TIMESTAMP
            """)
            migrations.append("✅ Added last_rank_up_at (TIMESTAMP, nullable)")
        else:
            print("⏭️  last_rank_up_at already exists")
        
        # 4. Add current_streak column
        if 'current_streak' not in existing_columns:
            print("📝 Adding current_streak column...")
            cursor.execute("""
                ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0
            """)
            migrations.append("✅ Added current_streak (INTEGER, default 0)")
        else:
            print("⏭️  current_streak already exists")
        
        # 5. Add longest_streak column
        if 'longest_streak' not in existing_columns:
            print("📝 Adding longest_streak column...")
            cursor.execute("""
                ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0
            """)
            migrations.append("✅ Added longest_streak (INTEGER, default 0)")
        else:
            print("⏭️  longest_streak already exists")
        
        # Commit all changes
        conn.commit()
        
        # Verify final state
        print("\n" + "="*60)
        print("🔍 Verifying Column Structure")
        print("="*60 + "\n")
        
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                column_default,
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' 
              AND column_name IN ('total_buzz_dust', 'bee_class', 'last_rank_up_at', 'current_streak', 'longest_streak')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        if columns:
            print(f"{'Column Name':<20} {'Type':<15} {'Default':<20} {'Nullable':<10}")
            print("-" * 70)
            for col in columns:
                col_name, data_type, default, nullable = col
                default_str = str(default)[:18] if default else "NULL"
                print(f"{col_name:<20} {data_type:<15} {default_str:<20} {nullable:<10}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 Migration Complete!")
        print("="*60 + "\n")
        
        if migrations:
            print("Changes made:")
            for migration in migrations:
                print(f"  {migration}")
        else:
            print("  ℹ️  All columns already existed - no changes needed")
        
        print("\n✅ Railway database is now ready for Buzz Dust system!")
        print("🚀 The 500 error should be fixed - try refreshing beesmart.up.railway.app\n")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
