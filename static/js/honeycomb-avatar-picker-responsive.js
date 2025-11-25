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
// Current user's honey points from API
let currentUserHoneyPoints = 0;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🐝 BeeSmart Avatar Picker - Initializing...');
    console.log('THREE available:', typeof THREE !== 'undefined');
    console.log('GLTFLoader available:', typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined');
    console.log('DRACOLoader available:', typeof THREE !== 'undefined' && typeof THREE.DRACOLoader !== 'undefined');
    
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
// Update dynamic marquee with unlock status
function updateDynamicMarquee(avatars) {
    const marquee = document.getElementById('dynamic-marquee');
    if (!marquee) return;
    
    const locked = avatars.filter(a => a.is_locked);
    const unlocked = avatars.filter(a => !a.is_locked);
    
    let messages = [];
    // Honey Points hint
    if (typeof currentUserHoneyPoints === 'number') {
        messages.push(`🍯 You have ${Number(currentUserHoneyPoints).toLocaleString()} Honey Points`);
    }
    
    // Congratulate on unlocked count
    messages.push(`🎉 You have ${unlocked.length} bees unlocked!`);
    
    if (locked.length > 0) {
        messages.push(`🔒 ${locked.length} more bees available to unlock`);
        
        // Find next unlock tier
        const nextUnlocks = locked
            .filter(a => a.unlock_message && a.unlock_message.includes('Honey Points'))
            .sort((a, b) => {
                const aPoints = parseInt(a.unlock_message.match(/\d+/)?.[0] || '999999');
                const bPoints = parseInt(b.unlock_message.match(/\d+/)?.[0] || '999999');
                return aPoints - bPoints;
            });
        
        if (nextUnlocks.length > 0) {
            const next = nextUnlocks[0];
            messages.push(`⭐ Next unlock: ${next.name} - ${next.unlock_message}`);
        }
        
        // Count premium avatars
        const premiumCount = locked.filter(a => 
            a.unlock_message && a.unlock_message.includes('Purchase')
        ).length;
        
        if (premiumCount > 0) {
            messages.push(`💎 ${premiumCount} premium bees available for purchase`);
        }
    } else {
        messages.push(`👑 Congratulations! You've unlocked the entire hive!`);
    }
    
    // Create marquee HTML
    const marqueeHTML = messages.map(msg => 
        `<span class="banner-message" style="display: inline-block; padding: 0 3rem;">${msg}</span>`
    ).join('');
    
    marquee.innerHTML = marqueeHTML;
}

// Compute a consistent locked message based on user points and avatar tier
function computeLockedMessage(avatar) {
    const tier = avatar.tier;
    const price = (typeof avatar.price === 'number') ? avatar.price : null;
    const hasPointsTier = (typeof avatar.unlock_points === 'number' && avatar.unlock_points > 0);
    const isPremiumOnly = (tier === 'premium') || (price && !hasPointsTier);

    if (hasPointsTier && !isPremiumOnly) {
        const remaining = Math.max(avatar.unlock_points - (currentUserHoneyPoints || 0), 0);
        if (remaining > 0) {
            let msg = `You need ${remaining.toLocaleString()} more Honey Points to unlock this bee.`;
            if (price && tier === 'earn_or_buy') {
                msg += ` Or purchase for $${Number(price).toFixed(2)}.`;
            }
            return msg;
        }
        return 'You have enough Honey Points to unlock this bee! Try selecting again.';
    } else if (isPremiumOnly && price) {
        return `Purchase for $${Number(price).toFixed(2)}.`;
    }
    return avatar.unlock_message || 'Complete more quizzes to unlock this bee!';
}

// Load avatars from API
async function loadAvatars() {
    try {
        const response = await fetch('/api/avatars', { credentials: 'same-origin' });
        if (!response.ok) {
            let bodySnippet = '';
            try {
                bodySnippet = (await response.text()).slice(0, 500);
            } catch (_) { /* ignore */ }
            console.error('🐞 Avatar API non-OK response', {
                status: response.status,
                contentType: response.headers.get('content-type') || '',
                preview: bodySnippet
            });
            throw new Error(`Failed to load avatars (HTTP ${response.status})`);
        }
        
        const data = await response.json();
        // Capture current user's honey points if provided
        if (data && typeof data.user_honey_points === 'number') {
            currentUserHoneyPoints = data.user_honey_points;
            console.log('🍯 Current user honey points:', currentUserHoneyPoints);
        }
        
        // API returns {status: 'success', avatars: [...]} in current app
        // Be tolerant to older shapes like an array directly
        let apiAvatars = null;
        if (Array.isArray(data)) {
            apiAvatars = data;
        } else if (data && Array.isArray(data.avatars)) {
            apiAvatars = data.avatars;
        } else if (data && data.status === 'success' && data.data && Array.isArray(data.data)) {
            apiAvatars = data.data;
        }
        if (!apiAvatars) {
            console.error('🐞 Unexpected avatar API payload shape', data);
            throw new Error('Invalid API response format');
        }
        
        const rawAvatars = apiAvatars.map(avatar => {
            // Extract GLB URL from standard urls.glb field (all avatars are now GLB-only)
            const glbUrl = avatar.urls?.glb;
            const isGlbFormat = true; // All avatars are GLB format
            
            return {
                slug: avatar.id,
                name: avatar.name,
                description: avatar.description,
                category: avatar.category,
                folder_path: avatar.folder,
                is_glb: isGlbFormat,
                // Store full URL from API - GLB-only (all avatars are GLB now)
                glb_url: glbUrl,
                thumbnail: avatar.thumbnail || (avatar.urls ? avatar.urls.thumbnail : avatar.thumbnail_url),
                // NEW: Lock status from monetization system
                is_locked: avatar.is_locked || false,
                unlock_message: avatar.unlock_message || '',
                // NEW: Numeric unlock info for computing remaining points
                unlock_points: typeof avatar.unlock_points === 'number' ? avatar.unlock_points : null,
                tier: avatar.tier || null,
                price: typeof avatar.price === 'number' ? avatar.price : null,
            };
        });

        // Helper: normalize string to a canonical key
        const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

        // Helper: derive a stable "base" key for an avatar regardless of tiny naming variations
        const baseKeyFor = (av) => {
            // Prefer explicit slug when present
            const slugKey = norm(av.slug);
            if (slugKey) return slugKey;
            // Use thumbnail base name for fallback
            const thumbName = (av.thumbnail || '').split('/').pop().replace(/\.[^.]+$/,'').replace(/!+$/,'');
            if (thumbName) return norm(thumbName);
            // Finally, the display name
            return norm(av.name);
        };

        // Helper: normalize thumbnail to detect duplicates that point to the same image
        const normThumb = (url) => {
            const file = (url || '').split('/').pop();
            return (file || '').toLowerCase().replace(/!+/g,'');
        };

        // Dedupe; all avatars are GLB format now (no OBJ fallback needed)
        const pickPreferGLB = (a, b) => {
            // If both same type, keep the one with a thumbnail
            if (a.thumbnail && !b.thumbnail) return a;
            if (!a.thumbnail && b.thumbnail) return b;
            // Default: keep first
            return a;
        };
        // First pass: group by a canonical base key to collapse visually duplicate avatars
        const byBase = new Map();
        const duplicates = [];
        for (const avatar of rawAvatars) {
            const key = baseKeyFor(avatar);
            if (!byBase.has(key)) {
                byBase.set(key, avatar);
            } else {
                const chosen = pickPreferGLB(avatar, byBase.get(key));
                if (chosen !== byBase.get(key)) {
                    duplicates.push(key);
                    byBase.set(key, chosen);
                }
            }
        }

        // Second pass: avoid keeping multiple entries pointing at the same thumbnail file,
        // but NEVER collapse distinct avatars that use our generic fallback thumbnail
        const seenThumb = new Set();
        avatarsData = [];
        for (const av of byBase.values()) {
            const t = normThumb(av.thumbnail);
            // Treat these as generic fallback thumbnails; don't dedupe on them
            const isGenericThumb = t === 'honeycomb!.png' || t === 'honeycomb.png';
            if (t && !isGenericThumb && seenThumb.has(t)) continue;
            if (t && !isGenericThumb) seenThumb.add(t);
            avatarsData.push(av);
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
        if (duplicates.length) console.log(`🧹 Collapsed ${duplicates.length} duplicate variants (base/name/slug)`);
        
        totalThumbnails = avatarsData.length;
        loadedThumbnails = 0;
        
    console.log('Loaded avatars:', avatarsData.length);
    updateDynamicMarquee(avatarsData);
    renderAvatarGrid();
    // Show a celebratory modal if new avatars have become unlocked since last visit
    maybeShowNewlyUnlockedModal(avatarsData);
    } catch (error) {
        console.error('Error loading avatars:', error);
        const msg = (error && error.message) ? error.message : 'Failed to load avatars. Please refresh the page.';
        showError(msg);
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

// Detect newly unlocked avatars and show unlock modal (uses avatar-unlock-notification.js)
function maybeShowNewlyUnlockedModal(avatars) {
    try {
        if (!Array.isArray(avatars) || avatars.length === 0) return;
        const storageKey = 'bee_unlocked_slugs_v1';
        const prev = JSON.parse(localStorage.getItem(storageKey) || '[]');
        const currentUnlocked = avatars.filter(a => !a.is_locked).map(a => (a.slug || '').toLowerCase());
        const prevSet = new Set((prev || []).map(s => String(s).toLowerCase()));
        const newly = currentUnlocked.filter(s => !prevSet.has(s));
        // Update storage immediately to avoid repeated modals
        localStorage.setItem(storageKey, JSON.stringify(currentUnlocked));
        if (newly.length === 0) return;
        // Build avatar objects for the modal (first few only to reduce noise)
        const bySlug = new Map();
        avatars.forEach(a => bySlug.set((a.slug||'').toLowerCase(), a));
        const unlockedObjs = newly.slice(0, 3).map(slug => {
            const a = bySlug.get(slug);
            return {
                name: a?.name || slug,
                slug: a?.slug || slug,
                description: a?.description || '',
                thumbnail: a?.thumbnail || ''
            };
        });
        if (window.showAvatarUnlockNotification) {
            // Slight delay to ensure grid is visible before overlay
            setTimeout(() => window.showAvatarUnlockNotification(unlockedObjs), 600);
        } else {
            console.log('🎉 Newly unlocked avatars:', unlockedObjs.map(x => x.name));
        }
    } catch (err) {
        console.warn('Failed to show newly unlocked avatar modal:', err);
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
    div.dataset.locked = avatar.is_locked ? 'true' : 'false';
    div.dataset.unlockMessage = avatar.unlock_message || '';
    
    // Add locked class if avatar is locked
    if (avatar.is_locked) {
        div.classList.add('avatar-locked');
    }
    
    // Thumbnail container
    const thumbDiv = document.createElement('div');
    thumbDiv.className = 'avatar-hex-thumb loading';
    thumbDiv.id = `avatar-thumb-${index}`;
    
    // Checkmark for selection
    const checkmark = document.createElement('div');
    checkmark.className = 'avatar-hex-checkmark';
    checkmark.textContent = '✓';
    
    // Lock icon for locked avatars
    if (avatar.is_locked) {
        const lockIcon = document.createElement('div');
        lockIcon.className = 'avatar-lock-icon';
        lockIcon.innerHTML = '🔒';
        lockIcon.title = computeLockedMessage(avatar);
        thumbDiv.appendChild(lockIcon);
    }
    
    // Avatar name
    const nameDiv = document.createElement('div');
    nameDiv.className = 'avatar-hex-name';
    nameDiv.textContent = avatar.name;
    
    div.appendChild(checkmark);
    div.appendChild(thumbDiv);
    div.appendChild(nameDiv);
    
    // Unlock tooltip
    if (avatar.is_locked) {
        const tooltip = document.createElement('div');
        tooltip.className = 'avatar-unlock-tooltip';
        tooltip.textContent = computeLockedMessage(avatar);
        div.appendChild(tooltip);
    }
    
    // Click handler - disabled for locked avatars
    if (avatar.is_locked) {
        div.addEventListener('click', (e) => {
            e.preventDefault();
            showLockedMessage(avatar);
        });
    } else {
        div.addEventListener('click', () => selectAvatar(avatar, div));
    }
    
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
    // STRICT mode: do not use generic fallbacks to avoid misrepresentation
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
    const modelPath = avatar.glb_url; // Use full GLB URL from API
    
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
                model.rotation.y += 0.003; // Slow rotation to show all angles
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
            const url = (avatar.glb_url || '').toLowerCase();
            // All avatars are now GLB-only, no OBJ fallback needed
            // Show thumbnail as fallback
            if (avatar.thumbnail) {
                container.innerHTML = `<img src="${avatar.thumbnail}" style="width: 100%; height: 100%; object-fit: contain;" alt="${avatar.name}">`;
            } else {
                container.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
            }
        }
    );
}

// All avatars are now GLB-only. OBJ/MTL loading removed.

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
    
    // Add or update unlock message for locked avatars
    let unlockMsgEl = previewContent.querySelector('.preview-unlock-message');
    if (avatar.is_locked) {
        const message = computeLockedMessage(avatar);
        if (!unlockMsgEl) {
            unlockMsgEl = document.createElement('div');
            unlockMsgEl.className = 'preview-unlock-message';
            // Insert after description
            if (descEl && descEl.nextSibling) {
                descEl.parentNode.insertBefore(unlockMsgEl, descEl.nextSibling);
            } else if (descEl) {
                descEl.parentNode.appendChild(unlockMsgEl);
            }
        }
        unlockMsgEl.textContent = message;
        unlockMsgEl.style.display = 'block';
        
        // Hide choose button for locked avatars
        if (btnEl) btnEl.style.display = 'none';
    } else {
        // Remove unlock message for unlocked avatars
        if (unlockMsgEl) {
            unlockMsgEl.style.display = 'none';
        }
        // Show choose button for unlocked avatars
        if (btnEl) btnEl.style.display = 'block';
    }

    console.log(`🎨 Previewing avatar: ${avatar.name}`);
    currentLoadingAvatar = avatar.name;    // Load 3D model in preview with loading indicator
    if (previewContainer) {
        // Show loading indicator first
        showPreviewLoading(avatar.name);

        // All avatars are now GLB-only format - no detection needed
        const modelUrl = (avatar.glb_url || '').toLowerCase();
        const folderPath = (avatar.folder_path || '').toLowerCase();
        const isGLB = true; // All avatars are GLB

        console.log(`🔍 Loading GLB model for ${avatar.name}: url=${modelUrl}`);

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

            // Load 3D model (GLB-only, all avatars are GLB format)
            if (avatar.glb_url && typeof THREE.GLTFLoader !== 'undefined') {
                console.log('📦 Loading GLB model:', avatar.name);
                load3DAvatarGLB(avatar, previewId);
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
    
    // Save selection via API (authentication required)
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
            // If not authenticated, redirect to login/registration
            if (response.status === 401 || response.status === 403) {
                const next = encodeURIComponent(window.location.pathname);
                window.location.href = `/auth/login?next=${next}`;
                return Promise.reject(new Error('Authentication required'));
            }
            return response.json().then(err => Promise.reject(new Error(err.error || `HTTP ${response.status}`)));
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
        // If we got here without redirecting, show a friendly message and reset button
        alert('Please log in or register to change your avatar.');
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

// Show locked avatar message
function showLockedMessage(avatar) {
    // Use the unified computation for consistency across UI
    const message = computeLockedMessage(avatar);
    const modal = document.createElement('div');
    modal.className = 'locked-avatar-modal';
    modal.innerHTML = `
        <div class="locked-modal-content">
            <button class="locked-modal-close" onclick="this.parentElement.parentElement.remove()">×</button>
            <div class="locked-modal-icon">🔒</div>
            <h2>${avatar.name} is Locked</h2>
            <p>${message}</p>
            <p style="margin-top: 1rem; color: #FFB300;">Keep spelling to unlock more awesome bees!</p>
            <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}


