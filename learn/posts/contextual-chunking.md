---
title: A chunk has to carry its own context
lede: What gets embedded and what gets displayed do not have to be the same string. Once you separate them, a whole class of retrieval failure disappears.
topic: Retrieval
level: intermediate
tags: chunking, rag, embeddings
prereq: chunking-sets-the-ceiling, what-is-an-embedding
related: the-chunk-that-inherited-the-wrong-heading, why-hybrid-search
footer: Implementation in [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/chunking.py`.
---

Imagine finding a sticky note that says **"within 30 days"** and nothing else.

It is not wrong. It is unusable, because it lost the thing that gave it
meaning. You could ask whoever wrote it. A retriever cannot — the chunk is
all there is.

## The failure this causes

Split a support document into chunks and you routinely get one like this:

```
Processing takes 30 days from the date we receive the item back.
Refunds are issued to the original payment method.
```

Nowhere in that text does the word **"refund"** appear as a topic. It was in
the heading, two hundred characters up, and the heading is now a different
chunk.

So when a customer asks *"how long do refunds take"*, the passage that answers
them exactly does not surface. Not because retrieval is bad — because the
chunk does not contain the word the question is about.

## The fix is one property

The insight is that **what gets embedded and what gets displayed do not have to
be the same string.**

```python
@property
def embedding_text(self) -> str:
    """What actually gets embedded.

    The heading is prepended so a chunk saying "within 30 days" still
    carries "Refunds" into its vector. Without this, that chunk is
    unreachable by anyone who asks about refunds - which is everyone.
    """
    return f"{self.heading}\n\n{self.text}".strip() if self.heading else self.text
```

Embed `embedding_text`. Show `text`. The heading does its work in vector space
and then gets out of the way.

## How far to take it

The heading is the cheapest version. You can attach more:

- **Section path** — `Refunds > Damaged goods > Reporting` rather than just the
  nearest heading
- **Document title** — matters when one corpus covers several products
- **A generated one-line summary** of the parent section

Each addition costs tokens in every chunk, in storage and at comparison time,
and dilutes the chunk's own content in its vector. A chunk that is 60% context
and 40% substance retrieves for the context and answers nothing.

I use the heading and the document title. I have not needed more, and I would
want an eval set showing a gain before adding it.

## The bug that made me careful

I had a minimum chunk size — fragments below it merge backwards into the
previous chunk, because a thirty-character fragment embeds to noise.

Correct, *within a section*. My implementation did not check that. A short
"Returns" section merged into the preceding "Refunds" chunk and
**inherited its heading** — so the returns text was now embedded under the
refunds topic, and unreachable by anyone asking about returns.

[The full write-up is here.](the-chunk-that-inherited-the-wrong-heading.html)

The fix was one line: only merge backwards into a chunk from the same section.

## What to test

Assert the negative, because it is the direction that silently stops being
true:

```python
def test_a_short_section_is_not_absorbed_into_the_previous_one():
    chunks = chunk_document(DOC, "help.md")
    assert "Returns" in {c.heading for c in chunks}
```

And make sure the test can actually fail. Mine could not, at first — the
fixture I used had a body that already began with the heading word, so
`embedding_text.startswith("Refunds")` was true whether or not the heading was
prepended at all. [I only found that by breaking the code on
purpose.](tests-that-were-lying.html)
