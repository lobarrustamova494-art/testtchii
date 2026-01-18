"""
Authentication Middleware
JWT token validation for protected routes
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import logging

from services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token
        
    Returns:
        dict: Current user data
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Verify token
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        'username': payload['sub'],
        'role': payload['role'],
        'full_name': payload['full_name'],
        'email': payload['email']
    }

def require_role(required_role: str):
    """
    Decorator to require specific role
    
    Args:
        required_role: Required user role ('admin', 'teacher')
    """
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        if current_user['role'] != required_role and current_user['role'] != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    
    return role_checker

def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Require admin role
    """
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict]:
    """
    Optional authentication - returns user if token provided and valid
    
    Returns:
        dict: User data if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        payload = auth_service.verify_token(credentials.credentials)
        if payload:
            return {
                'username': payload['sub'],
                'role': payload['role'],
                'full_name': payload['full_name'],
                'email': payload['email']
            }
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
    
    return None