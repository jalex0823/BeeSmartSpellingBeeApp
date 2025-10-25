// Shared configuration for BeeSmart dotted rainbow voice visualizer
// Adjust values here to tune BOTH quiz and speed-round visualizers.
(function(){
  window.BeeSmartVoiceVizCfg = {
    // Densify to look like a ribbon (more waves, closer spacing, smaller dots)
  MAX_WAVES: 12,
  DOTS_PER_WAVE: 96,
  DOT_RADIUS: 2.8,
  WAVE_SPACING: 14,
  // Make lines longer by reducing side padding
  HORIZONTAL_PAD_CSS: 1, // px inside-card buffer left/right (closer to card edges)

    // Amber-first palette (bottom -> top) — minimal green, warm ambers/oranges
    waveColors: [
      'rgba(255, 209, 102, 0.95)', // light amber
      'rgba(255, 192, 77, 0.95)',  // soft amber
      'rgba(255, 180, 55, 0.95)',  // amber
      'rgba(255, 162, 41, 0.95)',  // orange-amber
      'rgba(255, 140, 26, 0.95)',  // orange
      'rgba(255, 111, 0, 0.95)',   // deep orange
      'rgba(255, 95, 0, 0.95)',    // richer orange
      'rgba(255, 80, 0, 0.95)'     // deepest orange - fuller bottom
    ],

    // Optional left-to-right gradient overlay applied per dot (second pass)
    gradientLR: {
      enabled: true,
      alpha: 0.45, // overlay strength
      stops: [
        { offset: 0.0, color: 'rgba(255, 209, 102, 1.0)' },  // amber at left
        { offset: 1.0, color: 'rgba(255, 111, 0, 1.0)' }     // deep orange at right
      ]
    },

    // Fade both ends of the ribbon to transparent
    endFade: {
      enabled: true,
      // portion of the drawable width at each edge used for fading (0-0.5)
      fraction: 0.16
    },

    // Subtle thickness variation across X to mimic a single wavy sheet
    thicknessBulge: {
      enabled: true,
      magnitude: 0.18, // 0..1 additional amplitude at bulge peak
      speed: 0.002,    // animation speed over time
      cycles: 1.2      // how many bulges appear across the width
    },

    // Soft central glow highlight (like a gentle white core)
    centerGlow: {
      enabled: true,
      alpha: 0.6,         // base opacity of the glow (increased)
      verticalSpan: 0.7,  // portion of height covered (centered) 0..1 (fuller)
      energyScale: 1.1,   // multiply by current energy level (more responsive)
      // Horizontal taper at both ends (as fraction of drawable width per side)
      horizontalFraction: 0.12
    },

    // Force waves to meet at a shared tip near both ends by collapsing
    // amplitude AND vertical wave spacing towards zero at edges.
    tipPinch: {
      enabled: true,
      power: 1.25 // controls how sharply it pinches to the tips (1-2)
    },

    // Energy targets by mode
    energyTargets: {
      speaking: 1.0,
      pausing: 0.06,
      idle: 0.04
    },

    // Easing/decay speeds (higher = faster)
    easing: {
      energy: 0.18,
      wavePack: 0.22,
      dipDecay: 0.15,
      surgeDecay: 0.10
    },

    // Boost scales for pause/speak transitions
    boostScales: {
      dip: 0.65,   // lowers motion more on pause
      surge: 0.15  // slight lift when speaking resumes
    },

    // Wave shape parameters
    waveShape: {
      baseFreq: 2,
      freqStep: 0.3,
      ampBase: 22,
      ampStep: 6,
      rippleFreq: 10,
      rippleBase: 4
    }
  };
})();
