
    // =============================================================
    // AVATAR PERSONIFICATION SYSTEM - ALL 40 AVATARS
    // =============================================================

    const AVATAR_PERSONAS = {
        // FREE (5)
        brotherBee: { id: 'brother-bee', displayName: 'Brother Bee', tier: 'FREE', pointsRequired: 0, priceUsd: 0, vibe: 'Friendly, cool, and loyal.', signatureMoveKey: 'brother_bump', defaultAnimation: 'broWave', bgFxClass: 'avatar-bg-brother', clickBurstClass: 'avatar-burst-generic' },
        builderBee: { id: 'builder-bee', displayName: 'Builder Bee', tier: 'FREE', pointsRequired: 0, priceUsd: 0, vibe: 'Hammer in hand, construction expert.', signatureMoveKey: 'builder_hammer', defaultAnimation: 'hammerSwing', bgFxClass: 'avatar-bg-builder', clickBurstClass: 'avatar-burst-generic' },
        coolBee: { id: 'cool-bee', displayName: 'Cool Bee', tier: 'FREE', pointsRequired: 0, priceUsd: 0, vibe: 'Shades on, chill mode.', signatureMoveKey: 'cool_headbob', defaultAnimation: 'coolIdle', bgFxClass: 'avatar-bg-cool', clickBurstClass: 'avatar-burst-cool' },
        detectiveBee: { id: 'detective-bee', displayName: 'Detective Bee', tier: 'FREE', pointsRequired: 0, priceUsd: 0, vibe: 'Always on the case.', signatureMoveKey: 'detective_scan', defaultAnimation: 'scanLoop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        explorerBee: { id: 'explorer-bee', displayName: 'Explorer Bee', tier: 'FREE', pointsRequired: 0, priceUsd: 0, vibe: 'Adventurous and curious.', signatureMoveKey: 'explorer_map', defaultAnimation: 'mapCheck', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        
        // MASCOT (1)
        mascotBee: { id: 'mascot-bee', displayName: 'BeeSmart Mascot', tier: 'MASCOT', pointsRequired: 0, priceUsd: 0, vibe: 'Official BeeSmart cheerleader.', signatureMoveKey: 'mascot_cheer', defaultAnimation: 'cheer', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        
        // EARN OR BUY (7)
        buzzBee: { id: 'buzz-bee', displayName: 'Buzz Bee', tier: 'EARN_OR_BUY', pointsRequired: 3000, priceUsd: 0.99, vibe: 'Energetic and always buzzing.', signatureMoveKey: 'buzz_spin', defaultAnimation: 'spinBurst', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        cutieBee: { id: 'cutie-bee', displayName: 'Cutie Bee', tier: 'EARN_OR_BUY', pointsRequired: 4000, priceUsd: 0.99, vibe: 'Adorable and playful.', signatureMoveKey: 'cutie_heart', defaultAnimation: 'heartPop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        knightBee: { id: 'knight-bee', displayName: 'Knight Bee', tier: 'EARN_OR_BUY', pointsRequired: 4000, priceUsd: 0.99, vibe: 'Brave defender of the hive.', signatureMoveKey: 'knight_guard', defaultAnimation: 'shieldRaise', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        professorBee: { id: 'professor-bee', displayName: 'Professor Bee', tier: 'EARN_OR_BUY', pointsRequired: 9000, priceUsd: 0.99, vibe: 'Wise and loves big words.', signatureMoveKey: 'professor_point', defaultAnimation: 'chalkboard', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        rockerBee: { id: 'rocker-bee', displayName: 'Rocker Bee', tier: 'EARN_OR_BUY', pointsRequired: 8000, priceUsd: 0.99, vibe: 'Rockstar with a guitar.', signatureMoveKey: 'rocker_riff', defaultAnimation: 'guitarSolo', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        selfieBee: { id: 'selfie-bee', displayName: 'Selfie Bee', tier: 'EARN_OR_BUY', pointsRequired: 5000, priceUsd: 0.99, vibe: 'Always camera-ready.', signatureMoveKey: 'selfie_snap', defaultAnimation: 'selfiePose', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        vampBee: { id: 'vamp-bee', displayName: 'Vamp Bee', tier: 'EARN_OR_BUY', pointsRequired: 10000, priceUsd: 0.99, vibe: 'Spooky but stylish.', signatureMoveKey: 'vamp_cape', defaultAnimation: 'capeSwirl', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        
        // PREMIUM (27)
        alBee: { id: 'al-bee', displayName: 'Al Bee', tier: 'PREMIUM', pointsRequired: 20000, priceUsd: 0.99, vibe: 'Boss of the books and budgets.', signatureMoveKey: 'al_confident', defaultAnimation: 'armsFold', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        budaBee: { id: 'buda-bee', displayName: 'Buda Bee', tier: 'PREMIUM', pointsRequired: 15000, priceUsd: 0.99, vibe: 'Calm and centered.', signatureMoveKey: 'buda_float', defaultAnimation: 'lotusPose', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        divaBee: { id: 'diva-bee', displayName: 'Diva Bee', tier: 'PREMIUM', pointsRequired: 12000, priceUsd: 0.99, vibe: 'Center stage with sparkle.', signatureMoveKey: 'diva_hairflip', defaultAnimation: 'stageBow', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        docBee: { id: 'doc-bee', displayName: 'Doc Bee', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Always on call to help.', signatureMoveKey: 'doc_stethoscope', defaultAnimation: 'checkup', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        fairyBee: { id: 'fairy-bee', displayName: 'Fairy Bee', tier: 'PREMIUM', pointsRequired: 25000, priceUsd: 1.99, vibe: 'Sparkly wings and magic dust.', signatureMoveKey: 'fairy_twirl', defaultAnimation: 'sparkleSpin', bgFxClass: 'avatar-bg-fairy', clickBurstClass: 'avatar-burst-fairy' },
        frankenBee: { id: 'franken-bee', displayName: 'Franken Bee', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Stitched together and fun.', signatureMoveKey: 'franken_stomp', defaultAnimation: 'monsterWalk', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        gamerBee: { id: 'gamer-bee', displayName: 'Gamer Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Headset on, ready to play.', signatureMoveKey: 'gamer_combo', defaultAnimation: 'controllerMash', bgFxClass: 'avatar-bg-gamer', clickBurstClass: 'avatar-burst-gamer' },
        honeyComb: { id: 'honey-comb', displayName: 'Honey Comb', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Sweet and golden.', signatureMoveKey: 'honey_drip', defaultAnimation: 'gooeyWave', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        inventorBee: { id: 'inventor-bee', displayName: 'Inventor Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Goggles on, always tinkering.', signatureMoveKey: 'inventor_idea', defaultAnimation: 'lightbulb', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        jRockBee: { id: 'j-rock-bee', displayName: 'J Rock Bee', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Hip-hop swagger and rhythm.', signatureMoveKey: 'jrock_poplock', defaultAnimation: 'danceLoop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        lumberjackBee: { id: 'lumberjack-bee', displayName: 'Lumberjack Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Strong and steady.', signatureMoveKey: 'lumberjack_chop', defaultAnimation: 'axeChop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        motorBee: { id: 'motor-bee', displayName: 'Motor Bee', tier: 'PREMIUM', pointsRequired: 20000, priceUsd: 0.99, vibe: 'Fast and noisy.', signatureMoveKey: 'motor_rev', defaultAnimation: 'engineRev', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        nurseBee: { id: 'nurse-bee', displayName: 'Nurse Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Kind and caring.', signatureMoveKey: 'nurse_shot', defaultAnimation: 'syringeReady', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        oBee: { id: 'o-bee', displayName: 'O Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 0.99, vibe: 'Mysterious and slick.', signatureMoveKey: 'obee_spin', defaultAnimation: 'cloakSpin', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        plumberBee: { id: 'plumber-bee', displayName: 'Plumber Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Fixes any leak.', signatureMoveKey: 'plumber_wrench', defaultAnimation: 'pipeFix', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        queenBee: { id: 'queen-bee', displayName: 'Queen Bee', tier: 'PREMIUM', pointsRequired: 28000, priceUsd: 0.99, vibe: 'Royal and commanding.', signatureMoveKey: 'queen_wave', defaultAnimation: 'royalWave', bgFxClass: 'avatar-bg-queen', clickBurstClass: 'avatar-burst-queen' },
        roboBee: { id: 'robo-bee', displayName: 'Robo Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 0.99, vibe: 'Mechanical and precise.', signatureMoveKey: 'robo_scan', defaultAnimation: 'robotLoop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        seaBee: { id: 'sea-bee', displayName: 'Sea Bee', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Ocean-loving wave rider.', signatureMoveKey: 'sea_wave', defaultAnimation: 'surfPose', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        singerBee: { id: 'singer-bee', displayName: 'Singer Bee', tier: 'PREMIUM', pointsRequired: 22000, priceUsd: 0.99, vibe: 'Loves the spotlight.', signatureMoveKey: 'singer_belt', defaultAnimation: 'singLoop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        spaceBee: { id: 'space-bee', displayName: 'Space Bee', tier: 'PREMIUM', pointsRequired: 18000, priceUsd: 0.99, vibe: 'Rocket pack and stars.', signatureMoveKey: 'space_launch', defaultAnimation: 'liftOff', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        superBee: { id: 'super-bee', displayName: 'Super Bee', tier: 'PREMIUM', pointsRequired: 26000, priceUsd: 0.99, vibe: 'Cape and heroic stance.', signatureMoveKey: 'super_hero', defaultAnimation: 'heroLanding', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        technoBee: { id: 'techno-bee', displayName: 'Techno Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Neon lights and beats.', signatureMoveKey: 'techno_glitch', defaultAnimation: 'beatDrop', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        umpireBee: { id: 'umpire-bee', displayName: 'Umpire Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Calls it like it is.', signatureMoveKey: 'umpire_safe', defaultAnimation: 'safeOut', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        wareBee: { id: 'ware-bee', displayName: 'Ware Bee', tier: 'PREMIUM', pointsRequired: 27000, priceUsd: 0.99, vibe: 'Cyber security guardian.', signatureMoveKey: 'ware_shield', defaultAnimation: 'dataShield', bgFxClass: 'avatar-bg-ware', clickBurstClass: 'avatar-burst-ware' },
        xrayBee: { id: 'xray-bee', displayName: 'Xray Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Sees through everything.', signatureMoveKey: 'xray_peek', defaultAnimation: 'xrayScan', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        yetiBee: { id: 'yeti-bee', displayName: 'Yeti Bee', tier: 'PREMIUM', pointsRequired: 30000, priceUsd: 1.99, vibe: 'Snowy and strong.', signatureMoveKey: 'yeti_roar', defaultAnimation: 'snowRoar', bgFxClass: null, clickBurstClass: 'avatar-burst-generic' },
        zomBee: { id: 'zom-bee', displayName: 'Zom Bee', tier: 'PREMIUM', pointsRequired: 25000, priceUsd: 0.99, vibe: 'Shuffly and spooky but fun.', signatureMoveKey: 'zom_lurch', defaultAnimation: 'zombieWalk', bgFxClass: 'avatar-bg-zombee', clickBurstClass: 'avatar-burst-zombee' }
    };

    const AVATAR_ID_TO_KEY = {};
    Object.keys(AVATAR_PERSONAS).forEach((key) => {
        const cfg = AVATAR_PERSONAS[key];
        AVATAR_ID_TO_KEY[cfg.id] = key;
    });

    let CURRENT_AVATAR_KEY = 'mascotBee';

    // =============================================================
    // CONTROLLER HELPERS
    // =============================================================

    // Avatar control state
    const avatarControlState = {
        autoRotate: false,
        animationFrame: null,
        targetCameraZ: null,
        targetRotationY: null
    };

    function getAvatarController() {
        try {
            console.log('getAvatarController called');
            
            // Try NEW clean container first
            const cleanInstance = window.SmartyBee3DInstances?.['avatarControls3D'];
            if (cleanInstance) {
                console.log('Found avatar controller in NEW clean container (avatarControls3D)');
                return cleanInstance;
            }
            
            // Fallback to static method
            const controller = window.SmartyBee3D?.getController?.('avatarControls3D');
            if (controller) {
                console.log('Found avatar controller via static method');
                return controller;
            }
            
            console.warn('No avatar controller found in avatarControls3D');
            return null;
        } catch (e) {
            console.warn('Avatar controller not available:', e);
            return null;
        }
    }
```

    function safeAvatarSpin360() {
        const controller = getAvatarController();
        if (!controller || !controller.bee) return;
        
        // Trigger alphabet spill effect
        createAlphabetSpill();
        
        // Calculate the nearest front-facing position (0, 2π, 4π, etc.)
        const currentRotation = controller.bee.rotation.y;
        const currentCycles = currentRotation / (Math.PI * 2);
        const targetCycles = Math.round(currentCycles) + 1; // Complete one more full rotation
        const targetRotation = targetCycles * (Math.PI * 2); // Always ends at exact multiple of 2π
        
        const duration = 1000; // 1 second
        const startTime = Date.now();
        
        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease-out animation
            const eased = 1 - Math.pow(1 - progress, 3);
            controller.bee.rotation.y = currentRotation + ((targetRotation - currentRotation) * eased);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Ensure exact front-facing position
                controller.bee.rotation.y = targetRotation;
                console.log('✅ 360° spin complete, avatar locked to front:', controller.bee.rotation.y);
            }
        }
        
        animate();
    }

    function safeAvatarRotate(deltaDegrees, smooth = true) {
        const controller = getAvatarController();
        console.log('safeAvatarRotate called. Controller:', controller);
        console.log('  controller.bee:', controller?.bee);
        console.log('  controller.camera:', controller?.camera);
        if (!controller) return;
        
        if (smooth && controller.bee && controller.bee.rotation) {
            // Smooth rotation animation - no manualControl flag interference
            const deltaRad = deltaDegrees * (Math.PI / 180);
            if (avatarControlState.animationFrame) cancelAnimationFrame(avatarControlState.animationFrame);
            avatarControlState.targetRotationY = controller.bee.rotation.y + deltaRad;
            console.log('Starting rotation animation: current=' + controller.bee.rotation.y.toFixed(3) + ', target=' + avatarControlState.targetRotationY.toFixed(3) + ', delta=' + deltaRad.toFixed(3));
            
            function animate() {
                if (!controller.bee || !controller.bee.rotation || avatarControlState.targetRotationY === null) return;
                const diff = avatarControlState.targetRotationY - controller.bee.rotation.y;
                if (Math.abs(diff) > 0.001) {
                    controller.bee.rotation.y += diff * 0.2;
                    console.log('  Animating: rotation.y = ' + controller.bee.rotation.y.toFixed(3));
                    avatarControlState.animationFrame = requestAnimationFrame(animate);
                } else {
                    controller.bee.rotation.y = avatarControlState.targetRotationY;
                    avatarControlState.targetRotationY = null;
                    console.log('  Animation complete at ' + controller.bee.rotation.y.toFixed(3));
                }
            }
            animate();
        } else if (typeof controller.rotate === 'function') {
            console.log('  Using controller.rotate() fallback');
            controller.rotate(0, deltaDegrees * (Math.PI / 180));
        } else {
            console.warn('  No rotation method available!');
        }
    }

    function safeAvatarZoom(deltaAmount, smooth = true) {
        const controller = getAvatarController();
        console.log('safeAvatarZoom called. Controller:', controller);
        console.log('  controller.camera:', controller?.camera);
        console.log('  deltaAmount:', deltaAmount);
        if (!controller) return;
        
        if (smooth && controller.camera) {
            // Smooth zoom animation - no manualControl flag interference
            if (avatarControlState.animationFrame) cancelAnimationFrame(avatarControlState.animationFrame);
            const newZ = Math.max(1, Math.min(12, controller.camera.position.z + deltaAmount));
            avatarControlState.targetCameraZ = newZ;
            
            function animate() {
                if (!controller.camera || avatarControlState.targetCameraZ === null) return;
                const diff = avatarControlState.targetCameraZ - controller.camera.position.z;
                if (Math.abs(diff) > 0.01) {
                    controller.camera.position.z += diff * 0.15;
                    avatarControlState.animationFrame = requestAnimationFrame(animate);
                } else {
                    controller.camera.position.z = avatarControlState.targetCameraZ;
                    avatarControlState.targetCameraZ = null;
                }
            }
            animate();
        } else if (typeof controller.zoom === 'function') {
            console.log('  Using controller.zoom() fallback');
            controller.zoom(deltaAmount);
        } else {
            console.warn('  No zoom method available!');
        }
    }

    function safeAvatarReset() {
        const controller = getAvatarController();
        if (!controller) return;
        
        // Cancel any ongoing animations
        if (avatarControlState.animationFrame) {
            cancelAnimationFrame(avatarControlState.animationFrame);
            avatarControlState.targetCameraZ = null;
            avatarControlState.targetRotationY = null;
        }
        
        if (typeof controller.resetView === 'function') {
            controller.resetView();
        } else if (typeof controller.resetCamera === 'function') {
            controller.resetCamera();
        } else if (typeof controller.setDefaultPose === 'function') {
            controller.setDefaultPose();
        }
    }
    
    function toggleAutoRotate() {
        avatarControlState.autoRotate = !avatarControlState.autoRotate;
        const controller = getAvatarController();
        
        // Update button state
        const btn = document.querySelector('[data-avatar-control="auto-rotate"]');
        if (btn) {
            btn.classList.toggle('active', avatarControlState.autoRotate);
            btn.style.background = avatarControlState.autoRotate ? 
                'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' : '';
        }
        
        // Clear any existing morph timer
        if (window._avatarMorphTimer) {
            clearInterval(window._avatarMorphTimer);
            window._avatarMorphTimer = null;
        }
        
        // If controller supports it, enable/disable auto-rotation
        if (controller && controller.bee) {
            if (avatarControlState.autoRotate) {
                // Start auto-rotation animation (slower speed)
                function autoRotateLoop() {
                    if (!avatarControlState.autoRotate) return;
                    if (controller.bee) {
                        controller.bee.rotation.y += 0.001; // Reduced from 0.003 to 0.001 for slower rotation
                    }
                    requestAnimationFrame(autoRotateLoop);
                }
                autoRotateLoop();
                
                // Start avatar morphing carousel
                startAvatarMorphCarousel();
            }
        }
        
        return avatarControlState.autoRotate;
    }
    
    // Avatar morphing carousel - cycles through different avatar models with fade transitions
    function startAvatarMorphCarousel() {
        // Clear any existing timer
        if (window._avatarMorphTimer) {
            clearInterval(window._avatarMorphTimer);
        }
        
        // Build list of all avatar IDs
        const avatarIds = Object.keys(AVATAR_PERSONAS).map(key => AVATAR_PERSONAS[key].id);
        
        // Shuffle for variety
        for (let i = avatarIds.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [avatarIds[i], avatarIds[j]] = [avatarIds[j], avatarIds[i]];
        }
        
        let currentIndex = 0;
        
        const morphToNext = () => {
            if (!avatarControlState.autoRotate) return;
            
            const controller = getAvatarController();
            const container = document.getElementById('mascotBee3D') || document.getElementById('avatarControls3D');
            
            if (container && controller && controller.bee) {
                // Add pulse animation
                container.style.animation = 'avatar-morph-pulse 0.6s ease-in-out';
                
                // Fade out current avatar
                setTimeout(() => {
                    container.style.transition = 'opacity 400ms ease-out';
                    container.style.opacity = '0';
                }, 200); // Start fade after pulse begins
                
                // Wait for fade out, then change avatar and fade in
                setTimeout(() => {
                    const nextAvatarId = avatarIds[currentIndex % avatarIds.length];
                    console.log('🔄 Morphing to:', nextAvatarId);
                    
                    // Update via setCurrentAvatar to trigger full avatar change
                    if (typeof window.setCurrentAvatar === 'function') {
                        window.setCurrentAvatar(nextAvatarId);
                    }
                    
                    // Fade in new avatar with pulse
                    setTimeout(() => {
                        container.style.opacity = '1';
                        container.style.animation = 'avatar-morph-pulse 0.6s ease-in-out';
                    }, 50);
                    
                    // Clear animation after completion
                    setTimeout(() => {
                        container.style.animation = '';
                    }, 700);
                    
                    currentIndex++;
                }, 600); // Match pulse + fade-out duration
            } else {
                // Fallback without fade if container not found
                const nextAvatarId = avatarIds[currentIndex % avatarIds.length];
                console.log('🔄 Morphing to:', nextAvatarId);
                
                if (typeof window.setCurrentAvatar === 'function') {
                    window.setCurrentAvatar(nextAvatarId);
                }
                
                currentIndex++;
            }
        };
        
        // Change avatar every 4 seconds (increased from 3.5s for smoother transitions)
        window._avatarMorphTimer = setInterval(morphToNext, 4000);
        
        // Start with first avatar
        morphToNext();
    }
