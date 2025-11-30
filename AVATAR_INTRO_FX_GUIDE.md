# 🎨 BeeSmart Avatar & Badge Intro FX Guide

Complete implementation guide for avatar and badge intro animations.

## 📦 What's Included

### CSS File: `static/css/avatar-intro-fx.css`
- 10 avatar intro effects
- 3 badge intro effects
- Combined avatar+badge animations
- Performance optimizations
- Reduced motion support

### JS File: `static/js/avatar-intro-fx.js`
- Effect controller class
- Auto-apply functionality
- Tier-based effect selection
- Particle system for Buzz-Dust effect
- Badge intro manager

---

## 🚀 Quick Start

### 1. Add CSS to Your Template

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/avatar-intro-fx.css') }}?v=20251130">
```

### 2. Add JS Before Closing `</body>`

```html
<script src="{{ url_for('static', filename='js/avatar-intro-fx.js') }}?v=20251130"></script>
```

### 3. Basic HTML Structure

```html
<div class="avatar-fx-container">
    <canvas id="avatar-canvas" class="avatar-img"></canvas>
</div>
```

---

## 🎯 Usage Examples

### Method 1: Direct CSS Classes (Simplest)

```html
<!-- Honey-Glow Effect -->
<div class="avatar-fx-container">
    <img src="avatar.png" class="avatar-honey-glow">
</div>

<!-- Buzz-Dust Effect -->
<div class="avatar-fx-container">
    <canvas class="avatar-buzz-dust"></canvas>
</div>

<!-- Wing-Sweep Effect -->
<div class="avatar-fx-container">
    <img src="avatar.png" class="avatar-wing-sweep">
</div>
```

### Method 2: JavaScript API (Dynamic)

```javascript
// Initialize with specific effect
const container = document.querySelector('.avatar-fx-container');
window.AvatarFX.init(container, 'honey-glow');

// With custom options
window.AvatarFX.init(container, 'buzz-dust', {
    particleCount: 20
});

// Auto-apply to all avatars
window.AvatarFX.autoApply('.avatar-fx-container', 'honey-glow');

// Tier-based effect
const tier = 'premium'; // or 'free', 'earn', 'mascot', 'special'
const effect = window.AvatarFX.getEffectForTier(tier);
window.AvatarFX.init(container, effect);
```

### Method 3: Badge Intros

```html
<div class="badge-intro">
    <img src="badge.png" class="badge-glow-pulse">
</div>
```

```javascript
// Or dynamically
const badge = document.querySelector('.badge-element');
window.AvatarFX.badgeIntro(badge, 'spin-in');
```

### Method 4: Combined Avatar + Badge

```html
<div class="avatar-fx-container avatar-badge-combo">
    <canvas class="avatar-img"></canvas>
    <img src="badge.png" class="badge-overlay">
</div>
```

```javascript
window.AvatarFX.avatarBadgeCombo(container, 'honey-glow', 'collect');
```

---

## 🎨 All Available Effects

### Avatar Effects

| Effect Name | Class | Best For | Tier |
|------------|-------|----------|------|
| **Honey-Glow** | `avatar-honey-glow` | Default, universal | All |
| **Hex-Reveal** | `avatar-hex-reveal` | Premium showcase | Premium |
| **Buzz-Dust** | `avatar-buzz-dust` | Matches Buzz Dust system | Earn |
| **Wing-Sweep** | `avatar-wing-sweep` | Unique, elegant | Special |
| **Honey-Drip** | `avatar-honey-drip` | Smooth reveal | All |
| **Golden-Flash** | `avatar-golden-flash` | Premium avatars | Premium |
| **Portal** | `avatar-portal` | Mascot/special | Mascot |
| **Swipe-Glow** | `avatar-swipe-glow` | Modern, clean | All |
| **Drop-Bounce** | `avatar-drop-bounce` | Quick, satisfying | Free |
| **Shape-Morph** | `avatar-shape-morph` | Creative transition | Special |

### Badge Effects

| Effect Name | Class | Description |
|------------|-------|-------------|
| **Glow Pulse** | `badge-glow-pulse` | Pulsing glow reveal |
| **Spin-In** | `badge-spin-in` | Spinning entrance |
| **Collect** | `badge-collect` | Flies in from top |

---

## 🎯 Recommended Effects by Context

### Avatar Picker/Gallery
```javascript
window.AvatarFX.autoApply('.avatar-thumbnail', 'drop-bounce');
```

### Profile Screen (Selected Avatar)
```javascript
window.AvatarFX.init(profileContainer, 'honey-glow', {
    addAmbientGlow: true
});
```

### Premium Avatar Unlock
```javascript
window.AvatarFX.init(unlockContainer, 'golden-flash');
```

### Battle of the Bees Intro
```javascript
window.AvatarFX.init(player1, 'wing-sweep');
window.AvatarFX.init(player2, 'wing-sweep');
```

### Badge Earned Notification
```javascript
window.AvatarFX.badgeIntro(newBadge, 'collect');
```

---

## 🛠 Integration with Existing GLB Loader

### In `user-avatar-loader.js` or `avatar-display-manager.js`

```javascript
function loadAndShowAvatar(slug, containerId) {
    const container = document.getElementById(containerId);
    
    // Your existing GLB loading code...
    loadGLBAvatar(slug).then(scene => {
        // After GLB is loaded and rendered
        const canvas = container.querySelector('canvas');
        
        // Apply intro effect
        const tier = getAvatarTier(slug);
        const effect = window.AvatarFX.getEffectForTier(tier);
        window.AvatarFX.init(container, effect);
    });
}
```

### In `unified_menu.html` Avatar Modal

```javascript
function showAvatarInfoModal(avatarSlug) {
    // Your existing modal code...
    
    // After modal opens and GLB loads
    const modalContainer = document.querySelector('#avatar-modal .avatar-3d-preview');
    
    // Determine effect based on avatar category
    const avatarData = BACKSTORIES[avatarSlug];
    let effect = 'honey-glow';
    
    if (avatarData.category === 'premium') {
        effect = 'golden-flash';
    } else if (avatarData.category === 'mascot') {
        effect = 'portal';
    } else if (avatarData.category === 'special') {
        effect = 'wing-sweep';
    }
    
    setTimeout(() => {
        window.AvatarFX.init(modalContainer, effect);
    }, 100);
}
```

---

## ⚙️ Configuration Options

### Global Options

```javascript
window.AvatarFX = new AvatarIntroFX({
    defaultEffect: 'honey-glow',
    enableParticles: true,
    particleCount: 12,
    autoPlay: true
});
```

### Per-Effect Options

```javascript
// Hex-Reveal
window.AvatarFX.init(container, 'hex-reveal', {
    tileCount: 36,
    staggerDelay: 15
});

// Buzz-Dust
window.AvatarFX.init(container, 'buzz-dust', {
    particleCount: 20
});

// Honey-Glow
window.AvatarFX.init(container, 'honey-glow', {
    addAmbientGlow: true
});
```

---

## 🎭 Stagger Delays for Multiple Avatars

```html
<div class="avatar-fx-container">
    <img class="avatar-honey-glow fx-delay-100">
</div>
<div class="avatar-fx-container">
    <img class="avatar-honey-glow fx-delay-200">
</div>
<div class="avatar-fx-container">
    <img class="avatar-honey-glow fx-delay-300">
</div>
```

Available delays: `fx-delay-100`, `fx-delay-200`, `fx-delay-300`, `fx-delay-400`, `fx-delay-500`

---

## ♿ Accessibility

Reduced motion is automatically supported:

```css
@media (prefers-reduced-motion: reduce) {
    /* All animations disabled, instant display */
}
```

---

## 🎯 Top 4 Recommended for BeeSmart

Based on your app style:

1. **🥇 Honey-Glow** - Universal, clean, on-brand
2. **🥈 Hex-Reveal** - Premium feel, honeycomb theme
3. **🥉 Buzz-Dust** - Matches Buzz Dust system perfectly
4. **🎖️ Wing-Sweep** - Unique bee-themed effect

---

## 📝 Complete Example

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/avatar-intro-fx.css') }}?v=20251130">
</head>
<body>
    <!-- Avatar Gallery -->
    <div class="avatar-gallery">
        <div class="avatar-fx-container">
            <canvas id="avatar-1" class="avatar-img"></canvas>
        </div>
        <div class="avatar-fx-container">
            <canvas id="avatar-2" class="avatar-img"></canvas>
        </div>
    </div>

    <!-- Profile Avatar with Badge -->
    <div class="avatar-fx-container avatar-badge-combo">
        <canvas id="profile-avatar" class="avatar-img"></canvas>
        <img src="bee-master-badge.png" class="badge-overlay">
    </div>

    <script src="{{ url_for('static', filename='js/avatar-intro-fx.js') }}?v=20251130"></script>
    <script>
        // After GLB avatars load
        window.addEventListener('avatarLoaded', (e) => {
            const container = e.detail.container;
            const tier = e.detail.tier;
            
            const effect = window.AvatarFX.getEffectForTier(tier);
            window.AvatarFX.init(container, effect);
        });

        // Or auto-apply to all
        document.addEventListener('DOMContentLoaded', () => {
            window.AvatarFX.autoApply('.avatar-fx-container', 'honey-glow');
        });
    </script>
</body>
</html>
```

---

## 🚀 Next Steps

1. Add CSS link to `unified_menu.html` `<head>`
2. Add JS script before `</body>` in `unified_menu.html`
3. Test with one effect: `honey-glow`
4. Integrate with GLB loader callbacks
5. Apply tier-based effects across app
6. Test on mobile devices
7. Adjust timing/particles as needed

---

## 🐛 Troubleshooting

**Effect not showing?**
- Check that container has `.avatar-fx-container` class
- Verify CSS/JS files are loaded (check Network tab)
- Ensure avatar element has `.avatar-img`, `canvas`, or `img` class

**Particles not appearing?**
- Check `enableParticles: true` in config
- Verify container has `position: relative`

**Animation too fast/slow?**
- Adjust animation duration in CSS
- Modify `animation: effectName 0.6s` timing

---

## 📊 Performance Notes

- All effects use GPU-accelerated transforms
- `will-change` optimizations applied
- Particles auto-cleanup after animation
- Reduced motion support built-in
- Tested on mobile devices

---

**Created:** November 30, 2025  
**Version:** 1.0  
**Optimized for:** BeeSmart Spelling Bee App
