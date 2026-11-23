"""0006_portada_libros

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-23

Agrega columnas portada_url y portada_public_id a la tabla libros para soporte de Cloudinary.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "libros",
        sa.Column("portada_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "libros",
        sa.Column("portada_public_id", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("libros", "portada_public_id")
    op.drop_column("libros", "portada_url")

