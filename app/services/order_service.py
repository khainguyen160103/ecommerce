"""
Order Service - Xử lý logic đơn hàng
Admin: Quản lý tất cả đơn hàng
User: Tạo đơn hàng, xem đơn hàng của mình
"""
from app.models.order_model import Order, OrderOut
from app.models.order_item_model import OrderItem
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from app.models.product_model import Product
from app.models.user_model import User
from app.enum.role_enum import OrderStatus
from fastapi import HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Dict, Any, List


class OrderService:
    """Service quản lý đơn hàng"""
    
    # ==================== USER FUNCTIONS ====================
    
    def create_order_from_cart(self, user: User, session: Session) -> Dict[str, Any]:
        """
        [USER] Tạo đơn hàng từ giỏ hàng
        Args:
            user: User hiện tại
            session: Database session
        Returns:
            Dict chứa message và order info
        Raises:
            HTTPException 400: Giỏ hàng trống
        """
        # Lấy giỏ hàng
        cart = session.exec(
            select(Cart).where(Cart.user_id == user.id)
        ).first()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống"
            )
        
        # Lấy các items trong giỏ
        cart_items = session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id)
        ).all()
        
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giỏ hàng trống"
            )
        
        # Tính tổng tiền
        total = 0
        for item in cart_items:
            product = session.exec(
                select(Product).where(Product.id == item.product_id)
            ).first()
            if product and product.price:
                total += float(product.price) * item.quantity
        
        # Tạo order
        order = Order(
            user_id=user.id,
            total=int(total),
            status=OrderStatus.PENDING
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Tạo order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity
            )
            session.add(order_item)
        
        # Xóa giỏ hàng sau khi tạo order
        for item in cart_items:
            session.delete(item)
        cart.total = 0
        session.add(cart)
        session.commit()
        
        return {
            "message": "Đặt hàng thành công",
            "order_id": order.id,
            "total": order.total
        }
    
    def get_my_orders(
        self, 
        user: User, 
        session: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        [USER] Lấy danh sách đơn hàng của user
        Args:
            user: User hiện tại
            session: Database session
            skip: Số record bỏ qua
            limit: Số record tối đa
        Returns:
            List các order
        """
        orders = session.exec(
            select(Order)
            .where(Order.user_id == user.id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for order in orders:
            order_items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            ).all()
            
            result.append({
                "id": order.id,
                "total": order.total,
                "status": getattr(order, 'status', OrderStatus.PENDING),
                "create_at": order.create_at,
                "items_count": len(order_items)
            })
        
        return result
    
    def get_order_detail(
        self, 
        user: User, 
        order_id: UUID, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [USER] Xem chi tiết đơn hàng
        Args:
            user: User hiện tại
            order_id: UUID của order
            session: Database session
        Returns:
            Dict chứa order và items chi tiết
        Raises:
            HTTPException 404: Order không tồn tại hoặc không thuộc về user
        """
        order = session.exec(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user.id
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đơn hàng không tồn tại"
            )
        
        # Lấy order items kèm product info
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()
        
        items_detail = []
        for item in order_items:
            product = session.exec(
                select(Product).where(Product.id == item.product_id)
            ).first()
            items_detail.append({
                "product_id": item.product_id,
                "product_name": product.name if product else None,
                "product_price": product.price if product else None,
                "quantity": item.quantity
            })
        
        return {
            "id": order.id,
            "total": order.total,
            "status": getattr(order, 'status', OrderStatus.PENDING),
            "create_at": order.create_at,
            "items": items_detail
        }
    
    def cancel_order(
        self, 
        user: User, 
        order_id: UUID, 
        session: Session
    ) -> Dict[str, str]:
        """
        [USER] Hủy đơn hàng (chỉ khi status = PENDING)
        Args:
            user: User hiện tại
            order_id: UUID của order
            session: Database session
        Returns:
            Dict chứa message
        Raises:
            HTTPException 400: Không thể hủy đơn hàng
        """
        order = session.exec(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user.id
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đơn hàng không tồn tại"
            )
        
        current_status = getattr(order, 'status', OrderStatus.PENDING)
        if current_status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể hủy đơn hàng đang chờ xác nhận"
            )
        
        order.status = OrderStatus.CANCELLED
        session.add(order)
        session.commit()
        
        return {"message": "Đã hủy đơn hàng"}
    
    # ==================== ADMIN FUNCTIONS ====================
    
    def get_all_orders(
        self, 
        session: Session,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None
    ) -> Dict[str, Any]:
        """
        [ADMIN] Lấy tất cả đơn hàng
        Args:
            session: Database session
            skip: Số record bỏ qua
            limit: Số record tối đa
            status_filter: Lọc theo trạng thái
        Returns:
            Dict chứa orders và pagination
        """
        query = select(Order)
        
        if status_filter:
            query = query.where(Order.status == status_filter)
        
        orders = session.exec(query.offset(skip).limit(limit)).all()
        total = len(session.exec(query).all())
        
        result = []
        for order in orders:
            user = session.exec(
                select(User).where(User.id == order.user_id)
            ).first()
            
            result.append({
                "id": order.id,
                "user_email": user.email if user else None,
                "total": order.total,
                "status": getattr(order, 'status', OrderStatus.PENDING),
                "create_at": order.create_at
            })
        
        return {
            "orders": result,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def update_order_status(
        self, 
        order_id: UUID, 
        new_status: str, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [ADMIN] Cập nhật trạng thái đơn hàng
        Args:
            order_id: UUID của order
            new_status: Trạng thái mới
            session: Database session
        Returns:
            Dict chứa message và order info
        """
        order = session.exec(
            select(Order).where(Order.id == order_id)
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đơn hàng không tồn tại"
            )
        
        # Validate status
        valid_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPING,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED
        ]
        
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trạng thái không hợp lệ. Cho phép: {valid_statuses}"
            )
        
        order.status = new_status
        session.add(order)
        session.commit()
        
        return {
            "message": "Cập nhật trạng thái thành công",
            "order_id": order.id,
            "new_status": new_status
        }