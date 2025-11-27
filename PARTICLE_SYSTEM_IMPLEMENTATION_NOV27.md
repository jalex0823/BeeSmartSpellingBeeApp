# 🎨 Particle System Implementation - November 27, 2025

## Summary
Successfully converted smooth wave visualizations to dynamic particle systems across both quiz pages while maintaining full visual polish and responsiveness.

## Changes Made

### 1. **Quiz Page Particle System** (`templates/quiz.html`)
- **Lines 3184-3260:** Replaced `drawHorizontalWaveform()` with `drawParticleSystem()`
- **Color Theme:** Amber/Orange gradient (6 layers)
- **Particle Behavior:**
  - Spawn from center (W/2, H/2)
  - Emanate outward in all directions
  - Constrained to circular boundary (maxRadius = 35% of canvas size)
  - Energy-driven spawn rate: 5-50 particles per frame
  - Individual layer speeds: 1.0x to 2.8x base speed
  - Particle lifecycle: 200-300ms with fade in/out

**Color Layers:**
1. Deep amber (153, 63, 0) - alpha 0.7
2. Medium amber (204, 92, 0) - alpha 0.6
3. Light amber (230, 115, 0) - alpha 0.55
4. Orange (255, 153, 51) - alpha 0.5
5. Light orange (255, 184, 112) - alpha 0.45
6. Peachy (255, 216, 176) - alpha 0.4

### 2. **Speed Round Particle System** (`templates/speed_round_quiz.html`)
- **Lines 2278-2355:** Identical particle system with blue color theme
- **Color Theme:** Blue gradient (6 layers from deep blue to sky blue)
- **Canvas Size:** 840×220px (responsive aspect ratio maintained)

**Color Layers:**
1. Deep blue (14, 95, 181) - alpha 0.7
2. Rich blue (26, 116, 204) - alpha 0.6
3. Vibrant blue (38, 135, 224) - alpha 0.55
4. Classic blue (58, 155, 238) - alpha 0.5
5. Lighter blue (94, 179, 242) - alpha 0.45
6. Light blue (125, 195, 247) - alpha 0.4

### 3. **Centering & Responsive Layout**
- **Quiz Canvas:** 860×260px base → responsive via aspect-ratio: 860/260
- **Speed Round Canvas:** 840×220px base → responsive via aspect-ratio: 840/220
- **CSS Updates:**
  - Added `width: 100%` and `margin: 0 auto` to `.dotwave-wrapper`
  - Changed canvas from `width: 100%; height: Xpx` to `max-width: 100%; aspect-ratio: W/H`
  - Added `display: block; margin: 0 auto` for horizontal centering
  - Flex centering via `justify-content: center; align-items: center`

### 4. **Mask Integration**
- **Russia Map Mask:** Embedded SVG base64 data URL at correct resolution
  - Black areas = visible particles
  - White areas = transparent (hidden)
  - Antialiased with Gaussian blur (stdDeviation: 1)
- **Mask Application:** Applied after particle rendering via `applyMask()`
  - Loads mask into temporary canvas
  - Compares pixel brightness (>200 = white)
  - Sets alpha=0 for white areas
  - Per-pixel precision masking

## Technical Details

### Particle Lifecycle (0-100%)
- **0-30% (Birth):** Particles spawn at center, minimal movement
- **30-80% (Life):** Particles move outward with energy-driven velocity
  - Velocity: `baseSpeed × energyFactor × 3`
  - Direction: Random angle (0-360°)
  - Boundary: Constrained to circular max radius
- **80-100% (Death):** Fade out alpha from 1.0 → 0.0

### Energy Mapping
- **Idle:** energyTarget = 0.05 (minimal activity)
- **Pausing/Hint:** energyTarget = 0.15 (moderate activity)
- **Speaking:** energyTarget = 1.2 (maximum activity)
- **Smooth transition:** `energy += (energyTarget - energy) × 0.12` per frame

### Performance
- **Spawn Rate:** `Math.max(5, Math.ceil(particlesPerLayer × energy × 2))`
  - At idle: ~5 particles/frame
  - At speaking: 25-50 particles/frame
- **Max Particles:** 150 (25 particles × 6 layers)
- **Cleanup:** Expired particles automatically filtered each frame
- **Target FPS:** 60fps via requestAnimationFrame

## Animation Features

### 1. **Center Emanation**
- All particles originate from canvas center (W/2, H/2)
- Spread uniformly in all directions (360° full circle)
- No directional bias

### 2. **Layer Differentiation**
- Each layer has unique base speed (1.0x to 2.8x)
- Frequency parameter preserved for future enhancement (not used in particles)
- 6 distinct color gradients create depth perception

### 3. **Energy Responsiveness**
- Particle count directly proportional to speech detection energy
- Velocity magnitude scales with energy
- Smooth energy transitions prevent jarring changes

### 4. **Visual Polish**
- Soft particle edges (2-5px radius circles)
- Smooth alpha blending (RGBA colors)
- Drop-shadow effects on canvas:
  - Outer glow: `drop-shadow(0 0 4px rgba(255,255,255,0.4))`
  - Color glow: `drop-shadow(0 0 12px rgba(R,G,B,0.4))`

## Mask Behavior

### Black Areas (Visible)
- Particles fully visible with full alpha
- Used for all interactive regions

### White Areas (Hidden)
- Particles fade to transparent
- Creates geographic/shape-based occlusion
- Per-pixel precision masking

### Antialiasing
- SVG mask includes Gaussian blur (σ=1)
- Smooth transition between black/white areas
- Natural edge softening

## Browser Compatibility
- ✅ Canvas 2D API
- ✅ requestAnimationFrame
- ✅ Image API (mask loading)
- ✅ Responsive via CSS aspect-ratio
- ✅ Drop-shadow filter effects

## Testing Verification
- ✅ Particles emit from center in all directions
- ✅ All 6 layer colors visible and distinct
- ✅ Energy states (idle/pausing/speaking) affect particle intensity
- ✅ Mask correctly hides white areas
- ✅ Animation smooth at 60fps target
- ✅ Mask + particles integration working seamlessly
- ✅ Canvas centered in container
- ✅ Responsive layout maintains aspect ratio
- ✅ Both quiz and speed round pages operational

## Files Modified
1. `/templates/quiz.html` - Particle system (amber theme) + centering CSS
2. `/templates/speed_round_quiz.html` - Particle system (blue theme) + centering CSS

## Next Steps
- Monitor performance on various devices
- Consider particle count optimization if needed on lower-end devices
- Potential enhancements: particle trail effects, collision detection, layer-specific patterns

---
**Status:** ✅ COMPLETE - Particle system fully implemented and centered across all quiz pages
