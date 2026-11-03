"""Rutas de autores con autenticación y autorización por rol."""
from typing import Optional
from fastapi import APIRouter

from app.core.dependencies import PaginacionDep, SessionDep, requiere_rol
from app.models.usuario import RolUsuario
from app.schemas.autor import AutorCreate, AutorUpdate, AutorOut
from app.schemas.pagina import Pagina
import app.controllers.autores as ctrl

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get(
    "/",
    response_model=Pagina[AutorOut],
    summary="Listar autores (público)",
)
def listar(pag: PaginacionDep, db: SessionDep, nacionalidad: Optional[str] = None):
    items, total = ctrl.listar_autores(db, pag.skip, pag.limit, nacionalidad)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.get(
    "/{autor_id}",
    response_model=AutorOut,
    summary="Obtener autor por ID (público)",
    responses={404: {"description": "Autor no encontrado"}},
)
def obtener(autor_id: int, db: SessionDep):
    return ctrl.obtener_autor(db, autor_id)


@router.post(
    "/",
    response_model=AutorOut,
    status_code=201,
    summary="Crear autor",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Autor duplicado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def crear(datos: AutorCreate, db: SessionDep):
    return ctrl.crear_autor(db, datos)


@router.patch(
    "/{autor_id}",
    response_model=AutorOut,
    summary="Actualizar autor",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Autor no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def actualizar(autor_id: int, datos: AutorUpdate, db: SessionDep):
    return ctrl.actualizar_autor(db, autor_id, datos)


@router.delete(
    "/{autor_id}",
    status_code=204,
    summary="Eliminar autor",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Tiene libros registrados"},
    },
    dependencies=[requiere_rol(RolUsuario.admin)],
)
def eliminar(autor_id: int, db: SessionDep):
    ctrl.eliminar_autor(db, autor_id)
