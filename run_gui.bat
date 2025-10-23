@echo off
echo Starting Enhanced 3D File Processor GUI...
echo.
echo This version separates file processing from thumbnail generation.
echo Basic processing works without additional dependencies.
echo.
echo For thumbnail generation, install these dependencies:
echo   pip install trimesh pyrender pillow numpy "pyglet<2"
echo.
python "3DFile_FileFolderGenerator_GUI_Enhanced.py"
pause