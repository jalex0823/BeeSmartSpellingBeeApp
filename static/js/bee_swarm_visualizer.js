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
  analyser: null,
  audioData: null,
  audioStarted: false,
  amplitude: 0,
  ampSmooth: 0,
  
  // Particle data
  COUNT: 25000,
  positions: null,
  velocities: null,
  targets: null,
  colors: null,
  geo: null,
  mat: null,
  BASE_POINT_SIZE: 0.13,
  
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
      autoStart: false,
      showControls: true,
      particleCount: 25000,
      background: '#050505',
      zIndex: 0,
      ...options
    };
    
    this.COUNT = opts.particleCount;
    
    // Setup scene
    this.initScene(container, opts);
    this.initParticles();
    this.animate(0);
    
    if (opts.showControls) {
      this.addControls(container);
    }
    
    if (opts.autoStart) {
      this.startMic();
    }
    
    return this;
  },
  
  initScene(container, opts) {
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(parseInt(opts.background.replace('#', '0x')), 0.07);
    
    this.camera = new THREE.PerspectiveCamera(
      60, container.clientWidth / container.clientHeight, 0.1, 200
    );
    this.camera.position.set(0, 0, 24);
    
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.domElement.style.position = 'absolute';
    this.renderer.domElement.style.top = '0';
    this.renderer.domElement.style.left = '0';
    this.renderer.domElement.style.zIndex = opts.zIndex;
    this.renderer.domElement.style.pointerEvents = 'none';
    container.appendChild(this.renderer.domElement);
    
    // Resize handler
    window.addEventListener("resize", () => {
      this.camera.aspect = container.clientWidth / container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(container.clientWidth, container.clientHeight);
    });
    
    // Subtle background stars
    const starGeo = new THREE.BufferGeometry();
    const N = 1200;
    const pos = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pos[i * 3 + 0] = (Math.random() - 0.5) * 160;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 160;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 160;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const starMat = new THREE.PointsMaterial({ size: 0.25, transparent: true, opacity: 0.25 });
    const stars = new THREE.Points(starGeo, starMat);
    this.scene.add(stars);
  },
  
  initParticles() {
    this.positions = new Float32Array(this.COUNT * 3);
    this.velocities = new Float32Array(this.COUNT * 3);
    this.targets = new Float32Array(this.COUNT * 3);
    this.colors = new Float32Array(this.COUNT * 3);
    this.baseColors = new Float32Array(this.COUNT * 3); // Store original honey shades
    
    // Honey / golden brown palette
    const honey = new THREE.Color("#FFD540");
    const goldenBr = new THREE.Color("#B86B1A");
    const darkAmber = new THREE.Color("#7A3E00");
    
    const randomHoneyColor = () => {
      const t = Math.random();
      let c = honey.clone();
      if (t < 0.70) c.lerp(goldenBr, t / 0.70);
      else c.lerp(darkAmber, (t - 0.70) / 0.30);
      
      const hsl = {};
      c.getHSL(hsl);
      hsl.h += (Math.random() - 0.5) * 0.02;
      hsl.s = THREE.MathUtils.clamp(hsl.s + (Math.random() - 0.5) * 0.08, 0, 1);
      hsl.l = THREE.MathUtils.clamp(hsl.l + (Math.random() - 0.5) * 0.08, 0, 1);
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
  
  async startMic() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaStreamSource(stream);
      
      this.analyser = ctx.createAnalyser();
      this.analyser.fftSize = 1024;
      this.audioData = new Uint8Array(this.analyser.frequencyBinCount);
      
      src.connect(this.analyser);
      this.audioStarted = true;
      return true;
    } catch (e) {
      console.error('Mic permission denied or unavailable:', e);
      return false;
    }
  },
  
  updateAmplitude() {
    if (!this.audioStarted) {
      this.amplitude = 0;
      return;
    }
    this.analyser.getByteTimeDomainData(this.audioData);
    
    let sum = 0;
    for (let i = 0; i < this.audioData.length; i++) {
      const v = (this.audioData[i] - 128) / 128;
      sum += v * v;
    }
    const rms = Math.sqrt(sum / this.audioData.length);
    // Increased sensitivity for more dramatic voice response
    this.amplitude = THREE.MathUtils.clamp(rms * 4.5, 0, 1);
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
  
  pulseStep(time) {
    // Radial wave that pulses from center outward and back
    const waveSpeed = 0.002;
    // Stronger audio pulse influence for more dramatic voice sync
    const audioPulse = this.ampSmooth * 0.6;
    
    const posAttr = this.geo.getAttribute("position");
    const colorAttr = this.geo.getAttribute("color");
    
    for (let i = 0; i < this.COUNT; i++) {
      const ix = i * 3;
      const px = this.positions[ix + 0];
      const py = this.positions[ix + 1];
      const pz = this.positions[ix + 2];
      
      // Distance from center (0,0,0)
      const dist = Math.sqrt(px * px + py * py + pz * pz);
      
      // Wave travels outward based on distance and time
      const wave = Math.sin(dist * 0.3 - time * waveSpeed) * 0.5 + 0.5;
      const pulse = wave * (1 + audioPulse);
      
      // Modulate brightness based on wave while keeping base honey shade
      // Increased brightness range for more dramatic voice response
      const brightness = 0.4 + pulse * 0.6;
      const baseR = this.baseColors[ix + 0];
      const baseG = this.baseColors[ix + 1];
      const baseB = this.baseColors[ix + 2];
      
      colorAttr.setXYZ(i, 
        baseR * brightness,
        baseG * brightness,
        baseB * brightness
      );
    }
    
    colorAttr.needsUpdate = true;
    
    // More dramatic size pulsing in sync with voice
    this.mat.size = this.BASE_POINT_SIZE * (1 + audioPulse * 0.25);
    this.mat.opacity = 0.70 + audioPulse * 0.15;
  },
  
  animate(time) {
    requestAnimationFrame((t) => this.animate(t));
    
    this.updateAmplitude();
    this.swarmStep(time);
    this.pulseStep(time);
    
    this.camera.position.x = Math.sin(time * 0.0002) * 0.8;
    this.camera.position.y = Math.cos(time * 0.0002) * 0.6;
    this.camera.lookAt(0, 0, 0);
    
    this.renderer.render(this.scene, this.camera);
  },
  
  addControls(container) {
    const ui = document.createElement('div');
    ui.style.cssText = `
      position: fixed; inset: 16px auto auto 16px; z-index: 10;
      display:flex; gap:8px; align-items:center;
      background:rgba(0,0,0,.5); padding:10px 12px; border-radius:12px;
      color:#fff; backdrop-filter: blur(6px);
    `;
    
    const btn = document.createElement('button');
    btn.id = 'beeSwarmStartBtn';
    btn.textContent = 'Start Mic';
    btn.style.cssText = `
      border:0; padding:8px 12px; border-radius:10px; cursor:pointer;
      background:#FFD540; color:#2b1a00; font-weight:700;
      box-shadow:0 0 0 2px rgba(255,213,64,.2) inset;
    `;
    btn.onclick = async () => {
      const success = await this.startMic();
      if (success) {
        btn.textContent = 'Mic Live ✅';
      } else {
        alert('Mic permission denied or unavailable.');
      }
    };
    
    const ampChip = document.createElement('span');
    ampChip.id = 'beeSwarmAmpChip';
    ampChip.className = 'chip';
    ampChip.style.cssText = 'font-size:12px; opacity:.8;';
    ampChip.textContent = 'amp: 0.00';
    
    const modeChip = document.createElement('span');
    modeChip.className = 'chip';
    modeChip.style.cssText = 'font-size:12px; opacity:.8;';
    modeChip.textContent = '🐝 Bee Swarm Mode';
    
    ui.appendChild(btn);
    ui.appendChild(ampChip);
    ui.appendChild(modeChip);
    container.appendChild(ui);
    
    // Update amplitude display
    setInterval(() => {
      if (ampChip) {
        ampChip.textContent = `amp: ${this.amplitude.toFixed(2)}`;
      }
    }, 100);
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
