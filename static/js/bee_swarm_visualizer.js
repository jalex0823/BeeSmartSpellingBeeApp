/**
 * Bee Swarm Voice Visualizer
 * Dense bee-swarm mouth shape that expands/contracts with speech amplitude.
 * Uses soft bee-dot sprites for realistic particle appearance.
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
  COUNT: 5000,
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

  BASE_POINT_SIZE: 0.35,  // Larger particles so bees are visible (not lines)

  // Animation parameters - SIGNIFICANTLY increased for dramatic movement
  tSpeedBase: 0.08,      // Much faster attraction to target shape
  noiseBase: 0.025,      // Strong breathing motion for organic feel
  buzzBase: 0.004,       // More random buzz movement
  damp: 0.92,            // Less damping for fluid, bouncy motion

  // swarm expansion state
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
    console.log("🐝 Bee swarm visualizer initialized (3D swarm cloud)");

    return this;
  },

  initScene(container) {
    this.scene = new THREE.Scene();

    const rect = container.getBoundingClientRect();
    const width = rect.width || window.innerWidth || 860;
    const height = rect.height || window.innerHeight || 260;
    
    console.log('🎬 BeeSwarmVisualizer scene dimensions:', { width, height });

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
    
    console.log('✅ Canvas appended, size:', this.renderer.domElement.width, 'x', this.renderer.domElement.height);

    window.addEventListener("resize", () => {
      const r = container.getBoundingClientRect();
      const w = r.width || window.innerWidth || 860;
      const h = r.height || window.innerHeight || 260;

      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
  },

  // create a soft circular "bee dot" sprite so particles don't look like lines
  makeBeeTexture() {
    const size = 64;
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const ctx = c.getContext("2d");

    const grd = ctx.createRadialGradient(
      size/2, size/2, 0,
      size/2, size/2, size/2
    );
    grd.addColorStop(0, "rgba(255,255,255,1)");
    grd.addColorStop(0.35, "rgba(255,255,255,0.9)");
    grd.addColorStop(1, "rgba(255,255,255,0)");

    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.arc(size/2, size/2, size/2, 0, Math.PI*2);
    ctx.fill();

    const tex = new THREE.CanvasTexture(c);
    tex.needsUpdate = true;
    return tex;
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
    // FILLED mouth swarm: upper lip + lower lip + inner volume (not just two lines!)
    const buildMouthTargets = (openFactor, outArray) => {
      const mouthWidth = 5.8;
      const lipCurve = 0.9;
      const maxOpen = 2.4 * openFactor;

      for (let i = 0; i < this.COUNT; i++) {
        const u = i / this.COUNT; // 0..1 across mouth
        const x = (u - 0.5) * mouthWidth + (Math.random() - 0.5) * 0.35;

        // smile curve (gentle arc)
        const smileCurve = -Math.cos(u * Math.PI * 2) * lipCurve * 0.45;

        const bandPick = Math.random();

        let y;
        if (bandPick < 0.35) {
          // upper lip band with thickness
          y = smileCurve + (maxOpen * 0.55) + (Math.random() - 0.5) * 0.35;
        } else if (bandPick < 0.70) {
          // lower lip band with thickness
          y = smileCurve - (maxOpen * 0.55) + (Math.random() - 0.5) * 0.35;
        } else {
          // inner swarm volume (fills mouth)
          y = smileCurve + (Math.random() - 0.5) * maxOpen * 0.9;
        }

        // 3D depth — thicker in center, thinner at edges
        const centerBias = 1.0 - Math.abs(u - 0.5) * 2;
        const z = (Math.random() - 0.5) * 1.2 * (0.35 + centerBias * 0.65);

        outArray[i * 3 + 0] = x;
        outArray[i * 3 + 1] = y;
        outArray[i * 3 + 2] = z;
      }
    };

    buildMouthTargets(0.45, this.targetsClosed);  // Subtle closed mouth
    buildMouthTargets(1.0, this.targetsOpen);     // Wide open mouth

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
      opacity: 0.95,  // More opaque for better visibility
      depthWrite: false,
      blending: THREE.AdditiveBlending,  // Additive blending for glowing effect
      map: this.makeBeeTexture(),  // Soft bee-dot sprite
      alphaTest: 0.02
    });

    this.bees = new THREE.Points(this.geo, this.mat);
    this.scene.add(this.bees);
  },

  // interpolate between closed/open mouth targets every frame
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
      // More dramatic amplitude with faster, varied oscillation
      const time = Date.now() * 0.015;  // Faster movement
      const wave1 = Math.sin(time);
      const wave2 = Math.sin(time * 1.7) * 0.5;
      const wave3 = Math.sin(time * 2.3) * 0.3;
      this.amplitude = 0.5 + (wave1 + wave2 + wave3) * 0.4;  // Range: 0.1 to 0.9
    } else {
      this.amplitude *= 0.85;  // Faster decay when not speaking
    }
  },

  swarmStep(time) {
    const posAttr = this.geo.getAttribute("position");

    // Faster amplitude smoothing for more responsive movement
    this.ampSmooth = this.ampSmooth * 0.6 + this.amplitude * 0.4;

    // mouth opening target - much more dramatic
    this.mouthPulse *= 0.80;  // Faster pulse decay
    const targetOpen = THREE.MathUtils.clamp(
      this.ampSmooth * 1.5 + this.mouthPulse * 0.8,  // Much more responsive
      0, 1
    );

    // Bouncy swarm physics - expands and contracts with speech
    const stiffness = 0.35;  // Very responsive spring
    const damping = 0.70;    // Less damping for bouncier motion
    this.mouthOpenVel = this.mouthOpenVel * damping + (targetOpen - this.mouthOpen) * stiffness;
    this.mouthOpen += this.mouthOpenVel;

    this.updateMouthTargets(this.mouthOpen);

    const attractStrength = this.tSpeedBase + this.ampSmooth * 0.25;  // Much stronger speech-driven attraction
    const noiseStrength   = this.noiseBase + this.ampSmooth * 0.08;   // Strong breathing motion
    const buzzStrength    = this.buzzBase  + this.ampSmooth * 0.01;   // More buzz energy

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
