# Gamification Backend (Flask)

## Overview
This is the Flask API for the Gamification Platform. It handles user authentication, game logic, and data persistence.

## Features
- JWT Authentication
- REST API for Games, Competitions, and Rewards
- PostgreSQL Database Integration
- Prometheus Metrics (`/metrics`)
- Health Checks (`/health`)

## Setup
1.  Install Python 3.9+.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## Testing
Unit tests are implemented using `pytest`.

To run tests:
```bash
pytest
```
To run with coverage:
```bash
pytest --cov=.
```

## Docker
Build the image:
```bash
docker build -t backend-image:latest .
```
Run the container:
```bash
docker run -p 5000:5000 -e DATABASE_URL="sqlite:///instance/games.db" backend-image:latest
```

## Kubernetes
Manifests are located in `../k8s/backend.yaml`.
