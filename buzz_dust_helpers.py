"""
BeeSmart Buzz Dust & Ranking System
Helpers for calculating gamified XP (Buzz Dust) and managing Bee Class ranks
"""

import json
import os
from datetime import datetime
from typing import Dict, Tuple, Optional

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'buzz_dust_config.json')

def load_buzz_dust_config() -> dict:
    """Load Buzz Dust configuration from JSON file"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load buzz_dust_config.json: {e}")
        # Return default config if file not found
        return {
            "buzz_dust": {
                "multiplier": 0.10,
                "bonuses": {
                    "perfect_round": 25,
                    "daily_challenge": 50,
                    "no_hint": 10,
                    "speed_bonus_base": 5,
                    "streaks": {"5": 5, "10": 15, "20": 40, "50": 100, "100": 250}
                }
            },
            "bee_classes": [
                {"id": "novice", "label": "Novice Bee", "min_buzz_dust": 0},
                {"id": "apprentice", "label": "Apprentice Bee", "min_buzz_dust": 500},
                {"id": "scholar", "label": "Scholar Bee", "min_buzz_dust": 2500},
                {"id": "elite", "label": "Elite Bee", "min_buzz_dust": 10000},
                {"id": "magistrate", "label": "Magistrate Bee", "min_buzz_dust": 50000},
                {"id": "master", "label": "Buzz Dust Master", "min_buzz_dust": 100000}
            ]
        }

# Cache config on module load
_CONFIG = load_buzz_dust_config()
BUZZ_DUST_MULTIPLIER = _CONFIG['buzz_dust']['multiplier']
BONUSES = _CONFIG['buzz_dust']['bonuses']
BEE_CLASSES = _CONFIG['bee_classes']


def get_bee_class(total_buzz_dust: int) -> Dict[str, any]:
    """
    Return the highest bee class whose min threshold is <= total_buzz_dust.
    
    Args:
        total_buzz_dust: User's cumulative Buzz Dust
        
    Returns:
        Dict with id, label, min_buzz_dust, emoji, description, etc.
    """
    current_class = BEE_CLASSES[0]  # Start with novice
    
    for bee_class in BEE_CLASSES:
        if total_buzz_dust >= bee_class['min_buzz_dust']:
            current_class = bee_class
        else:
            break
    
    # Add min_points alias for frontend compatibility
    result = current_class.copy()
    result['min_points'] = result.get('min_buzz_dust', 0)
    
    return result


def get_next_bee_class(total_buzz_dust: int) -> Optional[Dict[str, any]]:
    """
    Return the next bee class the user can achieve.
    Returns None if already at max rank.
    """
    current = get_bee_class(total_buzz_dust)
    current_index = next((i for i, c in enumerate(BEE_CLASSES) if c['id'] == current['id']), 0)
    
    if current_index < len(BEE_CLASSES) - 1:
        next_class = BEE_CLASSES[current_index + 1].copy()
        # Add min_points alias for frontend compatibility
        next_class['min_points'] = next_class.get('min_buzz_dust', 0)
        return next_class
    
    return None  # Already at max rank


def get_rank_progress(total_buzz_dust: int) -> Dict[str, any]:
    """
    Get detailed rank progress information.
    
    Returns:
        Dict with current_class, next_class, progress_percent, dust_needed, etc.
    """
    current = get_bee_class(total_buzz_dust)
    next_class = get_next_bee_class(total_buzz_dust)
    
    if next_class:
        current_threshold = current['min_buzz_dust']
        next_threshold = next_class['min_buzz_dust']
        dust_range = next_threshold - current_threshold
        dust_progress = total_buzz_dust - current_threshold
        progress_percent = min(100, int((dust_progress / dust_range) * 100))
        dust_needed = next_threshold - total_buzz_dust
    else:
        # Max rank achieved
        progress_percent = 100
        dust_needed = 0
    
    return {
        'current_class': current,
        'next_class': next_class,
        'progress_percent': progress_percent,
        'dust_needed': dust_needed,
        'total_buzz_dust': total_buzz_dust,
        'at_max_rank': next_class is None
    }


def calculate_quiz_buzz_dust(
    points: int,
    *,
    perfect_round: bool = False,
    daily_challenge: bool = False,
    no_hints: bool = False,
    streak_length: int = 0,
    speed_bonus_multiplier: float = 1.0
) -> Tuple[int, Dict[str, int]]:
    """
    Calculate Buzz Dust earned from a quiz.
    
    Args:
        points: Base points earned in the quiz
        perfect_round: True if all answers correct
        daily_challenge: True if this was a daily challenge quiz
        no_hints: True if no hints were used
        streak_length: Current streak of consecutive correct answers
        speed_bonus_multiplier: Multiplier for speed (1.0 = no bonus, 2.0 = double)
        
    Returns:
        Tuple of (total_buzz_dust, breakdown_dict)
    """
    breakdown = {}
    
    # Base Buzz Dust from points
    base_dust = int(points * BUZZ_DUST_MULTIPLIER)
    breakdown['base'] = base_dust
    total_dust = base_dust
    
    # Perfect round bonus
    if perfect_round:
        bonus = BONUSES.get('perfect_round', 25)
        breakdown['perfect_round'] = bonus
        total_dust += bonus
    
    # Daily challenge bonus
    if daily_challenge:
        bonus = BONUSES.get('daily_challenge', 50)
        breakdown['daily_challenge'] = bonus
        total_dust += bonus
    
    # No hint bonus
    if no_hints:
        bonus = BONUSES.get('no_hint', 10)
        breakdown['no_hint'] = bonus
        total_dust += bonus
    
    # Speed bonus
    if speed_bonus_multiplier > 1.0:
        speed_base = BONUSES.get('speed_bonus_base', 5)
        speed_bonus = int(speed_base * speed_bonus_multiplier)
        breakdown['speed'] = speed_bonus
        total_dust += speed_bonus
    
    # Streak bonuses (cumulative - give all bonuses up to current streak)
    streak_bonuses = BONUSES.get('streaks', {})
    streak_total = 0
    for threshold_str, bonus in sorted(streak_bonuses.items(), key=lambda x: int(x[0])):
        threshold = int(threshold_str)
        if streak_length >= threshold:
            streak_total += bonus
    
    if streak_total > 0:
        breakdown['streak'] = streak_total
        total_dust += streak_total
    
    return total_dust, breakdown


def add_buzz_dust(user, amount: int) -> Dict[str, any]:
    """
    Add Buzz Dust to user and check for rank-up.
    
    Args:
        user: User model instance
        amount: Buzz Dust to add
        
    Returns:
        Dict with rank_up info: {'ranked_up': bool, 'old_class': dict, 'new_class': dict}
    """
    from models import db
    
    before_dust = user.total_buzz_dust or 0
    user.total_buzz_dust = before_dust + amount
    
    old_class = get_bee_class(before_dust)
    new_class = get_bee_class(user.total_buzz_dust)
    
    ranked_up = old_class['id'] != new_class['id']
    
    if ranked_up:
        user.bee_class = new_class['id']
        user.last_rank_up_at = datetime.utcnow()
    
    db.session.commit()
    
    return {
        'ranked_up': ranked_up,
        'old_class': old_class,
        'new_class': new_class,
        'buzz_dust_added': amount,
        'total_buzz_dust': user.total_buzz_dust
    }


def get_leaderboard_data(limit: int = 50, role_filter: str = None) -> list:
    """
    Get leaderboard data sorted by Buzz Dust.
    
    Args:
        limit: Maximum number of users to return
        role_filter: Optional role filter ('student', 'teacher', etc.)
        
    Returns:
        List of dicts with rank, username, bee_class, total_buzz_dust
    """
    from models import User
    
    query = User.query.filter(User.is_active == True)
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    users = query.order_by(User.total_buzz_dust.desc()).limit(limit).all()
    
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        bee_class_info = get_bee_class(user.total_buzz_dust or 0)
        leaderboard.append({
            'rank': rank,
            'username': user.username,
            'display_name': user.display_name,
            'bee_class': bee_class_info,
            'total_buzz_dust': user.total_buzz_dust or 0,
            'avatar_id': user.avatar_id or 'cool-bee'
        })
    
    return leaderboard


def get_all_bee_classes() -> list:
    """Return list of all bee classes with metadata"""
    return BEE_CLASSES


def format_buzz_dust_display(amount: int) -> str:
    """Format Buzz Dust amount for display with proper separators"""
    if amount >= 1000000:
        return f"{amount / 1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount / 1000:.1f}K"
    else:
        return f"{amount:,}"
