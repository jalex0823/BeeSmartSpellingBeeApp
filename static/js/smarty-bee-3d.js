/**
 * Smarty Bee 3D Mascot Component
 * Renders and animates the 3D bee mascot using Three.js
 */

class SmartyBee3D {
    static instances = new Map();

    static getController(containerId) {
        return SmartyBee3D.instances.get(containerId);
    }

    constructor(containerId, options = {}) {
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
        // Check if Three.js is loaded
        if (typeof THREE === 'undefined') {
            console.error('Three.js not loaded. Please include Three.js library.');
            this.showFallbackImage();
            return;
        }

        this.setupScene();
        this.setupLighting();
        
        // Fetch avatar from server if needed (MUST complete before loading model)
        if (this.options.fetchFromServer && !this.options.modelPath) {
            await this.fetchUserAvatar();
        }
        
        // Only load model if we have a path
        if (this.options.modelPath) {
            this.loadModel();
        } else {
            console.error('❌ No modelPath available after fetch');
            this.addFallbackBee();
        }
        
        this.setupControls();
        this.animate();
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

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true 
        });
        this.renderer.setSize(this.options.width, this.options.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        this.container.appendChild(this.renderer.domElement);
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

    loadModel() {
        // GLB-only loader - all avatars are GLB format
        const loader = new THREE.GLTFLoader();
        
        // Use modelPath directly (already set from server or options)
        if (!this.options.modelPath) {
            console.error('❌ No modelPath specified');
            this.addFallbackBee();
            return;
        }
        
        const correctedPath = this.options.modelPath.replace('/static/models/', '/static/assets/avatars/glb_files/');
        const glbPath = correctedPath;
        
        // Cache-busting: add timestamp to force reload of updated files
        const cacheBuster = Date.now();
        const glbPathWithCache = `${glbPath}?v=${cacheBuster}`;

        const avatarName = this.avatarData ? (this.avatarData.name || this.avatarData.avatar_id) : 'Avatar';
        console.log(`🐝 Loading GLB model: ${avatarName}`, glbPathWithCache);

        // Load GLB model with materials and textures embedded
        loader.load(
            glbPathWithCache,
            (gltf) => {
                const object = gltf.scene;
                
                // Center and scale the model
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 3 / maxDim;
                object.scale.set(scale, scale, scale);
                
                object.position.sub(center.multiplyScalar(scale));

                this.bee = object;
                
                // Save default bee rotation for resetView()
                this.defaultBeeRotation = this.bee.rotation.clone();
                
                this.scene.add(object);
                
                const avatarName = this.avatarData ? (this.avatarData.name || this.avatarData.avatar_id) : 'Avatar';
                console.log(`✅ ${avatarName} GLB model loaded successfully!`);
                
                // Call onReady callback if provided
                if (this.options.onReady && typeof this.options.onReady === 'function') {
                    console.log('🚀 Calling onReady callback');
                    this.options.onReady();
                }
            },
            (xhr) => {
                const percentComplete = (xhr.loaded / xhr.total * 100).toFixed(0);
                console.log(`Loading GLB model: ${percentComplete}%`);
            },
            (error) => {
                console.error('❌ Error loading GLB model:', error);
                console.error('GLB path attempted:', glbPath);
                this.addFallbackBee();
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

    addFallbackBee() {
        // Lightweight 3D fallback so UI still looks alive if GLB loading fails
        try {
            const geom = new THREE.SphereGeometry(1, 20, 20);
            const mat = new THREE.MeshStandardMaterial({ color: 0xffdd00, metalness: 0.2, roughness: 0.6 });
            const bee = new THREE.Mesh(geom, mat);
            bee.position.set(0, 1, 0);
            this.scene.add(bee);
            this.bee = bee;
            console.warn('Fallback 3D bee added (GLB not available).');
        } catch (e) {
            console.error('Failed to add fallback 3D bee, showing image instead.', e);
            this.showFallbackImage();
        }
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
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
        // Show 2D bee image if 3D fails to load
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
        if (this.renderer) {
            this.renderer.dispose();
            if (this.container.contains(this.renderer.domElement)) {
                this.container.removeChild(this.renderer.domElement);
            }
        }
        SmartyBee3D.instances.delete(this.container.id);
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
