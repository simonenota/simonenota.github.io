#!/usr/bin/env python3
"""Make a small picture of the first page of each article's PDF.

For every article in data/publications.yaml with a PDF, the page given in
"cover_page" (1 if empty) becomes static/papers/covers/<pdf name>.jpg.
The home page shows that picture next to the article, if it exists.
Runs by itself on GitHub before each publication; needs pdftoppm (poppler-utils).
"""
import os
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "papers", "covers")

with open(os.path.join(ROOT, "data", "publications.yaml"), encoding="utf-8") as f:
    articles = (yaml.safe_load(f) or {}).get("articles") or []

os.makedirs(OUT, exist_ok=True)
for a in articles:
    pdf = (a or {}).get("pdf")
    if not pdf:
        continue
    src = os.path.join(ROOT, "static", pdf.lstrip("/"))
    if not os.path.exists(src):
        print(f"skipped (file not found): {pdf}")
        continue
    page = str(int(a.get("cover_page") or 1))
    name = os.path.splitext(os.path.basename(pdf))[0]
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=82", "-f", page, "-l", page,
                    "-singlefile", "-scale-to", "560", src, os.path.join(OUT, name)], check=True)
    print(f"cover: {pdf} page {page}")
