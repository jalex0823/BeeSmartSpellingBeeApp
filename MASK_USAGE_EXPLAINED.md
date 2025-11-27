# 🗺️ Mask Implementation in Particle System Visualization

## Overview
The mask is used as a **per-pixel alpha filter** that runs AFTER particles are drawn to the canvas. It creates geographic/shape-based occlusion, hiding particles in certain areas while keeping them visible in others.

## Implementation Flow

### 1. **Mask Loading** (Lines 3057-3073)

```javascript
function loadMask() {
    maskImage = new Image();
    maskImage.onload = function() {
        maskLoaded = true;
    };
    maskImage.onerror = function() {
        console.warn('Failed to load mask image');
        maskLoaded = false;
    };
    // SVG mask embedded as data URL - Russia map shape
    // Black areas = visible, white areas = hidden
    maskImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0i...';
}
loadMask();
```

**Key Points:**
- Mask is an **embedded SVG as base64 data URL** (no external file needed)
- SVG dimensions: **860×260px** (matches quiz canvas exactly)
- SVG contains:
  - White background rectangle (hidden areas)
  - Black path shape (Russia map contour with antialiasing filter)
  - Gaussian blur filter (stdDeviation: 1) for smooth edges

### 2. **Mask Application** (Lines 3164-3186)

```javascript
function applyMask() {
    if (!maskLoaded || !maskImage) return;
    
    // Step 1: Get current canvas pixel data (RGBA)
    const imageData = ctx.getImageData(0, 0, W, H);
    const data = imageData.data;
    
    // Step 2: Create temporary canvas for mask
    const maskCanvas = document.createElement('canvas');
    maskCanvas.width = W;
    maskCanvas.height = H;
    const maskCtx = maskCanvas.getContext('2d');
    maskCtx.drawImage(maskImage, 0, 0, W, H);
    const maskData = maskCtx.getImageData(0, 0, W, H).data;
    
    // Step 3: Per-pixel alpha blending
    for (let i = 0; i < data.length; i += 4) {
        // Calculate mask brightness: (R + G + B) / 3
        const maskBrightness = (maskData[i] + maskData[i+1] + maskData[i+2]) / 3;
        
        // If mask is white (brightness > 200), hide particle
        if (maskBrightness > 200) {
            data[i + 3] = 0; // Set alpha to fully transparent
        }
        // If mask is black (brightness ≤ 200), keep particle visible
    }
    
    // Step 4: Put modified pixels back to canvas
    ctx.putImageData(imageData, 0, 0);
}
```

**Detailed Algorithm:**
1. **Get Canvas Data:** Extract all pixel data from the 2D canvas context (RGBA format)
2. **Create Mask Layer:** Draw the mask SVG onto a temporary canvas
3. **Extract Mask Data:** Get pixel data from the mask canvas
4. **Per-Pixel Processing:** 
   - Loop through every pixel (i += 4 for RGBA quadlets)
   - Calculate mask brightness: average of R, G, B channels
   - Threshold: if brightness > 200 (white area), set alpha to 0 (transparent)
   - Otherwise: keep original alpha (visible)
5. **Update Canvas:** Put the modified pixel data back to main canvas

### 3. **Mask Called in Particle Loop** (Line 3273)

```javascript
function drawParticleSystem() {
    ctx.clearRect(0, 0, W, H);
    
    // ... draw all particles ...
    particles.forEach(p => {
        // Draw particle circle at (p.x, p.y)
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // Spawn new particles
    // ... spawning logic ...
    
    // Apply mask AFTER all particles drawn
    applyMask();
}
```

## Mask Design Details

### SVG Structure
```xml
<svg width="860" height="260" viewBox="0 0 860 260" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="antialias">
      <feGaussianBlur stdDeviation="1" />
    </filter>
  </defs>
  <!-- White background (hidden areas) -->
  <rect width="860" height="260" fill="white" />
  <!-- Black Russia map (visible areas) -->
  <g filter="url(#antialias)">
    <path d="M120 60 L360 100 L560 70 ..." fill="black" />
  </g>
</svg>
```

### Color Mapping
- **White (RGB: 255, 255, 255):** Hidden - particles set to transparent
- **Black (RGB: 0, 0, 0):** Visible - particles remain at original alpha
- **Gray (antialiased edges):** Partial transparency - smooth transition
- **Threshold:** brightness > 200 = hidden, ≤ 200 = visible

### Antialiasing
- Gaussian blur filter (σ=1) applied to the black path
- Creates smooth edges at black/white boundaries
- Prevents hard pixelated edges on geographic contours

## Execution Order (Per Frame)

```
1. clearRect() - Clear previous frame
   ↓
2. particles.forEach() - Draw all particles as circles
   ↓
3. Particle spawning - Add new particles based on energy
   ↓
4. applyMask() - FINAL STEP: Hide particles in white areas
   ├─ getImageData() - Extract current canvas pixels
   ├─ drawImage(maskImage) - Draw mask to temp canvas
   ├─ Per-pixel brightness check - Compare R+G+B/3 to 200
   ├─ Set alpha = 0 for white pixels - Make transparent
   └─ putImageData() - Apply changes back to canvas
   ↓
5. requestAnimationFrame() - Schedule next frame
```

## Performance Considerations

### Why Post-Processing?
- **Simplicity:** No need to check mask before drawing each particle
- **Flexibility:** Can change mask without rewriting particle rendering
- **Performance:** Single ImageData operation vs per-particle checks

### Pixel Operations
- **Per-frame cost:** 860 × 260 × 4 bytes = 896KB data traversal
- **Optimization:** Simple brightness calculation (no complex math)
- **Threshold:** Single comparison (brightness > 200)

### Memory Usage
- **Canvas data:** 860 × 260 × 4 = ~896KB
- **Temporary mask canvas:** 860 × 260 × 4 = ~896KB
- **Total overhead:** ~2MB (negligible on modern browsers)

## Visual Result

### What Users See
- **Black areas (Russia map):** Particles fully visible with colors and glow
- **White areas (outside map):** Particles completely hidden
- **Edges (antialiased):** Smooth fade transition
- **Effect:** Particles contained within geographic shape

### Color Preservation
- **Before mask:** Particles have original RGBA colors (amber/orange layers)
- **After mask:** Colors unchanged, only alpha channel modified
- **Result:** Color gradient layers remain distinct within visible region

## Comparison with Alternatives

### Why Not Clip Path?
- **Cons:** Not all browsers support on canvas elements
- **Chosen:** Per-pixel masking is universally supported

### Why Not Clipping Region?
- **Cons:** Limited to geometric shapes (paths, rects)
- **Chosen:** Mask allows arbitrary complex shapes (geographic borders)

### Why Post-Process vs Pre-Process?
- **Pre-process:** Check each particle before drawing
  - Complexity: per-particle mask checks
  - Overhead: Branches in inner loop
- **Post-process:** Draw all particles, then mask
  - Simplicity: Single mask application
  - Chosen: Better performance for many particles

## Mask Updates

### When Mask Changes
1. Edit SVG base64 data in `loadMask()` function
2. New mask loads when page refreshes
3. `maskLoaded` flag ensures mask is ready before use
4. If load fails, `applyMask()` exits early (graceful degradation)

### Extending Mask
- **Add regions:** Modify SVG path coordinates
- **Change shape:** Replace path element
- **Adjust fade:** Modify Gaussian blur stdDeviation
- **Different theme:** Use different color (currently black/white)

## Code Structure

### Global Variables
```javascript
let maskImage = null;        // Image object holding mask
let maskLoaded = false;      // Flag: mask ready to use
```

### Functions
```javascript
loadMask()        // Load SVG mask on initialization
applyMask()       // Apply mask to canvas pixels (called each frame)
drawParticleSystem() // Main loop that calls applyMask() at end
```

## Summary

The mask implementation uses a **post-render per-pixel alpha filter** that:
1. ✅ Loads a Russia map SVG (860×260px) as embedded base64
2. ✅ Draws all particles to canvas without mask awareness
3. ✅ Applies mask by comparing pixel brightness to threshold (>200)
4. ✅ Sets alpha=0 for white areas (hidden)
5. ✅ Keeps particles in black areas (visible)
6. ✅ Creates smooth edges via antialiased SVG filter
7. ✅ Runs every frame for dynamic masking of moving particles

**Result:** Geographic shape masking that constrains particle visualization to a specific region while maintaining smooth, antialiased edges and full color fidelity.
