"""
Avatar File Parser - Extract mesh, materials, textures from OBJ files
Intelligent diagnostics for identifying rendering issues
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
import json


@dataclass
class TextureInfo:
    """Texture file information"""
    name: str
    path: str
    type: str  # diffuse, normal, specular, metallic, roughness, etc.
    exists: bool = False
    size_bytes: int = 0
    resolution: Optional[Tuple[int, int]] = None
    format: str = "unknown"
    issues: List[str] = field(default_factory=list)


@dataclass
class MaterialInfo:
    """Material definition from MTL file"""
    name: str
    ambient: Tuple[float, float, float] = (0.2, 0.2, 0.2)
    diffuse: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    specular: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    shininess: float = 32.0
    opacity: float = 1.0
    textures: List[TextureInfo] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


@dataclass
class MeshInfo:
    """Mesh geometry information"""
    name: str
    vertex_count: int = 0
    face_count: int = 0
    normal_count: int = 0
    texture_coord_count: int = 0
    min_bounds: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    max_bounds: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    materials_used: List[str] = field(default_factory=list)
    has_normals: bool = False
    has_texture_coords: bool = False
    issues: List[str] = field(default_factory=list)


@dataclass
class AvatarFileAnalysis:
    """Complete avatar file analysis"""
    avatar_name: str
    file_path: str
    file_size: int
    file_modified: str
    obj_file: str
    mtl_file: Optional[str]
    meshes: List[MeshInfo] = field(default_factory=list)
    materials: List[MaterialInfo] = field(default_factory=list)
    textures: List[TextureInfo] = field(default_factory=list)
    total_issues: int = 0
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)


class AvatarFileParser:
    """Parse and analyze avatar OBJ/MTL files"""

    def __init__(self, avatar_dir: str):
        self.avatar_dir = Path(avatar_dir)
        self.avatar_name = self.avatar_dir.name

    def parse(self) -> AvatarFileAnalysis:
        """Parse avatar files and return complete analysis"""
        analysis = AvatarFileAnalysis(
            avatar_name=self.avatar_name,
            file_path=str(self.avatar_dir),
            file_size=self._get_dir_size(),
            file_modified=self._get_modified_time(),
            obj_file="",
            mtl_file=None
        )

        # Find OBJ file
        obj_file = self._find_obj_file()
        if not obj_file:
            analysis.critical_issues.append(f"No .obj file found in {self.avatar_dir}")
            analysis.total_issues = len(analysis.critical_issues)
            return analysis

        analysis.obj_file = str(obj_file)

        # Find MTL file
        mtl_file = self._find_mtl_file(obj_file)
        if mtl_file:
            analysis.mtl_file = str(mtl_file)
        else:
            analysis.warnings.append(f"No .mtl file found (may affect materials/textures)")

        # Parse OBJ file
        self._parse_obj_file(obj_file, analysis)

        # Parse MTL file if it exists
        if mtl_file:
            self._parse_mtl_file(mtl_file, analysis)

        # Validate textures
        self._validate_textures(analysis)

        # Run diagnostics
        self._run_diagnostics(analysis)

        analysis.total_issues = len(analysis.critical_issues) + len(analysis.warnings)

        return analysis

    def _find_obj_file(self) -> Optional[Path]:
        """Find OBJ file in avatar directory"""
        for file in self.avatar_dir.glob("*.obj"):
            return file
        return None

    def _find_mtl_file(self, obj_file: Path) -> Optional[Path]:
        """Find MTL file referenced in OBJ or in same directory"""
        # Check same directory
        mtl_name = obj_file.stem + ".mtl"
        mtl_path = obj_file.parent / mtl_name
        if mtl_path.exists():
            return mtl_path

        # Search for any MTL file
        for file in self.avatar_dir.glob("*.mtl"):
            return file

        return None

    def _parse_obj_file(self, obj_file: Path, analysis: AvatarFileAnalysis) -> None:
        """Parse OBJ file and extract mesh data"""
        try:
            with open(obj_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            mesh = MeshInfo(name=obj_file.stem)

            # Count vertices, faces, normals, texture coordinates
            mesh.vertex_count = len(re.findall(r'^v\s+', content, re.MULTILINE))
            mesh.face_count = len(re.findall(r'^f\s+', content, re.MULTILINE))
            mesh.normal_count = len(re.findall(r'^vn\s+', content, re.MULTILINE))
            mesh.texture_coord_count = len(re.findall(r'^vt\s+', content, re.MULTILINE))

            # Check for normals and texture coords
            mesh.has_normals = mesh.normal_count > 0
            mesh.has_texture_coords = mesh.texture_coord_count > 0

            # Extract materials used
            mesh.materials_used = re.findall(r'^usemtl\s+(\S+)', content, re.MULTILINE)
            mesh.materials_used = list(set(mesh.materials_used))  # Remove duplicates

            # Extract bounds (rough estimate)
            vertices = re.findall(r'^v\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', content, re.MULTILINE)
            if vertices:
                v_floats = [(float(x), float(y), float(z)) for x, y, z in vertices]
                xs = [v[0] for v in v_floats]
                ys = [v[1] for v in v_floats]
                zs = [v[2] for v in v_floats]
                mesh.min_bounds = (min(xs), min(ys), min(zs))
                mesh.max_bounds = (max(xs), max(ys), max(zs))

            # Diagnostics
            if mesh.vertex_count == 0:
                mesh.issues.append("No vertices found - likely corrupted")
            if mesh.face_count == 0:
                mesh.issues.append("No faces found - mesh is empty")
            if mesh.face_count > 0 and mesh.vertex_count == 0:
                mesh.issues.append("Faces without vertices - malformed geometry")
            if not mesh.has_normals:
                mesh.warnings.append("No normals - lighting may look flat")
            if mesh.face_count > 0 and mesh.vertex_count > 0:
                if mesh.face_count / mesh.vertex_count > 10:
                    mesh.issues.append(f"Unusually high face-to-vertex ratio ({mesh.face_count}/{mesh.vertex_count}) - may be corrupted")

            analysis.meshes.append(mesh)

        except Exception as e:
            analysis.critical_issues.append(f"Error parsing OBJ file: {str(e)}")

    def _parse_mtl_file(self, mtl_file: Path, analysis: AvatarFileAnalysis) -> None:
        """Parse MTL file and extract material/texture info"""
        try:
            with open(mtl_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            current_material = None

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                cmd = parts[0]

                # New material definition
                if cmd == 'newmtl':
                    if current_material:
                        analysis.materials.append(current_material)
                    current_material = MaterialInfo(name=parts[1] if len(parts) > 1 else "Unknown")

                # Color values
                elif cmd in ['Ka', 'Kd', 'Ks'] and current_material and len(parts) >= 4:
                    values = (float(parts[1]), float(parts[2]), float(parts[3]))
                    if cmd == 'Ka':
                        current_material.ambient = values
                    elif cmd == 'Kd':
                        current_material.diffuse = values
                    elif cmd == 'Ks':
                        current_material.specular = values

                # Shininess
                elif cmd == 'Ns' and current_material and len(parts) > 1:
                    current_material.shininess = float(parts[1])

                # Transparency
                elif cmd in ['d', 'Tr'] and current_material and len(parts) > 1:
                    current_material.opacity = float(parts[1])

                # Texture maps
                elif cmd.startswith('map_') and current_material and len(parts) > 1:
                    texture_type = cmd.replace('map_', '')
                    texture_path = ' '.join(parts[1:])
                    texture_info = TextureInfo(
                        name=Path(texture_path).name,
                        path=texture_path,
                        type=texture_type
                    )
                    current_material.textures.append(texture_info)

            # Add final material
            if current_material:
                analysis.materials.append(current_material)

        except Exception as e:
            analysis.warnings.append(f"Error parsing MTL file: {str(e)}")

    def _validate_textures(self, analysis: AvatarFileAnalysis) -> None:
        """Check if texture files exist and are valid"""
        base_dir = self.avatar_dir

        for material in analysis.materials:
            for texture in material.textures:
                # Try multiple path resolution strategies
                possible_paths = [
                    base_dir / texture.path,
                    base_dir / texture.name,
                    base_dir / "textures" / texture.name,
                    base_dir / "Textures" / texture.name,
                ]

                found = False
                for path in possible_paths:
                    if path.exists():
                        texture.exists = True
                        texture.size_bytes = path.stat().st_size
                        texture.format = path.suffix.lower()
                        found = True
                        analysis.textures.append(texture)
                        break

                if not found:
                    texture.issues.append(f"Texture file not found: {texture.path}")
                    material.issues.append(f"Missing texture: {texture.name} ({texture.type})")
                    analysis.warnings.append(f"Missing texture in material '{material.name}': {texture.name}")

    def _run_diagnostics(self, analysis: AvatarFileAnalysis) -> None:
        """Run comprehensive diagnostics and generate intelligent findings"""
        
        # Collect all issues
        for mesh in analysis.meshes:
            for issue in mesh.issues:
                analysis.critical_issues.append(f"[Mesh] {issue}")

        for material in analysis.materials:
            for issue in material.issues:
                analysis.warnings.append(f"[Material] {issue}")

        # Smart diagnostics
        if len(analysis.materials) == 0 and not analysis.mtl_file:
            analysis.warnings.append("No materials defined - avatar may render as untextured/white")

        if len(analysis.meshes) > 0:
            total_verts = sum(m.vertex_count for m in analysis.meshes)
            total_faces = sum(m.face_count for m in analysis.meshes)

            if total_verts == 0:
                analysis.critical_issues.append("CRITICAL: No mesh data found - avatar is empty")
            elif total_faces == 0:
                analysis.critical_issues.append("CRITICAL: No faces in mesh - geometry is corrupted")

            meshes_without_normals = sum(1 for m in analysis.meshes if not m.has_normals)
            if meshes_without_normals > 0:
                analysis.info.append(f"{meshes_without_normals} mesh(es) missing vertex normals - shading will be compromised")

            meshes_without_texcoords = sum(1 for m in analysis.meshes if not m.has_texture_coords)
            if meshes_without_texcoords > 0 and len(analysis.textures) > 0:
                analysis.warnings.append(f"{meshes_without_texcoords} mesh(es) missing texture coordinates - textures won't map")

    def _get_dir_size(self) -> int:
        """Calculate total directory size"""
        total = 0
        for entry in self.avatar_dir.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total

    def _get_modified_time(self) -> str:
        """Get latest modification time in directory"""
        try:
            latest = max((entry.stat().st_mtime for entry in self.avatar_dir.rglob("*") if entry.is_file()), default=0)
            from datetime import datetime
            return datetime.fromtimestamp(latest).isoformat()
        except:
            return "Unknown"

    def to_dict(self) -> dict:
        """Convert analysis to dictionary"""
        return {
            "avatar_name": self.avatar_name,
            "file_path": str(self.avatar_dir),
            "file_size": asdict(AvatarFileAnalysis(
                avatar_name=self.avatar_name,
                file_path=str(self.avatar_dir),
                file_size=self._get_dir_size(),
                file_modified=self._get_modified_time(),
                obj_file="",
                mtl_file=None
            ))["file_size"],
        }


class AvatarDeltaComparator:
    """Compare two avatars and identify differences"""

    @staticmethod
    def compare(working_analysis: AvatarFileAnalysis, broken_analysis: AvatarFileAnalysis) -> dict:
        """Compare two avatar analyses and return intelligent findings"""
        
        delta = {
            "comparison": {
                "working": working_analysis.avatar_name,
                "broken": broken_analysis.avatar_name,
            },
            "summary": {
                "working_issues": len(working_analysis.critical_issues),
                "broken_issues": len(broken_analysis.critical_issues),
                "issue_delta": len(broken_analysis.critical_issues) - len(working_analysis.critical_issues),
            },
            "mesh_differences": {},
            "material_differences": {},
            "texture_differences": {},
            "diagnostic_findings": [],
            "suggested_fixes": []
        }

        # Mesh comparison
        working_total_verts = sum(m.vertex_count for m in working_analysis.meshes)
        broken_total_verts = sum(m.vertex_count for m in broken_analysis.meshes)
        working_total_faces = sum(m.face_count for m in working_analysis.meshes)
        broken_total_faces = sum(m.face_count for m in broken_analysis.meshes)

        delta["mesh_differences"] = {
            "working": {"vertices": working_total_verts, "faces": working_total_faces},
            "broken": {"vertices": broken_total_verts, "faces": broken_total_faces},
            "delta": {
                "vertex_delta": broken_total_verts - working_total_verts,
                "face_delta": broken_total_faces - working_total_faces
            }
        }

        # Material comparison
        delta["material_differences"] = {
            "working_count": len(working_analysis.materials),
            "broken_count": len(broken_analysis.materials),
            "delta": len(broken_analysis.materials) - len(working_analysis.materials)
        }

        # Texture comparison
        working_textures = sum(len(m.textures) for m in working_analysis.materials)
        broken_textures = sum(len(m.textures) for m in broken_analysis.materials)

        delta["texture_differences"] = {
            "working_count": working_textures,
            "broken_count": broken_textures,
            "delta": broken_textures - working_textures,
            "working_textures": len([t for t in working_analysis.textures if t.exists]),
            "broken_textures": len([t for t in broken_analysis.textures if t.exists]),
        }

        # Intelligent findings
        if broken_total_verts == 0:
            delta["diagnostic_findings"].append("🔴 CRITICAL: Broken avatar has NO mesh data - file is corrupted")
            delta["suggested_fixes"].append("The broken avatar file appears to be corrupted. Try re-exporting from the 3D model tool.")

        if broken_total_verts < working_total_verts * 0.5:
            delta["diagnostic_findings"].append(f"⚠️ Broken avatar has significantly fewer vertices ({broken_total_verts} vs {working_total_verts})")
            delta["suggested_fixes"].append("The mesh may be incomplete or truncated. Check if the file was properly saved.")

        if len(broken_analysis.materials) < len(working_analysis.materials):
            delta["diagnostic_findings"].append(f"⚠️ Missing materials: {len(working_analysis.materials)} → {len(broken_analysis.materials)}")
            delta["suggested_fixes"].append("Re-assign materials in the 3D editor and re-export.")

        missing_textures = len([t for t in broken_analysis.textures if not t.exists])
        if missing_textures > 0:
            delta["diagnostic_findings"].append(f"🔴 Missing texture files: {missing_textures}")
            delta["suggested_fixes"].append("Ensure all texture files are in the same directory as the avatar.")

        if len(broken_analysis.critical_issues) > len(working_analysis.critical_issues):
            delta["diagnostic_findings"].append("The broken avatar has more critical issues than the working reference.")

        return delta
