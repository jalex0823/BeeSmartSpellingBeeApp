"""
Direct Railway PostgreSQL Migration - Create WordBankStorage Table
Connects directly to Railway PostgreSQL using connection string.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def create_wordbank_storage_table():
    """Create wordbank_storage table in Railway PostgreSQL"""
    
    print("🔧 Connecting to Railway PostgreSQL...")
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("✅ Connected to Railway PostgreSQL")
        
        # Check if table already exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wordbank_storage'
            );
        """)
        
        exists = cur.fetchone()[0]
        
        if exists:
            print("✅ Table 'wordbank_storage' already exists!")
            
            # Show count
            cur.execute("SELECT COUNT(*) FROM wordbank_storage;")
            count = cur.fetchone()[0]
            print(f"📊 Current entries: {count}")
            
            cur.close()
            conn.close()
            return True
        
        print("🔨 Creating wordbank_storage table...")
        
        # Create the table
        cur.execute("""
            CREATE TABLE wordbank_storage (
                id SERIAL PRIMARY KEY,
                storage_id VARCHAR(36) UNIQUE NOT NULL,
                words_data JSONB NOT NULL,
                word_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
            );
        """)
        
        print("✅ Table created!")
        
        # Create indexes
        print("🔨 Creating indexes...")
        
        cur.execute("CREATE INDEX idx_wordbank_storage_storage_id ON wordbank_storage(storage_id);")
        cur.execute("CREATE INDEX idx_wordbank_storage_user_id ON wordbank_storage(user_id);")
        cur.execute("CREATE INDEX idx_wordbank_storage_created_at ON wordbank_storage(created_at);")
        cur.execute("CREATE INDEX idx_wordbank_storage_last_accessed ON wordbank_storage(last_accessed);")
        
        print("✅ Indexes created!")
        
        # Verify
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'wordbank_storage'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print("\n📋 Table schema:")
        for col_name, col_type in columns:
            print(f"   - {col_name}: {col_type}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🚂 Railway PostgreSQL Migration: WordBankStorage Table")
    print("=" * 70)
    
    success = create_wordbank_storage_table()
    
    print("=" * 70)
    if success:
        print("✅ SUCCESS! The wordbank_storage table is ready.")
        print("\n📝 Next steps:")
        print("   1. Upload words in your Railway app")
        print("   2. Check logs for: '✅ Saved X words to database'")
        print("   3. Restart Railway - words should persist!")
    else:
        print("❌ FAILED - Check errors above")
    print("=" * 70)
