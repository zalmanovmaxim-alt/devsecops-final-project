from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import db
from ..utils.utils import L
from datetime import datetime
from .games import Competition, Participation, UserCompetition  # 👈 use Competition, Participation, and UserCompetition from games.py

competitions_bp = Blueprint('competitions_bp', __name__)

# ---------- HELPERS ----------
def _uid_or_anon() -> str:
    user = get_jwt_identity()
    return user if user else 'anonymous'

def _ser(c: Competition):
    # Get participants from both Participation and UserCompetition tables
    participation_participants = [{'username': p.user_id, 'progress': p.progress} for p in c.participants]
    user_competitions = UserCompetition.query.filter_by(competition_id=c.id).all()
    user_competition_participants = [{'username': uc.user_id, 'progress': 0} for uc in user_competitions]
    all_participants = participation_participants + user_competition_participants
    
    # Calculate duration
    duration = None
    if c.start_at and c.end_at:
        duration_delta = c.end_at - c.start_at
        duration = f"{duration_delta.days} days" if duration_delta.days > 0 else f"{duration_delta.seconds // 3600} hours"
    
    return {
        "id": c.id,
        "title": getattr(c, "title", None),  # since Competition in games.py uses 'title'
        "description": c.description,
        "start_at": c.start_at.isoformat() if c.start_at else None,
        "end_at": c.end_at.isoformat() if c.end_at else None,
        "participants": all_participants,
        "duration": duration,
        "is_active": c.is_active,
    }

def _join_competition(category: str, default_title: str, description: str):
    """Shared logic: ensure competition exists, join it for the current user."""
    try:
        comp = Competition.query.filter_by(title=default_title).first()
        if not comp:
            comp = Competition(
                title=default_title,
                description=description,
                start_at=None,
                end_at=None,
                is_active=True
            )
            db.session.add(comp)
            db.session.commit()

        user_id = _uid_or_anon()
        # Allow duplicate competitions - users can join multiple of the same competition
        uc = UserCompetition(user_id=user_id, competition_id=comp.id)
        db.session.add(uc)
        db.session.commit()
        L.log(f"Competition joined by {user_id}: {comp.title}")
        return jsonify({"message": "joined", "competition": _ser(comp)}), 200
    except Exception as e:
        L.log(f"Error in _join_competition: {str(e)}")
        db.session.rollback()
        raise e

# ---------- ROUTES ----------
@competitions_bp.post("/code-quality")
# POST http://127.0.0.1:5001/competitions/code-quality
# Body: {}
@jwt_required(optional=True)
def competitions_code_quality():
    try:
        return _join_competition("code-quality", "Code Quality Challenge", "Improve code readability and maintainability")
    except Exception as e:
        L.log(f"Error in competitions_code_quality: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/learning")
# POST http://127.0.0.1:5001/competitions/learning
# Body: {}
@jwt_required(optional=True)
def competitions_learning():
    try:
        return _join_competition("learning", "Learning Challenge", "Upskill and share knowledge")
    except Exception as e:
        L.log(f"Error in competitions_learning: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/fitness")
# POST http://127.0.0.1:5001/competitions/fitness
# Body: {}
@jwt_required(optional=True)
def competitions_fitness():
    try:
        return _join_competition("fitness", "Office Fitness Challenge", "Stay active at work")
    except Exception as e:
        L.log(f"Error in competitions_fitness: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/sustainability")
# POST http://127.0.0.1:5001/competitions/sustainability
# Body: {}
@jwt_required(optional=True)
def competitions_sustainability():
    try:
        return _join_competition("sustainability", "Green Office Challenge", "Promote eco-friendly practices")
    except Exception as e:
        L.log(f"Error in competitions_sustainability: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/creativity")
# POST http://127.0.0.1:5001/competitions/creativity
# Body: {}
@jwt_required(optional=True)
def competitions_creativity():
    try:
        return _join_competition("creativity", "Creativity Challenge", "Express and innovate")
    except Exception as e:
        L.log(f"Error in competitions_creativity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/team-building")
# POST http://127.0.0.1:5001/competitions/team-building
# Body: {}
@jwt_required(optional=True)
def competitions_team_building():
    try:
        return _join_competition("team-building", "Team Building Activity", "Strengthen collaboration")
    except Exception as e:
        L.log(f"Error in competitions_team_building: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.get("/my-competitions")
# GET http://127.0.0.1:5001/competitions/my-competitions
@jwt_required(optional=True)
def competitions_my_competitions():
    """View competitions that the current user has joined"""
    try:
        user_id = _uid_or_anon()
        
        # Get user competition IDs from BOTH Participation table (games route joins) AND UserCompetition table (competitions route joins)
        participation_ids = db.session.query(Participation.competition_id).filter_by(user_id=user_id).all()
        user_competition_ids = db.session.query(UserCompetition.competition_id).filter_by(user_id=user_id).all()
        
        # Combine both lists and remove duplicates
        competition_ids = list(set([row[0] for row in participation_ids] + [row[0] for row in user_competition_ids]))
        
        L.log(f"User {user_id} has {len(competition_ids)} competitions: {competition_ids}")
        
        if not competition_ids:
            return jsonify([]), 200
        
        # Get the actual competitions
        competitions = Competition.query.filter(Competition.id.in_(competition_ids)).all()
        
        # Copy EXACT logic from games route
        result = []
        for c in competitions:
            # Get participants from Participation table (games route joins)
            participation_participants = [{'username': p.user_id, 'progress': p.progress} for p in c.participants]
            
            # Get participants from UserCompetition table (competitions route joins)
            user_competitions = UserCompetition.query.filter_by(competition_id=c.id).all()
            user_competition_participants = [{'username': uc.user_id, 'progress': 0} for uc in user_competitions]
            
            # Combine both lists
            all_participants = participation_participants + user_competition_participants
            
            # Check both tables for join date
            participation = Participation.query.filter_by(user_id=user_id, competition_id=c.id).first()
            user_competition = UserCompetition.query.filter_by(user_id=user_id, competition_id=c.id).first()
            
            joined_at = None
            if user_competition and user_competition.joined_at:
                joined_at = user_competition.joined_at.isoformat()
            elif participation and participation.updated_at:
                joined_at = participation.updated_at.isoformat()
            
            result.append({
                'id': c.id,
                'title': c.title,
                'description': c.description,
                'start_at': c.start_at.isoformat() if c.start_at else None,
                'end_at': c.end_at.isoformat() if c.end_at else None,
                'participants': all_participants,
                'joined_at': joined_at
            })
        
        return jsonify(result), 200
    except Exception as e:
        L.log(f"Error in competitions_my_competitions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.get("/test-joined")
def test_joined():
    """Test endpoint for joined competitions"""
    return jsonify({"message": "joined endpoint is working"}), 200

@competitions_bp.get("/create-tables")
def create_tables():
    """Create database tables"""
    try:
        db.create_all()
        return jsonify({"message": "Tables created successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competitions_bp.get("/debug-competitions")
def debug_competitions():
    """Debug endpoint to see all competitions"""
    try:
        db.create_all()
        
        # Get all competitions
        all_competitions = Competition.query.all()
        active_competitions = Competition.query.filter_by(is_active=True).all()
        
        # Also check UserCompetition and Participation records
        user_competitions = UserCompetition.query.all()
        participations = Participation.query.all()
        
        result = {
            "total_competitions": len(all_competitions),
            "active_competitions": len(active_competitions),
            "user_competitions": len(user_competitions),
            "participations": len(participations),
            "all_competitions": [_ser(c) for c in all_competitions],
            "active_competitions_list": [_ser(c) for c in active_competitions],
            "user_competitions_list": [{"id": uc.id, "user_id": uc.user_id, "competition_id": uc.competition_id} for uc in user_competitions],
            "participations_list": [{"id": p.id, "user_id": p.user_id, "competition_id": p.competition_id, "progress": p.progress} for p in participations]
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competitions_bp.post("/test-create")
def test_create_competition():
    """Test endpoint to create a competition and verify it exists"""
    try:
        # Create a test competition
        comp = Competition(
            title="Test Competition from Competitions Route",
            description="This was created in competitions route",
            is_active=True
        )
        db.session.add(comp)
        db.session.commit()
        
        # Immediately check if it exists
        all_competitions = Competition.query.all()
        active_competitions = Competition.query.filter_by(is_active=True).all()
        
        result = {
            "created_competition": _ser(comp),
            "total_competitions": len(all_competitions),
            "active_competitions": len(active_competitions),
            "all_competitions": [_ser(c) for c in all_competitions]
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@competitions_bp.get("/all")
# GET http://127.0.0.1:5001/competitions/all
@jwt_required(optional=True)
def competitions_all():
    """View all available competitions"""
    try:
        # Ensure tables exist
        db.create_all()
        
        competitions = Competition.query.filter_by(is_active=True).all()
        L.log(f"Found {len(competitions)} active competitions")
        for comp in competitions:
            L.log(f"Competition: {comp.id} - {comp.title}")
        
        # Copy EXACT logic from games route
        result = []
        for c in competitions:
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
    except Exception as e:
        L.log(f"Error in competitions_all: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.post("/join")
# POST http://127.0.0.1:5001/competitions/join
# Body: {"competition_id": 1}
@jwt_required(optional=True)
def competitions_join():
    """Join a competition by ID"""
    data = request.get_json(silent=True) or {}
    competition_id = data.get('competition_id')
    
    if not competition_id:
        return jsonify({'error': 'competition_id is required'}), 400
    
    user_id = _uid_or_anon()
    
    # Check if competition exists
    comp = Competition.query.get(competition_id)
    if not comp:
        return jsonify({'error': 'competition not found'}), 404
    
    # Allow duplicate competitions - users can join multiple of the same competition
    uc = UserCompetition(user_id=user_id, competition_id=competition_id)
    db.session.add(uc)
    db.session.commit()
    
    L.log(f"Competition joined by {user_id}: {comp.title}")
    return jsonify({"message": "joined", "competition": _ser(comp)}), 200

@competitions_bp.delete("/leave")
# DELETE http://127.0.0.1:5001/competitions/leave
# Body: {"competition_id": 1}
@jwt_required(optional=True)
def competitions_leave():
    """Leave a competition"""
    try:
        data = request.get_json(silent=True) or {}
        competition_id = data.get('competition_id')
        
        L.log(f"Leave request: competition_id={competition_id}, data={data}")
        
        if not competition_id:
            return jsonify({'error': 'competition_id is required'}), 400
        
        user_id = _uid_or_anon()
        L.log(f"User {user_id} trying to leave competition {competition_id}")
        
        # Ensure tables exist
        try:
            db.create_all()
        except Exception as create_error:
            L.log(f"Error creating tables: {str(create_error)}")
        
        # Check both UserCompetition and Participation tables
        user_competition = UserCompetition.query.filter_by(
            user_id=user_id, 
            competition_id=competition_id
        ).first()
        
        participation = Participation.query.filter_by(
            user_id=user_id, 
            competition_id=competition_id
        ).first()
        
        L.log(f"Found user_competition: {user_competition}")
        L.log(f"Found participation: {participation}")
        
        if not user_competition and not participation:
            return jsonify({'error': 'user not joined to this competition'}), 404
        
        # Remove from whichever table has the record
        if user_competition:
            db.session.delete(user_competition)
            L.log(f"Removed UserCompetition record")
        
        if participation:
            # Bank points before deleting participation
            if (participation.progress or 0) > 0:
                from ..models.models import User
                user = User.query.filter_by(username=user_id).first()
                if user:
                    user.banked_points += int(participation.progress)
                    db.session.add(user)
                    L.log(f"CRITICAL BANKING: {participation.progress} points for user {user_id} (left comp {competition_id}). New banked: {user.banked_points}")
                else:
                    L.log(f"ERROR: Could not find user {user_id} to bank {participation.progress} points.")
            
            db.session.flush()
            db.session.delete(participation)
            L.log(f"Removed Participation record")
        
        db.session.commit()
        
        L.log(f"Competition left by {user_id}: {competition_id}")
        return jsonify({'message': 'left competition', 'competition_id': competition_id}), 200
    except Exception as e:
        L.log(f"Error in competitions_leave: {str(e)}")
        return jsonify({'error': str(e)}), 500

@competitions_bp.delete("/remove")
# DELETE http://127.0.0.1:5001/competitions/remove
# Body: {"competition_id": 1}
@jwt_required(optional=True)
def competitions_remove():
    """Remove/delete a competition entirely (for testing purposes)"""
    try:
        data = request.get_json(silent=True) or {}
        competition_id = data.get('competition_id')
        
        if not competition_id:
            return jsonify({'error': 'competition_id is required'}), 400
        
        # Check if competition exists
        comp = Competition.query.get(competition_id)
        if not comp:
            return jsonify({'error': 'competition not found'}), 404
        
        # Store the title before deletion
        comp_title = comp.title
        
        # Delete all user participations first (UserCompetition)
        UserCompetition.query.filter_by(competition_id=competition_id).delete()
        
        # Delete all game participations (Participation)
        # Bank points for all participants first
        from ..models.models import User
        participations = Participation.query.filter_by(competition_id=competition_id).all()
        for p in participations:
            if (p.progress or 0) > 0:
                user = User.query.filter_by(username=p.user_id).first()
                if user:
                    user.banked_points += int(p.progress)
                    db.session.add(user)
                    L.log(f"CRITICAL BANKING: {p.progress} points for user {p.user_id} (comp {competition_id} removed). New banked: {user.banked_points}")
                else:
                    L.log(f"ERROR: Could not find user {p.user_id} to bank {p.progress} points.")
        
        db.session.flush()
        Participation.query.filter_by(competition_id=competition_id).delete()
        
        # Delete the competition itself
        db.session.delete(comp)
        db.session.commit()
        
        L.log(f"Competition deleted: {comp_title} (ID: {competition_id})")
        return jsonify({'message': 'competition deleted', 'competition_id': competition_id}), 200
    except Exception as e:
        db.session.rollback()
        L.log(f"Error deleting competition: {str(e)}")
        return jsonify({'error': f'Failed to delete competition: {str(e)}'}), 500
