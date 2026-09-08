---
title: The tests that were lying to me
lede: I had ninety-one passing tests and I felt safe. Three of them were protecting nothing at all, and the only way I found out was by breaking my own code on purpose.
tag: Things I got wrong
description: Ninety-one passing tests, and three of them asserted nothing at all. How deliberately breaking my own code found them.
footer: The fault injection script and the tests are public: [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent).
---

Put your hand up if you have a smoke alarm. Keep it up if you have pressed
the test button in the last six months.

That gap is the whole problem. We install the thing that is supposed to save
us and then trust it for years without ever asking it to prove it works. I did
exactly that, in code, for about eighteen months.

## The false comfort

The project is a contact-centre chat bot: retrieval over a knowledge base,
and a rule that it must refuse to answer rather than guess. Ninety-one tests,
all green, running on every push with no cloud account needed.

The word that matters is *safe*. Not confident — safe. I had stopped
looking at them.

## The uncomfortable question

Then: **how do I know any of these tests would actually notice?**

A test that cannot fail passes forever. It sits in the list looking exactly
like a real one, it gets counted, it gets cited in a README — and it is
protecting nothing.

So I wrote a script that reintroduces each defect on purpose, one at a time,
runs the suite, restores the file, and **fails the build if the suite
stayed green**.

```
ok    caught: the bot answers weak matches instead of refusing
ok    caught: a model saying "I don't know" counts as a contained answer
ok    caught: escalation never sets the flag the contact flow branches on
ok    caught: a confidently wrong bot reports perfect containment
...
All 15 defects are caught. The checks are load-bearing.
```

Twelve caught something. Three did not.

## What the three were

### 1. An assertion that passed either way

My chunker prepends a document heading to each chunk before embedding it, so
that a passage reading *"within 30 days"* still carries the word
*"Refunds"*. The test:

```
assert chunk.embedding_text.startswith("Refunds")
```

The fixture I used was a section whose body already began with the word
"Refunds". So the assertion was true whether or not the heading was prepended
at all. Delete the feature, test still passes.

The fix was to change the fixture so the body starts with a different word,
and add the assertion that actually matters:

```
assert not chunk.text.startswith("Refunds")   # fixture isolates the heading
assert chunk.embedding_text.startswith("Refunds")
assert chunk.embedding_text != chunk.text
```

### 2. A validator no code path could reach

I have a rule that an ungrounded answer must escalate to a human — otherwise
the customer is told "I don't know" and then left in a loop with the bot. It is
enforced in a Pydantic validator on the response model.

It was untested, and it looked tested. Every test went through the HTTP
endpoint, and the handler *derives* the escalation flag from whether the
answer was grounded. The invalid combination the validator guards against can
never be produced by that path.

The fix was to construct the model directly:

```
with pytest.raises(ValidationError):
    AskResponse(answer="I don't know", grounded=False, escalate=False, ...)
```

### 3. A safety check tested on one branch of two

I had refactored to add an async version of the answer path. That created two
copies of the check that treats a model refusal as an abstention. Only the
synchronous one had a test.

The injected fault landed in the async copy. Nothing went red.

## What actually got me

All three had been *counted*. When I said "ninety-one tests", I meant
it. I would have said it in an interview. I was not lying — I was
**confidently wrong**, which is worse, because being confidently
wrong does not feel like anything at all.

## The rule I use now

> A safety net I have not seen catch something is a decoration.

Not a bad thing. Just not the thing I thought it was.

This is not a new idea — it is mutation testing, and tools for it have
existed for years. What was new to me was running it against my own work and
finding out the answer was three.

The smoke alarm. The backup you have never restored from. The failover you
have never triggered. You do not need to distrust them. You need to make one of
them prove it, once.
