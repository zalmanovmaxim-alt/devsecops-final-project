from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..utils.db import db
from ..utils.utils import L
from ..models.models import User
from datetime import datetime

social_bp = Blueprint('social_bp', __name__)

# ---------- HELPERS ----------
def _uid_or_anon() -> str:
    user = get_jwt_identity()
    return user if user else 'anonymous'


# ---------- ROUTES ----------

@social_bp.post("/teams/create")  # יצירת צוותי תחרות
@jwt_required(optional=True)
# POST http://127.0.0.1:5001/social/teams/create
# Body:
# {
#   "team_name": "Winners",
#   "members": ["alice", "bob"]
# }
def social_teams_create():
    try:
        body = request.get_json() or {}
        team_name = body.get("team_name")
        members = body.get("members", [])
        uid = _uid_or_anon()  # Get actual logged-in user or anonymous

        if not team_name:
            return jsonify({"status": "error", "message": "team_name is required"}), 400

        # Create UserTeam records for each member
        for member in members:
            # Remove existing team membership for this user
            UserTeam.query.filter_by(user_id=member).delete()
            # Add new team membership
            user_team = UserTeam(user_id=member, team_name=team_name)
            db.session.add(user_team)

        # Record team creation activity
        activity = SocialActivity(
            user_id=uid,
            activity_type="team_created",
            description=f"Created team '{team_name}' with {len(members)} members",
            team_name=team_name,
            members_count=len(members),
            member_names=", ".join(members) if members else ""
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Team created successfully",
            "team": {"name": team_name, "members": members}
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to create team: {str(e)}"}), 500


@social_bp.get("/friends")  # צפייה בחברים/עמיתים מהמשרד
# GET http://127.0.0.1:5001/social/friends
def social_friends():
    data = []
    # L.log("Fetched friends list")
    return jsonify({"friends": data}), 200


@social_bp.post("/challenges/send")  # שליחת אתגרים אישיים
# POST http://127.0.0.1:5001/social/challenges/send
# Body:
# {
#   "to": "alice",
#   "challenge": "Push-up contest"
# }
@jwt_required(optional=True)
def social_challenges_send():
    try:
        body = request.get_json() or {}
        target = body.get("to")
        challenge = body.get("challenge")
        uid = _uid_or_anon()

        if not target or not challenge:
            return jsonify({"status": "error", "message": "to and challenge are required"}), 400

        # Store challenge in database
        challenge_entry = Challenge(challenger=uid, challenged=target, challenge_text=challenge)
        db.session.add(challenge_entry)
        db.session.commit()
        
        # Record challenge activity
        activity = SocialActivity(
            user_id=uid,
            activity_type="challenge_sent",
            description=f"Sent challenge to {target}: {challenge}",
            team_name=None,
            members_count=None,
            member_names=None
        )
        db.session.add(activity)
        db.session.commit()

        # L.log(f"Challenge sent by {uid} to {target}: {challenge}")
        return jsonify({
            "status": "success",
            "message": "Challenge sent",
            "from": uid,
            "to": target,
            "challenge": challenge
        }), 200
    except Exception as e:
        # L.log(f"Error sending challenge: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to send challenge"}), 500


@social_bp.get("/challenges/view")
# GET http://127.0.0.1:5001/social/challenges/view
@jwt_required(optional=True)
def social_challenges_view():
    try:
        # Clean up old challenges (older than 7 days to keep them longer than activities)
        from datetime import datetime, timedelta
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        old_challenges = Challenge.query.filter(Challenge.created_at < one_week_ago).all()
        for challenge in old_challenges:
            db.session.delete(challenge)
        db.session.commit()
        
        challenges = Challenge.query.order_by(Challenge.created_at.desc()).limit(20).all()
        data = []
        for challenge in challenges:
            data.append({
                "id": challenge.id,
                "challenger": challenge.challenger,
                "challenged": challenge.challenged,
                "challenge": challenge.challenge_text,
                "created_at": challenge.created_at.isoformat() if challenge.created_at else None
            })
        return jsonify({"challenges": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch challenges: {str(e)}"}), 500


@social_bp.get("/activity-feed")  # פיד של פעילות חברתית
# GET http://127.0.0.1:5001/social/activity-feed
def social_activity_feed():
    try:
        # Clean up old activities (older than 1 day)
        from datetime import datetime, timedelta
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        old_activities = SocialActivity.query.filter(SocialActivity.created_at < one_day_ago).all()
        for activity in old_activities:
            db.session.delete(activity)
        db.session.commit()
        
        activities = SocialActivity.query.order_by(SocialActivity.created_at.desc()).limit(20).all()
        data = []
        for activity in activities:
            data.append({
                "id": activity.id,
                "user": activity.user_id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "team_name": activity.team_name,
                "members_count": activity.members_count,
                "member_names": getattr(activity, 'member_names', None) or "",
                "created_at": activity.created_at.isoformat() if activity.created_at else None
            })
        # L.log("Fetched activity feed")
        return jsonify({"feed": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch activity feed: {str(e)}"}), 500


@social_bp.get("/celebrations")  # View celebrations
def social_celebrations():
    try:
        # Fetch celebrations from achievements endpoint
        from flask import current_app
        with current_app.test_client() as client:
            response = client.get('/achievements/celebrations')
            if response.status_code == 200:
                data = response.get_json()
                return jsonify(data), 200
            else:
                return jsonify({"celebrations": []}), 200
    except Exception as e:
        return jsonify({"celebrations": []}), 200


@social_bp.get("/rivalries")  # יריבויות משרדיות מהנות
# GET http://127.0.0.1:5001/social/rivalries
@jwt_required(optional=True)
def social_rivalries():
    try:
        # Clean up old challenges (older than 7 days)
        from datetime import datetime, timedelta
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        old_challenges = Challenge.query.filter(Challenge.created_at < one_week_ago).all()
        for challenge in old_challenges:
            db.session.delete(challenge)
        db.session.commit()
        
        challenges = Challenge.query.order_by(Challenge.created_at.desc()).limit(20).all()
        data = []
        for challenge in challenges:
            data.append({
                "id": challenge.id,
                "challenger": challenge.challenger,
                "challenged": challenge.challenged,
                "challenge": challenge.challenge_text,
                "created_at": challenge.created_at.isoformat() if challenge.created_at else None
            })
        return jsonify({"rivalries": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch rivalries: {str(e)}"}), 500


@social_bp.delete("/activity/remove")
# DELETE http://127.0.0.1:5001/social/activity/remove
# Body: { "id": 1 }
@jwt_required(optional=True)
def social_activity_remove():
    try:
        body = request.get_json() or {}
        activity_id = body.get("id")
        if not activity_id:
            return jsonify({"status": "error", "message": "id is required"}), 400
        try:
            activity_id = int(activity_id)
        except Exception:
            return jsonify({"status": "error", "message": "id must be integer"}), 400
        
        activity = SocialActivity.query.get(activity_id)
        if not activity:
            return jsonify({"status": "error", "message": "activity not found"}), 404
        
        db.session.delete(activity)
        db.session.commit()
        return jsonify({"status": "success", "message": "Activity removed successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to remove activity: {str(e)}"}), 500


@social_bp.delete("/challenges/remove")
# DELETE http://127.0.0.1:5001/social/challenges/remove
# Body: { "id": 1 }
@jwt_required(optional=True)
def social_challenges_remove():
    try:
        body = request.get_json() or {}
        challenge_id = body.get("id")
        if not challenge_id:
            return jsonify({"status": "error", "message": "id is required"}), 400
        try:
            challenge_id = int(challenge_id)
        except Exception:
            return jsonify({"status": "error", "message": "id must be integer"}), 400
        
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({"status": "error", "message": "challenge not found"}), 404
        
        db.session.delete(challenge)
        db.session.commit()
        return jsonify({"status": "success", "message": "Challenge removed successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to remove challenge: {str(e)}"}), 500


# --- Models ---
class UserTeam(db.Model):
    __tablename__ = 'user_teams'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    team_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SocialActivity(db.Model):
    __tablename__ = 'social_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # team_created, challenge_sent, etc.
    description = db.Column(db.String(500), nullable=False)
    team_name = db.Column(db.String(150), nullable=True)
    members_count = db.Column(db.Integer, nullable=True)
    member_names = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Challenge(db.Model):
    __tablename__ = 'social_challenges'
    id = db.Column(db.Integer, primary_key=True)
    challenger = db.Column(db.String(120), nullable=False)
    challenged = db.Column(db.String(120), nullable=False)
    challenge_text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
