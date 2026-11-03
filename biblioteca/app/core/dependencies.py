"""
Dependencias reutilizables de FastAPI:
  SessionDep        → sesión de base de datos
  CurrentUser       → usuario autenticado
  requiere_rol()    → verifica que el usuario tenga el rol requerido
  Staff             → shortcut para admin o bibliotecario
  PaginacionDep     → parámetros skip / limit
"""
from typing import Annotated, Generator

import jwt
from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import NoAutenticado, Prohibido
from app.core.security import decodificar_token, oauth2_scheme
from app.models.usuario import RolUsuario, Usuario


# ─── Sesión de base de datos ─────────────────────────────────────────────────

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


# ─── Usuario autenticado ──────────────────────────────────────────────────────

def get_current_user(
    db: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Usuario:
    """
    Decodifica el Bearer token y devuelve el usuario activo.
    Reglas A4, A5 y A7.
    """
    try:
        payload = decodificar_token(token)
    except jwt.InvalidTokenError:
        raise NoAutenticado("Token inválido o vencido")

    if payload.get("type") != "access":
        raise NoAutenticado("Tipo de token inválido")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise NoAutenticado("Token inválido o vencido")

    usuario: Usuario | None = db.get(Usuario, int(user_id_str))
    if not usuario:
        raise NoAutenticado("Token inválido o vencido")

    # A7: si el usuario fue desactivado, su token deja de servir
    if not usuario.activo:
        raise Prohibido("Usuario inactivo")

    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


# ─── Autorización por rol ─────────────────────────────────────────────────────

def requiere_rol(*roles: RolUsuario):
    """
    Devuelve una dependencia de FastAPI que verifica que el usuario tenga
    uno de los roles indicados. Regla Z1.
    """
    def verificar(usuario: CurrentUser) -> Usuario:
        if usuario.rol not in roles:
            raise Prohibido("No tiene permisos para esta acción")
        return usuario
    return Depends(verificar)


# Shortcut para endpoints de personal (admin o bibliotecario)
Staff = Annotated[
    Usuario,
    requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
]

SoloAdmin = Annotated[
    Usuario,
    requiere_rol(RolUsuario.admin),
]


# ─── Paginación ───────────────────────────────────────────────────────────────

class Paginacion:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Registros a omitir"),
        limit: int = Query(default=10, ge=1, le=100, description="Max registros"),
    ):
        self.skip = skip
        self.limit = limit


PaginacionDep = Annotated[Paginacion, Depends()]
