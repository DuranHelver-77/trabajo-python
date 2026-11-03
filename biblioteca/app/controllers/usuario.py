"""Controlador de gestión de usuarios (solo admin)."""
from sqlalchemy.orm import Session

from app.controllers.auth import _revocar_todos_refresh
from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.core.security import hashear_password
from app.models.refresh_token import RefreshToken
from app.models.socio import Socio
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import CambiarActivo, CambiarRol, UsuarioCrearStaff, UsuarioRespuesta


def listar_usuarios(
    db: Session,
    skip: int,
    limit: int,
    rol: RolUsuario | None = None,
    activo: bool | None = None,
) -> tuple[list[Usuario], int]:
    q = db.query(Usuario)
    if rol is not None:
        q = q.filter(Usuario.rol == rol)
    if activo is not None:
        q = q.filter(Usuario.activo == activo)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return items, total


def crear_usuario_staff(db: Session, datos: UsuarioCrearStaff) -> UsuarioRespuesta:
    email = datos.email.lower()
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise Conflicto(f"Ya existe un usuario con email '{email}'")
    usuario = Usuario(
        email=email,
        nombre=datos.nombre,
        password_hash=hashear_password(datos.password),
        rol=datos.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UsuarioRespuesta.model_validate(usuario)


def cambiar_rol(
    db: Session, usuario_id: int, datos: CambiarRol, solicitante: Usuario
) -> UsuarioRespuesta:
    """Z5 – Un admin no puede quitarse el rol a sí mismo."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise NoEncontrado(f"Usuario {usuario_id} no encontrado")

    if usuario.id == solicitante.id:
        raise ReglaNegocio("Un administrador no puede cambiar su propio rol")

    usuario.rol = datos.rol
    db.commit()
    # Z6 – revocar todos los refresh tokens del usuario afectado
    _revocar_todos_refresh(db, usuario.id)
    db.refresh(usuario)
    return UsuarioRespuesta.model_validate(usuario)


def cambiar_activo(
    db: Session, usuario_id: int, datos: CambiarActivo, solicitante: Usuario
) -> UsuarioRespuesta:
    """Z5 – Un admin no puede desactivarse a sí mismo."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise NoEncontrado(f"Usuario {usuario_id} no encontrado")

    if usuario.id == solicitante.id and not datos.activo:
        raise ReglaNegocio("Un administrador no puede desactivarse a sí mismo")

    usuario.activo = datos.activo
    db.commit()
    # Z6 – revocar todos los refresh tokens si se desactiva
    if not datos.activo:
        _revocar_todos_refresh(db, usuario.id)
    db.refresh(usuario)
    return UsuarioRespuesta.model_validate(usuario)
