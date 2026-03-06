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


@analytics_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get comprehensive metrics for analytics page."""
    try:
        user, error_response, status_code = get_auth_user()
        if error_response:
            return error_response, status_code

        range_type = request.args.get('range', '7d')
        days = 7
        if range_type == '30d':
            days = 30
        elif range_type == '90d':
            days = 90
        elif range_type == '1y':
            days = 365

        start_date = datetime.utcnow() - timedelta(days=days)

        with get_db_context() as db:
            clients = db.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).all()

            client_ids = [c.id for c in clients]

            if not client_ids:
                return jsonify({
                    "total_calls": 0,
                    "completed_calls": 0,
                    "missed_calls": 0,
                    "average_duration": 0,
                    "success_rate": 0,
                    "total_revenue": 0,
                    "sentiment_positive": 0,
                    "sentiment_neutral": 0,
                    "sentiment_negative": 0,
                    "calls_by_day": [],
                    "revenue_by_day": []
                }), 200

            # Aggregated stats
            stats = db.query(
                func.count(Call.id).label('total_calls'),
                func.sum(case([(Call.success == True, 1)], else_=0)).label('completed_calls'),
                func.sum(Call.duration_seconds).label('total_duration')
            ).filter(
                Call.client_id.in_(client_ids),
                Call.created_at >= start_date
            ).first()

            total_calls = stats.total_calls or 0
            completed_calls = stats.completed_calls or 0
            total_duration = stats.total_duration or 0
            missed_calls = total_calls - completed_calls
            average_duration = (total_duration / total_calls) if total_calls > 0 else 0
            success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0

            # Sentiment distribution
            sentiment_stats = db.query(
                Call.sentiment,
                func.count(Call.id).label('count')
            ).filter(
                Call.client_id.in_(client_ids),
                Call.created_at >= start_date
            ).group_by(Call.sentiment).all()

            sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
            for s, count in sentiment_stats:
                if s and s.upper() in sentiment_counts:
                    sentiment_counts[s.upper()] += count
                else:
                    sentiment_counts["NEUTRAL"] += count

            sentiment_positive = (sentiment_counts["POSITIVE"] / total_calls * 100) if total_calls > 0 else 0
            sentiment_neutral = (sentiment_counts["NEUTRAL"] / total_calls * 100) if total_calls > 0 else 0
            sentiment_negative = (sentiment_counts["NEGATIVE"] / total_calls * 100) if total_calls > 0 else 0

            # Calls by day
            calls_by_day_query = db.query(
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

            calls_by_day = [
                {"date": str(row.date), "calls": row.count}
                for row in calls_by_day_query
            ]

            # Mock revenue for now as it's not in the model
            # $10 per completed call
            total_revenue = completed_calls * 10
            revenue_by_day = [
                {"date": row["date"], "revenue": row["calls"] * 10}
                for row in calls_by_day
            ]

            return jsonify({
                "total_calls": total_calls,
                "completed_calls": completed_calls,
                "missed_calls": missed_calls,
                "average_duration": round(average_duration, 1),
                "success_rate": round(success_rate, 1),
                "total_revenue": total_revenue,
                "sentiment_positive": round(sentiment_positive, 1),
                "sentiment_neutral": round(sentiment_neutral, 1),
                "sentiment_negative": round(sentiment_negative, 1),
                "calls_by_day": calls_by_day,
                "revenue_by_day": revenue_by_day
            }), 200

    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        return jsonify({"error": "Failed to get metrics"}), 500


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

            # Get call statistics
            calls = db.query(Call).filter(Call.client_id.in_(client_ids)).all()

            total_calls = len(calls)
            total_duration = sum(c.duration_seconds or 0 for c in calls)
            successful_calls = sum(1 for c in calls if c.success)
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

            # Calculate average sentiment
            sentiments = [c.sentiment for c in calls if c.sentiment]
            avg_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "NEUTRAL"

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
