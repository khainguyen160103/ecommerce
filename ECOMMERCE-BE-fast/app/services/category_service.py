"""
Category Service - Xử lý logic quản lý danh mục sản phẩm
Admin: CRUD danh mục
User/Guest: Xem danh mục
"""
from app.models.category_model import Category, CategoryIn, CategoryOut
from app.repositories.category_repository import CategoryRepository
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
        Args:
            category_id: UUID của danh mục
            session: Database session
        Returns:
            Dict chứa message
        Raises:
            HTTPException 400: Danh mục đang có sản phẩm
        """
        category = session.exec(
            select(Category).where(Category.id == category_id)
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Danh mục không tồn tại"
            )
        
        # Kiểm tra có sản phẩm không
        if category.products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa danh mục đang có sản phẩm"
            )
        
        session.delete(category)
        session.commit()
        
        return {"message": "Xóa danh mục thành công"}