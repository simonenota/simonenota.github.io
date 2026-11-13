#!/usr/bin/env python3
"""Update the Italian texts of the site from the English ones with DeepL.

Only texts whose English version changed since BASE (a git commit) are
translated again, or whose Italian version is empty. Italian texts you
corrected by hand stay as they are until their English original changes.

Usage:  DEEPL_API_KEY=... python3 scripts/translate.py [BASE_COMMIT]
        python3 scripts/translate.py [BASE_COMMIT] --dry-run   (no API calls)

Without BASE_COMMIT the commit stored in .translation-base is used: the
English version that the Italian one was last brought in line with.
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Front-matter pages: English file -> Italian file.
PAGES = {
    "content/_index.en.md": "content/_index.it.md",
    "content/ai-philosophy.en.md": "content/ai-philosophy.it.md",
}
# Data files holding {en: ..., it: ...} pairs.
DATA = ["data/publications.yaml", "data/aifun.yaml"]
# Fields that are never translated (links, files, settings, names).
SKIP = {"color", "link_url", "url", "image", "pdf", "layout", "year", "venue"}
SKIP_PATHS = {("title",)}  # the page title is the person's name


# ---------- DeepL with Markdown protection ----------

def md_to_tags(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s.replace("\n\n", "<p/>").replace("\n", " ")


def tags_to_md(s):
    s = s.replace("<p/>", "\n\n").replace("<p />", "\n\n")
    s = re.sub(r'<a href="([^"]+)">(.+?)</a>', r"[\2](\1)", s)
    s = re.sub(r"<b>(.+?)</b>", r"**\1**", s)
    s = re.sub(r"<i>(.+?)</i>", r"*\1*", s)
    return html.unescape(s)


def deepl(texts):
    key = os.environ.get("DEEPL_API_KEY", "").strip()
    if not key:
        sys.exit("DEEPL_API_KEY is missing.")
    host = "api-free.deepl.com" if key.endswith(":fx") else "api.deepl.com"
    out = []
    for i in range(0, len(texts), 40):
        chunk = texts[i:i + 40]
        body = [("source_lang", "EN"), ("target_lang", "IT"), ("tag_handling", "html"),
                ("preserve_formatting", "1")] + [("text", md_to_tags(t)) for t in chunk]
        req = urllib.request.Request(
            f"https://{host}/v2/translate",
            data=urllib.parse.urlencode(body).encode(),
            headers={"Authorization": f"DeepL-Auth-Key {key}"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.load(r)
        out += [tags_to_md(t["text"]) for t in res["translations"]]
    return out


def fake(texts):
    return [f"[IT] {t}" for t in texts]


# ---------- reading files at a commit ----------

def read(path, rev=None):
    if rev is None:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return f.read()
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def split_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def dump(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100000)


# ---------- collecting what needs translating ----------

class Job:
    def __init__(self):
        self.items = []  # (setter, english text)

    def add(self, setter, text):
        self.items.append((setter, text))

    def run(self, translate):
        if not self.items:
            return 0
        done = translate([t for _, t in self.items])
        for (setter, _), it in zip(self.items, done):
            setter(it)
        return len(self.items)


def walk_page(new_en, old_en, it, job, path=()):
    """Mirror the English tree into the Italian one, translating changed strings."""
    if isinstance(new_en, dict):
        for k, v in new_en.items():
            p = path + (k,)
            if k in SKIP or p in SKIP_PATHS:
                if k not in it:
                    it[k] = v
                continue
            old_v = old_en.get(k) if isinstance(old_en, dict) else None
            if isinstance(v, (dict, list)):
                same_shape = isinstance(it.get(k), type(v)) and (
                    not isinstance(v, list) or len(it[k]) == len(v))
                if not same_shape:
                    it[k] = {} if isinstance(v, dict) else [None] * len(v)
                    old_v = None
                walk_page(v, old_v, it[k], job, p)
            else:
                leaf(v, old_v, it, k, job)
    elif isinstance(new_en, list):
        old_ok = isinstance(old_en, list) and len(old_en) == len(new_en)
        for i, v in enumerate(new_en):
            old_v = old_en[i] if old_ok else None
            if isinstance(v, (dict, list)):
                if not isinstance(it[i], type(v)):
                    it[i] = {} if isinstance(v, dict) else []
                    old_v = None
                walk_page(v, old_v, it[i], job, path + (i,))
            else:
                leaf(v, old_v, it, i, job)


def leaf(v, old_v, container, key, job):
    if not isinstance(v, str) or not v.strip():
        container[key] = v  # empty or non-text values are copied as they are
        return
    current = container[key] if (isinstance(container, list) or key in container) else None
    if current and v == old_v:
        return
    job.add(lambda t, c=container, k=key: c.__setitem__(k, t), v)


def item_key(d):
    for k in ("pdf", "image", "title"):
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return None


def walk_data(new, old, job):
    """Translate every {en, it} pair whose English changed or whose Italian is empty."""
    if isinstance(new, dict):
        if "en" in new and "it" in new and not isinstance(new["en"], (dict, list)):
            en, old_en = new.get("en") or "", (old or {}).get("en") if isinstance(old, dict) else None
            if en.strip() and (not (new.get("it") or "").strip() or en != old_en):
                job.add(lambda t, d=new: d.__setitem__("it", t), en)
            elif not en.strip():
                new["it"] = ""
            return
        for k, v in new.items():
            walk_data(v, old.get(k) if isinstance(old, dict) else None, job)
    elif isinstance(new, list):
        old_by_key = {item_key(o): o for o in (old or []) if item_key(o)}
        for i, v in enumerate(new):
            o = old_by_key.get(item_key(v)) if item_key(v) else (
                old[i] if isinstance(old, list) and i < len(old) else None)
            walk_data(v, o, job)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        base = args[0]
    else:
        try:
            base = read(".translation-base").strip() or None
        except FileNotFoundError:
            base = None
    translate = fake if "--dry-run" in sys.argv else deepl
    total = 0

    for en_path, it_path in PAGES.items():
        new_text, it_text = read(en_path), read(it_path)
        if new_text is None or it_text is None:
            continue
        new_en, _ = split_fm(new_text)
        old_text = read(en_path, base) if base else None
        old_en = split_fm(old_text)[0] if old_text else None
        it, body = split_fm(it_text)
        job = Job()
        walk_page(new_en, old_en, it, job)
        n = job.run(translate)
        if n:
            with open(os.path.join(ROOT, it_path), "w", encoding="utf-8") as f:
                f.write("---\n" + dump(it) + "---\n" + body)
            print(f"{it_path}: {n} text(s) translated")
        total += n

    for path in DATA:
        text = read(path)
        if text is None:
            continue
        head = "".join(l for l in text.splitlines(True) if l.startswith("#"))
        new = yaml.safe_load(text)
        old_text = read(path, base) if base else None
        old = yaml.safe_load(old_text) if old_text else None
        job = Job()
        walk_data(new, old, job)
        n = job.run(translate)
        if n:
            with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
                f.write(head + dump(new))
            print(f"{path}: {n} text(s) translated")
        total += n

    print(f"Done: {total} text(s) translated.")


if __name__ == "__main__":
    main()
