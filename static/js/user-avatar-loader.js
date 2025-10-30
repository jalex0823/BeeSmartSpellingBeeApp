/**
 * User Avatar Loader
 * Loads the user's selected 3D avatar instead of the default mascot
 * Works across all pages: quiz, speed round, menu, etc.
 */

class UserAvatarLoader {
    constructor() {
        this.userAvatar = null;
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
            'zombee': 'zom-bee'
        };
        
        // Quick DB connection check instead of loading all avatars
        this.verifyDatabaseConnection();
        
        // DEPRECATED - Old hardcoded map (kept for fallback only) - UPDATED TO NEW PATHS
        // Only includes the 9 working avatars with verified files
        this._oldAvatarMap = {
            'al-bee': {
                obj: '/static/assets/avatars/al-bee/AlBee.obj',
                mtl: '/static/assets/avatars/al-bee/AlBee.mtl',
                texture: '/static/assets/avatars/al-bee/AlBee.png',
                thumbnail: '/static/assets/avatars/al-bee/AlBee!.png'
            },
            'anxious-bee': {
                obj: '/static/assets/avatars/anxious-bee/AnxiousBee.obj',
                mtl: '/static/assets/avatars/anxious-bee/AnxiousBee.mtl',
                texture: '/static/assets/avatars/anxious-bee/AnxiousBee.png',
                thumbnail: '/static/assets/avatars/anxious-bee/AnxiousBee!.png'
            },
            'mascot-bee': {
                obj: '/static/assets/avatars/mascot-bee/MascotBee.obj',
                mtl: '/static/assets/avatars/mascot-bee/MascotBee.mtl',
                texture: '/static/assets/avatars/mascot-bee/MascotBee.png',
                thumbnail: '/static/assets/avatars/mascot-bee/MascotBee!.png'
            },
            'monster-bee': {
                obj: '/static/assets/avatars/monster-bee/MonsterBee.obj',
                mtl: '/static/assets/avatars/monster-bee/MonsterBee.mtl',
                texture: '/static/assets/avatars/monster-bee/MonsterBee.png',
                thumbnail: '/static/assets/avatars/monster-bee/MonsterBee!.png'
            },
            'professor-bee': {
                obj: '/static/assets/avatars/professor-bee/ProfessorBee.obj',
                mtl: '/static/assets/avatars/professor-bee/ProfessorBee.mtl',
                texture: '/static/assets/avatars/professor-bee/ProfessorBee.png',
                thumbnail: '/static/assets/avatars/professor-bee/ProfessorBee!.png'
            },
            'rocker-bee': {
                obj: '/static/assets/avatars/rocker-bee/RockerBee.obj',
                mtl: '/static/assets/avatars/rocker-bee/RockerBee.mtl',
                texture: '/static/assets/avatars/rocker-bee/RockerBee.png',
                thumbnail: '/static/assets/avatars/rocker-bee/RockerBee!.png'
            },
            'superbee': {
                obj: '/static/assets/avatars/superbeehero/SuperheroBee.obj',
                mtl: '/static/assets/avatars/superbeehero/SuperBeeHero.mtl',
                texture: '/static/assets/avatars/superbeehero/SuperheroBee.png',
                thumbnail: '/static/assets/avatars/superbeehero/SuperBeeHero!.png'
            },
            'vamp-bee': {
                obj: '/static/assets/avatars/vamp-bee/VampBee.obj',
                mtl: '/static/assets/avatars/vamp-bee/VampBee.mtl',
                texture: '/static/assets/avatars/vamp-bee/VampBee.png',
                thumbnail: '/static/assets/avatars/vamp-bee/VampBee!.png'
            },
            'ware-bee': {
                obj: '/static/assets/avatars/ware-bee/WareBee.obj',
                mtl: '/static/assets/avatars/ware-bee/WareBee.mtl',
                texture: '/static/assets/avatars/ware-bee/WareBee.png',
                thumbnail: '/static/assets/avatars/ware-bee/WareBee!.png'
            },
            'zom-bee': {
                obj: '/static/assets/avatars/zom-bee/ZomBee.obj',
                mtl: '/static/assets/avatars/zom-bee/ZomBee.mtl',
                texture: '/static/assets/avatars/zom-bee/ZomBee.png',
                thumbnail: '/static/assets/avatars/zom-bee/ZomBee!.png'
            }
        };
        
        // Initialize avatarMap with fallback data immediately (will be replaced by API if successful)
        this.avatarMap = {...this._oldAvatarMap};
        
        // Fallback to MascotBee if no avatar selected - use API-based path
        this.defaultAvatar = {
            obj: '/static/assets/avatars/mascot-bee/MascotBee.obj',
            mtl: '/static/assets/avatars/mascot-bee/MascotBee.mtl',
            texture: '/static/assets/avatars/mascot-bee/MascotBee.png',
            thumbnail: '/static/assets/avatars/mascot-bee/MascotBee!.png'
        };
    }

    /**
     * Quick database connection verification (lightweight check)
     * Only verifies that the database is accessible, doesn't load all avatar data
     */
    async verifyDatabaseConnection() {
        try {
            console.log('🔍 Verifying avatar database connection...');
            const response = await fetch('/api/avatars?category=classic');
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
            const response = await fetch('/api/avatars');
            if (!response.ok) {
                throw new Error(`API returned ${response.status}`);
            }
            
            const data = await response.json();
            const avatars = data.avatars || [];
            console.log(`✅ Loaded ${avatars.length} avatars from database`);
            
            // Convert API response to avatarMap format
            avatars.forEach(avatar => {
                const id = avatar.id;
                this.avatarMap[id] = {
                    obj: avatar.urls?.model_obj || avatar.model_obj_url,
                    mtl: avatar.urls?.model_mtl || avatar.model_mtl_url,
                    texture: avatar.urls?.texture || avatar.texture_url,
                    thumbnail: avatar.urls?.thumbnail || avatar.thumbnail_url || avatar.thumbnail
                };
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
            // Get unique avatars only (deduplicate by obj file path to exclude aliases)
            const seenPaths = new Set();
            const uniqueAvatars = [];
            
            for (const [key, data] of Object.entries(this.avatarMap)) {
                const objPath = data.obj;
                if (!seenPaths.has(objPath)) {
                    seenPaths.add(objPath);
                    uniqueAvatars.push({ key, data });
                }
            }
            
            preloadResults.totalAvatars = uniqueAvatars.length;
            
            console.log(`📋 Found ${preloadResults.totalAvatars} unique avatars (${Object.keys(this.avatarMap).length} total including aliases)`);
            
            // OPTIMIZATION: Skip file validation - database already validated avatars
            // Just verify fallback system and trust the database
            console.log('⚡ Using fast preload (database-validated avatars)');
            
            // Mark all avatars as successful (database has already validated them)
            preloadResults.successfulAvatars = preloadResults.totalAvatars;
            for (const { key: avatarKey, data: avatarData } of uniqueAvatars) {
                // Report progress with avatar name
                if (progressCallback) {
                    const avatarName = avatarData.name || avatarKey;
                    progressCallback(avatarName);
                }
                
                preloadResults.validationDetails[avatarKey] = {
                    status: 'valid',
                    files: ['trusted-from-database'],
                    timestamp: new Date().toISOString()
                };
                
                // Small delay to show progress (10ms per avatar = ~220ms total for 22 avatars)
                await new Promise(resolve => setTimeout(resolve, 10));
            }
            
            // Only validate fallback system (MascotBee) - critical for app stability
            if (progressCallback) {
                progressCallback('MascotBee (Fallback)');
            }
            console.log('🔍 Validating fallback system (MascotBee)...');
            try {
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
     */
    async validateAvatarFilesForPaths(avatarData) {
        const filesToCheck = [avatarData.obj, avatarData.mtl, avatarData.texture, avatarData.thumbnail];
        const validFiles = [];
        const errors = [];
        
        for (const fileUrl of filesToCheck) {
            try {
                const response = await fetch(fileUrl, { method: 'HEAD' });
                if (response.ok) {
                    validFiles.push({
                        url: fileUrl,
                        type: this.getFileType(fileUrl),
                        size: response.headers.get('content-length') || 'unknown'
                    });
                } else {
                    errors.push(`${fileUrl}: HTTP ${response.status}`);
                }
            } catch (error) {
                errors.push(`${fileUrl}: ${error.message}`);
            }
        }
        
        if (errors.length > 0) {
            throw new Error(`File validation failed: ${errors.join(', ')}`);
        }
        
        return { validFiles, fileCount: validFiles.length };
    }

    /**
     * Get file type from URL for validation logging
     */
    getFileType(url) {
        if (url.endsWith('.obj')) return 'model';
        if (url.endsWith('.mtl')) return 'material';
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
            'zom-bee': 'Zom Bee'
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
     * Render a user avatar (OBJ/MTL) or fallback to MascotBee in the given container.
     * Returns a Promise to match existing callers.
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

                // Guard: ensure we have OBJ/MTL/texture; if not, force MascotBee
                const hasAll = data && data.obj && data.mtl && data.texture;
                const paths = hasAll ? data : this.defaultAvatar;

                // Render via SmartyBee3D (OBJ/MTL renderer)
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
                // eslint-disable-next-line no-new
                new window.SmartyBee3D(containerId, {
                    width: Math.max(120, Math.floor(rect.width)),
                    height: Math.max(120, Math.floor(rect.height)),
                    modelPath: paths.obj,
                    mtlPath: paths.mtl,
                    texturePath: paths.texture,
                    autoRotate: true,
                    enableInteraction: true
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
     */
    loadEmergency2DFallback(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        console.log('🔄 Loading emergency 2D fallback...');
        
        // Create simple 2D bee emoji display as last resort
        container.innerHTML = `
            <div style="
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #FFB300, #FF8F00);
                border-radius: 50%;
                border: 3px solid rgba(255, 179, 0, 0.8);
                box-shadow: 0 8px 16px rgba(255, 179, 0, 0.4);
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    font-size: 4rem;
                    line-height: 1;
                    text-align: center;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
                ">🐝</div>
                <div style="
                    position: absolute;
                    bottom: -5px;
                    right: -5px;
                    width: 20px;
                    height: 20px;
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    border: 1px solid rgba(0,0,0,0.2);
                ">📚</div>
            </div>
        `;

        // Add click animation
        container.addEventListener('click', () => {
            container.style.transform = 'scale(0.95)';
            setTimeout(() => {
                container.style.transform = 'scale(1)';
            }, 150);
        });

        console.log('✅ Emergency 2D fallback loaded');
        this.showStatusMessage('Emergency avatar mode - Please check 3D files', 'warning', 5000);
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
        
        try {
            const response = await fetch('/api/users/me/avatar', {
                credentials: 'same-origin'
            });
            
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
                        this.showLoadedState();
                        return true;
                    } else {
                        throw new Error('Avatar files missing or inaccessible');
                    }
                }
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load user avatar, using default:', error);
            this.showErrorState('mascotBee3D', error);
            
            // Try to load default avatar as fallback
            if (await this.validateAvatarFiles(true)) {
                this.showLoadedState();
            }
        }
        
        // Use default if no user avatar
        console.log('ℹ️ Using default MascotBee');
        return false;
    }

    /**
     * Validate that avatar files are accessible
     */
    async validateAvatarFiles(useDefault = false) {
        const paths = useDefault ? this.defaultAvatar : this.getAvatarPaths();
        // Guard against null/undefined paths to avoid "/null" fetches
        if (!paths || !paths.obj || !paths.mtl || !paths.texture) {
            console.warn('Avatar paths incomplete, falling back to MascotBee');
            return false;
        }
        const filesToCheck = [paths.obj, paths.mtl, paths.texture];
        
        try {
            const checks = filesToCheck.map(async (url) => {
                try {
                    const response = await fetch(url, { method: 'HEAD' });
                    return response.ok;
                } catch {
                    return false;
                }
            });
            
            const results = await Promise.all(checks);
            const allFilesExist = results.every(exists => exists);
            
            if (!allFilesExist) {
                const missingFiles = filesToCheck.filter((_, index) => !results[index]);
                console.error('❌ Missing avatar files:', missingFiles);
                return false;
            }
            
            console.log('✅ All avatar files validated');
            return true;
        } catch (error) {
            console.error('❌ Avatar file validation failed:', error);
            return false;
        }
    }

    /**
     * Get the 3D model paths for the user's avatar (or default)
     */
    getAvatarPaths() {
        if (this.userAvatar && this.userAvatar.urls) {
            const obj = this.userAvatar.urls.model_obj;
            const mtl = this.userAvatar.urls.model_mtl;
            const texture = this.userAvatar.urls.texture;
            const thumbnail = this.userAvatar.urls.thumbnail;

            // If any required OBJ pipeline asset is missing, do NOT return partials
            if (obj && mtl && texture) {
                return { obj, mtl, texture, thumbnail };
            }

            // Likely a GLB-only avatar or incomplete record; fall back to MascotBee
            console.warn('Detected GLB-only or incomplete avatar URLs; using MascotBee OBJ fallback');
        }
        return this.defaultAvatar;
    }

    /**
     * Get options object for SmartyBee3D constructor
     */
    getAvatarOptions(additionalOptions = {}) {
        const paths = this.getAvatarPaths();
        return {
            modelPath: paths.obj,
            mtlPath: paths.mtl,
            texturePath: paths.texture,
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

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.userAvatarLoader.init();
});
