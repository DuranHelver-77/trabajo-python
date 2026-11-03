"""
Fixtures de pytest para el Taller 2.
Usa una base de datos de prueba separada (TEST_DATABASE_URL).

ENVIRONMENT=test se inyecta vía pytest.ini (pytest-env) antes de importar la app,
lo que hace que main.py construya el Limiter con enabled=False.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app

settings = get_settings()

# ─── Motor de pruebas ─────────────────────────────────────────────────────────
TEST_URL = (
    settings.test_database_url
    or settings.database_url.replace("/biblioteca", "/biblioteca_test")
)
engine_test = create_engine(TEST_URL)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def crear_tablas():
    """Crea todas las tablas antes de los tests y las borra al finalizar."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db():
    """Sesión de BD de prueba con rollback automático."""
    connection = engine_test.connect()
    transaction = connection.begin()
    session = SessionTest(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """TestClient con la DB de prueba inyectada.
    
    El rate limiter está desactivado porque ENVIRONMENT=test hace que
    main.py construya el Limiter con enabled=False.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def registrar_socio(client, email="test@example.com", nombre="Test User", password="Password1"):
    resp = client.post("/api/v1/auth/registro", json={
        "email": email,
        "nombre": nombre,
        "password": password,
        "confirmar_password": password,
    })
    return resp


def login_usuario(client, email, password="Password1"):
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password,
    })
    return resp


def token_headers(client, email, password="Password1"):
    resp = login_usuario(client, email, password)
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


def crear_admin_directo(db):
    """Crea un admin directamente en la BD (sin pasar por la API)."""
    from app.core.security import hashear_password
    from app.models.usuario import Usuario, RolUsuario
    admin = Usuario(
        email="admin@biblioteca.com",
        nombre="Admin Sistema",
        password_hash=hashear_password("Admin1234"),
        rol=RolUsuario.admin,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def crear_biblio_directo(db):
    """Crea un bibliotecario directamente en la BD."""
    from app.core.security import hashear_password
    from app.models.usuario import Usuario, RolUsuario
    biblio = Usuario(
        email="biblio@biblioteca.com",
        nombre="Bibliotecario Test",
        password_hash=hashear_password("Biblio123"),
        rol=RolUsuario.bibliotecario,
    )
    db.add(biblio)
    db.commit()
    db.refresh(biblio)
    return biblio
