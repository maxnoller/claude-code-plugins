# Profiling with yappi

## Why yappi over cProfile

Python's built-in `cProfile` breaks down with multithreaded and async code — it can't track coroutines or threads properly, and you can't attach/detach it at runtime. yappi is written in C (so it's fast), handles threads/async/gevent natively, and lets you start/stop profiling from any thread at any time. It's also PyCharm's default profiler.

## Basic usage

```python
import yappi

yappi.set_clock_type("cpu")  # or "wall" for wall-clock time
yappi.start()

# ... code to profile ...

yappi.stop()
yappi.get_func_stats().print_all()
yappi.get_thread_stats().print_all()
```

## Clock types

Pick the right clock for what you're measuring:

- **`cpu`** — actual CPU cycles consumed. Use this to find CPU-bound bottlenecks (ignores time spent waiting on I/O, sleep, locks).
- **`wall`** — real elapsed time. Use this for async code, I/O-bound work, or when you care about end-to-end latency.

```python
yappi.set_clock_type("wall")  # set before yappi.start()
```

## Context manager

```python
import yappi

yappi.set_clock_type("wall")
with yappi.run():
    asyncio.run(main())
yappi.get_func_stats().print_all()
```

## Async profiling

yappi correctly tracks coroutine execution time across context switches:

```python
yappi.set_clock_type("wall")
with yappi.run():
    asyncio.run(your_async_function())

# each coroutine shows up as its own function with accurate timing
yappi.get_func_stats().print_all()
```

## Multithreaded profiling

Per-thread breakdown without any manual wrapping:

```python
yappi.start()
# ... threaded work ...
yappi.stop()

for thread in yappi.get_thread_stats():
    print(f"Thread {thread.name} ({thread.id}):")
    yappi.get_func_stats(ctx_id=thread.id).print_all()
```

## Filtering results

Focus on what matters:

```python
# by module
stats = yappi.get_func_stats(
    filter_callback=lambda x: "myapp" in x.module
)

# by specific functions
stats = yappi.get_func_stats(
    filter_callback=lambda x: yappi.func_matches(x, [func_a, func_b])
)

# sort by total time
stats.sort("totaltime", "desc").print_all()
```

## Exporting results

```python
# for KCachegrind visualization
yappi.get_func_stats().save("profile.callgrind", type="callgrind")

# for Python's pstats module
yappi.get_func_stats().save("profile.pstat", type="pstat")
```

## When to use

- Profiling async applications (asyncio, anyio)
- Multithreaded or gevent-based services
- Long-running services where you need to profile on-the-fly
- When you need CPU time vs wall time distinction

## When NOT to use

- Quick one-off scripts where `python -m cProfile script.py` is good enough
- When you need line-level profiling (use `py-spy` or `scalene` instead)
