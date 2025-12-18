/**
 * Avatar Picker JavaScript
 * Handles avatar selection, 3D preview, and saving
 */

// GLB Cache - avoid re-downloading same models
const GLB_CACHE = new Map(); // avatarId -> gltf object
const GLB_LOADING = new Map(); // avatarId -> Promise (prevent duplicate loads)
const MAX_CACHE_SIZE = 10; // Limit to 10 cached models (~200-250MB max)

let avatars = [];
let selectedAvatar = null;
let viewer3D = null;

// Load avatars on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAvatars();
});

async function loadAvatars() {
    const grid = document.getElementById('avatarGrid');
    
    try {
        // Show loading indicator
        if (grid) {
            grid.innerHTML = `
                <div class="avatar-loading-indicator" style="
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 3rem 2rem;
                    color: #FF9800;
                    font-size: 1.1rem;
                    font-weight: 600;
                    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%);
                    border-radius: 0.75rem;
                    margin-bottom: 1rem;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🐝</div>
                    <div class="loading-text">Loading bee avatars...</div>
                    <div class="loading-progress" style="
                        margin-top: 1rem;
                        font-size: 0.9rem;
                        color: #666;
                    ">
                        <span id="avatarLoadCount">0</span> avatars ready
                    </div>
                    <div role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="Avatar list loading progress" style="width: min(60vw, 240px); height: 0.5rem; background: rgba(255, 152, 0, 0.2); border-radius: 9999px; margin: 1rem auto; overflow: hidden;">
                        <div id="avatarLoadBar" style="
                            width: 0%;
                            height: 100%;
                            background: linear-gradient(90deg, #FFD700, #FF9800);
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                </div>
            `;
        }
        
        console.log('🐝 Fetching avatars from /api/avatars...');
        const response = await fetch('/api/avatars');
        const data = await response.json();
        console.log('📦 API Response:', data);
        
        if (data.status === 'success') {
            avatars = data.avatars;
            console.log(`✅ Loaded ${avatars.length} avatars`);
            if (avatars.length > 0) {
                console.log('🔍 First avatar sample:', avatars[0]);
            }
            
            // Update progress bar to 100%
            const loadBar = document.getElementById('avatarLoadBar');
            const loadCount = document.getElementById('avatarLoadCount');
            if (loadBar && loadCount) {
                loadCount.textContent = avatars.length;
                loadBar.style.width = '100%';
                const outer = loadBar.parentElement;
                if (outer && outer.getAttribute('role') === 'progressbar') {
                    outer.setAttribute('aria-valuenow', '100');
                }
            }
            
            // Update test page avatar count if present
            const avatarCountSpan = document.getElementById('avatarCount');
            if (avatarCountSpan) {
                avatarCountSpan.textContent = avatars.length;
            }
            
            // ✅ Calculate and update owned/unlocked avatar counts
            const unlockedCount = avatars.filter(a => !a.is_locked).length;
            const lockedCount = avatars.filter(a => a.is_locked).length;
            console.log(`📊 Avatar library status: ${unlockedCount} unlocked, ${lockedCount} locked, ${avatars.length} total`);
            
            // Update any avatar status displays on the page
            updateAvatarCountDisplays(avatars.length, unlockedCount, lockedCount);
            
            // Small delay to show completion
            await new Promise(resolve => setTimeout(resolve, 300));
            
            renderAvatarGrid(avatars);
        } else {
            console.error('❌ API returned error status');
            if (grid) {
                grid.innerHTML = '<p style="padding: 2rem; text-align: center; color: #f56565;">Failed to load avatars. Please refresh the page.</p>';
            }
        }
    } catch (error) {
        console.error('❌ Error loading avatars:', error);
        if (grid) {
            grid.innerHTML = '<p style="padding: 2rem; text-align: center; color: #f56565;">Failed to load avatars. Please refresh the page.</p>';
        }
    }
}

function renderAvatarGrid(avatarsToRender) {
    const grid = document.getElementById('avatarGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    console.log(`🎨 Rendering ${avatarsToRender.length} avatar cards with 3D OBJ thumbnails...`);
    
    avatarsToRender.forEach(avatar => {
        const card = document.createElement('div');
        card.className = 'avatar-option';
        card.dataset.avatarId = avatar.id;
        
        // Add locked class if avatar is locked
        if (avatar.is_locked) {
            card.classList.add('locked');
            card.title = 'Locked - Earn or purchase to unlock';
        }

        // Create 3D thumbnail container (render OBJ as thumbnail)
        const thumbContainer = document.createElement('div');
        thumbContainer.className = 'avatar-3d-thumbnail';
        thumbContainer.style.width = '100%';
        thumbContainer.style.height = '120px';
        thumbContainer.style.position = 'relative';
        thumbContainer.style.overflow = 'hidden';
        thumbContainer.style.borderRadius = '8px';
        thumbContainer.style.background = 'linear-gradient(135deg, #FFE8CC 0%, #FFD700 100%)';
        
        // Add lock badge for locked avatars
        if (avatar.is_locked) {
            const lockBadge = document.createElement('div');
            lockBadge.className = 'avatar-lock-badge';
            lockBadge.innerHTML = `<span class="lock-icon">🔒</span><span>Locked</span>`;
            thumbContainer.appendChild(lockBadge);
            
            // Add unlock requirement tooltip
            if (avatar.unlock_requirement || avatar.price_usd) {
                const unlockInfo = document.createElement('div');
                unlockInfo.className = 'avatar-unlock-info';
                
                let unlockText = '';
                if (avatar.tier === 'premium') {
                    unlockText = avatar.price_usd ? `Purchase: $${avatar.price_usd}` : 'Premium - Purchase to unlock';
                } else if (avatar.unlock_requirement) {
                    unlockText = `Earn ${avatar.unlock_requirement} 🍯 points`;
                } else {
                    unlockText = 'Complete quizzes to unlock';
                }
                
                unlockInfo.textContent = unlockText;
                card.appendChild(unlockInfo);
            }
        }

        // Use standardized name from catalog (includes "Avatar" suffix for Apple compliance)
        const displayName = avatar.name;

        // Create name div (appears below thumbnail)
        const nameDiv = document.createElement('div');
        nameDiv.className = 'avatar-name';
        nameDiv.dataset.avatarId = avatar.id;
        nameDiv.title = avatar.is_locked ? 'Locked' : 'Click for details';
        nameDiv.textContent = displayName;

        card.appendChild(thumbContainer);
        card.appendChild(nameDiv);

        // Card click selects avatar (unless clicking the name or avatar is locked)
        card.addEventListener('click', (e) => {
            // Prevent selection of locked avatars
            if (avatar.is_locked) {
                console.log(`🔒 Avatar "${avatar.name}" is locked`);
                // Show a friendly message
                showLockedAvatarMessage(avatar);
                return;
            }
            if (!e.target.classList.contains('avatar-name')) {
                selectAvatar(avatar);
            }
        });

        // Name click opens description popup
        nameDiv.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card selection
            showAvatarDescriptionPopup(avatar);
        });
        
        grid.appendChild(card);

        // Use 2D thumbnail (simple and fast)
        const thumbnailUrl = (avatar && avatar.urls && avatar.urls.thumbnail)
            ? avatar.urls.thumbnail
            : (avatar.thumbnail || `/static/assets/avatars/${avatar.id}/thumbnail.png`);
        const img = document.createElement('img');
        img.src = thumbnailUrl;
        img.alt = displayName;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';
        img.style.borderRadius = '0.5rem';
        // Preserve any badges already appended (e.g., lock badge)
        thumbContainer.insertBefore(img, thumbContainer.firstChild);
    });
    
    console.log(`✅ Rendered ${avatarsToRender.length} avatar cards with 2D thumbnails`);
}

// Render a 3D avatar model in a small, consistent-size thumbnail canvas
async function render3DThumbnail(container, avatar) {
    // Optional enhancement: render a tiny rotating GLB thumbnail.
    // If Three.js isn't available (or no GLB URL), callers should fall back to 2D thumbnails.
    if (!container || !window.THREE || !THREE.GLTFLoader) {
        throw new Error('Three.js not available');
    }
    const glbUrl = (avatar && avatar.urls && (avatar.urls.glb || avatar.urls.model_obj))
        ? String(avatar.urls.glb || avatar.urls.model_obj)
        : '';
    if (!glbUrl) {
        throw new Error('No GLB URL available');
    }

    const scene = new THREE.Scene();
    scene.background = null;
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.set(0, 0, 3);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    const sizePx = 140;
    renderer.setSize(sizePx, sizePx);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    container.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 0.6);
    dir.position.set(5, 5, 5);
    scene.add(dir);

    const loader = new THREE.GLTFLoader();
    return new Promise((resolve, reject) => {
        loader.load(
            glbUrl,
            (gltf) => {
                const object = gltf.scene;
                const box = new THREE.Box3().setFromObject(object);
                const sizeVec = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(sizeVec.x, sizeVec.y, sizeVec.z) || 1;
                const center = box.getCenter(new THREE.Vector3());
                object.position.sub(center);
                object.scale.setScalar(1.6 / maxDim);
                scene.add(object);
                let rotation = 0;
                const animate = () => {
                    rotation += 0.01;
                    object.rotation.y = rotation;
                    renderer.render(scene, camera);
                    requestAnimationFrame(animate);
                };
                animate();
                resolve();
            },
            undefined,
            (err) => reject(err)
        );
    });
}

function selectAvatar(avatar) {
    selectedAvatar = avatar;
    
    // Update UI - remove selected from all, add to clicked
    document.querySelectorAll('.avatar-option').forEach(card => {
        card.classList.remove('selected');
    });
    (function(){ const el = document.querySelector(`.avatar-option[data-avatar-id="${avatar.id}"]`); if(el && el.classList) el.classList.add('selected'); })();
    
    // Defer 3D preview loading to not block UI
    const idle = window.requestIdleCallback || function(cb){ return setTimeout(cb, 0); };
    idle(() => {
        updatePreview();
    }, { timeout: 100 });
    
    // Enable select button immediately
    const selectBtn = document.getElementById('selectAvatarBtn');
    if (selectBtn) {
        selectBtn.disabled = false;
    }
}

function updatePreview() {
    if (!selectedAvatar) return;
    
    const preview = document.getElementById('avatarPreview');
    const avatarInfo = document.getElementById('avatarInfo');
    
    if (!preview || !avatarInfo) return;
    
    // Show info
    avatarInfo.style.display = 'block';
    
    // Update info
    const nameEl = document.getElementById('avatarName');
    const descEl = document.getElementById('avatarDescription');
    if (nameEl) nameEl.textContent = selectedAvatar.name;
    if (descEl) descEl.textContent = selectedAvatar.description;
    
    // Detect if GLB format available (ALL avatars are GLB now)
    const isGLB = !!(selectedAvatar.urls && selectedAvatar.urls.glb);
    
    // Try to render 3D preview if GLTFLoader is available
    const loaderCheck = window.THREE && THREE.GLTFLoader;
    
    if (loaderCheck && selectedAvatar.urls) {
        try {
            // Show loading indicator
            preview.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🐝</div>
                    <div role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="Avatar preview loading progress" style="width: min(80%, 320px); height: 0.5rem; background: #FFE8CC; border-radius: 9999px; margin: 1rem auto; overflow: hidden;">
                        <div id="preview3DProgress" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%); transition: width 0.3s ease;"></div>
                    </div>
                    <p id="preview3DText" style="color: #8B6914; font-weight: 600; margin-top: 0.5rem;">Loading 3D model... 0%</p>
                </div>
            `;
            
            const progressBar = document.getElementById('preview3DProgress');
            const progressText = document.getElementById('preview3DText');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, preview.clientWidth / preview.clientHeight, 0.1, 1000);
            camera.position.set(0, 0.5, 3.0);  // Moved up from 1.1 to 0.5
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(preview.clientWidth, preview.clientHeight);
            renderer.setClearColor(0x000000, 0);

            const ambient = new THREE.AmbientLight(0xffffff, 1.5); // Brighter ambient light
            scene.add(ambient);
            const dir = new THREE.DirectionalLight(0xffffff, 1.5); // Brighter directional light
            dir.position.set(5, 10, 7.5);
            scene.add(dir);
            
            renderer.outputColorSpace = THREE.SRGBColorSpace; // Correct color space for GLB
            
            // Add OrbitControls for better interaction (zoom, pan, rotate)
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.1;
            controls.screenSpacePanning = false;
            controls.minDistance = 1;
            controls.maxDistance = 10;
            controls.target.set(0, 0.5, 0);
            controls.autoRotate = true; // Enable auto-rotation
            controls.autoRotateSpeed = 1.0; // Adjust speed as needed
            controls.update();
            
            // Stop auto-rotation on user interaction
            controls.addEventListener('start', () => {
                controls.autoRotate = false;
            });

            // Mouse controls for rotation and position
            let isDragging = false;
            let previousMousePosition = { x: 0, y: 0 };
            let rotationX = 0;
            let rotationY = 0;
            let positionX = 0;
            let positionY = 0.3;  // Start higher (moved up)
            
            renderer.domElement.addEventListener('mousedown', (e) => {
                isDragging = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });
            
            renderer.domElement.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;
                
                if (e.shiftKey) {
                    // Shift + drag = move position
                    positionX += deltaX * 0.005;
                    positionY -= deltaY * 0.005;
                } else {
                    // Normal drag = rotate
                    rotationY += deltaX * 0.01;
                    rotationX += deltaY * 0.01;
                }
                
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });
            
            renderer.domElement.addEventListener('mouseup', () => {
                isDragging = false;
            });
            
            renderer.domElement.addEventListener('mouseleave', () => {
                isDragging = false;
            });
            
            // Touch controls for mobile
            renderer.domElement.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    isDragging = true;
                    previousMousePosition = { 
                        x: e.touches[0].clientX, 
                        y: e.touches[0].clientY 
                    };
                }
            }, { passive: true });
            
            renderer.domElement.addEventListener('touchmove', (e) => {
                if (!isDragging || e.touches.length !== 1) return;
                e.preventDefault();
                
                const deltaX = e.touches[0].clientX - previousMousePosition.x;
                const deltaY = e.touches[0].clientY - previousMousePosition.y;
                
                // Touch always rotates (no shift key on mobile)
                rotationY += deltaX * 0.01;
                rotationX += deltaY * 0.01;
                
                previousMousePosition = { 
                    x: e.touches[0].clientX, 
                    y: e.touches[0].clientY 
                };
            }, { passive: false });
            
            renderer.domElement.addEventListener('touchend', () => {
                isDragging = false;
            }, { passive: true });
            
            // Add cursor style
            renderer.domElement.style.cursor = 'grab';
            renderer.domElement.addEventListener('mousedown', () => {
                renderer.domElement.style.cursor = 'grabbing';
            });
            renderer.domElement.addEventListener('mouseup', () => {
                renderer.domElement.style.cursor = 'grab';
            });

            const cacheBuster = Date.now();
            let loadProgress = { file: 0 };
            
            const updateProgress = () => {
                if (progressBar) progressBar.style.width = loadProgress.file + '%';
                if (progressText) progressText.textContent = `Loading 3D model... ${loadProgress.file}%`;
                const outer = progressBar ? progressBar.parentElement : null;
                if (outer && outer.getAttribute('role') === 'progressbar') {
                    outer.setAttribute('aria-valuenow', String(loadProgress.file));
                }
            };
            
            // ========== GLB LOADING ==========
            if (isGLB) {
                const glbUrl = selectedAvatar.urls.glb || selectedAvatar.urls.model_obj;
                const avatarId = selectedAvatar.id;
                
                // Check cache first for instant loading
                if (GLB_CACHE.has(avatarId)) {
                    console.log(`🚀 Preview cache HIT for avatar ${avatarId} - instant load`);
                    const cachedGltf = GLB_CACHE.get(avatarId);
                    const object = cachedGltf.scene.clone(); // Clone to avoid conflicts
                    
                    loadProgress.file = 100;
                    updateProgress();
                    
                    // Clear loading indicator and show 3D model
                    preview.innerHTML = '';
                    renderer.domElement.style.position = 'relative';
                    renderer.domElement.style.zIndex = '10';
                    preview.appendChild(renderer.domElement);
                    
                    // Center/scale for preview
                    const box = new THREE.Box3().setFromObject(object);
                    const size = box.getSize(new THREE.Vector3()).length();
                    const center = box.getCenter(new THREE.Vector3());
                    object.position.sub(center);
                    const targetSize = 2.2;
                    object.scale.setScalar(targetSize / size);
                    
                    // Fix materials to use SRGB
                    object.traverse((node) => {
                        if (node.isMesh) {
                            const mats = Array.isArray(node.material) ? node.material : [node.material];
                            mats.forEach(mat => {
                                if (mat.map) {
                                    mat.map.colorSpace = THREE.SRGBColorSpace;
                                    mat.map.needsUpdate = true;
                                }
                                mat.transparent = true;
                                mat.alphaTest = 0.1;
                            });
                        }
                    });
                    
                    scene.add(object);
                    return;
                }
                
                // Not in cache - load fresh (but cache the result)
                console.log(`📥 Preview cache MISS for avatar ${avatarId} - downloading GLB...`);
                const glbUrlWithCache = `${glbUrl}?v=${cacheBuster}`;
                
                const gltfLoader = new THREE.GLTFLoader();
                gltfLoader.load(
                    glbUrlWithCache,
                    (gltf) => {
                        // Cache management - remove oldest if cache is full
                        if (GLB_CACHE.size >= MAX_CACHE_SIZE) {
                            const oldestKey = GLB_CACHE.keys().next().value;
                            GLB_CACHE.delete(oldestKey);
                            console.log(`🗑️ Preview cache full - removed oldest model: ${oldestKey}`);
                        }
                        
                        // Cache the loaded model for future use
                        GLB_CACHE.set(avatarId, gltf);
                        console.log(`✅ Preview cached avatar ${avatarId} (${GLB_CACHE.size}/${MAX_CACHE_SIZE} models cached)`);
                        
                        const object = gltf.scene;
                        loadProgress.file = 100;
                        updateProgress();
                        
                        // Clear loading indicator and show 3D model
                        preview.innerHTML = '';
                        renderer.domElement.style.position = 'relative';
                        renderer.domElement.style.zIndex = '10';
                        preview.appendChild(renderer.domElement);
                        
                        // Center/scale for preview
                        const box = new THREE.Box3().setFromObject(object);
                        const size = box.getSize(new THREE.Vector3()).length();
                        const center = box.getCenter(new THREE.Vector3());
                        object.position.sub(center);
                        const targetSize = 2.2;
                        object.scale.setScalar(targetSize / size);
                        
                        // Fix materials to use SRGB
                        object.traverse((node) => {
                            if (node.isMesh) {
                                const mats = Array.isArray(node.material) ? node.material : [node.material];
                                mats.forEach(mat => {
                                    if (mat.map) {
                                        mat.map.colorSpace = THREE.SRGBColorSpace;
                                        mat.map.needsUpdate = true;
                                    }
                                    mat.transparent = true;
                                    mat.alphaTest = 0.1;
                                });
                            }
                        });
                        
                        scene.add(object);
                        
                        // Animation loop with mouse controls
                        const animate = () => {
                            requestAnimationFrame(animate);
                            controls.update(); // Required for damping and auto-rotation
                            renderer.render(scene, camera);
                        };
                        animate();
                    },
                    (xhr) => {
                        // GLB loading progress
                        if (xhr.lengthComputable) {
                            loadProgress.file = Math.round((xhr.loaded / xhr.total) * 100);
                            updateProgress();
                        }
                    },
                    (err) => {
                        console.warn('3D preview GLB load failed:', err);
                        showPreviewPlaceholder(preview);
                    }
                );
            }
            // Note: All avatars now use GLB format exclusively
            // Legacy OBJ/MTL loading code has been removed
        } catch (e) {
            console.warn('3D preview error:', e);
            showPreviewPlaceholder(preview);
        }
    } else {
        showPreviewPlaceholder(preview);
    }
}

function showPreviewPlaceholder(preview) {
    preview.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">${(selectedAvatar && selectedAvatar.emoji !== undefined) ? (selectedAvatar.emoji || '🐝') : '🐝'}</div>
            <p style="color: #8B6914; font-size: 1.2rem; font-weight: bold;">${(selectedAvatar && selectedAvatar.name !== undefined) ? (selectedAvatar.name || 'Bee Avatar') : 'Bee Avatar'}</p>
            <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">3D Preview</p>
        </div>
    `;
}

// Category filter
function filterByCategory(category) {
    if (category === 'all') {
        renderAvatarGrid(avatars);
    } else {
        const filtered = avatars.filter(a => a.category === category);
        renderAvatarGrid(filtered);
    }
}

// Show avatar description popup when clicking on avatar name
function showAvatarDescriptionPopup(avatar) {
    // Remove any existing popup
    const existingPopup = document.getElementById('avatarDescriptionPopup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    // Create popup overlay
    const popup = document.createElement('div');
    popup.id = 'avatarDescriptionPopup';
    popup.innerHTML = `
        <div class="avatar-popup-overlay">
            <div class="avatar-popup-content">
                <button class="avatar-popup-close" aria-label="Close">×</button>
                <div class="avatar-popup-header">
                    <img src="${avatar.thumbnail || `/static/assets/avatars/${avatar.id}/thumbnail.png`}" 
                         alt="${avatar.name}" 
                         class="avatar-popup-image">
                    <h3>${avatar.name}</h3>
                    <span class="avatar-popup-category">${avatar.category || 'Bee'}</span>
                </div>
                <div class="avatar-popup-body">
                    <p class="avatar-popup-description">${avatar.description || 'A wonderful bee companion for your spelling journey!'}</p>
                    <div class="avatar-popup-actions">
                        <button type="button" class="btn-select-this-avatar" data-avatar-id="${avatar.id}" aria-label="Select ${avatar.name} as your avatar">
                            Select This Avatar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Fade in animation
    setTimeout(() => {
        popup.querySelector('.avatar-popup-overlay').classList.add('show');
    }, 10);
    
    // Close button handler
    popup.querySelector('.avatar-popup-close').addEventListener('click', closeAvatarPopup);
    
    // Select avatar button handler
    popup.querySelector('.btn-select-this-avatar').addEventListener('click', () => {
        selectAvatar(avatar);
        closeAvatarPopup();
    });
    
    // Click outside to close
    popup.querySelector('.avatar-popup-overlay').addEventListener('click', (e) => {
        if (e.target.classList.contains('avatar-popup-overlay')) {
            closeAvatarPopup();
        }
    });
    
    // ESC key to close
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeAvatarPopup();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

function closeAvatarPopup() {
    const popup = document.getElementById('avatarDescriptionPopup');
    if (popup) {
        popup.querySelector('.avatar-popup-overlay').classList.remove('show');
        setTimeout(() => {
            popup.remove();
        }, 300);
    }
}

/**
 * Show a friendly message when a locked avatar is clicked
 * @param {Object} avatar - The locked avatar that was clicked
 */
function showLockedAvatarMessage(avatar) {
    // Create a temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        text-align: center;
        width: min(90%, 400px);
        animation: slideIn 0.3s ease;
    `;
    
    let unlockText = '';
    if (avatar.tier === 'premium') {
        unlockText = avatar.price_usd 
            ? `<strong>Purchase for $${avatar.price_usd}</strong>` 
            : '<strong>Premium Avatar - Purchase to unlock</strong>';
    } else if (avatar.unlock_requirement) {
        unlockText = `<strong>Earn ${avatar.unlock_requirement} 🍯 Honey Points</strong>`;
    } else {
        unlockText = '<strong>Complete quizzes to unlock</strong>';
    }
    
    notification.innerHTML = `
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
        <h3 style="margin: 0 0 1rem 0; color: #000;">${avatar.name}</h3>
        <p style="margin: 0 0 1.5rem 0; color: #333;">This avatar is locked!</p>
        <p style="margin: 0 0 1.5rem 0; font-size: 1.1rem;">${unlockText}</p>
        <button type="button" aria-label="Dismiss locked avatar notice" onclick="this.parentElement.remove()" style="
            padding: 0.75rem 2rem;
            background: #fff;
            border: 2px solid #FF8C00;
            border-radius: 0.5rem;
            color: #FF8C00;
            font-weight: 700;
            font-size: clamp(0.95rem, 2vw, 1rem);
            cursor: pointer;
            transition: all 0.3s ease;
        ">Got it!</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Update avatar count displays across the page
 * @param {number} total - Total number of avatars available
 * @param {number} unlocked - Number of avatars unlocked/owned
 * @param {number} locked - Number of avatars still locked
 */
function updateAvatarCountDisplays(total, unlocked, locked) {
    console.log(`📊 Updating avatar count displays: ${unlocked}/${total} unlocked`);
    
    // Update any avatar count badges on the page
    const countBadges = document.querySelectorAll('[data-avatar-count]');
    countBadges.forEach(badge => {
        const type = badge.getAttribute('data-avatar-count');
        if (type === 'total') {
            badge.textContent = total;
        } else if (type === 'unlocked') {
            badge.textContent = unlocked;
        } else if (type === 'locked') {
            badge.textContent = locked;
        }
    });
    
    // If parent window exists (opened from main menu), notify it to refresh avatar status
    if (window.opener && typeof window.opener.refreshAvatarSystemStatus === 'function') {
        try {
            window.opener.refreshAvatarSystemStatus();
            console.log('✅ Notified parent window to refresh avatar status');
        } catch (e) {
            console.warn('Could not notify parent window:', e);
        }
    }
    
    // If updateAvatarSystemStatus function exists in current window, call it
    if (typeof window.updateAvatarSystemStatus === 'function') {
        try {
            window.updateAvatarSystemStatus();
            console.log('✅ Updated avatar system status in current window');
        } catch (e) {
            console.warn('Could not update avatar system status:', e);
        }
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.updateAvatarCountDisplays = updateAvatarCountDisplays;
}
