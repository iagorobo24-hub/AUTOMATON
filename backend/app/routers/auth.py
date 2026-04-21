from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..services.database import DatabaseService
from ..services.auth_service import (
    authenticate_user,
    create_token,
    create_user,
    hash_password,
    decode_token,
)
from ..api.deps import get_db_service
from ..models.auth import Token, UserCreate, User

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: DatabaseService = Depends(get_db_service)
) -> User:
    """Dependency to get current authenticated user"""
    token_data = decode_token(token)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        is_active=user.get("is_active", True),
        is_superuser=user.get("is_superuser", False),
        created_at=user.get("created_at")
    )


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DatabaseService = Depends(get_db_service)
):
    """Login endpoint"""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token(user["username"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: DatabaseService = Depends(get_db_service)
):
    """Register new user"""
    hashed_password = get_password_hash(user.password)

    try:
        new_user = await db.create_user({
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
        })
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return User(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        is_active=new_user.get("is_active", True),
        is_superuser=new_user.get("is_superuser", False),
        created_at=new_user.get("created_at")
    )


@router.get("/me", response_model=User)
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint"""
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Refresh access token"""
    # TODO: Implement token refresh
    return {"access_token": token, "token_type": "bearer"}