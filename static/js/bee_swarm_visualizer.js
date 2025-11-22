/**
 * Bee Swarm Voice Visualizer
 * A reusable 3D particle system that responds to voice/audio input
 * Usage: BeeSwarmVisualizer.init(containerElement, options)
 */

import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

const BeeSwarmVisualizer = {
  // State
  scene: null,
  camera: null,
  renderer: null,
  bees: null,
  container: null,
  amplitude: 0,
  ampSmooth: 0,
  isActive: false,
  
  // Particle data
  COUNT: 25000,
  positions: null,
  velocities: null,
  targets: null,
  colors: null,
  geo: null,
  mat: null,
  BASE_POINT_SIZE: 0.18,  // Increased bee size for better visibility
  
  // Animation params
  tSpeedBase: 0.015,
  noiseBase: 0.025,
  buzzBase: 0.004,
  damp: 0.93,
  
  /**
   * Initialize the visualizer
   * @param {HTMLElement} container - DOM element to attach canvas
   * @param {Object} options - Configuration options
   */
  init(container, options = {}) {
    const opts = {
      autoStart: true,
      showControls: false,
      particleCount: 8000,
      background: 'transparent',
      zIndex: 1,
      ...options
    };
    
    this.container = container;
    this.COUNT = opts.particleCount;
    
    // Setup scene to fit container
    this.initScene(container, opts);
    this.initParticles();
    this.animate(0);
    
    // Connect to speech synthesis events
    this.setupSpeechIntegration();
    
    console.log('🐝 Bee swarm visualizer initialized for quiz voice integration');
    
    return this;
  },
  
  initScene(container, opts) {
    // Create scene
    this.scene = new THREE.Scene();
    
    // Get container dimensions
    const rect = container.getBoundingClientRect();
    const width = rect.width || 860;
    const height = rect.height || 260;
    
    // Setup camera for contained view
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, 0, 15);
    
    // Setup renderer with transparent background
    this.renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      premultipliedAlpha: false
    });
    this.renderer.setSize(width, height);
    this.renderer.setClearColor(0x000000, 0); // Transparent
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    
    // Position canvas properly in container
    this.renderer.domElement.style.position = 'absolute';
    this.renderer.domElement.style.top = '0';
    this.renderer.domElement.style.left = '0';
    this.renderer.domElement.style.pointerEvents = 'none';
    this.renderer.domElement.style.zIndex = '1';
    
    // Add canvas to container
    container.appendChild(this.renderer.domElement);
    
    // Handle resize
    window.addEventListener('resize', () => {
      const newRect = container.getBoundingClientRect();
      const newWidth = newRect.width || 860;
      const newHeight = newRect.height || 260;
      
      this.camera.aspect = newWidth / newHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(newWidth, newHeight);
    });
  },
  
  initParticles() {
    this.positions = new Float32Array(this.COUNT * 3);
    this.velocities = new Float32Array(this.COUNT * 3);
    this.targets = new Float32Array(this.COUNT * 3);
    this.colors = new Float32Array(this.COUNT * 3);
    this.baseColors = new Float32Array(this.COUNT * 3); // Store original honey shades
    
    // Honey / golden brown palette - Enhanced for better visibility
    const honey = new THREE.Color("#FFD540");      // Bright golden honey
    const goldenBr = new THREE.Color("#B86B1A");   // Rich golden brown
    const darkAmber = new THREE.Color("#8B4513");  // Saddle brown
    const lightHoney = new THREE.Color("#FFF8DC"); // Cornsilk
    const deepAmber = new THREE.Color("#D2691E");  // Chocolate
    
    const randomHoneyColor = () => {
      const colorChoice = Math.random();
      let c;
      
      // Distribute colors more evenly with better honey shades
      if (colorChoice < 0.30) {
        c = honey.clone(); // 30% bright honey
      } else if (colorChoice < 0.55) {
        c = goldenBr.clone(); // 25% golden brown  
      } else if (colorChoice < 0.75) {
        c = lightHoney.clone(); // 20% light honey
      } else if (colorChoice < 0.90) {
        c = deepAmber.clone(); // 15% deep amber
      } else {
        c = darkAmber.clone(); // 10% dark amber
      }
      
      // Add slight variation to avoid uniformity
      const hsl = {};
      c.getHSL(hsl);
      hsl.h += (Math.random() - 0.5) * 0.03; // Slightly more hue variation
      hsl.s = THREE.MathUtils.clamp(hsl.s + (Math.random() - 0.5) * 0.1, 0.3, 1); // Ensure good saturation
      hsl.l = THREE.MathUtils.clamp(hsl.l + (Math.random() - 0.5) * 0.1, 0.2, 0.9); // Prevent too dark/light
      c.setHSL(hsl.h, hsl.s, hsl.l);
      return c;
    };
    
    const setHiveTargets = () => {
      const radiusBase = 7.5;
      for (let i = 0; i < this.COUNT; i++) {
        const a = i * 0.03;
        const r = radiusBase + 0.9 * Math.sin(i * 0.015);
        const y = Math.sin(i * 0.008) * 1.6;
        
        this.targets[i * 3 + 0] = Math.cos(a) * r;
        this.targets[i * 3 + 1] = y;
        this.targets[i * 3 + 2] = Math.sin(a) * r;
      }
    };
    
    for (let i = 0; i < this.COUNT; i++) {
      this.positions[i * 3 + 0] = (Math.random() - 0.5) * 30;
      this.positions[i * 3 + 1] = (Math.random() - 0.5) * 18;
      this.positions[i * 3 + 2] = (Math.random() - 0.5) * 30;
      
      this.velocities[i * 3 + 0] = (Math.random() - 0.5) * 0.02;
      this.velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
      this.velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
      
      const c = randomHoneyColor();
      this.colors[i * 3 + 0] = c.r;
      this.colors[i * 3 + 1] = c.g;
      this.colors[i * 3 + 2] = c.b;
      // Store base color for wave modulation
      this.baseColors[i * 3 + 0] = c.r;
      this.baseColors[i * 3 + 1] = c.g;
      this.baseColors[i * 3 + 2] = c.b;
    }
    setHiveTargets();
    
    this.geo = new THREE.BufferGeometry();
    this.geo.setAttribute("position", new THREE.BufferAttribute(this.positions, 3));
    this.geo.setAttribute("color", new THREE.BufferAttribute(this.colors, 3));
    
    this.mat = new THREE.PointsMaterial({
      size: this.BASE_POINT_SIZE,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    
    this.bees = new THREE.Points(this.geo, this.mat);
    this.scene.add(this.bees);
  },
  
  /**
   * Setup integration with quiz speech synthesis
   */
  setupSpeechIntegration() {
    // Listen for speech synthesis events from quiz
    window.addEventListener('quiz-speech-start', () => {
      this.isActive = true;
      console.log('🐝 Speech started - activating bee swarm');
    });
    
    window.addEventListener('quiz-speech-end', () => {
      this.isActive = false;
      console.log('🐝 Speech ended - calming bee swarm');
    });
    
    // Monitor global speech synthesis state
    if (typeof speechSynthesis !== 'undefined') {
      setInterval(() => {
        this.updateSpeechAmplitude();
      }, 50);
    }
  },
  
  /**
   * Update amplitude based on speech synthesis state
   */
  updateSpeechAmplitude() {
    if (typeof speechSynthesis === 'undefined') {
      this.amplitude = 0;
      return;
    }
    
    // Check if speech is currently active
    const isSpeaking = speechSynthesis.speaking;
    
    if (isSpeaking && this.isActive) {
      // Simulate amplitude based on speech activity
      this.amplitude = 0.3 + Math.sin(Date.now() * 0.008) * 0.2;
    } else {
      // Gradually fade amplitude
      this.amplitude *= 0.95;
    }
  },
  
  swarmStep(time) {
    const posAttr = this.geo.getAttribute("position");
    
    // Faster response to voice with less smoothing
    this.ampSmooth = this.ampSmooth * 0.7 + this.amplitude * 0.3;
    
    // More dramatic voice influence on swarm behavior
    const attractStrength = this.tSpeedBase + this.ampSmooth * 0.18;
    const noiseStrength = this.noiseBase + this.ampSmooth * 0.45;
    const buzzStrength = this.buzzBase + this.ampSmooth * 0.04;
    
    for (let i = 0; i < this.COUNT; i++) {
      const ix = i * 3;
      
      const px = this.positions[ix + 0];
      const py = this.positions[ix + 1];
      const pz = this.positions[ix + 2];
      
      const tx = this.targets[ix + 0];
      const ty = this.targets[ix + 1];
      const tz = this.targets[ix + 2];
      
      let vx = this.velocities[ix + 0];
      let vy = this.velocities[ix + 1];
      let vz = this.velocities[ix + 2];
      
      vx += (tx - px) * attractStrength;
      vy += (ty - py) * attractStrength;
      vz += (tz - pz) * attractStrength;
      
      const n1 = Math.sin(time * 0.001 + px * 0.7 + i * 0.0007);
      const n2 = Math.cos(time * 0.0013 + pz * 0.7 + i * 0.0009);
      const n3 = Math.sin(time * 0.0011 + py * 0.9 + i * 0.0005);
      
      vx += n1 * noiseStrength;
      vy += n3 * noiseStrength * 0.65;
      vz += n2 * noiseStrength;
      
      vx += (Math.random() - 0.5) * buzzStrength;
      vy += (Math.random() - 0.5) * buzzStrength;
      vz += (Math.random() - 0.5) * buzzStrength;
      
      vx *= this.damp;
      vy *= this.damp;
      vz *= this.damp;
      
      this.positions[ix + 0] = px + vx;
      this.positions[ix + 1] = py + vy;
      this.positions[ix + 2] = pz + vz;
      
      this.velocities[ix + 0] = vx;
      this.velocities[ix + 1] = vy;
      this.velocities[ix + 2] = vz;
      
      posAttr.setXYZ(i, this.positions[ix + 0], this.positions[ix + 1], this.positions[ix + 2]);
    }
    
    posAttr.needsUpdate = true;
  },
  
  /**
   * Update particle colors based on speech activity
   */
  updateColors(time) {
    const waveSpeed = 0.003;
    const speechPulse = this.ampSmooth * 0.5;
    
    const colorAttr = this.geo.getAttribute("color");
    
    for (let i = 0; i < this.COUNT; i++) {
      const ix = i * 3;
      const px = this.positions[ix + 0];
      const py = this.positions[ix + 1];
      const pz = this.positions[ix + 2];
      
      // Distance from center for wave effect
      const dist = Math.sqrt(px * px + py * py + pz * pz);
      const wave = Math.sin(dist * 0.5 - time * waveSpeed) * 0.5 + 0.5;
      
      // Brightness modulation
      const brightness = 0.7 + (wave * speechPulse * 0.3);
      
      // Get base color and apply brightness
      const baseR = this.baseColors[ix + 0];
      const baseG = this.baseColors[ix + 1];
      const baseB = this.baseColors[ix + 2];
      
      colorAttr.setXYZ(i, 
        Math.min(1, baseR * brightness),
        Math.min(1, baseG * brightness),
        Math.min(1, baseB * brightness)
      );
    }
    
    colorAttr.needsUpdate = true;
    
    // Update particle size based on speech
    this.mat.size = this.BASE_POINT_SIZE * (1 + speechPulse * 0.3);
    this.mat.opacity = 0.8 + speechPulse * 0.2;
  },
  
  animate(time) {
    if (!this.scene) return;
    
    requestAnimationFrame((t) => this.animate(t));
    
    // Update amplitude from speech
    this.updateSpeechAmplitude();
    
    // Smooth amplitude
    this.ampSmooth = this.ampSmooth * 0.9 + this.amplitude * 0.1;
    
    // Update swarm dynamics
    this.swarmStep(time);
    
    // Update colors based on speech activity
    this.updateColors(time);
    
    // Render the scene
    this.renderer.render(this.scene, this.camera);
  },
  
  destroy() {
    if (this.renderer) {
      this.renderer.domElement.remove();
      this.renderer.dispose();
    }
    if (this.geo) this.geo.dispose();
    if (this.mat) this.mat.dispose();
  }
};

export default BeeSwarmVisualizer;
