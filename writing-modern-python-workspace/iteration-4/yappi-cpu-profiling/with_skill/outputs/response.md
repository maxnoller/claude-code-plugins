Use `yappi` with `cpu` clock mode — it's strictly better than `cProfile` for all Python profiling.

```python
import yappi
import pandas as pd

def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # your CPU-bound transformation
    ...

df = pd.read_parquet("large_file.parquet")

yappi.set_clock_type("cpu")  # cpu = measures actual compute time, ignores I/O wait
with yappi.run():
    result = transform_dataframe(df)

yappi.get_func_stats().print_all()
```

**Why `cpu` clock**: it measures only time spent on CPU, so I/O-waiting time (file reads, memory allocation pauses) doesn't inflate your numbers. You'll see exactly where computation is happening.

**Why yappi over cProfile**: same API simplicity, but yappi works correctly with threads and async — so you won't need to switch profilers if your code ever gains concurrency.

Install it:

```bash
uv add --group dev yappi
```

If you find a hot function and want to see *which lines within it* are slow, reach for `py-spy` or `scalene` — yappi is function-level only.
