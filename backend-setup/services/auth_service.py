"""
Authentication service for user registration, login, and JWT token management.
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..db.models import User
from ..db.connection import get_db_context
import logging

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for user."""
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def register_user(email: str, password: str, name: str = None) -> Tuple[Optional[User], Optional[str]]:
    """
    Register a new user.
    Returns: (user, error_message)
    """
    try:
        with get_db_context() as db:
            # Check if user exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return None, "Email already registered"

            # Create new user
            user = User(
                email=email,
                name=name or email.split("@")[0],
                password_hash=hash_password(password),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"✅ User registered: {email}")
            return user, None

    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        return None, str(e)


def login_user(email: str, password: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Login user and return JWT token.
    Returns: (token_data, error_message)
    """
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                return None, "Invalid email or password"

            if not verify_password(password, user.password_hash):
                return None, "Invalid email or password"

            if not user.is_active:
                return None, "Account is inactive"

            # Create JWT token
            token = create_jwt_token(user.id, user.email)

            logger.info(f"✅ User logged in: {email}")
            return {
                "token": token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name
                }
            }, None

    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return None, str(e)


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    try:
        with get_db_context() as db:
            return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    try:
        with get_db_context() as db:
            return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return None


def create_oauth_user(email: str, name: str, oauth_provider: str, oauth_id: str) -> Tuple[Optional[User], Optional[str]]:
    """Create or get OAuth user."""
    try:
        with get_db_context() as db:
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()

            if user:
                # Update OAuth info if not already set
                if not user.oauth_provider:
                    user.oauth_provider = oauth_provider
                    user.oauth_id = oauth_id
                    db.commit()
                return user, None

            # Create new OAuth user
            user = User(
                email=email,
                name=name,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"✅ OAuth user created: {email} ({oauth_provider})")
            return user, None

    except Exception as e:
        logger.error(f"❌ OAuth user creation error: {e}")
        return None, str(e)
