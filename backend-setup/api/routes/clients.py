"""
Client management API routes.
Handles CRUD operations for clients (businesses).
"""

from flask import Blueprint, request, jsonify
from backend_setup.services.auth_service import verify_jwt_token, get_user_by_id
from backend_setup.db.connection import get_db_context
from backend_setup.db.models import Client
import logging
import uuid

logger = logging.getLogger(__name__)

clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')


def get_auth_user():
    """Extract and verify user from JWT token."""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return None, jsonify({"error": "Missing authorization header"}), 401

    token = auth_header.replace('Bearer ', '')
    payload = verify_jwt_token(token)

    if not payload:
        return None, jsonify({"error": "Invalid or expired token"}), 401

    user = get_user_by_id(payload['user_id'])

    if not user:
        return None, jsonify({"error": "User not found"}), 404

    return user, None, None


@clients_bp.route('', methods=['GET'])
def list_clients():
    """Get all clients for the current user."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            clients = db.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).all()

            return jsonify({
                "clients": [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "phone_number": c.phone_number,
                        "profession": c.profession,
                        "voice_name": c.voice_name,
                        "created_at": c.created_at.isoformat()
                    }
                    for c in clients
                ]
            }), 200

    except Exception as e:
        logger.error(f"List clients error: {e}")
        return jsonify({"error": "Failed to list clients"}), 500


@clients_bp.route('', methods=['POST'])
def create_client():
    """Create a new client."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        name = data.get('name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        profession = data.get('profession', '').strip()
        voice_name = data.get('voice_name', 'af_sarah')

        if not name or not phone_number:
            return jsonify({"error": "Name and phone number required"}), 400

        with get_db_context() as db:
            # Check if phone number already exists
            existing = db.query(Client).filter(
                Client.phone_number == phone_number
            ).first()

            if existing:
                return jsonify({"error": "Phone number already in use"}), 400

            # Create client
            client = Client(
                user_id=user.id,
                name=name,
                phone_number=phone_number,
                profession=profession,
                voice_name=voice_name,
                is_active=True
            )
            db.add(client)
            db.commit()
            db.refresh(client)

            logger.info(f"✅ Client created: {name} ({phone_number})")

            return jsonify({
                "client": {
                    "id": str(client.id),
                    "name": client.name,
                    "phone_number": client.phone_number,
                    "profession": client.profession,
                    "voice_name": client.voice_name,
                    "created_at": client.created_at.isoformat()
                }
            }), 201

    except Exception as e:
        logger.error(f"Create client error: {e}")
        return jsonify({"error": "Failed to create client"}), 500


@clients_bp.route('/<client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            client = db.query(Client).filter(
                Client.id == client_id,
                Client.user_id == user.id
            ).first()

            if not client:
                return jsonify({"error": "Client not found"}), 404

            return jsonify({
                "client": {
                    "id": str(client.id),
                    "name": client.name,
                    "phone_number": client.phone_number,
                    "profession": client.profession,
                    "voice_name": client.voice_name,
                    "created_at": client.created_at.isoformat()
                }
            }), 200

    except Exception as e:
        logger.error(f"Get client error: {e}")
        return jsonify({"error": "Failed to get client"}), 500


@clients_bp.route('/<client_id>', methods=['PUT'])
def update_client(client_id):
    """Update a client."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        with get_db_context() as db:
            client = db.query(Client).filter(
                Client.id == client_id,
                Client.user_id == user.id
            ).first()

            if not client:
                return jsonify({"error": "Client not found"}), 404

            # Update fields
            if 'name' in data:
                client.name = data['name'].strip()
            if 'profession' in data:
                client.profession = data['profession'].strip()
            if 'voice_name' in data:
                client.voice_name = data['voice_name'].strip()

            db.commit()
            db.refresh(client)

            logger.info(f"✅ Client updated: {client.name}")

            return jsonify({
                "client": {
                    "id": str(client.id),
                    "name": client.name,
                    "phone_number": client.phone_number,
                    "profession": client.profession,
                    "voice_name": client.voice_name,
                    "created_at": client.created_at.isoformat()
                }
            }), 200

    except Exception as e:
        logger.error(f"Update client error: {e}")
        return jsonify({"error": "Failed to update client"}), 500


@clients_bp.route('/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client (soft delete)."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            client = db.query(Client).filter(
                Client.id == client_id,
                Client.user_id == user.id
            ).first()

            if not client:
                return jsonify({"error": "Client not found"}), 404

            # Soft delete
            client.is_active = False
            db.commit()

            logger.info(f"✅ Client deleted: {client.name}")

            return jsonify({"message": "Client deleted"}), 200

    except Exception as e:
        logger.error(f"Delete client error: {e}")
        return jsonify({"error": "Failed to delete client"}), 500
