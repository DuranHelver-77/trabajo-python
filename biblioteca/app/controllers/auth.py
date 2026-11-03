"""
Controlador de autenticación.
Reglas: A1-A7 del Taller 2.
"""
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    Conflicto,
    CuentaBloqueada,
    NoAutenticado,
    Prohibido,
    ReglaNegocio,
)
from app.core.security import (
    crear_token,
    decodificar_token,
    hashear_password,
    verificar_password,
)
from app.models.refresh_token import RefreshToken
from app.models.socio import Socio
from app.models.usuario import RolUsuario, Usuario
from app.schemas.auth import CambioPassword, TokenRespuesta
from app.schemas.usuario import UsuarioRegistro, UsuarioRespuesta

settings = get_settings()

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 15


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _par_tokens(db: Session, usuario: Usuario) -> TokenRespuesta:
    """Crea un par access+refresh, persiste el refresh token y retorna la respuesta."""
    access_td = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_td = timedelta(days=settings.refresh_token_expire_days)

    access_token, _ = crear_token(usuario, "access", access_td)
    refresh_token_str, jti = crear_token(usuario, "refresh", refresh_td)

    rt = RefreshToken(
        jti=jti,
        usuario_id=usuario.id,
        expira_en=datetime.now(timezone.utc) + refresh_td,
    )
    db.add(rt)
    db.commit()

    return TokenRespuesta(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=int(access_td.total_seconds()),
    )


def _revocar_todos_refresh(db: Session, usuario_id: int) -> None:
    """Revoca todos los refresh tokens de un usuario."""
    db.query(RefreshToken).filter(
        RefreshToken.usuario_id == usuario_id,
        RefreshToken.revocado.is_(False),
    ).update({"revocado": True})
    db.commit()


# ─── Registro ─────────────────────────────────────────────────────────────────

def registrar_usuario(db: Session, datos: UsuarioRegistro) -> UsuarioRespuesta:
    """
    Crea un usuario con rol socio y su socio vinculado en una sola transacción.
    409 si el email ya existe en usuarios o en socios.
    """
    email = datos.email.lower()

    if db.query(Usuario).filter(Usuario.email == email).first():
        raise Conflicto(f"Ya existe un usuario con email '{email}'")
    if db.query(Socio).filter(Socio.email == email).first():
        raise Conflicto(f"Ya existe un socio con email '{email}'")

    # Crear socio
    socio = Socio(
        nombre=datos.nombre,
        email=email,
        telefono=datos.telefono,
    )
    db.add(socio)
    db.flush()  # obtener el id sin commit aún

    # Crear usuario
    usuario = Usuario(
        email=email,
        nombre=datos.nombre,
        password_hash=hashear_password(datos.password),
        rol=RolUsuario.socio,
        socio_id=socio.id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UsuarioRespuesta.model_validate(usuario)


# ─── Login ────────────────────────────────────────────────────────────────────

def login(db: Session, username: str, password: str) -> TokenRespuesta:
    """
    Reglas:
      A1 – Credenciales incorrectas → 401 con mensaje genérico
      A2 – Usuario inactivo → 403
      A3 – 5 intentos → bloqueo 15 min → 423
    """
    ahora = datetime.now(timezone.utc)
    usuario: Usuario | None = db.query(Usuario).filter(
        Usuario.email == username.lower()
    ).first()

    # A3 – verificar bloqueo antes de validar la contraseña
    if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
        raise CuentaBloqueada("Cuenta bloqueada temporalmente")

    # A1 – mensaje idéntico si el email no existe o si la clave es incorrecta
    if not usuario or not verificar_password(password, usuario.password_hash):
        if usuario:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= MAX_INTENTOS:
                usuario.bloqueado_hasta = ahora + timedelta(minutes=BLOQUEO_MINUTOS)
            db.commit()
        raise NoAutenticado("Credenciales inválidas")

    # A2
    if not usuario.activo:
        raise Prohibido("Usuario inactivo")

    # Login correcto → resetear intentos
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.commit()

    return _par_tokens(db, usuario)


# ─── Refresh ──────────────────────────────────────────────────────────────────

def refresh_tokens(db: Session, refresh_token_str: str) -> TokenRespuesta:
    """
    A6 – Rota el refresh token.
    Si se reutiliza uno ya revocado, revoca todos los tokens del usuario.
    """
    try:
        payload = decodificar_token(refresh_token_str)
    except jwt.InvalidTokenError:
        raise NoAutenticado("Token inválido o vencido")

    if payload.get("type") != "refresh":
        raise NoAutenticado("Tipo de token inválido")

    jti = payload.get("jti")
    rt: RefreshToken | None = db.query(RefreshToken).filter(
        RefreshToken.jti == jti
    ).first()

    if not rt:
        raise NoAutenticado("Token inválido o vencido")

    # Token ya revocado: posible robo → revocar todos
    if rt.revocado:
        _revocar_todos_refresh(db, rt.usuario_id)
        raise NoAutenticado("Token ya utilizado: sesión cerrada por seguridad")

    # Vencido
    if rt.expira_en < datetime.now(timezone.utc):
        raise NoAutenticado("Token inválido o vencido")

    usuario: Usuario | None = db.get(Usuario, rt.usuario_id)
    if not usuario or not usuario.activo:
        raise Prohibido("Usuario inactivo")

    # Revocar el token actual (rotación)
    rt.revocado = True
    db.commit()

    return _par_tokens(db, usuario)


# ─── Logout ───────────────────────────────────────────────────────────────────

def logout(db: Session, refresh_token_str: str) -> None:
    """Revoca el refresh token recibido."""
    try:
        payload = decodificar_token(refresh_token_str)
    except jwt.InvalidTokenError:
        return  # silencioso: el token ya estaba inválido

    jti = payload.get("jti")
    if jti:
        db.query(RefreshToken).filter(RefreshToken.jti == jti).update(
            {"revocado": True}
        )
        db.commit()


# ─── Cambio de contraseña ─────────────────────────────────────────────────────

def cambiar_password(
    db: Session, usuario: Usuario, datos: CambioPassword
) -> None:
    """Verifica la contraseña actual, aplica el hash de la nueva y revoca tokens."""
    if not verificar_password(datos.password_actual, usuario.password_hash):
        raise ReglaNegocio("Contraseña actual incorrecta")
    usuario.password_hash = hashear_password(datos.password_nueva)
    db.commit()
    _revocar_todos_refresh(db, usuario.id)
