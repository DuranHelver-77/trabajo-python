"""
Configuración de Alembic para migraciones de la Biblioteca.

La URL de la base de datos se toma de get_settings() (nunca de alembic.ini).
target_metadata apunta a Base.metadata con todos los modelos importados.
"""
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ─── Asegurar que el paquete app esté en el path ──────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.core.database import Base

# Importar TODOS los modelos para que autogenerate los detecte
import app.models  # noqa: F401

# ─── Configuración de Alembic ──────────────────────────────────────────────────
config = context.config

# Interpretar el archivo de logging de alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# La URL viene de Settings, nunca de alembic.ini
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


# ─── Migraciones offline ───────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """
    Ejecuta migraciones sin conexión a la base de datos (genera SQL puro).
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ─── Migraciones online ────────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """
    Ejecuta migraciones con conexión activa a la base de datos.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
