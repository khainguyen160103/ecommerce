"""
Product Service - Xử lý logic quản lý sản phẩm
Admin: CRUD sản phẩm
User/Guest: Xem sản phẩm, tìm kiếm, lọc
"""
from app.models.product_model import Product, ProductIn, ProductOut
from app.models.produc_detail_model import ProductDetail, ProductDetailIn
from fastapi import HTTPException, status
from sqlmodel import Session, select, or_
from uuid import UUID
from typing import List, Dict, Any, Optional


class ProductService:
    """Service quản lý sản phẩm"""
    
    # ==================== GUEST/USER FUNCTIONS ====================
    
    def get_all_products(
        self, 
        session: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: UUID | None = None,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None
    ) -> Dict[str, Any]:
        """
        [GUEST] Lấy danh sách sản phẩm với filter và pagination
        Args:
            session: Database session
            skip: Số record bỏ qua
            limit: Số record tối đa
            category_id: Lọc theo danh mục
            search: Tìm kiếm theo tên/mô tả
            min_price: Giá tối thiểu
            max_price: Giá tối đa
        Returns:
            Dict chứa products và pagination info
        """
        query = select(Product)
        
        # Filter theo category
        if category_id:
            query = query.where(Product.category_id == category_id)
        
        # Tìm kiếm theo tên/mô tả
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Filter theo giá (giả sử price là string, cần convert)
        # Có thể cải thiện bằng cách đổi kiểu dữ liệu price sang Decimal
        
        # Thực hiện query với pagination
        products = session.exec(query.offset(skip).limit(limit)).all()
        total = len(session.exec(query).all())
        
        return {
            "products": [ProductOut.model_validate(p) for p in products],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_product_by_id(self, product_id: UUID, session: Session) -> Dict[str, Any]:
        """
        [GUEST] Lấy chi tiết sản phẩm theo ID
        Args:
            product_id: UUID của sản phẩm
            session: Database session
        Returns:
            Dict chứa product và product_details
        """
        product = session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không tồn tại"
            )
        
        return {
            "product": ProductOut.model_validate(product),
            "details": product.product_details  # Lấy các variants
        }
    
    def get_products_by_category(
        self, 
        category_id: UUID, 
        session: Session,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProductOut]:
        """
        [GUEST] Lấy sản phẩm theo danh mục
        Args:
            category_id: UUID của danh mục
            session: Database session
            skip: Số record bỏ qua
            limit: Số record tối đa
        Returns:
            List các ProductOut
        """
        products = session.exec(
            select(Product)
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
        ).all()
        
        return [ProductOut.model_validate(p) for p in products]
    
    # ==================== ADMIN FUNCTIONS ====================
    
    def create_product(self, data: ProductIn, session: Session) -> Dict[str, Any]:
        """
        [ADMIN] Tạo sản phẩm mới
        Args:
            data: Thông tin sản phẩm
            session: Database session
        Returns:
            Dict chứa message và product info
        """
        product = Product(**data.model_dump())
        session.add(product)
        session.commit()
        session.refresh(product)
        
        return {
            "message": "Tạo sản phẩm thành công",
            "product": ProductOut.model_validate(product)
        }
    
    def update_product(
        self, 
        product_id: UUID, 
        data: ProductIn, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [ADMIN] Cập nhật sản phẩm
        Args:
            product_id: UUID của sản phẩm
            data: Thông tin mới
            session: Database session
        Returns:
            Dict chứa message và product info
        """
        product = session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không tồn tại"
            )
        
        # Cập nhật các fields
        for key, value in data.model_dump().items():
            setattr(product, key, value)
        
        session.add(product)
        session.commit()
        session.refresh(product)
        
        return {
            "message": "Cập nhật sản phẩm thành công",
            "product": ProductOut.model_validate(product)
        }
    
    def delete_product(self, product_id: UUID, session: Session) -> Dict[str, str]:
        """
        [ADMIN] Xóa sản phẩm
        Args:
            product_id: UUID của sản phẩm
            session: Database session
        Returns:
            Dict chứa message
        """
        product = session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không tồn tại"
            )
        
        session.delete(product)
        session.commit()
        
        return {"message": "Xóa sản phẩm thành công"}
    
    def add_product_detail(
        self, 
        product_id: UUID, 
        data: ProductDetailIn, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [ADMIN] Thêm variant cho sản phẩm (color, size, stock...)
        Args:
            product_id: UUID của sản phẩm
            data: Thông tin variant
            session: Database session
        Returns:
            Dict chứa message và detail info
        """
        # Kiểm tra product tồn tại
        product = session.exec(
            select(Product).where(Product.id == product_id)
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sản phẩm không tồn tại"
            )
        
        detail = ProductDetail(product_id=product_id, **data.model_dump(exclude={'product_id'}))
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        return {
            "message": "Thêm variant thành công",
            "detail": detail
        }