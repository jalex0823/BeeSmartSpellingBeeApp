content = open('templates/unified_menu.html', encoding='utf-8').read()
print(f'Script open: {content.count("<script")}')
print(f'Script close: {content.count("</script>")}')
print(f'Difference: {content.count("<script") - content.count("</script>")}')
