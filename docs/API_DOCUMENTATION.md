# Gaming Platform - API Documentation

Complete API reference for the Gaming Platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [API Endpoints](#api-endpoints)
8. [WebSocket API](#websocket-api)
9. [SDKs & Examples](#sdks--examples)

---

## Overview

The Gaming Platform API is a RESTful API built with FastAPI. It provides comprehensive endpoints for:

- User authentication and management
- KYC verification
- Wallet operations (deposits, withdrawals)
- Game management and sessions
- Real-time gameplay via WebSocket
- Referrals and rewards
- Admin operations

**API Version:** 1.0.0
**Protocol:** HTTPS (Production), HTTP (Development)
**Format:** JSON

---

## Authentication

### Overview

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require a valid access token.

### Authentication Flow

1. **Send OTP** - Request OTP to phone number
2. **Verify OTP** - Verify OTP and receive access token
3. **Use Token** - Include token in subsequent requests
4. **Refresh Token** - Refresh access token when expired

### Token Usage

Include the access token in the `Authorization` header:

```http
Authorization: Bearer <your-access-token>
```

### Token Expiry

- **Access Token:** 30 minutes
- **Refresh Token:** 7 days

---

## Base URL

### Development
```
http://localhost:8000/api/v1
```

### Production
```
https://api.yourdomain.com/api/v1
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_OTP` | OTP is incorrect |
| `OTP_EXPIRED` | OTP has expired |
| `USER_NOT_FOUND` | User does not exist |
| `INVALID_TOKEN` | JWT token is invalid |
| `TOKEN_EXPIRED` | JWT token has expired |
| `INSUFFICIENT_BALANCE` | Wallet balance is insufficient |
| `KYC_NOT_VERIFIED` | KYC verification required |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## Rate Limiting

API requests are rate-limited to prevent abuse.

### Limits

- **Per Minute:** 60 requests
- **Per Hour:** 1000 requests

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642534800
```

### Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 60
    }
  }
}
```

---

## API Endpoints

### Authentication

#### Send OTP

```http
POST /auth/send-otp
```

**Request Body:**
```json
{
  "phone": "+919876543210"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "otp_sent": true,
    "expires_in": 300
  }
}
```

#### Verify OTP & Login

```http
POST /auth/verify-otp
```

**Request Body:**
```json
{
  "phone": "+919876543210",
  "otp": "123456",
  "device_id": "device-uuid",
  "device_name": "iPhone 12",
  "device_os": "iOS 15.0"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "username": "user123",
      "phone": "+919876543210",
      "status": "active",
      "role": "user",
      "kyc_status": "pending"
    },
    "tokens": {
      "access_token": "jwt-token",
      "refresh_token": "refresh-token",
      "token_type": "bearer",
      "expires_in": 1800
    }
  }
}
```

#### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

---

### User Management

#### Get User Profile

```http
GET /users/profile
Authorization: Bearer <token>
```

#### Update User Profile

```http
PUT /users/profile
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "state": "Maharashtra",
  "city": "Mumbai"
}
```

---

### KYC Management

#### Upload KYC Document

```http
POST /kyc/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `document_type`: "aadhaar" | "pan" | "driving_license"
- `document_number`: Document number
- `front_image`: File (image)
- `back_image`: File (image, optional)

#### Get KYC Status

```http
GET /kyc/status
Authorization: Bearer <token>
```

---

### Wallet Operations

#### Get Wallet Balance

```http
GET /wallet/balance
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "cash_balance": 1000.00,
    "bonus_balance": 50.00,
    "winnings_balance": 500.00,
    "total_balance": 1550.00
  }
}
```

#### Create Deposit

```http
POST /wallet/deposit
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 1000,
  "payment_method": "razorpay"
}
```

#### Create Withdrawal

```http
POST /wallet/withdraw
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 500,
  "account_id": "bank-account-uuid"
}
```

#### Get Transaction History

```http
GET /wallet/transactions?skip=0&limit=20
Authorization: Bearer <token>
```

---

### Game Management

#### Get Game Catalog

```http
GET /games/catalog
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Ludo",
      "description": "Classic board game",
      "min_players": 2,
      "max_players": 4,
      "entry_fee_range": {"min": 10, "max": 1000},
      "status": "active",
      "thumbnail_url": "https://..."
    }
  ]
}
```

#### Create Game Session

```http
POST /games/sessions
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "game_id": "game-uuid",
  "entry_fee": 100,
  "max_players": 4,
  "is_private": false
}
```

#### Join Game Session

```http
POST /games/sessions/{session_id}/join
Authorization: Bearer <token>
```

#### Start Game Session

```http
POST /games/sessions/{session_id}/start
Authorization: Bearer <token>
```

#### Get Active Sessions

```http
GET /games/sessions/active
Authorization: Bearer <token>
```

---

### Rewards & Achievements

#### Get User Achievements

```http
GET /rewards/achievements
Authorization: Bearer <token>
```

#### Get Leaderboard

```http
GET /rewards/leaderboard?period=weekly&limit=100
```

#### Apply Referral Code

```http
POST /rewards/apply-referral
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "referral_code": "REFER123"
}
```

---

### Admin Endpoints

All admin endpoints require admin role.

#### Get Dashboard Stats

```http
GET /admin/dashboard/stats
Authorization: Bearer <admin-token>
```

#### Get All Users

```http
GET /admin/users?skip=0&limit=50
Authorization: Bearer <admin-token>
```

#### Review KYC

```http
POST /admin/kyc/review
Authorization: Bearer <admin-token>
```

**Request Body:**
```json
{
  "kyc_id": "kyc-uuid",
  "action": "approve",
  "rejection_reason": "Optional reason if rejected",
  "admin_notes": "Optional notes"
}
```

#### Review Withdrawal

```http
POST /admin/withdrawals/review
Authorization: Bearer <admin-token>
```

---

## WebSocket API

### Game Session WebSocket

Connect to a game session for real-time updates.

**URL:**
```
ws://localhost:8000/api/v1/ws/game/{game_session_id}?token=<jwt-token>
```

#### Message Types

**Client → Server:**

```json
// Make a move
{
  "type": "move",
  "move": { /* game-specific move data */ }
}

// Send chat message
{
  "type": "chat",
  "message": "Hello!"
}

// Request game state
{
  "type": "game_state_request"
}

// Ping (keep alive)
{
  "type": "ping"
}
```

**Server → Client:**

```json
// Connection confirmation
{
  "type": "connection",
  "status": "connected",
  "game_session_id": "uuid",
  "timestamp": "2025-01-16T10:00:00Z"
}

// Game state update
{
  "type": "game_state_update",
  "game_session_id": "uuid",
  "state": { /* game state */ },
  "timestamp": "2025-01-16T10:00:00Z"
}

// Player joined
{
  "type": "player_joined",
  "user_id": "uuid",
  "username": "player1",
  "timestamp": "2025-01-16T10:00:00Z"
}

// Move made
{
  "type": "move_made",
  "user_id": "uuid",
  "move": { /* move data */ },
  "timestamp": "2025-01-16T10:00:00Z"
}

// Chat message
{
  "type": "chat_message",
  "user_id": "uuid",
  "username": "player1",
  "message": "Hello!",
  "timestamp": "2025-01-16T10:00:00Z"
}
```

### Notifications WebSocket

Connect for real-time user notifications.

**URL:**
```
ws://localhost:8000/api/v1/ws/notifications?token=<jwt-token>
```

**Server → Client:**

```json
{
  "type": "notification",
  "notification_type": "info",
  "title": "New Achievement",
  "message": "You unlocked a new achievement!",
  "data": {},
  "timestamp": "2025-01-16T10:00:00Z"
}
```

---

## SDKs & Examples

### JavaScript/TypeScript Example

```typescript
// Initialize API client
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Send OTP
const sendOTP = async (phone: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/send-otp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phone }),
  });
  return response.json();
};

// Verify OTP
const verifyOTP = async (phone: string, otp: string) => {
  const response = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      phone,
      otp,
      device_id: 'device-id',
      device_name: 'Browser',
      device_os: 'Web',
    }),
  });
  return response.json();
};

// Get user profile
const getProfile = async (token: string) => {
  const response = await fetch(`${API_BASE_URL}/users/profile`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
};

// WebSocket connection
const connectToGame = (gameSessionId: string, token: string) => {
  const ws = new WebSocket(
    `ws://localhost:8000/api/v1/ws/game/${gameSessionId}?token=${token}`
  );

  ws.onopen = () => console.log('Connected');
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Message:', message);
  };
  ws.onerror = (error) => console.error('Error:', error);
  ws.onclose = () => console.log('Disconnected');

  return ws;
};
```

### Python Example

```python
import requests

API_BASE_URL = "http://localhost:8000/api/v1"

# Send OTP
response = requests.post(f"{API_BASE_URL}/auth/send-otp", json={
    "phone": "+919876543210"
})
print(response.json())

# Verify OTP
response = requests.post(f"{API_BASE_URL}/auth/verify-otp", json={
    "phone": "+919876543210",
    "otp": "123456",
    "device_id": "device-id",
    "device_name": "Python Script",
    "device_os": "Linux"
})
data = response.json()
token = data["data"]["tokens"]["access_token"]

# Get profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{API_BASE_URL}/users/profile", headers=headers)
print(response.json())
```

---

## Interactive Documentation

### Swagger UI

Access interactive API documentation at:

```
http://localhost:8000/docs
```

### ReDoc

Alternative documentation interface:

```
http://localhost:8000/redoc
```

### OpenAPI Schema

Download the OpenAPI schema:

```
http://localhost:8000/api/v1/openapi.json
```

---

## Support

For API support and questions:

- **Email:** support@gamingplatform.com
- **Documentation:** https://docs.gamingplatform.com
- **Status Page:** https://status.gamingplatform.com

---

**Last Updated:** 2025-01-16
**API Version:** 1.0.0
