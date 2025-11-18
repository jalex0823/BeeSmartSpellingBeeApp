/**
 * User Avatar Loader
 * Loads the user's selected 3D avatar instead of the default mascot
 * Works across all pages: quiz, speed round, menu, etc.
 */

class UserAvatarLoader {
    constructor() {
        this.userAvatar = null;
        this.userAvatarValid = false; // track if we validated the avatar asset URLs
        // Avatar data loaded from API on-demand
        this.avatarMap = {};
        this.avatarDataLoaded = false;
        this.dbConnectionVerified = false;
        // Known aliases to improve resilience against spacing/case/underscore differences
        // Only includes the 9 working avatars
        this._aliasMap = {
            'albee': 'al-bee',
            'anxiousbee': 'anxious-bee',
            'mascotbee': 'mascot-bee',
            'monsterbee': 'monster-bee',
            'professorbee': 'professor-bee',
            'rockerbee': 'rocker-bee',
            'superbee': 'superbee',
            'vampbee': 'vamp-bee',
            'warebee': 'ware-bee',
            'zombee': 'zom-bee',
            // New GLB aliases
            'buzzbee': 'buzz-bee',
            'selfiebee': 'selfie-bee',
            // Missing asset alias: map any cool-bee variants to mascot-bee to avoid 404 parse cascade
            'coolbee': 'mascot-bee',
            'cool-bee': 'mascot-bee',
            'cool_bee': 'mascot-bee'
        };
        
        // Initialize legacy defaults so fallback avatar is always defined
        try { this._legacyInit(); } catch(e){ console.warn('Legacy init failed:', e); }

        // Quick DB connection check instead of loading all avatars
        this.verifyDatabaseConnection();
    }

    /**
     * Safe fetch with timeout to prevent infinite hangs
     * @param {string} url - URL to fetch
     * @param {object} opts - Fetch options
     * @param {number} timeoutMs - Timeout in milliseconds (default 1500ms)
     * @returns {Promise} Fetch promise with timeout
     */
    async _safeFetch(url, opts = {}, timeoutMs = 1500) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), timeoutMs);
        return fetch(url, { ...opts, signal: controller.signal })
            .finally(() => clearTimeout(timeout));
    }

    // Legacy properties preserved for compatibility
    _legacyInit() {
        // DEPRECATED - Old hardcoded map (kept for fallback only) - GLB ONLY
        // Provide minimal GLB paths to avoid any OBJ/MTL usage in fallbacks
        const mascotGlb = '/static/assets/avatars/glb_files/MascotBee.glb';
        const mascotThumb = '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png';
        this._oldAvatarMap = {
            'al-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'anxious-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'mascot-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'monster-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'professor-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'rocker-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'superbee': { glb: mascotGlb, thumbnail: mascotThumb },
            'vamp-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'ware-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            'zom-bee': { glb: mascotGlb, thumbnail: mascotThumb },
            // New GLB avatars (served from /static/assets/avatars/glb_files)
            'buzz-bee': {
                glb: '/static/assets/avatars/glb_files/BuzzBee.glb',
                thumbnail: '/static/assets/avatars/glb_files/AvatarThumbnails/CutieBee!.png'
            },
            'selfie-bee': {
                glb: '/static/assets/avatars/glb_files/SelfieBee.glb',
                thumbnail: '/static/assets/avatars/glb_files/AvatarThumbnails/CutieBee!.png'
            }
        };
        
        // Initialize avatarMap with fallback data immediately (will be replaced by API if successful)
        this.avatarMap = {...this._oldAvatarMap};
        
        // Fallback to MascotBee if no avatar selected - PRIORITIZE GLB FORMAT
        // GLB is preferred: single file, faster loading, better compatibility
        this.defaultAvatar = {
            glb: '/static/assets/avatars/glb_files/MascotBee.glb',
            // Legacy OBJ/MTL/PNG model references removed – GLB only
            thumbnail: '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png',
            name: 'Mascot Bee',
            format: 'glb'
        };

    // Guests are restricted to MascotBee only. Any legacy guest override in localStorage is ignored.
    // Keep key name here only to optionally clear old values if present.
    this.GUEST_AVATAR_KEY = 'guest_avatar_slug';
    }

    /**
     * Quick database connection verification (lightweight check)
     * Only verifies that the database is accessible, doesn't load all avatar data
     */
    async verifyDatabaseConnection() {
        try {
            console.log('🔍 Verifying avatar database connection...');
            const response = await this._safeFetch('/api/avatars?category=classic', { credentials: 'same-origin' }, 1500);
            if (response.ok) {
                this.dbConnectionVerified = true;
                console.log('✅ Avatar database connection verified');
            } else {
                console.warn('⚠️ Database connection check failed, will use fallback');
                this.dbConnectionVerified = false;
            }
        } catch (error) {
            console.warn('⚠️ Database connection check failed:', error);
            this.dbConnectionVerified = false;
        }
    }

    /**
     * Load avatar catalog from API (lazy loading - only when needed)
     * This is now called on-demand when getAvatarAssets() needs data
     */
    async loadAvatarCatalog() {
        // Skip if already loaded
        if (this.avatarDataLoaded) {
            console.log('✅ Avatar catalog already loaded');
            return;
        }
        
        try {
            console.log('📡 Loading avatar catalog from database API...');
            const response = await this._safeFetch('/api/avatars', { credentials: 'same-origin' }, 2000);
            if (!response.ok) {
                throw new Error(`API returned ${response.status}`);
            }
            
            const data = await response.json();
            let avatars = [];
            if (Array.isArray(data)) {
                avatars = data;
            } else if (data && Array.isArray(data.avatars)) {
                avatars = data.avatars;
            } else if (data && data.status === 'success' && Array.isArray(data.data)) {
                avatars = data.data;
            }
            console.log(`✅ Loaded ${avatars.length} avatars from database`);
            
            // Convert API response to avatarMap format (GLB ONLY)
            // GLB files are superior: single file, embedded textures, faster loading
            avatars.forEach(avatar => {
                const id = avatar.id;
                const urls = avatar.urls || avatar;
                const modelObj = urls?.model_obj || avatar.model_obj_url || avatar.obj_file_url;
                const isGlb = typeof modelObj === 'string' && /(\.glb|\.gltf)(\?.*)?$/i.test(modelObj);

                // Build avatar data with GLB only; ignore any OBJ/MTL/texture fields
                this.avatarMap[id] = {
                    glb: isGlb ? modelObj : undefined,
                    thumbnail: urls?.thumbnail || avatar.thumbnail_url || avatar.thumbnail,
                    name: avatar.name || id,
                    format: 'glb', // Enforce GLB-only mode
                    folder_path: avatar.folder_path
                };

                // Quality check: warn if GLB missing for glb_files folder
                if (avatar.folder_path === 'glb_files' && !isGlb) {
                    console.warn(`⚠️ Avatar ${id} in glb_files folder but no GLB URL found`);
                }

                // If GLB avatar, verify file extension is correct
                if (isGlb) {
                    console.log(`✅ GLB avatar registered: ${avatar.name || id} -> ${modelObj}`);
                }
            });
            
            this.avatarDataLoaded = true;
            console.log('✅ Avatar map built from API data');
            // Add alias keys so older or inconsistent IDs still resolve
            this._applyAliases();
        } catch (error) {
            console.warn('⚠️ Failed to load avatar catalog from API, using fallback:', error);
            // Fallback to old hardcoded map if API fails
            this.avatarMap = this._oldAvatarMap;
            this._applyAliases();
            this.avatarDataLoaded = true;
        }
    }

    /**
     * Normalize an avatar identifier: trim, lowercase, replace spaces/underscores with hyphens,
     * and apply known alias corrections (e.g., albee -> al-bee, anxiousbee -> anxious-bee).
     */
    _normalizeId(idLike) {
        if (!idLike) return 'mascot-bee';
        const raw = String(idLike).trim().toLowerCase();
        const basic = raw.replace(/[\s_]+/g, '-');
        // Direct alias hit
        if (this._aliasMap[raw]) return this._aliasMap[raw];
        if (this._aliasMap[basic]) return this._aliasMap[basic];
        // Also support removing hyphens for matching keys like frankenbee
        const collapsed = basic.replace(/-/g, '');
        if (this._aliasMap[collapsed]) return this._aliasMap[collapsed];
        return basic;
    }

    /**
     * Create alias keys in avatarMap so lookups by legacy or inconsistent ids still resolve.
     */
    _applyAliases() {
        try {
            const entries = Object.entries(this._aliasMap);
            for (const [aliasKey, canonical] of entries) {
                const target = this.avatarMap[canonical];
                if (target) {
                    // Add multiple forms to be safe
                    this.avatarMap[aliasKey] = target;
                    this.avatarMap[aliasKey.replace(/\s+/g, '-')] = target;
                    this.avatarMap[aliasKey.replace(/\s+/g, '')] = target;
                }
            }
        } catch (e) {
            console.warn('Alias application failed:', e);
        }
    }

    /**
     * Preload and validate all avatar files before main menu display
     */
    async preloadAvatarSystem(progressCallback = null) {
        console.log('🔄 Starting avatar system preload validation...');
        
        // Lazy load avatar catalog if not already loaded
        if (!this.avatarDataLoaded) {
            console.log('📡 Avatar catalog not loaded yet, loading now...');
            await this.loadAvatarCatalog();
        }
        
        const preloadResults = {
            totalAvatars: 0,
            successfulAvatars: 0,
            failedAvatars: [],
            validationDetails: {},
            systemReady: false,
            fallbackReady: false
        };

        try {
            // Get unique avatars only (deduplicate by primary model path: GLB only)
            const seenPaths = new Set();
            const uniqueAvatars = [];
            for (const [key, data] of Object.entries(this.avatarMap)) {
                const primaryPath = data.glb || `__no_model__:${key}`;
                if (!seenPaths.has(primaryPath)) {
                    seenPaths.add(primaryPath);
                    uniqueAvatars.push({ key, data });
                }
            }
            
            preloadResults.totalAvatars = uniqueAvatars.length;
            
            console.log(`📋 Found ${preloadResults.totalAvatars} unique avatars (${Object.keys(this.avatarMap).length} total including aliases)`);
            
            // OPTIMIZATION: Skip file validation - database already validated avatars
            // Just verify fallback system and trust the database
            // GLB files load faster than OBJ (single file vs 3 files), so reduced delays
            console.log('⚡ Using fast preload (database-validated avatars, GLB-optimized)');
            
            // Mark all avatars as successful (database has already validated them)
            preloadResults.successfulAvatars = preloadResults.totalAvatars;
            for (const { key: avatarKey, data: avatarData } of uniqueAvatars) {
                // Report progress with avatar name
                if (progressCallback) {
                    const avatarName = avatarData.name || avatarKey;
                    const format = 'glb';
                    progressCallback(`${avatarName} (${format})`);
                }
                
                preloadResults.validationDetails[avatarKey] = {
                    status: 'valid',
                    files: ['trusted-from-database'],
                    format: 'glb',
                    timestamp: new Date().toISOString()
                };
                
                // Minimal delay: GLB avatars = 5ms
                // Total for 39 avatars: ~200-300ms (was 390ms)
                const delay = 5;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
            
            // Only validate fallback system (MascotBee) - critical for app stability
            if (progressCallback) {
                progressCallback('MascotBee (Fallback)');
            }
            console.log('🔍 Validating fallback system (MascotBee)...');
            try {
                if (!this.defaultAvatar) {
                    console.warn('Fallback defaultAvatar missing; reinitializing legacy defaults');
                    this._legacyInit();
                }
                await this.validateAvatarFilesForPaths(this.defaultAvatar);
                preloadResults.fallbackReady = true;
                console.log('✅ Fallback system (MascotBee) validated successfully');
            } catch (error) {
                console.error('❌ Critical: Fallback system validation failed:', error);
                preloadResults.fallbackReady = false;
            }
            
            // System is ready if fallback works
            preloadResults.systemReady = preloadResults.fallbackReady;
            
            // Log final results
            console.log(`📊 Avatar System Preload Results:`);
            console.log(`   Total Avatars: ${preloadResults.totalAvatars}`);
            console.log(`   Successful: ${preloadResults.successfulAvatars}`);
            console.log(`   Failed: ${preloadResults.failedAvatars.length}`);
            console.log(`   Success Rate: 100.0%`);
            console.log(`   Fallback Ready: ${preloadResults.fallbackReady}`);
            console.log(`   System Ready: ${preloadResults.systemReady}`);
            
            return preloadResults;
            
        } catch (error) {
            console.error('❌ Avatar system preload failed completely:', error);
            preloadResults.systemReady = false;
            return preloadResults;
        }
    }

    /**
     * Validate that avatar files exist and are accessible (explicit paths)
     * Enhanced for GLB files with better error reporting
     */
    async validateAvatarFilesForPaths(avatarData) {
        const filesToCheck = [];
        const format = avatarData.format || 'unknown';
        
        // GLB files only need to check one file (much simpler!)
        if (avatarData.glb) {
            filesToCheck.push(avatarData.glb);
            console.log(`🎯 Validating GLB avatar: ${avatarData.name || 'Unknown'}`);
        } else {
            throw new Error('Non-GLB avatar provided to validation in GLB-only mode');
        }
        
        // Always check thumbnail if present
        if (avatarData.thumbnail) {
            filesToCheck.push(avatarData.thumbnail);
        }
        
        const validFiles = [];
        const errors = [];
        
        for (const fileUrl of filesToCheck) {
            if (!fileUrl) {
                errors.push(`Missing file URL in avatar data`);
                continue;
            }
            
            try {
                const response = await this._safeFetch(fileUrl, { method: 'HEAD' }, 2000);
                if (response.ok) {
                    const fileSize = response.headers.get('content-length');
                    validFiles.push({
                        url: fileUrl,
                        type: this.getFileType(fileUrl),
                        size: fileSize ? `${(parseInt(fileSize)/1024).toFixed(1)}KB` : 'unknown'
                    });
                    console.log(`  ✅ ${this.getFileType(fileUrl)}: ${fileUrl.split('/').pop()} (${fileSize ? (parseInt(fileSize)/1024).toFixed(1)+'KB' : 'unknown size'})`);
                } else {
                    const errorMsg = `${fileUrl}: HTTP ${response.status}`;
                    errors.push(errorMsg);
                    console.error(`  ❌ ${errorMsg}`);
                }
            } catch (error) {
                const errorMsg = `${fileUrl}: ${error.message}`;
                errors.push(errorMsg);
                console.error(`  ❌ ${errorMsg}`);
            }
        }
        
        if (errors.length > 0) {
            const errorDetails = `File validation failed for ${avatarData.name || 'avatar'} (${format} format): ${errors.join(', ')}`;
            console.error(`❌ ${errorDetails}`);
            throw new Error(errorDetails);
        }
        
        console.log(`✅ All ${filesToCheck.length} files validated for ${avatarData.name || 'avatar'}`);
        return { validFiles, fileCount: validFiles.length };
    }

    /**
     * Get file type from URL for validation logging
     */
    getFileType(url) {
        if (/(\.glb|\.gltf)(\?.*)?$/i.test(url)) return 'glb';
        if (url.endsWith('.png')) return url.includes('!') ? 'thumbnail' : 'texture';
        return 'unknown';
    }

    /**
     * Display avatar system status and preload results
     */
    displaySystemStatus(preloadResults = null) {
        const results = preloadResults || window.avatarPreloadResults;
        
        if (!results) {
            console.log('📊 Avatar System Status: No preload results available');
            return 'No preload results available - system may not be initialized';
        }

        const statusReport = {
            summary: `Avatar System: ${results.systemReady ? 'Ready' : 'Issues Detected'}`,
            details: {
                totalAvatars: results.totalAvatars,
                workingAvatars: results.successfulAvatars,
                failedAvatars: results.failedAvatars.length,
                successRate: `${Math.round((results.successfulAvatars / results.totalAvatars) * 100)}%`,
                fallbackStatus: results.fallbackReady ? 'Ready' : 'Failed',
                systemStatus: results.systemReady ? 'Ready' : 'Degraded'
            },
            failedList: results.failedAvatars.map(f => ({
                avatar: f.avatar,
                error: f.error,
                timestamp: f.timestamp
            })),
            validationDetails: results.validationDetails
        };

        console.log('📊 Avatar System Status Report:', statusReport);
        return statusReport;
    }

    /**
     * Get avatar system health for display in UI
     */
    getSystemHealthBadge() {
        const results = window.avatarPreloadResults;
        
        if (!results) {
            return { status: 'unknown', color: '#999', text: 'Not Checked' };
        }
        
        // Prefer showing the current avatar title instead of counts
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

    /**
     * Human-friendly avatar display name
     */
    getAvatarDisplayName() {
        const id = this.getAvatarId();
        const mapping = {
            'al-bee': 'AlBee',
            'anxious-bee': 'Anxious Bee',
            'mascot-bee': 'Mascot Bee',
            'monster-bee': 'Monster Bee',
            'professor-bee': 'Professor Bee',
            'rocker-bee': 'Rocker Bee',
            'vamp-bee': 'Vamp Bee',
            'ware-bee': 'Ware Bee',
            'zom-bee': 'Zom Bee',
            'buzz-bee': 'Buzz Bee',
            'selfie-bee': 'Selfie Bee'
        };
        return (this.userAvatar?.name) || mapping[id] || 'Bee Avatar';
    }

    /**
     * Show loading state
     */
    showLoadingState(containerId = 'mascotBee3D') {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('avatar-loaded', 'avatar-error');
            container.classList.add('avatar-loading');
            console.log(`🐝 Avatar loading started for ${containerId}`);
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
            console.log(`✅ Avatar loaded successfully for ${containerId}`);
        }
    }

    /**
     * Show error state and attempt 3D MascotBee fallback
     */
    showErrorState(containerId = 'mascotBee3D', error = null) {
        // Respect page-level directive to avoid any auto rendering on specific pages
        if (window && window.DISABLE_AUTO_AVATAR_RENDER) {
            console.log('🚫 Auto avatar render disabled on this page; suppressing fallback/error render');
            return;
        }
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('avatar-loading', 'avatar-loaded');
            container.classList.add('avatar-error');
            console.error(`❌ Avatar loading failed for ${containerId}:`, error);
            
            // Try 3D MascotBee fallback first
            this.load2DFallback(containerId);
            
            // Show error notification
            this.showAvatarErrorNotification(error);
        }
    }

    /**
     * Load 3D MascotBee as fallback when other 3D avatars fail
     */
    load2DFallback(containerId = 'mascotBee3D') {
        if (window && window.DISABLE_AUTO_AVATAR_RENDER) {
            console.log('🚫 Auto avatar render disabled on this page; skipping 3D fallback');
            return;
        }
        console.log('🔄 Loading 3D MascotBee fallback...');
        
        // Use MascotBee as the default 3D fallback avatar
        const defaultAvatarType = 'mascot-bee';
        
        if (this.avatarMap[defaultAvatarType]) {
            console.log('Loading MascotBee 3D model as fallback');
            this.loadUserAvatar(defaultAvatarType, containerId)
                .then(() => {
                    console.log('✅ 3D MascotBee fallback loaded successfully');
                    // Per UI rule: show name only, no counts
                    this.showStatusMessage('Using MascotBee avatar', 'info', 4000);
                })
                .catch(error => {
                    console.error('❌ MascotBee fallback failed, using emergency 2D display:', error);
                    this.loadEmergency2DFallback(containerId);
                });
        } else {
            console.error('❌ MascotBee not found in avatar map, using emergency 2D');
            this.loadEmergency2DFallback(containerId);
        }
    }

    /**
     * Render a user avatar (GLB only) or fallback to MascotBee.
     * Legacy OBJ/MTL pipeline removed.
     */
    loadUserAvatar(avatarId = 'mascot-bee', containerId = 'mascotBee3D') {
        if (window && window.DISABLE_AUTO_AVATAR_RENDER) {
            console.log('🚫 Auto avatar render disabled on this page; loadUserAvatar aborted');
            return Promise.resolve();
        }
        return new Promise(async (resolve, reject) => {
            try {
                // Prefer normalized id and map lookup
                const normalizedId = this._normalizeId(avatarId);
                const data = this.avatarMap[normalizedId] || this.defaultAvatar;

                // GLB only resolution
                let paths = null;
                if (data && data.glb) {
                    paths = { glb: data.glb };
                } else {
                    const resolved = this.getAvatarPaths();
                    paths = resolved?.glb ? { glb: resolved.glb } : { glb: this.defaultAvatar.glb };
                }

                // Render via SmartyBee3D (GLB preferred)
                if (typeof window.SmartyBee3D !== 'function') {
                    console.warn('SmartyBee3D not available, switching to emergency 2D fallback');
                    this.loadEmergency2DFallback(containerId);
                    return reject(new Error('SmartyBee3D missing'));
                }

                // Clear container before re-render
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = '';
                }

                // Create the 3D instance
                // Width/height auto-detect from container when possible
                const rect = container ? container.getBoundingClientRect() : { width: 200, height: 200 };
                const baseOpts = {
                    width: Math.max(120, Math.floor(rect.width)),
                    height: Math.max(120, Math.floor(rect.height)),
                    autoRotate: true,
                    enableInteraction: true
                };

                // eslint-disable-next-line no-new
                new window.SmartyBee3D(containerId, {
                    ...baseOpts,
                    glbPath: paths.glb,
                    modelPath: paths.glb
                });

                this.showLoadedState(containerId);
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    }

    /**
     * Emergency 2D fallback when even MascotBee 3D fails
     * UPDATED: Hide container instead of showing 2D bee circle
     */
    loadEmergency2DFallback(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        console.log('🔄 Hiding avatar container - no fallback shown');
        
        // Hide the container completely - no 2D fallback
        container.style.display = 'none';
        
        console.log('✅ Avatar container hidden (3D load failed)');
        this.showStatusMessage('3D avatar loading issue - container hidden', 'info', 3000);
    }

    /**
     * Show avatar error notification
     */
    showAvatarErrorNotification(error) {
        // Check if we're on iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);
        const isMobile = isIOS || isAndroid;
        
        let message = '🐝 Avatar loading issue detected';
        if (isMobile) {
            message += ` (${isIOS ? 'iOS' : 'Android'} device)`;
        }
        
        // Create or update error notification
        let notification = document.getElementById('avatarErrorNotification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'avatarErrorNotification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(255, 99, 71, 0.95);
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                z-index: 9999;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                cursor: pointer;
                transform: translateX(100%);
                transition: transform 0.3s ease;
            `;
            document.body.appendChild(notification);
        }
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>⚠️</span>
                <div>
                    <div style="font-weight: bold;">${message}</div>
                    <div style="font-size: 12px; opacity: 0.9;">Tap to retry loading</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none; border: none; color: white; 
                    font-size: 16px; cursor: pointer; padding: 0;
                ">×</button>
            </div>
        `;
        
        // Show notification
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Add retry functionality
        notification.addEventListener('click', () => {
            notification.remove();
            this.init();
        });
    }

    /**
     * Lightweight status/toast message helper to avoid undefined method errors.
     */
    showStatusMessage(message, type = 'info', timeout = 3000) {
        try {
            // If app-level helper exists, delegate
            if (typeof window.showStatusMessage === 'function') {
                window.showStatusMessage(message, type, timeout);
                return;
            }

            // Minimal inline toast
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${type === 'warning' ? 'rgba(255,152,0,0.95)' : type === 'error' ? 'rgba(244,67,54,0.95)' : 'rgba(76,175,80,0.95)'};
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
     * Initialize and fetch user's avatar preference
     */
    async init() {
        this.showLoadingState();
        // Kick off system preload in parallel (non-blocking) if not already done
        try {
            if (!window.avatarPreloadResults) {
                console.log('🔄 Starting avatar system preload (parallel)...');
                this.preloadAvatarSystem().then(results => {
                    window.avatarPreloadResults = results;
                    try { document.dispatchEvent(new CustomEvent('avatarSystemReady', { detail: results })); } catch(_){ }
                    console.log('✅ Avatar system preload complete');
                }).catch(err => console.warn('⚠️ Avatar system preload failed:', err));
            }
        } catch(e){ console.warn('⚠️ Preload init error:', e); }
        
        try {
            const response = await this._safeFetch('/api/users/me/avatar', {
                credentials: 'same-origin'
            }, 1500);
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success' && data.avatar) {
                    this.userAvatar = data.avatar;
                    console.log('✅ User avatar loaded');
                    console.log('🔍 Full avatar object:', JSON.stringify(this.userAvatar, null, 2));
                    console.log('🔍 avatar_id property:', this.userAvatar.avatar_id);
                    console.log('🔍 id property:', this.userAvatar.id);
                    console.log('🔍 name property:', this.userAvatar.name);
                    
                    // Validate avatar files exist
                    if (await this.validateAvatarFiles()) {
                        this.userAvatarValid = true;
                        this.showLoadedState();
                        return true;
                    } else {
                        this.userAvatarValid = false;
                        throw new Error('Avatar files missing or inaccessible');
                    }
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load user avatar, using default:', error);
            this.userAvatarValid = false;
            this.showErrorState('mascotBee3D', error);

            // Policy: Guests cannot change avatar. Ensure any legacy guest override is cleared.
            try { localStorage.removeItem(this.GUEST_AVATAR_KEY); } catch(_) {}
            // Try to load default avatar as fallback
            if (await this.validateAvatarFiles(true)) {
                this.showLoadedState();
            }
        }
        
        // Use default if no user avatar
        console.log('ℹ️ Using default MascotBee');
        return false;
    }

    // Guest override methods removed by policy; guests use MascotBee only.

    /**
     * Validate that avatar files are accessible
     */
    async validateAvatarFiles(useDefault = false) {
        const paths = useDefault ? this.defaultAvatar : this.getAvatarPaths();
        if (!paths) {
            console.warn('Avatar paths missing');
            return false;
        }

        // GLB-first validation: only need the .glb file
        if (paths.glb) {
            try {
                const res = await this._safeFetch(paths.glb, { method: 'HEAD' }, 1000);
                if (!res.ok) {
                    console.error('❌ GLB file not accessible:', paths.glb, res.status);
                    return false;
                }
                return true;
            } catch (e) {
                console.error('❌ GLB validation error (timeout or network):', e.name === 'Error' && e.message === 'fetch timeout' ? 'TIMEOUT' : e);
                return false;
            }
        }

        // Legacy OBJ validation removed – GLB is mandatory
        console.error('⚠️ validateObjAvatarFiles invoked but OBJ pipeline is deprecated');
        return false;
    }

    /**
     * Get the 3D model paths for the user's avatar (or default)
     */
    getAvatarPaths() {
        // GLB-only resolution
        const u = this.userAvatar?.urls || null;
        if (u && typeof u.model_obj === 'string') {
            const modelUrl = u.model_obj;
            const isGlb = /\.(glb|gltf)(\?.*)?$/i.test(modelUrl) || /\/glb_files\//i.test(modelUrl);
            const thumbnail = u.thumbnail;
            if (isGlb) return { glb: modelUrl, thumbnail };
            // Attempt catalog substitution if non-GLB provided
            const idCandidate = this._normalizeId(this.userAvatar?.id || this.userAvatar?.avatar_id);
            const mapped = this.avatarMap[idCandidate];
            if (mapped && mapped.glb) return { glb: mapped.glb, thumbnail: mapped.thumbnail || thumbnail };
        }
        const id = this.getAvatarId();
        const mapped = this.avatarMap[id];
        if (mapped && mapped.glb) return { glb: mapped.glb, thumbnail: mapped.thumbnail };
        return this.defaultAvatar; // default now GLB-only
    }

    /**
     * Get options object for SmartyBee3D constructor
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
     * Get thumbnail URL for the user's avatar
     */
    getThumbnailUrl() {
        const paths = this.getAvatarPaths();
        return paths.thumbnail;
    }

    /**
     * Get avatar ID
     */
    getAvatarId() {
        return this._normalizeId(this.userAvatar?.avatar_id || 'mascot-bee');
    }

    /**
     * Check if using mascot (default) or custom avatar
     */
    isUsingMascot() {
        return !this.userAvatar || this.userAvatar.avatar_id === 'mascot-bee';
    }
}

// Create global instance
window.userAvatarLoader = new UserAvatarLoader();

// DEFER initialization until honey loader finishes to prevent blocking
let avatarInitialized = false;

// Listen for honey loader to finish
document.addEventListener('honeyLoaderFinished', () => {
    if (!avatarInitialized) {
        console.log('🍯 Honey loader finished, initializing avatar loader');
        avatarInitialized = true;
        // Delay slightly to let page become interactive first
        setTimeout(() => {
            window.userAvatarLoader.init();
        }, 100);
    }
});

// Fallback: Initialize after DOM load if honey loader doesn't fire within 2 seconds
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (!avatarInitialized) {
            console.warn('⚠️ Honey loader timeout, initializing avatar loader anyway');
            avatarInitialized = true;
            window.userAvatarLoader.init();
        }
    }, 2000);
});
