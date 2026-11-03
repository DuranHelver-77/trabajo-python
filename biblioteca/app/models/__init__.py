"""Importa todos los modelos para que Alembic autogenerate los detecte."""
from app.models.autor import Autor  # noqa: F401
from app.models.categoria import Categoria  # noqa: F401
from app.models.libro_categoria import libro_categoria  # noqa: F401
from app.models.libro import Libro  # noqa: F401
from app.models.socio import Socio  # noqa: F401
from app.models.prestamo import Prestamo  # noqa: F401
from app.models.usuario import Usuario, RolUsuario  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
