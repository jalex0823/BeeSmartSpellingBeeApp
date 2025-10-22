# Avatar Management Guide

## Quick Start

### Adding New Avatars

1. **Prepare your avatar files** in a folder with this exact structure:
   ```
   YourAvatarName/
   ├── YourAvatarName.obj     (3D model file)
   ├── YourAvatarName.mtl     (material definition)
   ├── YourAvatarName.png     (texture image)
   └── YourAvatarName!.png    (thumbnail for selection UI)
   ```

2. **Run the avatar manager:**
   ```bash
   python avatar_quick_manager.py --add "YourAvatarName" --source "C:/path/to/YourAvatarName/"
   ```

### Examples

**Add CyberBee avatar:**
```bash
python avatar_quick_manager.py --add "CyberBee" --source "C:/Downloads/CyberBee/"
```

**Add SpaceBee avatar:**
```bash
python avatar_quick_manager.py --add "SpaceBee" --source "D:/Avatars/SpaceBee/"
```

## Commands

### List all avatars
```bash
python avatar_quick_manager.py --list
```

### Validate all avatars
```bash
python avatar_quick_manager.py --validate
```

### Create backup before changes
```bash
python avatar_quick_manager.py --backup
```

### Show expected file structure
```bash
python avatar_quick_manager.py --example
python avatar_quick_manager.py --example "MyNewBee"
```

## File Requirements

### Naming Convention
- **Folder name:** Must match avatar name exactly (e.g., `CyberBee`)
- **Files must be named:** `AvatarName.obj`, `AvatarName.mtl`, `AvatarName.png`, `AvatarName!.png`
- **Case sensitive:** Make sure capitalization matches

### File Types
- **`.obj`** - 3D model geometry
- **`.mtl`** - Material definition (references textures)
- **`.png`** - Main texture image
- **`!.png`** - Thumbnail for UI (256x256px recommended)

## What the Script Does

1. **Validates** your avatar name and files
2. **Creates** proper folder structure in `/static/Avatars/3D Avatar Files/`
3. **Copies** all files to correct locations
4. **Updates** JavaScript mapping in `user-avatar-loader.js`
5. **Backs up** existing avatars before changes

## Troubleshooting

### Common Issues

**Missing files:**
- Make sure all 4 files exist: `.obj`, `.mtl`, `.png`, `!.png`
- Check file names match folder name exactly

**Avatar already exists:**
- Use `--list` to see current avatars
- Choose a different name or remove existing avatar first

**Source path not found:**
- Use full path: `C:/Users/Jeff/Downloads/MyAvatar/`
- Make sure folder exists and contains files

### Manual Verification

After adding an avatar, check:
1. Files copied to: `/static/Avatars/3D Avatar Files/YourAvatarName/`
2. JavaScript updated in: `/static/js/user-avatar-loader.js`
3. Avatar appears in app's selection screen

## Current Avatar Count

Run `python avatar_quick_manager.py --list` to see all 18+ avatars currently in the system.