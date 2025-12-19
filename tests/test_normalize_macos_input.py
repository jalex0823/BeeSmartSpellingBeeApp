import importlib


def test_normalize_strips_invisible_and_control_chars():
    m = importlib.import_module('AjaSpellBApp')
    normalize = m.normalize

    # Common characters that can sneak in via macOS/iOS keyboards, IME, or copy/paste
    # and cause false "incorrect" comparisons.
    samples = [
        'type\u200b',   # zero-width space
        'type\u200d',   # zero-width joiner
        'type\ufeff',   # BOM / zero-width no-break space
        't\u202Eype',   # bidi override
        't\u2060ype',   # word joiner
        't\x7fype',     # DEL control
        't\u00ady\u00adpe',  # soft hyphens
    ]

    for s in samples:
        assert normalize(s) == 'type'
