---
title: Counting tokens without a tokenizer
lede: I budget context in tokens and I do not use a tokenizer to do it. That is a deliberate choice, and the reason is the same reason every model ships its own.
topic: Engineering
level: intermediate
tags: tokens, cost, context, llm
prereq: what-is-an-embedding
related: rag-one-problem-at-a-time
footer: Implementation in [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/prompts.py`.
---

My context packer fills a token budget. It decides how many retrieved passages
fit in the prompt before the cost stops being worth it.

It counts tokens like this:

```python
CHARS_PER_TOKEN = 4

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)
```

Divide by four. That is the whole thing, and it is on purpose.

## What the estimate is for

The question this number answers is narrow: **does one more passage fit?**

That is a budgeting decision, and it tolerates error in a way that a hard limit
does not. If the estimate is 15% out, I drop a passage I could have kept, or
keep one I should have dropped. Neither is a failed request.

Being wrong in the safe direction costs a passage. Being precise costs a
dependency.

## Why a tokenizer is a bigger commitment than it looks

The obvious objection is: just use the real tokenizer, it is a pip install.

The problem is *which* real tokenizer. Every model family ships its own, and
they are not interchangeable — because a tokenizer is not a utility bolted on
before the model, it is **part of the model**.

The model was trained against specific token IDs. Swap the tokenizer and the
IDs stop meaning what the weights expect. You cannot upgrade one without
retraining the other.

So committing to a tokenizer means committing to a model family in a place in
my code that otherwise does not care which model it is talking to. My pipeline
is deliberately raw HTTP against an API. Pulling in a model-specific tokenizer
to count characters would put a hard dependency in the one layer I kept
portable.

## Why they differ at all

Three reasons, and they compound.

**Training data.** The tokenizer is learned from the corpus. One trained mostly
on English learns "hello" as a single token. Show it Hindi or Chinese and it
has no learned pieces for those words, so it fragments them into many small
ones. More tokens for the same meaning — slower and more expensive for exactly
the users who are already least well served.

**Vocabulary size.** Bigger vocabulary means fewer tokens per word, but a
larger embedding matrix. It is a real trade and teams land in different places:
T5-base uses a 32k vocabulary; Gemma 3 uses 256k
([SentencePiece README](https://github.com/google/sentencepiece)).

**Algorithm.** Byte-Pair Encoding, WordPiece, and the unigram language model
split text differently.

## One correction worth making

You will often see this listed as "BPE, SentencePiece, or WordPiece", as
though they were three algorithms.

They are not parallel. **SentencePiece is a library, and it implements BPE and
unigram** — from its own README: *"It implements subword units—including
Byte-Pair-Encoding (BPE) and the unigram language model."*

The algorithms are BPE, WordPiece and unigram. SentencePiece is one way to run
two of them, notable for treating input as raw Unicode so it needs no
language-specific pre-processing.

I mention it because I have repeated the wrong version myself, and because it
is the kind of detail that separates having read about something from having
looked it up.

## Where my estimate breaks

Four characters per token is a rule of thumb for English prose. It degrades on:

- **Other scripts** — the fragmentation problem above, and the direction of
  the error flips
- **Code** — punctuation-dense text tokenizes differently from prose
- **Long identifiers** — `ApproximateNumberOfMessagesVisible` is one word and
  several tokens

My corpus is English support documentation, so the heuristic holds. On a
multilingual corpus I would measure the real ratio before trusting it, and
probably land on a different constant rather than a different method.

## Estimated is not measured

The important part: **I do not report the estimate as usage.**

The estimate decides what to pack. The number I record as actual token
consumption comes back from the model response, where it is exact and costs
nothing to read.

Estimate to make a decision in advance. Measure to know what happened. Those
are different jobs and conflating them is how a cost dashboard ends up
confidently wrong.

## When I would switch

If I needed to *enforce* a hard limit rather than budget against a soft one —
rejecting a request that would exceed a context window rather than trimming
toward it — the estimate is no longer good enough and the dependency becomes
worth it.

I have not needed that. The budget is well below the window precisely so the
approximation has room to be wrong.
