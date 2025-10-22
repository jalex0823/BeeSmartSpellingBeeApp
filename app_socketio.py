"""
Battle of the Bees - Socket.IO Integration
Real-time communication for live battles and NewBee alerts
"""
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
from flask import request
import logging

# Initialize Socket.IO
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

logger = logging.getLogger(__name__)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'Connected to BeeSmart Battle System!'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join_battles_lobby')
def join_battles_lobby():
    """Join the battles lobby to receive live battle updates"""
    join_room('battles_lobby')
    logger.info(f"Client {request.sid} joined battles lobby")
    emit('lobby_joined', {'message': 'Joined battles lobby'})


@socketio.on('leave_battles_lobby')
def leave_battles_lobby():
    """Leave the battles lobby"""
    leave_room('battles_lobby')
    logger.info(f"Client {request.sid} left battles lobby")


@socketio.on('join_battle_room')
def join_battle_room(data):
    """Join a specific battle room for real-time updates"""
    try:
        code = data.get('code')
        if not code:
            emit('error', {'message': 'Battle code required'})
            return
        
        room = f"battle_{code}"
        join_room(room)
        logger.info(f"Client {request.sid} joined battle room: {room}")
        emit('battle_room_joined', {'code': code, 'message': f'Joined battle {code}'})
        
        # Notify others in the room
        emit('user_joined_room', {
            'message': f'A new viewer joined the battle',
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)
        
    except Exception as e:
        logger.error(f"Error joining battle room: {e}")
        emit('error', {'message': 'Failed to join battle room'})


@socketio.on('leave_battle_room')
def leave_battle_room(data):
    """Leave a battle room"""
    try:
        code = data.get('code')
        if not code:
            return
        
        room = f"battle_{code}"
        leave_room(room)
        logger.info(f"Client {request.sid} left battle room: {room}")
        emit('battle_room_left', {'code': code})
        
    except Exception as e:
        logger.error(f"Error leaving battle room: {e}")


@socketio.on('battle_message')
def handle_battle_message(data):
    """Handle chat messages in battles"""
    try:
        code = data.get('code')
        message = data.get('message', '').strip()
        username = data.get('username', 'Anonymous')
        
        if not code or not message:
            return
        
        # Limit message length
        message = message[:200]
        
        # Broadcast message to battle room
        emit('battle_message', {
            'username': username,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"battle_{code}")
        
        logger.info(f"Battle message in {code}: {username}: {message}")
        
    except Exception as e:
        logger.error(f"Error handling battle message: {e}")


@socketio.on('battle_answer')
def handle_battle_answer(data):
    """Handle spelling answers in real-time battles"""
    try:
        code = data.get('code')
        answer = data.get('answer', '').strip()
        word_id = data.get('word_id')
        username = data.get('username', 'Anonymous')
        
        if not all([code, answer, word_id]):
            return
        
        # Emit answer attempt to battle room (for live updates)
        emit('battle_answer_attempt', {
            'username': username,
            'word_id': word_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"battle_{code}", include_self=False)
        
        logger.info(f"Battle answer in {code}: {username} answered word {word_id}")
        
    except Exception as e:
        logger.error(f"Error handling battle answer: {e}")


@socketio.on('request_battle_update')
def handle_battle_update_request(data):
    """Client requests current battle status"""
    try:
        code = data.get('code')
        if not code:
            return
        
        # Import here to avoid circular imports
        from models import BattleSession, BattlePlayer
        
        battle = BattleSession.query.filter_by(code=code).first()
        if not battle:
            emit('error', {'message': 'Battle not found'})
            return
        
        # Get current players
        active_players = BattlePlayer.query.filter_by(
            session_id=battle.id,
            left_at=None
        ).order_by(BattlePlayer.total_points.desc()).all()
        
        # Send current battle state
        emit('battle_status_update', {
            'code': code,
            'status': battle.status,
            'current_players': battle.current_players,
            'max_players': battle.max_players,
            'leaderboard': [
                {
                    'name': p.display_name,
                    'points': p.total_points,
                    'accuracy': p.accuracy,
                    'streak': p.current_streak
                } for p in active_players[:10]
            ]
        })
        
    except Exception as e:
        logger.error(f"Error handling battle update request: {e}")
        emit('error', {'message': 'Failed to get battle update'})


# Helper functions for emitting events from API routes
def emit_new_player_alert(battle_code, player_name):
    """Emit NewBee alert when someone joins a battle"""
    socketio.emit('battle:new_player', {
        'name': player_name,
        'code': battle_code,
        'message': f'🐝 NewBee Alert! {player_name} just joined!',
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'battle_{battle_code}')


def emit_battle_refresh():
    """Tell all clients in battles lobby to refresh the battle list"""
    socketio.emit('battles:refresh', {
        'message': 'Battle list updated',
        'timestamp': datetime.utcnow().isoformat()
    }, room='battles_lobby')


def emit_battle_status_change(battle_code, new_status):
    """Notify when battle status changes (waiting -> in_progress -> ended)"""
    socketio.emit('battle:status_change', {
        'code': battle_code,
        'status': new_status,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'battle_{battle_code}')


# Import datetime at the bottom to avoid circular imports
from datetime import datetime