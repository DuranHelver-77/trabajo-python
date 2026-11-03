"""Tests del endpoint de health y usuarios."""
from tests.conftest import crear_admin_directo, token_headers


class TestHealth:
    def test_health_ok(self, client):
        """Caso 31: GET /api/v1/health → 200 con status ok y database ok."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "ok"


class TestSociosMe:
    def test_socio_actualizar_campo_no_permitido(self, client):
        """Caso 20: PATCH /socios/me con campo 'activo' → 422 (extra=forbid)."""
        from tests.conftest import registrar_socio
        registrar_socio(client, "ana@example.com", "Ana Torres")
        headers = token_headers(client, "ana@example.com")
        resp = client.patch("/api/v1/socios/me", json={"activo": False}, headers=headers)
        assert resp.status_code == 422


class TestUsuariosAdmin:
    def test_listar_usuarios_requiere_admin(self, client):
        """GET /usuarios sin token → 401."""
        resp = client.get("/api/v1/usuarios")
        assert resp.status_code == 401

    def test_listar_usuarios_admin(self, client, db):
        """Admin puede listar usuarios con paginación."""
        crear_admin_directo(db)
        headers = token_headers(client, "admin@biblioteca.com", "Admin1234")
        resp = client.get("/api/v1/usuarios", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_crear_bibliotecario(self, client, db):
        """Admin puede crear un bibliotecario."""
        crear_admin_directo(db)
        headers = token_headers(client, "admin@biblioteca.com", "Admin1234")
        resp = client.post("/api/v1/usuarios", json={
            "email": "nuevo@biblioteca.com",
            "nombre": "Nuevo Biblio",
            "password": "Biblio123",
            "rol": "bibliotecario",
        }, headers=headers)
        assert resp.status_code == 201
        assert resp.json()["rol"] == "bibliotecario"
