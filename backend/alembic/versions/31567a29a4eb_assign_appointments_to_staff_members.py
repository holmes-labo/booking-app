"""assign appointments to staff members

Revision ID: 31567a29a4eb
Revises: c6640ad5b976
Create Date: 2026-09-17 19:27:38.828089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31567a29a4eb'
down_revision: Union[str, Sequence[str], None] = 'c6640ad5b976'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "appointments",
        sa.Column(
            "staff_member_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE appointments
        SET staff_member_id = 1
        WHERE staff_member_id IS NULL
        """
    )

    op.alter_column(
        "appointments",
        "staff_member_id",
        nullable=False,
    )

    op.create_foreign_key(
        "fk_appointments_staff_member_id",
        "appointments",
        "staff_members",
        ["staff_member_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_appointments_staff_member_id",
        "appointments",
        type_="foreignkey",
    )

    op.drop_column(
        "appointments",
        "staff_member_id",
    )
