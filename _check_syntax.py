import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
content = open(r'e:\GitHub\BeeSmartSpellingBeeApp\templates\quiz.html', encoding='utf-8').read()

blocks = []
for m in re.finditer(r'<script>(.*?)</script>', content, re.DOTALL):
    start = content[:m.start()].count('\n') + 2
    blocks.append((start, m.group(1)))

for bi, (start_line, js) in enumerate(blocks):
    depth_paren = 0
    depth_brace = 0
    i = 0
    lines_so_far = 0
    while i < len(js):
        c = js[i]
        if c == '\n':
            lines_so_far += 1
        elif c == '/' and i+1 < len(js) and js[i+1] == '/':
            end = js.find('\n', i)
            if end == -1: break
            i = end
            continue
        elif c == '/' and i+1 < len(js) and js[i+1] == '*':
            end = js.find('*/', i+2)
            if end == -1: break
            lines_so_far += js[i:end+2].count('\n')
            i = end + 2
            continue
        elif c == '`':
            i += 1
            while i < len(js):
                if js[i] == '\\' and i+1 < len(js):
                    i += 2
                    continue
                if js[i] == '\n':
                    lines_so_far += 1
                if js[i] == '`':
                    break
                i += 1
        elif c in ('"', "'"):
            quote = c
            i += 1
            while i < len(js):
                if js[i] == '\\' and i+1 < len(js):
                    i += 2
                    continue
                if js[i] == '\n':
                    lines_so_far += 1
                if js[i] == quote:
                    break
                i += 1
        elif c == '(':
            depth_paren += 1
        elif c == ')':
            depth_paren -= 1
            if depth_paren < 0:
                tl = start_line + lines_so_far
                print(f'BLOCK {bi} (template ~line {tl}): Unbalanced ) at JS line {lines_so_far+1}')
                line_start = js.rfind('\n', 0, i)
                line_end = js.find('\n', i)
                if line_end == -1: line_end = len(js)
                ctx_line = js[line_start+1:line_end].strip()
                print(f'  Line content: {ctx_line[:120]}')
                depth_paren = 0
        elif c == '{':
            depth_brace += 1
        elif c == '}':
            depth_brace -= 1
            if depth_brace < 0:
                tl = start_line + lines_so_far
                print(f'BLOCK {bi} (template ~line {tl}): Unbalanced }} at JS line {lines_so_far+1}')
                depth_brace = 0
        i += 1

    if depth_paren != 0 or depth_brace != 0:
        print(f'BLOCK {bi} (template line {start_line}, {lines_so_far+1} JS lines): End depths: paren={depth_paren} brace={depth_brace}')

print("Done.")
