---
title: Why hybrid search, and how rank fusion actually works
lede: A good embedding model cannot reliably find RTN-14. Keyword search cannot find a paraphrase. The interesting part is not running both — it is that you cannot add their scores together, and what you do instead.
topic: Retrieval
level: intermediate
tags: rag, retrieval, ranking, bm25
prereq: what-is-an-embedding, chunking-sets-the-ceiling
related: the-chunk-that-inherited-the-wrong-heading
description: Dense search cannot find RTN-14. Keyword search cannot find a paraphrase. Combining them needs rank, not score — worked through with real numbers.
footer: Implementation: [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/rag.py`.
---

## Where dense search fails

Ask a helpful shop assistant for "that blue jacket from the advert" and they
will find it. Ask for "SKU 4471-B" and the *helpful* one guesses at
something similar. You wanted the till system, which either matches the code
exactly or tells you it does not exist.

Embeddings generalise. That is the entire point of them, and it is precisely
wrong for identifiers. Order numbers, policy codes, SKUs, the literal phrase
"30 days" — an embedding maps those to whatever sits near them in vector space,
which is not the same as matching them.

And the assistant at least *knows* they are guessing. A vector search
returns its nearest neighbour with no signal that the match is a stretch.

Keyword search has the opposite failure: it cannot see that "how long for a
refund" and "when do I get my money back" are the same question. Which is how
customers actually write.

## The problem with combining them

So run both. Now you have two ranked lists and you need one.

The obvious move is to add the scores. It does not work, because cosine
similarity and BM25 relevance are not on the same scale and there is no honest
conversion between them. Normalising is a guess that changes with the corpus:
min-max over a batch means one outlier rescales everything, and z-scores assume
a distribution neither list has.

Two friends each rank ten restaurants. One scores out of ten, the other out
of a hundred, one is generous and one is harsh. Adding their numbers is
meaningless. But you can still use the *order*.

## Reciprocal rank fusion

```
RRFscore(d) = Σ  1 / (k + rank(d))
```

Position only. No scores at all, so there is nothing to normalise. A passage
that appears in both lists accumulates from both.

### Worked through

Query: *"What is the refund policy for RTN-14?"* — with k = 60.

<table>
<tr><th>Passage</th><th>Dense rank</th><th>Keyword rank</th><th>RRF score</th></tr>
<tr><td>**A** — refund policy</td><td>1</td><td>2</td><td>1/61 + 1/62 = **0.032522**</td></tr>
<tr><td>**D** — RTN-14 damaged goods</td><td>—</td><td>1</td><td>1/61 = **0.016393**</td></tr>
<tr><td>**B** — returns portal</td><td>2</td><td>—</td><td>1/62 = **0.016129**</td></tr>
<tr><td>**C** — shipping times</td><td>3</td><td>—</td><td>1/63 = **0.015873**</td></tr>
</table>

Two things fall out of that, and both are the point:

**A wins by roughly double.** Appearing in both lists beats
ranking first in one. That is what fusion is for.

**D beats B and C.** The exact policy code — which dense search
returned *nothing* for — still ranks second overall. That single row is
the argument for hybrid search.

Notice how close the individual contributions are: 0.0164, 0.0161, 0.0159.
With k = 60 the gap between rank 1 and rank 3 is tiny, so being present in two
lists matters far more than topping one. That is the behaviour k controls.

## On the value of k

k = 60 comes from the original paper — Cormack, Clarke and Büttcher,
*Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning
Methods*, SIGIR 2009. Their wording:

> k = 60 was fixed during a pilot investigation and not altered during
subsequent validation.

That is the whole justification. It is empirical, and the paper offers no
theory for it. I mention this because I originally wrote a plausible-sounding
explanation in my own code — something about damping the influence of any one
list's top result — and then read the paper and found the authors say no such
thing. Mathematically that damping is a real property of the formula. It is
just not why they chose the number.

[The paper is two pages.](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
It is worth the ten minutes.

## Then rerank

Fusion gives you a shortlist, not an answer. Retrieval optimises
**recall** — is the right passage in the top twenty at all.
Reranking optimises **precision** — is it first.

Sifting CVs works the same way: thirty seconds each to get four hundred down
to twenty, then read those twenty properly. You would never read four hundred
properly, and you would never hire from the thirty-second pass.

The reranker is a different kind of model. A bi-encoder embeds query and
document separately, so documents can be indexed in advance — fast, and it never
sees the pair together. A cross-encoder scores the pair jointly, which is
["generally superior"
and "often slower"](https://github.com/UKPLab/sentence-transformers/blob/master/docs/cross_encoder/usage/usage.rst), and far too slow to run over a whole corpus. Hence two
stages.

## What mine does not do

My reranker scores term overlap, not a cross-encoder. That measures
vocabulary, not meaning, and it has a failure I keep as a deliberately failing
test rather than deleting from the eval set: the question *"what policy
covers salary disputes"* scores at the threshold because the word "policy"
matches, even though the corpus says nothing about salaries.

The fix is a cross-encoder behind the same interface — not a higher
threshold, which would start refusing real questions.
