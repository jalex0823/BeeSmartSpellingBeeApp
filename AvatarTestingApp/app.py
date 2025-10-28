"""
Avatar Comparison API - Flask Backend
RESTful endpoints for avatar analysis and comparison
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import traceback
from avatar_analyzer import AvatarAnalyzer, serialize_analysis, serialize_delta
from avatar_discovery import AvatarDiscovery
from avatar_file_parser import AvatarFileParser, AvatarDeltaComparator, AvatarFileAnalysis

# Configuration
UPLOAD_FOLDER = 'avatars'
ALLOWED_EXTENSIONS = {'gltf', 'glb', 'fbx', 'obj'}

# Create Flask app
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize analyzer
analyzer = AvatarAnalyzer(UPLOAD_FOLDER)

# Initialize avatar discovery
avatar_discovery = AvatarDiscovery()

# BeeSmart Spelling Bee Avatar Database
AVATAR_DATABASE = {
    # Working avatars
    'working': {
        'Al Bee': {'file': 'working/Al_Bee.glb', 'status': 'working'},
        'Anxious Bee': {'file': 'working/Anxious_Bee.glb', 'status': 'working'},
        'Mascot Bee': {'file': 'working/Mascot_Bee.glb', 'status': 'working'},
        'Monster Bee': {'file': 'working/Monster_Bee.glb', 'status': 'working'},
        'Professor Bee': {'file': 'working/Professor_Bee.glb', 'status': 'working'},
        'Rocker Bee': {'file': 'working/Rocker_Bee.glb', 'status': 'working'},
        'Vamp Bee': {'file': 'working/Vamp_Bee.glb', 'status': 'working'},
        'Ware Bee': {'file': 'working/Ware_Bee.glb', 'status': 'working'},
        'Zom Bee': {'file': 'working/Zom_Bee.glb', 'status': 'working'},
    },
    # Non-rendering white blob avatars
    'broken': {
        'Doctor Bee': {'file': 'broken/Doctor_Bee.glb', 'status': 'white_blob'},
        'Knight Bee': {'file': 'broken/Knight_Bee.glb', 'status': 'white_blob'},
        'Builder Bee': {'file': 'broken/Builder_Bee.glb', 'status': 'white_blob'},
        'Buzzbot Bee': {'file': 'broken/Buzzbot_Bee.glb', 'status': 'white_blob'},
        'Buzzhero Bee': {'file': 'broken/Buzzhero_Bee.glb', 'status': 'white_blob'},
        'Detective Bee': {'file': 'broken/Detective_Bee.glb', 'status': 'white_blob'},
        'Explorer Bee': {'file': 'broken/Explorer_Bee.glb', 'status': 'white_blob'},
        'Franken Bee': {'file': 'broken/Franken_Bee.glb', 'status': 'white_blob'},
        'Motorcyclebuzz Bee': {'file': 'broken/Motorcyclebuzz_Bee.glb', 'status': 'white_blob'},
        'Queen Bee Majesty': {'file': 'broken/Queen_Bee_Majesty.glb', 'status': 'white_blob'},
        'Space Bee Explorer': {'file': 'broken/Space_Bee_Explorer.glb', 'status': 'white_blob'},
        'Super Bee Hero': {'file': 'broken/Super_Bee_Hero.glb', 'status': 'white_blob'},
        'Sea Bee': {'file': 'broken/Sea_Bee.glb', 'status': 'white_blob'},
    }
}


@app.route('/api/avatars', methods=['GET'])
def list_avatars():
    """List all available avatars from static folder"""
    try:
        avatar_list = avatar_discovery.get_avatar_list()
        
        # Format for frontend
        working_avatars = [
            {
                'name': avatar['name'],
                'path': avatar['path'],
                'type': avatar['file_type'],
                'status': 'working',
                'size': avatar['size_bytes']
            }
            for avatar in avatar_list['working']
        ]
        
        broken_avatars = [
            {
                'name': avatar['name'],
                'path': avatar['path'],
                'type': avatar['file_type'],
                'status': 'broken',
                'size': avatar['size_bytes']
            }
            for avatar in avatar_list['broken']
        ]
        
        return jsonify({
            'success': True,
            'working': working_avatars,
            'broken': broken_avatars,
            'total': avatar_list['total'],
            'working_count': avatar_list['working_count'],
            'broken_count': avatar_list['broken_count']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a single avatar"""
    try:
        data = request.json
        avatar_name = data.get('name')
        
        if not avatar_name:
            return jsonify({'success': False, 'error': 'Avatar name required'}), 400
        
        # Find avatar in database
        file_path = None
        for category, items in AVATAR_DATABASE.items():
            if avatar_name in items:
                file_path = items[avatar_name]['file']
                break
        
        if not file_path:
            return jsonify({'success': False, 'error': 'Avatar not found'}), 404
        
        # Analyze
        analysis = analyzer.analyze_file(file_path)
        
        return jsonify({
            'success': True,
            'analysis': serialize_analysis(analysis)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare():
    """Compare two avatars and generate delta analysis"""
    try:
        data = request.json
        working_name = data.get('working')
        broken_name = data.get('broken')
        
        if not working_name or not broken_name:
            return jsonify({'success': False, 'error': 'Working and broken avatar names required'}), 400
        
        # Find avatars in database
        working_file = None
        broken_file = None
        
        for category, items in AVATAR_DATABASE.items():
            if working_name in items:
                working_file = items[working_name]['file']
            if broken_name in items:
                broken_file = items[broken_name]['file']
        
        if not working_file or not broken_file:
            return jsonify({'success': False, 'error': 'One or both avatars not found'}), 404
        
        # Analyze both
        working_analysis = analyzer.analyze_file(working_file)
        broken_analysis = analyzer.analyze_file(broken_file)
        
        # Compare
        delta = analyzer.compare_avatars(working_analysis, broken_analysis)
        
        return jsonify({
            'success': True,
            'working': serialize_analysis(working_analysis),
            'broken': serialize_analysis(broken_analysis),
            'delta': serialize_delta(delta)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/compare/bulk', methods=['POST'])
def compare_bulk():
    """Compare multiple broken avatars against a working reference"""
    try:
        data = request.json
        working_name = data.get('working')
        broken_names = data.get('broken', [])
        
        if not working_name:
            return jsonify({'success': False, 'error': 'Working avatar name required'}), 400
        
        # Find working avatar
        working_file = None
        for category, items in AVATAR_DATABASE.items():
            if working_name in items:
                working_file = items[working_name]['file']
                break
        
        if not working_file:
            return jsonify({'success': False, 'error': f'Working avatar "{working_name}" not found'}), 404
        
        # Analyze working once
        working_analysis = analyzer.analyze_file(working_file)
        
        # Compare against each broken avatar
        results = []
        for broken_name in broken_names:
            try:
                broken_file = None
                for category, items in AVATAR_DATABASE.items():
                    if broken_name in items:
                        broken_file = items[broken_name]['file']
                        break
                
                if not broken_file:
                    results.append({
                        'broken_avatar': broken_name,
                        'success': False,
                        'error': 'Not found'
                    })
                    continue
                
                # Analyze broken
                broken_analysis = analyzer.analyze_file(broken_file)
                
                # Compare
                delta = analyzer.compare_avatars(working_analysis, broken_analysis)
                
                results.append({
                    'broken_avatar': broken_name,
                    'success': True,
                    'delta': serialize_delta(delta)
                })
            
            except Exception as e:
                results.append({
                    'broken_avatar': broken_name,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'working_avatar': working_name,
            'working_analysis': serialize_analysis(working_analysis),
            'comparisons': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Get detailed diagnostic report for why avatar renders as white blob"""
    try:
        data = request.json
        avatar_name = data.get('avatar')
        reference_name = data.get('reference')
        
        if not avatar_name:
            return jsonify({'success': False, 'error': 'Avatar name required'}), 400
        
        # Find avatar
        avatar_file = None
        for category, items in AVATAR_DATABASE.items():
            if avatar_name in items:
                avatar_file = items[avatar_name]['file']
                break
        
        if not avatar_file:
            return jsonify({'success': False, 'error': 'Avatar not found'}), 404
        
        # Analyze
        analysis = analyzer.analyze_file(avatar_file)
        
        # Generate diagnostic report
        report = {
            'avatar': avatar_name,
            'analysis': serialize_analysis(analysis),
            'diagnosis': generate_diagnostic_report(analysis),
        }
        
        # If reference provided, compare
        if reference_name:
            ref_file = None
            for category, items in AVATAR_DATABASE.items():
                if reference_name in items:
                    ref_file = items[reference_name]['file']
                    break
            
            if ref_file:
                ref_analysis = analyzer.analyze_file(ref_file)
                delta = analyzer.compare_avatars(ref_analysis, analysis)
                report['comparison'] = serialize_delta(delta)
        
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def generate_diagnostic_report(analysis):
    """Generate a diagnostic report explaining rendering issues"""
    issues = {
        'critical': [],
        'warnings': [],
        'suggestions': [],
    }
    
    # Check mesh
    if analysis.mesh.vertex_count == 0:
        issues['critical'].append("No vertices - mesh is empty")
    
    if analysis.mesh.face_count == 0:
        issues['critical'].append("No faces - mesh has no geometry")
    
    if not analysis.mesh.has_normals:
        issues['warnings'].append("Missing vertex normals - may cause shading issues")
    
    if not analysis.mesh.has_uvs:
        issues['critical'].append("Missing UV coordinates - textures cannot render")
    
    # Check materials
    if not analysis.materials:
        issues['warnings'].append("No materials defined")
    
    for mat in analysis.materials:
        if mat.issues:
            for issue in mat.issues:
                issues['warnings'].append(f"Material '{mat.name}': {issue}")
        
        if not mat.textures:
            issues['warnings'].append(f"Material '{mat.name}' has no textures")
        else:
            for tex_name, tex in mat.textures.items():
                if tex.issues:
                    for issue in tex.issues:
                        issues['critical'].append(f"Texture issue: {issue}")
    
    # Check rigging
    if analysis.rigging.bone_count == 0:
        issues['warnings'].append("No rigging/skeleton found")
    
    for bone in analysis.rigging.bones:
        if bone.issues:
            for issue in bone.issues:
                issues['warnings'].append(f"Bone '{bone.name}': {issue}")
    
    # Generate suggestions
    if issues['critical']:
        issues['suggestions'].append("Critical issues found - model may not render correctly")
    
    if 'No UV coordinates' in str(issues['critical']):
        issues['suggestions'].append("Re-export with UV mapping enabled")
    
    if 'Missing vertex normals' in str(issues['warnings']):
        issues['suggestions'].append("Recalculate vertex normals in 3D editor before export")
    
    return issues


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'avatar-analyzer'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
    
    # Run Flask app
    app.run(debug=False, port=5000, host='127.0.0.1')


# ============================================
# DEEP AVATAR DELTA ANALYZER ENDPOINTS
# ============================================

@app.route('/api/analyze/file/<avatar_name>', methods=['GET'])
def analyze_avatar_file(avatar_name):
    """Deep file analysis of a single avatar"""
    try:
        # Find avatar directory - use relative path from app directory
        avatar_dir = None
        # Try multiple path options (in order of preference)
        possible_paths = [
            Path('../static/Avatars/3D Avatar Files'),  # Relative path from AvatarTestingApp
            Path(r'C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\static\Avatars\3D Avatar Files'),  # Absolute path
            Path('static/Avatars/3D Avatar Files'),  # Alternative relative path
        ]
        
        base_path = None
        for path in possible_paths:
            if path.exists():
                base_path = path
                break
        
        if not base_path:
            return jsonify({"error": f"Avatar directory not found at any of: {[str(p) for p in possible_paths]}"}), 500
        
        if base_path.exists():
            for subdir in base_path.iterdir():
                if subdir.is_dir() and subdir.name.lower() == avatar_name.lower():
                    avatar_dir = subdir
                    break
        
        if not avatar_dir:
            return jsonify({"error": f"Avatar '{avatar_name}' not found"}), 404
        
        # Parse avatar
        parser = AvatarFileParser(str(avatar_dir))
        analysis = parser.parse()
        
        # Convert to JSON-serializable format
        result = {
            "avatar_name": analysis.avatar_name,
            "file_path": analysis.file_path,
            "file_size": analysis.file_size,
            "file_modified": analysis.file_modified,
            "obj_file": analysis.obj_file,
            "mtl_file": analysis.mtl_file,
            "meshes": [
                {
                    "name": m.name,
                    "vertex_count": m.vertex_count,
                    "face_count": m.face_count,
                    "normal_count": m.normal_count,
                    "texture_coord_count": m.texture_coord_count,
                    "min_bounds": m.min_bounds,
                    "max_bounds": m.max_bounds,
                    "materials_used": m.materials_used,
                    "has_normals": m.has_normals,
                    "has_texture_coords": m.has_texture_coords,
                    "issues": m.issues
                } for m in analysis.meshes
            ],
            "materials": [
                {
                    "name": m.name,
                    "ambient": m.ambient,
                    "diffuse": m.diffuse,
                    "specular": m.specular,
                    "shininess": m.shininess,
                    "opacity": m.opacity,
                    "texture_count": len(m.textures),
                    "textures": [
                        {
                            "name": t.name,
                            "path": t.path,
                            "type": t.type,
                            "exists": t.exists,
                            "size_bytes": t.size_bytes,
                            "format": t.format,
                            "issues": t.issues
                        } for t in m.textures
                    ],
                    "issues": m.issues
                } for m in analysis.materials
            ],
            "summary": {
                "total_meshes": len(analysis.meshes),
                "total_materials": len(analysis.materials),
                "total_textures": len(analysis.textures),
                "total_issues": analysis.total_issues,
                "critical_issues": analysis.critical_issues,
                "warnings": analysis.warnings,
                "info": analysis.info
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/compare/delta', methods=['POST'])
def compare_avatars_delta():
    """Compare two avatars and return detailed delta analysis"""
    try:
        data = request.get_json()
        working_name = data.get('working')
        broken_name = data.get('broken')
        
        if not working_name or not broken_name:
            return jsonify({"error": "Missing 'working' or 'broken' avatar names"}), 400
        
        # Find avatar directories - use relative path from app directory
        possible_paths = [
            Path('../static/Avatars/3D Avatar Files'),  # Relative path from AvatarTestingApp
            Path(r'C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\static\Avatars\3D Avatar Files'),  # Absolute path
            Path('static/Avatars/3D Avatar Files'),  # Alternative relative path
        ]
        
        base_path = None
        for path in possible_paths:
            if path.exists():
                base_path = path
                break
        
        if not base_path:
            return jsonify({"error": f"Avatar directory not found at any of: {[str(p) for p in possible_paths]}"}), 500
        
        working_dir = None
        broken_dir = None
        
        if base_path.exists():
            for subdir in base_path.iterdir():
                if subdir.is_dir():
                    if subdir.name.lower() == working_name.lower():
                        working_dir = subdir
                    elif subdir.name.lower() == broken_name.lower():
                        broken_dir = subdir
        
        if not working_dir or not broken_dir:
            return jsonify({"error": "One or both avatars not found"}), 404
        
        # Parse both avatars
        working_parser = AvatarFileParser(str(working_dir))
        broken_parser = AvatarFileParser(str(broken_dir))
        
        working_analysis = working_parser.parse()
        broken_analysis = broken_parser.parse()
        
        # Perform delta comparison
        delta = AvatarDeltaComparator.compare(working_analysis, broken_analysis)
        
        # Add individual analyses
        delta["working_analysis"] = {
            "meshes": len(working_analysis.meshes),
            "materials": len(working_analysis.materials),
            "textures": len([t for t in working_analysis.textures if t.exists]),
            "critical_issues": working_analysis.critical_issues,
            "warnings": working_analysis.warnings
        }
        
        delta["broken_analysis"] = {
            "meshes": len(broken_analysis.meshes),
            "materials": len(broken_analysis.materials),
            "textures": len([t for t in broken_analysis.textures if t.exists]),
            "critical_issues": broken_analysis.critical_issues,
            "warnings": broken_analysis.warnings
        }
        
        return jsonify(delta), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/diagnose/<avatar_name>', methods=['GET'])
def diagnose_avatar(avatar_name):
    """Generate comprehensive diagnostic report for an avatar"""
    try:
        # Find avatar directory - use relative path from app directory
        possible_paths = [
            Path('../static/Avatars/3D Avatar Files'),  # Relative path from AvatarTestingApp
            Path(r'C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\static\Avatars\3D Avatar Files'),  # Absolute path
            Path('static/Avatars/3D Avatar Files'),  # Alternative relative path
        ]
        
        base_path = None
        for path in possible_paths:
            if path.exists():
                base_path = path
                break
        
        if not base_path:
            return jsonify({"error": f"Avatar directory not found at any of: {[str(p) for p in possible_paths]}"}), 500
        
        avatar_dir = None
        
        if base_path.exists():
            for subdir in base_path.iterdir():
                if subdir.is_dir() and subdir.name.lower() == avatar_name.lower():
                    avatar_dir = subdir
                    break
        
        if not avatar_dir:
            return jsonify({"error": f"Avatar '{avatar_name}' not found"}), 404
        
        # Parse avatar
        parser = AvatarFileParser(str(avatar_dir))
        analysis = parser.parse()
        
        # Generate diagnostic report
        report = {
            "avatar_name": analysis.avatar_name,
            "status": "healthy" if len(analysis.critical_issues) == 0 else "critical",
            "summary": {
                "total_issues": analysis.total_issues,
                "critical_count": len(analysis.critical_issues),
                "warning_count": len(analysis.warnings),
                "info_count": len(analysis.info)
            },
            "findings": {
                "critical": analysis.critical_issues,
                "warnings": analysis.warnings,
                "info": analysis.info
            },
            "mesh_health": {
                "total_meshes": len(analysis.meshes),
                "meshes_with_issues": sum(1 for m in analysis.meshes if len(m.issues) > 0),
                "total_vertices": sum(m.vertex_count for m in analysis.meshes),
                "total_faces": sum(m.face_count for m in analysis.meshes)
            },
            "material_health": {
                "total_materials": len(analysis.materials),
                "materials_with_issues": sum(1 for m in analysis.materials if len(m.issues) > 0),
                "materials_with_missing_textures": sum(1 for m in analysis.materials 
                                                       for t in m.textures if not t.exists)
            },
            "texture_health": {
                "total_textures": len(analysis.textures),
                "textures_found": len([t for t in analysis.textures if t.exists]),
                "textures_missing": len([t for t in analysis.textures if not t.exists])
            },
            "suggested_actions": _generate_suggestions(analysis)
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


def _generate_suggestions(analysis) -> list:
    """Generate intelligent fix suggestions based on analysis"""
    suggestions = []
    
    # Mesh issues
    if sum(m.vertex_count for m in analysis.meshes) == 0:
        suggestions.append({
            "priority": "critical",
            "issue": "No mesh data found",
            "suggestion": "Re-export the avatar from your 3D modeling tool",
            "details": "The OBJ file appears to be empty or corrupted"
        })
    
    # Material issues
    if len(analysis.materials) == 0 and sum(m.vertex_count for m in analysis.meshes) > 0:
        suggestions.append({
            "priority": "high",
            "issue": "No materials defined",
            "suggestion": "Assign materials in the 3D editor and re-export with MTL file",
            "details": "Avatar will render as untextured/white without materials"
        })
    
    # Missing textures
    missing_textures = [t for t in analysis.textures if not t.exists]
    if missing_textures:
        suggestions.append({
            "priority": "high",
            "issue": f"Missing {len(missing_textures)} texture file(s)",
            "suggestion": "Verify all texture files are in the same directory as the avatar",
            "details": f"Missing: {', '.join(t.name for t in missing_textures)}"
        })
    
    # Normal issues
    meshes_no_normals = [m for m in analysis.meshes if not m.has_normals and m.vertex_count > 0]
    if meshes_no_normals:
        suggestions.append({
            "priority": "medium",
            "issue": "Missing vertex normals",
            "suggestion": "Recalculate normals in your 3D editor before exporting",
            "details": "Lighting will appear flat without normals"
        })
    
    # Texture coordinate issues
    if sum(m.texture_coord_count for m in analysis.meshes) == 0 and len(analysis.textures) > 0:
        suggestions.append({
            "priority": "medium",
            "issue": "Missing texture coordinates",
            "suggestion": "UV unwrap the model in your 3D editor and re-export",
            "details": "Textures cannot be applied without UV coordinates"
        })
    
    return suggestions
