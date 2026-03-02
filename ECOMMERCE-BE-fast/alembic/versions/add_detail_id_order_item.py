"""
Add detail_id to order_item table

Revision ID: add_detail_id_order_item
Revises: a3059659f1a0
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_detail_id_order_item'
down_revision = 'a3059659f1a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add detail_id column to order_item table
    op.add_column('order_item', 
        sa.Column('detail_id', sa.String(length=36), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_order_item_detail_id',
        'order_item', 'product_detail',
        ['detail_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Create index for performance
    op.create_index(
        'ix_order_item_detail_id',
        'order_item',
        ['detail_id']
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_order_item_detail_id', 'order_item')
    
    # Remove foreign key
    op.drop_constraint('fk_order_item_detail_id', 'order_item', type_='foreignkey')
    
    # Remove column
    op.drop_column('order_item', 'detail_id')
