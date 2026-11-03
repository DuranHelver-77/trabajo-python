"""Script one-shot para crear el admin vía args. Uso interno."""
import sys
from app.core.database import SessionLocal
from app.core.security import hashear_password
from app.models.usuario import RolUsuario, Usuario

email, nombre, password = sys.argv[1], sys.argv[2], sys.argv[3]
db = SessionLocal()
existente = db.query(Usuario).filter(Usuario.email == email).first()
if existente:
    print(f"Ya existe: {email}")
else:
    admin = Usuario(email=email, nombre=nombre, password_hash=hashear_password(password), rol=RolUsuario.admin)
    db.add(admin); db.commit(); db.refresh(admin)
    print(f"Admin creado: id={admin.id} email={admin.email}")
db.close()
