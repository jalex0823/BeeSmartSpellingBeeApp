# Avatar Persistence System - Verification & Documentation
## October 19, 2025

## Current Avatar System Architecture

### Overview
The avatar system allows users to select a personalized 3D avatar at registration that persists across all sessions and displays consistently throughout the application. If no avatar is selected, the default MascotBee displays instead.

---

## Flow Diagram

```
Registration → Avatar Selection → Save to Database → Display on Every Page
                     ↓
            (If none selected)
                     ↓
            Default MascotBee
                     ↓
        User can change in Dashboard
                     ↓
            Updated avatar persists
```

---

## Implementation Details

### 1. Database Schema (`models.py`)

**User Model Fields:**
```python
avatar_id = db.Column(db.String(50), default='cool-bee', index=True)
avatar_variant = db.Column(db.String(20), default='default')
avatar_last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
avatar_locked = db.Column(db.Boolean, default=False)
preferences = db.Column(db.JSON, default=dict)  # Stores avatar_selected flag
```

**Key Methods:**
- `update_avatar(avatar_id, variant='default')` - Updates user's avatar
- `get_avatar_data()` - Returns complete avatar data with URLs
- `has_selected_avatar()` - Returns True if user explicitly selected an avatar (not default)

**Avatar Selection Logic:**
```python
def has_selected_avatar(self) -> bool:
    try:
        prefs = self.preferences or {}
        # Avatar is "selected" if:
        # 1. preferences['avatar_selected'] == True, OR
        # 2. avatar_id is set and != 'cool-bee' (default)
        explicit = bool(prefs.get('avatar_selected'))
        non_default = bool(self.avatar_id and self.avatar_id != 'cool-bee')
        return explicit or non_default
    except Exception:
        return bool(self.avatar_id and self.avatar_id != 'cool-bee')
```

---

### 2. Registration Flow (`AjaSpellBApp.py` - Line 4279)

**Form Processing:**
```python
avatar_id = data.get('avatar_id', 'cool-bee').strip()  # Default to 'cool-bee'

new_user = User(
    username=username,
    display_name=display_name,
    email=email if email else None,
    role=role,
    grade_level=grade_level if grade_level else None,
    avatar_id=avatar_id,  # ✅ Saved to database
    avatar_variant='default'
)

# Mark avatar as selected ONLY if user chose non-default
prefs = new_user.preferences or {}
prefs['avatar_selected'] = (avatar_id is not None and avatar_id != 'cool-bee')
new_user.preferences = prefs
```

**Registration Template (`templates/auth/register.html`):**
- Displays avatar grid dynamically from `/api/avatars`
- Default selection: `cool-bee` (if available)
- Hidden input field: `<input type="hidden" id="selected_avatar" name="avatar_id" value="cool-bee">`
- JavaScript updates value on click

---

### 3. Avatar Loading System

**API Endpoint:** `/api/users/me/avatar` (GET)

**Logic Flow:**
```python
@app.route("/api/users/me/avatar", methods=["GET"])
def api_get_my_avatar():
    # 1. Get authenticated user (or guest user)
    user = current_user if current_user.is_authenticated else get_or_create_guest_user()
    
    # 2. Check if user has explicitly selected avatar
    use_mascot = not user.has_selected_avatar()
    
    # 3. If no selection → Return MascotBee
    if use_mascot:
        return jsonify({
            'avatar': {
                'avatar_id': 'mascot-bee',
                'urls': {
                    'model_obj': '/static/models/MascotBee_1019174653_texture.obj',
                    'model_mtl': '/static/models/MascotBee_1019174653_texture.mtl',
                    'texture': '/static/models/MascotBee_1019174653_texture.png',
                    'thumbnail': '/static/BeeSmartBee.png'
                }
            },
            'use_mascot': True
        })
    
    # 4. Otherwise → Return user's selected avatar
    return jsonify({
        'avatar': user.get_avatar_data(),
        'use_mascot': False
    })
```

**Front-End Loader (`static/js/user-avatar-loader.js`):**

```javascript
class UserAvatarLoader {
    async init() {
        // Fetch user's avatar from API
        const response = await fetch('/api/users/me/avatar');
        const data = await response.json();
        
        if (data.status === 'success' && data.avatar) {
            this.userAvatar = data.avatar;
            return true;
        }
        
        // Fallback to default MascotBee
        return false;
    }
    
    getAvatarOptions() {
        // Returns 3D model paths for SmartyBee3D constructor
        if (this.userAvatar && this.userAvatar.urls) {
            return {
                modelPath: this.userAvatar.urls.model_obj,
                mtlPath: this.userAvatar.urls.model_mtl,
                texturePath: this.userAvatar.urls.texture
            };
        }
        return this.defaultAvatar;  // MascotBee paths
    }
}
```

---

### 4. Display on Every Page

**Menu Page (`templates/unified_menu.html`):**
```javascript
async function initDefaultMascot() {
    const container = document.getElementById('mascotBee3D');
    
    // Wait for avatar loader to fetch user's avatar
    await window.userAvatarLoader.init();
    
    // Get avatar options (will be user's choice or MascotBee)
    const avatarOptions = window.userAvatarLoader.getAvatarOptions({
        width: 250,
        height: 250,
        autoRotate: true,
        enableInteraction: true
    });
    
    // Initialize 3D model with user's avatar or MascotBee
    window.mascotBee = new SmartyBee3D('mascotBee3D', avatarOptions);
}
```

**Quiz Page & Other Pages:**
- Same pattern: use `window.userAvatarLoader.getAvatarOptions()` to get correct paths
- Automatically loads user's selected avatar or defaults to MascotBee

---

### 5. Dashboard Avatar Management

**Student Dashboard (`templates/auth/student_dashboard.html`):**
```javascript
// Load user's avatar thumbnail
fetch('/api/users/me/avatar')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success' && data.avatar && data.avatar.urls) {
            const avatarImg = document.getElementById('userAvatarImg');
            avatarImg.src = data.avatar.urls.thumbnail;
        }
    });
```

**Change Avatar Button:**
- Links to `/test/avatar-picker` (or avatar picker component)
- User can select new avatar
- Updates via `PUT /api/users/me/avatar`

**API Endpoint for Updating:**
```python
@app.route("/api/users/me/avatar", methods=["PUT"])
def api_update_my_avatar():
    data = request.get_json()
    avatar_id = data.get('avatar_id')
    variant = data.get('variant', 'default')
    
    # Update user's avatar in database
    success, message = current_user.update_avatar(avatar_id, variant)
    
    if success:
        # Mark as explicitly selected
        prefs = current_user.preferences or {}
        prefs['avatar_selected'] = True
        current_user.preferences = prefs
        db.session.commit()
    
    return jsonify({'status': 'success' if success else 'error', 'message': message})
```

---

## Verification Checklist

### ✅ Current Status

1. **Registration:**
   - [ ] Avatar grid displays all available avatars
   - [ ] Default selection is 'cool-bee'
   - [ ] Selected avatar is saved to `user.avatar_id`
   - [ ] `preferences['avatar_selected']` is set correctly

2. **Database Persistence:**
   - [x] `avatar_id` field exists in User model
   - [x] `avatar_variant` field exists
   - [x] `preferences` JSON field exists
   - [x] `has_selected_avatar()` method implemented

3. **API Endpoints:**
   - [x] `GET /api/users/me/avatar` returns user's avatar or MascotBee
   - [x] `PUT /api/users/me/avatar` updates user's avatar
   - [x] Proper fallback to MascotBee when no selection

4. **Front-End Loading:**
   - [x] `UserAvatarLoader` class exists
   - [x] Auto-initializes on page load
   - [x] Fetches avatar from API
   - [x] Provides correct paths to 3D loader

5. **Display Consistency:**
   - [ ] Menu page displays user's avatar (or MascotBee)
   - [ ] Quiz page displays user's avatar
   - [ ] Dashboard shows correct avatar thumbnail
   - [ ] Avatar persists after logout/login

6. **Dashboard Management:**
   - [ ] "Change Avatar" button exists
   - [ ] Links to avatar picker
   - [ ] Updates are saved to database
   - [ ] Updates reflected immediately

---

## Known Issues & Recommendations

### Current Implementation Strengths:
✅ Database schema supports avatar persistence  
✅ API properly checks `has_selected_avatar()`  
✅ Front-end loader has fallback logic  
✅ Registration form includes avatar selection  

### Potential Issues to Test:

1. **Registration Flow:**
   - Verify avatar_id is actually saved to database on registration
   - Check if `preferences['avatar_selected']` is being set correctly
   - Test with both default ('cool-bee') and custom avatars

2. **Avatar Selection Flag:**
   - Current logic: Only sets `avatar_selected=True` if avatar != 'cool-bee'
   - **Issue:** If user explicitly selects 'cool-bee' at registration, it won't be marked as "selected"
   - **Recommendation:** Always set `avatar_selected=True` if user clicks any avatar (even cool-bee)

3. **Guest User Handling:**
   - Verify guest users get MascotBee (not 'cool-bee')
   - Ensure guest→authenticated user migration preserves avatar choice

---

## Testing Script

```python
# Test avatar persistence
from app import app, db
from models import User

with app.app_context():
    # 1. Create test user with custom avatar
    test_user = User(
        username='test_avatar_user',
        display_name='Test User',
        avatar_id='explorer-bee',
        avatar_variant='default'
    )
    test_user.set_password('password123')
    
    # Mark avatar as selected
    test_user.preferences = {'avatar_selected': True}
    
    db.session.add(test_user)
    db.session.commit()
    
    # 2. Query back and verify
    user = User.query.filter_by(username='test_avatar_user').first()
    print(f"Avatar ID: {user.avatar_id}")  # Should be 'explorer-bee'
    print(f"Has Selected: {user.has_selected_avatar()}")  # Should be True
    print(f"Avatar Data: {user.get_avatar_data()}")
    
    # 3. Test has_selected_avatar() logic
    assert user.has_selected_avatar() == True
    
    # 4. Create user with default (no selection)
    default_user = User(
        username='test_default_user',
        display_name='Default User',
        avatar_id='cool-bee'
    )
    default_user.set_password('password123')
    db.session.add(default_user)
    db.session.commit()
    
    # Should return False (no selection)
    assert default_user.has_selected_avatar() == False
    
    print("✅ All avatar persistence tests passed!")
```

---

## Recommended Improvements

### 1. Fix Registration Logic
**Current Issue:** If user selects default 'cool-bee', it's not marked as "selected"

**Fix in `AjaSpellBApp.py` registration route:**
```python
# BEFORE:
prefs['avatar_selected'] = (avatar_id is not None and avatar_id != 'cool-bee')

# AFTER (recommended):
# Mark as selected if avatar_id was explicitly provided in the form
prefs['avatar_selected'] = bool(avatar_id and 'avatar_id' in data)
```

### 2. Add Visual Feedback on Selection
- Show checkmark on selected avatar at registration
- Display "You chose: [Avatar Name]" message
- Confirm avatar selection before account creation

### 3. Database Migration
Create migration to set `avatar_selected` for existing users:
```python
# For users with non-default avatars
UPDATE users 
SET preferences = jsonb_set(
    COALESCE(preferences, '{}'), 
    '{avatar_selected}', 
    'true'
) 
WHERE avatar_id IS NOT NULL AND avatar_id != 'cool-bee';
```

### 4. Add Avatar Preview on Registration
Show live 3D preview of selected avatar before account creation

---

## Summary

**Current State:** ✅ System is architecturally sound and should work correctly

**Next Steps:**
1. Test registration flow with actual form submission
2. Verify database writes `avatar_id` correctly
3. Test login → menu display cycle
4. Confirm dashboard avatar display
5. Test avatar change functionality

**Expected Behavior:**
- ✅ User selects avatar at registration → Saved to database
- ✅ User logs in → Avatar loads from database
- ✅ Avatar displays on menu, quiz, and all pages
- ✅ User can change avatar in dashboard → Updates persist
- ✅ No selection → MascotBee displays as default

---

**Status:** System implemented correctly. Needs live testing to confirm database writes and API responses.
