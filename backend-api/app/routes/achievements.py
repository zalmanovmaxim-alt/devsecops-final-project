from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..models.models import User
from ..utils.db import db
from datetime import datetime
from ..utils.utils import L, get_achievement_points
from flask_jwt_extended import jwt_required, get_jwt_identity

achievements_bp = Blueprint('achievements_bp', __name__)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    locked = db.Column(db.String(20), default="locked") 
    rarity = db.Column(db.String(20), default="common")  # common, rare, epic, legendary
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    achievement = db.relationship('Achievement')

class Celebration(db.Model):
    __tablename__ = 'celebrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    achievement_name = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----Helpers-----

def _uid_or_anon() -> str:
    user = get_jwt_identity()
    return user if user else 'anonymous'


def _ser(a: Achievement):
    return {
        'id': a.id,
        'name': a.name,
        'description': a.description,
        'locked': a.locked,
        'rarity': a.rarity
    }

@achievements_bp.get('/available')  # view available achievements # GET http://127.0.0.1:5001/achievements/available
@jwt_required(optional=True)
def achievements_available():
    user_id = _uid_or_anon()
    
    # Get all achievements (exclude deleted)
    q = Achievement.query.filter((Achievement.is_deleted == False) | (Achievement.is_deleted == None))
    items = q.order_by(Achievement.name.asc()).all()
    
    # Get user's unlocked achievements
    unlocked_ids = {ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id).all()}
    
    # Create response with user-specific status
    result = []
    for a in items:
        achievement_data = _ser(a)
        achievement_data['user_unlocked'] = a.id in unlocked_ids
        achievement_data['locked'] = 'unlocked' if a.id in unlocked_ids else 'locked'
        result.append(achievement_data)
    
    return jsonify(result), 200

@achievements_bp.post('/unlock')  # unlock achievements
@jwt_required(optional=True)
def achievements_unlock():
    data = request.get_json(silent=True) or {}
    achievement_id = data.get('achievement_id')
    if not achievement_id:
        return jsonify({'error': 'achievement_id is required'}), 400

    a = Achievement.query.get(achievement_id)
    if not a:
        return jsonify({'error': 'achievement not found'}), 404

    user_id = _uid_or_anon()
    
    # Check if user already has this achievement
    existing = UserAchievement.query.filter_by(user_id=user_id, achievement_id=a.id).first()
    if existing:
        return jsonify({'error': 'achievement already unlocked by this user'}), 400

    # Create user achievement record (don't change global achievement status)
    ua = UserAchievement(user_id=user_id, achievement_id=a.id)
    db.session.add(ua)
    
    # Create automatic celebration
    celebration_message = f"{user_id} has unlocked {a.name} achievement! 🎉"
    celebration = Celebration(
        user_id=user_id,
        achievement_name=a.name,
        message=celebration_message
    )
    db.session.add(celebration)
    
    db.session.commit()

    L.log(f'Achievement unlocked by {user_id}: {a.name}')
    return jsonify({'message': 'unlocked', 'achievement': a.name, 'user': user_id}), 200


@achievements_bp.post('/lock')  # lock achievements
@jwt_required(optional=True)
def achievements_lock():
    data = request.get_json(silent=True) or {}
    achievement_id = data.get('achievement_id')
    user_id = _uid_or_anon()
    
    if not achievement_id:
        return jsonify({'error': 'achievement_id is required'}), 400
    
    # Check if user has this achievement unlocked
    user_achievement = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if not user_achievement:
        return jsonify({'error': 'achievement not unlocked by this user'}), 400
    
    # Remove the user achievement (lock it)
    db.session.delete(user_achievement)
    db.session.commit()
    
    L.log(f'Achievement locked by {user_id}: {achievement_id}')
    return jsonify({'message': 'locked', 'achievement_id': achievement_id, 'user': user_id}), 200


@achievements_bp.get('/my-progress')  # view achievements progress # GET http://127.0.0.1:5001/achievements/my-progress
@jwt_required(optional=True)
def achievements_my_progress():
    user_id = _uid_or_anon()
    unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
    unlocked_ids = {u.achievement_id for u in unlocked}
    all_ach = Achievement.query.all()
    
    # Calculate total points based on rarity
    total_points = 0
    for ua in unlocked:
        achievement = Achievement.query.get(ua.achievement_id)
        if achievement:
                total_points += get_achievement_points(achievement.rarity)
    
    return jsonify({
        'user_id': user_id,
        'total_points': total_points,
        'unlocked': [_ser(a) for a in all_ach if a.id in unlocked_ids],
        'locked':   [_ser(a) for a in all_ach if a.id not in unlocked_ids]
    }), 200

@achievements_bp.post('/create-custom')  # create custom achievements # POST http://127.0.0.1:5001/achievements/create-custom - {"name":"My Custom Achievement", "description": "ok?", "rarity": "rare" }
#@jwt_required(optional=True)
def achievements_create_custom():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    a = Achievement(
        name=name,
        description=data.get('description'),
        locked=data.get('locked', 'locked'),
        rarity=data.get('rarity', 'common')
    )
    db.session.add(a)
    db.session.commit()
    return jsonify(_ser(a)), 201

@achievements_bp.get('/celebrations')  # view celebrations
@jwt_required(optional=True)
def achievements_celebrations():
    celebrations = Celebration.query.order_by(Celebration.created_at.desc()).limit(20).all()
    celebration_data = []
    for c in celebrations:
        celebration_data.append({
            'id': c.id,
            'user_id': c.user_id,
            'achievement_name': c.achievement_name,
            'message': c.message,
            'created_at': c.created_at.isoformat() if c.created_at else None
        })
    return jsonify({'celebrations': celebration_data}), 200

@achievements_bp.delete('/achievement/remove')  # Remove achievement
@jwt_required(optional=True)
def remove_achievement():
    data = request.get_json(silent=True) or {}
    achievement_id = data.get('id')
    if not achievement_id:
        return jsonify({'error': 'id is required'}), 400
    
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return jsonify({'error': 'achievement not found'}), 404
    
    # Soft delete: Don't remove user achievements, just mark achievement as deleted
    # UserAchievement.query.filter_by(achievement_id=achievement_id).delete()
    
    # Mark as deleted and rename to free up the name
    achievement.is_deleted = True
    achievement.name = f"{achievement.name}_deleted_{int(datetime.utcnow().timestamp())}"
    
    db.session.commit()
    
    return jsonify({'message': 'achievement removed'}), 200

@achievements_bp.delete('/user-achievement/remove')  # Remove user achievement
@jwt_required(optional=True)
def remove_user_achievement():
    data = request.get_json(silent=True) or {}
    user_achievement_id = data.get('id')
    if not user_achievement_id:
        return jsonify({'error': 'id is required'}), 400
    
    user_achievement = UserAchievement.query.get(user_achievement_id)
    if not user_achievement:
        return jsonify({'error': 'user achievement not found'}), 404
    
    db.session.delete(user_achievement)
    db.session.commit()
    
    return jsonify({'message': 'user achievement removed'}), 200
