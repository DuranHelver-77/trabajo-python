"""
Punto de entrada principal de la API Biblioteca.
Taller 2: autenticación JWT, autorización por roles, migraciones Alembic.
"""
import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# ─── Importar todos los modelos para Alembic autogenerate ────────────────────
from app.core.config import get_settings
from app.core.limiter import limiter
import app.models  # noqa: F401
from app.core.exceptions import ErrorAplicacion, NoAutenticado
from app.routes import (
    auth,
    autores,
    categorias,
    health,
    libros,
    prestamos,
    reportes,
    socios,
    usuario,
)

# ─── Configuración ───────────────────────────────────────────────────────────
settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("biblioteca")

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
# limiter viene de app.core.limiter (disabled cuando ENVIRONMENT=test)

# ─── Instancia FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title="Biblioteca API REST – Taller 2",
    description=(
        "API REST segura con FastAPI, SQLAlchemy, Alembic, JWT y autorización por roles.\n\n"
        "**Roles**: anónimo · socio · bibliotecario · admin\n\n"
        "**Autenticación**: Bearer token (access token, 15 min) + refresh token (7 días)"
    ),
    version="2.0.0",
    docs_url=None if settings.environment == "prod" else "/docs",
    redoc_url=None if settings.environment == "prod" else "/redoc",
)

# ─── Rate limiting ────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Middleware: Request ID + logging ─────────────────────────────────────────
@app.middleware("http")
async def request_id_logging(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    response = await call_next(request)

    duracion_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s → %d (%.2f ms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
        request_id,
    )
    return response


# ─── Manejadores de errores ───────────────────────────────────────────────────
@app.exception_handler(ErrorAplicacion)
async def error_aplicacion_handler(request: Request, exc: ErrorAplicacion):
    headers = {}
    if isinstance(exc, NoAutenticado):
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


@app.exception_handler(Exception)
async def error_generico_handler(request: Request, exc: Exception):
    """Handler 500: registra el error internamente sin mostrar el stacktrace."""
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


# ─── Routers bajo /api/v1 ─────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(health.router, prefix=PREFIX)
app.include_router(auth.router, prefix=PREFIX)
app.include_router(usuario.router, prefix=PREFIX)
app.include_router(autores.router, prefix=PREFIX)
app.include_router(categorias.router, prefix=PREFIX)
app.include_router(libros.router, prefix=PREFIX)
app.include_router(socios.router, prefix=PREFIX)
app.include_router(prestamos.router, prefix=PREFIX)
app.include_router(reportes.router, prefix=PREFIX)
