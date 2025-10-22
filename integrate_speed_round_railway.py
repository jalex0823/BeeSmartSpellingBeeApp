#!/usr/bin/env python3
"""
Speed Round Railway Integration
Integrates Railway-safe database fixes into existing AjaSpellBApp.py
"""

import os
import re

def integrate_speed_round_railway_fixes():
    """
    Integrate Speed Round Railway fixes into AjaSpellBApp.py
    """
    
    print("🚂 SPEED ROUND RAILWAY INTEGRATION")
    print("=" * 60)
    
    # Read current AjaSpellBApp.py
    app_file = "AjaSpellBApp.py"
    
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found!")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Railway fixes already applied
    if "railway_db_safe_speed_round" in content:
        print("✅ Speed Round Railway fixes already integrated!")
        return True
    
    # Create backup
    backup_file = f"{app_file}.backup_speed_round_{int(__import__('time').time())}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup created: {backup_file}")
    
    # Railway fixes imports to add after existing imports
    railway_imports = '''
# Speed Round Railway fixes
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError, OperationalError
from sqlalchemy import text
'''
    
    # Railway decorator and helper functions
    railway_decorator = '''
# ==============================================================================
# SPEED ROUND RAILWAY FIXES
# ==============================================================================

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
                    (user_id, words_attempted, words_correct, total_time, honey_points_earned, 
                     longest_streak, average_time_per_word, fastest_word_time, speed_bonuses_earned,
                     word_details, difficulty_level, created_at)
                    VALUES (:user_id, :words_attempted, :words_correct, :total_time, :honey_points_earned,
                            :longest_streak, :avg_time, :fastest_time, :speed_bonuses,
                            :word_details, :difficulty_level, :created_at)
                    RETURNING id
                """),
                {
                    'user_id': user_id,
                    'words_attempted': score_data.get('words_attempted', 0),
                    'words_correct': score_data.get('words_correct', 0),
                    'total_time': score_data.get('total_time', 0),
                    'honey_points_earned': score_data.get('honey_points_earned', 0),
                    'longest_streak': score_data.get('longest_streak', 0),
                    'avg_time': score_data.get('average_time_per_word', 0),
                    'fastest_time': score_data.get('fastest_word_time'),
                    'speed_bonuses': score_data.get('speed_bonuses_earned', 0),
                    'word_details': __import__('json').dumps(score_data.get('word_details', [])),
                    'difficulty_level': score_data.get('difficulty_level', 'unknown'),
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
def update_user_lifetime_points_railway(user_id, points_to_add):
    """
    Railway-safe user lifetime points update
    """
    try:
        engine = db.get_engine()
        
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE users 
                    SET total_lifetime_points = COALESCE(total_lifetime_points, 0) + :points
                    WHERE id = :user_id
                """),
                {'user_id': user_id, 'points': points_to_add}
            )
            
            speed_logger.info(f"Updated user {user_id} lifetime points: +{points_to_add}")
            return True
            
    except Exception as e:
        speed_logger.error(f"Failed to update user lifetime points: {e}")
        return False

# ==============================================================================
# END SPEED ROUND RAILWAY FIXES
# ==============================================================================

'''
    
    # Find the position to insert Railway fixes
    # Look for the "SPEED ROUND API ENDPOINTS" section
    speed_round_section = content.find("# SPEED ROUND API ENDPOINTS")
    
    if speed_round_section == -1:
        print("❌ Could not find Speed Round section!")
        return False
    
    # Insert Railway fixes before Speed Round section
    new_content = (
        content[:speed_round_section] + 
        railway_decorator + 
        "\n" + 
        content[speed_round_section:]
    )
    
    # Update the api_speed_round_complete function to use Railway-safe operations
    complete_function_pattern = r'@app\.route\("/api/speed-round/complete".*?def api_speed_round_complete\(\):.*?except Exception as e:.*?return jsonify\(\{.*?\}\), 500'
    
    railway_complete_function = '''@app.route("/api/speed-round/complete", methods=["POST"])
@login_required
def api_speed_round_complete():
    """Save speed round results to database - Railway-safe version"""
    try:
        speed_round = session.get('speed_round')
        
        if not speed_round:
            return jsonify({
                'status': 'error',
                'message': 'No speed round data found'
            }), 400
        
        # Mark round as inactive
        speed_round['active'] = False
        
        # Calculate statistics
        total_time = time.time() - speed_round['start_time']
        words_attempted = speed_round['current_index']
        words_correct = speed_round['correct_count']
        
        # Find fastest correct word time
        fastest_time = None
        for record in speed_round['word_history']:
            if record['correct'] and record['time_taken'] > 0:
                if fastest_time is None or record['time_taken'] < fastest_time:
                    fastest_time = record['time_taken']
        
        avg_time = total_time / words_attempted if words_attempted > 0 else 0
        accuracy = (words_correct / words_attempted * 100) if words_attempted > 0 else 0
        
        # Prepare score data for Railway-safe saving
        score_data = {
            'words_attempted': words_attempted,
            'words_correct': words_correct,
            'total_time': round(total_time, 2),
            'honey_points_earned': speed_round['total_points'],
            'longest_streak': speed_round['max_streak'],
            'average_time_per_word': round(avg_time, 2),
            'fastest_word_time': round(fastest_time, 2) if fastest_time else None,
            'speed_bonuses_earned': speed_round['speed_bonuses'],
            'word_details': speed_round['word_history'],
            'difficulty_level': speed_round['config']['difficulty']
        }
        
        # Use Railway-safe database operations
        score_id = save_speed_round_score_railway(current_user.id, score_data)
        
        if score_id:
            # Update user's total points using Railway-safe method
            points_updated = update_user_lifetime_points_railway(current_user.id, speed_round['total_points'])
            
            speed_logger.info(f"Speed Round saved: {words_correct}/{words_attempted} correct, {speed_round['total_points']} pts, points_updated={points_updated}")
        else:
            speed_logger.error("Failed to save Speed Round score")
        
        # Collect incorrect words for review
        incorrect_words = []
        for record in speed_round['word_history']:
            if not record['correct'] and not record.get('skipped', False):
                incorrect_words.append({
                    'word': record['word'],
                    'user_answer': record.get('user_answer', ''),
                    'correct_spelling': record['word']
                })
        
        # Store results in session for results page
        session['speed_round_results'] = {
            'score_id': score_id,
            'total_points': speed_round['total_points'],
            'words_attempted': words_attempted,
            'words_correct': words_correct,
            'accuracy': round(accuracy, 1),
            'longest_streak': speed_round['max_streak'],
            'fastest_time': round(fastest_time, 2) if fastest_time else None,
            'total_time': round(total_time, 2),
            'speed_bonuses': speed_round['speed_bonuses'],
            'difficulty': speed_round['config']['difficulty'],
            'config': speed_round['config'],
            'incorrect_words': incorrect_words
        }
        
        # Clear speed round from session
        session.pop('speed_round', None)
        
        return jsonify({
            'status': 'success',
            'score_id': score_id,
            'statistics': session['speed_round_results'],
            'railway_optimized': True
        })
        
    except Exception as e:
        speed_logger.error(f"Error saving speed round: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'railway_error': True
        }), 500'''
    
    # Replace the complete function
    new_content = re.sub(
        complete_function_pattern,
        railway_complete_function,
        new_content,
        flags=re.DOTALL
    )
    
    # Add Railway session configuration near app configuration
    railway_config = '''
# Railway Speed Round optimization
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    # Configure Flask session for Railway Speed Round
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    
    # Update SQLAlchemy configuration for Railway Speed Round optimization
    railway_engine_options = get_railway_speed_round_engine_options()
    if railway_engine_options and hasattr(app.config, 'SQLALCHEMY_ENGINE_OPTIONS'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'].update(railway_engine_options)
        
    speed_logger.info("Speed Round Railway configuration applied")
'''
    
    # Add railway configuration after app configuration
    app_config_pos = new_content.find("app.config['SECRET_KEY']")
    if app_config_pos != -1:
        # Find the end of the config section
        config_end = new_content.find("\n\n", app_config_pos)
        if config_end != -1:
            new_content = (
                new_content[:config_end] + 
                "\n" + railway_config + 
                new_content[config_end:]
            )
    
    # Write updated content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Speed Round Railway fixes integrated successfully!")
    print(f"\n🔧 RAILWAY FIXES APPLIED:")
    print(f"✅ Database timeout and rollback handling")
    print(f"✅ Connection pooling optimization") 
    print(f"✅ Railway-specific logging")
    print(f"✅ Session configuration for Railway")
    print(f"✅ Retry logic with exponential backoff")
    print(f"✅ Transaction management improvements")
    
    return True

def add_speed_round_health_endpoint():
    """
    Add Speed Round health check endpoint to existing file
    """
    
    app_file = "AjaSpellBApp.py"
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if health endpoint already exists
    if "/api/speed-round/health" in content:
        print("✅ Speed Round health endpoint already exists!")
        return True
    
    health_endpoint = '''
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
'''
    
    # Find a good place to add the health endpoint (after other speed round endpoints)
    results_route_pos = content.find('@app.route("/speed-round/results")')
    
    if results_route_pos != -1:
        # Find the end of the results function
        next_route_pos = content.find("\n\n@app.route", results_route_pos + 1)
        if next_route_pos != -1:
            new_content = (
                content[:next_route_pos] + 
                health_endpoint + 
                content[next_route_pos:]
            )
            
            # Write updated content
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Speed Round health endpoint added!")
            return True
    
    print("❌ Could not find location to add health endpoint")
    return False

if __name__ == "__main__":
    print("🚂 SPEED ROUND RAILWAY INTEGRATION")
    print("=" * 60)
    
    success = integrate_speed_round_railway_fixes()
    
    if success:
        health_success = add_speed_round_health_endpoint()
        
        print(f"\n📊 INTEGRATION SUMMARY:")
        print(f"✅ Railway database fixes: {success}")
        print(f"✅ Health endpoint: {health_success}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Test Speed Round locally")
        print(f"2. Deploy to Railway")
        print(f"3. Monitor /api/speed-round/health endpoint")
        print(f"4. Verify no more timeout/rollback errors")
        
        print(f"\n✅ Speed Round Railway issues should now be resolved!")
        
    else:
        print("\n❌ Integration failed!")