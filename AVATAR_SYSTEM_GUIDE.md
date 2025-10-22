# 3D Bee Avatar System Implementation Guide

## Overview
The BeeSmart Spelling Bee app now includes a customizable 3D Bee Avatar system with 13 bee types and male/female variants (26 total avatars).

## Database Schema

### User Model Updates
Added fields to `users` table:
- `avatar_id` (String): Avatar identifier (e.g., 'explorer-bee', 'rockstar-bee')
- `avatar_variant` (String): 'male' or 'female'
- `avatar_locked` (Boolean): Parental control lock
- `avatar_last_updated` (DateTime): Last time avatar was changed

Default values:
- avatar_id: 'classic-bee'
- avatar_variant: 'male'
- avatar_locked: False

## Avatar Catalog

### 13 Bee Types (26 Variants Total)

1. **Classic Bee** (classic-bee)
   - Traditional honeybee - hardworking and sweet!
   - Category: classic

2. **Rockstar Bee** (rockstar-bee)
   - Rock out with style - guitar and all!
   - Category: entertainment

3. **Explorer Bee** (explorer-bee)
   - Adventure awaits! Complete with safari hat and binoculars.
   - Category: adventure

4. **Nurse/Doctor Bee** (nurse-bee)
   - Here to heal and help! Medical professional bee.
   - Category: profession

5. **Astronaut Bee** (astronaut-bee)
   - Reaching for the stars! Space explorer bee.
   - Category: adventure

6. **Chef Bee** (chef-bee)
   - Culinary master! Creates delicious honey dishes.
   - Category: profession

7. **Athlete Bee** (athlete-bee)
   - Sporty and active! Always ready for action.
   - Category: sports

8. **Artist Bee** (artist-bee)
   - Creative and colorful! Paintbrush and palette ready.
   - Category: arts

9. **Scientist Bee** (scientist-bee)
   - Curious and intelligent! Lab coat and beakers.
   - Category: profession

10. **Pirate Bee** (pirate-bee)
    - Ahoy matey! Sailing the honey seas.
    - Category: adventure

11. **Superhero Bee** (superhero-bee)
    - Saving the day with bee powers! Cape included.
    - Category: fantasy

12. **Wizard Bee** (wizard-bee)
    - Magical and mysterious! Wand and wizard hat.
    - Category: fantasy

13. **Ninja Bee** (ninja-bee)
    - Stealthy and skilled! Master of the bee-do arts.
    - Category: adventure

## Asset Structure

```
static/assets/avatars/
├── classic-bee/
│   ├── male.glb           # 3D model file (glTF binary)
│   ├── male_thumb.png     # Thumbnail (256x256)
│   ├── female.glb
│   ├── female_thumb.png
│   └── fallback.png       # Static fallback image
├── rockstar-bee/
│   ├── male.glb
│   ├── male_thumb.png
│   ├── female.glb
│   ├── female_thumb.png
│   └── fallback.png
├── explorer-bee/
│   └── ...
└── ... (11 more types)
```

### Asset Requirements

**3D Models (.glb files)**:
- Format: glTF 2.0 binary (.glb)
- Max file size: 2MB per model
- Polygon count: <10,000 triangles
- Optimized for web loading
- Includes embedded textures

**Thumbnails (.png files)**:
- Size: 256x256 pixels
- Format: PNG with transparency
- Max file size: 50KB
- Clear view of character

**Fallback images**:
- Size: 256x256 pixels
- Static 2D representation
- Used when 3D fails to load

## API Endpoints

### 1. Get Avatar Catalog
```
GET /api/avatars
GET /api/avatars?category=adventure
GET /api/avatars?search=pirate
```

Response:
```json
{
  "status": "success",
  "avatars": [
    {
      "id": "explorer-bee",
      "name": "Explorer Bee",
      "description": "Adventure awaits!",
      "variants": ["male", "female"],
      "category": "adventure"
    }
  ],
  "total": 13
}
```

### 2. Get Avatar Categories
```
GET /api/avatars/categories
```

Response:
```json
{
  "status": "success",
  "categories": {
    "adventure": [...],
    "profession": [...],
    "fantasy": [...]
  }
}
```

### 3. Get User's Avatar
```
GET /api/users/{user_id}/avatar
GET /api/users/me/avatar
```

Response:
```json
{
  "status": "success",
  "avatar": {
    "avatar_id": "explorer-bee",
    "variant": "female",
    "name": "Explorer Bee",
    "thumbnail_url": "/static/assets/avatars/explorer-bee/female_thumb.png",
    "model_url": "/static/assets/avatars/explorer-bee/female.glb",
    "last_updated": "2025-10-19T03:00:00Z",
    "locked": false
  }
}
```

### 4. Update User's Avatar
```
PUT /api/users/{user_id}/avatar
PUT /api/users/me/avatar

Body:
{
  "avatar_id": "rockstar-bee",
  "variant": "male"
}
```

Response:
```json
{
  "status": "success",
  "message": "Avatar updated successfully",
  "avatar": {
    "avatar_id": "rockstar-bee",
    "variant": "male",
    ...
  }
}
```

### 5. Lock/Unlock Avatar (Parental Control)
```
POST /api/users/{user_id}/avatar/lock
POST /api/users/{user_id}/avatar/unlock
```

Permissions:
- Parents can lock/unlock their linked students' avatars
- Teachers can lock/unlock their linked students' avatars
- Admins can lock/unlock any avatar

## Frontend Implementation

### 1. Registration Flow

Update `templates/auth/register.html`:
- Add avatar selection step after role selection
- Show avatar grid with categories
- Display 3D preview using Three.js or model-viewer
- Require selection before completing registration

### 2. Dashboard Display

Update dashboard templates:
- Replace mascot with user's selected avatar
- Position avatar next to grade badge
- Add "Change Avatar" button
- Lazy load 3D model

### 3. Settings/Profile Page

Create avatar management UI:
- Grid view of all avatars
- Category filters
- Search functionality
- 3D preview on hover/selection
- Save/Cancel buttons

### 4. 3D Model Viewer

Use one of these libraries:
- **model-viewer** (Google): Simplest, web component
- **Three.js**: Most powerful, requires more code
- **Babylon.js**: Game engine, feature-rich

Example with model-viewer:
```html
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>

<model-viewer 
  src="/static/assets/avatars/explorer-bee/female.glb"
  alt="Explorer Bee Avatar"
  auto-rotate
  camera-controls
  style="width: 300px; height: 300px;">
</model-viewer>
```

## Migration Steps

### 1. Database Migration
```python
# Run this to add avatar columns to existing users
python init_db.py migrate-avatars
```

### 2. Create Asset Directories
```bash
mkdir -p static/assets/avatars
# Create subdirectories for each bee type
```

### 3. Add Placeholder Assets
For development, create simple placeholder images:
```bash
# Generate placeholder thumbnails
# Use any bee icon/emoji as fallback
```

### 4. Update Templates
- Add avatar picker to registration
- Update dashboard to show avatar
- Create settings page for avatar management

### 5. Test Flow
1. Register new user → select avatar → see on dashboard
2. Change avatar from settings → updates immediately
3. Lock avatar (as parent) → student cannot change
4. Test fallback when 3D fails to load

## Accessibility

- Alt text format: "{Bee Name} Avatar ({Variant})"
- Keyboard navigation for avatar picker
- Screen reader announcements for avatar changes
- Color contrast compliance for UI elements

## Performance Optimization

1. **Lazy Loading**: Load 3D models only when visible
2. **Caching**: Cache loaded models in browser
3. **Progressive Enhancement**: Show thumbnail first, then 3D
4. **Compression**: Use Draco compression for .glb files
5. **CDN**: Serve assets from CDN if possible

## Security Considerations

1. **Validation**: All avatar_id values validated against catalog
2. **Authorization**: Users can only change their own avatars
3. **Parental Controls**: Lock mechanism prevents unauthorized changes
4. **Rate Limiting**: Limit avatar changes (e.g., max 10 per hour)

## Future Enhancements

1. **Avatar Customization**: Allow color customization
2. **Unlockable Avatars**: Earn special avatars through achievements
3. **Animations**: Add idle animations to 3D models
4. **Voice Lines**: Add character-specific sound effects
5. **Avatar Shop**: Premium avatars for purchase/unlock

## Testing Checklist

- [ ] Database migration adds avatar columns
- [ ] API endpoints return correct data
- [ ] Avatar catalog loads correctly
- [ ] Registration requires avatar selection
- [ ] Dashboard displays selected avatar
- [ ] Avatar changes update immediately
- [ ] Fallback works when 3D fails
- [ ] Parental lock prevents changes
- [ ] Parents can lock/unlock linked students
- [ ] Thumbnails load quickly
- [ ] 3D models are optimized
- [ ] Mobile devices handle 3D rendering
- [ ] Accessibility features work correctly

## Support

For issues or questions:
1. Check avatar_catalog.py for valid avatar IDs
2. Verify asset files exist in correct directories
3. Check browser console for 3D loading errors
4. Ensure database migration completed successfully

## Version History

- **v1.0 (2025-10-19)**: Initial avatar system implementation
  - 13 bee types with male/female variants
  - Basic selection and display
  - Parental control locks
