/**
 * BeeSmart Logo Configuration
 * Central configuration for all logo references across the application
 * When you need to change the logo, only update the MASTER_LOGO_PATH here
 */

(function() {
    'use strict';
    
    // MASTER LOGO PATH - Change this to update logo everywhere
    const MASTER_LOGO_PATH = '/static/BeeSmartCrestLogo1.png';
    const LOGO_VERSION = '20251118'; // Update this when logo changes to bust cache
    
    // Generate versioned logo URL
    const LOGO_URL = `${MASTER_LOGO_PATH}?v=${LOGO_VERSION}`;
    
    // Export to window for global access
    window.BeeSmartLogo = {
        path: MASTER_LOGO_PATH,
        url: LOGO_URL,
        version: LOGO_VERSION,
        
        // Get the logo URL (with cache busting)
        getUrl: function() {
            return this.url;
        },
        
        // Get the logo path (without version)
        getPath: function() {
            return this.path;
        },
        
        // Apply logo to an image element
        applyToImage: function(imgElement) {
            if (imgElement && imgElement.tagName === 'IMG') {
                imgElement.src = this.url;
                imgElement.alt = imgElement.alt || 'BeeSmart Spelling Bee Application';
            }
        },
        
        // Apply logo to all images with a specific class
        applyToClass: function(className) {
            const images = document.querySelectorAll(`.${className}`);
            images.forEach(img => this.applyToImage(img));
        },
        
        // Replace all logo images on the page
        replaceAll: function() {
            // Find all images that might be logos
            const logoSelectors = [
                '.crest-logo',
                '.brand-logo',
                'img[alt*="BeeSmart"]',
                'img[alt*="Logo"]'
            ];
            
            logoSelectors.forEach(selector => {
                const images = document.querySelectorAll(selector);
                images.forEach(img => this.applyToImage(img));
            });
        }
    };
    
    // Also set the legacy BeeSmartBrand for backward compatibility
    window.BeeSmartBrand = window.BeeSmartBrand || {};
    window.BeeSmartBrand.logoPath = LOGO_URL;
    
    // Auto-apply on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.BeeSmartLogo.replaceAll();
        });
    } else {
        window.BeeSmartLogo.replaceAll();
    }
})();
