---
title: Abstention is a feature, not a failure
lede: The expensive mistake is not "I don't know". It is a confident wrong answer about somebody's money, delivered in the brand's voice.
topic: Production
level: intermediate
tags: rag, grounding, guardrails
prereq: why-hybrid-search
related: tests-that-were-lying
footer: Implementation in [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent) — `src/rag.py`.
---

A good pharmacist says "I can't advise on that, see your doctor." A bad one
guesses, to be helpful. The good one is more trustworthy precisely because
there is a line they will not cross.

## Why a prompt is not enough

The usual approach is an instruction: *"If the context does not contain the
answer, say you don't know."*

A prompt is a request. A persistent customer can move a model off it, and so
can text inside a retrieved document, because the model has no channel
separation — your instructions and the retrieved content are one token stream.

A function that returns early cannot be talked round.

## Two gates before, one after

```python
if not passages:
    return REFUSAL
if len(passages) < MIN_PASSAGES:      # one hit can be coincidence
    return REFUSAL
if max(p.score for p in passages) < MIN_RELEVANCE:
    return REFUSAL
```

Then generate. Then check again: if the model declined despite adequate
context, that is an abstention, not an answer.

## Generate last, not first

Checking after generating costs a model call you throw away — and it leaves an
unusable answer sitting in the process where a future maintainer may be tempted
to return it.

## The asymmetry that sets the threshold

Refusing a question you could have answered costs one transfer to a human.
Answering one you could not costs a customer a wrong answer about their money.

Those are not equal, so the threshold should not sit in the middle.

## Test each gate separately

Mine did not, at first. The passage-count gate was catching everything, so the
relevance threshold refused nothing at all — while still being cited as a
control in the README. Two checks where one is inert is worse than one honest
check, because the inert one still gets counted.
