#!/usr/bin/env python3
"""Turn posts/*.md into the pages under learn/.

Usage:
    pip install markdown          # once
    python3 build.py              # after editing or adding a post

Writing a new post:
    cp posts/TEMPLATE.md posts/my-new-post.md
    # edit it, then run build.py

The filename becomes the URL. posts/why-hybrid-search.md publishes to
learn/why-hybrid-search.html, so renaming a file breaks anyone's link to it.
"""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("pip install markdown")

HERE = pathlib.Path(__file__).resolve().parent
POSTS = HERE / "posts"

# Sections on the index, in the order they appear. A post's `tag:` decides
# which one it lands in; an unrecognised tag gets its own section at the end
# rather than being silently dropped.
SECTIONS = [
    ("Things I got wrong",
     "The most useful notes. Each one is a bug that produced no error message."),
    ("Retrieval", ""),
    ("Agents", ""),
    ("Production", ""),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Sadhvi Sharma</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="wrap">

<header class="site">
  <nav><a href="/">Portfolio</a><a href="/learn/">Notes</a><a href="https://github.com/sadvi11">GitHub</a></nav>
</header>

<span class="tag">{tag}</span>
<h1>{title}</h1>
<p class="lede">{lede}</p>
<p class="meta">Sadhvi Sharma · Calgary</p>

{body}

<footer>
{footer}
  <p><a href="/learn/">← more notes</a></p>
</footer>

</div>
</body>
</html>
"""


def parse(path: pathlib.Path) -> dict:
    """Split the `---` front matter from the body.

    Deliberately not YAML: three keys, one level deep, no dependency. If this
    ever needs nesting it needs a real parser instead of growing one here.
    """
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing the --- front matter block")

    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            sys.exit(f"{path.name}: front matter line is not key: value -> {line!r}")
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()

    for required in ("title", "lede", "tag"):
        if not meta.get(required):
            sys.exit(f"{path.name}: front matter needs a non-empty '{required}'")

    meta["body_md"] = m.group(2)
    meta["slug"] = path.stem
    meta.setdefault("description", meta["lede"])
    meta.setdefault("footer", "")
    return meta


def render(meta: dict) -> str:
    body = markdown.markdown(
        meta["body_md"], extensions=["extra", "sane_lists", "smarty"])
    footer = (f"  <p>{markdown.markdown(meta['footer'])[3:-4]}</p>\n"
              if meta["footer"] else "")
    return PAGE.format(
        title=meta["title"], description=meta["description"].replace('"', "&quot;"),
        tag=meta["tag"], lede=meta["lede"], body=body, footer=footer)


def build_index(posts: list[dict]) -> str:
    by_tag: dict[str, list[dict]] = {}
    for p in posts:
        by_tag.setdefault(p["tag"], []).append(p)

    known = [name for name, _ in SECTIONS]
    ordered = known + [t for t in sorted(by_tag) if t not in known]

    chunks = []
    for name in ordered:
        items = by_tag.get(name)
        if not items:
            continue
        blurb = dict(SECTIONS).get(name, "")
        chunks.append(f"  <h2>{name}</h2>")
        if blurb:
            chunks.append(f'  <p style="color:var(--muted); margin-top:-.4rem;">{blurb}</p>')
        for p in sorted(items, key=lambda x: x["slug"]):
            chunks.append(
                f'\n  <a class="card" href="{p["slug"]}.html">\n'
                f'    <h3>{p["title"]}</h3>\n'
                f'    <p>{p["lede"]}</p>\n'
                f'  </a>')
    return "\n".join(chunks)


def main() -> int:
    paths = sorted(p for p in POSTS.glob("*.md") if p.stem != "TEMPLATE")
    if not paths:
        sys.exit("no posts found in posts/")

    posts = []
    for path in paths:
        meta = parse(path)
        (HERE / f"{meta['slug']}.html").write_text(render(meta))
        posts.append(meta)
        print(f"  wrote {meta['slug']}.html")

    index = (HERE / "index.html").read_text()
    new = re.sub(r"(<!-- POSTS -->).*?(<!-- /POSTS -->)",
                 lambda m: f"{m.group(1)}\n{build_index(posts)}\n  {m.group(2)}",
                 index, flags=re.S)
    if new == index and "<!-- POSTS -->" not in index:
        sys.exit("index.html is missing the <!-- POSTS --> markers")
    (HERE / "index.html").write_text(new)
    print(f"  wrote index.html ({len(posts)} posts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
