"""
Authentication API routes.
Handles user registration, login, and token management.
"""

from flask import Blueprint, request, jsonify
from backend_setup.services.auth_service import (
    register_user, login_user, verify_jwt_token, get_user_by_id
)
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "name": "John Doe"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()

        # Validation
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        if '@' not in email:
            return jsonify({"error": "Invalid email format"}), 400

        # Register user
        user, error = register_user(email, password, name)

        if error:
            return jsonify({"error": error}), 400

        # Generate token
        from backend_setup.services.auth_service import create_jwt_token
        token = create_jwt_token(user.id, user.email)

        return jsonify({
            "token": token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Login user
        result, error = login_user(email, password)

        if error:
            return jsonify({"error": error}), 401

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current user from JWT token.
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.replace('Bearer ', '')

        # Verify token
        payload = verify_jwt_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get user
        user = get_user_by_id(payload['user_id'])

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({"error": "Failed to get user"}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh JWT token.
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.replace('Bearer ', '')

        # Verify token
        payload = verify_jwt_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get user
        user = get_user_by_id(payload['user_id'])

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create new token
        from backend_setup.services.auth_service import create_jwt_token
        new_token = create_jwt_token(user.id, user.email)

        return jsonify({
            "token": new_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500
