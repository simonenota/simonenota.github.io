#!/usr/bin/env python3
"""Make pictures of the first pages of each article's PDF.

For every article in data/publications.yaml with a PDF, the page given in
"cover_page" (1 if empty) becomes static/papers/covers/<pdf name>.jpg, a small
picture shown next to the article on the home page. That page and the next
ones (PREVIEW_PAGES in all) also become larger pictures,
static/papers/pages/<pdf name>-1.jpg, -2.jpg, ..., which the reader can leaf
through after clicking the small picture.
Runs by itself on GitHub before each publication; needs pdftoppm and pdfinfo
(poppler-utils).
"""
import os
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "papers", "covers")
PAGES = os.path.join(ROOT, "static", "papers", "pages")
PREVIEW_PAGES = 4


def page_count(src):
    info = subprocess.run(["pdfinfo", src], capture_output=True, text=True).stdout
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 1


with open(os.path.join(ROOT, "data", "publications.yaml"), encoding="utf-8") as f:
    articles = (yaml.safe_load(f) or {}).get("articles") or []

os.makedirs(OUT, exist_ok=True)
os.makedirs(PAGES, exist_ok=True)
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
    last = min(page_count(src), int(page) + PREVIEW_PAGES - 1)
    for i, n in enumerate(range(int(page), last + 1), start=1):
        subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80", "-f", str(n), "-l", str(n),
                        "-singlefile", "-scale-to", "1500", src, os.path.join(PAGES, f"{name}-{i}")], check=True)
    print(f"pages: {pdf} {page} to {last}")
