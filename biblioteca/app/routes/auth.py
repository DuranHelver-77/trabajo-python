"""Rutas de autenticación: registro, login, refresh, logout y perfil propio."""
from fastapi import APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.core.dependencies import CurrentUser, SessionDep
from app.core.exceptions import NoAutenticado
from app.schemas.auth import CambioPassword, LogoutRequest, RefreshRequest, TokenRespuesta
from app.schemas.usuario import UsuarioRegistro, UsuarioRespuesta
import app.controllers.auth as ctrl

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Importar el limiter compartido (respeta enabled=False en tests)
from app.core.limiter import limiter


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=201,
    summary="Registro público de socio",
    responses={409: {"description": "Email duplicado"}, 429: {"description": "Límite de peticiones superado"}},
)
@limiter.limit("5/minute")
def registro(request: Request, datos: UsuarioRegistro, db: SessionDep):
    """
    Crea un usuario con rol **socio** y su registro de socio vinculado.
    La operación es atómica: si falla cualquiera de los dos, no se guarda nada.
    """
    return ctrl.registrar_usuario(db, datos)


@router.post(
    "/login",
    response_model=TokenRespuesta,
    summary="Inicio de sesión (OAuth2 Password Flow)",
    responses={
        401: {"description": "Credenciales inválidas"},
        423: {"description": "Cuenta bloqueada por demasiados intentos"},
        429: {"description": "Límite de peticiones superado"},
    },
)
@limiter.limit("10/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: SessionDep = None,
):
    """
    Recibe `username` (email) y `password` como formulario.
    Devuelve access token (15 min) y refresh token (7 días).
    Tras 5 intentos fallidos la cuenta se bloquea 15 minutos.
    """
    return ctrl.login(db, form.username, form.password)


@router.post(
    "/refresh",
    response_model=TokenRespuesta,
    summary="Renovar tokens con el refresh token",
    responses={401: {"description": "Token inválido, vencido o revocado"}},
)
def refresh(datos: RefreshRequest, db: SessionDep):
    """
    Rota el refresh token: el recibido queda revocado y se emite un par nuevo.
    Si se detecta reutilización de un token ya revocado, se revocan todos los del usuario.
    """
    return ctrl.refresh_tokens(db, datos.refresh_token)


@router.post(
    "/logout",
    status_code=204,
    summary="Cerrar sesión",
)
def logout(datos: LogoutRequest, db: SessionDep):
    """Revoca el refresh token recibido."""
    ctrl.logout(db, datos.refresh_token)


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Datos del usuario autenticado",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Usuario inactivo"},
    },
)
def me(usuario: CurrentUser):
    return usuario


@router.patch(
    "/me/password",
    status_code=204,
    summary="Cambiar contraseña propia",
    responses={422: {"description": "Contraseña actual incorrecta"}},
)
def cambiar_password(datos: CambioPassword, usuario: CurrentUser, db: SessionDep):
    """
    Cambia la contraseña del usuario autenticado y revoca todos sus refresh tokens.
    """
    ctrl.cambiar_password(db, usuario, datos)
