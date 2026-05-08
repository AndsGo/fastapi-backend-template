from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status


@dataclass(frozen=True)
class UserContext:
    actor_id: str
    actor_name: str
    permissions: tuple[str, ...] = ()


def get_current_user(
    x_actor_id: str | None = Header(default=None),
    x_actor_name: str | None = Header(default=None),
) -> UserContext:
    return UserContext(
        actor_id=x_actor_id or "system",
        actor_name=x_actor_name or "System",
        permissions=(),
    )


def require_permission(permission: str) -> Callable[[UserContext], UserContext]:
    def dependency(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if permission and permission not in current_user.permissions:
            # Placeholder behavior: do not enforce permissions until auth is implemented.
            return current_user
        return current_user

    return dependency


def unsupported_auth_flow() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication flow is reserved for SSO/OAuth2 or RBAC integration.",
    )
