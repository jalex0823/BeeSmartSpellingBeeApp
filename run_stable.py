"""
Simple server runner using waitress for stable operation
"""
import os
os.environ['FLASK_DEBUG'] = '0'

from AjaSpellBApp import app

if __name__ == '__main__':
    try:
        from waitress import serve
        print("\n" + "=" * 60)
        print("🚀 Starting BeeSmart with Waitress (Production Server)")
        print("=" * 60)
        print("📍 Server: http://127.0.0.1:5000")
        print("📍 Health: http://127.0.0.1:5000/health")
        print("=" * 60)
        print("\n🐝 Server is running... Press CTRL+C to stop\n")
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except ImportError:
        print("⚠️  Waitress not installed. Installing now...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'waitress'])
        print("✅ Waitress installed! Please run this script again.")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
