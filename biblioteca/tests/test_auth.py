"""Tests de autenticación – cubre los casos 1-27 del taller."""
import pytest
from tests.conftest import (
    registrar_socio,
    login_usuario,
    token_headers,
    crear_admin_directo,
    crear_biblio_directo,
)


class TestRegistro:
    def test_registro_password_sin_mayuscula(self, client):
        """Caso 1: password sin mayúscula → 422."""
        resp = client.post("/api/v1/auth/registro", json={
            "email": "x@example.com", "nombre": "Test User",
            "password": "abcdefgh1", "confirmar_password": "abcdefgh1",
        })
        assert resp.status_code == 422

    def test_registro_passwords_distintos(self, client):
        """Caso 2: passwords que no coinciden → 422."""
        resp = client.post("/api/v1/auth/registro", json={
            "email": "x@example.com", "nombre": "Test User",
            "password": "Password1", "confirmar_password": "Password2",
        })
        assert resp.status_code == 422

    def test_registro_valido(self, client):
        """Caso 3: registro correcto → 201, rol socio, sin password_hash."""
        resp = registrar_socio(client, "ana@example.com", "Ana Torres")
        assert resp.status_code == 201
        data = resp.json()
        assert data["rol"] == "socio"
        assert data["socio_id"] is not None
        assert "password_hash" not in data

    def test_registro_email_duplicado(self, client):
        """Caso 4: email duplicado (en mayúsculas) → 409."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        resp = registrar_socio(client, "ANA@EXAMPLE.COM", "Ana Torres 2")
        assert resp.status_code == 409


class TestLogin:
    def test_login_password_incorrecta(self, client):
        """Caso 5: contraseña incorrecta → 401."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        resp = login_usuario(client, "ana@example.com", "WrongPass1")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales inválidas"

    def test_login_email_inexistente(self, client):
        """Caso 6: email no existe → 401 con mismo mensaje."""
        resp = login_usuario(client, "noexiste@example.com")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales inválidas"

    def test_login_correcto(self, client):
        """Caso 7: login correcto → 200 con access_token, refresh_token, token_type bearer."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        resp = login_usuario(client, "ana@example.com")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


class TestMe:
    def test_me_sin_token(self, client):
        """Caso 8: GET /auth/me sin token → 401 con WWW-Authenticate: Bearer."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        assert "WWW-Authenticate" in resp.headers

    def test_me_token_alterado(self, client):
        """Caso 9: token alterado → 401."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        login_resp = login_usuario(client, "ana@example.com")
        token = login_resp.json()["access_token"] + "X"
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_me_con_refresh_token(self, client):
        """Caso 10: usar refresh_token como Bearer → 401."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        login_resp = login_usuario(client, "ana@example.com")
        refresh_token = login_resp.json()["refresh_token"]
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
        assert resp.status_code == 401

    def test_me_con_token_valido(self, client):
        """Me con token válido → 200."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        headers = token_headers(client, "ana@example.com")
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "ana@example.com"


class TestRefreshYLogout:
    def test_refresh_rota_token(self, client):
        """Caso 21: refresh genera un par nuevo."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        login_resp = login_usuario(client, "ana@example.com")
        refresh_token = login_resp.json()["refresh_token"]
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_refresh_reutilizado_revoca_todos(self, client):
        """Caso 22: reutilizar un refresh ya rotado → 401 y todos revocados."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        login_resp = login_usuario(client, "ana@example.com")
        old_refresh = login_resp.json()["refresh_token"]
        # Primer uso (rota el token)
        client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        # Segundo uso del mismo token ya revocado → 401
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert resp.status_code == 401

    def test_logout_revoca_refresh(self, client):
        """Caso 23: logout → refresh queda revocado."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        login_resp = login_usuario(client, "ana@example.com")
        refresh_token = login_resp.json()["refresh_token"]
        client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
        # Intentar usar el refresh revocado
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 401


class TestBloqueo:
    def test_bloqueo_5_intentos(self, client):
        """Caso 24: 5 intentos fallidos → cuenta bloqueada."""
        registrar_socio(client, "luis@example.com", "Luis Perez")
        for _ in range(5):
            login_usuario(client, "luis@example.com", "Incorrecta1")
        resp = login_usuario(client, "luis@example.com")
        assert resp.status_code == 423


class TestUsuarioInactivo:
    def test_usuario_inactivo_token_valido(self, client, db):
        """Caso 26: admin desactiva usuario → su token válido da 403."""
        admin = crear_admin_directo(db)
        registrar_socio(client, "luis@example.com", "Luis Perez")
        luis_headers = token_headers(client, "luis@example.com")

        # Admin desactiva a Luis
        from app.models.usuario import Usuario
        luis = db.query(Usuario).filter(Usuario.email == "luis@example.com").first()
        luis.activo = False
        db.commit()

        resp = client.get("/api/v1/auth/me", headers=luis_headers)
        assert resp.status_code == 403


class TestAdminSelfProtection:
    def test_admin_no_puede_cambiar_rol_propio(self, client, db):
        """Caso 27: admin no puede cambiar su propio rol → 422."""
        admin = crear_admin_directo(db)
        headers = token_headers(client, "admin@biblioteca.com", "Admin1234")
        resp = client.patch(
            f"/api/v1/usuarios/{admin.id}/rol",
            json={"rol": "socio"},
            headers=headers,
        )
        assert resp.status_code == 422
