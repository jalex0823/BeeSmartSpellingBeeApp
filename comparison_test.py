"""
Quick test showing Original vs Enhanced number removal
"""
import re

# ORIGINAL SCRIPT LOGIC
def original_clean(stem: str) -> str:
    """Original cleaning logic from the script"""
    NUM_SUFFIX = re.compile(r"(?:[_-]\d{6,})+$", re.IGNORECASE)
    SEP_SPLIT = re.compile(r"[_\-]+")
    DROP_TRAILING_TOKENS = {
        "texture", "tex", "mat", "material", "albedo", "basecolor", "base_color", "obj", "mtl"
    }
    
    def camel_no_underscores(s: str) -> str:
        parts = [p for p in SEP_SPLIT.split(s) if p]
        if not parts:
            return s.replace("_", "").replace("-", "")
        return "".join(p[:1].upper() + p[1:] for p in parts)
    
    stem = NUM_SUFFIX.sub("", stem)
    parts = [p for p in SEP_SPLIT.split(stem) if p]
    while parts and parts[-1].lower() in DROP_TRAILING_TOKENS:
        parts.pop()
    if not parts:
        parts = [stem]
    cleaned = camel_no_underscores("_".join(parts))
    return cleaned or "MeshyModel"

# ENHANCED GUI LOGIC
def enhanced_clean(stem: str) -> str:
    """Enhanced cleaning logic from GUI"""
    NUM_SUFFIX = re.compile(r"(?:[_-]\d{4,})+$", re.IGNORECASE)  # 4+ digits instead of 6+
    SEP_SPLIT = re.compile(r"[_\-]+")
    DROP_TRAILING_TOKENS = {
        "texture", "tex", "mat", "material", "albedo", "basecolor", "base_color", "obj", "mtl"
    }
    
    def camel_no_underscores(s: str) -> str:
        parts = [p for p in SEP_SPLIT.split(s) if p]
        if not parts:
            return s.replace("_", "").replace("-", "")
        return "".join(p[:1].upper() + p[1:] for p in parts)
    
    # Enhanced cleaning
    stem = NUM_SUFFIX.sub("", stem)
    parts = [p for p in SEP_SPLIT.split(stem) if p]
    
    # Remove trailing junk tokens
    while parts and parts[-1].lower() in DROP_TRAILING_TOKENS:
        parts.pop()
        
    # Remove any remaining pure numeric parts at the end
    while parts and parts[-1].isdigit():
        parts.pop()
        
    # Remove common suffixes that might remain
    while parts and parts[-1].lower() in {"export", "meshy", "model", "3d"}:
        parts.pop()
        
    if not parts:
        parts = [stem.split('_')[0] if '_' in stem else stem]
        
    cleaned = camel_no_underscores("_".join(parts))
    return cleaned or "MeshyModel"

def compare_cleaning():
    print("🔍 ORIGINAL vs ENHANCED Number Removal Comparison")
    print("=" * 70)
    
    test_cases = [
        "Explorer_Bee_1023150321_texture_obj",      # Long Meshy ID
        "Robot_Spider_12345",                       # Medium number (5 digits)
        "AstronautBee_9876_basecolor",             # Short number (4 digits)
        "SuperHero_texture_123_obj",               # 3 digits (should keep in original)
        "Dragon_Model_3D_98765432_export_meshy",   # Multiple suffixes
        "Simple_Bee_999",                          # 3 digits (edge case)
        "ComplexModel_texture_87654321_material",   # Mixed tokens and numbers
    ]
    
    print(f"{'Test Case':<35} | {'Original':<15} | {'Enhanced':<15} | {'Improvement'}")
    print("-" * 85)
    
    for case in test_cases:
        orig_result = original_clean(case)
        enhanced_result = enhanced_clean(case)
        improved = "✅ YES" if orig_result != enhanced_result else "→ Same"
        
        print(f"{case:<35} | {orig_result:<15} | {enhanced_result:<15} | {improved}")
    
    print("\n📈 Key Improvements:")
    print("• Catches 4-digit numbers (vs 6-digit minimum in original)")
    print("• Removes remaining pure numbers after token removal")
    print("• Removes common export-related suffixes (export, meshy, model, 3d)")
    print("• Better fallback when no valid parts remain")
    print("• Same transparent PNG generation with '!' suffix")

if __name__ == "__main__":
    compare_cleaning()