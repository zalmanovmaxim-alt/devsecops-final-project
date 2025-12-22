
#!/bin/bash

# Setup script for DevSecOps Project
echo "🏗️ Initializing Infrastructure..."

# 1. Provision Infrastructure with Terraform
# cd devops-infra/terraform/environments/dev
# terraform init && terraform apply -auto-approve

# 2. Deploy to Kubernetes
echo "🚀 Deploying Applications to Kubernetes..."
kubectl apply -f devops-infra/kubernetes/namespace.yaml
kubectl apply -f devops-infra/kubernetes/

echo "✅ Setup Complete!"
