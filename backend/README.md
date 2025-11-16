# Gaming Platform Backend API

FastAPI-based backend for the multi-game skill gaming platform.

## 🚀 Phase 1 Complete!

This implementation includes:
- ✅ User Authentication (OTP-based)
- ✅ User Profile Management
- ✅ JWT Token Authentication
- ✅ Database Models (PostgreSQL)
- ✅ Error Handling & Logging
- ✅ Docker Setup

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL 15+ (if not using Docker)
- MongoDB 7+ (if not using Docker)
- Redis 7+ (if not using Docker)

## 🛠️ Quick Start with Docker (Recommended)

### 1. Start all services
```bash
# From project root directory
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- MongoDB on port 27017
- Redis on port 6379
- Backend API on port 8000

### 2. Create database tables
```bash
# Enter the backend container
docker exec -it gaming_platform_backend bash

# Run migrations
alembic upgrade head
```

### 3. Access the API
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💻 Local Development Setup (Without Docker)

### 1. Install Python dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up databases

**PostgreSQL:**
```bash
psql -U postgres
CREATE DATABASE gaming_platform;
```

**MongoDB:**
```bash
# MongoDB should be running on localhost:27017
```

**Redis:**
```bash
# Redis should be running on localhost:6379
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run database migrations
```bash
alembic upgrade head
```

### 5. Start the server
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## 📖 API Documentation

### Authentication Endpoints

#### 1. Send OTP
```http
POST /api/v1/auth/send-otp
Content-Type: application/json

{
  "phone": "+919876543210",
  "purpose": "login"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "otp_sent": true,
    "expires_in": 300,
    "message": "OTP sent to +919876543210"
  }
}
```

**Note**: In development, OTP is printed to console instead of sending SMS.

#### 2. Verify OTP & Login
```http
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "phone": "+919876543210",
  "otp": "123456",
  "device_id": "unique-device-id",
  "device_name": "Samsung Galaxy S21",
  "device_os": "Android 12"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "username": "user_543210",
      "phone": "+919876543210",
      "email": null,
      "kyc_status": "pending",
      "referral_code": "USER1234",
      "created_at": "2025-01-16T10:00:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGc...",
      "refresh_token": "eyJhbGc...",
      "token_type": "bearer",
      "expires_in": 1800
    },
    "is_new_user": true
  }
}
```

#### 3. Refresh Token
```http
POST /api/v1/auth/refresh-token
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

#### 4. Logout
```http
POST /api/v1/auth/logout
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "all_devices": false
}
```

### User Profile Endpoints

#### 1. Get Profile
```http
GET /api/v1/users/profile
Authorization: Bearer <access_token>
```

#### 2. Update Profile
```http
PUT /api/v1/users/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "display_name": "John Doe",
  "bio": "Professional gamer",
  "email": "john@example.com",
  "date_of_birth": "1995-01-15",
  "state": "Maharashtra",
  "city": "Mumbai"
}
```

#### 3. Get Statistics
```http
GET /api/v1/users/statistics
Authorization: Bearer <access_token>
```

## 🗄️ Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `username` (String, Unique)
- `phone` (String, Unique)
- `email` (String, Nullable)
- `password_hash` (String, Nullable)
- `display_name` (String)
- `avatar_url` (String)
- `kyc_status` (Enum: pending, verified, rejected)
- `referral_code` (String, Unique)
- `created_at` (Timestamp)

### User Sessions
- JWT token management
- Device tracking
- Session expiry

### OTP Attempts
- OTP storage
- Attempt tracking
- Rate limiting

See `models/user.py` for complete schema.

## 🧪 Testing

### Run tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Test Authentication Flow
```bash
# 1. Send OTP
curl -X POST http://localhost:8000/api/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "purpose": "login"}'

# 2. Check console for OTP, then verify
curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'
```

## 📦 Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py
├── api/                  # API endpoints
│   └── v1/
│       ├── auth.py       # Authentication
│       └── users.py      # User profile
├── config/               # Configuration
│   ├── settings.py       # App settings
│   └── database.py       # DB connections
├── core/                 # Core utilities
│   ├── security.py       # JWT, hashing
│   └── exceptions.py     # Custom exceptions
├── middleware/           # Middleware
│   ├── error_handler.py  # Error handling
│   └── logging_middleware.py
├── models/               # Database models
│   └── user.py           # User models
├── schemas/              # Pydantic schemas
│   ├── auth.py           # Auth schemas
│   └── user.py           # User schemas
├── services/             # Business logic (future)
├── utils/                # Utilities (future)
├── main.py               # FastAPI app
├── requirements.txt      # Dependencies
├── Dockerfile            # Docker config
└── .env.example          # Environment template
```

## 🔧 Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Add new table"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## 🐛 Debugging

### View logs
```bash
# Docker
docker-compose logs -f backend

# Local
# Logs are printed to console
```

### Connect to databases
```bash
# PostgreSQL
docker exec -it gaming_platform_postgres psql -U postgres -d gaming_platform

# MongoDB
docker exec -it gaming_platform_mongodb mongosh -u admin -p admin

# Redis
docker exec -it gaming_platform_redis redis-cli
```

## 🚨 Common Issues

### Issue: Database connection failed
**Solution**: Ensure PostgreSQL/MongoDB/Redis are running:
```bash
docker-compose ps
```

### Issue: OTP not received
**Solution**: In development, OTP is printed to console. Check backend logs.

### Issue: Migration failed
**Solution**: Drop and recreate database:
```bash
docker-compose down -v
docker-compose up -d
docker exec -it gaming_platform_backend alembic upgrade head
```

## 📝 Environment Variables

See `.env.example` for all available configuration options.

**Required variables:**
- `SECRET_KEY`: JWT secret (use strong random string in production)
- `DATABASE_URL`: PostgreSQL connection string
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string

**Optional variables:**
- `TWILIO_*`: For SMS OTP (required in production)
- `SENDGRID_*`: For email notifications
- `RAZORPAY_*`: For payments (Phase 3)
- `AWS_*`: For file uploads (Phase 1+)

## 🔐 Security Notes

1. **Change SECRET_KEY** in production to a strong random string
2. **Enable HTTPS** in production
3. **Configure CORS** properly for production domains
4. **Set DEBUG=False** in production
5. **Use environment variables** for all secrets
6. **Enable rate limiting** on all endpoints

## ✅ Next Steps (Phase 2)

- [ ] KYC verification endpoints
- [ ] Wallet management
- [ ] Payment integration (add money)
- [ ] Bank account verification

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Contributing

This is an internal project. Follow the coding standards and update tests for any new features.

---

**Phase 1 Status**: ✅ Complete
**Last Updated**: November 16, 2025
**API Version**: 1.0.0
