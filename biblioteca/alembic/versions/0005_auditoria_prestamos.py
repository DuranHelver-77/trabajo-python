"""0005_auditoria_prestamos

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-27

Agrega columna registrado_por_id a prestamos para auditoría (Z7).
Guarda qué usuario del staff registró el préstamo.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "prestamos",
        sa.Column("registrado_por_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_prestamos_registrado_por_id_usuarios",
        "prestamos",
        "usuarios",
        ["registrado_por_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_prestamos_registrado_por_id_usuarios",
        "prestamos",
        type_="foreignkey",
    )
    op.drop_column("prestamos", "registrado_por_id")
