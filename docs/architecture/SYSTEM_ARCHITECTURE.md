# System Architecture

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────┬─────────────┬─────────────┬────────────────────────┤
│ Flutter App │  Web App    │ Admin Panel │   3rd Party (Payment) │
│  (Mobile)   │  (Next.js)  │  (Next.js)  │   Gateways, etc.      │
└──────┬──────┴──────┬──────┴──────┬──────┴────────────────────────┘
       │             │             │
       └─────────────┼─────────────┘
                     │
       ┌─────────────▼──────────────┐
       │      API GATEWAY           │
       │    (Kong / Nginx)          │
       │  - Rate Limiting           │
       │  - Authentication          │
       │  - Load Balancing          │
       └─────────────┬──────────────┘
                     │
       ┌─────────────▼──────────────────────────────────┐
       │           BACKEND SERVICES (FastAPI)           │
       ├────────────────────────────────────────────────┤
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ User Service │  │ Auth Service           │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Game Engine  │  │ Matchmaking Service    │ │
       │  │   Service    │  │  (AI-powered)          │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Wallet &     │  │ Payment Service        │ │
       │  │ Transaction  │  │ (Razorpay/Cashfree)    │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Tournament   │  │ Leaderboard Service    │ │
       │  │   Service    │  │                        │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Fraud &      │  │ Notification Service   │ │
       │  │ Fairplay AI  │  │ (Push/SMS/Email)       │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Referral     │  │ Analytics Service      │ │
       │  │   Service    │  │                        │ │
       │  └──────────────┘  └────────────────────────┘ │
       └─────────────┬──────────────────────────────────┘
                     │
       ┌─────────────▼──────────────────────────────────┐
       │              REAL-TIME LAYER                   │
       │         WebSocket / Socket.IO                  │
       │  - Game state synchronization                  │
       │  - Live tournament updates                     │
       │  - Real-time notifications                     │
       └─────────────┬──────────────────────────────────┘
                     │
       ┌─────────────▼──────────────────────────────────┐
       │              DATA LAYER                        │
       ├────────────────────────────────────────────────┤
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ PostgreSQL   │  │ MongoDB                │ │
       │  │ (Users,      │  │ (Game Records,         │ │
       │  │  Wallet,     │  │  Match History,        │ │
       │  │  Transactions)│ │  Game States)          │ │
       │  └──────────────┘  └────────────────────────┘ │
       │                                                │
       │  ┌──────────────┐  ┌────────────────────────┐ │
       │  │ Redis        │  │ Elasticsearch          │ │
       │  │ (Cache,      │  │ (Logs, Search,         │ │
       │  │  Session,    │  │  Analytics)            │ │
       │  │  Leaderboard)│  │                        │ │
       │  └──────────────┘  └────────────────────────┘ │
       └────────────────────────────────────────────────┘
                     │
       ┌─────────────▼──────────────────────────────────┐
       │           MESSAGE QUEUE                        │
       │         RabbitMQ / Kafka                       │
       │  - Event streaming                             │
       │  - Async task processing                       │
       │  - Service communication                       │
       └────────────────────────────────────────────────┘
                     │
       ┌─────────────▼──────────────────────────────────┐
       │        MONITORING & LOGGING                    │
       │  - Prometheus (Metrics)                        │
       │  - Grafana (Visualization)                     │
       │  - ELK Stack (Logging)                         │
       │  - Sentry (Error tracking)                     │
       └────────────────────────────────────────────────┘
```

## 2. Microservices Architecture

### 2.1 User Service
**Responsibility**: User management, authentication, profile
**Port**: 8001
**Database**: PostgreSQL
**Key Features**:
- User registration (OTP, Email, Social)
- Authentication & Authorization (JWT)
- Profile management
- KYC verification
- Device binding
- Session management

### 2.2 Game Engine Service
**Responsibility**: Game logic, state management, gameplay
**Port**: 8002
**Database**: MongoDB
**Key Features**:
- Multi-game support (Ludo, Carrom, etc.)
- Real-time game state management
- Game rules enforcement
- Bot players (fallback)
- Game result calculation
- Anti-cheat integration

### 2.3 Matchmaking Service
**Responsibility**: AI-powered player matching
**Port**: 8003
**Database**: Redis (for quick lookups)
**Key Features**:
- Skill-based matching (ELO rating)
- Queue management
- Room creation
- Match history analysis
- Fair play pairing
- Bot assignment when needed

### 2.4 Wallet Service
**Responsibility**: Wallet management, balance tracking
**Port**: 8004
**Database**: PostgreSQL (ACID compliance critical)
**Key Features**:
- Multi-wallet system (Cash, Winnings, Bonus)
- Balance management
- Transaction logging
- Wallet restrictions
- Bonus calculation
- Tax deduction (TDS)

### 2.5 Payment Service
**Responsibility**: Payment gateway integration
**Port**: 8005
**Database**: PostgreSQL
**Key Features**:
- Add money (UPI, Card, Netbanking)
- Withdrawal processing
- Payment gateway integration (Razorpay, Cashfree)
- Webhook handling
- Refund management
- Payment reconciliation

### 2.6 Tournament Service
**Responsibility**: Tournament management
**Port**: 8006
**Database**: PostgreSQL + MongoDB
**Key Features**:
- Tournament creation
- Player registration
- Prize pool calculation
- Leaderboard management
- Auto-payout
- Tournament types (Knockout, League, Timed)

### 2.7 Fraud & Fairplay Service
**Responsibility**: AI-powered fraud detection
**Port**: 8007
**Database**: MongoDB + Elasticsearch
**Key Features**:
- Multi-accounting detection
- Suspicious gameplay detection
- Device fingerprinting
- IP analysis
- Win pattern analysis
- Auto-ban system
- ML model integration

### 2.8 Notification Service
**Responsibility**: All notifications
**Port**: 8008
**Database**: MongoDB
**Key Features**:
- Push notifications (FCM)
- SMS (Twilio/MSG91)
- Email notifications
- In-app notifications
- Notification templates
- Scheduling

### 2.9 Referral Service
**Responsibility**: Referral program management
**Port**: 8009
**Database**: PostgreSQL
**Key Features**:
- Referral code generation
- Referral tracking
- Multi-level rewards
- Bonus distribution
- Referral analytics

### 2.10 Analytics Service
**Responsibility**: Data analytics and reporting
**Port**: 8010
**Database**: Elasticsearch + BigQuery
**Key Features**:
- User behavior tracking
- Game analytics
- Revenue reports
- Cohort analysis
- Real-time dashboards
- Data export

### 2.11 Leaderboard Service
**Responsibility**: Real-time leaderboards
**Port**: 8011
**Database**: Redis
**Key Features**:
- Global leaderboards
- Game-specific leaderboards
- Tournament leaderboards
- Weekly/Monthly rankings
- Redis sorted sets for performance

## 3. Database Design Strategy

### PostgreSQL (Primary relational DB)
**Use Cases**:
- Users table
- Wallets & Transactions
- KYC records
- Tournaments
- Referrals
- Admin users

**Why**: ACID compliance, complex joins, financial data integrity

### MongoDB (Document store)
**Use Cases**:
- Game records & history
- Match details
- Player statistics
- Logs
- Notification history

**Why**: Flexible schema, high write throughput, complex nested data

### Redis (In-memory cache)
**Use Cases**:
- Session management
- Leaderboards (sorted sets)
- Cache layer
- Rate limiting
- Real-time data

**Why**: Ultra-fast reads/writes, TTL support, data structures

### Elasticsearch
**Use Cases**:
- Log aggregation
- Search functionality
- Analytics
- Fraud pattern detection

**Why**: Full-text search, log analysis, aggregations

## 4. Communication Patterns

### Synchronous (REST APIs)
- Client to API Gateway
- Service-to-service for critical operations
- Admin panel operations

### Asynchronous (Message Queue)
- Payment callbacks
- Notification dispatch
- Analytics events
- Fraud detection jobs

### Real-Time (WebSocket)
- Game state updates
- Live leaderboards
- Tournament updates
- In-game chat

## 5. Security Architecture

### Authentication Flow
```
User → Login Request → Auth Service
     → Verify OTP/Password
     → Generate JWT (Access + Refresh)
     → Return tokens
     → Client stores in secure storage
```

### Authorization
- Role-based access control (RBAC)
- JWT token validation
- API key for service-to-service
- Rate limiting per user/IP

### Data Security
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII data masking
- Regular security audits

## 6. Scalability Strategy

### Horizontal Scaling
- All services stateless
- Load balancer distribution
- Auto-scaling based on metrics

### Database Scaling
- PostgreSQL: Read replicas
- MongoDB: Sharding
- Redis: Cluster mode

### Caching Strategy
- Multi-level caching (Redis, CDN)
- Cache invalidation strategies
- Cache-aside pattern

## 7. High Availability

### Redundancy
- Multi-region deployment
- Database replication
- Service redundancy (min 3 instances)

### Disaster Recovery
- Automated backups (hourly)
- Point-in-time recovery
- Backup testing
- RTO: 1 hour, RPO: 15 minutes

## 8. Monitoring & Observability

### Metrics (Prometheus)
- Service health
- API latency
- Error rates
- Resource usage

### Logging (ELK Stack)
- Centralized logging
- Log levels
- Structured logging
- Log retention (90 days)

### Tracing (Jaeger)
- Distributed tracing
- Request flow visualization
- Performance bottlenecks

### Alerts
- PagerDuty integration
- Slack notifications
- Email alerts
- Alert severity levels

## 9. DevOps Architecture

### CI/CD Pipeline
```
Git Push → GitHub Actions
        → Run Tests
        → Build Docker Image
        → Push to Registry
        → Deploy to Staging
        → Run Integration Tests
        → Deploy to Production (Manual approval)
```

### Infrastructure as Code
- Terraform for cloud resources
- Kubernetes manifests
- Helm charts
- Ansible for configuration

### Environments
- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment
- **DR**: Disaster recovery

## 10. Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time | < 100ms | < 500ms |
| Real-time Game Latency | < 50ms | < 150ms |
| Database Query Time | < 20ms | < 100ms |
| Concurrent Users | 100K+ | 500K+ |
| Uptime | 99.9% | 99.5% |
| Payment Processing | < 2s | < 5s |

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Owner**: Engineering Team
