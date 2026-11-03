"""Esquema genérico de respuesta paginada."""
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Respuesta paginada con total, skip y limit."""
    items: list[T]
    total: int
    skip: int
    limit: int
