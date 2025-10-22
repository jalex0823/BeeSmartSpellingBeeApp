#!/usr/bin/env python3
"""
Example Integration: Adding Avatar Theme Generation to AjaSpellBApp.py

Add these code snippets to your main Flask application to integrate the theme system
"""

# ========================================
# 1. ADD IMPORT AT THE TOP OF AjaSpellBApp.py
# ========================================
"""
from avatar_catalog import (
    generate_theme_from_title,
    install_new_avatar, 
    get_avatar_theme,
    bulk_install_avatars,
    get_avatar_info
)
"""

# ========================================
# 2. ADD NEW API ROUTES TO YOUR FLASK APP
# ========================================

"""
@app.route('/api/avatar/theme/<avatar_id>')
def get_avatar_theme_api(avatar_id):
    '''Get theme configuration for an avatar'''
    try:
        theme = get_avatar_theme(avatar_id)
        return jsonify({
            'success': True,
            'theme': theme,
            'avatar_id': avatar_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/avatar/install', methods=['POST'])
def install_avatar_api():
    '''Install new avatar with automatic theme generation'''
    try:
        data = request.get_json()
        folder_name = data.get('folder_name', '')
        
        if not folder_name:
            return jsonify({
                'success': False,
                'error': 'Folder name required'
            }), 400
        
        # Install the avatar with theme generation
        avatar_config = install_new_avatar(
            folder_name=folder_name,
            display_name=data.get('display_name'),
            category=data.get('category'),
            description=data.get('description')
        )
        
        if avatar_config:
            return jsonify({
                'success': True,
                'avatar': avatar_config,
                'message': f"Avatar '{avatar_config['name']}' installed with {avatar_config['theme']['ui_style']} theme!"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to install avatar - check folder structure'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/avatar/personality-message')
def get_personality_message():
    '''Get personalized message based on user's avatar theme'''
    try:
        user_avatar_id = session.get('avatar_id', 'cool-bee')
        context = request.args.get('context', 'greeting')  # greeting, encouragement, celebration
        
        theme = get_avatar_theme(user_avatar_id)
        
        # Simple personality message generation
        messages = {
            'tech': {
                'greeting': "System initialized! Ready to compute spelling success! 🤖",
                'encouragement': "Recalibrating... Your next attempt will be optimized! 🔧",
                'celebration': "SUCCESS! Achievement unlocked! 🏆"
            },
            'royal': {
                'greeting': "Greetings, noble speller! Your royal quiz awaits! 👑",
                'encouragement': "Even royalty learns from mistakes. Carry on! 👑",
                'celebration': "Magnificent! Truly worthy of the crown! 👑"
            },
            'superhero': {
                'greeting': "With great spelling comes great responsibility! 💪",
                'encouragement': "Every hero faces challenges! You've got this! 💫",
                'celebration': "AMAZING! You've saved the day again! 🌟"
            },
            'default': {
                'greeting': "Buzzing with excitement for your spelling adventure! 🐝",
                'encouragement': "No worries! Every bee learns at their own pace! 🐝",
                'celebration': "Bee-utiful spelling! You're awesome! 🐝"
            }
        }
        
        ui_style = theme.get('ui_style', 'default')
        style_messages = messages.get(ui_style, messages['default'])
        message = style_messages.get(context, style_messages['greeting'])
        
        return jsonify({
            'success': True,
            'message': message,
            'avatar_id': user_avatar_id,
            'theme': theme,
            'context': context
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
"""

# ========================================
# 3. ENHANCE EXISTING AVATAR SELECTION
# ========================================

"""
@app.route('/api/set-avatar', methods=['POST'])
def set_avatar():
    '''Enhanced avatar selection with theme information'''
    try:
        data = request.get_json()
        avatar_id = data.get('avatar_id')
        
        # Validate avatar exists
        avatar_info = get_avatar_info(avatar_id)
        if not avatar_info:
            return jsonify({
                'success': False, 
                'error': 'Avatar not found'
            }), 404
        
        # Get theme information
        theme = get_avatar_theme(avatar_id)
        
        # Store in session
        session['avatar_id'] = avatar_id
        session['avatar_theme'] = theme
        
        return jsonify({
            'success': True,
            'avatar_id': avatar_id,
            'avatar_info': avatar_info,
            'theme': theme,
            'message': f"Avatar set to {avatar_info['name']} with {theme['ui_style']} theme!"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
"""

# ========================================
# 4. ADD CSS THEME SUPPORT TO TEMPLATES
# ========================================

"""
<!-- Add this to your template head section -->
<style>
.avatar-themed {
    --primary-color: #FFD700;
    --secondary-color: #FFA500;
    --accent-color: #FFFF00;
    transition: all 0.3s ease;
}

.primary-bg { background-color: var(--primary-color); }
.secondary-bg { background-color: var(--secondary-color); }
.accent-bg { background-color: var(--accent-color); }
.primary-text { color: var(--primary-color); }
.secondary-text { color: var(--secondary-color); }
.accent-text { color: var(--accent-color); }
.themed-border { border: 2px solid var(--primary-color); }
.themed-shadow { box-shadow: 0 4px 8px var(--primary-color)33; }

/* Tech theme effects */
.tech-theme .tech-glow {
    animation: techGlow 2s ease-in-out infinite alternate;
}

@keyframes techGlow {
    from { box-shadow: 0 0 5px var(--primary-color); }
    to { box-shadow: 0 0 20px var(--primary-color), 0 0 30px var(--accent-color); }
}

/* Royal theme effects */
.royal-theme .royal-shine {
    background: linear-gradient(45deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    background-size: 200% 200%;
    animation: royalShine 3s ease infinite;
}

@keyframes royalShine {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Superhero theme effects */
.superhero-theme .hero-pulse {
    animation: heroPulse 1.5s ease-in-out infinite;
}

@keyframes heroPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
</style>
"""

# ========================================
# 5. JAVASCRIPT TO APPLY THEMES DYNAMICALLY
# ========================================

"""
// Add this JavaScript to your templates
function applyAvatarTheme(theme) {
    const root = document.documentElement;
    
    // Apply CSS custom properties
    root.style.setProperty('--primary-color', theme.primary_color);
    root.style.setProperty('--secondary-color', theme.secondary_color);
    root.style.setProperty('--accent-color', theme.accent_color);
    
    // Add theme class to body
    document.body.classList.remove('tech-theme', 'royal-theme', 'superhero-theme', 'default-theme');
    document.body.classList.add(theme.ui_style + '-theme');
    
    // Update themed elements
    document.querySelectorAll('.avatar-themed').forEach(element => {
        element.classList.add(theme.ui_style + '-themed');
    });
}

// Load user's avatar theme on page load
function loadUserAvatarTheme() {
    fetch('/api/avatar/theme/' + userAvatarId)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                applyAvatarTheme(data.theme);
                console.log('Avatar theme loaded:', data.theme.ui_style);
            }
        })
        .catch(error => console.error('Error loading avatar theme:', error));
}

// Get personalized messages
function getPersonalityMessage(context = 'greeting') {
    return fetch('/api/avatar/personality-message?context=' + context)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.message;
            }
            return "Ready to buzz into action! 🐝";
        })
        .catch(error => {
            console.error('Error getting personality message:', error);
            return "Ready to buzz into action! 🐝";
        });
}
"""

print("🎨 AVATAR THEME INTEGRATION GUIDE")
print("=" * 60)
print("✅ Theme generation system ready")
print("✅ Avatar installation framework complete")
print("✅ API routes defined")
print("✅ CSS theme support ready")
print("✅ JavaScript integration examples provided")
print()
print("📝 Next Steps:")
print("1. Add the import statement to AjaSpellBApp.py")
print("2. Add the new API routes to your Flask app")
print("3. Add CSS theme support to your templates")  
print("4. Add JavaScript theme application functions")
print("5. Test with: python -m flask run")
print()
print("🎯 Key Features:")
print("• Automatic theme generation from avatar names")
print("• Dynamic color schemes and personality traits")
print("• Personality-based messages and interactions")
print("• CSS custom properties for easy theming")
print("• Bulk avatar installation support")
print()
print("🔥 Ready to make your avatar system more dynamic and themed!")