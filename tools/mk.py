#!/usr/bin/env python3
"""新しいページの骨組みを作る。共通部分は目印だけ置き、中身は tools/i18n.py が埋める。

    python3 tools/mk.py <path> <title> <description> < body.html
"""
import pathlib
import sys

path, title, desc = sys.argv[1], sys.argv[2], sys.argv[3]
body = sys.stdin.read().strip("\n")
p = pathlib.Path(path)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(
    '<!DOCTYPE html>\n<html lang="x">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    f'<title>{title}</title>\n<meta name="description" content="{desc}">\n'
    '<!--chrome:alt-->\n<!--/chrome:alt-->\n</head>\n<body>\n'
    '<!--chrome:head-->\n<!--/chrome:head-->\n\n'
    f'{body}\n\n'
    '<!--chrome:foot-->\n<!--/chrome:foot-->\n</body>\n</html>\n',
    encoding="utf-8")
print(f"作った: {path}")
