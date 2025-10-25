# Enhanced 3D File Generator with Meshy API Integration

This enhanced version of the 3D File Generator now includes powerful Meshy AI integration for advanced 3D model processing and Railway app deployment features.

## 🆕 New Features

### Meshy API Integration
- **AI-Powered Texture Generation**: Create high-quality textures using AI
- **Mesh Refinement**: Optimize and enhance 3D models
- **Multiple Style Options**: Choose from various texture styles
- **Automatic Processing**: Upload, process, and download seamlessly

### Railway App Compatibility
- **Smart File Organization**: Automatically organize files for web deployment
- **PNG Snapshots with '!' Naming**: Distinguishes snapshots from material files
- **GLB Format Support**: Web-optimized 3D model format
- **Asset Management**: Proper file referencing for web applications

### Enhanced GUI
- **Dark Theme**: Professional dark interface
- **Real-time Progress**: Detailed logging of all operations
- **Multiple Processing Options**: Choose between standard and AI processing
- **API Key Management**: Secure handling of Meshy API credentials

## 📋 Requirements

### Python Dependencies
```bash
pip install trimesh pyrender pillow numpy matplotlib requests tkinter
```

### Meshy API Account
1. Sign up at [https://meshy.ai](https://meshy.ai)
2. Get your API key from the dashboard
3. Enter the key in the application settings

## 🚀 Quick Start

### 1. Standard Processing (Existing Functionality)
1. Launch the application: `python 3DFile_FileFolderGenerator.py`
2. Select ZIP files containing OBJ models
3. Choose output directory
4. Click "Convert Files"
5. Optionally create PNG thumbnails

### 2. Meshy AI Processing (New Feature)
1. Enable "Use Meshy API for Processing"
2. Enter your Meshy API key
3. Select texture style
4. Enable "Railway App Ready" for web deployment
5. Click "Meshy Process"

## 📁 File Structure

### Input Files
```
your_model.zip
├── model.obj          # 3D model geometry
├── model.mtl          # Material definitions
├── texture.png        # Texture files
└── normal.png         # Additional texture maps
```

### Output Structure
```
processed_models/
├── ModelName/
│   ├── ModelName.obj           # Cleaned OBJ file
│   ├── ModelName.mtl           # Updated material file
│   ├── ModelName.png           # Primary texture
│   ├── ModelName!.png          # Snapshot (note the '!')
│   └── meshy_processed/        # Meshy API results
│       ├── ModelName_textured.glb
│       ├── ModelName_refined.glb
│       └── ModelName_refined!.png
└── railway_assets/             # Railway-ready files
    ├── ModelName_meshy.glb
    ├── ModelName!.png
    └── ModelName_texture.png
```

## 🎨 Meshy API Features

### Texture Styles Available
- **High Quality, Detailed Textures**: Professional realistic textures
- **Cartoon Style, Vibrant Colors**: Stylized colorful appearance
- **Realistic Materials, PBR Textures**: Physically-based rendering
- **Metallic Finish, Reflective Surfaces**: Metallic and shiny materials
- **Wood Grain, Natural Materials**: Organic textures
- **Fabric Texture, Soft Materials**: Cloth and soft surfaces

### Processing Options
- **Texture Generation**: AI-enhanced texture creation
- **Mesh Refinement**: Geometry optimization
- **Format Conversion**: OBJ to GLB conversion
- **Thumbnail Generation**: High-quality previews

## 🚂 Railway Deployment

### File Naming Convention
- **Model Files**: `ModelName.obj`, `ModelName_meshy.glb`
- **Textures**: `ModelName.png`, `ModelName_Normal.png`
- **Snapshots**: `ModelName!.png` (note the '!' to distinguish from textures)
- **Materials**: `ModelName.mtl`

### Web-Ready Features
- GLB format for optimal web performance
- Proper texture references
- Compressed file sizes
- Cross-platform compatibility

## 🔧 Configuration

### Meshy API Settings
```python
# In 3DFile_FileFolderGenerator.py
MESHY_API_KEY = "your_api_key_here"
MESHY_API_BASE = "https://api.meshy.ai"

# Available texture styles
MESHY_TEXTURE_STYLES = [
    "high quality, detailed textures",
    "cartoon style, vibrant colors",
    "realistic materials, PBR textures",
    # ... more styles
]
```

### File Processing Options
```python
# Thumbnail generation
RENDER_SIZE = (640, 640)
BACKGROUND_COLOR = (0, 0, 0, 1)  # Transparent background

# File naming patterns
# Snapshots use '!' to distinguish from material files
snapshot_name = f"{base_name}!.png"
```

## 📖 Usage Examples

### Basic File Conversion
```python
from pathlib import Path
from 3DFile_FileFolderGenerator import process_model_folder

# Process a folder containing OBJ files
source_folder = Path("path/to/models")
output_folder = Path("path/to/output")
process_model_folder(source_folder, output_folder, {}, False, True, False)
```

### Meshy API Processing
```python
from meshy_api_client import MeshyAPIClient

# Initialize client
client = MeshyAPIClient("your_api_key")

# Process OBJ file
obj_file = Path("model.obj")
output_dir = Path("output")
results = client.process_obj_file(obj_file, output_dir, "realistic materials")

# Check results
if results['success']:
    print(f"Downloaded {len(results['downloaded_files'])} files")
```

### Railway Snapshot Creation
```python
from 3DFile_FileFolderGenerator import create_railway_snapshot

# Create a Railway-compatible snapshot
obj_file = Path("model.obj")
output_dir = Path("railway_assets")
snapshot_path = create_railway_snapshot(obj_file, output_dir)

if snapshot_path:
    print(f"Railway snapshot created: {snapshot_path}")
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies are installed
- Check Python path includes the application directory

**Meshy API Errors**
- Verify API key is correct
- Check internet connection
- Ensure sufficient API credits

**Rendering Issues**
- Try different rendering backends
- Check graphics drivers
- Use fallback thumbnail generation

**File Processing Issues**
- Verify OBJ files are valid
- Check file permissions
- Ensure sufficient disk space

### Debug Mode
Enable verbose logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Migration from Previous Version

Your existing workflows will continue to work unchanged. New features are additive:

1. **Existing ZIP Processing**: Works exactly as before
2. **Thumbnail Generation**: Enhanced with better quality
3. **File Organization**: Improved structure with Railway compatibility
4. **New Features**: Meshy API integration and advanced processing options

## 📞 Support

For issues related to:
- **Core Application**: Check the original documentation
- **Meshy API**: Visit [Meshy.ai Documentation](https://docs.meshy.ai)
- **Railway Deployment**: See [Railway Documentation](https://docs.railway.app)

## 📝 License

This enhanced version maintains the same license as the original application. Meshy API usage is subject to Meshy.ai terms of service.