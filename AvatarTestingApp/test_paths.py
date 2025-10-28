from pathlib import Path
import os

print(f"Current dir: {os.getcwd()}")
print()

paths = [
    Path('../static/Avatars/3D Avatar Files'),
    Path('../../static/Avatars/3D Avatar Files'),
    Path('C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/static/Avatars/3D Avatar Files'),
]

for p in paths:
    abs_p = p.resolve()
    exists = p.exists()
    print(f"Path: {p}")
    print(f"  Resolved: {abs_p}")
    print(f"  Exists: {exists}")
    if exists:
        files = list(p.glob('*.glb'))
        print(f"  GLB files found: {len(files)}")
        for f in sorted(files)[:5]:
            print(f"    - {f.name}")
    print()
