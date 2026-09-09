#!/usr/bin/env python3
"""Build the notes reference from posts/*.md.

    pip install markdown      # once
    python3 build.py          # after editing or adding a note

This is a reference, not a blog. Notes are grouped by topic, ordered basic to
advanced within each topic, and can declare what to read first. Nothing is
ordered by date, because a date is the least useful thing about a note you
intend to re-read in three years.
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

LEVELS = ["basic", "intermediate", "advanced"]

# Topic order on the index. A topic not listed here still renders - it goes to
# the bottom rather than being silently dropped.
TOPICS = [
    ("Foundations",  "Start here. Everything else assumes these."),
    ("Retrieval",    "Chunking, embeddings, search, ranking."),
    ("Agents",       "Tool use, memory, state, and keeping control of it."),
    ("Engineering",  "Python, APIs, testing, observability."),
    ("Production",   "What breaks, what it costs, and how you find out."),
    ("Things I got wrong", "Bugs that produced no error message."),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Notes — Sadhvi Sharma</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="wrap">

<header class="site">
  <nav><a href="/">Portfolio</a><a href="/learn/">Notes</a><a href="https://github.com/sadvi11">GitHub</a></nav>
</header>

<p class="crumb"><a href="/learn/">Notes</a> / {topic}</p>
<h1>{title}</h1>
<p class="lede">{lede}</p>
<p class="meta"><span class="lvl lvl-{level}">{level}</span>{tags}</p>
{prereq}
{toc}
{body}
{related}
<footer>
{footer}
  <p><a href="/learn/">← all notes</a></p>
</footer>

</div>
</body>
</html>
"""


def parse(path: pathlib.Path) -> dict:
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

    for req in ("title", "lede", "topic", "level"):
        if not meta.get(req):
            sys.exit(f"{path.name}: front matter needs a non-empty '{req}'")
    if meta["level"] not in LEVELS:
        sys.exit(f"{path.name}: level must be one of {LEVELS}, got {meta['level']!r}")

    meta["body_md"] = m.group(2)
    meta["slug"] = path.stem
    meta.setdefault("description", meta["lede"])
    meta.setdefault("footer", "")
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["prereq"] = [s.strip() for s in meta.get("prereq", "").split(",") if s.strip()]
    meta["related"] = [s.strip() for s in meta.get("related", "").split(",") if s.strip()]
    return meta


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def add_anchors(html: str) -> tuple[str, list[tuple[str, str]]]:
    """Give every h2 an id, and collect them for the contents box.

    Anchors matter more here than on a blog: the point of a reference is
    linking someone straight to the paragraph that answers them.
    """
    headings: list[tuple[str, str]] = []

    def repl(mo):
        text = mo.group(1)
        sid = slugify(text)
        headings.append((sid, re.sub(r"<[^>]+>", "", text)))
        return f'<h2 id="{sid}">{text}<a class="anchor" href="#{sid}">#</a></h2>'

    return re.sub(r"<h2>(.*?)</h2>", repl, html, flags=re.S), headings


def render(meta: dict, index: dict) -> str:
    body = markdown.markdown(
        meta["body_md"], extensions=["extra", "sane_lists", "smarty", "tables"])
    body, headings = add_anchors(body)

    toc = ""
    if len(headings) >= 3:
        items = "\n".join(f'    <li><a href="#{i}">{t}</a></li>' for i, t in headings)
        toc = f'<nav class="toc">\n  <p>On this page</p>\n  <ol>\n{items}\n  </ol>\n</nav>\n'

    prereq = ""
    if meta["prereq"]:
        links = ", ".join(
            f'<a href="{s}.html">{index[s]["title"]}</a>' for s in meta["prereq"] if s in index)
        if links:
            prereq = f'<p class="prereq"><b>Read first:</b> {links}</p>\n'

    related = ""
    if meta["related"]:
        items = "\n".join(
            f'  <li><a href="{s}.html">{index[s]["title"]}</a></li>'
            for s in meta["related"] if s in index)
        if items:
            related = f'<h2 id="related">Related</h2>\n<ul>\n{items}\n</ul>\n'

    tags = "".join(f'<span class="tg">#{t}</span>' for t in meta["tags"])

    footer = (f"  <p>{markdown.markdown(meta['footer'])[3:-4]}</p>\n"
              if meta["footer"] else "")

    return PAGE.format(
        title=meta["title"], description=meta["description"].replace('"', "&quot;"),
        topic=meta["topic"], lede=meta["lede"], level=meta["level"], tags=tags,
        prereq=prereq, toc=toc, body=body, related=related, footer=footer)


def build_index(posts: list[dict]) -> str:
    by_topic: dict[str, list[dict]] = {}
    for p in posts:
        by_topic.setdefault(p["topic"], []).append(p)

    known = [n for n, _ in TOPICS]
    ordered = known + [t for t in sorted(by_topic) if t not in known]

    out = []
    for name in ordered:
        items = by_topic.get(name)
        if not items:
            continue
        out.append(f'  <h2>{name}</h2>')
        blurb = dict(TOPICS).get(name, "")
        if blurb:
            out.append(f'  <p class="topic-blurb">{blurb}</p>')
        # basic first - the whole point of the ordering
        items.sort(key=lambda x: (LEVELS.index(x["level"]), x["title"]))
        for p in items:
            tags = "".join(f'<span class="tg">#{t}</span>' for t in p["tags"])
            out.append(
                f'\n  <a class="card" href="{p["slug"]}.html">\n'
                f'    <h3>{p["title"]}</h3>\n'
                f'    <p>{p["lede"]}</p>\n'
                f'    <p class="cardmeta"><span class="lvl lvl-{p["level"]}">'
                f'{p["level"]}</span>{tags}</p>\n'
                f'  </a>')
    return "\n".join(out)


MANIFEST = HERE / ".generated"


def prune(current: set[str]) -> None:
    """Delete pages whose markdown is gone.

    Without this, removing a note takes it off the index and leaves the page
    live at its URL. Only files this script previously wrote are removed -
    hand-written pages were never in the manifest, so a bug here cannot touch
    them.
    """
    previous = set()
    if MANIFEST.exists():
        previous = {line.strip() for line in MANIFEST.read_text().splitlines() if line.strip()}
    for orphan in sorted(previous - current):
        target = HERE / orphan
        if target.exists():
            target.unlink()
            print(f"  removed {orphan} (its markdown is gone)")
    MANIFEST.write_text("\n".join(sorted(current)) + "\n")


def main() -> int:
    paths = sorted(p for p in POSTS.glob("*.md") if p.stem != "TEMPLATE")
    if not paths:
        sys.exit("no notes found in posts/")

    posts = [parse(p) for p in paths]
    index = {p["slug"]: p for p in posts}

    # Fail on a reference to a note that does not exist. In a reference, a
    # dead "read first" link is worse than no link at all.
    for p in posts:
        for kind in ("prereq", "related"):
            for slug in p[kind]:
                if slug not in index:
                    sys.exit(f"{p['slug']}.md: {kind} points at '{slug}', which does not exist")

    for p in posts:
        (HERE / f"{p['slug']}.html").write_text(render(p, index))
        print(f"  {p['level']:12} {p['topic']:22} {p['slug']}.html")

    idx = (HERE / "index.html").read_text()
    new = re.sub(r"(<!-- POSTS -->).*?(<!-- /POSTS -->)",
                 lambda m: f"{m.group(1)}\n{build_index(posts)}\n  {m.group(2)}",
                 idx, flags=re.S)
    if "<!-- POSTS -->" not in idx:
        sys.exit("index.html is missing the <!-- POSTS --> markers")
    (HERE / "index.html").write_text(new)
    prune({f"{p['slug']}.html" for p in posts})

    print(f"\n  {len(posts)} notes across {len({p['topic'] for p in posts})} topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
