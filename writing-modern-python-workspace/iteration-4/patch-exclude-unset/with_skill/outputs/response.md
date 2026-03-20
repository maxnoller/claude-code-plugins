```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

# Sentinel for "field was not sent"
_UNSET = object()

NonEmptyStr = Annotated[str, Field(min_length=1)]


class UserProfilePatch(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr | None = None
    email: EmailStr | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None

    def sent_fields(self) -> dict:
        """Returns only fields the client explicitly sent."""
        return self.model_dump(exclude_unset=True)
```

The key is `model_dump(exclude_unset=True)` — it distinguishes fields the client sent (even if `null`) from fields that were absent entirely:

```python
# Client sent: {"name": "Alice", "bio": null}
patch = UserProfilePatch(name="Alice", bio=None)

patch.sent_fields()
# {"name": "Alice", "bio": None}
# ✓ bio included — client explicitly nulled it
# ✓ email/avatar_url absent — client didn't send them

# Apply to DB: only update what was sent
await db.users.update(user_id, patch.sent_fields())
```

**Why not `exclude_none`**: it conflates "client sent null (clear the field)" with "client didn't send it at all" — you'd lose the ability to distinguish intentional nulling from absence.

If you need to distinguish "set to null" from "absent" for validation logic:

```python
def validate_patch(patch: UserProfilePatch) -> None:
    sent = patch.sent_fields()
    
    # bio can be nulled (cleared), but name cannot
    if "name" in sent and sent["name"] is None:
        raise ValueError("name cannot be cleared")
```
