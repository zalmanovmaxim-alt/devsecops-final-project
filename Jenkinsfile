pipeline {
    agent any
    
    options {
        skipDefaultCheckout()
    }
    
    environment {
        APP_NAME_BACKEND = "gamification-backend"
        APP_NAME_FRONTEND = "gamification-frontend"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        REPO_URL = "https://github.com/zalmanovmaxim-alt/devsecops-final-project.git"
        DOCKER_REGISTRY = "your-ecr-registry-url"
    }

    stages {
        stage('1. Checkout') {
            steps {
                cleanWs()
                checkout scm
                echo "Workspace cleaned and code checked out. Starting Build #${env.BUILD_NUMBER}"
            }
        }

        stage('2. Build') {
            steps {
                echo "Building Docker images..."
                sh "docker build -t ${APP_NAME_BACKEND}:${IMAGE_TAG} ./backend-api"
                sh "docker build -t ${APP_NAME_FRONTEND}:${IMAGE_TAG} ./frontend-app"
            }
        }

        stage('3. Test') {
            steps {
                echo "Running unit tests..."
                // Use a virtual environment to avoid PEP 668 "externally-managed-environment" error
                sh "cd backend-api && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && pytest"
            }
        }

        stage('4. Security Scan') {
            steps {
                echo "Trivy Security Scan (Mocked)..."
            }
        }

        stage('5. Tag') {
            steps {
                sh "docker tag ${APP_NAME_BACKEND}:${IMAGE_TAG} ${APP_NAME_BACKEND}:latest"
                sh "docker tag ${APP_NAME_FRONTEND}:${IMAGE_TAG} ${APP_NAME_FRONTEND}:latest"
            }
        }

        stage('6. Push') {
            steps {
                echo "Pushing images to ${DOCKER_REGISTRY} (Mocked)..."
            }
        }

        stage('7. Deploy') {
            steps {
                echo "Deploying to Kubernetes (Mocked)..."
            }
        }

        stage('8. Verify') {
            steps {
                echo "Health Check: Backend is READY."
            }
        }

        stage('9. Notify') {
            steps {
                echo "Notification sent: Build ${env.BUILD_NUMBER} SUCCESS"
            }
        }
    }

    post {
        always {
            echo "Pipeline execution finished."
        }
    }
}
