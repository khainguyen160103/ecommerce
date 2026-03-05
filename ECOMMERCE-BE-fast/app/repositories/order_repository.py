"""
Order Repository - Xử lý tất cả query liên quan đến đơn hàng
"""
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from app.models.product_model import Product
from app.models.product_detail_model import ProductDetail
from app.models.user_model import User
from app.enum.role_enum import OrderStatus


class OrderRepository:
    """Repository quản lý đơn hàng"""
    
    # ==================== CART FUNCTIONS ====================
    
    def get_cart_by_user_id(self, user_id: UUID, session: Session) -> Cart | None:
        """Lấy giỏ hàng của user"""
        return session.exec(
            select(Cart).where(Cart.user_id == user_id)
        ).first()
    
    def get_cart_items(self, cart_id: UUID, session: Session) -> List[CartItem]:
        """Lấy tất cả items trong giỏ"""
        return session.exec(
            select(CartItem).where(CartItem.cart_id == cart_id)
        ).all()
    
    def delete_cart_item(self, item: CartItem, session: Session) -> None:
        """Xóa item khỏi giỏ"""
        session.delete(item)
    
    def update_cart_total(self, cart: Cart, session: Session) -> None:
        """Cập nhật tổng tiền giỏ"""
        session.add(cart)
        session.commit()
    
    # ==================== ORDER FUNCTIONS ====================
    
    def create_order(self, order: Order, session: Session) -> Order:
        """Tạo đơn hàng mới"""
        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    
    def create_order_item(self, order_item: OrderItem, session: Session) -> OrderItem:
        """Tạo order item"""
        session.add(order_item)
        return order_item
    
    def bulk_commit(self, session: Session) -> None:
        """Commit tất cả changes"""
        session.commit()
    
    def get_order_by_id(self, order_id: UUID, session: Session) -> Order | None:
        """Lấy đơn hàng theo ID"""
        return session.exec(
            select(Order).where(Order.id == order_id)
        ).first()
    
    def get_orders_by_user_id(
        self, 
        user_id: UUID, 
        session: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[Order]:
        """Lấy danh sách đơn hàng của user"""
        return session.exec(
            select(Order)
            .where(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
        ).all()
    
    def get_order_items(self, order_id: UUID, session: Session) -> List[OrderItem]:
        """Lấy tất cả items của đơn hàng"""
        return session.exec(
            select(OrderItem).where(OrderItem.order_id == order_id)
        ).all()
    
    def get_all_orders(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None
    ) -> tuple[List[Order], int]:
        """Lấy tất cả đơn hàng (admin)"""
        query = select(Order)
        
        if status_filter:
            query = query.where(Order.status == status_filter)
        
        orders = session.exec(query.offset(skip).limit(limit)).all()
        total = len(session.exec(query).all())
        
        return orders, total
    
    def update_order_status(
        self, 
        order: Order, 
        new_status: str, 
        session: Session
    ) -> Order:
        """Cập nhật trạng thái đơn hàng"""
        order.status = new_status
        session.commit()
        return order
    
    def cancel_order(self, order: Order, session: Session) -> Order:
        """Hủy đơn hàng"""
        order.status = OrderStatus.CANCELLED
        session.commit()
        return order
    
    # ==================== PRODUCT FUNCTIONS ====================
    
    def get_product_by_id(self, product_id: UUID, session: Session) -> Product | None:
        """Lấy sản phẩm theo ID"""
        return session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
    
    # ==================== USER FUNCTIONS ====================
    
    def get_user_by_id(self, user_id: UUID, session: Session) -> User | None:
        """Lấy user theo ID"""
        return session.exec(
            select(User).where(User.id == user_id)
        ).first()

    # ==================== INVENTORY FUNCTIONS ====================

    def get_product_detail_by_id(
        self, detail_id: UUID, session: Session
    ) -> ProductDetail | None:
        """Lấy chi tiết sản phẩm theo ID"""
        return session.exec(
            select(ProductDetail).where(ProductDetail.id == detail_id)
        ).first()

    def reduce_product_stock(
        self, detail_id: UUID, quantity: int, session: Session
    ) -> bool:
        """
        Giảm stock của product detail
        Returns: True nếu thành công, False nếu không đủ stock
        """
        detail = self.get_product_detail_by_id(detail_id, session)
        if not detail:
            return False

        if detail.stock < quantity:
            return False

        detail.stock -= quantity
        session.add(detail)
        return True

    def restore_product_stock(
        self, detail_id: UUID, quantity: int, session: Session
    ) -> None:
        """Hoàn trả stock khi hủy đơn"""
        detail = self.get_product_detail_by_id(detail_id, session)
        if detail:
            detail.stock += quantity
            session.add(detail)

    def delete_order_items(self, order_id: UUID, session: Session) -> None:
        """Xóa tất cả items của đơn hàng"""
        items = self.get_order_items(order_id, session)
        for item in items:
            session.delete(item)

    def delete_order(self, order: Order, session: Session) -> None:
        """Xóa đơn hàng"""
        session.delete(order)
