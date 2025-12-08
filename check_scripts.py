with open('templates/unified_menu.html', 'r', encoding='utf-8') as f:
    content = f.read()
    open_count = content.count('<script')
    close_count = content.count('</script>')
    print(f'Script open tags: {open_count}')
    print(f'Script close tags: {close_count}')
    print(f'Difference: {open_count - close_count}')
