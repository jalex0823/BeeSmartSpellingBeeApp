/**
 * Honeycomb Avatar Picker JavaScript
 * Handles hexagonal grid layout with 3D avatar rendering
 */

let avatars = [];
let selectedAvatar = null;
let viewer3D = null;

// Hexagon position mapping (percentage-based for responsiveness)
// Based on the SVG hexagon centers
const HEXAGON_POSITIONS = [
    // Row 1 (2 hexagons)
    { top: '13%', left: '10.7%' },  // hex 0
    { top: '13%', left: '25%' },    // hex 1
    
    // Row 2 (3 hexagons)
    { top: '27%', left: '3.6%' },   // hex 2
    { top: '27%', left: '17.9%' },  // hex 3
    { top: '27%', left: '32.1%' },  // hex 4
    
    // Row 3 (4 hexagons)
    { top: '41%', left: '10.7%' },  // hex 5
    { top: '41%', left: '25%' },    // hex 6
    { top: '41%', left: '39.3%' },  // hex 7
    { top: '41%', left: '53.6%' },  // hex 8
    
    // Row 4 (5 hexagons) - Center row
    { top: '55%', left: '3.6%' },   // hex 9
    { top: '55%', left: '17.9%' },  // hex 10
    { top: '55%', left: '32.1%' },  // hex 11
    { top: '55%', left: '46.4%' },  // hex 12
    { top: '55%', left: '60.7%' },  // hex 13
    
    // Row 5 (4 hexagons)
    { top: '69%', left: '10.7%' },  // hex 14
    { top: '69%', left: '25%' },    // hex 15
    { top: '69%', left: '39.3%' },  // hex 16
    { top: '69%', left: '53.6%' },  // hex 17
    
    // Row 6 (3 hexagons)
    { top: '83%', left: '3.6%' },   // hex 18
    { top: '83%', left: '17.9%' },  // hex 19
    { top: '83%', left: '32.1%' },  // hex 20
    
    // Row 7 (2 hexagons)
    { top: '97%', left: '10.7%' },  // hex 21
    { top: '97%', left: '25%' },    // hex 22
];

// Load avatars on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAvatars();
});

async function loadAvatars() {
    const container = document.getElementById('honeycombGrid');
    
    try {
        // Show loading indicator
        if (container) {
            container.innerHTML = `
                <div class="avatar-hex-loading">🐝</div>
            `;
        }

        // Fetch avatars
        const response = await fetch('/api/avatars');
        const data = await response.json();
        
        if (data.status === 'success') {
            avatars = data.avatars;
            renderHoneycombGrid(avatars);
        } else {
            console.error('Failed to load avatars:', data);
            if (container) {
                container.innerHTML = `
                    <div style="color: #FF6B6B; text-align: center; padding: 2rem;">
                        Failed to load bee avatars. Please refresh the page.
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading avatars:', error);
        if (container) {
            container.innerHTML = `
                <div style="color: #FF6B6B; text-align: center; padding: 2rem;">
                    Error loading avatars: ${error.message}
                </div>
            `;
        }
    }
}

function renderHoneycombGrid(avatarsToRender) {
    const container = document.getElementById('honeycombGrid');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create avatar containers positioned at hexagon centers
    avatarsToRender.slice(0, HEXAGON_POSITIONS.length).forEach((avatar, index) => {
        const position = HEXAGON_POSITIONS[index];
        const hexContainer = document.createElement('div');
        hexContainer.className = 'avatar-hex-position';
        hexContainer.style.top = position.top;
        hexContainer.style.left = position.left;
        hexContainer.dataset.avatarId = avatar.id;
        
        // Thumbnail container
        const thumbDiv = document.createElement('div');
        thumbDiv.className = 'avatar-hex-thumb';
        thumbDiv.id = `hex-thumb-${avatar.id}`;
        
        // Name label
    const nameDiv = document.createElement('div');
    nameDiv.className = 'avatar-hex-name';
    nameDiv.textContent = avatar.name;
    // Accessibility + tooltip for optional label hiding scenarios
    nameDiv.setAttribute('title', avatar.name);
    hexContainer.setAttribute('aria-label', avatar.name);
    hexContainer.setAttribute('role', 'button');
    hexContainer.setAttribute('tabindex', '0');
        
        hexContainer.appendChild(thumbDiv);
        hexContainer.appendChild(nameDiv);
        
        // Click handler
        hexContainer.addEventListener('click', () => {
            selectAvatar(avatar);
        });
        
        container.appendChild(hexContainer);
        
        // Render 3D thumbnail
        render3DThumb(thumbDiv, avatar);
    });
}

async function render3DThumb(container, avatar) {
    if (!window.THREE) {
        // Fallback to placeholder
        container.innerHTML = '<div style="font-size: 2rem;">🐝</div>';
        return;
    }
    
    try {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
        camera.position.set(0, 0.5, 2.5);
        
        // 🎨 PREMIUM QUALITY RENDERER for thumbnails
        const renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: 'high-performance',
            precision: 'highp'
        });
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
        renderer.setPixelRatio(pixelRatio);
        renderer.setSize(100, 100);
        renderer.setClearColor(0x000000, 0);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        if (typeof THREE.sRGBEncoding !== 'undefined') {
            renderer.outputEncoding = THREE.sRGBEncoding;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
        }
        container.appendChild(renderer.domElement);
        
        // Lighting
        const ambient = new THREE.AmbientLight(0xffffff, 1.5);
        scene.add(ambient);
        const dir = new THREE.DirectionalLight(0xffffff, 1);
        dir.position.set(5, 10, 7.5);
        scene.add(dir);
        
        // Detect GLB (all avatars are now GLB-only)
        const isGLB = avatar.urls?.glb && avatar.urls.glb.toLowerCase().endsWith('.glb');
        
        if (isGLB && THREE.GLTFLoader) {
            const loader = new THREE.GLTFLoader();
            loader.load(
                avatar.urls.glb,
                (gltf) => {
                    const model = gltf.scene;
                    
                    // 🎨 PREMIUM TEXTURE OPTIMIZATION
                    const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
                    model.traverse((child) => {
                        if (child.isMesh) {
                            child.castShadow = true;
                            child.receiveShadow = true;
                            
                            const materials = Array.isArray(child.material) ? child.material : [child.material];
                            materials.forEach(mat => {
                                if (!mat) return;
                                Object.keys(mat).forEach(key => {
                                    const value = mat[key];
                                    if (value && value.isTexture) {
                                        value.anisotropy = maxAnisotropy;
                                        value.encoding = THREE.sRGBEncoding;
                                        value.needsUpdate = true;
                                    }
                                });
                            });
                        }
                    });
                    
                    // Center and scale
                    const box = new THREE.Box3().setFromObject(model);
                    const size = box.getSize(new THREE.Vector3()).length();
                    const center = box.getCenter(new THREE.Vector3());
                    model.position.sub(center);
                    model.scale.setScalar(2.0 / size);
                    
                    scene.add(model);
                    
                    // Animation
                    function animate() {
                        requestAnimationFrame(animate);
                        model.rotation.y += 0.01;
                        renderer.render(scene, camera);
                    }
                    animate();
                },
                undefined,
                (error) => {
                    console.warn('GLB load failed:', error);
                    container.innerHTML = '<div style="font-size: 2rem;">🐝</div>';
                }
            );
        } else {
            // Fallback to bee emoji
            container.innerHTML = '<div style="font-size: 2rem;">🐝</div>';
        }
    } catch (error) {
        console.warn('3D rendering failed:', error);
        container.innerHTML = '<div style="font-size: 2rem;">🐝</div>';
    }
}

function selectAvatar(avatar) {
    selectedAvatar = avatar;
    
    // Update selected state in grid
    document.querySelectorAll('.avatar-hex-position').forEach(el => {
        el.classList.remove('selected');
        const checkmark = el.querySelector('.avatar-hex-checkmark');
        if (checkmark) checkmark.remove();
    });
    
    const selectedEl = document.querySelector(`[data-avatar-id="${avatar.id}"]`);
    if (selectedEl) {
        selectedEl.classList.add('selected');
        
        // Add checkmark
        const checkmark = document.createElement('div');
        checkmark.className = 'avatar-hex-checkmark';
        checkmark.innerHTML = '✓';
        selectedEl.appendChild(checkmark);
    }
    
    // Update preview panel
    updatePreview();
}

function updatePreview() {
    const preview = document.getElementById('previewPanel');
    if (!preview) return;
    
    if (!selectedAvatar) {
        preview.innerHTML = `
            <div class="preview-placeholder">
                <div class="preview-placeholder-icon">🐝</div>
                <div class="preview-placeholder-text">Select a bee avatar to preview</div>
            </div>
        `;
        return;
    }
    
    preview.innerHTML = `
        <div class="preview-avatar-name" title="${selectedAvatar.name}">${selectedAvatar.name}</div>
        <div class="preview-avatar-render" id="previewRender"></div>
        <div class="preview-avatar-description">${selectedAvatar.description || 'A wonderful bee companion!'}</div>
        <button class="preview-select-button" onclick="saveSelectedAvatar()">
            Choose This Bee
        </button>
    `;
    
    // Render 3D preview (larger)
    const renderContainer = document.getElementById('previewRender');
    if (renderContainer && window.THREE) {
        render3DPreview(renderContainer, selectedAvatar);
    }
}

async function render3DPreview(container, avatar) {
    // Similar to thumbnail but larger
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0.5, 3);
    
    // 🎨 PREMIUM PREVIEW RENDERER
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true, 
        alpha: true,
        powerPreference: 'high-performance',
        precision: 'highp'
    });
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000000, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    if (typeof THREE.sRGBEncoding !== 'undefined') {
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
    }
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 1.5);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 1.5);
    dir.position.set(5, 10, 7.5);
    scene.add(dir);
    
    const isGLB = avatar.urls?.glb && avatar.urls.glb.toLowerCase().endsWith('.glb');
    
    if (isGLB && THREE.GLTFLoader) {
        const loader = new THREE.GLTFLoader();
        loader.load(
            avatar.urls.glb,
            (gltf) => {
                const model = gltf.scene;
                
                // 🎨 PREMIUM TEXTURE OPTIMIZATION for preview
                const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
                model.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                        
                        const materials = Array.isArray(child.material) ? child.material : [child.material];
                        materials.forEach(mat => {
                            if (!mat) return;
                            Object.keys(mat).forEach(key => {
                                const value = mat[key];
                                if (value && value.isTexture) {
                                    value.anisotropy = maxAnisotropy;
                                    value.encoding = THREE.sRGBEncoding;
                                    value.needsUpdate = true;
                                }
                            });
                        });
                    }
                });
                
                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3()).length();
                const center = box.getCenter(new THREE.Vector3());
                model.position.sub(center);
                model.scale.setScalar(2.2 / size);
                
                scene.add(model);
                
                // Interactive rotation
                let isDragging = false;
                let previousMouseX = 0;
                
                renderer.domElement.addEventListener('mousedown', () => { isDragging = true; });
                renderer.domElement.addEventListener('mouseup', () => { isDragging = false; });
                renderer.domElement.addEventListener('mousemove', (e) => {
                    if (isDragging) {
                        const deltaX = e.clientX - previousMouseX;
                        model.rotation.y += deltaX * 0.01;
                    }
                    previousMouseX = e.clientX;
                });
                
                function animate() {
                    requestAnimationFrame(animate);
                    if (!isDragging) {
                        model.rotation.y += 0.005;
                    }
                    renderer.render(scene, camera);
                }
                animate();
            },
            undefined,
            (error) => {
                console.warn('Preview GLB load failed:', error);
                container.innerHTML = '<div style="font-size: 5rem; text-align: center; padding: 3rem;">🐝</div>';
            }
        );
    }
}

async function saveSelectedAvatar() {
    if (!selectedAvatar) return;
    
    try {
        const response = await fetch('/api/user/avatar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                avatar_id: selectedAvatar.id
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert(`${selectedAvatar.name} selected! 🐝`);
            // Optionally redirect or update UI
            window.location.href = '/dashboard';
        } else {
            alert('Failed to save avatar: ' + data.message);
        }
    } catch (error) {
        console.error('Error saving avatar:', error);
        alert('Error saving avatar. Please try again.');
    }
}

// Search functionality
function filterAvatars(searchTerm) {
    if (!searchTerm) {
        renderHoneycombGrid(avatars);
        return;
    }
    
    const filtered = avatars.filter(avatar => 
        avatar.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (avatar.description && avatar.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    
    renderHoneycombGrid(filtered);
}

// Expose to global scope for HTML events
window.filterAvatars = filterAvatars;
window.saveSelectedAvatar = saveSelectedAvatar;
