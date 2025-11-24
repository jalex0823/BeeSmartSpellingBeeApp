/**
 * Honey Bokeh Lips Visualizer - CLEAN IMPLEMENTATION
 * Builds a particle mouth silhouette from a mask image and reacts to speech.
 */
const THREE = window.THREE;

const BeeSwarmVisualizer = {
  init(container, options = {}) {
    const opts = {
      autoStart: true,
      particleCount: 7000, // lighter default to reduce GPU/CPU load
      overallScale: 2.6,
      cameraZ: 7.2,
      zIndex: 2,
      background: 'transparent',
      // Use the in-repo visualizer mask (clean lip mask) for sampling
      maskUrl: '/static/assets/masks/lips_mask_double.png',
      sampleStep: 3,
      maskBrightnessThreshold: 60,
      maskInvert: false,
      lazyInit: true, // defer mask + particle build until first speech start
      ...options
    };

    // Performance heuristics fallback
    const lowPerf = (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 6) ||
                    (window.devicePixelRatio && window.devicePixelRatio < 1.25) ||
                    (window.innerWidth < 640);
    if (lowPerf) {
      opts.particleCount = Math.min(opts.particleCount, 6000);
      opts.sampleStep = Math.max(opts.sampleStep, 3);
    }

    const viz = {
      // config/state
      container,
      COUNT: opts.particleCount,
      // Use frame-driven amplitude updates on high-performance devices to reduce timers
      _useFrameAmplitude: !lowPerf,
      overallScale: opts.overallScale,
      cameraZ: opts.cameraZ,
      maskThreshold: opts.maskBrightnessThreshold,
      maskInvert: opts.maskInvert,
      amplitude: 0,
      ampSmooth: 0,
      isActive: false,
      mouthOpen: 0,
      mouthOpenVel: 0,
      mouthPulse: 0,
      // motion params
      tSpeedBase: 0.08,
      noiseBase: 0.025,
      buzzBase: 0.004,
      damp: 0.92,
      // buffers
      positions: null,
      velocities: null,
      targets: null,
      targetsClosed: null,
      targetsOpen: null,
      colors: null,
      sizes: null,
      phases: null,
      geo: null,
      mat: null,
      scene: null,
      camera: null,
      renderer: null,
      ready: false,
      _glyphTex: null,
      _glyphGrid: null,

      createGlyphAtlas(){
        if(this._glyphTex) return this._glyphTex;
        const letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const cols=6;
        const size=64;
        const rows=Math.ceil(letters.length/cols);
        const canvas=document.createElement('canvas');
        canvas.width=cols*size;
        canvas.height=rows*size;
        const ctx=canvas.getContext('2d');
        ctx.fillStyle='rgba(0,0,0,0)';
        ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.fillStyle='#fff';
        ctx.textAlign='center';
        ctx.textBaseline='middle';
        ctx.font='bold 48px Arial';
        for(let i=0;i<letters.length;i++){
          const c=letters[i];
          const col=i%cols;
          const row=Math.floor(i/cols);
          ctx.fillText(c,col*size+size/2,row*size+size/2+4);
        }
        const tex=new THREE.CanvasTexture(canvas);
        tex.needsUpdate=true;
        tex.minFilter=THREE.LinearFilter;
        tex.magFilter=THREE.LinearFilter;
        this._glyphTex=tex;
        this._glyphGrid={x:cols,y:rows,count:letters.length};
        return tex;
      },

      initThree() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(55, 1, 0.1, 1000);
        this.camera.position.z = this.cameraZ;
        this.renderer = new THREE.WebGLRenderer({ alpha:true, antialias:true });
        this.renderer.setClearColor(0x000000, 0);
        const r = container.getBoundingClientRect();
        const w = r.width || window.innerWidth || 860;
        const h = r.height || window.innerHeight || 260;
        this.camera.aspect = w/h; this.camera.updateProjectionMatrix();
        this.renderer.setSize(w,h);
        const el = this.renderer.domElement;
        el.style.position='absolute'; 
        el.style.inset=0; 
        el.style.pointerEvents='none'; 
        el.style.zIndex=opts.zIndex;
        
        // ✅ Prevent white flash - hide until first render
        el.style.background = 'transparent';
        el.style.opacity = '0';
        el.style.visibility = 'hidden';
        el.style.transition = 'opacity 450ms ease';
        
        container.appendChild(el);
        window.addEventListener('resize', () => {
          const r2 = container.getBoundingClientRect();
          const w2 = r2.width || window.innerWidth || 860;
          const h2 = r2.height || window.innerHeight || 260;
          this.camera.aspect = w2/h2; this.camera.updateProjectionMatrix();
          this.renderer.setSize(w2,h2);
        });
      },

      async buildTargetsFromMask(maskUrl, sampleStep){
        const img = new Image(); img.crossOrigin='anonymous'; img.src = maskUrl;
        try { await img.decode(); } catch(e){ console.warn('Mask decode failed', e, maskUrl); return; }
        const canvas = document.createElement('canvas');
        const w = canvas.width = img.width || 512;
        const h = canvas.height = img.height || 256;
        const ctx = canvas.getContext('2d'); ctx.drawImage(img,0,0,w,h);
        const data = ctx.getImageData(0,0,w,h).data;
        // Persist pixel data for dynamic rebuilds (threshold tuning)
        this._maskPixels = { data, w, h };
        const threshold = typeof this.maskThreshold === 'number' ? this.maskThreshold : 60;
        const pts = [];
        for (let y=0;y<h;y+=sampleStep){
          for (let x=0;x<w;x+=sampleStep){
            const i=(y*w+x)*4; const r=data[i], g=data[i+1], b=data[i+2], a=data[i+3];
            const bright = (r+g+b)/3;
            const alphaOK = a > 40;
            const lit = alphaOK && bright>=threshold; const include = this.maskInvert ? !lit : lit;
            if(include) pts.push({x,y});
          }
        }
        if(!pts.length) console.warn('Mask produced no points; procedural fallback');
        this.targetsClosed = new Float32Array(this.COUNT*3);
        this.targetsOpen   = new Float32Array(this.COUNT*3);
        this.targets       = new Float32Array(this.COUNT*3);
        const toWorld = p => ({ x:(p.x/w - 0.5)*8.0, y:-(p.y/h - 0.5)*4.0 });
        const openStretch=1.0, closedStretch=0.35;
        if (pts.length){
          for(let i=0;i<this.COUNT;i++){
            const p=pts[i%pts.length]; const wp=toWorld(p); const u=p.x/w; const centerBias=1-Math.abs(u-0.5)*2;
            const z=(Math.random()-0.5)*1.4*(0.25+centerBias*0.75); const s=this.overallScale;
            this.targetsClosed[i*3]=wp.x*s; this.targetsClosed[i*3+1]=wp.y*s*closedStretch; this.targetsClosed[i*3+2]=z;
            this.targetsOpen[i*3]=wp.x*s; this.targetsOpen[i*3+1]=wp.y*s*openStretch; this.targetsOpen[i*3+2]=z;
          }
        } else {
          const mouthWidth=5.8, lipCurve=0.9;
          const build=(openFactor,out)=>{
            const maxOpen=2.4*openFactor;
            for(let i=0;i<this.COUNT;i++){
              const u=i/this.COUNT; const x=(u-0.5)*mouthWidth+(Math.random()-0.5)*0.35; const smileCurve=-Math.cos(u*Math.PI*2)*lipCurve*0.45;
              const band=Math.random(); let y; if(band<0.35) y=smileCurve+(maxOpen*0.55)+(Math.random()-0.5)*0.85; else if(band<0.70) y=smileCurve-(maxOpen*0.55)+(Math.random()-0.5)*0.85; else y=smileCurve+(Math.random()-0.5)*maxOpen*0.9;
              const centerBias=1-Math.abs(u-0.5)*2; const z=(Math.random()-0.5)*1.2*(0.35+centerBias*0.65); const s=this.overallScale;
              out[i*3]=x*s; out[i*3+1]=y*s; out[i*3+2]=z*s;
            }
          };
          build(0.35,this.targetsClosed); build(1.0,this.targetsOpen);
        }
        this.targets.set(this.targetsClosed);
      },

      // Rebuild targets from stored pixel data with new threshold/sample settings
      rebuildFromStoredMask({ threshold = this.maskThreshold, sampleStep =  this._lastSampleStep || 2, invert = this.maskInvert } = {}) {
        if(!this._maskPixels) { console.warn('No stored mask pixels; cannot rebuild.'); return; }
        const { data, w, h } = this._maskPixels;
        this.maskThreshold = threshold; this.maskInvert = invert; this._lastSampleStep = sampleStep;
        const pts = [];
        for (let y=0; y<h; y+=sampleStep) {
          for (let x=0; x<w; x+=sampleStep) {
            const i=(y*w+x)*4; const r=data[i], g=data[i+1], b=data[i+2], a=data[i+3];
            const bright=(r+g+b)/3; const alphaOK = a>40; const lit=alphaOK && bright>=threshold; const include=invert? !lit : lit;
            if(include) pts.push({x,y});
          }
        }
        if(!pts.length){ console.warn('Rebuild produced zero points; keeping previous targets'); return; }
        this.targetsClosed = new Float32Array(this.COUNT*3);
        this.targetsOpen   = new Float32Array(this.COUNT*3);
        this.targets       = new Float32Array(this.COUNT*3);
        const toWorld = p => ({ x:(p.x/w - 0.5)*8.0, y:-(p.y/h - 0.5)*4.0 });
        const openStretch=1.0, closedStretch=0.35;
        for(let i=0;i<this.COUNT;i++){
          const p=pts[i%pts.length]; const wp=toWorld(p); const u=p.x/w; const centerBias=1-Math.abs(u-0.5)*2;
          const z=(Math.random()-0.5)*1.4*(0.25+centerBias*0.75); const s=this.overallScale;
          this.targetsClosed[i*3]=wp.x*s; this.targetsClosed[i*3+1]=wp.y*s*closedStretch; this.targetsClosed[i*3+2]=z;
          this.targetsOpen[i*3]=wp.x*s; this.targetsOpen[i*3+1]=wp.y*s*openStretch; this.targetsOpen[i*3+2]=z;
        }
        this.targets.set(this.targetsClosed);
      },

      // Switch performance mode (reinitializes particles with new count)
      setPerformanceMode(mode){
        const desired = mode==='low' ? 8000 : (mode==='high' ? 18000 : this.COUNT); // 'auto' leaves as-is
        if(desired === this.COUNT) return;
        // Dispose current geometry/material
        if(this.bees){ this.scene.remove(this.bees); }
        if(this.geo){ this.geo.dispose(); }
        if(this.mat){ this.mat.dispose(); }
        this.COUNT = desired;
        // Rebuild targets with current mask settings, or fallback procedural if mask isn't ready
        if (this._maskPixels) {
          this.rebuildFromStoredMask({ threshold: this.maskThreshold, sampleStep: this._lastSampleStep || 2, invert: this.maskInvert });
        } else {
          // Procedural fallback sized to COUNT (matches fallback in buildTargetsFromMask)
          this.targetsClosed = new Float32Array(this.COUNT*3);
          this.targetsOpen   = new Float32Array(this.COUNT*3);
          this.targets       = new Float32Array(this.COUNT*3);
          const mouthWidth=5.8, lipCurve=0.9;
          const build=(openFactor,out)=>{
            const maxOpen=2.4*openFactor;
            for(let i=0;i<this.COUNT;i++){
              const u=i/this.COUNT; const x=(u-0.5)*mouthWidth+(Math.random()-0.5)*0.35; const smileCurve=-Math.cos(u*Math.PI*2)*lipCurve*0.45;
              const band=Math.random(); let y; if(band<0.35) y=smileCurve+(maxOpen*0.55)+(Math.random()-0.5)*0.85; else if(band<0.70) y=smileCurve-(maxOpen*0.55)+(Math.random()-0.5)*0.85; else y=smileCurve+(Math.random()-0.5)*maxOpen*0.9;
              const centerBias=1-Math.abs(u-0.5)*2; const z=(Math.random()-0.5)*1.2*(0.35+centerBias*0.65); const s=this.overallScale;
              out[i*3]=x*s; out[i*3+1]=y*s; out[i*3+2]=z*s;
            }
          };
          build(0.35,this.targetsClosed); build(1.0,this.targetsOpen);
          this.targets.set(this.targetsClosed);
        }
        // Re-init particle buffers & points
        this.initParticles();
        console.log(`Performance mode switched to ${mode} (COUNT=${this.COUNT})`);
      },

      initParticles(){
        this.positions=new Float32Array(this.COUNT*3);
        this.velocities=new Float32Array(this.COUNT*3);
        this.colors=new Float32Array(this.COUNT*3);
        this.sizes=new Float32Array(this.COUNT);
        this.phases=new Float32Array(this.COUNT);
        this.glyphs=new Float32Array(this.COUNT);
        const palette=['#FDB813','#FFCC33','#FFB84D','#FFF6CC','#E08A00'].map(c=>new THREE.Color(c));
        const pick=()=>palette[Math.floor(Math.random()*palette.length)].clone();
        this.createGlyphAtlas();
        for(let i=0;i<this.COUNT;i++){
          const ix=i*3; this.positions[ix]=(Math.random()-0.5)*4.5; this.positions[ix+1]=(Math.random()-0.5)*2.0; this.positions[ix+2]=(Math.random()-0.5)*1.2;
          this.velocities[ix]=(Math.random()-0.5)*0.01; this.velocities[ix+1]=(Math.random()-0.5)*0.01; this.velocities[ix+2]=(Math.random()-0.5)*0.01;
          const c=pick(); this.colors[ix]=c.r; this.colors[ix+1]=c.g; this.colors[ix+2]=c.b;
          const r=Math.random(); let size; if(r<0.80) size=6+Math.random()*6; else if(r<0.97) size=12+Math.random()*10; else size=24+Math.random()*18;
          this.sizes[i]=size; this.phases[i]=Math.random()*Math.PI*2;
          this.glyphs[i]=Math.floor(Math.random()*this._glyphGrid.count);
        }
        this.geo=new THREE.BufferGeometry();
        this.geo.setAttribute('position',new THREE.BufferAttribute(this.positions,3));
        this.geo.setAttribute('color',new THREE.BufferAttribute(this.colors,3));
        this.geo.setAttribute('aSize',new THREE.BufferAttribute(this.sizes,1));
        this.geo.setAttribute('aPhase',new THREE.BufferAttribute(this.phases,1));
        this.geo.setAttribute('aGlyph',new THREE.BufferAttribute(this.glyphs,1));
        this.mat=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, vertexColors:true,
          uniforms:{ uTime:{value:0}, uPulse:{value:0}, uOpacity:{value:0.9}, uGlyphTex:{value:this._glyphTex}, uGlyphGrid:{value:new THREE.Vector2(this._glyphGrid.x,this._glyphGrid.y)} },
          vertexShader:`attribute float aSize; attribute float aPhase; attribute float aGlyph; varying vec3 vColor; varying float vPhase; varying float vGlyph; uniform float uTime; uniform float uPulse; void main(){ vColor=color; vPhase=aPhase; vGlyph=aGlyph; vec4 mvPosition=modelViewMatrix*vec4(position,1.0); float beat=1.0+uPulse*0.12; gl_PointSize=aSize*beat*(300.0/-mvPosition.z); gl_Position=projectionMatrix*mvPosition; }`,
          fragmentShader:`varying vec3 vColor; varying float vPhase; varying float vGlyph; uniform float uTime; uniform float uPulse; uniform float uOpacity; uniform sampler2D uGlyphTex; uniform vec2 uGlyphGrid; void main(){ vec2 uv=gl_PointCoord.xy; float d=length(uv-0.5); float glow=smoothstep(0.5,0.0,d); float twinkle=0.65+0.35*sin(uTime*2.0+vPhase); float audioBoost=1.0+uPulse*0.35; float cols=uGlyphGrid.x; float rows=uGlyphGrid.y; float ci=mod(vGlyph, cols); float ri=floor(vGlyph/cols); vec2 glyphUV=(vec2(ci,ri)+uv)/vec2(cols,rows); vec4 glyph=texture2D(uGlyphTex,glyphUV); float alpha=glyph.a*glow*uOpacity; vec3 col=vColor*glyph.r*glow*twinkle*audioBoost; gl_FragColor=vec4(col,alpha); if(alpha<0.03) discard; }` });
        this.bees=new THREE.Points(this.geo,this.mat); this.scene.add(this.bees);
      },

      updateMouthTargets(openAmount){
        const o=THREE.MathUtils.clamp(openAmount,0,1); for(let i=0;i<this.COUNT*3;i++){ const a=this.targetsClosed[i]; const b=this.targetsOpen[i]; this.targets[i]=a+(b-a)*o; }
      },

      setupSpeechIntegration(){
        window.addEventListener('quiz-speech-start',()=>{ this.isActive=true; this.amplitude=0.7; this.mouthPulse=1.2; });
        window.addEventListener('quiz-speech-end',()=>{ this.isActive=false; this.amplitude=0; });
        window.addEventListener('quiz-speech-boundary',()=>{ this.mouthPulse=0.9; });
        // If device is low-perf, use interval polling to avoid per-frame work; otherwise update per-frame
        if(typeof speechSynthesis!=='undefined' && !this._speechTimer && !this._useFrameAmplitude){
          this._speechTimer = setInterval(()=>this.updateSpeechAmplitude(),50);
        }
      },

      updateSpeechAmplitude(){
        if(typeof speechSynthesis==='undefined'){ this.amplitude=0; return; }
        const speaking=speechSynthesis.speaking; if(speaking && this.isActive){ const t=Date.now()*0.015; const w1=Math.sin(t), w2=Math.sin(t*1.6)*0.55, w3=Math.sin(t*2.3)*0.35; this.amplitude=0.45+(w1+w2+w3)*0.25; } else { this.amplitude*=0.85; }
      },

      swarmStep(time){
        const posAttr=this.geo.getAttribute('position');
        this.ampSmooth=this.ampSmooth*0.6+this.amplitude*0.4; this.mouthPulse*=0.8;
        const targetOpen=THREE.MathUtils.clamp(this.ampSmooth*1.4+this.mouthPulse*0.6,0,1);
        const stiffness=0.35, damping=0.7; this.mouthOpenVel=this.mouthOpenVel*damping+(targetOpen-this.mouthOpen)*stiffness; this.mouthOpen+=this.mouthOpenVel;
        this.updateMouthTargets(this.mouthOpen);
        const attractStrength=this.tSpeedBase+this.ampSmooth*0.25;
        const noiseStrength=this.noiseBase+this.ampSmooth*0.08;
        const buzzStrength=this.buzzBase+this.ampSmooth*0.01;
        const tBase=time*0.001;
        for(let i=0;i<this.COUNT;i++){
          const ix=i*3;
          const px=this.positions[ix], py=this.positions[ix+1], pz=this.positions[ix+2];
          const tx=this.targets[ix], ty=this.targets[ix+1], tz=this.targets[ix+2];
          let vx=this.velocities[ix], vy=this.velocities[ix+1], vz=this.velocities[ix+2];
          vx+=(tx-px)*attractStrength; vy+=(ty-py)*attractStrength; vz+=(tz-pz)*attractStrength;
          // merged trig noise (single sin/cos pair)
          const base=px*0.6+py*0.4+pz*0.5+i*0.0007;
          const s=Math.sin(tBase+base);
          const c=Math.cos(tBase*1.1+base*0.9);
          vx+=s*noiseStrength; vy+=s*noiseStrength*0.5; vz+=c*noiseStrength;
          vx+=(Math.random()-0.5)*buzzStrength; vy+=(Math.random()-0.5)*buzzStrength; vz+=(Math.random()-0.5)*buzzStrength;
          vx*=this.damp; vy*=this.damp; vz*=this.damp;
          this.positions[ix]=px+vx; this.positions[ix+1]=py+vy; this.positions[ix+2]=pz+vz;
          this.velocities[ix]=vx; this.velocities[ix+1]=vy; this.velocities[ix+2]=vz;
          posAttr.setXYZ(i,this.positions[ix],this.positions[ix+1],this.positions[ix+2]);
        }
        posAttr.needsUpdate=true;
      },

      animate(time){
        if(!this.scene || !this.ready) return;
        requestAnimationFrame(t=>this.animate(t));
        // On high-performance devices, update amplitude every frame for tighter responsiveness
        if(this._useFrameAmplitude) this.updateSpeechAmplitude();
        this.ampSmooth = this.ampSmooth*0.9 + this.amplitude*0.1;
        this.swarmStep(time);
        if(this.mat){
          this.mat.uniforms.uTime.value = time*0.001;
          this.mat.uniforms.uPulse.value = this.ampSmooth;
          this.mat.uniforms.uOpacity.value = 0.9;
        }
        this.renderer.render(this.scene, this.camera);
      },

      _performHeavyInit(){ 
        if(this._heavyDone) return; 
        this._heavyDone=true; 
        this.buildTargetsFromMask(opts.maskUrl, opts.sampleStep).then(()=>{ 
          this.initParticles(); 
          this.setupSpeechIntegration(); 
          this.ready=true; 
          
          // ✅ Render once, then fade in canvas (prevents white flash)
          this.renderer.render(this.scene, this.camera);
          
          const el = this.renderer?.domElement;
          if (el) {
            el.style.visibility = 'visible';
            // Next tick so CSS transition applies
            requestAnimationFrame(() => { el.style.opacity = '1'; });
          }
          // Also make sure the container is visible (some pages hide the container until visualizer ready)
          try {
            if (this.container) {
               this.container.style.visibility = 'visible';
               this.container.style.opacity = '1';

             // 🔥 REQUIRED FOR YOUR CSS TO WORK
             this.container.classList.add("active");
            }
          } catch (e) {
            // ignore
          }
          
          if(opts.autoStart) this.animate(performance.now()); 
        }); 
      },
      start(){ this._performHeavyInit(); },

      destroy(){ if(this._speechTimer) { clearInterval(this._speechTimer); this._speechTimer=null; } if(this.renderer){ this.renderer.domElement.remove(); this.renderer.dispose(); } if(this.geo) this.geo.dispose(); if(this.mat) this.mat.dispose(); }
    };

    if(!opts.lazyInit){
      viz.initThree();
      viz._performHeavyInit();
    } else {
      const trigger = () => { 
        window.removeEventListener('quiz-speech-start', trigger); 
        viz.initThree();
        viz.start(); 
      };
      window.addEventListener('quiz-speech-start', trigger);
    }
    return viz;
  }
};

export default BeeSwarmVisualizer;
