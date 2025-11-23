/**
 * Bee Swarm Voice Visualizer (Mouth Morph Edition)
 * Compact mouth shape that opens/closes with speech amplitude.
 * Uses global THREE from base.html to avoid multiple Three.js imports
 */
// Use global THREE instead of importing to avoid conflicts
const THREE = window.THREE;

const BeeSwarmVisualizer = {
  scene: null,
  camera: null,
  renderer: null,
  bees: null,
  container: null,

  amplitude: 0,
  ampSmooth: 0,
  isActive: false,

  // particle data
  COUNT: 8000,
  positions: null,
  velocities: null,

  // targets
  targets: null,
  targetsClosed: null,
  targetsOpen: null,

  colors: null,
  baseColors: null,
  geo: null,
  mat: null,

  BASE_POINT_SIZE: 0.15,  // Slightly larger particles for better visibility

  // Animation parameters - increased for more dynamic movement
  tSpeedBase: 0.05,      // Faster attraction to target shape (was 0.03)
  noiseBase: 0.012,      // More breathing motion (was 0.006)
  buzzBase: 0.002,       // More random buzz movement (was 0.0012)
  damp: 0.95,            // Less damping for more fluid motion (was 0.965)

  // mouth morph state
  mouthOpen: 0,        // 0..1
  mouthOpenVel: 0,
  mouthPulse: 0,       // snaps on boundaries

  init(container, options = {}) {
    const opts = {
      autoStart: true,
      showControls: false,
      particleCount: 8000,
      background: "transparent",
      zIndex: 1,
      ...options
    };

    this.container = container;
    this.COUNT = opts.particleCount;

    this.initScene(container);
    this.initParticles();
    this.animate(0);

    this.setupSpeechIntegration();
    console.log("🐝 Bee swarm visualizer initialized (mouth morph ON)");

    return this;
  },

  initScene(container) {
    this.scene = new THREE.Scene();

    const rect = container.getBoundingClientRect();
    const width = rect.width || 860;
    const height = rect.height || 260;

    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, 0, 15);

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      premultipliedAlpha: false
    });

    this.renderer.setSize(width, height);
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));

    this.renderer.domElement.style.position = "absolute";
    this.renderer.domElement.style.inset = "0";
    this.renderer.domElement.style.pointerEvents = "none";
    this.renderer.domElement.style.zIndex = "1";

    container.appendChild(this.renderer.domElement);

    window.addEventListener("resize", () => {
      const r = container.getBoundingClientRect();
      const w = r.width || 860;
      const h = r.height || 260;

      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
  },

  initParticles() {
    this.positions = new Float32Array(this.COUNT * 3);
    this.velocities = new Float32Array(this.COUNT * 3);

    this.targets = new Float32Array(this.COUNT * 3);
    this.targetsClosed = new Float32Array(this.COUNT * 3);
    this.targetsOpen = new Float32Array(this.COUNT * 3);

    this.colors = new Float32Array(this.COUNT * 3);
    this.baseColors = new Float32Array(this.COUNT * 3);

    // Honey palette
    const honey = new THREE.Color("#FFD540");
    const goldenBr = new THREE.Color("#B86B1A");
    const darkAmber = new THREE.Color("#8B4513");
    const lightHoney = new THREE.Color("#FFF8DC");
    const deepAmber = new THREE.Color("#D2691E");

    const randomHoneyColor = () => {
      const r = Math.random();
      let c;
      if (r < 0.30) c = honey.clone();
      else if (r < 0.55) c = goldenBr.clone();
      else if (r < 0.75) c = lightHoney.clone();
      else if (r < 0.90) c = deepAmber.clone();
      else c = darkAmber.clone();

      const hsl = {};
      c.getHSL(hsl);
      hsl.h += (Math.random() - 0.5) * 0.02;
      hsl.s = THREE.MathUtils.clamp(hsl.s + (Math.random() - 0.5) * 0.08, 0.35, 1);
      hsl.l = THREE.MathUtils.clamp(hsl.l + (Math.random() - 0.5) * 0.08, 0.25, 0.9);
      c.setHSL(hsl.h, hsl.s, hsl.l);
      return c;
    };

    // --- Build CLOSED and OPEN mouth targets ---
    const buildMouthTargets = (openFactor, outArray) => {
      const mouthWidth = 6.0;
      const lipCurve = 0.9;
      const maxOpen = 2.2 * openFactor;

      const layers = 8; // More layers for better depth
      const perLayer = Math.floor(this.COUNT / layers);

      for (let i = 0; i < this.COUNT; i++) {
        const layer = Math.floor(i / perLayer);
        const layerT = layer / (layers - 1);

        const u = (i % perLayer) / (perLayer - 1); // 0..1
        const x = (u - 0.5) * mouthWidth;

        const smile = -Math.cos(u * Math.PI) * lipCurve * 0.22;

        const isUpper = layerT < 0.5;
        const lipSide = isUpper ? 1 : -1;
        const lipBlend = isUpper ? layerT / 0.5 : (layerT - 0.5) / 0.5;
        const spread = maxOpen * lipBlend;

        const y = smile + lipSide * spread + (Math.random() - 0.5) * 0.08;
        const z = (Math.random() - 0.5) * 0.8; // More depth variation

        outArray[i * 3 + 0] = x;
        outArray[i * 3 + 1] = y;
        outArray[i * 3 + 2] = z;
      }
    };

    buildMouthTargets(0.35, this.targetsClosed);  // Increased from 0.04 to 0.35 for visible closed state
    buildMouthTargets(1.0, this.targetsOpen);

    // start particles near center so shape forms fast
    for (let i = 0; i < this.COUNT; i++) {
      const ix = i * 3;

      this.positions[ix + 0] = (Math.random() - 0.5) * 3.2;
      this.positions[ix + 1] = (Math.random() - 0.5) * 1.6;
      this.positions[ix + 2] = (Math.random() - 0.5) * 1.0;

      this.velocities[ix + 0] = (Math.random() - 0.5) * 0.01;
      this.velocities[ix + 1] = (Math.random() - 0.5) * 0.01;
      this.velocities[ix + 2] = (Math.random() - 0.5) * 0.01;

      const c = randomHoneyColor();
      this.colors[ix + 0] = c.r;
      this.colors[ix + 1] = c.g;
      this.colors[ix + 2] = c.b;

      this.baseColors[ix + 0] = c.r;
      this.baseColors[ix + 1] = c.g;
      this.baseColors[ix + 2] = c.b;
    }

    // start closed
    this.targets.set(this.targetsClosed);

    this.geo = new THREE.BufferGeometry();
    this.geo.setAttribute("position", new THREE.BufferAttribute(this.positions, 3));
    this.geo.setAttribute("color", new THREE.BufferAttribute(this.colors, 3));

    this.mat = new THREE.PointsMaterial({
      size: this.BASE_POINT_SIZE,
      vertexColors: true,
      transparent: true,
      opacity: 0.92,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });

    this.bees = new THREE.Points(this.geo, this.mat);
    this.scene.add(this.bees);
  },

  // interpolate between closed/open targets every frame
  updateMouthTargets(openAmount) {
    const o = THREE.MathUtils.clamp(openAmount, 0, 1);
    for (let i = 0; i < this.COUNT * 3; i++) {
      const a = this.targetsClosed[i];
      const b = this.targetsOpen[i];
      this.targets[i] = a + (b - a) * o;
    }
  },

  setupSpeechIntegration() {
    window.addEventListener("quiz-speech-start", () => {
      this.isActive = true;
    });

    window.addEventListener("quiz-speech-end", () => {
      this.isActive = false;
    });

    // Optional sharp syncing if you dispatch this in quiz speech onboundary
    window.addEventListener("quiz-speech-boundary", () => {
      this.mouthPulse = 1.0;
    });

    if (typeof speechSynthesis !== "undefined") {
      setInterval(() => this.updateSpeechAmplitude(), 50);
    }
  },

  updateSpeechAmplitude() {
    if (typeof speechSynthesis === "undefined") {
      this.amplitude = 0;
      return;
    }

    const isSpeaking = speechSynthesis.speaking;
    if (isSpeaking && this.isActive) {
      this.amplitude = 0.32 + Math.sin(Date.now() * 0.01) * 0.22;
    } else {
      this.amplitude *= 0.92;
    }
  },

  swarmStep(time) {
    const posAttr = this.geo.getAttribute("position");

    // smoother amplitude
    this.ampSmooth = this.ampSmooth * 0.7 + this.amplitude * 0.3;  // Faster response (was 0.75/0.25)

    // mouth opening target
    this.mouthPulse *= 0.85;  // Slightly faster pulse decay (was 0.88)
    const targetOpen = THREE.MathUtils.clamp(
      this.ampSmooth * 1.3 + this.mouthPulse * 0.7,  // More responsive (was 1.15/0.6)
      0, 1
    );

    // smooth mouth motion with more responsive physics
    const stiffness = 0.25;  // More responsive spring (was 0.18)
    const damping = 0.75;    // Better damping (was 0.7)
    this.mouthOpenVel = this.mouthOpenVel * damping + (targetOpen - this.mouthOpen) * stiffness;
    this.mouthOpen += this.mouthOpenVel;

    this.updateMouthTargets(this.mouthOpen);

    const attractStrength = this.tSpeedBase + this.ampSmooth * 0.18;  // Stronger speech-based attraction (was 0.12)
    const noiseStrength   = this.noiseBase + this.ampSmooth * 0.05;   // More breathing motion (was 0.03)
    const buzzStrength    = this.buzzBase  + this.ampSmooth * 0.006;  // More buzz energy (was 0.004)

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

      // pull into mouth shape
      vx += (tx - px) * attractStrength;
      vy += (ty - py) * attractStrength;
      vz += (tz - pz) * attractStrength;

      // tight breathing noise
      const n1 = Math.sin(time * 0.001 + px * 0.9 + i * 0.0009);
      const n2 = Math.cos(time * 0.0012 + pz * 0.9 + i * 0.0011);
      const n3 = Math.sin(time * 0.0011 + py * 1.0 + i * 0.0008);

      vx += n1 * noiseStrength;
      vy += n3 * noiseStrength * 0.6;
      vz += n2 * noiseStrength;

      // tiny buzz
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

  updateColors(time) {
    const waveSpeed = 0.003;
    const speechPulse = this.ampSmooth * 0.55;
    const colorAttr = this.geo.getAttribute("color");

    for (let i = 0; i < this.COUNT; i++) {
      const ix = i * 3;
      const px = this.positions[ix + 0];
      const py = this.positions[ix + 1];
      const pz = this.positions[ix + 2];

      const dist = Math.sqrt(px * px + py * py + pz * pz);
      const wave = Math.sin(dist * 0.65 - time * waveSpeed) * 0.5 + 0.5;

      const brightness = 0.75 + (wave * speechPulse * 0.25);

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
    this.mat.size = this.BASE_POINT_SIZE * (1 + speechPulse * 0.25);
    this.mat.opacity = 0.86 + speechPulse * 0.14;
  },

  animate(time) {
    if (!this.scene) return;
    requestAnimationFrame((t) => this.animate(t));

    this.updateSpeechAmplitude();
    this.ampSmooth = this.ampSmooth * 0.9 + this.amplitude * 0.1;

    this.swarmStep(time);
    this.updateColors(time);

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
