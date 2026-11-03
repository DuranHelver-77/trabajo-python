from datetime import date
from decimal import Decimal
from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.libro import LibroOut
from app.schemas.socio import SocioOut


class PrestamoCreate(BaseModel):
    socio_id: int
    libro_id: int
    fecha_prestamo: Optional[date] = None
    dias: int = 14

    @field_validator("dias")
    @classmethod
    def validar_dias(cls, v: int) -> int:
        if not (1 <= v <= 30):
            raise ValueError("dias debe estar entre 1 y 30")
        return v


class PrestamoDevolucion(BaseModel):
    fecha_devolucion: Optional[date] = None


class PrestamoOut(BaseModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: Optional[date] = None
    multa: Decimal
    multa_pagada: bool = False
    estado: str
    registrado_por_id: Optional[int] = None
    socio: Optional[SocioOut] = None
    libro: Optional[LibroOut] = None

    model_config = {"from_attributes": True}


class MultaInfo(BaseModel):
    """Información de deuda de multas del socio."""
    prestamo_id: int
    libro_titulo: str
    multa: Decimal
    fecha_limite: date

    model_config = {"from_attributes": True}
