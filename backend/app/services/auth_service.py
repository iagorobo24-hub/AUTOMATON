import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from typing import Optional
from app.models.auth import Token, TokenData
from app.core.config import settings


# Use config settings instead of hardcoded values
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return bcrypt.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except jwt.PyJWTError:
        return None


async def authenticate_user(username: str, password: str, db_service=None) -> Optional[dict]:
    """Authenticate user against database"""
    if db_service is None:
        # Fallback to mock for backward compatibility
        users_db = {
            "admin": {
                "id": "1",
                "username": "admin",
                "email": "admin@automaton.local",
                "hashed_password": get_password_hash("admin123"),
                "is_active": True,
            }
        }
        user = users_db.get(username)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user

    # Use real database
    return await db_service.authenticate_user(username, password)


def create_token(username: str) -> Token:
    """Create token for user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def create_user(username: str, email: str, password: str, db_service=None) -> dict:
    """Create a new user"""
    user_data = {
        "username": username,
        "email": email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    if db_service:
        # Save to database
        result = await db_service.db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
    else:
        user_data["id"] = "1"
    
    return user_data


# Alias for backward compatibility
hash_password = get_password_hash