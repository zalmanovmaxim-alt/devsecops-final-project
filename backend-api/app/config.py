
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'DEVSECOPS'
    JWT_SECRET_KEY = os.getenv('SECRET_KEY') or 'DEVSECOPS'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///instance/games.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Development settings
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
