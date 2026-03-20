This is a pattern worth pushing back on. The modern Python principle here is: **don't add without intent**.

A `utils.py` full of speculative helpers is one of the most common sources of dead code in Python projects. Here's why each of these probably shouldn't exist:

**`capitalize_words`** — this is just `str.title()` or `" ".join(w.capitalize() for w in s.split())`. One line wherever you need it. No helper needed.

**`format_date`** — `datetime.strftime(fmt)` already does this. A wrapper adds a layer of indirection with no benefit. When you know what format you need, call it directly.

**`flatten_list`** — for one level: `list(itertools.chain.from_iterable(nested))`. For deep nesting, requirements vary enough that a generic helper is usually wrong. Write it when you have the actual data shape.

**`chunk_list`** — `itertools.batched(lst, n)` (Python 3.12+) does exactly this. It's in the stdlib.

```python
from itertools import batched, chain

# Need chunks? Just use this directly:
for chunk in batched(items, 100):
    process(chunk)

# Need to flatten? Just use this directly:
flat = list(chain.from_iterable(nested))
```

**The real rule**: write a helper when you've used the same 3+ lines in 3+ places in the *actual* codebase. Not before. A utils module created speculatively almost always ends up with half its functions never called, and the other half subtly wrong for the real use case when it arrives.

If you have a specific feature or module you're building, I'm happy to write exactly the utilities that feature needs — with the right signatures, edge case handling, and tests for the actual data shapes involved.
