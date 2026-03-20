from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Reusable constrained types — define once, import everywhere.
# ---------------------------------------------------------------------------

NonEmptyStr = Annotated[str, Field(min_length=1)]
Email = Annotated[str, Field(pattern=r"^[\w.-]+@[\w.-]+\.\w+$")]
HttpUrl = Annotated[str, Field(pattern=r"^https?://")]


# ---------------------------------------------------------------------------
# Full / read model — what we store and return.
# ---------------------------------------------------------------------------


class UserSettings(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    theme: str
    notifications_enabled: bool


class UserProfile(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr
    email: Email
    bio: str | None
    avatar_url: HttpUrl | None
    settings: UserSettings


# ---------------------------------------------------------------------------
# PATCH models — every field is optional (no default means "not sent").
# frozen=False because these are transient input containers, not domain objects.
# ---------------------------------------------------------------------------


class UserSettingsPatch(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    theme: str | None = None
    notifications_enabled: bool | None = None


class UserProfilePatch(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr | None = None
    email: Email | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None
    settings: UserSettingsPatch | None = None


# ---------------------------------------------------------------------------
# Helper: extract only the fields that were actually sent by the client.
# ---------------------------------------------------------------------------


def get_patch_updates(patch: UserProfilePatch) -> dict:
    """Return a dict of only the fields the client explicitly sent.

    Uses exclude_unset=True — not exclude_none — so that a client sending
    {"bio": null} (intentional clear) is kept, while a field omitted entirely
    is dropped.  Nested settings are unpacked the same way.
    """
    updates = patch.model_dump(exclude_unset=True)

    # Unwrap the nested settings patch to its own unset-only dict so we don't
    # accidentally overwrite keys the client didn't mention.
    if "settings" in updates and patch.settings is not None:
        updates["settings"] = patch.settings.model_dump(exclude_unset=True)

    return updates


# ---------------------------------------------------------------------------
# FastAPI endpoint — wires everything together.
# ---------------------------------------------------------------------------

app = FastAPI()


@app.patch("/users/{user_id}", response_model=UserProfile)
async def patch_user(user_id: int, patch: UserProfilePatch) -> UserProfile:
    updates = get_patch_updates(patch)

    # `updates` contains only the keys the client sent, ready to merge into
    # whatever persistence layer you use.  Example:
    #
    #   existing = await db.get_user(user_id)           # fetch current record
    #   merged   = existing.model_copy(update=updates)  # non-mutating merge
    #   await db.save_user(user_id, merged)             # persist
    #
    # For demonstration, return a stub response showing what would be updated.
    stub_current = UserProfile(
        name="Alice",
        email="alice@example.com",
        bio=None,
        avatar_url=None,
        settings=UserSettings(theme="light", notifications_enabled=True),
    )

    # Merge nested settings separately if present.
    if "settings" in updates:
        current_settings = stub_current.settings.model_dump()
        current_settings.update(updates.pop("settings"))
        updates["settings"] = current_settings

    return stub_current.model_copy(update=updates)
