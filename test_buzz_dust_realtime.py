"""
Test script to verify buzz dust and badge updates are working in real-time
"""
from models import db, User, Achievement
from config import get_config
from flask import Flask
from buzz_dust_helpers import get_bee_class, get_rank_progress

app = Flask(__name__)
cfg = get_config()
app.config['SQLALCHEMY_DATABASE_URI'] = cfg.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Get the student user
    user = User.query.filter_by(username='student').first()
    
    if not user:
        print("❌ No student user found!")
    else:
        print(f"\n{'='*70}")
        print(f"🐝 USER: {user.username} (ID: {user.id})")
        print(f"{'='*70}")
        print(f"Total Buzz Dust: {user.total_buzz_dust}")
        print(f"Bee Class: {user.bee_class}")
        print(f"Honey Points: {user.honey_points}")
        print(f"Total Lifetime Points: {user.total_lifetime_points}")
        
        # Get rank progress
        rank_progress = get_rank_progress(user.total_buzz_dust or 0)
        print(f"\n{'='*70}")
        print(f"🏆 RANK PROGRESS")
        print(f"{'='*70}")
        print(f"Current Class: {rank_progress['current_class']['label']}")
        print(f"Current Class Min Points: {rank_progress['current_class']['min_points']}")
        if rank_progress['next_class']:
            print(f"Next Class: {rank_progress['next_class']['label']}")
            print(f"Next Class Min Points: {rank_progress['next_class']['min_points']}")
            print(f"Progress: {rank_progress['progress_percent']:.1f}%")
            print(f"Dust Needed: {rank_progress['dust_needed']}")
        else:
            print(f"🎉 AT MAX RANK!")
        print(f"At Max Rank: {rank_progress['at_max_rank']}")
        
        # Get achievements/badges
        achievements = Achievement.query.filter_by(user_id=user.id).all()
        print(f"\n{'='*70}")
        print(f"🏅 BADGES/ACHIEVEMENTS ({len(achievements)} total)")
        print(f"{'='*70}")
        
        # Group by type
        badge_types = {}
        for ach in achievements:
            badge_type = ach.achievement_type
            if badge_type not in badge_types:
                badge_types[badge_type] = {
                    'count': 0,
                    'total_points': 0,
                    'latest': None
                }
            badge_types[badge_type]['count'] += 1
            badge_types[badge_type]['total_points'] += (ach.points_bonus or 0)
            if not badge_types[badge_type]['latest'] or ach.earned_date > badge_types[badge_type]['latest']:
                badge_types[badge_type]['latest'] = ach.earned_date
        
        if badge_types:
            for badge_type, data in sorted(badge_types.items()):
                print(f"  {badge_type}: {data['count']} earned, {data['total_points']} points, latest: {data['latest']}")
        else:
            print("  No badges earned yet")
        
        # Check specifically for elite badges
        elite_badges = [a for a in achievements if 'elite' in a.achievement_type.lower()]
        print(f"\n{'='*70}")
        print(f"👑 ELITE BADGES ({len(elite_badges)} total)")
        print(f"{'='*70}")
        if elite_badges:
            for badge in elite_badges:
                print(f"  {badge.achievement_type}: {badge.points_bonus} points, earned: {badge.earned_date}")
        else:
            print("  ⚠️ NO ELITE BADGES FOUND!")
            print(f"\n  💡 Debug: User has {user.total_buzz_dust} Buzz Dust")
            print(f"  💡 Current bee_class field: {user.bee_class}")
            
            # Check what the threshold should be
            from buzz_dust_helpers import BEE_CLASSES
            print(f"\n  📊 Bee Class Thresholds:")
            for bc in BEE_CLASSES:
                marker = " ← CURRENT" if bc['id'] == user.bee_class else ""
                print(f"    {bc['id']}: {bc['min_buzz_dust']} Buzz Dust ('{bc['label']}'){marker}")
