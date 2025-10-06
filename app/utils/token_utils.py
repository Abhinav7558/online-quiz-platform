from datetime import datetime, timedelta, timezone

from jose import jwt, ExpiredSignatureError,JWTError

from app.config import settings

def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_access_token_from_refresh_token(refresh_token: str) -> str:
    """Verify refresh token and create a new access token"""
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type, expected refresh")

        username: str = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token payload")

        return create_access_token(data={"sub": username})

    except ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except JWTError:
        raise ValueError("Invalid refresh token")