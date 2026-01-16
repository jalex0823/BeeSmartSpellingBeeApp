#!/usr/bin/env python3
"""
BeeSmart App - System-Wide Smoke Test

Comprehensive health check for all critical systems before deployment.
Checks: Database, IAP endpoints, Authentication, API endpoints, iOS build config.

Usage:
    python3 smoke_test.py
"""

import os
import sys
import json
import re
import requests
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class SmokeTest:
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.start_time = datetime.now()
        
    def log_pass(self, test_name, message=""):
        """Log a passing test"""
        self.results['passed'].append({'test': test_name, 'message': message})
        print(f"{GREEN}✅ PASS{RESET}: {test_name}")
        if message:
            print(f"   {message}")
    
    def log_fail(self, test_name, message=""):
        """Log a failing test"""
        self.results['failed'].append({'test': test_name, 'message': message})
        print(f"{RED}❌ FAIL{RESET}: {test_name}")
        if message:
            print(f"   {message}")
    
    def log_warning(self, test_name, message=""):
        """Log a warning"""
        self.results['warnings'].append({'test': test_name, 'message': message})
        print(f"{YELLOW}⚠️  WARN{RESET}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_database_connection(self):
        """Test database connection and basic queries"""
        print(f"\n{BOLD}{BLUE}Testing Database Connection...{RESET}")
        try:
            from config import Config
            from models import db, User
            from flask import Flask
            
            app = Flask(__name__)
            app.config.from_object(Config)
            db.init_app(app)
            
            with app.app_context():
                # Test connection
                try:
                    user_count = User.query.count()
                    self.log_pass("Database Connection", f"Connected successfully (found {user_count} users)")
                    return True
                except Exception as e:
                    self.log_fail("Database Connection", f"Query failed: {str(e)}")
                    return False
        except Exception as e:
            self.log_fail("Database Connection", f"Failed to initialize: {str(e)}")
            return False
    
    def test_database_pool_config(self):
        """Test database pool configuration"""
        print(f"\n{BOLD}{BLUE}Testing Database Pool Configuration...{RESET}")
        try:
            from config import Config
            
            options = Config.SQLALCHEMY_ENGINE_OPTIONS
            required_keys = ['pool_pre_ping', 'pool_recycle', 'pool_timeout', 'pool_size', 'max_overflow']
            
            missing = [key for key in required_keys if key not in options]
            if missing:
                self.log_fail("Database Pool Config", f"Missing keys: {', '.join(missing)}")
                return False
            
            # Check values
            if options.get('pool_timeout', 0) < 10:
                self.log_warning("Database Pool Config", "pool_timeout is less than 10 seconds")
            
            if options.get('pool_size', 0) < 3:
                self.log_warning("Database Pool Config", "pool_size is less than 3")
            
            self.log_pass("Database Pool Config", 
                         f"pool_size={options.get('pool_size')}, "
                         f"max_overflow={options.get('max_overflow')}, "
                         f"pool_timeout={options.get('pool_timeout')}")
            return True
        except Exception as e:
            self.log_fail("Database Pool Config", f"Error: {str(e)}")
            return False
    
    def test_iap_endpoints_exist(self):
        """Test that IAP endpoints are defined"""
        print(f"\n{BOLD}{BLUE}Testing IAP Endpoints...{RESET}")
        try:
            import re
            
            with open('AjaSpellBApp.py', 'r') as f:
                content = f.read()
            
            endpoints = {
                '/api/iap/verify/<platform>': r'@app\.route\([\'"]/api/iap/verify/',
                '/api/iap/restore': r'@app\.route\([\'"]/api/iap/restore',
                '/api/bundles/redeem': r'@app\.route\([\'"]/api/bundles/redeem'
            }
            
            all_found = True
            for endpoint, pattern in endpoints.items():
                if re.search(pattern, content):
                    self.log_pass(f"IAP Endpoint: {endpoint}")
                else:
                    self.log_fail(f"IAP Endpoint: {endpoint}", "Endpoint not found")
                    all_found = False
            
            # Check for resilient error handling
            if 'with_for_update' in content and 'skip_locked=True' in content:
                self.log_pass("IAP Race Condition Prevention", "Database locking implemented")
            else:
                self.log_warning("IAP Race Condition Prevention", "Database locking may be missing")
            
            return all_found
        except Exception as e:
            self.log_fail("IAP Endpoints Check", f"Error: {str(e)}")
            return False
    
    def test_ios_build_config(self):
        """Test iOS build configuration files"""
        print(f"\n{BOLD}{BLUE}Testing iOS Build Configuration...{RESET}")
        
        # Try multiple possible paths
        possible_paths = [
            Path('mobile/ios/App/App.xcodeproj/project.pbxproj'),
            Path('mobile/ios/App/App/App.xcodeproj/project.pbxproj'),
            Path('mobile/ios/App/App/App.xcodeproj/project.pbxproj')
        ]
        
        pbxproj_path = None
        for path in possible_paths:
            if path.exists():
                pbxproj_path = path
                break
        
        if not pbxproj_path:
            self.log_fail("iOS Build Config", "project.pbxproj not found in any expected location")
            return False
        
        try:
            with open(pbxproj_path, 'r') as f:
                pbxproj_content = f.read()
            
            # Check for version numbers
            if 'CURRENT_PROJECT_VERSION' in pbxproj_content:
                # Extract version
                import re
                version_match = re.search(r'CURRENT_PROJECT_VERSION = (\d+)', pbxproj_content)
                if version_match:
                    version = int(version_match.group(1))
                    self.log_pass("iOS Build Version", f"Found version: {version}")
                else:
                    self.log_warning("iOS Build Version", "Version number format not recognized")
            else:
                self.log_fail("iOS Build Version", "CURRENT_PROJECT_VERSION not found")
            
            # Check config.xml (try multiple locations)
            config_xml_paths = [
                pbxproj_path.parent.parent / 'config.xml',
                pbxproj_path.parent.parent / 'App' / 'config.xml'
            ]
            
            config_found = False
            for config_path in config_xml_paths:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config_content = f.read()
                    
                    if 'widget version' in config_content:
                        self.log_pass("iOS Config.xml", f"Found widget version in {config_path.name}")
                        config_found = True
                        break
            
            if not config_found:
                self.log_warning("iOS Config.xml", "config.xml not found in expected locations")
            
            return True
        except Exception as e:
            self.log_fail("iOS Build Config", f"Error: {str(e)}")
            return False
    
    def test_models_import(self):
        """Test that all critical models can be imported"""
        print(f"\n{BOLD}{BLUE}Testing Models Import...{RESET}")
        try:
            from models import (
                User, QuizSession, QuizResult, PurchaseRecord,
                AnonPurchaseOwnership, Achievement
            )
            self.log_pass("Models Import", "All critical models imported successfully")
            return True
        except ImportError as e:
            self.log_fail("Models Import", f"Import error: {str(e)}")
            return False
        except Exception as e:
            self.log_fail("Models Import", f"Error: {str(e)}")
            return False
    
    def test_config_import(self):
        """Test that config can be imported"""
        print(f"\n{BOLD}{BLUE}Testing Config Import...{RESET}")
        try:
            from config import Config
            self.log_pass("Config Import", "Config imported successfully")
            
            # Check database URL is set
            if hasattr(Config, 'SQLALCHEMY_DATABASE_URI'):
                db_url = Config.SQLALCHEMY_DATABASE_URI
                if db_url and db_url != 'sqlite:///beesmart.db':
                    self.log_pass("Database URL", "Production database URL configured")
                else:
                    self.log_warning("Database URL", "Using default SQLite database")
            
            return True
        except Exception as e:
            self.log_fail("Config Import", f"Error: {str(e)}")
            return False
    
    def test_error_handling_patterns(self):
        """Test that error handling patterns are in place"""
        print(f"\n{BOLD}{BLUE}Testing Error Handling Patterns...{RESET}")
        try:
            with open('AjaSpellBApp.py', 'r') as f:
                content = f.read()
            
            patterns = {
                'Database commit error handling': r'db\.session\.commit\(\)[\s\S]{0,500}except.*commit',
                'Rollback on error': r'except.*rollback',
                'Error logging': r'app\.logger\.error.*exc_info=True',
                'Graceful degradation': r'return.*200.*warning'
            }
            
            all_found = True
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, content, re.MULTILINE):
                    self.log_pass(f"Error Handling: {pattern_name}")
                else:
                    self.log_warning(f"Error Handling: {pattern_name}", "Pattern not found")
            
            return True
        except Exception as e:
            self.log_fail("Error Handling Patterns", f"Error: {str(e)}")
            return False
    
    def test_file_structure(self):
        """Test that required files exist"""
        print(f"\n{BOLD}{BLUE}Testing File Structure...{RESET}")
        required_files = [
            'AjaSpellBApp.py',
            'models.py',
            'config.py',
            'requirements.txt'
        ]
        
        # Check iOS project file (may be in different location)
        ios_project_paths = [
            'mobile/ios/App/App.xcodeproj/project.pbxproj',
            'mobile/ios/App/App/App.xcodeproj/project.pbxproj'
        ]
        
        all_exist = True
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                self.log_pass(f"File Exists: {file_path}")
            else:
                self.log_fail(f"File Exists: {file_path}", "File not found")
                all_exist = False
        
        # Check iOS project file separately
        ios_found = False
        for ios_path in ios_project_paths:
            if Path(ios_path).exists():
                self.log_pass(f"File Exists: {ios_path}")
                ios_found = True
                break
        
        if not ios_found:
            self.log_warning("iOS Project File", "project.pbxproj not found in expected locations")
        
        return all_exist
    
    def run_all_tests(self):
        """Run all smoke tests"""
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}BeeSmart App - System-Wide Smoke Test{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        tests = [
            self.test_file_structure,
            self.test_config_import,
            self.test_models_import,
            self.test_database_pool_config,
            self.test_database_connection,
            self.test_iap_endpoints_exist,
            self.test_error_handling_patterns,
            self.test_ios_build_config,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_fail(f"Test Execution: {test.__name__}", f"Unexpected error: {str(e)}")
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}SMOKE TEST REPORT{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"\nTotal Tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"{YELLOW}Warnings: {warnings}{RESET}")
        print(f"\nDuration: {duration:.2f} seconds")
        
        if failed > 0:
            print(f"\n{RED}{BOLD}❌ SMOKE TEST FAILED{RESET}")
            print(f"\nFailed Tests:")
            for failure in self.results['failed']:
                print(f"  - {failure['test']}: {failure.get('message', '')}")
            return False
        elif warnings > 0:
            print(f"\n{YELLOW}{BOLD}⚠️  SMOKE TEST PASSED WITH WARNINGS{RESET}")
            return True
        else:
            print(f"\n{GREEN}{BOLD}✅ ALL TESTS PASSED{RESET}")
            return True

def main():
    """Main entry point"""
    tester = SmokeTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
