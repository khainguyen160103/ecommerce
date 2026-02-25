"""
Cart Repository - Xử lý tất cả query liên quan đến giỏ hàng
"""
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime

from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from app.models.product_model import Product


class CartRepository:
    """Repository quản lý giỏ hàng"""
    
    # ==================== CART FUNCTIONS ====================
    
    def get_cart_by_user_id(self, user_id: UUID, session: Session) -> Cart | None:
        """Lấy giỏ hàng của user"""
        return session.exec(
            select(Cart).where(Cart.user_id == user_id)
        ).first()
    
    def get_cart_by_id(self, cart_id: UUID, session: Session) -> Cart | None:
        """Lấy giỏ hàng theo ID"""
        return session.exec(
            select(Cart).where(Cart.id == cart_id)
        ).first()
    
    def create_cart(self, cart: Cart, session: Session) -> Cart:
        """Tạo giỏ hàng mới"""
        session.add(cart)
        session.commit()
        session.refresh(cart)
        return cart
    
    def update_cart(self, cart: Cart, session: Session) -> Cart:
        """Cập nhật giỏ hàng"""
        session.add(cart)
        session.commit()
        session.refresh(cart)
        return cart
    
    def update_cart_total(self, cart: Cart, total: int, session: Session) -> Cart:
        """Cập nhật tổng số lượng giỏ hàng"""
        cart.total = total
        cart.update_at = datetime.now()
        return self.update_cart(cart, session)
    
    # ==================== CART ITEM FUNCTIONS ====================
    
    def get_cart_items(self, cart_id: UUID, session: Session) -> List[CartItem]:
        """Lấy tất cả items trong giỏ"""
        return session.exec(
            select(CartItem).where(CartItem.cart_id == cart_id)
        ).all()
    
    def get_cart_item_by_id(self, cart_item_id: UUID, session: Session) -> CartItem | None:
        """Lấy cart item theo ID"""
        return session.exec(
            select(CartItem).where(CartItem.id == cart_item_id)
        ).first()
    
    def get_cart_item_by_product(
        self, 
        cart_id: UUID, 
        product_id: UUID, 
        session: Session
    ) -> CartItem | None:
        """Lấy cart item theo cart id và product id"""
        return session.exec(
            select(CartItem).where(
                (CartItem.cart_id == cart_id) & 
                (CartItem.product_id == product_id)
            )
        ).first()
    
    def get_cart_item_by_detail(self, cart_id: UUID, detail_id: UUID, session: Session):
        return session.exec(
            select(CartItem).where(
                (CartItem.cart_id == cart_id) & (CartItem.detail_id == detail_id)
            )
        ).first()
    def create_cart_item(self, cart_item: CartItem, session: Session) -> CartItem:
        """Tạo cart item mới"""
        session.add(cart_item)
        session.commit()
        session.refresh(cart_item)
        return cart_item
    
    def update_cart_item(self, cart_item: CartItem, session: Session) -> CartItem:
        """Cập nhật cart item"""
        cart_item.update_at = datetime.now()
        session.add(cart_item)
        session.commit()
        session.refresh(cart_item)
        return cart_item
    
    def delete_cart_item(self, cart_item: CartItem, session: Session) -> None:
        """Xóa cart item"""
        session.delete(cart_item)
        session.commit()
    
    def delete_all_cart_items(self, cart_id: UUID, session: Session) -> None:
        """Xóa tất cả cart items"""
        cart_items = self.get_cart_items(cart_id, session)
        for item in cart_items:
            session.delete(item)
        session.commit()
    
    # ==================== PRODUCT FUNCTIONS ====================
    
    def get_product_by_id(self, product_id: UUID, session: Session) -> Product | None:
        """Lấy sản phẩm theo ID"""
        return session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
