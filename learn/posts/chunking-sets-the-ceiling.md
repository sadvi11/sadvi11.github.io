---
title: Chunking sets the ceiling on everything downstream
lede: Retrieval cannot return a passage that chunking never produced. Whatever you do afterwards is bounded by that.
topic: Retrieval
level: basic
tags: chunking, rag, embeddings
prereq: what-is-an-embedding
related: the-chunk-that-inherited-the-wrong-heading, why-hybrid-search
footer: Implementation in [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/chunking.py`.
---

Everything clever you do downstream — hybrid search, rank fusion, a
cross-encoder reranker — is bounded by whether the right span of text exists as
a unit in the index. If chunking never produced it, no amount of ranking will
find it.

That makes chunking the least glamorous and most load-bearing decision in a
retrieval pipeline.

## The default is wrong in a specific way

Split every 500 characters. It is a photocopier with the guillotine set to a
fixed width: some pages come out cut mid-sentence, the fragment makes no sense
alone, and — this is the part that matters — **it still looks like a complete
page**.

A chunk beginning with half a clause and ending with half another gets embedded
as one unit. The resulting vector is a blend of two incomplete thoughts and
matches neither well.

## Three rules that fix most of it

**Structure before size.** Headings and paragraphs are authored boundaries.
Somebody already decided those ideas belong together, and that decision is free
information you are throwing away by counting characters.

**Overlap by whole sentences.** A sentence near a boundary belongs to both
neighbours — without overlap, an answer sitting across the seam is retrievable
from neither side. Overlapping by *character count* reintroduces exactly the
mid-sentence cut you were avoiding.

**Carry the heading into the chunk.** A passage reading "within 30 days" is
useless without "Refunds", and nothing scrolls up inside a vector index. What
gets embedded should be the heading plus the body, even if what gets displayed
is only the body.

## What it costs

Overlap costs storage and produces duplicate hits — the same passage arriving
twice from adjacent chunks. Reranking collapses those, so the cost is real but
bounded.

Structure-aware splitting costs you a parser and some edge cases. One of those
edge cases [cost me a section that became
unreachable](the-chunk-that-inherited-the-wrong-heading.html).

## How to choose the size

Honestly: start at roughly 500–800 characters, then tune against an eval set on
your actual corpus. Anyone quoting a universal number is quoting a starting
point as though it were a result.

Big enough to hold one complete idea. Small enough that one chunk is about one
thing.

## Why this is hard to notice going wrong

A bad photocopy is visibly bad. A bad chunk is not. It embeds fine, retrieves
sometimes, produces plausible answers to adjacent questions, and quietly lowers
quality with nothing in any log.

There is no exception, no alert, no red build — just answers slightly worse
than they should be, in a way that only surfaces if you go looking.
