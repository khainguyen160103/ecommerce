"""
Cart Service - Xử lý logic giỏ hàng
User: CRUD giỏ hàng cá nhân
Admin: Xem tất cả giỏ hàng
"""
from app.models.cart_model import Cart, CartOut
from app.models.cart_item_model import CartItem, CartItemIn, CartItemOut
from app.models.product_model import Product
from app.models.user_model import User
from fastapi import HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Dict, Any
from datetime import datetime


class CartService:
    """Service quản lý giỏ hàng"""
    
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
        cart = session.exec(
            select(Cart).where(Cart.user_id == current_user.id)
        ).first()
        
        if not cart:
            # Tạo cart mới nếu chưa có
            cart = Cart(user_id=current_user.id, total=0)
            session.add(cart)
            session.commit()
            session.refresh(cart)
        
        # Lấy cart items
        cart_items = session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id)
        ).all()
        
        return {
            "cart": CartOut.model_validate(cart),
            "items": [CartItemOut.model_validate(item) for item in cart_items],
            "total_items": len(cart_items)
        }
    
    def add_to_cart(
        self, 
        current_user: User, 
        product_id: UUID, 
        quantity: int, 
        session: Session
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
        product = session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không tồn tại"
            )
        
        # Tìm hoặc tạo cart
        cart = session.exec(
            select(Cart).where(Cart.user_id == current_user.id)
        ).first()
        
        if not cart:
            cart = Cart(user_id=current_user.id, total=0)
            session.add(cart)
            session.commit()
            session.refresh(cart)
        
        # Kiểm tra sản phẩm đã có trong cart chưa
        existing_item = session.exec(
            select(CartItem).where(
                (CartItem.cart_id == cart.id) & 
                (CartItem.product_id == product_id)
            )
        ).first()
        
        if existing_item:
            # Cập nhật số lượng
            existing_item.quantity += quantity
            existing_item.update_at = datetime.now()
            session.add(existing_item)
            cart_item = existing_item
            message = "Cập nhật số lượng sản phẩm trong giỏ hàng"
        else:
            # Thêm mới
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(cart_item)
            message = "Thêm sản phẩm vào giỏ hàng thành công"
        
        # Cập nhật tổng số lượng trong cart
        self._update_cart_total(cart=cart, session=session)
        
        session.commit()
        session.refresh(cart_item)
        
        return {
            "message": message,
            "cart_item": CartItemOut.model_validate(cart_item)
        }
    
    def update_cart_item(
        self, 
        current_user: User, 
        cart_item_id: UUID, 
        quantity: int, 
        session: Session
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
            current_user=current_user, 
            cart_item_id=cart_item_id, 
            session=session
        )
        
        if quantity <= 0:
            # Xóa nếu số lượng <= 0
            return self.remove_from_cart(
                current_user=current_user,
                cart_item_id=cart_item_id,
                session=session
            )
        
        cart_item.quantity = quantity
        cart_item.update_at = datetime.now()
        session.add(cart_item)
        
        # Cập nhật tổng cart
        cart = session.exec(
            select(Cart).where(Cart.id == cart_item.cart_id)
        ).first()
        self._update_cart_total(cart=cart, session=session)
        
        session.commit()
        session.refresh(cart_item)
        
        return {
            "message": "Cập nhật số lượng thành công",
            "cart_item": CartItemOut.model_validate(cart_item)
        }
    
    def remove_from_cart(
        self, 
        current_user: User, 
        cart_item_id: UUID, 
        session: Session
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
            current_user=current_user, 
            cart_item_id=cart_item_id, 
            session=session
        )
        
        cart = session.exec(
            select(Cart).where(Cart.id == cart_item.cart_id)
        ).first()
        
        session.delete(cart_item)
        
        # Cập nhật tổng cart
        self._update_cart_total(cart=cart, session=session)
        
        session.commit()
        
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
        cart = session.exec(
            select(Cart).where(Cart.user_id == current_user.id)
        ).first()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giỏ hàng không tồn tại"
            )
        
        # Xóa tất cả cart items
        cart_items = session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id)
        ).all()
        
        for item in cart_items:
            session.delete(item)
        
        cart.total = 0
        session.add(cart)
        session.commit()
        
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
        cart_item = session.exec(
            select(CartItem).where(CartItem.id == cart_item_id)
        ).first()
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không có trong giỏ hàng"
            )
        
        # Kiểm tra cart thuộc về user
        cart = session.exec(
            select(Cart).where(Cart.id == cart_item.cart_id)
        ).first()
        
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
        cart_items = session.exec(
            select(CartItem).where(CartItem.cart_id == cart.id)
        ).all()
        
        cart.total = sum(item.quantity for item in cart_items)
        cart.update_at = datetime.now()
        session.add(cart)
