"""
Backfill rank badges for users who already have Buzz Dust/bee_class but missing the rank badges
This fixes the issue where elite badges were not being awarded
"""
from models import db, User, Achievement
from config import get_config
from flask import Flask
from buzz_dust_helpers import get_bee_class
from datetime import datetime, timezone

app = Flask(__name__)
cfg = get_config()
app.config['SQLALCHEMY_DATABASE_URI'] = cfg.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def backfill_rank_badges():
    """Award missing rank badges to all users based on their current Buzz Dust"""
    with app.app_context():
        users = User.query.filter(User.role != 'guest').all()
        
        print(f"\n{'='*70}")
        print(f"\ud83d\udc1d BACKFILLING RANK BADGES FOR {len(users)} USERS")
        print(f"{'='*70}\n")
        
        total_awarded = 0
        
        for user in users:
            buzz_dust = user.total_buzz_dust or 0
            current_class = get_bee_class(buzz_dust)
            class_id = current_class.get('id', 'novice')
            
            print(f"User: {user.username} (Buzz Dust: {buzz_dust}, Class: {class_id})")
            
            # List of all ranks they should have based on their Buzz Dust
            ranks_earned = []
            from buzz_dust_helpers import BEE_CLASSES
            for bee_class in BEE_CLASSES:
                if buzz_dust >= bee_class['min_buzz_dust']:
                    ranks_earned.append(bee_class['id'])
            
            # Check each rank badge
            for rank_id in ranks_earned:
                badge_type = f"{rank_id}_rank"
                
                # Check if they already have this badge
                existing = Achievement.query.filter_by(
                    user_id=user.id,
                    achievement_type=badge_type
                ).first()
                
                if not existing:
                    # Award the missing rank badge
                    new_badge = Achievement(
                        user_id=user.id,
                        achievement_type=badge_type,
                        points_bonus=0,
                        earned_date=user.last_rank_up_at or datetime.now(timezone.utc)
                    )
                    db.session.add(new_badge)
                    total_awarded += 1
                    print(f"  \u2705 Awarded: {badge_type}")
                else:
                    print(f"  \u2705 Already has: {badge_type}")
            
            # Update bee_class field if it doesn't match
            if user.bee_class != class_id:
                print(f"  \ud83d\udd04 Updating bee_class: {user.bee_class} \u2192 {class_id}")
                user.bee_class = class_id
            
            print()
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"{'='*70}")
            print(f"\u2728 SUCCESS: Awarded {total_awarded} missing rank badges!")
            print(f"{'='*70}\n")
        except Exception as e:
            db.session.rollback()
            print(f"\u274c ERROR: Failed to commit changes: {e}")

if __name__ == '__main__':
    backfill_rank_badges()
