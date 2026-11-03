"""Rutas de categorías con autenticación y autorización por rol."""
from fastapi import APIRouter

from app.core.dependencies import PaginacionDep, SessionDep, requiere_rol
from app.models.usuario import RolUsuario
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaOut
from app.schemas.pagina import Pagina
import app.controllers.categorias as ctrl

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get(
    "/",
    response_model=Pagina[CategoriaOut],
    summary="Listar categorías (público)",
)
def listar(pag: PaginacionDep, db: SessionDep):
    items, total = ctrl.listar_categorias(db, pag.skip, pag.limit)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.post(
    "/",
    response_model=CategoriaOut,
    status_code=201,
    summary="Crear categoría",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "Categoría duplicada"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def crear(datos: CategoriaCreate, db: SessionDep):
    return ctrl.crear_categoria(db, datos)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaOut,
    summary="Actualizar categoría",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Categoría no encontrada"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def actualizar(categoria_id: int, datos: CategoriaUpdate, db: SessionDep):
    return ctrl.actualizar_categoria(db, categoria_id, datos)


@router.delete(
    "/{categoria_id}",
    status_code=204,
    summary="Eliminar categoría",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
    },
    dependencies=[requiere_rol(RolUsuario.admin)],
)
def eliminar(categoria_id: int, db: SessionDep):
    ctrl.eliminar_categoria(db, categoria_id)
