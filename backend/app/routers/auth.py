from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.auth import Token, User, UserCreate
from app.services.auth_service import authenticate_user, create_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token(user["username"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register new user"""
    # TODO: Store in database
    hashed_password = get_password_hash(user.password)
    return {"username": user.username, "email": user.email, "hashed_password": hashed_password}


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user info"""
    # TODO: Implement with real auth
    return {"username": "current_user"}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout endpoint"""
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Refresh access token"""
    # TODO: Implement token refresh
    return {"access_token": token, "token_type": "bearer"}