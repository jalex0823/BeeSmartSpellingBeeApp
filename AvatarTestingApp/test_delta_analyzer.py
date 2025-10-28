#!/usr/bin/env python3
"""
Test script for Deep Avatar Delta Analyzer
Compare AlBee (working) vs BikerBee (broken)
"""

from avatar_file_parser import AvatarFileParser, AvatarDeltaComparator
from pathlib import Path
import json

BASE_PATH = Path(r'C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\static\Avatars\3D Avatar Files')

def main():
    print("=" * 80)
    print("DEEP AVATAR DELTA ANALYZER")
    print("=" * 80)
    
    # Analyze working avatar
    print("\n[1/3] Analyzing working avatar: AlBee")
    print("-" * 80)
    
    albee_dir = BASE_PATH / "AlBee"
    if not albee_dir.exists():
        print(f"❌ AlBee directory not found at {albee_dir}")
        return
    
    albee_parser = AvatarFileParser(str(albee_dir))
    albee_analysis = albee_parser.parse()
    
    print(f"✅ Parsed AlBee")
    print(f"   - OBJ File: {albee_analysis.obj_file}")
    print(f"   - MTL File: {albee_analysis.mtl_file}")
    print(f"   - File Size: {albee_analysis.file_size / (1024*1024):.2f} MB")
    print(f"   - Meshes: {len(albee_analysis.meshes)}")
    print(f"   - Total Vertices: {sum(m.vertex_count for m in albee_analysis.meshes)}")
    print(f"   - Total Faces: {sum(m.face_count for m in albee_analysis.meshes)}")
    print(f"   - Materials: {len(albee_analysis.materials)}")
    print(f"   - Textures: {len(albee_analysis.textures)} (found: {len([t for t in albee_analysis.textures if t.exists])})")
    print(f"   - Critical Issues: {len(albee_analysis.critical_issues)}")
    print(f"   - Warnings: {len(albee_analysis.warnings)}")
    
    if albee_analysis.critical_issues:
        print(f"   🔴 Critical Issues:")
        for issue in albee_analysis.critical_issues:
            print(f"      - {issue}")
    
    # Analyze broken avatar
    print("\n[2/3] Analyzing broken avatar: BikerBee")
    print("-" * 80)
    
    bikerbee_dir = BASE_PATH / "BikerBee"
    if not bikerbee_dir.exists():
        print(f"❌ BikerBee directory not found at {bikerbee_dir}")
        return
    
    bikerbee_parser = AvatarFileParser(str(bikerbee_dir))
    bikerbee_analysis = bikerbee_parser.parse()
    
    print(f"✅ Parsed BikerBee")
    print(f"   - OBJ File: {bikerbee_analysis.obj_file}")
    print(f"   - MTL File: {bikerbee_analysis.mtl_file}")
    print(f"   - File Size: {bikerbee_analysis.file_size / (1024*1024):.2f} MB")
    print(f"   - Meshes: {len(bikerbee_analysis.meshes)}")
    print(f"   - Total Vertices: {sum(m.vertex_count for m in bikerbee_analysis.meshes)}")
    print(f"   - Total Faces: {sum(m.face_count for m in bikerbee_analysis.meshes)}")
    print(f"   - Materials: {len(bikerbee_analysis.materials)}")
    print(f"   - Textures: {len(bikerbee_analysis.textures)} (found: {len([t for t in bikerbee_analysis.textures if t.exists])})")
    print(f"   - Critical Issues: {len(bikerbee_analysis.critical_issues)}")
    print(f"   - Warnings: {len(bikerbee_analysis.warnings)}")
    
    if bikerbee_analysis.critical_issues:
        print(f"   🔴 Critical Issues:")
        for issue in bikerbee_analysis.critical_issues:
            print(f"      - {issue}")
    
    # Compare
    print("\n[3/3] DELTA ANALYSIS: AlBee vs BikerBee")
    print("=" * 80)
    
    delta = AvatarDeltaComparator.compare(albee_analysis, bikerbee_analysis)
    
    print(f"\n📊 Mesh Comparison:")
    print(f"   Working (AlBee):      {delta['mesh_differences']['working']['vertices']} vertices, {delta['mesh_differences']['working']['faces']} faces")
    print(f"   Broken (BikerBee):    {delta['mesh_differences']['broken']['vertices']} vertices, {delta['mesh_differences']['broken']['faces']} faces")
    print(f"   Delta:                {delta['mesh_differences']['delta']['vertex_delta']:+d} vertices, {delta['mesh_differences']['delta']['face_delta']:+d} faces")
    
    print(f"\n🎨 Material Comparison:")
    print(f"   Working (AlBee):      {delta['material_differences']['working_count']} materials")
    print(f"   Broken (BikerBee):    {delta['material_differences']['broken_count']} materials")
    print(f"   Delta:                {delta['material_differences']['delta']:+d} materials")
    
    print(f"\n🖼️ Texture Comparison:")
    print(f"   Working (AlBee):      {delta['texture_differences']['working_count']} total, {delta['texture_differences']['working_textures']} found")
    print(f"   Broken (BikerBee):    {delta['texture_differences']['broken_count']} total, {delta['texture_differences']['broken_textures']} found")
    print(f"   Delta:                {delta['texture_differences']['delta']:+d} textures")
    
    print(f"\n🔍 Diagnostic Findings:")
    if delta['diagnostic_findings']:
        for finding in delta['diagnostic_findings']:
            print(f"   • {finding}")
    else:
        print("   No significant differences found")
    
    print(f"\n💡 Suggested Fixes:")
    if delta['suggested_fixes']:
        for fix in delta['suggested_fixes']:
            print(f"   ✓ {fix}")
    else:
        print("   No fixes needed")
    
    # Save detailed report
    print(f"\n📝 Generating detailed report...")
    report = {
        "comparison": delta['comparison'],
        "summary": delta['summary'],
        "mesh_differences": delta['mesh_differences'],
        "material_differences": delta['material_differences'],
        "texture_differences": delta['texture_differences'],
        "diagnostic_findings": delta['diagnostic_findings'],
        "suggested_fixes": delta['suggested_fixes'],
        "working_analysis": {
            "meshes": len(albee_analysis.meshes),
            "materials": len(albee_analysis.materials),
            "textures": len([t for t in albee_analysis.textures if t.exists]),
            "critical_issues": albee_analysis.critical_issues,
            "warnings": albee_analysis.warnings,
            "mesh_details": [
                {
                    "name": m.name,
                    "vertices": m.vertex_count,
                    "faces": m.face_count,
                    "normals": m.normal_count,
                    "tex_coords": m.texture_coord_count,
                    "has_normals": m.has_normals,
                    "has_texture_coords": m.has_texture_coords
                } for m in albee_analysis.meshes
            ]
        },
        "broken_analysis": {
            "meshes": len(bikerbee_analysis.meshes),
            "materials": len(bikerbee_analysis.materials),
            "textures": len([t for t in bikerbee_analysis.textures if t.exists]),
            "critical_issues": bikerbee_analysis.critical_issues,
            "warnings": bikerbee_analysis.warnings,
            "mesh_details": [
                {
                    "name": m.name,
                    "vertices": m.vertex_count,
                    "faces": m.face_count,
                    "normals": m.normal_count,
                    "tex_coords": m.texture_coord_count,
                    "has_normals": m.has_normals,
                    "has_texture_coords": m.has_texture_coords
                } for m in bikerbee_analysis.meshes
            ]
        }
    }
    
    report_path = Path("avatar_delta_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved to: {report_path.absolute()}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
