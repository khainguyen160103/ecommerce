"""add discount table

Revision ID: c5d6e7f8g9h0
Revises: b1c2d3e4f5a6
Create Date: 2026-03-03 00:00:00.000000

"""
# pylint: disable=no-member
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8g9h0'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'discount',
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('discount_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='percent'),
        sa.Column('discount_value', sa.Float(), nullable=False, server_default='0'),
        sa.Column('min_order_value', sa.Float(), nullable=False, server_default='0'),
        sa.Column('max_discount', sa.Float(), nullable=True),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_discount_code'), 'discount', ['code'], unique=True)

    # Thêm cột discount vào bảng order
    op.add_column('order', sa.Column('discount_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('order', sa.Column('discount_amount', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('order', 'discount_amount')
    op.drop_column('order', 'discount_code')
    op.drop_index(op.f('ix_discount_code'), table_name='discount')
    op.drop_table('discount')
