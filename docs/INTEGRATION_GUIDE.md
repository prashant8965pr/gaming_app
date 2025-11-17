# Backend-Mobile Integration Guide

This guide provides step-by-step instructions for integrating the Flutter mobile app with the FastAPI backend.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Mobile App Configuration](#mobile-app-configuration)
4. [API Integration](#api-integration)
5. [Testing Integration](#testing-integration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Backend Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- AWS Account (for S3)
- Razorpay Account

### Mobile Requirements
- Flutter SDK 3.0+
- Android Studio / Xcode
- Physical device or emulator

---

## Backend Setup

### 1. Start Backend Services

#### Development Mode
```bash
cd gaming_app
docker-compose up -d
```

This starts:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- Backend API on `localhost:8000`

#### Production Mode
```bash
# Copy and configure environment
cp .env.example .env.production
# Edit .env.production with your credentials

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-11-17T10:00:00Z"
}
```

### 3. Run Database Migrations

```bash
# Enter backend container
docker exec -it gaming_platform_backend bash

# Run migrations
alembic upgrade head

# Create admin user (optional)
python scripts/create_admin.py
```

### 4. API Documentation

Once backend is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Mobile App Configuration

### 1. Update API Base URL

Edit `mobile_app/lib/core/constants/app_constants.dart`:

```dart
class AppConstants {
  // Development
  static const String baseUrl = 'http://10.0.2.2:8000';  // Android Emulator
  // static const String baseUrl = 'http://localhost:8000';  // iOS Simulator
  // static const String baseUrl = 'http://192.168.1.100:8000';  // Physical Device

  // Production
  // static const String baseUrl = 'https://api.gameapp.com';

  static const String apiVersion = 'v1';
  static const String apiBasePath = '/api/$apiVersion';
}
```

### 2. Configure Razorpay

Edit `mobile_app/lib/core/constants/app_constants.dart`:

```dart
class PaymentConstants {
  static const String razorpayKeyId = 'YOUR_RAZORPAY_KEY_ID';
  // Test key: rzp_test_xxxxxxxxxxxxx
  // Live key: rzp_live_xxxxxxxxxxxxx
}
```

### 3. Configure Firebase

#### Android
1. Download `google-services.json` from Firebase Console
2. Place in `mobile_app/android/app/`

#### iOS
1. Download `GoogleService-Info.plist` from Firebase Console
2. Place in `mobile_app/ios/Runner/`

### 4. Install Dependencies

```bash
cd mobile_app
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

---

## API Integration

### Network Layer Setup

The mobile app uses Dio HTTP client with interceptors. The setup is in:
`mobile_app/lib/core/network/dio_client.dart`

#### Key Features:
- ✅ Automatic token refresh
- ✅ Request/Response logging
- ✅ Error handling
- ✅ Timeout management

### Authentication Flow

#### 1. Send OTP

**Endpoint**: `POST /api/v1/auth/send-otp`

```dart
// Mobile Implementation
final result = await authRepository.sendOTP(
  phoneNumber: '+919876543210',
);

result.fold(
  (failure) => print('Error: ${failure.message}'),
  (success) => print('OTP sent successfully'),
);
```

**Request**:
```json
{
  "phone_number": "+919876543210"
}
```

**Response**:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": {
    "phone_number": "+919876543210",
    "otp_sent": true
  }
}
```

#### 2. Verify OTP

**Endpoint**: `POST /api/v1/auth/verify-otp`

```dart
final result = await authRepository.verifyOTP(
  phoneNumber: '+919876543210',
  otp: '123456',
);
```

**Request**:
```json
{
  "phone_number": "+919876543210",
  "otp": "123456"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": "uuid",
      "username": "user123",
      "phone_number": "+919876543210"
    }
  }
}
```

#### 3. Store Tokens

Tokens are automatically stored in secure storage:
```dart
await secureStorage.saveAccessToken(token);
await secureStorage.saveRefreshToken(refreshToken);
```

### API Endpoints Mapping

| Feature | Endpoint | Mobile Implementation |
|---------|----------|----------------------|
| **Authentication** |
| Send OTP | `POST /auth/send-otp` | `AuthRemoteDataSource.sendOTP()` |
| Verify OTP | `POST /auth/verify-otp` | `AuthRemoteDataSource.verifyOTP()` |
| Logout | `POST /auth/logout` | `AuthRemoteDataSource.logout()` |
| **User** |
| Get Profile | `GET /users/me` | `UserRemoteDataSource.getProfile()` |
| Update Profile | `PATCH /users/me` | `UserRemoteDataSource.updateProfile()` |
| Upload Avatar | `POST /users/me/avatar` | `UserRemoteDataSource.uploadAvatar()` |
| **Wallet** |
| Get Balance | `GET /wallet/balance` | `WalletRemoteDataSource.getBalance()` |
| Add Money | `POST /wallet/deposit` | `WalletRemoteDataSource.deposit()` |
| Withdraw | `POST /wallet/withdraw` | `WalletRemoteDataSource.withdraw()` |
| Transactions | `GET /wallet/transactions` | `WalletRemoteDataSource.getTransactions()` |
| **Games** |
| List Games | `GET /games` | `GameRemoteDataSource.getGames()` |
| Game Details | `GET /games/:id` | `GameRemoteDataSource.getGameDetails()` |
| Join Session | `POST /games/:id/join` | `GameRemoteDataSource.joinSession()` |

---

## Testing Integration

### 1. Test Backend Connectivity

Create `test_api.dart`:

```dart
import 'package:dio/dio.dart';

void main() async {
  final dio = Dio(BaseOptions(
    baseUrl: 'http://10.0.2.2:8000/api/v1',
  ));

  try {
    final response = await dio.get('/health');
    print('✅ Backend is reachable');
    print('Response: ${response.data}');
  } catch (e) {
    print('❌ Cannot reach backend');
    print('Error: $e');
  }
}
```

Run: `dart run test_api.dart`

### 2. Test Authentication

```dart
// In your app, navigate to login screen
// Enter phone number: +919876543210
// Check backend logs for OTP (in development)
docker logs gaming_platform_backend | grep OTP
```

### 3. Test Payment Flow

#### Razorpay Test Cards:
- **Card Number**: 4111 1111 1111 1111
- **CVV**: Any 3 digits
- **Expiry**: Any future date

#### Test UPI:
- **UPI ID**: success@razorpay
- **Status**: Will succeed

### 4. Monitor Network Calls

Enable logging in mobile app:

```dart
// In dio_client.dart
interceptors.add(LogInterceptor(
  request: true,
  requestHeader: true,
  requestBody: true,
  responseHeader: true,
  responseBody: true,
  error: true,
));
```

---

## Common Integration Points

### 1. Image Upload

```dart
// Mobile: Upload profile picture
Future<String> uploadImage(File image) async {
  final formData = FormData.fromMap({
    'file': await MultipartFile.fromFile(
      image.path,
      filename: 'profile.jpg',
    ),
  });

  final response = await dio.post(
    '/users/me/avatar',
    data: formData,
  );

  return response.data['data']['url'];
}
```

**Backend**: Receives multipart/form-data, uploads to S3, returns URL

### 2. Real-time Updates (WebSocket)

```dart
// Mobile: Connect to WebSocket
import 'package:socket_io_client/socket_io_client.dart' as IO;

final socket = IO.io('http://10.0.2.2:8000', <String, dynamic>{
  'transports': ['websocket'],
  'extraHeaders': {'Authorization': 'Bearer $token'},
});

socket.on('game_update', (data) {
  print('Game update: $data');
});

socket.emit('join_game', {'session_id': 'xxx'});
```

### 3. Push Notifications

```dart
// Mobile: Handle FCM token
FirebaseMessaging.instance.getToken().then((token) {
  // Send to backend
  dio.post('/users/me/fcm-token', data: {'token': token});
});
```

**Backend**: Stores FCM token, sends notifications via Firebase Admin SDK

---

## Error Handling

### Mobile Side

```dart
result.fold(
  (failure) {
    if (failure is NetworkFailure) {
      // No internet
      showSnackBar('No internet connection');
    } else if (failure is UnauthorizedFailure) {
      // Token expired, logout
      navigateToLogin();
    } else if (failure is ServerFailure) {
      // Server error
      showSnackBar('Server error: ${failure.message}');
    }
  },
  (success) {
    // Handle success
  },
);
```

### Backend Responses

All backend responses follow this format:

**Success**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_OTP",
    "message": "Invalid or expired OTP",
    "details": {}
  }
}
```

---

## Troubleshooting

### Cannot Connect to Backend

#### Android Emulator
- Use `10.0.2.2` instead of `localhost`
- Check if backend is running: `docker ps`

#### iOS Simulator
- Use `localhost` or your machine's IP
- Check firewall settings

#### Physical Device
- Use your machine's IP address (e.g., `192.168.1.100`)
- Ensure device and machine are on same network
- Check `ALLOWED_ORIGINS` in backend `.env`

### CORS Issues

Add mobile app origin to backend `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://10.0.2.2:8000,http://192.168.1.100:8000
```

Restart backend:
```bash
docker-compose restart backend
```

### Token Expiration

Tokens expire after 30 minutes. The app automatically refreshes using refresh token.

Check token refresh logic in:
`mobile_app/lib/core/network/dio_client.dart` → `_AuthInterceptor`

### Database Connection

If backend can't connect to database:

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it gaming_platform_postgres psql -U postgres -d gaming_platform

# Run migrations
docker exec -it gaming_platform_backend alembic upgrade head
```

---

## Development Workflow

### 1. Make Backend Changes

```bash
# Backend auto-reloads on file changes
cd backend
# Edit files
# Check logs: docker logs -f gaming_platform_backend
```

### 2. Make Mobile Changes

```bash
cd mobile_app
# Edit files
# Hot reload: Press 'r' in terminal
# Hot restart: Press 'R' in terminal
```

### 3. Test Flow

1. Start backend: `docker-compose up -d`
2. Run mobile app: `flutter run`
3. Test feature end-to-end
4. Check backend logs if issues
5. Check mobile debug console

---

## Production Deployment

### Backend

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Mobile

```bash
# Android
flutter build appbundle --release

# iOS
flutter build ipa --release
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Use production Razorpay keys
- [ ] Enable rate limiting
- [ ] Setup Firebase security rules
- [ ] Enable certificate pinning (mobile)
- [ ] Use environment variables for secrets
- [ ] Enable database encryption

---

## Performance Tips

### Backend
- Enable Redis caching
- Use database connection pooling
- Configure CDN for static files
- Enable gzip compression

### Mobile
- Cache API responses locally
- Use image caching
- Implement pagination
- Lazy load data

---

## Support

### Backend Issues
- Check logs: `docker logs gaming_platform_backend`
- API Docs: `http://localhost:8000/docs`

### Mobile Issues
- Check Flutter logs: `flutter logs`
- Debug mode: `flutter run --verbose`

### Database Issues
- Connect: `docker exec -it gaming_platform_postgres psql -U postgres`
- Check tables: `\dt`
- Query data: `SELECT * FROM users;`

---

## Next Steps

1. ✅ Backend running locally
2. ✅ Mobile app configured
3. ✅ Test authentication flow
4. ✅ Test payment integration
5. ✅ Test all features end-to-end
6. Deploy to staging
7. User testing
8. Deploy to production

---

**Last Updated**: November 2024
**Version**: 1.0.0
