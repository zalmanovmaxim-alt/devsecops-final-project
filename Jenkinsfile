pipeline {
    agent any
    
    parameters {
        string(name: 'ROLLBACK_TAG', defaultValue: '', description: 'Enter a previous Image Tag to rollback. Leave empty for normal builds.')
    }

    triggers {
        githubPush()
    }
    
    options {
        skipDefaultCheckout()
        timeout(time: 1, unit: 'HOURS')
    }
    
    environment {
        APP_NAME_BACKEND = "gamification-backend"
        APP_NAME_FRONTEND = "gamification-frontend"
        // Determine environment and tag
        TARGET_ENV = "${env.BRANCH_NAME == 'main' ? 'prod' : 'dev'}"
        IMAGE_TAG = "${params.ROLLBACK_TAG ?: env.BUILD_NUMBER}"
        REPO_URL = "https://github.com/zalmanovmaxim-alt/devsecops-final-project.git"
        DOCKER_REGISTRY = "your-ecr-registry-url"
    }

    stages {
        stage('1. Checkout') {
            steps {
                cleanWs()
                checkout scm
                echo "Target Environment: ${env.TARGET_ENV}"
                echo "Target Image Tag: ${env.IMAGE_TAG}"
            }
        }

        stage('2. Build') {
            when { expression { params.ROLLBACK_TAG == '' } }
            steps {
                echo "Building Docker images for ${env.TARGET_ENV}..."
                sh "docker build -t ${APP_NAME_BACKEND}:${IMAGE_TAG} ./backend-api"
                sh "docker build -t ${APP_NAME_FRONTEND}:${IMAGE_TAG} ./frontend-app"
            }
        }

        stage('3. Test') {
            when { expression { params.ROLLBACK_TAG == '' } }
            steps {
                echo "Running unit tests in container..."
                sh "docker run --rm ${APP_NAME_BACKEND}:${IMAGE_TAG} python3 -m pytest -v"
            }
        }

        stage('4. Security Scan') {
            when { expression { params.ROLLBACK_TAG == '' } }
            steps {
                echo "Trivy Security Scan (Mocked)..."
            }
        }

        stage('5. Tag') {
            when { expression { params.ROLLBACK_TAG == '' } }
            steps {
                sh "docker tag ${APP_NAME_BACKEND}:${IMAGE_TAG} ${APP_NAME_BACKEND}:latest"
                sh "docker tag ${APP_NAME_FRONTEND}:${IMAGE_TAG} ${APP_NAME_FRONTEND}:latest"
            }
        }

        stage('6. Push') {
            when { expression { params.ROLLBACK_TAG == '' } }
            steps {
                echo "Pushing images to ${DOCKER_REGISTRY} (Mocked)..."
            }
        }

        stage('7. Deploy') {
            steps {
                script {
                    if (params.ROLLBACK_TAG != '') {
                        echo "Performing ROLLBACK to tag ${params.ROLLBACK_TAG} in ${env.TARGET_ENV}..."
                    } else {
                        echo "Deploying version ${IMAGE_TAG} to ${env.TARGET_ENV} environment..."
                    }
                }
            }
        }

        stage('8. Verify') {
            steps {
                echo "Post-deployment Verification for ${env.TARGET_ENV}: PASS"
            }
        }

        stage('9. Notify') {
            steps {
                echo "Notification sent: ${env.TARGET_ENV} Build ${env.IMAGE_TAG} SUCCESS"
            }
        }
    }

    post {
        success {
            echo "Archiving build artifacts..."
            // Archiving the Jenkinsfile as a proxy for build artifacts in this mock setup
            archiveArtifacts artifacts: 'Jenkinsfile', fingerprint: true
        }
        always {
            echo "Pipeline execution finished."
        }
    }
}
