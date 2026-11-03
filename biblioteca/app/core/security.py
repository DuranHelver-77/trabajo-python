"""Módulo de seguridad: hash de contraseñas y creación/verificación de JWT."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()

# ─── Hash de contraseñas con Argon2 ─────────────────────────────────────────
_password_hash = PasswordHash.recommended()  # usa Argon2 por defecto


def hashear_password(password: str) -> str:
    """Devuelve el hash Argon2 de la contraseña."""
    return _password_hash.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Verifica la contraseña contra el hash almacenado."""
    return _password_hash.verify(password, hash_guardado)


# ─── JWT ─────────────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def crear_token(usuario, tipo: str, duracion: timedelta) -> tuple[str, str]:
    """
    Crea un JWT firmado con HS256.

    Returns:
        (token_codificado, jti)
    """
    ahora = datetime.now(timezone.utc)
    jti = str(uuid4())
    payload = {
        "sub": str(usuario.id),
        "rol": usuario.rol.value,
        "type": tipo,
        "iat": ahora,
        "exp": ahora + duracion,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, jti


def decodificar_token(token: str) -> dict:
    """
    Decodifica y verifica un JWT. Lanza jwt.InvalidTokenError si no es válido.
    Nota: siempre se pasa la lista algorithms; nunca se confía en el header del token.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
