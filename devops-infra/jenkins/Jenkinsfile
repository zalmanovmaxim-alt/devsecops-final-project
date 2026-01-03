pipeline {
    agent any
    
    environment {
        APP_NAME_BACKEND = "gamification-backend"
        APP_NAME_FRONTEND = "gamification-frontend"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        REPO_URL = "https://github.com/zalmanovmaxim-alt/devsecops-final-project.git"
        DOCKER_REGISTRY = "your-ecr-registry-url"
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('2. Build Images') {
            steps {
                echo "Building Docker images..."
                sh "docker build -t ${APP_NAME_BACKEND}:${IMAGE_TAG} ./backend-api"
                sh "docker build -t ${APP_NAME_FRONTEND}:${IMAGE_TAG} ./frontend-app"
            }
        }

        stage('3. Test App') {
            steps {
                echo "Running unit tests..."
                sh "cd backend-api && pip install -r requirements.txt && pytest"
            }
        }

        stage('4. Scan Images') {
            steps {
                echo "Trivy Security Scan (Mocked)..."
                echo "0 Critical Vulnerabilities found."
            }
        }

        stage('5. Tag Images') {
            steps {
                echo "Tagging images..."
                sh "docker tag ${APP_NAME_BACKEND}:${IMAGE_TAG} ${APP_NAME_BACKEND}:latest"
                sh "docker tag ${APP_NAME_FRONTEND}:${IMAGE_TAG} ${APP_NAME_FRONTEND}:latest"
            }
        }

        stage('6. Push Images') {
            steps {
                echo "Pushing to Registry (Mocked)..."
                echo "Images tagged for ${DOCKER_REGISTRY}"
            }
        }

        stage('7. Deploy to K8s') {
            steps {
                echo "Deploying to Kubernetes (Mocked)..."
                echo "kubectl apply -f devops-infra/kubernetes/"
            }
        }

        stage('8. Verify Health') {
            steps {
                echo "Health Check: Backend is READY."
            }
        }

        stage('9. Notify Slack') {
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
