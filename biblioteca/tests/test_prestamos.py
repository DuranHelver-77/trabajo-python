"""Tests de préstamos – permisos, propiedad y reglas R11/Z2/Z3."""
from datetime import date, timedelta
from tests.conftest import (
    registrar_socio,
    token_headers,
    crear_admin_directo,
    crear_biblio_directo,
)


def setup_libro_y_socios(client, db):
    """Crea autor, libro, Ana y Luis listos para préstamos."""
    biblio = crear_biblio_directo(db)
    b_headers = token_headers(client, "biblio@biblioteca.com", "Biblio123")

    registrar_socio(client, "ana@example.com", "Ana Torres")
    registrar_socio(client, "luis@example.com", "Luis Perez")

    autor_resp = client.post("/api/v1/autores/", json={"nombre": "Autor Test"}, headers=b_headers)
    autor_id = autor_resp.json()["id"]

    libro_resp = client.post("/api/v1/libros", json={
        "titulo": "Libro Test", "isbn": "9780000000099",
        "anio_publicacion": 2020, "ejemplares": 3,
        "autor_id": autor_id, "categoria_ids": [],
    }, headers=b_headers)
    libro_id = libro_resp.json()["id"]

    from app.models.usuario import Usuario
    ana = db.query(Usuario).filter(Usuario.email == "ana@example.com").first()
    luis = db.query(Usuario).filter(Usuario.email == "luis@example.com").first()

    return b_headers, libro_id, ana.socio_id, luis.socio_id


class TestPrestamosPermisos:
    def test_registrar_prestamo_guarda_registrado_por(self, client, db):
        """Caso 15: registrado_por_id debe ser el id del bibliotecario."""
        b_headers, libro_id, ana_id, _ = setup_libro_y_socios(client, db)
        resp = client.post("/api/v1/prestamos/", json={
            "socio_id": ana_id,
            "libro_id": libro_id,
        }, headers=b_headers)
        assert resp.status_code == 201
        assert resp.json()["registrado_por_id"] is not None

    def test_listar_prestamos_socio_solo_ve_los_suyos(self, client, db):
        """Casos 17 y 18: socio solo ve sus préstamos, aunque envíe ?socio_id= de otro."""
        b_headers, libro_id, ana_id, luis_id = setup_libro_y_socios(client, db)

        # Crear préstamos para Ana y Luis
        client.post("/api/v1/prestamos/", json={"socio_id": ana_id, "libro_id": libro_id}, headers=b_headers)
        client.post("/api/v1/prestamos/", json={"socio_id": luis_id, "libro_id": libro_id}, headers=b_headers)

        ana_headers = token_headers(client, "ana@example.com")

        # Ana ve solo sus préstamos
        resp = client.get("/api/v1/prestamos/", headers=ana_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        # Ana intenta filtrar por luis_id → sigue viendo solo los suyos (Z3)
        resp2 = client.get(f"/api/v1/prestamos/?socio_id={luis_id}", headers=ana_headers)
        assert resp2.json()["total"] == 1

    def test_socio_no_ve_prestamo_ajeno_404(self, client, db):
        """Caso 19: socio recibe 404 en préstamo de otro (Z2)."""
        b_headers, libro_id, ana_id, luis_id = setup_libro_y_socios(client, db)

        # Crear préstamo para Luis
        pres_resp = client.post("/api/v1/prestamos/", json={"socio_id": luis_id, "libro_id": libro_id}, headers=b_headers)
        luis_pres_id = pres_resp.json()["id"]

        # Ana intenta ver el préstamo de Luis → 404
        ana_headers = token_headers(client, "ana@example.com")
        resp = client.get(f"/api/v1/prestamos/{luis_pres_id}", headers=ana_headers)
        assert resp.status_code == 404


class TestMultas:
    def test_multa_pendiente_bloquea_nuevo_prestamo(self, client, db):
        """Caso 29: socio con multa pendiente no puede pedir préstamo."""
        b_headers, libro_id, ana_id, _ = setup_libro_y_socios(client, db)

        # Crear préstamo atrasado para Ana
        hace_20 = (date.today() - timedelta(days=20)).isoformat()
        pres_resp = client.post("/api/v1/prestamos/", json={
            "socio_id": ana_id, "libro_id": libro_id,
            "fecha_prestamo": hace_20, "dias": 7,
        }, headers=b_headers)
        pres_id = pres_resp.json()["id"]

        # Devolver con multa
        client.post(f"/api/v1/prestamos/{pres_id}/devolucion", json={}, headers=b_headers)

        # Ana intenta pedir otro libro → 422 por multa pendiente
        resp = client.post("/api/v1/prestamos/", json={"socio_id": ana_id, "libro_id": libro_id}, headers=b_headers)
        assert resp.status_code == 422
        assert "multas pendientes" in resp.json()["detail"].lower()

    def test_pagar_multa_permite_nuevo_prestamo(self, client, db):
        """Caso 30: pagar multa → nuevo préstamo funciona."""
        b_headers, libro_id, ana_id, _ = setup_libro_y_socios(client, db)

        hace_20 = (date.today() - timedelta(days=20)).isoformat()
        pres_resp = client.post("/api/v1/prestamos/", json={
            "socio_id": ana_id, "libro_id": libro_id,
            "fecha_prestamo": hace_20, "dias": 7,
        }, headers=b_headers)
        pres_id = pres_resp.json()["id"]
        client.post(f"/api/v1/prestamos/{pres_id}/devolucion", json={}, headers=b_headers)

        # Pagar multa
        pago_resp = client.post(f"/api/v1/prestamos/{pres_id}/pago-multa", headers=b_headers)
        assert pago_resp.status_code == 200
        assert pago_resp.json()["multa_pagada"] is True

        # Ahora sí puede pedir préstamo
        resp = client.post("/api/v1/prestamos/", json={"socio_id": ana_id, "libro_id": libro_id}, headers=b_headers)
        assert resp.status_code == 201


class TestReportesPermisos:
    def test_reportes_socio_403(self, client):
        """Caso 28a: socio no puede ver reportes → 403."""
        registrar_socio(client, "ana@example.com", "Ana Torres")
        headers = token_headers(client, "ana@example.com")
        resp = client.get("/api/v1/reportes/resumen", headers=headers)
        assert resp.status_code == 403

    def test_reportes_bibliotecario_200(self, client, db):
        """Caso 28b: bibliotecario puede ver reportes → 200."""
        crear_biblio_directo(db)
        headers = token_headers(client, "biblio@biblioteca.com", "Biblio123")
        resp = client.get("/api/v1/reportes/resumen", headers=headers)
        assert resp.status_code == 200
