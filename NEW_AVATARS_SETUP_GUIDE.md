# 🐝 New Alphabet Avatars - Setup Guide

## ✅ Pre-configured Avatars (8 total)

All logic is ready! Just add the files:

| Letter | Avatar Name | GLB File | Thumbnail File | Tier | Points |
|--------|-------------|----------|----------------|------|--------|
| **G** | Genius Bee | `GeniusBee.glb` | `GeniusBee!.png` | earn_or_buy | 5,000 |
| **I** | Ice Bee | `IceBee.glb` | `IceBee!.png` | earn_or_buy | 6,000 |
| **L** | Lucky Bee | `LuckyBee.glb` | `LuckyBee!.png` | earn_or_buy | 7,000 |
| **N** | Ninja Bee | `NinjaBee.glb` | `NinjaBee!.png` | premium | 15,000 |
| **T** | Tiny Bee | `TinyBee.glb` | `TinyBee!.png` | **FREE** | 0 |
| **U** | Unicorn Bee | `UnicornBee.glb` | `UnicornBee!.png` | premium | 22,000 |
| **X** | Xray Bee | `XrayBee.glb` | `XrayBee!.png` | premium | 24,000 |
| **Y** | Yogi Bee | `YogiBee.glb` | `YogiBee!.png` | earn_or_buy | 8,000 |

## 📁 File Placement

### 1. GLB Files
Place your 8 GLB files here:
```
/static/assets/avatars/glb_files/GeniusBee.glb
/static/assets/avatars/glb_files/IceBee.glb
/static/assets/avatars/glb_files/LuckyBee.glb
/static/assets/avatars/glb_files/NinjaBee.glb
/static/assets/avatars/glb_files/TinyBee.glb
/static/assets/avatars/glb_files/UnicornBee.glb
/static/assets/avatars/glb_files/XrayBee.glb
/static/assets/avatars/glb_files/YogiBee.glb
```

### 2. Thumbnail PNG Files
Place your 8 PNG thumbnails here:
```
/static/assets/avatars/glb_files/AvatarThumbnails/GeniusBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/IceBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/LuckyBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/NinjaBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/TinyBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/UnicornBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/XrayBee!.png
/static/assets/avatars/glb_files/AvatarThumbnails/YogiBee!.png
```

**Important**: The `!` in the PNG filename is required!

## 🎨 Avatar Descriptions (already configured)

- **Genius Bee**: "Brilliant bee with a genius mind for spelling!"
- **Ice Bee**: "Cool as ice! This bee never melts under pressure!"
- **Lucky Bee**: "The luckiest bee in the hive! Fortune favors the brave speller!"
- **Ninja Bee**: "Silent and stealthy! Master of spelling stealth moves!"
- **Tiny Bee**: "Small but mighty! Proves big spelling comes in tiny packages!"
- **Unicorn Bee**: "Magical and unique! Spreads rainbow spelling magic everywhere!"
- **Xray Bee**: "Sees through tricky words! X-ray vision for perfect spelling!"
- **Yogi Bee**: "Zen master of spelling! Finds inner peace through perfect words!"

## ✨ What's Already Done

✅ Catalog entries added to `avatar_catalog.py` (lines 525-696)
✅ Thumbnail mappings configured
✅ App Store metadata added to card generator
✅ Product IDs and SKUs configured
✅ Unlock points and tiers set
✅ API endpoints will auto-detect the new avatars

## 🚀 After Adding Files

### 1. Generate App Store Cards (Optional)
```bash
python3 generate_avatar_cards_simple.py
```

This creates 2048x2048 preview cards in `/static/assets/avatars/app_store_cards/`

### 2. Test Locally
```bash
python3 AjaSpellBApp.py
```

Visit: `http://localhost:5000` and check the avatar picker

### 3. Commit & Deploy
```bash
git add static/assets/avatars/glb_files/*
git commit -m "Add 8 new alphabet avatars (G, I, L, N, T, U, X, Y)"
git push origin main
```

## 🎯 Final Avatar Count

- **Before**: 30 avatars
- **After**: 38 avatars
- **Alphabet Coverage**: ALL 26 letters! ✅

## 📊 Distribution by Tier

- **Free (6)**: Cool Bee, Brother Bee, Builder Bee, Detective Bee, Explorer Bee, **Tiny Bee**
- **Earn/Buy (9)**: Buzz Bee, Cutie Bee, **Genius Bee**, **Ice Bee**, Knight Bee, **Lucky Bee**, Professor Bee, Rocker Bee, Selfie Bee, Vamp Bee, **Yogi Bee**
- **Premium (22)**: Al Bee, Buda Bee, Diva Bee, Doc Bee, Franken Bee, HoneyComb, J-Rock Bee, Motor Bee, **Ninja Bee**, O Bee, Queen Bee, Robo Bee, Sea Bee, Singer Bee, Space Bee, Super Bee, **Unicorn Bee**, Ware Bee, **Xray Bee**, Zom Bee
- **Mascot (1)**: Mascot Bee

## 🔍 Verification

After adding files, run:
```bash
ls -1 static/assets/avatars/glb_files/*.glb | wc -l
# Should show: 38

ls -1 static/assets/avatars/glb_files/AvatarThumbnails/*!.png | wc -l
# Should show: 38
```

## ❓ Questions?

The system is ready - just drop in your GLB and PNG files and everything will work automatically! 🎉
