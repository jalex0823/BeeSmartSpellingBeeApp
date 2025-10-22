# Avatar System Fixes Required

## Issues to Fix:

1. **Thumbnail Size Consistency** - Registration page thumbnails need uniform sizing
2. **Dashboard Box Sizes** - All stat boxes should be same size
3. **Default Avatar** - Users without avatar selection should default to MascotBee
4. **3D Model Integration** - Selected avatar thumbnail must link to its 3D model variant
5. **Persistent Avatar Display** - Selected avatar replaces mascot on all pages

## Changes Needed:

### 1. Registration Page (`templates/auth/register.html`)
- Fix avatar grid to use fixed dimensions for all thumbnails
- Ensure images are square and same size
- Update default selection to 'cool-bee' (MascotBee)

### 2. Dashboard (`templates/auth/student_dashboard.html`)
- Make all stat cards uniform height/width
- Use flexbox/grid for consistent sizing

### 3. Avatar Selection Logic
- Default new users to 'cool-bee' avatar
- Store selected avatar_id in User model
- Load user's avatar on all pages instead of MascotBee

### 4. 3D Model Loading
- Map avatar_id to correct 3D model files
- Update SmartyBee3D initialization to use user's avatar
- Create mapping from avatar_id to model paths

### 5. Session/Database
- User.avatar_id defaults to 'cool-bee'
- Load avatar from DB on login
- Pass avatar to all templates via context

## File Structure for Avatars:
```
static/assets/avatars/
  ├── cool-bee/
  │   ├── thumbnail.png (128x128)
  │   ├── model.obj
  │   ├── model.mtl
  │   └── texture.png
  ├── explorer-bee/
  │   └── ...
  └── fallback.png
```

## Implementation Order:
1. Fix thumbnail sizing CSS
2. Fix dashboard box sizing
3. Update default avatar to cool-bee in models.py
4. Create avatar-to-3D-model mapping
5. Update template context to pass user avatar
6. Update 3D loading logic to use user's selected avatar
