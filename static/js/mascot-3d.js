/**
 * Smarty Bee 3D Mascot Component
 * Renders and animates the 3D bee mascot using Three.js
 */

class SmartyBee3D {
    constructor(containerId, options = {}) {
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
            // Build paths from injected base to avoid root-relative 404s
            modelBase: (typeof window !== 'undefined' && window.BEE_MODEL_BASE) ? window.BEE_MODEL_BASE : '/static/models/',
            modelName: options.modelName || 'MascotBee_1019174653_texture',
            modelPath: options.modelPath, // optional absolute override
            texturePath: options.texturePath, // optional absolute override
            mtlPath: options.mtlPath, // optional absolute override
            ...options
        };

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bee = null;
        this.animationId = null;
        this.isHovering = false;
        
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

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true 
        });
        this.renderer.setSize(this.options.width, this.options.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // Make canvas transparent to pointer events so parent div's onclick works
        this.renderer.domElement.style.pointerEvents = 'none';
        
        this.container.appendChild(this.renderer.domElement);
    }

    setupLighting() {
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // Directional light for shadows and definition
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);

        // Fill light from the side
        const fillLight = new THREE.DirectionalLight(0xffd700, 0.4);
        fillLight.position.set(-5, 0, 5);
        this.scene.add(fillLight);
    }

    loadModel() {
        const mtlLoader = new THREE.MTLLoader();
        const objLoader = new THREE.OBJLoader();

        // Resolve base and filenames
        let base, mtlPath, objPath, texPath, mtlFilename, objFilename;
        
        // Check if absolute paths are provided
        if (this.options.mtlPath && this.options.mtlPath.startsWith('/')) {
            // Absolute paths provided - extract directory and filename
            mtlPath = this.options.mtlPath;
            objPath = this.options.modelPath || mtlPath.replace('.mtl', '.obj');
            texPath = this.options.texturePath || mtlPath.replace('.mtl', '.png');
            
            // Extract base directory from the path
            base = mtlPath.substring(0, mtlPath.lastIndexOf('/') + 1);
            mtlFilename = mtlPath.substring(mtlPath.lastIndexOf('/') + 1);
            objFilename = objPath.substring(objPath.lastIndexOf('/') + 1);
        } else {
            // Relative paths - use modelBase
            base = this.options.modelBase.endsWith('/') ? this.options.modelBase : this.options.modelBase + '/';
            const modelName = this.options.modelName;
            mtlPath = this.options.mtlPath || `${base}${modelName}.mtl`;
            objPath = this.options.modelPath || `${base}${modelName}.obj`;
            texPath = this.options.texturePath || `${base}${modelName}.png`;
            mtlFilename = mtlPath.substring(mtlPath.lastIndexOf('/') + 1);
            objFilename = objPath.substring(objPath.lastIndexOf('/') + 1);
        }

        console.log('🐝 Loading 3D model from:', base);
        console.log('   MTL:', mtlFilename);
        console.log('   OBJ:', objFilename);
        console.log('   Texture:', texPath);
        
        // Cache-busting: add timestamp to force reload of updated files
        const cacheBuster = Date.now();
        const mtlFilenameWithCache = `${mtlFilename}?v=${cacheBuster}`;
        const objFilenameWithCache = `${objFilename}?v=${cacheBuster}`;
        const texPathWithCache = `${texPath}?v=${cacheBuster}`;

        // Configure loader base and resource paths
        mtlLoader.setPath(base);
        mtlLoader.setResourcePath(base);

        // Load MTL first (materials and textures)
        mtlLoader.load(
            mtlFilenameWithCache,
            (materials) => {
                console.log('✅ MTL materials loaded successfully');
                
                // CRITICAL FIX: Manually set the texture map for all materials
                // because MTL loader might not resolve texture paths correctly
                const textureLoader = new THREE.TextureLoader();
                console.log('🔧 Manually loading texture:', texPathWithCache);
                
                textureLoader.load(
                    texPathWithCache,
                    (texture) => {
                        console.log('✅ Texture loaded, applying to materials');
                        // Apply texture to all materials in the MTL
                        for (const materialName in materials.materials) {
                            const material = materials.materials[materialName];
                            if (material) {
                                material.map = texture;
                                material.needsUpdate = true;
                                console.log(`   Applied texture to material: ${materialName}`);
                            }
                        }
                        
                        materials.preload();
                        objLoader.setMaterials(materials);

                        // Configure OBJ loader base/resource paths as well
                        objLoader.setPath(base);
                        objLoader.setResourcePath(base);

                        // Now load OBJ with materials applied
                        objLoader.load(
                            objFilenameWithCache,
                            (object) => {
                                // IMPROVED: Better centering and camera positioning to prevent cropping
                                const box = new THREE.Box3().setFromObject(object);
                                const center = box.getCenter(new THREE.Vector3());
                                const size = box.getSize(new THREE.Vector3());
                                
                                const maxDim = Math.max(size.x, size.y, size.z);
                                const scaleMultiplier = (this.options && this.options.scaleMultiplier) ? this.options.scaleMultiplier : 1;
                                const scale = (3 * scaleMultiplier) / maxDim;
                                object.scale.set(scale, scale, scale);
                                
                                // Center the model properly at origin
                                object.position.x = -center.x * scale;
                                object.position.y = -center.y * scale;
                                object.position.z = -center.z * scale;

                                this.bee = object;
                                this.scene.add(object);
                                
                                // AVATAR CLIPPING FIX: Move bee model up to show bottom stinger/feet
                                object.position.y += 0.35;
                                
                                // Pull camera back further and position slightly higher to show full model
                                const maxScaledDim = maxDim * scale;
                                this.camera.position.z = maxScaledDim * 1.8; // Pull back more
                                this.camera.position.y = maxScaledDim * 0.15; // Raise camera slightly
                                this.camera.lookAt(0, 0, 0); // Look at center
                                this.camera.updateProjectionMatrix();
                                
                                if (this.renderer && typeof this.renderer.setScissorTest === 'function') {
                                    this.renderer.setScissorTest(false);
                                }
                                
                                console.log('✅ Mascot Bee 3D model loaded successfully with textures!');
                                window.mascotBeeLoaded = true;
                            },
                            (xhr) => {
                                const percentComplete = (xhr.loaded / xhr.total * 100).toFixed(0);
                                console.log(`Loading model: ${percentComplete}%`);
                            },
                            (error) => {
                                console.error('Error loading OBJ model:', error);
                                // Quick HEAD check for diagnostics
                                fetch(objPath, { method: 'HEAD' })
                                    .then(r => console.warn(`OBJ HEAD ${r.status} for ${objPath}`))
                                    .catch(e => console.warn('OBJ HEAD check failed', e));
                                this.addFallbackBee();
                            }
                        );
                    },
                    undefined, // onProgress callback
                    (error) => {
                        console.error('❌ Error loading texture for MTL:', error);
                        // Continue anyway with materials but no texture
                        materials.preload();
                        objLoader.setMaterials(materials);
                        objLoader.setPath(base);
                        objLoader.setResourcePath(base);
                        
                        // Load OBJ without texture
                        objLoader.load(
                            objFilename,
                            (object) => {
                                // IMPROVED: Better centering and camera positioning to prevent cropping
                                const box = new THREE.Box3().setFromObject(object);
                                const center = box.getCenter(new THREE.Vector3());
                                const size = box.getSize(new THREE.Vector3());
                                
                                const maxDim = Math.max(size.x, size.y, size.z);
                                const scaleMultiplier = (this.options && this.options.scaleMultiplier) ? this.options.scaleMultiplier : 1;
                                const scale = (3 * scaleMultiplier) / maxDim;
                                object.scale.set(scale, scale, scale);
                                
                                // Center the model properly at origin
                                object.position.x = -center.x * scale;
                                object.position.y = -center.y * scale;
                                object.position.z = -center.z * scale;

                                this.bee = object;
                                this.scene.add(object);
                                
                                // AVATAR CLIPPING FIX: Move bee model up to show bottom stinger/feet
                                object.position.y += 0.35;
                                
                                // Pull camera back further and position slightly higher to show full model
                                const maxScaledDim = maxDim * scale;
                                this.camera.position.z = maxScaledDim * 1.8; // Pull back more
                                this.camera.position.y = maxScaledDim * 0.15; // Raise camera slightly
                                this.camera.lookAt(0, 0, 0); // Look at center
                                this.camera.updateProjectionMatrix();
                                
                                if (this.renderer && typeof this.renderer.setScissorTest === 'function') {
                                    this.renderer.setScissorTest(false);
                                }
                                
                                console.log('⚠️ Mascot loaded but texture failed');
                                window.mascotBeeLoaded = true;
                            },
                            undefined,
                            (error) => {
                                console.error('Error loading OBJ:', error);
                                this.addFallbackBee();
                            }
                        );
                    }
                );
            },
            (xhr) => {
                const percentLoaded = xhr.loaded / xhr.total * 100;
                console.log(`Loading materials: ${percentLoaded.toFixed(0)}%`);
            },
            (error) => {
                console.error('❌ Error loading MTL materials:', error);
                console.error('   MTL path attempted:', base + mtlFilename);
                console.error('   Full MTL path:', mtlPath);
                console.error('   Error type:', error.type || 'unknown');
                console.error('   Error message:', error.message || error.toString());
                // Fallback: try loading without materials
                this.loadModelWithoutMaterials(base, objPath, texPath);
            }
        );
    }

    loadModelWithoutMaterials(base, objPath, texPath) {
        // Fallback method if MTL loading fails
        console.log('⚠️ Attempting fallback load without MTL');
        const loader = new THREE.OBJLoader();
        const textureLoader = new THREE.TextureLoader();
        
        // Extract filename for OBJ
        const objFilename = objPath.substring(objPath.lastIndexOf('/') + 1);
        
        loader.setPath(base);
        loader.setResourcePath(base);

        // Load texture with absolute path
        console.log('📦 Loading texture from:', texPath);
        textureLoader.load(
            texPath,
            (texture) => {
                console.log('✅ Texture loaded successfully');
                // Load OBJ model
                loader.load(
                    objFilename,
                    (object) => {
                        // Apply texture to all meshes
                        object.traverse((child) => {
                            if (child instanceof THREE.Mesh) {
                                child.material = new THREE.MeshPhongMaterial({
                                    map: texture,
                                    shininess: 30
                                });
                            }
                        });

                        // Center and scale the model
                        const box = new THREE.Box3().setFromObject(object);
                        const center = box.getCenter(new THREE.Vector3());
                        const size = box.getSize(new THREE.Vector3());
                        
                        const maxDim = Math.max(size.x, size.y, size.z);
                        const scaleMultiplier = (this.options && this.options.scaleMultiplier) ? this.options.scaleMultiplier : 1;
                        const scale = (3 * scaleMultiplier) / maxDim;
                        object.scale.set(scale, scale, scale);
                        
                        object.position.sub(center.multiplyScalar(scale));

                        this.bee = object;
                        this.scene.add(object);
                        
                        // AVATAR CLIPPING FIX: Move bee model up to show bottom stinger/feet
                        object.position.y += 0.35;
                        
                        // Slight upward camera bias for safety in fallback path
                        try {
                            const boxSize = Math.max(size.x, size.y, size.z) * scale;
                            this.camera.position.y += 0.07 * boxSize;
                            this.camera.updateProjectionMatrix();
                            if (this.renderer && typeof this.renderer.setScissorTest === 'function') {
                                this.renderer.setScissorTest(false);
                            }
                        } catch (e) { /* no-op */ }
                        
                        console.log('✅ Mascot Bee 3D model loaded (fallback mode without MTL)');
                        window.mascotBeeLoaded = true;
                    },
                    (xhr) => {
                        const percentComplete = (xhr.loaded / xhr.total * 100).toFixed(0);
                        console.log(`Loading model: ${percentComplete}%`);
                    },
                    (error) => {
                        console.error('❌ Error loading OBJ model in fallback:', error);
                        console.error('   OBJ path attempted:', base + objFilename);
                        this.addFallbackBee();
                    }
                );
            },
            undefined,
            (error) => {
                console.error('❌ Error loading texture in fallback:', error);
                console.error('   Texture path attempted:', texPath);
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
        // Lightweight 3D fallback so UI still looks alive if OBJ/MTL missing
        try {
            const geom = new THREE.SphereGeometry(1, 20, 20);
            const mat = new THREE.MeshStandardMaterial({ color: 0xffdd00, metalness: 0.2, roughness: 0.6 });
            const bee = new THREE.Mesh(geom, mat);
            bee.position.set(0, 1, 0);
            this.scene.add(bee);
            
            // AVATAR CLIPPING FIX: Move fallback bee up to show bottom
            bee.position.y += 0.35;
            
            this.bee = bee;
            console.warn('Fallback 3D bee added (OBJ not available).');
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

            // Auto-rotate if enabled - rotate around Y-axis to show all sides
            if (this.options.autoRotate && !this.isHovering) {
                this.bee.rotation.y += 0.005;
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
}

// Make it globally available
window.SmartyBee3D = SmartyBee3D;
