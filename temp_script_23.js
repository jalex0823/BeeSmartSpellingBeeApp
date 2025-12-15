
        //  Load student's Buzz Dust rank (authenticated users only)
        {% if current_user.is_authenticated %}
        async function loadStudentBuzzDust() {
            try {
                console.log(' [TICKER] Starting Buzz Dust load...');
                console.log(' [TICKER] Authentication state:', true);
                console.log(' [TICKER] Current user:', '{{ current_user.username }}');
                
                const res = await fetch('/api/buzz-dust/info', {
                    credentials: 'same-origin',
                    cache: 'no-store'
                });
                
                console.log(' [TICKER] Fetch response status:', res.status, res.statusText);
                
                if (!res.ok) {
                    console.error(' [TICKER] HTTP error:', res.status, res.statusText);
                    const errorText = await res.text();
                    console.error(' [TICKER] Error response body:', errorText);
                    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                
                const data = await res.json();
                console.log(' [TICKER] Full API response:', JSON.stringify(data, null, 2));
                
                // Validate response structure
                if (!data) {
                    console.error(' [TICKER] API returned null/undefined data');
                    throw new Error('No data returned from API');
                }
                
                if (!data.current_class) {
                    console.error(' [TICKER] Missing current_class in response:', data);
                    throw new Error('Invalid response structure: missing current_class');
                }
                
                // Update rank title
                const rankTitleEl = document.getElementById('rank-title');
                if (rankTitleEl) {
                    const rankLabel = data.current_class.label || 'Novice Bee';
                    rankTitleEl.textContent = rankLabel;
                    console.log(' [TICKER] Rank title updated:', rankLabel);
                } else {
                    console.warn(' [TICKER] Element #rank-title not found in DOM');
                }
                
                // Update Buzz Dust amount
                const amountEl = document.getElementById('student-buzz-dust-amount');
                if (amountEl) {
                    const buzzDust = data.total_buzz_dust || 0;
                    const formatted = buzzDust.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                    amountEl.textContent = formatted + ' ';
                    console.log(' [TICKER] Buzz Dust amount updated:', buzzDust);
                } else {
                    console.warn(' [TICKER] Element #student-buzz-dust-amount not found in DOM');
                }
                
                // Update badge with PNG (fallback from 3D GLB due to loading issues)
                const badgeEl = document.getElementById('student-rank-badge');
                if (badgeEl && data.current_class && data.current_class.badge_image) {
                    // Clear any existing content
                    badgeEl.innerHTML = '';
                    
                    // Use PNG badge image instead of 3D GLB
                    let pngFile = data.current_class.badge_image.replace('.glb', '.png');
                    // Normalize basename to handle case differences
                    const base = pngFile.split('/').pop();
                    const pngOverrides = new Map([
                        // GLB  PNG explicit mappings (present in static/assets/badges)
                        ['Novice.png', 'Novice.png'],
                        ['Apprentice.png', 'Apprentice.png'],
                        ['Scholar.png', 'Scholar.png'],
                        ['Magistrate.png', 'Magistrate.png'],
                        ['BuzzDustMaster.png', 'BuzzDustMaster.png'],
                        // Known typo: Elite.glb  Elete.png
                        ['Elite.png', 'Elete.png']
                    ]);
                    if (pngOverrides.has(base)) {
                        pngFile = pngOverrides.get(base);
                    }
                    const img = document.createElement('img');
                    // Primary path
                    img.src = `/static/assets/badges/${pngFile}`;
                    img.alt = data.current_class.label || 'Badge';
                    img.style.width = '200px';
                    img.style.height = '200px';
                    img.style.objectFit = 'contain';
                    img.style.filter = 'drop-shadow(0 4px 12px rgba(0,0,0,0.15))';
                    // Fallbacks for known filename mismatches
                    const fallbacks = new Map([
                        ['Elite.png', '/static/assets/badges/Elete.png']
                    ]);
                    img.onerror = function(){
                        const alt = fallbacks.get(pngFile);
                        if (alt) {
                            console.warn(' [TICKER] PNG not found, trying fallback:', alt);
                            img.onerror = null; // prevent loops
                            img.src = alt;
                        } else {
                            console.error(' [TICKER] PNG Badge failed to load:', pngFile);
                        }
                    };
                    badgeEl.appendChild(img);
                    
                    // Hide the left badge since we're using the morphing one on the right
                    badgeEl.style.display = 'none';
                    
                    console.log(' [TICKER] PNG Badge loaded:', pngFile);
                    
                    // Update morphing badge/logo container with same badge
                    const morphImg = document.getElementById('morph-badge-logo');
                    if (morphImg) {
                        // Store badge and crest URLs for morphing
                        window._badgeUrl = `/static/assets/badges/${pngFile}`;
                        window._crestUrl = "{{ url_for('static', filename='BeeSmartCrestLogo1.png') }}";
                        
                        // Set initial image to badge (not crest)
                        morphImg.src = window._badgeUrl;
                        
                        // Start morphing animation (guard if function missing)
                        if (!window._morphingInitialized && typeof initBadgeLogoMorphing === 'function') {
                            initBadgeLogoMorphing();
                            window._morphingInitialized = true;
                            console.log(' [TICKER] Badge/Logo morphing initialized - will alternate between badge and crest');
                        } else if (window._morphingInitialized) {
                            console.log(' [TICKER] Morphing already initialized, badge URL updated');
                        } else {
                            console.warn(' [TICKER] initBadgeLogoMorphing not available');
                        }
                    }
                } else if (!badgeEl) {
                    console.warn(' [TICKER] Element #student-rank-badge not found in DOM');
                } else if (!data.current_class) {
                    console.warn(' [TICKER] No current_class in response');
                } else {
                    console.warn(' [TICKER] No badge_image in response:', data.current_class);
                }
                
                // Update progress ticker - CRITICAL SECTION
                const tickerEl = document.getElementById('buzz-dust-ticker');
                const tickerTextEl = document.getElementById('ticker-text');
                
                console.log(' [TICKER] Ticker elements found:', {
                    tickerEl: !!tickerEl,
                    tickerTextEl: !!tickerTextEl,
                    at_max_rank: data.at_max_rank,
                    has_next_class: !!data.next_class
                });
                
                if (tickerEl && tickerTextEl) {
                    let tickerMessage = '';
                    
                    if (data.at_max_rank) {
                        // Maximum rank achieved
                        tickerMessage = ` You've reached the highest rank: ${data.current_class.label}! You're a legend! `;
                        console.log(' [TICKER] Max rank message set');
                    } else if (data.next_class && data.next_class.label) {
                        // Show progress to next rank
                        const nextRank = data.next_class.label;
                        const needed = data.dust_needed || (data.next_class.min_points - (data.total_buzz_dust || 0));
                        const formatted = needed.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        
                        tickerMessage = ` Earn ${formatted} more Buzz Dust to reach ${nextRank}! Keep spelling! `;
                        console.log(' [TICKER] Progress message set:', { nextRank, needed, formatted });
                    } else {
                        // Fallback if no next class data
                        tickerMessage = ` Keep practicing to earn more Buzz Dust and rank up! `;
                        console.log(' [TICKER] Using generic fallback message');
                    }
                    
                    tickerTextEl.textContent = tickerMessage;
                    tickerEl.style.display = 'block';
                    tickerEl.style.visibility = 'visible';
                    console.log(' [TICKER] Ticker text updated:', tickerMessage.substring(0, 50) + '...');
                    console.log(' [TICKER] Ticker visibility:', window.getComputedStyle(tickerEl).display);
                    
                    //  Add magical fairy dust to ticker!
                    setTimeout(() => createTickerFairyDust(), 300);
                } else {
                    // Ticker elements not present on this page (unified_menu) - this is expected
                    // They exist on student dashboard pages
                    if (!tickerEl) console.debug(' [TICKER] Element #buzz-dust-ticker not found (expected on main menu)');
                    if (!tickerTextEl) console.debug(' [TICKER] Element #ticker-text not found (expected on main menu)');
                }
                
                console.log(' [TICKER] loadStudentBuzzDust completed successfully');
                
            } catch (error) {
                console.error(' [TICKER] Fatal error in loadStudentBuzzDust:', error);
                console.error(' [TICKER] Error stack:', error.stack);
                
                // Set safe fallback values
                const rankTitleEl = document.getElementById('rank-title');
                const amountEl = document.getElementById('student-buzz-dust-amount');
                const tickerTextEl = document.getElementById('ticker-text');
                
                if (rankTitleEl) {
                    rankTitleEl.textContent = 'Novice Bee';
                    console.log(' [TICKER] Fallback: rank set to Novice Bee');
                }
                if (amountEl) {
                    amountEl.textContent = '0 ';
                    console.log(' [TICKER] Fallback: Buzz Dust set to 0');
                }
                if (tickerTextEl) {
                    tickerTextEl.textContent = ' Start practicing to earn Buzz Dust and rank up! ';
                    console.log(' [TICKER] Fallback: Generic ticker message set');
                }
            }
        }
        
        // Load immediately when DOM is ready (faster than window.load)
        console.log(' [TICKER] Setting up DOMContentLoaded listener');
        if (document.readyState === 'loading') {
            console.log(' [TICKER] DOM still loading, adding event listener');
            document.addEventListener('DOMContentLoaded', () => {
                console.log(' [TICKER] DOMContentLoaded fired, calling loadStudentBuzzDust');
                loadStudentBuzzDust();
            });
        } else {
            // DOM already loaded, execute immediately
            console.log(' [TICKER] DOM already ready, calling loadStudentBuzzDust immediately');
            loadStudentBuzzDust();
        }
        {% endif %}
    