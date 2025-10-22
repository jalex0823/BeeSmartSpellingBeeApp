#!/usr/bin/env python3
"""
Simple test to trigger default word loading and see debug output
"""

import requests

def trigger_word_loading():
    print("🔄 Triggering default word loading...")
    
    session = requests.Session()
    
    # Access quiz page to establish session
    response = session.get("http://localhost:5000/quiz")
    print(f"Quiz page access: {response.status_code}")
    
    # Call API next to trigger word loading
    response = session.post("http://localhost:5000/api/next")
    print(f"API next response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total words loaded: {data.get('total', 0)}")
    
    # Get first word details
    response = session.post("http://localhost:5000/api/pronounce")
    print(f"API pronounce response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"First word: {data.get('word', 'N/A')}")

if __name__ == "__main__":
    trigger_word_loading()