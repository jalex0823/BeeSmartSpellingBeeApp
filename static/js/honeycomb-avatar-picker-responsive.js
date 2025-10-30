/**
 * Responsive Honeycomb Avatar Picker
 * No absolute positioning - uses CSS Grid
 * Enhanced with real-time 3D model loading progress
 */

let avatarsData = [];
let selectedAvatar = null;
let loadedThumbnails = 0;
let totalThumbnails = 0;
let currentLoadingAvatar = null;
let previewLoadProgress = 0;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🐝 BeeSmart Avatar Picker - Initializing...');
    console.log('THREE available:', typeof THREE !== 'undefined');
    console.log('GLTFLoader available:', typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined');
    console.log('DRACOLoader available:', typeof THREE !== 'undefined' && typeof THREE.DRACOLoader !== 'undefined');
    console.log('OBJLoader available:', typeof THREE !== 'undefined' && typeof THREE.OBJLoader !== 'undefined');
    console.log('MTLLoader available:', typeof THREE !== 'undefined' && typeof THREE.MTLLoader !== 'undefined');
    
    loadAvatars();
    setupSearchFilter();

    // Safety: hide loading overlay after 10s even if some thumbnails stall
    setTimeout(() => {
        const overlay = document.getElementById('avatar-loading-overlay');
        if (overlay && !overlay.classList.contains('hidden')) {
            console.warn('⚠️ Hiding loading overlay due to timeout safeguard');
            overlay.classList.add('hidden');
        }
    }, 10000);
});

// Update loading progress with detailed status
function updateLoadingProgress(customMessage = null) {
    const percentage = Math.round((loadedThumbnails / totalThumbnails) * 100);
    const progressBar = document.getElementById('loading-progress');
    const loadingText = document.getElementById('loading-text');
    const loadingContent = document.getElementById('loading-status');
    const loadingDetail = document.getElementById('loading-detail');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
    
    if (loadingText) {
        loadingText.textContent = percentage + '%';
    }
    
    // Update loading message
    if (loadingContent && customMessage) {
        loadingContent.textContent = customMessage;
    } else if (loadingContent) {
        if (percentage < 100) {
            loadingContent.textContent = `Loading Bee Thumbnails...`;
        } else {
            loadingContent.textContent = 'All Bees Ready! 🎉';
        }
    }
    
    // Update detail text
    if (loadingDetail) {
        if (percentage < 100) {
            loadingDetail.textContent = `${loadedThumbnails} of ${totalThumbnails} avatars loaded`;
        } else {
            loadingDetail.textContent = 'Ready to choose your bee!';
        }
    }
    
    console.log(`📊 Loading Progress: ${percentage}% (${loadedThumbnails}/${totalThumbnails})`);
    
    // Hide overlay when complete
    if (loadedThumbnails >= totalThumbnails && totalThumbnails > 0) {
        console.log('✅ All thumbnails loaded! Hiding overlay...');
        setTimeout(() => {
            const overlay = document.getElementById('avatar-loading-overlay');
            if (overlay) {
                overlay.style.transition = 'opacity 0.5s ease, visibility 0.5s ease';
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.classList.add('hidden');
                    overlay.style.display = 'none';
                    console.log('✅ Loading overlay hidden successfully!');
                }, 500);
            }
        }, 800); // Give users time to see "All Bees Ready!" message
    }
}

// Show preview loading indicator
function showPreviewLoading(avatarName) {
    const previewContainer = document.querySelector('.preview-avatar-container');
    if (!previewContainer) return;
    
    previewContainer.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #FFD700;">
            <div style="font-size: 3rem; animation: bounce 1s infinite;">🐝</div>
            <div style="margin-top: 1rem; font-size: 1.2rem;">Loading ${avatarName}...</div>
            <div style="width: 80%; height: 8px; background: rgba(255,215,0,0.2); border-radius: 4px; margin-top: 1rem; overflow: hidden;">
                <div id="preview-load-progress" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FFD700, #FFA500); transition: width 0.3s;"></div>
            </div>
            <div id="preview-load-text" style="margin-top: 0.5rem; font-size: 0.9rem;">0%</div>
        </div>
    `;
    
    // Add animation keyframes if not already present
    if (!document.getElementById('preview-animation-styles')) {
        const style = document.createElement('style');
        style.id = 'preview-animation-styles';
        style.textContent = `
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Update preview loading progress
function updatePreviewProgress(percentage, message = null) {
    const progressBar = document.getElementById('preview-load-progress');
    const progressText = document.getElementById('preview-load-text');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = message || `${Math.round(percentage)}%`;
    }
}

// Load avatars from API
async function loadAvatars() {
    try {
        const response = await fetch('/api/avatars');
        if (!response.ok) throw new Error('Failed to load avatars');
        
        const data = await response.json();
        
        // API returns {status: 'success', avatars: [...]}
        if (data.status !== 'success' || !data.avatars) {
            throw new Error('Invalid API response format');
        }
        
        const rawAvatars = data.avatars.map(avatar => ({
            slug: avatar.id,
            name: avatar.name,
            description: avatar.description,
            category: avatar.category,
            folder_path: avatar.folder,
            is_glb: avatar.is_glb || false,
            // Store full URLs from API
            obj_file_url: avatar.urls.model_obj,
            mtl_file_url: avatar.urls.model_mtl,
            // Also store filenames for detection
            obj_file: avatar.urls.model_obj ? avatar.urls.model_obj.split('/').pop() : null,
            mtl_file: avatar.urls.model_mtl ? avatar.urls.model_mtl.split('/').pop() : null,
            thumbnail: avatar.thumbnail
        }));

        // Dedupe by slug/name; prefer GLB entries over OBJ when duplicates exist
        const pickPreferGLB = (a, b) => {
            const aIsGlb = (a.folder_path || '').toLowerCase() === 'glb_files' || (a.obj_file_url || '').toLowerCase().endsWith('.glb') || !!a.is_glb;
            const bIsGlb = (b.folder_path || '').toLowerCase() === 'glb_files' || (b.obj_file_url || '').toLowerCase().endsWith('.glb') || !!b.is_glb;
            if (aIsGlb && !bIsGlb) return a;
            if (!aIsGlb && bIsGlb) return b;
            // If both same type, keep the one with a thumbnail
            if (a.thumbnail && !b.thumbnail) return a;
            if (!a.thumbnail && b.thumbnail) return b;
            // Default: keep first
            return a;
        };

    const bySlug = new Map();
        const byName = new Map();
        const duplicates = [];
        for (const avatar of rawAvatars) {
            const keySlug = (avatar.slug || '').toLowerCase();
            if (keySlug) {
                if (!bySlug.has(keySlug)) {
                    bySlug.set(keySlug, avatar);
                } else {
                    const chosen = pickPreferGLB(avatar, bySlug.get(keySlug));
                    if (chosen !== bySlug.get(keySlug)) {
                        duplicates.push(keySlug);
                        bySlug.set(keySlug, chosen);
                    }
                }
            } else {
                const keyName = (avatar.name || '').toLowerCase();
                if (!byName.has(keyName)) {
                    byName.set(keyName, avatar);
                } else {
                    const chosen = pickPreferGLB(avatar, byName.get(keyName));
                    if (chosen !== byName.get(keyName)) {
                        duplicates.push(keyName);
                        byName.set(keyName, chosen);
                    }
                }
            }
        }

        avatarsData = Array.from(bySlug.values());
        // Include name-only keyed entries that didn't have slugs
        for (const [nameKey, av] of byName.entries()) {
            if (!av.slug) avatarsData.push(av);
        }
        // Enforce kid-safe filter in frontend as well (defense-in-depth)
        const banned = new Set(['anxious-bee','monster-bee']);
        avatarsData = avatarsData.filter(av => !banned.has((av.slug||'').toLowerCase()));

        // Alphabetize by display name for a friendlier picker
        avatarsData.sort((a, b) => {
            const an = (a.name || '').toLowerCase();
            const bn = (b.name || '').toLowerCase();
            return an.localeCompare(bn);
        });
        if (duplicates.length) {
            console.log(`🧹 Removed ${duplicates.length} duplicate avatar entries (prefer GLB when available)`);
        }
        
        totalThumbnails = avatarsData.length;
        loadedThumbnails = 0;
        
    console.log('Loaded avatars:', avatarsData.length);
        renderAvatarGrid();
    } catch (error) {
        console.error('Error loading avatars:', error);
        showError('Failed to load avatars. Please refresh the page.');
        // Hide loading overlay on error
        const overlay = document.getElementById('avatar-loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
}

function showError(message) {
    const gridContainer = document.querySelector('.honeycomb-grid');
    if (gridContainer) {
        gridContainer.innerHTML = `<div style="color: #FFD700; text-align: center; padding: 2rem; grid-column: 1/-1;">${message}</div>`;
    }
}

// Render avatar grid with CSS Grid (no positions needed!)
function renderAvatarGrid() {
    const gridContainer = document.querySelector('.honeycomb-grid');
    if (!gridContainer) return;
    
    gridContainer.innerHTML = '';
    
    avatarsData.forEach((avatar, index) => {
        const avatarElement = createAvatarElement(avatar, index);
        gridContainer.appendChild(avatarElement);
    });
}

// Create individual avatar element
function createAvatarElement(avatar, index) {
    const div = document.createElement('div');
    div.className = 'avatar-hex-position';
    div.dataset.slug = avatar.slug;
    div.dataset.name = avatar.name;
    div.dataset.description = avatar.description || '';
    
    // Thumbnail container
    const thumbDiv = document.createElement('div');
    thumbDiv.className = 'avatar-hex-thumb loading';
    thumbDiv.id = `avatar-thumb-${index}`;
    
    // Checkmark for selection
    const checkmark = document.createElement('div');
    checkmark.className = 'avatar-hex-checkmark';
    checkmark.textContent = '✓';
    
    // Avatar name
    const nameDiv = document.createElement('div');
    nameDiv.className = 'avatar-hex-name';
    nameDiv.textContent = avatar.name;
    
    div.appendChild(checkmark);
    div.appendChild(thumbDiv);
    div.appendChild(nameDiv);
    
    // Click handler
    div.addEventListener('click', () => selectAvatar(avatar, div));
    
    // Use 2D thumbnail for fast loading (like original picker)
    // 3D model will load in preview panel when selected
    
    if (avatar.thumbnail) {
        const img = document.createElement('img');
        // Intelligent thumbnail loading with fallbacks for filename/casing/punctuation mismatches
        const fallbackCandidates = buildThumbnailFallbacks(avatar, avatar.thumbnail);
        let candidateIdx = 0;
        img.src = fallbackCandidates[candidateIdx];
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        // Remove border-radius, hexagon shape is handled by CSS clip-path
        
        // Track loading progress
        img.onload = () => {
            thumbDiv.classList.remove('loading');
            loadedThumbnails++;
            updateLoadingProgress();
        };
        
        img.onerror = () => {
            // Try next fallback if available
            candidateIdx++;
            if (candidateIdx < fallbackCandidates.length) {
                const next = fallbackCandidates[candidateIdx];
                console.warn(`Thumbnail failed for ${avatar.name}, retrying with fallback: ${next}`);
                img.src = next;
                return;
            }
            console.warn(`Failed to load any thumbnail variant for ${avatar.name}`);
            thumbDiv.classList.remove('loading');
            thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
            loadedThumbnails++;
            updateLoadingProgress();
        };
        
        thumbDiv.appendChild(img);
    } else {
        // Fallback to emoji if no thumbnail
        console.warn(`No thumbnail for ${avatar.name}`);
        thumbDiv.classList.remove('loading');
        thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
        loadedThumbnails++;
        updateLoadingProgress();
    }
    
    return div;
}

// Build a minimal, stable set of thumbnail candidates (server now provides robust URLs)
function buildThumbnailFallbacks(avatar, initialUrl) {
    const candidates = [];
    if (initialUrl) candidates.push(initialUrl);
    // Single generic fallback keeps logs clean and ensures we always show something
    candidates.push('/static/assets/avatars/glb_files/AvatarThumbnails/HoneyComb!.png');
    return candidates;
}

// Load GLB 3D model with progress tracking
function load3DAvatarGLB(avatar, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('❌ Container not found:', containerId);
        return;
    }
    
    const width = container.clientWidth || 250;
    const height = container.clientHeight || 250;
    
    console.log(`🔄 Loading GLB: ${avatar.name}, container: ${width}x${height}`);
    updatePreviewProgress(10, 'Initializing 3D viewer...');
    
    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    // Color management for r128
    if (typeof THREE.sRGBEncoding !== 'undefined') {
        renderer.outputEncoding = THREE.sRGBEncoding;
    }
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    updatePreviewProgress(20, 'Setting up lights...');
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    updatePreviewProgress(30, 'Loading 3D model...');
    
    // Load GLB model
    const loader = new THREE.GLTFLoader();
    // Attach DRACO loader if available (needed for compressed .glb)
    if (typeof THREE.DRACOLoader !== 'undefined') {
        try {
            const dracoLoader = new THREE.DRACOLoader();
            // Use Google's hosted decoders (works cross-origin)
            dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
            loader.setDRACOLoader(dracoLoader);
            console.log('✅ DRACO loader enabled for GLB decoding');
        } catch (e) {
            console.warn('⚠️ Failed to configure DRACOLoader:', e);
        }
    }
    const modelPath = avatar.obj_file_url; // Use full URL from API
    
    loader.load(
        modelPath,
        function(gltf) {
            console.log('✅ GLB loaded successfully:', avatar.name);
            updatePreviewProgress(70, 'Processing model...');
            
            const model = gltf.scene;
            
            // Center and scale model for full-body display
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 2.5 / maxDim; // Slightly larger scale to show full body
            
            model.position.sub(center);
            model.scale.set(scale, scale, scale);
            model.position.y = 0; // Center vertically
            
            updatePreviewProgress(85, 'Applying textures...');
            
            // Ensure textures use sRGB encoding when applicable
            model.traverse((node) => {
                if (node.isMesh) {
                    const mats = Array.isArray(node.material) ? node.material : [node.material];
                    mats.forEach(mat => {
                        if (mat && mat.map && typeof THREE.sRGBEncoding !== 'undefined') {
                            mat.map.encoding = THREE.sRGBEncoding;
                            if (mat.map.image) {
                                mat.map.needsUpdate = true;
                            }
                        }
                    });
                }
            });

            scene.add(model);
            container.classList.remove('loading');
            
            updatePreviewProgress(95, 'Starting animation...');
            
            // Camera position for full-body view
            camera.position.set(0, 0.5, 3.5); // Elevated view to see full avatar
            camera.lookAt(0, 0, 0);
            
            // Animation loop with auto-rotation
            function animate() {
                requestAnimationFrame(animate);
                model.rotation.y += 0.01; // Slow rotation to show all angles
                renderer.render(scene, camera);
            }
            animate();
            
            // Final update - completely remove loading indicator
            setTimeout(() => {
                updatePreviewProgress(100, 'Complete!');
                // Ensure ALL loading UI is removed once rendering is ready
                setTimeout(() => {
                    clearPreviewLoading(container, renderer.domElement);
                    console.log('✅ Loading indicator removed from preview');
                }, 500);
            }, 300);
        },
        function(xhr) {
            // Progress callback
            if (xhr.lengthComputable) {
                const percentComplete = (xhr.loaded / xhr.total) * 100;
                const adjustedPercent = 30 + (percentComplete * 0.4); // Map to 30-70% range
                updatePreviewProgress(adjustedPercent, `Downloading: ${Math.round(percentComplete)}%`);
                console.log(`📥 Download progress: ${Math.round(percentComplete)}%`);
            }
        },
        function(error) {
            console.error('❌ Error loading GLB:', error);
            container.classList.remove('loading');
            // If GLB fails and OBJ+MTL exist, try OBJ as fallback
            const url = (avatar.obj_file_url || '').toLowerCase();
            const hasObjFallback = url.endsWith('.obj') || (avatar.mtl_file_url && typeof THREE.OBJLoader !== 'undefined');
            if (hasObjFallback) {
                console.warn('⚠️ Falling back to OBJ loader for', avatar.name);
                updatePreviewProgress(0, 'Retrying with OBJ format...');
                setTimeout(() => load3DAvatarOBJ(avatar, containerId), 500);
                return;
            }
            // As last resort, thumbnail fallback
            if (avatar.thumbnail) {
                container.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
            } else {
                container.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
            }
        }
    );
}

// Load OBJ 3D model with progress tracking
function load3DAvatarOBJ(avatar, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('❌ Container not found:', containerId);
        return;
    }
    
    const width = container.clientWidth || 250;
    const height = container.clientHeight || 250;
    
    console.log(`🔄 Loading OBJ: ${avatar.name}, container: ${width}x${height}`);
    updatePreviewProgress(10, 'Initializing 3D viewer...');
    
    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    // Color management for r128
    if (typeof THREE.sRGBEncoding !== 'undefined') {
        renderer.outputEncoding = THREE.sRGBEncoding;
    }
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    updatePreviewProgress(20, 'Setting up lights...');
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    // Function to load OBJ (with or without materials)
    function loadOBJFile(materials = null) {
        updatePreviewProgress(40, materials ? 'Loading model with materials...' : 'Loading model...');
        
        const objLoader = new THREE.OBJLoader();
        if (materials) {
            objLoader.setMaterials(materials);
        }
        
        const objPath = avatar.obj_file_url; // Use full URL from API
        
        objLoader.load(
            objPath,
            function(object) {
                console.log('✅ OBJ loaded successfully:', avatar.name);
                updatePreviewProgress(70, 'Processing geometry...');
                
                // If no materials provided, apply a default golden material
                if (!materials) {
                    const defaultMaterial = new THREE.MeshPhongMaterial({ 
                        color: 0xFFD700,  // Golden color
                        shininess: 30,
                        flatShading: false
                    });
                    object.traverse(function(child) {
                        if (child instanceof THREE.Mesh) {
                            child.material = defaultMaterial;
                        }
                    });
                }
                
                updatePreviewProgress(80, 'Centering model...');
                
                // Center and scale for full-body display
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 2.5 / maxDim; // Slightly larger scale to show full body
                
                object.position.sub(center);
                object.scale.set(scale, scale, scale);
                object.position.y = 0; // Center vertically
                
                updatePreviewProgress(90, 'Applying materials...');
                
                // Post-load material/texture adjustments
                object.traverse((node) => {
                    if (node.isMesh) {
                        const mats = Array.isArray(node.material) ? node.material : [node.material];
                        mats.forEach(mat => {
                            if (mat) {
                                if (mat.map && typeof THREE.sRGBEncoding !== 'undefined') {
                                    mat.map.encoding = THREE.sRGBEncoding;
                                    if (mat.map.image) {
                                        mat.map.needsUpdate = true;
                                    }
                                }
                                mat.transparent = true;
                                mat.alphaTest = 0.1;
                            }
                        });
                    }
                });

                scene.add(object);
                container.classList.remove('loading');
                
                updatePreviewProgress(95, 'Starting animation...');
                
                // Camera position for full-body view
                camera.position.set(0, 0.5, 3.5); // Elevated view to see full avatar
                camera.lookAt(0, 0, 0);
                
                function animate() {
                    requestAnimationFrame(animate);
                    object.rotation.y += 0.01; // Slow rotation to show all angles
                    renderer.render(scene, camera);
                }
                animate();
                
                // Final update
                setTimeout(() => {
                    updatePreviewProgress(100, 'Complete!');
                    setTimeout(() => clearPreviewLoading(container, renderer.domElement), 300);
                }, 300);
            },
            function(xhr) {
                // Progress callback for OBJ file
                if (xhr.lengthComputable) {
                    const percentComplete = (xhr.loaded / xhr.total) * 100;
                    const adjustedPercent = 40 + (percentComplete * 0.3); // Map to 40-70% range
                    updatePreviewProgress(adjustedPercent, `Downloading: ${Math.round(percentComplete)}%`);
                    console.log(`📥 OBJ download progress: ${Math.round(percentComplete)}%`);
                }
            },
            function(error) {
                console.error('❌ Error loading OBJ:', error);
                container.classList.remove('loading');
                // Try loading thumbnail as fallback
                if (avatar.thumbnail) {
                    container.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
                } else {
                    container.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
                }
            }
        );
    }
    
    // Try to load MTL if available, otherwise load OBJ directly
    if (avatar.mtl_file_url) {
        updatePreviewProgress(30, 'Loading materials...');
        
        const basePath = avatar.mtl_file_url.substring(0, avatar.mtl_file_url.lastIndexOf('/') + 1);
        const mtlFilename = avatar.mtl_file_url.substring(avatar.mtl_file_url.lastIndexOf('/') + 1);
        
        const mtlLoader = new THREE.MTLLoader();
        mtlLoader.setPath(basePath);
        if (mtlLoader.setResourcePath) mtlLoader.setResourcePath(basePath);
        
        mtlLoader.load(
            mtlFilename,
            function(materials) {
                console.log('✅ MTL materials loaded for', avatar.name);
                materials.preload();
                
                // Ensure all materials use proper color space
                Object.values(materials.materials).forEach(mat => {
                    // Defer texture updates to after OBJ load to avoid undefined image warnings
                    mat.transparent = true;
                    mat.alphaTest = 0.1;
                });
                
                loadOBJFile(materials);
            },
            undefined,
            function(error) {
                console.warn('⚠️ MTL file not found, loading OBJ with default material:', error);
                loadOBJFile(null); // Load without materials
            }
        );
    } else {
        // No MTL file specified, load OBJ directly with default material
        console.log(`Loading OBJ without MTL for ${avatar.name}`);
        loadOBJFile(null);
    }
}

// Remove any loading UI from the preview container, keeping the WebGL canvas intact
function clearPreviewLoading(container, canvasEl) {
    if (!container) return;
    Array.from(container.children).forEach(child => {
        // Keep the actual renderer canvas; remove everything else that looks like loading UI
        if (canvasEl && child === canvasEl) return;
        const text = (child.textContent || '').toLowerCase();
        const isLoading = text.includes('loading') || /\d+%/.test(text);
        const styleStr = (child.getAttribute && child.getAttribute('style')) || '';
        const looksLikeLoader = styleStr.includes('flex') || styleStr.includes('column');
        if (isLoading || looksLikeLoader) {
            child.remove();
        }
    });
}

// Select avatar with theme activation
function selectAvatar(avatar, element) {
    console.log(`🎯 Avatar selected: ${avatar.name} (${avatar.slug})`);
    
    // Remove previous selection and theme classes
    document.querySelectorAll('.avatar-hex-position.selected, .avatar-hex-position.theme-active').forEach(el => {
        el.classList.remove('selected', 'theme-active');
        el.style.boxShadow = '';
        el.style.borderColor = '';
        el.style.animation = '';
    });
    
    // Mark as selected
    element.classList.add('selected', 'theme-active');
    selectedAvatar = avatar;
    
    // Activate avatar theme
    if (window.avatarThemeManager) {
        try {
            const theme = window.avatarThemeManager.activateTheme(avatar.slug, element);
            console.log(`🎨 Theme activated for ${avatar.name}:`, theme);
            
            // Show personality message
            const personalityMsg = window.avatarThemeManager.getPersonalityMessage(avatar.slug, 'greeting');
            console.log(`💬 ${avatar.name} says: "${personalityMsg}"`);
            
            // Optionally update description with personality message
            const descEl = document.querySelector('.preview-description');
            if (descEl && avatar.description) {
                descEl.textContent = avatar.description + ' - ' + personalityMsg;
            }
        } catch (error) {
            console.warn('⚠️ Theme activation failed:', error);
        }
    } else {
        console.warn('⚠️ Avatar Theme Manager not loaded');
    }
    
    // Update preview panel
    updatePreview(avatar);
}

// Update preview panel with loading progress
function updatePreview(avatar) {
    const previewContent = document.querySelector('.preview-content');
    if (!previewContent) return;
    
    const nameEl = previewContent.querySelector('.preview-name');
    const descEl = previewContent.querySelector('.preview-description');
    const btnEl = previewContent.querySelector('.preview-choose-btn');
    const previewContainer = previewContent.querySelector('.preview-avatar-container');
    
    if (nameEl) nameEl.textContent = avatar.name;
    if (descEl) descEl.textContent = avatar.description || 'Choose this amazing bee!';
    if (btnEl) btnEl.style.display = 'block';
    
    console.log(`🎨 Previewing avatar: ${avatar.name}`);
    currentLoadingAvatar = avatar.name;
    
    // Load 3D model in preview with loading indicator
    if (previewContainer) {
        // Show loading indicator first
        showPreviewLoading(avatar.name);

        // Detect file type based on folder_path and URL
        // GLB avatars are in 'glb_files' folder, OBJ avatars have individual folders
        const modelUrl = (avatar.obj_file_url || '').toLowerCase();
        const folderPath = (avatar.folder_path || '').toLowerCase();
        const isGLB = folderPath === 'glb_files' || modelUrl.endsWith('.glb') || !!avatar.is_glb;

        console.log(`🔍 Avatar format detection for ${avatar.name}: folder=${folderPath}, url=${modelUrl}, isGLB=${isGLB}`);

        // Create container that fills the preview area
        const previewId = 'avatar-preview-3d';
        
        const loadPreview = () => {
            const innerContainer = document.getElementById(previewId);
            if (!innerContainer) {
                // Re-insert the container if the loading screen replaced it
                const loadingScreen = previewContainer.querySelector('[style*="flex-direction: column"]');
                if (loadingScreen) {
                    const newContainer = document.createElement('div');
                    newContainer.id = previewId;
                    newContainer.style.cssText = 'width: 100%; height: 100%; position: absolute; top: 0; left: 0;';
                    previewContainer.appendChild(newContainer);
                }
            }

            const container = document.getElementById(previewId);
            if (!container) return;

            const w = container.clientWidth || previewContainer.clientWidth;
            const h = container.clientHeight || previewContainer.clientHeight;
            
            // If the container hasn't laid out yet, try on next frame
            if (!w || !h) {
                requestAnimationFrame(loadPreview);
                return;
            }

            // If Three.js or loaders are missing, show image fallback
            if (typeof THREE === 'undefined') {
                console.warn('⚠️ Three.js not available; using thumbnail fallback');
                if (avatar.thumbnail) {
                    previewContainer.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
                }
                return;
            }

            // Load 3D model (prefer GLB)
            if (isGLB && avatar.obj_file_url && typeof THREE.GLTFLoader !== 'undefined') {
                console.log('📦 Loading GLB model:', avatar.name);
                load3DAvatarGLB(avatar, previewId);
            } else if (avatar.obj_file_url && typeof THREE.OBJLoader !== 'undefined') {
                console.log('📦 Loading OBJ model:', avatar.name);
                load3DAvatarOBJ(avatar, previewId);
            } else if (avatar.thumbnail) {
                // Fallback to large thumbnail
                console.log('🖼️ Using thumbnail fallback for:', avatar.name);
                previewContainer.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
            }
        };

        // Start loading after a brief delay to show the loading screen
        setTimeout(loadPreview, 100);
    }
}

// Choose avatar and save selection
function chooseAvatar() {
    if (!selectedAvatar) {
        alert('Please select an avatar first!');
        return;
    }
    
    console.log(`🎯 User chose avatar: ${selectedAvatar.name} (${selectedAvatar.slug})`);
    
    // Disable button during save
    const btn = document.querySelector('.preview-choose-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Saving...';
    }
    
    // Save selection via API
    fetch('/api/avatar/select', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({ avatar_slug: selectedAvatar.slug })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || `HTTP ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Avatar selection saved:', data);
        
        if (data.success) {
            // Show success message
            if (btn) {
                btn.textContent = '✓ Saved!';
                btn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
            }
            
            // Update user-avatar-loader if available (force refresh)
            if (window.userAvatarLoader) {
                console.log('🔄 Refreshing user avatar loader...');
                window.userAvatarLoader.init().then(() => {
                    console.log('✅ User avatar loader refreshed');
                });
            }
            
            // Redirect after brief delay to show success
            setTimeout(() => {
                const redirectUrl = data.redirect || '/';
                console.log(`🔀 Redirecting to: ${redirectUrl}`);
                window.location.href = redirectUrl;
            }, 1000);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('❌ Error selecting avatar:', error);
        alert('Failed to save avatar selection: ' + error.message);
        
        // Reset button
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Choose This Bee';
            btn.style.background = '';
        }
    });
}

// Search/filter functionality
function setupSearchFilter() {
    const searchInput = document.querySelector('.honeycomb-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        filterAvatars(query);
    });
}

function filterAvatars(query) {
    const avatarElements = document.querySelectorAll('.avatar-hex-position');
    
    avatarElements.forEach(el => {
        const name = el.dataset.name.toLowerCase();
        const matches = name.includes(query);
        
        if (matches) {
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    });
}
