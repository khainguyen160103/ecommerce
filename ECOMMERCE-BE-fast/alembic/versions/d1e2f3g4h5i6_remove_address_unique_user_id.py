"""remove unique constraint on address.user_id to allow multiple addresses per user

Revision ID: d1e2f3g4h5i6
Revises: c5d6e7f8g9h0
Create Date: 2026-03-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, Sequence[str], None] = 'c5d6e7f8g9h0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint on address.user_id."""
    # Drop the unique constraint on user_id to allow multiple addresses per user
    op.drop_constraint('uq_address_user_id', 'address', type_='unique')


def downgrade() -> None:
    """Re-add unique constraint on address.user_id."""
    op.create_unique_constraint(
        'uq_address_user_id', 'address', ['user_id']
    )
