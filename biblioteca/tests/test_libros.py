"""Tests de libros – permisos y paginación."""
from tests.conftest import (
    registrar_socio,
    token_headers,
    crear_admin_directo,
    crear_biblio_directo,
)


def crear_autor(client, headers, nombre="Gabriel García Márquez"):
    return client.post("/api/v1/autores/", json={"nombre": nombre}, headers=headers)


def crear_libro(client, headers, autor_id, isbn="9781234567890"):
    return client.post("/api/v1/libros", json={
        "titulo": "Cien años de soledad",
        "isbn": isbn,
        "anio_publicacion": 1967,
        "ejemplares": 3,
        "autor_id": autor_id,
        "categoria_ids": [],
    }, headers=headers)


class TestLibrosPublicos:
    def test_listar_libros_sin_token(self, client):
        """Caso 11: GET /libros sin token → 200 con items/total/skip/limit."""
        resp = client.get("/api/v1/libros")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data


class TestLibrosPermisos:
    def test_socio_no_puede_crear_libro(self, client, db):
        """Caso 12: POST /libros con token de socio → 403."""
        registrar_socio(client, "socio@example.com", "Socio Test")
        headers = token_headers(client, "socio@example.com")
        resp = client.post("/api/v1/libros", json={
            "titulo": "Libro", "isbn": "1234567890123",
            "anio_publicacion": 2020, "ejemplares": 1,
            "autor_id": 1, "categoria_ids": [],
        }, headers=headers)
        assert resp.status_code == 403

    def test_bibliotecario_puede_crear_libro(self, client, db):
        """Caso 13: POST /libros con token de bibliotecario → 201."""
        biblio = crear_biblio_directo(db)
        headers = token_headers(client, "biblio@biblioteca.com", "Biblio123")
        autor_resp = crear_autor(client, headers)
        assert autor_resp.status_code == 201
        autor_id = autor_resp.json()["id"]

        resp = crear_libro(client, headers, autor_id)
        assert resp.status_code == 201

    def test_bibliotecario_no_puede_borrar_libro(self, client, db):
        """Caso 14: DELETE /libros con token de bibliotecario → 403."""
        biblio = crear_biblio_directo(db)
        headers = token_headers(client, "biblio@biblioteca.com", "Biblio123")
        autor_resp = crear_autor(client, headers)
        autor_id = autor_resp.json()["id"]
        libro_resp = crear_libro(client, headers, autor_id)
        libro_id = libro_resp.json()["id"]

        resp = client.delete(f"/api/v1/libros/{libro_id}", headers=headers)
        assert resp.status_code == 403

    def test_admin_puede_borrar_libro(self, client, db):
        """Admin sí puede borrar libro sin préstamos activos."""
        admin = crear_admin_directo(db)
        admin_headers = token_headers(client, "admin@biblioteca.com", "Admin1234")
        autor_resp = crear_autor(client, admin_headers, "Autor Único")
        autor_id = autor_resp.json()["id"]
        libro_resp = crear_libro(client, admin_headers, autor_id, "9780000000001")
        libro_id = libro_resp.json()["id"]

        resp = client.delete(f"/api/v1/libros/{libro_id}", headers=admin_headers)
        assert resp.status_code == 204


class TestPortadaLibro:
    def test_subir_portada_sin_token_401(self, client):
        resp = client.post("/api/v1/libros/1/portada")
        assert resp.status_code == 401

    def test_subir_portada_socio_403(self, client, db):
        registrar_socio(client, "socio_portada@example.com", "Socio Portada")
        headers = token_headers(client, "socio_portada@example.com")
        resp = client.post(
            "/api/v1/libros/1/portada",
            files={"archivo": ("test.jpg", b"dummy content", "image/jpeg")},
            headers=headers,
        )
        assert resp.status_code == 403
