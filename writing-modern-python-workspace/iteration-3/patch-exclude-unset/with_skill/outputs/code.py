from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

NonEmptyStr = Annotated[str, Field(min_length=1)]


class UserProfilePatch(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    name: NonEmptyStr | None = None
    email: NonEmptyStr | None = None
    bio: str | None = None
    avatar_url: HttpUrl | None = None

    def fields_sent(self) -> dict:
        """Return only the fields explicitly included in the request."""
        return self.model_dump(exclude_unset=True)
