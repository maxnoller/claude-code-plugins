from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# Reusable constrained types
NonEmptyStr = Annotated[str, Field(min_length=1)]
Email = Annotated[str, Field(pattern=r"^[\w.-]+@[\w.-]+\.\w+$")]
HttpUrl = Annotated[str, Field(pattern=r"^https?://")]


class UserSettingsPatch(BaseModel):
    """Partial update model for nested user settings."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    theme: str | None = None
    notifications_enabled: bool | None = None


class UserProfilePatch(BaseModel):
    """Partial update model for user profile (PATCH).

    All fields are optional. Use model_fields_set or model_dump(exclude_unset=True)
    to distinguish fields the caller explicitly sent from fields that are absent.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr | None = None
    email: Email | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None
    settings: UserSettingsPatch | None = None


def get_patch_fields(patch: UserProfilePatch) -> dict:
    """Return only the fields explicitly included in the PATCH request.

    Uses exclude_unset=True so that fields absent from the request body are
    omitted entirely — a field set to null is kept (intentional clear),
    while a field never sent is dropped (no-op for that column).

    For nested settings, the same logic applies: only sub-fields the caller
    sent are included, so you never accidentally overwrite a setting the
    client didn't touch.
    """
    dumped = patch.model_dump(exclude_unset=True)

    # If settings was included, also exclude unset sub-fields within it
    if "settings" in dumped and patch.settings is not None:
        dumped["settings"] = patch.settings.model_dump(exclude_unset=True)

    return dumped


# ---------------------------------------------------------------------------
# Usage example (not part of the production path — illustrative only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # Simulate a PATCH body that only touches name and one settings sub-field
    raw_body = '{"name": "Alice", "settings": {"theme": "dark"}}'

    patch = UserProfilePatch.model_validate_json(raw_body)

    print("Fields set by the caller:", patch.model_fields_set)
    # Fields set by the caller: {'name', 'settings'}

    updates = get_patch_fields(patch)
    print("Fields to apply to DB:", json.dumps(updates, indent=2))
    # {
    #   "name": "Alice",
    #   "settings": {
    #     "theme": "dark"
    #   }
    # }
    # Note: email, bio, avatar_url are absent — they won't be touched.
    # Note: notifications_enabled is absent inside settings — it won't be touched either.
