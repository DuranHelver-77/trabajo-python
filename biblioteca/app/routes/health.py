"""Endpoint de salud del sistema."""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.dependencies import SessionDep

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Estado de la API y base de datos",
    responses={503: {"description": "Base de datos no disponible"}},
)
def health_check(db: SessionDep):
    """
    Verifica que la API y la conexión a PostgreSQL estén activas.
    Responde 200 con status ok si todo funciona, 503 si la base de datos falla.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {"status": "ok", "database": db_status}
