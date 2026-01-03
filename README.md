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
- **Backend Health**: [http://localhost:5000/health/ready](http://localhost:5000/health/ready)
- **Jenkins CI/CD**: [http://localhost:8081](http://localhost:8081)
- **Prometheus UI**: [http://localhost:9090](http://localhost:9090)
- **Grafana Dashboards**: [http://localhost:3000](http://localhost:3000) (User/Pass: `admin`/`admin`)

---

## 🔍 How to Verify the DevSecOps Features

If you are presenting this project, follow these steps to showcase the work:

### 1. Start the Platform
```powershell
# In the root directory
docker-compose up --build -d
```
- **Verify**: Open [http://localhost:8080](http://localhost:8080) and log in.
- **Backend Health**: Check [http://localhost:5000/health/ready](http://localhost:5000/health/ready).

### 2. Inspect the CI/CD Pipeline
- **File**: `devops-infra/jenkins/Jenkinsfile`
- **What to show**: Point out the **9 stages** (Scan, Build, Test, etc.). These stages ensure that every commit is secure and functional before reaching production.

### 3. Review Infrastructure as Code (IaC)
- **Folder**: `devops-infra/terraform/`
- **Key Modules**:
    - `modules/registry`: Show how ECR repositories are automated.
    - `environments/dev/backend.tf`: Highlight the **Remote State** (S3) and **State Locking** (DynamoDB) setup—crucial for team collaboration.

### 4. Explore Monitoring & Observability
- **Prometheus**: Open `devops-infra/monitoring/prometheus/alerts.yaml` to show the active alerting rules for high error rates and database failures.
- **Grafana**: Show the dashboard configuration in `devops-infra/monitoring/grafana/dashboards.yaml`.
- **Live Metrics**: Visit [http://localhost:5000/metrics](http://localhost:5000/metrics) to see the raw data being scraped by Prometheus.

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
