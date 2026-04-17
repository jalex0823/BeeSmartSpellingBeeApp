keywords = ['upload', 'word-list', 'word_list', 'library', 'speed', 'battle', 'saved', 'import-text', 'panel-btn', 'action-btn', 'menu-option', 'tile', 'word-library', 'wordbank']
with open('templates/unified_menu.html', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    ll = line.lower()
    if any(kw in ll for kw in keywords):
        print(f'{i}: {line.rstrip()[:140]}')
