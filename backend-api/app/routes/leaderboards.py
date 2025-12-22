from flask import Blueprint, jsonify
from ..utils.db import db
from ..utils.utils import L, get_achievement_points
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from datetime import datetime
from .achievements import UserAchievement, Achievement
from .social import UserTeam
from .games import Participation
from .games import Competition

leaderboards_bp = Blueprint('leaderboards_bp', __name__)
# ---------- MODELS ----------
class ManualLeaderboard(db.Model):
    __tablename__ = 'manual_leaderboard'  # legacy entries without board
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ManualLeaderboardEntry(db.Model):
    __tablename__ = 'manual_leaderboard_entries'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    board = db.Column(db.String(50), nullable=False, default='global')  # global|team|monthly|hall_of_fame
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- HELPERS ----------
def _uid_or_anon() -> str:
    try:
        # Allow missing token without raising
        verify_jwt_in_request(optional=True)
        user = get_jwt_identity()
    except Exception:
        user = None
    return user if user else 'anonymous'


def _calculate_user_achievement_points(user_id: str) -> int:
    """Calculate total achievement points for a user based on rarity (prevent duplicates)"""
    unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
    total_points = 0
    seen_achievements = set()  # Track seen achievement IDs to prevent duplicates
    for ua in unlocked:
        achievement = Achievement.query.get(ua.achievement_id)
        if achievement and achievement.id not in seen_achievements:
            seen_achievements.add(achievement.id)
            total_points += get_achievement_points(achievement.rarity)
    return total_points


# ---------- ROUTES ----------
@leaderboards_bp.get("/global")
# GET http://127.0.0.1:5001/leaderboards/global
# Body: None
# Example cURL:
# curl -X GET http://127.0.0.1:5001/leaderboards/global
def leaderboard_global():
    # Get all users who have achievements or manual entries
    from ..models.models import User
    from .games import Participation
    
    # Get all users from the system
    all_users = set()
    
    # Add users from manual entries
    legacy = ManualLeaderboard.query.all()
    entries = ManualLeaderboardEntry.query.filter_by(board='global').all()
    for m in legacy:
        all_users.add(m.user)
    for e in entries:
        all_users.add(e.user)
    
    # Add users from achievements
    achievement_users = db.session.query(UserAchievement.user_id).distinct().all()
    for (user_id,) in achievement_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Add users from games/participations
    game_users = db.session.query(Participation.user_id).distinct().all()
    for (user_id,) in game_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Calculate total points for each user
    leaderboard_data = []
    for user in all_users:
        # Achievement points and get achievement details (prevent duplicates)
        unlocked_achievements = UserAchievement.query.filter_by(user_id=user).all()
        achievement_points = 0
        achievement_details = []
        seen_achievements = set()  # Track seen achievement IDs to prevent duplicates
        for ua in unlocked_achievements:
            achievement = Achievement.query.get(ua.achievement_id)
            if achievement and achievement.id not in seen_achievements:
                seen_achievements.add(achievement.id)
                points = get_achievement_points(achievement.rarity)
                achievement_points += points
                achievement_details.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "points": points,
                    "rarity": achievement.rarity
                })
        
        # Game points (from participations)
        participation_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
        from ..models.models import User
        
        # Manual leaderboard points
        manual_points = 0
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='global').first()
        if manual_entry:
            manual_points = manual_entry.points
        
        # Banked points from permanent account
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        
        # Combined game points (participation + manual + banked)
        # Banked points
        from ..models.models import User
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        combined_game_points = int(participation_points) + manual_points + banked_points + banked_points
        
        # Calculate spent points from redemptions
        from .rewards import Redemption
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
        spent_points = int(spent)
        
        # Total points (achievement + game - spent)
        total_points = achievement_points + combined_game_points - spent_points
        
        
        # Create a unique ID for each user entry (use user name as ID for removal)
        user_id = f"user_{user.replace(' ', '_')}"
        
        leaderboard_data.append({
            "user": user,
            "achievements": achievement_details,
            "points": total_points,  # Just show total points
            "id": user_id  # Always provide an ID for removal
        })
    
    # Sort by total points descending
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    L.log("Fetched global leaderboard with achievement points")
    return jsonify({"leaderboard": leaderboard_data}), 200


@leaderboards_bp.get("/team")
# GET http://127.0.0.1:5001/leaderboards/team
# Headers: (optional) Authorization: Bearer <jwt_token>
# Body: None
# Example cURL:
# curl -X GET http://127.0.0.1:5001/leaderboards/team -H "Authorization: Bearer <jwt_token>"
@jwt_required(optional=True)
def leaderboard_team():
    from routes.games import Participation
    
    # Only get users who belong to teams
    team_users = db.session.query(UserTeam.user_id).distinct().all()
    all_users = {user_id for (user_id,) in team_users}
    
    # Calculate total points for each team user
    leaderboard_data = []
    for user in all_users:
        # Achievement points and get achievement details (prevent duplicates)
        unlocked_achievements = UserAchievement.query.filter_by(user_id=user).all()
        achievement_points = 0
        achievement_details = []
        seen_achievements = set()  # Track seen achievement IDs to prevent duplicates
        for ua in unlocked_achievements:
            achievement = Achievement.query.get(ua.achievement_id)
            if achievement and achievement.id not in seen_achievements:
                seen_achievements.add(achievement.id)
                points = get_achievement_points(achievement.rarity)
                achievement_points += points
                achievement_details.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "points": points,
                    "rarity": achievement.rarity
                })
        
        # Game points (from participations)
        participation_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
        from ..models.models import User
        
        # Manual team points
        manual_points = 0
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='team').first()
        if manual_entry:
            manual_points = manual_entry.points
        
        # Combined game points (participation + manual)
        # Banked points
        from ..models.models import User
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        combined_game_points = int(participation_points) + manual_points + banked_points
        
        # Calculate spent points from redemptions
        from .rewards import Redemption
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
        spent_points = int(spent)
        
        # Total points (achievement + game - spent)
        total_points = achievement_points + combined_game_points - spent_points
        
        # Get team name for this user
        user_team = UserTeam.query.filter_by(user_id=user).first()
        team_name = user_team.team_name if user_team else "No Team"
        
        # Create a unique ID for each user entry (use user name as ID for removal)
        user_id = f"user_{user.replace(' ', '_')}"
        
        leaderboard_data.append({
            "user": user,
            "team_name": team_name,
            "achievements": achievement_details,
            "points": total_points,  # Just show total points
            "id": user_id  # Always provide an ID for removal
        })
    
    # Sort by total points descending
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    L.log("Fetched team leaderboard with achievement points (team members only)")
    return jsonify({"leaderboard": leaderboard_data}), 200


@leaderboards_bp.get("/monthly")
# GET http://127.0.0.1:5001/leaderboards/monthly
# Body: None
# Example cURL:
# curl -X GET http://127.0.0.1:5001/leaderboards/monthly
def leaderboard_monthly():
    from routes.games import Participation
    
    # Get all users who have monthly entries or achievements
    all_users = set()
    
    # Add users from monthly entries
    entries = ManualLeaderboardEntry.query.filter_by(board='monthly').all()
    for e in entries:
        all_users.add(e.user)
    
    # Add users from achievements
    achievement_users = db.session.query(UserAchievement.user_id).distinct().all()
    for (user_id,) in achievement_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Add users from games/participations
    game_users = db.session.query(Participation.user_id).distinct().all()
    for (user_id,) in game_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Calculate total points for each user
    leaderboard_data = []
    for user in all_users:
        # Achievement points and get achievement details (prevent duplicates)
        unlocked_achievements = UserAchievement.query.filter_by(user_id=user).all()
        achievement_points = 0
        achievement_details = []
        seen_achievements = set()  # Track seen achievement IDs to prevent duplicates
        for ua in unlocked_achievements:
            achievement = Achievement.query.get(ua.achievement_id)
            if achievement and achievement.id not in seen_achievements:
                seen_achievements.add(achievement.id)
                points = get_achievement_points(achievement.rarity)
                achievement_points += points
                achievement_details.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "points": points,
                    "rarity": achievement.rarity
                })
        
        # Game points (from participations)
        participation_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
        from ..models.models import User
        
        # Manual monthly points
        manual_points = 0
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='monthly').first()
        if manual_entry:
            manual_points = manual_entry.points
        
        # Combined game points (participation + manual)
        # Banked points
        from ..models.models import User
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        combined_game_points = int(participation_points) + manual_points + banked_points
        
        # Calculate spent points from redemptions
        from .rewards import Redemption
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
        spent_points = int(spent)
        
        # Total points (achievement + game - spent)
        total_points = achievement_points + combined_game_points - spent_points
        
        leaderboard_data.append({
            "user": user,
            "achievements": achievement_details,
            "points": total_points,  # Just show total points
            "id": f"user_{user.replace(' ', '_')}"  # Always provide an ID for removal
        })
    
    # Sort by points descending
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    L.log("Fetched monthly leaderboard with achievement points")
    return jsonify({"leaderboard": leaderboard_data}), 200


@leaderboards_bp.get("/hall-of-fame")
# GET http://127.0.0.1:5001/leaderboards/hall-of-fame
# Body: None
# Example cURL:
# curl -X GET http://127.0.0.1:5001/leaderboards/hall-of-fame
def leaderboard_hall_of_fame():
    from routes.games import Participation
    
    # Get all users who have hall of fame entries or achievements
    all_users = set()
    
    # Add users from hall of fame entries
    entries = ManualLeaderboardEntry.query.filter_by(board='hall_of_fame').all()
    for e in entries:
        all_users.add(e.user)
    
    # Add users from achievements
    achievement_users = db.session.query(UserAchievement.user_id).distinct().all()
    for (user_id,) in achievement_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Add users from games/participations
    game_users = db.session.query(Participation.user_id).distinct().all()
    for (user_id,) in game_users:
        all_users.add(user_id)
    
    # Add all registered users
    for u in User.query.all():
        all_users.add(u.username)
    
    # Calculate total points for each user
    leaderboard_data = []
    for user in all_users:
        # Achievement points and get achievement details (prevent duplicates)
        unlocked_achievements = UserAchievement.query.filter_by(user_id=user).all()
        achievement_points = 0
        achievement_details = []
        seen_achievements = set()  # Track seen achievement IDs to prevent duplicates
        for ua in unlocked_achievements:
            achievement = Achievement.query.get(ua.achievement_id)
            if achievement and achievement.id not in seen_achievements:
                seen_achievements.add(achievement.id)
                points = get_achievement_points(achievement.rarity)
                achievement_points += points
                achievement_details.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "points": points,
                    "rarity": achievement.rarity
                })
        
        # Game points (from participations)
        participation_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
        from ..models.models import User
        
        # Manual hall of fame points
        manual_points = 0
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='hall_of_fame').first()
        if manual_entry:
            manual_points = manual_entry.points
        
        # Combined game points (participation + manual)
        # Banked points
        from ..models.models import User
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        combined_game_points = int(participation_points) + manual_points + banked_points
        
        # Calculate spent points from redemptions
        from routes.rewards import Redemption
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
        spent_points = int(spent)
        
        # Total points (achievement + game - spent)
        total_points = achievement_points + combined_game_points - spent_points
        
        leaderboard_data.append({
            "user": user,
            "achievements": achievement_details,
            "points": total_points,  # Just show total points
            "id": f"user_{user.replace(' ', '_')}"  # Always provide an ID for removal
        })
    
    # Sort by points descending
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    L.log("Fetched hall of fame with achievement points")
    return jsonify({"hall_of_fame": leaderboard_data}), 200


@leaderboards_bp.post("/predictions")
# POST http://127.0.0.1:5001/leaderboards/predictions
# Headers: Content-Type: application/json
# Body:
# {
#   "prediction": "Alice will win the Code Quality Challenge"
# }
# Example cURL:
# curl -X POST http://127.0.0.1:5001/leaderboards/predictions \
#   -H "Content-Type: application/json" \
#   -d '{"prediction": "Alice will win the Code Quality Challenge"}'
def leaderboard_predictions():
    body = request.get_json(force=True)
    prediction = body.get("prediction", "No prediction provided")
    uid = _uid_or_anon()
    
    # Store prediction in database
    pred_entry = Prediction(user_id=uid, prediction=prediction)
    db.session.add(pred_entry)
    db.session.commit()
    
    L.log(f"Prediction submitted by {uid}: {prediction}")
    return jsonify({"message": "Prediction received", "prediction": prediction}), 200


@leaderboards_bp.get("/predictions")
# GET http://127.0.0.1:5001/leaderboards/predictions
def leaderboard_predictions_view():
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(20).all()
    data = []
    for pred in predictions:
        data.append({
            "id": pred.id,
            "user": pred.user_id,
            "prediction": pred.prediction,
            "created_at": pred.created_at.isoformat() if pred.created_at else None
        })
    L.log("Fetched predictions")
    return jsonify({"predictions": data}), 200


@leaderboards_bp.delete("/predictions/remove")
# DELETE http://127.0.0.1:5001/leaderboards/predictions/remove {"id": 1}
@jwt_required(optional=True)
def leaderboard_predictions_remove():
    data = request.get_json(silent=True) or {}
    prediction_id = data.get('id')
    
    if not prediction_id:
        return jsonify({'error': 'id is required'}), 400
    
    prediction = Prediction.query.get(prediction_id)
    if not prediction:
        return jsonify({'error': 'prediction not found'}), 404
    
    db.session.delete(prediction)
    db.session.commit()
    
    L.log(f"Removed prediction {prediction_id}")
    return jsonify({'message': 'prediction removed'}), 200


@leaderboards_bp.post("/add")
# POST http://127.0.0.1:5001/leaderboards/add {"user":"dave","points":450, "board":"global"}
@jwt_required(optional=True)
def leaderboard_add():
    body = request.get_json(silent=True) or {}
    user = body.get("user")
    points = body.get("points")
    board = (body.get("board") or 'global').lower().replace('-', '_')
    if board not in {"global", "team", "monthly", "hall_of_fame"}:
        return jsonify({"error": "board must be one of global|team|monthly|hall_of_fame"}), 400
    if not user or points is None:
        return jsonify({"error": "user and points are required"}), 400
    try:
        points = int(points)
    except Exception:
        return jsonify({"error": "points must be integer"}), 400
    
    # Check if user already has an entry for this board
    existing_entry = ManualLeaderboardEntry.query.filter_by(user=user, board=board).first()
    if existing_entry:
        # Update existing entry
        existing_entry.points = points
        db.session.commit()
        L.log(f"Manual leaderboard update: [{board}] {user} -> {points}")
        return jsonify({"message": "updated", "board": board, "user": user, "points": points}), 200
    else:
        # Create new entry
        row = ManualLeaderboardEntry(user=user, points=points, board=board)
        db.session.add(row)
        db.session.commit()
        L.log(f"Manual leaderboard add: [{board}] {user} -> {points}")
        return jsonify({"message": "added", "board": board, "user": user, "points": points}), 201


@leaderboards_bp.delete("/remove")
# DELETE http://127.0.0.1:5001/leaderboards/remove {"id": "user_max1"}
@jwt_required(optional=True)
def leaderboard_remove():
    body = request.get_json(silent=True) or {}
    entry_id = body.get("id")
    if not entry_id:
        return jsonify({"error": "id is required"}), 400
    
    # Handle user removal (format: "user_username")
    if entry_id.startswith("user_"):
        username = entry_id.replace("user_", "").replace("_", " ")
        
        L.log(f"Removing user {username} from leaderboards and banking competition points.")
        
        # Bank points from participations before removing them
        from classes.user import User
        from routes.games import Participation
        participations = Participation.query.filter_by(user_id=username).all()
        user_obj = User.query.filter_by(username=username).first()
        
        if user_obj:
            for p in participations:
                if (p.progress or 0) > 0:
                    user_obj.banked_points += int(p.progress)
                    L.log(f"Banking {p.progress} points for user {username} during user removal.")
            db.session.add(user_obj)
        
        # Remove participations and manual entries
        Participation.query.filter_by(user_id=username).delete()
        ManualLeaderboardEntry.query.filter_by(user=username).delete()
        ManualLeaderboard.query.filter_by(user=username).delete()
        db.session.commit()
        
        return jsonify({"message": f"User {username} removed from manual leaderboards.", "id": entry_id}), 200
    
    # Handle legacy manual entry removal (integer ID)
    try:
        entry_id = int(entry_id)
        entry = ManualLeaderboardEntry.query.get(entry_id)
        if not entry:
            return jsonify({"error": "entry not found"}), 404
        
        db.session.delete(entry)
        db.session.commit()
        L.log(f"Manual leaderboard remove: [{entry.board}] {entry.user} -> {entry.points}")
        return jsonify({"message": "removed", "board": entry.board, "user": entry.user, "points": entry.points}), 200
    except Exception:
        return jsonify({"error": "invalid id format"}), 400




# --- Models ---
class Prediction(db.Model):
    __tablename__ = 'leaderboard_predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    prediction = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
