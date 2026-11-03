"""0002_multa_pagada

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-27

Agrega columna multa_pagada a prestamos y migra los datos:
- Los préstamos con multa = 0 quedan marcados como pagados.
Esta migración se escribe a mano (no autogenerate) para incluir la migración de datos.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna con server_default=false (necesario para tablas con datos)
    op.add_column(
        "prestamos",
        sa.Column(
            "multa_pagada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    # Migración de datos: préstamos sin multa ya están "pagados"
    op.execute("UPDATE prestamos SET multa_pagada = true WHERE multa = 0")


def downgrade() -> None:
    op.drop_column("prestamos", "multa_pagada")
