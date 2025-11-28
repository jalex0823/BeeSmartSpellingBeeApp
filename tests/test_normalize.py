import pytest

# We will import normalize from AjaSpellBApp by path import
import importlib.util
import sys
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / 'AjaSpellBApp.py'
spec = importlib.util.spec_from_file_location('AjaSpellBApp', str(APP_PATH))
AjaSpellBApp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AjaSpellBApp)

normalize = AjaSpellBApp.normalize

@pytest.mark.parametrize('raw,expected', [
    ('naïve', 'naive'),
    ('résumé', 'resume'),
    ('café', 'cafe'),
    ('coöperate', 'cooperate'),
    (' Niño ', 'nino'),
    ('abc-123', 'abc123'),
    ('A B C', 'abc'),
    ('\u200Bhidden', 'hidden'),  # zero-width space
    (None, ''),
])
def test_normalize_removes_diacritics_and_non_alnum(raw, expected):
    assert normalize(raw) == expected
