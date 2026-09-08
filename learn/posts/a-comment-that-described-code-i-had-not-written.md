---
title: A comment that described code I had not written
lede: The docstring said the blocking call was dispatched to a thread so it would not hold the event loop. It was not. The results were identical, the tests passed, and the concurrency simply never happened.
tag: Things I got wrong
description: My docstring said the blocking call went to a thread pool. It did not. Same results, passing tests, no concurrency at all.
footer: Code and test: [amazon-connect-rag-agent](https://github.com/sadvi11/amazon-connect-rag-agent).
---

## The setup

A retrieval pipeline runs two searches — a dense vector search and a keyword
search. They hit different systems and neither depends on the other, so they
should run at the same time. The cost is then the slower of the two rather than
the sum.

```
dense, keyword = await asyncio.gather(
    _maybe_await(store.dense_search, query, k=k * 2),
    _maybe_await(store.keyword_search, query, k=k * 2),
)
```

The helper exists because the store might be synchronous — a plain boto3 or
psycopg client — or already async. Here is what I wrote:

```
async def _maybe_await(fn, *args, **kwargs):
    result = fn(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    # A synchronous store would block the event loop, so it goes to a thread.
    return result
```

Read the comment. Then read the last line.

## What was actually happening

Nothing goes to a thread. `fn(*args, **kwargs)` is called
*inline*, inside a coroutine. A blocking call there holds the event loop
for its entire duration, so the second search cannot begin until the first has
finished.

`asyncio.gather` was doing exactly what it was told and there was
nothing to overlap. I had written a comment describing the code I meant to
write, and then not written it.

The Python documentation is direct about the mechanism —
`loop.run_in_executor()` with a thread pool runs blocking code
*"in a different OS thread without blocking the OS thread that the event loop
runs in"*
([asyncio developer notes](https://docs.python.org/3/library/asyncio-dev.html#running-blocking-code)).
`asyncio.to_thread()` is the modern wrapper. I had used neither.

## Why no test caught it

This is the part worth sitting with. **The results were identical.**

Sequential and concurrent execution return the same passages in the same
order. Every correctness test passed, because correctness was never affected.
The only difference was elapsed time, and nothing was measuring elapsed time.

It is a bug that appears exclusively under load, in production, when
concurrency is the thing you were counting on.

## The fix, and the test that can see it

```
async def _maybe_await(fn, *args, **kwargs):
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return await asyncio.to_thread(fn, *args, **kwargs)
```

And the test measures **wall-clock time**, because that is the
only thing that can tell the difference:

```
async def test_the_two_searches_actually_overlap():
    store = SlowStore()          # each search sleeps 150ms
    start = time.perf_counter()
    await rag.retrieve_async("how long do refunds take", store)
    elapsed = time.perf_counter() - start

    sequential = SlowStore.DELAY * 2
    assert elapsed < sequential * 0.75, (
        f"took {elapsed:.3f}s against {sequential:.3f}s sequential - the "
        f"searches are not overlapping")
```

## What I took from it

Two things.

**A comment is not evidence about behaviour.** It is evidence
about intent, and intent and behaviour drift silently. I now read comments as a
question — *does it actually do this?* — rather than as documentation.

**Some properties are invisible to correctness tests.**
Concurrency, cost, and latency are not about whether the output is right. If
the only thing you assert is the result, you cannot see them — and they will
be perfectly fine right up until traffic arrives.
