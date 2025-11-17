#!/usr/bin/env python3
"""
🏥 BeeSmart Spelling App - Comprehensive Health Check
Tests all systems, subsystems, and processes
"""

import sys
import os
import json
import requests
import time
from datetime import datetime
from collections import defaultdict

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class HealthChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = defaultdict(list)
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.warning_count = 0
        
    def log(self, status, category, test_name, message=""):
        """Log test result"""
        self.test_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status == "PASS":
            self.pass_count += 1
            color = GREEN
            symbol = "✅"
        elif status == "FAIL":
            self.fail_count += 1
            color = RED
            symbol = "❌"
        elif status == "WARN":
            self.warning_count += 1
            color = YELLOW
            symbol = "⚠️"
        else:
            color = BLUE
            symbol = "ℹ️"
            
        print(f"{color}{symbol} [{timestamp}] {category}: {test_name}{RESET}")
        if message:
            print(f"   {message}")
            
        self.results[category].append({
            'status': status,
            'test': test_name,
            'message': message,
            'timestamp': timestamp
        })
        
    def test_core_application(self):
        """Test 1: Core Application Health"""
        category = "Core Application"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Core Application Health{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: App is running
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("PASS", category, "Health Endpoint", 
                        f"Version: {data.get('version', 'unknown')}")
            else:
                self.log("FAIL", category, "Health Endpoint", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Health Endpoint", str(e))
            
        # Test: Main page loads
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Main Page Load", 
                        f"Size: {len(response.content)} bytes")
            else:
                self.log("FAIL", category, "Main Page Load", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Main Page Load", str(e))
            
        # Test: Session management
        try:
            response = self.session.get(f"{self.base_url}/api/wordbank")
            if response.status_code in [200, 401]:
                self.log("PASS", category, "Session Management", 
                        "API responds correctly")
            else:
                self.log("WARN", category, "Session Management", 
                        f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Session Management", str(e))
            
        # Test: Static assets
        static_files = [
            '/static/css/BeeSmart.css',
            '/static/js/avatar-picker.js',
            '/service-worker.js'
        ]
        for asset in static_files:
            try:
                response = self.session.get(f"{self.base_url}{asset}", timeout=3)
                if response.status_code == 200:
                    self.log("PASS", category, f"Static Asset: {asset.split('/')[-1]}", 
                            f"{len(response.content)} bytes")
                else:
                    self.log("WARN", category, f"Static Asset: {asset.split('/')[-1]}", 
                            f"HTTP {response.status_code}")
            except Exception as e:
                self.log("FAIL", category, f"Static Asset: {asset.split('/')[-1]}", str(e))
                
    def test_authentication(self):
        """Test 2: Authentication System"""
        category = "Authentication"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Authentication System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Login page loads
        try:
            response = self.session.get(f"{self.base_url}/login", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Login Page Load", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Login Page Load", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Login Page Load", str(e))
            
        # Test: Register page loads
        try:
            response = self.session.get(f"{self.base_url}/register", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Register Page Load", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Register Page Load", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Register Page Load", str(e))
            
        # Test: Forgot password page loads
        try:
            response = self.session.get(f"{self.base_url}/forgot-password", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Forgot Password Page", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Forgot Password Page", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Forgot Password Page", str(e))
            
        # Test: Protected routes require auth
        try:
            response = self.session.get(f"{self.base_url}/admin", timeout=5)
            if response.status_code in [302, 401, 403]:
                self.log("PASS", category, "Protected Route Security", 
                        "Admin requires authentication")
            else:
                self.log("WARN", category, "Protected Route Security", 
                        f"Expected redirect/401/403, got {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Protected Route Security", str(e))
            
    def test_word_management(self):
        """Test 3: Word Management System"""
        category = "Word Management"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Word Management System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Upload page loads
        try:
            response = self.session.get(f"{self.base_url}/upload", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Upload Page Load", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Upload Page Load", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Upload Page Load", str(e))
            
        # Test: API wordbank endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/wordbank")
            if response.status_code == 200:
                data = response.json()
                word_count = len(data.get('words', []))
                self.log("PASS", category, "Wordbank API", 
                        f"{word_count} words loaded")
            elif response.status_code == 401:
                self.log("PASS", category, "Wordbank API", 
                        "Requires authentication (expected)")
            else:
                self.log("WARN", category, "Wordbank API", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Wordbank API", str(e))
            
        # Test: Upload API endpoint exists
        try:
            # We don't actually upload, just check the endpoint responds
            response = self.session.post(
                f"{self.base_url}/api/upload",
                timeout=5
            )
            # Should return 400 (bad request) or 401 (unauthorized), not 404
            if response.status_code in [400, 401, 403]:
                self.log("PASS", category, "Upload API Endpoint", 
                        "Endpoint exists and validates requests")
            else:
                self.log("WARN", category, "Upload API Endpoint", 
                        f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Upload API Endpoint", str(e))
            
        # Test: Saved lists API
        try:
            response = self.session.get(f"{self.base_url}/api/saved-lists")
            if response.status_code in [200, 401]:
                self.log("PASS", category, "Saved Lists API", 
                        "Endpoint accessible")
            else:
                self.log("WARN", category, "Saved Lists API", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Saved Lists API", str(e))
            
    def test_quiz_system(self):
        """Test 4: Quiz System"""
        category = "Quiz System"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Quiz System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Quiz page loads
        try:
            response = self.session.get(f"{self.base_url}/quiz", timeout=5)
            if response.status_code == 200:
                content = response.text
                # Check for key quiz elements
                has_container = 'quiz-container' in content
                has_input = 'spellingInput' in content
                has_submit = 'submitButton' in content
                
                if has_container and has_input and has_submit:
                    self.log("PASS", category, "Quiz Page Load", 
                            "All key elements present")
                else:
                    self.log("WARN", category, "Quiz Page Load", 
                            "Some elements missing")
            else:
                self.log("FAIL", category, "Quiz Page Load", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Quiz Page Load", str(e))
            
        # Test: Quiz API endpoints
        endpoints = [
            '/api/next',
            '/api/answer',
            '/api/results'
        ]
        for endpoint in endpoints:
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json={},
                    timeout=5
                )
                # Should return 400/401/403, not 404
                if response.status_code in [400, 401, 403, 500]:
                    self.log("PASS", category, f"Quiz API: {endpoint}", 
                            "Endpoint exists")
                else:
                    self.log("WARN", category, f"Quiz API: {endpoint}", 
                            f"HTTP {response.status_code}")
            except Exception as e:
                self.log("FAIL", category, f"Quiz API: {endpoint}", str(e))
                
        # Test: Speed round quiz
        try:
            response = self.session.get(f"{self.base_url}/speed-round-quiz", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Speed Round Quiz", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Speed Round Quiz", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Speed Round Quiz", str(e))
            
    def test_avatar_system(self):
        """Test 5: Avatar System"""
        category = "Avatar System"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Avatar System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Avatar API
        try:
            response = self.session.get(f"{self.base_url}/api/avatars")
            if response.status_code == 200:
                data = response.json()
                if 'avatars' in data:
                    avatar_count = len(data['avatars'])
                    self.log("PASS", category, "Avatar API", 
                            f"{avatar_count} avatars available")
                else:
                    self.log("WARN", category, "Avatar API", 
                            "No avatars field in response")
            else:
                self.log("FAIL", category, "Avatar API", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Avatar API", str(e))
            
        # Test: Avatar picker page
        try:
            response = self.session.get(f"{self.base_url}/avatar-picker", timeout=5)
            if response.status_code == 200:
                self.log("PASS", category, "Avatar Picker Page", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Avatar Picker Page", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Avatar Picker Page", str(e))
            
        # Test: Avatar assets directory
        try:
            response = self.session.get(
                f"{self.base_url}/static/assets/avatars/glb_files/BuzzbotBee.glb",
                timeout=5
            )
            if response.status_code == 200:
                self.log("PASS", category, "Avatar Assets", 
                        f"GLB file accessible ({len(response.content)} bytes)")
            else:
                self.log("WARN", category, "Avatar Assets", 
                        f"Sample GLB file: HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Avatar Assets", str(e))
            
    def test_dictionary_system(self):
        """Test 6: Dictionary & Definition System"""
        category = "Dictionary System"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Dictionary & Definition System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Dictionary cache file exists
        try:
            cache_file = "data/dictionary.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cache_size = len(cache_data)
                    self.log("PASS", category, "Dictionary Cache", 
                            f"{cache_size} cached definitions")
            else:
                self.log("WARN", category, "Dictionary Cache", 
                        "Cache file not found")
        except Exception as e:
            self.log("FAIL", category, "Dictionary Cache", str(e))
            
        # Test: Wiktionary cache
        try:
            wikt_file = "data/wiktionary_cache.json"
            if os.path.exists(wikt_file):
                with open(wikt_file, 'r') as f:
                    wikt_data = json.load(f)
                    wikt_size = len(wikt_data)
                    self.log("PASS", category, "Wiktionary Cache", 
                            f"{wikt_size} cached entries")
            else:
                self.log("INFO", category, "Wiktionary Cache", 
                        "Cache file not found (may be loading)")
        except Exception as e:
            self.log("FAIL", category, "Wiktionary Cache", str(e))
            
    def test_points_achievements(self):
        """Test 7: Points & Achievement System"""
        category = "Points & Achievements"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Points & Achievement System{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Achievements page
        try:
            response = self.session.get(f"{self.base_url}/achievements", timeout=5)
            if response.status_code in [200, 302]:
                self.log("PASS", category, "Achievements Page", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Achievements Page", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Achievements Page", str(e))
            
        # Test: Leaderboard page
        try:
            response = self.session.get(f"{self.base_url}/leaderboard", timeout=5)
            if response.status_code in [200, 302]:
                self.log("PASS", category, "Leaderboard Page", 
                        "Page accessible")
            else:
                self.log("FAIL", category, "Leaderboard Page", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Leaderboard Page", str(e))
            
    def test_admin_dashboard(self):
        """Test 8: Admin Dashboard"""
        category = "Admin Dashboard"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Admin Dashboard{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Admin page (should redirect or require auth)
        try:
            response = self.session.get(f"{self.base_url}/admin", timeout=5)
            if response.status_code in [302, 401, 403]:
                self.log("PASS", category, "Admin Page Protection", 
                        "Requires authentication")
            elif response.status_code == 200:
                self.log("WARN", category, "Admin Page Protection", 
                        "Admin page accessible without auth")
            else:
                self.log("FAIL", category, "Admin Page Protection", 
                        f"HTTP {response.status_code}")
        except Exception as e:
            self.log("FAIL", category, "Admin Page Protection", str(e))
            
        # Test: Admin API endpoints
        admin_endpoints = [
            '/admin/api/users',
            '/admin/api/stats'
        ]
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code in [302, 401, 403]:
                    self.log("PASS", category, f"Admin API: {endpoint}", 
                            "Protected endpoint")
                else:
                    self.log("WARN", category, f"Admin API: {endpoint}", 
                            f"HTTP {response.status_code}")
            except Exception as e:
                self.log("FAIL", category, f"Admin API: {endpoint}", str(e))
                
    def test_database(self):
        """Test 9: Database Integrity"""
        category = "Database"
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Testing Database Integrity{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        # Test: Database files exist
        db_files = [
            'data/spelling_bee.db',
            'data/users.db'
        ]
        for db_file in db_files:
            if os.path.exists(db_file):
                size = os.path.getsize(db_file)
                self.log("PASS", category, f"Database File: {db_file}", 
                        f"{size} bytes")
            else:
                self.log("WARN", category, f"Database File: {db_file}", 
                        "File not found")
                        
        # Test: Railway database connection (if configured)
        try:
            import psycopg2
            db_url = os.environ.get('DATABASE_URL')
            if db_url:
                # Parse the URL to connect
                conn = psycopg2.connect(db_url)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM avatars;")
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                self.log("PASS", category, "Railway PostgreSQL", 
                        f"{count} avatars in database")
            else:
                self.log("INFO", category, "Railway PostgreSQL", 
                        "DATABASE_URL not configured")
        except ImportError:
            self.log("INFO", category, "Railway PostgreSQL", 
                    "psycopg2 not installed")
        except Exception as e:
            self.log("WARN", category, "Railway PostgreSQL", str(e))
            
    def generate_report(self):
        """Test 10: Generate Health Report"""
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}Health Check Summary{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
        total_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{BOLD}Test Results:{RESET}")
        print(f"  {GREEN}✅ Passed: {self.pass_count}{RESET}")
        print(f"  {RED}❌ Failed: {self.fail_count}{RESET}")
        print(f"  {YELLOW}⚠️  Warnings: {self.warning_count}{RESET}")
        print(f"  {BLUE}Total Tests: {self.test_count}{RESET}\n")
        
        # Calculate health score
        if self.test_count > 0:
            health_score = (self.pass_count / self.test_count) * 100
            if health_score >= 90:
                status = f"{GREEN}EXCELLENT{RESET}"
            elif health_score >= 75:
                status = f"{GREEN}GOOD{RESET}"
            elif health_score >= 60:
                status = f"{YELLOW}FAIR{RESET}"
            else:
                status = f"{RED}NEEDS ATTENTION{RESET}"
                
            print(f"{BOLD}Overall Health: {status} ({health_score:.1f}%){RESET}\n")
            
        # Category breakdown
        print(f"{BOLD}Category Breakdown:{RESET}")
        for category, tests in self.results.items():
            passes = sum(1 for t in tests if t['status'] == 'PASS')
            fails = sum(1 for t in tests if t['status'] == 'FAIL')
            warns = sum(1 for t in tests if t['status'] == 'WARN')
            total = len(tests)
            
            if fails > 0:
                color = RED
            elif warns > 0:
                color = YELLOW
            else:
                color = GREEN
                
            print(f"  {color}{category}: {passes}/{total} passed{RESET}")
            
        # Save detailed report
        report = {
            'timestamp': total_time,
            'summary': {
                'total': self.test_count,
                'passed': self.pass_count,
                'failed': self.fail_count,
                'warnings': self.warning_count,
                'health_score': round(health_score, 2) if self.test_count > 0 else 0
            },
            'results': dict(self.results)
        }
        
        report_file = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n{BLUE}📊 Detailed report saved to: {report_file}{RESET}\n")
        
    def run_all_tests(self):
        """Run all health checks"""
        print(f"\n{BOLD}{GREEN}{'='*60}{RESET}")
        print(f"{BOLD}{GREEN}🏥 BeeSmart Spelling App - Comprehensive Health Check{RESET}")
        print(f"{BOLD}{GREEN}{'='*60}{RESET}\n")
        print(f"Base URL: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            self.test_core_application()
            self.test_authentication()
            self.test_word_management()
            self.test_quiz_system()
            self.test_avatar_system()
            self.test_dictionary_system()
            self.test_points_achievements()
            self.test_admin_dashboard()
            self.test_database()
            self.generate_report()
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Health check interrupted by user{RESET}\n")
            self.generate_report()
        except Exception as e:
            print(f"\n{RED}Health check failed with error: {e}{RESET}\n")
            self.generate_report()
            raise

def main():
    """Main entry point"""
    # Check if app is running
    base_url = "http://localhost:5000"
    
    print(f"{BLUE}Checking if Flask app is running at {base_url}...{RESET}")
    try:
        response = requests.get(f"{base_url}/health", timeout=3)
        print(f"{GREEN}✅ App is running!{RESET}\n")
    except:
        print(f"{RED}❌ App is not running at {base_url}{RESET}")
        print(f"{YELLOW}Please start the app first: python AjaSpellBApp.py{RESET}\n")
        return 1
        
    # Run health checks
    checker = HealthChecker(base_url)
    checker.run_all_tests()
    
    return 0 if checker.fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
