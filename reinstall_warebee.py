from avatar_catalog import ais_install_with_railway_validation
import shutil
import os

# Remove the old WareBee with incorrect software theme
warebee_path = 'static/Avatars/3D Avatar Files/WareBee'
if os.path.exists(warebee_path):
    shutil.rmtree(warebee_path)
    print("🗑️ Removed old WareBee with software theme")

# Reinstall WareBee with correct werewolf theme
print("🐺 Reinstalling WareBee with werewolf theme...")
result = ais_install_with_railway_validation('WareBee')

if result:
    print(f"✅ WareBee successfully reinstalled!")
    print(f"   Theme: {result.get('theme', {}).get('ui_style', 'unknown')} style")
    print(f"   Primary Color: {result.get('theme', {}).get('primary_color', 'unknown')}")
    print(f"   Personality: {', '.join(result.get('theme', {}).get('personality', []))}")
    print(f"🌙 WareBee is now a fierce werewolf bee, not a software bee!")
else:
    print("❌ Failed to reinstall WareBee")