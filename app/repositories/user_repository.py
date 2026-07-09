from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_by_name(self, db: Session, name: str):
        return db.query(User).filter(User.name == name).first()

    def get_all(self, db: Session):
        return db.query(User).all()

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()

    def update(self, db: Session, user: User):
        db.commit()
        db.refresh(user)
        return user