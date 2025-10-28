"""
Avatar Analyzer Module - Analyzes 3D model attributes
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import trimesh


@dataclass
class MeshData:
    """Mesh geometry data"""
    vertex_count: int = 0
    face_count: int = 0
    has_normals: bool = False
    has_uvs: bool = False


@dataclass
class MaterialData:
    """Material properties"""
    name: str
    color: Optional[tuple] = None
    transparency: Optional[float] = None
    textures: Dict = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.textures is None:
            self.textures = {}
        if self.issues is None:
            self.issues = []


@dataclass
class BoneData:
    """Rigging bone data"""
    name: str
    position: tuple = (0, 0, 0)
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class RiggingData:
    """Skeleton/rigging data"""
    bone_count: int = 0
    bones: List[BoneData] = None
    
    def __post_init__(self):
        if self.bones is None:
            self.bones = []


@dataclass
class AvatarAnalysis:
    """Complete avatar analysis"""
    filename: str
    mesh: MeshData = None
    materials: List[MaterialData] = None
    rigging: RiggingData = None
    
    def __post_init__(self):
        if self.mesh is None:
            self.mesh = MeshData()
        if self.materials is None:
            self.materials = []
        if self.rigging is None:
            self.rigging = RiggingData()


class AvatarAnalyzer:
    """Analyzes 3D avatar models using trimesh"""
    
    def __init__(self, upload_folder='avatars'):
        self.upload_folder = upload_folder
    
    def analyze_file(self, file_path: str) -> AvatarAnalysis:
        """Analyze a 3D model file"""
        try:
            # Load model
            mesh = trimesh.load(file_path, force='mesh')
            
            # Extract mesh data
            mesh_data = MeshData(
                vertex_count=len(mesh.vertices) if hasattr(mesh, 'vertices') else 0,
                face_count=len(mesh.faces) if hasattr(mesh, 'faces') else 0,
                has_normals=hasattr(mesh, 'vertex_normals') and len(mesh.vertex_normals) > 0,
                has_uvs=False  # Would need to check visual properties
            )
            
            # Analyze materials (basic)
            materials = []
            if hasattr(mesh, 'visual') and mesh.visual:
                # Try to get color information
                try:
                    visual = mesh.visual
                    if hasattr(visual, 'vertex_colors'):
                        mat = MaterialData(
                            name='default',
                            color=tuple(visual.vertex_colors[0][:3]) if len(visual.vertex_colors) > 0 else None,
                            transparency=None
                        )
                        materials.append(mat)
                except:
                    pass
            
            if not materials:
                materials.append(MaterialData(name='default'))
            
            # Create analysis
            analysis = AvatarAnalysis(
                filename=file_path,
                mesh=mesh_data,
                materials=materials,
                rigging=RiggingData(bone_count=0, bones=[])
            )
            
            return analysis
            
        except Exception as e:
            # Return failed analysis
            return AvatarAnalysis(
                filename=file_path,
                mesh=MeshData(),
                materials=[MaterialData(name='error', issues=[str(e)])],
                rigging=RiggingData()
            )
    
    def compare_avatars(self, working: AvatarAnalysis, broken: AvatarAnalysis) -> Dict:
        """Compare two avatars and generate delta"""
        return {
            'vertex_diff': broken.mesh.vertex_count - working.mesh.vertex_count,
            'face_diff': broken.mesh.face_count - working.mesh.face_count,
            'has_normals_working': working.mesh.has_normals,
            'has_normals_broken': broken.mesh.has_normals,
            'material_count_working': len(working.materials),
            'material_count_broken': len(broken.materials),
            'issues': []
        }


def serialize_analysis(analysis: AvatarAnalysis) -> Dict:
    """Serialize analysis to JSON-compatible dict"""
    return {
        'filename': analysis.filename,
        'mesh': asdict(analysis.mesh),
        'materials': [
            {
                'name': m.name,
                'color': m.color,
                'transparency': m.transparency,
                'textures': m.textures,
                'issues': m.issues
            }
            for m in analysis.materials
        ],
        'rigging': {
            'bone_count': analysis.rigging.bone_count,
            'bones': [
                {'name': b.name, 'position': b.position, 'issues': b.issues}
                for b in analysis.rigging.bones
            ]
        }
    }


def serialize_delta(delta: Dict) -> Dict:
    """Serialize delta analysis to JSON-compatible dict"""
    return delta
