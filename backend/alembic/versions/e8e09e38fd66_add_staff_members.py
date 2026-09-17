"""add staff members

Revision ID: e8e09e38fd66
Revises: 63a854d7a751
Create Date: 2026-09-15 17:54:35.618258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8e09e38fd66'
down_revision: Union[str, Sequence[str], None] = '63a854d7a751'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Ajouter d'abord la colonne en autorisant temporairement NULL
    op.add_column(
        "availabilities",
        sa.Column(
            "staff_member_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Rattacher les anciennes disponibilités à Léa (id = 1)
    op.execute(
        """
        UPDATE availabilities
        SET staff_member_id = 1
        WHERE staff_member_id IS NULL
        """
    )

    # Maintenant toutes les lignes ont un employé :
    # la colonne peut devenir obligatoire
    op.alter_column(
        "availabilities",
        "staff_member_id",
        nullable=False,
    )

    # Créer la clé étrangère avec un nom explicite
    op.create_foreign_key(
        "fk_availabilities_staff_member_id",
        "availabilities",
        "staff_members",
        ["staff_member_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_availabilities_staff_member_id",
        "availabilities",
        type_="foreignkey",
    )

    op.drop_column(
        "availabilities",
        "staff_member_id",
    )