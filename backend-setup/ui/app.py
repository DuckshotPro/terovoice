"""
Flask dashboard for multi-tenant AI receptionist service.
Real-time analytics, call logs, revenue tracking.
"""
import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from functools import wraps

from analytics.db import get_client_stats, get_recent_calls
from agent.router import ClientRouter
from config.settings import settings

logger = logging.getLogger("dashboard")

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.flask_secret_key
socketio = SocketIO(app, cors_allowed_origins="*")

router = ClientRouter(settings.clients_db_path)


def require_api_key(f):
    """Decorator to require API key for endpoints."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != os.getenv("DASHBOARD_API_KEY", ""):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/client/<client_name>/stats")
@require_api_key
def get_stats(client_name):
    """Get stats for a specific client."""
    stats = get_client_stats(client_name)
    return jsonify(stats)


@app.route("/api/client/<client_name>/calls")
@require_api_key
def get_calls(client_name):
    """Get recent calls for a client."""
    limit = request.args.get("limit", 50, type=int)
    calls = get_recent_calls(client_name, limit)
    return jsonify(calls)


@app.route("/api/clients")
@require_api_key
def list_clients():
    """List all clients (admin only)."""
    clients = router.get_all_clients()
    return jsonify(clients)


@app.route("/api/client", methods=["POST"])
@require_api_key
def create_client():
    """Create new client."""
    data = request.json

    success = router.add_client(
        name=data.get("name"),
        phone_numbers=data.get("phone_numbers", []),
        profession=data.get("profession", "dentist"),
        voice_id=data.get("voice_id", "default"),
        dashboard_url=data.get("dashboard_url", ""),
    )

    if success:
        return jsonify({"status": "success", "message": "Client created"}), 201
    else:
        return jsonify({"status": "error", "message": "Failed to create client"}), 400


@socketio.on("connect")
def handle_connect():
    """Handle WebSocket connection."""
    emit("status", {"message": "Connected to dashboard"})
    logger.info("Client connected to dashboard")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info("Client disconnected from dashboard")


@socketio.on("request_stats")
def handle_stats_request(data):
    """Handle real-time stats request."""
    client_name = data.get("client_name")
    if not client_name:
        return

    stats = get_client_stats(client_name)
    emit("stats_update", stats)


@socketio.on("request_calls")
def handle_calls_request(data):
    """Handle real-time calls request."""
    client_name = data.get("client_name")
    if not client_name:
        return

    calls = get_recent_calls(client_name, limit=10)
    emit("calls_update", calls)


if __name__ == "__main__":
    logger.info(f"Starting dashboard on port {settings.flask_port}")
    socketio.run(app, host="0.0.0.0", port=settings.flask_port, debug=False)
