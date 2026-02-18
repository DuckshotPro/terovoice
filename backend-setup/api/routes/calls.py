"""
Call logging API routes.
Handles call recording, transcripts, and analytics.
"""

from flask import Blueprint, request, jsonify
from backend_setup.services.auth_service import verify_jwt_token, get_user_by_id
from backend_setup.db.connection import get_db_context
from backend_setup.db.models import Call, Client
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

calls_bp = Blueprint('calls', __name__, url_prefix='/api/calls')


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


@calls_bp.route('', methods=['GET'])
def list_calls():
    """Get all calls for the current user's clients."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        # Query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        client_id = request.args.get('client_id')
        days = request.args.get('days', 30, type=int)

        with get_db_context() as db:
            query = db.query(Call).join(Client).filter(
                Client.user_id == user.id
            )

            # Filter by client if provided
            if client_id:
                query = query.filter(Call.client_id == client_id)

            # Filter by date range
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Call.created_at >= start_date)

            # Get total count
            total = query.count()

            # Get paginated results
            calls = query.order_by(Call.created_at.desc()).limit(limit).offset(offset).all()

            return jsonify({
                "total": total,
                "limit": limit,
                "offset": offset,
                "calls": [
                    {
                        "id": str(c.id),
                        "client_id": str(c.client_id),
                        "caller_phone": c.caller_phone,
                        "caller_name": c.caller_name,
                        "duration_seconds": c.duration_seconds,
                        "sentiment": c.sentiment,
                        "success": c.success,
                        "created_at": c.created_at.isoformat()
                    }
                    for c in calls
                ]
            }), 200

    except Exception as e:
        logger.error(f"List calls error: {e}")
        return jsonify({"error": "Failed to list calls"}), 500


@calls_bp.route('', methods=['POST'])
def log_call():
    """Log a new call (called by Ollama agent)."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        client_id = data.get('client_id')
        caller_phone = data.get('caller_phone')
        caller_name = data.get('caller_name')
        duration_seconds = data.get('duration_seconds', 0)
        stt_latency_ms = data.get('stt_latency_ms', 0)
        llm_latency_ms = data.get('llm_latency_ms', 0)
        tts_latency_ms = data.get('tts_latency_ms', 0)
        transcript = data.get('transcript', '')
        sentiment = data.get('sentiment', 'NEUTRAL')
        success = data.get('success', True)
        recording_url = data.get('recording_url')
        notes = data.get('notes')

        if not client_id:
            return jsonify({"error": "Client ID required"}), 400

        with get_db_context() as db:
            # Verify client exists
            client = db.query(Client).filter(Client.id == client_id).first()

            if not client:
                return jsonify({"error": "Client not found"}), 404

            # Create call record
            call = Call(
                client_id=client_id,
                caller_phone=caller_phone,
                caller_name=caller_name,
                duration_seconds=duration_seconds,
                stt_latency_ms=stt_latency_ms,
                llm_latency_ms=llm_latency_ms,
                tts_latency_ms=tts_latency_ms,
                transcript=transcript,
                sentiment=sentiment,
                success=success,
                recording_url=recording_url,
                notes=notes
            )
            db.add(call)
            db.commit()
            db.refresh(call)

            logger.info(f"✅ Call logged: {caller_phone} -> {client.name}")

            return jsonify({
                "call": {
                    "id": str(call.id),
                    "client_id": str(call.client_id),
                    "created_at": call.created_at.isoformat()
                }
            }), 201

    except Exception as e:
        logger.error(f"Log call error: {e}")
        return jsonify({"error": "Failed to log call"}), 500


@calls_bp.route('/<call_id>', methods=['GET'])
def get_call(call_id):
    """Get a specific call."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            call = db.query(Call).join(Client).filter(
                Call.id == call_id,
                Client.user_id == user.id
            ).first()

            if not call:
                return jsonify({"error": "Call not found"}), 404

            return jsonify({
                "call": {
                    "id": str(call.id),
                    "client_id": str(call.client_id),
                    "caller_phone": call.caller_phone,
                    "caller_name": call.caller_name,
                    "duration_seconds": call.duration_seconds,
                    "stt_latency_ms": call.stt_latency_ms,
                    "llm_latency_ms": call.llm_latency_ms,
                    "tts_latency_ms": call.tts_latency_ms,
                    "transcript": call.transcript,
                    "sentiment": call.sentiment,
                    "success": call.success,
                    "recording_url": call.recording_url,
                    "notes": call.notes,
                    "created_at": call.created_at.isoformat()
                }
            }), 200

    except Exception as e:
        logger.error(f"Get call error: {e}")
        return jsonify({"error": "Failed to get call"}), 500
