#!/usr/bin/env python3
"""
Guest Filtering Implementation
Adds guest user filtering to admin dashboard queries
"""

def add_guest_filtering_to_app():
    """
    Add guest filtering functions to AjaSpellBApp.py
    """
    
    guest_filter_code = '''
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
'''
    
    return guest_filter_code

def create_updated_admin_dashboard_function():
    """
    Create updated admin dashboard function with guest filtering
    """
    
    updated_function = '''
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with guest user filtering"""
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    # Get MY teacher key to find students/family under my supervision
    # (Admins use teacher_key field for tracking their students)
    my_key = current_user.teacher_key
    
    # Find all students who registered with MY teacher key (exclude guests)
    my_students = []
    if my_key:
        # Get student IDs from TeacherStudent link table
        student_links = TeacherStudent.query.filter_by(
            teacher_key=my_key,
            is_active=True
        ).all()
        
        # Get the actual user objects for these students (exclude guests)
        student_ids = [link.student_id for link in student_links]
        if student_ids:
            my_students = filter_non_guest_users(
                User.query.filter(User.id.in_(student_ids))
            ).order_by(User.created_at.desc()).all()
        
        # Enrich student data with their stats (filter out any remaining guests)
        my_students = [student for student in my_students if not is_guest_user(student)]
        
        for student in my_students:
            # Count ALL quiz sessions (completed AND incomplete with progress)
            student.quiz_count = QuizSession.query.filter_by(
                user_id=student.id
            ).filter(
                # Include completed sessions OR incomplete sessions with at least one answer
                or_(
                    QuizSession.completed == True,
                    and_(
                        QuizSession.completed == False,
                        (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                    )
                )
            ).count()
            
            student.words_practiced = QuizResult.query.filter_by(
                user_id=student.id
            ).count()
            
            student.correct_count = QuizResult.query.filter_by(
                user_id=student.id,
                is_correct=True
            ).count()
            
            # Calculate accuracy
            if student.words_practiced > 0:
                student.accuracy = round((student.correct_count / student.words_practiced) * 100, 1)
            else:
                student.accuracy = 0
            
            # Get latest quiz date (including incomplete sessions)
            latest_quiz = QuizSession.query.filter_by(
                user_id=student.id
            ).filter(
                or_(
                    QuizSession.completed == True,
                    and_(
                        QuizSession.completed == False,
                        (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                    )
                )
            ).order_by(
                QuizSession.session_end.desc().nullslast(),
                QuizSession.session_start.desc()
            ).first()
            
            student.last_active = (
                latest_quiz.session_end if (latest_quiz and latest_quiz.session_end)
                else latest_quiz.session_start if (latest_quiz and latest_quiz.session_start)
                else student.created_at
            )
    
    # System-wide statistics (exclude guest users)
    stats = {
        'total_users': get_non_guest_users_query().count(),
        'total_students': filter_non_guest_users(User.query.filter_by(role='student')).count(),
        'total_teachers': filter_non_guest_users(User.query.filter_by(role='teacher')).count(),
        'total_quizzes': QuizSession.query.join(User).filter(
            and_(
                or_(
                    QuizSession.completed == True,
                    and_(
                        QuizSession.completed == False,
                        (QuizSession.correct_count + QuizSession.incorrect_count) > 0
                    )
                ),
                # Exclude guest users from quiz counts
                not_(User.username.like('guest_%')),
                User.password_hash.isnot(None)
            )
        ).count(),
        'total_words_attempted': QuizResult.query.join(User).filter(
            and_(
                not_(User.username.like('guest_%')),
                User.password_hash.isnot(None)
            )
        ).count(),
        'my_students_count': len(my_students)
    }
    
    # Battle Bee Statistics (placeholder - Battle models not yet implemented)
    total_battles = 0
    active_battles = 0
    completed_battles = 0
    
    # Get top 10 players on the leaderboard (exclude guests)
    leaderboard = get_leaderboard_no_guests(10)
    
    # Enrich leaderboard with stats (battle stats placeholders until Battle models implemented)
    for idx, player in enumerate(leaderboard, start=1):
        player.rank = idx
        # Placeholder: battle stats not yet implemented
        player.total_battles_played = getattr(player, 'total_battles_played', 0)
        player.total_battles_won = getattr(player, 'total_battles_won', 0)
        player.win_rate = round((player.total_battles_won / player.total_battles_played * 100), 1) if player.total_battles_played > 0 else 0
        # Use total_lifetime_points as honey_points for now
        player.honey_points = getattr(player, 'honey_points', player.total_lifetime_points or 0)
    
    battle_stats = {
        'total_battles': total_battles,
        'active_battles': active_battles,
        'completed_battles': completed_battles,
        'total_battle_participants': 0  # Placeholder until Battle models implemented
    }
    
    return render_template('admin/dashboard.html', 
                         user=current_user, 
                         stats=stats,
                         battle_stats=battle_stats,
                         leaderboard=leaderboard,
                         my_students=my_students,
                         admin_key=my_key)  # Pass teacher_key as admin_key for template
'''
    
    return updated_function

if __name__ == "__main__":
    print("🚫 GUEST FILTERING IMPLEMENTATION")
    print("=" * 50)
    
    guest_filter_code = add_guest_filtering_to_app()
    updated_dashboard_function = create_updated_admin_dashboard_function()
    
    # Save guest filtering utilities
    with open("guest_filtering_utilities.py", "w", encoding='utf-8') as f:
        f.write(guest_filter_code)
    
    # Save updated dashboard function
    with open("updated_admin_dashboard_function.py", "w", encoding='utf-8') as f:
        f.write(updated_dashboard_function)
    
    print(f"\n💾 Files created:")
    print(f"   guest_filtering_utilities.py")
    print(f"   updated_admin_dashboard_function.py")
    
    print(f"\n🔧 GUEST FILTERING FEATURES:")
    print(f"✅ is_guest_user() - Check if user is guest")
    print(f"✅ filter_non_guest_users() - Add query filters")
    print(f"✅ get_students_no_guests() - Get students only")
    print(f"✅ get_leaderboard_no_guests() - Get leaderboard only")
    print(f"✅ Updated admin dashboard with filtering")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Add utilities to AjaSpellBApp.py")
    print(f"2. Replace admin_dashboard() function") 
    print(f"3. Update other admin routes")
    print(f"4. Test guest filtering works")
    
    print(f"\n✅ Guest filtering ready for integration!")