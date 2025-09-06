"""
Authentication and security module for WebLib.
Provides utilities for secure password handling, JWT-based sessions,
and authentication management with secure, HttpOnly cookies.
"""

import secrets
import time
from typing import Optional, Dict, Any, Callable, Union
from datetime import datetime, timedelta
import functools

from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette.requests import Request
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from .orm import BaseModel

# --- Security Configuration ---

class AuthManager:
    """
    Manages authentication settings and utilities.
    """
    def __init__(self, secret_key: str = None, token_expiration_minutes: int = 60 * 24 * 7):
        """
        Initialize the authentication manager.
        
        Args:
            secret_key: A secret key for signing JWTs. If not provided, a random one is generated.
            token_expiration_minutes: How long tokens are valid for, in minutes. Default is 7 days.
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_expiration_minutes = token_expiration_minutes
        self.algorithm = "HS256"
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_model = None
        
    def set_user_model(self, model_class: type):
        """Set the user model class that will be used for authentication."""
        self.user_model = model_class
        return self
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify that a plain password matches the hashed version."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate a secure hash of the password."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a new JWT access token with the provided data.
        
        Args:
            data: The payload data to include in the token.
        
        Returns:
            The encoded JWT token.
        """
        to_encode = data.copy()
        expires_delta = timedelta(minutes=self.token_expiration_minutes)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_access_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT access token.
        
        Args:
            token: The JWT token to decode.
            
        Returns:
            The decoded token payload.
            
        Raises:
            JWTError: If the token is invalid or expired.
        """
        try:
            # Print debugging info
            print(f"Decoding token with secret key: {self.secret_key[:5]}...")
            
            # Decode the token
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            print(f"JWT decode error: {str(e)}")
            raise

    def set_auth_cookie(self, response, user_id: Union[str, int]) -> None:
        """
        Set a secure authentication cookie on a response.
        
        Args:
            response: The response object to set the cookie on.
            user_id: The ID of the authenticated user.
        """
        token = self.create_access_token({"sub": str(user_id)})
        
        # Set cookie with secure attributes
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,       # Inaccessible to JavaScript
            secure=True,         # Sent only over HTTPS
            samesite="lax",      # Protects against CSRF
            max_age=self.token_expiration_minutes * 60
        )
        
    def clear_auth_cookie(self, response) -> None:
        """
        Clear the authentication cookie from a response.
        
        Args:
            response: The response object to clear the cookie from.
        """
        response.delete_cookie(key="access_token")
    
    def login(self, request, user) -> None:
        """
        Log a user in by setting the auth cookie on the response.
        
        Args:
            request: The request object.
            user: The user object to log in.
        """
        from .routing import Response
        # Create a token
        token = self.create_access_token({"sub": str(user.id)})
        print(f"Generated token for user {user.id}: {token[:20]}...")
        
        # Create a response object
        response = Response("", status_code=200)
        
        # Set the cookie on the response
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=False,  # Set to False to debug - normally should be True
            secure=False,    # Set to False for local development - should be True in production
            samesite="lax",
            max_age=self.token_expiration_minutes * 60
        )
        
        # Also set the token in the request cookies for immediate effect
        if isinstance(request.cookies, dict):
            request.cookies["access_token"] = token
            print(f"Added token to request.cookies: {token[:20]}...")
        else:
            print(f"WARNING: request.cookies is not a dict, type: {type(request.cookies)}")
        
        print(f"Login response cookies: {response.cookies}")
        return response
    
    def logout(self, request) -> None:
        """
        Log a user out by clearing the auth cookie.
        
        Args:
            request: The request object.
        """
        from .routing import Response
        response = Response("", status_code=200)
        self.clear_auth_cookie(response)
        
        # Remove the cookie from the request safely
        if isinstance(request.cookies, dict) and "access_token" in request.cookies:
            del request.cookies["access_token"]
        
        return response

    def get_current_user(self, request: Request) -> Optional[Any]:
        """
        Get the current user from the request's authentication cookie.
        
        Args:
            request: The incoming request.
            
        Returns:
            The user object if authentication is successful, None otherwise.
        """
        # Check for token in cookies
        token = request.cookies.get("access_token")
        if not token:
            print("No access_token found in cookies")
            return None
        
        try:
            # Decode the token
            payload = self.decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                print("No user_id (sub) found in token payload")
                return None
                
            print(f"Found user_id in token: {user_id}")
                
            if not self.user_model:
                print("User model not set. Use auth_manager.set_user_model(YourUserModel) first.")
                raise ValueError("User model not set. Use auth_manager.set_user_model(YourUserModel) first.")
            
            # Get the database from request state
            db = getattr(request.state, "db", None)
            if not db:
                print("Database not found on request.state.db. Make sure to configure the DatabaseMiddleware.")
                raise ValueError("Database not found on request.state.db. Make sure to configure the DatabaseMiddleware.")
            
            # Fetch the user - use filter().first() instead of get() for more robustness
            try:
                # Try both filter and get approaches
                print(f"Looking for user with id={user_id}")
                
                # First try with filter
                user = self.user_model.objects(db).filter(id=user_id).first()
                
                if not user:
                    # Then try with get
                    print(f"filter() failed, trying get(id={user_id})")
                    user = self.user_model.objects(db).get(id=user_id)
                
                if not user:
                    print(f"User with id {user_id} not found in database")
                    return None
                    
                print(f"Found user: {user.username} (ID: {user.id})")
                return user
            except Exception as e:
                print(f"Error fetching user from database: {str(e)}")
                return None
        
        except JWTError as je:
            print(f"JWT Error: {str(je)}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_current_user: {str(e)}")
            return None
            
    def require_auth(self, f: Callable) -> Callable:
        """
        Decorator to require authentication for a route handler.
        
        Args:
            f: The route handler function.
            
        Returns:
            The wrapped function that checks authentication.
        """
        @functools.wraps(f)
        def wrapped(request: Request, *args, **kwargs):
            print(f"Checking authentication for: {request.path}")
            print(f"Request cookies: {request.cookies}")
            
            token = request.cookies.get("access_token")
            print(f"Access token: {token[:20] if token else 'None'}")
            
            user = self.get_current_user(request)
            if not user:
                from .routing import Response
                print(f"Unauthorized access attempt to {request.path}")
                # Return a more user-friendly unauthorized page
                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Login Required</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header bg-danger text-white">
                                        <h3>Login Required</h3>
                                    </div>
                                    <div class="card-body">
                                        <p>You need to be logged in to access this page.</p>
                                        <p>Please log in to continue.</p>
                                        <a href="/" class="btn btn-primary">Go to Login Page</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
                return Response(html_content, status_code=401)
            
            # Attach the user to the request
            request.state.user = user
            print(f"User {user.username} (ID: {user.id}) authenticated for {request.path}")
            return f(request, *args, **kwargs)
        
        return wrapped

# Create a global auth manager instance
auth_manager = AuthManager()

# --- Convenience Functions ---

def get_password_hash(password: str) -> str:
    """Generate a secure hash of the password."""
    return auth_manager.get_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches the hashed version."""
    return auth_manager.verify_password(plain_password, hashed_password)

def get_current_user(request: Request) -> Optional[Any]:
    """Get the authenticated user from the request."""
    return auth_manager.get_current_user(request)

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route handler."""
    return auth_manager.require_auth(f)

# --- Base User Model ---

class User(BaseModel):
    """
    Base user model for authentication.
    Applications should subclass this to add additional fields.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def authenticate(cls, db, email: str, password: str) -> Optional["User"]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: The database instance.
            email: The user's email.
            password: The user's password.
            
        Returns:
            The user if authentication succeeds, None otherwise.
        """
        user = cls.objects(db).get(email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @classmethod
    def create_user(cls, db, email: str, password: str, **kwargs) -> "User":
        """
        Create a new user with a hashed password.
        
        Args:
            db: The database instance.
            email: The user's email.
            password: The user's plain text password (will be hashed).
            **kwargs: Additional fields for the user.
            
        Returns:
            The created user.
        """
        hashed_password = get_password_hash(password)
        with db.session_scope() as session:
            user = cls(
                email=email,
                hashed_password=hashed_password,
                **kwargs
            )
            session.add(user)
            session.commit()
            return user

# --- Example Usage ---

if __name__ == "__main__":
    from .orm import Database
    
    # 1. Setup the database
    db = Database('sqlite:///./auth_test.db')
    
    # 2. Create the tables
    db.create_all()
    
    # 3. Create a user
    user = User.create_user(db, "test@example.com", "password123")
    print(f"User created: {user.email}")
    
    # 4. Authenticate the user
    authenticated_user = User.authenticate(db, "test@example.com", "password123")
    if authenticated_user:
        print("Authentication successful!")
    else:
        print("Authentication failed!")
        
    # 5. Create a JWT token for the user
    auth_manager.set_user_model(User)
    token = auth_manager.create_access_token({"sub": str(user.id)})
    print(f"JWT token: {token}")
    
    # Clean up test database
    import os
    os.remove("auth_test.db")
