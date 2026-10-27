"""
seeder.py – Carga los datos de prueba de la Fase 7.
Ejecutar con la API en marcha O directamente contra la BD:

    python seeder.py
"""

import requests
from datetime import date, timedelta

BASE = "http://127.0.0.1:8000"


def post(ruta, datos):
    r = requests.post(f"{BASE}{ruta}", json=datos)
    print(f"  POST {ruta} → {r.status_code}")
    if r.status_code not in (200, 201):
        print("   ", r.json())
        return None
    return r.json()


def patch(ruta, datos):
    r = requests.patch(f"{BASE}{ruta}", json=datos)
    print(f"  PATCH {ruta} → {r.status_code}")
    if r.status_code not in (200, 201):
        print("   ", r.json())
    return r.json() if r.ok else None


def get(ruta, params=None):
    r = requests.get(f"{BASE}{ruta}", params=params)
    print(f"  GET {ruta} → {r.status_code}")
    return r.json() if r.ok else None


# ── Autores ──────────────────────────────────────────────────
print("\n=== Autores ===")
a1 = post("/autores", {"nombre": "Gabriel Garcia Marquez", "nacionalidad": "Colombiana", "anio_nacimiento": 1927})
a2 = post("/autores", {"nombre": "Isabel Allende", "nacionalidad": "Chilena", "anio_nacimiento": 1942})
a3 = post("/autores", {"nombre": "George Orwell", "nacionalidad": "Britanica", "anio_nacimiento": 1903})

# ── Categorias ───────────────────────────────────────────────
print("\n=== Categorias ===")
c1 = post("/categorias", {"nombre": "Novela"})
c2 = post("/categorias", {"nombre": "Realismo Magico"})
c3 = post("/categorias", {"nombre": "Distopia"})
c4 = post("/categorias", {"nombre": "Poesia"})

# ── Libros ───────────────────────────────────────────────────
print("\n=== Libros ===")
l1 = post("/libros", {
    "titulo": "Cien Anos de Soledad",
    "isbn": "9780307474728",
    "anio_publicacion": 1967,
    "ejemplares": 2,
    "autor_id": a1["id"],
    "categoria_ids": [c1["id"], c2["id"]],
})
l2 = post("/libros", {
    "titulo": "El Amor en los Tiempos del Colera",
    "isbn": "9780307389732",
    "anio_publicacion": 1985,
    "ejemplares": 1,
    "autor_id": a1["id"],
    "categoria_ids": [c1["id"]],
})
l3 = post("/libros", {
    "titulo": "La Casa de los Espiritus",
    "isbn": "9781416523932",
    "anio_publicacion": 1982,
    "ejemplares": 2,
    "autor_id": a2["id"],
    "categoria_ids": [c1["id"], c2["id"]],
})
l4 = post("/libros", {
    "titulo": "1984",
    "isbn": "9780451524935",
    "anio_publicacion": 1949,
    "ejemplares": 3,
    "autor_id": a3["id"],
    "categoria_ids": [c1["id"], c3["id"]],
})

# ── Socios ───────────────────────────────────────────────────
print("\n=== Socios ===")
s1 = post("/socios", {"nombre": "Ana Torres", "email": "ANA@example.com"})
s2 = post("/socios", {"nombre": "Luis Perez", "email": "luis@example.com"})
s3 = post("/socios", {"nombre": "Marta Ruiz", "email": "marta@example.com"})

print("\n=== Datos de prueba cargados. ===")
print("Ahora ejecuta los 24 casos desde /docs o Postman.")
