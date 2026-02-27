from sqlalchemy.sql.functions import user
from sqlmodel import Session, select
from app.models.user_model import User, UserOut
from app.models.role_model import Role
from uuid import UUID
class UserRepository: 
    def create(self, data: User, session: Session) -> User:
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    def get_all(self, session: Session, skip: int , limit: int):
         result = [] 
         users = session.exec(
            select(User,Role.description.label('role'))
            .join_from(User, Role, User.role_id == Role.id).offset(skip).limit(limit)).all()
         for user_obj , role_description in users: 
            result.append(UserOut( 
                username=user_obj.username, 
                email=user_obj.email, 
                id = user_obj.id,
                status = user_obj.status,
                create_at=user_obj.create_at, 
                update_at=user_obj.update_at,
                role = role_description
            ))
         return result
     
    def get_by_id(self, id: UUID, session : Session):
        stmt = select(User, Role.description.label('role')).join_from(User, Role, User.role_id == Role.id).where(User.id == id)
        result = session.exec(stmt).first()
        user_obj, role_description = result
        user = UserOut( 
            username = user_obj.username, 
            email=user_obj.email,
            id= user_obj.id, 
            status = user_obj.status, 
            create_at=user_obj.create_at, 
            update_at=user_obj.update_at,
            role = role_description

        )
        return user
        
    def get_by_email(self,email : str , session : Session) -> UserOut:
       stmt = select(User, Role.description.label("role")).join_from(User , Role, User.role_id ==Role.id).where(User.email == email)
       result = session.exec(stmt).first()
       if not result: 
          return None
       user_obj, role_description = result
       user_data = User.model_validate(user_obj).model_dump()
       user_data.pop('role_id')
       user_data['role'] = role_description
       return user_data
    
    