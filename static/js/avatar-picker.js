/**
 * Avatar Picker JavaScript
 * Handles avatar selection, 3D preview, and saving
 */

let avatars = [];
let selectedAvatar = null;
let viewer3D = null;

// Load avatars on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAvatars();
    setupEventListeners();
});

async function loadAvatars() {
    try {
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
            renderAvatarGrid(avatars);
            // Verify asset naming consistency across OBJ/MTL/Texture
            verifyAvatarsConsistency(avatars);
        } else {
            console.error('❌ API returned error status');
        }
    } catch (error) {
        console.error('❌ Error loading avatars:', error);
        document.getElementById('avatarGrid').innerHTML = '<p style="padding: 2rem; text-align: center; color: #f56565;">Failed to load avatars. Please refresh the page.</p>';
    }
}

function renderAvatarGrid(avatarsToRender) {
    const grid = document.getElementById('avatarGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    console.log(`🎨 Rendering ${avatarsToRender.length} avatar cards...`);
    
    const bust = Date.now();
    avatarsToRender.forEach(avatar => {
        const card = document.createElement('div');
        card.className = 'avatar-option';
        card.dataset.avatarId = avatar.id;

        // Prefer catalog thumbnail; fallback to static path used in registration
        const thumbnailUrl = avatar.thumbnail || `/static/assets/avatars/${avatar.id}/thumbnail.png?t=${bust}`;
        console.log(`🖼️ Avatar ${avatar.id}: ${thumbnailUrl}`);

        card.innerHTML = `
            <img src="${thumbnailUrl}" alt="${avatar.name}" onerror="this.src='/static/assets/avatars/fallback.png'; console.error('Failed to load: ${thumbnailUrl}');">
            <div class="avatar-name" data-avatar-id="${avatar.id}" title="Click for details">${avatar.name}</div>
        `;

        // Card click selects avatar
        card.addEventListener('click', (e) => {
            // Don't select if clicking on the name (name opens popup instead)
            if (!e.target.classList.contains('avatar-name')) {
                selectAvatar(avatar);
            }
        });
        
        // Name click opens description popup
        const nameEl = card.querySelector('.avatar-name');
        nameEl.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card selection
            showAvatarDescriptionPopup(avatar);
        });
        
        grid.appendChild(card);
    });
    
    console.log(`✅ Rendered ${avatarsToRender.length} avatar cards to grid`);
}

function selectAvatar(avatar) {
    selectedAvatar = avatar;
    
    // Update UI - remove selected from all, add to clicked
    document.querySelectorAll('.avatar-option').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.avatar-option[data-avatar-id="${avatar.id}"]`)?.classList.add('selected');
    
    // Show preview
    updatePreview();
    
    // Enable select button
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
    
    // Try to render a lightweight 3D preview if THREE loaders are available
    // Fallback to placeholder if not
    if (window.THREE && THREE.MTLLoader && THREE.OBJLoader && selectedAvatar.urls) {
        try {
            // Show loading indicator
            preview.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🐝</div>
                    <div style="width: 80%; max-width: 200px; height: 8px; background: #FFE8CC; border-radius: 10px; margin: 1rem auto; overflow: hidden;">
                        <div id="preview3DProgress" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%); transition: width 0.3s ease;"></div>
                    </div>
                    <p id="preview3DText" style="color: #8B6914; font-weight: 600; margin-top: 0.5rem;">Loading 3D model... 0%</p>
                </div>
            `;
            
            const progressBar = document.getElementById('preview3DProgress');
            const progressText = document.getElementById('preview3DText');
            let loadProgress = { mtl: 0, obj: 0 };
            
            const updateProgress = () => {
                const totalProgress = Math.round((loadProgress.mtl + loadProgress.obj) / 2);
                if (progressBar) progressBar.style.width = totalProgress + '%';
                if (progressText) progressText.textContent = `Loading 3D model... ${totalProgress}%`;
            };
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, preview.clientWidth / preview.clientHeight, 0.1, 1000);
            camera.position.set(0, 0.5, 3.0);  // Moved up from 1.1 to 0.5
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(preview.clientWidth, preview.clientHeight);
            renderer.setClearColor(0x000000, 0);

            const ambient = new THREE.AmbientLight(0xffffff, 0.7); scene.add(ambient);
            const dir = new THREE.DirectionalLight(0xffffff, 0.7); dir.position.set(5,5,5); scene.add(dir);
            
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
            });
            
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
            });
            
            // Add cursor style
            renderer.domElement.style.cursor = 'grab';
            renderer.domElement.addEventListener('mousedown', () => {
                renderer.domElement.style.cursor = 'grabbing';
            });
            renderer.domElement.addEventListener('mouseup', () => {
                renderer.domElement.style.cursor = 'grab';
            });

            const mtlUrl = selectedAvatar.urls.model_mtl;
            const objUrl = selectedAvatar.urls.model_obj;
            const basePath = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);
            const mtlFilename = mtlUrl.substring(mtlUrl.lastIndexOf('/') + 1);
            const objFilename = objUrl.substring(objUrl.lastIndexOf('/') + 1);
            
            // Cache-busting: add timestamp to force reload of updated files
            const cacheBuster = Date.now();
            const mtlFilenameWithCache = `${mtlFilename}?v=${cacheBuster}`;
            const objFilenameWithCache = `${objFilename}?v=${cacheBuster}`;

            const mtlLoader = new THREE.MTLLoader();
            mtlLoader.setPath(basePath);
            if (mtlLoader.setTexturePath) mtlLoader.setTexturePath(basePath);
            if (mtlLoader.setResourcePath) mtlLoader.setResourcePath(basePath);

            mtlLoader.load(
                mtlFilenameWithCache,
                (materials) => {
                    materials.preload();
                    loadProgress.mtl = 100;
                    updateProgress();
                    
                    const objLoader = new THREE.OBJLoader();
                    objLoader.setMaterials(materials);
                    objLoader.setPath(basePath);
                    objLoader.load(
                        objFilenameWithCache,
                        (object) => {
                            loadProgress.obj = 100;
                            updateProgress();
                    
                    // Clear loading indicator and show 3D model
                    preview.innerHTML = '';
                    
                    // Set z-index on canvas to ensure it's above placeholder
                    renderer.domElement.style.position = 'relative';
                    renderer.domElement.style.zIndex = '10';
                    
                    preview.appendChild(renderer.domElement);
                    
                    // Center/scale for preview
                    object.traverse((c) => { if (c.isMesh) { c.castShadow = false; c.receiveShadow = false; }});
                    const box = new THREE.Box3().setFromObject(object);
                    const size = box.getSize(new THREE.Vector3()).length();
                    const center = box.getCenter(new THREE.Vector3());
                    object.position.sub(center);
                    const targetSize = 2.2;
                    object.scale.setScalar(targetSize / size);
                    scene.add(object);
                    
                    // Animation loop with mouse controls
                    const animate = () => { 
                        requestAnimationFrame(animate); 
                        
                        // Apply mouse-controlled rotation
                        object.rotation.x = rotationX;
                        object.rotation.y = rotationY;
                        
                        // Apply mouse-controlled position
                        object.position.x = positionX;
                        object.position.y = positionY;
                        
                        // Auto-rotate when not dragging
                        if (!isDragging) {
                            rotationY += 0.005;
                        }
                        
                        renderer.render(scene, camera); 
                    };
                    animate();
                }, (xhr) => {
                    // OBJ loading progress
                    if (xhr.lengthComputable) {
                        loadProgress.obj = Math.round((xhr.loaded / xhr.total) * 100);
                        updateProgress();
                    }
                }, (err) => {
                    console.warn('3D preview OBJ load failed:', err); showPreviewPlaceholder(preview);
                });
            }, (xhr) => {
                // MTL loading progress
                if (xhr.lengthComputable) {
                    loadProgress.mtl = Math.round((xhr.loaded / xhr.total) * 100);
                    updateProgress();
                }
            }, (err) => {
                console.warn('3D preview MTL load failed:', err); showPreviewPlaceholder(preview);
            });
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
            <div style="font-size: 4rem; margin-bottom: 1rem;">${selectedAvatar?.emoji || '🐝'}</div>
            <p style="color: #8B6914; font-size: 1.2rem; font-weight: bold;">${selectedAvatar?.name || 'Bee Avatar'}</p>
            <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">3D Preview</p>
        </div>
    `;
}

function setupEventListeners() {
    // Category filter
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const category = e.target.dataset.category;
            filterByCategory(category);
        });
    });
    
    // Search
    const searchInput = document.getElementById('avatarSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = avatars.filter(a => 
                a.name.toLowerCase().includes(query) ||
                (a.description && a.description.toLowerCase().includes(query))
            );
            renderAvatarGrid(filtered);
        });
    }
    
    // Select avatar button
    const selectBtn = document.getElementById('selectAvatarBtn');
    if (selectBtn) {
        selectBtn.addEventListener('click', () => {
            if (selectedAvatar) {
                saveAvatar(selectedAvatar.id, 'default');
            }
        });
    }
}

function filterByCategory(category) {
    if (category === 'all') {
        renderAvatarGrid(avatars);
    } else {
        const filtered = avatars.filter(a => a.category === category);
        renderAvatarGrid(filtered);
    }
}

async function saveAvatar(avatarId, variant) {
    // Show loading overlay
    const overlay = document.getElementById('avatarLoadingOverlay');
    const progressBar = document.getElementById('avatarLoadProgress');
    const loadingText = document.getElementById('avatarLoadingText');
    
    if (!overlay) {
        alert('Loading overlay not found');
        return;
    }
    
    overlay.style.display = 'flex';
    
    try {
        // Step 1: Preload 3D assets (20%)
        if (loadingText) loadingText.textContent = '🐝 Loading 3D model...';
        if (progressBar) progressBar.style.width = '20%';
        await preload3DAvatarAssets(avatarId, variant);
        
        // Step 2: Save to database (50%)
        if (loadingText) loadingText.textContent = '💾 Saving your choice...';
        if (progressBar) progressBar.style.width = '50%';
        
        const response = await fetch('/api/users/me/avatar', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                avatar_id: avatarId,
                variant: variant
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Step 3: Update UI cache (80%)
            if (loadingText) loadingText.textContent = '✨ Applying your new bee...';
            if (progressBar) progressBar.style.width = '80%';
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Step 4: Complete (100%)
            if (loadingText) loadingText.textContent = '🎉 All set!';
            if (progressBar) progressBar.style.width = '100%';
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Redirect based on context
            if (window.location.pathname.includes('register')) {
                // Continue registration flow
                window.location.href = '/student-dashboard';
            } else {
                // Reload to show new avatar (assets already cached)
                window.location.reload();
            }
        } else {
            overlay.style.display = 'none';
            alert(data.message || 'Failed to save avatar');
        }
    } catch (error) {
        console.error('Error saving avatar:', error);
        overlay.style.display = 'none';
        alert('Error saving avatar. Please try again.');
    }
}

async function preload3DAvatarAssets(avatarId, variant) {
    // Preload 3D model files so they're cached when page reloads
    return new Promise(async (resolve) => {
        try {
            // Find the avatar data
            const avatar = avatars.find(a => a.id === avatarId);
            if (!avatar) {
                resolve(); // No avatar found, skip preload
                return;
            }
            
            // Use canonical URLs from API if available to ensure consistency
            const modelUrl = avatar.urls?.model_obj || `/static/assets/avatars/${avatarId}/${capitalizeId(avatarId)}.obj`;
            const materialUrl = avatar.urls?.model_mtl || `/static/assets/avatars/${avatarId}/${capitalizeId(avatarId)}.mtl`;
            const textureUrl = avatar.urls?.texture || `/static/assets/avatars/${avatarId}/${capitalizeId(avatarId)}.png`;
            
            // Preload files using fetch to cache them
            const preloadPromises = [
                fetch(modelUrl).catch(e => console.warn('Model preload failed:', e)),
                fetch(materialUrl).catch(e => console.warn('Material preload failed:', e)),
                fetch(textureUrl).catch(e => console.warn('Texture preload failed:', e))
            ];
            
            // Wait for all preloads (or failures)
            await Promise.allSettled(preloadPromises);
            
            console.log(`✅ Preloaded 3D assets for ${avatarId}`);
            resolve();
        } catch (error) {
            console.warn('Asset preload error:', error);
            resolve(); // Don't block on preload errors
        }
    });
}

function capitalizeId(id) {
    // Convert kebab-case to PascalCase for filename fallback (e.g., seabea -> Seabea, astro-bee -> AstroBee)
    return id.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('');
}

function verifyAvatarsConsistency(list) {
    const getBase = (url, ext) => url ? url.substring(url.lastIndexOf('/') + 1).replace(new RegExp(`\.${ext}$`, 'i'), '') : '';
    list.forEach(a => {
        if (a.urls && a.urls.model_obj && a.urls.model_mtl && a.urls.texture) {
            const objBase = getBase(a.urls.model_obj, 'obj');
            const mtlBase = getBase(a.urls.model_mtl, 'mtl');
            const texBase = getBase(a.urls.texture, (a.urls.texture.match(/\.([a-zA-Z0-9]+)$/) || [,'png'])[1]);
            const same = objBase === mtlBase && (texBase === objBase || texBase === `${objBase}_texture`);
            if (same) {
                console.log(`🧩 Consistency PASS for ${a.id}: ${objBase}`);
            } else {
                console.warn(`🧩 Consistency FAIL for ${a.id}: OBJ=${objBase}, MTL=${mtlBase}, TEX=${texBase}`);
            }
        } else {
            console.warn(`ℹ️ Missing URL set for ${a.id}; skipping consistency check`);
        }
    });
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
                        <button class="btn-select-this-avatar" data-avatar-id="${avatar.id}">
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
