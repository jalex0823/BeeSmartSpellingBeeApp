"""
Create Fairy Bee Thumbnail from GLB File
========================================
Renders FairyBee.glb and saves a thumbnail image.
"""

import os
import sys
from pathlib import Path

try:
    import trimesh
    import pyglet
    from PIL import Image
    import numpy as np
except ImportError:
    print("Installing required packages...")
    os.system("pip install trimesh pyglet pillow pyrender")
    import trimesh
    import pyglet
    from PIL import Image
    import numpy as np

def create_thumbnail_from_glb(glb_path, output_path, size=(512, 512)):
    """
    Load GLB file and create a thumbnail PNG.
    """
    try:
        print(f"Loading GLB file: {glb_path}")
        
        # Load the GLB file
        scene = trimesh.load(str(glb_path))
        
        if isinstance(scene, trimesh.Scene):
            # Get all meshes from scene
            mesh = trimesh.util.concatenate([
                geom for geom in scene.geometry.values() 
                if isinstance(geom, trimesh.Trimesh)
            ])
        else:
            mesh = scene
        
        print(f"Loaded mesh with {len(mesh.vertices)} vertices")
        
        # Create a simple rendering using pyrender
        try:
            import pyrender
            
            # Create scene
            render_scene = pyrender.Scene()
            render_mesh = pyrender.Mesh.from_trimesh(mesh)
            render_scene.add(render_mesh)
            
            # Add camera
            camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
            camera_pose = np.array([
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 3.0],
                [0.0, 0.0, 0.0, 1.0]
            ])
            render_scene.add(camera, pose=camera_pose)
            
            # Add light
            light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=3.0)
            render_scene.add(light, pose=camera_pose)
            
            # Render
            r = pyrender.OffscreenRenderer(*size)
            color, depth = r.render(render_scene)
            
            # Save image
            img = Image.fromarray(color)
            img.save(output_path)
            print(f"✅ Thumbnail saved: {output_path}")
            
        except ImportError:
            print("⚠️ pyrender not available, creating placeholder thumbnail...")
            # Create a placeholder with text
            img = Image.new('RGB', size, color=(255, 215, 0))  # Gold background
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            text = "Fairy Bee"
            # Use default font
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
            draw.text(position, text, fill=(0, 0, 0))
            img.save(output_path)
            print(f"✅ Placeholder thumbnail saved: {output_path}")
            print("   For better results, install pyrender: pip install pyrender")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating thumbnail: {e}")
        print("\nCreating simple placeholder...")
        
        # Create basic placeholder
        img = Image.new('RGBA', size, color=(255, 215, 0, 255))  # Gold
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Draw a simple bee shape
        center_x, center_y = size[0] // 2, size[1] // 2
        draw.ellipse([center_x - 100, center_y - 100, center_x + 100, center_y + 100], 
                     fill=(255, 193, 7, 255), outline=(0, 0, 0, 255))
        img.save(output_path)
        print(f"✅ Basic placeholder saved: {output_path}")
        return True

if __name__ == "__main__":
    glb_file = Path("static/assets/avatars/glb_files/FairyBee.glb")
    output_file = Path("static/assets/avatars/glb_files/AvatarThumbnails/FairyBee!.png")
    
    if not glb_file.exists():
        print(f"❌ GLB file not found: {glb_file}")
        sys.exit(1)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n🐝 Creating Fairy Bee Thumbnail")
    print("=" * 60)
    
    success = create_thumbnail_from_glb(glb_file, output_file)
    
    if success:
        print("\n✅ Thumbnail creation complete!")
        print(f"   File: {output_file}")
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"   Size: {size_kb:.2f} KB")
    else:
        print("\n❌ Failed to create thumbnail")
        sys.exit(1)
