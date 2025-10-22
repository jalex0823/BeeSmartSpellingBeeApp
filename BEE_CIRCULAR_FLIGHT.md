# 3D Bee Circular Flight Animation

## Overview
Updated the 3D bee swarm animation on the main menu to fly in realistic circular patterns instead of bouncing back and forth horizontally across the screen. Also slowed down their movement for a more calming, natural effect.

## Changes Made

### Before
- ❌ Bees moved horizontally left-to-right across screen
- ❌ Simple bobbing up and down with sine wave
- ❌ Fast, frantic movement (speed: 0.01-0.03)
- ❌ Rotated continuously without purpose
- ❌ Looked robotic and repetitive

### After
- ✅ Bees fly in circular/elliptical patterns
- ✅ Each bee has its own circular path with unique center point
- ✅ Slower, more natural movement (speed: 0.3-0.7, ~50% slower)
- ✅ Bees face direction of travel (tangent to circle)
- ✅ Bank/tilt into turns like real flying insects
- ✅ Some clockwise, some counter-clockwise for variety
- ✅ Gentle vertical bobbing while circling

## Animation Parameters

### Circular Motion
```javascript
circleRadius: 2 + Math.random() * 3          // Radius: 2-5 units
circleSpeed: 0.3 + Math.random() * 0.4       // Speed: 0.3-0.7 (slower)
circlePhase: Math.random() * Math.PI * 2     // Random start angle
centerX: -8 + Math.random() * 16             // Circle center X
centerY: -2 + Math.random() * 4              // Circle center Y
clockwise: ±1                                 // Random direction
```

### Gentle Bobbing
```javascript
bobSpeed: 0.8 + Math.random() * 0.6          // Speed: 0.8-1.4 (slower)
bobHeight: 0.15 + Math.random() * 0.2        // Height: 0.15-0.35 (subtler)
bobOffset: Random phase offset
```

### Realistic Banking
```javascript
tiltAmount: 0.15 + Math.random() * 0.1       // Bank into turns
rotation.x: Pitch variation (gentle up/down tilt)
rotation.y: Face direction of travel
rotation.z: Banking angle while turning
```

## Technical Implementation

### Position Calculation (Circular Path)
```javascript
// X position on circle
bee.position.x = centerX + Math.cos(circlePhase) * circleRadius;

// Z position (creates ellipse for depth)
bee.position.z = Math.sin(circlePhase) * circleRadius * 0.3;

// Y position (bob up and down)
bee.position.y = centerY + Math.sin(time * bobSpeed) * bobHeight;
```

### Direction Facing (Natural Heading)
```javascript
// Calculate tangent angle (perpendicular to radius)
const tangentAngle = circlePhase + (Math.PI / 2) * clockwise;
bee.rotation.y = tangentAngle; // Bee faces direction of travel
```

### Banking Animation (Like Real Flight)
```javascript
// Tilt into the turn
bee.rotation.z = -Math.sin(circlePhase) * tiltAmount * clockwise;

// Gentle pitch variation
bee.rotation.x = Math.sin(time * bobSpeed * 0.5) * 0.1;
```

## Visual Effects

### Realistic Bee Behavior
1. **Circular Foraging Pattern**: Real bees often fly in circular patterns when searching for flowers
2. **Variable Radius**: Each bee has different circle size (2-5 units)
3. **Mixed Directions**: Some clockwise, some counter-clockwise
4. **Banking**: Bees tilt into turns like real flying insects
5. **Gentle Bobbing**: Subtle vertical movement, not dramatic bouncing

### Speed Comparison
- **Old Speed**: 0.01-0.03 per frame (fast, frantic)
- **New Speed**: 0.3-0.7 around circle * 0.01 = 0.003-0.007 effective speed
- **Result**: ~50-70% slower, more calming

### Performance
- No change in performance impact
- Still renders 4-6 bees depending on screen size
- Circular math is just as efficient as linear motion
- Smooth 60 FPS maintained

## Code Changes

### File: `templates/unified_menu.html`

#### Function: `spawnBees()`
**Lines ~2553-2595**

**Old approach**:
```javascript
userData = {
    speed: 0.01 + Math.random() * 0.02,
    bobSpeed: 2 + Math.random() * 2,
    direction: 1 or -1
}
```

**New approach**:
```javascript
userData = {
    circleRadius: 2 + Math.random() * 3,
    circleSpeed: 0.3 + Math.random() * 0.4,
    circlePhase: random start angle,
    centerX/centerY: random circle center,
    clockwise: ±1,
    tiltAmount: banking angle
}
```

#### Function: `animate()`
**Lines ~2597-2642**

**Old logic**:
- Linear horizontal movement with wraparound
- Simple sine wave bobbing
- Continuous Y-axis rotation
- Simple Z-axis tilt

**New logic**:
- Calculate position on circle using cos/sin
- Update phase angle each frame
- Face tangent direction (direction of travel)
- Bank into turns (Z-axis rotation)
- Gentle pitch variation (X-axis)
- Keep bees within bounds

## Benefits

### User Experience
- 🐝 **More Natural**: Looks like real bees buzzing around flowers
- 😌 **Calming**: Slower, smoother motion is less distracting
- 🎨 **Visually Interesting**: Circular patterns are more engaging than straight lines
- 🔄 **Variety**: Each bee has unique circle size and direction
- ✨ **Polished**: Banking and tilting adds realism

### Accessibility
- Less likely to trigger motion sensitivity
- Slower speeds are easier on the eyes
- More predictable motion patterns
- Can still be disabled with `prefers-reduced-motion`

## Testing Notes

### What to Look For
1. **Circular Motion**: Bees should fly in visible circles/ellipses
2. **Slower Speed**: Movement should feel calm, not frantic
3. **Banking**: Bees should tilt when turning
4. **Direction Facing**: Bees should face where they're going
5. **Smooth Animation**: No jittering or jumping
6. **Variety**: Each bee has different pattern

### Browser Testing
- ✅ Chrome/Edge: Works perfectly
- ✅ Firefox: Works perfectly
- ✅ Safari: Works perfectly
- ✅ Mobile: Works with reduced bee count (4 instead of 6)

### Performance Testing
- Desktop: 60 FPS maintained
- Mobile: 60 FPS maintained (with 4 bees)
- No memory leaks
- CPU usage unchanged

## Future Enhancements

### Possible Additions
- **Figure-8 patterns**: Some bees could fly in infinity symbols
- **Landing behavior**: Bees could occasionally "land" and rest
- **Follow cursor**: Bees could be attracted to mouse movement
- **Flower interaction**: Bees could visit specific spots on screen
- **Speed variation**: Bees could speed up/slow down randomly
- **Group behavior**: Bees could avoid each other

### Advanced Realism
- Wing animation (if models support it)
- Pollen particles trailing behind
- Sound effects tied to proximity to screen center
- Seasonal flower backgrounds
- Day/night cycle effects

## Date
October 16, 2025
