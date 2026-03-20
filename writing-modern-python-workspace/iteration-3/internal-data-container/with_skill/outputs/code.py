from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserInfo:
    user_id: int
    username: str
    roles: tuple[str, ...]
    created_at: datetime


def get_user(user_id: int) -> UserInfo:
    # Simulated fetch — replace with real DB/service call
    return UserInfo(
        user_id=user_id,
        username="alice",
        roles=("admin", "editor"),
        created_at=datetime(2025, 1, 15, 9, 0, 0),
    )


def has_role(user: UserInfo, role: str) -> bool:
    return role in user.roles


def greet(user: UserInfo) -> str:
    return f"Hello, {user.username} (id={user.user_id})"


if __name__ == "__main__":
    user = get_user(42)
    print(greet(user))
    print(has_role(user, "admin"))
