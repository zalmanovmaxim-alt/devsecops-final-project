
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .utils.db import db
from .metrics import init_metrics

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    init_metrics(app)
    
    with app.app_context():
        # Import and register blueprints
        from .routes.login import login_bp
        from .routes.achievements import achievements_bp
        from .routes.competitions import competitions_bp
        from .routes.games import games_bp
        from .routes.rewards import rewards_bp
        from .routes.leaderboards import leaderboards_bp
        from .routes.social import social_bp
        from .routes.health import health_bp
        from .routes.api import api_bp
        
        app.register_blueprint(login_bp)
        app.register_blueprint(games_bp, url_prefix='/games')
        app.register_blueprint(achievements_bp, url_prefix='/achievements')
        app.register_blueprint(competitions_bp, url_prefix='/competitions')
        app.register_blueprint(rewards_bp, url_prefix='/rewards')
        app.register_blueprint(leaderboards_bp, url_prefix='/leaderboards')
        app.register_blueprint(social_bp, url_prefix='/social')
        app.register_blueprint(health_bp, url_prefix='/health')
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Ensure instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # Create database tables
        # db.create_all() # Disabled to prevent crash on import. Use migrations or manual init.
        
    return app

app = create_app()