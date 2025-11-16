# API Contracts & Endpoints

## Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Staging**: `https://staging-api.gamingplatform.com/api/v1`
- **Production**: `https://api.gamingplatform.com/api/v1`

## Authentication

All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

## Common Response Format

### Success Response
```json
{
    "success": true,
    "data": { ... },
    "message": "Operation successful",
    "timestamp": "2025-01-16T10:30:00Z"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_BALANCE",
        "message": "Insufficient wallet balance",
        "details": {}
    },
    "timestamp": "2025-01-16T10:30:00Z"
}
```

## HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## 1. Authentication APIs

### 1.1 Send OTP
**Endpoint**: `POST /auth/send-otp`
**Auth**: No

**Request**:
```json
{
    "phone": "+919876543210",
    "purpose": "login" // login, registration, verification
}
```

**Response**:
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

**Rate Limit**: 3 requests per hour per phone

---

### 1.2 Verify OTP & Login
**Endpoint**: `POST /auth/verify-otp`
**Auth**: No

**Request**:
```json
{
    "phone": "+919876543210",
    "otp": "123456",
    "device_id": "unique-device-id",
    "device_name": "Samsung Galaxy S21",
    "device_os": "Android 12"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "uuid",
            "username": "john_doe",
            "phone": "+919876543210",
            "email": "john@example.com",
            "kyc_status": "verified",
            "referral_code": "JOHN1234"
        },
        "tokens": {
            "access_token": "eyJhbGc...",
            "refresh_token": "eyJhbGc...",
            "expires_in": 1800
        },
        "is_new_user": false
    }
}
```

---

### 1.3 Refresh Token
**Endpoint**: `POST /auth/refresh-token`
**Auth**: No

**Request**:
```json
{
    "refresh_token": "eyJhbGc..."
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGc...",
        "expires_in": 1800
    }
}
```

---

### 1.4 Logout
**Endpoint**: `POST /auth/logout`
**Auth**: Required

**Request**:
```json
{
    "all_devices": false
}
```

**Response**:
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

---

### 1.5 Social Login (Google)
**Endpoint**: `POST /auth/social/google`
**Auth**: No

**Request**:
```json
{
    "id_token": "google-id-token",
    "device_id": "unique-device-id"
}
```

**Response**: Same as 1.2

---

## 2. User Profile APIs

### 2.1 Get User Profile
**Endpoint**: `GET /users/profile`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "username": "john_doe",
        "display_name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "avatar_url": "https://...",
        "date_of_birth": "1995-01-15",
        "kyc_status": "verified",
        "referral_code": "JOHN1234",
        "level": 10,
        "experience_points": 5000,
        "statistics": {
            "total_games_played": 150,
            "total_games_won": 90,
            "win_percentage": 60.0,
            "total_winnings": 15000.50
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

---

### 2.2 Update Profile
**Endpoint**: `PUT /users/profile`
**Auth**: Required

**Request**:
```json
{
    "display_name": "John Smith",
    "bio": "Professional gamer",
    "avatar_url": "https://..."
}
```

**Response**:
```json
{
    "success": true,
    "data": { /* updated profile */ },
    "message": "Profile updated successfully"
}
```

---

### 2.3 Upload Avatar
**Endpoint**: `POST /users/avatar`
**Auth**: Required
**Content-Type**: `multipart/form-data`

**Request**:
```
avatar: [file]
```

**Response**:
```json
{
    "success": true,
    "data": {
        "avatar_url": "https://cdn.example.com/avatars/uuid.jpg"
    }
}
```

---

### 2.4 Get User Statistics
**Endpoint**: `GET /users/statistics`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "total_games_played": 150,
        "total_games_won": 90,
        "total_games_lost": 55,
        "total_games_drawn": 5,
        "win_percentage": 60.0,
        "total_winnings": 15000.50,
        "total_spent": 10000.00,
        "net_profit": 5000.50,
        "current_streak": 5,
        "longest_streak": 12,
        "game_wise_stats": [
            {
                "game_code": "ludo",
                "games_played": 80,
                "games_won": 50,
                "elo_rating": 1850
            }
        ]
    }
}
```

---

## 3. KYC APIs

### 3.1 Submit KYC Documents
**Endpoint**: `POST /kyc/submit`
**Auth**: Required
**Content-Type**: `multipart/form-data`

**Request**:
```
document_type: "aadhaar"
document_number: "1234 5678 9012"
document_front: [file]
document_back: [file]
```

**Response**:
```json
{
    "success": true,
    "data": {
        "kyc_id": "uuid",
        "status": "pending",
        "message": "KYC documents submitted for verification"
    }
}
```

---

### 3.2 Get KYC Status
**Endpoint**: `GET /kyc/status`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "kyc_status": "verified", // pending, verified, rejected
        "documents": [
            {
                "id": "uuid",
                "document_type": "aadhaar",
                "status": "verified",
                "submitted_at": "2024-01-01T00:00:00Z",
                "verified_at": "2024-01-02T00:00:00Z"
            }
        ]
    }
}
```

---

### 3.3 Add Bank Account
**Endpoint**: `POST /kyc/bank-account`
**Auth**: Required

**Request**:
```json
{
    "account_holder_name": "John Doe",
    "account_number": "12345678901234",
    "ifsc_code": "SBIN0001234",
    "account_type": "savings"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "bank_account_id": "uuid",
        "is_verified": false,
        "message": "Bank account added successfully. Verification pending."
    }
}
```

---

## 4. Wallet APIs

### 4.1 Get Wallet Balance
**Endpoint**: `GET /wallet/balance`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "wallets": [
            {
                "wallet_type": "cash",
                "balance": 1000.50,
                "currency": "INR"
            },
            {
                "wallet_type": "winnings",
                "balance": 500.00,
                "currency": "INR"
            },
            {
                "wallet_type": "bonus",
                "balance": 100.00,
                "currency": "INR"
            }
        ],
        "total_balance": 1600.50
    }
}
```

---

### 4.2 Get Transaction History
**Endpoint**: `GET /wallet/transactions`
**Auth**: Required
**Query Params**:
- `page` (default: 1)
- `limit` (default: 20, max: 100)
- `transaction_type` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response**:
```json
{
    "success": true,
    "data": {
        "transactions": [
            {
                "id": "uuid",
                "transaction_type": "game_winning",
                "amount": 100.00,
                "wallet_type": "winnings",
                "balance_before": 400.00,
                "balance_after": 500.00,
                "description": "Won match #123",
                "status": "success",
                "created_at": "2025-01-16T10:30:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_items": 100,
            "items_per_page": 20
        }
    }
}
```

---

## 5. Payment APIs

### 5.1 Create Add Money Order
**Endpoint**: `POST /payments/add-money/create-order`
**Auth**: Required

**Request**:
```json
{
    "amount": 500,
    "payment_gateway": "razorpay" // razorpay, cashfree
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "order_id": "order_xyz123",
        "amount": 500,
        "currency": "INR",
        "gateway_order_id": "razorpay_order_id",
        "key": "razorpay_key_id",
        "callback_url": "https://api.example.com/payments/callback"
    }
}
```

---

### 5.2 Verify Payment
**Endpoint**: `POST /payments/add-money/verify`
**Auth**: Required

**Request**:
```json
{
    "order_id": "order_xyz123",
    "payment_id": "pay_xyz456",
    "signature": "signature_hash"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "payment_verified": true,
        "amount_credited": 500.00,
        "wallet_type": "cash",
        "new_balance": 1500.50,
        "transaction_id": "uuid"
    }
}
```

---

### 5.3 Request Withdrawal
**Endpoint**: `POST /payments/withdraw`
**Auth**: Required

**Request**:
```json
{
    "amount": 1000,
    "bank_account_id": "uuid"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "withdrawal_id": "uuid",
        "amount": 1000.00,
        "tds_amount": 0.00,
        "net_amount": 1000.00,
        "status": "pending",
        "estimated_completion": "2-3 business days"
    }
}
```

---

### 5.4 Get Withdrawal History
**Endpoint**: `GET /payments/withdrawals`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "withdrawals": [
            {
                "id": "uuid",
                "amount": 1000.00,
                "tds_amount": 0.00,
                "net_amount": 1000.00,
                "status": "success",
                "utr_number": "UTR123456789",
                "created_at": "2025-01-15T10:00:00Z",
                "processed_at": "2025-01-16T15:30:00Z"
            }
        ]
    }
}
```

---

## 6. Game APIs

### 6.1 Get All Games
**Endpoint**: `GET /games`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "games": [
            {
                "id": "uuid",
                "game_code": "ludo",
                "game_name": "Ludo",
                "game_type": "turn_based",
                "min_players": 2,
                "max_players": 4,
                "min_entry_fee": 10,
                "max_entry_fee": 10000,
                "is_active": true,
                "thumbnail_url": "https://..."
            }
        ]
    }
}
```

---

### 6.2 Get Game Details
**Endpoint**: `GET /games/{game_code}`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "game_code": "ludo",
        "game_name": "Ludo",
        "description": "Classic Ludo game",
        "rules": "...",
        "game_type": "turn_based",
        "min_players": 2,
        "max_players": 4,
        "available_entry_fees": [10, 50, 100, 500, 1000],
        "config": {},
        "user_stats": {
            "games_played": 50,
            "games_won": 30,
            "elo_rating": 1850
        }
    }
}
```

---

## 7. Matchmaking APIs

### 7.1 Join Matchmaking Queue
**Endpoint**: `POST /matchmaking/join`
**Auth**: Required

**Request**:
```json
{
    "game_code": "ludo",
    "entry_fee": 100,
    "match_type": "quick" // quick, skill_based
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "queue_id": "uuid",
        "position": 5,
        "estimated_wait_time": 30,
        "message": "Finding opponents..."
    }
}
```

---

### 7.2 Leave Queue
**Endpoint**: `POST /matchmaking/leave`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "message": "Left matchmaking queue"
}
```

---

### 7.3 Match Found (WebSocket Event)
**Event**: `match_found`

**Payload**:
```json
{
    "match_id": "uuid",
    "game_code": "ludo",
    "entry_fee": 100,
    "prize_pool": 360,
    "players": [
        {
            "user_id": "uuid",
            "username": "john_doe",
            "avatar_url": "https://...",
            "elo_rating": 1850
        }
    ],
    "join_deadline": "2025-01-16T10:35:00Z"
}
```

---

### 7.4 Join Match
**Endpoint**: `POST /matches/{match_id}/join`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "match_id": "uuid",
        "websocket_url": "wss://game.example.com/match/uuid",
        "token": "websocket_auth_token"
    }
}
```

---

## 8. Match/Game Play APIs

### 8.1 Get Match Details
**Endpoint**: `GET /matches/{match_id}`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "match_id": "uuid",
        "game_code": "ludo",
        "status": "in_progress",
        "entry_fee": 100,
        "prize_pool": 360,
        "players": [...],
        "current_turn": "user_uuid",
        "game_state": {},
        "started_at": "2025-01-16T10:30:00Z"
    }
}
```

---

### 8.2 Make Move (WebSocket)
**Event**: `make_move`

**Payload**:
```json
{
    "match_id": "uuid",
    "move_data": {
        "dice_value": 6,
        "token_id": 1,
        "from_position": 10,
        "to_position": 16
    }
}
```

**Response Event**: `move_validated`
```json
{
    "valid": true,
    "updated_game_state": {},
    "next_turn": "user_uuid"
}
```

---

### 8.3 Get Match Result
**Endpoint**: `GET /matches/{match_id}/result`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "match_id": "uuid",
        "status": "completed",
        "winner": {
            "user_id": "uuid",
            "username": "john_doe",
            "prize_amount": 360.00
        },
        "rankings": [
            {
                "rank": 1,
                "user_id": "uuid",
                "username": "john_doe",
                "score": 100,
                "prize_amount": 360.00
            }
        ],
        "completed_at": "2025-01-16T10:45:00Z"
    }
}
```

---

### 8.4 Get Match History
**Endpoint**: `GET /matches/history`
**Auth**: Required
**Query Params**: `page`, `limit`, `game_code`

**Response**:
```json
{
    "success": true,
    "data": {
        "matches": [
            {
                "match_id": "uuid",
                "game_code": "ludo",
                "entry_fee": 100,
                "result": "won",
                "prize_amount": 360.00,
                "rank": 1,
                "played_at": "2025-01-16T10:30:00Z"
            }
        ],
        "pagination": { ... }
    }
}
```

---

## 9. Tournament APIs

### 9.1 Get Active Tournaments
**Endpoint**: `GET /tournaments/active`
**Auth**: Required
**Query Params**: `game_code` (optional)

**Response**:
```json
{
    "success": true,
    "data": {
        "tournaments": [
            {
                "id": "uuid",
                "tournament_name": "Mega Ludo Championship",
                "game_code": "ludo",
                "tournament_type": "paid",
                "entry_fee": 50,
                "prize_pool": 50000,
                "max_participants": 1000,
                "current_participants": 750,
                "status": "registration_open",
                "registration_end_time": "2025-01-17T00:00:00Z",
                "start_time": "2025-01-17T10:00:00Z"
            }
        ]
    }
}
```

---

### 9.2 Get Tournament Details
**Endpoint**: `GET /tournaments/{tournament_id}`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "tournament_name": "Mega Ludo Championship",
        "description": "...",
        "game_code": "ludo",
        "entry_fee": 50,
        "prize_pool": 50000,
        "prize_distribution": [
            {"rank": 1, "percentage": 40, "amount": 20000},
            {"rank": 2, "percentage": 25, "amount": 12500}
        ],
        "max_participants": 1000,
        "current_participants": 750,
        "status": "registration_open",
        "rules": "...",
        "start_time": "2025-01-17T10:00:00Z",
        "is_registered": false
    }
}
```

---

### 9.3 Register for Tournament
**Endpoint**: `POST /tournaments/{tournament_id}/register`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "registration_id": "uuid",
        "tournament_id": "uuid",
        "entry_fee_paid": 50,
        "status": "registered",
        "message": "Successfully registered for tournament"
    }
}
```

---

### 9.4 Get Tournament Leaderboard
**Endpoint**: `GET /tournaments/{tournament_id}/leaderboard`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "leaderboard": [
            {
                "rank": 1,
                "user_id": "uuid",
                "username": "john_doe",
                "avatar_url": "https://...",
                "total_points": 1500,
                "games_played": 10,
                "prize_position": true,
                "estimated_prize": 20000
            }
        ],
        "user_rank": {
            "rank": 25,
            "total_points": 800,
            "prize_position": false
        }
    }
}
```

---

## 10. Leaderboard APIs

### 10.1 Get Global Leaderboard
**Endpoint**: `GET /leaderboards/global`
**Auth**: Required
**Query Params**: `game_code`, `period` (all_time, weekly, monthly)

**Response**:
```json
{
    "success": true,
    "data": {
        "leaderboard": [
            {
                "rank": 1,
                "user_id": "uuid",
                "username": "pro_gamer",
                "avatar_url": "https://...",
                "elo_rating": 2100,
                "total_games": 500,
                "win_percentage": 75.5
            }
        ],
        "user_rank": {
            "rank": 150,
            "elo_rating": 1850
        }
    }
}
```

---

## 11. Referral APIs

### 11.1 Get Referral Details
**Endpoint**: `GET /referrals/details`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "referral_code": "JOHN1234",
        "referral_link": "https://app.example.com/ref/JOHN1234",
        "total_referrals": 25,
        "active_referrals": 18,
        "total_earnings": 2500.00,
        "referrals": [
            {
                "referred_user": "user123",
                "joined_at": "2025-01-10T00:00:00Z",
                "status": "activated",
                "earnings": 100.00
            }
        ]
    }
}
```

---

## 12. Rewards APIs

### 12.1 Get Daily Rewards
**Endpoint**: `GET /rewards/daily`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "today_claimed": false,
        "current_streak": 5,
        "reward_amount": 10,
        "streak_bonus": 50,
        "total_reward": 60
    }
}
```

---

### 12.2 Claim Daily Reward
**Endpoint**: `POST /rewards/daily/claim`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "reward_amount": 60,
        "wallet_type": "bonus",
        "new_balance": 160,
        "streak_count": 6
    }
}
```

---

### 12.3 Spin Wheel
**Endpoint**: `POST /rewards/spin`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "data": {
        "prize": "50 bonus coins",
        "amount": 50,
        "next_spin_available_at": "2025-01-17T00:00:00Z"
    }
}
```

---

## 13. Notification APIs

### 13.1 Get Notifications
**Endpoint**: `GET /notifications`
**Auth**: Required
**Query Params**: `page`, `limit`, `unread_only`

**Response**:
```json
{
    "success": true,
    "data": {
        "notifications": [
            {
                "id": "uuid",
                "type": "match_found",
                "title": "Match Found!",
                "body": "Your match is ready",
                "data": {
                    "match_id": "uuid"
                },
                "is_read": false,
                "created_at": "2025-01-16T10:30:00Z"
            }
        ],
        "unread_count": 5
    }
}
```

---

### 13.2 Mark as Read
**Endpoint**: `PUT /notifications/{notification_id}/read`
**Auth**: Required

**Response**:
```json
{
    "success": true,
    "message": "Notification marked as read"
}
```

---

## 14. Admin APIs (Separate Base URL)

**Base URL**: `https://api.example.com/api/v1/admin`

### 14.1 Admin Login
**Endpoint**: `POST /admin/auth/login`
**Auth**: No

**Request**:
```json
{
    "email": "admin@example.com",
    "password": "secure_password"
}
```

**Response**:
```json
{
    "success": true,
    "data": {
        "admin_user": {
            "id": "uuid",
            "username": "admin",
            "role": "admin"
        },
        "access_token": "eyJhbGc..."
    }
}
```

---

### 14.2 Get Dashboard Stats
**Endpoint**: `GET /admin/dashboard/stats`
**Auth**: Admin Required

**Response**:
```json
{
    "success": true,
    "data": {
        "active_users_today": 5000,
        "total_games_today": 15000,
        "revenue_today": 500000,
        "pending_withdrawals": 50,
        "fraud_alerts": 10
    }
}
```

---

### 14.3 Get Users List
**Endpoint**: `GET /admin/users`
**Auth**: Admin Required
**Query Params**: `page`, `limit`, `search`, `status`, `kyc_status`

**Response**:
```json
{
    "success": true,
    "data": {
        "users": [ ... ],
        "pagination": { ... }
    }
}
```

---

### 14.4 Ban User
**Endpoint**: `POST /admin/users/{user_id}/ban`
**Auth**: Admin Required

**Request**:
```json
{
    "ban_type": "permanent",
    "reason": "Multiple fraud alerts"
}
```

**Response**:
```json
{
    "success": true,
    "message": "User banned successfully"
}
```

---

### 14.5 Approve Withdrawal
**Endpoint**: `POST /admin/withdrawals/{withdrawal_id}/approve`
**Auth**: Admin Required (Finance role)

**Request**:
```json
{
    "utr_number": "UTR123456789"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Withdrawal approved and processed"
}
```

---

## WebSocket Events

### Connection
```
URL: wss://game.example.com/ws
Auth: ?token=<access_token>
```

### Events

#### 1. Player Connected
```json
{
    "event": "player_connected",
    "data": {
        "user_id": "uuid",
        "username": "john_doe"
    }
}
```

#### 2. Game Started
```json
{
    "event": "game_started",
    "data": {
        "match_id": "uuid",
        "game_state": {},
        "current_turn": "user_uuid"
    }
}
```

#### 3. Move Made
```json
{
    "event": "move_made",
    "data": {
        "user_id": "uuid",
        "move_data": {},
        "updated_game_state": {},
        "next_turn": "user_uuid"
    }
}
```

#### 4. Game Completed
```json
{
    "event": "game_completed",
    "data": {
        "winner": "user_uuid",
        "rankings": [],
        "prize_distribution": []
    }
}
```

---

## Error Codes

| Code | Message | HTTP Status |
|------|---------|-------------|
| `INVALID_CREDENTIALS` | Invalid phone or OTP | 401 |
| `OTP_EXPIRED` | OTP has expired | 400 |
| `INSUFFICIENT_BALANCE` | Insufficient wallet balance | 400 |
| `KYC_NOT_VERIFIED` | KYC verification required | 403 |
| `USER_BANNED` | Account has been banned | 403 |
| `MATCH_FULL` | Match is already full | 400 |
| `INVALID_MOVE` | Invalid game move | 400 |
| `TOURNAMENT_FULL` | Tournament is full | 400 |
| `ALREADY_REGISTERED` | Already registered for tournament | 400 |

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Total Endpoints**: 50+
**WebSocket Events**: 10+
