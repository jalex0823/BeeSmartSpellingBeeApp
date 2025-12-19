"""Regression test: macOS/iOS input can include invisible/control characters.

If those sneak into the spelling input, a correct answer can be marked incorrect.
This test ensures `normalize()` strips the common troublemakers.
"""

import importlib


def main():
    m = importlib.import_module('AjaSpellBApp')
    normalize = m.normalize

    samples = [
        'type\u200b',        # zero-width space
        'type\u200d',        # zero-width joiner
        'type\ufeff',        # BOM / zero-width no-break space
        't\u202Eype',        # bidi override
        't\u2060ype',        # word joiner
        't\x7fype',          # DEL control
        't\u00ady\u00adpe', # soft hyphens
    ]

    for s in samples:
        got = normalize(s)
        assert got == 'type', f"normalize({s!r}) -> {got!r} (expected 'type')"

    print('✅ normalize() strips macOS/iOS invisible/control chars')


if __name__ == '__main__':
    main()
