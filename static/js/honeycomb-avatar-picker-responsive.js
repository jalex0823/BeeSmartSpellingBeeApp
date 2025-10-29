/**
 * Responsive Honeycomb Avatar Picker
 * No absolute positioning - uses CSS Grid
 */

let avatarsData = [];
let selectedAvatar = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking Three.js availability...');
    console.log('THREE available:', typeof THREE !== 'undefined');
    console.log('GLTFLoader available:', typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined');
    console.log('OBJLoader available:', typeof THREE !== 'undefined' && typeof THREE.OBJLoader !== 'undefined');
    console.log('MTLLoader available:', typeof THREE !== 'undefined' && typeof THREE.MTLLoader !== 'undefined');
    
    loadAvatars();
    setupSearchFilter();
});

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
        
        avatarsData = data.avatars.map(avatar => ({
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
        
        console.log('Loaded avatars:', avatarsData.length);
        renderAvatarGrid();
    } catch (error) {
        console.error('Error loading avatars:', error);
        showError('Failed to load avatars. Please refresh the page.');
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
    thumbDiv.classList.remove('loading');
    
    if (avatar.thumbnail) {
        const img = document.createElement('img');
        img.src = avatar.thumbnail;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '50%';
        thumbDiv.appendChild(img);
    } else {
        // Fallback to emoji if no thumbnail
        console.warn(`No thumbnail for ${avatar.name}`);
        thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
    }
    
    return div;
}

// Load GLB 3D model
function load3DAvatarGLB(avatar, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const width = container.clientWidth || 120;
    const height = container.clientHeight || 120;
    
    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    // Load GLB model
    const loader = new THREE.GLTFLoader();
    const modelPath = avatar.obj_file_url; // Use full URL from API
    
    loader.load(
        modelPath,
        function(gltf) {
            const model = gltf.scene;
            
            // Center and scale model
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 2 / maxDim;
            
            model.position.sub(center);
            model.scale.set(scale, scale, scale);
            
            scene.add(model);
            container.classList.remove('loading');
            
            // Camera position
            camera.position.z = 3;
            
            // Animation loop
            function animate() {
                requestAnimationFrame(animate);
                model.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
        },
        undefined,
        function(error) {
            console.error('Error loading GLB:', error);
            container.classList.remove('loading');
            // Try loading thumbnail as fallback
            if (avatar.thumbnail) {
                container.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: cover;" alt="${avatar.name}">`;
            } else {
                container.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
            }
        }
    );
}

// Load OBJ 3D model
function load3DAvatarOBJ(avatar, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const width = container.clientWidth || 120;
    const height = container.clientHeight || 120;
    
    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);
    
    // Function to load OBJ (with or without materials)
    function loadOBJFile(materials = null) {
        const objLoader = new THREE.OBJLoader();
        if (materials) {
            objLoader.setMaterials(materials);
        }
        
        const objPath = avatar.obj_file_url; // Use full URL from API
        
        objLoader.load(
            objPath,
            function(object) {
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
                } else {
                    // Fix color space for materials with textures
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
                }
                
                // Center and scale
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 2 / maxDim;
                
                object.position.sub(center);
                object.scale.set(scale, scale, scale);
                
                scene.add(object);
                container.classList.remove('loading');
                
                camera.position.z = 3;
                
                function animate() {
                    requestAnimationFrame(animate);
                    object.rotation.y += 0.01;
                    renderer.render(scene, camera);
                }
                animate();
            },
            undefined,
            function(error) {
                console.error('Error loading OBJ:', error);
                container.classList.remove('loading');
                // Try loading thumbnail as fallback
                if (avatar.thumbnail) {
                    container.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: cover;" alt="${avatar.name}">`;
                } else {
                    container.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
                }
            }
        );
    }
    
    // Try to load MTL if available, otherwise load OBJ directly
    if (avatar.mtl_file_url) {
        const basePath = avatar.mtl_file_url.substring(0, avatar.mtl_file_url.lastIndexOf('/') + 1);
        const mtlFilename = avatar.mtl_file_url.substring(avatar.mtl_file_url.lastIndexOf('/') + 1);
        
        const mtlLoader = new THREE.MTLLoader();
        mtlLoader.setPath(basePath);
        if (mtlLoader.setResourcePath) mtlLoader.setResourcePath(basePath);
        
        mtlLoader.load(
            mtlFilename,
            function(materials) {
                materials.preload();
                
                // Ensure all materials use proper color space
                Object.values(materials.materials).forEach(mat => {
                    if (mat.map) {
                        mat.map.colorSpace = THREE.SRGBColorSpace;
                        mat.map.needsUpdate = true;
                    }
                    mat.transparent = true;
                    mat.alphaTest = 0.1;
                });
                
                loadOBJFile(materials);
            },
            undefined,
            function(error) {
                console.warn('MTL file not found, loading OBJ with default material:', error);
                loadOBJFile(null); // Load without materials
            }
        );
    } else {
        // No MTL file specified, load OBJ directly with default material
        console.log(`Loading OBJ without MTL for ${avatar.name}`);
        loadOBJFile(null);
    }
}

// Select avatar
function selectAvatar(avatar, element) {
    // Remove previous selection
    document.querySelectorAll('.avatar-hex-position.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Mark as selected
    element.classList.add('selected');
    selectedAvatar = avatar;
    
    // Update preview panel
    updatePreview(avatar);
}

// Update preview panel
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
    
    // Load 3D model in preview
    if (previewContainer) {
        // Clear previous preview
        previewContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: #FFD700;">Loading 3D preview...</div>';
        
        // Detect file type
        const isGLB = avatar.is_glb || (avatar.obj_file && avatar.obj_file.toLowerCase().endsWith('.glb'));
        
        // Create unique container ID for this preview
        const previewId = 'avatar-preview-3d';
        previewContainer.innerHTML = `<div id="${previewId}" style="width: 100%; height: 300px;"></div>`;
        
        // Load 3D model
        if (isGLB && avatar.obj_file_url) {
            load3DAvatarGLB(avatar, previewId);
        } else if (avatar.obj_file_url) {
            load3DAvatarOBJ(avatar, previewId);
        } else if (avatar.thumbnail) {
            // Fallback to large thumbnail
            previewContainer.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
        }
    }
}

// Choose avatar and redirect
function chooseAvatar() {
    if (!selectedAvatar) {
        alert('Please select an avatar first!');
        return;
    }
    
    // Save selection and redirect
    fetch('/api/avatar/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ avatar_slug: selectedAvatar.slug })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect || '/';
        } else {
            alert('Error selecting avatar: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to select avatar');
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
