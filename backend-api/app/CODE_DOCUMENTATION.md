# Complete Code Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [Main Application (main.py)](#main-application-mainpy)
4. [Database Models](#database-models)
5. [Routes/API Endpoints](#routesapi-endpoints)
6. [Frontend (homepage.html)](#frontend-homepagehtml)
7. [Key Functions Explained](#key-functions-explained)
8. [Data Flow Examples](#data-flow-examples)
9. [Recent Changes Made](#recent-changes-made)

---

## Project Overview

This is a **Gamification Platform** built with Flask (Python backend) and vanilla JavaScript (frontend). It allows users to:
- Create and join competitions
- Earn achievements and points
- Redeem rewards
- Donate points to other users
- View leaderboards
- Social features (teams, challenges, activity feed)

---

## File Structure

```
DevSecOps-Project6-main/
├── main.py                 # Main Flask application entry point
├── classes/
│   └── user.py            # User database model
├── routes/                # API endpoints (Flask blueprints)
│   ├── login.py           # User registration/login
│   ├── games.py           # Game competitions
│   ├── achievements.py    # Achievement system
│   ├── competitions.py    # Competition management
│   ├── rewards.py         # Rewards and donations
│   ├── leaderboards.py    # Leaderboard management
│   └── social.py          # Social features
├── templates/
│   └── homepage.html      # Main frontend interface
├── static/
│   └── presets.txt        # API endpoint configurations
├── utils/
│   ├── db.py              # Database configuration
│   ├── logger.py          # Logging utilities
│   └── utils.py           # Helper functions
└── instance/
    └── games.db           # SQLite database file
```

---

## Main Application (main.py)

### Imports and Setup
```python
import datetime
from flask import Flask, request, g, jsonify, redirect, url_for, render_template
from routes.login import login_bp
from routes.achievements import achievements_bp
# ... other blueprint imports
```

**What this does:** Imports Flask framework and all the route blueprints (modular API endpoints).

### Flask App Configuration
```python
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY') or 'dev-secret-change-me'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
```

**What this does:**
- Creates Flask application
- Enables CORS (Cross-Origin Resource Sharing) for web requests
- Sets up JWT (JSON Web Token) authentication with secret key
- Sets token expiration to 1 hour

### Database Setup
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
```

**What this does:**
- Configures SQLite database location
- Initializes SQLAlchemy ORM (Object-Relational Mapping)
- Creates database connection

### Blueprint Registration
```python
app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(achievements_bp, url_prefix='/achievements')
app.register_blueprint(competitions_bp, url_prefix='/competitions')
# ... other blueprints
```

**What this does:** Registers each route module with URL prefixes (e.g., `/achievements/available`)

### Homepage Route
```python
@app.route('/')
def homepage():
    # Complex logic to gather all user data
    # Returns homepage.html with data
```

**What this does:** Main route that serves the homepage with all user data pre-loaded.

### API Endpoint for Frontend
```python
@app.route('/api/players_grouped')
def api_players_grouped():
    # Returns JSON data of all users with their points
```

**What this does:** Provides JSON API for the frontend to get user data dynamically.

---

## Database Models

### User Model (classes/user.py)
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(1100), nullable=False)
```

**What this does:** Defines the User table with unique usernames and hashed passwords.

### Competition Models (routes/games.py)
```python
class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**What this does:** Stores competition information (title, description, dates, active status).

```python
class Participation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    competition = db.relationship('Competition', backref='participants')
```

**What this does:** Tracks user participation in competitions and their progress points.

```python
class UserCompetition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    competition = db.relationship('Competition')
```

**What this does:** Alternative way to track competition membership (used by competitions route).

### Achievement Models (routes/achievements.py)
```python
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rarity = db.Column(db.String(20), nullable=False)  # common, rare, epic, legendary
    points = db.Column(db.Integer, nullable=False)
```

**What this does:** Defines available achievements with rarity levels and point values.

```python
class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    achievement = db.relationship('Achievement')
```

**What this does:** Tracks which achievements each user has unlocked.

### Reward Models (routes/rewards.py)
```python
class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
```

**What this does:** Defines available rewards and their point costs.

```python
class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=True)
    points = db.Column(db.Integer, nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**What this does:** Tracks when users redeem rewards (spend points).

---

## Routes/API Endpoints

### Login Routes (routes/login.py)
```python
@login_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    # Create new user
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully!", "username": username}), 201
```

**What this does:** Handles user registration by checking for duplicates and creating new users.

```python
@login_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"error": "Invalid credentials"}), 401
```

**What this does:** Authenticates users and returns JWT token for future requests.

### Games Routes (routes/games.py)
```python
@games_bp.route('/active', methods=['GET'])
@jwt_required(optional=True)
def get_active_games():
    user_id = get_jwt_identity() or 'anonymous'
    
    # Get all active competitions
    competitions = Competition.query.filter_by(is_active=True).all()
    
    # Get user's participations
    participations = Participation.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "competitions": [{"id": c.id, "title": c.title, "description": c.description} for c in competitions],
        "participations": [{"competition_id": p.competition_id, "progress": p.progress} for p in participations]
    })
```

**What this does:** Returns all active competitions and user's participation status.

```python
@games_bp.route('/join', methods=['POST'])
@jwt_required(optional=True)
def join_game():
    user_id = get_jwt_identity() or 'anonymous'
    data = request.get_json()
    competition_id = data.get('competition_id')
    
    # Check if already participating
    existing = Participation.query.filter_by(user_id=user_id, competition_id=competition_id).first()
    if existing:
        return jsonify({"error": "Already participating"}), 400
    
    # Create participation
    participation = Participation(user_id=user_id, competition_id=competition_id, progress=0)
    db.session.add(participation)
    db.session.commit()
    
    return jsonify({"message": "Joined competition successfully"}), 201
```

**What this does:** Allows users to join competitions by creating a Participation record.

### Achievements Routes (routes/achievements.py)
```python
@achievements_bp.route('/available', methods=['GET'])
@jwt_required(optional=True)
def get_available_achievements():
    user_id = get_jwt_identity() or 'anonymous'
    
    # Get all achievements
    all_achievements = Achievement.query.all()
    
    # Get user's unlocked achievements
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
    unlocked_ids = [ua.achievement_id for ua in user_achievements]
    
    # Filter out unlocked achievements
    available = [a for a in all_achievements if a.id not in unlocked_ids]
    
    return jsonify([{
        "id": a.id,
        "name": a.name,
        "description": a.description,
        "rarity": a.rarity,
        "points": a.points
    } for a in available])
```

**What this does:** Returns achievements that the user hasn't unlocked yet.

```python
@achievements_bp.route('/unlock', methods=['POST'])
@jwt_required(optional=True)
def unlock_achievement():
    user_id = get_jwt_identity() or 'anonymous'
    data = request.get_json()
    achievement_id = data.get('achievement_id')
    
    # Check if already unlocked
    existing = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if existing:
        return jsonify({"error": "Achievement already unlocked"}), 400
    
    # Unlock achievement
    user_achievement = UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.session.add(user_achievement)
    db.session.commit()
    
    return jsonify({"message": "Achievement unlocked successfully"}), 201
```

**What this does:** Allows users to unlock achievements (adds UserAchievement record).

### Rewards Routes (routes/rewards.py)
```python
@rewards_bp.route('/available', methods=['GET'])
@jwt_required(optional=True)
def get_available_rewards():
    user_id = get_jwt_identity() or 'anonymous'
    
    # Calculate available points
    ach_points = _calculate_user_achievement_points(user_id)
    game_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user_id).scalar() or 0
    manual_points = db.session.query(db.func.coalesce(db.func.sum(ManualLeaderboardEntry.points), 0)).filter_by(user=user_id).scalar() or 0
    spent = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user_id).scalar() or 0
    
    available = max(0, int(ach_points) + int(game_points) + int(manual_points) - int(spent))
    
    # Get all rewards
    rewards = Reward.query.all()
    
    return jsonify({
        "available_points": available,
        "rewards": [{"id": r.id, "name": r.name, "points": r.points, "description": r.description} for r in rewards]
    })
```

**What this does:** Calculates user's available points and returns all rewards they can afford.

```python
@rewards_bp.route('/redeem', methods=['POST'])
@jwt_required(optional=True)
def rewards_redeem():
    user_id = get_jwt_identity() or 'anonymous'
    data = request.get_json()
    reward_id = data.get('reward_id')
    
    # Get reward details
    reward = Reward.query.get(reward_id)
    if not reward:
        return jsonify({"error": "Reward not found"}), 404
    
    # Calculate available points (same logic as above)
    available = max(0, int(ach_points) + int(game_points) + int(manual_points) - int(spent))
    
    # Check if user has enough points
    if available < reward.points:
        return jsonify({"error": "Insufficient points", "available_points": available}), 400
    
    # Create redemption record
    redemption = Redemption(user_id=user_id, reward_id=reward_id, points=reward.points)
    db.session.add(redemption)
    db.session.commit()
    
    return jsonify({"message": "Reward redeemed successfully"}), 201
```

**What this does:** Allows users to redeem rewards by spending points (creates Redemption record).

### Donation System (routes/rewards.py)
```python
@rewards_bp.route('/donate-points', methods=['POST'])
@jwt_required(optional=True)
def rewards_donate_points():
    donor = get_jwt_identity() or 'anonymous'
    data = request.get_json()
    recipient = data.get('recipient')
    amount = int(data.get('amount'))
    
    # Check if recipient exists in system
    recipient_user = User.query.filter_by(username=recipient).first()
    if not recipient_user:
        # Check if they have any data in the system
        has_manual_points = ManualLeaderboardEntry.query.filter_by(user=recipient).first()
        has_participations = Participation.query.filter_by(user_id=recipient).first()
        has_competitions = UserCompetition.query.filter_by(user_id=recipient).first()
        has_achievements = UserAchievement.query.filter_by(user_id=recipient).first()
        
        if not any([has_manual_points, has_participations, has_competitions, has_achievements]):
            return jsonify({"error": "recipient user not found"}), 404
    
    # Calculate donor's available points
    available = max(0, int(ach_points) + int(game_points) + int(manual_points) - int(spent))
    
    # Check if donor has enough points
    if available < amount:
        return jsonify({"error": "insufficient points", "available_points": available}), 400
    
    # Record donation as redemption for donor
    donation_redemption = Redemption(user_id=donor, reward_id=None, points=amount)
    db.session.add(donation_redemption)
    
    # Add points to recipient via manual leaderboard
    recipient_entry = ManualLeaderboardEntry.query.filter_by(user=recipient, board='global').first()
    if recipient_entry:
        recipient_entry.points += amount
    else:
        recipient_entry = ManualLeaderboardEntry(user=recipient, board='global', points=amount)
        db.session.add(recipient_entry)
    
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "donated_by": donor,
        "recipient": recipient,
        "donated": amount,
        "remaining_points": available - amount
    })
```

**What this does:** Allows users to donate points to other users by:
1. Recording the donation as a redemption (spent points) for the donor
2. Adding points to the recipient via manual leaderboard

---

## Frontend (homepage.html)

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Gamification Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Dark theme CSS variables and styles */
  </style>
</head>
<body>
  <div class="flex">
    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-white shadow-lg min-h-screen p-4 space-y-4">
      <button onclick="showSection('home-section')">🏠 home</button>
      <button onclick="showSection('games-section')">🎮 games</button>
      <button onclick="showSection('achievements-section')">🏆 Achievements</button>
      <!-- ... other navigation buttons -->
    </aside>
    
    <!-- Main Content -->
    <main class="flex-1 p-6">
      <!-- Home Section -->
      <section id="home-section" class="mb-6">
        <!-- Homepage content with user data -->
      </section>
      
      <!-- Games Section -->
      <section id="games-section" class="hidden">
        <h2>Games</h2>
        <div class="space-x-2">
          <button onclick="sendRequest('games_active')">Active</button>
          <button onclick="sendRequest('games_create')">Create</button>
        </div>
        <div id="games-output" class="bg-white p-1 mt-1 rounded shadow"></div>
      </section>
      
      <!-- ... other sections -->
    </main>
  </div>
</body>
</html>
```

**What this does:** Creates a single-page application with sidebar navigation and multiple content sections.

### JavaScript State Management
```javascript
let authToken = null;           // JWT token for authentication
let presets = {};               // API endpoint configurations
let currentPreset = null;       // Currently selected API preset
let currentTarget = null;       // DOM element to update with results
let currentLeaderboardType = null;  // Track current leaderboard view
let currentGamesType = null;    // Track current games view
// ... other state variables
```

**What this does:** Global variables that track the current state of the application.

### Section Navigation
```javascript
function showSection(id) {
  // Hide all sections
  document.querySelectorAll("main section").forEach(sec => sec.classList.add("hidden"));
  
  // Show selected section
  document.getElementById(id).classList.remove("hidden");
  
  // Set default tab for each section
  setDefaultTabForSection(id);
  
  // Clear all output divs
  const outputDivs = ['leaderboards-output', 'games-output', 'achievements-output', 'competitions-output', 'rewards-output', 'social-output'];
  outputDivs.forEach(outputId => {
    const outputDiv = document.getElementById(outputId);
    if (outputDiv) {
      outputDiv.innerHTML = '';
    }
  });
}
```

**What this does:** Switches between different sections of the app and automatically loads default tabs.

### Default Tab System
```javascript
function setDefaultTabForSection(sectionId) {
  setTimeout(() => {
    switch(sectionId) {
      case 'games-section':
        sendRequest('games_active');
        break;
      case 'achievements-section':
        sendRequest('achievements_available');
        break;
      case 'competitions-section':
        sendRequest('competitions_my_competitions');
        break;
      case 'rewards-section':
        sendRequest('rewards_available');
        break;
      case 'social-section':
        sendRequest('social_activity_feed');
        break;
      case 'leaderboards-section':
        sendRequest('leaderboards_global');
        break;
    }
  }, 100);
}
```

**What this does:** Automatically triggers the most relevant tab when switching sections.

### API Communication
```javascript
function sendRequest(name) {
  console.log('sendRequest called with:', name);
  
  // Get preset configuration
  if (!presets[name]) return alert("Preset not found: " + name);
  currentPreset = presets[name];
  currentPreset.name = name;
  
  // Find target output div
  currentTarget = document.querySelector(`#${name.split("_")[0]}-output`);
  
  // Track current type for refresh purposes
  if (name.startsWith('leaderboards_')) {
    currentLeaderboardType = name;
  }
  // ... similar tracking for other types
  
  // Make API request
  fetch(currentPreset.url, {
    method: currentPreset.method,
    headers: { 
      "Content-Type": "application/json",
      ...(authToken && { "Authorization": `Bearer ${authToken}` })
    },
    body: currentPreset.body
  })
  .then(response => response.json())
  .then(data => {
    // Update UI with response
    if (currentTarget) {
      currentTarget.innerHTML = jsonToTable(data);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    if (currentTarget) {
      currentTarget.innerHTML = `<p>Error: ${error.message}</p>`;
    }
  });
}
```

**What this does:** Handles all API communication by:
1. Looking up preset configuration
2. Making HTTP request with proper headers
3. Updating the UI with the response

### Data Display
```javascript
function jsonToTable(json) {
  if (!json) return "<p>No data</p>";
  if (typeof json === "string") return `<p>${json}</p>`;
  
  if (Array.isArray(json)) {
    if (json.length === 0) return "<p>No data available</p>";
    
    // Create table from array
    let table = "<table class='w-full border-collapse border border-gray-300'><thead><tr>";
    const keys = Object.keys(json[0]);
    keys.forEach(key => {
      table += `<th class='border border-gray-300 px-4 py-2 bg-gray-100'>${key}</th>`;
    });
    table += "</tr></thead><tbody>";
    
    json.forEach(item => {
      table += "<tr>";
      keys.forEach(key => {
        table += `<td class='border border-gray-300 px-4 py-2'>${item[key]}</td>`;
      });
      table += "</tr>";
    });
    table += "</tbody></table>";
    return table;
  }
  
  // Handle object
  let table = "<table class='w-full border-collapse border border-gray-300'><tbody>";
  Object.entries(json).forEach(([key, value]) => {
    table += `<tr><td class='border border-gray-300 px-4 py-2 bg-gray-100 font-semibold'>${key}</td><td class='border border-gray-300 px-4 py-2'>${value}</td></tr>`;
  });
  table += "</tbody></table>";
  return table;
}
```

**What this does:** Converts JSON responses into HTML tables for display.

### Authentication
```javascript
async function loginUser() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  
  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  
  const data = await res.json();
  if (res.ok) {
    authToken = data.access_token;  // Save JWT token
    document.getElementById("user-status").innerText = "Logged in as " + username;
    alert("Login successful!");
  } else {
    alert("Login failed: " + JSON.stringify(data));
  }
}
```

**What this does:** Handles user login and stores JWT token for future requests.

### Homepage Data Loading
```javascript
async function refreshPlayers() {
  try {
    const response = await fetch('/api/players_grouped');
    const data = await response.json();
    
    // Update homepage with user data
    updateHomepageData(data);
  } catch (e) {
    console.error('Error refreshing players:', e);
  }
}

window.addEventListener('DOMContentLoaded', refreshPlayers);
```

**What this does:** Loads user data when the page loads and updates the homepage display.

---

## Key Functions Explained

### Point Calculation Logic
The system calculates user points from multiple sources:

```python
# In main.py - homepage route
def calculate_user_points(user_id):
    # Achievement points
    achievement_points = sum([ua.achievement.points for ua in UserAchievement.query.filter_by(user_id=user_id).all()])
    
    # Game progress points
    game_points = db.session.query(db.func.coalesce(db.func.sum(Participation.progress), 0)).filter_by(user_id=user_id).scalar() or 0
    
    # Manual points (from leaderboard)
    manual_points = db.session.query(db.func.coalesce(db.func.sum(ManualLeaderboardEntry.points), 0)).filter_by(user=user_id).scalar() or 0
    
    # Spent points (from redemptions)
    spent_points = db.session.query(db.func.coalesce(db.func.sum(Redemption.points), 0)).filter_by(user_id=user_id).scalar() or 0
    
    # Total points (capped at 0 minimum)
    total_points = max(0, achievement_points + game_points + manual_points - spent_points)
    
    return {
        "achievement_points": achievement_points,
        "total_progress": game_points,
        "manual_points": manual_points,
        "spent_points": spent_points,
        "total_points": total_points
    }
```

**What this does:** Calculates total user points from all sources, ensuring points never go below 0.

### Competition Management
The system has two ways to track competition participation:

1. **Participation Table** (used by games route):
```python
class Participation(db.Model):
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Tracks progress points
```

2. **UserCompetition Table** (used by competitions route):
```python
class UserCompetition(db.Model):
    user_id = db.Column(db.String(120), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)  # Just tracks membership
```

**What this does:** Provides two different ways to join competitions, which is why we had to fix the homepage to show both types.

### Preset System
The `presets.txt` file acts as a configuration system:

```json
{
  "games_active": {
    "url": "http://127.0.0.1:5001/games/active",
    "method": "GET",
    "body": "{}"
  },
  "achievements_unlock": {
    "url": "http://127.0.0.1:5001/achievements/unlock",
    "method": "POST",
    "body": "{\"achievement_id\":1}"
  }
}
```

**What this does:** Allows the frontend to make API calls without hardcoding URLs and parameters.

---

## Data Flow Examples

### Example 1: User Joins a Competition

1. **User clicks "Join Competition" button**
2. **Frontend calls `sendRequest('competitions_join')`**
3. **JavaScript looks up preset configuration**
4. **Makes POST request to `/competitions/join`**
5. **Backend creates UserCompetition record**
6. **Returns success response**
7. **Frontend updates UI**

### Example 2: User Unlocks Achievement

1. **User clicks "Unlock Achievement" button**
2. **Frontend calls `sendRequest('achievements_unlock')`**
3. **Makes POST request to `/achievements/unlock`**
4. **Backend creates UserAchievement record**
5. **Returns success response**
6. **Frontend refreshes achievement list**

### Example 3: User Redeems Reward

1. **User clicks "Redeem Reward" button**
2. **Frontend calls `sendRequest('rewards_redeem')`**
3. **Makes POST request to `/rewards/redeem`**
4. **Backend calculates available points**
5. **Creates Redemption record**
6. **Returns success response**
7. **Frontend updates available points**

---

## Recent Changes Made

### 1. Fixed Competition Management
**Problem:** Leave/Remove buttons were not working correctly.
**Solution:** Modified JavaScript to directly call appropriate functions based on current preset.

### 2. Added Default Tabs
**Problem:** Sections showed empty content when first opened.
**Solution:** Added `setDefaultTabForSection()` function to automatically load relevant tabs.

### 3. Fixed Homepage Display
**Problem:** Homepage only showed competitions from games route, not competitions route.
**Solution:** Modified homepage logic to query both Participation and UserCompetition tables.

### 4. Fixed Point Calculation
**Problem:** Users could have negative points.
**Solution:** Added `max(0, ...)` to cap points at minimum 0.

### 5. Fixed Donation System
**Problem:** Donation system was too restrictive and had logic errors.
**Solution:** 
- Modified to allow donations to any user with data in system
- Fixed donation logic to properly track spent points and recipient points

### 6. Fixed Database Schema
**Problem:** User table had incorrect UNIQUE constraint on password field.
**Solution:** Removed unique constraint and recreated database.

### 7. Added Section Descriptions
**Problem:** Users didn't understand what each section did.
**Solution:** Added descriptive text to each section with dark theme styling.

---

## How to Extend the System

### Adding a New Feature

1. **Create Database Model** (if needed):
```python
class NewFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # ... other fields
```

2. **Add API Endpoint**:
```python
@newfeature_bp.route('/endpoint', methods=['POST'])
@jwt_required(optional=True)
def new_feature_endpoint():
    # Implementation
    return jsonify({"message": "Success"})
```

3. **Add Preset Configuration**:
```json
{
  "newfeature_action": {
    "url": "http://127.0.0.1:5001/newfeature/endpoint",
    "method": "POST",
    "body": "{\"param\":\"value\"}"
  }
}
```

4. **Add Frontend Button**:
```html
<button onclick="sendRequest('newfeature_action')">New Feature</button>
```

### Debugging Tips

1. **Check Browser Console** for JavaScript errors
2. **Check Server Logs** for Python errors
3. **Test API Endpoints** directly with tools like Postman
4. **Verify Database State** using SQL queries
5. **Use `console.log()`** in JavaScript for debugging

---

This documentation covers all the major components of your gamification platform. Each section explains what the code does and why it's structured that way. If you need clarification on any specific part, let me know!
