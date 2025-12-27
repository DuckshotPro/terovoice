"""
Flask API application for AI Receptionist SaaS.
Main entry point for the backend API.
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Import database
from backend_setup.db.connection import test_connection, init_db

# Initialize database
try:
    init_db()
    if test_connection():
        logger.info("✅ Database initialized and connected")
    else:
        logger.error("❌ Database connection failed")
except Exception as e:
    logger.error(f"❌ Database initialization error: {e}")


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "ai-receptionist-api",
        "version": "1.0.0"
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors."""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    return jsonify({"error": "Forbidden"}), 403


# Import and register blueprints
try:
    from backend_setup.api.routes import auth, clients, calls, analytics
    
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(clients.clients_bp)
    app.register_blueprint(calls.calls_bp)
    app.register_blueprint(analytics.analytics_bp)
    
    logger.info("✅ API routes registered")
except ImportError as e:
    logger.warning(f"⚠️  Some routes not available yet: {e}")


if __name__ == '__main__':
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False") == "True"
    
    logger.info(f"🚀 Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
