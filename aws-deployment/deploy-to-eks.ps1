# PowerShell Script for AWS EKS Fargate Deployment
# Optimized for Windows environment

param(
    [string]$Region = "ap-south-1",
    [string]$ClusterName = "thales-cyber-shield-cluster",
    [string]$Namespace = "thales-cyber-shield"
)

Write-Host "🛡️ Thales Cyber Shield - AWS EKS Fargate Deployment" -ForegroundColor Cyan
Write-Host "📍 Region: $Region" -ForegroundColor Green
Write-Host "💰 Cost-optimized configuration" -ForegroundColor Yellow

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Blue

$requiredTools = @("eksctl", "kubectl", "aws", "docker")
foreach ($tool in $requiredTools) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "❌ $tool is required but not installed. Please install it first."
        exit 1
    }
}

# Check AWS credentials
Write-Host "⚙️ Checking AWS credentials..." -ForegroundColor Blue
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS credentials configured" -ForegroundColor Green
} catch {
    Write-Error "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
}

# Get AWS Account ID
$AccountId = (aws sts get-caller-identity --query Account --output text)
$EcrRepoUri = "$AccountId.dkr.ecr.$Region.amazonaws.com"

Write-Host "📦 Creating ECR repositories..." -ForegroundColor Blue

# Create ECR repositories
try {
    aws ecr create-repository --repository-name thales-cyber-shield --region $Region 2>$null
    aws ecr create-repository --repository-name thales-frontend --region $Region 2>$null
    Write-Host "✅ ECR repositories created" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ ECR repositories may already exist" -ForegroundColor Yellow
}

# ECR login
Write-Host "🔐 Logging into ECR..." -ForegroundColor Blue
$ecrPassword = aws ecr get-login-password --region $Region
echo $ecrPassword | docker login --username AWS --password-stdin $EcrRepoUri

# Build and push images
Write-Host "🏗️ Building and pushing Docker images..." -ForegroundColor Blue

# Build backend
Write-Host "Building backend image..." -ForegroundColor Cyan
docker build -t thales-cyber-shield .
docker tag thales-cyber-shield:latest "$EcrRepoUri/thales-cyber-shield:latest"
docker push "$EcrRepoUri/thales-cyber-shield:latest"

# Build frontend
Write-Host "Building frontend image..." -ForegroundColor Cyan
docker build -f Dockerfile.frontend -t thales-frontend .
docker tag thales-frontend:latest "$EcrRepoUri/thales-frontend:latest"
docker push "$EcrRepoUri/thales-frontend:latest"

# Check if cluster exists
Write-Host "🚀 Checking EKS cluster..." -ForegroundColor Blue
$clusterExists = $false
try {
    eksctl get cluster --name $ClusterName --region $Region | Out-Null
    $clusterExists = $true
    Write-Host "ℹ️ Cluster already exists" -ForegroundColor Yellow
} catch {
    Write-Host "Creating new cluster..." -ForegroundColor Cyan
}

# Create or update cluster
if (!$clusterExists) {
    Write-Host "🚀 Creating EKS Fargate cluster..." -ForegroundColor Blue
    eksctl create cluster --config-file=cluster-config.yaml
}

# Update kubeconfig
Write-Host "⚙️ Updating kubeconfig..." -ForegroundColor Blue
aws eks update-kubeconfig --region $Region --name $ClusterName

# Install AWS Load Balancer Controller
Write-Host "🔧 Installing AWS Load Balancer Controller..." -ForegroundColor Blue

# Download IAM policy
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json" -OutFile "iam-policy.json"

# Create IAM policy
try {
    aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam-policy.json
    Write-Host "✅ IAM policy created" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ IAM policy may already exist" -ForegroundColor Yellow
}

# Create service account
try {
    eksctl create iamserviceaccount `
        --cluster=$ClusterName `
        --namespace=kube-system `
        --name=aws-load-balancer-controller `
        --role-name AmazonEKSLoadBalancerControllerRole `
        --attach-policy-arn=arn:aws:iam::${AccountId}:policy/AWSLoadBalancerControllerIAMPolicy `
        --approve `
        --region=$Region
    Write-Host "✅ Service account created" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ Service account may already exist" -ForegroundColor Yellow
}

# Install Helm if not present
if (!(Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Helm..." -ForegroundColor Blue
    choco install kubernetes-helm -y
}

# Install AWS Load Balancer Controller with Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
try {
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller `
        -n kube-system `
        --set clusterName=$ClusterName `
        --set serviceAccount.create=false `
        --set serviceAccount.name=aws-load-balancer-controller
    Write-Host "✅ AWS Load Balancer Controller installed" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ Controller may already be installed" -ForegroundColor Yellow
}

# Update deployment YAML with ECR URIs
Write-Host "📝 Updating deployment configuration..." -ForegroundColor Blue
$deploymentContent = Get-Content "eks-fargate-deployment.yaml" -Raw
$deploymentContent = $deploymentContent -replace "your-ecr-repo", $EcrRepoUri
Set-Content "eks-fargate-deployment.yaml" -Value $deploymentContent

# Deploy application
Write-Host "🚀 Deploying Thales Cyber Shield..." -ForegroundColor Blue
kubectl apply -f eks-fargate-deployment.yaml

# Wait for deployments
Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor Blue
kubectl wait --for=condition=available --timeout=300s deployment/thales-backend -n $Namespace
kubectl wait --for=condition=available --timeout=300s deployment/thales-frontend -n $Namespace

# Get ingress URL
Write-Host "🌐 Getting application URL..." -ForegroundColor Blue
Start-Sleep -Seconds 30  # Wait for ALB to be created
$IngressUrl = kubectl get ingress thales-ingress -n $Namespace -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Clean up
Remove-Item "iam-policy.json" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Summary:" -ForegroundColor Cyan
Write-Host "🏷️  Cluster Name: $ClusterName" -ForegroundColor White
Write-Host "📍 Region: $Region" -ForegroundColor White
Write-Host "🌐 Application URL: http://$IngressUrl" -ForegroundColor White
Write-Host "🔗 API Documentation: http://$IngressUrl/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "💰 Cost Optimization Features:" -ForegroundColor Yellow
Write-Host "• Fargate serverless compute (pay per use)" -ForegroundColor White
Write-Host "• Minimal resource requests and limits" -ForegroundColor White
Write-Host "• Single database instance" -ForegroundColor White
Write-Host "• Auto-scaling with cost-aware limits" -ForegroundColor White
Write-Host "• GP3 storage for cost efficiency" -ForegroundColor White
Write-Host ""
Write-Host "💰 Estimated Monthly Cost (Mumbai region):" -ForegroundColor Magenta
Write-Host "• EKS Cluster: ~$73 USD" -ForegroundColor White
Write-Host "• Fargate (2 vCPU, 4GB): ~$25-35 USD" -ForegroundColor White
Write-Host "• Application Load Balancer: ~$20 USD" -ForegroundColor White
Write-Host "• EBS Storage (10GB GP3): ~$1 USD" -ForegroundColor White
Write-Host "• Data Transfer: ~$5-10 USD" -ForegroundColor White
Write-Host "• Total Estimated: ~$124-139 USD/month" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure DNS to point to the ALB" -ForegroundColor White
Write-Host "2. Set up SSL certificate in AWS Certificate Manager" -ForegroundColor White
Write-Host "3. Update ingress with certificate ARN" -ForegroundColor White
Write-Host "4. Configure CloudWatch monitoring and alerting" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "kubectl get pods -n $Namespace" -ForegroundColor White
Write-Host "kubectl logs -f deployment/thales-backend -n $Namespace" -ForegroundColor White
Write-Host "kubectl describe ingress thales-ingress -n $Namespace" -ForegroundColor White