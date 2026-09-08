---
title: The thing I am writing about
lede: One or two sentences. This shows on the index card and under the title. Say what happened, not what the article covers.
tag: Things I got wrong
description: Optional. Defaults to the lede. Used for search results and link previews.
footer: Optional. A closing line, usually a link to the repo. Markdown is fine.
---

Open with the concrete thing. Not "in this post I will explain" — start with
the situation.

## Use h2 for sections

Ordinary markdown works: **bold**, `code`, [links](https://example.com), lists,
tables, and fenced code blocks.

```python
def example():
    return "fenced blocks are fine"
```

> Blockquotes render as pull quotes.

## Tags that already have a section

- `Things I got wrong`
- `Retrieval`
- `Agents`
- `Production`

Any other tag gets its own section at the bottom of the index.

## Before publishing

- Does it open with something concrete rather than a preamble?
- Is there at least one number, file name, or piece of real output?
- Would this be useful if someone else wrote it?
