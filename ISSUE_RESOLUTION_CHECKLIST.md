# Issue Resolution Checklist - January 2026

## Issue 1: Paid Apps Agreement ✅ ACTION REQUIRED

**Status**: ⚠️ **Manual Action Required in App Store Connect**

**Owner**: Jeffery

**Description**: Apple Developer has 2 agreements. Request to sign the Paid App Agreement too.

### Steps to Complete:
1. [ ] Log into App Store Connect
2. [ ] Navigate to: Agreements, Tax, and Banking
3. [ ] Find "Paid Applications Agreement"
4. [ ] Check current status
5. [ ] If not "Active", complete the agreement:
   - [ ] Accept agreement terms
   - [ ] Complete tax information
   - [ ] Complete banking information
6. [ ] Wait for "Active" status (24-48 hours)
7. [ ] Verify IAP products work in sandbox

**Reference**: See `PAID_APPS_AGREEMENT_GUIDE.md` for detailed instructions

**Impact**: 
- ⚠️ **Critical**: IAP purchases will not work without this agreement
- ⚠️ **Blocks**: App Store review cannot test IAP functionality
- ✅ **Fix Time**: 24-48 hours after completing all information

---

## Issue 2: Remove Required Background Modes ✅ ACTION REQUIRED

**Status**: ⚠️ **Manual Action Required in Xcode**

**Owner**: Jeffery

**Description**: Required Background Modes is in Xcode. In case if there is no current usage of this capability field, request to please remove it for now.

### Steps to Complete:
1. [ ] Open Xcode project: `mobile/ios/App/App.xcodeproj`
2. [ ] Select "App" target (under TARGETS)
3. [ ] Go to "Signing & Capabilities" tab
4. [ ] Find "Background Modes" section
5. [ ] Remove Background Modes:
   - [ ] Click "-" button to remove, OR
   - [ ] Uncheck all background mode options
6. [ ] Verify "Background Modes" no longer appears
7. [ ] Clean build folder (Shift+Cmd+K)
8. [ ] Rebuild project to verify

**Reference**: See `XCODE_BACKGROUND_MODES_REMOVAL_GUIDE.md` for detailed instructions

**Current Status**:
- ✅ Info.plist: UIBackgroundModes is commented out (not active)
- ⚠️ Xcode Project: May still have Background Modes in Capabilities (needs removal)

**Impact**:
- ⚠️ **Review Issue**: Apple Guideline 2.5.4 violation
- ✅ **Fix Time**: 5 minutes (manual Xcode change)
- ✅ **No Code Impact**: App functionality unchanged

---

## Summary

### Code Changes ✅
- ✅ Info.plist verified (UIBackgroundModes commented out)
- ✅ Documentation created for both issues

### Manual Actions Required ⚠️
1. ⚠️ **App Store Connect**: Sign Paid Apps Agreement
2. ⚠️ **Xcode**: Remove Background Modes capability

### Documentation Created
- ✅ `PAID_APPS_AGREEMENT_GUIDE.md` - Complete guide for signing agreement
- ✅ `XCODE_BACKGROUND_MODES_REMOVAL_GUIDE.md` - Step-by-step Xcode instructions
- ✅ `ISSUE_RESOLUTION_CHECKLIST.md` - This checklist

---

## Priority Order

1. **HIGH PRIORITY**: Paid Apps Agreement (blocks IAP testing)
2. **MEDIUM PRIORITY**: Remove Background Modes (review compliance)

---

## Completion Verification

After completing both actions:

- [ ] Paid Apps Agreement shows "Active" in App Store Connect
- [ ] Background Modes removed from Xcode Capabilities
- [ ] IAP purchases work in sandbox environment
- [ ] App builds successfully without warnings
- [ ] Ready for App Store resubmission
