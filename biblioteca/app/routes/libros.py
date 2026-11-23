"""Rutas de libros con autenticación y autorización por rol."""
from typing import Optional
from fastapi import APIRouter, File, UploadFile

from app.core.dependencies import CurrentUser, PaginacionDep, SessionDep, Staff, requiere_rol
from app.models.usuario import RolUsuario
from app.schemas.libro import LibroCreate, LibroUpdate, LibroOut
from app.schemas.pagina import Pagina
from app.controllers.libros import OrdenLibro
import app.controllers.libros as ctrl

router = APIRouter(tags=["Libros"])


@router.get(
    "/libros",
    response_model=Pagina[LibroOut],
    summary="Listar libros (público)",
)
def listar(
    pag: PaginacionDep,
    db: SessionDep,
    buscar: Optional[str] = None,
    autor: Optional[str] = None,
    categoria_id: Optional[int] = None,
    desde: Optional[int] = None,
    hasta: Optional[int] = None,
    orden: Optional[OrdenLibro] = None,
):
    items, total = ctrl.listar_libros(
        db, pag.skip, pag.limit, buscar, autor, categoria_id, desde, hasta, orden
    )
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)


@router.get(
    "/libros/{libro_id}",
    response_model=LibroOut,
    summary="Obtener libro por ID (público)",
    responses={404: {"description": "Libro no encontrado"}},
)
def obtener(libro_id: int, db: SessionDep):
    return ctrl.obtener_libro(db, libro_id)


@router.post(
    "/libros",
    response_model=LibroOut,
    status_code=201,
    summary="Crear libro",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        409: {"description": "ISBN duplicado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def crear(datos: LibroCreate, db: SessionDep):
    return ctrl.crear_libro(db, datos)


@router.patch(
    "/libros/{libro_id}",
    response_model=LibroOut,
    summary="Actualizar libro",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Libro no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def actualizar(libro_id: int, datos: LibroUpdate, db: SessionDep):
    return ctrl.actualizar_libro(db, libro_id, datos)


@router.delete(
    "/libros/{libro_id}",
    status_code=204,
    summary="Eliminar libro",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Libro no encontrado"},
        409: {"description": "Tiene préstamos activos"},
    },
    dependencies=[requiere_rol(RolUsuario.admin)],
)
def eliminar(libro_id: int, db: SessionDep):
    ctrl.eliminar_libro(db, libro_id)


@router.post(
    "/libros/{libro_id}/portada",
    response_model=LibroOut,
    summary="Subir portada de libro",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Libro no encontrado"},
        422: {"description": "Error de validación o regla de negocio"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def subir_portada(
    libro_id: int,
    db: SessionDep,
    archivo: UploadFile = File(..., description="Imagen JPG, PNG o WEBP (máx. 5 MB)"),
):
    return ctrl.actualizar_portada_libro(db, libro_id, archivo)


@router.delete(
    "/libros/{libro_id}/portada",
    response_model=LibroOut,
    summary="Eliminar portada de libro",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso"},
        404: {"description": "Libro no encontrado"},
    },
    dependencies=[requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)],
)
def eliminar_portada(libro_id: int, db: SessionDep):
    return ctrl.eliminar_portada_libro(db, libro_id)


@router.get(
    "/autores/{autor_id}/libros",
    response_model=Pagina[LibroOut],
    tags=["Autores"],
    summary="Libros de un autor (público)",
    responses={404: {"description": "Autor no encontrado"}},
)
def libros_de_autor(autor_id: int, pag: PaginacionDep, db: SessionDep):
    items, total = ctrl.libros_de_autor(db, autor_id, pag.skip, pag.limit)
    return Pagina(items=items, total=total, skip=pag.skip, limit=pag.limit)
