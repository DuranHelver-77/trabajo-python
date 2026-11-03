"""Rutas de gestión de usuarios (solo admin)."""
from typing import Optional
from fastapi import APIRouter

from app.core.dependencies import SessionDep, SoloAdmin, PaginacionDep
from app.models.usuario import RolUsuario
from app.schemas.pagina import Pagina
from app.schemas.usuario import (
    CambiarActivo,
    CambiarRol,
    UsuarioCrearStaff,
    UsuarioRespuesta,
)
import app.controllers.usuario as ctrl

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get(
    "",
    response_model=Pagina[UsuarioRespuesta],
    summary="Listar usuarios",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def listar(
    pag: PaginacionDep,
    db: SessionDep,
    admin: SoloAdmin,
    rol: Optional[RolUsuario] = None,
    activo: Optional[bool] = None,
):
    items, total = ctrl.listar_usuarios(db, pag.skip, pag.limit, rol, activo)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.post(
    "",
    response_model=UsuarioRespuesta,
    status_code=201,
    summary="Crear usuario staff",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Email duplicado"},
    },
)
def crear(datos: UsuarioCrearStaff, db: SessionDep, admin: SoloAdmin):
    return ctrl.crear_usuario_staff(db, datos)


@router.patch(
    "/{usuario_id}/rol",
    response_model=UsuarioRespuesta,
    summary="Cambiar rol de usuario",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "No puede cambiarse el rol a sí mismo"},
    },
)
def cambiar_rol(
    usuario_id: int, datos: CambiarRol, db: SessionDep, admin: SoloAdmin
):
    return ctrl.cambiar_rol(db, usuario_id, datos, admin)


@router.patch(
    "/{usuario_id}/activo",
    response_model=UsuarioRespuesta,
    summary="Activar o desactivar usuario",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "No puede desactivarse a sí mismo"},
    },
)
def cambiar_activo(
    usuario_id: int, datos: CambiarActivo, db: SessionDep, admin: SoloAdmin
):
    return ctrl.cambiar_activo(db, usuario_id, datos, admin)
