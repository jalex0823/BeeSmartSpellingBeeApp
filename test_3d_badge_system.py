"""
3D Badge System Test
Verifies GLB badge files and renderer integration
"""
import os
from pathlib import Path

def test_badge_glb_files_exist():
    """Verify all GLB badge files exist"""
    badges_dir = Path('static/assets/badges/glb_files')
    
    expected_badges = [
        'Novice.glb',
        'Apprentice.glb',
        'Scholar.glb',
        'Elite.glb',
        'Magistrate.glb',
        'BuzzDustMaster.glb'
    ]
    
    missing = []
    for badge in expected_badges:
        badge_path = badges_dir / badge
        if not badge_path.exists():
            missing.append(badge)
    
    if missing:
        print(f"❌ Missing GLB badge files: {missing}")
        return False
    
    print(f"✅ All {len(expected_badges)} GLB badge files exist")
    return True

def test_config_uses_glb():
    """Verify buzz_dust_config.json uses .glb extensions"""
    import json
    
    config_path = Path('config/buzz_dust_config.json')
    if not config_path.exists():
        print("❌ buzz_dust_config.json not found")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    bee_classes = config.get('bee_classes', [])
    incorrect = []
    
    for bee_class in bee_classes:
        badge_image = bee_class.get('badge_image', '')
        if not badge_image.endswith('.glb'):
            incorrect.append({
                'id': bee_class.get('id'),
                'badge_image': badge_image
            })
    
    if incorrect:
        print(f"❌ Config has non-GLB badge images: {incorrect}")
        return False
    
    print(f"✅ All {len(bee_classes)} bee classes use .glb badge files")
    return True

def test_badge_renderer_exists():
    """Verify badge-3d-renderer.js exists"""
    renderer_path = Path('static/js/badge-3d-renderer.js')
    
    if not renderer_path.exists():
        print("❌ badge-3d-renderer.js not found")
        return False
    
    content = renderer_path.read_text(encoding='utf-8')
    
    # Check for key classes/functions
    required = [
        'class Badge3DRenderer',
        'window.Badge3DRenderer',
        'window.renderBadge3D',
        'THREE.GLTFLoader',
        'loadBadge()',
        'fallbackToPNG()'
    ]
    
    missing = [item for item in required if item not in content]
    
    if missing:
        print(f"❌ badge-3d-renderer.js missing: {missing}")
        return False
    
    print("✅ badge-3d-renderer.js contains all required components")
    return True

def test_base_html_loads_renderer():
    """Verify base.html loads badge-3d-renderer.js"""
    base_html = Path('templates/base.html')
    
    if not base_html.exists():
        print("❌ base.html not found")
        return False
    
    content = base_html.read_text(encoding='utf-8')
    
    if 'badge-3d-renderer.js' not in content:
        print("❌ base.html does not load badge-3d-renderer.js")
        return False
    
    print("✅ base.html loads badge-3d-renderer.js")
    return True

def test_rank_progress_bar_uses_3d():
    """Verify rank_progress_bar.html uses 3D badge container"""
    component_path = Path('templates/components/rank_progress_bar.html')
    
    if not component_path.exists():
        print("❌ rank_progress_bar.html not found")
        return False
    
    content = component_path.read_text(encoding='utf-8')
    
    # Check for 3D badge container
    if 'rank-badge-3d' not in content:
        print("❌ rank_progress_bar.html missing rank-badge-3d container")
        return False
    
    if 'Badge3DRenderer' not in content:
        print("❌ rank_progress_bar.html missing Badge3DRenderer initialization")
        return False
    
    # Check old IMG tag is removed
    if 'rank-badge-image' in content and 'img' in content.lower():
        print("⚠️ Warning: rank_progress_bar.html may still have old IMG badge code")
    
    print("✅ rank_progress_bar.html uses 3D badge rendering")
    return True

def test_admin_dashboard_uses_3d():
    """Verify admin dashboard uses 3D badges"""
    dashboard_path = Path('templates/admin/dashboard.html')
    
    if not dashboard_path.exists():
        print("❌ admin/dashboard.html not found")
        return False
    
    content = dashboard_path.read_text(encoding='utf-8')
    
    # Check for 3D badge initialization
    if 'new Badge3DRenderer(badgeEl' not in content:
        print("❌ admin/dashboard.html missing Badge3DRenderer initialization")
        return False
    
    print("✅ admin/dashboard.html uses 3D badge rendering")
    return True

def main():
    """Run all 3D badge system tests"""
    print("🎖️ 3D Badge System Verification")
    print("=" * 50)
    
    tests = [
        ("GLB Badge Files Exist", test_badge_glb_files_exist),
        ("Config Uses GLB Extensions", test_config_uses_glb),
        ("Badge Renderer Exists", test_badge_renderer_exists),
        ("Base.html Loads Renderer", test_base_html_loads_renderer),
        ("Rank Progress Bar Uses 3D", test_rank_progress_bar_uses_3d),
        ("Admin Dashboard Uses 3D", test_admin_dashboard_uses_3d),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Testing: {test_name}")
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - 3D badge system ready!")
        print("\n📝 Summary:")
        print("   1. All 6 GLB badge files exist")
        print("   2. Config uses .glb extensions")
        print("   3. Badge3DRenderer class implemented")
        print("   4. Loaded in base.html globally")
        print("   5. Rank progress bar component updated")
        print("   6. Admin dashboard updated")
    else:
        print(f"❌ {failed} test(s) failed - review errors above")
    
    return failed == 0

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
