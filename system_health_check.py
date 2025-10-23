"""
BeeSmart System Health Check
Comprehensive diagnostic to verify all app processes before mobile packaging
Run this before deploying to mobile app stores
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class HealthChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'checks': []
        }
        
    def add_result(self, category, name, status, message, details=None):
        """Add check result"""
        self.results['checks'].append({
            'category': category,
            'name': name,
            'status': status,  # 'pass', 'fail', 'warning'
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if status == 'pass':
            self.results['passed'] += 1
            print_success(f"{name}: {message}")
        elif status == 'fail':
            self.results['failed'] += 1
            print_error(f"{name}: {message}")
        elif status == 'warning':
            self.results['warnings'] += 1
            print_warning(f"{name}: {message}")
            
        if details:
            print(f"   Details: {details}")
    
    def check_file_structure(self):
        """Verify critical files and directories exist"""
        print_header("FILE STRUCTURE CHECK")
        
        required_files = [
            'AjaSpellBApp.py',
            'models.py',
            'requirements.txt',
            'Procfile',
            'railway.toml',
            'migrate_avatars_to_db.py',
            'avatar_catalog.py'
        ]
        
        required_dirs = [
            'static',
            'static/js',
            'static/css',
            'static/assets/avatars',
            'templates',
            'templates/auth',
            'templates/components',
            'data'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                self.add_result('Files', file, 'pass', 'Exists')
            else:
                self.add_result('Files', file, 'fail', 'Missing')
        
        for directory in required_dirs:
            if os.path.isdir(directory):
                file_count = len(list(Path(directory).rglob('*')))
                self.add_result('Directories', directory, 'pass', 
                              f'Exists with {file_count} files')
            else:
                self.add_result('Directories', directory, 'fail', 'Missing')
    
    def check_python_dependencies(self):
        """Check if critical Python packages are installed"""
        print_header("PYTHON DEPENDENCIES CHECK")
        
        critical_packages = [
            'flask',
            'sqlalchemy',
            'gunicorn',
            'python-dotenv',
            'flask_login',
            'werkzeug'
        ]
        
        for package in critical_packages:
            try:
                __import__(package.replace('-', '_'))
                self.add_result('Dependencies', package, 'pass', 'Installed')
            except ImportError:
                self.add_result('Dependencies', package, 'fail', 'Not installed')
    
    def check_database_models(self):
        """Verify database models are correctly defined"""
        print_header("DATABASE MODELS CHECK")
        
        try:
            from models import User, QuizSession, WordMastery, Achievement, Avatar
            
            models = [
                ('User', User),
                ('QuizSession', QuizSession),
                ('WordMastery', WordMastery),
                ('Achievement', Achievement),
                ('Avatar', Avatar)
            ]
            
            for model_name, model_class in models:
                try:
                    # Check if model has required attributes
                    if hasattr(model_class, '__tablename__'):
                        self.add_result('Models', model_name, 'pass', 
                                      f'Defined with table: {model_class.__tablename__}')
                    else:
                        self.add_result('Models', model_name, 'warning', 
                                      'Missing __tablename__')
                except Exception as e:
                    self.add_result('Models', model_name, 'fail', str(e))
                    
        except Exception as e:
            self.add_result('Models', 'Import', 'fail', f'Failed to import models: {e}')
    
    def check_database_connection(self):
        """Test database connectivity and table creation"""
        print_header("DATABASE CONNECTION CHECK")
        
        try:
            from AjaSpellBApp import app, db
            from models import User, Avatar
            
            with app.app_context():
                # Test database connection
                try:
                    db.engine.connect()
                    self.add_result('Database', 'Connection', 'pass', 'Connected successfully')
                except Exception as e:
                    self.add_result('Database', 'Connection', 'fail', str(e))
                    return
                
                # Check if tables exist
                try:
                    user_count = User.query.count()
                    self.add_result('Database', 'Users Table', 'pass', 
                                  f'{user_count} users in database')
                except Exception as e:
                    self.add_result('Database', 'Users Table', 'warning', 
                                  f'Query failed: {e}')
                
                try:
                    avatar_count = Avatar.query.count()
                    if avatar_count > 0:
                        self.add_result('Database', 'Avatars Table', 'pass', 
                                      f'{avatar_count} avatars in database')
                    else:
                        self.add_result('Database', 'Avatars Table', 'warning', 
                                      'Table exists but empty')
                except Exception as e:
                    self.add_result('Database', 'Avatars Table', 'warning', 
                                  f'Query failed: {e}')
                    
        except Exception as e:
            self.add_result('Database', 'Setup', 'fail', f'Database check failed: {e}')
    
    def check_avatar_assets(self):
        """Verify avatar 3D model files exist"""
        print_header("AVATAR ASSETS CHECK")
        
        avatar_base = Path('static/assets/avatars')
        if not avatar_base.exists():
            self.add_result('Avatars', 'Base Directory', 'fail', 'Missing')
            return
        
        avatar_folders = [d for d in avatar_base.iterdir() if d.is_dir()]
        total_avatars = len(avatar_folders)
        
        if total_avatars == 0:
            self.add_result('Avatars', 'Folders', 'fail', 'No avatar folders found')
            return
        
        self.add_result('Avatars', 'Folders', 'pass', 
                       f'Found {total_avatars} avatar folders')
        
        complete_avatars = 0
        incomplete_avatars = []
        
        for avatar_folder in avatar_folders:
            obj_files = list(avatar_folder.glob('*.obj'))
            mtl_files = list(avatar_folder.glob('*.mtl'))
            png_files = list(avatar_folder.glob('*.png'))
            
            if obj_files and png_files:
                complete_avatars += 1
            else:
                incomplete_avatars.append(avatar_folder.name)
        
        if complete_avatars == total_avatars:
            self.add_result('Avatars', 'Asset Completeness', 'pass', 
                          f'All {complete_avatars} avatars have required files')
        else:
            self.add_result('Avatars', 'Asset Completeness', 'warning', 
                          f'{complete_avatars}/{total_avatars} complete',
                          f'Incomplete: {", ".join(incomplete_avatars)}')
    
    def check_api_endpoints_local(self):
        """Test critical API endpoints locally"""
        print_header("LOCAL API ENDPOINTS CHECK")
        
        # Check if local server is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.add_result('API', 'Health Endpoint', 'pass', 
                              f'Server running: {response.json()}')
            else:
                self.add_result('API', 'Health Endpoint', 'fail', 
                              f'Status code: {response.status_code}')
                return
        except requests.exceptions.RequestException as e:
            self.add_result('API', 'Local Server', 'warning', 
                          'Server not running (start with: python AjaSpellBApp.py)')
            return
        
        # Test critical endpoints
        endpoints = [
            ('/api/avatars', 'GET', 'Avatar Catalog'),
            ('/api/users/me/avatar', 'GET', 'User Avatar'),
        ]
        
        for endpoint, method, name in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code in [200, 401]:  # 401 is ok (not logged in)
                    self.add_result('API', name, 'pass', 
                                  f'Endpoint accessible ({response.status_code})')
                else:
                    self.add_result('API', name, 'warning', 
                                  f'Status: {response.status_code}')
            except Exception as e:
                self.add_result('API', name, 'fail', str(e))
    
    def check_railway_deployment(self):
        """Test Railway production deployment"""
        print_header("RAILWAY DEPLOYMENT CHECK")
        
        railway_url = "https://beesmart.up.railway.app"
        
        try:
            # Test health endpoint
            response = requests.get(f"{railway_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.add_result('Railway', 'Health', 'pass', 
                              f'Server online: {data}')
            else:
                self.add_result('Railway', 'Health', 'fail', 
                              f'Status: {response.status_code}')
                return
        except Exception as e:
            self.add_result('Railway', 'Health', 'fail', f'Cannot reach: {e}')
            return
        
        # Test avatar API
        try:
            response = requests.get(f"{railway_url}/api/avatars", timeout=10)
            if response.status_code == 200:
                data = response.json()
                avatar_count = len(data.get('avatars', []))
                self.add_result('Railway', 'Avatar API', 'pass', 
                              f'{avatar_count} avatars available')
            else:
                self.add_result('Railway', 'Avatar API', 'warning', 
                              f'Status: {response.status_code}')
        except Exception as e:
            self.add_result('Railway', 'Avatar API', 'fail', str(e))
        
        # Test main page
        try:
            response = requests.get(railway_url, timeout=10)
            if response.status_code == 200:
                self.add_result('Railway', 'Main Page', 'pass', 
                              f'Homepage accessible ({len(response.content)} bytes)')
            else:
                self.add_result('Railway', 'Main Page', 'fail', 
                              f'Status: {response.status_code}')
        except Exception as e:
            self.add_result('Railway', 'Main Page', 'fail', str(e))
    
    def check_static_assets(self):
        """Verify critical static files"""
        print_header("STATIC ASSETS CHECK")
        
        critical_js = [
            'static/js/avatar-picker.js',
            'static/js/user-avatar-loader.js',
            'static/js/three.min.js',
            'static/js/OBJLoader.js',
            'static/js/MTLLoader.js'
        ]
        
        critical_css = [
            'static/css/BeeSmart.css'
        ]
        
        for js_file in critical_js:
            if os.path.exists(js_file):
                size = os.path.getsize(js_file)
                self.add_result('Static JS', os.path.basename(js_file), 'pass', 
                              f'{size:,} bytes')
            else:
                self.add_result('Static JS', os.path.basename(js_file), 'fail', 
                              'Missing')
        
        for css_file in critical_css:
            if os.path.exists(css_file):
                size = os.path.getsize(css_file)
                self.add_result('Static CSS', os.path.basename(css_file), 'pass', 
                              f'{size:,} bytes')
            else:
                self.add_result('Static CSS', os.path.basename(css_file), 'fail', 
                              'Missing')
    
    def check_templates(self):
        """Verify critical template files"""
        print_header("TEMPLATES CHECK")
        
        critical_templates = [
            'templates/unified_menu.html',
            'templates/quiz.html',
            'templates/test_avatar_picker.html',
            'templates/auth/student_dashboard.html',
            'templates/components/avatar_picker.html'
        ]
        
        for template in critical_templates:
            if os.path.exists(template):
                size = os.path.getsize(template)
                self.add_result('Templates', os.path.basename(template), 'pass', 
                              f'{size:,} bytes')
            else:
                self.add_result('Templates', os.path.basename(template), 'fail', 
                              'Missing')
    
    def generate_report(self):
        """Generate final report"""
        print_header("HEALTH CHECK SUMMARY")
        
        total = self.results['passed'] + self.results['failed'] + self.results['warnings']
        
        print(f"\n{Colors.BOLD}Total Checks: {total}{Colors.END}")
        print(f"{Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.results['warnings']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        
        # Calculate percentage
        if total > 0:
            pass_rate = (self.results['passed'] / total) * 100
            print(f"\n{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.END}")
            
            if pass_rate >= 90:
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 System is healthy and ready for mobile packaging!{Colors.END}")
            elif pass_rate >= 70:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  System is functional but has some warnings. Review before mobile packaging.{Colors.END}")
            else:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ System has critical issues. Fix before mobile packaging.{Colors.END}")
        
        # Save detailed report
        report_file = f'health_check_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Colors.BLUE}📄 Detailed report saved: {report_file}{Colors.END}")
        
        return self.results['failed'] == 0
    
    def run_all_checks(self):
        """Run all health checks"""
        print_header("🐝 BEESMART SYSTEM HEALTH CHECK")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.check_file_structure()
        self.check_python_dependencies()
        self.check_database_models()
        self.check_database_connection()
        self.check_avatar_assets()
        self.check_static_assets()
        self.check_templates()
        self.check_api_endpoints_local()
        self.check_railway_deployment()
        
        return self.generate_report()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BeeSmart System Health Check')
    parser.add_argument('--local-only', action='store_true', 
                       help='Skip Railway deployment checks')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Local server URL (default: http://localhost:5000)')
    
    args = parser.parse_args()
    
    checker = HealthChecker(base_url=args.url)
    
    try:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Health check interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Health check failed with error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
