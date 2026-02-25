from app.models.category_model import Category, CategoryIn, CategoryOut
from sqlmodel import Session, select
from typing import Dict , Any, List
from uuid import UUID

from app.utils.response_helper import ResponseHandler
class CategoryRepository: 
    def get_all(self, session: Session) -> List[CategoryOut]: 
        return session.exec(select(Category)).all()
    
    def get_by_id(self, id :UUID , session: Session) -> CategoryOut | None : 
        return session.exec(select(Category).where(Category.id == id)).first()

    def get_by_name(self, name:str , session: Session) -> CategoryOut: 
        return session.exec(select(Category).where(Category.name == name)).first()
    
    def create(self, category: CategoryIn , session: Session) -> CategoryOut: 
            session.add(category)
            session.commit()
            return category
    
    def update(self, category: CategoryIn, session:Session) -> CategoryOut: 
        pass

    def delete(self, category_id: UUID, session: Session) -> None: 
        category = self.get_by_id(category_id, session)
        if category: 
            session.delete(category)
        else: 
            return ResponseHandler.error("Lỗi không thể xóa từ server" , 500)