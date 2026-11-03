from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import Conflicto, NoEncontrado
from app.models.prestamo import Prestamo
from app.models.socio import Socio
from app.schemas.socio import SocioActualizarPropio, SocioCreate, SocioUpdate


def listar_socios(
    db: Session, skip: int, limit: int, activo: Optional[bool]
) -> tuple[list[Socio], int]:
    q = db.query(Socio)
    if activo is not None:
        q = q.filter(Socio.activo == activo)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return items, total


def obtener_socio(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if not socio:
        raise NoEncontrado(f"Socio {socio_id} no encontrado")
    return socio


def crear_socio(db: Session, datos: SocioCreate) -> Socio:
    if db.query(Socio).filter(Socio.email == datos.email).first():
        raise Conflicto(f"Ya existe un socio con email '{datos.email}'")
    socio = Socio(**datos.model_dump())
    db.add(socio)
    db.commit()
    db.refresh(socio)
    return socio


def actualizar_socio(db: Session, socio_id: int, datos: SocioUpdate) -> Socio:
    socio = obtener_socio(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios and cambios["email"] != socio.email:
        if db.query(Socio).filter(Socio.email == cambios["email"]).first():
            raise Conflicto(f"Ya existe un socio con email '{cambios['email']}'")
    for k, v in cambios.items():
        setattr(socio, k, v)
    db.commit()
    db.refresh(socio)
    return socio


def actualizar_socio_propio(
    db: Session, socio_id: int, datos: SocioActualizarPropio
) -> Socio:
    """Actualización limitada (solo nombre y teléfono) para el socio autenticado."""
    socio = obtener_socio(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    for k, v in cambios.items():
        setattr(socio, k, v)
    db.commit()
    db.refresh(socio)
    return socio


def eliminar_socio(db: Session, socio_id: int) -> None:
    socio = obtener_socio(db, socio_id)
    tiene_historial = db.query(Prestamo).filter(Prestamo.socio_id == socio_id).first()
    if tiene_historial:
        # Borrado lógico
        socio.activo = False
        db.commit()
    else:
        db.delete(socio)
        db.commit()


def prestamos_de_socio(
    db: Session, socio_id: int, skip: int, limit: int, estado: Optional[str]
) -> tuple[list[Prestamo], int]:
    obtener_socio(db, socio_id)  # verifica existencia
    hoy = date.today()
    q = (
        db.query(Prestamo)
        .options(selectinload(Prestamo.libro), selectinload(Prestamo.socio))
        .filter(Prestamo.socio_id == socio_id)
    )
    if estado == "activo":
        q = q.filter(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite >= hoy,
        )
    elif estado == "vencido":
        q = q.filter(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < hoy,
        )
    elif estado == "devuelto":
        q = q.filter(Prestamo.fecha_devolucion.isnot(None))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return items, total
