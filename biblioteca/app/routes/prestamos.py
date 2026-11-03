"""Rutas de préstamos con autenticación y autorización."""
from typing import Optional
from fastapi import APIRouter

from app.core.dependencies import CurrentUser, PaginacionDep, SessionDep, Staff, requiere_rol
from app.models.usuario import RolUsuario
from app.schemas.pagina import Pagina
from app.schemas.prestamo import PrestamoCreate, PrestamoDevolucion, PrestamoOut
import app.controllers.prestamos as ctrl

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.get(
    "/",
    response_model=Pagina[PrestamoOut],
    summary="Listar préstamos",
    responses={401: {"description": "No autenticado"}},
)
def listar(
    pag: PaginacionDep,
    db: SessionDep,
    usuario: CurrentUser,
    estado: Optional[str] = None,
    socio_id: Optional[int] = None,
    libro_id: Optional[int] = None,
):
    """
    - Staff: ve todos los préstamos (filtros opcionales).
    - Socio: solo sus propios préstamos (el filtro socio_id se ignora, Z3).
    """
    items, total = ctrl.listar_prestamos(
        db, pag.skip, pag.limit, estado, socio_id, libro_id, usuario
    )
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.get(
    "/{prestamo_id}",
    response_model=PrestamoOut,
    summary="Obtener préstamo por ID",
    responses={
        401: {"description": "No autenticado"},
        404: {"description": "Préstamo no encontrado o no pertenece al socio"},
    },
)
def obtener(prestamo_id: int, db: SessionDep, usuario: CurrentUser):
    """Z2 – Un socio recibe 404 si el préstamo no es suyo."""
    return ctrl.obtener_prestamo(db, prestamo_id, usuario)


@router.post(
    "/",
    response_model=PrestamoOut,
    status_code=201,
    summary="Registrar préstamo",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Ya tiene el libro"},
        422: {"description": "Regla de negocio no cumplida"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def crear(datos: PrestamoCreate, db: SessionDep, usuario: CurrentUser):
    """Z7 – registrado_por_id se guarda automáticamente."""
    return ctrl.crear_prestamo(db, datos, registrado_por=usuario)


@router.post(
    "/{prestamo_id}/devolucion",
    response_model=PrestamoOut,
    summary="Registrar devolución",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Préstamo no encontrado"},
        409: {"description": "Ya fue devuelto"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def devolver(prestamo_id: int, datos: PrestamoDevolucion, db: SessionDep):
    return ctrl.devolver_prestamo(db, prestamo_id, datos)


@router.post(
    "/{prestamo_id}/pago-multa",
    response_model=PrestamoOut,
    summary="Registrar pago de multa",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Préstamo no encontrado"},
        409: {"description": "Sin multa o ya pagada"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def pagar_multa(prestamo_id: int, db: SessionDep):
    return ctrl.pagar_multa(db, prestamo_id)
