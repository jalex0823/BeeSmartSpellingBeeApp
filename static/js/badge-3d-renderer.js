/**
 * Badge 3D Renderer - GLB Badge Display System
 * Renders 3D GLB badge models in place of PNG images throughout the app
 * Uses THREE.js and GLTFLoader for 3D model rendering
 */

class Badge3DRenderer {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' 
            ? document.getElementById(container) || document.querySelector(container)
            : container;
        
        if (!this.container) {
            console.error('❌ Badge3DRenderer: Container not found');
            return;
        }
        
        this.options = {
            badgeFile: options.badgeFile || 'Novice.glb',
            width: options.width || 60,
            height: options.height || 60,
            autoRotate: options.autoRotate === true, // Default to false unless explicitly true
            rotationSpeed: options.rotationSpeed || 0.5,
            cameraDistance: options.cameraDistance || 2.5,
            enableLighting: options.enableLighting !== false,
            backgroundColor: options.backgroundColor || 'transparent',
            enableShadow: options.enableShadow !== false,
            ...options
        };
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.model = null;
        this.animationId = null;
        this.isLoaded = false;
        
        this.init();
    }
    
    init() {
        // Verify THREE.js is available
        if (typeof THREE === 'undefined') {
            console.error('❌ THREE.js not loaded - required for 3D badges');
            this.fallbackToPNG();
            return;
        }
        
        // Verify GLTFLoader is available
        if (typeof THREE.GLTFLoader === 'undefined') {
            console.error('❌ GLTFLoader not loaded - required for GLB badges');
            this.fallbackToPNG();
            return;
        }
        
        this.createScene();
        this.loadBadge();
    }
    
    createScene() {
        // Create scene
        this.scene = new THREE.Scene();
        if (this.options.backgroundColor !== 'transparent') {
            this.scene.background = new THREE.Color(this.options.backgroundColor);
        }
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            45,
            this.options.width / this.options.height,
            0.1,
            1000
        );
        this.camera.position.z = this.options.cameraDistance;
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({
            alpha: true,
            antialias: true,
            preserveDrawingBuffer: true
        });
        this.renderer.setSize(this.options.width, this.options.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        if (this.options.enableShadow) {
            this.renderer.shadowMap.enabled = true;
            this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        }
        
        // Setup lighting
        if (this.options.enableLighting) {
            // Ambient light for overall illumination - BRIGHTENED
            const ambientLight = new THREE.AmbientLight(0xffffff, 2.0);
            this.scene.add(ambientLight);
            
            // Directional light for highlights - BRIGHTENED
            const dirLight = new THREE.DirectionalLight(0xffffff, 2.5);
            dirLight.position.set(2, 3, 2);
            if (this.options.enableShadow) {
                dirLight.castShadow = true;
                dirLight.shadow.mapSize.width = 1024;
                dirLight.shadow.mapSize.height = 1024;
            }
            this.scene.add(dirLight);
            
            // Rim light for depth - BRIGHTENED
            const rimLight = new THREE.DirectionalLight(0xffd700, 0.6);
            rimLight.position.set(-1, -1, -2);
            this.scene.add(rimLight);
        }
        
        // Clear container and append canvas
        this.container.innerHTML = '';
        this.container.appendChild(this.renderer.domElement);
        
        // Style canvas
        this.renderer.domElement.style.display = 'block';
        this.renderer.domElement.style.borderRadius = '8px';
    }
    
    loadBadge() {
        const badgePath = `/static/assets/badges/glb_files/${this.options.badgeFile}`;
        const loader = new THREE.GLTFLoader();
        
        console.log(`🎖️ Loading 3D badge: ${badgePath}`);
        
        loader.load(
            badgePath,
            (gltf) => {
                this.model = gltf.scene;
                
                // Center and scale the model
                const box = new THREE.Box3().setFromObject(this.model);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                
                // Center model
                this.model.position.x = -center.x;
                this.model.position.y = -center.y;
                this.model.position.z = -center.z;
                
                // Scale to fit
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 1.8 / maxDim;
                this.model.scale.setScalar(scale);
                
                // Rotate badge to face front (Y-axis rotation)
                this.model.rotation.y = -Math.PI / 2; // -90 degrees to show FRONT face
                
                // Enable shadows if supported
                if (this.options.enableShadow) {
                    this.model.traverse((child) => {
                        if (child.isMesh) {
                            child.castShadow = true;
                            child.receiveShadow = true;
                        }
                    });
                }
                
                this.scene.add(this.model);
                this.isLoaded = true;
                
                // Start animation loop
                this.animate();
                
                console.log(`✅ 3D badge loaded: ${this.options.badgeFile}`);
            },
            (progress) => {
                // Progress callback (optional)
                const percentComplete = (progress.loaded / progress.total) * 100;
                console.log(`Loading badge: ${percentComplete.toFixed(0)}%`);
            },
            (error) => {
                console.error('❌ Error loading 3D badge:', error);
                this.fallbackToPNG();
            }
        );
    }
    
    animate() {
        if (!this.isLoaded || !this.renderer || !this.scene || !this.camera) {
            return;
        }
        
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Auto-rotate badge
        if (this.options.autoRotate && this.model) {
            this.model.rotation.y += this.options.rotationSpeed * 0.01;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    fallbackToPNG() {
        // Fallback to PNG badge if 3D rendering fails
        const pngFile = this.options.badgeFile.replace('.glb', '.png');
        const pngPath = `/static/assets/badges/${pngFile}`;
        
        console.warn(`⚠️ Falling back to PNG badge: ${pngPath}`);
        
        const img = document.createElement('img');
        img.src = pngPath;
        img.alt = 'Badge';
        img.style.width = `${this.options.width}px`;
        img.style.height = `${this.options.height}px`;
        img.style.objectFit = 'contain';
        img.style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))';
        
        this.container.innerHTML = '';
        this.container.appendChild(img);
    }
    
    destroy() {
        // Stop animation
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        // Dispose of Three.js resources
        if (this.model) {
            this.model.traverse((child) => {
                if (child.isMesh) {
                    if (child.geometry) child.geometry.dispose();
                    if (child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(mat => mat.dispose());
                        } else {
                            child.material.dispose();
                        }
                    }
                }
            });
            this.scene.remove(this.model);
            this.model = null;
        }
        
        if (this.renderer) {
            this.renderer.dispose();
            if (this.renderer.domElement && this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
            this.renderer = null;
        }
        
        this.scene = null;
        this.camera = null;
        this.isLoaded = false;
    }
    
    updateBadge(badgeFile) {
        this.options.badgeFile = badgeFile;
        this.destroy();
        this.init();
    }
}

// Global helper function for easy badge rendering
window.renderBadge3D = function(container, badgeFile, options = {}) {
    return new Badge3DRenderer(container, {
        badgeFile,
        ...options
    });
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Badge3DRenderer;
}

window.Badge3DRenderer = Badge3DRenderer;
