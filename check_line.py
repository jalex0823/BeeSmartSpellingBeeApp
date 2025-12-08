with open('templates/unified_menu.html', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
print(f'Total lines: {len(lines)}')
print(f'Script tags open: {content.count("<script")}')
print(f'Script tags close: {content.count("</script>")}')
print(f'Curly brackets: {content.count("{")} open, {content.count("}")} close')
print(f'Difference: {content.count("{") - content.count("}")}')

if len(lines) > 16687:
    print(f'\nLine 16687 content:')
    print(lines[16686][:100])
