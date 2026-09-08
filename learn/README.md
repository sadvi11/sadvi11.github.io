# learn/ — how to add a post

Pages here are **generated**. Edit the markdown, not the HTML.

## Adding a note — two ways

### From the browser, no checkout

1. Go to `learn/posts/` on GitHub → **Add file → Create new file**
2. Name it `my-note.md`, paste the front matter from `TEMPLATE.md`, write
3. Commit

A GitHub Action rebuilds every page and the index, and commits the HTML back.
Live in about a minute. This works from a phone.

Editing an existing note is the same: open the `.md`, click the pencil, commit.

### Locally

```bash
cd learn
cp posts/TEMPLATE.md posts/my-new-post.md
# write it
python3 build.py
git add -A && git commit -m "notes: my new post" && git push
```

Live in about a minute at `sadvi11.github.io/learn/my-new-post.html`.

`build.py` regenerates every page and rebuilds the index cards. It needs one
dependency, once:

```bash
pip install markdown
```

## Front matter

```
---
title: The thing I am writing about
lede: One or two sentences. Shows on the index card and under the title.
tag: Things I got wrong
description: Optional. Defaults to the lede.
footer: Optional. Usually a link to the repo.
---
```

`title`, `lede` and `tag` are required — the build stops with a message naming
the file if one is missing, rather than publishing something half-formed.

**Tags with an existing section:** `Things I got wrong`, `Retrieval`, `Agents`,
`Production`. Anything else gets its own section at the bottom of the index.

## The filename is the URL

`posts/why-hybrid-search.md` publishes to `learn/why-hybrid-search.html`.
Renaming the file breaks every link anyone has to it, so rename deliberately.

## What makes these worth reading

Every post so far is a thing that went wrong in code that is public. That is
the whole differentiator — anyone can explain reciprocal rank fusion, and
almost nobody writes up the afternoon their own tests turned out to be
asserting nothing.

Before publishing, three checks are in `posts/TEMPLATE.md`:

- Does it open with something concrete, not a preamble?
- Is there at least one number, filename, or piece of real output?
- Would it be useful if somebody else had written it?

## What does not go here

The interview prep repository is private for a reason. Gap analyses, CV notes
and weakness logs are working files about shortfalls — they help nobody who
reads them, and they actively harm anyone recruiting.

Concepts, worked examples and bugs: public. Anything cataloguing what I cannot
do yet: private.
