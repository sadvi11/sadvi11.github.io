---
title: The chunk that inherited the wrong heading
lede: A short section fell below my minimum chunk size, merged backwards into the section before it, and took that section's heading with it. It then embedded under the wrong topic and became unreachable by anyone asking about it. Nothing errored.
tag: Things I got wrong
description: A short section merged into its neighbour, embedded under the wrong topic, and became unreachable. Nothing logged anything.
footer: Implementation: [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/chunking.py`.
---

## Why chunking is the ceiling

Retrieval cannot return a passage that chunking never produced. Whatever you
do downstream — hybrid search, fusion, a cross-encoder reranker — is bounded by
whether the right span of text exists as a unit in the index.

The default is to split every N characters. It is a photocopier with the
guillotine set to a fixed width: some pages come out cut mid-sentence, the
fragment makes no sense on its own, and — this is the part that matters — it
still looks like a complete page.

A chunk that starts with half a clause and ends with half another gets
embedded as a unit. The resulting vector is a blend of two incomplete thoughts
and matches neither well.

## So I split on structure

Headings and paragraphs are authored boundaries. Somebody already decided
those ideas belong together, and that decision is free information.

Three rules:

- **Structure before size.** Sections first, then pack paragraphs
up to a target length.
- **Overlap by whole sentences, not characters.** A sentence near
a boundary belongs to both neighbours; overlapping by character count
reintroduces exactly the mid-sentence cut you are trying to avoid.
- **Carry the heading into the chunk.** "Within 30 days" is
useless without "Refunds", and nothing scrolls up inside a vector index.

## The bug

I also had a minimum size, because a thirty-character fragment embeds to
noise and pollutes retrieval for everything else. Fragments below it get merged
backwards into the previous chunk.

Which is correct — *within a section*. My implementation did not check
that:

```
too_small = len(piece) < MIN_CHARS
can_merge = len(chunks) > 0          # <- the bug
```

Given a document like this:

```
# Refunds

Refunds are processed within 30 days of receiving the returned item...

# Returns

To return an item, use the returns portal and print the prepaid label.
```

The Returns section is 117 characters. Below the minimum. So it merged
backwards into the Refunds chunk — **and inherited the heading
"Refunds"**.

The text about the returns portal was now embedded under a refunds heading.
Anyone asking "how do I return an item" would not find it, and anyone asking
about refunds would get a passage half about something else.

## The fix is one line

```
section_start = len(chunks)          # per section
...
can_merge = len(chunks) > section_start
```

Merge backwards only into a chunk from the same section. A short section is
still a section.

And the test that catches it asserts the negative, which is the one that
silently stops being true:

```
headings = {c.heading for c in chunks}
assert "Returns" in headings, "the Returns section was absorbed"
```

## The test that was not testing anything

There is a second lesson here, and it is the one I did not expect.

I also had a test for the heading being carried into the chunk:

```
assert chunk.embedding_text.startswith("Refunds")
```

My fixture was a Refunds section whose body *already began* with the
word "Refunds". So that assertion was true whether or not the heading was
prepended at all. I could have deleted the feature entirely and the test would
still have passed.

I only found that by
[deliberately breaking the code and checking
whether anything went red](tests-that-were-lying.html). The fixture now starts the body with a different
word.

## What makes this class of bug hard

A bad photocopy is *visibly* bad. A bad chunk is not. It embeds fine,
it retrieves sometimes, it produces plausible answers to adjacent questions,
and it lowers quality quietly with nothing in any log.

Retrieval systems fail in this shape constantly. There is no exception, no
alert, no red build — just answers that are slightly worse than they should be,
in a way that only shows up if you go looking.
