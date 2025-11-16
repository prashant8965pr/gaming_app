# Deployment & DevOps Architecture

## Overview

This document describes the complete deployment architecture, CI/CD pipelines, monitoring, and operational procedures.

---

## 1. Environment Strategy

### Development Environment
**Purpose**: Local development and testing

**Infrastructure**:
- Local Docker Compose setup
- PostgreSQL, MongoDB, Redis containers
- Mock payment gateway
- Local file storage

**Access**:
- All developers
- No production data

---

### Staging Environment
**Purpose**: Pre-production testing and QA

**Infrastructure**:
- AWS EC2 (smaller instances)
- RDS PostgreSQL (db.t3.medium)
- DocumentDB (1 instance)
- ElastiCache Redis (cache.t3.micro)
- Real payment gateway (test mode)

**URL**: `https://staging-api.gamingplatform.com`

**Access**:
- Development team
- QA team
- Product team

**Data**:
- Sanitized production data copy
- Test users

---

### Production Environment
**Purpose**: Live user-facing platform

**Infrastructure**:
- AWS EC2 Auto Scaling Group
- RDS PostgreSQL (db.r6g.xlarge) with Multi-AZ
- DocumentDB (3-node cluster)
- ElastiCache Redis (cluster mode)
- S3 + CloudFront CDN
- Load Balancer (Application LB)

**URL**: `https://api.gamingplatform.com`

**Access**:
- DevOps team (restricted)
- On-call engineers

---

## 2. Architecture Diagram

```
                    ┌─────────────────┐
                    │   CloudFlare    │
                    │   (DDoS, CDN)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Route 53 (DNS) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│ CloudFront CDN │  │  Application    │  │   Static Web   │
│  (S3 Assets)   │  │  Load Balancer  │  │   (S3 + CF)    │
└────────────────┘  └────────┬────────┘  └────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐ ┌───────▼──────┐ ┌──────▼──────┐
    │   Backend    │ │   Backend    │ │   Backend   │
    │  Instance 1  │ │  Instance 2  │ │  Instance 3 │
    │  (EC2 Auto   │ │  (EC2 Auto   │ │  (EC2 Auto  │
    │   Scaling)   │ │   Scaling)   │ │   Scaling)  │
    └───────┬──────┘ └───────┬──────┘ └──────┬──────┘
            │                │                │
            └────────────────┼────────────────┘
                             │
        ┌────────────────────┼────────────────────────┐
        │                    │                        │
┌───────▼─────────┐  ┌───────▼──────────┐  ┌─────────▼────────┐
│   PostgreSQL    │  │   MongoDB        │  │   Redis Cluster  │
│   (RDS Multi-AZ)│  │   (DocumentDB)   │  │   (ElastiCache)  │
│   Master/Replica│  │   3-node cluster │  │   Cluster Mode   │
└─────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 3. AWS Infrastructure

### VPC Configuration

```
VPC: 10.0.0.0/16

Subnets:
- Public Subnet 1 (AZ-a): 10.0.1.0/24  → Load Balancer
- Public Subnet 2 (AZ-b): 10.0.2.0/24  → Load Balancer
- Private Subnet 1 (AZ-a): 10.0.11.0/24 → App Servers
- Private Subnet 2 (AZ-b): 10.0.12.0/24 → App Servers
- Private Subnet 3 (AZ-a): 10.0.21.0/24 → Databases
- Private Subnet 4 (AZ-b): 10.0.22.0/24 → Databases

NAT Gateway: For private subnets internet access
Internet Gateway: For public subnets
```

---

### EC2 Auto Scaling

**Launch Template**:
```yaml
Instance Type: t3.large (2 vCPU, 8GB RAM)
AMI: Ubuntu 22.04 LTS
Storage: 50GB GP3 SSD

User Data:
#!/bin/bash
apt-get update
apt-get install -y docker.io
systemctl start docker
docker pull <ecr-repo>/backend:latest
docker run -d -p 8000:8000 <ecr-repo>/backend:latest
```

**Auto Scaling Policy**:
```yaml
Minimum: 2 instances
Desired: 3 instances
Maximum: 10 instances

Scale Out (add instance):
  - CPU > 70% for 5 minutes
  - OR Active connections > 5000

Scale In (remove instance):
  - CPU < 30% for 10 minutes
  - AND Active connections < 2000
```

---

### Application Load Balancer

**Configuration**:
```yaml
Scheme: Internet-facing
Listeners:
  - Port 80 (HTTP) → Redirect to 443
  - Port 443 (HTTPS) → Target Group

Health Check:
  Path: /health
  Interval: 30 seconds
  Timeout: 5 seconds
  Healthy threshold: 2
  Unhealthy threshold: 3

Sticky Sessions: Enabled (for WebSocket)
```

---

### RDS PostgreSQL

**Configuration**:
```yaml
Engine: PostgreSQL 15.4
Instance Class: db.r6g.xlarge (4 vCPU, 32GB RAM)
Storage: 500GB GP3 SSD, Auto-scaling enabled
Multi-AZ: Yes (automatic failover)
Backup:
  Retention: 30 days
  Window: 03:00-04:00 UTC
  Automated snapshots: Daily
Read Replicas: 2 (for read scaling)

Parameter Group:
  max_connections: 500
  shared_buffers: 8GB
  work_mem: 64MB
```

---

### DocumentDB (MongoDB)

**Configuration**:
```yaml
Engine: MongoDB 5.0 compatible
Instance Class: db.r6g.large
Cluster: 3 nodes (1 primary, 2 replicas)
Storage: 200GB, Auto-scaling enabled
Backup:
  Retention: 7 days
  Window: 04:00-05:00 UTC
```

---

### ElastiCache Redis

**Configuration**:
```yaml
Engine: Redis 7.0
Node Type: cache.r6g.large (2 vCPU, 13GB RAM)
Cluster Mode: Enabled
Shards: 3
Replicas per shard: 2
Total nodes: 9 (3 primary + 6 replicas)

Snapshot:
  Retention: 7 days
  Window: 05:00-06:00 UTC
```

---

### S3 Buckets

**Buckets**:
1. `gaming-app-uploads-prod`: User uploads (avatars, KYC docs)
2. `gaming-app-static-prod`: Static assets
3. `gaming-app-backups-prod`: Database backups
4. `gaming-app-logs-prod`: Log archives

**Lifecycle Policies**:
```yaml
gaming-app-logs-prod:
  - Move to Glacier after 90 days
  - Delete after 365 days

gaming-app-backups-prod:
  - Delete after 90 days
```

**CORS Configuration** (for uploads):
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://app.gamingplatform.com"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

---

## 4. CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: gaming-app-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster gaming-app-cluster \
            --service backend-service \
            --force-new-deployment

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production completed!'
```

---

### Deployment Process

```
1. Developer commits to `develop` branch
   ↓
2. GitHub Actions runs tests
   ↓
3. Tests pass → Merge to `main` (via PR)
   ↓
4. Auto-deploy to Staging
   ↓
5. QA team tests on Staging
   ↓
6. Manual approval required
   ↓
7. Deploy to Production
   ↓
8. Health checks
   ↓
9. Slack notification
```

---

## 5. Monitoring & Alerting

### Prometheus + Grafana

**Metrics Collected**:
- API request rate
- Response time (p50, p95, p99)
- Error rate
- Database query time
- WebSocket connections
- Cache hit rate
- Queue size

**Sample Dashboard**:
```
┌─────────────────────────────────────────────┐
│  API Response Time (p95)                    │
│  [Line graph showing 95th percentile]       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Active Users (Real-time)                   │
│  Current: 5,234                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Error Rate                                 │
│  [Line graph with threshold line at 1%]     │
└─────────────────────────────────────────────┘
```

---

### Sentry

**Configuration**:
```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
    integrations=[FastApiIntegration()],
)
```

**Alerts**:
- New error type detected
- Error spike (>100 errors in 5 min)
- Performance degradation

---

### CloudWatch

**Alarms**:
```yaml
High CPU Utilization:
  Metric: CPUUtilization
  Threshold: > 80%
  Duration: 5 minutes
  Action: SNS notification + Auto-scale

Database Connection Errors:
  Metric: DatabaseConnections
  Threshold: > 90% of max
  Action: SNS notification

Disk Space Low:
  Metric: DiskSpaceUtilization
  Threshold: > 85%
  Action: SNS notification
```

---

### ELK Stack

**Log Aggregation**:
```
Application → Filebeat → Logstash → Elasticsearch → Kibana
```

**Log Format** (JSON):
```json
{
  "timestamp": "2025-01-16T10:30:00Z",
  "level": "ERROR",
  "service": "user_service",
  "endpoint": "/api/v1/users/profile",
  "user_id": "uuid",
  "error": "Database connection timeout",
  "trace_id": "xyz123",
  "duration_ms": 5000
}
```

---

## 6. Backup & Disaster Recovery

### Backup Strategy

**PostgreSQL**:
```yaml
Automated Backups:
  Frequency: Daily
  Retention: 30 days
  Window: 03:00-04:00 UTC

Manual Snapshots:
  Before major releases
  Retention: 90 days

Point-in-Time Recovery:
  Enabled
  Recovery window: 30 days
```

**MongoDB**:
```yaml
Automated Snapshots:
  Frequency: Daily
  Retention: 7 days

Export to S3:
  Frequency: Weekly
  Retention: 30 days
```

**Redis**:
```yaml
Snapshots:
  Frequency: Every 6 hours
  Retention: 7 days

AOF (Append-Only File):
  Enabled
  Fsync: everysec
```

---

### Disaster Recovery Plan

**RTO (Recovery Time Objective)**: 1 hour
**RPO (Recovery Point Objective)**: 15 minutes

**Procedure**:
1. **Detect**: Monitoring alerts → On-call engineer paged
2. **Assess**: Determine severity (P1/P2/P3)
3. **Communicate**: Update status page
4. **Recover**:
   - Database: Restore from snapshot or promote replica
   - Application: Rollback to previous version
   - Cache: Clear and rebuild
5. **Verify**: Run health checks
6. **Post-mortem**: Document incident

---

## 7. Security

### SSL/TLS

**Certificate**:
- Provider: AWS Certificate Manager (ACM)
- Type: Wildcard (*.gamingplatform.com)
- Auto-renewal: Yes

**Configuration**:
```nginx
# Nginx config
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

### Secrets Management

**AWS Secrets Manager**:
```yaml
Secrets:
  - /production/database/password
  - /production/jwt/secret_key
  - /production/razorpay/key_secret
  - /production/twilio/auth_token

Rotation:
  Database passwords: Every 90 days
  API keys: Manual rotation
```

**Access**:
```python
# Python example
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='/production/database/password')
```

---

### Network Security

**Security Groups**:
```yaml
Load Balancer:
  Inbound:
    - Port 80 (HTTP) from 0.0.0.0/0
    - Port 443 (HTTPS) from 0.0.0.0/0
  Outbound: All

Application Servers:
  Inbound:
    - Port 8000 from Load Balancer SG
  Outbound: All

Database:
  Inbound:
    - Port 5432 from Application Servers SG
  Outbound: None
```

---

### DDoS Protection

**CloudFlare**:
- Rate limiting: 100 req/min per IP
- Bot protection
- Web Application Firewall (WAF)

**AWS Shield**:
- Standard: Enabled by default
- Advanced: Optional ($3000/month)

---

## 8. Performance Optimization

### CDN (CloudFront)

**Configuration**:
```yaml
Origins:
  - S3 bucket (static assets)
  - Load Balancer (API)

Cache Behavior:
  /static/*: Cache for 1 year
  /api/*: No cache
  /images/*: Cache for 1 week

Geo Restriction: None (global)
Price Class: All edge locations
```

---

### API Caching

**Redis Cache Strategy**:
```python
# Cache-aside pattern
def get_user_profile(user_id):
    cache_key = f"user:{user_id}:profile"

    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss, query DB
    profile = db.query(User).filter(User.id == user_id).first()

    # Store in cache (10 min TTL)
    redis.setex(cache_key, 600, json.dumps(profile))

    return profile
```

---

### Database Optimization

**Connection Pooling**:
```python
# SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Query Optimization**:
- Indexes on frequently queried columns
- Avoid N+1 queries (use joins)
- Use EXPLAIN ANALYZE for slow queries

---

## 9. Scaling Plan

### Vertical Scaling
**Current → Future**:
- EC2: t3.large → t3.xlarge
- RDS: db.r6g.xlarge → db.r6g.2xlarge
- Redis: cache.r6g.large → cache.r6g.xlarge

---

### Horizontal Scaling

**Auto-Scaling Triggers**:
```yaml
Scale Out:
  Condition: CPU > 70% OR Requests > 10K/min
  Action: Add 1 instance
  Cooldown: 5 minutes

Scale In:
  Condition: CPU < 30% AND Requests < 3K/min
  Action: Remove 1 instance
  Cooldown: 10 minutes
```

---

### Database Sharding (Future)

**Strategy**: Shard by `user_id`
```python
# Shard 0: user_id % 4 == 0
# Shard 1: user_id % 4 == 1
# Shard 2: user_id % 4 == 2
# Shard 3: user_id % 4 == 3

def get_shard(user_id):
    return user_id % 4
```

---

## 10. Rollback Procedure

### Application Rollback

**Steps**:
1. Identify bad deployment version
2. Update ECS task definition to previous version
3. Force new deployment
4. Monitor health checks
5. Verify functionality

**Command**:
```bash
# Rollback to previous version
aws ecs update-service \
  --cluster gaming-app-cluster \
  --service backend-service \
  --task-definition backend-task:42  # Previous version

# Monitor rollout
aws ecs describe-services \
  --cluster gaming-app-cluster \
  --services backend-service
```

---

### Database Rollback

**Migration Rollback**:
```bash
# Using Alembic (Python)
alembic downgrade -1  # Rollback last migration

# Verify database state
alembic current
```

---

## 11. Cost Optimization

### Strategies

1. **Reserved Instances**: 40% savings on EC2/RDS
2. **Spot Instances**: For non-critical background jobs
3. **S3 Lifecycle**: Move old files to Glacier
4. **Right-sizing**: Monitor and adjust instance sizes
5. **Auto-scaling**: Scale down during off-peak

### Cost Breakdown (Monthly)

| Service | Cost |
|---------|------|
| EC2 (3x t3.large) | $225 |
| RDS PostgreSQL | $450 |
| DocumentDB | $350 |
| ElastiCache Redis | $250 |
| S3 + CloudFront | $100 |
| Load Balancer | $25 |
| Data Transfer | $150 |
| Monitoring | $100 |
| **Total** | **~$1,650** |

---

## 12. Runbook

### Common Operations

#### Deploy New Version
```bash
# 1. Build and push image
docker build -t backend:v1.2.0 .
docker tag backend:v1.2.0 <ecr-repo>/backend:v1.2.0
docker push <ecr-repo>/backend:v1.2.0

# 2. Update ECS
aws ecs update-service --cluster gaming-app-cluster \
  --service backend-service --force-new-deployment

# 3. Monitor
watch -n 5 'aws ecs describe-services --cluster gaming-app-cluster --services backend-service'
```

---

#### Scale Up Manually
```bash
# Increase desired count
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name backend-asg \
  --desired-capacity 6
```

---

#### Database Maintenance
```bash
# Take manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier gaming-db-prod \
  --db-snapshot-identifier manual-snapshot-2025-01-16

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier gaming-db-restored \
  --db-snapshot-identifier manual-snapshot-2025-01-16
```

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Review Cycle**: Monthly
**On-Call Rotation**: 24/7 coverage required
