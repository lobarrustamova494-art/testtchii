"""
Authentication Routes
Login, logout, user management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict
import logging

from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize auth service
auth_service = AuthService()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str
    full_name: str
    email: EmailStr

class UserResponse(BaseModel):
    username: str
    role: str
    full_name: str
    email: str
    created_at: str
    is_active: bool

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    
    Returns JWT access token on successful authentication
    """
    logger.info(f"Login attempt for user: {request.username}")
    
    # Attempt login
    result = auth_service.login(request.username, request.password)
    
    if not result:
        logger.warning(f"Login failed for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    logger.info(f"Login successful for user: {request.username}")
    return result

@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """
    User logout endpoint
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint is for logging purposes.
    """
    logger.info(f"User logged out: {current_user['username']}")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """
    Get current user information
    """
    user_info = auth_service.get_user_info(current_user['username'])
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_info

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Change current user's password
    """
    success = auth_service.change_password(
        current_user['username'],
        request.old_password,
        request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Check your old password."
        )
    
    return {"message": "Password changed successfully"}

@router.post("/create-user", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    current_user: Dict = Depends(require_admin)
):
    """
    Create new user (admin only)
    """
    # Validate role
    if request.role not in ['admin', 'teacher']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'teacher'"
        )
    
    success = auth_service.create_user(
        request.username,
        request.password,
        request.role,
        request.full_name,
        request.email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user. Username may already exist."
        )
    
    # Return created user info
    user_info = auth_service.get_user_info(request.username)
    return user_info

@router.get("/verify-token")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """
    Verify if current token is valid
    """
    return {
        "valid": True,
        "user": current_user
    }