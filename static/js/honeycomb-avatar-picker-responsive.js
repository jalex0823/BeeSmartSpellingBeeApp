/**
 * Responsive Honeycomb Avatar Picker
 * No absolute positioning - uses CSS Grid
 * Enhanced with real-time 3D model loading progress
 */

let avatarsData = [];
// Server-provided list of avatar ids/slugs that have been purchased by the current user
let purchasedAvatarIds = [];
let selectedAvatar = null;
let loadedThumbnails = 0;
let totalThumbnails = 0;
let failedThumbnails = 0; // Track failed thumbnail loads
let pendingThumbnails = new Set(); // Track thumbnails that haven't completed loading
let currentLoadingAvatar = null;
let previewLoadProgress = 0;
// Current user's honey points from API
let currentUserHoneyPoints = 0;
// Bundle catalog for bundle shop modal
let bundlesData = [];
// 3D viewer state to support zoom/rotate/reset controls
const avatarViewerState = {
    scene: null,
    camera: null,
    renderer: null,
    model: null,
    containerId: null,
    default: {
        cameraPos: { x: 0, y: 0.5, z: 3.5 },
        modelRotationY: 0,
        modelScale: 1,
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🐝 BeeSmart Avatar Picker - Initializing...');
    console.log('THREE available:', typeof THREE !== 'undefined');
    console.log('GLTFLoader available:', typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined');
    console.log('DRACOLoader available:', typeof THREE !== 'undefined' && typeof THREE.DRACOLoader !== 'undefined');
    
    // CRITICAL: Verify user authentication FIRST during loading screen
    await verifyUserAuthentication();
    // Apply initial role-based UI before heavy loading
    applyRoleBasedUI();

    // If the native IAP bridge is missing/late (common in TestFlight),
    // native-iap-bridge.js will do a server reconcile and emit events.
    // Listen and refresh avatars so locks/unlocks update immediately.
    (function installIapRefreshListeners() {
        try {
            if (window.__beesmartAvatarIapListenersInstalled) return;
            window.__beesmartAvatarIapListenersInstalled = true;

            let refreshTimer = null;
            const scheduleRefresh = function(reason) {
                try {
                    if (refreshTimer) clearTimeout(refreshTimer);
                } catch (e) { /* ignore */ }
                refreshTimer = setTimeout(async function() {
                    try {
                        console.log('🔄 IAP event refresh avatars:', reason);
                        await loadAvatars();
                    } catch (e) {
                        // Non-fatal: avoid breaking the avatar page if refresh fails.
                        console.warn('🐞 IAP-triggered avatar refresh failed:', e);
                    }
                }, 350);
            };

            window.addEventListener('beesmart:iap-reconciled', function(ev) {
                const ok = ev && ev.detail ? ev.detail.ok : null;
                scheduleRefresh('iap-reconciled' + (ok === false ? ':fail' : ''));
            });
            window.addEventListener('beesmart:iap-ready', function(ev) {
                const platform = ev && ev.detail ? ev.detail.platform : null;
                scheduleRefresh('iap-ready' + (platform ? ':' + platform : ''));
            });
        } catch (e) { /* ignore */ }
    })();
    
    loadAvatars();
    setupSearchFilter();
    setupBundleShop();

    // Safety: hide loading overlay after 10s even if some thumbnails stall
    setTimeout(() => {
        const overlay = document.getElementById('avatar-loading-overlay');
        if (overlay && !overlay.classList.contains('hidden')) {
            console.warn('⚠️ Hiding loading overlay due to timeout safeguard');
            overlay.classList.add('hidden');
        }
    }, 10000);
});

// Verify user authentication before loading avatars
async function verifyUserAuthentication() {
    const loadingDetail = document.getElementById('loading-detail');
    
    try {
        if (loadingDetail) {
            loadingDetail.textContent = '🔐 Verifying authentication...';
        }
        
        console.log('🔐 AUTHENTICATION CHECK: Starting verification...');
        
        // Check if user data was passed from template
        const templateUserData = window.user_data || {};
        console.log('📋 Template user_data:', templateUserData);
        
        // Fetch fresh user session status from server
        // iOS/Safari compatible fetch with proper credentials and headers
        const response = await fetch('/api/user/session', { 
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-cache',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (response.ok) {
            const sessionData = await response.json();
            console.log('✅ Session data received:', sessionData);
            
            // Store for later use
            window.userSessionData = sessionData;
            
            if (loadingDetail) {
                if (sessionData.authenticated) {
                    loadingDetail.textContent = `✅ Authenticated as ${sessionData.username || 'user'}`;
                } else {
                    loadingDetail.textContent = '👋 Guest mode - Register to unlock more bees!';
                }
            }
        } else {
            console.warn('⚠️ Could not fetch session data, proceeding with template data');
            if (loadingDetail) {
                loadingDetail.textContent = 'Proceeding with cached credentials...';
            }
        }
        
        // Brief delay so user sees the auth check (iOS-safe timing)
        await new Promise(resolve => setTimeout(resolve, 300));
        
    } catch (error) {
        console.error('❌ Authentication verification failed:', error);
        if (loadingDetail) {
            loadingDetail.textContent = 'Initializing...';
        }
    }
}

// Apply role-based UI consistency at avatar loading screen
function applyRoleBasedUI() {
    try {
        const session = window.userSessionData || {};
        const userInfo = window.avatarUserInfo || {};
        const isAuthenticated = !!(session.authenticated || userInfo.user_authenticated);
        const isAdmin = !!(session.is_admin || userInfo.is_admin || (session.role === 'admin') || (userInfo.user_role === 'admin'));
        const isGuest = !!(session.is_guest || userInfo.is_guest);

        // Expose simple flags globally for other scripts
        window.isUserLoggedIn = isAuthenticated;
        window.isUserAdmin = isAdmin;
        window.isUserGuest = isGuest && !isAdmin && !isAuthenticated ? true : false;

        // Toggle any admin-only UI elements
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = isAdmin ? '' : 'none';
        });

        // Toggle any authenticated-only UI elements
        document.querySelectorAll('.auth-only').forEach(el => {
            el.style.display = isAuthenticated ? '' : 'none';
        });

        // Toggle any guest-only hints
        document.querySelectorAll('.guest-only').forEach(el => {
            el.style.display = window.isUserGuest ? '' : 'none';
        });

        // Admin Portal badge in header (if present)
        const adminBadge = document.getElementById('admin-portal-badge');
        if (adminBadge) {
            adminBadge.classList.toggle('hidden', !isAdmin);
        }

        // Loading overlay detail line reflects role
        const loadingDetail = document.getElementById('loading-detail');
        if (loadingDetail) {
            if (isAdmin) {
                loadingDetail.textContent = `✅ Admin access confirmed for ${session.username || 'admin'}`;
            } else if (isAuthenticated) {
                loadingDetail.textContent = `✅ Authenticated as ${session.username || 'user'}`;
            } else if (window.isUserGuest) {
                loadingDetail.textContent = '👋 Guest mode - Register to unlock more bees!';
            }
        }
    } catch (e) {
        console.warn('⚠️ Failed to apply role-based UI:', e);
    }
}

// Update loading progress with detailed status
function updateLoadingProgress(customMessage = null) {
    // Calculate percentage based on completed thumbnails (loaded + failed)
    const completedThumbnails = loadedThumbnails + failedThumbnails;
    const percentage = Math.round((completedThumbnails / totalThumbnails) * 100);
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
            const completed = loadedThumbnails + failedThumbnails;
            if (failedThumbnails > 0) {
                loadingDetail.textContent = `${loadedThumbnails} loaded, ${failedThumbnails} failed (${completed}/${totalThumbnails} processed)`;
            } else {
                loadingDetail.textContent = `${loadedThumbnails} of ${totalThumbnails} avatars loaded`;
            }
        } else {
            if (failedThumbnails > 0) {
                loadingDetail.textContent = `Ready! (${failedThumbnails} avatar${failedThumbnails > 1 ? 's' : ''} using fallback)`;
            } else {
                loadingDetail.textContent = 'Ready to choose your bee!';
            }
        }
    }
    
    console.log(`📊 Loading Progress: ${percentage}% (${loadedThumbnails}/${totalThumbnails})`);
    
    // Hide overlay when complete (all thumbnails loaded OR failed)
    const completedThumbnails = loadedThumbnails + failedThumbnails;
    if (completedThumbnails >= totalThumbnails && totalThumbnails > 0) {
        if (failedThumbnails > 0) {
            console.warn(`⚠️ ${failedThumbnails} thumbnail(s) failed to load, but proceeding...`);
        }
        console.log(`✅ All thumbnails processed (${loadedThumbnails} loaded, ${failedThumbnails} failed)! Hiding overlay...`);
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
        <div id="preview-loading-overlay" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255, 255, 255, 0.95); z-index: 10; transition: opacity 0.5s ease;">
            <div style="font-size: 3rem; animation: bounce 1s infinite;">🐝</div>
            <div style="margin-top: 1rem; font-size: 1.2rem; color: #5A2C15; font-weight: 600;">Loading ${avatarName}...</div>
            <div style="width: 80%; height: 8px; background: rgba(90, 44, 21, 0.2); border-radius: 4px; margin-top: 1rem; overflow: hidden;">
                <div id="preview-load-progress" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FF8C00, #FF6B00); transition: width 0.3s;"></div>
            </div>
            <div id="preview-load-text" style="margin-top: 0.5rem; font-size: 0.9rem; color: #5A2C15; font-weight: 500;">0%</div>
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
    
    // Fade out loading overlay when reaching 100%
    if (percentage >= 100) {
        const overlay = document.getElementById('preview-loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                if (overlay && overlay.parentNode) {
                    overlay.remove();
                }
            }, 500);
        }
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
                var aMatch = a.unlock_message ? a.unlock_message.match(/\d+/) : null;
                var aPoints = parseInt((aMatch && aMatch[0]) ? aMatch[0] : '999999');
                var bMatch = b.unlock_message ? b.unlock_message.match(/\d+/) : null;
                var bPoints = parseInt((bMatch && bMatch[0]) ? bMatch[0] : '999999');
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
        // Add timestamp to bypass stale cache + force=1 for server-side cache bypass
        const timestamp = new Date().getTime();
        // iOS/Safari compatible fetch with explicit headers
        const response = await fetch(`/api/avatars?force=1&t=${timestamp}`, { 
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-cache',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
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
        
        // Store user info globally for chooseAvatar to check admin/guest status
        // CRITICAL FIX: API returns data.user.{field}, not data.{field}
        const userData = data.user || {};
        window.avatarUserInfo = {
            is_guest: userData.is_guest || false,
            is_admin: userData.is_admin || false,
            user_role: userData.role || null,
            user_authenticated: userData.is_authenticated || false,  // From data.user.is_authenticated
            purchased_avatars: data.purchased_avatars || userData.purchased_avatars || []  // CRITICAL: Avatar unlock gate
        };
        console.log('👤 User Info:', window.avatarUserInfo);
        // Re-apply role UI with fresh data from avatars API
        applyRoleBasedUI();
        
        // Capture current user's honey points from data.user.honey_points
        if (userData && typeof userData.honey_points === 'number') {
            currentUserHoneyPoints = userData.honey_points;
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
        
        console.log('📦 Raw API avatars count:', apiAvatars.length);
        if (apiAvatars.length > 0) {
            console.log('📦 Sample avatar structure:', JSON.stringify(apiAvatars[0], null, 2));
        }
        
        // Capture purchased avatar ids so the grid can distinguish Purchased (Owned) vs Earned (Unlocked)
        try {
            purchasedAvatarIds = Array.isArray(data && data.purchased_avatars)
                ? data.purchased_avatars.map(x => String(x || '').toLowerCase())
                : [];
        } catch (e) {
            purchasedAvatarIds = [];
        }

        const rawAvatars = apiAvatars.map(avatar => {
            // Extract GLB URL from standard urls.glb field (all avatars are now GLB-only)
            var urlsObj = (avatar && typeof avatar.urls === 'object') ? avatar.urls : {};
            var glbUrl = urlsObj.glb;
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
                thumbnail: (avatar.urls && avatar.urls.thumbnail) || avatar.thumbnail || avatar.thumbnail_url || null,
                // NEW: Lock status from monetization system
                is_locked: avatar.is_locked || false,
                unlock_message: avatar.unlock_message || '',
                // NEW: Numeric unlock info for computing remaining points
                unlock_points: (typeof avatar.unlock_points === 'number')
                    ? avatar.unlock_points
                    : ((typeof avatar.unlock_requirement === 'number') ? avatar.unlock_requirement : null),
                tier: avatar.tier || null,
                price: (typeof avatar.price === 'number')
                    ? avatar.price
                    : ((typeof avatar.price_usd === 'number') ? avatar.price_usd : null),
                // NEW: In-app purchase product id / SKU (server-provided)
                product_id: avatar.product_id || null,
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
        failedThumbnails = 0;
        pendingThumbnails.clear();
        
    console.log('Loaded avatars:', avatarsData.length);
    updateDynamicMarquee(avatarsData);
    renderAvatarGrid();
    
    // Always show mascot bee (honey-comb) by default in the viewer
    setTimeout(() => {
        const mascotSlugs = ['honey-comb', 'honeycomb', 'mascot-bee', 'mascotbee'];
        let defaultAvatar = null;
        
        // Try to find mascot bee by slug
        for (const slug of mascotSlugs) {
            defaultAvatar = avatarsData.find(a => 
                (a.slug || '').toLowerCase() === slug.toLowerCase()
            );
            if (defaultAvatar) break;
        }
        
        // If no mascot found, use first unlocked avatar, or first avatar if all locked
        if (!defaultAvatar) {
            defaultAvatar = avatarsData.find(a => !a.is_locked) || avatarsData[0];
        }
        
        if (defaultAvatar) {
            console.log('🐝 Loading default avatar in viewer:', defaultAvatar.name);
            const avatarElement = document.querySelector(`.avatar-hex-position[data-slug="${defaultAvatar.slug}"]`);
            if (avatarElement) {
                selectAvatar(defaultAvatar, avatarElement);
            } else {
                // If element not found yet, update preview directly
                updatePreview(defaultAvatar);
            }
        }
    }, 300); // Small delay to ensure grid is rendered
    
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
                name: (a && a.name) ? a.name : slug,
                slug: (a && a.slug) ? a.slug : slug,
                description: (a && a.description) ? a.description : '',
                thumbnail: (a && a.thumbnail) ? a.thumbnail : ''
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

    // Optional status label (small, below thumbnail)
    // - Locked purchasable: "Buy $X.XX"
    // - Unlocked (but purchasable tier): "Unlocked"
    // NOTE: We do NOT show "Owned" unless the API gives an explicit entitlement flag.
    const label = getAvatarGridStatusLabel(avatar);
    let priceDiv = null;
    if (label) {
        priceDiv = document.createElement('div');
        priceDiv.className = 'avatar-hex-price';
        priceDiv.textContent = label;
        priceDiv.title = label.startsWith('Buy ') ? 'In-app purchase price' : '';
    }
    
    div.appendChild(checkmark);
    div.appendChild(thumbDiv);
    if (priceDiv) div.appendChild(priceDiv);
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
        const avatarId = avatar.id || avatar.name;
        pendingThumbnails.add(avatarId); // Track this thumbnail as pending
        
        // Set timeout to handle thumbnails that never load (10 seconds per avatar)
        const loadTimeout = setTimeout(() => {
            if (pendingThumbnails.has(avatarId)) {
                console.warn(`⏱️ Thumbnail load timeout for ${avatar.name} after 10s`);
                pendingThumbnails.delete(avatarId);
                thumbDiv.classList.remove('loading');
                thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
                failedThumbnails++;
                updateLoadingProgress();
            }
        }, 10000);
        
        img.src = fallbackCandidates[candidateIdx];
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        // Remove border-radius, hexagon shape is handled by CSS clip-path
        
        // Track loading progress
        img.onload = () => {
            clearTimeout(loadTimeout);
            if (pendingThumbnails.has(avatarId)) {
                pendingThumbnails.delete(avatarId);
                thumbDiv.classList.remove('loading');
                loadedThumbnails++;
                updateLoadingProgress();
            }
        };
        
        img.onerror = () => {
            // Try next fallback if available
            candidateIdx++;
            if (candidateIdx < fallbackCandidates.length) {
                const next = fallbackCandidates[candidateIdx];
                console.warn(`⚠️ Thumbnail failed for ${avatar.name}, retrying with fallback: ${next}`);
                img.src = next;
                return; // Don't mark as failed yet, try next fallback
            }
            // All fallbacks exhausted - log detailed error info
            clearTimeout(loadTimeout);
            if (pendingThumbnails.has(avatarId)) {
                pendingThumbnails.delete(avatarId);
                console.error(`❌ Failed to load thumbnail for "${avatar.name}" (ID: ${avatar.id})`);
                console.error(`   Attempted URLs:`, fallbackCandidates);
                console.error(`   Avatar data:`, {
                    id: avatar.id,
                    name: avatar.name,
                    thumbnail: avatar.thumbnail,
                    urls: avatar.urls,
                    glb: avatar.glb_url
                });
                thumbDiv.classList.remove('loading');
                thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
                failedThumbnails++;
                updateLoadingProgress();
            }
        };
        
        thumbDiv.appendChild(img);
    } else {
        // Fallback to emoji if no thumbnail
        console.warn(`⚠️ No thumbnail URL provided for ${avatar.name}`);
        thumbDiv.classList.remove('loading');
        thumbDiv.innerHTML = '<div style="color: #FFD700; font-size: 3rem;">🐝</div>';
        failedThumbnails++; // Count as failed since no thumbnail was provided
        updateLoadingProgress();
    }
    
    return div;
}

function isPurchasableTier(avatar) {
    const tier = (avatar && avatar.tier) ? String(avatar.tier).toLowerCase().trim() : '';
    return tier === 'premium' || tier === 'earn_or_buy';
}

function getAvatarDisplayPrice(avatar) {
    if (!avatar) return null;
    if (typeof avatar.price === 'number') return avatar.price;
    if (typeof avatar.price_usd === 'number') return avatar.price_usd;
    return null;
}

function getAvatarGridStatusLabel(avatar) {
    if (!avatar) return null;
    if (!isPurchasableTier(avatar)) return null;

    // Locked purchasable avatars should show their price so kids/parents know the cost.
    if (avatar.is_locked) {
        const price = getAvatarDisplayPrice(avatar);
        if (price == null) return null;
        return `Buy $${Number(price).toFixed(2)}`;
    }

    // Unlocked purchasable-tier avatars: distinguish Purchased vs Earned.
    if (isAvatarPurchased(avatar)) return 'Owned';
    return 'Unlocked';
}

function isAvatarPurchased(avatar) {
    const slug = (avatar && avatar.slug) ? String(avatar.slug).toLowerCase() : '';
    if (!slug) return false;
    return Array.isArray(purchasedAvatarIds) && purchasedAvatarIds.includes(slug);
}

// Build a minimal, stable set of thumbnail candidates (server now provides robust URLs)
function buildThumbnailFallbacks(avatar, initialUrl) {
    const candidates = [];
    if (initialUrl) {
        // Add the original URL
        candidates.push(initialUrl);
        
        // Handle URL encoding: if URL has %21, also try with !
        if (initialUrl.includes('%21')) {
            candidates.push(initialUrl.replace(/%21/g, '!'));
        }
        // Handle literal !: if URL has !, also try with %21
        else if (initialUrl.includes('!')) {
            candidates.push(initialUrl.replace(/!/g, '%21'));
        }
        
        // If we have a GLB URL, derive thumbnail from it as fallback
        if (avatar.glb_url) {
            try {
                // Extract GLB filename and derive thumbnail path
                const glbMatch = avatar.glb_url.match(/\/([^\/]+\.glb)/);
                if (glbMatch) {
                    const glbFilename = glbMatch[1];
                    const baseName = glbFilename.replace(/\.glb$/i, '');
                    const derivedThumb = `/static/assets/avatars/glb_files/AvatarThumbnails/${baseName}!.png`;
                    if (!candidates.includes(derivedThumb)) {
                        candidates.push(derivedThumb);
                    }
                }
            } catch (e) {
                console.warn('Failed to derive thumbnail from GLB URL:', e);
            }
        }
    }
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
    // Save viewer state for controls
    avatarViewerState.scene = scene;
    avatarViewerState.camera = camera;
    avatarViewerState.renderer = renderer;
    avatarViewerState.containerId = containerId;
    
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
            // Save model in viewer state
            avatarViewerState.model = model;
            avatarViewerState.default.modelRotationY = 0;
            avatarViewerState.default.modelScale = scale;
            
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
            avatarViewerState.default.cameraPos = { x: 0, y: 0.5, z: 3.5 };
            // Enable controls UI now that model is ready
            enablePreviewControls(true);
            
            // Add touch gesture support for mobile
            setupTouchGestures(renderer.domElement, camera, model);
            
            // Animation loop with auto-rotation (only if enabled)
            function animate() {
                requestAnimationFrame(animate);
                // Only auto-rotate if state says so
                if (avatarViewerState.autoRotate !== false) {
                    model.rotation.y += 0.003; // Slow rotation to show all angles
                }
                renderer.render(scene, camera);
            }
            animate();
            
            // Final update - fade out loading indicator
            setTimeout(() => {
                updatePreviewProgress(100, 'Complete!');
                // The fade-out is handled in updatePreviewProgress when percentage >= 100
                console.log('✅ Loading indicator fading out');
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
            // Disable controls UI in fallback
            enablePreviewControls(false);
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
        // Ensure control bar exists
        ensureControlsToolbar(previewContent);
        setTimeout(loadPreview, 100);
    }
}

// Ensure controls toolbar exists in preview panel
function ensureControlsToolbar(previewContent) {
    let toolbar = previewContent.querySelector('.preview-controls');
    if (!toolbar) {
        toolbar = document.createElement('div');
        toolbar.className = 'preview-controls';
        toolbar.style.cssText = 'display:flex; gap:0.5rem; align-items:center; justify-content:center; margin-top:0.5rem; flex-wrap: wrap;';
        toolbar.innerHTML = `
            <button class="ctrl-btn" id="ctrl-auto-rotate" title="Auto-Rotate (Spacebar)" aria-label="Toggle auto-rotate">🔄</button>
            <div style="width: 1px; height: 24px; background: rgba(255,215,0,0.3);"></div>
            <button class="ctrl-btn" id="ctrl-zoom-in" title="Zoom In (+)" aria-label="Zoom in">🔍＋</button>
            <button class="ctrl-btn" id="ctrl-zoom-out" title="Zoom Out (-)" aria-label="Zoom out">🔍－</button>
            <div style="width: 1px; height: 24px; background: rgba(255,215,0,0.3);"></div>
            <button class="ctrl-btn" id="ctrl-rotate-left" title="Rotate Left (←)" aria-label="Rotate left">⟲</button>
            <button class="ctrl-btn" id="ctrl-rotate-right" title="Rotate Right (→)" aria-label="Rotate right">⟳</button>
            <div style="width: 1px; height: 24px; background: rgba(255,215,0,0.3);"></div>
            <button class="ctrl-btn" id="ctrl-reset" title="Reset View (R)" aria-label="Reset view">↺</button>
        `;
        const descEl = previewContent.querySelector('.preview-description');
        if (descEl && descEl.parentNode) {
            descEl.parentNode.insertBefore(toolbar, descEl.nextSibling);
        } else {
            previewContent.appendChild(toolbar);
        }
        bindControls(toolbar);
    }
}

// Enable/disable controls UI
function enablePreviewControls(enabled) {
    document.querySelectorAll('.preview-controls .ctrl-btn').forEach(btn => {
        btn.disabled = !enabled;
        btn.style.opacity = enabled ? '1' : '0.5';
        btn.style.cursor = enabled ? 'pointer' : 'not-allowed';
    });
}

// Setup touch gestures for mobile interaction
function setupTouchGestures(canvas, camera, model) {
    if (!canvas || !camera || !model) return;
    
    let touchStartDistance = 0;
    let touchStartRotation = 0;
    let lastTouchX = 0;
    let lastTouchY = 0;
    let isTouching = false;
    
    // Handle touch start
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isTouching = true;
        
        if (e.touches.length === 1) {
            // Single touch - prepare for rotation
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
            touchStartRotation = model.rotation.y;
            
            // Disable auto-rotate during manual interaction
            if (avatarViewerState.autoRotate !== false) {
                avatarViewerState.wasAutoRotating = true;
                avatarViewerState.autoRotate = false;
            }
        } else if (e.touches.length === 2) {
            // Two finger touch - prepare for pinch zoom
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            touchStartDistance = Math.sqrt(dx * dx + dy * dy);
        }
    }, { passive: false });
    
    // Handle touch move
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        
        if (e.touches.length === 1) {
            // Single touch - rotate model
            const deltaX = e.touches[0].clientX - lastTouchX;
            model.rotation.y += deltaX * 0.01;
            
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
        } else if (e.touches.length === 2) {
            // Two finger touch - pinch to zoom
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (touchStartDistance > 0) {
                const scale = distance / touchStartDistance;
                const newZ = camera.position.z / scale;
                camera.position.z = Math.max(0.8, Math.min(10, newZ));
                touchStartDistance = distance;
            }
        }
    }, { passive: false });
    
    // Handle touch end
    canvas.addEventListener('touchend', (e) => {
        if (e.touches.length === 0) {
            isTouching = false;
            touchStartDistance = 0;
            
            // Re-enable auto-rotate if it was on before
            if (avatarViewerState.wasAutoRotating) {
                setTimeout(() => {
                    avatarViewerState.autoRotate = true;
                    avatarViewerState.wasAutoRotating = false;
                }, 1000); // Resume after 1 second of no touch
            }
        } else if (e.touches.length === 1) {
            // Switched from two fingers to one
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
            touchStartDistance = 0;
        }
    }, { passive: false });
    
    // Prevent context menu on long press
    canvas.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });
}

// Bind control handlers with smooth animations and keyboard support
function bindControls(toolbar) {
    const zoomIn = toolbar.querySelector('#ctrl-zoom-in');
    const zoomOut = toolbar.querySelector('#ctrl-zoom-out');
    const rotLeft = toolbar.querySelector('#ctrl-rotate-left');
    const rotRight = toolbar.querySelector('#ctrl-rotate-right');
    const resetBtn = toolbar.querySelector('#ctrl-reset');
    const autoRotateBtn = toolbar.querySelector('#ctrl-auto-rotate');

    const zoomStep = 0.3; // move camera closer/farther
    const rotStep = 0.15; // radians per click
    
    // State for smooth animations
    let animationFrame = null;
    let targetCameraZ = null;
    let targetRotationY = null;
    let isAutoRotating = false;
    
    // Smooth camera zoom animation
    function smoothZoom(targetZ) {
        if (animationFrame) cancelAnimationFrame(animationFrame);
        targetCameraZ = targetZ;
        
        function animate() {
            const cam = avatarViewerState.camera;
            if (!cam || targetCameraZ === null) return;
            
            const diff = targetCameraZ - cam.position.z;
            if (Math.abs(diff) > 0.01) {
                cam.position.z += diff * 0.15; // Smooth easing
                animationFrame = requestAnimationFrame(animate);
            } else {
                cam.position.z = targetCameraZ;
                targetCameraZ = null;
            }
        }
        animate();
    }
    
    // Smooth rotation animation
    function smoothRotate(delta) {
        const model = avatarViewerState.model;
        if (!model) return;
        
        if (animationFrame) cancelAnimationFrame(animationFrame);
        targetRotationY = model.rotation.y + delta;
        
        function animate() {
            if (!model || targetRotationY === null) return;
            
            const diff = targetRotationY - model.rotation.y;
            if (Math.abs(diff) > 0.001) {
                model.rotation.y += diff * 0.2; // Smooth easing
                animationFrame = requestAnimationFrame(animate);
            } else {
                model.rotation.y = targetRotationY;
                targetRotationY = null;
            }
        }
        animate();
    }

    // Zoom controls with smooth animation
    if (zoomIn) {
        zoomIn.addEventListener('click', () => {
            const cam = avatarViewerState.camera;
            if (!cam) return;
            const newZ = Math.max(0.8, cam.position.z - zoomStep);
            smoothZoom(newZ);
            
            // Visual feedback
            zoomIn.style.transform = 'scale(0.9)';
            setTimeout(() => { zoomIn.style.transform = ''; }, 100);
        });
    }
    
    if (zoomOut) {
        zoomOut.addEventListener('click', () => {
            const cam = avatarViewerState.camera;
            if (!cam) return;
            const newZ = Math.min(10, cam.position.z + zoomStep);
            smoothZoom(newZ);
            
            // Visual feedback
            zoomOut.style.transform = 'scale(0.9)';
            setTimeout(() => { zoomOut.style.transform = ''; }, 100);
        });
    }
    
    // Rotation controls with smooth animation
    if (rotLeft) {
        rotLeft.addEventListener('click', () => {
            smoothRotate(-rotStep);
            
            // Visual feedback
            rotLeft.style.transform = 'rotate(-15deg) scale(0.9)';
            setTimeout(() => { rotLeft.style.transform = ''; }, 100);
        });
    }
    
    if (rotRight) {
        rotRight.addEventListener('click', () => {
            smoothRotate(rotStep);
            
            // Visual feedback
            rotRight.style.transform = 'rotate(15deg) scale(0.9)';
            setTimeout(() => { rotRight.style.transform = ''; }, 100);
        });
    }
    
    // Reset with smooth animation
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            const cam = avatarViewerState.camera;
            const model = avatarViewerState.model;
            const d = avatarViewerState.default;
            
            if (cam) smoothZoom(d.cameraPos.z);
            if (model) {
                targetRotationY = d.modelRotationY;
                model.rotation.y = d.modelRotationY; // Instant reset for rotation
                model.scale.set(d.modelScale, d.modelScale, d.modelScale);
            }
            
            // Visual feedback
            resetBtn.style.transform = 'rotate(360deg) scale(0.9)';
            setTimeout(() => { resetBtn.style.transform = ''; }, 300);
        });
    }
    
    // Auto-rotate toggle
    if (autoRotateBtn) {
        autoRotateBtn.addEventListener('click', () => {
            isAutoRotating = !isAutoRotating;
            autoRotateBtn.classList.toggle('active', isAutoRotating);
            autoRotateBtn.style.background = isAutoRotating ? '#FFD700' : '';
            
            // Store state
            avatarViewerState.autoRotate = isAutoRotating;
        });
    }
    
    // Keyboard shortcuts (only when preview is visible)
    const keyboardHandler = (e) => {
        const previewPanel = document.querySelector('.preview-panel');
        if (!previewPanel || previewPanel.classList.contains('hidden')) return;
        
        // Don't interfere with typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        switch(e.key) {
            case '+':
            case '=':
                e.preventDefault();
                zoomIn?.click();
                break;
            case '-':
            case '_':
                e.preventDefault();
                zoomOut?.click();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                rotLeft?.click();
                break;
            case 'ArrowRight':
                e.preventDefault();
                rotRight?.click();
                break;
            case 'r':
            case 'R':
                e.preventDefault();
                resetBtn?.click();
                break;
            case ' ':
                e.preventDefault();
                autoRotateBtn?.click();
                break;
        }
    };
    
    // Add keyboard listener
    document.addEventListener('keydown', keyboardHandler);
    
    // Store handler for cleanup if needed
    toolbar.dataset.keyboardHandlerAttached = 'true';
}

// Choose avatar and save selection
function chooseAvatar() {
    if (!selectedAvatar) {
        alert('Please select an avatar first!');
        return;
    }
    
    // Extra safety: Check if user is guest (NOT admin) and trying to select non-HoneyComb avatar
    // Use API-provided user status from window.avatarUserInfo (set during loadAvatars)
    const userInfo = window.avatarUserInfo || {};
    const isGuest = userInfo.is_guest === true;
    const isAdmin = userInfo.is_admin === true || userInfo.user_role === 'admin';
    const isHoneyComb = selectedAvatar.slug === 'honey-comb' || selectedAvatar.slug === 'honeycomb';
    
    console.log(`🔍 chooseAvatar - User: guest=${isGuest}, admin=${isAdmin}, avatar=${selectedAvatar.slug}`);
    
    // Only restrict guests - admins have unrestricted access
    if (isGuest && !isAdmin && !isHoneyComb) {
        console.warn('🚫 Guest user attempted to select locked avatar:', selectedAvatar.slug);
        alert('🔐 Guest users can only use the Honey Comb mascot avatar.\n\nPlease register for a free account to unlock more bee avatars!');
        
        // Reset to Honey Comb avatar
        const honeycombAvatar = allAvatars.find(a => a.slug === 'honey-comb' || a.slug === 'honeycomb');
        if (honeycombAvatar) {
            const honeycombElement = document.querySelector(`.avatar-hex-position[data-slug="${honeycombAvatar.slug}"]`);
            if (honeycombElement) {
                selectAvatar(honeycombAvatar, honeycombElement);
            }
        }
        return;
    }
    
    // Check if avatar is locked before attempting selection (skip for admins)
    if (!isAdmin && selectedAvatar.is_locked) {
        console.log('🔒 Avatar is locked for non-admin user');
        showLockedMessage(selectedAvatar);
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
        console.log(`📡 Avatar select response status: ${response.status}`);
        
        if (!response.ok) {
            // Try to parse error details
            return response.json().catch(() => ({})).then(data => {
                const errorMsg = data.error || `HTTP ${response.status}`;
                const errorReason = data.reason || 'unknown';
                console.error(`❌ Avatar select failed (${response.status}): ${errorMsg}`, data);

                // Friendly, kid-safe messaging for backend fail-closed unlock enforcement
                if (response.status === 503 && errorReason === 'unlock_system_unavailable') {
                    alert(
                        '🐝 Uh-oh! Our bee unlock system is taking a quick break.\n\n' +
                        'Please try again in a little bit. Your account is safe!'
                    );
                    return Promise.reject(new Error('Unlock system temporarily unavailable'));
                }

                if (response.status === 500 && errorReason === 'unlock_check_failed') {
                    alert(
                        '🐝 Hmm… we couldn\'t check if that bee is unlocked right now.\n\n' +
                        'Please try again in a moment.'
                    );
                    return Promise.reject(new Error('Unlock check failed'));
                }
                
                // Handle specific error reasons (server no longer uses guest_restricted)
                if (errorReason === 'premium_locked') {
                    // Premium avatar that must be purchased
                    alert(`🔒 ${selectedAvatar.name} is a premium avatar.\\n\\nThis avatar is only available for purchase.`);
                    return Promise.reject(new Error('Premium avatar locked'));
                } else if (errorReason === 'points_required') {
                    // Need more honey points
                    const pointsNeeded = data.points_needed || 0;
                    alert(`🍯 ${selectedAvatar.name} requires more Honey Points!\\n\\nEarn ${pointsNeeded.toLocaleString()} more Honey Points or purchase to unlock this avatar.`);
                    return Promise.reject(new Error('Insufficient honey points'));
                } else if ((response.status === 401 || response.status === 403) && !window.isUserLoggedIn) {
                    // Authentication required
                    const next = encodeURIComponent(window.location.pathname);
                    window.location.href = `/auth/login?next=${next}`;
                    return Promise.reject(new Error('Authentication required'));
                }
                
                // For other errors, show detailed message
                return Promise.reject(new Error(errorMsg));
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Avatar selection response:', data);
        
        if (data.success) {
            console.log(`🎉 Avatar successfully selected: ${data.avatar.name}`);
            
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

        // Most errors are already shown via a friendly alert above.
        // This is a safe fallback for unexpected cases.
        if (!(error && error.message && (
            error.message.includes('Premium avatar locked') ||
            error.message.includes('Insufficient honey points') ||
            error.message.includes('Authentication required') ||
            error.message.includes('Unlock system temporarily unavailable') ||
            error.message.includes('Unlock check failed')
        ))) {
            alert('Could not change your avatar. Please try again.');
        }
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
    
    // Determine if this is a guest restriction
    const isGuestRestriction = message.includes('Guest users must register');
    const tier = avatar.tier || 'premium';
    
    // Create appropriate messaging
    let actionHtml = '';
    if (isGuestRestriction) {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300; font-weight: 600;">
                🎓 Register for free to unlock amazing bee avatars!
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem;">
                <button class="locked-modal-btn" onclick="window.location.href='/auth/login'">Sign In</button>
                <button class="locked-modal-btn-secondary" onclick="this.closest('.locked-avatar-modal').remove()">Maybe Later</button>
            </div>
        `;
    } else if (tier === 'premium' || tier === 'earn_or_buy') {
        const canPurchase = canPurchaseAvatar(avatar);
        const purchaseLabel = avatar.price ? `Purchase for $${Number(avatar.price).toFixed(2)}` : 'Purchase to Unlock';
        const notReadyMsg = isProbablyNativeAppContext()
            ? 'In-app purchases are still loading. If you are in TestFlight, wait a few seconds and try again.'
            : 'Purchases are available in the BeeSmart iOS/Android app.';
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">💎 This bee is available for purchase.</p>
            <div style="display:flex; gap:1rem; justify-content:center; margin-top: 1.25rem; flex-wrap: wrap;">
                ${canPurchase ? `<button class="locked-modal-btn" onclick="purchaseLockedAvatar('${escapeAttr(avatar.slug)}')">${purchaseLabel}</button>` : ''}
                <button class="locked-modal-btn-secondary" onclick="this.closest('.locked-avatar-modal').remove()">Not now</button>
            </div>
            ${!canPurchase ? `<p style="margin-top: 0.75rem; color: rgba(255,215,0,0.85); font-weight: 600;">${notReadyMsg}</p>` : ''}
        `;
    } else {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">Keep spelling to unlock more awesome bees!</p>
            <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
        `;
    }
    
    const modal = document.createElement('div');
    modal.className = 'locked-avatar-modal';
    modal.innerHTML = `
        <div class="locked-modal-content">
            <button class="locked-modal-close" onclick="this.parentElement.parentElement.remove()">×</button>
            <div class="locked-modal-icon">🔒</div>
            <h2>${avatar.name} is Locked</h2>
            <p>${message}</p>
            ${actionHtml}
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

// --------- Purchases (Native IAP bridge) ---------

function escapeAttr(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function getIapPlatform() {
    if (window.BeeSmartIAP && window.BeeSmartIAP.platform) {
        return String(window.BeeSmartIAP.platform).toLowerCase();
    }
    const ua = navigator.userAgent || '';
    if (/Android/i.test(ua)) return 'google';
    if (/iPhone|iPad|Mac/i.test(ua)) return 'apple';
    return 'web';
}

function isUserAuthenticated() {
    const session = window.userSessionData || {};
    const userInfo = window.avatarUserInfo || {};
    return !!(session.authenticated || userInfo.user_authenticated || window.IS_AUTH);
}

function canPurchaseAvatar(avatar) {
    if (!avatar || !avatar.product_id) return false;
    if (!(window.BeeSmartIAP && typeof window.BeeSmartIAP.purchase === 'function')) return false;
    // Purchases require an authenticated user (server verify endpoint is login_required)
    return isUserAuthenticated();
}

function isProbablyNativeAppContext() {
    try {
        // Capacitor present is our strongest signal.
        if (window.Capacitor) return true;
    } catch (e) { /* ignore */ }
    const ua = navigator.userAgent || '';
    // TestFlight still reports as iPhone/iPad; Android wrapper reports Android.
    return (/iPhone|iPad|iPod/i.test(ua) || /Android/i.test(ua));
}

function findAvatarBySlug(slug) {
    const s = String(slug || '').toLowerCase();
    return (avatarsData || []).find(a => String(a.slug || '').toLowerCase() === s) || null;
}

async function _sleep(ms){
    return new Promise((r) => setTimeout(r, ms));
}

async function _waitForNativeIapBridge(timeoutMs){
    const deadline = Date.now() + (timeoutMs || 2000);
    // Fast path
    if (window.BeeSmartIAP && typeof window.BeeSmartIAP.purchase === 'function') return true;

    // In TestFlight, the bridge can become ready after the page JS runs.
    // Listen for the readiness event emitted by native-iap-bridge.js.
    let sawReadyEvent = false;
    const onReady = function() { sawReadyEvent = true; };
    try { window.addEventListener('beesmart:iap-ready', onReady); } catch (e) { /* ignore */ }

    try {
        while (Date.now() < deadline) {
            if (window.BeeSmartIAP && typeof window.BeeSmartIAP.purchase === 'function') return true;
            // If the ready event fired, poll a little more aggressively for a moment.
            if (sawReadyEvent) {
                await _sleep(50);
            } else {
                await _sleep(100);
            }
        }
    } finally {
        try { window.removeEventListener('beesmart:iap-ready', onReady); } catch (e) { /* ignore */ }
    }
    return !!(window.BeeSmartIAP && typeof window.BeeSmartIAP.purchase === 'function');
}

async function purchaseLockedAvatar(slug) {
    const avatar = findAvatarBySlug(slug);
    if (!avatar) {
        alert('Could not find that avatar. Please refresh and try again.');
        return;
    }

    // Apple Guideline 5.1.1: Allow IAP purchases without requiring registration
    // Registration is optional - users can purchase without an account
    // If user is not authenticated, they can still purchase (purchase will be tied to device/Apple ID)
    // We'll suggest registration after purchase for cross-device access

    // Capacitor plugins can register after page JS runs; wait a bit longer in TestFlight
    // and prefer the explicit iap-ready event.
    await _waitForNativeIapBridge(isProbablyNativeAppContext() ? 5000 : 2000);
    if (!window.BeeSmartIAP || typeof window.BeeSmartIAP.purchase !== 'function') {
        // Don't hard-block TestFlight if bridge detection is flaky.
        // Try a quick server-side restore/reconcile for users who already own premium/avatars.
        try {
            const res = await fetch('/api/iap/restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ platform: 'web', product_ids: [] })
            });
            const data = await res.json().catch(() => ({}));
            const restored = !!(data && (data.ok === true || data.success === true));
            if (restored) {
                await loadAvatars();
                alert('Restored purchases. If you already owned this avatar, it should be unlocked now.');
                return;
            }
        } catch (e) {
            // ignore
        }

        alert('In-app purchase is not ready yet. If you are in TestFlight, please wait a few seconds and try again. If this continues, reinstall the TestFlight build.');
        return;
    }

    if (!avatar.product_id) {
        alert('This avatar is not available for purchase right now.');
        return;
    }

    const proceed = confirm(`Purchase ${avatar.name}? You can manage purchases in your App Store / Play settings.`);
    if (!proceed) return;

    try {
        const platform = getIapPlatform();
        const productId = avatar.product_id;
        const result = await Promise.resolve(window.BeeSmartIAP.purchase(productId));

        // Important: On iOS (StoreKit2), the native layer already returns VERIFIED transactions
        // and `native-iap-bridge.js` immediately reconciles owned products via `/api/iap/restore`.
        // So `/api/iap/verify` is best-effort only; if it fails we can still succeed by reconciling.
        let verifyOk = false;
        try {
            const body = {
                product_id: productId,
                transaction_id: result && (result.transaction_id || result.transactionId || null),
                purchase_token: result && (result.purchase_token || result.purchaseToken || null),
                payload: (result && result.payload) ? result.payload : (result || {})
            };
            const resp = await fetch(`/api/iap/verify/${platform}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify(body)
            });
            const json = await resp.json().catch(() => ({}));
            verifyOk = !!(resp.ok && json && json.success);
        } catch (e) {
            verifyOk = false;
        }

        // Always reconcile after purchase so locks update immediately.
        try {
            if (window.BeeSmartIAP && typeof window.BeeSmartIAP.reconcile === 'function') {
                await Promise.resolve(window.BeeSmartIAP.reconcile('post_purchase'));
            } else {
                await fetch('/api/iap/restore', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ platform: 'web', product_ids: [] })
                });
            }
        } catch (e) { /* ignore */ }

        // Refresh the avatar list to reflect new entitlements
        await loadAvatars();
        const updated = findAvatarBySlug(slug);
        if (updated && !updated.is_locked) {
            alert(`✅ ${avatar.name} unlocked!`);
            const escSlug = (window.CSS && typeof CSS.escape === 'function')
                ? CSS.escape(updated.slug)
                : String(updated.slug).replace(/"/g, '\\"');
            const el = document.querySelector(`.avatar-hex-position[data-slug="${escSlug}"]`);
            if (el) selectAvatar(updated, el);
            return;
        }

        // If we got here, the purchase likely completed but the entitlement didn't apply yet.
        // Give a clear next step rather than a hard failure.
        const note = verifyOk
            ? 'Purchase completed, but the unlock has not appeared yet. Please tap Restore Purchases and try again.'
            : 'Purchase completed, but verification/reconcile is still catching up. Please tap Restore Purchases and try again.';
        alert(note);
    } catch (err) {
        console.error('❌ Avatar purchase failed:', err);
        alert(`Purchase failed: ${(err && err.message) ? err.message : 'Unknown error'}`);
    }
}

// Expose for inline onclick handlers in modal HTML
window.purchaseLockedAvatar = purchaseLockedAvatar;


// --------- Bundle Shop (Packs) ---------
// Bundle shop UI was removed from the picker. Keep this as a no-op so older
// scripts/HTML can call it safely without throwing.
function setupBundleShop() {
    return;
}

function setBundleShopStatus(text) {
    const el = document.getElementById('bundleShopStatus');
    if (el) el.textContent = text;
}

function canPurchaseBundles() {
    if (!(window.BeeSmartIAP && typeof window.BeeSmartIAP.purchase === 'function')) return false;
    // Purchases require an authenticated user (verify endpoint is login_required)
    return isUserAuthenticated();
}

async function loadBundles() {
    const listEl = document.getElementById('bundleShopList');
    if (!listEl) return;

    setBundleShopStatus('Loading bundles...');
    listEl.innerHTML = '';

    const ts = Date.now();
    const resp = await fetch(`/api/bundles?t=${ts}`, {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-cache',
        headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    });
    const json = await resp.json().catch(() => ({}));
    if (!(resp.ok && json && json.success && Array.isArray(json.bundles))) {
        const msg = (json && (json.error || json.message)) ? (json.error || json.message) : `Failed to load bundles (HTTP ${resp.status})`;
        setBundleShopStatus('Could not load bundles');
        listEl.innerHTML = `<div style="grid-column: 1/-1; color:#5a4000; font-weight:700;">${escapeHtml(msg)}</div>`;
        return;
    }

    bundlesData = json.bundles;
    renderBundles(bundlesData, json.user || {});
}

function escapeHtml(s) {
    return String(s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function renderBundles(bundles, user) {
    const listEl = document.getElementById('bundleShopList');
    if (!listEl) return;

    const isPremium = !!(user && user.premium_member);
    const purchaseEnabled = canPurchaseBundles();

    if (!bundles || bundles.length === 0) {
        setBundleShopStatus('No bundles available');
        listEl.innerHTML = `<div style="grid-column: 1/-1; color:#5a4000; font-weight:700;">No bundle packs are configured yet.</div>`;
        return;
    }

    if (!purchaseEnabled) {
        setBundleShopStatus('Purchases available in the BeeSmart iOS/Android app');
    } else {
        setBundleShopStatus(isPremium ? 'Premium includes all avatars 🎉' : 'Choose a pack to unlock more bees');
    }

    listEl.innerHTML = '';
    bundles.forEach(b => {
        const owned = !!b.is_owned;
        const count = typeof b.count === 'number' ? b.count : (Array.isArray(b.avatars) ? b.avatars.length : 0);
        const name = b.name || b.id || 'Bundle';
        const pid = b.product_id || '';

        const card = document.createElement('div');
        card.style.cssText = [
            'background: rgba(255,255,255,0.65)',
            'border: 2px solid rgba(255, 215, 0, 0.35)',
            'border-radius: 16px',
            'padding: 12px',
            'box-shadow: 0 10px 20px rgba(0,0,0,0.08)'
        ].join(';');

        const avatarList = Array.isArray(b.avatars) ? b.avatars.slice(0, 5) : [];
        const more = Array.isArray(b.avatars) && b.avatars.length > 5 ? (b.avatars.length - 5) : 0;

        card.innerHTML = `
            <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:10px;">
                <div>
                    <div style="font-weight:900; color:#5a4000; font-size:1.05rem;">${escapeHtml(name)}</div>
                    <div style="color:#6b4a00; font-weight:700; margin-top:2px;">Includes ${count} avatars</div>
                </div>
                <div style="font-size:1.5rem;">🎁</div>
            </div>
            <div style="margin-top:10px; color:#5a4000; font-weight:600; font-size:0.92rem; line-height:1.3;">
                ${avatarList.map(a => `• ${escapeHtml(a)}`).join('<br/>')}
                ${more > 0 ? `<br/><span style="opacity:0.85;">…and ${more} more</span>` : ''}
            </div>
            <div style="display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; justify-content:flex-end;">
                <button type="button" class="bundle-buy-btn" ${owned ? 'disabled' : ''} style="
                    padding: 10px 12px;
                    border-radius: 12px;
                    border: none;
                    font-weight: 800;
                    cursor: ${owned ? 'not-allowed' : 'pointer'};
                    background: ${owned ? 'rgba(76,175,80,0.85)' : 'linear-gradient(135deg, #8E24AA, #5E35B1)'};
                    color: #fff;
                    opacity: ${(!purchaseEnabled && !owned) ? '0.75' : '1'};
                ">${owned ? (isPremium ? 'Included with Premium' : 'Owned') : 'Purchase Pack'}</button>
            </div>
            ${(!purchaseEnabled && !owned) ? `<div style="margin-top:8px; color:#6b4a00; font-weight:700; opacity:0.9;">Available in the BeeSmart app</div>` : ''}
        `;

        const buyBtn = card.querySelector('.bundle-buy-btn');
        if (buyBtn && !owned) {
            buyBtn.disabled = !purchaseEnabled;
            buyBtn.addEventListener('click', async () => {
                await purchaseBundle(pid, name);
            });
        }

        listEl.appendChild(card);
    });
}

async function purchaseBundle(productId, bundleName) {
    if (!productId) {
        alert('This bundle is not available for purchase right now.');
        return;
    }
    // Apple Guideline 5.1.1: Allow IAP purchases without requiring registration
    // Registration is optional - users can purchase without an account
    if (!window.BeeSmartIAP || typeof window.BeeSmartIAP.purchase !== 'function') {
        alert('Purchases are available in the BeeSmart iOS/Android app.');
        return;
    }

    const proceed = confirm(`Purchase "${bundleName}"? You can manage purchases in your App Store / Play settings.`);
    if (!proceed) return;

    try {
        const platform = getIapPlatform();
        const result = await Promise.resolve(window.BeeSmartIAP.purchase(productId));

        // Best-effort verification (non-blocking).
        let verifyOk = false;
        try {
            const body = {
                product_id: productId,
                transaction_id: result && (result.transaction_id || result.transactionId || null),
                purchase_token: result && (result.purchase_token || result.purchaseToken || null),
                payload: (result && result.payload) ? result.payload : (result || {})
            };
            const resp = await fetch(`/api/iap/verify/${platform}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify(body)
            });
            const json = await resp.json().catch(() => ({}));
            verifyOk = !!(resp.ok && json && json.success);
        } catch (e) {
            verifyOk = false;
        }

        // Always reconcile after purchase so locks update immediately.
        try {
            if (window.BeeSmartIAP && typeof window.BeeSmartIAP.reconcile === 'function') {
                await Promise.resolve(window.BeeSmartIAP.reconcile('post_bundle_purchase'));
            } else {
                await fetch('/api/iap/restore', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ platform: 'web', product_ids: [] })
                });
            }
        } catch (e) { /* ignore */ }

        // Refresh both bundles and avatars so locks update immediately
        await loadBundles();
        await loadAvatars();

        alert(`✅ Bundle unlocked: ${bundleName}${verifyOk ? '' : ' (syncing...)'}`);
    } catch (err) {
        console.error('❌ Bundle purchase failed:', err);
        alert(`Purchase failed: ${(err && err.message) ? err.message : 'Unknown error'}`);
    }
}


