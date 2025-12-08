/**
 * Smarty Bee 3D Mascot Component
 * Renders and animates the 3D bee mascot using Three.js
 */

class SmartyBee3D {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        this.options = {
            width: options.width || 200,
            height: options.height || 200,
            autoRotate: options.autoRotate !== false,
            enableInteraction: options.enableInteraction !== false,
            // Allow disabling the subtle idle animation for static display (e.g., home screen)
            idleAnimation: options.idleAnimation !== false,
            // Build paths from injected base to avoid root-relative 404s
            modelBase: (typeof window !== 'undefined' && window.BEE_MODEL_BASE) ? window.BEE_MODEL_BASE : '/static/models/',
            modelName: options.modelName || 'MascotBee_1019174653_texture',
            modelPath: options.modelPath, // optional absolute override
            texturePath: options.texturePath, // optional absolute override
            mtlPath: options.mtlPath, // optional absolute override
            // Framing controls (hero mode zoom)
            // zoom > 1.0 makes the avatar appear larger on screen by moving the camera in
            zoom: typeof options.zoom === 'number' ? options.zoom : 1.0,
            // Camera distance factor baseline used with model size; smaller = closer
            cameraDistanceFactor: typeof options.cameraDistanceFactor === 'number' ? options.cameraDistanceFactor : 1.8,
            // Vertical offset to keep feet from clipping
            verticalOffset: typeof options.verticalOffset === 'number' ? options.verticalOffset : 0.35,
            ...options
        };

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bee = null;
        this.animationId = null;
        this.isHovering = false;
        
        // Default positions for reset
        this.defaultCameraPos = null;
        this.defaultBeeRotation = null;
        
        // Animation states
        this.currentAnimation = 'idle';
        this.animationTime = 0;
        
        // Manual control state - pauses auto animations
        this.manualControl = false;
        this.manualControlResumeTimer = null;
        
        // Sound effects setup
        this.soundEffects = [
            '/static/SoundFxs/pzzlrvl.mp3',
            '/static/SoundFxs/salamisound-5949974-bee-or-wasp-in-flight-fast.mp3',
            '/static/SoundFxs/timer_beep.mp3',
            '/static/SoundFxs/we-can-be-bees.mp3'
        ];
        this.audioElements = [];
        this.preloadSounds();
        
        // Register this instance
        SmartyBee3D.instances[containerId] = this;
        console.log(`✅ SmartyBee3D instance registered: ${containerId}`);
        
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

    init() {
        // Check if Three.js is loaded
        if (typeof THREE === 'undefined') {
            console.error('Three.js not loaded. Please include Three.js library.');
            this.showFallbackImage();
            return;
        }

        this.setupScene();
        this.setupLighting();
        this.loadModel();
        this.setupControls();
        this.animate();
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
        
        // Save default camera position for reset
        this.defaultCameraPos = this.camera.position.clone();

        // Create renderer with 4K quality settings for crisp GLB avatars
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true,
            // 🎨 HIGH QUALITY RENDERING FOR GLB FILES 🎨
            powerPreference: 'high-performance',
            precision: 'highp',
            logarithmicDepthBuffer: true,
            preserveDrawingBuffer: false,
            premultipliedAlpha: true,
            stencil: false,
            depth: true
        });
        
        this.renderer.setSize(this.options.width, this.options.height);
        
        // 🔥 4K QUALITY SETTINGS - CRISP AND CLEAR 🔥
        // Use higher pixel ratio for sharper rendering (capped at 2 for performance)
        const pixelRatio = Math.min(window.devicePixelRatio * 1.5, 2);
        this.renderer.setPixelRatio(pixelRatio);
        console.log(`🎨 Rendering at ${pixelRatio}x pixel ratio for crisp detail`);
        
        // Enable shadow maps for realistic depth
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Soft shadows
        
        // Ensure correct color space and tone mapping so colors don't look washed out
        try {
            if (typeof this.renderer.outputColorSpace !== 'undefined' && THREE.SRGBColorSpace) {
                this.renderer.outputColorSpace = THREE.SRGBColorSpace;
            } else if (typeof this.renderer.outputEncoding !== 'undefined' && THREE.sRGBEncoding) {
                // Back-compat for older Three.js builds
                this.renderer.outputEncoding = THREE.sRGBEncoding;
            }
            if (typeof THREE.ACESFilmicToneMapping !== 'undefined') {
                this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
                this.renderer.toneMappingExposure = 1.0;
            }
        } catch (e) { /* no-op */ }
        
        // Ensure fully transparent background so the home page design shows through
        if (this.renderer && typeof this.renderer.setClearColor === 'function') {
            this.renderer.setClearColor(0x000000, 0);
        }
        
        // Make canvas transparent to pointer events so parent div's onclick works
        this.renderer.domElement.style.pointerEvents = 'none';
        
        this.container.appendChild(this.renderer.domElement);
        // Defensive: canvas inherits transparency explicitly
        try {
            this.renderer.domElement.style.background = 'transparent';
        } catch (e) { /* no-op */ }
    }

    setupLighting() {
        // Consistent lighting for all avatars - matches dashboard vivid colors
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
        this.scene.add(ambientLight);

        // Directional light for shadows and definition
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        // Fill light from the side
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.7);
        fillLight.position.set(-5, 0, 5);
        this.scene.add(fillLight);
    }

    loadModel() {
        // GLB-only support using GLTFLoader
        // Accept either explicit options.glbPath or a modelPath ending with .glb/.gltf
        // GLB is the PREFERRED format: single file, embedded textures, faster loading
        const explicitGlb = this.options.glbPath;
        const inferredGlb = (this.options.modelPath && /\.(glb|gltf)(\?.*)?$/i.test(this.options.modelPath)) ? this.options.modelPath : null;
        const glbPath = explicitGlb || inferredGlb;
        
        if (glbPath) {
            // GLB path - use GLTF loader
            this.loadGLB(glbPath);
            return;
        }
        
        // No valid model path - show fallback
        console.error('❌ No valid GLB model path provided');
        this.addFallbackBee();
    }
    
    loadGLB(glbPath) {
        // Wait for GLTFLoader to be available (iOS Safari and Windows desktop fix)
        const waitForGLTFLoader = async () => {
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds max wait
            
            // Check both THREE.GLTFLoader and window.THREE.GLTFLoader for cross-browser compatibility
            while ((!window.THREE || !window.THREE.GLTFLoader) && attempts < maxAttempts) {
                console.log(`⏳ Waiting for GLTFLoader... (${attempts + 1}/${maxAttempts})`);
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
                
                // Early exit if found
                if (window.THREE && window.THREE.GLTFLoader) {
                    console.log('✅ GLTFLoader detected!');
                    break;
                }
            }
            
            if (!window.THREE || !window.THREE.GLTFLoader) {
                console.error('❌ GLTFLoader not available after ' + attempts + ' attempts');
                console.error('   window.THREE:', !!window.THREE);
                console.error('   GLTFLoader:', window.THREE ? !!window.THREE.GLTFLoader : 'N/A');
                throw new Error('GLTFLoader not available after 5 seconds');
            }
            
            console.log('✅ GLTFLoader ready for use');
        };
        
        // Start loading process
        (async () => {
            try {
                // Wait for GLTFLoader to be ready
                await waitForGLTFLoader();
                
                console.log('🎯 GLB MODE ACTIVATED - Loading single-file 3D model');
                const cacheBuster = Date.now();
                const glbUrl = glbPath + (glbPath.includes('?') ? `&v=${cacheBuster}` : `?v=${cacheBuster}`);
                const gltfLoader = new THREE.GLTFLoader();
                console.log('🐝 Loading GLB model:', glbUrl);
                
                // Add timeout protection for GLB loading
                const loadTimeout = setTimeout(() => {
                    console.error('❌ GLB loading timeout (10s) - file may be corrupted or too large');
                    this.addFallbackBee();
                }, 10000);
                
                gltfLoader.load(
                    glbUrl,
                    (gltf) => {
                        clearTimeout(loadTimeout);
                            try {
                                const object = gltf.scene || (gltf.scenes && gltf.scenes[0] !== undefined) ? gltf.scenes[0] : null;
                                if (!object) {
                                    throw new Error('GLB contained no scene - file may be corrupted');
                                }
                                
                                console.log('✅ GLB file parsed successfully');
                                
                                // 🎨 HIGH QUALITY GLB TEXTURE PROCESSING 🎨
                                // Ensure GLB textures use sRGB for correct color and apply anisotropic filtering
                                try {
                                    // Get max anisotropy for crisp textures at all angles
                                    const maxAnisotropy = this.renderer.capabilities.getMaxAnisotropy();
                                    console.log(`🔥 Applying ${maxAnisotropy}x anisotropic filtering for ultra-crisp textures`);
                                    
                                    let meshCount = 0;
                                    let textureCount = 0;
                                    
                                    object.traverse((node) => {
                                        if (node.isMesh) {
                                            meshCount++;
                                            // Enable shadow casting and receiving for depth
                                            node.castShadow = true;
                                            node.receiveShadow = true;
                                            
                                            const mats = Array.isArray(node.material) ? node.material : [node.material];
                                            mats.forEach((mat) => {
                                                if (mat) {
                                                    // Process all texture maps (diffuse, normal, roughness, etc.)
                                                    ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap'].forEach(texType => {
                                                        if (mat[texType]) {
                                                            textureCount++;
                                                            // Set color space for accurate colors
                                                            if (typeof mat[texType].colorSpace !== 'undefined' && THREE.SRGBColorSpace) {
                                                                mat[texType].colorSpace = THREE.SRGBColorSpace;
                                                            } else if (typeof mat[texType].encoding !== 'undefined' && THREE.sRGBEncoding) {
                                                                mat[texType].encoding = THREE.sRGBEncoding;
                                                            }
                                                            
                                                            // 🔥 ANISOTROPIC FILTERING - Makes textures ultra-crisp at all angles 🔥
                                                            mat[texType].anisotropy = maxAnisotropy;
                                                            
                                                            // High-quality filtering
                                                            mat[texType].minFilter = THREE.LinearMipmapLinearFilter;
                                                            mat[texType].magFilter = THREE.LinearFilter;
                                                            mat[texType].generateMipmaps = true;
                                                            mat[texType].needsUpdate = true;
                                                        }
                                                    });
                                                    
                                                    mat.needsUpdate = true;
                                                }
                                            });
                                        }
                                    });
                                    console.log(`✅ Applied 4K quality texture filtering to ${meshCount} meshes, ${textureCount} textures`);
                                } catch (e) { 
                                    console.warn('⚠️ Could not apply full quality settings:', e);
                                }
                                
                                // Center/scale like OBJ path
                                const box = new THREE.Box3().setFromObject(object);
                                const center = box.getCenter(new THREE.Vector3());
                                const size = box.getSize(new THREE.Vector3());
                                const maxDim = Math.max(size.x, size.y, size.z);
                                const scaleMultiplier = (this.options && this.options.scaleMultiplier) ? this.options.scaleMultiplier : 1;
                                const scale = (3 * scaleMultiplier) / (maxDim || 1);
                                object.scale.set(scale, scale, scale);
                                object.position.x = -center.x * scale;
                                object.position.y = -center.y * scale;
                                object.position.z = -center.z * scale;

                                this.bee = object;
                                this.scene.add(object);

                                // Offset up a bit to avoid bottom clipping
                                object.position.y += (this.options.verticalOffset || 0.35);

                                const maxScaledDim = (maxDim || 1) * scale;
                                const distance = (maxScaledDim * (this.options.cameraDistanceFactor || 1.8)) / (this.options.zoom || 1.0);
                                this.camera.position.z = distance;
                                this.camera.position.y = maxScaledDim * 0.15;
                                this.camera.lookAt(0, 0, 0);
                                this.camera.updateProjectionMatrix();
                                
                                // Save default positions for reset functionality
                                this.defaultCameraPos = this.camera.position.clone();
                                this.defaultBeeRotation = this.bee.rotation.clone();
                                console.log('💾 Default positions saved for reset');

                                if (this.renderer && typeof this.renderer.setScissorTest === 'function') {
                                    this.renderer.setScissorTest(false);
                                }

                                console.log('✅ GLB model loaded and rendered successfully');
                                window.mascotBeeLoaded = true;
                            } catch (e) {
                                console.error('❌ Error processing GLB scene:', e);
                                console.log('🔄 Attempting OBJ fallback...');
                                this.addFallbackBee();
                            }
                        },
                        (xhr) => {
                            if (xhr && xhr.total) {
                                const pct = (xhr.loaded / xhr.total) * 100;
                                console.log(`📥 Loading GLB: ${pct.toFixed(0)}% (${(xhr.loaded/1024).toFixed(1)}KB / ${(xhr.total/1024).toFixed(1)}KB)`);
                            }
                        },
                        (error) => {
                            clearTimeout(loadTimeout);
                            console.error('❌ Error loading GLB model:', error);
                            console.error('   File path:', glbPath);
                            console.error('   Error details:', error.message || error);
                            this.addFallbackBee();
                        }
                    );
            } catch (error) {
                console.error('❌ GLTFLoader initialization failed:', error);
                this.addFallbackBee();
            }
        })();
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
        // Log error - GLB should work on all devices with proper loading
        console.error('❌ GLB avatar failed to load - this should not happen on iOS');
        console.error('   Check: 1) GLTFLoader script loaded, 2) GLB file exists, 3) Network connectivity');
        
        // Show error state instead of fallback image
        this.container.innerHTML = `
            <div style="
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #FFE082 0%, #FFD54F 100%);
                border-radius: 1rem;
                border: 3px solid #FFB300;
                padding: 1rem;
                text-align: center;
            ">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">⚠️</div>
                <div style="font-size: 0.9rem; color: #5D4037; font-weight: 600;">
                    3D model failed to load
                </div>
                <div style="font-size: 0.75rem; color: #8D6E63; margin-top: 0.25rem;">
                    Check console for details
                </div>
            </div>
        `;
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (this.bee) {
            this.animationTime += 0.016; // ~60fps

            // Skip auto-animations during manual control
            if (!this.manualControl) {
                switch (this.currentAnimation) {
                    case 'idle':
                        // Respect idleAnimation flag to allow static poses on certain pages
                        if (this.options.idleAnimation !== false) {
                            this.idleAnimation();
                        }
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

                // Auto-rotate if enabled - rotate around Y-axis to show all sides
                if (this.options.autoRotate && !this.isHovering) {
                    this.bee.rotation.y += 0.005;
                }
            }

            // Hover effect
            if (this.isHovering) {
                this.bee.position.y = Math.sin(this.animationTime * 3) * 0.1;
            }
        }

        this.renderer.render(this.scene, this.camera);
    }

    idleAnimation() {
        if (!this.bee) return;
        
        // Gentle floating motion
        this.bee.position.y = Math.sin(this.animationTime * 2) * 0.05;
        
        // Slight wing flutter (rotation)
        this.bee.rotation.z = Math.sin(this.animationTime * 8) * 0.02;
    }

    celebrateAnimation() {
        if (!this.bee) return;
        
        const duration = 2; // 2 seconds
        const progress = (this.animationTime % duration) / duration;
        
        // Single smooth 360-degree rotation (0 to 2π radians)
        this.bee.rotation.y = progress * Math.PI * 2;
        this.bee.position.y = Math.sin(progress * Math.PI * 4) * 0.3;
        this.bee.scale.setScalar(1 + Math.sin(progress * Math.PI * 2) * 0.1);
        
        // Return to idle after duration
        if (progress > 0.95) {
            this.bee.rotation.y = 0; // Reset to starting position
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
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #FFE082 0%, #FFD54F 100%);
                border-radius: 1rem;
                border: 3px solid #FFB300;
            ">
                <div style="font-size: 4rem; animation: bounce 1s infinite;">🐝</div>
            </div>
        `;
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
    
    // Control methods for external access
    rotate(pitchRad = 0, yawRad = 0) {
        if (this.bee) {
            this.bee.rotation.x += (pitchRad || 0);
            this.bee.rotation.y += (yawRad || 0);
            console.log(`🔄 Rotate: pitch=${this.bee.rotation.x.toFixed(2)}, yaw=${this.bee.rotation.y.toFixed(2)}`);
            this.pauseAutoAnimations();
        }
    }
    
    zoom(delta = 0) {
        if (this.camera) {
            const newZ = this.camera.position.z + delta;
            this.camera.position.z = Math.max(0.8, Math.min(10, newZ));
            console.log(`🔍 Zoom: camera.z=${this.camera.position.z.toFixed(2)} (delta=${delta.toFixed(2)})`);
            this.pauseAutoAnimations();
        }
    }
    
    resetView() {
        if (this.camera && this.defaultCameraPos) {
            this.camera.position.copy(this.defaultCameraPos);
            console.log(`🔄 Reset camera to z=${this.defaultCameraPos.z.toFixed(2)}`);
        }
        if (this.bee && this.defaultBeeRotation) {
            this.bee.rotation.copy(this.defaultBeeRotation);
            console.log(`🔄 Reset bee rotation to y=${this.defaultBeeRotation.y.toFixed(2)}`);
        }
        this.resumeAutoAnimations();
    }
    
    pauseAutoAnimations() {
        this.manualControl = true;
        console.log('⏸️ Auto-animations paused for manual control');
        
        // Resume after 2 seconds of no interaction
        if (this.manualControlResumeTimer) {
            clearTimeout(this.manualControlResumeTimer);
        }
        this.manualControlResumeTimer = setTimeout(() => {
            this.resumeAutoAnimations();
        }, 2000);
    }
    
    resumeAutoAnimations() {
        this.manualControl = false;
        console.log('▶️ Auto-animations resumed');
        if (this.manualControlResumeTimer) {
            clearTimeout(this.manualControlResumeTimer);
            this.manualControlResumeTimer = null;
        }
    }
}

// Static instance registry
SmartyBee3D.instances = {};

// Static method to get controller by container ID
SmartyBee3D.getController = function(containerId) {
    return SmartyBee3D.instances[containerId] || null;
};

// Make it globally available
window.SmartyBee3D = SmartyBee3D;
