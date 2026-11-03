"""Rutas de reportes – solo para staff (admin o bibliotecario)."""
from typing import List
from fastapi import APIRouter

from app.core.dependencies import SessionDep, Staff
from app.schemas.reportes import (
    LibroMasPrestado,
    CategoriaTotalLibros,
    PrestamoVencido,
    SocioConMulta,
    AutorReporte,
    ResumenBiblioteca,
)
import app.controllers.reportes as ctrl

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get(
    "/libros-mas-prestados",
    response_model=List[LibroMasPrestado],
    summary="Top libros más prestados",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def libros_mas_prestados(db: SessionDep, staff: Staff, limite: int = 5):
    return ctrl.libros_mas_prestados(db, limite)


@router.get(
    "/categorias",
    response_model=List[CategoriaTotalLibros],
    summary="Total de libros por categoría",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def categorias(db: SessionDep, staff: Staff):
    return ctrl.categorias_total_libros(db)


@router.get(
    "/prestamos-vencidos",
    response_model=List[PrestamoVencido],
    summary="Préstamos vencidos",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def prestamos_vencidos(db: SessionDep, staff: Staff):
    return ctrl.prestamos_vencidos(db)


@router.get(
    "/socios-con-multas",
    response_model=List[SocioConMulta],
    summary="Socios con multas",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def socios_con_multas(db: SessionDep, staff: Staff):
    return ctrl.socios_con_multas(db)


@router.get(
    "/autores",
    response_model=List[AutorReporte],
    summary="Reporte de autores",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def autores(db: SessionDep, staff: Staff):
    return ctrl.reporte_autores(db)


@router.get(
    "/resumen",
    response_model=ResumenBiblioteca,
    summary="Resumen general de la biblioteca",
    responses={401: {"description": "No autenticado"}, 403: {"description": "Sin permiso"}},
)
def resumen(db: SessionDep, staff: Staff):
    return ctrl.resumen_biblioteca(db)
