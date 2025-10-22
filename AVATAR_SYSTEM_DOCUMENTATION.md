# 🐝 BeeSmart Avatar System - Complete Documentation

## Overview
The BeeSmart avatar system provides a personalized 3D bee character for each user throughout the application. Avatars are displayed consistently across all areas: forms, profile pages, games, quizzes, and battles.

---

## System Architecture

### 1. Avatar Selection Flow

#### **Registered Users**
```
Registration → Avatar Selection → Database Storage → Automatic Loading Across App
```

1. **During Registration** (`/register`):
   - User selects avatar from catalog (18 bee types available)
   - Selected avatar ID stored in `users.avatar_id` field (default: 'cool-bee')
   - `preferences.avatar_selected = True` flag set to indicate explicit choice
   - Avatar variant stored as 'default' (all bees use single model, no gender variants)

2. **On Login/Session Start**:
   - System loads user's `avatar_id` from database
   - Validates avatar exists in catalog via `get_avatar_info()`
   - Preloads all assets: OBJ model, MTL materials, textures, thumbnails
   - Avatar data available globally via `current_user.get_avatar_data()`

3. **Across Application**:
   - Profile pages display avatar with `/api/users/me/avatar` endpoint
   - Quiz interface shows avatar during gameplay
   - Battle system uses avatar for player representation
   - Admin dashboard displays avatars for user management

#### **Guest Users**
```
Guest Access → Default Mascot Bee → Registration → Selected Avatar Replaces Mascot
```

1. **Guest Session**:
   - System automatically assigns **Mascot Bee** as default
   - No database storage (session-based only)
   - Full functionality available with mascot representation

2. **Upon Registration**:
   - Guest selects permanent avatar during signup
   - Mascot Bee immediately replaced with chosen avatar
   - Session upgraded to registered user with persistent avatar

---

## Database Schema

### User Model (`models.py`)

```python
class User(UserMixin, db.Model):
    # Avatar fields
    avatar_id = db.Column(db.String(50), default='cool-bee', index=True)
    avatar_variant = db.Column(db.String(10), default='default')
    avatar_locked = db.Column(db.Boolean, default=False)  # Parental control
    avatar_last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Preferences JSON includes:
    # preferences.avatar_selected = True/False (explicit selection flag)
```

### Key Methods

#### `has_selected_avatar()` → bool
```python
def has_selected_avatar(self) -> bool:
    """Returns True if user has explicitly chosen an avatar (not default)"""
    prefs = self.preferences or {}
    explicit = bool(prefs.get('avatar_selected'))
    non_default = bool(self.avatar_id and self.avatar_id != 'cool-bee')
    return explicit or non_default
```

#### `get_avatar_data()` → dict
```python
def get_avatar_data(self):
    """Returns complete avatar data with URLs for rendering"""
    return {
        'avatar_id': self.avatar_id,
        'variant': self.avatar_variant,
        'name': 'Professor Bee',  # Display name from catalog
        'urls': {
            'thumbnail': '/static/assets/avatars/professor-bee/thumbnail.png',
            'preview': '/static/assets/avatars/professor-bee/preview.png',
            'model_obj': '/static/assets/avatars/professor-bee/ProfessorBee.obj',
            'model_mtl': '/static/assets/avatars/professor-bee/ProfessorBee.mtl',
            'texture': '/static/assets/avatars/professor-bee/ProfessorBee.png'
        },
        'locked': False,
        'last_updated': '2025-10-20T14:52:12.895548'
    }
```

#### `update_avatar(avatar_id, variant)` → (success, message)
```python
def update_avatar(self, avatar_id, variant='default'):
    """Updates user's avatar and marks as explicitly selected"""
    # Validates avatar exists in catalog
    # Updates database fields
    # Sets preferences.avatar_selected = True
    # Returns (True, "Avatar updated successfully")
```

---

## Avatar Catalog (`avatar_catalog.py`)

### Available Avatars (18 Types)
1. **Al Bee** (`al-bee`) - AI-powered tech bee
2. **Anxious Bee** (`anxious-bee`) - Nervous but trying
3. **Biker Bee** (`biker-bee`) - Fast motorcycle enthusiast
4. **Brother Bee** (`brother-bee`) - Friendly and helpful
5. **Builder Bee** (`builder-bee`) - Hard-hat constructor
6. **Cool Bee** (`cool-bee`) - Stylish and cool (DEFAULT)
7. **Diva Bee** (`diva-bee`) - Glamorous star
8. **Doctor Bee** (`doctor-bee`) - Medical professional
9. **Explorer Bee** (`explorer-bee`) - Adventure seeker
10. **Knight Bee** (`knight-bee`) - Brave defender
11. **Mascot Bee** (`mascot-bee`) - Official BeeSmart mascot (GUEST DEFAULT)
12. **Monster Bee** (`monster-bee`) - Spooky but friendly
13. **Professor Bee** (`professor-bee`) - Wise educator 🎓
14. **Queen Bee** (`queen-bee`) - Royal leader
15. **Robo Bee** (`robo-bee`) - Futuristic robot
16. **Rocker Bee** (`rocker-bee`) - Musical rock star
17. **Seabea** (`seabea`) - Oceanic explorer
18. **Scientist Bee** (`scientist-bee`) - Lab researcher

### Catalog Structure
```python
AVATAR_CATALOG = [
    {
        "id": "professor-bee",
        "name": "Professor Bee",
        "folder": "ProfessorBee",  # Source folder name
        "obj_file": "ProfessorBee.obj",
        "mtl_file": "ProfessorBee.mtl",
        "texture_file": "ProfessorBee.png",
        "description": "Wise and knowledgeable! Master of education.",
        "variants": ["default"],
        "category": "profession"
    },
    # ... more avatars
]
```

### File System Layout
```
static/assets/avatars/
├── professor-bee/              # Avatar ID (lowercase with hyphens)
│   ├── ProfessorBee.obj       # 3D model geometry
│   ├── ProfessorBee.mtl       # Material definitions
│   ├── ProfessorBee.png       # Texture image
│   ├── thumbnail.png          # Small preview (150x150)
│   ├── preview.png            # Large preview (512x512)
│   ├── model.obj              # Generic fallback
│   ├── model.mtl              # Generic fallback
│   └── texture.png            # Generic fallback
├── cool-bee/
│   └── [same structure]
└── mascot-bee/
    └── [same structure]
```

### Key Function: `get_avatar_info(avatar_id, variant='default')`
```python
def get_avatar_info(avatar_id, variant='default'):
    """
    Returns complete avatar data with asset URLs
    - Finds avatar in AVATAR_CATALOG
    - Falls back to first avatar if not found
    - Constructs full URLs for all assets
    """
```

---

## API Endpoints

### `GET /api/users/me/avatar`
**Purpose**: Get current user's avatar (authenticated or guest)

**Response**:
```json
{
  "status": "success",
  "avatar": {
    "avatar_id": "professor-bee",
    "variant": "default",
    "name": "Professor Bee",
    "urls": {
      "thumbnail": "/static/assets/avatars/professor-bee/thumbnail.png",
      "preview": "/static/assets/avatars/professor-bee/preview.png",
      "model_obj": "/static/assets/avatars/professor-bee/ProfessorBee.obj",
      "model_mtl": "/static/assets/avatars/professor-bee/ProfessorBee.mtl",
      "texture": "/static/assets/avatars/professor-bee/ProfessorBee.png"
    }
  },
  "use_mascot": false
}
```

**Logic**:
- If authenticated: Load user's selected avatar
- If guest: Return Mascot Bee
- `use_mascot` flag: `true` if user hasn't explicitly selected avatar

### `GET /api/users/<user_id>/avatar`
**Purpose**: Get specific user's avatar (requires authentication)

**Authorization**: User can only access own avatar unless admin

### `PUT /api/users/<user_id>/avatar`
**Purpose**: Update user's avatar selection

**Request**:
```json
{
  "avatar_id": "professor-bee",
  "variant": "default"
}
```

**Actions**:
1. Validates avatar exists in catalog
2. Updates `user.avatar_id` and `user.avatar_variant`
3. Sets `preferences.avatar_selected = True`
4. Updates `avatar_last_updated` timestamp
5. Returns updated avatar data

### `GET /api/avatars`
**Purpose**: Get all available avatars (catalog)

**Response**:
```json
{
  "status": "success",
  "avatars": [
    {
      "id": "professor-bee",
      "name": "Professor Bee",
      "description": "Wise and knowledgeable! Master of education.",
      "category": "profession",
      "thumbnail": "/static/assets/avatars/professor-bee/thumbnail.png",
      "preview": "/static/assets/avatars/professor-bee/preview.png"
    },
    // ... more avatars
  ]
}
```

---

## Frontend Integration

### JavaScript Avatar Loading (`unified_menu.html`)

```javascript
async function loadUserAvatar() {
    try {
        const response = await fetch('/api/users/me/avatar');
        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.use_mascot) {
                // Show Mascot Bee (guest or no selection)
                displayMascotBee();
            } else {
                // Show user's 3D avatar
                load3DAvatar(data.avatar.urls);
            }
        }
    } catch (error) {
        console.error('Failed to load avatar:', error);
        displayMascotBee(); // Fallback
    }
}
```

### Three.js 3D Avatar Rendering

```javascript
function load3DAvatar(urls) {
    const loader = new THREE.OBJLoader();
    const mtlLoader = new THREE.MTLLoader();
    
    // Load materials first
    mtlLoader.load(urls.model_mtl, (materials) => {
        materials.preload();
        loader.setMaterials(materials);
        
        // Load 3D model
        loader.load(urls.model_obj, (object) => {
            // Load texture
            const textureLoader = new THREE.TextureLoader();
            textureLoader.load(urls.texture, (texture) => {
                object.traverse((child) => {
                    if (child.isMesh) {
                        child.material.map = texture;
                    }
                });
                
                scene.add(object);
                animateAvatar(object);
            });
        });
    });
}
```

---

## Registration Flow with Avatar Selection

### `POST /register` Handler

```python
@app.route("/register", methods=["POST"])
def register():
    # Get form data
    username = data.get('username')
    display_name = data.get('display_name')
    password = data.get('password')
    avatar_id = data.get('avatar_id', 'cool-bee')  # Default if not selected
    
    # Create user
    new_user = User(
        username=username,
        display_name=display_name,
        avatar_id=avatar_id,
        avatar_variant='default'
    )
    new_user.set_password(password)
    
    # Mark avatar as explicitly selected
    prefs = new_user.preferences or {}
    prefs['avatar_selected'] = bool(avatar_id and 'avatar_id' in data)
    new_user.preferences = prefs
    
    db.session.add(new_user)
    db.session.commit()
    
    # Auto-login
    login_user(new_user, remember=True)
    
    return jsonify({"success": True})
```

---

## Avatar Consistency Across Features

### ✅ Profile Page
- Displays avatar thumbnail in header
- Shows 3D rotating avatar in profile section
- Edit button to change avatar

### ✅ Quiz Interface
- Avatar visible during spelling practice
- Reacts to correct/incorrect answers
- Animations: success celebrations, encouragement

### ✅ Battle of the Bees
- Each player represented by their avatar
- Real-time avatar updates during competition
- Victory/defeat animations

### ✅ Admin Dashboard
- User list shows thumbnails
- Avatar visible in user detail views
- Admin can see all users' avatar selections

### ✅ Forms & Inputs
- Avatar preview in registration form
- Profile edit shows current avatar
- Parent/teacher dashboards show student avatars

---

## Troubleshooting & Diagnostics

### Check User's Current Avatar (Railway Production)

```python
# check_railway_bigdaddy_avatar.py
import psycopg2

RAILWAY_DB_URL = "postgresql://postgres:...@shuttle.proxy.rlwy.net:46186/railway"

conn = psycopg2.connect(RAILWAY_DB_URL)
cursor = conn.cursor()

cursor.execute("""
    SELECT username, avatar_id, avatar_variant, avatar_last_updated
    FROM users
    WHERE username = 'BigDaddy2'
""")

result = cursor.fetchone()
print(f"Avatar ID: {result[1]}")
```

### Update Avatar in Railway Database

```python
# update_railway_bigdaddy_to_professor.py
cursor.execute("""
    UPDATE users
    SET 
        avatar_id = 'professor-bee',
        avatar_variant = 'default',
        avatar_last_updated = NOW()
    WHERE username = 'BigDaddy2'
""")
conn.commit()
```

### Verify Avatar Files Exist

```powershell
# Check if avatar files are deployed
ls static/assets/avatars/professor-bee/

# Expected output:
# ProfessorBee.obj
# ProfessorBee.mtl
# ProfessorBee.png
# thumbnail.png
# preview.png
# model.obj (fallback)
# model.mtl (fallback)
# texture.png (fallback)
```

### Common Issues

#### Issue: Cool Bee shows instead of selected avatar
**Cause**: Database has `cool-bee` stored instead of selected avatar
**Fix**: Run `update_railway_bigdaddy_to_professor.py` to update database

#### Issue: Avatar not loading (404 errors)
**Cause**: Mismatch between `avatar_catalog.py` folder name and actual filesystem
**Fix**: Ensure folder names match:
- Catalog `folder: "ProfessorBee"` → Should be `professor-bee/` on disk
- Update catalog or rename folders to match

#### Issue: Mascot Bee shows for registered user
**Cause**: `preferences.avatar_selected = False` or missing
**Fix**: Set flag to True in database:
```python
prefs = user.preferences or {}
prefs['avatar_selected'] = True
user.preferences = prefs
db.session.commit()
```

#### Issue: 3D model not rendering
**Cause**: Missing OBJ/MTL/texture files
**Fix**: Verify all three files exist:
- `ProfessorBee.obj` (geometry)
- `ProfessorBee.mtl` (materials)
- `ProfessorBee.png` (texture)

---

## Deployment Checklist

### Before Deploy
- [ ] Verify all avatar folders exist in `static/assets/avatars/`
- [ ] Check each avatar has required files: obj, mtl, texture, thumbnail, preview
- [ ] Test `get_avatar_info()` for all avatar IDs in catalog
- [ ] Confirm Railway database schema includes avatar fields
- [ ] Test guest → registration → avatar persistence flow

### After Deploy
- [ ] Test `/api/users/me/avatar` endpoint
- [ ] Verify 3D avatars load in browser console (no 404s)
- [ ] Check admin dashboard shows user avatars correctly
- [ ] Test avatar selection during registration
- [ ] Verify avatar updates via `/api/users/<id>/avatar`
- [ ] Confirm avatar consistency across profile/quiz/battle

---

## Recent Fix (October 20, 2025)

### Problem
BigDaddy2 account showed "Cool Bee" instead of "Professor Bee" on Railway production.

### Root Cause
Database `users.avatar_id` field contained `'cool-bee'` instead of `'professor-bee'`.

### Solution
1. Created diagnostic script: `check_railway_bigdaddy_avatar.py`
2. Confirmed mismatch: database showed `cool-bee`, expected `professor-bee`
3. Ran update script: `update_railway_bigdaddy_to_professor.py`
4. Successfully updated to `professor-bee` with timestamp `2025-10-21 02:26:05`

### Verification
```sql
SELECT avatar_id, avatar_last_updated 
FROM users 
WHERE username = 'BigDaddy2';

-- Result: professor-bee | 2025-10-21 02:26:05.162164
```

### User Action Required
Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

---

## Future Enhancements

### Planned Features
1. **Avatar Unlocks**: Earn new avatars through achievements
2. **Avatar Customization**: Color variations, accessories
3. **Animated Avatars**: Idle animations, reactions
4. **Avatar Marketplace**: Premium avatars for purchase
5. **Parental Controls**: Avatar lock for children's accounts
6. **Avatar Social Features**: Share avatar with friends

### Technical Improvements
1. **CDN Integration**: Serve avatar assets from CDN for faster loading
2. **Progressive Loading**: Load low-res thumbnail first, then 3D model
3. **Caching**: Browser cache strategy for avatar assets
4. **Fallback Chain**: Graceful degradation if 3D fails → 2D image → text
5. **Analytics**: Track most popular avatars, selection rates

---

## Summary

The BeeSmart avatar system provides a seamless, personalized experience:

1. **Registration**: User selects avatar → Stored in database
2. **Startup**: System validates avatar → Preloads assets
3. **Throughout App**: Avatar displayed consistently everywhere
4. **Guest Experience**: Mascot Bee → Selected avatar after registration
5. **Persistence**: Avatar saved permanently, loads on every session

**Key Philosophy**: One avatar, everywhere, always. The user's chosen bee character is their identity across the entire BeeSmart platform.

---

*Documentation version: 1.0*  
*Last updated: October 20, 2025*  
*BeeSmart Spelling Bee App v1.6*
