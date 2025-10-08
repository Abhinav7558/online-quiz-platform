from sqlalchemy.orm import Session

from app.models.user import User, UserRole

def get_users(db: Session, limit: int = 10, offset: int = 0):
    return db.query(User).offset(offset).limit(limit).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user_role(db: Session, user: User, new_role: str):
    if not isinstance(new_role, UserRole):
        raise ValueError("Invalid role provided")
    
    user.role = new_role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
