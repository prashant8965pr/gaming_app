# Quick Start Guide

Get the Gaming Platform up and running in under 10 minutes!

## 🚀 Option 1: One-Command Setup (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- 8GB RAM minimum
- 10GB free disk space

### Start Everything

```bash
# Clone the repository
git clone <repository-url>
cd gaming_app

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
# Check status
docker-compose ps
```

That's it! You now have:
- ✅ Backend API running on `http://localhost:8000`
- ✅ PostgreSQL database on `localhost:5432`
- ✅ Redis cache on `localhost:6379`
- ✅ API Documentation at `http://localhost:8000/docs`

---

## 📱 Option 2: Mobile App Development

### Prerequisites
- Flutter SDK 3.0+
- Android Studio / Xcode
- Physical device or emulator

### Quick Start

```bash
# 1. Start backend services
docker-compose up -d

# 2. Navigate to mobile app
cd mobile_app

# 3. Install dependencies
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# 4. Run the app
flutter run
```

### Configure API Endpoint

Edit `mobile_app/lib/core/constants/app_constants.dart`:

```dart
// For Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// For iOS Simulator
// static const String baseUrl = 'http://localhost:8000';

// For Physical Device (use your computer's IP)
// static const String baseUrl = 'http://192.168.1.100:8000';
```

---

## 🛠️ Option 3: Full Development Setup

### Backend Development

```bash
# 1. Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start services (database, redis)
docker-compose up -d postgres redis

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

---

## 🧪 Testing the Setup

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# API Documentation
open http://localhost:8000/docs

# Test authentication (send OTP)
curl -X POST http://localhost:8000/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### Test Mobile App

1. Open app on emulator/device
2. You should see the onboarding screens
3. Try authentication flow
4. Check backend logs for OTP: `docker logs gaming_platform_backend`

---

## 🎮 Sample Test Data

### Test User Credentials
```
Phone: +919876543210
OTP: Check backend logs or use 123456 in development
```

### Test Payment Cards (Razorpay)
```
Card Number: 4111 1111 1111 1111
CVV: 123
Expiry: 12/25
```

### Test UPI
```
UPI ID: success@razorpay
```

---

## 📊 Accessing Services

### Swagger API Documentation
```
http://localhost:8000/docs
```

### ReDoc API Documentation
```
http://localhost:8000/redoc
```

### Database
```bash
# Connect to PostgreSQL
docker exec -it gaming_platform_postgres psql -U postgres -d gaming_platform

# List tables
\dt

# Query users
SELECT * FROM users LIMIT 5;
```

### Redis
```bash
# Connect to Redis
docker exec -it gaming_platform_redis redis-cli

# Check keys
KEYS *

# Get user session
GET user:session:xxx
```

---

## 🔍 Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f gaming_platform_backend
docker logs -f gaming_platform_postgres
docker logs -f gaming_platform_redis

# Mobile app logs
flutter logs
```

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker exec gaming_platform_postgres pg_isready -U postgres

# Redis health
docker exec gaming_platform_redis redis-cli ping
```

---

## 🐛 Common Issues & Solutions

### Issue: Cannot connect to backend from mobile app

**Solution for Android Emulator:**
```dart
// Use 10.0.2.2 instead of localhost
static const String baseUrl = 'http://10.0.2.2:8000';
```

**Solution for iOS Simulator:**
```dart
// Use localhost
static const String baseUrl = 'http://localhost:8000';
```

**Solution for Physical Device:**
```dart
// Use your computer's IP address
static const String baseUrl = 'http://192.168.1.100:8000';

// Also update backend ALLOWED_ORIGINS in .env:
ALLOWED_ORIGINS=http://localhost:3000,http://192.168.1.100:8000
```

### Issue: Database connection failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker logs gaming_platform_postgres
```

### Issue: Port already in use

```bash
# Check what's using port 8000
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Kill the process or change port in docker-compose.yml
```

### Issue: Code generation errors in Flutter

```bash
cd mobile_app

# Clean and regenerate
flutter clean
flutter pub get
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

---

## 🔐 Default Credentials

### Development Environment

#### PostgreSQL
```
Host: localhost
Port: 5432
Database: gaming_platform
User: postgres
Password: postgres
```

#### Redis
```
Host: localhost
Port: 6379
Password: (none in development)
```

⚠️ **Important**: Change these in production!

---

## 📱 Mobile App Features to Test

1. **Authentication**
   - [ ] Phone number login
   - [ ] OTP verification
   - [ ] Profile setup

2. **Wallet**
   - [ ] View balance
   - [ ] Add money (test mode)
   - [ ] Withdraw money
   - [ ] Transaction history

3. **Games**
   - [ ] Browse games
   - [ ] View game details
   - [ ] Join session (mock)

4. **Profile**
   - [ ] Edit profile
   - [ ] Upload avatar
   - [ ] View statistics
   - [ ] KYC verification (mock)

---

## 🚢 Deployment

### Development
```bash
./scripts/deploy.sh development
```

### Staging
```bash
./scripts/deploy.sh staging
```

### Production
```bash
./scripts/deploy.sh production
```

---

## 📚 Next Steps

1. **Read Documentation**
   - [Backend Documentation](docs/API_DOCUMENTATION.md)
   - [Mobile App Documentation](docs/FLUTTER_APP_DOCUMENTATION.md)
   - [Integration Guide](docs/INTEGRATION_GUIDE.md)

2. **Configure Services**
   - Setup AWS S3 for file uploads
   - Configure Razorpay for payments
   - Setup Firebase for push notifications
   - Configure SendGrid for emails

3. **Development**
   - Explore API endpoints in Swagger UI
   - Test mobile app features
   - Review architecture documentation
   - Check project roadmap

---

## 🆘 Need Help?

### Documentation
- [Full Documentation](docs/)
- [API Reference](http://localhost:8000/docs)
- [Integration Guide](docs/INTEGRATION_GUIDE.md)

### Troubleshooting
- [Common Issues](docs/TROUBLESHOOTING.md)
- Check logs: `docker-compose logs -f`
- GitHub Issues

### Support
- Email: dev@gameapp.com
- Slack: #gaming-platform-dev

---

## ⚡ Pro Tips

1. **Use Docker Compose**
   - Simplest way to get started
   - Everything pre-configured
   - One command deployment

2. **Enable Hot Reload**
   - Backend: `--reload` flag in uvicorn
   - Mobile: Built-in Flutter hot reload

3. **Use Separate Terminals**
   - Terminal 1: Docker services
   - Terminal 2: Flutter app
   - Terminal 3: Logs

4. **Bookmark These URLs**
   - API Docs: `http://localhost:8000/docs`
   - Health: `http://localhost:8000/health`

5. **IDE Setup**
   - VSCode: Install Flutter, Python extensions
   - PyCharm/IntelliJ: Configure Python interpreter
   - Android Studio: Configure Flutter SDK

---

## 🎉 You're All Set!

Your gaming platform is now running. Start building amazing features!

```
Backend API:    http://localhost:8000
API Docs:       http://localhost:8000/docs
Database:       localhost:5432
Redis:          localhost:6379
Mobile App:     Run with `flutter run`
```

Happy coding! 🚀

---

**Last Updated**: November 2024
**Version**: 1.0.0
