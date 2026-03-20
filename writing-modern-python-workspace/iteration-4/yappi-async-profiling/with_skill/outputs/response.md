For async FastAPI, use `yappi` with wall clock — it follows execution across `await` boundaries, which `cProfile` can't do.

## Quick diagnosis: middleware-based profiling

Add this to your FastAPI app to profile every request:

```python
import yappi
from fastapi import FastAPI, Request
import asyncio

app = FastAPI()

@app.middleware("http")
async def profile_middleware(request: Request, call_next):
    yappi.set_clock_type("wall")  # wall clock for async — measures real elapsed time
    with yappi.run():
        response = await call_next(request)
    
    stats = yappi.get_func_stats()
    stats.sort("ttot")  # sort by total time
    stats.print_all(out=open(f"/tmp/profile_{request.url.path.replace('/', '_')}.txt", "w"))
    yappi.clear_stats()
    return response
```

Hit your slow endpoint once, then read the output file — it shows you exactly where time is spent.

## Targeted profiling for a specific endpoint

```python
import yappi
from fastapi import APIRouter

router = APIRouter()

@router.get("/slow-endpoint")
async def slow_endpoint():
    yappi.set_clock_type("wall")
    yappi.start()
    
    result = await do_the_work()
    
    yappi.stop()
    stats = yappi.get_func_stats()
    stats.sort("ttot")
    stats.print_all()
    yappi.clear_stats()
    
    return result
```

## Reading the output

```
name                          ncall  tsub   ttot   tavg
..orm/query.py:execute         12    0.002  2.341  0.195  ← database
..httpx/_client.py:send         3    0.001  0.891  0.297  ← external API
..myapp/service.py:transform    1    0.008  0.012  0.012  ← your code (fine)
```

- `ttot` — total time including callees (where the wall time actually goes)
- `tsub` — time in the function itself, excluding callees
- A high `ttot` with low `tsub` means the function is waiting on something it called

## Pinpointing further once you know the culprit

**If it's DB queries** — log slow queries directly:

```python
# SQLAlchemy: log queries over 100ms
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Or use event listeners for precise timing
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.monotonic())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.monotonic() - conn.info["query_start_time"].pop(-1)
    if total > 0.1:
        print(f"SLOW QUERY ({total:.3f}s): {statement[:200]}")
```

**If it's external API calls** — check if they're accidentally sequential:

```python
# BAD — these run one after another (2-3s if each takes 1s)
result_a = await fetch_service_a()
result_b = await fetch_service_b()

# GOOD — concurrent (total = slowest one, ~1s)
result_a, result_b = await asyncio.gather(
    fetch_service_a(),
    fetch_service_b(),
)
```

**If it's your own CPU-bound code** — it's blocking the event loop. Offload it:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor()

@router.get("/cpu-heavy")
async def cpu_heavy():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, cpu_bound_function, data)
    return result
```

## Install

```bash
uv add yappi
```

Start with the middleware approach — one request gives you the full call tree and you'll know within seconds whether you're looking at DB, network, or compute.
