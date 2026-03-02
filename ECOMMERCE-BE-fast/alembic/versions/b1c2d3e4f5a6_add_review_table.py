"""add review table

Revision ID: b1c2d3e4f5a6
Revises: a3059659f1a0
Create Date: 2026-03-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'add_detail_id_order_item'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('review',
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    # Đảm bảo mỗi user chỉ đánh giá 1 lần cho mỗi sản phẩm
    op.create_index('ix_review_user_product', 'review', ['user_id', 'product_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_review_user_product', table_name='review')
    op.drop_table('review')
