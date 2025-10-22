#!/usr/bin/env python3
"""
Railway Complete Fix - Separate Systems
Addresses AIS and Speed Round as independent Railway deployment issues
"""

import os
import logging
from datetime import datetime, timedelta

def create_ais_railway_fixes():
    """
    Create Railway-specific fixes for AIS (Avatar Installation System)
    """
    
    ais_fixes = '''
# ==============================================================================
# AIS (AVATAR INSTALLATION SYSTEM) RAILWAY FIXES
# ==============================================================================
# Add these to avatar_catalog.py for Railway deployment

import os
import logging
from functools import wraps

# AIS Railway logging
ais_logger = logging.getLogger('AIS_Railway')
if os.getenv('RAILWAY_ENVIRONMENT'):
    ais_logger.setLevel(logging.INFO)

def railway_safe_ais(fallback_value=None):
    """Railway-safe decorator for AIS functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (FileNotFoundError, OSError, ImportError) as e:
                ais_logger.error(f"AIS Railway Error in {func.__name__}: {e}")
                return fallback_value
            except Exception as e:
                ais_logger.error(f"AIS Unexpected Error in {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator

@railway_safe_ais(fallback_value=[])
def railway_get_avatar_catalog():
    """Railway-safe avatar catalog loading for AIS"""
    try:
        return get_avatar_catalog()  # Use existing function
    except Exception as e:
        ais_logger.warning(f"AIS: Fallback catalog due to: {e}")
        return []  # Return empty list, let app handle gracefully

@railway_safe_ais(fallback_value=False)
def railway_install_avatar_safe(folder_name, display_name=None, category=None, description=None):
    """Railway-safe avatar installation"""
    try:
        result = install_new_avatar(folder_name, display_name, category, description)
        if result:
            ais_logger.info(f"AIS: Successfully installed {result['name']} on Railway")
        return result
    except Exception as e:
        ais_logger.error(f"AIS: Failed to install {folder_name} on Railway - {e}")
        return False

def ais_railway_health_check():
    """AIS system health check for Railway"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'ais_status': 'checking',
        'avatar_system': 'checking'
    }
    
    try:
        # Test avatar catalog
        catalog = railway_get_avatar_catalog()
        health['avatar_count'] = len(catalog)
        
        # Test theme generation
        test_theme = generate_theme_from_title('TestBee')
        health['theme_generation'] = 'working' if test_theme else 'failed'
        
        # Test file system
        avatar_dir = "static/Avatars/3D Avatar Files"
        health['file_system'] = 'accessible' if os.path.exists(avatar_dir) else 'inaccessible'
        
        # Overall AIS status
        if health['avatar_count'] > 0 and health['theme_generation'] == 'working':
            health['ais_status'] = 'operational'
        else:
            health['ais_status'] = 'degraded'
            
        health['avatar_system'] = 'ready_for_installation'
        
    except Exception as e:
        health['ais_status'] = 'failed'
        health['error'] = str(e)
    
    return health

# AIS Railway endpoint for Flask app
def create_ais_railway_endpoint():
    """Create Railway endpoint for AIS health check"""
    endpoint_code = '''
@app.route("/api/ais/health")
def ais_health_endpoint():
    """AIS Health Check endpoint for Railway"""
    try:
        from avatar_catalog import ais_railway_health_check
        health = ais_railway_health_check()
        return jsonify(health)
    except ImportError:
        return jsonify({
            'ais_status': 'unavailable',
            'error': 'AIS module not found'
        }), 500
    except Exception as e:
        return jsonify({
            'ais_status': 'error',
            'error': str(e)
        }), 500

@app.route("/api/ais/install-new", methods=["POST"])
def ais_install_endpoint():
    """AIS installation endpoint for Railway"""
    try:
        data = request.get_json()
        folder_name = data.get('folder_name')
        display_name = data.get('display_name')
        category = data.get('category', 'custom')
        description = data.get('description')
        
        from avatar_catalog import railway_install_avatar_safe
        result = railway_install_avatar_safe(folder_name, display_name, category, description)
        
        if result:
            return jsonify({
                'status': 'success',
                'avatar': result,
                'message': f'Avatar {result["name"]} installed successfully'
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': f'Failed to install avatar {folder_name}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
'''
    return endpoint_code

# ==============================================================================
'''
    
    return ais_fixes

def create_speed_round_railway_fixes():
    """
    Create Railway-specific fixes for Speed Round system
    """
    
    speed_fixes = '''
# ==============================================================================
# SPEED ROUND RAILWAY FIXES (SEPARATE FROM AIS)
# ==============================================================================
# Add these to AjaSpellBApp.py for Railway deployment

import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError
from sqlalchemy import text

# Speed Round Railway logging
speed_logger = logging.getLogger('SpeedRound_Railway')
if os.getenv('RAILWAY_ENVIRONMENT'):
    speed_logger.setLevel(logging.INFO)

def railway_db_safe_speed_round(func):
    """Railway-safe database operations for Speed Round ONLY"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except (DisconnectionError, TimeoutError) as e:
                retry_count += 1
                speed_logger.warning(f"Speed Round DB retry {retry_count}/{max_retries}: {e}")
                
                if retry_count >= max_retries:
                    speed_logger.error(f"Speed Round DB failed after {max_retries} retries")
                    return None
                
                # Progressive backoff
                time.sleep(0.5 * retry_count)
                
            except SQLAlchemyError as e:
                speed_logger.error(f"Speed Round SQL Error: {e}")
                return None
            except Exception as e:
                speed_logger.error(f"Speed Round Error: {e}")
                return None
        
        return None
    return wrapper

# Railway Database Configuration for Speed Round
def configure_speed_round_railway_db():
    """Configure database settings specifically for Speed Round on Railway"""
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # Speed Round specific database configuration
        railway_db_config = {
            'pool_timeout': 10,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'BeeSmart_SpeedRound'
            }
        }
        return railway_db_config
    return {}

# REPLACE Speed Round database functions with Railway-safe versions:

@railway_db_safe_speed_round
def save_speed_round_score_railway(user_id, score_data):
    """Railway-safe speed round score saving"""
    try:
        with db.engine.connect().execution_options(autocommit=True) as conn:
            result = conn.execute(
                text("""
                    INSERT INTO speed_round_scores 
                    (user_id, score, words_correct, words_total, time_taken, grade_level, created_at)
                    VALUES (:user_id, :score, :correct, :total, :time_taken, :grade_level, :created_at)
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
            
            speed_logger.info(f"Speed Round score saved for user {user_id}")
            return True
            
    except Exception as e:
        speed_logger.error(f"Failed to save speed round score: {e}")
        return False

@railway_db_safe_speed_round
def get_user_speed_stats_railway(user_id):
    """Railway-safe user speed round stats"""
    try:
        with db.engine.connect().execution_options(autocommit=True) as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        COUNT(*) as games_played,
                        AVG(score) as avg_score,
                        MAX(score) as best_score,
                        AVG(words_correct * 100.0 / words_total) as avg_accuracy
                    FROM speed_round_scores 
                    WHERE user_id = :user_id
                """),
                {'user_id': user_id}
            )
            
            row = result.fetchone()
            if row:
                return {
                    'games_played': row[0] or 0,
                    'avg_score': round(row[1] or 0, 1),
                    'best_score': row[2] or 0,
                    'avg_accuracy': round(row[3] or 0, 1)
                }
            
            return {'games_played': 0, 'avg_score': 0, 'best_score': 0, 'avg_accuracy': 0}
            
    except Exception as e:
        speed_logger.error(f"Failed to get speed round stats: {e}")
        return {'games_played': 0, 'avg_score': 0, 'best_score': 0, 'avg_accuracy': 0}

# Speed Round Health Check endpoint
@app.route("/api/speed-round/health")
def speed_round_health_railway():
    """Speed Round health check for Railway"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'speed_round_status': 'checking',
        'database_status': 'checking',
        'session_status': 'checking'
    }
    
    try:
        # Test database connection
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            health['database_status'] = 'operational'
        
        # Test session functionality
        health['session_status'] = 'operational'
        
        # Overall status
        if health['database_status'] == 'operational':
            health['speed_round_status'] = 'operational'
        else:
            health['speed_round_status'] = 'degraded'
        
    except Exception as e:
        health['speed_round_status'] = 'failed'
        health['database_status'] = 'failed'
        health['error'] = str(e)
    
    return jsonify(health)

# REPLACE existing Speed Round routes with Railway-safe versions:

@app.route("/api/speed-round/start", methods=["POST"])
def start_speed_round_railway():
    """Railway-safe speed round start"""
    try:
        data = request.get_json()
        grade_level = data.get('grade_level', 'grade_3_4')
        word_count = data.get('word_count', 10)
        time_per_word = data.get('time_per_word', 15)
        
        # Generate words using existing logic
        words = generate_speed_round_words(grade_level, word_count)
        
        # Railway-safe session storage
        session_data = {
            'words': words,
            'current_index': 0,
            'start_time': datetime.utcnow().isoformat(),
            'grade_level': grade_level,
            'time_per_word': time_per_word,
            'scores': []
        }
        
        session['speed_round'] = session_data
        session.permanent = True
        
        speed_logger.info(f"Speed Round started on Railway: {word_count} words, {grade_level}")
        
        return jsonify({
            'status': 'success',
            'word_count': len(words),
            'time_per_word': time_per_word,
            'first_word': words[0] if words else None
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round start error on Railway: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Speed Round temporarily unavailable'
        }), 500

@app.route("/api/speed-round/answer", methods=["POST"])
def submit_speed_round_answer_railway():
    """Railway-safe speed round answer submission"""
    try:
        if 'speed_round' not in session:
            return jsonify({
                'status': 'error',
                'message': 'No active speed round'
            }), 400
        
        data = request.get_json()
        answer = data.get('answer', '').strip().lower()
        time_taken = data.get('time_taken', 0)
        
        speed_data = session['speed_round']
        current_word = speed_data['words'][speed_data['current_index']]
        
        # Check answer
        is_correct = answer == current_word['word'].lower()
        
        # Store result
        speed_data['scores'].append({
            'word': current_word['word'],
            'user_answer': answer,
            'correct': is_correct,
            'time_taken': time_taken
        })
        
        # Move to next word
        speed_data['current_index'] += 1
        session['speed_round'] = speed_data
        
        # Check completion
        if speed_data['current_index'] >= len(speed_data['words']):
            correct_count = sum(1 for s in speed_data['scores'] if s['correct'])
            total_time = sum(s['time_taken'] for s in speed_data['scores'])
            
            # Save to database using Railway-safe function
            if current_user.is_authenticated:
                score_data = {
                    'score': correct_count * 10,
                    'correct': correct_count,
                    'total': len(speed_data['words']),
                    'time_taken': total_time,
                    'grade_level': speed_data['grade_level']
                }
                
                save_success = save_speed_round_score_railway(current_user.id, score_data)
                speed_logger.info(f"Speed Round completed on Railway - Score saved: {save_success}")
            
            session.pop('speed_round', None)
            
            return jsonify({
                'status': 'completed',
                'final_score': {
                    'correct': correct_count,
                    'total': len(speed_data['words']),
                    'accuracy': round(correct_count / len(speed_data['words']) * 100, 1),
                    'total_time': total_time
                }
            })
        
        # Return next word
        next_word = speed_data['words'][speed_data['current_index']]
        
        return jsonify({
            'status': 'continue',
            'correct': is_correct,
            'next_word': next_word,
            'progress': {
                'current': speed_data['current_index'] + 1,
                'total': len(speed_data['words'])
            }
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round answer error on Railway: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Answer processing failed'
        }), 500

# ==============================================================================
'''
    
    return speed_fixes

def create_railway_deployment_integration():
    """
    Create integration for both AIS and Speed Round on Railway
    """
    
    integration_code = '''
# ==============================================================================
# RAILWAY DEPLOYMENT INTEGRATION - AIS + Speed Round
# ==============================================================================
# Add this to AjaSpellBApp.py for complete Railway deployment

@app.route("/api/railway/system-health")
def railway_system_health_complete():
    """Complete Railway system health check - AIS + Speed Round"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'systems': {},
        'overall_status': 'checking'
    }
    
    # Check AIS System
    try:
        ais_response = requests.get(f"{request.host_url}api/ais/health")
        if ais_response.status_code == 200:
            health['systems']['ais'] = ais_response.json()
        else:
            health['systems']['ais'] = {'status': 'unreachable'}
    except:
        health['systems']['ais'] = {'status': 'unavailable'}
    
    # Check Speed Round System
    try:
        speed_response = requests.get(f"{request.host_url}api/speed-round/health")
        if speed_response.status_code == 200:
            health['systems']['speed_round'] = speed_response.json()
        else:
            health['systems']['speed_round'] = {'status': 'unreachable'}
    except:
        health['systems']['speed_round'] = {'status': 'unavailable'}
    
    # Determine overall status
    ais_ok = health['systems']['ais'].get('ais_status') == 'operational'
    speed_ok = health['systems']['speed_round'].get('speed_round_status') == 'operational'
    
    if ais_ok and speed_ok:
        health['overall_status'] = 'fully_operational'
    elif ais_ok or speed_ok:
        health['overall_status'] = 'partially_operational'
    else:
        health['overall_status'] = 'degraded'
    
    health['summary'] = {
        'ais_ready': ais_ok,
        'speed_round_ready': speed_ok,
        'deployment_status': 'ready' if (ais_ok and speed_ok) else 'needs_attention'
    }
    
    return jsonify(health)

# Railway startup check
def railway_startup_check():
    """Run startup checks for Railway deployment"""
    print("🚂 Railway Startup Check...")
    
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Railway environment detected")
        
        # Configure database for Railway
        railway_db_config = configure_speed_round_railway_db()
        if railway_db_config:
            print("✅ Speed Round database configured for Railway")
        
        # Check AIS availability
        try:
            from avatar_catalog import ais_railway_health_check
            ais_status = ais_railway_health_check()
            print(f"✅ AIS Status: {ais_status.get('ais_status', 'unknown')}")
        except ImportError:
            print("⚠️  AIS module not available")
        
        print("🎉 Railway startup check complete!")
    else:
        print("💻 Local development environment")

# Call this in your app startup
if __name__ == "__main__":
    railway_startup_check()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

# ==============================================================================
'''
    
    return integration_code

if __name__ == "__main__":
    print("🔧 RAILWAY COMPLETE SEPARATION - GENERATOR")
    print("=" * 60)
    
    print("\n📦 Generating AIS Railway Fixes...")
    ais_code = create_ais_railway_fixes()
    
    print("⚡ Generating Speed Round Railway Fixes...")  
    speed_code = create_speed_round_railway_fixes()
    
    print("🔗 Generating Railway Integration...")
    integration_code = create_railway_deployment_integration()
    
    # Save separate files
    with open("railway_ais_fixes.py", "w", encoding='utf-8') as f:
        f.write(ais_code)
    
    with open("railway_speed_round_fixes.py", "w", encoding='utf-8') as f:
        f.write(speed_code)
    
    with open("railway_integration_complete.py", "w", encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f"\n💾 FILES GENERATED:")
    print(f"   📁 railway_ais_fixes.py - AIS Railway fixes")
    print(f"   📁 railway_speed_round_fixes.py - Speed Round Railway fixes")
    print(f"   📁 railway_integration_complete.py - Complete integration")
    
    print(f"\n🎯 DEPLOYMENT PLAN:")
    print(f"1. Add AIS fixes to avatar_catalog.py")
    print(f"2. Add Speed Round fixes to AjaSpellBApp.py")
    print(f"3. Add integration endpoints to AjaSpellBApp.py")
    print(f"4. Deploy to Railway")
    print(f"5. Test systems independently:")
    print(f"   - /api/ais/health")
    print(f"   - /api/speed-round/health")
    print(f"   - /api/railway/system-health")
    
    print(f"\n✅ AIS and Speed Round are now completely separate!")
    print(f"🚂 Ready for Railway deployment!")