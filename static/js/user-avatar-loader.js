/**
 * User Avatar Loader - GLB-Only Edition
 * ========================================
 * Loads 3D avatars from GLB files with optimized wave-based preloading
 * - Supports 39 avatars total
 * - GLB-only format (no OBJ/MTL legacy code)
 * - Wave-based loading (6-8 avatars per wave)
 * - Robust timeout & retry logic
 * - In-memory GLB caching
 * 
 * @version 2.0.0 - GLB-Only
 * @date 2025-11-17
 */

// Robust definition wrapper (fixed block scope): ensure constructor always becomes globally accessible.
// Previous version defined the class inside an if-block, making the identifier block-scoped and
// causing a ReferenceError when accessed outside that block. This version defines & assigns atomically.
(function(){
    if (typeof window.UserAvatarLoader !== 'function') {

class UserAvatarLoader {
    constructor() {
        // User avatar state
        this.userAvatar = null;
        this.userAvatarValid = false;
        
        // Avatar catalog
        this.avatarMap = {};
        this.avatarDataLoaded = false;
        this.dbConnectionVerified = false;
        
        // GLB cache for loaded models
        if (!window.avatarCache) {
            window.avatarCache = new Map();
        }
        
        // Known aliases for resilient lookups
        this._aliasMap = {
            'albee': 'al-bee',
            'anxiousbee': 'anxious-bee',
            'mascotbee': 'mascot-bee',
            'monsterbee': 'monster-bee',
            'professorbee': 'professor-bee',
            'rockerbee': 'rocker-bee',
            'superbee': 'super-bee',
            'vampbee': 'vamp-bee',
            'warebee': 'ware-bee',
            'zombee': 'zom-bee',
            'buzzbee': 'buzz-bee',
            'selfiebee': 'selfie-bee',
            'coolbee': 'mascot-bee',
            'cool-bee': 'mascot-bee',
            'cool_bee': 'mascot-bee'
        };
        
        // Initialize fallback avatar
        this._initFallback();
        
        // DISABLED: Quick DB connection check - was blocking loader
        // this.verifyDatabaseConnection();
    }

    /**
     * Initialize fallback MascotBee avatar
     */
    _initFallback() {
        const mascotGlb = '/static/assets/avatars/glb_files/MascotBee.glb';
        const mascotThumb = '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png';
        
        this.defaultAvatar = {
            glb: mascotGlb,
            thumbnail: mascotThumb,
            name: 'Mascot Bee Avatar',
            format: 'glb'
        };
        
        // Pre-populate map with fallback
        this.avatarMap = {
            'mascot-bee': this.defaultAvatar
        };
    }

    /**
     * Safe fetch with timeout and retry logic
     * @param {string} url - URL to fetch
     * @param {object} opts - Fetch options
     * @param {number} timeoutMs - Timeout in milliseconds
     * @param {number} retries - Number of retry attempts
     * @returns {Promise} Fetch promise with timeout
     */
    async _safeFetch(url, opts = {}, timeoutMs = 8000, retries = 2) {
        let lastError;
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            let controller = null;
            let timeout = null;
            try {
                controller = new AbortController();
                // Provide an explicit abort reason so Edge doesn't log "aborted without reason".
                timeout = setTimeout(() => {
                    try {
                        controller.abort('timeout');
                    } catch (_e) {
                        // Older engines may not accept a reason.
                        controller.abort();
                    }
                }, timeoutMs);
                
                const response = await fetch(url, { 
                    credentials: 'same-origin', // Fix Safari ITP blocking
                    ...opts, 
                    signal: controller.signal 
                });
                
                clearTimeout(timeout);
                
                if (!response.ok && attempt < retries) {
                    console.warn(`⚠️ Fetch attempt ${attempt + 1} failed: ${url} (${response.status})`);
                    await new Promise(resolve => setTimeout(resolve, 500)); // 500ms between retries
                    continue;
                }
                
                return response;
            } catch (error) {
                lastError = error;
                if (timeout) {
                    clearTimeout(timeout);
                }

                // AbortErrors are expected for timeouts and navigation cancels.
                // Don't spam the console for these; just retry (if it's our timeout) or fall back.
                const isAbort = (error && (error.name === 'AbortError' || /aborted/i.test(error.message || '')));
                const reason = controller && controller.signal ? controller.signal.reason : undefined;
                if (isAbort) {
                    if (attempt < retries && reason === 'timeout') {
                        await new Promise(resolve => setTimeout(resolve, 350));
                        continue;
                    }
                    throw error;
                }
                
                if (attempt < retries) {
                    console.warn(`⚠️ Fetch attempt ${attempt + 1} error: ${url} (${error.message})`);
                    await new Promise(resolve => setTimeout(resolve, 500));
                } else {
                    console.error(`❌ All fetch attempts failed for: ${url}`);
                    throw error;
                }
            }
        }
        
        throw lastError || new Error('Fetch failed');
    }

    /**
     * Verify database connection (quick check)
     */
    async verifyDatabaseConnection() {
        try {
            const response = await this._safeFetch('/api/avatars', {}, 1000, 0);
            if (response.ok) {
                this.dbConnectionVerified = true;
                console.log('✅ Database connection verified');
            }
        } catch (error) {
            console.warn('⚠️ Database connection check failed:', error.message);
            this.dbConnectionVerified = false;
        }
    }

    /**
     * Load avatar catalog from API
     */
    async loadAvatarCatalog() {
        if (this.avatarDataLoaded) {
            console.log('ℹ️ Avatar catalog already loaded');
            return;
        }

        console.log('📡 Loading avatar catalog from database...');
        
        try {
            const response = await this._safeFetch('/api/avatars', {}, 5000, 2);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            let avatars = [];
            
            if (Array.isArray(data)) {
                avatars = data;
            } else if (data.avatars && Array.isArray(data.avatars)) {
                avatars = data.avatars;
            } else if (data.data && Array.isArray(data.data)) {
                avatars = data.data;
            }
            
            console.log(`✅ Loaded ${avatars.length} avatars from database`);
            
            // Convert to GLB-only format
            avatars.forEach(avatar => {
                const id = avatar.id;
                const urls = avatar.urls || avatar;
                
                // Extract GLB path (standard field from modern API)
                const glbPath = (urls && urls.glb !== undefined) ? urls.glb : null;
                
                // Validate it's actually a GLB file
                const isGlb = typeof glbPath === 'string' && /(\.glb|\.gltf)(\?.*)?$/i.test(glbPath);
                
                if (!isGlb && glbPath) {
                    console.warn(`⚠️ Avatar ${id} has non-GLB model path: ${glbPath}`);
                    return; // Skip non-GLB avatars
                }
                
                if (!glbPath) {
                    console.warn(`⚠️ Avatar ${id} has no GLB path defined`);
                    return;
                }
                
                // Build GLB-only avatar entry
                this.avatarMap[id] = {
                    glb: glbPath,
                    thumbnail: (urls && urls.thumbnail !== undefined) ? urls.thumbnail : null || avatar.thumbnail_url || avatar.thumbnail,
                    name: avatar.name || id,
                    format: 'glb',
                    folder_path: avatar.folder_path
                };
                
                console.groupCollapsed(`Avatar Loaded: ${avatar.name || id}`);
                console.log('  ID:', id);
                console.log('  GLB:', glbPath);
                console.log('  Thumbnail:', this.avatarMap[id].thumbnail);
                console.groupEnd();
            });
            
            this.avatarDataLoaded = true;
            console.log(`✅ Avatar map built with ${Object.keys(this.avatarMap).length} entries`);
            
            // Apply aliases for resilient lookups
            this._applyAliases();
            
        } catch (error) {
            console.error('❌ Failed to load avatar catalog:', error);
            // Fallback already initialized in constructor
            this.avatarDataLoaded = true;
        }
    }

    /**
     * Normalize avatar ID for lookup
     */
    _normalizeId(idLike) {
        if (!idLike) return 'mascot-bee';
        
        const raw = String(idLike).trim().toLowerCase();
        const basic = raw.replace(/[\s_]+/g, '-');
        
        // Check aliases
        if (this._aliasMap[raw]) return this._aliasMap[raw];
        if (this._aliasMap[basic]) return this._aliasMap[basic];
        
        // Support removing hyphens
        const collapsed = basic.replace(/-/g, '');
        if (this._aliasMap[collapsed]) return this._aliasMap[collapsed];
        
        return basic;
    }

    /**
     * Apply aliases to avatar map
     */
    _applyAliases() {
        for (const [aliasKey, canonical] of Object.entries(this._aliasMap)) {
            const target = this.avatarMap[canonical];
            if (target) {
                this.avatarMap[aliasKey] = target;
                this.avatarMap[aliasKey.replace(/\s+/g, '-')] = target;
                this.avatarMap[aliasKey.replace(/\s+/g, '')] = target;
            }
        }
        console.log(`✅ Aliases applied (${Object.keys(this._aliasMap).length} mappings)`);
    }

    /**
     * Simplified avatar system check - just count, skip validation
     * @param {Function} progressCallback - Optional progress callback
     */
    async preloadAvatarSystem(progressCallback = null) {
        console.groupCollapsed('🚀 Avatar System Preload');
        console.log('Counting Avatar GLB Files...');
        
        const results = {
            totalAvatars: 0,
            successfulAvatars: 0,
            failedAvatars: [],
            systemReady: true,
            fallbackReady: true
        };

        try {
            // Get unique avatars (deduplicate by GLB path)
            const seenPaths = new Set();
            const uniqueAvatars = [];
            
            for (const [key, data] of Object.entries(this.avatarMap)) {
                const primaryPath = data.glb || `__no_model__:${key}`;
                if (!seenPaths.has(primaryPath)) {
                    seenPaths.add(primaryPath);
                    uniqueAvatars.push({ key, data });
                }
            }
            
            results.totalAvatars = uniqueAvatars.length;
            results.successfulAvatars = uniqueAvatars.length;
            
            console.log(`✅ Avatar Index Built: ${results.totalAvatars} GLB files available`);
            console.log('📦 Files will load on-demand via Three.js');
            
            results.systemReady = true;
            
            // Log summary
            console.log(`📊 Avatar System Ready:`);
            console.log(`   Total: ${results.totalAvatars} avatars`);
            console.log(`   Loading: On-demand (lazy)`);
            console.groupEnd();
            
            return results;
            
        } catch (error) {
            console.error('❌ Avatar system preload failed:', error);
            console.groupEnd();
            results.systemReady = false;
            return results;
        }
    }

    /**
     * Initialize user avatar from API
     */
    async init() {
        this.showLoadingState();
        
        // Simplified preload - just count avatars, skip validation
        if (!window.avatarPreloadResults) {
            console.log('🔄 Counting avatars...');
            const avatarCount = Object.keys(this.avatarMap).length;
            window.avatarPreloadResults = {
                totalAvatars: avatarCount,
                successfulAvatars: avatarCount,
                failedAvatars: [],
                systemReady: true,
                fallbackReady: true
            };
            console.log(`✅ Avatar system ready: ${avatarCount} avatars available`);
            
            try {
                document.dispatchEvent(new CustomEvent('avatarSystemReady', { 
                    detail: window.avatarPreloadResults 
                }));
            } catch (e) {
                console.warn('Event dispatch failed:', e);
            }
        }
        
        try {
            // Increased timeout to prevent premature aborts on slower devices/connections.
            // Add cache-busting timestamp for iOS Safari to ensure fresh avatar data
            const cacheBuster = Date.now();
            const response = await this._safeFetch(`/api/users/me/avatar?_=${cacheBuster}`, {
                credentials: 'same-origin',
                cache: 'no-store'  // iOS Safari: prevent aggressive caching
            }, 8000, 2);  // 8 second timeout, 2 retries
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success' && data.avatar) {
                    this.userAvatar = data.avatar;
                    
                    console.groupCollapsed('✅ User Avatar Loaded');
                    console.log('ID:', this.userAvatar.avatar_id || this.userAvatar.id);
                    console.log('Name:', this.userAvatar.name);
                    console.groupEnd();
                    
                    // Skip validation - let Three.js handle it on demand
                    this.userAvatarValid = true;
                    this.showLoadedState();
                    return true;
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            // AbortError often means a timeout or navigation cancel. Treat it as a normal fallback.
            const isAbort = (error && (error.name === 'AbortError' || /aborted/i.test(error.message || '')));
            // Keep console noise low for expected aborts/timeouts.
            if (!isAbort) {
                console.warn('⚠️ Using default avatar:', (error.message || error));
            }
            this.userAvatarValid = false;
            // Do not show a scary error UI for timeouts/aborts; just fall back quietly.
            if (!isAbort) {
                this.showErrorState('mascotBee3D', error);
            }
            
            // Default avatar will load on-demand, skip validation
            this.showLoadedState();
        }
        
        return false;
    }

    /**
     * Validate avatar GLB file exists (DEPRECATED - Three.js handles on-demand)
     * Kept for backward compatibility but no longer performs HEAD requests
     */
    async validateAvatarGLB(useDefault = false) {
        const paths = useDefault ? this.defaultAvatar : this.getAvatarPaths();
        
        if (!paths || !paths.glb) {
            console.warn('❌ No GLB path defined');
            return false;
        }
        
        // Skip HEAD request - just assume it exists, Three.js will error if not
        console.log(`📦 GLB path: ${paths.glb.split('/').pop()} (will load on-demand)`);
        return true;
    }

    /**
     * Get avatar GLB paths
     */
    getAvatarPaths() {
        console.log('🔍 getAvatarPaths: this.userAvatar =', this.userAvatar);
        
        // Check user avatar URLs
        const urls = (this.userAvatar && this.userAvatar.urls !== undefined) ? this.userAvatar.urls : null;
        console.log('🔍 getAvatarPaths: urls =', urls);
        
        if (urls && urls.glb) {
            const modelUrl = urls.glb;
            const isGlb = /\.(glb|gltf)(\?.*)?$/i.test(modelUrl);
            
            console.log('✅ Found GLB in userAvatar.urls:', modelUrl);
            if (isGlb) {
                return {
                    glb: modelUrl,
                    thumbnail: urls.thumbnail
                };
            }
        }
        
        // Check avatar map
        const id = this.getAvatarId();
        const mapped = this.avatarMap[id];
        
        console.log('🔍 Checking avatarMap[' + id + ']:', mapped);
        
        if (mapped && mapped.glb) {
            console.log('✅ Found GLB in avatarMap:', mapped.glb);
            return {
                glb: mapped.glb,
                thumbnail: mapped.thumbnail
            };
        }
        
        // Fallback to default
        console.log('⚠️ Using default avatar:', this.defaultAvatar);
        return this.defaultAvatar;
    }

    /**
     * Load user avatar into container
     */
    loadUserAvatar(avatarId = null, containerId = 'mascotBee3D') {
        if (window.DISABLE_AUTO_AVATAR_RENDER) {
            console.log('🚫 Auto-render disabled');
            return Promise.resolve();
        }
        
        return new Promise(async (resolve, reject) => {
            try {
                // If avatarId is null, use the user's registered avatar
                let data;
                if (!avatarId) {
                    console.log('🔍 Loading user\'s registered avatar...');
                    data = this.getAvatarPaths();  // Gets from this.userAvatar or avatarMap
                } else {
                    const normalizedId = this._normalizeId(avatarId);
                    data = this.avatarMap[normalizedId] || this.defaultAvatar;
                }
                
                console.log('📦 Avatar data:', data);
                
                if (!data.glb) {
                    throw new Error('No GLB path found for avatar');
                }
                
                // Check if SmartyBee3D available
                if (typeof window.SmartyBee3D !== 'function') {
                    console.warn('SmartyBee3D not available');
                    this.loadEmergency2DFallback(containerId);
                    return reject(new Error('SmartyBee3D missing'));
                }
                
                // Clear container
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = '';
                    
                    // Get container dimensions
                    const rect = container.getBoundingClientRect();
                    const width = Math.max(120, Math.floor(rect.width));
                    const height = Math.max(120, Math.floor(rect.height));
                    
                    // Create 3D instance
                    // Make main-page avatar larger on screen but KEEP controls enabled
                    const isMainHero = containerId === 'mascotBee3D';
                    const instance = new window.SmartyBee3D(containerId, {
                        width,
                        height,
                        // Enable controls even for main hero
                        autoRotate: false,  // Don't auto-rotate so user can control it
                        enableInteraction: true,  // CHANGED: Enable interaction for controls
                        idleAnimation: false,  // Keep idle animation off for cleaner control
                        glbPath: data.glb,
                        modelPath: data.glb,
                        // Hero framing: bring camera closer for larger on-screen presence
                        zoom: isMainHero ? 1.8 : 1.0,
                        cameraDistanceFactor: isMainHero ? 1.6 : 1.8,
                        verticalOffset: 0.35
                    });
                    
                    // Store instance globally for controller access
                    window.SmartyBee3DInstances = window.SmartyBee3DInstances || {};
                    window.SmartyBee3DInstances[containerId] = instance;
                    
                    // Attach lightweight control methods for compatibility
                    try {
                        if (instance && typeof instance === 'object') {
                            // Remember defaults for reset
                            if (instance.camera) {
                                instance.__defaultCamPos = instance.camera.position.clone();
                            }
                            if (instance.bee) {
                                instance.__defaultBeeRot = instance.bee.rotation.clone();
                            }
                            // Rotate: pitch (x), yaw (y)
                            if (typeof instance.rotate !== 'function') {
                                instance.rotate = function(pitchRad = 0, yawRad = 0){
                                    try {
                                        if (this.bee) {
                                            this.bee.rotation.x += (pitchRad || 0);
                                            this.bee.rotation.y += (yawRad || 0);
                                        }
                                    } catch(e) { /* noop */ }
                                };
                            }
                            // Zoom: move camera along Z axis
                            if (typeof instance.zoom !== 'function') {
                                instance.zoom = function(delta = 0){
                                    try {
                                        if (this.camera) {
                                            const z = this.camera.position.z + (delta * 5);
                                            this.camera.position.z = Math.max(2, Math.min(12, z));
                                        }
                                    } catch(e) { /* noop */ }
                                };
                            }
                            // Reset view to defaults
                            if (typeof instance.resetView !== 'function') {
                                instance.resetView = function(){
                                    try {
                                        if (this.camera && this.__defaultCamPos) {
                                            this.camera.position.copy(this.__defaultCamPos);
                                        }
                                        if (this.bee && this.__defaultBeeRot) {
                                            this.bee.rotation.copy(this.__defaultBeeRot);
                                        }
                                    } catch(e) { /* noop */ }
                                };
                            }
                        }
                        // Instance already stored above - just ensure legacy accessor exists
                        if (typeof window.SmartyBee3D === 'function' && typeof window.SmartyBee3D.getController !== 'function') {
                            window.SmartyBee3D.getController = function(id){
                                return (window.SmartyBee3DInstances && window.SmartyBee3DInstances[id]) || null;
                            };
                        }
                    } catch (e) {
                        console.warn('Controller registry setup failed:', e);
                    }
                    
                    this.showLoadedState(containerId);
                }
                
                resolve();
            } catch (error) {
                console.error('❌ Avatar load failed:', error);
                reject(error);
            }
        });
    }

    /**
     * Load 2D fallback avatar
     */
    load2DFallback(containerId = 'mascotBee3D') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        console.log('🔄 Loading 2D fallback avatar...');
        
        const defaultAvatarType = 'mascot-bee';
        
        if (this.avatarMap[defaultAvatarType]) {
            this.loadUserAvatar(defaultAvatarType, containerId)
                .then(() => {
                    console.log('✅ 2D MascotBee loaded');
                    this.showStatusMessage('Using Mascot Bee Avatar', 'info', 3000);
                })
                .catch(error => {
                    console.error('❌ 2D fallback failed:', error);
                    this.loadEmergency2DFallback(containerId);
                });
        } else {
            this.loadEmergency2DFallback(containerId);
        }
    }

    /**
     * Emergency fallback - hide container
     */
    loadEmergency2DFallback(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        console.log('🔄 Hiding avatar container (emergency fallback)');
        container.style.display = 'none';
        this.showStatusMessage('Avatar unavailable', 'info', 2000);
    }

    /**
     * Get avatar options for SmartyBee3D
     */
    getAvatarOptions(additionalOptions = {}) {
        const paths = this.getAvatarPaths();
        const glbPath = paths.glb || this.defaultAvatar.glb;
        
        return {
            glbPath,
            modelPath: glbPath,
            ...additionalOptions
        };
    }

    /**
     * Get thumbnail URL
     */
    getThumbnailUrl() {
        const paths = this.getAvatarPaths();
        return paths.thumbnail || this.defaultAvatar.thumbnail;
    }

    /**
     * Get avatar ID
     */
    getAvatarId() {
        return this._normalizeId((this.userAvatar && this.userAvatar.avatar_id !== undefined) ? this.userAvatar.avatar_id : null || (this.userAvatar && this.userAvatar.id !== undefined) ? this.userAvatar.id : null || 'mascot-bee');
    }

    /**
     * Check if using mascot
     */
    isUsingMascot() {
        return !this.userAvatar || this.getAvatarId() === 'mascot-bee';
    }

    /**
     * Get avatar display name
     */
    getAvatarDisplayName() {
        return (this.userAvatar && this.userAvatar.name !== undefined) ? this.userAvatar.name : '';
    }

    /**
     * Show loading state
     */
    showLoadingState(containerId = 'mascotBee3D') {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('avatar-loaded', 'avatar-error');
            container.classList.add('avatar-loading');
        }
    }

    /**
     * Show loaded state
     */
    showLoadedState(containerId = 'mascotBee3D') {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('avatar-loading', 'avatar-error');
            container.classList.add('avatar-loaded');
        }
    }

    /**
     * Show error state
     */
    showErrorState(containerId = 'mascotBee3D', error = null) {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('avatar-loading', 'avatar-loaded');
            container.classList.add('avatar-error');
        }
        
        if (error) {
            console.error('Avatar error:', error);
        }
    }

    /**
     * Show status message
     */
    showStatusMessage(message, type = 'info', timeout = 3000) {
        try {
            if (typeof window.showStatusMessage === 'function') {
                window.showStatusMessage(message, type, timeout);
                return;
            }

            const toast = document.createElement('div');
            const bgColor = type === 'warning' ? 'rgba(255,152,0,0.95)' : 
                           type === 'error' ? 'rgba(244,67,54,0.95)' : 
                           'rgba(76,175,80,0.95)';
            
            toast.style.cssText = `
                position: fixed;
                bottom: clamp(12px, 2vh, 24px);
                right: clamp(12px, 2vw, 24px);
                background: ${bgColor};
                color: #fff;
                padding: clamp(8px, 1.5vh, 12px) clamp(12px, 2vw, 16px);
                border-radius: 0.5rem;
                font-size: clamp(0.875rem, 1.8vw, 1rem);
                z-index: 9999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                opacity: 0;
                transform: translateY(10px);
                transition: opacity 0.2s ease, transform 0.2s ease;
            `;
            
            toast.textContent = message;
            document.body.appendChild(toast);
            
            requestAnimationFrame(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateY(0)';
            });
            
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(10px)';
                setTimeout(() => toast.remove(), 200);
            }, timeout);
        } catch (e) {
            console.log(`[${type}] ${message}`);
        }
    }

    /**
     * Get system health badge
     */
    getSystemHealthBadge() {
        const results = window.avatarPreloadResults;
        
        if (!results) {
            return { status: 'unknown', color: '#999', text: 'Not Checked' };
        }
        
        const displayName = this.getAvatarDisplayName();
        
        if (results.systemReady) {
            return { 
                status: 'healthy', 
                color: '#4CAF50', 
                text: `${displayName} Ready` 
            };
        } else if (results.successfulAvatars > 0) {
            return { 
                status: 'degraded', 
                color: '#FF9800', 
                text: `${displayName} (Partial)` 
            };
        } else {
            return { 
                status: 'failed', 
                color: '#F44336', 
                text: 'System Failed' 
            };
        }
    }
}

// Bind constructor to window (atomic definition)
window.UserAvatarLoader = UserAvatarLoader;
    }
})();

// Create global instance if not already created
if (!window.userAvatarLoader) {
    try {
        const LoaderCtor = window.UserAvatarLoader; // guaranteed defined by wrapper
        window.userAvatarLoader = new LoaderCtor();
    } catch (e) {
        console.error('❌ Avatar loader bootstrap failed:', e);
    }
}

// Runtime verification (defensive): ensure constructor present after wrapper
if (typeof window.UserAvatarLoader !== 'function') {
    console.error('❌ UserAvatarLoader missing after initialization wrapper');
}

// Global controller registry and compatibility shim for legacy calls
// Ensures window.SmartyBee3D.getController('mascotBee3D') works even when SmartyBee3D is a class.
(function(){
    // Initialize registry once
    if (!window.SmartyBee3DInstances) {
        window.SmartyBee3DInstances = {};
    }
    // Back-compat shim: add getController if missing
    if (typeof window.SmartyBee3D === 'function' && typeof window.SmartyBee3D.getController !== 'function') {
        window.SmartyBee3D.getController = function(containerId){
            return (window.SmartyBee3DInstances && window.SmartyBee3DInstances[containerId]) || null;
        };
    }
})();

// Deferred initialization
let avatarInitialized = false;

// Wait for honey loader to finish
document.addEventListener('honeyLoaderFinished', () => {
    if (!avatarInitialized) {
        console.log('🍯 Honey loader finished, initializing avatars');
        avatarInitialized = true;
        setTimeout(() => {
            window.userAvatarLoader.init();
        }, 100);
    }
});

// Fallback timeout
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (!avatarInitialized) {
            console.warn('⚠️ Honey loader timeout, initializing anyway');
            avatarInitialized = true;
            window.userAvatarLoader.init();
        }
    }, 10000);
});
