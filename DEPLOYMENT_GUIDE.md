# Gaming Platform - Complete Deployment Guide

**Version:** 1.0
**Last Updated:** November 18, 2025
**Branch:** `claude/main_v1-019ZqDeywFs9GCL8MsxDs1j7`

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Mobile App Build](#mobile-app-build)
7. [Data Seeding](#data-seeding)
8. [Testing & Verification](#testing--verification)
9. [Production Checklist](#production-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** (recommended) OR individual services:
  - PostgreSQL 15+
  - MongoDB 7+
  - Redis 7+
- **Node.js** 18+ and npm
- **Python** 3.10+
- **Flutter** 3.16+ (for mobile app)
- **Git**

### Required Services

- **Email Service:** SendGrid account (or alternative)
- **SMS Service:** Twilio account (optional)
- **Payment Gateway:** Razorpay account (India)
- **Cloud Storage:** AWS S3 bucket (for file uploads)
- **Push Notifications:** Firebase Cloud Messaging
- **Domain & SSL:** Valid domain with SSL certificate

### System Requirements

**Minimum (Development):**
- 4 GB RAM
- 2 CPU cores
- 20 GB disk space

**Recommended (Production):**
- 8 GB RAM
- 4 CPU cores
- 100 GB disk space
- Load balancer
- CDN for static assets

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd gaming_app
git checkout claude/main_v1-019ZqDeywFs9GCL8MsxDs1j7
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend (User App):**
```bash
cd frontend
npm install
```

**Frontend (Admin Panel):**
```bash
cd frontend-admin
npm install
```

**Mobile App:**
```bash
cd mobile_app
flutter pub get
```

---

## Database Setup

### Option A: Docker Compose (Recommended)

```bash
# Start all database services
cd /home/user/gaming_app
docker-compose up -d postgres mongodb redis

# Verify services are running
docker-compose ps
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis
```

### Option B: Manual Installation

**PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-15

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE gaming_platform;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE gaming_platform TO postgres;
\q
```

**MongoDB:**
```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Redis:**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Start service
sudo systemctl start redis
sudo systemctl enable redis
```

### Database Configuration

Create `.env` file in backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gaming_platform

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=gaming_platform

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## Backend Deployment

### 1. Environment Configuration

Edit `backend/.env` with all required settings:

```env
# Application
APP_NAME=Gaming Platform API
APP_VERSION=1.0.0
DEBUG=False  # Set to False in production
ENVIRONMENT=production

# Security
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database URLs (as configured above)
DATABASE_URL=postgresql+asyncpg://...
MONGODB_URL=mongodb://...
REDIS_URL=redis://...

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# Email (SendGrid)
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Payment Gateway (Razorpay)
RAZORPAY_KEY_ID=<your-razorpay-key-id>
RAZORPAY_KEY_SECRET=<your-razorpay-key-secret>

# AWS S3
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_S3_BUCKET=gaming-platform-uploads
AWS_REGION=us-east-1

# Firebase Cloud Messaging
FCM_SERVER_KEY=<your-fcm-server-key>

# SMS (Optional - Twilio)
TWILIO_ACCOUNT_SID=<your-account-sid>
TWILIO_AUTH_TOKEN=<your-auth-token>
TWILIO_PHONE_NUMBER=<your-twilio-number>
```

### 2. Run Database Migrations

```bash
cd backend
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

### 3. Seed Initial Data

Run seed scripts in this order:

```bash
# 1. Create admin user (REQUIRED)
python scripts/seed_admin_user.py

# 2. Seed game catalog (REQUIRED)
python scripts/seed_games.py

# 3. Seed quiz categories (REQUIRED for Quiz game)
python scripts/seed_quiz_categories.py

# 4. Seed quiz questions (REQUIRED for Quiz game)
python scripts/seed_quiz_questions.py
```

**Important:** Save the admin credentials displayed by `seed_admin_user.py`:
- Username: `admin`
- Password: `Admin@123` (change immediately!)

### 4. Start Backend Server

**Development:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Production (with Gunicorn):**
```bash
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**With systemd (recommended for production):**

Create `/etc/systemd/system/gaming-backend.service`:
```ini
[Unit]
Description=Gaming Platform Backend
After=network.target postgresql.service mongodb.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/gaming_app/backend
Environment="PATH=/var/www/gaming_app/backend/venv/bin"
ExecStart=/var/www/gaming_app/backend/venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start gaming-backend
sudo systemctl enable gaming-backend
sudo systemctl status gaming-backend
```

### 5. Verify Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API docs
# Open browser: http://localhost:8000/docs
```

---

## Frontend Deployment

### User Frontend (Next.js)

**1. Configure Environment:**

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_API_BASE_PATH=/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

**2. Build:**
```bash
cd frontend
npm run build
```

**3. Start (Development):**
```bash
npm run dev
```

**4. Start (Production):**
```bash
npm run start
```

**5. Deploy with PM2:**
```bash
npm install -g pm2
pm2 start npm --name "gaming-frontend" -- start
pm2 save
pm2 startup
```

### Admin Panel (Next.js)

**1. Configure Environment:**

Create `frontend-admin/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
```

**2. Build & Start:**
```bash
cd frontend-admin
npm run build
npm run start
# Or with PM2:
pm2 start npm --name "gaming-admin" -- start
```

### Nginx Configuration

Create `/etc/nginx/sites-available/gaming-platform`:

```nginx
# User Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Admin Panel
server {
    listen 443 ssl http2;
    server_name admin.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/gaming-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Mobile App Build

### Android Build

**1. Configure:**

Edit `mobile_app/android/app/build.gradle`:
```gradle
android {
    defaultConfig {
        applicationId "com.yourcompany.gamingapp"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
        }
    }
}
```

**2. Create keystore:**
```bash
keytool -genkey -v -keystore ~/gaming-app-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias gaming-app
```

**3. Configure signing:**

Create `mobile_app/android/key.properties`:
```properties
storePassword=<your-keystore-password>
keyPassword=<your-key-password>
keyAlias=gaming-app
storeFile=<path-to-your-keystore>/gaming-app-key.jks
```

**4. Build APK/App Bundle:**
```bash
cd mobile_app

# Build APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### iOS Build

**1. Configure:**

Edit `mobile_app/ios/Runner/Info.plist` with your bundle ID.

**2. Open in Xcode:**
```bash
cd mobile_app
open ios/Runner.xcworkspace
```

**3. Configure signing in Xcode:**
- Select Runner target
- Go to Signing & Capabilities
- Select your team
- Configure bundle identifier

**4. Build:**
```bash
flutter build ios --release
```

**5. Archive and Submit:**
- In Xcode: Product → Archive
- Submit to App Store

---

## Data Seeding

Run these scripts in order after database setup:

### 1. Admin User
```bash
cd backend
python scripts/seed_admin_user.py
```

**Output:**
```
✅ Admin user created successfully!
   Username: admin
   Email: admin@gamingplatform.com
   Password: Admin@123
   ⚠️  IMPORTANT: Change the default password immediately!

✅ Created 3 demo users
   Demo credentials:
   - player1 / Player1@123
   - player2 / Player2@123
   - player3 / Player3@123
```

### 2. Game Catalog
```bash
python scripts/seed_games.py
```

**Output:**
```
✅ Game Catalog Seeding Complete!
Total Games: 6
Active Games: 1
Coming Soon: 5

📝 Active Games:
   ✅ Quiz Master

🔜 Coming Soon:
   ⏳ Ludo Classic
   ⏳ Indian Rummy
   ⏳ Texas Hold'em Poker
   ⏳ Carrom Board
   ⏳ 8-Ball Pool
```

### 3. Quiz Categories
```bash
python scripts/seed_quiz_categories.py
```

**Output:**
```
✅ Seeding complete!
Created: 10
Total: 10
```

### 4. Quiz Questions
```bash
python scripts/seed_quiz_questions.py
```

**Output:**
```
✅ Seeding complete!
Total Categories: 10
Total Questions: 1200+

  General Knowledge: 150 questions
  Science & Nature: 150 questions
  History: 150 questions
  ... (and more)
```

---

## Testing & Verification

### Backend API Testing

```bash
cd backend

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v --cov

# Run all tests with coverage
pytest --cov=. --cov-report=html
```

### Frontend Testing

```bash
cd frontend

# Run E2E tests
npm run test:e2e

# Run component tests
npm run test
```

### API Endpoint Verification

```bash
# Health check
curl https://api.yourdomain.com/health

# Get games catalog
curl https://api.yourdomain.com/api/v1/games

# Login as admin
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'
```

### Load Testing

```bash
cd backend
locust -f tests/load/locustfile.py --host=https://api.yourdomain.com
```

Open browser: `http://localhost:8089`

---

## Production Checklist

### Security

- [ ] Change default admin password
- [ ] Generate strong `SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Set `DEBUG=False` in production
- [ ] Enable SSL/HTTPS for all domains
- [ ] Configure firewall (allow only 80, 443, SSH)
- [ ] Set up fail2ban for SSH protection
- [ ] Configure rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Secure database passwords
- [ ] Rotate API keys regularly

### Performance

- [ ] Enable Redis caching
- [ ] Configure CDN for static assets
- [ ] Set up database connection pooling
- [ ] Enable gzip compression in Nginx
- [ ] Optimize images and assets
- [ ] Configure database indexes
- [ ] Set up database backups
- [ ] Monitor memory usage

### Monitoring

- [ ] Set up Sentry for error tracking
- [ ] Configure application logging
- [ ] Set up database monitoring
- [ ] Monitor API response times
- [ ] Set up uptime monitoring
- [ ] Configure alerts for critical errors
- [ ] Track user analytics

### Compliance

- [ ] Add Terms of Service
- [ ] Add Privacy Policy
- [ ] Add Cookie Policy
- [ ] Implement GDPR compliance (if EU users)
- [ ] Add age verification (18+)
- [ ] Implement responsible gaming features
- [ ] Configure data retention policies

### Backups

- [ ] Set up automated database backups
- [ ] Test backup restoration
- [ ] Configure backup retention policy
- [ ] Back up environment files securely
- [ ] Document disaster recovery plan

---

## Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to PostgreSQL
```
Solution:
1. Check service status: sudo systemctl status postgresql
2. Verify credentials in .env
3. Check PostgreSQL logs: sudo journalctl -u postgresql
4. Ensure pg_hba.conf allows connections
```

### Migration Errors

**Problem:** Alembic migration fails
```
Solution:
1. Check current version: alembic current
2. Rollback if needed: alembic downgrade -1
3. Check migration file for errors
4. Ensure database user has correct permissions
```

### Frontend Build Errors

**Problem:** Next.js build fails
```
Solution:
1. Clear cache: rm -rf .next node_modules
2. Reinstall: npm install
3. Check environment variables
4. Verify API URL is accessible
```

### Mobile App Build Errors

**Problem:** Flutter build fails
```
Solution:
1. Clean build: flutter clean
2. Get dependencies: flutter pub get
3. Check Flutter version: flutter --version
4. Update if needed: flutter upgrade
```

### API 500 Errors

**Problem:** Backend returning 500 errors
```
Solution:
1. Check backend logs: journalctl -u gaming-backend
2. Verify database is running
3. Check .env configuration
4. Ensure all migrations are applied
5. Verify external services (SendGrid, Razorpay) are configured
```

---

## Support & Maintenance

### Log Locations

- **Backend:** `/var/log/gaming-backend/`
- **Nginx:** `/var/log/nginx/`
- **PostgreSQL:** `/var/log/postgresql/`
- **System:** `journalctl -u <service-name>`

### Useful Commands

```bash
# Check all services
sudo systemctl status gaming-backend
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status mongodb
sudo systemctl status redis

# View logs
sudo journalctl -u gaming-backend -f
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gaming-backend
sudo systemctl restart nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python
ps aux | grep node
```

---

## Next Steps After Deployment

1. **Change Admin Password** - Login and change default password
2. **Create Test Accounts** - Use demo users or create new ones
3. **Test Quiz Game** - Play complete game session
4. **Verify Payments** - Test deposit and withdrawal
5. **Submit Mobile Apps** - Upload to Play Store and App Store
6. **Marketing** - Launch marketing campaigns
7. **Monitor** - Watch logs and metrics for first 24 hours

---

## Quick Launch Checklist (TL;DR)

```bash
# 1. Setup databases
docker-compose up -d postgres mongodb redis

# 2. Configure backend
cd backend
cp .env.example .env
# Edit .env with your credentials

# 3. Run migrations and seed
alembic upgrade head
python scripts/seed_admin_user.py
python scripts/seed_games.py
python scripts/seed_quiz_categories.py
python scripts/seed_quiz_questions.py

# 4. Start backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 5. Build and start frontend
cd ../frontend
npm install
npm run build
npm run start

# 6. Build and start admin
cd ../frontend-admin
npm install
npm run build
npm run start

# 7. Build mobile apps
cd ../mobile_app
flutter build apk --release
flutter build ios --release

# ✅ Platform is live!
```

---

**Document Version:** 1.0
**Last Updated:** November 18, 2025
**Status:** Production Ready

For questions or issues, check the troubleshooting section or review application logs.
