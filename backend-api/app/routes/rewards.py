"""
Rewards Route Module
===================

This module handles the rewards system including:
- Reward redemption (spending points for rewards)
- Point donations between users
- Available rewards listing
- Point balance calculations

Key Features:
- Users can redeem rewards using their earned points
- Users can donate points to other users (unique feature)
- Point calculations include achievement points, game progress, manual points, and spent points
- Support for both authenticated and anonymous users
- Points are capped at minimum 0 (no negative balances)

Point Sources:
- Achievement points (based on rarity: common=10, rare=20, epic=40, legendary=80)
- Game progress points (from Participation.progress)
- Manual points (from donations via ManualLeaderboardEntry)
- Spent points (from redemptions via Redemption table)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import db
from datetime import datetime

from .achievements import UserAchievement, Achievement
from ..utils.utils import L, get_achievement_points
from .games import Participation

# Create Flask blueprint for rewards routes
rewards_bp = Blueprint('rewards_bp', __name__)

# =============================================================================
# DATABASE MODELS
# =============================================================================

class Reward(db.Model):
    """
    Reward model representing rewards that users can redeem with points.
    
    Attributes:
        id (int): Primary key, auto-incrementing reward ID
        name (str): Reward name, max 150 characters
        points (int): Point cost to redeem this reward
        created_at (datetime): When the reward was created
    """
    __tablename__ = 'rewards_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        """Convert reward to dictionary for JSON serialization"""
        return {"id": self.id, "name": self.name, "points": self.points}


class Redemption(db.Model):
    """
    Redemption model tracking when users redeem rewards.
    
    This model records all reward redemptions and is used to calculate
    how many points a user has spent.
    
    Attributes:
        id (int): Primary key, auto-incrementing redemption ID
        user_id (str): User identifier (username or 'anonymous')
        reward_id (int): Foreign key to Reward
        points (int): Points spent on this redemption
        created_at (datetime): When the redemption occurred
    """
    __tablename__ = 'rewards_redemptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards_rewards.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _calculate_user_achievement_points(user_id: str) -> int:
    """
    Calculate total achievement points for a user based on rarity.
    
    This function sums up all achievement points earned by a user,
    where points are determined by achievement rarity:
    - Common: 10 points
    - Rare: 20 points  
    - Epic: 40 points
    - Legendary: 80 points
    
    Args:
        user_id (str): User identifier (username or 'anonymous')
        
    Returns:
        int: Total achievement points earned by the user
    """
    unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
    total_points = 0
    for ua in unlocked:
        achievement = Achievement.query.get(ua.achievement_id)
        if achievement:
            total_points += get_achievement_points(achievement.rarity)
    return total_points

# -------------------------------
# Rewards-related Routes
# -------------------------------
@rewards_bp.get("/available")
# GET http://127.0.0.1:5001/rewards/available
def rewards_available():
    """List available rewards (manual only)."""
    rewards = Reward.query.order_by(Reward.points.asc()).all()
    return jsonify({"status": "success", "rewards": [r.serialize() for r in rewards]}), 200


@rewards_bp.route("/redeem", methods=["POST"])
@jwt_required(optional=True)
def rewards_redeem():
    """Redeem points for a reward by id from DB with points check."""
    try:
        data = request.get_json(silent=True) or {}
        reward_id = data.get("reward_id")
        if not reward_id:
            return jsonify({"status": "error", "message": "reward_id is required"}), 400
        
        try:
            reward_id = int(reward_id)
        except Exception:
            return jsonify({"status": "error", "message": "reward_id must be integer"}), 400

        r = Reward.query.get(reward_id)
        if not r:
            return jsonify({"status": "error", "message": "reward not found"}), 404

        user = (get_jwt_identity() or 'anonymous')
        
        # compute available points (same logic as homepage)
        ach_points = _calculate_user_achievement_points(user)
        game_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
        
        # Include manual points from leaderboard donations
        from .leaderboards import ManualLeaderboardEntry
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='global').first()
        manual_points = manual_entry.points if manual_entry else 0
        
        # Include banked points from permanent account
        from ..models.models import User
        user_obj = User.query.filter_by(username=user).first()
        banked_points = user_obj.banked_points if user_obj else 0
        
        available = max(0, int(ach_points) + int(game_points) + int(manual_points) + int(banked_points) - int(spent))
        
        if available < r.points:
            return jsonify({"status": "error", "message": "insufficient points", "available_points": int(available)}), 400

        # record redemption
        red = Redemption(user_id=user, reward_id=r.id, points=r.points)
        db.session.add(red)
        db.session.commit()

        return jsonify({"status": "success", "reward": r.serialize(), "redeemed_by": user, "remaining_points": available - r.points}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500


@rewards_bp.get("/my-points")
# GET http://127.0.0.1:5001/rewards/my-points
@jwt_required(optional=True)
def rewards_my_points():
    """Return computed points: achievements + game progress - redemptions."""
    user = (get_jwt_identity() or 'anonymous')
    ach_points = _calculate_user_achievement_points(user)
    game_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user).scalar() or 0
    spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user).scalar() or 0
    # Include manual points from leaderboard donations
    from .leaderboards import ManualLeaderboardEntry
    manual_entry = ManualLeaderboardEntry.query.filter_by(user=user, board='global').first()
    manual_points = manual_entry.points if manual_entry else 0
    
    # Include banked points from permanent account
    from ..models.models import User
    user_obj = User.query.filter_by(username=user).first()
    banked_points = user_obj.banked_points if user_obj else 0
    
    total = int(ach_points) + int(game_points) + int(manual_points) + int(banked_points)
    available = max(0, total - int(spent))
    return jsonify({
        "achievement_points": int(ach_points),
        "game_points": int(game_points),
        "manual_points": int(manual_points),
        "banked_points": int(banked_points),
        "spent_points": int(spent),
        "available_points": int(available)
    }), 200


@rewards_bp.route("/donate-points", methods=["POST"])
@jwt_required(optional=True)
def rewards_donate_points():
    """Donate points to another user with points validation."""
    try:
        data = request.get_json(silent=True) or {}
        amount = data.get("amount")
        recipient = data.get("recipient")

        if not amount or not recipient:
            return jsonify({"status": "error", "message": "amount and recipient are required"}), 400

        try:
            amount = int(amount)
        except Exception:
            return jsonify({"status": "error", "message": "amount must be integer"}), 400

        donor = (get_jwt_identity() or 'anonymous')
        
        # Check if recipient exists in the system
        from ..models.models import User
        from .leaderboards import ManualLeaderboardEntry
        from .games import Participation, UserCompetition
        from .achievements import UserAchievement
        
        # Check if recipient is a registered user
        recipient_user = User.query.filter_by(username=recipient).first()
        
        # If not registered, check if they have any data in the system
        if not recipient_user:
            has_manual_points = ManualLeaderboardEntry.query.filter_by(user=recipient).first()
            has_participations = Participation.query.filter_by(user_id=recipient).first()
            has_competitions = UserCompetition.query.filter_by(user_id=recipient).first()
            has_achievements = UserAchievement.query.filter_by(user_id=recipient).first()
            
            if not any([has_manual_points, has_participations, has_competitions, has_achievements]):
                return jsonify({"status": "error", "message": "recipient user not found"}), 404
        
        # Check available points for donor
        ach_points = _calculate_user_achievement_points(donor)
        game_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=donor).scalar() or 0
        spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=donor).scalar() or 0
        manual_entry = ManualLeaderboardEntry.query.filter_by(user=donor, board='global').first()
        manual_points = manual_entry.points if manual_entry else 0
        
        # Include banked points from permanent account
        user_obj = User.query.filter_by(username=donor).first()
        banked_points = user_obj.banked_points if user_obj else 0
        
        available = max(0, int(ach_points) + int(game_points) + int(manual_points) + int(banked_points) - int(spent))
        
        if available < amount:
            return jsonify({"status": "error", "message": "insufficient points", "available_points": int(available)}), 400

        # Use manual leaderboard entries for donations
        donor_entry = ManualLeaderboardEntry.query.filter_by(user=donor, board='global').first()
        if donor_entry:
            donor_entry.points -= amount
        else:
            donor_entry = ManualLeaderboardEntry(user=donor, board='global', points=-amount)
            db.session.add(donor_entry)
        
        recipient_entry = ManualLeaderboardEntry.query.filter_by(user=recipient, board='global').first()
        if recipient_entry:
            recipient_entry.points += amount
        else:
            recipient_entry = ManualLeaderboardEntry(user=recipient, board='global', points=amount)
            db.session.add(recipient_entry)

        db.session.commit()

        return jsonify({
            "status": "success",
            "donated": amount,
            "recipient": recipient,
            "donated_by": donor,
            "remaining_points": available - amount
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500


@rewards_bp.route("/add", methods=["POST"])
# POST http://127.0.0.1:5001/rewards/add
# Body: { "name": "Gym Membership", "points": 400 }
@jwt_required(optional=True)
def rewards_add():
    """Add a new reward to the available list."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    points = data.get("points")

    if not name or points is None:
        return jsonify({"status": "error", "message": "name and points are required"}), 400
    try:
        points = int(points)
    except Exception:
        return jsonify({"status": "error", "message": "points must be integer"}), 400

    r = Reward(name=name, points=points)
    db.session.add(r)
    db.session.commit()

    user = get_jwt_identity()
    return jsonify({
        "status": "success",
        "reward": r.serialize(),
        "added_by": user
    }), 201


@rewards_bp.route("/remove", methods=["DELETE"])
# DELETE http://127.0.0.1:5001/rewards/remove
# Body: { "id": 1 }
@jwt_required(optional=True)
def rewards_remove():
    """Remove a reward from the available list."""
    data = request.get_json(silent=True) or {}
    reward_id = data.get("id")
    
    if not reward_id:
        return jsonify({"status": "error", "message": "id is required"}), 400
    
    try:
        reward_id = int(reward_id)
    except Exception:
        return jsonify({"status": "error", "message": "id must be integer"}), 400
    
    reward = Reward.query.get(reward_id)
    if not reward:
        return jsonify({"status": "error", "message": "reward not found"}), 404
    
    db.session.delete(reward)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Reward removed successfully"}), 200








