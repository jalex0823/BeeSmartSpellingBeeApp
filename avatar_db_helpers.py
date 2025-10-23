"""
Avatar Database Helpers
Database-backed avatar management functions to replace avatar_catalog.py functions
Maintains backward compatibility with existing API contracts
"""

from models import Avatar, db
from flask import current_app


def get_avatar_info_db(avatar_id, variant='default'):
    """
    Get avatar information from database with URLs for 3D model and thumbnail
    Database-backed version of avatar_catalog.get_avatar_info()
    
    Args:
        avatar_id: Avatar slug/identifier (e.g., 'cool-bee', 'explorer-bee')
        variant: 'default' (all avatars use single default variant)
        
    Returns:
        dict with avatar info including URLs, or None if not found
    """
    # Query database for avatar
    avatar = Avatar.get_by_slug(avatar_id)
    
    # Fallback to 'cool-bee' if not found (was 'al-bee' in catalog version)
    if not avatar:
        avatar = Avatar.get_by_slug('cool-bee')
        if not avatar:
            # Ultimate fallback - get first active avatar
            avatar = Avatar.query.filter_by(is_active=True).first()
    
    if not avatar:
        return None  # No avatars in database at all
    
    # Build asset URLs
    base_path = f"/static/assets/avatars/{avatar.folder_path}"
    
    # Auto-validate MTL references (optional - can import from avatar_catalog if needed)
    # Skipping for now to avoid circular imports
    
    return {
        'id': avatar.slug,  # Keep 'id' key for backward compatibility
        'name': avatar.name,
        'description': avatar.description,
        'variant': variant,  # Always 'default'
        'category': avatar.category,
        'thumbnail_url': f"{base_path}/{avatar.thumbnail_file}",
        'preview_url': f"{base_path}/{avatar.thumbnail_file}",  # Use same as thumbnail
        'model_obj_url': f"{base_path}/{avatar.obj_file}",
        'model_mtl_url': f"{base_path}/{avatar.mtl_file}" if avatar.mtl_file else None,
        'texture_url': f"{base_path}/{avatar.texture_file}" if avatar.texture_file else None,
        'fallback_url': "/static/assets/avatars/fallback.png",
        # Additional fields from database
        'unlock_level': avatar.unlock_level,
        'points_required': avatar.points_required,
        'is_premium': avatar.is_premium,
        'sort_order': avatar.sort_order
    }


def get_avatars_by_category_db():
    """Get avatars grouped by category from database"""
    categories = {}
    
    avatars = Avatar.get_all_active()
    
    for avatar in avatars:
        cat = avatar.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(avatar.to_dict())
    
    return categories


def get_all_avatars_db():
    """Get all active avatars from database"""
    avatars = Avatar.get_all_active()
    return [avatar.to_dict() for avatar in avatars]


def validate_avatar_db(avatar_id):
    """
    Check if avatar exists and is active in database
    
    Args:
        avatar_id: Avatar slug to validate
        
    Returns:
        bool: True if avatar exists and is active, False otherwise
    """
    avatar = Avatar.get_by_slug(avatar_id)
    return avatar is not None and avatar.is_active


def get_unlocked_avatars_for_user(user):
    """
    Get avatars that are unlocked for a specific user based on level/points
    
    Args:
        user: User model instance
        
    Returns:
        list: Avatar dictionaries that user has unlocked
    """
    user_level = getattr(user, 'account_level', 1)
    user_points = getattr(user, 'total_lifetime_points', 0)
    
    # Query avatars that user can access
    avatars = Avatar.query.filter(
        Avatar.is_active == True,
        db.or_(
            Avatar.unlock_level <= user_level,
            Avatar.points_required <= user_points
        )
    ).order_by(Avatar.sort_order, Avatar.name).all()
    
    return [avatar.to_dict() for avatar in avatars]


def get_locked_avatars_for_user(user):
    """
    Get avatars that are still locked for a specific user
    
    Args:
        user: User model instance
        
    Returns:
        list: Avatar dictionaries that user has not yet unlocked
    """
    user_level = getattr(user, 'account_level', 1)
    user_points = getattr(user, 'total_lifetime_points', 0)
    
    # Query avatars that user cannot access yet
    avatars = Avatar.query.filter(
        Avatar.is_active == True,
        Avatar.unlock_level > user_level,
        Avatar.points_required > user_points
    ).order_by(Avatar.unlock_level, Avatar.points_required).all()
    
    return [avatar.to_dict() for avatar in avatars]


# Backward compatibility wrapper - can be used as drop-in replacement
def get_avatar_info(avatar_id, variant='default', use_db=True):
    """
    Hybrid function that can use database or fallback to catalog
    
    Args:
        avatar_id: Avatar slug
        variant: Variant name (always 'default' for our avatars)
        use_db: If True, query database first. If False or DB fails, use catalog
        
    Returns:
        dict with avatar info
    """
    if use_db:
        try:
            info = get_avatar_info_db(avatar_id, variant)
            if info:
                return info
        except Exception as e:
            current_app.logger.warning(f"Database avatar lookup failed for {avatar_id}: {e}")
    
    # Fallback to catalog version
    from avatar_catalog import get_avatar_info as catalog_get_avatar_info
    return catalog_get_avatar_info(avatar_id, variant)
