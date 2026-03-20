Perfect use case for `inline-snapshot` + `dirty-equals`. Run it once with `--inline-snapshot=fix` and it writes the expected output for you.

```python
from dirty_equals import IsDatetime, IsInt, IsUrl
from inline_snapshot import snapshot


def test_get_user_profile():
    result = get_user_profile(user_id=1)
    assert result == snapshot({
        "id": IsInt(),
        "name": "Alice",
        "email": "alice@example.com",
        "bio": "Software engineer",
        "avatar_url": IsUrl(),
        "created_at": IsDatetime(iso_string=True),
        "updated_at": IsDatetime(iso_string=True),
        "follower_count": IsInt(ge=0),
        "following_count": IsInt(ge=0),
        "is_verified": False,
        "location": "San Francisco, CA",
        "website": IsUrl(),
        "twitter_handle": "@alice",
    })
```

**First run** — populate the snapshot automatically:

```bash
uv run pytest --inline-snapshot=fix
```

This fills in all the exact values from your actual API response. For stable fields (`name`, `email`, `is_verified`, etc.) it writes the literal value. For dynamic fields you've already annotated with matchers (`IsInt`, `IsDatetime`, `IsUrl`), those stay as matchers.

**What each matcher does:**

| Matcher | Matches |
|---|---|
| `IsInt()` | any int |
| `IsInt(ge=0)` | non-negative int |
| `IsDatetime(iso_string=True)` | ISO 8601 string like `"2024-01-15T10:30:00Z"` |
| `IsUrl()` | any valid URL string |

**Why this catches regressions:** If someone renames `twitter_handle` to `twitter`, removes `bio`, or changes `is_verified` to a string — the assertion fails immediately with a clear diff showing exactly what changed. No per-field assertions to maintain.

Install the deps:

```bash
uv add --group dev inline-snapshot dirty-equals
```
