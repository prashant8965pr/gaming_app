# Complete Database Schema

## PostgreSQL Schema (Relational Data)

### 1. Users & Authentication

#### Table: `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL if only social/OTP login
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    date_of_birth DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, banned
    kyc_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_phone_verified BOOLEAN DEFAULT TRUE,
    referral_code VARCHAR(10) UNIQUE NOT NULL,
    referred_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_phone (phone),
    INDEX idx_email (email),
    INDEX idx_referral_code (referral_code),
    INDEX idx_status (status)
);
```

#### Table: `user_sessions`
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    device_id VARCHAR(255),
    device_name VARCHAR(100),
    device_os VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_access_token (access_token),
    INDEX idx_refresh_token (refresh_token),
    INDEX idx_expires_at (expires_at)
);
```

#### Table: `otp_attempts`
```sql
CREATE TABLE otp_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(15) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL, -- login, registration, verification
    is_verified BOOLEAN DEFAULT FALSE,
    attempts_count INT DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone_purpose (phone, purpose),
    INDEX idx_expires_at (expires_at)
);
```

#### Table: `social_auth_providers`
```sql
CREATE TABLE social_auth_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL, -- google, facebook, apple
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id),
    INDEX idx_user_id (user_id)
);
```

---

### 2. User Profile & KYC

#### Table: `user_profiles`
```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    state VARCHAR(50),
    city VARCHAR(100),
    pincode VARCHAR(10),
    preferred_language VARCHAR(10) DEFAULT 'en',
    notification_preferences JSONB DEFAULT '{"push": true, "email": true, "sms": true}'::jsonb,
    privacy_settings JSONB DEFAULT '{"show_profile": true, "show_stats": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `user_statistics`
```sql
CREATE TABLE user_statistics (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_games_played INT DEFAULT 0,
    total_games_won INT DEFAULT 0,
    total_games_lost INT DEFAULT 0,
    total_winnings DECIMAL(10, 2) DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    current_level INT DEFAULT 1,
    experience_points INT DEFAULT 0,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `kyc_documents`
```sql
CREATE TABLE kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(20) NOT NULL, -- aadhaar, pan, driving_license
    document_number VARCHAR(50) NOT NULL,
    document_front_url VARCHAR(500),
    document_back_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    rejection_reason TEXT,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

#### Table: `bank_accounts`
```sql
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_holder_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    bank_name VARCHAR(100),
    branch_name VARCHAR(100),
    account_type VARCHAR(20), -- savings, current
    is_verified BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

---

### 3. Wallet & Transactions

#### Table: `wallets`
```sql
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_type VARCHAR(20) NOT NULL, -- cash, winnings, bonus
    balance DECIMAL(10, 2) DEFAULT 0.00 CHECK (balance >= 0),
    currency VARCHAR(3) DEFAULT 'INR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, wallet_type),
    INDEX idx_user_wallet (user_id, wallet_type)
);
```

#### Table: `transactions`
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    transaction_type VARCHAR(30) NOT NULL, -- add_money, withdrawal, game_entry, game_winning, referral_bonus, admin_adjustment
    amount DECIMAL(10, 2) NOT NULL,
    wallet_type VARCHAR(20) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, success, failed, reversed
    reference_id VARCHAR(100), -- Payment gateway reference, game ID, etc.
    reference_type VARCHAR(50), -- payment, game, referral, etc.
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_type (transaction_type),
    INDEX idx_created_at (created_at),
    INDEX idx_reference (reference_type, reference_id)
);
```

#### Table: `payment_orders`
```sql
CREATE TABLE payment_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    order_id VARCHAR(100) UNIQUE NOT NULL, -- Gateway order ID
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_gateway VARCHAR(20) NOT NULL, -- razorpay, cashfree
    payment_method VARCHAR(20), -- upi, card, netbanking
    status VARCHAR(20) DEFAULT 'created', -- created, pending, success, failed
    gateway_response JSONB,
    webhook_received_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_order_id (order_id),
    INDEX idx_status (status)
);
```

#### Table: `withdrawal_requests`
```sql
CREATE TABLE withdrawal_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    tds_amount DECIMAL(10, 2) DEFAULT 0.00,
    net_amount DECIMAL(10, 2) NOT NULL,
    bank_account_id UUID NOT NULL REFERENCES bank_accounts(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, success, failed, cancelled
    processed_by UUID REFERENCES users(id), -- Admin user ID
    utr_number VARCHAR(50), -- Bank transaction reference
    failure_reason TEXT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### Table: `tds_records`
```sql
CREATE TABLE tds_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    financial_year VARCHAR(10) NOT NULL, -- 2024-25
    quarter VARCHAR(5) NOT NULL, -- Q1, Q2, Q3, Q4
    total_winnings DECIMAL(10, 2) NOT NULL,
    tds_amount DECIMAL(10, 2) NOT NULL,
    tds_percentage DECIMAL(5, 2) DEFAULT 30.00,
    certificate_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_year (user_id, financial_year)
);
```

---

### 4. Games & Matches

#### Table: `games`
```sql
CREATE TABLE games (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_code VARCHAR(50) UNIQUE NOT NULL, -- ludo, carrom, quiz
    game_name VARCHAR(100) NOT NULL,
    game_type VARCHAR(20) NOT NULL, -- turn_based, real_time, time_based
    min_players INT NOT NULL,
    max_players INT NOT NULL,
    min_entry_fee DECIMAL(10, 2) DEFAULT 0,
    max_entry_fee DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB, -- Game-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_code (game_code),
    INDEX idx_is_active (is_active)
);
```

#### Table: `matches`
```sql
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES games(id),
    match_type VARCHAR(20) NOT NULL, -- battle, tournament, practice
    entry_fee DECIMAL(10, 2) DEFAULT 0,
    prize_pool DECIMAL(10, 2) DEFAULT 0,
    max_players INT NOT NULL,
    current_players INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'waiting', -- waiting, in_progress, completed, cancelled
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_id (game_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### Table: `match_players`
```sql
CREATE TABLE match_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    is_bot BOOLEAN DEFAULT FALSE,
    bot_difficulty VARCHAR(20), -- easy, medium, hard
    position INT, -- Player position in game (1-4 for Ludo)
    score DECIMAL(10, 2) DEFAULT 0,
    rank INT, -- Final rank after game completion
    prize_amount DECIMAL(10, 2) DEFAULT 0,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, user_id),
    INDEX idx_match_id (match_id),
    INDEX idx_user_id (user_id)
);
```

#### Table: `match_results`
```sql
CREATE TABLE match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    winner_user_id UUID REFERENCES users(id),
    result_data JSONB, -- Complete result details
    is_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_match_id (match_id),
    INDEX idx_winner (winner_user_id)
);
```

#### Table: `player_ratings`
```sql
CREATE TABLE player_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    elo_rating INT DEFAULT 1500,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, game_id),
    INDEX idx_user_game (user_id, game_id),
    INDEX idx_elo (game_id, elo_rating)
);
```

---

### 5. Tournaments

#### Table: `tournaments`
```sql
CREATE TABLE tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES games(id),
    tournament_name VARCHAR(200) NOT NULL,
    tournament_type VARCHAR(20) NOT NULL, -- free, paid, knockout, league
    entry_fee DECIMAL(10, 2) DEFAULT 0,
    max_participants INT NOT NULL,
    current_participants INT DEFAULT 0,
    prize_pool DECIMAL(10, 2) DEFAULT 0,
    prize_distribution JSONB, -- JSON array of prize breakup
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, registration_open, in_progress, completed, cancelled
    registration_start_time TIMESTAMP NOT NULL,
    registration_end_time TIMESTAMP NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_id (game_id),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
);
```

#### Table: `tournament_registrations`
```sql
CREATE TABLE tournament_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_fee_paid DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'registered', -- registered, waitlist, cancelled
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, user_id),
    INDEX idx_tournament_id (tournament_id),
    INDEX idx_user_id (user_id)
);
```

---

### 6. Referrals & Rewards

#### Table: `referrals`
```sql
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, activated, rewarded
    referrer_bonus DECIMAL(10, 2) DEFAULT 0,
    referee_bonus DECIMAL(10, 2) DEFAULT 0,
    activated_at TIMESTAMP, -- When referred user made first deposit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_referrer (referrer_user_id),
    INDEX idx_referred (referred_user_id)
);
```

#### Table: `daily_rewards`
```sql
CREATE TABLE daily_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward_date DATE NOT NULL,
    reward_type VARCHAR(20) NOT NULL, -- login, streak
    reward_amount DECIMAL(10, 2) DEFAULT 0,
    streak_count INT DEFAULT 1,
    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, reward_date),
    INDEX idx_user_date (user_id, reward_date)
);
```

#### Table: `tasks`
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_code VARCHAR(50) UNIQUE NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    task_description TEXT,
    reward_amount DECIMAL(10, 2) NOT NULL,
    reward_type VARCHAR(20) DEFAULT 'bonus', -- bonus, cash
    is_active BOOLEAN DEFAULT TRUE,
    max_completions INT DEFAULT 1, -- Per user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `task_completions`
```sql
CREATE TABLE task_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reward_given BOOLEAN DEFAULT FALSE,
    INDEX idx_user_task (user_id, task_id)
);
```

---

### 7. Fraud & Security

#### Table: `device_fingerprints`
```sql
CREATE TABLE device_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    device_name VARCHAR(100),
    device_os VARCHAR(50),
    device_model VARCHAR(100),
    is_rooted BOOLEAN DEFAULT FALSE,
    is_emulator BOOLEAN DEFAULT FALSE,
    trust_score INT DEFAULT 100, -- 0-100
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE,
    INDEX idx_user_id (user_id),
    INDEX idx_device_id (device_id)
);
```

#### Table: `ip_logs`
```sql
CREATE TABLE ip_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    country VARCHAR(50),
    region VARCHAR(100),
    city VARCHAR(100),
    is_vpn BOOLEAN DEFAULT FALSE,
    is_proxy BOOLEAN DEFAULT FALSE,
    risk_score INT DEFAULT 0, -- 0-100
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_ip (ip_address),
    INDEX idx_logged_at (logged_at)
);
```

#### Table: `fraud_alerts`
```sql
CREATE TABLE fraud_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50) NOT NULL, -- multi_account, collusion, bot, cheat
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    description TEXT,
    evidence JSONB,
    status VARCHAR(20) DEFAULT 'open', -- open, investigating, resolved, false_positive
    investigated_by UUID REFERENCES users(id), -- Admin user
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_severity (severity)
);
```

#### Table: `ban_records`
```sql
CREATE TABLE ban_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ban_type VARCHAR(20) NOT NULL, -- temporary, permanent
    ban_reason TEXT NOT NULL,
    banned_by UUID REFERENCES users(id), -- Admin user
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unban_at TIMESTAMP, -- NULL for permanent
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active)
);
```

---

### 8. Admin & System

#### Table: `admin_users`
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- super_admin, admin, support, finance
    permissions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

#### Table: `admin_audit_logs`
```sql
CREATE TABLE admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES admin_users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- user, withdrawal, tournament, etc.
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admin_user (admin_user_id),
    INDEX idx_created_at (created_at)
);
```

---

## MongoDB Schema (Document Store)

### Collection: `game_records`
```javascript
{
    _id: ObjectId,
    match_id: "uuid",
    game_code: "ludo",
    players: [
        {
            user_id: "uuid",
            username: "john_doe",
            position: 1,
            score: 100,
            rank: 1
        }
    ],
    game_data: {
        // Game-specific data
        moves: [],
        duration_seconds: 300,
        winner_position: 1
    },
    started_at: ISODate,
    completed_at: ISODate,
    created_at: ISODate
}
```

**Indexes**:
- `match_id`: unique
- `players.user_id`: multi-key index
- `created_at`: descending

---

### Collection: `game_moves`
```javascript
{
    _id: ObjectId,
    match_id: "uuid",
    user_id: "uuid",
    move_sequence: 1,
    move_data: {
        // Game-specific move data
        dice_value: 6,
        token_moved: 1,
        from_position: 10,
        to_position: 16
    },
    timestamp: ISODate,
    validation_status: "valid" // valid, invalid, suspicious
}
```

**Indexes**:
- `match_id, move_sequence`: compound index
- `match_id, user_id`: compound index

---

### Collection: `notification_history`
```javascript
{
    _id: ObjectId,
    user_id: "uuid",
    notification_type: "push", // push, sms, email, in_app
    title: "Match Found!",
    body: "Your match is ready. Join now!",
    data: {
        match_id: "uuid",
        action: "join_match"
    },
    status: "sent", // sent, delivered, failed, read
    sent_at: ISODate,
    delivered_at: ISODate,
    read_at: ISODate
}
```

**Indexes**:
- `user_id, sent_at`: compound index descending
- `status`: single field index

---

### Collection: `analytics_events`
```javascript
{
    _id: ObjectId,
    event_type: "game_started",
    user_id: "uuid",
    event_data: {
        game_code: "ludo",
        match_id: "uuid",
        entry_fee: 50
    },
    session_id: "session_uuid",
    device_info: {
        os: "android",
        version: "12",
        app_version: "1.0.0"
    },
    timestamp: ISODate
}
```

**Indexes**:
- `event_type, timestamp`: compound index
- `user_id, timestamp`: compound index

---

### Collection: `fraud_behavior_logs`
```javascript
{
    _id: ObjectId,
    user_id: "uuid",
    match_id: "uuid",
    behavior_type: "suspicious_timing",
    details: {
        average_move_time_ms: 50,
        expected_min_time_ms: 200,
        confidence_score: 0.95
    },
    ai_prediction: {
        is_fraud: true,
        fraud_probability: 0.89
    },
    timestamp: ISODate
}
```

**Indexes**:
- `user_id, timestamp`: compound index
- `behavior_type`: single field index

---

## Redis Schema (Cache & Real-time Data)

### Key Patterns:

#### 1. Session Management
```
Key: session:{session_id}
Type: Hash
TTL: 30 minutes
Fields:
    user_id: "uuid"
    device_id: "device_uuid"
    created_at: timestamp
    last_activity: timestamp
```

#### 2. Leaderboards
```
Key: leaderboard:{game_code}:global
Type: Sorted Set
Score: ELO rating or points
Member: user_id

Commands:
ZADD leaderboard:ludo:global 1850 user_id_1
ZREVRANGE leaderboard:ludo:global 0 99 WITHSCORES  # Top 100
ZREVRANK leaderboard:ludo:global user_id_1  # User's rank
```

#### 3. Tournament Leaderboards
```
Key: tournament:{tournament_id}:leaderboard
Type: Sorted Set
Score: Total points
Member: user_id
TTL: 7 days after tournament end
```

#### 4. Matchmaking Queue
```
Key: queue:{game_code}:{skill_range}
Type: List
Value: JSON string of player data

LPUSH queue:ludo:1400-1600 '{"user_id":"uuid","elo":1500}'
RPOP queue:ludo:1400-1600  # Get next player
```

#### 5. Active Matches
```
Key: match:{match_id}:state
Type: Hash
TTL: 1 hour
Fields:
    current_turn: user_id
    game_state: JSON string
    started_at: timestamp
    player_count: 4
```

#### 6. User Online Status
```
Key: user:{user_id}:online
Type: String
Value: "true"
TTL: 5 minutes (auto-refresh)
```

#### 7. Rate Limiting
```
Key: ratelimit:{user_id}:{action}
Type: String
Value: request count
TTL: 1 hour

Example:
INCR ratelimit:user123:add_money
EXPIRE ratelimit:user123:add_money 3600
```

#### 8. Cache: User Profile
```
Key: cache:user:{user_id}:profile
Type: Hash
TTL: 10 minutes
Fields:
    username: "john_doe"
    avatar_url: "https://..."
    level: 10
    elo_ludo: 1850
```

#### 9. Cache: Wallet Balance
```
Key: cache:wallet:{user_id}
Type: Hash
TTL: 1 minute
Fields:
    cash: 1000.50
    winnings: 500.00
    bonus: 100.00
```

#### 10. Tournament Countdown
```
Key: tournament:{tournament_id}:countdown
Type: String
Value: remaining_seconds
TTL: Auto-decrement
```

---

## Elasticsearch Schema (Logs & Analytics)

### Index: `application_logs`
```json
{
    "timestamp": "2025-01-16T10:30:00Z",
    "level": "ERROR",
    "service": "game_service",
    "message": "Failed to save game state",
    "user_id": "uuid",
    "match_id": "uuid",
    "error": {
        "type": "DatabaseException",
        "stack_trace": "..."
    },
    "metadata": {}
}
```

---

### Index: `user_activity`
```json
{
    "timestamp": "2025-01-16T10:30:00Z",
    "user_id": "uuid",
    "activity_type": "game_played",
    "game_code": "ludo",
    "match_id": "uuid",
    "duration_seconds": 300,
    "result": "won",
    "amount_won": 100.00
}
```

---

## Data Relationships

```
users (1) ─── (M) wallets
users (1) ─── (M) transactions
users (1) ─── (M) matches (via match_players)
users (1) ─── (1) user_statistics
users (1) ─── (M) referrals (as referrer)
users (1) ─── (M) referrals (as referee)

games (1) ─── (M) matches
matches (1) ─── (M) match_players
matches (1) ─── (1) match_results

tournaments (1) ─── (M) tournament_registrations
games (1) ─── (M) tournaments
```

---

## Backup Strategy

### PostgreSQL
- **Continuous Archiving**: WAL archiving
- **Point-in-Time Recovery**: Enabled
- **Automated Backups**: Every 6 hours
- **Retention**: 30 days

### MongoDB
- **Replica Set**: 3 nodes
- **Oplog**: Enabled
- **Automated Backups**: Daily
- **Retention**: 30 days

### Redis
- **Persistence**: RDB + AOF
- **Snapshot**: Every hour
- **Retention**: 7 days

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Total Tables (PostgreSQL)**: 35+
**Total Collections (MongoDB)**: 5+
**Total Redis Patterns**: 10+
