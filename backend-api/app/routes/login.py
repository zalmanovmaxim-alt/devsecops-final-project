from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from ..utils.db import db
from ..utils.utils import L
from ..models.models import User

login_bp = Blueprint('login_bp', __name__)


#try jwt
users_db = {} 

@login_bp.post('/register') #postman - http://127.0.0.1:5001/register - {"username":"gilad","password":123}
def register_user():
    """Endpoint to register a new user."""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    # בדיקה אם המשתמש כבר קיים
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "Username already exists"}), 409

    # יצירת אובייקט משתמש חדש והוספתו ל-session של בסיס הנתונים
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    
    # ביצוע commit כדי לשמור את השינויים באופן קבוע
    db.session.commit()

    return jsonify({"msg": "User created successfully!", "username": new_user.username}), 201

@login_bp.post('/login')#postman - http://127.0.0.1:5001/login - {"username":"gilad","password":123}
def login_user():
    """Endpoint for user login."""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    # Check user in the database
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@login_bp.get('/protected')# postman - auth - bearer Token - Token - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1Njg5NTUxMywianRpIjoiZmU2ODdkMjUtOTcwNS00OWQ2LThkNWQtMzA5MGEyNmQ2ZTcyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImdpbGFkIiwibmJmIjoxNzU2ODk1NTEzLCJjc3JmIjoiYzU4NjIyNjgtZDdkZC00OTAxLWE2YzUtNWViYTYxZGVlOGUyIiwiZXhwIjoxNzU2ODk2NDEzfQ.S8_eh7zr2chmYrsMahVdpDYWltKY-JqLC2ck5JsEDpI
@jwt_required() #expire in 15 minutes
def protected_route():
    """A protected endpoint that requires a valid JWT."""
    # Access the user identity from the JWT
    current_user_username = get_jwt_identity()
    return jsonify(logged_in_as=current_user_username), 200
#end try jwt