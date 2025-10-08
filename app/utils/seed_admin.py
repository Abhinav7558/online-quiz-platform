from app.dependencies import SessionLocal
from app.models.user import User, UserRole
from app.utils import password_utils
from app.config import settings

import logging

logger = logging.getLogger(__name__)

def create_default_admin():
    """Create a default admin user if none exists."""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            new_admin = User(
                username=settings.default_admin_username,
                email=settings.default_admin_email,
                hashed_password=password_utils.get_password_hash(settings.default_admin_password),
                role=UserRole.ADMIN,
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            logger.info(f"Default admin user created: {settings.default_admin_username}")
        else:
            logger.info("Admin user already exists. Skipping creation.")
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
    finally:
        db.close()
