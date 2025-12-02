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
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🐝 BeeSmart Avatar Picker - Initializing...');
    console.log('THREE available:', typeof THREE !== 'undefined');
    console.log('GLTFLoader available:', typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined');
    console.log('DRACOLoader available:', typeof THREE !== 'undefined' && typeof THREE.DRACOLoader !== 'undefined');

    // Step 1: Verify session/auth
    await verifyUserAuthentication();

    // Step 2: Fetch consolidated user meta for robust role gating
    await fetchUserMeta();

    // Gate guests completely from picker (except showing mascot + prompt)
    if (!window.avatarUserInfo || !window.avatarUserInfo.user_authenticated) {
        showGuestRestriction();
        // Still load minimal HoneyComb avatar for preview UX familiarity
        try { await loadAvatars(true); } catch (_) {}
        setupSearchFilter();
        return; // Do NOT proceed with full picker for guests
    }

    // Authenticated path
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

        if (reason === 'not_purchased') {
            actionHtml = `
                <p style="margin-top: 1rem; color: #FFB300;">💎 This is a premium avatar available for purchase.</p>
                <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
            `;
        } else if (reason === 'not_enough_points') {
            actionHtml = `
                <p style="margin-top: 1rem; color: #FFB300;">Keep spelling to earn more Honey Points!</p>
                <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
            `;
        } else if (reason === 'guest_restriction') {
            actionHtml = `
                <p style="margin-top: 1rem; color: #FFB300;">Create a free account to unlock and customize more bees!</p>
                <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.5rem;">
                    <button onclick="window.location.href='/auth/register'" style="background:#FFD700;color:#222;font-weight:600;padding:0.5rem 0.8rem;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">Register</button>
                    <button onclick="window.location.href='/auth/login'" style="background:#222;color:#FFD700;font-weight:600;padding:0.5rem 0.8rem;border:1px solid #FFD700;border-radius:6px;cursor:pointer;font-size:0.85rem;">Log In</button>
                </div>
            `;
        } else if (reason === 'progress_required') {
            actionHtml = `
                <p style="margin-top: 1rem; color: #FFB300;">Complete more quizzes to unlock this bee!</p>
                <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
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

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
// internal loader with guest-minimal mode
async function loadAvatars(guestMinimal) {
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

        // Store assigned students / delegated unlock metadata if provided
        if (Array.isArray(data.assigned_students)) {
            window.avatarAssignedStudents = data.assigned_students;
        }
        if (data.can_delegated_unlock) {
            window.canDelegatedUnlock = true;
        }
        
        // Store user info globally for chooseAvatar to check admin/guest status
        // Build robust user info object with defensive fallbacks.
        const inferredRole = data.user_role || data.role || (data.is_admin ? 'admin' : (data.is_guest ? 'guest' : (data.user_authenticated ? 'registered' : null)));
        window.avatarUserInfo = {
            is_guest: !!(data.is_guest),
            is_admin: !!(data.is_admin),
            user_role: inferredRole,
            role: inferredRole, // alias for convenience
            user_authenticated: !!(data.user_authenticated),
            admin_all_access: !!(data.admin_all_access),
            premium_member: !!(data.premium_member),
            total_unlocked: typeof data.total_unlocked === 'number' ? data.total_unlocked : null
        };
        // If total_unlocked not provided by API, derive it now.
        if (window.avatarUserInfo.total_unlocked === null && Array.isArray(data.avatars)) {
            window.avatarUserInfo.total_unlocked = data.avatars.filter(a => !a.is_locked).length;
        }
        console.log('👤 User Info (enhanced):', window.avatarUserInfo);
        if (!window.avatarUserInfo.user_role) {
            console.warn('⚠️ user_role is null after inference; front-end may treat user as guest.');
        }

        // Inject an auth mismatch banner if we appear unauthenticated yet many avatars are unlocked.
        maybeShowAuthMismatchBanner();
        
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
        
        console.log('📦 Raw API avatars count:', apiAvatars.length);
        if (apiAvatars.length > 0) {
            console.log('📦 Sample avatar structure:', JSON.stringify(apiAvatars[0], null, 2));
        }
        
        let sourceAvatars = apiAvatars;
        if (guestMinimal) {
            // Restrict guests to ONLY mascot avatar (honey-comb) for rendering clarity
            sourceAvatars = apiAvatars.filter(a => (a.id === 'honey-comb' || a.id === 'honeycomb'));
        }

        const rawAvatars = sourceAvatars.map(avatar => {
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
                thumbnail: avatar.thumbnail || (avatar.urls ? avatar.urls.thumbnail : avatar.thumbnail_url),
                // NEW: Lock status from monetization system
                is_locked: avatar.is_locked || false,
                unlock_message: avatar.unlock_message || '',
                // NEW: Numeric unlock info for computing remaining points
                unlock_points: typeof avatar.unlock_points === 'number' ? avatar.unlock_points : null,
                tier: avatar.tier || null,
                price: typeof avatar.price === 'number' ? avatar.price : null,
                locked_reason: avatar.locked_reason || null,
                unlock_requirements: (avatar.unlock_requirements && typeof avatar.unlock_requirements === 'object') ? avatar.unlock_requirements : null,
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
    // Inject delegated unlock UI if role qualifies
    maybeInjectDelegatedUnlockUI();
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

// Detect potential session/auth mismatch: lots of unlocked avatars but not authenticated.
function maybeShowAuthMismatchBanner() {
    try {
        const info = window.avatarUserInfo || {};
        // Heuristic: if user not authenticated and unlocked total >= 10, show banner
        if (info.user_authenticated || typeof info.total_unlocked !== 'number') return;
        if (info.total_unlocked < 10) return; // small counts fine for guests
        const existing = document.getElementById('auth-mismatch-banner');
        if (existing) return; // already shown

        const banner = document.createElement('div');
        banner.id = 'auth-mismatch-banner';
        banner.style.cssText = 'background:linear-gradient(90deg,#ffbf47,#ff9f1c);color:#222;padding:0.6rem 1rem;font-weight:600;font-size:0.9rem;display:flex;align-items:center;gap:0.75rem;justify-content:center;border-bottom:2px solid #d08900;position:relative;z-index:1000;';
        banner.innerHTML = `🔐 You have many avatars unlocked, but you are not signed in. <button id="auth-mismatch-login" style="background:#222;color:#FFD700;border:1px solid #222;padding:0.35rem 0.75rem;border-radius:4px;cursor:pointer;font-weight:600;">Log In</button>`;

        banner.querySelector('#auth-mismatch-login').addEventListener('click', () => {
            const next = encodeURIComponent(window.location.pathname);
            window.location.href = `/auth/login?next=${next}`;
        });

        // Insert banner at top of body or before main content wrapper
        const target = document.body;
        if (target.firstChild) {
            target.insertBefore(banner, target.firstChild);
        } else {
            target.appendChild(banner);
        }
        console.log('⚠️ Auth mismatch banner displayed');
    } catch (e) {
        console.warn('Auth mismatch banner failed:', e);
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

    // 🔄 Dispose any previous preview renderer to prevent WebGL context leaks
    if (window._avatarPreviewCtx && window._avatarPreviewCtx.renderer) {
        try {
            window._avatarPreviewCtx.renderer.dispose();
        } catch (e) {
            console.warn('⚠️ Previous renderer dispose failed (safe to ignore):', e);
        }
        const oldCanvas = window._avatarPreviewCtx.renderer.domElement;
        if (oldCanvas && oldCanvas.parentNode) {
            oldCanvas.parentNode.removeChild(oldCanvas);
        }
        window._avatarPreviewCtx = null;
    }
    
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

    // Store current preview context globally for lifecycle management
    window._avatarPreviewCtx = { renderer, scene, avatarSlug: avatar.slug };
    
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
    // Refresh delegated unlock target selector if present
    refreshDelegatedTargetSelector();
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
                
                // Handle specific error reasons
                if (errorReason === 'guest_restricted') {
                    // Guest user trying to select non-mascot avatar
                    alert('🔐 Guest users can only use the Honey Comb mascot avatar.\\n\\nPlease register for a free account to unlock more bee avatars!');
                    return Promise.reject(new Error('Guest user restriction'));
                } else if (errorReason === 'premium_locked') {
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
        const errorMsg = error.message || 'An unexpected error occurred. Please try again.';
        
        // Show detailed error message
        alert(`Could not change your avatar: ${errorMsg}`);
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Choose This Bee';
            btn.style.background = '';
        }
    });
}

// Fetch /api/user/me for unified meta (role, auth, counts)
async function fetchUserMeta() {
    try {
        const resp = await fetch('/api/user/me', { credentials: 'same-origin' });
        if (!resp.ok) return;
        const meta = await resp.json();
        // Merge into existing avatarUserInfo if present
        window.avatarUserInfo = Object.assign(window.avatarUserInfo || {}, {
            user_authenticated: !!meta.user_authenticated,
            user_role: meta.user_role || meta.role,
            role: meta.role || meta.user_role,
            is_guest: meta.role === 'guest',
            is_admin: !!meta.is_admin,
            premium_member: !!meta.premium_member,
            total_unlocked: meta.total_unlocked || (window.avatarUserInfo ? window.avatarUserInfo.total_unlocked : null)
        });
        console.log('🔐 Fetched user meta:', window.avatarUserInfo);
    } catch (e) {
        console.warn('Failed to fetch /api/user/me:', e);
    }
}

// Show guest restriction overlay instead of full picker
function showGuestRestriction() {
    const grid = document.querySelector('.honeycomb-grid');
    if (grid) {
        grid.innerHTML = `
            <div style="grid-column:1/-1;text-align:center;padding:2rem;color:#FFD700;">
                <h2 style="margin:0 0 1rem;">🔐 Avatar Customization Locked</h2>
                <p style="max-width:520px;margin:0 auto 1.25rem;font-size:1.05rem;line-height:1.5;">
                    Guest users can explore the mascot bee but need a free account to unlock and customize other avatars.
                </p>
                <div style="display:flex;gap:1rem;justify-content:center;">
                    <button onclick="window.location.href='/auth/register'" style="background:#FFD700;color:#222;font-weight:600;padding:0.6rem 1.2rem;border:none;border-radius:6px;cursor:pointer;">Register Free</button>
                    <button onclick="window.location.href='/auth/login'" style="background:#222;color:#FFD700;font-weight:600;padding:0.6rem 1.2rem;border:1px solid #FFD700;border-radius:6px;cursor:pointer;">Log In</button>
                </div>
            </div>`;
    }
}

// Inject delegated unlock UI (teacher/parent/admin only)
function maybeInjectDelegatedUnlockUI() {
    try {
        const info = window.avatarUserInfo || {};
        if (!info.user_authenticated) return;
        if (!['teacher','parent','admin'].includes(info.user_role)) return;
        const sidebar = document.querySelector('.preview-content');
        if (!sidebar) return;
        if (document.getElementById('delegated-unlock-panel')) return; // already inserted
        const panel = document.createElement('div');
        panel.id = 'delegated-unlock-panel';
        panel.style.cssText = 'margin-top:1rem;padding:0.75rem;border:1px solid rgba(255,215,0,0.3);border-radius:8px;background:rgba(255,215,0,0.08);';
        panel.innerHTML = `
            <div style="font-weight:600;color:#FFD700;display:flex;align-items:center;gap:0.5rem;">
                <span>👪 Assign Avatar To Student</span>
            </div>
            <div style="margin-top:0.5rem;">
                <select id="delegated-target-select" style="width:100%;padding:0.4rem;border-radius:6px;border:1px solid #444;background:#222;color:#FFD700;font-size:0.9rem;"></select>
            </div>
            <button id="delegated-unlock-btn" style="margin-top:0.6rem;width:100%;background:linear-gradient(90deg,#ffbf47,#ff9f1c);color:#222;font-weight:600;padding:0.55rem 0;border:none;border-radius:6px;cursor:pointer;">Unlock & Assign To Student</button>
            <div id="delegated-unlock-status" style="margin-top:0.5rem;font-size:0.75rem;color:#FFA500;"></div>
        `;
        sidebar.appendChild(panel);
        refreshDelegatedTargetSelector();
        document.getElementById('delegated-unlock-btn').addEventListener('click', delegatedUnlockSubmit);
    } catch (e) {
        console.warn('Delegated unlock UI failed:', e);
    }
}

function refreshDelegatedTargetSelector() {
    const sel = document.getElementById('delegated-target-select');
    if (!sel) return;
    const students = window.avatarAssignedStudents || [];
    sel.innerHTML = '';
    if (!students.length) {
        sel.innerHTML = '<option value="">No linked students</option>';
        sel.disabled = true;
        return;
    }
    students.forEach(stu => {
        const opt = document.createElement('option');
        opt.value = stu.id;
        opt.textContent = `${stu.display_name || stu.username} (#${stu.id})`;
        sel.appendChild(opt);
    });
    sel.disabled = false;
}

async function delegatedUnlockSubmit() {
    const statusEl = document.getElementById('delegated-unlock-status');
    if (!selectedAvatar) {
        statusEl.textContent = 'Select an avatar first.';
        return;
    }
    const sel = document.getElementById('delegated-target-select');
    if (!sel || !sel.value) {
        statusEl.textContent = 'Choose a student.';
        return;
    }
    statusEl.textContent = 'Assigning avatar...';
    try {
        const resp = await fetch('/api/avatars/delegated-unlock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ avatar_slug: selectedAvatar.slug, target_user_id: Number(sel.value) })
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.success) {
            statusEl.textContent = 'Failed: ' + (data.error || `HTTP ${resp.status}`);
            statusEl.style.color = '#ff4d4f';
            return;
        }
        statusEl.textContent = '✅ Assigned successfully!';
        statusEl.style.color = '#4caf50';
    } catch (e) {
        statusEl.textContent = 'Error: ' + e.message;
        statusEl.style.color = '#ff4d4f';
    }
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
function computeLockedMessage(avatar) {
    // Prefer server-provided structured reason codes for consistency
    const reason = avatar.locked_reason;
    const req = avatar.unlock_requirements || {};
    const tier = avatar.tier || req.tier;
    const price = (typeof avatar.price === 'number') ? avatar.price : (typeof req.price === 'number' ? req.price : null);
    const requiredPoints = (typeof avatar.unlock_points === 'number') ? avatar.unlock_points : (typeof req.required_points === 'number' ? req.required_points : null);
    const userPoints = (typeof currentUserHoneyPoints === 'number') ? currentUserHoneyPoints : (typeof req.user_points === 'number' ? req.user_points : 0);

    if (!avatar.is_locked) {
        return 'Unlocked!';
    }
    switch (reason) {
        case 'guest_restriction':
            return 'Register to customize your bee!';
        case 'guest_mascot':
            return 'Mascot bee is always available!';
        case 'not_enough_points': {
            if (requiredPoints != null) {
                const remaining = Math.max(requiredPoints - userPoints, 0);
                let msg = `Earn ${remaining.toLocaleString()} more Honey Points to unlock.`;
                if (price && tier === 'earn_or_buy') {
                    msg += ` Or purchase for $${Number(price).toFixed(2)}.`;
                }
                return msg;
            }
            return 'Earn more Honey Points to unlock.';
        }
        case 'not_purchased':
            if (price) {
                if (tier === 'earn_or_buy' && requiredPoints != null) {
                    const remaining = Math.max(requiredPoints - userPoints, 0);
                    return remaining > 0
                        ? `Earn ${remaining.toLocaleString()} more Honey Points or purchase for $${Number(price).toFixed(2)}.`
                        : `Purchase for $${Number(price).toFixed(2)}.`;
                }
                return `Purchase for $${Number(price).toFixed(2)}.`;
            }
            return 'Purchase required to unlock.';
        case 'progress_required':
            return 'Complete more quizzes to unlock this bee!';
        case 'admin_unlocked':
            return 'Admin access granted.';
        case 'free':
            return 'Free avatar';
        default:
            // Fallback to legacy message if provided
            return avatar.unlock_message || 'Locked';
    }
}

// Show a modal explaining the lock reason with contextual actions
function showLockedMessage(avatar) {
    if (!avatar) return;
    const message = computeLockedMessage(avatar);
    const reason = avatar.locked_reason;
    let actionHtml = '';

    if (reason === 'not_purchased') {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">💎 This is a premium avatar available for purchase.</p>
            <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
        `;
    } else if (reason === 'not_enough_points') {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">Keep spelling to earn more Honey Points!</p>
            <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
        `;
    } else if (reason === 'guest_restriction') {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">Create a free account to unlock and customize more bees!</p>
            <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.5rem;">
                <button onclick="window.location.href='/auth/register'" style="background:#FFD700;color:#222;font-weight:600;padding:0.5rem 0.8rem;border:none;border-radius:6px;cursor:pointer;font-size:0.85rem;">Register</button>
                <button onclick="window.location.href='/auth/login'" style="background:#222;color:#FFD700;font-weight:600;padding:0.5rem 0.8rem;border:1px solid #FFD700;border-radius:6px;cursor:pointer;font-size:0.85rem;">Log In</button>
            </div>
        `;
    } else if (reason === 'progress_required') {
        actionHtml = `
            <p style="margin-top: 1rem; color: #FFB300;">Complete more quizzes to unlock this bee!</p>
            <button class="locked-modal-btn" onclick="this.parentElement.parentElement.remove()">Got It!</button>
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

    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
}

// --- Real-time Wordbank Integration ---------------------------------------
// Listen for wordbank-stats-updated events (emitted by quiz/menu pages) to
// update honey points display and trigger auto-refresh if unlock thresholds reached.
// This keeps avatar unlock messaging responsive without a full page reload.
let _avatarAutoRefreshScheduled = false;
function _maybeAutoRefreshUnlocks() {
    if (_avatarAutoRefreshScheduled) return;
    // If any locked avatar now meets its unlock_points threshold, schedule a refresh
    const unlockable = avatarsData && avatarsData.some(a => a.is_locked && typeof a.unlock_points === 'number' && typeof currentUserHoneyPoints === 'number' && a.unlock_points <= currentUserHoneyPoints);
    if (!unlockable) return;
    _avatarAutoRefreshScheduled = true;
    console.log('🔄 Detected newly unlockable avatar(s); scheduling avatar list refresh...');
    setTimeout(() => {
        // Refresh with full list (not guest minimal)
        loadAvatars(false).catch(e => console.warn('Avatar refresh after unlock failed:', e));
        _avatarAutoRefreshScheduled = false;
    }, 800);
}

function _handleWordbankStatsUpdated(evt) {
    const detail = (evt && evt.detail) || {};
    const incomingPoints = (typeof detail.sessionPoints === 'number') ? detail.sessionPoints : (typeof detail.honey_points === 'number' ? detail.honey_points : null);
    if (incomingPoints != null && incomingPoints !== currentUserHoneyPoints) {
        console.log(`🍯 Honey/Session points updated via wordbank event: ${incomingPoints}`);
        currentUserHoneyPoints = incomingPoints;
        // Re-render marquee to reflect new honey points
        updateDynamicMarquee(avatarsData || []);
        _maybeAutoRefreshUnlocks();
    }
}

document.addEventListener('wordbank-stats-updated', _handleWordbankStatsUpdated);


