from __future__ import annotations

from pydantic import BaseModel, EmailStr, HttpUrl


class UserProfilePatch(BaseModel):
    """
    Model for PATCH updates to a user profile.

    Only fields that are explicitly included in the request payload are
    considered "set". Fields that are absent from the payload are not
    included in model_fields_set, so callers can distinguish between
    "user sent this field" and "user did not mention this field".
    """

    name: str | None = None
    email: EmailStr | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None

    def updated_fields(self) -> dict:
        """
        Return only the fields that were explicitly provided in the request,
        even if their value is None (i.e. the caller intentionally cleared them).
        """
        return self.model_dump(include=self.model_fields_set)


# ---------------------------------------------------------------------------
# Usage examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Simulate a PATCH body that only updates name and clears bio
    payload = {"name": "Alice", "bio": None}
    patch = UserProfilePatch.model_validate(payload)

    print("Fields sent by client:", patch.model_fields_set)
    # -> {'name', 'bio'}

    print("Values for sent fields:", patch.updated_fields())
    # -> {'name': 'Alice', 'bio': None}

    print("email was sent?", "email" in patch.model_fields_set)
    # -> False  (absent, not touched)

    # Simulate a PATCH body that only updates email
    patch2 = UserProfilePatch.model_validate({"email": "alice@example.com"})
    print("\nFields sent by client:", patch2.model_fields_set)
    # -> {'email'}

    print("Values for sent fields:", patch2.updated_fields())
    # -> {'email': 'alice@example.com'}
