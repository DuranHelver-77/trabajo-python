"""
Script para crear el primer administrador del sistema.
Uso: python -m app.scripts.crear_admin

- Pide email, nombre y contraseña por consola (getpass para la clave).
- No hace nada si el email ya existe.
- La contraseña nunca se escribe en el código ni en migraciones.
"""
import getpass
import sys

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hashear_password
from app.models.usuario import RolUsuario, Usuario


def crear_admin():
    email = input("Email del administrador: ").strip().lower()
    nombre = input("Nombre completo: ").strip().title()
    password = getpass.getpass("Contraseña (no se mostrará): ")
    confirmar = getpass.getpass("Confirmar contraseña: ")

    if password != confirmar:
        print("❌ Las contraseñas no coinciden.")
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            print(f"⚠️  Ya existe un usuario con email '{email}'. No se hizo nada.")
            return

        admin = Usuario(
            email=email,
            nombre=nombre,
            password_hash=hashear_password(password),
            rol=RolUsuario.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"✅ Administrador '{nombre}' ({email}) creado con id={admin.id}.")
    finally:
        db.close()


if __name__ == "__main__":
    crear_admin()
