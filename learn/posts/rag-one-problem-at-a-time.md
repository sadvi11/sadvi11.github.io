---
title: RAG, one problem at a time
lede: Every piece of a retrieval pipeline exists because something simpler broke first. This is the ladder, and an honest note about which rungs I have actually stood on.
topic: Foundations
level: basic
tags: rag, retrieval, architecture
related: what-is-an-embedding, chunking-sets-the-ceiling, why-hybrid-search
footer: Most of this is implemented in [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent).
---

RAG pipelines look complicated when you meet them as a finished diagram. They
are much easier to hold if you meet them the way they were built: each piece
exists because the thing before it broke.

Here is the ladder, with a note on each rung about whether I have built it or
only read about it. I am keeping that distinction visible because it is the
difference between a note worth reading and a summary of somebody else's blog.

## 1. The model does not know your data

**Fix: retrieval.** Fetch relevant documents at query time and put them in the
prompt.

That is the entire idea. Everything below is a repair to a problem this
creates.

→ [Why retrieval rather than fine-tuning](rag-versus-fine-tuning.html) · *built*

## 2. Keyword search misses meaning

Someone asks "when do I get my money back". Your document says "refunds are
processed within 30 days". Not one content word in common.

**Fix: embeddings and vector search.** Search by meaning rather than by string.

→ [What an embedding actually is](what-is-an-embedding.html) · *built*

## 3. Semantic search misses exact identifiers

Now the opposite failure. Somebody asks about policy `RTN-14` and the embedding
maps it to whatever happens to sit nearby, because generalising is what
embeddings do.

**Fix: hybrid search.** Run keyword search alongside vector search and fuse the
two rankings — by position, not score, because the scores are not on the same
scale.

→ [Why hybrid search, and how rank fusion works](why-hybrid-search.html) · *built*

## 4. Documents are too long to embed as one unit

**Fix: chunking.** Split into retrievable pieces.

And immediately: chunking sets the ceiling on everything downstream, because
retrieval cannot return a passage chunking never produced.

→ [Chunking sets the ceiling](chunking-sets-the-ceiling.html) · *built*

## 5. Chunks lose the context around them

A chunk reading "within 30 days" is useless on its own. The heading that gave
it meaning is two chunks up, and nothing scrolls up inside a vector index.

**Fix: attach document-level context to each chunk before embedding it.**

→ [The chunk that inherited the wrong heading](the-chunk-that-inherited-the-wrong-heading.html)
· *built, and got it wrong first*

## 6. The top results are noisy

Retrieval optimises recall — is the right passage in the top twenty at all.
That is not the same as having it first.

**Fix: reranking.** Score the shortlist again, more carefully.

*Built — with a caveat I would rather state than have found.* Mine scores term
overlap, not a cross-encoder. It measures vocabulary, not meaning, and it has a
failure I keep as a deliberately failing test: the question "what policy covers
salary disputes" scores at the threshold because the word "policy" matches,
though the corpus says nothing about salaries. The fix is a cross-encoder
behind the same interface, not a higher threshold.

---

## The three rungs I have not built

I have read about these. That is not the same thing, and this section exists so
I do not quietly imply otherwise.

**Query rewriting and HyDE.** The user's question is vague, so you improve it
before searching — or generate a hypothetical answer, embed *that*, and search
with it, on the theory that an answer looks more like the target passage than a
question does. It helps on sparse corpora. It also adds a model call to every
query, which on a chat turn is latency the customer feels. I would want to
measure that trade before adopting it, and I have not.

**GraphRAG.** When the answer is spread across documents and no single chunk
connects them, you extract entities and relationships into a graph and traverse
it. The cases I have seen it used for are multi-hop questions — "which of our
suppliers are affected by X" — where chunk-level retrieval structurally cannot
help. I have not built one, so I have no view on what it costs to maintain.

**Agentic RAG.** One retrieval pass is not enough, so the system retrieves,
judges what came back, and retrieves again. I have built agents with tool use
and iteration caps, but not a retrieval loop that evaluates its own results and
goes round again.

## Why the ladder is worth keeping in this order

Two reasons.

**Debugging.** When an answer is wrong, walk the rungs downward. Was the
passage retrieved at all? Then it is chunking or retrieval. Retrieved but
ranked low? Reranking. Ranked first but dropped before the prompt? Context
budget. In the prompt and still wrong? Now it is the prompt or the model.

**Not adding things you do not need.** Every rung costs latency, money and
another thing that can break. Hybrid search doubles your query cost. Reranking
adds a model call. GraphRAG adds an extraction pipeline and a graph to keep
current.

The right question is never "which techniques does a good RAG system have". It
is "which problem am I actually having".
