# Gamification Platform - DevSecOps Modernization 🚀

Welcome to the modernized Gamification Platform! This project has been restructured into a professional, containerized architecture ready for a DevSecOps presentation.

## 🏗 Project Structure

- **`backend-api/`**: Modular Flask backend (REST API, JWT auth, Prometheus metrics).
- **`frontend-app/`**: React + Vite frontend with Nginx serving.
- **`devops-infra/`**: Infrastructure as Code (Terraform) and CI/CD (Jenkins/Kubernetes).
- **`docker-compose.yml`**: Full environment orchestration.

---

## 🚀 Getting Started (The 2-Minute Setup)

The easiest way to run the entire system is using **Docker Compose**.

### 1. Prerequisites
- Install **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**.
- Ensure Docker is running.

### 2. Initialization
If you just downloaded the ZIP file, extract it and open your terminal (PowerShell or Bash) in the project root:

```powershell
# Build and start all services (Backend, Frontend, Database)
docker-compose up --build -d
```

### 3. Verify the Services
Once the containers are running, check these URLs:
- **Frontend**: [http://localhost:8080](http://localhost:8080)
- **Backend Health**: [http://localhost:5000/health/live](http://localhost:5000/health/live)
- **Prometheus Metrics**: [http://localhost:5000/metrics](http://localhost:5000/metrics)

---

## 🛠 Manual Development Setup (Optional)

If you prefer to run things locally without Docker:

### Backend Setup
```powershell
cd backend-api
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python wsgi.py
```

### Frontend Setup
```powershell
cd frontend-app
npm install
npm run dev
```

---

## 🛡 DevSecOps Features
- **Containerization**: Fully Dockerized with multi-stage builds.
- **Observability**: Prometheus metrics exported on `/metrics`.
- **Infrastructure**: Terraform modules for AWS EKS & RDS in `devops-infra/`.
- **Health Probes**: Kubernetes-ready `/health/live` and `/health/ready` endpoints.
