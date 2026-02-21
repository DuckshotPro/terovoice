"""
Analytics API routes.
Provides dashboard stats, trends, and revenue data.
"""

from flask import Blueprint, request, jsonify
from backend_setup.services.auth_service import verify_jwt_token, get_user_by_id
from backend_setup.db.connection import get_db_context
from backend_setup.db.models import Call, Client, Subscription
from datetime import datetime, timedelta
from sqlalchemy import func, case
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


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


@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            # Get user's clients
            clients = db.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).all()

            client_ids = [c.id for c in clients]

            if not client_ids:
                return jsonify({
                    "total_calls": 0,
                    "total_duration": 0,
                    "success_rate": 0,
                    "avg_sentiment": "NEUTRAL",
                    "total_clients": 0
                }), 200

            # Get call statistics with aggregation
            stats = db.query(
                func.count(Call.id).label('total_calls'),
                func.sum(Call.duration_seconds).label('total_duration'),
                func.sum(case((Call.success == True, 1), else_=0)).label('successful_calls')
            ).filter(Call.client_id.in_(client_ids)).first()

            total_calls = stats.total_calls or 0
            total_duration = stats.total_duration or 0
            successful_calls = stats.successful_calls or 0
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

            # Calculate average sentiment
            most_frequent_sentiment = db.query(
                Call.sentiment,
                func.count(Call.sentiment).label('count')
            ).filter(
                Call.client_id.in_(client_ids),
                Call.sentiment != None
            ).group_by(
                Call.sentiment
            ).order_by(
                func.count(Call.sentiment).desc()
            ).first()

            avg_sentiment = most_frequent_sentiment.sentiment if most_frequent_sentiment else "NEUTRAL"

            return jsonify({
                "total_calls": total_calls,
                "total_duration": round(total_duration, 2),
                "success_rate": round(success_rate, 1),
                "avg_sentiment": avg_sentiment,
                "total_clients": len(clients)
            }), 200

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({"error": "Failed to get dashboard stats"}), 500


@analytics_bp.route('/calls-per-day', methods=['GET'])
def calls_per_day():
    """Get calls per day trend."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        days = request.args.get('days', 30, type=int)

        with get_db_context() as db:
            clients = db.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).all()

            client_ids = [c.id for c in clients]

            if not client_ids:
                return jsonify({"data": []}), 200

            # Get calls grouped by day
            start_date = datetime.utcnow() - timedelta(days=days)

            calls_by_day = db.query(
                func.date(Call.created_at).label('date'),
                func.count(Call.id).label('count')
            ).filter(
                Call.client_id.in_(client_ids),
                Call.created_at >= start_date
            ).group_by(
                func.date(Call.created_at)
            ).order_by(
                func.date(Call.created_at)
            ).all()

            return jsonify({
                "data": [
                    {
                        "date": str(row.date),
                        "calls": row.count
                    }
                    for row in calls_by_day
                ]
            }), 200

    except Exception as e:
        logger.error(f"Calls per day error: {e}")
        return jsonify({"error": "Failed to get calls per day"}), 500


@analytics_bp.route('/sentiment', methods=['GET'])
def sentiment_analysis():
    """Get sentiment distribution."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            clients = db.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).all()

            client_ids = [c.id for c in clients]

            if not client_ids:
                return jsonify({
                    "POSITIVE": 0,
                    "NEGATIVE": 0,
                    "NEUTRAL": 0
                }), 200

            # Get sentiment counts
            sentiment_counts = db.query(
                Call.sentiment,
                func.count(Call.id).label('count')
            ).filter(
                Call.client_id.in_(client_ids)
            ).group_by(
                Call.sentiment
            ).all()

            result = {
                "POSITIVE": 0,
                "NEGATIVE": 0,
                "NEUTRAL": 0
            }

            for sentiment, count in sentiment_counts:
                if sentiment in result:
                    result[sentiment] = count

            return jsonify(result), 200

    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return jsonify({"error": "Failed to get sentiment analysis"}), 500


@analytics_bp.route('/client/<client_id>/stats', methods=['GET'])
def client_stats(client_id):
    """Get statistics for a specific client."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        with get_db_context() as db:
            # Verify client belongs to user
            client = db.query(Client).filter(
                Client.id == client_id,
                Client.user_id == user.id
            ).first()

            if not client:
                return jsonify({"error": "Client not found"}), 404

            # Get client's calls
            calls = db.query(Call).filter(Call.client_id == client_id).all()

            total_calls = len(calls)
            total_duration = sum(c.duration_seconds or 0 for c in calls)
            successful_calls = sum(1 for c in calls if c.success)
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

            # Calculate average latencies
            avg_stt_latency = sum(c.stt_latency_ms or 0 for c in calls) / total_calls if total_calls > 0 else 0
            avg_llm_latency = sum(c.llm_latency_ms or 0 for c in calls) / total_calls if total_calls > 0 else 0
            avg_tts_latency = sum(c.tts_latency_ms or 0 for c in calls) / total_calls if total_calls > 0 else 0

            return jsonify({
                "client_id": str(client_id),
                "client_name": client.name,
                "total_calls": total_calls,
                "total_duration": round(total_duration, 2),
                "success_rate": round(success_rate, 1),
                "avg_stt_latency_ms": round(avg_stt_latency, 2),
                "avg_llm_latency_ms": round(avg_llm_latency, 2),
                "avg_tts_latency_ms": round(avg_tts_latency, 2)
            }), 200

    except Exception as e:
        logger.error(f"Client stats error: {e}")
        return jsonify({"error": "Failed to get client stats"}), 500
