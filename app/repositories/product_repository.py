from sqlmodel import Session, select
from fastapi import HTTPException
from typing import Any
from sqlalchemy.orm import selectinload , joinedload
from app.models.product_model import ProductIn, Product, ProductOut
from app.models.product_image_model import ProductImage
from app.utils.response_helper import ResponseHandler
from app.models.product_detail_model import ProductDetail
from uuid import UUID
from typing import List, Dict, Any

class ProductRepository :
    def get_all(self, session: Session,
                 category_id : UUID | None = None, 
                page: int = 1, 
                limit: int = 20
                ) -> Dict[str,Any]: 
        off_set = (page - 1) * limit
        stmt = select(Product).options(joinedload(Product.category),selectinload(Product.images)).offset(offset=off_set).limit(limit=limit)
        if category_id: 
              stmt = select(Product).options(joinedload(Product.category),selectinload(Product.images)).where(Product.category_id == category_id).offset(offset=off_set).limit(limit=limit)
        products = session.exec(stmt).all()
        return products
        

    def get_by_id(self,  product_id: UUID, session: Session) -> Product:         
            product = session.exec(
            select(Product).where(Product.id == product_id)
            ).first()
            return product
    
    def get_by_category(self ,skip : int , limit: int , category_id: UUID , session: Session) -> List[Product]: 
            products = session.exec(
            select(Product)
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
        ).all()
            return products
    
    def create(self ,session: Session , product: Product) -> Product: 
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
    
    def update(self, session: Session, product: Product) -> Product:
        """Cập nhật sản phẩm"""
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    
    def delete(self, product : Product, session: Session) -> None: 
        session.delete(product)
        session.commit()
    
    # ==================== PRODUCT DETAIL METHODS ====================
    
    def create_detail(self, detail: ProductDetail, session : Session) -> ProductDetail: 
        """Tạo chi tiết sản phẩm mới"""
        session.add(detail)
        session.commit()
        session.refresh(detail)
        return detail

    def get_detail_by_id(self, detail_id: UUID, session: Session) -> ProductDetail | None: 
        """Lấy chi tiết sản phẩm theo ID chi tiết"""
        stmt = select(ProductDetail).where(ProductDetail.id == detail_id)
        result = session.exec(stmt).first()
        return result
    
    def get_details_by_product(self, product_id: UUID, session: Session) -> List[ProductDetail]:
        """Lấy tất cả chi tiết của một sản phẩm"""
        stmt = select(ProductDetail).where(ProductDetail.product_id == product_id)
        results = session.exec(stmt).all()
        return results
    
    def update_detail(self, detail: ProductDetail, session: Session) -> ProductDetail:
        """Cập nhật chi tiết sản phẩm"""
        session.add(detail)
        session.commit()
        session.refresh(detail)
        return detail
    
    def delete_detail(self, detail: ProductDetail, session: Session) -> None:
        """Xóa chi tiết sản phẩm"""
        session.delete(detail)
        session.commit()

