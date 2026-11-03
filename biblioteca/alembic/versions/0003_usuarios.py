"""0003_usuarios

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-27

Tabla usuarios con enum rolusuario y relación 1 a 1 con socios.
IMPORTANTE: El downgrade debe borrar el tipo enum de PostgreSQL.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

rolusuario_enum = sa.Enum("admin", "bibliotecario", "socio", name="rolusuario")


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "rol",
            sa.Enum("admin", "bibliotecario", "socio", name="rolusuario"),
            nullable=False,
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("intentos_fallidos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("socio_id", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["socio_id"],
            ["socios.id"],
            name="fk_usuarios_socio_id_socios",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("email", name=op.f("uq_usuarios_email")),
        sa.UniqueConstraint("socio_id", name=op.f("uq_usuarios_socio_id")),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    # Eliminar el tipo enum de PostgreSQL (necesario para poder volver a aplicar la migración)
    rolusuario_enum.drop(op.get_bind(), checkfirst=True)
