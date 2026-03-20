"""
Pydantic models for partial PATCH updates to a user profile.

The key pattern: all fields are Optional with a default of None so that
clients can omit any field they don't want to change.  After validation,
model_fields_set tells you exactly which fields were present in the
incoming JSON, so you can apply only those to the stored record.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, HttpUrl


# ---------------------------------------------------------------------------
# Nested settings model
# ---------------------------------------------------------------------------

class UserSettingsPatch(BaseModel):
    """Partial update payload for the nested settings object."""

    theme: str | None = None
    notifications_enabled: bool | None = None


# ---------------------------------------------------------------------------
# Top-level patch request model
# ---------------------------------------------------------------------------

class UserProfilePatch(BaseModel):
    """
    All fields are optional so clients only need to send what they want
    to change.  Fields that are absent from the JSON body are NOT included
    in model_fields_set, which lets the endpoint distinguish "not provided"
    from "explicitly set to None".
    """

    name: str | None = None
    email: EmailStr | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None
    settings: UserSettingsPatch | None = None


# ---------------------------------------------------------------------------
# Helper: extract only the fields that were actually sent
# ---------------------------------------------------------------------------

def get_patch_data(patch: UserProfilePatch) -> dict[str, Any]:
    """
    Return a dict containing only the fields present in the request body.

    Uses model_fields_set (populated by Pydantic during validation) so that
    fields the client simply omitted are not included — even if their value
    would happen to be None.

    For nested models (e.g. settings) the same logic is applied recursively,
    so a partial settings update doesn't silently wipe fields the client
    didn't mention.
    """
    result: dict[str, Any] = {}

    for field_name in patch.model_fields_set:
        value = getattr(patch, field_name)

        # Recurse into nested patch models so we get their sent-fields too.
        if isinstance(value, BaseModel):
            result[field_name] = get_patch_data(value)  # type: ignore[arg-type]
        else:
            result[field_name] = value

    return result


# ---------------------------------------------------------------------------
# FastAPI application with the PATCH endpoint
# ---------------------------------------------------------------------------

app = FastAPI()

# Simulated database record — replace with a real DB call in production.
_fake_db: dict[str, Any] = {
    "user_123": {
        "name": "Alice",
        "email": "alice@example.com",
        "bio": "Software engineer",
        "avatar_url": "https://example.com/alice.png",
        "settings": {
            "theme": "light",
            "notifications_enabled": True,
        },
    }
}


@app.patch("/users/{user_id}", response_model=dict)
async def patch_user(user_id: str, patch: UserProfilePatch) -> dict[str, Any]:
    """
    Partially update a user profile.

    Only the fields present in the request body are applied; everything
    else is left untouched.
    """
    if user_id not in _fake_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    stored = _fake_db[user_id]
    updates = get_patch_data(patch)

    # Merge top-level fields.
    for key, value in updates.items():
        if key == "settings" and isinstance(value, dict):
            # Deep-merge the settings sub-object so only sent keys change.
            stored.setdefault("settings", {}).update(value)
        else:
            # Convert Pydantic special types (HttpUrl, EmailStr) to plain str.
            stored[key] = str(value) if not isinstance(value, (str, int, float, bool, type(None))) else value

    return stored


# ---------------------------------------------------------------------------
# Usage demo (run directly: python models.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # Simulate a request that only updates name and the theme setting.
    raw_payload = {
        "name": "Alice Smith",
        "settings": {
            "theme": "dark",
            # notifications_enabled intentionally omitted
        },
    }

    patch = UserProfilePatch.model_validate(raw_payload)

    print("Fields sent by the client:", patch.model_fields_set)
    # → Fields sent by the client: {'name', 'settings'}

    if patch.settings:
        print("Settings fields sent:", patch.settings.model_fields_set)
        # → Settings fields sent: {'theme'}

    patch_data = get_patch_data(patch)
    print("Data to apply to the DB:", json.dumps(patch_data, indent=2))
    # → {
    #     "name": "Alice Smith",
    #     "settings": {
    #       "theme": "dark"
    #     }
    #   }
