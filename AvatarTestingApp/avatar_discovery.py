"""
Avatar Discovery Module - Scans and categorizes BeeSmart avatars
"""

from pathlib import Path
import os


class AvatarDiscovery:
    """Discovers and categorizes avatars from static folder"""
    
    def __init__(self):
        # BeeSmart avatars location - try multiple paths
        self.static_paths = [
            Path('../static/Avatars/3D Avatar Files'),  # Relative from AvatarTestingApp
            Path('../../static/Avatars/3D Avatar Files'),  # Alternative relative path
            Path('C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/static/Avatars/3D Avatar Files'),  # Absolute path
        ]
        
        # Known working avatars (from existing code)
        self.working_names = {
            'AlBee', 'AnxiousBee', 'MascotBee', 'MonsterBee', 'ProfessorBee',
            'RockerBee', 'VampBee', 'WareBee', 'ZomBee'
        }
        
        # Known broken avatars (rest)
        self.broken_names = {
            'BikerBee', 'BrotherBee', 'BuilderBee', 'CoolBee', 'DivaBee',
            'DoctorBee', 'ExplorerBee', 'KnightBee', 'QueenBee', 'RoboBee',
            'Seabea', 'Superbee', 'AstroBee', 'DetectiveBee', 'Frankenbee'
        }
    
    def get_avatar_list(self):
        """Get categorized list of avatars from static folder"""
        working = []
        broken = []
        
        # Find the first valid path
        static_path = None
        for path in self.static_paths:
            if path.exists():
                static_path = path
                break
        
        # Check if any path exists
        if not static_path:
            return {
                'working': [],
                'broken': [],
                'total': 0,
                'working_count': 0,
                'broken_count': 0
            }
        
        # Scan for avatar subdirectories and find .obj/.glb files
        for avatar_dir in sorted(static_path.iterdir()):
            if not avatar_dir.is_dir():
                continue
            
            name = avatar_dir.name
            
            # Look for .obj or .glb file
            obj_file = avatar_dir / f"{name}.obj"
            glb_file = avatar_dir / f"{name}.glb"
            
            file_path = None
            file_type = None
            
            if obj_file.exists():
                file_path = obj_file
                file_type = 'obj'
            elif glb_file.exists():
                file_path = glb_file
                file_type = 'glb'
            else:
                # Skip if no model file found
                continue
            
            size_bytes = file_path.stat().st_size if file_path.exists() else 0
            
            avatar_info = {
                'name': name,
                'path': str(file_path),
                'file_type': file_type,
                'size_bytes': size_bytes
            }
            
            # Categorize based on known lists
            if name in self.working_names:
                working.append(avatar_info)
            elif name in self.broken_names:
                broken.append(avatar_info)
            else:
                # Default to broken if unknown
                broken.append(avatar_info)
        
        return {
            'working': sorted(working, key=lambda x: x['name']),
            'broken': sorted(broken, key=lambda x: x['name']),
            'total': len(working) + len(broken),
            'working_count': len(working),
            'broken_count': len(broken)
        }
