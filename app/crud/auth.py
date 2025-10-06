from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas import auth as auth_schemas
from ..utils import password_utils

def get_user_by_username_or_email(db: Session, username: str, email: str):
    return db.query(User).filter((User.username == username) | (User.email == email)).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: auth_schemas.UserRegister) -> User:
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=password_utils.get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user