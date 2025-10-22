#!/usr/bin/env python3
"""
Railway Avatar Generation Fix - Deployment Solution
Addresses specific Railway deployment issues with avatar generation
"""

def add_railway_avatar_fixes_to_main_app():
    """
    Generate code to add Railway-safe avatar handling to AjaSpellBApp.py
    """
    
    fix_code = '''
# ==============================================================================
# RAILWAY AVATAR GENERATION FIX
# Add this code to your AjaSpellBApp.py to resolve Railway avatar issues
# ==============================================================================

import os
import logging
from functools import wraps

# Configure logging for Railway
if os.getenv('RAILWAY_ENVIRONMENT'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def railway_safe(fallback_value=None):
    """Decorator to make functions Railway-deployment safe"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except ImportError as e:
                logger.error(f"Railway Import Error in {func.__name__}: {e}")
                return fallback_value
            except FileNotFoundError as e:
                logger.error(f"Railway File Error in {func.__name__}: {e}")
                return fallback_value
            except Exception as e:
                logger.error(f"Railway Error in {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator

@railway_safe(fallback_value=[])
def get_avatar_catalog_safe():
    """Railway-safe avatar catalog retrieval"""
    try:
        from avatar_catalog import get_avatar_catalog
        catalog = get_avatar_catalog()
        logger.info(f"Avatar catalog loaded: {len(catalog)} avatars")
        return catalog
    except Exception as e:
        logger.warning(f"Using fallback avatar catalog due to: {e}")
        # Minimal fallback catalog
        return [
            {
                "id": "cool-bee",
                "name": "Cool Bee", 
                "folder": "CoolBee",
                "obj_file": "CoolBee.obj",
                "mtl_file": "CoolBee.mtl", 
                "texture_file": "CoolBee.png",
                "description": "Default cool bee avatar",
                "variants": ["default"],
                "category": "classic"
            }
        ]

@railway_safe(fallback_value=None)
def get_avatar_info_safe(avatar_id, variant='default'):
    """Railway-safe avatar info retrieval"""
    try:
        from avatar_catalog import get_avatar_info
        result = get_avatar_info(avatar_id, variant)
        if result:
            logger.info(f"Avatar info retrieved for: {avatar_id}")
        return result
    except Exception as e:
        logger.warning(f"Avatar info fallback for {avatar_id}: {e}")
        # Return minimal avatar info
        return {
            "id": avatar_id,
            "name": avatar_id.replace('-', ' ').title(),
            "description": "Avatar temporarily unavailable", 
            "category": "classic"
        }

@railway_safe(fallback_value=(False, "Validation temporarily unavailable"))
def validate_avatar_safe(avatar_id, variant='default'):
    """Railway-safe avatar validation"""
    try:
        from avatar_catalog import validate_avatar
        is_valid, message = validate_avatar(avatar_id, variant)
        logger.info(f"Avatar validation for {avatar_id}: {is_valid}")
        return is_valid, message
    except Exception as e:
        logger.warning(f"Avatar validation fallback for {avatar_id}: {e}")
        # Always return valid for common avatars in fallback mode
        common_avatars = ['cool-bee', 'al-bee', 'doctor-bee', 'queen-bee']
        if avatar_id in common_avatars:
            return True, "Validated (fallback mode)"
        return False, "Avatar validation temporarily unavailable"

@railway_safe(fallback_value={})
def get_avatar_theme_safe(avatar_id):
    """Railway-safe avatar theme retrieval"""
    try:
        from avatar_catalog import get_avatar_theme, generate_theme_from_title
        
        # Try to get existing theme
        theme = get_avatar_theme(avatar_id)
        if theme:
            return theme
            
        # Generate new theme as fallback
        name = avatar_id.replace('-', ' ').title()
        theme = generate_theme_from_title(name)
        logger.info(f"Generated theme for {avatar_id}: {theme['ui_style']}")
        return theme
        
    except Exception as e:
        logger.warning(f"Using default theme for {avatar_id}: {e}")
        # Return default theme
        return {
            'primary_color': '#FFD700',
            'secondary_color': '#FFA500',
            'accent_color': '#FFFF00',
            'personality': ['friendly', 'helpful', 'cheerful'],
            'ui_style': 'default',
            'animation_style': 'standard',
            'description_keywords': ['friendly', 'helpful', 'bee']
        }

# ==============================================================================
# REPLACE YOUR EXISTING AVATAR API ROUTES WITH THESE RAILWAY-SAFE VERSIONS
# ==============================================================================

@app.route("/api/avatars", methods=["GET"])
def api_get_avatars_railway_safe():
    """Railway-safe avatar catalog API"""
    try:
        # Get avatars with Railway-safe method
        avatars = get_avatar_catalog_safe()
        
        # Check if filtering by category or search
        category = request.args.get('category')
        search_query = request.args.get('search')
        
        if search_query:
            # Safe search filtering
            search_lower = search_query.lower()
            avatars = [a for a in avatars if search_lower in a.get('name', '').lower() 
                      or search_lower in a.get('description', '').lower()]
        
        if category:
            avatars = [a for a in avatars if a.get('category') == category]
        
        # Enrich with Railway-safe URLs
        enriched_avatars = []
        for avatar in avatars:
            avatar_id = avatar['id']
            enriched = avatar.copy()
            
            # Use safe URL generation
            try:
                enriched['thumbnail'] = f"/static/assets/avatars/{avatar_id}/thumbnail.png"
                enriched['preview'] = f"/static/assets/avatars/{avatar_id}/preview.png"
            except:
                # Fallback URLs
                enriched['thumbnail'] = f"/static/default_avatar_thumb.png"
                enriched['preview'] = f"/static/default_avatar_preview.png"
            
            enriched_avatars.append(enriched)
        
        return jsonify({
            'status': 'success',
            'avatars': enriched_avatars,
            'total': len(enriched_avatars),
            'railway_safe': True,
            'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local')
        })
    
    except Exception as e:
        logger.error(f"Avatar API critical error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Avatar system temporarily unavailable',
            'railway_safe': True,
            'fallback': True
        }), 500

@app.route("/api/avatar/<avatar_id>", methods=["GET"])
def api_get_avatar_railway_safe(avatar_id):
    """Railway-safe individual avatar API"""
    try:
        # Validate with Railway-safe method
        is_valid, reason = validate_avatar_safe(avatar_id)
        
        if not is_valid and "temporarily unavailable" not in reason:
            return jsonify({
                'status': 'error',
                'message': f'Avatar not found: {avatar_id}',
                'reason': reason,
                'railway_safe': True
            }), 404
        
        # Get avatar info with Railway-safe method
        avatar_info = get_avatar_info_safe(avatar_id)
        
        if not avatar_info:
            return jsonify({
                'status': 'error',
                'message': f'Avatar data unavailable: {avatar_id}',
                'railway_safe': True
            }), 404
        
        return jsonify({
            'status': 'success',
            'avatar': avatar_info,
            'railway_safe': True
        })
    
    except Exception as e:
        logger.error(f"Individual avatar API error for {avatar_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Avatar temporarily unavailable',
            'railway_safe': True
        }), 500

@app.route("/api/avatar/theme/<avatar_id>", methods=["GET"])
def api_get_avatar_theme_railway_safe(avatar_id):
    """Railway-safe avatar theme API"""
    try:
        theme = get_avatar_theme_safe(avatar_id)
        
        return jsonify({
            'status': 'success',
            'theme': theme,
            'avatar_id': avatar_id,
            'railway_safe': True
        })
    
    except Exception as e:
        logger.error(f"Avatar theme API error for {avatar_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Avatar theme temporarily unavailable',
            'railway_safe': True
        }), 500

# ==============================================================================
# RAILWAY DEPLOYMENT HEALTH CHECK
# ==============================================================================

@app.route("/api/avatar/health", methods=["GET"])
def avatar_system_health():
    """Health check for avatar system on Railway"""
    try:
        health_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
            'railway_deployment': bool(os.getenv('RAILWAY_ENVIRONMENT')),
            'avatar_system_status': 'operational'
        }
        
        # Test avatar catalog access
        try:
            avatars = get_avatar_catalog_safe()
            health_data['avatar_count'] = len(avatars)
            health_data['catalog_accessible'] = True
        except:
            health_data['catalog_accessible'] = False
            health_data['avatar_count'] = 0
        
        # Test file system access
        try:
            avatar_dir = "static/Avatars/3D Avatar Files"
            health_data['avatar_files_accessible'] = os.path.exists(avatar_dir)
            if health_data['avatar_files_accessible']:
                health_data['avatar_folders'] = len(os.listdir(avatar_dir))
        except:
            health_data['avatar_files_accessible'] = False
            health_data['avatar_folders'] = 0
        
        # Test theme generation
        try:
            test_theme = get_avatar_theme_safe('cool-bee')
            health_data['theme_generation'] = bool(test_theme)
        except:
            health_data['theme_generation'] = False
        
        return jsonify(health_data)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'avatar_system_status': 'degraded',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ==============================================================================
# END OF RAILWAY AVATAR FIX
# ==============================================================================
'''
    
    return fix_code

if __name__ == "__main__":
    print("🚂 RAILWAY AVATAR GENERATION FIX")
    print("=" * 60)
    print("Generating Railway-safe avatar handling code...")
    
    fix_code = add_railway_avatar_fixes_to_main_app()
    
    # Save to file
    with open("railway_avatar_fix_code.txt", "w") as f:
        f.write(fix_code)
    
    print("✅ Railway avatar fix generated!")
    print()
    print("📝 INTEGRATION STEPS:")
    print("1. Copy code from railway_avatar_fix_code.txt")
    print("2. Add it to your AjaSpellBApp.py file")  
    print("3. Replace existing avatar routes with Railway-safe versions")
    print("4. Deploy to Railway")
    print("5. Test with /api/avatar/health endpoint")
    print()
    print("🔧 KEY IMPROVEMENTS:")
    print("• Railway-safe error handling with fallbacks")
    print("• Comprehensive logging for debugging")
    print("• Graceful degradation when files missing")
    print("• Health check endpoint for monitoring")
    print("• Environment detection and adaptation")
    print()
    print("💡 After deployment, check Railway logs and test:")
    print("   GET https://your-app.railway.app/api/avatar/health")
    print("   GET https://your-app.railway.app/api/avatars")