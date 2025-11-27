# Mask Implementation Workflow Diagram

## Frame-by-Frame Execution

```
┌─────────────────────────────────────────────────────────────────┐
│                    EACH ANIMATION FRAME                         │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Clear Canvas
┌─────────────────────┐
│  ctx.clearRect()    │  ← Remove previous frame
│  (860×260 canvas)   │
└─────────────────────┘
           ↓

STEP 2: Draw Particles
┌──────────────────────────────────────────┐
│  particles.forEach(p => {                │
│    ctx.arc(p.x, p.y, size)              │  ← Draw 150 particles max
│    ctx.fill()                            │     with full colors
│  })                                      │     (amber/orange)
└──────────────────────────────────────────┘
           ↓

STEP 3: Spawn New Particles
┌──────────────────────────────────────────┐
│  const spawnRate = 5-50 (energy-based)  │
│  Add new particles to array              │  ← Based on speech
└──────────────────────────────────────────┘     detection energy
           ↓

STEP 4: APPLY MASK ⭐ (THE KEY STEP)
┌───────────────────────────────────────────────────────────┐
│  applyMask()                                              │
│  ├─ Get canvas ImageData (all pixels RGBA)               │
│  ├─ Draw mask SVG to temp canvas                         │
│  ├─ Get mask ImageData                                   │
│  ├─ Loop every pixel (i += 4):                           │
│  │  ├─ Calculate brightness = (R+G+B)/3                  │
│  │  └─ IF brightness > 200 THEN alpha = 0                │
│  └─ Put modified pixels back to canvas                   │
└───────────────────────────────────────────────────────────┘
           ↓

STEP 5: Schedule Next Frame
┌─────────────────────────────────┐
│  requestAnimationFrame(animate)  │  ← 60fps target
└─────────────────────────────────┘
           ↓
      [REPEAT]
```

## Mask Pixel Comparison (Per-Pixel)

```
BEFORE MASK (Canvas Pixels)
┌──────────────────────────────────────────┐
│  Particle A at (400, 130)                │
│  Color: rgba(255, 153, 51, 0.5)         │  ← Orange particle
│  ✓ Visible (full alpha)                  │
│                                          │
│  Particle B at (100, 50)                 │
│  Color: rgba(255, 153, 51, 0.5)         │  ← Orange particle
│  ✓ Visible (full alpha)                  │
└──────────────────────────────────────────┘

                    ↓

APPLY MASK (Check Each Pixel)
┌──────────────────────────────────────────┐
│  Particle A location (400, 130):         │
│  Mask brightness at (400, 130) = 10     │  ← Black area
│  10 > 200? NO                            │
│  → Keep alpha = 0.5 (VISIBLE ✓)          │
│                                          │
│  Particle B location (100, 50):          │
│  Mask brightness at (100, 50) = 245     │  ← White area
│  245 > 200? YES                          │
│  → Set alpha = 0 (HIDDEN ✗)              │
└──────────────────────────────────────────┘

                    ↓

AFTER MASK (Canvas Result)
┌──────────────────────────────────────────┐
│  Particle A at (400, 130)                │
│  Color: rgba(255, 153, 51, 0.5)         │  ← Visible in black area
│  ✓ SHOWN                                 │
│                                          │
│  Particle B at (100, 50)                 │
│  Color: rgba(255, 153, 51, 0)           │  ← Hidden in white area
│  ✗ HIDDEN (transparent)                  │
└──────────────────────────────────────────┘
```

## Mask SVG Structure

```
SVG (860×260)
├─ <defs>
│  └─ <filter id="antialias">
│     └─ <feGaussianBlur stdDeviation="1" />  ← Smooth edges
│
├─ <rect> (860×260, white)                     ← Background (hidden)
│  └─ This covers entire canvas with white
│
└─ <g filter="url(#antialias)">
   └─ <path> (black shape)                     ← Russia map contour
      └─ Points: M120,60 L360,100 L560,70...
         └─ Blurred edges for antialiasing
```

## Brightness Threshold Visualization

```
Mask Pixel Brightness Scale
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  0 (Black)        100         200      255 (White)    │
│  |────────────────|-----------|─────────|               │
│  ✓ SHOW PARTICLES │ TRANSITION  ✗ HIDE PARTICLES      │
│                   │ (antialiased)                      │
│                                                         │
│  Decision: if (brightness > 200) → alpha = 0           │
│                                                         │
└─────────────────────────────────────────────────────────┘

Examples:
- Black pixels (0-10):     brightness ≤ 200 → VISIBLE
- Gray edges (150-200):    brightness ≤ 200 → VISIBLE
- Light gray (200-240):    brightness > 200 → HIDDEN
- White pixels (250-255):  brightness > 200 → HIDDEN
```

## Data Flow Diagram

```
┌─────────────────────────────┐
│   Animation Loop Running    │
│   (requestAnimationFrame)   │
└──────────────┬──────────────┘
               │
               ↓
        ┌──────────────┐
        │ drawParticle │
        │   System()   │
        └──────┬───────┘
               │
        ┌──────┴──────────────┐
        ↓                     ↓
   ┌────────────┐      ┌─────────────┐
   │ Clear      │      │ Get Canvas  │
   │ Canvas     │      │ ImageData   │
   └────┬───────┘      └─────┬───────┘
        ↓                    ↓
   ┌────────────┐      ┌─────────────┐
   │ Draw All   │      │ Load Mask   │
   │ Particles  │      │ SVG to Temp │
   │ (full      │      │ Canvas      │
   │ colors)    │      └─────┬───────┘
   └────┬───────┘            ↓
        │              ┌─────────────┐
        │              │ Get Mask    │
        │              │ ImageData   │
        │              └─────┬───────┘
        │                    ↓
        │              ┌─────────────┐
        │              │ Per-Pixel   │
        │              │ Brightness  │
        │              │ Comparison  │
        │              └─────┬───────┘
        │                    ↓
        │              ┌─────────────┐
        │              │ Set Alpha=0 │
        │              │ if >200     │
        │              └─────┬───────┘
        │                    ↓
        └────────┬───────────┘
                 ↓
         ┌──────────────────┐
         │ Put Modified     │
         │ ImageData Back   │
         │ to Canvas        │
         └─────────┬────────┘
                   ↓
         ┌──────────────────┐
         │ Frame Rendered   │
         │ (Masked Result)  │
         └──────────────────┘
```

## Energy States & Particle Visibility

```
ENERGY STATE: IDLE (energyTarget = 0.05)
┌────────────────────────────────┐
│ Spawn Rate: 5-10 particles/fr  │
│ Particle Velocity: slow        │  → Sparse particles
│ Alpha: varies by lifecycle     │  → Very subtle effect
└────────────────────────────────┘
       After Mask Applied
       ┌─────────────────┐
       │ Only 50% show   │
       │ (in black area) │
       │ ••  (sparse)    │
       └─────────────────┘

ENERGY STATE: PAUSING (energyTarget = 0.15)
┌────────────────────────────────┐
│ Spawn Rate: 10-20 particles/fr │
│ Particle Velocity: moderate    │  → Moderate particles
│ Alpha: varies by lifecycle     │  → Noticeable effect
└────────────────────────────────┘
       After Mask Applied
       ┌─────────────────┐
       │ ~70% show       │
       │ (in black area) │
       │ • • •• • (more) │
       └─────────────────┘

ENERGY STATE: SPEAKING (energyTarget = 1.2)
┌────────────────────────────────┐
│ Spawn Rate: 40-50 particles/fr │
│ Particle Velocity: fast        │  → Many fast particles
│ Alpha: varies by lifecycle     │  → Strong effect
└────────────────────────────────┘
       After Mask Applied
       ┌─────────────────┐
       │ ~80% show       │
       │ (in black area) │
       │ ••••••• (dense) │
       └─────────────────┘
```

## Color Preservation Through Mask

```
PARTICLE COLORS (6 Layers - Amber Theme)
┌──────────────────────────────────────────────────────┐
│ Layer 1: rgba(153,  63,   0, 0.7) │ Deep Amber      │
│ Layer 2: rgba(204,  92,   0, 0.6) │ Medium Amber    │
│ Layer 3: rgba(230, 115,   0, 0.55)│ Light Amber     │
│ Layer 4: rgba(255, 153,  51, 0.5) │ Orange          │
│ Layer 5: rgba(255, 184, 112, 0.45)│ Light Orange    │
│ Layer 6: rgba(255, 216, 176, 0.4) │ Peachy          │
└──────────────────────────────────────────────────────┘

              MASK APPLIED
       (only modifies ALPHA channel)

┌──────────────────────────────────────────────────────┐
│ Layer 1: rgba(153,  63,   0, X  ) │ Colors same ✓   │
│ Layer 2: rgba(204,  92,   0, X  ) │ Colors same ✓   │
│ Layer 3: rgba(230, 115,   0, X  ) │ Colors same ✓   │
│ Layer 4: rgba(255, 153,  51, X  ) │ Colors same ✓   │
│ Layer 5: rgba(255, 184, 112, X  ) │ Colors same ✓   │
│ Layer 6: rgba(255, 216, 176, X  ) │ Colors same ✓   │
└──────────────────────────────────────────────────────┘

Legend: X = alpha modified (0 if in white area, unchanged if in black)
Result: Color gradients fully preserved, only visibility changes
```

---

**Summary:** The mask works as a **final post-processing filter** that:
1. ✅ Lets particles render at full quality with all colors
2. ✅ Then selectively hides particles in white regions
3. ✅ Creates geographic/shape-based occlusion
4. ✅ Maintains performance with simple brightness threshold
5. ✅ Produces smooth edges via antialiased SVG mask
