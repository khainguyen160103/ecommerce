"""
Order Service - Xử lý logic đơn hàng
Admin: Quản lý tất cả đơn hàng
User: Tạo đơn hàng, xem đơn hàng của mình
"""
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.user_model import User
from app.enum.role_enum import OrderStatus
from app.repositories.order_repository import OrderRepository
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, List, Annotated


class OrderService:
    """Service quản lý đơn hàng"""

    def __init__(self, repository: Annotated[OrderRepository, Depends()]):
        self.repository = repository

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
        cart = self.repository.get_cart_by_user_id(user.id, session)

        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Giỏ hàng trống"
            )

        # Lấy các items trong giỏ
        cart_items = self.repository.get_cart_items(cart.id, session)

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Giỏ hàng trống"
            )

        # Tính tổng tiền
        total = 0
        for item in cart_items:
            product = self.repository.get_product_by_id(item.product_id, session)
            if product and product.price:
                total += float(product.price) * item.quantity

        # Tạo order
        order = Order(user_id=user.id, total=int(total), status=OrderStatus.PENDING)
        order = self.repository.create_order(order, session)

        # Tạo order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )
            self.repository.create_order_item(order_item, session)

        # Xóa giỏ hàng sau khi tạo order
        for item in cart_items:
            self.repository.delete_cart_item(item, session)
        cart.total = 0
        self.repository.update_cart_total(cart, session)
        self.repository.bulk_commit(session)

        return {
            "message": "Đặt hàng thành công",
            "order_id": order.id,
            "total": order.total,
        }

    def get_my_orders(
        self, user: User, session: Session, skip: int = 0, limit: int = 20
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
        orders = self.repository.get_orders_by_user_id(user.id, session, skip, limit)

        result = []
        for order in orders:
            order_items = self.repository.get_order_items(order.id, session)

            result.append(
                {
                    "id": order.id,
                    "total": order.total,
                    "status": getattr(order, "status", OrderStatus.PENDING),
                    "create_at": order.create_at,
                    "items_count": len(order_items),
                }
            )

        return result

    def get_order_detail(
        self, user: User, order_id: UUID, session: Session
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
        order = self.repository.get_order_by_id(order_id, session)

        if not order or order.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Đơn hàng không tồn tại"
            )

        # Lấy order items kèm product info
        order_items = self.repository.get_order_items(order.id, session)

        items_detail = []
        for item in order_items:
            product = self.repository.get_product_by_id(item.product_id, session)
            items_detail.append(
                {
                    "product_id": item.product_id,
                    "product_name": product.name if product else None,
                    "product_price": product.price if product else None,
                    "quantity": item.quantity,
                }
            )

        return {
            "id": order.id,
            "total": order.total,
            "status": getattr(order, "status", OrderStatus.PENDING),
            "create_at": order.create_at,
            "items": items_detail,
        }

    def cancel_order(
        self, user: User, order_id: UUID, session: Session
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
        order = self.repository.get_order_by_id(order_id, session)

        if not order or order.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Đơn hàng không tồn tại"
            )

        current_status = getattr(order, "status", OrderStatus.PENDING)
        if current_status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể hủy đơn hàng đang chờ xác nhận",
            )

        self.repository.cancel_order(order, session)

        return {"message": "Đã hủy đơn hàng"}

    # ==================== ADMIN FUNCTIONS ====================

    def get_order_by_id(self, order_id: UUID, session: Session) -> Dict[str, Any]:
        """
        [ADMIN] Xem chi tiết đơn hàng bất kỳ
        Args:
            order_id: UUID của order
            session: Database session
        Returns:
            Dict chứa order, user info và items chi tiết
        Raises:
            HTTPException 404: Order không tồn tại
        """
        order = self.repository.get_order_by_id(order_id, session)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Đơn hàng không tồn tại"
            )

        # Lấy user info
        user = self.repository.get_user_by_id(order.user_id, session)

        # Lấy order items kèm product info
        order_items = self.repository.get_order_items(order.id, session)

        items_detail = []
        for item in order_items:
            product = self.repository.get_product_by_id(item.product_id, session)
            items_detail.append(
                {
                    "product_id": item.product_id,
                    "product_name": product.name if product else None,
                    "product_price": product.price if product else None,
                    "quantity": item.quantity,
                }
            )

        return {
            "id": order.id,
            "total": order.total,
            "status": getattr(order, "status", OrderStatus.PENDING),
            "create_at": order.create_at,
            "update_at": order.update_at,
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else None,
                "email": user.email if user else None,
                "role": user.role.description if user and user.role else None,
            }
            if user
            else None,
            "items": items_detail,
        }

    def get_all_orders(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
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
        orders, total = self.repository.get_all_orders(
            session, skip, limit, status_filter
        )

        result = []
        for order in orders:
            user = self.repository.get_user_by_id(order.user_id, session)

            result.append(
                {
                    "id": order.id,
                    "user_email": user.email if user else None,
                    "total": order.total,
                    "status": getattr(order, "status", OrderStatus.PENDING),
                    "create_at": order.create_at,
                    "shipping_code": getattr(order, "shipping_code", None),
                    "carrier": getattr(order, "carrier", None),
                    "tracking_number": getattr(order, "tracking_number", None),
                    "shipping_fee": getattr(order, "shipping_fee", 0),
                    "rate_id": getattr(order, "rate_id", None),
                }
            )

        return {"orders": result, "total": total, "skip": skip, "limit": limit}

    def update_order_status(
        self, order_id: UUID, new_status: str, session: Session
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
        order = self.repository.get_order_by_id(order_id, session)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Đơn hàng không tồn tại"
            )

        # Validate status
        valid_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPING,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED,
        ]

        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trạng thái không hợp lệ. Cho phép: {valid_statuses}",
            )

        order = self.repository.update_order_status(order, new_status, session)
        
        return {
            "message": "Cập nhật trạng thái thành công",
            "order_id": order.id,
            "new_status": new_status
        }