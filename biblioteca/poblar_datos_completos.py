"""
poblar_datos_completos.py
Inserta un catálogo completo y realista en la base de datos (PostgreSQL de Render):
- Usuarios: admin, bibliotecario, promueve al usuario actual.
- Autores con nacionalidad y año de nacimiento.
- Categorías con descripciones.
- Libros con portadas reales de OpenLibrary, ISBNs, ejemplares y categorías.
- Socios con perfiles activos.
- Préstamos: activos, devueltos, vencidos y con multas.
"""
from datetime import date, timedelta
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.security import hashear_password
from app.models.usuario import Usuario, RolUsuario
from app.models.socio import Socio
from app.models.autor import Autor
from app.models.categoria import Categoria
from app.models.libro import Libro
from app.models.prestamo import Prestamo

db = SessionLocal()

print("🚀 Iniciando carga de datos completa...")

# ── 1. Usuarios y Roles ─────────────────────────────────────────
print("\n[1] Configurando usuarios y roles...")

# Promover duranivan11@gmail.com a Admin
mi_usuario = db.query(Usuario).filter(Usuario.email == "duranivan11@gmail.com").first()
if mi_usuario:
    mi_usuario.rol = RolUsuario.admin
    print(f"  ⭐ Usuario '{mi_usuario.email}' promovido a ADMIN para control total del frontend.")

# Admin general
admin = db.query(Usuario).filter(Usuario.email == "admin@biblioteca.com").first()
if not admin:
    admin = Usuario(
        email="admin@biblioteca.com",
        nombre="Administrador General",
        password_hash=hashear_password("Admin1234*"),
        rol=RolUsuario.admin,
        activo=True,
    )
    db.add(admin)
    print("  ✅ Creado: admin@biblioteca.com (clave: Admin1234*)")

# Bibliotecario
biblio = db.query(Usuario).filter(Usuario.email == "biblio@biblioteca.com").first()
if not biblio:
    biblio = Usuario(
        email="biblio@biblioteca.com",
        nombre="Carlos Bibliotecario",
        password_hash=hashear_password("Biblio1234*"),
        rol=RolUsuario.bibliotecario,
        activo=True,
    )
    db.add(biblio)
    print("  ✅ Creado: biblio@biblioteca.com (clave: Biblio1234*)")

db.commit()

# ── 2. Autores ──────────────────────────────────────────────────
print("\n[2] Insertando autores...")
autores_datos = [
    {"nombre": "Gabriel Garcia Marquez", "nacionalidad": "Colombiana", "anio_nacimiento": 1927},
    {"nombre": "Isabel Allende", "nacionalidad": "Chilena", "anio_nacimiento": 1942},
    {"nombre": "George Orwell", "nacionalidad": "Britanica", "anio_nacimiento": 1903},
    {"nombre": "Antoine De Saint-Exupery", "nacionalidad": "Francesa", "anio_nacimiento": 1900},
    {"nombre": "J.K. Rowling", "nacionalidad": "Britanica", "anio_nacimiento": 1965},
    {"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina", "anio_nacimiento": 1899},
    {"nombre": "Julio Cortazar", "nacionalidad": "Argentina", "anio_nacimiento": 1914},
    {"nombre": "Miguel De Cervantes", "nacionalidad": "Espanola", "anio_nacimiento": 1547},
    {"nombre": "Jane Austen", "nacionalidad": "Britanica", "anio_nacimiento": 1775},
    {"nombre": "Franz Kafka", "nacionalidad": "Checa", "anio_nacimiento": 1883},
]

autores_map = {}
for ad in autores_datos:
    a = db.query(Autor).filter(Autor.nombre == ad["nombre"]).first()
    if not a:
        a = Autor(**ad)
        db.add(a)
        db.flush()
    autores_map[ad["nombre"]] = a
print(f"  ✅ {len(autores_map)} autores listos.")

# ── 3. Categorías ───────────────────────────────────────────────
print("\n[3] Insertando categorías...")
cat_datos = [
    {"nombre": "Novela", "descripcion": "Obras narrativas extensas de ficcion y prosa"},
    {"nombre": "Realismo Magico", "descripcion": "Fusion de elementos magicos y cotidianos"},
    {"nombre": "Ciencia Ficcion", "descripcion": "Futuros distopicos, tecnologia y mundos especulativos"},
    {"nombre": "Fantasia", "descripcion": "Universos con magia, criaturas y aventuras legendarias"},
    {"nombre": "Clasicos Universales", "descripcion": "Obras inmortales de la literatura universal"},
    {"nombre": "Filosofia y Ensayo", "descripcion": "Reflexiones profundas sobre la existencia y la sociedad"},
]

cat_map = {}
for cd in cat_datos:
    c = db.query(Categoria).filter(Categoria.nombre == cd["nombre"]).first()
    if not c:
        c = Categoria(**cd)
        db.add(c)
        db.flush()
    cat_map[cd["nombre"]] = c
print(f"  ✅ {len(cat_map)} categorías listas.")

# ── 4. Libros con Portadas ─────────────────────────────────────
print("\n[4] Insertando libros con portadas...")
libros_datos = [
    {
        "titulo": "Cien Anos De Soledad",
        "isbn": "9780307474728",
        "anio_publicacion": 1967,
        "ejemplares": 5,
        "autor": "Gabriel Garcia Marquez",
        "cats": ["Novela", "Realismo Magico"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780307474728-L.jpg",
    },
    {
        "titulo": "El Amor En Los Tiempos Del Colera",
        "isbn": "9780307389732",
        "anio_publicacion": 1985,
        "ejemplares": 4,
        "autor": "Gabriel Garcia Marquez",
        "cats": ["Novela", "Realismo Magico"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780307389732-L.jpg",
    },
    {
        "titulo": "1984",
        "isbn": "9780451524935",
        "anio_publicacion": 1949,
        "ejemplares": 6,
        "autor": "George Orwell",
        "cats": ["Novela", "Ciencia Ficcion"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
    },
    {
        "titulo": "Rebelion En La Granja",
        "isbn": "9780451526342",
        "anio_publicacion": 1945,
        "ejemplares": 4,
        "autor": "George Orwell",
        "cats": ["Novela", "Filosofia y Ensayo"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780451526342-L.jpg",
    },
    {
        "titulo": "La Casa De Los Espiritus",
        "isbn": "9781416523932",
        "anio_publicacion": 1982,
        "ejemplares": 4,
        "autor": "Isabel Allende",
        "cats": ["Novela", "Realismo Magico"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9781416523932-L.jpg",
    },
    {
        "titulo": "El Principito",
        "isbn": "9780156012195",
        "anio_publicacion": 1943,
        "ejemplares": 8,
        "autor": "Antoine De Saint-Exupery",
        "cats": ["Clasicos Universales", "Filosofia y Ensayo"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg",
    },
    {
        "titulo": "Harry Potter Y La Piedra Filosofal",
        "isbn": "9788478884452",
        "anio_publicacion": 1997,
        "ejemplares": 5,
        "autor": "J.K. Rowling",
        "cats": ["Fantasia", "Novela"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9788478884452-L.jpg",
    },
    {
        "titulo": "Ficciones",
        "isbn": "9780307950925",
        "anio_publicacion": 1944,
        "ejemplares": 3,
        "autor": "Jorge Luis Borges",
        "cats": ["Clasicos Universales", "Filosofia y Ensayo"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780307950925-L.jpg",
    },
    {
        "titulo": "Rayuela",
        "isbn": "9780307476579",
        "anio_publicacion": 1963,
        "ejemplares": 4,
        "autor": "Julio Cortazar",
        "cats": ["Novela", "Clasicos Universales"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9780307476579-L.jpg",
    },
    {
        "titulo": "Don Quijote De La Mancha",
        "isbn": "9788424116484",
        "anio_publicacion": 1605,
        "ejemplares": 5,
        "autor": "Miguel De Cervantes",
        "cats": ["Clasicos Universales", "Novela"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9788424116484-L.jpg",
    },
    {
        "titulo": "Orgullo Y Prejuicio",
        "isbn": "9788497940863",
        "anio_publicacion": 1813,
        "ejemplares": 4,
        "autor": "Jane Austen",
        "cats": ["Novela", "Clasicos Universales"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9788497940863-L.jpg",
    },
    {
        "titulo": "La Metamorfosis",
        "isbn": "9788420651361",
        "anio_publicacion": 1915,
        "ejemplares": 6,
        "autor": "Franz Kafka",
        "cats": ["Clasicos Universales", "Novela"],
        "portada_url": "https://covers.openlibrary.org/b/isbn/9788420651361-L.jpg",
    },
]

libros_creados = []
for ld in libros_datos:
    l = db.query(Libro).filter(Libro.isbn == ld["isbn"]).first()
    if not l:
        l = Libro(
            titulo=ld["titulo"],
            isbn=ld["isbn"],
            anio_publicacion=ld["anio_publicacion"],
            ejemplares=ld["ejemplares"],
            autor_id=autores_map[ld["autor"]].id,
            portada_url=ld["portada_url"],
        )
        l.categorias = [cat_map[c] for c in ld["cats"]]
        db.add(l)
        db.flush()
    libros_creados.append(l)
print(f"  ✅ {len(libros_creados)} libros listos.")

# ── 5. Socios ───────────────────────────────────────────────────
print("\n[5] Insertando socios...")
socios_nuevos = [
    {"nombre": "Maria Camila Lopez", "email": "camila.lopez@example.com", "telefono": "+57 310 1234567"},
    {"nombre": "Andres Felipe Gomez", "email": "andres.gomez@example.com", "telefono": "+57 315 9876543"},
    {"nombre": "Sofia Martinez Diaz", "email": "sofia.martinez@example.com", "telefono": "+57 320 4567890"},
    {"nombre": "Santiago Ramirez", "email": "santiago.ramirez@example.com", "telefono": "+57 301 7890123"},
]

socios_creados = list(db.query(Socio).all())
for sd in socios_nuevos:
    s = db.query(Socio).filter(Socio.email == sd["email"]).first()
    if not s:
        s = Socio(**sd, activo=True)
        db.add(s)
        db.flush()
        socios_creados.append(s)
print(f"  ✅ {len(socios_creados)} socios listos.")

# ── 6. Préstamos ────────────────────────────────────────────────
print("\n[6] Insertando préstamos de ejemplo...")
hoy = date.today()
admin_user = db.query(Usuario).filter(Usuario.rol == RolUsuario.admin).first()

if socios_creados and libros_creados:
    socio1 = socios_creados[0]
    socio2 = socios_creados[1] if len(socios_creados) > 1 else socio1
    socio3 = socios_creados[2] if len(socios_creados) > 2 else socio1

    prestamos_ejemplos = [
        # Activo normal
        {
            "libro_id": libros_creados[0].id,
            "socio_id": socio1.id,
            "fecha_prestamo": hoy - timedelta(days=5),
            "fecha_limite": hoy + timedelta(days=9),
            "fecha_devolucion": None,
            "multa": Decimal("0.00"),
            "multa_pagada": False,
        },
        # Activo por vencer
        {
            "libro_id": libros_creados[2].id,
            "socio_id": socio2.id,
            "fecha_prestamo": hoy - timedelta(days=12),
            "fecha_limite": hoy + timedelta(days=2),
            "fecha_devolucion": None,
            "multa": Decimal("0.00"),
            "multa_pagada": False,
        },
        # Devuelto a tiempo
        {
            "libro_id": libros_creados[5].id,
            "socio_id": socio1.id,
            "fecha_prestamo": hoy - timedelta(days=20),
            "fecha_limite": hoy - timedelta(days=6),
            "fecha_devolucion": hoy - timedelta(days=7),
            "multa": Decimal("0.00"),
            "multa_pagada": False,
        },
        # Vencido con multa pendiente
        {
            "libro_id": libros_creados[1].id,
            "socio_id": socio1.id,
            "fecha_prestamo": hoy - timedelta(days=25),
            "fecha_limite": hoy - timedelta(days=11),
            "fecha_devolucion": None,
            "multa": Decimal("11.00"),
            "multa_pagada": False,
        },
        # Vencido con multa pagada
        {
            "libro_id": libros_creados[6].id,
            "socio_id": socio2.id,
            "fecha_prestamo": hoy - timedelta(days=30),
            "fecha_limite": hoy - timedelta(days=16),
            "fecha_devolucion": hoy - timedelta(days=2),
            "multa": Decimal("14.00"),
            "multa_pagada": True,
        },
        # Activo para otro socio
        {
            "libro_id": libros_creados[4].id,
            "socio_id": socio3.id,
            "fecha_prestamo": hoy - timedelta(days=3),
            "fecha_limite": hoy + timedelta(days=11),
            "fecha_devolucion": None,
            "multa": Decimal("0.00"),
            "multa_pagada": False,
        },
    ]

    for pe in prestamos_ejemplos:
        # Evitar duplicar préstamo idéntico
        p_existente = db.query(Prestamo).filter(
            Prestamo.libro_id == pe["libro_id"],
            Prestamo.socio_id == pe["socio_id"],
            Prestamo.fecha_prestamo == pe["fecha_prestamo"]
        ).first()
        if not p_existente:
            p = Prestamo(**pe, registrado_por_id=admin_user.id if admin_user else None)
            db.add(p)

db.commit()
db.close()

print("\n🎉 ¡Carga de datos completa finalizada con éxito!")
