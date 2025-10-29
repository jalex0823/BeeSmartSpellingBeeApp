# 🚀 Install Node.js - Required First Step

## Download & Install (5 minutes)

### Step 1: Download Node.js
**Click this link:** https://nodejs.org/en/download

**Choose:** 
- Windows Installer (.msi)
- **64-bit** version
- **LTS (Long Term Support)** - Currently v20.x

### Step 2: Run Installer
1. Double-click the downloaded `.msi` file
2. Click "Next" through all prompts (accept defaults)
3. **Important:** Check the box that says "Automatically install necessary tools"
4. Click "Install" (may need administrator password)
5. Wait 2-3 minutes for installation

### Step 3: Verify Installation
1. **Close all PowerShell windows** (important!)
2. Open **NEW** PowerShell window
3. Run these commands:
   ```powershell
   node --version   # Should show v20.x.x
   npm --version    # Should show 10.x.x
   ```

If you see version numbers, you're ready! 🎉

---

## Next Steps After Node.js is Installed

Run these commands in PowerShell (in your project folder):

```powershell
# Install Capacitor and plugins (~2 minutes)
npm install

# Choose your platform:

# For Android (any computer):
npm run cap:add:android
npm run cap:open:android

# For iOS (Mac only):
npm run cap:add:ios
npm run cap:open:ios
```

---

## Quick Reference

**Download Link:** https://nodejs.org/en/download
**Choose:** Windows 64-bit LTS Installer

After installation, come back here and run `npm install`!

🐝 Your mobile app journey begins now! 🐝
