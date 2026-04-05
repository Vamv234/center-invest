from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.enums import TokenType

password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class TokenValidationError(ValueError):
    """Raised when a JWT token is invalid or expired."""


@dataclass(slots=True)
class TokenPayload:
    subject: UUID
    session_id: UUID
    token_type: TokenType
    jti: str
    expires_at: datetime


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


def create_token(
    subject: UUID,
    session_id: UUID,
    token_type: TokenType,
    ttl_seconds: int,
    *,
    jti: str | None = None,
) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = datetime.fromtimestamp(issued_at.timestamp() + ttl_seconds, tz=timezone.utc)
    token_jti = jti or str(uuid4())
    payload = {
        "sub": str(subject),
        "session_id": str(session_id),
        "type": token_type.value,
        "jti": token_jti,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as error:
        raise TokenValidationError("Token has expired.") from error
    except InvalidTokenError as error:
        raise TokenValidationError("Token is invalid.") from error

    try:
        token_type = TokenType(payload["type"])
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        return TokenPayload(
            subject=UUID(str(payload["sub"])),
            session_id=UUID(str(payload["session_id"])),
            token_type=token_type,
            jti=str(payload["jti"]),
            expires_at=expires_at,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise TokenValidationError("Token payload is malformed.") from error


def create_access_token(subject: UUID, session_id: UUID) -> str:
    ttl_seconds = int(settings.access_token_ttl.total_seconds())
    return create_token(subject=subject, session_id=session_id, token_type=TokenType.ACCESS, ttl_seconds=ttl_seconds)


def create_refresh_token(subject: UUID, session_id: UUID, *, jti: str | None = None) -> tuple[str, str]:
    ttl_seconds = int(settings.refresh_token_ttl.total_seconds())
    refresh_jti = jti or str(uuid4())
    token = create_token(
        subject=subject,
        session_id=session_id,
        token_type=TokenType.REFRESH,
        ttl_seconds=ttl_seconds,
        jti=refresh_jti,
    )
    return token, refresh_jti


def refresh_token_key(jti: str) -> str:
    return f"auth:refresh:{jti}"
