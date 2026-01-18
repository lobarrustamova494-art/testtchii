"""
JWT-based Authentication Service
Secure user authentication with password hashing
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class AuthService:
    """
    JWT-based authentication service
    """
    
    def __init__(
        self,
        secret_key: str = "your-secret-key-change-in-production",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        users_file: str = "users.json"
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.users_file = Path(users_file)
        
        # Initialize default users if file doesn't exist
        self._init_default_users()
        
    def _init_default_users(self):
        """Initialize default users if users.json doesn't exist"""
        if not self.users_file.exists():
            default_users = {
                "admin": {
                    "username": "admin",
                    "password_hash": self._hash_password("admin123"),  # Changed from 'admin'
                    "role": "admin",
                    "full_name": "System Administrator",
                    "email": "admin@example.com",
                    "created_at": datetime.now().isoformat(),
                    "is_active": True
                },
                "teacher": {
                    "username": "teacher",
                    "password_hash": self._hash_password("teacher123"),  # Changed from 'teacher'
                    "role": "teacher",
                    "full_name": "Teacher User",
                    "email": "teacher@example.com",
                    "created_at": datetime.now().isoformat(),
                    "is_active": True
                }
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
            
            logger.info(f"Default users created in {self.users_file}")
            logger.info("Default credentials: admin/admin123, teacher/teacher123")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return {}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with username and password
        
        Returns:
            dict: User data if authenticated, None otherwise
        """
        users = self._load_users()
        user = users.get(username)
        
        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None
        
        if not user.get('is_active', True):
            logger.warning(f"Authentication failed: user '{username}' is inactive")
            return None
        
        if not self._verify_password(password, user['password_hash']):
            logger.warning(f"Authentication failed: invalid password for user '{username}'")
            return None
        
        logger.info(f"User '{username}' authenticated successfully")
        
        # Return user data without password hash
        return {
            'username': user['username'],
            'role': user['role'],
            'full_name': user['full_name'],
            'email': user['email']
        }
    
    def create_access_token(self, user_data: Dict) -> str:
        """
        Create JWT access token
        
        Args:
            user_data: User information
            
        Returns:
            str: JWT token
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'sub': user_data['username'],  # Subject
            'role': user_data['role'],
            'full_name': user_data['full_name'],
            'email': user_data['email'],
            'exp': expire,  # Expiration time
            'iat': datetime.utcnow(),  # Issued at
            'type': 'access_token'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Access token created for user '{user_data['username']}'")
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("Token verification failed: token expired")
                return None
            
            # Check token type
            if payload.get('type') != 'access_token':
                logger.warning("Token verification failed: invalid token type")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """
        Complete login process
        
        Returns:
            dict: Login response with token and user info
        """
        # Authenticate user
        user_data = self.authenticate_user(username, password)
        if not user_data:
            return None
        
        # Create access token
        access_token = self.create_access_token(user_data)
        
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': self.access_token_expire_minutes * 60,  # seconds
            'user': user_data
        }
    
    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        full_name: str,
        email: str
    ) -> bool:
        """
        Create new user
        
        Returns:
            bool: True if user created successfully
        """
        users = self._load_users()
        
        if username in users:
            logger.warning(f"User creation failed: username '{username}' already exists")
            return False
        
        # Create new user
        new_user = {
            'username': username,
            'password_hash': self._hash_password(password),
            'role': role,
            'full_name': full_name,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        users[username] = new_user
        
        # Save to file
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"User '{username}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user '{username}': {e}")
            return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Returns:
            bool: True if password changed successfully
        """
        users = self._load_users()
        user = users.get(username)
        
        if not user:
            logger.warning(f"Password change failed: user '{username}' not found")
            return False
        
        # Verify old password
        if not self._verify_password(old_password, user['password_hash']):
            logger.warning(f"Password change failed: invalid old password for user '{username}'")
            return False
        
        # Update password
        user['password_hash'] = self._hash_password(new_password)
        user['password_changed_at'] = datetime.now().isoformat()
        
        # Save to file
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"Password changed successfully for user '{username}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to change password for user '{username}': {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information
        
        Returns:
            dict: User data without password hash
        """
        users = self._load_users()
        user = users.get(username)
        
        if not user:
            return None
        
        return {
            'username': user['username'],
            'role': user['role'],
            'full_name': user['full_name'],
            'email': user['email'],
            'created_at': user['created_at'],
            'is_active': user.get('is_active', True)
        }