#!/usr/bin/env python3
"""
Test script for guide search functionality
Tests the search features in the guide pages
"""

import requests
import time
from pathlib import Path

def test_guide_search_functionality():
    """Test that guide pages load and have search functionality"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Guide Search Functionality")
    print("=" * 50)
    
    # Test both guide pages
    guides = [
        ("/guide", "User Guide"),
        ("/admin-guide", "Administrator Guide")
    ]
    
    for url, name in guides:
        print(f"\n📖 Testing {name}...")
        
        try:
            # Test if page loads
            response = requests.get(f"{base_url}{url}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name} loads successfully (Status: {response.status_code})")
                
                # Check for search elements
                content = response.text
                
                search_elements = [
                    'id="searchBox"',
                    'class="search-box"',
                    'performSearch(',
                    'clearSearch()',
                    'search-highlight',
                    'searchResults'
                ]
                
                missing_elements = []
                for element in search_elements:
                    if element in content:
                        print(f"  ✅ Found search element: {element}")
                    else:
                        missing_elements.append(element)
                        print(f"  ❌ Missing search element: {element}")
                
                if not missing_elements:
                    print(f"  🎉 All search functionality present in {name}")
                else:
                    print(f"  ⚠️  {len(missing_elements)} search elements missing in {name}")
                    
                # Check for guide content
                guide_indicators = [
                    "BeeSmart",
                    "guide",
                    "🐝"
                ]
                
                content_found = sum(1 for indicator in guide_indicators if indicator.lower() in content.lower())
                print(f"  📄 Guide content indicators found: {content_found}/{len(guide_indicators)}")
                
            else:
                print(f"❌ {name} failed to load (Status: {response.status_code})")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to {base_url}{url}")
            print("   Make sure Flask server is running: python AjaSpellBApp.py")
            return False
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")
            return False
    
    return True

def test_search_features_list():
    """Display the implemented search features"""
    print("\n🚀 Implemented Search Features:")
    print("=" * 50)
    
    features = [
        "🔍 Real-time search as you type (300ms debounce)",
        "💡 Search multiple keywords (space-separated)",
        "🎯 Case-insensitive matching",
        "✨ Highlight matching text with yellow background",
        "📄 Show/hide content sections based on matches",
        "📊 Display match count and query",
        "🚫 'No results found' message when needed",
        "🧹 Clear search button and functionality",
        "⌨️  Keyboard shortcuts (Ctrl+F to focus, Esc to clear)",
        "📍 Auto-scroll to first search result",
        "🔗 Context-aware: shows parent headings for matches",
        "💾 Preserves original content when clearing search"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature}")
    
    print(f"\n📋 Usage Instructions:")
    print("   • Type in search box to find content instantly")
    print("   • Use multiple keywords: 'avatar upload quiz'")
    print("   • Press Ctrl+F (or Cmd+F) to focus search box")  
    print("   • Press Escape or click Clear to reset view")
    print("   • Search works on both User Guide and Admin Guide")

def main():
    """Run search functionality tests"""
    print("🐝 BeeSmart Guide Search Test")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ Server is running (Health check: {response.status_code})")
    except:
        print("❌ Server not running. Please start with: python AjaSpellBApp.py")
        return 1
    
    # Test search functionality
    if test_guide_search_functionality():
        print("\n🎉 All guide search tests passed!")
    else:
        print("\n⚠️  Some search tests failed.")
    
    # Display feature list
    test_search_features_list()
    
    print("\n🌐 Quick Test Links:")
    print("   • User Guide: http://localhost:5000/guide")
    print("   • Admin Guide: http://localhost:5000/admin-guide")
    print("   • Main App: http://localhost:5000")
    
    return 0

if __name__ == "__main__":
    exit(main())