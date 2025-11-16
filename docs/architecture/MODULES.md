# Complete Module & Submodule Breakdown

## Module A: User Management Module

### A.1 Authentication Submodule
**Location**: `backend/services/user_service/auth/`

#### Features:
- **OTP Login**
  - Send OTP via SMS
  - Verify OTP (6-digit)
  - OTP expiry (5 minutes)
  - Rate limiting (max 3 OTPs per hour)

- **Email Login**
  - Email validation
  - Password hashing (bcrypt)
  - Password reset flow
  - Email verification

- **Social Login**
  - Google OAuth 2.0
  - Facebook Login
  - Apple Sign In

- **JWT Token Management**
  - Access token (30 minutes)
  - Refresh token (30 days)
  - Token rotation
  - Token blacklisting

#### Database Tables:
- `users`
- `user_sessions`
- `otp_attempts`
- `social_auth_tokens`

---

### A.2 User Profile Submodule
**Location**: `backend/services/user_service/profile/`

#### Features:
- **Profile Management**
  - Username (unique, 3-20 chars)
  - Display name
  - Avatar upload (S3/Cloudinary)
  - Phone number
  - Email
  - Date of birth (age verification)

- **User Statistics**
  - Total games played
  - Win/Loss ratio
  - Winnings
  - Current level
  - ELO rating (per game)

- **Badges & Achievements**
  - First win badge
  - 10/50/100 games badge
  - Tournament winner
  - Referral champion
  - Daily streak badges

#### Database Tables:
- `user_profiles`
- `user_statistics`
- `user_badges`
- `achievements`

---

### A.3 KYC & Verification Submodule
**Location**: `backend/services/user_service/kyc/`

#### Features:
- **Document Verification**
  - Aadhaar verification (Digio API)
  - PAN verification
  - Driving license
  - Age verification (18+)

- **Bank Verification**
  - Bank account details
  - IFSC code validation
  - Penny drop verification

- **KYC Status**
  - Pending
  - Under review
  - Approved
  - Rejected (with reason)

- **Withdrawal Limits**
  - Before KYC: ₹0
  - After KYC: ₹1,00,000 per day

#### Database Tables:
- `kyc_documents`
- `kyc_status`
- `bank_accounts`

---

### A.4 Device & Security Submodule
**Location**: `backend/services/user_service/security/`

#### Features:
- **Device Binding**
  - Device fingerprinting
  - Max 3 devices per user
  - Device trust score

- **IP Tracking**
  - IP geolocation
  - VPN/Proxy detection
  - Suspicious IP flagging

- **Two-Factor Authentication (2FA)**
  - TOTP (Google Authenticator)
  - SMS backup codes

- **Security Alerts**
  - New device login
  - Unusual location
  - Failed login attempts

#### Database Tables:
- `user_devices`
- `ip_logs`
- `security_alerts`
- `login_attempts`

---

## Module B: Wallet & Payments Module

### B.1 Wallet Management Submodule
**Location**: `backend/services/wallet_service/wallet/`

#### Features:
- **Multi-Wallet System**
  - **Cash Wallet**: Deposited money (withdrawable)
  - **Winnings Wallet**: Game winnings (withdrawable after TDS)
  - **Bonus Wallet**: Promotional bonuses (non-withdrawable, usable for entry)

- **Wallet Operations**
  - Get balance (all wallets)
  - Deduct from wallet (priority: Bonus → Cash → Winnings)
  - Add to wallet
  - Wallet transfer restrictions

- **Bonus Rules**
  - Expiry dates
  - Usage limits
  - Game restrictions
  - Wagering requirements

#### Database Tables:
- `wallets`
- `wallet_transactions`
- `bonus_wallets`
- `bonus_rules`

---

### B.2 Add Money Submodule
**Location**: `backend/services/payment_service/add_money/`

#### Features:
- **Payment Methods**
  - UPI (GPay, PhonePe, Paytm)
  - Debit/Credit Cards
  - Net Banking
  - Wallets (Paytm, PhonePe)

- **Payment Gateway Integration**
  - Razorpay (Primary)
  - Cashfree (Backup)
  - Order creation
  - Payment verification
  - Webhook handling

- **Transaction Flow**
  - Create order
  - Redirect to payment gateway
  - Verify payment signature
  - Update wallet
  - Send confirmation

#### Database Tables:
- `payment_orders`
- `payment_transactions`
- `gateway_webhooks`

---

### B.3 Withdraw Money Submodule
**Location**: `backend/services/payment_service/withdraw/`

#### Features:
- **Withdrawal Process**
  - Minimum withdrawal: ₹100
  - Maximum withdrawal: ₹1,00,000 per day
  - KYC mandatory
  - Bank account verification

- **TDS Calculation**
  - 30% TDS on winnings > ₹10,000
  - TDS certificate generation

- **Withdrawal Methods**
  - Bank transfer (IMPS/NEFT)
  - UPI transfer

- **Withdrawal Status**
  - Pending
  - Processing
  - Success
  - Failed (with reason)
  - Reversed

#### Database Tables:
- `withdrawal_requests`
- `tds_records`
- `withdrawal_logs`

---

### B.4 Transaction Management Submodule
**Location**: `backend/services/wallet_service/transactions/`

#### Features:
- **Transaction Types**
  - Add money
  - Withdrawal
  - Game entry fee
  - Game winnings
  - Referral bonus
  - Admin adjustment
  - Refund

- **Transaction Logs**
  - Complete audit trail
  - Transaction ID (unique)
  - Timestamp
  - Amount
  - Wallet type
  - Status

- **Reconciliation**
  - Daily reconciliation report
  - Gateway vs DB matching
  - Dispute management

#### Database Tables:
- `transactions`
- `transaction_logs`
- `reconciliation_reports`

---

## Module C: Game Engine Module

### C.1 Game Management Submodule
**Location**: `backend/services/game_service/games/`

#### Features:
- **Game Registry**
  - Game ID
  - Game name
  - Game type (Turn-based, Real-time)
  - Min/Max players
  - Entry fee range
  - Status (Active/Inactive)

- **Supported Games**
  - **Ludo**: 2-4 players, turn-based
  - **Carrom**: 2-4 players, turn-based
  - **Quiz**: 1-100 players, time-based
  - **Cricket Fantasy**: Team building, live scoring
  - **Rummy**: 2-6 players, card game
  - **Chess**: 2 players, turn-based
  - **8 Ball Pool**: 2 players, real-time
  - **Bubble Shooter**: Single player, time-based
  - **Archery**: Single player, score-based

#### Database Tables:
- `games`
- `game_configs`
- `game_rules`

---

### C.2 Game Logic Submodule
**Location**: `backend/services/game_service/logic/`

#### Features:
- **Game-Specific Logic**
  - Ludo: Dice roll, token movement, rules
  - Carrom: Physics simulation, scoring
  - Quiz: Question randomization, scoring
  - Each game has separate logic module

- **Game State Management**
  - Current turn
  - Player positions
  - Score tracking
  - Time limits

- **Move Validation**
  - Valid move checking
  - Anti-cheat validation
  - Turn sequence enforcement

#### Database Tables:
- `game_states`
- `game_moves`
- `game_snapshots`

---

### C.3 Match Management Submodule
**Location**: `backend/services/game_service/matches/`

#### Features:
- **Match Creation**
  - Match ID generation
  - Player assignment
  - Entry fee collection
  - Prize pool calculation

- **Match Types**
  - **1v1 Battle**: Direct competition
  - **1v4 Battle**: Multi-player
  - **Tournament Match**: Part of tournament
  - **Practice Match**: No entry fee

- **Match Lifecycle**
  - Created → Waiting → In Progress → Completed → Settled

- **Result Calculation**
  - Winner determination
  - Prize distribution
  - Tie handling
  - Dispute resolution

#### Database Tables:
- `matches`
- `match_players`
- `match_results`
- `prize_distributions`

---

### C.4 Bot Players Submodule
**Location**: `backend/services/game_service/bots/`

#### Features:
- **Bot Difficulty Levels**
  - Easy: Basic moves
  - Medium: Moderate strategy
  - Hard: Advanced AI

- **Bot Behavior**
  - Simulated human timing
  - Mistake probability
  - Learning from patterns

- **Bot Usage**
  - Fill matches when players unavailable
  - Practice mode
  - Tutorial mode

#### Database Tables:
- `bot_profiles`
- `bot_difficulty_settings`

---

## Module D: Matchmaking Module

### D.1 Queue Management Submodule
**Location**: `backend/services/matchmaking_service/queue/`

#### Features:
- **Queue Types**
  - Quick match (any skill level)
  - Skill-based match
  - Tournament queue

- **Queue Operations**
  - Join queue
  - Leave queue
  - Queue position
  - Estimated wait time

- **Queue Priority**
  - VIP users
  - Premium members
  - Waiting time

#### Database Tables:
- `matchmaking_queue`
- `queue_history`

---

### D.2 Skill-Based Matching Submodule
**Location**: `backend/services/matchmaking_service/matching/`

#### Features:
- **ELO Rating System**
  - Initial rating: 1500
  - Rating calculation after each game
  - Separate rating per game type

- **Matchmaking Algorithm**
  - Match players with ±200 ELO range
  - Expand range after 30 seconds
  - Consider win/loss ratio
  - Consider recent performance

- **Fair Play Matching**
  - Avoid repeated opponents
  - Region-based matching (low latency)
  - Device type consideration

#### Database Tables:
- `player_ratings`
- `elo_history`
- `match_history`

---

### D.3 Room Management Submodule
**Location**: `backend/services/matchmaking_service/rooms/`

#### Features:
- **Room Creation**
  - Unique room ID
  - Room capacity
  - Entry fee
  - Game type

- **Room States**
  - Waiting for players
  - Full
  - In progress
  - Completed

- **WebSocket Rooms**
  - Real-time player join/leave
  - Room chat
  - Ready status

#### Database Tables:
- `game_rooms`
- `room_players`
- `room_events`

---

## Module E: Tournament Module

### E.1 Tournament Management Submodule
**Location**: `backend/services/tournament_service/management/`

#### Features:
- **Tournament Types**
  - **Free Tournaments**: No entry fee
  - **Paid Tournaments**: Entry fee required
  - **Mega Contests**: Large prize pools
  - **League**: Season-based
  - **Knockout**: Single elimination

- **Tournament Configuration**
  - Name & description
  - Game type
  - Entry fee
  - Max participants
  - Start & end time
  - Prize distribution (%, fixed)

- **Tournament Lifecycle**
  - Scheduled → Registration Open → Full → In Progress → Completed → Settled

#### Database Tables:
- `tournaments`
- `tournament_configs`
- `tournament_schedules`

---

### E.2 Tournament Registration Submodule
**Location**: `backend/services/tournament_service/registration/`

#### Features:
- **Registration Process**
  - Check eligibility
  - Deduct entry fee
  - Assign tournament ID
  - Send confirmation

- **Registration Limits**
  - Max entries per user (usually 1)
  - Multiple teams (for fantasy)
  - Late registration cutoff

- **Registration Status**
  - Registered
  - Waitlist
  - Cancelled (refund)

#### Database Tables:
- `tournament_registrations`
- `tournament_waitlist`

---

### E.3 Leaderboard Submodule
**Location**: `backend/services/leaderboard_service/`

#### Features:
- **Leaderboard Types**
  - Tournament leaderboard
  - Global leaderboard (all-time)
  - Weekly leaderboard
  - Monthly leaderboard
  - Game-specific leaderboard

- **Ranking Calculation**
  - Real-time score updates
  - Tie-breaker rules
  - Historical rankings

- **Leaderboard Display**
  - Top 100
  - User rank
  - Rank change indicator
  - Prize position indicator

#### Database Tables:
- `leaderboards` (Redis sorted sets)
- `leaderboard_snapshots` (MongoDB)

---

### E.4 Prize Distribution Submodule
**Location**: `backend/services/tournament_service/prizes/`

#### Features:
- **Prize Pool Calculation**
  - Total pool = Entry fee × Participants
  - Platform fee deduction
  - Prize distribution percentage

- **Prize Distribution**
  - Winner: 50%
  - Runner-up: 30%
  - 3rd place: 15%
  - 4th-10th: Share 5%

- **Payout Process**
  - Auto-credit to winning wallet
  - TDS deduction
  - Prize history

#### Database Tables:
- `prize_pools`
- `prize_distributions`
- `winner_payouts`

---

## Module F: Referral & Rewards Module

### F.1 Referral Management Submodule
**Location**: `backend/services/referral_service/`

#### Features:
- **Referral Code**
  - Unique code per user (e.g., JOHN1234)
  - Shareable link
  - QR code

- **Referral Tracking**
  - Track who referred whom
  - Multi-level tracking (up to 3 levels)

- **Referral Rewards**
  - **Referrer**: ₹50 bonus when friend joins
  - **Referee**: ₹50 bonus on first deposit
  - **Referrer**: 5% of friend's entry fees (for 30 days)

- **Referral Limits**
  - Max ₹10,000 per month
  - Fraud prevention checks

#### Database Tables:
- `referral_codes`
- `referral_tracking`
- `referral_rewards`

---

### F.2 Rewards & Bonuses Submodule
**Location**: `backend/services/rewards_service/`

#### Features:
- **Daily Rewards**
  - Login bonus (₹5 daily)
  - Streak bonus (7-day streak = ₹100)

- **Task-Based Rewards**
  - Play first game: ₹20
  - Win first game: ₹50
  - Complete profile: ₹10

- **Spin & Win**
  - Daily spin wheel
  - Prizes: ₹5 to ₹1000

- **Level-Based Rewards**
  - Level up bonus
  - Milestone rewards

#### Database Tables:
- `daily_rewards`
- `tasks`
- `task_completions`
- `spin_history`

---

## Module G: Fraud & Fairplay Module

### G.1 Fraud Detection Submodule
**Location**: `backend/services/fraud_service/detection/`

#### Features:
- **Multi-Accounting Detection**
  - Same device ID
  - Same IP address
  - Similar gameplay patterns
  - Same payment method

- **Collusion Detection**
  - Players consistently playing together
  - Intentional losing patterns
  - Prize splitting indicators

- **Bot Detection**
  - Inhuman reaction times
  - Perfect accuracy
  - Repetitive patterns

#### Database Tables:
- `fraud_alerts`
- `suspicious_accounts`
- `device_fingerprints`

---

### G.2 Anti-Cheat Submodule
**Location**: `backend/services/fraud_service/anti_cheat/`

#### Features:
- **Client-Side Checks**
  - Root/Jailbreak detection
  - Screen recording detection
  - Emulator detection
  - Modified APK detection

- **Server-Side Validation**
  - Move validation
  - Timing validation
  - Score validation

- **Cheat Patterns**
  - Speed hacking
  - Auto-clicker
  - Memory manipulation

#### Database Tables:
- `cheat_detections`
- `banned_devices`

---

### G.3 AI Monitoring Submodule
**Location**: `backend/services/fraud_service/ai/`

#### Features:
- **ML Models**
  - Win pattern anomaly detection
  - Player behavior clustering
  - Fraud probability scoring

- **Real-Time Monitoring**
  - Live gameplay monitoring
  - Instant alerts on high-risk behavior

- **Actions**
  - Warning
  - Temporary ban
  - Permanent ban
  - Manual review flag

#### Database Tables:
- `ai_predictions`
- `behavior_logs`
- `ban_records`

---

## Module H: Admin Panel Module

### H.1 User Management (Admin)
**Location**: `admin-panel/src/pages/users/`

#### Features:
- **User Search**
  - Search by username, email, phone
  - Filter by status, KYC, level

- **User Actions**
  - View user details
  - Ban/unban user
  - Adjust wallet
  - Approve/reject KYC
  - View transaction history

- **Bulk Operations**
  - Bulk ban
  - Bulk bonus distribution

---

### H.2 Game Management (Admin)
**Location**: `admin-panel/src/pages/games/`

#### Features:
- **Game Configuration**
  - Enable/disable games
  - Set entry fee limits
  - Configure game rules

- **Game Monitoring**
  - Active games count
  - Game-wise revenue
  - Popular games analytics

---

### H.3 Financial Management (Admin)
**Location**: `admin-panel/src/pages/finance/`

#### Features:
- **Withdrawal Approval**
  - View pending withdrawals
  - Approve/reject
  - Bulk approval

- **Payment Monitoring**
  - Failed payments
  - Refund requests
  - Reconciliation reports

- **Revenue Dashboard**
  - Daily/weekly/monthly revenue
  - Game-wise revenue
  - Payment method breakdown

---

### H.4 Tournament Management (Admin)
**Location**: `admin-panel/src/pages/tournaments/`

#### Features:
- **Create Tournament**
  - Configure all parameters
  - Set prize distribution
  - Schedule tournament

- **Monitor Tournaments**
  - Live tournament status
  - Participant count
  - Prize pool

---

### H.5 Fraud Management (Admin)
**Location**: `admin-panel/src/pages/fraud/`

#### Features:
- **Fraud Alerts Dashboard**
  - High-priority alerts
  - Suspicious accounts
  - Review queue

- **Investigation Tools**
  - User device history
  - IP logs
  - Match history
  - Transaction patterns

- **Actions**
  - Ban user
  - Flag for review
  - Dismiss alert

---

### H.6 Analytics Dashboard (Admin)
**Location**: `admin-panel/src/pages/analytics/`

#### Features:
- **User Analytics**
  - DAU, MAU, WAU
  - User retention
  - Cohort analysis

- **Game Analytics**
  - Games played per day
  - Average game duration
  - Popular games

- **Financial Analytics**
  - Total deposits
  - Total withdrawals
  - Net revenue
  - ARPU (Average Revenue Per User)

---

### H.7 Marketing Management (Admin)
**Location**: `admin-panel/src/pages/marketing/`

#### Features:
- **Push Notifications**
  - Create campaign
  - Target audience selection
  - Schedule notification

- **Bonus Distribution**
  - Create bonus offer
  - Target specific users
  - Set expiry

- **Coupon Management**
  - Create coupon codes
  - Usage limits
  - Track redemptions

---

## Module I: Notification Module

### I.1 Push Notifications
**Location**: `backend/services/notification_service/push/`

#### Features:
- **FCM Integration** (Firebase Cloud Messaging)
- **Notification Types**
  - Game start reminder
  - Match found
  - Tournament starting
  - Money added/withdrawn
  - Referral reward
  - Daily reward

- **Targeting**
  - Individual user
  - User segment
  - All users

- **Scheduling**
  - Immediate
  - Scheduled
  - Recurring

---

### I.2 SMS Notifications
**Location**: `backend/services/notification_service/sms/`

#### Features:
- **Twilio/MSG91 Integration**
- **SMS Types**
  - OTP
  - Withdrawal success
  - KYC approved
  - Security alerts

- **Template Management**
  - DLT registration
  - Template variables

---

### I.3 Email Notifications
**Location**: `backend/services/notification_service/email/`

#### Features:
- **SendGrid Integration**
- **Email Types**
  - Welcome email
  - Password reset
  - Weekly summary
  - Promotional emails

- **Email Templates**
  - HTML templates
  - Personalization

---

### I.4 In-App Notifications
**Location**: `backend/services/notification_service/in_app/`

#### Features:
- **Notification Center**
  - Unread count
  - Notification history
  - Mark as read

- **Real-Time Updates**
  - WebSocket push
  - Badge updates

---

## Module J: Analytics Module

### J.1 User Analytics
**Location**: `backend/services/analytics_service/user/`

#### Features:
- **User Metrics**
  - Daily Active Users (DAU)
  - Monthly Active Users (MAU)
  - Session duration
  - User retention

- **Cohort Analysis**
  - Registration cohorts
  - Retention by cohort
  - LTV by cohort

---

### J.2 Game Analytics
**Location**: `backend/services/analytics_service/game/`

#### Features:
- **Game Metrics**
  - Total games played
  - Average game duration
  - Game completion rate
  - Popular games

- **Revenue Analytics**
  - Revenue per game
  - Entry fee distribution
  - Prize pool analysis

---

### J.3 Financial Analytics
**Location**: `backend/services/analytics_service/finance/`

#### Features:
- **Revenue Metrics**
  - Total deposits
  - Total withdrawals
  - Net revenue
  - Platform fee collected

- **User Economics**
  - ARPU (Average Revenue Per User)
  - LTV (Lifetime Value)
  - CAC (Customer Acquisition Cost)

---

### J.4 Event Tracking
**Location**: `backend/services/analytics_service/events/`

#### Features:
- **Event Types**
  - User registration
  - Game start/end
  - Payment events
  - Feature usage

- **Integration**
  - Google Analytics
  - Mixpanel
  - Custom analytics

---

## Summary

**Total Modules**: 10 major modules
**Total Submodules**: 50+ submodules
**Microservices**: 11 independent services
**Database Tables**: 100+ tables

Each module is designed to be:
- **Independent**: Can be developed and deployed separately
- **Scalable**: Horizontal scaling support
- **Testable**: Unit and integration tests
- **Documented**: API documentation
- **Monitored**: Logging and metrics

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Owner**: Engineering Team
