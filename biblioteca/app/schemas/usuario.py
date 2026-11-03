"""Schemas de usuarios."""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.models.usuario import RolUsuario


class UsuarioRegistro(BaseModel):
    """Datos para el registro público de un socio."""
    email: EmailStr
    nombre: str
    telefono: Optional[str] = None
    password: str
    confirmar_password: str

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, v: str) -> str:
        v = " ".join(v.split()).title()
        if not (3 <= len(v) <= 100):
            raise ValueError("nombre debe tener entre 3 y 100 caracteres")
        return v

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not (7 <= len(v) <= 15):
                raise ValueError("telefono debe tener entre 7 y 15 caracteres")
            if not re.match(r"^[\d\s+]+$", v):
                raise ValueError("telefono solo puede contener dígitos, espacios o +")
        return v

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if not (8 <= len(v) <= 64):
            raise ValueError("La contraseña debe tener entre 8 y 64 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

    @model_validator(mode="after")
    def passwords_coinciden(self) -> "UsuarioRegistro":
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class UsuarioRespuesta(BaseModel):
    """Respuesta pública de usuario (sin password_hash)."""
    id: int
    email: str
    nombre: str
    rol: RolUsuario
    activo: bool
    socio_id: Optional[int] = None
    creado_en: datetime

    model_config = {"from_attributes": True}


class UsuarioCrearStaff(BaseModel):
    """Crear usuario con rol bibliotecario o admin (solo para admin)."""
    email: EmailStr
    nombre: str
    password: str
    rol: RolUsuario

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, v: str) -> str:
        return " ".join(v.split()).title()

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if not (8 <= len(v) <= 64):
            raise ValueError("La contraseña debe tener entre 8 y 64 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v


class CambiarRol(BaseModel):
    rol: RolUsuario


class CambiarActivo(BaseModel):
    activo: bool
