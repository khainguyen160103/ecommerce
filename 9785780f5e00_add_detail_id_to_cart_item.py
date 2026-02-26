"""add detail_id to cart_item

Revision ID: 9785780f5e00
Revises: 0384419a65ea
Create Date: 2026-02-24 17:30:26.894235

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9785780f5e00'
down_revision: Union[str, Sequence[str], None] = '0384419a65ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add detail_id with data preservation"""
    
    # 1️⃣ Thêm column NULL (không xóa dữ liệu)
    op.add_column('cart_item', 
        sa.Column('detail_id', sa.Uuid(), nullable=True)
    )
    
    # 2️⃣ Update dữ liệu cũ - gán detail_id từ product_detail
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE cart_item ci
        SET detail_id = (
            SELECT id FROM product_detail 
            WHERE product_id = ci.product_id 
            LIMIT 1
        )
        WHERE ci.detail_id IS NULL AND ci.product_id IS NOT NULL
    """))
    
    # 3️⃣ Kiểm tra xem còn NULL không, nếu còn thì xóa
    connection.execute(sa.text("""
        DELETE FROM cart_item WHERE detail_id IS NULL
    """))
    
    # 4️⃣ Set NOT NULL
    op.alter_column('cart_item', 'detail_id',
        existing_type=sa.Uuid(),
        nullable=False
    )
    
    # 5️⃣ Thêm Foreign Key constraint
    op.create_foreign_key(
        'fk_cart_item_detail_id',
        'cart_item', 
        'product_detail', 
        ['detail_id'], 
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema"""
    op.drop_constraint('fk_cart_item_detail_id', 'cart_item', type_='foreignkey')
    op.drop_column('cart_item', 'detail_id')
