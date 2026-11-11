from dataclasses import dataclass
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import settings

# auto_error=False: return our own 401 (with WWW-Authenticate) when the header is missing
_bearer = HTTPBearer(auto_error=False)

# Fetches Keycloak's public keys once and caches them; refetches for an unknown key id
_jwks_client = jwt.PyJWKClient(
    f"{settings.keycloak_issuer}/protocol/openid-connect/certs"
)


@dataclass(frozen=True)
class User:
    sub: str
    username: str
    roles: frozenset[str]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"}
    )


def signing_key(token: str) -> Any:
    """Public key matching the token's `kid` header. Tests replace this."""
    return _jwks_client.get_signing_key_from_jwt(token).key


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        signing_key(token),
        algorithms=["RS256"],  # never trust the token's own "alg" header
        audience=settings.api_audience,
        issuer=settings.keycloak_issuer,
        options={"require": ["exp", "iat", "sub"]},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise _unauthorized("Not authenticated")
    try:
        claims = decode_token(credentials.credentials)
    except (jwt.InvalidTokenError, jwt.PyJWKClientError):
        raise _unauthorized("Invalid or expired token") from None
    return User(
        sub=claims["sub"],
        username=claims.get("preferred_username", claims["sub"]),
        roles=frozenset(claims.get("realm_access", {}).get("roles", [])),
    )


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(role: str):
    def check(user: CurrentUser) -> User:
        if role not in user.roles:
            raise HTTPException(status_code=403, detail=f"Requires the {role} role")
        return user

    return check


TraderUser = Annotated[User, Depends(require_role("trader"))]
