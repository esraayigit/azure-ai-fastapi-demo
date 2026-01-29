"""Authentication Endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
import uuid
import logging
from datetime import datetime

from app.auth.models import UserCreate, UserLogin, Token, User
from app.auth.jwt_handler import (
    create_access_token,
    verify_password,
    get_password_hash
)
from app.auth.dependencies import get_current_active_user
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)
USERS_DB = {}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **full_name**: Optional full name
    """
    # check if username already exists
    if any(u["username"] == user_data.username for u in USERS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # check if email already exists
    if any(u["email"] == user_data.email for u in USERS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    USERS_DB[user_id] = user
    
    logger.info(f"New user registered: {user_data.username}")
    
    # return user without password
    return User(**{k: v for k, v in user.items() if k != "hashed_password"})


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login and get access token
    
    - **username**: Your username
    - **password**: Your password
    
    Returns JWT access token
    """
    # find user by username
    user = next(
        (u for u in USERS_DB.values() if u["username"] == login_data.username),
        None
    )
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "user_id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"]
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {login_data.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user information
    
    Requires authentication token
    """
    # find user in database
    user = USERS_DB.get(current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(**{k: v for k, v in user.items() if k != "hashed_password"})
