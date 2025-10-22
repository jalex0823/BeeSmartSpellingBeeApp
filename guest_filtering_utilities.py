
# ============================================================================
# GUEST USER FILTERING UTILITIES
# ============================================================================

def is_guest_user(user):
    """
    Check if a user is a guest user
    Returns True if user is guest, False otherwise
    """
    if not user:
        return False
    
    # Check username pattern (guest users have usernames starting with 'guest_')
    if user.username and user.username.startswith('guest_'):
        return True
    
    # Check if user has no password hash (guests don't have passwords)
    if not hasattr(user, 'password_hash') or not user.password_hash:
        return True
    
    # Check if display name indicates guest
    if user.display_name and user.display_name.startswith('Guest '):
        return True
    
    return False

def filter_non_guest_users(query):
    """
    Add filter to exclude guest users from a User query
    Returns modified query that excludes guests
    """
    from sqlalchemy import and_, not_
    
    return query.filter(
        and_(
            # Exclude usernames starting with 'guest_'
            not_(User.username.like('guest_%')),
            # Ensure user has a password hash (guests don't)
            User.password_hash.isnot(None),
            User.password_hash != '',
            # Exclude display names starting with 'Guest '
            not_(User.display_name.like('Guest %'))
        )
    )

def get_non_guest_users_query():
    """
    Get a base User query that excludes all guest users
    """
    return filter_non_guest_users(User.query)

def get_students_no_guests():
    """
    Get all student users excluding guests
    """
    return filter_non_guest_users(
        User.query.filter_by(role='student')
    ).order_by(User.created_at.desc()).all()

def get_leaderboard_no_guests(limit=10):
    """
    Get leaderboard excluding guest users
    """
    return filter_non_guest_users(
        User.query.filter(
            User.role.in_(['student', 'teacher', 'parent', 'admin'])
        )
    ).order_by(
        User.total_lifetime_points.desc(),
        User.total_quizzes_completed.desc(),
        User.created_at.asc()
    ).limit(limit).all()

# ============================================================================
# END GUEST USER FILTERING
# ============================================================================
