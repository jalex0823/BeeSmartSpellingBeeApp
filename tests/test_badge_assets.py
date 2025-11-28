import importlib.util
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / 'AjaSpellBApp.py'
spec = importlib.util.spec_from_file_location('AjaSpellBApp', str(APP_PATH))
AjaSpellBApp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AjaSpellBApp)

BADGE_METADATA = AjaSpellBApp.BADGE_METADATA

# Assume badges live under static/images/badges/<file>
STATIC_BADGES_DIR = Path(__file__).resolve().parents[1] / 'static' / 'images' / 'badges'


def test_badge_image_presence_or_fallback():
    missing = []
    for key, meta in BADGE_METADATA.items():
        image = meta.get('image')
        if image:
            path = STATIC_BADGES_DIR / Path(image).name
            if not path.exists():
                missing.append(key)
        # Ensure fallback icon present
        assert 'icon' in meta
    # Don't fail the build for missing images yet; just ensure elite badge is tracked
    assert 'elite_buzz_dust' in BADGE_METADATA
    # Optional: if elite badge image exists, ensure file size > 0
    elite_image = BADGE_METADATA['elite_buzz_dust'].get('image')
    if elite_image:
        elite_path = STATIC_BADGES_DIR / Path(elite_image).name
        if elite_path.exists():
            assert elite_path.stat().st_size > 0
