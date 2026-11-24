from datetime import date
from sqlalchemy import Boolean, Column, Date, Numeric, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    socio_id = Column(Integer, ForeignKey("socios.id"), nullable=False)
    fecha_prestamo = Column(Date, nullable=False, default=date.today)
    fecha_limite = Column(Date, nullable=False)
    fecha_devolucion = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    multa = Column(Numeric(10, 2), nullable=False, default=0)
    multa_pagada = Column(Boolean, nullable=False, default=False)
    registrado_por_id = Column(
        Integer,
        ForeignKey("usuarios.id", name="fk_prestamos_registrado_por_id_usuarios"),
        nullable=True,
    )

    socio = relationship("Socio", back_populates="prestamos")
    libro = relationship("Libro", back_populates="prestamos")
    registrado_por = relationship("Usuario", foreign_keys=[registrado_por_id])
