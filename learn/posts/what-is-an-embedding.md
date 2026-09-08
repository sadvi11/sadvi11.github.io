---
title: What an embedding actually is
lede: A vector where distance means similarity. The useful part is knowing what that buys you and, more importantly, what it cannot do.
topic: Foundations
level: basic
tags: embeddings, rag, vectors
related: why-hybrid-search, chunking-sets-the-ceiling
footer: Measured in [bedrock-rag-app](https://github.com/sadvi11/bedrock-rag-app).
---

In a supermarket, coriander sits near parsley. Not because the words look
alike, but because they get used the same way — someone looking for one will
find the other useful. The shelf position encodes meaning.

An embedding is that idea with numbers. Text goes in, a list of floats comes
out, and the distance between two lists approximates how related the two pieces
of text are. "How long for a refund" lands near "when do I get my money back"
without sharing a single content word.

## Where the analogy stops

A supermarket has one aisle per idea, and a person chose where things go.

Embedding space has hundreds of dimensions and no human-readable axes — you
cannot point at "the refund direction". And nobody chose the positions; they
were **learned from data**, which means they inherit whatever that data
believed.

## Dimensionality is a decision, not a property

I assumed for a long time that a model's vector size was fixed. It often is
not. Amazon's Titan Text Embeddings V2 takes an optional `dimensions`
parameter accepting **1024 (the default), 512, or 256**
([AWS docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-embed-text.html)).

So you are trading recall against storage and comparison time explicitly.
Every dimension is bytes on disk and work at query time.

## The thing that will bite you

**Embeddings are model-specific.** Change the model and the entire corpus has
to be re-embedded.

If you do not, old and new vectors sit in incompatible spaces. Nothing errors.
Nothing warns you. Search quality just degrades, and it degrades in a way that
looks like "the model got worse" rather than "the index is now meaningless".

## What they are bad at

They generalise. That is the whole point, and it is precisely wrong for
identifiers.

Order numbers, policy codes, SKUs, the literal string `RTN-14` — an embedding
maps those to whatever happens to sit near them, which is not the same as
matching them. A vector search will return its nearest neighbour with no
signal that the match is a stretch.

That single limitation is why [hybrid search](why-hybrid-search.html) exists.

## What I measured

In `bedrock-rag-app`, embedding is the cheapest stage of the pipeline —
**195 ms average**, against 1.53 s for generation. If you are optimising
latency, this is not where the time is going.
