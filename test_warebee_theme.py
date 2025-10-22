from avatar_catalog import generate_theme_from_title

# Test the updated WareBee werewolf theme
theme = generate_theme_from_title('WareBee')
print('🐺 WareBee Werewolf Theme:')
print(f'  Style: {theme["ui_style"]}')
print(f'  Primary Color: {theme["primary_color"]}') 
print(f'  Secondary Color: {theme["secondary_color"]}')
print(f'  Accent Color: {theme["accent_color"]}')
print(f'  Personality: {", ".join(theme["personality"])}')
print(f'  Animation: {theme["animation_style"]}')
print(f'  Keywords: {", ".join(theme["description_keywords"])}')