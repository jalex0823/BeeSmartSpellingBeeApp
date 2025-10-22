"""
Battle of the Bees - Live Multiplayer Battle API
Real-time spelling battles with Socket.IO integration
"""
from flask import Blueprint, request, jsonify, abort, current_app
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room
from models import db, BattleSession, BattlePlayer, User
from datetime import datetime
import uuid

# Create battles blueprint
battles_bp = Blueprint('battles', __name__, url_prefix='/api/battles')


def _session_to_dict(session):
    """Convert BattleSession to dictionary for JSON response"""
    return {
        'id': session.id,
        'code': session.code,
        'status': session.status,
        'is_public': session.is_public,
        'allow_guests': session.allow_guests,
        'current_players': session.current_players,
        'max_players': session.max_players,
        'grade_range': session.grade_range,
        'mode': session.mode,
        'wordset': session.wordset_name,
        'created_at': session.created_at.isoformat() if session.created_at else None,
        'started_at': session.started_at.isoformat() if session.started_at else None,
        'player_names': session.player_names
    }


def _player_to_dict(player):
    """Convert BattlePlayer to dictionary for JSON response"""
    return {
        'id': player.id,
        'display_name': player.display_name,
        'joined_at': player.joined_at.isoformat() if player.joined_at else None,
        'words_attempted': player.words_attempted,
        'words_correct': player.words_correct,
        'accuracy': player.accuracy,
        'current_streak': player.current_streak,
        'max_streak': player.max_streak,
        'total_points': player.total_points,
        'is_active': player.is_active
    }


@battles_bp.route("/live", methods=["GET"])
def list_live_battles():
    """Get list of public live battles"""
    try:
        battles = BattleSession.query.filter(
            BattleSession.is_public.is_(True),
            BattleSession.status.in_(["waiting", "in_progress"])
        ).order_by(
            BattleSession.status.desc(), 
            BattleSession.created_at.desc()
        ).limit(50).all()
        
        return jsonify([_session_to_dict(battle) for battle in battles])
    
    except Exception as e:
        current_app.logger.error(f"Error listing live battles: {e}")
        return jsonify({"error": "Failed to load battles"}), 500


@battles_bp.route("/create", methods=["POST"])
@login_required
def create_battle():
    """Create a new battle session"""
    try:
        data = request.get_json() or {}
        
        # Validate input
        wordset_name = data.get("wordset_name", "Custom Set").strip()
        mode = data.get("mode", "standard").strip()
        max_players = min(max(int(data.get("max_players", 20)), 2), 50)
        is_public = bool(data.get("is_public", True))
        allow_guests = bool(data.get("allow_guests", True))
        grade_range = data.get("grade_range", "").strip()
        
        # Create battle session
        battle = BattleSession(
            created_by=current_user.id,
            wordset_name=wordset_name,
            mode=mode,
            max_players=max_players,
            is_public=is_public,
            allow_guests=allow_guests,
            grade_range=grade_range,
            status="waiting"
        )
        
        db.session.add(battle)
        db.session.commit()
        
        # Auto-join creator
        creator_player = BattlePlayer(
            session_id=battle.id,
            user_id=current_user.id,
            display_name=current_user.display_name
        )
        db.session.add(creator_player)
        db.session.commit()
        
        # Emit to all clients watching battles
        from app_socketio import socketio
        socketio.emit("battles:refresh", room="battles_lobby")
        
        return jsonify({
            "ok": True, 
            "battle": _session_to_dict(battle),
            "message": f"Battle {battle.code} created!"
        })
    
    except Exception as e:
        current_app.logger.error(f"Error creating battle: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to create battle"}), 500


@battles_bp.route("/<code>/join", methods=["POST"])
def join_battle(code):
    """Join an existing battle"""
    try:
        data = request.get_json() or {}
        display_name = (data.get("name") or "").strip()
        
        if not display_name:
            return jsonify({"error": "Name required"}), 400
        
        # Find battle
        battle = BattleSession.query.filter_by(code=code).first()
        if not battle:
            return jsonify({"error": "Battle not found"}), 404
        
        # Check if battle is joinable
        if battle.status not in ("waiting", "in_progress"):
            return jsonify({"error": "Battle is not joinable"}), 409
        
        # Check guest permissions
        if not battle.allow_guests and not current_user.is_authenticated:
            return jsonify({"error": "Guests not allowed in this battle"}), 403
        
        # Check if battle is full
        if battle.current_players >= battle.max_players:
            return jsonify({"error": "Battle is full"}), 409
        
        # Check if already joined
        existing_player = None
        if current_user.is_authenticated:
            existing_player = BattlePlayer.query.filter_by(
                session_id=battle.id,
                user_id=current_user.id,
                left_at=None
            ).first()
        
        if existing_player:
            return jsonify({"error": "Already joined this battle"}), 409
        
        # Create player record
        player = BattlePlayer(
            session_id=battle.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            display_name=display_name
        )
        
        db.session.add(player)
        db.session.commit()
        
        # Emit Socket.IO events
        from app_socketio import socketio
        socketio.emit("battle:new_player", {
            "name": display_name, 
            "code": battle.code,
            "player_count": battle.current_players
        }, room=f"battle_{battle.code}")
        
        socketio.emit("battles:refresh", room="battles_lobby")
        
        return jsonify({
            "ok": True, 
            "code": battle.code,
            "message": f"{display_name} joined the battle!"
        })
    
    except Exception as e:
        current_app.logger.error(f"Error joining battle {code}: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to join battle"}), 500


@battles_bp.route("/<code>", methods=["GET"])
def get_battle_info(code):
    """Get detailed battle information"""
    try:
        battle = BattleSession.query.filter_by(code=code).first()
        if not battle:
            return jsonify({"error": "Battle not found"}), 404
        
        # Get active players
        active_players = BattlePlayer.query.filter_by(
            session_id=battle.id,
            left_at=None
        ).order_by(BattlePlayer.total_points.desc()).all()
        
        return jsonify({
            "battle": _session_to_dict(battle),
            "players": [_player_to_dict(p) for p in active_players]
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting battle info for {code}: {e}")
        return jsonify({"error": "Failed to load battle"}), 500


@battles_bp.route("/<code>/leave", methods=["POST"])
def leave_battle(code):
    """Leave a battle"""
    try:
        battle = BattleSession.query.filter_by(code=code).first()
        if not battle:
            return jsonify({"error": "Battle not found"}), 404
        
        # Find player record
        player_query = BattlePlayer.query.filter_by(
            session_id=battle.id,
            left_at=None
        )
        
        if current_user.is_authenticated:
            player_query = player_query.filter_by(user_id=current_user.id)
        
        player = player_query.first()
        if not player:
            return jsonify({"error": "Not in this battle"}), 404
        
        # Mark as left
        player.left_at = datetime.utcnow()
        db.session.commit()
        
        # Emit Socket.IO events
        from app_socketio import socketio
        socketio.emit("battle:player_left", {
            "name": player.display_name,
            "code": battle.code,
            "player_count": battle.current_players
        }, room=f"battle_{battle.code}")
        
        socketio.emit("battles:refresh", room="battles_lobby")
        
        return jsonify({"ok": True, "message": "Left battle"})
    
    except Exception as e:
        current_app.logger.error(f"Error leaving battle {code}: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to leave battle"}), 500


@battles_bp.route("/my", methods=["GET"])
@login_required
def my_battles():
    """Get battles I've created or joined"""
    try:
        # Battles I created
        created = BattleSession.query.filter_by(created_by=current_user.id).all()
        
        # Battles I joined
        joined_sessions = db.session.query(BattleSession).join(BattlePlayer).filter(
            BattlePlayer.user_id == current_user.id
        ).distinct().all()
        
        return jsonify({
            "created": [_session_to_dict(b) for b in created],
            "joined": [_session_to_dict(b) for b in joined_sessions]
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting user battles: {e}")
        return jsonify({"error": "Failed to load battles"}), 500