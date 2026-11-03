"""Rutas de socios con autenticación, autorización y endpoints de perfil propio."""
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter

from app.core.dependencies import CurrentUser, PaginacionDep, SessionDep, Staff, requiere_rol
from app.core.exceptions import Prohibido, ReglaNegocio
from app.models.usuario import RolUsuario
from app.schemas.pagina import Pagina
from app.schemas.prestamo import MultaInfo, PrestamoOut
from app.schemas.socio import SocioActualizarPropio, SocioCreate, SocioOut, SocioUpdate
import app.controllers.socios as ctrl
import app.controllers.prestamos as ctrl_pres

router = APIRouter(prefix="/socios", tags=["Socios"])


# ─── Rutas de "me" (perfil propio del socio) ─────────────────────────────────

@router.get(
    "/me",
    response_model=SocioOut,
    summary="Perfil propio del socio",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def mi_perfil(usuario: CurrentUser, db: SessionDep):
    """Un socio puede ver su propio perfil."""
    if usuario.rol != RolUsuario.socio or not usuario.socio_id:
        raise Prohibido("No tiene un perfil de socio")
    return ctrl.obtener_socio(db, usuario.socio_id)


@router.patch(
    "/me",
    response_model=SocioOut,
    summary="Actualizar perfil propio (solo nombre y teléfono)",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        422: {"description": "Campo no permitido (extra=forbid)"},
    },
)
def actualizar_mi_perfil(
    datos: SocioActualizarPropio, usuario: CurrentUser, db: SessionDep
):
    """Z4 – Un socio solo puede cambiar nombre y teléfono."""
    if usuario.rol != RolUsuario.socio or not usuario.socio_id:
        raise Prohibido("No tiene un perfil de socio")
    return ctrl.actualizar_socio_propio(db, usuario.socio_id, datos)


@router.get(
    "/me/prestamos",
    response_model=Pagina[PrestamoOut],
    summary="Préstamos propios del socio",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def mis_prestamos(
    pag: PaginacionDep,
    usuario: CurrentUser,
    db: SessionDep,
    estado: Optional[str] = None,
):
    """Un socio ve solo sus propios préstamos."""
    if usuario.rol != RolUsuario.socio or not usuario.socio_id:
        raise Prohibido("No tiene un perfil de socio")
    items, total = ctrl.prestamos_de_socio(
        db, usuario.socio_id, pag.skip, pag.limit, estado
    )
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.get(
    "/me/multas",
    summary="Multas pendientes del socio",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def mis_multas(usuario: CurrentUser, db: SessionDep):
    """Devuelve préstamos con multa sin pagar y el total adeudado."""
    if usuario.rol != RolUsuario.socio or not usuario.socio_id:
        raise Prohibido("No tiene un perfil de socio")
    prestamos, total = ctrl_pres.multas_socio(db, usuario.socio_id)
    return {
        "items": [
            {
                "prestamo_id": p.id,
                "libro_titulo": p.libro.titulo if p.libro else "—",
                "multa": p.multa,
                "fecha_limite": str(p.fecha_limite),
            }
            for p in prestamos
        ],
        "total_adeudado": float(total),
    }


# ─── Rutas de administración (staff) ─────────────────────────────────────────

@router.get(
    "/",
    response_model=Pagina[SocioOut],
    summary="Listar socios",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def listar(pag: PaginacionDep, db: SessionDep, activo: Optional[bool] = None):
    items, total = ctrl.listar_socios(db, pag.skip, pag.limit, activo)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.get(
    "/{socio_id}",
    response_model=SocioOut,
    summary="Obtener socio por ID",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Socio no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def obtener(socio_id: int, db: SessionDep):
    return ctrl.obtener_socio(db, socio_id)


@router.post(
    "/",
    response_model=SocioOut,
    status_code=201,
    summary="Crear socio",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Email duplicado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def crear(datos: SocioCreate, db: SessionDep):
    return ctrl.crear_socio(db, datos)


@router.patch(
    "/{socio_id}",
    response_model=SocioOut,
    summary="Actualizar socio",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Socio no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def actualizar(socio_id: int, datos: SocioUpdate, db: SessionDep):
    return ctrl.actualizar_socio(db, socio_id, datos)


@router.delete(
    "/{socio_id}",
    status_code=204,
    summary="Eliminar o desactivar socio",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
    },
    dependencies=[requiere_rol(RolUsuario.admin)],
)
def eliminar(socio_id: int, db: SessionDep):
    ctrl.eliminar_socio(db, socio_id)


@router.get(
    "/{socio_id}/prestamos",
    response_model=Pagina[PrestamoOut],
    summary="Préstamos de un socio específico",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Socio no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def prestamos_del_socio(
    socio_id: int,
    pag: PaginacionDep,
    db: SessionDep,
    estado: Optional[str] = None,
):
    items, total = ctrl.prestamos_de_socio(db, socio_id, pag.skip, pag.limit, estado)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)
