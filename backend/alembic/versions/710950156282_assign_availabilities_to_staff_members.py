"""assign availabilities to staff members

Revision ID: 710950156282
Revises: e8e09e38fd66
Create Date: 2026-09-15 18:12:16.017406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '710950156282'
down_revision: Union[str, Sequence[str], None] = 'e8e09e38fd66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "availabilities",
        sa.Column(
            "staff_member_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE availabilities
        SET staff_member_id = 1
        WHERE staff_member_id IS NULL
        """
    )

    op.alter_column(
        "availabilities",
        "staff_member_id",
        nullable=False,
    )

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
