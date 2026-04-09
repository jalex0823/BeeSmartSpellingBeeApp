/**
 * Smarty Bee 3D Mascot Component
 * Renders and animates the 3D bee mascot using Three.js
 */

// Prevent duplicate declaration
if (typeof SmartyBee3D === 'undefined') {
class SmartyBee3D {
    static instances = new Map();

    static getController(containerId) {
        return SmartyBee3D.instances.get(containerId);
    }

    constructor(containerId, options = {}) {
        // If a controller already exists for this container, dispose it first.
        // This prevents leaking WebGL contexts (a common cause of "Error creating WebGL context").
        try {
            const existing = SmartyBee3D.instances.get(containerId);
            if (existing && existing !== this && typeof existing.destroy === 'function') {
                existing.destroy();
            }
        } catch (e) {
            console.warn('⚠️ Failed to dispose previous SmartyBee3D instance:', e);
        }

        SmartyBee3D.instances.set(containerId, this);
        
        // ALSO register in global window object for getAvatarController()
        if (!window.SmartyBee3DInstances) {
            window.SmartyBee3DInstances = {};
        }
        window.SmartyBee3DInstances[containerId] = this;
        console.log(`✅ Registered ${containerId} in window.SmartyBee3DInstances. Total instances:`, Object.keys(window.SmartyBee3DInstances));

        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        this.options = {
            width: options.width || 400,
            height: options.height || 412,
            autoRotate: options.autoRotate !== false,
            enableInteraction: options.enableInteraction !== false,
            modelPath: options.modelPath, // Direct GLB path (required if not fetching from server)
            fetchFromServer: options.fetchFromServer !== false, // Default: fetch user avatar from server
            brighterLighting: options.brighterLighting !== undefined ? options.brighterLighting : options.fetchFromServer, // Brighter for registered users
            ...options
        };

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bee = null;
        this.animationId = null;
        this.isHovering = false;
        this.avatarData = null; // Store fetched avatar data
        this.manualControl = false; // Flag to disable animations during manual control

        // WebGL availability flag
        this.webglDisabled = false;
        
        // Animation states
        this.currentAnimation = 'idle';
        this.animationTime = 0;
        
        // Sound effects setup
        this.soundEffects = [
            '/static/SoundFxs/pzzlrvl.mp3',
            '/static/SoundFxs/salamisound-5949974-bee-or-wasp-in-flight-fast.mp3',
            '/static/SoundFxs/timer_beep.mp3',
            '/static/SoundFxs/we-can-be-bees.mp3'
        ];
        this.audioElements = [];
        this.preloadSounds();
        
        this.init();
    }
    
    preloadSounds() {
        // Preload all sound effects for instant playback
        this.soundEffects.forEach(soundPath => {
            const audio = new Audio(soundPath);
            audio.preload = 'auto';
            audio.volume = 0.6; // Set volume to 60%
            this.audioElements.push(audio);
        });
    console.log('🔊 Mascot Bee sounds preloaded:', this.soundEffects.length);
    }
    
    playRandomSound() {
        // Pick a random sound effect
        const randomIndex = Math.floor(Math.random() * this.audioElements.length);
        const audio = this.audioElements[randomIndex];
        
        // Stop any currently playing sound
        this.audioElements.forEach(a => {
            a.pause();
            a.currentTime = 0;
        });
        
        // Play the random sound
        audio.currentTime = 0;
        audio.play().catch(error => {
            console.warn('Could not play sound:', error);
        });
        
        console.log('🎵 Playing sound:', this.soundEffects[randomIndex]);
    }

    async init() {
        // Check if Three.js is loaded.
        // In some iOS WebView/Safari builds, deferred scripts can settle slightly later than this init.
        // Wait briefly before giving up so we don't permanently fall back due to a transient load order hiccup.
        if (typeof window.THREE === 'undefined') {
            try { await this._waitForThree(5000); } catch (_e) { /* ignore */ }
        }
        if (typeof window.THREE === 'undefined') {
            console.error('Three.js not loaded. Please include Three.js library.');
            this.showFallbackImage();
            return;
        }

        try {
            const ok = this.setupScene();
            if (!ok) {
                // setupScene already fell back
                return;
            }
            this.setupLighting();
        } catch (e) {
            console.warn('⚠️ 3D mascot initialization failed, falling back to 2D:', e);
            this.showFallbackImage();
            return;
        }
        
        // Fetch avatar from server if needed (MUST complete before loading model)
        if (this.options.fetchFromServer && !this.options.modelPath) {
            await this.fetchUserAvatar();
        }
        
        // Only load model if we have a path
        if (this.options.modelPath) {
            // Kick off GLB loading (async) but don't block UI thread.
            this.loadModel();
        } else {
            console.error('❌ No modelPath available after fetch');
            this.addFallbackBee();
        }
        
        this.setupControls();
        this.animate();
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async _waitForThree(maxWaitMs = 5000) {
        const start = Date.now();
        while (typeof window.THREE === 'undefined' && (Date.now() - start) < maxWaitMs) {
            await this._sleep(50);
        }
        return typeof window.THREE !== 'undefined';
    }

    async _waitForGLTFLoader(maxWaitMs = 5000) {
        // iOS Safari can evaluate scripts out-of-order vs module globals.
        // Wait for GLTFLoader to exist before attempting a GLB load.
        const start = Date.now();
        while ((!window.THREE || !window.THREE.GLTFLoader) && (Date.now() - start) < maxWaitMs) {
            // Some builds expose GLTFLoader as a global constructor instead of THREE.GLTFLoader.
            try {
                if (window.THREE && !window.THREE.GLTFLoader && typeof window.GLTFLoader === 'function') {
                    window.THREE.GLTFLoader = window.GLTFLoader;
                }
            } catch (_e) { /* ignore */ }
            await this._sleep(50);
        }
        if (!window.THREE || !window.THREE.GLTFLoader) {
            throw new Error('GLTFLoader not available');
        }
    }

    _normalizeGlbPath(modelPath) {
        if (!modelPath) return null;
        // Some older code used /static/models/. All avatars now live under glb_files.
        try {
            return String(modelPath).replace('/static/models/', '/static/assets/avatars/glb_files/');
        } catch (_e) {
            return modelPath;
        }
    }

    _withCacheBuster(urlStr) {
        // Always create a valid URL and use searchParams to avoid invalid "??" URLs.
        try {
            const url = new URL(urlStr, window.location.origin);
            url.searchParams.set('v', String(Date.now()));
            return url.toString();
        } catch (_e) {
            // Fallback: best-effort string concat
            const sep = (String(urlStr).includes('?')) ? '&' : '?';
            return `${urlStr}${sep}v=${Date.now()}`;
        }
    }
    
    async fetchUserAvatar() {
        try {
            console.log('🔍 Fetching user avatar from server...');
            const response = await fetch('/api/users/me/avatar', {
                credentials: 'same-origin',
                cache: 'no-store'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            if (data.status === 'success' && data.avatar && data.avatar.urls && data.avatar.urls.glb) {
                this.avatarData = data.avatar;
                this.options.modelPath = data.avatar.urls.glb;
                console.log('✅ User avatar fetched:', data.avatar.name || data.avatar.avatar_id);
            } else {
                throw new Error('No GLB URL in response');
            }
        } catch (error) {
            console.error('❌ Failed to fetch user avatar:', error.message);
            // DO NOT set a fallback path - let init() validation handle it
            // Server should tell us which avatar to use (could be any of 40 avatars)
        }
    }

    setupScene() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = null; // Transparent background

        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            45,
            this.options.width / this.options.height,
            0.1,
            1000
        );
        this.camera.position.z = 5;

        // Save default camera position for resetView()
        this.defaultCameraPosition = this.camera.position.clone();

        // Remove any existing canvases left behind (defensive cleanup)
        try {
            const existingCanvas = this.container.querySelector('canvas');
            if (existingCanvas && existingCanvas.parentElement === this.container) {
                existingCanvas.remove();
            }
        } catch (e) {
            // ignore
        }

        // Create renderer (may throw if WebGL is unavailable/disabled)
        try {
            this.renderer = new THREE.WebGLRenderer({
                alpha: true,
                antialias: true,
                powerPreference: 'high-performance'
            });
        } catch (e) {
            // WebGL context could not be created (hardware acceleration disabled, too many contexts, etc.)
            this.webglDisabled = true;
            console.warn('🚫 WebGL unavailable for SmartyBee3D. Using 2D fallback.', e);
            this.showFallbackImage();
            return false;
        }

        // Mark WebGL as confirmed available so other components skip their probe.
        try { window.__webglConfirmedAvailable = true; } catch (_e) {}

        this.renderer.setSize(this.options.width, this.options.height);
        // iOS Safari is prone to WebGL memory pressure; cap DPR for stability.
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        // iOS Safari alignment fix:
        // Ensure the WebGL canvas behaves like a centered block within the container.
        // Some iOS layouts can right-shift replaced elements inside nested flex/scroll contexts.
        try {
            const canvasEl = this.renderer.domElement;
            canvasEl.style.display = 'block';
            canvasEl.style.marginLeft = 'auto';
            canvasEl.style.marginRight = 'auto';
            canvasEl.style.maxWidth = '100%';
            canvasEl.style.flexShrink = '0';

            const forceCentered = () => {
                try {
                    // Make sure we have a positioning context so absolute centering works.
                    let cs = null;
                    try { cs = window.getComputedStyle(this.container); } catch (_e) {}
                    if (!cs || cs.position === 'static') {
                        this.container.style.position = 'relative';
                    }

                    // Anchor at 50/50 like the guest carousel does.
                    canvasEl.style.position = 'absolute';
                    canvasEl.style.top = '50%';
                    canvasEl.style.left = '50%';
                    canvasEl.style.transform = 'translate(-50%, -50%)';
                } catch (_e) {
                    // ignore
                }
            };

            // If the container establishes a positioning context (recommended),
            // anchor the canvas at 50/50 like the guest carousel does.
            // This avoids Safari flexbox rounding/layout quirks that can
            // right-shift <canvas> elements.
            try {
                const cs = window.getComputedStyle(this.container);
                if (cs && cs.position && cs.position !== 'static') {
                    forceCentered();
                }
            } catch (_e) {
                // ignore
            }

            // iOS Safari: the first layout pass can happen *after* canvas insertion,
            // leaving it uncentered on initial load. Re-assert over a few frames.
            try {
                this._forceCanvasCentered = forceCentered;
                requestAnimationFrame(() => {
                    forceCentered();
                    setTimeout(forceCentered, 60);
                    setTimeout(forceCentered, 220);
                });
                window.addEventListener('resize', forceCentered, { passive: true });
                window.addEventListener('orientationchange', forceCentered, { passive: true });
                window.addEventListener('pageshow', forceCentered, { passive: true });
            } catch (_e) {
                // ignore
            }
        } catch (e) {
            // ignore
        }

        // Handle WebGL context loss gracefully
        try {
            const canvas = this.renderer.domElement;
            canvas.addEventListener('webglcontextlost', (evt) => {
                evt.preventDefault();
                console.warn('🚫 WebGL context lost for SmartyBee3D. Falling back to 2D.');
                this.webglDisabled = true;
                this.showFallbackImage();
            }, false);
        } catch (e) {
            // ignore
        }

        this.container.appendChild(this.renderer.domElement);
        // Re-assert centering after insertion (iOS Safari can shift after append).
        try {
            if (typeof this._forceCanvasCentered === 'function') {
                this._forceCanvasCentered();
            }
        } catch (_e) {
            // ignore
        }
        return true;
    }

    setupLighting() {
        // Consistent lighting for all avatars
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        const fillLight = new THREE.DirectionalLight(0xffffff, 0.7);
        fillLight.position.set(-5, 0, 5);
        this.scene.add(fillLight);
    }

    async loadModel() {
        // GLB-only loader - all avatars are GLB format.
        // IMPORTANT: No substitute model fallbacks (per product requirement).
        if (!this.options.modelPath) {
            console.error('❌ No modelPath specified');
            this.addFallbackBee(new Error('No modelPath specified'));
            return;
        }

        const basePath = this._normalizeGlbPath(this.options.modelPath);
        const avatarName = this.avatarData ? (this.avatarData.name || this.avatarData.avatar_id) : 'Avatar';

        // Retry can help when iOS/PWA has just updated SW caches.
        this._glbLoadAttempts = (this._glbLoadAttempts || 0) + 1;
        const attempt = this._glbLoadAttempts;

        // IMPORTANT: Do NOT cache-bust on the first attempt — that defeats the browser's HTTP
        // cache and the prefetch we inject during the loading screen. Only bust on retries
        // (attempt >= 2) to recover from stale service-worker caches.
        const shouldBust = attempt >= 2;

        try {
            await this._waitForGLTFLoader(5000);
        } catch (e) {
            console.error('❌ GLTFLoader not ready (Safari race?)', e);
            if (attempt < 3) {
                await this._sleep(150);
                return this.loadModel();
            }
            this.addFallbackBee(e);
            return;
        }

        const glbUrl = shouldBust ? this._withCacheBuster(basePath) : basePath;
        console.log(`🐝 Loading GLB model: ${avatarName} (attempt ${attempt})`, glbUrl);

        let loader;
        try {
            loader = new THREE.GLTFLoader();
            // If avatars are hosted on a CDN or different origin, Safari can be stricter.
            if (loader && typeof loader.setCrossOrigin === 'function') {
                loader.setCrossOrigin('anonymous');
            }
            // If the GLB references external resources, set a sane base path.
            try {
                const baseUrl = new URL(basePath, window.location.origin);
                baseUrl.search = '';
                const baseDir = baseUrl.toString().split('/').slice(0, -1).join('/') + '/';
                if (typeof loader.setResourcePath === 'function') {
                    loader.setResourcePath(baseDir);
                }
            } catch (_e) {
                // ignore
            }
        } catch (e) {
            console.error('❌ Failed to construct GLTFLoader', e);
            this.addFallbackBee(e);
            return;
        }

        loader.load(
            glbUrl,
            (gltf) => {
                try {
                    const object = gltf && gltf.scene;
                    if (!object) {
                        throw new Error('GLB contained no scene');
                    }

                    // Center and scale the model
                    const box = new THREE.Box3().setFromObject(object);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());

                    const maxDim = Math.max(size.x, size.y, size.z) || 1;
                    const scale = 3 / maxDim;
                    object.scale.set(scale, scale, scale);
                    object.position.sub(center.multiplyScalar(scale));

                    this.bee = object;

                    // Save default bee rotation for resetView()
                    this.defaultBeeRotation = this.bee.rotation.clone();

                    this.scene.add(object);

                    console.log(`✅ ${avatarName} GLB model loaded successfully!`);

                    // Call onReady callback if provided
                    if (this.options.onReady && typeof this.options.onReady === 'function') {
                        try {
                            console.log('🚀 Calling onReady callback');
                            this.options.onReady();
                        } catch (e) {
                            console.warn('⚠️ onReady callback threw', e);
                        }
                    }
                } catch (e) {
                    console.error('❌ Error processing GLB scene:', e);
                    this.addFallbackBee(e);
                }
            },
            (xhr) => {
                try {
                    if (!xhr || !xhr.total) return;
                    const pct = Math.round((xhr.loaded / xhr.total) * 100);
                    console.log(`Loading GLB model: ${pct}%`);
                } catch (_e) {
                    // ignore
                }
            },
            async (error) => {
                console.error('❌ Error loading GLB model:', error);
                console.error('GLB path attempted:', basePath);
                console.error('GLB URL attempted:', glbUrl);

                // Extra diagnostics: attempt to fetch to surface status/content-type in Safari.
                try {
                    let resp = null;
                    try {
                        resp = await fetch(glbUrl, { method: 'HEAD', credentials: 'same-origin', cache: 'no-store' });
                    } catch (_e) {
                        resp = null;
                    }

                    // Some setups disallow HEAD. Fall back to a tiny range request.
                    if (!resp || (resp.status === 405)) {
                        resp = await fetch(glbUrl, {
                            method: 'GET',
                            headers: { 'Range': 'bytes=0-0' },
                            credentials: 'same-origin',
                            cache: 'no-store'
                        });
                    }

                    console.error('GLB fetch diagnostics:', {
                        ok: !!resp && resp.ok,
                        status: resp ? resp.status : null,
                        contentType: (resp && resp.headers && resp.headers.get) ? resp.headers.get('content-type') : null,
                        contentLength: (resp && resp.headers && resp.headers.get) ? resp.headers.get('content-length') : null,
                        acceptRanges: (resp && resp.headers && resp.headers.get) ? resp.headers.get('accept-ranges') : null
                    });
                } catch (e) {
                    console.error('GLB fetch diagnostics failed:', e);
                }

                if (attempt < 2) {
                    await this._sleep(250);
                    return this.loadModel();
                }
                this.addFallbackBee(error);
            }
        );
    }

    setupControls() {
        if (!this.options.enableInteraction) return;

        const canvas = this.renderer.domElement;

        canvas.addEventListener('mouseenter', () => {
            this.isHovering = true;
        });

        canvas.addEventListener('mouseleave', () => {
            this.isHovering = false;
        });

        canvas.addEventListener('click', () => {
            this.playRandomSound(); // Play random bee sound!
            this.playAnimation('celebrate');
        });
    }

    addFallbackBee(error) {
        // NO 3D/2D substitute avatar model. Show a clear error state instead.
        // (We keep the method name for compatibility with existing call sites.)
        try {
            console.error('❌ GLB avatar failed to load (no fallback model).', error || 'Unknown error');
        } catch (_e) {
            // ignore
        }

        try {
            // Avoid blowing away the renderer if it already exists; but if there's no canvas yet,
            // show an inline error panel.
            const hasCanvas = !!(this.container && this.container.querySelector && this.container.querySelector('canvas'));
            if (this.container && !hasCanvas) {
                this.container.innerHTML = `
                    <div style="
                        width: 100%;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        background: rgba(255, 224, 130, 0.25);
                        border-radius: 1rem;
                        border: 2px solid rgba(255, 179, 0, 0.6);
                        padding: 0.75rem;
                        text-align: center;
                    ">
                        <div style="font-size: 0.95rem; color: #5D4037; font-weight: 700;">
                            3D avatar failed to load
                        </div>
                        <div style="font-size: 0.75rem; color: #8D6E63; margin-top: 0.25rem;">
                            Please refresh and check console logs
                        </div>
                    </div>
                `;
            }
        } catch (_e) {
            // ignore
        }
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        if (this.webglDisabled || !this.renderer) {
            return;
        }
        
        if (this.bee) {
            this.animationTime += 0.016; // ~60fps

            switch (this.currentAnimation) {
                case 'idle':
                    this.idleAnimation();
                    break;
                case 'celebrate':
                    this.celebrateAnimation();
                    break;
                case 'encourage':
                    this.encourageAnimation();
                    break;
                case 'thinking':
                    this.thinkingAnimation();
                    break;
            }

            // Auto-rotate if enabled (but not during manual control)
            if (this.options.autoRotate && !this.isHovering && !this.manualControl) {
                this.bee.rotation.y += 0.005;
            }

            // Hover effect (but not during manual control)
            if (this.isHovering && !this.manualControl) {
                this.bee.position.y = Math.sin(this.animationTime * 3) * 0.1;
            }
        }

        this.renderer.render(this.scene, this.camera);
    }

    idleAnimation() {
        if (!this.bee) return;
        
        // Disabled floating motion to keep avatar still
        // this.bee.position.y = Math.sin(this.animationTime * 2) * 0.05;
        
        // Disabled wing flutter
        // this.bee.rotation.z = Math.sin(this.animationTime * 8) * 0.02;
    }

    celebrateAnimation() {
        if (!this.bee) return;
        
        const duration = 2; // 2 seconds
        const progress = (this.animationTime % duration) / duration;
        
        // Spinning celebration
        this.bee.rotation.y += 0.1;
        this.bee.position.y = Math.sin(progress * Math.PI * 4) * 0.3;
        this.bee.scale.setScalar(1 + Math.sin(progress * Math.PI * 2) * 0.1);
        
        // Return to idle after duration
        if (progress > 0.95) {
            this.playAnimation('idle');
        }
    }

    encourageAnimation() {
        if (!this.bee) return;
        
        const duration = 1.5;
        const progress = (this.animationTime % duration) / duration;
        
        // Nodding motion
        this.bee.rotation.x = Math.sin(progress * Math.PI * 4) * 0.2;
        this.bee.position.y = Math.sin(progress * Math.PI * 2) * 0.1;
        
        if (progress > 0.95) {
            this.playAnimation('idle');
        }
    }

    thinkingAnimation() {
        if (!this.bee) return;
        
        // Tilting head, pondering
        this.bee.rotation.z = Math.sin(this.animationTime * 1.5) * 0.15;
        this.bee.position.y = Math.sin(this.animationTime * 1) * 0.03;
    }

    playAnimation(animationName) {
        this.currentAnimation = animationName;
        this.animationTime = 0;
    }

    // Public methods for quiz integration
    onCorrectAnswer() {
        this.playAnimation('celebrate');
    }

    onIncorrectAnswer() {
        this.playAnimation('encourage');
    }

    onQuestionStart() {
        this.playAnimation('thinking');
    }

    onQuizComplete() {
        this.playAnimation('celebrate');
    }

    showFallbackImage() {
        // Show 2D bee image if 3D fails to load.
        // IMPORTANT: If we've already successfully rendered once (canvas exists),
        // do NOT replace it with the generic fallback. That would look like the
        // avatar "turned into" the default bee after a transient error.
        try {
            const hasCanvas = !!(this.container && this.container.querySelector && this.container.querySelector('canvas'));
            if (hasCanvas) {
                try {
                    this.container.dataset.avatarFallbackSuppressed = '1';
                } catch (_e) { /* ignore */ }
                return;
            }
        } catch (_e) {
            // ignore and continue to fallback
        }

        this.container.innerHTML = `
            <div style="
                width: ${this.options.width}px;
                height: ${this.options.height}px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #FFE082 0%, #FFD54F 100%);
                border-radius: 20px;
                border: 3px solid #FFB300;
            ">
                <div style="font-size: 4rem; animation: bounce 1s infinite;">🐝</div>
            </div>
        `;
    }

    // Avatar Control Methods
    zoom(delta) {
        // Zoom by adjusting camera position
        if (this.camera) {
            const currentZ = this.camera.position.z;
            const newZ = Math.max(2, Math.min(10, currentZ - (delta * 5))); // Invert delta for intuitive zoom
            this.camera.position.z = newZ;
            console.log(`🔍 Zoom: ${delta > 0 ? 'in' : 'out'} (camera.z: ${newZ.toFixed(2)})`);
        }
    }

    rotateY(degrees) {
        // Rotate the bee model around Y axis
        if (this.bee) {
            const radians = (degrees * Math.PI) / 180;
            this.bee.rotation.y += radians;
            console.log(`🔄 Rotate Y: ${degrees}° (total: ${((this.bee.rotation.y * 180 / Math.PI) % 360).toFixed(1)}°)`);
        }
    }

    rotate(pitchRad = 0, yawRad = 0) {
        // Rotate bee with pitch (X) and yaw (Y)
        if (this.bee) {
            this.bee.rotation.x += pitchRad;
            this.bee.rotation.y += yawRad;
            console.log(`🔄 Rotate: pitch=${(pitchRad * 180 / Math.PI).toFixed(1)}° yaw=${(yawRad * 180 / Math.PI).toFixed(1)}°`);
        }
    }

    resetView() {
        // Reset camera and bee rotation to defaults
        if (this.camera && this.defaultCameraPosition) {
            this.camera.position.copy(this.defaultCameraPosition);
            this.camera.lookAt(0, 0.1, 0);
        }
        if (this.bee && this.defaultBeeRotation) {
            this.bee.rotation.copy(this.defaultBeeRotation);
        }
        console.log('🔄 View reset to defaults');
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        // Dispose WebGL resources aggressively (iOS Safari is sensitive to leaked contexts).
        try {
            if (this.scene && typeof this.scene.traverse === 'function') {
                this.scene.traverse((obj) => {
                    try {
                        if (obj && obj.geometry && typeof obj.geometry.dispose === 'function') {
                            obj.geometry.dispose();
                        }
                        if (obj && obj.material) {
                            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
                            for (const m of mats) {
                                if (!m) continue;
                                // Dispose textures referenced by material
                                for (const k in m) {
                                    try {
                                        const v = m[k];
                                        if (v && v.isTexture && typeof v.dispose === 'function') v.dispose();
                                    } catch (_e) { /* ignore */ }
                                }
                                if (typeof m.dispose === 'function') m.dispose();
                            }
                        }
                    } catch (_e) { /* ignore */ }
                });
            }
        } catch (_e) { /* ignore */ }

        try {
            if (this.renderer) {
                // Force context loss to release GPU memory promptly on iOS.
                if (typeof this.renderer.forceContextLoss === 'function') {
                    try { this.renderer.forceContextLoss(); } catch (_e2) { /* ignore */ }
                }
                this.renderer.dispose();
                if (this.container && this.renderer.domElement && this.container.contains(this.renderer.domElement)) {
                    this.container.removeChild(this.renderer.domElement);
                }
            }
        } catch (_e) { /* ignore */ }

        try {
            if (this.container && this.container.id) {
                SmartyBee3D.instances.delete(this.container.id);
                if (window.SmartyBee3DInstances) {
                    try { delete window.SmartyBee3DInstances[this.container.id]; } catch (_e2) { /* ignore */ }
                }
            }
        } catch (_e) { /* ignore */ }

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bee = null;
    }

    resize(width, height) {
        this.options.width = width;
        this.options.height = height;
        
        if (this.camera) {
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
        }
        
        if (this.renderer) {
            this.renderer.setSize(width, height);
        }
    }
}

// Make it globally available
window.SmartyBee3D = SmartyBee3D;

} // End of SmartyBee3D guard
