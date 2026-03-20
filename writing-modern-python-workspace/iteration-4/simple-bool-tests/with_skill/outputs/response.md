```python
import pytest
from your_module import is_valid_email


@pytest.mark.parametrize("email", [
    "user@example.com",
    "a@b",
    "user+tag@example.org",
    "user@sub.domain.com",
    "user@domain",
])
def test_valid_emails(email: str) -> None:
    assert is_valid_email(email)


@pytest.mark.parametrize("email", [
    "",           # empty string
    "@",          # empty local and domain
    "@domain",    # empty local part
    "user@",      # empty domain part
    "no-at-sign", # missing @
    "a@b@c",      # multiple @
    "@@",         # multiple @ with empty parts
])
def test_invalid_emails(email: str) -> None:
    assert not is_valid_email(email)
```

Since `is_valid_email` returns a plain `bool`, `parametrize` is the right tool here — inline-snapshot would be overkill for scalar boolean returns.

A few things worth noting about what these tests cover:

- **`all(parts)`** is the key behavior — it rejects empty strings on either side of `@`, so `@domain`, `user@`, and `@` all fail.
- **`len(parts) == 2`** means `a@b@c` fails (splits into 3 parts).
- The function has no regex — it won't reject `"not an email@also not"`, which is intentional given the docstring's stated contract. The tests reflect the *actual* contract, not an imagined stricter one.
