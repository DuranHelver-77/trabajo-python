import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class RolUsuario(str, enum.Enum):
    admin = "admin"
    bibliotecario = "bibliotecario"
    socio = "socio"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rolusuario"), nullable=False, default=RolUsuario.socio
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    socio_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("socios.id", name="fk_usuarios_socio_id_socios"),
        unique=True,
        nullable=True,
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relaciones
    socio: Mapped["Socio"] = relationship("Socio", back_populates="usuario")  # noqa: F821
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(  # noqa: F821
        "RefreshToken", back_populates="usuario", cascade="all, delete-orphan"
    )
