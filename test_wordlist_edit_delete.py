#!/usr/bin/env python3
"""
Test script to validate word list edit and delete functionality.
This script tests the /api/saved-lists endpoints for editing and deleting word lists.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_word_list_operations():
    """Test creating, editing, and deleting a word list."""
    
    print("🐝 Testing Word List Edit & Delete Functionality\n")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Create a test word list
    print("\n1️⃣ Creating test word list...")
    create_payload = {
        "name": "Test Edit List",
        "words": ["apple", "banana", "cherry"],
        "description": "Test list for edit/delete functionality"
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/saved-lists",
            json=create_payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create list. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        data = response.json()
        if not data.get("ok"):
            print(f"❌ Create failed: {data.get('error')}")
            return False
            
        list_id = data.get("list", {}).get("id")
        if not list_id:
            print("❌ No list ID returned")
            return False
            
        print(f"✅ Created list with ID: {list_id}")
        print(f"   Words: {data.get('list', {}).get('word_count')} words")
        
    except Exception as e:
        print(f"❌ Error creating list: {e}")
        return False
    
    # Step 2: Edit the word list
    print("\n2️⃣ Editing word list...")
    edit_payload = {
        "name": "Test Edit List - UPDATED",
        "words": ["apple", "banana", "cherry", "date", "elderberry"],
        "replace_words": True
    }
    
    try:
        response = session.put(
            f"{BASE_URL}/api/saved-lists/{list_id}",
            json=edit_payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to edit list. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        data = response.json()
        if not data.get("ok"):
            print(f"❌ Edit failed: {data.get('error')}")
            return False
            
        updated_list = data.get("list", {})
        print(f"✅ Successfully edited list")
        print(f"   New name: {updated_list.get('name')}")
        print(f"   New word count: {updated_list.get('word_count')}")
        
        # Verify the changes
        if updated_list.get("name") != "Test Edit List - UPDATED":
            print("❌ Name was not updated correctly")
            return False
            
        if updated_list.get("word_count") != 5:
            print(f"❌ Word count incorrect. Expected 5, got {updated_list.get('word_count')}")
            return False
            
        print("✅ Edit verification passed")
        
    except Exception as e:
        print(f"❌ Error editing list: {e}")
        return False
    
    # Step 3: Verify the edit by fetching the list
    print("\n3️⃣ Verifying edited list...")
    try:
        response = session.get(
            f"{BASE_URL}/api/saved-lists/{list_id}",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch list. Status: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get("ok"):
            print(f"❌ Fetch failed: {data.get('error')}")
            return False
            
        fetched_list = data.get("list", {})
        words = fetched_list.get("words", [])
        
        print(f"✅ Fetched list successfully")
        print(f"   Words in list: {words}")
        
        expected_words = ["apple", "banana", "cherry", "date", "elderberry"]
        if words != expected_words:
            print(f"❌ Words don't match. Expected {expected_words}, got {words}")
            return False
            
        print("✅ Verification passed - words match!")
        
    except Exception as e:
        print(f"❌ Error verifying list: {e}")
        return False
    
    # Step 4: Delete the word list
    print("\n4️⃣ Deleting word list...")
    try:
        response = session.delete(
            f"{BASE_URL}/api/saved-lists/{list_id}",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to delete list. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        data = response.json()
        if not data.get("ok"):
            print(f"❌ Delete failed: {data.get('error')}")
            return False
            
        print(f"✅ Successfully deleted list ID: {list_id}")
        
    except Exception as e:
        print(f"❌ Error deleting list: {e}")
        return False
    
    # Step 5: Verify deletion
    print("\n5️⃣ Verifying deletion...")
    try:
        response = session.get(
            f"{BASE_URL}/api/saved-lists/{list_id}",
            timeout=10
        )
        
        # Should return 404 or error
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print("❌ List still exists after deletion!")
                return False
        
        print("✅ Deletion verified - list no longer exists")
        
    except Exception as e:
        print(f"✅ Deletion verified (error expected): {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("🐝 BeeSmart Word List Edit & Delete Test Suite")
    print("Make sure the Flask app is running on http://localhost:5000\n")
    
    success = test_word_list_operations()
    
    sys.exit(0 if success else 1)
