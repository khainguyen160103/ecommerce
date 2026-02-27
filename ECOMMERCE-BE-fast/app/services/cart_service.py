"""
Cart Service - Xử lý logic giỏ hàng
User: CRUD giỏ hàng cá nhân
Admin: Xem tất cả giỏ hàng
"""
from app.models.cart_model import Cart, CartOut
from app.models.cart_item_model import CartItem, CartItemOut
from app.models.user_model import User
from app.repositories.cart_repository import CartRepository
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from uuid import UUID
from typing import Dict, Any, Annotated, Optional


class CartService:
    """Service quản lý giỏ hàng"""

    def __init__(self, repository: Annotated[CartRepository, Depends()]):
        self.repository = repository

    # ==================== USER FUNCTIONS ====================

    def get_my_cart(self, current_user: User, session: Session) -> Dict[str, Any]:
        """
        [USER] Lấy giỏ hàng của user hiện tại
        Args:
            current_user: User hiện tại
            session: Database session
        Returns:
            Dict chứa cart và cart items
        """
        # Tìm hoặc tạo cart cho user
        cart = self.repository.get_cart_by_user_id(current_user.id, session)

        if not cart:
            # Tạo cart mới nếu chưa có
            cart = Cart(user_id=current_user.id, total=0)
            cart = self.repository.create_cart(cart, session)

        # Lấy cart items
        cart_items = self.repository.get_cart_items(cart.id, session)

        return {
            "cart": CartOut.model_validate(cart),
            "items": [CartItemOut.model_validate(item) for item in cart_items],
            "total_items": len(cart_items),
        }

    def add_to_cart(
        self,
        current_user: User,
        product_id: UUID,
        detail_id: UUID,
        quantity: int,
        session: Session = None,
    ) -> Dict[str, Any]:
        """
        [USER] Thêm sản phẩm vào giỏ hàng
        Args:
            current_user: User hiện tại
            product_id: ID sản phẩm
            quantity: Số lượng
            session: Database session
        Returns:
            Dict chứa message và cart item
        """
        # Kiểm tra sản phẩm tồn tại
        product = self.repository.get_product_by_id(product_id, session)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sản phẩm không tồn tại"
            )

        # Tìm hoặc tạo cart
        cart = self.repository.get_cart_by_user_id(current_user.id, session)

        # if not cart:
        #     cart = Cart(user_id=current_user.id, total=0)
        #     cart = self.repository.create_cart(cart, session)

        # Kiểm tra sản phẩm đã có trong cart chưa
        existing_item = self.repository.get_cart_item_by_detail(
            cart.id, detail_id, session
        )
        print("exist cart: ", existing_item)
        if existing_item:
            # Cập nhật số lượng
            existing_item.quantity += quantity
            cart_item = self.repository.update_cart_item(existing_item, session)
            message = "Cập nhật số lượng sản phẩm trong giỏ hàng"
        else:
            # Thêm mới
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                detail_id=detail_id,
            )
            cart_item = self.repository.create_cart_item(cart_item, session)
            message = "Thêm sản phẩm vào giỏ hàng thành công"

        # Cập nhật tổng số lượng trong cart
        self._update_cart_total(cart=cart, session=session)

        return {"message": message, "cart_item": CartItemOut.model_validate(cart_item)}

    def update_cart_item(
        self, current_user: User, cart_item_id: UUID, quantity: int, session: Session
    ) -> Dict[str, Any]:
        """
        [USER] Cập nhật số lượng sản phẩm trong giỏ
        Args:
            current_user: User hiện tại
            cart_item_id: ID của cart item
            quantity: Số lượng mới
            session: Database session
        Returns:
            Dict chứa message và cart item
        """
        # Kiểm tra cart item thuộc về user
        cart_item = self._get_user_cart_item(
            current_user=current_user, cart_item_id=cart_item_id, session=session
        )

        if quantity <= 0:
            # Xóa nếu số lượng <= 0
            return self.remove_from_cart(
                current_user=current_user, cart_item_id=cart_item_id, session=session
            )

        cart_item.quantity = quantity
        cart_item = self.repository.update_cart_item(cart_item, session)

        # Cập nhật tổng cart
        cart = self.repository.get_cart_by_id(cart_item.cart_id, session)
        self._update_cart_total(cart=cart, session=session)

        return {
            "message": "Cập nhật số lượng thành công",
            "cart_item": CartItemOut.model_validate(cart_item),
        }

    def remove_from_cart(
        self, current_user: User, cart_item_id: UUID, session: Session
    ) -> Dict[str, str]:
        """
        [USER] Xóa sản phẩm khỏi giỏ hàng
        Args:
            current_user: User hiện tại
            cart_item_id: ID của cart item
            session: Database session
        Returns:
            Dict chứa message
        """
        cart_item = self._get_user_cart_item(
            current_user=current_user, cart_item_id=cart_item_id, session=session
        )

        cart = self.repository.get_cart_by_id(cart_item.cart_id, session)

        self.repository.delete_cart_item(cart_item, session)

        # Cập nhật tổng cart
        self._update_cart_total(cart=cart, session=session)

        return {"message": "Xóa sản phẩm khỏi giỏ hàng thành công"}
    
    def clear_cart(self, current_user: User, session: Session) -> Dict[str, str]:
        """
        [USER] Xóa toàn bộ giỏ hàng
        Args:
            current_user: User hiện tại
            session: Database session
        Returns:
            Dict chứa message
        """
        cart = self.repository.get_cart_by_user_id(current_user.id, session)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giỏ hàng không tồn tại"
            )
        
        # Xóa tất cả cart items
        self.repository.delete_all_cart_items(cart.id, session)

        # Cập nhật cart total
        self.repository.update_cart_total(cart, 0, session)
        
        return {"message": "Đã xóa toàn bộ giỏ hàng"}
    
    # ==================== HELPER FUNCTIONS ====================
    
    def _get_user_cart_item(
        self, 
        current_user: User, 
        cart_item_id: UUID, 
        session: Session
    ) -> CartItem:
        """
        Helper: Lấy cart item và kiểm tra quyền sở hữu
        """
        cart_item = self.repository.get_cart_item_by_id(cart_item_id, session)
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không có trong giỏ hàng"
            )
        
        # Kiểm tra cart thuộc về user
        cart = self.repository.get_cart_by_id(cart_item.cart_id, session)
        
        if cart.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thao tác với giỏ hàng này"
            )
        
        return cart_item
    
    def _update_cart_total(self, cart: Cart, session: Session) -> None:
        """
        Helper: Cập nhật tổng số lượng trong cart
        """
        cart_items = self.repository.get_cart_items(cart.id, session)
        total = sum(item.quantity for item in cart_items)
        self.repository.update_cart_total(cart, total, session)
