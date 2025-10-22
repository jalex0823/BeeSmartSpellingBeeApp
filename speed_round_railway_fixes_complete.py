
# ==============================================================================
# SPEED ROUND RAILWAY FIXES - Add to AjaSpellBApp.py
# ==============================================================================

import os
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError, OperationalError
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Speed Round Railway logging
speed_logger = logging.getLogger('SpeedRound_Railway')
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    speed_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - SpeedRound - %(levelname)s - %(message)s'))
    speed_logger.addHandler(handler)

def railway_db_safe_speed_round(max_retries=3, backoff_factor=0.5):
    """
    Railway-safe database decorator for Speed Round operations
    Handles connection timeouts, recycling, and rollbacks
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Use fresh connection with shorter timeout
                    result = func(*args, **kwargs)
                    speed_logger.info(f"Speed Round DB operation successful: {func.__name__}")
                    return result
                    
                except (DisconnectionError, TimeoutError, OperationalError) as e:
                    retry_count += 1
                    wait_time = backoff_factor * (2 ** retry_count)
                    
                    speed_logger.warning(
                        f"Speed Round DB retry {retry_count}/{max_retries} for {func.__name__}: {e}"
                    )
                    
                    if retry_count >= max_retries:
                        speed_logger.error(
                            f"Speed Round DB failed after {max_retries} retries: {func.__name__}"
                        )
                        return None
                    
                    # Progressive backoff
                    time.sleep(wait_time)
                    
                except SQLAlchemyError as e:
                    speed_logger.error(f"Speed Round SQL Error in {func.__name__}: {e}")
                    return None
                    
                except Exception as e:
                    speed_logger.error(f"Speed Round Unexpected Error in {func.__name__}: {e}")
                    return None
            
            return None
        return wrapper
    return decorator

# Railway-specific database configuration for Speed Round
def get_railway_speed_round_engine_options():
    """Get Railway-optimized engine options for Speed Round"""
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
        return {
            'pool_timeout': 5,          # Shorter timeout for Railway
            'pool_recycle': 300,        # 5 minutes
            'pool_pre_ping': True,      # Test connections
            'pool_size': 3,             # Smaller pool for Speed Round
            'max_overflow': 2,          # Limited overflow
            'connect_args': {
                'connect_timeout': 5,
                'application_name': 'BeeSmart_SpeedRound',
                'options': '-c statement_timeout=10000'  # 10 second query timeout
            }
        }
    return {}

# REPLACE your existing Speed Round database functions with these Railway-safe versions:

@railway_db_safe_speed_round()
def save_speed_round_score_railway(user_id, score_data):
    """
    Railway-safe speed round score saving with connection management
    """
    try:
        # Use direct SQL with explicit transaction management
        engine = db.get_engine()
        
        with engine.begin() as conn:  # Auto-commit transaction
            result = conn.execute(
                text("""
                    INSERT INTO speed_round_scores 
                    (user_id, score, words_correct, words_total, time_taken, grade_level, created_at)
                    VALUES (:user_id, :score, :correct, :total, :time_taken, :grade_level, :created_at)
                    RETURNING id
                """),
                {
                    'user_id': user_id,
                    'score': score_data.get('score', 0),
                    'correct': score_data.get('correct', 0),
                    'total': score_data.get('total', 0),
                    'time_taken': score_data.get('time_taken', 0),
                    'grade_level': score_data.get('grade_level', 'unknown'),
                    'created_at': datetime.utcnow()
                }
            )
            
            score_id = result.fetchone()[0]
            speed_logger.info(f"Speed Round score saved: user_id={user_id}, score_id={score_id}")
            return score_id
            
    except Exception as e:
        speed_logger.error(f"Failed to save speed round score: {e}")
        return None

@railway_db_safe_speed_round()
def get_user_speed_stats_railway(user_id):
    """
    Railway-safe user speed round statistics retrieval
    """
    try:
        engine = db.get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        COUNT(*) as games_played,
                        COALESCE(AVG(score), 0) as avg_score,
                        COALESCE(MAX(score), 0) as best_score,
                        COALESCE(AVG(CASE 
                            WHEN words_total > 0 
                            THEN (words_correct * 100.0 / words_total) 
                            ELSE 0 
                        END), 0) as avg_accuracy
                    FROM speed_round_scores 
                    WHERE user_id = :user_id
                """),
                {'user_id': user_id}
            )
            
            row = result.fetchone()
            if row:
                stats = {
                    'games_played': int(row[0]),
                    'avg_score': round(float(row[1]), 1),
                    'best_score': int(row[2]),
                    'avg_accuracy': round(float(row[3]), 1)
                }
                
                speed_logger.info(f"Speed Round stats retrieved: user_id={user_id}")
                return stats
            
            return {'games_played': 0, 'avg_score': 0, 'best_score': 0, 'avg_accuracy': 0}
            
    except Exception as e:
        speed_logger.error(f"Failed to get speed round stats: {e}")
        return {'games_played': 0, 'avg_score': 0, 'best_score': 0, 'avg_accuracy': 0}

@railway_db_safe_speed_round()
def get_speed_round_leaderboard_railway(limit=10):
    """
    Railway-safe speed round leaderboard retrieval
    """
    try:
        engine = db.get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        u.display_name, 
                        u.username,
                        s.score,
                        s.words_correct,
                        s.words_total,
                        s.time_taken,
                        s.created_at
                    FROM speed_round_scores s
                    JOIN users u ON s.user_id = u.id
                    ORDER BY s.score DESC, s.time_taken ASC
                    LIMIT :limit
                """),
                {'limit': limit}
            )
            
            leaderboard = []
            for row in result:
                leaderboard.append({
                    'display_name': row[0],
                    'username': row[1],
                    'score': row[2],
                    'words_correct': row[3],
                    'words_total': row[4],
                    'time_taken': row[5],
                    'created_at': row[6]
                })
            
            speed_logger.info(f"Speed Round leaderboard retrieved: {len(leaderboard)} entries")
            return leaderboard
            
    except Exception as e:
        speed_logger.error(f"Failed to get speed round leaderboard: {e}")
        return []

# REPLACE your existing Speed Round API routes with these Railway-safe versions:

@app.route("/api/speed-round/start", methods=["POST"])
def start_speed_round_railway():
    """Railway-safe speed round start with improved session management"""
    try:
        data = request.get_json() or {}
        grade_level = data.get('grade_level', 'grade_3_4')
        word_count = min(int(data.get('word_count', 10)), 20)  # Limit to 20 words max
        time_per_word = max(int(data.get('time_per_word', 15)), 5)  # Minimum 5 seconds
        
        # Generate words using existing word generation logic
        words = generate_speed_round_words(grade_level, word_count)
        
        if not words:
            speed_logger.error(f"Failed to generate words for grade_level: {grade_level}")
            return jsonify({
                'status': 'error',
                'message': 'Unable to generate word list'
            }), 500
        
        # Railway-safe session storage with reduced data
        session_data = {
            'words': words[:word_count],  # Ensure exact count
            'current_index': 0,
            'start_time': datetime.utcnow().isoformat(),
            'grade_level': grade_level,
            'time_per_word': time_per_word,
            'correct_count': 0,
            'total_time': 0
        }
        
        # Clear any existing speed round session
        session.pop('speed_round', None)
        session['speed_round'] = session_data
        session.permanent = True
        
        speed_logger.info(
            f"Speed Round started - user_id: {current_user.id if current_user.is_authenticated else 'anonymous'}, "
            f"words: {len(words)}, grade: {grade_level}, time_per_word: {time_per_word}s"
        )
        
        return jsonify({
            'status': 'success',
            'session_id': session.get('session_id'),
            'word_count': len(words),
            'time_per_word': time_per_word,
            'grade_level': grade_level,
            'first_word': words[0] if words else None
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round start error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to start Speed Round'
        }), 500

@app.route("/api/speed-round/answer", methods=["POST"])
def submit_speed_round_answer_railway():
    """Railway-safe speed round answer submission with optimized database operations"""
    try:
        if 'speed_round' not in session:
            return jsonify({
                'status': 'error',
                'message': 'No active Speed Round session'
            }), 400
        
        data = request.get_json() or {}
        answer = (data.get('answer', '') or '').strip().lower()
        time_taken = max(float(data.get('time_taken', 0)), 0)
        
        speed_data = session['speed_round']
        current_index = speed_data.get('current_index', 0)
        
        if current_index >= len(speed_data['words']):
            return jsonify({
                'status': 'error',
                'message': 'Speed Round already completed'
            }), 400
        
        current_word = speed_data['words'][current_index]
        correct_answer = current_word['word'].lower().strip()
        
        # Check answer
        is_correct = answer == correct_answer
        
        # Update session data efficiently
        if is_correct:
            speed_data['correct_count'] = speed_data.get('correct_count', 0) + 1
        
        speed_data['total_time'] = speed_data.get('total_time', 0) + time_taken
        speed_data['current_index'] = current_index + 1
        
        session['speed_round'] = speed_data
        
        # Check if round completed
        if speed_data['current_index'] >= len(speed_data['words']):
            # Calculate final results
            correct_count = speed_data.get('correct_count', 0)
            total_words = len(speed_data['words'])
            total_time = speed_data.get('total_time', 0)
            final_score = correct_count * 10  # 10 points per correct answer
            
            # Save to database only if user is authenticated
            save_success = False
            if current_user.is_authenticated:
                score_data = {
                    'score': final_score,
                    'correct': correct_count,
                    'total': total_words,
                    'time_taken': total_time,
                    'grade_level': speed_data.get('grade_level', 'unknown')
                }
                
                score_id = save_speed_round_score_railway(current_user.id, score_data)
                save_success = score_id is not None
                
                speed_logger.info(
                    f"Speed Round completed - user_id: {current_user.id}, "
                    f"score: {final_score}, correct: {correct_count}/{total_words}, "
                    f"time: {total_time:.1f}s, saved: {save_success}"
                )
            
            # Clear session
            session.pop('speed_round', None)
            
            return jsonify({
                'status': 'completed',
                'final_score': {
                    'score': final_score,
                    'correct': correct_count,
                    'total': total_words,
                    'accuracy': round((correct_count / total_words) * 100, 1) if total_words > 0 else 0,
                    'total_time': round(total_time, 1),
                    'average_time_per_word': round(total_time / total_words, 1) if total_words > 0 else 0
                },
                'saved_to_database': save_success
            })
        
        # Continue to next word
        next_word_index = speed_data['current_index']
        next_word = speed_data['words'][next_word_index] if next_word_index < len(speed_data['words']) else None
        
        return jsonify({
            'status': 'continue',
            'correct': is_correct,
            'correct_answer': correct_answer,
            'next_word': next_word,
            'progress': {
                'current': speed_data['current_index'],
                'total': len(speed_data['words']),
                'correct_so_far': speed_data.get('correct_count', 0)
            }
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round answer error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to process answer'
        }), 500

@app.route("/api/speed-round/stats")
def get_speed_round_stats_railway():
    """Railway-safe speed round statistics endpoint"""
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        stats = get_user_speed_stats_railway(current_user.id)
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round stats error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve statistics'
        }), 500

@app.route("/api/speed-round/leaderboard")
def get_speed_round_leaderboard_railway():
    """Railway-safe speed round leaderboard endpoint"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 entries
        leaderboard = get_speed_round_leaderboard_railway(limit)
        
        return jsonify({
            'status': 'success',
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round leaderboard error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve leaderboard'
        }), 500

@app.route("/api/speed-round/health")
def speed_round_health_railway():
    """Speed Round system health check for Railway"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'Railway' if (os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL')) else 'Local',
        'speed_round_status': 'checking',
        'database_status': 'checking',
        'session_status': 'checking'
    }
    
    try:
        # Test database connection with timeout
        engine = db.get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                health['database_status'] = 'operational'
            else:
                health['database_status'] = 'degraded'
        
        # Test session functionality
        health['session_status'] = 'operational'
        
        # Test Speed Round table access
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM speed_round_scores LIMIT 1"))
                health['speed_round_table'] = 'accessible'
        except:
            health['speed_round_table'] = 'inaccessible'
        
        # Overall status
        if (health['database_status'] == 'operational' and 
            health['session_status'] == 'operational' and
            health['speed_round_table'] == 'accessible'):
            health['speed_round_status'] = 'operational'
        else:
            health['speed_round_status'] = 'degraded'
        
        speed_logger.info(f"Speed Round health check: {health['speed_round_status']}")
        
    except Exception as e:
        health['speed_round_status'] = 'failed'
        health['database_status'] = 'failed'
        health['error'] = str(e)
        speed_logger.error(f"Speed Round health check failed: {e}")
    
    return jsonify(health)

# Add this to your app configuration for Railway optimization
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    # Configure Flask session for Railway
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Update SQLAlchemy configuration for Railway Speed Round optimization
    railway_engine_options = get_railway_speed_round_engine_options()
    if railway_engine_options and hasattr(app.config, 'SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'].update(railway_engine_options)

# ==============================================================================
# END OF SPEED ROUND RAILWAY FIXES
# ==============================================================================
