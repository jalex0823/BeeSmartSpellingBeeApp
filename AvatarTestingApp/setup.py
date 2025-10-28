#!/usr/bin/env python3
"""
Deep Avatar Delta Analyzer - Setup Script
Initializes the Python backend environment and creates directory structure
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directory structure"""
    base_dir = Path(__file__).parent
    
    dirs = [
        base_dir / 'avatars' / 'working',
        base_dir / 'avatars' / 'broken',
        base_dir / 'reports',
        base_dir / 'uploads',
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def install_dependencies():
    """Install Python dependencies"""
    import subprocess
    
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        sys.exit(1)

def check_python_version():
    """Verify Python version compatibility"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"✗ Python 3.8+ required, found {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_env_file():
    """Create .env configuration file"""
    env_content = """# Avatar Analyzer Configuration

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# Server Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Avatar Paths
AVATAR_BASE_PATH=./avatars
REPORTS_PATH=./reports

# Analysis Configuration
MAX_FILE_SIZE=500MB
ENABLE_PARALLEL_ANALYSIS=True

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=DEBUG
"""
    
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        env_path.write_text(env_content)
        print(f"✓ Created configuration file: .env")
    else:
        print(f"✓ Configuration file already exists: .env")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add your avatar files to the 'avatars/' directory:")
    print("   - Working avatars → avatars/working/")
    print("   - Broken avatars → avatars/broken/")
    print("\n2. Start the Python backend:")
    print("   python app.py")
    print("\n3. In another terminal, start the React frontend:")
    print("   npm run dev")
    print("\n4. Open your browser to http://localhost:5173")
    print("\n" + "="*60)

if __name__ == '__main__':
    print("🚀 Deep Avatar Delta Analyzer - Setup")
    print("="*60)
    
    check_python_version()
    create_directories()
    install_dependencies()
    create_env_file()
    print_next_steps()
