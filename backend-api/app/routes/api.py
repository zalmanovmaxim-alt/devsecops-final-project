
from flask import Blueprint, jsonify, request, render_template
from ..utils.db import db
from ..utils.utils import get_achievement_points
from ..models.models import User
from .games import Competition, Participation, Game, UserCompetition
from .achievements import Achievement, UserAchievement
from .rewards import Redemption
from collections import defaultdict

api_bp = Blueprint('api_bp', __name__)

# =============================================================================
# ITEMS CRUD (REQUIRED FOR PRESENTATION)
# =============================================================================

# Temporary in-memory items store for the demonstration CRUD
# In a real app, this would be a Postgres table.
items_db = [
    {"id": 1, "name": "Standard Laptop", "category": "Hardware", "price": 1200},
    {"id": 2, "name": "Ergonomic Chair", "category": "Furniture", "price": 350}
]

@api_bp.route("/items", methods=["GET"])
def list_items():
    return jsonify(items_db), 200

@api_bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json() or {}
    new_item = {
        "id": len(items_db) + 1,
        "name": data.get("name", "New Item"),
        "category": data.get("category", "General"),
        "price": data.get("price", 0)
    }
    items_db.append(new_item)
    return jsonify(new_item), 201

@api_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((i for i in items_db if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200

@api_bp.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = next((i for i in items_db if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json() or {}
    item.update({
        "name": data.get("name", item["name"]),
        "category": data.get("category", item["category"]),
        "price": data.get("price", item["price"])
    })
    return jsonify(item), 200

@api_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global items_db
    items_db = [i for i in items_db if i["id"] != item_id]
    return jsonify({"message": "Item deleted"}), 200

# =============================================================================
# LEGACY MAIN ROUTES (MIGRATED)
# =============================================================================

@api_bp.route("/players_grouped")
def api_players_grouped():
    """Aggregated dashboard data for all players across all activities."""
    all_users = set()
    
    # Collect users from all relevant sources
    games_users = db.session.query(Participation.user_id).distinct().all()
    for (uid,) in games_users: all_users.add(uid)
    
    competitions_users = db.session.query(UserCompetition.user_id).distinct().all()
    for (uid,) in competitions_users: all_users.add(uid)
    
    achievement_users = db.session.query(UserAchievement.user_id).distinct().all()
    for (uid,) in achievement_users: all_users.add(uid)
    
    for u in User.query.all(): all_users.add(u.username)
    
    # Data aggregation
    grouped = defaultdict(lambda: {"competitions": [], "total_progress": 0, "achievement_points": 0, "spent_points": 0, "manual_points": 0, "banked_points": 0})
    
    # 1. Game progress
    games_participations = db.session.query(Participation.user_id, Competition.title, Participation.progress).join(Competition, Competition.id == Participation.competition_id).all()
    for uid, title, progress in games_participations:
        grouped[uid]["competitions"].append(title)
        grouped[uid]["total_progress"] += int(progress or 0)
        
    # 2. Basic competitions
    comp_members = db.session.query(UserCompetition.user_id, Competition.title).join(Competition, Competition.id == UserCompetition.competition_id).all()
    for uid, title in comp_members:
        grouped[uid]["competitions"].append(title)
        
    # 3. User details (Achievement, Banked, Spent)
    for username in all_users:
        # Banked
        u_obj = User.query.filter_by(username=username).first()
        if u_obj:
            grouped[username]["banked_points"] = u_obj.banked_points
            
        # Achievements
        unlocked = UserAchievement.query.filter_by(user_id=username).all()
        for ua in unlocked:
            ach = Achievement.query.get(ua.achievement_id)
            if ach: grouped[username]["achievement_points"] += get_achievement_points(ach.rarity)
            
        # Spent
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=username).scalar() or 0
        grouped[username]["spent_points"] = int(spent)

    # Final mapping
    players_grouped = [
        {
            "username": uname,
            "competitions": sorted(list(set(data["competitions"]))),
            "total_progress": data["total_progress"],
            "achievement_points": data["achievement_points"],
            "spent_points": data["spent_points"],
            "total_points": max(0, data["total_progress"] + data["achievement_points"] + data["banked_points"] - data["spent_points"]),
        }
        for uname, data in grouped.items()
    ]
    
    return jsonify(players_grouped), 200

@api_bp.route("/")
def homepage():
    # Redirect to legacy root if needed or show simple status
    return jsonify({"message": "API Root", "docs": "/health"}), 200

