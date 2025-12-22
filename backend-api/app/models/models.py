"""
User Database Model
==================

This module defines the User model for the gamification platform.
Users can register, login, and participate in various platform activities.

The User model stores:
- Unique username (max 20 characters)
- Hashed password (up to 1100 characters to accommodate various hashing algorithms)
- Auto-incrementing ID as primary key

Note: The password field was previously incorrectly set as unique, which has been fixed.
Multiple users can have the same password (though not recommended for security).
"""

from ..utils.db import db


class User(db.Model):
    """
    User model representing registered users in the gamification platform.
    
    Attributes:
        id (int): Primary key, auto-incrementing user ID
        username (str): Unique username, max 20 characters
        password (str): Hashed password, max 1100 characters (not unique)
    
    Relationships:
        - One-to-many with UserAchievement (users can have multiple achievements)
        - One-to-many with Participation (users can participate in multiple competitions)
        - One-to-many with UserCompetition (users can join multiple competitions)
        - One-to-many with Redemption (users can redeem multiple rewards)
        - One-to-many with ManualLeaderboardEntry (users can have manual points)
    """
    
    # Table name (optional, defaults to lowercase class name)
    __tablename__ = 'user'
    
    # Primary key - auto-incrementing integer
    id = db.Column(db.Integer, primary_key=True)
    
    # Username - must be unique and not null, max 20 characters
    username = db.Column(db.String(20), unique=True, nullable=False)
    
    # Password - hashed password, not unique (multiple users can have same password)
    # Max 1100 characters to accommodate various hashing algorithms
    password = db.Column(db.String(1100), nullable=False)
    
    # Banked points - permanent currency earned from competitions
    banked_points = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        """String representation of User object for debugging"""
        return f'User-{self.id} ({self.username})'