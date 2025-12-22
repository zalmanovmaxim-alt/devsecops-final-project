
from flask import Blueprint, jsonify
from ..utils.db import db
import sqlalchemy

health_bp = Blueprint('health_bp', __name__)

@health_bp.route("/", methods=["GET"])
def health():
    """Basic health check"""
    return jsonify({"status": "healthy", "service": "backend-api"}), 200

@health_bp.route("/ready", methods=["GET"])
def readiness():
    """Readiness probe - checks DB connection"""
    try:
        # Try a simple query to check DB connection
        db.session.execute(sqlalchemy.text("SELECT 1"))
        return jsonify({"status": "ready", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "database": "disconnected", "error": str(e)}), 503

@health_bp.route("/live", methods=["GET"])
def liveness():
    """Liveness probe - indicates process is running"""
    return jsonify({"status": "live"}), 200
