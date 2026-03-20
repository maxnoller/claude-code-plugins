"""
Internal user info data container.

Uses a frozen dataclass — the right tool for an internal data structure that:
  - groups related fields with type hints
  - is never serialized or received from outside
  - benefits from immutability (frozen=True) to prevent accidental mutation
  - needs a useful __repr__ and __eq__ for free
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class UserInfo:
    """Immutable snapshot of user information passed between service functions.

    Frozen so that callers cannot accidentally mutate shared state. If you need
    to derive a modified copy (e.g. updated roles), use dataclasses.replace().
    """

    user_id: int
    username: str
    roles: tuple[str, ...]  # tuple instead of list to preserve immutability
    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: int,
        username: str,
        roles: list[str],
        created_at: datetime | None = None,
    ) -> UserInfo:
        """Convenience constructor that accepts a plain list for roles and
        defaults created_at to the current UTC time when omitted."""
        return cls(
            user_id=user_id,
            username=username,
            roles=tuple(roles),
            created_at=created_at if created_at is not None else datetime.now(timezone.utc),
        )

    def has_role(self, role: str) -> bool:
        """Return True if this user holds the given role."""
        return role in self.roles


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

def get_user_from_db(user_id: int) -> UserInfo:
    """Simulate fetching a user and returning it as an internal container."""
    return UserInfo.create(
        user_id=user_id,
        username="alice",
        roles=["viewer", "editor"],
        created_at=datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


def process_user(user: UserInfo) -> None:
    print(f"Processing user: {user.username!r} (id={user.user_id})")
    print(f"  Roles  : {list(user.roles)}")
    print(f"  Created: {user.created_at.isoformat()}")
    print(f"  Is editor? {user.has_role('editor')}")
    print(f"  Is admin?  {user.has_role('admin')}")

    # Derive a modified copy without mutating the original
    import dataclasses
    promoted = dataclasses.replace(user, roles=(*user.roles, "admin"))
    print(f"  After promotion — roles: {list(promoted.roles)}")


if __name__ == "__main__":
    user = get_user_from_db(42)
    process_user(user)
