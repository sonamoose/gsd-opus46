#!/usr/bin/env python3
import os

BASE = ".planning"

files = [
    (os.path.join(BASE, "STATE.md"), "=== PROJECT STATE ==="),
    (os.path.join(BASE, "codebase", "CODEMAP.md"), "=== CODEBASE MAP ==="),
]

for path, header in files:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        print(header)
        print(content)

print("GSD Context Loaded.")
