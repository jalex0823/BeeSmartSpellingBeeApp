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
    async _safeFetch(url, opts = {}, timeoutMs = 1200, retries = 1) {
        let lastError;
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), timeoutMs);
                
                const response = await fetch(url, { 
                    credentials: 'same-origin', // Fix Safari ITP blocking
                    ...opts, 
                    signal: controller.signal 
                });
                
                clearTimeout(timeout);
                
                if (!response.ok && attempt < retries) {
                    console.warn(`⚠️ Fetch attempt ${attempt + 1} failed: ${url} (${response.status})`);
                    await new Promise(resolve => setTimeout(resolve, 200)); // 200ms between retries
                    continue;
                }
                
                return response;
            } catch (error) {
                lastError = error;
                
                if (attempt < retries) {
                    console.warn(`⚠️ Fetch attempt ${attempt + 1} error: ${url} (${error.message})`);
                    await new Promise(resolve => setTimeout(resolve, 200));
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
                
                // Extract GLB path (prefer new 'glb' key, fallback to legacy 'model_obj')
                const glbPath = urls?.glb || urls?.model_obj || avatar.glb_url || avatar.model_obj_url || avatar.obj_file_url;
                
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
                    thumbnail: urls?.thumbnail || avatar.thumbnail_url || avatar.thumbnail,
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
            const response = await this._safeFetch('/api/users/me/avatar', {
                credentials: 'same-origin'
            }, 1500, 1);
            
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
            console.warn('⚠️ Using default avatar:', error.message);
            this.userAvatarValid = false;
            this.showErrorState('mascotBee3D', error);
            
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
        // Check user avatar URLs
        const urls = this.userAvatar?.urls;
        if (urls && urls.model_obj) {
            const modelUrl = urls.model_obj;
            const isGlb = /\.(glb|gltf)(\?.*)?$/i.test(modelUrl);
            
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
        
        if (mapped && mapped.glb) {
            return {
                glb: mapped.glb,
                thumbnail: mapped.thumbnail
            };
        }
        
        // Fallback to default
        return this.defaultAvatar;
    }

    /**
     * Load user avatar into container
     */
    loadUserAvatar(avatarId = 'mascot-bee', containerId = 'mascotBee3D') {
        if (window.DISABLE_AUTO_AVATAR_RENDER) {
            console.log('🚫 Auto-render disabled');
            return Promise.resolve();
        }
        
        return new Promise(async (resolve, reject) => {
            try {
                const normalizedId = this._normalizeId(avatarId);
                const data = this.avatarMap[normalizedId] || this.defaultAvatar;
                
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
                    // Make main-page avatar larger on screen and reduce animations
                    const isMainHero = containerId === 'mascotBee3D';
                    new window.SmartyBee3D(containerId, {
                        width,
                        height,
                        // Keep the hero static by default on the home screen
                        autoRotate: isMainHero ? false : true,
                        enableInteraction: isMainHero ? false : true,
                        idleAnimation: isMainHero ? false : true,
                        glbPath: data.glb,
                        modelPath: data.glb,
                        // Hero framing: bring camera closer for larger on-screen presence
                        zoom: isMainHero ? 1.8 : 1.0,
                        cameraDistanceFactor: isMainHero ? 1.6 : 1.8,
                        verticalOffset: 0.35
                    });
                    
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
        return this._normalizeId(this.userAvatar?.avatar_id || this.userAvatar?.id || 'mascot-bee');
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
        return this.userAvatar?.name || 'Mascot Bee Avatar';
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
                bottom: 20px;
                right: 20px;
                background: ${bgColor};
                color: #fff;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 14px;
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

// Create global instance
window.userAvatarLoader = new UserAvatarLoader();

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
    }, 2000);
});
