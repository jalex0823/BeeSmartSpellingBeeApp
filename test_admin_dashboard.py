#!/usr/bin/env python3
"""
Admin Dashboard Route Test
Tests the admin dashboard route for any database schema issues
"""

import traceback
from flask import Flask
from flask_login import current_user

def test_admin_dashboard_route():
    """Test admin dashboard route for database issues"""
    print("🔧 Testing Admin Dashboard Route")
    print("=" * 40)
    
    try:
        # Import the Flask app
        from AjaSpellBApp import app
        
        with app.test_client() as client:
            # Test admin dashboard endpoint
            print("🧪 Testing /admin/dashboard route...")
            response = client.get('/admin/dashboard')
            
            if response.status_code == 302:
                print(f"✅ Route exists - redirects to login (expected for non-authenticated user)")
                print(f"   Status: {response.status_code}")
                print(f"   Location: {response.headers.get('Location', 'No redirect')}")
            elif response.status_code == 200:
                print(f"✅ Route accessible - Status: {response.status_code}")
            else:
                print(f"❌ Route error - Status: {response.status_code}")
                if hasattr(response, 'data'):
                    print(f"   Response: {response.data.decode()[:200]}...")
                    
    except Exception as e:
        print(f"❌ Error testing admin dashboard: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Test for database schema issues
    try:
        print("\n🗄️  Testing Database Schema...")
        from AjaSpellBApp import db, User, QuizSession, QuizResult, SpeedRoundScore
        
        # Test QuizSession model
        print("   Testing QuizSession model...")
        sample_session = QuizSession.query.first()
        if sample_session:
            # Check if session_end attribute exists
            if hasattr(sample_session, 'session_end'):
                print("   ✅ QuizSession.session_end exists")
            else:
                print("   ❌ QuizSession.session_end missing")
                
            # Check if completed_at attribute exists (it shouldn't)
            if hasattr(sample_session, 'completed_at'):
                print("   ⚠️ QuizSession.completed_at exists (should be session_end)")
            else:
                print("   ✅ QuizSession.completed_at properly removed")
        else:
            print("   📝 No QuizSession records to test")
            
        # Test SpeedRoundScore model  
        print("   Testing SpeedRoundScore model...")
        sample_score = SpeedRoundScore.query.first()
        if sample_score:
            if hasattr(sample_score, 'completed_at'):
                print("   ✅ SpeedRoundScore.completed_at exists")
            else:
                print("   ❌ SpeedRoundScore.completed_at missing")
        else:
            print("   📝 No SpeedRoundScore records to test")
            
    except Exception as e:
        print(f"❌ Database schema test error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    print("\n🎯 Admin Dashboard Test Complete!")

if __name__ == "__main__":
    test_admin_dashboard_route()