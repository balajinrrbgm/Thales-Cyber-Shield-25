#!/bin/bash

# AWS EKS Fargate Deployment Script for Thales Cyber Shield
# Optimized for minimum cost deployment

set -e

# Configuration
CLUSTER_NAME="thales-cyber-shield-cluster"
REGION="ap-south-1"
NAMESPACE="thales-cyber-shield"
ECR_REPO_URI="YOUR-ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com"

echo "🛡️ Starting Thales Cyber Shield AWS EKS Fargate Deployment"
echo "📍 Region: $REGION"
echo "💰 Cost-optimized configuration"

# Check prerequisites
echo "🔍 Checking prerequisites..."
command -v eksctl >/dev/null 2>&1 || { echo "❌ eksctl is required but not installed. Aborting." >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed. Aborting." >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }

# Configure AWS CLI
echo "⚙️ Configuring AWS credentials..."
aws configure list || { echo "❌ AWS credentials not configured. Run 'aws configure' first." >&2; exit 1; }

# Create ECR repositories
echo "📦 Creating ECR repositories..."
aws ecr create-repository --repository-name thales-cyber-shield --region $REGION || echo "Repository may already exist"
aws ecr create-repository --repository-name thales-frontend --region $REGION || echo "Repository may already exist"

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO_URI

# Build and push images
echo "🏗️ Building and pushing Docker images..."

# Build backend image
echo "Building backend image..."
docker build -t thales-cyber-shield .
docker tag thales-cyber-shield:latest $ECR_REPO_URI/thales-cyber-shield:latest
docker push $ECR_REPO_URI/thales-cyber-shield:latest

# Build frontend image
echo "Building frontend image..."
docker build -f Dockerfile.frontend -t thales-frontend .
docker tag thales-frontend:latest $ECR_REPO_URI/thales-frontend:latest
docker push $ECR_REPO_URI/thales-frontend:latest

# Create EKS cluster
echo "🚀 Creating EKS Fargate cluster..."
if ! eksctl get cluster --name $CLUSTER_NAME --region $REGION &>/dev/null; then
    echo "Creating new cluster..."
    eksctl create cluster --config-file=cluster-config.yaml
else
    echo "Cluster already exists, updating..."
fi

# Update kubeconfig
echo "⚙️ Updating kubeconfig..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Install AWS Load Balancer Controller
echo "🔧 Installing AWS Load Balancer Controller..."
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam-policy.json || echo "Policy may already exist"

# Create service account
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
eksctl create iamserviceaccount \
    --cluster=$CLUSTER_NAME \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --role-name AmazonEKSLoadBalancerControllerRole \
    --attach-policy-arn=arn:aws:iam::$ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
    --approve \
    --region=$REGION || echo "Service account may already exist"

# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=$CLUSTER_NAME \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller || echo "Controller may already be installed"

# Update deployment YAML with ECR image URIs
echo "📝 Updating deployment with ECR image URIs..."
sed -i "s|your-ecr-repo|$ECR_REPO_URI|g" eks-fargate-deployment.yaml

# Deploy application
echo "🚀 Deploying Thales Cyber Shield to EKS Fargate..."
kubectl apply -f eks-fargate-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/thales-backend -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/thales-frontend -n $NAMESPACE

# Get ingress URL
echo "🌐 Getting application URL..."
INGRESS_URL=$(kubectl get ingress thales-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "🏷️  Cluster Name: $CLUSTER_NAME"
echo "📍 Region: $REGION"
echo "🌐 Application URL: http://$INGRESS_URL"
echo "🔗 API Documentation: http://$INGRESS_URL/api/docs"
echo ""
echo "💰 Cost Optimization Features:"
echo "• Fargate serverless compute (pay per use)"
echo "• Minimal resource requests and limits"
echo "• Single database instance"
echo "• Auto-scaling with cost-aware limits"
echo "• GP3 storage for cost efficiency"
echo ""
echo "📋 Next Steps:"
echo "1. Configure DNS to point to the ALB"
echo "2. Set up SSL certificate in ACM"
echo "3. Update ingress with certificate ARN"
echo "4. Configure monitoring and alerting"
echo ""
echo "🔧 Useful Commands:"
echo "kubectl get pods -n $NAMESPACE"
echo "kubectl logs -f deployment/thales-backend -n $NAMESPACE"
echo "kubectl describe ingress thales-ingress -n $NAMESPACE"

# Cost estimation
echo ""
echo "💰 Estimated Monthly Cost (Mumbai region):"
echo "• EKS Cluster: ~$73 USD"
echo "• Fargate (2 vCPU, 4GB): ~$25-35 USD"
echo "• Application Load Balancer: ~$20 USD"
echo "• EBS Storage (10GB GP3): ~$1 USD"
echo "• Data Transfer: ~$5-10 USD"
echo "• Total Estimated: ~$124-139 USD/month"