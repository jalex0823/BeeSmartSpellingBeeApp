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
                    border-radius: 12px;
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
                    <div style="
                        width: 200px;
                        height: 4px;
                        background: rgba(255, 152, 0, 0.2);
                        border-radius: 2px;
                        margin: 1rem auto;
                        overflow: hidden;
                    ">
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
            }
            
            // Update test page avatar count if present
            const avatarCountSpan = document.getElementById('avatarCount');
            if (avatarCountSpan) {
                avatarCountSpan.textContent = avatars.length;
            }
            
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

        // Create 3D thumbnail container (render OBJ as thumbnail)
        const thumbContainer = document.createElement('div');
        thumbContainer.className = 'avatar-3d-thumbnail';
        thumbContainer.style.width = '100%';
        thumbContainer.style.height = '120px';
        thumbContainer.style.position = 'relative';
        thumbContainer.style.overflow = 'hidden';
        thumbContainer.style.borderRadius = '8px';
        thumbContainer.style.background = 'linear-gradient(135deg, #FFE8CC 0%, #FFD700 100%)';

        // Extract display name from PNG filename (remove ! and .png)
        // e.g., "AlBee!.png" → "AlBee"
        let displayName = avatar.name;
        if (avatar.urls?.thumbnail) {
            const pngFilename = avatar.urls.thumbnail.split('/').pop();
            displayName = pngFilename.replace('!.png', '').replace('.png', '');
        }

        // Create name div (appears below thumbnail)
        const nameDiv = document.createElement('div');
        nameDiv.className = 'avatar-name';
        nameDiv.dataset.avatarId = avatar.id;
        nameDiv.title = 'Click for details';
        nameDiv.textContent = displayName;

        card.appendChild(thumbContainer);
        card.appendChild(nameDiv);

        // Card click selects avatar (unless clicking the name)
        card.addEventListener('click', (e) => {
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

        // Use 2D PNG thumbnail (simple and fast)
        const thumbnailUrl = avatar.urls?.thumbnail || avatar.thumbnail || `/static/assets/avatars/${avatar.id}/thumbnail.png`;
        thumbContainer.innerHTML = `<img src="${thumbnailUrl}" 
                                        alt="${displayName}" 
                                        style="width:100%;height:100%;object-fit:contain;border-radius:8px;">`;
    });
    
    console.log(`✅ Rendered ${avatarsToRender.length} avatar cards with 2D thumbnails`);
}

// Render a 3D avatar model in a small, consistent-size thumbnail canvas
async function render3DThumbnail(container, avatar) {
    if (!avatar.urls || !avatar.urls.model_obj) {
        throw new Error('No 3D model URLs available');
    }

    // Create mini scene
    const scene = new THREE.Scene();
    scene.background = null; // Transparent
    
    const fov = 45;
    const camera = new THREE.PerspectiveCamera(fov, 1, 0.1, 1000);
    camera.position.set(0, 0, 3);
    
    const renderer = new THREE.WebGLRenderer({ 
        antialias: true, 
        alpha: true,
        preserveDrawingBuffer: true
    });
    const sizePx = 140; // enforce uniform thumbnail size
    renderer.setSize(sizePx, sizePx);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Load model
    const basePath = avatar.urls.model_obj.substring(0, avatar.urls.model_obj.lastIndexOf('/') + 1);
    const mtlFilename = avatar.urls.model_mtl.substring(avatar.urls.model_mtl.lastIndexOf('/') + 1);
    const objFilename = avatar.urls.model_obj.substring(avatar.urls.model_obj.lastIndexOf('/') + 1);

    return new Promise((resolve, reject) => {
        const mtlLoader = new THREE.MTLLoader();
        mtlLoader.setPath(basePath);
        if (mtlLoader.setResourcePath) mtlLoader.setResourcePath(basePath);

        mtlLoader.load(mtlFilename, (materials) => {
            materials.preload();

            // Apply texture settings
            Object.values(materials.materials).forEach(mat => {
                if (mat.map) {
                    mat.map.colorSpace = THREE.SRGBColorSpace;
                    mat.map.needsUpdate = true;
                }
                mat.transparent = true;
                mat.alphaTest = 0.1;
            });

            const objLoader = new THREE.OBJLoader();
            objLoader.setMaterials(materials);
            objLoader.setPath(basePath);
            
            objLoader.load(objFilename, (object) => {
                // Self-heal: apply texture to any mesh without map
                if (avatar.urls.texture) {
                    const textureLoader = new THREE.TextureLoader();
                    textureLoader.load(avatar.urls.texture, (texture) => {
                        texture.colorSpace = THREE.SRGBColorSpace;
                        object.traverse(node => {
                            if (node.isMesh) {
                                const mats = Array.isArray(node.material) ? node.material : [node.material];
                                mats.forEach(mat => {
                                    if (!mat.map) {
                                        mat.map = texture;
                                        mat.needsUpdate = true;
                                    }
                                });
                            }
                        });
                    });
                }

                // Center and scale uniformly so all thumbnails appear same visual size
                const box = new THREE.Box3().setFromObject(object);
                const sizeVec = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(sizeVec.x, sizeVec.y, sizeVec.z) || 1;
                const center = box.getCenter(new THREE.Vector3());
                object.position.sub(center);
                // Scale to target normalized dimension (fills ~80% of frame)
                const target = 1.6; // tune fill factor
                const scale = target / maxDim;
                object.scale.setScalar(scale);
                scene.add(object);

                // Animate
                let rotation = 0;
                const animate = () => {
                    rotation += 0.01;
                    object.rotation.y = rotation;
                    renderer.render(scene, camera);
                    requestAnimationFrame(animate);
                };
                animate();

                resolve();
            }, undefined, reject);
        }, undefined, reject);
    });
}

function selectAvatar(avatar) {
    selectedAvatar = avatar;
    
    // Update UI - remove selected from all, add to clicked
    document.querySelectorAll('.avatar-option').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.avatar-option[data-avatar-id="${avatar.id}"]`)?.classList.add('selected');
    
    // Defer 3D preview loading to not block UI
    requestIdleCallback(() => {
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
    
    // Detect if GLB or OBJ format
    const isGLB = selectedAvatar.urls?.model_obj && selectedAvatar.urls.model_obj.toLowerCase().endsWith('.glb');
    
    // Try to render a lightweight 3D preview if THREE loaders are available
    // Fallback to placeholder if not
    const loaderCheck = isGLB ? 
        (window.THREE && THREE.GLTFLoader) : 
        (window.THREE && THREE.MTLLoader && THREE.OBJLoader);
    
    if (loaderCheck && selectedAvatar.urls) {
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
            };
            
            // ========== GLB LOADING ==========
            if (isGLB) {
                const glbUrl = selectedAvatar.urls.model_obj;
                const glbUrlWithCache = `${glbUrl}?v=${cacheBuster}`;
                
                const gltfLoader = new THREE.GLTFLoader();
                gltfLoader.load(
                    glbUrlWithCache,
                    (gltf) => {
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
            // ========== OBJ LOADING ==========
            else {
                const mtlUrl = selectedAvatar.urls.model_mtl;
                const objUrl = selectedAvatar.urls.model_obj;
                const basePath = mtlUrl.substring(0, mtlUrl.lastIndexOf('/') + 1);
                const mtlFilename = mtlUrl.substring(mtlUrl.lastIndexOf('/') + 1);
                const objFilename = objUrl.substring(objUrl.lastIndexOf('/') + 1);
                
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
                        
                        // Ensure all materials use proper color space and texture settings
                        Object.values(materials.materials).forEach(mat => {
                            if (mat.map) {
                                mat.map.colorSpace = THREE.SRGBColorSpace;
                                mat.map.needsUpdate = true;
                            }
                            mat.transparent = true;
                            mat.depthWrite = true;
                            mat.alphaTest = 0.1;
                        mat.side = THREE.FrontSide;
                    });
                    
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
                    
                    // Self-healing: Load texture and force-apply to any mesh without a map
                    const textureUrl = selectedAvatar.urls.texture;
                    const textureLoader = new THREE.TextureLoader();
                    textureLoader.load(textureUrl, (texture) => {
                        texture.colorSpace = THREE.SRGBColorSpace;
                        texture.needsUpdate = true;
                        
                        // Traverse all meshes and ensure they have the texture
                        object.traverse((node) => {
                            if (node.isMesh) {
                                const materials = Array.isArray(node.material) ? node.material : [node.material];
                                materials.forEach(mat => {
                                    if (!mat.map) {
                                        // Mesh has no texture - apply it now (self-heal)
                                        console.log('Self-healing: Applying texture to mesh without map');
                                        mat.map = texture;
                                        mat.needsUpdate = true;
                                    } else if (mat.map && !mat.map.colorSpace) {
                                        // Mesh has texture but wrong color space
                                        mat.map.colorSpace = THREE.SRGBColorSpace;
                                        mat.map.needsUpdate = true;
                                    }
                                    mat.transparent = true;
                                    mat.alphaTest = 0.1;
                                });
                                node.castShadow = false;
                                node.receiveShadow = false;
                            }
                        });
                    }, undefined, (err) => {
                        console.warn('Texture load failed, continuing without self-heal:', err);
                    });
                    
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
                        controls.update(); // Required for damping and auto-rotation
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
            }
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
