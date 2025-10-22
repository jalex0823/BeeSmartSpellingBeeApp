#!/usr/bin/env python3
"""
Avatar Theme Integration for BeeSmart App
Functions to integrate avatar themes into the main Flask application
"""

def add_avatar_theme_routes(app):
    """
    Add avatar theme-related routes to the Flask app
    
    Args:
        app: Flask application instance
    """
    from flask import jsonify, request
    from avatar_catalog import (
        generate_theme_from_title, 
        install_new_avatar, 
        get_avatar_theme,
        bulk_install_avatars
    )
    
    @app.route('/api/avatar/theme/<avatar_id>')
    def get_avatar_theme_api(avatar_id):
        """Get theme configuration for an avatar"""
        try:
            theme = get_avatar_theme(avatar_id)
            if theme:
                return jsonify({
                    'success': True,
                    'theme': theme,
                    'avatar_id': avatar_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Avatar not found'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/avatar/generate-theme', methods=['POST'])
    def generate_theme_api():
        """Generate theme configuration from avatar name"""
        try:
            data = request.get_json()
            avatar_name = data.get('name', '')
            
            if not avatar_name:
                return jsonify({
                    'success': False,
                    'error': 'Avatar name required'
                }), 400
            
            theme = generate_theme_from_title(avatar_name)
            
            return jsonify({
                'success': True,
                'theme': theme,
                'avatar_name': avatar_name
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/avatar/install', methods=['POST'])
    def install_avatar_api():
        """Install new avatar with theme generation"""
        try:
            data = request.get_json()
            folder_name = data.get('folder_name', '')
            display_name = data.get('display_name')
            category = data.get('category')
            description = data.get('description')
            
            if not folder_name:
                return jsonify({
                    'success': False,
                    'error': 'Folder name required'
                }), 400
            
            # Install the avatar
            avatar_config = install_new_avatar(
                folder_name=folder_name,
                display_name=display_name,
                category=category,
                description=description
            )
            
            if avatar_config:
                return jsonify({
                    'success': True,
                    'avatar': avatar_config,
                    'message': f"Avatar '{avatar_config['name']}' installed successfully"
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

def apply_avatar_theme_to_ui(theme, element_id=None):
    """
    Generate CSS styling based on avatar theme
    
    Args:
        theme (dict): Theme configuration
        element_id (str, optional): Specific element ID to target
        
    Returns:
        str: CSS styling string
    """
    
    base_selector = f"#{element_id}" if element_id else ".avatar-themed"
    
    css = f"""
    {base_selector} {{
        --primary-color: {theme['primary_color']};
        --secondary-color: {theme['secondary_color']};
        --accent-color: {theme['accent_color']};
        --ui-style: {theme['ui_style']};
    }}
    
    {base_selector} .primary-bg {{
        background-color: {theme['primary_color']};
    }}
    
    {base_selector} .secondary-bg {{
        background-color: {theme['secondary_color']};
    }}
    
    {base_selector} .accent-bg {{
        background-color: {theme['accent_color']};
    }}
    
    {base_selector} .primary-text {{
        color: {theme['primary_color']};
    }}
    
    {base_selector} .secondary-text {{
        color: {theme['secondary_color']};
    }}
    
    {base_selector} .accent-text {{
        color: {theme['accent_color']};
    }}
    
    {base_selector} .themed-border {{
        border: 2px solid {theme['primary_color']};
    }}
    
    {base_selector} .themed-shadow {{
        box-shadow: 0 4px 8px {theme['primary_color']}33;
    }}
    """
    
    # Add style-specific animations and effects
    if theme['ui_style'] == 'tech':
        css += f"""
        {base_selector} .tech-glow {{
            animation: techGlow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes techGlow {{
            from {{ box-shadow: 0 0 5px {theme['primary_color']}; }}
            to {{ box-shadow: 0 0 20px {theme['primary_color']}, 0 0 30px {theme['accent_color']}; }}
        }}
        """
    elif theme['ui_style'] == 'royal':
        css += f"""
        {base_selector} .royal-shine {{
            background: linear-gradient(45deg, {theme['primary_color']}, {theme['secondary_color']}, {theme['accent_color']});
            background-size: 200% 200%;
            animation: royalShine 3s ease infinite;
        }}
        
        @keyframes royalShine {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        """
    elif theme['ui_style'] == 'superhero':
        css += f"""
        {base_selector} .hero-pulse {{
            animation: heroPulse 1.5s ease-in-out infinite;
        }}
        
        @keyframes heroPulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        """
    
    return css

def get_avatar_personality_message(theme, context='greeting'):
    """
    Generate personality-based messages for avatars
    
    Args:
        theme (dict): Avatar theme configuration
        context (str): Context for the message ('greeting', 'encouragement', 'celebration')
        
    Returns:
        str: Personality-appropriate message
    """
    
    personality = theme.get('personality', ['friendly'])
    style = theme.get('ui_style', 'default')
    
    messages = {
        'greeting': {
            'tech': [
                "System initialized! Ready to compute spelling success! 🤖",
                "AI analysis complete: You're ready to spell! 💻",
                "Digital dictionary loaded. Let's process some words! ⚡"
            ],
            'royal': [
                "Greetings, noble speller! Your royal quiz awaits! 👑",
                "By royal decree, let the spelling commence! ✨",
                "Your majesty's spelling prowess shall be legendary! 🏰"
            ],
            'superhero': [
                "With great spelling comes great responsibility! 💪",
                "Ready to save the day with perfect spelling? 🦸‍♂️",
                "Your spelling superpowers are about to shine! ⚡"
            ],
            'medical': [
                "Doctor's orders: spell with precision! 🩺",
                "Prescribing a healthy dose of spelling practice! 💊",
                "Let's diagnose your spelling skills! 🏥"
            ],
            'default': [
                "Buzzing with excitement for your spelling adventure! 🐝",
                "Ready to bee-come a spelling champion? 🍯",
                "Let's make this hive busy with learning! 🌻"
            ]
        },
        'encouragement': {
            'tech': [
                "Recalibrating... Your next attempt will be optimized! 🔧",
                "Error detected and corrected. Continuing process... 🛠️",
                "Updating spelling algorithms... Keep trying! 📡"
            ],
            'royal': [
                "Even royalty learns from mistakes. Carry on, noble one! 👑",
                "A true ruler perseveres! Try once more! 🗡️",
                "Your kingdom believes in you! 🏰"
            ],
            'superhero': [
                "Every hero faces challenges! You've got this! 💫",
                "Superpowers are earned through practice! 🚀",
                "Heroes never give up! Ready for round two? 🎯"
            ],
            'default': [
                "No worries! Every bee learns at their own pace! 🐝",
                "Keep buzzing along! You're doing great! 🌸",
                "The hive believes in you! Try again! 🍯"
            ]
        },
        'celebration': {
            'tech': [
                "SUCCESS! Achievement unlocked! 🏆",
                "Data confirmed: You're a spelling genius! 📊",
                "System upgrade complete: You're getting smarter! 🎮"
            ],
            'royal': [
                "Magnificent! Truly worthy of the crown! 👑",
                "Splendid! Your royal spelling skills shine! ✨",
                "Bravo! A performance fit for the palace! 🎭"
            ],
            'superhero': [
                "AMAZING! You've saved the day again! 🌟",
                "Incredible! Your spelling powers are unstoppable! ⚡",
                "Fantastic! Another victory for team spelling! 🎊"
            ],
            'default': [
                "Bee-utiful spelling! You're awesome! 🐝",
                "Sweet success! You're the bee's knees! 🍯",
                "Buzz-worthy performance! Keep it up! 🌻"
            ]
        }
    }
    
    style_messages = messages.get(context, {}).get(style, messages[context]['default'])
    
    import random
    return random.choice(style_messages)

# Usage example for Flask app integration:
"""
# In AjaSpellBApp.py, add this:

from avatar_theme_integration import add_avatar_theme_routes, apply_avatar_theme_to_ui, get_avatar_personality_message

# Add theme routes to your app
add_avatar_theme_routes(app)

# In your quiz route, you can get personalized messages:
@app.route('/api/quiz/encouragement')
def get_encouragement():
    user_avatar_id = session.get('avatar_id', 'cool-bee')
    theme = get_avatar_theme(user_avatar_id)
    message = get_avatar_personality_message(theme, 'encouragement')
    return jsonify({'message': message, 'theme': theme})
"""