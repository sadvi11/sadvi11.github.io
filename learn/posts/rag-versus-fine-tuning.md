---
title: RAG or fine-tuning — they answer different questions
lede: One changes what the model knows. The other changes how it behaves. Choosing between them is usually a category error.
topic: Foundations
level: basic
tags: rag, fine-tuning, architecture
related: what-is-an-embedding, chunking-sets-the-ceiling
---

The question is usually posed as a choice. It is not really one, because the
two things do different jobs.

**Retrieval changes what the model knows.** Put relevant text in the prompt and
the model answers from your data instead of its training.

**Fine-tuning changes how the model behaves.** Tone, output format, the shape
of its reasoning.

## The practical test

If the refund policy changes on Tuesday, what has to happen?

With retrieval: you update a document. With fine-tuning: you assemble training
data, run a job, evaluate it, and have a rollback story ready.

For facts that change, that is the whole argument.

## The reason I care more about

Retrieval is **auditable**. Every answer in my pipeline returns the passages
that produced it, with their scores. When a customer disputes an answer, I can
show which chunk caused it.

A fine-tuned model cannot tell you why it said something. For anything touching
money, policy, or a regulated domain, that traceability is not a nice-to-have.

## When fine-tuning is genuinely right

- **Consistent output format** — when schema validation keeps failing and you
  are tired of repairing responses
- **Domain tone** — a voice that a prompt keeps drifting away from
- **Cost** — when a small fine-tuned model beats a large prompted one at the
  same quality, which is a real and underrated reason

They also compose. Fine-tune for format and tone, retrieve for facts.

## The failure mode people hit

Reaching for fine-tuning because retrieval quality is poor.

If the right passage is not being retrieved, fine-tuning does not fix it — you
have taught the model to sound more confident about the same missing
information. The fix is upstream:
[chunking](chunking-sets-the-ceiling.html), then
[hybrid retrieval](why-hybrid-search.html), then reranking.

Fix retrieval before you consider training anything.
