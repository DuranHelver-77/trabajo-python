"""Schemas de autenticación y tokens."""
from pydantic import BaseModel


class TokenRespuesta(BaseModel):
    """Respuesta del login con access y refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshRequest(BaseModel):
    """Cuerpo para renovar tokens."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Cuerpo para revocar el refresh token en logout."""
    refresh_token: str


class CambioPassword(BaseModel):
    """Cuerpo para cambiar contraseña propia."""
    password_actual: str
    password_nueva: str
