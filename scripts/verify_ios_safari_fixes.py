import os

def check_file_content(filepath, checks):
    print(f"Checking {filepath}...")
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for check_name, check_func in checks.items():
        if check_func(content):
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")

def verify_ios_safari_fixes():
    print("🚀 Verifying iOS/Safari Compatibility Fixes")
    
    # Checks for base.html (inherited by quiz.html)
    base_checks = {
        "Viewport Meta Tag (Mobile Scale)": lambda c: '<meta name="viewport"' in c and "maximum-scale=1" in c
    }
    check_file_content("templates/base.html", base_checks)

    # Checks for unified_menu.html
    menu_checks = {
        "Modern Three.js CDN (jsdelivr)": lambda c: "cdn.jsdelivr.net/npm/three" in c and "cdn.rawgit.com" not in c,
        "AudioContext Resume on Touch": lambda c: "audioContext.resume()" in c or "resumeAudioContext" in c,
        "Viewport Meta Tag (Mobile Scale)": lambda c: '<meta name="viewport"' in c and "maximum-scale=1" in c
    }
    check_file_content("templates/unified_menu.html", menu_checks)

    # Checks for quiz.html
    quiz_checks = {
        "Speech Synthesis Voice Loading": lambda c: "speechSynthesis.getVoices()" in c and ("voiceschanged" in c or "waitForVoices" in c),
        "AudioContext Resume on Touch": lambda c: "audioContext.resume()" in c or "resumeAudioContext" in c
    }
    check_file_content("templates/quiz.html", quiz_checks)

if __name__ == "__main__":
    verify_ios_safari_fixes()
