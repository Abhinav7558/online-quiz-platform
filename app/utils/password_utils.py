from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    """Hash a plain password"""
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password"""
    return password_hash.verify(plain_password, hashed_password)
