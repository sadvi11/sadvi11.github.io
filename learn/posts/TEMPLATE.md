---
title: The thing I am writing about
lede: One or two sentences. Shows on the index card and under the title. Say what happened, not what the note covers.
topic: Retrieval
level: basic
tags: rag, embeddings
prereq: what-is-an-embedding
related: why-hybrid-search
description: Optional. Defaults to the lede.
footer: Optional. Usually a link to the repo. Markdown fine.
---

Open with the concrete thing. Not "in this note I will explain" - start with
the situation, the number, or the bug.

## Sections are h2

They become the contents box automatically once there are three or more, and
each gets an anchor so you can link someone straight to the paragraph that
answers them.

Ordinary markdown: **bold**, `code`, [links](https://example.com), lists,
tables, fenced blocks, blockquotes.

## Front matter that matters

**topic** - groups it on the index. Existing: `Foundations`, `Retrieval`,
`Agents`, `Engineering`, `Production`, `Things I got wrong`. A new one gets its
own section at the bottom.

**level** - `basic`, `intermediate` or `advanced`. Index sorts basic first
within each topic, so the page reads as a path rather than a pile.

**prereq** - slugs to read first. Renders as a banner at the top. The build
**fails** if a slug does not exist, because a dead "read first" link is worse
than none.

**related** - slugs, rendered at the bottom.

## Before publishing

- Does it open with something concrete rather than a preamble?
- Is there a number, a filename, or real output somewhere in it?
- Would this be useful if somebody else had written it?
