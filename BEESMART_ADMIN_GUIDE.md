# 🔧 BeeSmart Spelling Bee - Administrator Technical Guide

## 📋 System Overview
This document provides technical guidance for administrators managing the BeeSmart Spelling Bee application, including recent updates, troubleshooting, and maintenance procedures.

---

## 🚀 Recent System Updates (October 2025)

### ✅ **Critical Fixes Implemented**

#### **1. JavaScript Syntax Error Resolution**
- **Issue**: `await` syntax error in MenuBeeSwarm3D constructor causing loading freeze
- **Location**: `templates/unified_menu.html` line ~5796
- **Fix**: Wrapped async `loadBeeModels()` call in IIFE with proper error handling
- **Impact**: Loading page now completes successfully, 3D avatars render properly

#### **2. Avatar Visibility System Overhaul**
- **MTL Texture References**: Fixed 16+ avatar MTL files with correct texture paths
- **Z-Index Issues**: Enhanced CSS positioning (avatar z-index: 15, cards: 5)
- **AI Validation**: Integrated automatic MTL reference validation and correction
- **WebGL Rendering**: Improved 3D object scaling, camera positioning, transparency

#### **3. Content Filtering with Guardian Reporting**
- **Enhanced Detection**: Multi-tier inappropriate content detection system
- **Progressive Warnings**: 3-level warning system (green → yellow → red)
- **Guardian Notifications**: Automated report generation after 3+ violations
- **Session Tracking**: 24-hour violation history with IP-based session management

---

## 🛡️ Content Filter Administration

### **System Components**
```
content_filter_guardian.py - Core filtering logic
AjaSpellBApp.py - Flask integration  
templates/unified_menu.html - Frontend notifications
data/content_violations.json - Violation log
data/guardian_reports/ - Generated reports directory
```

### **Configuration Management**

#### **Inappropriate Words Categories**
```python
ENHANCED_INAPPROPRIATE_WORDS = {
    'profanity': {...},
    'sexual_content': {...}, 
    'violence': {...},
    'drugs_alcohol': {...},
    'hate_speech': {...},
    'disturbing_content': {...},
    'spam_patterns': {...}
}
```

#### **Violation Thresholds**
- **Warning Level 1**: First violation (yellow)
- **Warning Level 2**: Second violation (orange)  
- **Guardian Report**: 3+ violations in 24 hours (red)

#### **Session Management**
- **Session ID**: Generated from IP hash for tracking
- **Storage**: In-memory with file backup for persistence
- **Cleanup**: Automatic removal of old violation records

### **API Endpoints**

#### **Content Filter Status**
```
GET /api/content-filter-status
Returns: {
  "ok": true,
  "status": {
    "session_id": "session_12345",
    "violation_count_24h": 2,
    "warning_level": "yellow",
    "guardian_notification_triggered": false
  },
  "messages": {...}
}
```

#### **Upload Filtering Integration**
- `POST /api/upload` - File uploads with content filtering
- `POST /api/upload-manual-words` - Manual entry with filtering
- `POST /api/upload-enhanced` - Background processing with filtering

---

## 🎨 Avatar System Administration

### **3D Avatar Pipeline**

#### **File Structure**
```
static/assets/avatars/
├── professor-bee/
│   ├── ProfessorBee.obj
│   ├── ProfessorBee.mtl  
│   └── ProfessorBee.png
├── cool-bee/
│   ├── CoolBee.obj
│   ├── CoolBee.mtl
│   └── CoolBee.png
└── ... (16+ avatars)
```

#### **MTL Validation System**
```python
# Automatic validation in avatar_catalog.py
def validate_avatar_mtl_references(avatar_id: str) -> Dict[str, Any]:
    # Checks MTL files for correct texture references
    # Auto-fixes common naming pattern issues
    # Integrates with get_avatar_info() for seamless operation
```

#### **Common MTL Fixes Applied**
- `Bee_Scientist_1019002302_texture.png` → `AlBee.png`
- `Bee_Cool_1019002303_texture.png` → `CoolBee.png`
- Pattern-based corrections for generated vs. actual filenames

### **3D Rendering Pipeline**

#### **WebGL Configuration**
```javascript
// Enhanced camera positioning
camera.position.set(0, 1.2, 3.2);
camera.lookAt(0, 0.8, 0);

// Improved object scaling  
const targetSize = 2.5;
const scale = targetSize / size;
object.scale.setScalar(scale);

// Transparent renderer
renderer.setClearColor(0x000000, 0);
```

#### **CSS Z-Index Management**
```css
#mascotBee3D {
    z-index: 15 !important;  /* Above cards */
    overflow: visible !important;
}

.content-card {
    z-index: 5;  /* Below avatars */
    overflow: visible;
}
```

#### **Fallback System**
1. **Primary**: WebGL 3D rendering with OBJ/MTL loading
2. **Secondary**: CSS animated bees if 3D fails
3. **Tertiary**: Static bee images for maximum compatibility

---

## 🔧 Technical Troubleshooting

### **Loading Page Issues**

#### **Symptoms**: Page stuck at loading screen
**Diagnosis Steps**:
1. Check browser console for JavaScript errors
2. Verify `await` syntax is in async functions or IIFE
3. Check Three.js library loading
4. Validate OBJ/MTL loader availability

**Recent Fix**: Wrapped async calls in IIFE to prevent syntax errors
```javascript
// Fixed implementation
(async () => {
    try {
        await this.loadBeeModels();
        this.animate();
    } catch (error) {
        console.error('❌ Failed to load bee models:', error);
        this.hideLoader();
        this.fallbackToCSSBees();
    }
})();
```

### **Avatar Rendering Issues**

#### **Symptoms**: Avatars invisible, 404 texture errors, incorrect scaling
**Diagnosis Tools**:
```python
# Run MTL validation tool
python fix_all_avatar_mtl_references.py

# Test avatar system
python test_avatar_visibility_fixes.py
```

**Resolution Steps**:
1. **MTL References**: Run validation tool to fix texture paths
2. **Z-Index**: Verify CSS positioning rules  
3. **Scaling**: Check 3D object sizing parameters
4. **Fallback**: Ensure CSS bees work if 3D fails

### **Content Filter Issues**

#### **Symptoms**: False positives, missing violations, system errors
**Diagnosis**:
```python
# Test content filter
python content_filter_guardian.py

# Check violation logs
cat data/content_violations.json

# Review guardian reports
ls data/guardian_reports/
```

**Configuration**:
- **Adjust Categories**: Modify `ENHANCED_INAPPROPRIATE_WORDS`
- **Threshold Tuning**: Change violation count triggers
- **Whitelist**: Add educational exceptions if needed

---

## 📊 Monitoring and Maintenance

### **System Health Checks**

#### **Automated Monitoring**
```bash
# Health endpoint
GET /health
Returns: {"status": "ok", "version": "1.6"}

# Avatar system validation
python test_avatar_visibility_fixes.py

# Content filter testing  
python -c "from content_filter_guardian import filter_content_with_tracking; print('✅ Content filter operational')"
```

#### **Performance Metrics**
- **Loading Time**: Target <3 seconds for main page
- **Avatar Load**: Target <5 seconds for 3D models
- **Memory Usage**: Monitor WebGL texture memory
- **Error Rate**: Track JavaScript console errors

### **Log Monitoring**

#### **Key Log Files**
```
logs/flask.log - Application logs
data/content_violations.json - Content filter violations  
data/guardian_reports/ - Generated safety reports
browser console - JavaScript errors
```

#### **Critical Error Patterns**
```javascript
// JavaScript syntax errors
"SyntaxError: await is only valid in async functions"

// Avatar loading failures
"❌ OBJLoader or MTLLoader not available"
"404 Not Found" (texture files)

// Content filter issues
"⚠️ Enhanced filter failed, using fallback"
```

### **Database Maintenance**

#### **Session Cleanup**
```python
# Clean old violation records (run daily)
def cleanup_old_violations():
    cutoff = datetime.now() - timedelta(days=7)
    # Remove records older than 7 days
```

#### **Avatar Cache**
```python
# Validate avatar references (run weekly)
from avatar_catalog import validate_all_avatar_mtl_references
result = validate_all_avatar_mtl_references()
```

---

## 🚀 Deployment Management

### **Railway Deployment Process**

#### **Automatic Deployment**
- **Trigger**: Push to `main` branch
- **Build**: Uses `Dockerfile` for container setup
- **Port**: Dynamic `$PORT` environment variable  
- **Health Check**: `/health` endpoint with 300s timeout

#### **Environment Variables**
```bash
PORT=8080                    # Railway assigned
DATABASE_URL=postgresql://   # Railway PostgreSQL  
FLASK_ENV=production        # Production mode
```

#### **Deployment Verification**
1. **Health Check**: Verify `/health` returns 200
2. **Loading Test**: Confirm page loads completely  
3. **Avatar Test**: Check 3D models render properly
4. **Content Filter**: Test inappropriate word detection
5. **Mobile Test**: Verify responsive design works

### **Rollback Procedures**

#### **Emergency Rollback**
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or rollback to specific commit
git reset --hard <previous-commit-hash>
git push --force origin main
```

#### **Feature Flags** 
```python
# Disable content filter if needed
CONTENT_FILTER_ENABLED = os.environ.get('CONTENT_FILTER_ENABLED', 'true').lower() == 'true'

# Disable 3D avatars
AVATARS_3D_ENABLED = os.environ.get('AVATARS_3D_ENABLED', 'true').lower() == 'true'
```

---

## 📋 Maintenance Checklist

### **Daily Tasks**
- [ ] Check application health endpoint
- [ ] Review error logs for critical issues  
- [ ] Monitor loading page completion rate
- [ ] Verify content filter operation

### **Weekly Tasks**  
- [ ] Run avatar MTL validation tool
- [ ] Review content violation reports
- [ ] Clean up old session data
- [ ] Performance monitoring review
- [ ] Update inappropriate words list if needed

### **Monthly Tasks**
- [ ] Full system backup
- [ ] Security audit of content filter
- [ ] Avatar system performance review
- [ ] User feedback analysis
- [ ] Documentation updates

---

## 🛠️ Development Tools

### **Testing Scripts**
```bash
# Comprehensive avatar testing
python test_avatar_visibility_fixes.py

# Content filter testing
python content_filter_guardian.py

# API endpoint validation
python test_api_endpoints.py

# Live system testing
python test_avatar_live.py
```

### **Debugging Tools**
```javascript
// Browser console debugging
console.log('Avatar system status:', window.avatarSystem);
console.log('3D rendering active:', !!window.THREE);

// Content filter status
fetch('/api/content-filter-status').then(r => r.json()).then(console.log);
```

### **Performance Profiling**
```javascript
// WebGL memory usage
const info = renderer.info;
console.log('WebGL Memory:', {
    textures: info.memory.textures,
    geometries: info.memory.geometries
});
```

---

## 📞 Support Contacts

### **Technical Issues**
- **System Administrator**: [Contact Info]
- **Developer Support**: [Contact Info]  
- **Emergency Hotline**: [Contact Info]

### **Educational Support**
- **Content Review Team**: [Contact Info]
- **Safety Coordinator**: [Contact Info]
- **User Support**: [Contact Info]

---

*BeeSmart Technical Guide - Comprehensive System Administration*

**Document Version**: 2.1  
**Last Updated**: October 21, 2025  
**Next Review**: November 21, 2025