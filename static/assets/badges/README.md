# BeeSmart Bee Class Badge Images

This folder contains the official badge images for each Bee Class rank in the BeeSmart Spelling App.

## Badge Files

| Rank | File | Buzz Dust Required | Description |
|------|------|-------------------|-------------|
| Novice Bee | `Novice.png` | 0+ | Simple shield with bee - starting rank |
| Apprentice Bee | `Apprentice.png` | 500+ | Bee with book and pencil - learning |
| Scholar Bee | `Scholar.png` | 2,500+ | Bee with graduation cap and diploma - dedicated |
| Elite Bee | `Elete.png` | 10,000+ | Bee with open book - champion |
| Magistrate Bee | `Magistrate.png` | 50,000+ | Bee with crown and scepter - leader |
| Buzz Dust Master | `BuzzDustMaster.png` | 100,000+ | Bee with star - legendary |

## Usage in Templates

### Display Badge Image

```html
<img src="{{ url_for('static', filename='assets/badges/' + bee_class.badge_image) }}" 
     alt="{{ bee_class.label }}" 
     class="badge-image">
```

### With Fallback to Emoji

```html
<img src="{{ url_for('static', filename='assets/badges/' + bee_class.badge_image) }}" 
     alt="{{ bee_class.label }}" 
     class="badge-image"
     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
<span class="emoji" style="display:none;">{{ bee_class.emoji }}</span>
```

## Image Specifications

- **Format**: PNG with transparency
- **Dimensions**: Varies (optimized for display at 120-150px)
- **File Sizes**: ~1.3-1.8 MB each
- **Style**: Hand-drawn, vibrant, kid-friendly

## Design Notes

Each badge features:
- The BeeSmart bee character with unique accessories for each rank
- A shield/badge frame with decorative elements
- A banner with the rank name
- Distinctive colors and symbols representing the rank level
- Professional quality suitable for print and digital display

## Integration Status

✅ Configuration file updated with badge_image paths  
✅ Explanation page displays badges  
✅ Rank progress bar shows current badge  
✅ Rank-up animation uses badge images  
✅ Fallback to emoji if image fails to load  

## Maintenance

To add or update badges:
1. Place PNG file in this directory
2. Update `config/buzz_dust_config.json` with filename
3. Clear browser cache to see changes
4. Test on multiple devices for responsive display
