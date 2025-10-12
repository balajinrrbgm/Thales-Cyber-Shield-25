# AWS Cost Optimization Guide for Thales Cyber Shield
# Detailed breakdown of cost-saving measures

## 📊 Cost Breakdown Analysis

### Monthly Cost Estimation (ap-south-1 Mumbai):

| Service | Configuration | Monthly Cost (USD) |
|---------|--------------|-------------------|
| **EKS Cluster** | Control plane | ~$73 |
| **Fargate Compute** | 2 vCPU, 4GB RAM | ~$25-35 |
| **Application Load Balancer** | Internet-facing ALB | ~$20 |
| **EBS Storage** | 10GB GP3 | ~$1 |
| **Data Transfer** | Outbound traffic | ~$5-10 |
| **CloudWatch Logs** | Basic logging | ~$3-5 |
| **Total Estimated** | | **~$127-144 USD/month** |

## 💰 Cost Optimization Strategies

### 1. Fargate Right-Sizing
```yaml
# Optimized resource allocation
resources:
  requests:
    memory: "512Mi"    # Minimum needed
    cpu: "250m"        # 0.25 vCPU
  limits:
    memory: "1Gi"      # Prevent over-consumption
    cpu: "500m"        # 0.5 vCPU max
```

### 2. Auto-Scaling Configuration
```yaml
# Cost-aware scaling
minReplicas: 1         # Start with minimum
maxReplicas: 5         # Limit maximum to control costs
targetCPUUtilization: 70%  # Scale at 70% CPU
```

### 3. Storage Optimization
- **GP3 over GP2**: 20% cost savings
- **10GB minimum**: Sufficient for development/testing
- **No provisioned IOPS**: Use baseline performance

### 4. Network Cost Reduction
- **Single AZ deployment**: For development (not recommended for production)
- **VPC endpoints**: Reduce NAT gateway costs
- **CloudFront**: Cache static content to reduce origin requests

## 🔧 Further Cost Reduction Options

### Option 1: Spot Instances (for non-critical workloads)
```yaml
# Use EC2 spot instances instead of Fargate
nodeGroups:
  - name: spot-nodes
    instanceTypes: ["t3.medium", "t3a.medium"]
    spot: true
    desiredCapacity: 2
    minSize: 1
    maxSize: 5
```
**Savings**: Up to 70% on compute costs

### Option 2: Reserved Instances
- **1-year term**: 20% savings
- **3-year term**: 40% savings
- **Applicable to**: EKS cluster, RDS instances

### Option 3: Development Environment Scaling
```bash
# Scale down during off-hours
kubectl scale deployment thales-backend --replicas=0 -n thales-cyber-shield
kubectl scale deployment thales-frontend --replicas=0 -n thales-cyber-shield

# Scale up when needed
kubectl scale deployment thales-backend --replicas=2 -n thales-cyber-shield
kubectl scale deployment thales-frontend --replicas=2 -n thales-cyber-shield
```

### Option 4: Alternative Database Solutions
```yaml
# Use AWS RDS with burstable instances
# db.t3.micro: ~$12/month (instead of self-hosted PostgreSQL)
```

## 📈 Cost Monitoring Setup

### 1. AWS Cost Explorer
- Set up daily cost monitoring
- Create budget alerts at $100, $150
- Monitor by service and resource tags

### 2. CloudWatch Billing Alarms
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "ThalesCyberShield-CostAlarm" \
  --alarm-description "Alert when costs exceed $140" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 140 \
  --comparison-operator GreaterThanThreshold
```

### 3. AWS Trusted Advisor
- Enable cost optimization recommendations
- Regular reviews of underutilized resources

## 🏗️ Production Cost Considerations

### Minimal Production Setup (~$300-400/month):
- **Multi-AZ deployment**: High availability
- **Auto-scaling**: 2-10 replicas
- **RDS Multi-AZ**: Database redundancy
- **CloudFront CDN**: Global content delivery
- **WAF**: Web application firewall
- **Backup storage**: S3 snapshots

### Enterprise Setup (~$800-1200/month):
- **Multiple environments**: Dev, Staging, Prod
- **Enhanced monitoring**: Detailed CloudWatch metrics
- **Security services**: GuardDuty, Inspector
- **Compliance**: AWS Config, CloudTrail
- **High availability**: Multi-region setup

## 🔄 Cost Optimization Automation

### 1. Scheduled Scaling
```yaml
# CronJob to scale down during off-hours
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-job
spec:
  schedule: "0 18 * * *"  # 6 PM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - kubectl scale deployment thales-backend --replicas=1
```

### 2. AWS Lambda Cost Optimizer
```python
# Lambda function to optimize resources
import boto3

def lambda_handler(event, context):
    # Stop unused EC2 instances
    # Delete old snapshots
    # Optimize EBS volumes
    # Scale down unused resources
    pass
```

## 📝 Implementation Checklist

- [ ] Set up cost budgets and alerts
- [ ] Configure resource tagging for cost allocation
- [ ] Implement auto-scaling policies
- [ ] Set up scheduled scaling for off-hours
- [ ] Enable AWS Cost Explorer
- [ ] Configure CloudWatch billing alarms
- [ ] Review and optimize resource requests/limits
- [ ] Consider using Spot instances for non-critical workloads
- [ ] Set up automated resource cleanup
- [ ] Regular cost reviews and optimization

## 🎯 Target Cost Goals

| Environment | Target Monthly Cost | Use Case |
|-------------|-------------------|----------|
| **Development** | $50-80 USD | Single developer, basic features |
| **Testing** | $100-150 USD | CI/CD, automated testing |
| **Staging** | $200-300 USD | Pre-production validation |
| **Production** | $400-600 USD | Live application, high availability |

The current configuration targets the **Testing** environment level with room to scale up or down based on actual usage patterns.