"""
Category Service - Xử lý logic quản lý danh mục sản phẩm
Admin: CRUD danh mục
User/Guest: Xem danh mục
"""
from app.models.category_model import Category, CategoryIn, CategoryOut
from app.models.product_model import Product
from app.repositories.category_repository import CategoryRepository
from app.core.constants import DEFAULT_CATEGORY_NAME
from app.utils.timezone import vn_now
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Dict, Any, Annotated


class CategoryService:
    """Service quản lý danh mục sản phẩm"""
    def __init__(self, repository : Annotated[CategoryRepository, Depends()]):
        self.repository = repository
    # ==================== GUEST/USER FUNCTIONS ====================
    
    def get_all_categories(self, session: Session) -> List[CategoryOut]:
        return self.repository.get_all(session=session)
    
    
    def get_category_by_id(self, category_id: UUID, session: Session) -> CategoryOut:
         return self.repository.get_by_id(category_id, session=session)
    
    # ==================== ADMIN FUNCTIONS ====================
    
    def create_category(self, data: CategoryIn, session: Session) -> Dict[str, Any]:
        existing = self.repository.get_by_name(data.name, session=session)
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên danh mục đã tồn tại"
            )
        category = Category(
            name=data.name, 
            description=data.description
        )
        result = self.repository.create(category=category, session=session)
        
        return {
            "message": "Tạo danh mục thành công",
            "category": CategoryOut.model_validate(result)
        }
    
    def update_category(
        self, 
        category_id: UUID, 
        data: CategoryIn, 
        session: Session
    ) -> Dict[str, Any]:
        """
        [ADMIN] Cập nhật danh mục
        Args:
            category_id: UUID của danh mục
            data: Thông tin mới
            session: Database session
        Returns:
            Dict chứa message và category info
        """
        category = session.exec(
            select(Category).where(Category.id == category_id)
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Danh mục không tồn tại"
            )
        
        # Kiểm tra tên trùng (trừ chính nó)
        existing = session.exec(
            select(Category).where(
                Category.name == data.name,
                Category.id != category_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên danh mục đã tồn tại"
            )
        
        category.name = data.name
        category.description = data.description
        category.update_at = vn_now()
        session.add(category)
        session.commit()
        session.refresh(category)
        
        return {
            "message": "Cập nhật danh mục thành công",
            "category": CategoryOut.model_validate(category)
        }
    
    def delete_category(self, category_id: UUID, session: Session) -> Dict[str, str]:
        """
        [ADMIN] Xóa danh mục
        Nếu danh mục có sản phẩm, chuyển các sản phẩm sang danh mục 'Chưa phân loại'
        Args:
            category_id: UUID của danh mục
            session: Database session
        Returns:
            Dict chứa message
        """
        category = session.exec(
            select(Category).where(Category.id == category_id)
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Danh mục không tồn tại"
            )

        # Không cho xóa danh mục mặc định
        if category.name == DEFAULT_CATEGORY_NAME:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa danh mục mặc định",
            )

        # Nếu danh mục có sản phẩm → chuyển sang danh mục 'Chưa phân loại'
        if category.products:
            default_category = session.exec(
                select(Category).where(Category.name == DEFAULT_CATEGORY_NAME)
            ).first()

            if not default_category:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Danh mục mặc định chưa được tạo. Vui lòng chạy seed lại.",
                )

            moved_count = len(category.products)
            # Chuyển tất cả sản phẩm sang danh mục mặc định
            for product in category.products:
                product.category_id = default_category.id
                session.add(product)

            session.commit()
            session.delete(category)
            session.commit()

            return {
                "message": f"Xóa danh mục thành công. {moved_count} sản phẩm đã được chuyển sang danh mục '{DEFAULT_CATEGORY_NAME}'"
            }
        
        session.delete(category)
        session.commit()
        
        return {"message": "Xóa danh mục thành công"}