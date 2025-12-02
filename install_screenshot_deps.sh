#!/bin/bash
# Install dependencies for avatar screenshot generator

echo "📦 Installing dependencies for avatar screenshot generator..."
echo ""

pip3 install trimesh pyrender pillow numpy pyglet || {
    echo "❌ Installation failed"
    exit 1
}

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "🎨 Run the screenshot generator with:"
echo "   python3 generate_avatar_screenshots.py"
