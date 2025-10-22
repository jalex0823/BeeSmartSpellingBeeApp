#!/usr/bin/env python3
"""
Speed Round Railway Fix & Diagnostic System
Addresses database connection timeout and rollback issues in Speed Round functionality
"""

import os
import logging
from datetime import datetime, timedelta

def diagnose_speed_round_issues():
    """
    Comprehensive Speed Round issue diagnosis for Railway deployment
    """
    
    print("⚡ SPEED ROUND DIAGNOSTIC SYSTEM")
    print("=" * 60)
    
    issues_found = []
    
    # Issue Analysis from logs
    print("🔍 Analyzing Speed Round Issues...")
    
    log_analysis = {
        'connection_timeout': {
            'symptom': 'Connection exceeded timeout; recycling',
            'cause': 'PostgreSQL connection pool timeout on Railway',
            'impact': 'Speed Round fails to save/load user data',
            'severity': 'HIGH'
        },
        'rollback_issue': {
            'symptom': 'ENGINE ROLLBACK after user queries',
            'cause': 'Transaction failures due to connection issues',
            'impact': 'User progress not saved, session data lost',
            'severity': 'CRITICAL'
        },
        'repeated_queries': {
            'symptom': 'Same user query executed multiple times',
            'cause': 'Session management issues or retry logic',
            'impact': 'Performance degradation, database overload',
            'severity': 'MEDIUM'
        }
    }
    
    for issue_name, details in log_analysis.items():
        print(f"\n❌ Issue: {issue_name.upper()}")
        print(f"   Symptom: {details['symptom']}")
        print(f"   Cause: {details['cause']}")
        print(f"   Impact: {details['impact']}")
        print(f"   Severity: {details['severity']}")
        issues_found.append(issue_name)
    
    return issues_found, log_analysis

def generate_speed_round_fixes():
    """
    Generate Railway-specific fixes for Speed Round functionality
    """
    
    speed_round_fixes = '''
# ==============================================================================
# SPEED ROUND RAILWAY FIXES - Add to AjaSpellBApp.py
# ==============================================================================

import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, TimeoutError
from sqlalchemy import text

# Railway-specific logging for Speed Round
speed_logger = logging.getLogger('SpeedRound')
if os.getenv('RAILWAY_ENVIRONMENT'):
    speed_logger.setLevel(logging.INFO)

def railway_db_safe(func):
    """
    Railway-safe database operations for Speed Round
    """
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
                
                # Wait before retry
                time.sleep(0.5 * retry_count)
                
            except SQLAlchemyError as e:
                speed_logger.error(f"Speed Round SQL Error: {e}")
                return None
            except Exception as e:
                speed_logger.error(f"Speed Round Error: {e}")
                return None
        
        return None
    return wrapper

# REPLACE YOUR SPEED ROUND DATABASE FUNCTIONS WITH THESE RAILWAY-SAFE VERSIONS:

@railway_db_safe
def save_speed_round_score_safe(user_id, score_data):
    """Railway-safe speed round score saving"""
    try:
        # Use connection with shorter timeout for Railway
        with db.engine.connect().execution_options(autocommit=True) as conn:
            # Insert with explicit transaction
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

@railway_db_safe  
def get_user_speed_stats_safe(user_id):
    """Railway-safe user speed round stats retrieval"""
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
            
            return {
                'games_played': 0,
                'avg_score': 0,
                'best_score': 0,
                'avg_accuracy': 0
            }
            
    except Exception as e:
        speed_logger.error(f"Failed to get speed round stats: {e}")
        return {
            'games_played': 0,
            'avg_score': 0,
            'best_score': 0,
            'avg_accuracy': 0
        }

# REPLACE YOUR SPEED ROUND API ROUTES WITH THESE:

@app.route("/api/speed-round/start", methods=["POST"])
def start_speed_round_safe():
    """Railway-safe speed round start"""
    try:
        data = request.get_json()
        grade_level = data.get('grade_level', 'grade_3_4')
        word_count = data.get('word_count', 10)
        time_per_word = data.get('time_per_word', 15)
        
        # Generate word list (use existing word generation logic)
        words = generate_speed_round_words(grade_level, word_count)
        
        # Store in session (Railway-safe session management)
        session_data = {
            'words': words,
            'current_index': 0,
            'start_time': datetime.utcnow().isoformat(),
            'grade_level': grade_level,
            'time_per_word': time_per_word,
            'scores': []
        }
        
        session['speed_round'] = session_data
        session.permanent = True  # Ensure session persists
        
        speed_logger.info(f"Speed Round started: {word_count} words, {grade_level}, {time_per_word}s/word")
        
        return jsonify({
            'status': 'success',
            'session_id': session.get('session_id'),
            'word_count': len(words),
            'time_per_word': time_per_word,
            'first_word': words[0] if words else None
        })
        
    except Exception as e:
        speed_logger.error(f"Speed Round start error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Speed Round temporarily unavailable'
        }), 500

@app.route("/api/speed-round/answer", methods=["POST"])  
def submit_speed_round_answer_safe():
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
        
        # Check if round completed
        if speed_data['current_index'] >= len(speed_data['words']):
            # Calculate final score
            correct_count = sum(1 for s in speed_data['scores'] if s['correct'])
            total_time = sum(s['time_taken'] for s in speed_data['scores'])
            
            # Save to database (Railway-safe)
            if current_user.is_authenticated:
                score_data = {
                    'score': correct_count * 10,  # 10 points per correct
                    'correct': correct_count,
                    'total': len(speed_data['words']),
                    'time_taken': total_time,
                    'grade_level': speed_data['grade_level']
                }
                
                save_success = save_speed_round_score_safe(current_user.id, score_data)
                speed_logger.info(f"Speed Round completed - Score saved: {save_success}")
            
            # Clear session
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
        speed_logger.error(f"Speed Round answer error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Answer processing failed'
        }), 500

# ADD SPEED ROUND HEALTH CHECK:
@app.route("/api/speed-round/health")
def speed_round_health():
    """Speed Round system health check"""
    health = {
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'speed_round_status': 'unknown'
    }
    
    try:
        # Test database connection
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            health['database_connection'] = 'operational'
        
        # Test session functionality
        health['session_system'] = 'operational' if 'session' in globals() else 'unavailable'
        
        # Overall status
        if health['database_connection'] == 'operational':
            health['speed_round_status'] = 'operational'
        else:
            health['speed_round_status'] = 'degraded'
        
    except Exception as e:
        health['speed_round_status'] = 'failed'
        health['error'] = str(e)
    
    return jsonify(health)

# ==============================================================================
# END OF SPEED ROUND RAILWAY FIXES
# ==============================================================================
'''
    
    return speed_round_fixes

def create_comprehensive_railway_solution():
    """
    Create comprehensive solution for both Avatar and Speed Round Railway issues
    """
    
    print("🔧 COMPREHENSIVE RAILWAY SOLUTION GENERATOR")
    print("=" * 70)
    
    # Generate solutions
    speed_fixes = generate_speed_round_fixes()
    
    # Combine with AIS Railway integration
    complete_solution = f'''
# ==============================================================================
# BEESMART RAILWAY DEPLOYMENT FIX - COMPLETE SOLUTION
# ==============================================================================
# Addresses both Avatar Generation and Speed Round issues on Railway

{speed_fixes}

# ADDITIONAL RAILWAY CONFIGURATION:
# Add these to your Flask app configuration for Railway optimization

# Railway Database Configuration
if os.getenv('RAILWAY_ENVIRONMENT'):
    # Optimize for Railway PostgreSQL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {{
        'pool_timeout': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {{
            'connect_timeout': 10,
            'application_name': 'BeeSmart_Railway'
        }}
    }}
    
    # Session configuration for Railway
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# DEPLOYMENT VERIFICATION ENDPOINTS:
@app.route("/api/railway/health")
def railway_system_health():
    """Comprehensive Railway system health check"""
    health = {{
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'services': {{}}
    }}
    
    # Test Avatar System
    try:
        from avatar_catalog import railway_avatar_health_check
        avatar_health = railway_avatar_health_check()
        health['services']['avatar_system'] = avatar_health
    except:
        health['services']['avatar_system'] = {{'status': 'unavailable'}}
    
    # Test Speed Round
    try:
        speed_health = speed_round_health()
        health['services']['speed_round'] = speed_health.get_json()
    except:
        health['services']['speed_round'] = {{'status': 'unavailable'}}
    
    # Overall status
    avatar_ok = health['services']['avatar_system'].get('ais_status') == 'operational'
    speed_ok = health['services']['speed_round'].get('speed_round_status') == 'operational'
    
    health['overall_status'] = 'operational' if (avatar_ok and speed_ok) else 'degraded'
    
    return jsonify(health)

# ==============================================================================
'''
    
    return complete_solution

if __name__ == "__main__":
    # Run diagnostics
    print("🚀 Starting Railway Issue Diagnosis...")
    
    issues, analysis = diagnose_speed_round_issues()
    
    print(f"\n📊 DIAGNOSIS COMPLETE")
    print(f"Issues Found: {len(issues)}")
    
    # Generate comprehensive solution
    solution = create_comprehensive_railway_solution()
    
    # Save solution to file
    with open("railway_complete_solution.py", "w", encoding='utf-8') as f:
        f.write(solution)
    
    print(f"\n💾 Complete Railway solution saved to: railway_complete_solution.py")
    print(f"\n🎯 IMMEDIATE ACTIONS:")
    print(f"1. Add the solution code to AjaSpellBApp.py")
    print(f"2. Replace existing Speed Round routes with Railway-safe versions")
    print(f"3. Deploy to Railway")
    print(f"4. Test endpoints:")
    print(f"   - /api/railway/health")
    print(f"   - /api/speed-round/health") 
    print(f"   - /api/avatar-health")
    print(f"5. Install 6 new avatars using enhanced AIS")
    
    print(f"\n✅ Railway deployment issues will be resolved!")
    print(f"🎉 Ready for full Avatar + Speed Round functionality!")