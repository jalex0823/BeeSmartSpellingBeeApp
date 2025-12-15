import sys
import os
import requests
import json
from flask import Flask
from models import db, WordBankStorage, User
from config import get_config

# Add current directory to path
sys.path.append(os.getcwd())

def smoke_test():
    print("="*60)
    print("🔥 SMOKE TEST: Word Bank Connections")
    print("="*60)

    # 1. Initialize Flask App and Database
    print("\n[1] Initializing Flask App and Database...")
    try:
        app = Flask(__name__)
        config = get_config()
        app.config.from_object(config)
        db.init_app(app)
        print("✅ Flask app initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Flask app: {e}")
        return

    # 2. Test Database Connection
    print("\n[2] Testing Database Connection...")
    try:
        with app.app_context():
            # Try a simple query
            user_count = User.query.count()
            print(f"✅ Database connected. User count: {user_count}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # 3. Test WordBankStorage (PostgreSQL)
    print("\n[3] Testing WordBankStorage (PostgreSQL)...")
    try:
        with app.app_context():
            # Create a dummy storage ID
            test_storage_id = "smoke_test_id"
            test_words = [
                {"word": "apple", "sentence": "I eat an apple.", "hint": "Fruit"},
                {"word": "banana", "sentence": "Monkeys love bananas.", "hint": "Yellow fruit"}
            ]
            
            # Save words
            print(f"   Saving {len(test_words)} words to storage_id='{test_storage_id}'...")
            WordBankStorage.save_wordbank(test_storage_id, test_words)
            print("   ✅ Save successful")
            
            # Load words
            print(f"   Loading words from storage_id='{test_storage_id}'...")
            loaded_words = WordBankStorage.load_wordbank(test_storage_id)
            print(f"   Loaded {len(loaded_words)} words")
            
            if len(loaded_words) == 2 and loaded_words[0]['word'] == 'apple':
                print("   ✅ Load successful and data matches")
            else:
                print(f"   ❌ Load failed or data mismatch: {loaded_words}")
                
            # Delete words
            print(f"   Deleting storage_id='{test_storage_id}'...")
            WordBankStorage.delete_wordbank(test_storage_id)
            
            # Verify deletion
            loaded_after_delete = WordBankStorage.load_wordbank(test_storage_id)
            if not loaded_after_delete or len(loaded_after_delete) == 0:
                print("   ✅ Deletion successful")
            else:
                print(f"   ❌ Deletion failed, still has {len(loaded_after_delete)} words")

    except Exception as e:
        print(f"❌ WordBankStorage test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("🔥 SMOKE TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    smoke_test()
