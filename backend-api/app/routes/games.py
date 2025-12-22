"""
Games Route Module
=================

This module handles game competitions and participation tracking.
It provides two different ways to manage competitions:

1. Competition Model - Basic competition information
2. Participation Model - Tracks user progress in competitions (used by games route)
3. UserCompetition Model - Tracks simple membership (used by competitions route)
4. Game Model - Stores game rules and configurations

Key Features:
- Create and manage competitions
- Join competitions and track progress
- Update user progress in competitions
- Manage game rules and configurations
- Support for both authenticated and anonymous users
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import db
from ..utils.utils import L, get_achievement_points
from datetime import datetime
import json

# Create Flask blueprint for games routes
games_bp = Blueprint('games_bp', __name__)

# =============================================================================
# DATABASE MODELS
# =============================================================================

class Competition(db.Model):
    """
    Competition model representing a competition or challenge.
    
    This is the main competition entity that can be used by both
    the games route (with progress tracking) and competitions route (membership only).
    
    Attributes:
        id (int): Primary key, auto-incrementing competition ID
        title (str): Competition title, max 200 characters
        description (str): Optional detailed description
        start_at (datetime): Optional start date/time
        end_at (datetime): Optional end date/time
        is_active (bool): Whether the competition is currently active
        created_at (datetime): When the competition was created
    """
    __tablename__ = 'competitions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Participation(db.Model):
    """
    Participation model for tracking user progress in competitions.
    
    This model is used by the games route to track detailed participation
    including progress points earned by users.
    
    Attributes:
        id (int): Primary key, auto-incrementing participation ID
        user_id (str): User identifier (username or 'anonymous')
        competition_id (int): Foreign key to Competition
        progress (int): Progress points earned by user (default 0)
        updated_at (datetime): Last time progress was updated
        competition (Competition): Relationship to Competition model
    """
    __tablename__ = 'participations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Progress points earned
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    competition = db.relationship('Competition', backref='participants')


class UserCompetition(db.Model):
    """
    UserCompetition model for simple competition membership tracking.
    
    This model is used by the competitions route to track basic membership
    without detailed progress tracking.
    
    Attributes:
        id (int): Primary key, auto-incrementing membership ID
        user_id (str): User identifier (username or 'anonymous')
        competition_id (int): Foreign key to Competition
        joined_at (datetime): When the user joined the competition
        competition (Competition): Relationship to Competition model
    """
    __tablename__ = 'user_competitions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    competition = db.relationship('Competition')


class Game(db.Model):
    """
    Game model for storing game configurations and rules.
    
    This model stores game-specific rules and configurations
    that can be applied to competitions.
    
    Attributes:
        id (int): Primary key, auto-incrementing game ID
        name (str): Unique game name, max 120 characters
        rules_json (str): JSON string containing game rules
        is_active (bool): Whether the game is currently active
        created_at (datetime): When the game was created
    """
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    rules_json = db.Column(db.Text, nullable=True)  # JSON string containing game rules
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _uid_or_anon() -> str:
    """
    Get current user ID or return 'anonymous' if not authenticated.
    
    Returns:
        str: Username if authenticated, 'anonymous' otherwise
    """
    user = get_jwt_identity()
    return user if user else 'anonymous'


def _parse_dt(s):
    """
    Parse datetime string from ISO format.
    
    Args:
        s (str): ISO datetime string
        
    Returns:
        datetime: Parsed datetime object or None if parsing fails
    """
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _loads(txt):
    """
    Safely parse JSON string.
    
    Args:
        txt (str): JSON string to parse
        
    Returns:
        dict: Parsed JSON object or None if parsing fails
    """
    if txt is None:
        return None
    try:
        return json.loads(txt)
    except Exception:
        return None

def _dumps(obj):
    """
    Safely convert object to JSON string.
    
    Args:
        obj: Object to convert to JSON
        
    Returns:
        str: JSON string or None if conversion fails
    """
    try:
        return json.dumps(obj) if obj is not None else None
    except Exception:
        return None


# =============================================================================
# API ENDPOINTS
# =============================================================================

# Example usage for testing:
# POST http://127.0.0.1:5001/games/create
# Body: { "title": "Chess Championship", "description": "Online chess tournament", "start_at": "2025-09-20T10:00:00", "end_at": "2025-09-21T18:00:00", "is_active": true }

@games_bp.post('/create')  # Create new competition
@jwt_required(optional=True)
def create_game():
    try:
        data = request.get_json(silent=True) or {}
        title = data.get('title')
        L.log(f'Creating competition with data: {data}')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
        
        comp = Competition(
            title=title,
            description=data.get('description'),
            start_at=_parse_dt(data.get('start_at')),
            end_at=_parse_dt(data.get('end_at')),
            is_active=bool(data.get('is_active', True))
        )
        db.session.add(comp)
        db.session.commit()
        L.log(f'Competition created #{comp.id} "{comp.title}"')
        
        # Verify it was created
        all_comps = Competition.query.all()
        L.log(f'Total competitions in database: {len(all_comps)}')
        for c in all_comps:
            L.log(f'  - {c.id}: {c.title} (active: {c.is_active})')
        
        return jsonify({'id': comp.id, 'title': comp.title}), 201
    except Exception as e:
        L.log(f'Error creating competition: {str(e)}')
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@games_bp.get('/debug-competitions')  # debug endpoint
def debug_competitions():
    """Debug endpoint to see all competitions from games route"""
    try:
        db.create_all()
        
        # Get all competitions
        all_competitions = Competition.query.all()
        active_competitions = Competition.query.filter_by(is_active=True).all()
        
        result = {
            "total_competitions": len(all_competitions),
            "active_competitions": len(active_competitions),
            "all_competitions": [{"id": c.id, "title": c.title, "description": c.description, "is_active": c.is_active, "created_at": c.created_at.isoformat() if c.created_at else None} for c in all_competitions],
            "active_competitions_list": [{"id": c.id, "title": c.title, "description": c.description, "is_active": c.is_active, "created_at": c.created_at.isoformat() if c.created_at else None} for c in active_competitions]
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@games_bp.get('/active')  # view competition # http://127.0.0.1:5001/games/active
def active_game():
    now = datetime.utcnow()
    q = Competition.query.filter_by(is_active=True)
    # (Optional) filter by time window if desired
    comps = q.all()
    
    result = []
    for c in comps:
        # Get participants from Participation table (games route joins)
        participation_participants = [{'username': p.user_id, 'progress': p.progress} for p in c.participants]
        
        # Get participants from UserCompetition table (competitions route joins)
        user_competitions = UserCompetition.query.filter_by(competition_id=c.id).all()
        user_competition_participants = [{'username': uc.user_id, 'progress': 0} for uc in user_competitions]
        
        # Combine both lists
        all_participants = participation_participants + user_competition_participants
        
        result.append({
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'start_at': c.start_at.isoformat() if c.start_at else None,
            'end_at': c.end_at.isoformat() if c.end_at else None,
            'participants': all_participants
        })
    
    return jsonify(result), 200

@games_bp.post('/join')  # join competition #postman - http://127.0.0.1:5001/games/join - POST { "competition_id": 1}
@jwt_required(optional=True)
def join_game():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('competition_id')
    if not comp_id:
        return jsonify({'error': 'competition_id is required'}), 400
    user_id = _uid_or_anon()

    comp = Competition.query.get(comp_id)
    if not comp:
        return jsonify({'error': 'competition not found'}), 404

    existing = Participation.query.filter_by(user_id=user_id, competition_id=comp_id).first()
    if existing:
        return jsonify({'message': 'already joined', 'participation_id': existing.id}), 200

    p = Participation(user_id=user_id, competition_id=comp_id, progress=0)
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'joined', 'participation_id': p.id}), 201

@games_bp.put('/progress/update')  # competition progress and update #postman - http://127.0.0.1:5001/games/progress/update - PUT { "competition_id": "Game Name", "delta": 10}
@jwt_required(optional=True)
def update_progress_game():
    data = request.get_json(silent=True) or {}
    comp_id_or_name = data.get('competition_id')
    delta = data.get('delta', 0)
    if comp_id_or_name is None:
        return jsonify({'error': 'competition_id is required'}), 400
    user_id = _uid_or_anon()

    # Try to find competition by ID first, then by name
    comp = None
    if isinstance(comp_id_or_name, int) or (isinstance(comp_id_or_name, str) and comp_id_or_name.isdigit()):
        comp = Competition.query.get(int(comp_id_or_name))
    else:
        comp = Competition.query.filter_by(title=comp_id_or_name).first()
    
    if not comp:
        return jsonify({'error': f'competition not found. Searched for: "{comp_id_or_name}". Make sure you have joined this competition and the ID/name is correct.'}), 404

    p = Participation.query.filter_by(user_id=user_id, competition_id=comp.id).first()
    if not p:
        return jsonify({'error': f'You have not joined the competition "{comp.title}" (ID: {comp.id}). Please join the competition first before updating progress.'}), 404

    try:
        p.progress = int(p.progress) + int(delta)
    except Exception:
        return jsonify({'error': 'delta must be an integer'}), 400

    db.session.commit()
    return jsonify({'message': 'progress updated', 'progress': p.progress}), 200

@games_bp.get('/rules/update')  # view rules #postman - http://127.0.0.1:5001/games/rules/update - GET
def update_rules_game():
    games = Game.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': g.id,
        'name': g.name,
        'rules': _loads(g.rules_json)
    } for g in games]), 200

@games_bp.post('/custom/create')  # Create competition rules #postman - http://127.0.0.1:5001/games/custom/create - POST { "name": "Math Quiz", "rules": {  "questions": 20, "time_per_question": "15s" }}
@jwt_required(optional=True)
def create_custom_rules_game():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name is required'}), 400
    rules = data.get('rules')  # expect dict
    g = Game(name=name, rules_json=_dumps(rules), is_active=True)
    db.session.add(g)
    db.session.commit()
    return jsonify({'id': g.id, 'name': g.name, 'rules': _loads(g.rules_json)}), 201

@games_bp.delete('/competition/remove')  # Remove competition
@jwt_required(optional=True)
def remove_competition():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('id')
    if not comp_id:
        return jsonify({'error': 'id is required'}), 400
    
    comp = Competition.query.get(comp_id)
    if not comp:
        return jsonify({'error': 'competition not found'}), 404
    
    # Bank points for all participants before removing participations
    from ..models.models import User
    participations = Participation.query.filter_by(competition_id=comp_id).all()
    for p in participations:
        if (p.progress or 0) > 0:
            user = User.query.filter_by(username=p.user_id).first()
            if user:
                user.banked_points += int(p.progress)
                db.session.add(user)
                L.log(f"CRITICAL BANKING: {p.progress} points for user {p.user_id} (competition {comp_id} removed). New banked: {user.banked_points}")
            else:
                L.log(f"ERROR: Could not find user {p.user_id} to bank {p.progress} points.")
    
    db.session.flush() # Ensure banking is processed
    Participation.query.filter_by(competition_id=comp_id).delete()
    # Remove the competition
    db.session.delete(comp)
    db.session.commit()
    
    return jsonify({'message': 'competition removed'}), 200

@games_bp.delete('/participation/remove')  # Remove participation
@jwt_required(optional=True)
def remove_participation():
    data = request.get_json(silent=True) or {}
    part_id = data.get('id')
    if not part_id:
        return jsonify({'error': 'id is required'}), 400
    
    participation = Participation.query.get(part_id)
    if not participation:
        return jsonify({'error': 'participation not found'}), 404
    
    # Bank points before deleting participation
    if (participation.progress or 0) > 0:
        from ..models.models import User
        user = User.query.filter_by(username=participation.user_id).first()
        if user:
            user.banked_points += int(participation.progress)
            db.session.add(user)
            L.log(f"CRITICAL BANKING: {participation.progress} points for user {participation.user_id} (participation {part_id} removed). New banked: {user.banked_points}")
        else:
            L.log(f"ERROR: Could not find user {participation.user_id} to bank {participation.progress} points.")

    db.session.flush()
    db.session.delete(participation)
    db.session.commit()
    
    return jsonify({'message': 'participation removed'}), 200

@games_bp.delete('/game/remove')  # Remove game
@jwt_required(optional=True)
def remove_game():
    data = request.get_json(silent=True) or {}
    game_id = data.get('id')
    if not game_id:
        return jsonify({'error': 'id is required'}), 400
    
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'game not found'}), 404
    
    db.session.delete(game)
    db.session.commit()
    
    return jsonify({'message': 'game removed'}), 200

@games_bp.delete('/leave')  # Leave competition
@jwt_required(optional=True)
def leave_game():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('competition_id')
    if not comp_id:
        return jsonify({'error': 'competition_id is required'}), 400
    
    user_id = _uid_or_anon()
    
    # Find participation
    participation = Participation.query.filter_by(user_id=user_id, competition_id=comp_id).first()
    if not participation:
        return jsonify({'error': 'Not joined or competition not found'}), 404
    
    # Check if competition is active/exists? Maybe not needed for leaving.
    
    # Bank points before deleting participation
    if (participation.progress or 0) > 0:
        from ..models.models import User
        user = User.query.filter_by(username=user_id).first()
        if user:
            user.banked_points += int(participation.progress)
            db.session.add(user)
            L.log(f"CRITICAL BANKING: {participation.progress} points for user {user_id} (left game comp {comp_id}). New banked: {user.banked_points}")
        else:
            L.log(f"ERROR: Could not find user {user_id} to bank {participation.progress} points.")

    db.session.flush()
    db.session.delete(participation)
    db.session.commit()
    
    L.log(f"User {user_id} left competition {comp_id}")
    return jsonify({'message': 'left competition'}), 200