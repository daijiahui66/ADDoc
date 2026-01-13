from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "secret_key_for_dev"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Using bcrypt directly might be better if passlib is acting up, 
# but passlib is the standard for FastAPI.
# The error `AttributeError: module 'bcrypt' has no attribute '__about__'` suggests incompatibility.
# We will downgrade bcrypt or use a compatible version.
# For now, let's stick to standard config but maybe try a different scheme if needed.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
