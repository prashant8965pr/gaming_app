# 📱 Gaming Platform - Complete Features & User Flow Guide

## 📊 Executive Summary

**Total Features Implemented:** 50+
**Total API Endpoints:** 150+
**Database Tables:** 40+
**User Flows:** 15 Major Flows

---

## 🎯 COMPLETE FEATURE LIST

### 1️⃣ **AUTHENTICATION & USER MANAGEMENT** (Phase 1 & 5)

#### Features:
- ✅ OTP-based Phone Authentication
- ✅ JWT Token Authentication (Access + Refresh)
- ✅ Two-Factor Authentication (2FA/TOTP)
- ✅ Backup Codes for 2FA
- ✅ User Profile Management
- ✅ Password Reset via OTP
- ✅ Session Management

#### API Endpoints (15):
```
POST   /api/v1/auth/send-otp                    - Send OTP to phone
POST   /api/v1/auth/verify-otp                  - Verify OTP and login
POST   /api/v1/auth/refresh-token               - Refresh JWT token
POST   /api/v1/auth/logout                      - Logout user

POST   /api/v1/2fa/setup                        - Setup 2FA
POST   /api/v1/2fa/verify                       - Verify 2FA code
POST   /api/v1/2fa/disable                      - Disable 2FA
GET    /api/v1/2fa/backup-codes                 - Get backup codes
POST   /api/v1/2fa/regenerate-backup-codes      - Regenerate backup codes

GET    /api/v1/users/profile                    - Get user profile
PUT    /api/v1/users/profile                    - Update profile
GET    /api/v1/users/stats                      - Get user statistics
POST   /api/v1/users/avatar                     - Upload avatar
DELETE /api/v1/users/account                    - Delete account
GET    /api/v1/users/search                     - Search users
```

#### User Flow:
```
1. User enters phone number
2. Receives OTP via SMS
3. Verifies OTP
4. Gets JWT tokens (access + refresh)
5. Optional: Setup 2FA for extra security
6. Access protected endpoints with token
```

---

### 2️⃣ **KYC VERIFICATION** (Phase 2)

#### Features:
- ✅ Aadhaar Card Verification
- ✅ PAN Card Verification
- ✅ Document Upload (Photo + Back)
- ✅ Auto-OCR Extraction
- ✅ Verification Status Tracking
- ✅ Re-submission on Rejection

#### API Endpoints (6):
```
POST   /api/v1/kyc/submit                       - Submit KYC documents
GET    /api/v1/kyc/status                       - Get KYC status
PUT    /api/v1/kyc/update                       - Update KYC details
POST   /api/v1/kyc/verify                       - Verify documents (admin)
POST   /api/v1/kyc/reject                       - Reject KYC (admin)
GET    /api/v1/kyc/pending                      - List pending KYC (admin)
```

#### User Flow:
```
1. User uploads Aadhaar (front + back)
2. User uploads PAN card
3. System extracts details via OCR
4. User confirms/edits extracted data
5. Admin reviews documents
6. Status: Verified/Rejected/Pending
7. If rejected: User can resubmit
```

---

### 3️⃣ **MULTI-WALLET SYSTEM** (Phase 2)

#### Features:
- ✅ Cash Wallet (Deposits)
- ✅ Bonus Wallet (Non-withdrawable)
- ✅ Winnings Wallet (Game winnings)
- ✅ Wallet Transfers
- ✅ Transaction History
- ✅ Balance Tracking

#### API Endpoints (12):
```
GET    /api/v1/wallet/balance                   - Get all wallet balances
GET    /api/v1/wallet/balance/{type}            - Get specific wallet
POST   /api/v1/wallet/transfer                  - Transfer between wallets
GET    /api/v1/wallet/transactions              - Transaction history
GET    /api/v1/wallet/transactions/{id}         - Transaction details

POST   /api/v1/wallet/deposit                   - Create deposit order
POST   /api/v1/wallet/deposit/callback          - Payment callback
POST   /api/v1/wallet/withdraw                  - Withdraw to bank
GET    /api/v1/wallet/withdrawals               - Withdrawal history
PUT    /api/v1/wallet/withdrawals/{id}          - Update withdrawal status

GET    /api/v1/wallet/deposit-methods           - Available deposit methods
GET    /api/v1/wallet/limits                    - Wallet limits
```

#### User Flow:
```
DEPOSIT:
1. User selects deposit amount
2. Chooses payment method
3. Gets redirected to payment gateway
4. Completes payment
5. Cash wallet credited

WITHDRAWAL:
1. User selects withdrawal amount
2. Chooses bank account
3. Submits withdrawal request
4. Admin approves (24-48 hrs)
5. Amount transferred to bank
```

---

### 4️⃣ **BANK ACCOUNT MANAGEMENT** (Phase 2)

#### Features:
- ✅ Add Multiple Bank Accounts
- ✅ Verify via Penny Drop
- ✅ Set Primary Account
- ✅ IFSC Validation
- ✅ Delete Bank Account

#### API Endpoints (6):
```
POST   /api/v1/bank/add                         - Add bank account
GET    /api/v1/bank/list                        - List bank accounts
PUT    /api/v1/bank/{id}/set-primary            - Set primary account
DELETE /api/v1/bank/{id}                        - Delete bank account
POST   /api/v1/bank/{id}/verify                 - Verify via penny drop
GET    /api/v1/bank/ifsc/{code}                 - Get IFSC details
```

#### User Flow:
```
1. User adds bank details
2. System validates IFSC code
3. Optional: Penny drop verification
4. Account marked as verified
5. User can set as primary for withdrawals
```

---

### 5️⃣ **REFERRAL & REWARDS** (Phase 3)

#### Features:
- ✅ Unique Referral Codes
- ✅ Referral Link Generation
- ✅ Referral Tracking
- ✅ Tiered Rewards
- ✅ Referral Statistics
- ✅ Reward History

#### API Endpoints (4):
```
GET    /api/v1/rewards/referrals/stats          - Referral statistics
GET    /api/v1/rewards/referrals/list           - List all referrals
POST   /api/v1/rewards/referrals/check-code     - Validate referral code
GET    /api/v1/rewards/dashboard                - Rewards dashboard
```

#### Referral Rewards:
```
REFERRER GETS:
- ₹100 when friend completes KYC
- ₹50 when friend makes first deposit (₹500+)
- ₹25 when friend plays first game

REFERRED USER GETS:
- ₹50 welcome bonus on signup
- 100 practice tokens
```

#### User Flow:
```
1. User gets unique referral code
2. Shares link with friends
3. Friend signs up using code
4. Friend completes actions (KYC, deposit, game)
5. Both users earn rewards
6. Track earnings in dashboard
```

---

### 6️⃣ **ACHIEVEMENTS & GAMIFICATION** (Phase 3)

#### Features:
- ✅ 50+ Achievements
- ✅ Achievement Categories (Gaming, Social, Milestone)
- ✅ Progress Tracking
- ✅ Reward Claiming
- ✅ Achievement Points
- ✅ Badges & Titles

#### API Endpoints (5):
```
GET    /api/v1/rewards/achievements/list        - List achievements
GET    /api/v1/rewards/achievements/progress    - Get progress
POST   /api/v1/rewards/achievements/claim       - Claim reward
GET    /api/v1/rewards/achievements/categories  - Achievement categories
GET    /api/v1/rewards/dashboard                - Overall progress
```

#### Achievement Examples:
```
GAMING:
- First Win (10 XP, ₹10 bonus)
- Win Streak 5 (50 XP, ₹50 bonus)
- Play 100 Games (100 XP, ₹100 bonus)
- Tournament Winner (200 XP, ₹200 bonus)

SOCIAL:
- Invite 5 Friends (50 XP, ₹50 bonus)
- Play with Friends 10 times (30 XP)

MILESTONE:
- Complete KYC (25 XP, ₹25 bonus)
- First Deposit ₹500+ (50 XP, ₹50 bonus)
- Reach Level 10 (100 XP, ₹100 bonus)
```

#### User Flow:
```
1. User performs actions (win games, invite friends, etc.)
2. Achievement progress updates automatically
3. Notification when achievement unlocked
4. User claims reward
5. Bonus credited to wallet
6. XP added to level progression
```

---

### 7️⃣ **LEADERBOARD SYSTEM** (Phase 3)

#### Features:
- ✅ Daily/Weekly/Monthly/All-time Rankings
- ✅ Multiple Categories (Winnings, Wins, Win Rate)
- ✅ Real-time Rank Updates
- ✅ Rank Change Tracking
- ✅ Top Players Showcase
- ✅ User's Current Rank

#### API Endpoints (3):
```
POST   /api/v1/rewards/leaderboards/query       - Query leaderboard
GET    /api/v1/rewards/leaderboards/my-rank     - Get user's rank
GET    /api/v1/rewards/leaderboards/top         - Top 10 players
```

#### Leaderboard Categories:
```
WINNINGS: Total earnings
GAMES_WON: Number of wins
WIN_RATE: Win percentage
REFERRALS: Most referrals
```

#### User Flow:
```
1. User plays games and earns
2. Rank calculated in real-time
3. View position on leaderboard
4. See rank change (+/- from previous)
5. Top 3 players get special rewards
```

---

### 8️⃣ **DAILY BONUS & PROMO CODES** (Phase 3)

#### Features:
- ✅ Daily Login Bonuses
- ✅ Streak Tracking (7-day cycle)
- ✅ Promo Code System
- ✅ Percentage/Fixed Discounts
- ✅ Usage Limits
- ✅ Expiry Management

#### API Endpoints (7):
```
GET    /api/v1/rewards/daily-bonus/status       - Check bonus availability
POST   /api/v1/rewards/daily-bonus/claim        - Claim daily bonus

POST   /api/v1/rewards/promo/validate           - Validate promo code
POST   /api/v1/admin/promo/create               - Create promo code
GET    /api/v1/admin/promo/list                 - List promo codes
PUT    /api/v1/admin/promo/update/{id}          - Update promo code
GET    /api/v1/rewards/history                  - Reward history
```

#### Daily Bonus Calendar:
```
Day 1: ₹10
Day 2: ₹15
Day 3: ₹20
Day 4: ₹25
Day 5: ₹30
Day 6: ₹40
Day 7: ₹50 (Total: ₹190/week)
```

#### User Flow:
```
DAILY BONUS:
1. User logs in daily
2. Claims daily bonus
3. Streak continues if claimed daily
4. Miss a day = streak resets

PROMO CODE:
1. User enters promo code
2. System validates code
3. Discount applied to deposit/entry
4. Usage count incremented
```

---

### 9️⃣ **GAME MANAGEMENT** (Phase 4)

#### Features:
- ✅ Multiple Game Types (Ludo, Rummy, Poker, Quiz, etc.)
- ✅ Game Session Management
- ✅ Practice Mode (Free tokens)
- ✅ Cash Games (Real money)
- ✅ Real-time Gameplay via WebSocket
- ✅ Game History
- ✅ Match Results

#### API Endpoints (12):
```
GET    /api/v1/games/list                       - List available games
GET    /api/v1/games/{id}                       - Game details
POST   /api/v1/games/create-session             - Create game session
POST   /api/v1/games/join-session/{id}          - Join game session
POST   /api/v1/games/start-session/{id}         - Start game
POST   /api/v1/games/submit-move                - Submit game move
POST   /api/v1/games/complete-session/{id}      - Complete game
GET    /api/v1/games/sessions/active            - Active sessions
GET    /api/v1/games/sessions/history           - Game history
GET    /api/v1/games/sessions/{id}/details      - Session details

WS     /api/v1/ws/game/{session_id}             - Real-time gameplay
WS     /api/v1/ws/notifications                 - Real-time notifications
```

#### Game Types:
```
1. LUDO - 2-4 players, ₹10-₹10,000 entry
2. RUMMY - 2-6 players, ₹25-₹5,000 entry
3. POKER - 2-9 players, ₹50-₹10,000 entry
4. QUIZ - 2+ players, ₹5-₹1,000 entry
5. CARROM - 2-4 players, ₹10-₹5,000 entry
6. POOL - 2 players, ₹20-₹5,000 entry
```

#### User Flow:
```
1. User selects game type
2. Chooses entry amount (₹10 to ₹10,000)
3. Creates or joins game session
4. Waits for opponent(s)
5. Game starts when all players ready
6. Real-time gameplay via WebSocket
7. Game completes
8. Winner gets prize (entry × players × 0.9)
9. Platform fee: 10%
```

---

### 🔟 **FRIENDS SYSTEM** (Phase 6)

#### Features:
- ✅ Send Friend Requests
- ✅ Accept/Reject Requests
- ✅ Friend List with Online Status
- ✅ Remove Friends
- ✅ Invite Friends to Games
- ✅ Friend Search

#### API Endpoints (8):
```
POST   /api/v1/friends/send-request             - Send friend request
POST   /api/v1/friends/accept-request/{id}      - Accept request
POST   /api/v1/friends/reject-request/{id}      - Reject request
DELETE /api/v1/friends/{id}                     - Remove friend
GET    /api/v1/friends/list                     - List friends
GET    /api/v1/friends/requests                 - Pending requests
POST   /api/v1/friends/invite-to-game           - Invite to game
GET    /api/v1/users/search                     - Search users
```

#### User Flow:
```
1. User searches for friends by username
2. Sends friend request
3. Friend receives notification
4. Friend accepts/rejects
5. Both can now:
   - Chat with each other
   - Invite to games
   - See online status
   - View each other's stats
```

---

### 1️⃣1️⃣ **CHAT & MESSAGING** (Phase 7)

#### Features:
- ✅ Direct Messages (1-on-1)
- ✅ Real-time Chat
- ✅ Read Receipts
- ✅ Typing Indicators
- ✅ Message Editing
- ✅ Message Deletion
- ✅ Message Search
- ✅ Unread Count

#### API Endpoints (10):
```
POST   /api/v1/chat/conversations/create        - Create conversation
GET    /api/v1/chat/conversations               - List conversations
GET    /api/v1/chat/conversations/{id}/messages - Get messages
POST   /api/v1/chat/conversations/{id}/messages - Send message
POST   /api/v1/chat/conversations/{id}/mark-read - Mark as read
PUT    /api/v1/chat/messages/{id}               - Edit message
DELETE /api/v1/chat/messages/{id}               - Delete message
POST   /api/v1/chat/conversations/{id}/typing   - Set typing indicator
GET    /api/v1/chat/search                      - Search messages
GET    /api/v1/chat/unread-count                - Unread message count
```

#### User Flow:
```
1. User opens chat with friend
2. Types message
3. Friend sees typing indicator
4. Message sent and delivered
5. Friend sees unread badge
6. Friend opens chat
7. Message marked as read
8. Read receipts shown (✓✓)
9. User can edit/delete messages
10. Search through chat history
```

---

### 1️⃣2️⃣ **TOURNAMENT SYSTEM** (Phase 6)

#### Features:
- ✅ Tournament Creation
- ✅ Registration with Entry Fee
- ✅ Automatic Bracket Generation
- ✅ Single/Double Elimination
- ✅ Match Scheduling
- ✅ Prize Pool Distribution
- ✅ Live Tournament Status

#### API Endpoints (10):
```
POST   /api/v1/tournaments/create               - Create tournament
GET    /api/v1/tournaments/upcoming             - Upcoming tournaments
GET    /api/v1/tournaments/live                 - Live tournaments
GET    /api/v1/tournaments/{id}                 - Tournament details
POST   /api/v1/tournaments/{id}/register        - Register
GET    /api/v1/tournaments/{id}/bracket         - View bracket
POST   /api/v1/tournaments/{id}/generate-bracket - Generate bracket (admin)
POST   /api/v1/tournaments/matches/{id}/result  - Submit result
GET    /api/v1/tournaments/{id}/participants    - List participants
GET    /api/v1/tournaments/{id}/leaderboard     - Tournament standings
```

#### Prize Distribution:
```
1st Place: 50% of prize pool
2nd Place: 30% of prize pool
3rd Place: 20% of prize pool

Example: ₹1,000 entry × 16 players = ₹16,000
1st: ₹8,000
2nd: ₹4,800
3rd: ₹3,200
```

#### User Flow:
```
1. View upcoming tournaments
2. Check details (game, entry fee, prize pool)
3. Register for tournament (₹50-₹5,000 entry)
4. Entry fee deducted from cash wallet
5. Wait for tournament to start
6. Bracket generated when full
7. Play matches according to schedule
8. Winner advances, loser eliminated
9. Finals match
10. Winners get prizes automatically
11. Winnings credited to wallet
```

---

### 1️⃣3️⃣ **TOKEN SYSTEM (Practice Games)** (Phase 6)

#### Features:
- ✅ Token Wallet (Separate from cash)
- ✅ Daily Login Bonuses
- ✅ Ad Rewards (Watch ads for tokens)
- ✅ Achievement Rewards
- ✅ Token Packages (Purchase)
- ✅ Practice Games (No real money)

#### API Endpoints (8):
```
GET    /api/v1/tokens/wallet                    - Get token balance
POST   /api/v1/tokens/daily-bonus/claim         - Claim daily bonus
GET    /api/v1/tokens/daily-bonus/status        - Bonus status
POST   /api/v1/tokens/watch-ad                  - Earn from ad
POST   /api/v1/tokens/spend                     - Spend tokens
GET    /api/v1/tokens/transactions              - Transaction history
GET    /api/v1/tokens/packages                  - Token packages
POST   /api/v1/tokens/purchase-package          - Buy tokens
```

#### Token Economics:
```
EARNING:
- Welcome bonus: 100 tokens
- Daily login: 100 tokens + streak bonus
- Watch ad: 50 tokens (5 ads/day max)
- Achievements: 10-500 tokens
- Win practice game: 20 tokens

SPENDING:
- Practice Ludo: 50 tokens
- Practice Rummy: 75 tokens
- Practice Quiz: 25 tokens
```

#### User Flow:
```
1. User gets 100 welcome tokens
2. Plays practice games for free
3. Runs out of tokens
4. Claims daily bonus (+100 tokens)
5. Watches 5 ads (+250 tokens)
6. Unlocks achievements (+tokens)
7. Or purchases token package
8. Continues playing practice games
```

---

### 1️⃣4️⃣ **LIVE STREAMING** (Phase 7 - NEW)

#### Features:
- ✅ Create Live Streams
- ✅ RTMP Streaming (OBS compatible)
- ✅ HLS Playback for Viewers
- ✅ Live Chat
- ✅ Viewer Count (Real-time)
- ✅ Donations/Tips
- ✅ Monetized Streams (Entry fee)
- ✅ Stream Recording

#### API Endpoints (12):
```
POST   /api/v1/streams/create                   - Create stream
POST   /api/v1/streams/{id}/start               - Start streaming
POST   /api/v1/streams/{id}/end                 - End stream
GET    /api/v1/streams/live                     - Browse live streams
GET    /api/v1/streams/upcoming                 - Scheduled streams
GET    /api/v1/streams/{id}                     - Stream details

POST   /api/v1/streams/{id}/join                - Join as viewer
POST   /api/v1/streams/{id}/leave               - Leave stream
POST   /api/v1/streams/{id}/like                - Like stream

POST   /api/v1/streams/{id}/chat                - Send chat message
GET    /api/v1/streams/{id}/chat                - Get chat history
POST   /api/v1/streams/{id}/donate              - Send donation
```

#### Revenue Model:
```
FREE STREAMS:
- Open to all viewers
- Earn from donations only

MONETIZED STREAMS:
- Entry fee: ₹10-₹500
- 80% to streamer
- 20% platform fee

DONATIONS:
- Viewers can tip streamer
- Minimum: ₹10
- 80% to streamer, 20% to platform
```

#### User Flow:
```
STREAMER:
1. Create stream (title, game, free/paid)
2. Get RTMP URL and stream key
3. Configure OBS with stream key
4. Start broadcasting
5. Viewers join and chat
6. Receive donations
7. End stream
8. View statistics (viewers, revenue)
9. Earnings credited to wallet

VIEWER:
1. Browse live streams
2. Click to watch
3. If monetized: Pay entry fee
4. Watch stream (HLS player)
5. Chat with other viewers
6. Send donations to streamer
7. Like and share stream
```

---

### 1️⃣5️⃣ **PUSH NOTIFICATIONS** (Phase 7 - NEW)

#### Features:
- ✅ Cross-platform (iOS, Android, Web)
- ✅ Firebase Cloud Messaging (FCM)
- ✅ Category-based Notifications
- ✅ Granular Preferences
- ✅ Quiet Hours
- ✅ Notification History
- ✅ Scheduled Notifications

#### API Endpoints (10):
```
POST   /api/v1/notifications/devices/register   - Register device
POST   /api/v1/notifications/devices/unregister - Unregister device
GET    /api/v1/notifications/devices/list       - List devices

GET    /api/v1/notifications/preferences        - Get preferences
PUT    /api/v1/notifications/preferences        - Update preferences

GET    /api/v1/notifications/history            - Notification history
GET    /api/v1/notifications/unread-count       - Unread count
POST   /api/v1/notifications/{id}/mark-read     - Mark as read
POST   /api/v1/notifications/mark-all-read      - Mark all as read

POST   /api/v1/notifications/send-test          - Send test notification
```

#### Notification Categories:
```
SOCIAL:
- Friend request received
- Friend accepted request
- New message from friend
- Friend online

GAMING:
- Game invitation
- Tournament starting soon
- Match result
- Tournament bracket update

FINANCIAL:
- Deposit successful
- Withdrawal approved
- Withdrawal rejected
- Bonus credited

PROMOTIONAL:
- Daily bonus available
- New promo code
- Special offers
- Tournament announcements

SYSTEM:
- KYC verified
- KYC rejected
- Account security alert
- App update available
```

#### User Flow:
```
1. User installs app
2. App requests notification permission
3. User grants permission
4. Device token registered
5. User sets preferences:
   - Enable/disable categories
   - Set quiet hours (e.g., 10 PM - 8 AM)
   - Sound/vibration settings
6. Notifications sent based on actions
7. User receives notifications
8. Taps notification → redirected to relevant screen
9. Notification marked as read
10. View all notifications in history
```

---

## 🔄 COMPLETE USER JOURNEY FLOWS

### 🆕 NEW USER ONBOARDING FLOW

```
Step 1: Registration
├─ User opens app
├─ Enters phone number
├─ Receives OTP via SMS
├─ Verifies OTP
├─ Creates username
├─ Gets ₹50 welcome bonus + 100 tokens
└─ Onboarding complete

Step 2: Profile Setup
├─ Upload profile picture
├─ Set display name
├─ Optional: Add email
└─ Profile complete

Step 3: KYC (Required for withdrawals)
├─ Upload Aadhaar (front + back)
├─ Upload PAN card
├─ System extracts details via OCR
├─ User confirms details
├─ Admin verifies (24-48 hrs)
└─ KYC verified → Can withdraw

Step 4: Add Bank Account
├─ Enter bank details
├─ IFSC code validation
├─ Optional: Penny drop verification
└─ Bank account verified

Step 5: First Deposit
├─ Select amount (₹100+)
├─ Choose payment method
├─ Redirected to payment gateway
├─ Payment successful
├─ Cash wallet credited
└─ Ready to play!
```

---

### 🎮 GAME PLAYING FLOW

```
PRACTICE GAME (Free Tokens):
1. Select game (Ludo/Rummy/Quiz)
2. Choose "Practice Mode"
3. Select token amount (50-500 tokens)
4. Create or join session
5. Wait for opponent
6. Play game
7. Win = 2× tokens back
8. Lose = tokens deducted

CASH GAME (Real Money):
1. Select game
2. Choose "Cash Mode"
3. Select entry amount (₹10-₹10,000)
4. Create or join session
5. Entry fee deducted from cash wallet
6. Wait for opponent(s)
7. Play game
8. Winner gets prize pool × 0.9 (10% fee)
9. Winnings credited to winnings wallet
10. Can withdraw or play more
```

---

### 🏆 TOURNAMENT PARTICIPATION FLOW

```
BEFORE TOURNAMENT:
1. Browse upcoming tournaments
2. View details:
   - Game type
   - Entry fee
   - Start time
   - Prize pool
   - Total slots
   - Registered players
3. Click "Register"
4. Entry fee deducted from cash wallet
5. Confirmation received

DURING TOURNAMENT:
1. Tournament starts (all slots filled)
2. Bracket generated automatically
3. User sees their match schedule
4. Round 1: Play first match
5. Win → Advance to Round 2
6. Lose → Eliminated (or losers bracket if double elimination)
7. Continue until finals
8. Finals match determines winner

AFTER TOURNAMENT:
1. Results announced
2. Prizes distributed:
   - 1st place: 50% of pool
   - 2nd place: 30% of pool
   - 3rd place: 20% of pool
3. Winnings credited to wallet
4. Tournament stats updated
5. Leaderboard updated
```

---

### 💬 SOCIAL INTERACTION FLOW

```
MAKING FRIENDS:
1. Search user by username
2. Send friend request
3. Friend receives notification
4. Friend accepts/rejects
5. If accepted:
   - Can now chat
   - Can invite to games
   - See online status
   - View each other's stats

CHATTING:
1. Open chat with friend
2. Type message
3. Friend sees typing indicator
4. Send message
5. Message delivered (✓)
6. Friend reads message (✓✓)
7. Continue conversation
8. Can edit/delete messages
9. Search chat history

INVITING TO GAME:
1. User creates game session
2. Clicks "Invite Friend"
3. Selects friend from list
4. Friend receives notification
5. Friend accepts invitation
6. Friend joins game
7. Game starts when ready
```

---

### 📺 LIVE STREAMING FLOW

```
AS STREAMER:
1. Create stream
   - Enter title
   - Select game
   - Set free or paid (entry fee)
   - Schedule or go live now
2. Get streaming credentials
   - RTMP URL
   - Stream key
3. Configure OBS:
   - Add RTMP server
   - Paste stream key
4. Start broadcasting
5. Viewers start joining
6. Chat with viewers
7. Receive donations
8. View live stats (viewer count)
9. End stream when done
10. View final statistics
11. Earnings credited to wallet

AS VIEWER:
1. Browse live streams
2. Select stream to watch
3. If paid: Pay entry fee
4. Watch stream (HLS player)
5. Send chat messages
6. Like stream
7. Send donation to streamer
8. Share stream with friends
9. Leave stream when done
```

---

### 🔔 NOTIFICATION FLOW

```
SETUP:
1. Install app
2. Grant notification permission
3. Device registered automatically
4. Set preferences:
   - Social notifications: ON
   - Gaming notifications: ON
   - Financial notifications: ON
   - Promotional: OFF (example)
   - Quiet hours: 10 PM - 8 AM

RECEIVING NOTIFICATIONS:
1. Action triggers notification
   Examples:
   - Friend sends request
   - Tournament starting
   - Deposit successful
   - Daily bonus available
2. System checks preferences
3. If enabled and not quiet hours:
4. Notification sent via FCM
5. User receives push notification
6. User taps notification
7. App opens to relevant screen
8. Notification marked as read

MANAGING:
1. View all notifications
2. Filter by category
3. Mark as read/unread
4. Clear all
5. Update preferences anytime
```

---

### 💰 WITHDRAWAL FLOW

```
PREREQUISITES:
- KYC verified ✓
- Bank account added ✓
- Minimum ₹100 in winnings wallet

WITHDRAWAL PROCESS:
1. User opens wallet
2. Selects "Withdraw"
3. Enters amount (₹100 - ₹100,000)
4. Selects bank account
5. Confirms withdrawal
6. Request submitted
7. Status: Pending
8. Admin reviews (24-48 hrs)
9. Admin approves/rejects
10. If approved:
    - Amount transferred to bank
    - Status: Completed
    - User receives confirmation
11. If rejected:
    - Amount returned to wallet
    - Reason provided
    - User can resubmit
```

---

## 📊 API CONNECTIVITY & INTEGRATION

### BASE URL
```
Development: http://localhost:8000/api/v1
Production:  https://api.gamingplatform.com/api/v1
```

### AUTHENTICATION HEADER
All protected endpoints require JWT token:
```
Authorization: Bearer <access_token>
```

### API RESPONSE FORMAT

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

**Error Response:**
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

## 🔗 COMPLETE API ENDPOINT MAP

### Total Endpoints: **150+**

| Module | Endpoints | Status |
|--------|-----------|--------|
| Authentication | 15 | ✅ Active |
| KYC | 6 | ✅ Active |
| Wallet | 12 | ✅ Active |
| Bank Accounts | 6 | ✅ Active |
| Games | 12 | ✅ Active |
| Friends | 8 | ✅ Active |
| Chat | 10 | ✅ Active |
| Tournaments | 10 | ✅ Active |
| Tokens | 8 | ✅ Active |
| Referrals | 4 | ✅ Active |
| Achievements | 5 | ✅ Active |
| Leaderboards | 3 | ✅ Active |
| Daily Bonus | 2 | ✅ Active |
| Promo Codes | 5 | ✅ Active |
| Live Streaming | 12 | ✅ Active |
| Push Notifications | 10 | ✅ Active |
| Admin | 20+ | ✅ Active |
| WebSocket | 2 | ✅ Active |

---

## 🗄️ DATABASE SCHEMA

### Total Tables: **40+**

**Core Tables:**
- users
- user_levels
- device_tokens

**Authentication:**
- otps
- two_factor_settings
- backup_codes

**KYC & Banking:**
- kyc_documents
- bank_accounts

**Wallet & Transactions:**
- wallets
- wallet_transactions
- payment_orders

**Gaming:**
- games
- game_sessions
- game_session_players
- game_moves

**Social:**
- friendships
- friend_requests
- game_invitations
- conversations
- messages
- message_read_receipts
- typing_indicators

**Tournaments:**
- tournaments
- tournament_registrations
- tournament_matches

**Tokens:**
- token_wallets
- token_transactions
- token_packages

**Rewards:**
- referrals
- achievements
- user_achievements
- daily_bonuses
- promo_codes
- promo_code_usage
- leaderboards
- reward_transactions

**Live Streaming:**
- live_streams
- stream_viewers
- stream_chat
- stream_donations

**Notifications:**
- push_notifications
- notification_preferences
- notification_templates

---

## ✅ TESTING STATUS

### Unit Tests: ✅ Passed
- Models validation
- Service layer logic
- Utility functions

### Integration Tests: ✅ Passed
- API endpoints
- Database operations
- Authentication flow
- Payment integration

### E2E Tests: ✅ Passed
- Complete user journey
- Game playing flow
- Tournament participation
- Withdrawal process

### Load Tests: ⚙️ Configured
- Concurrent users: 1000+
- Requests/sec: 500+
- Response time: <200ms

---

## 🚀 DEPLOYMENT STATUS

### Infrastructure:
- ✅ Docker containerization
- ✅ PostgreSQL database
- ✅ MongoDB (game data)
- ✅ Redis (caching)
- ✅ Nginx (reverse proxy)
- ✅ CI/CD pipeline

### Monitoring:
- ✅ Prometheus metrics
- ✅ Sentry error tracking
- ✅ Application logs
- ✅ Database monitoring

---

## 📱 MOBILE APP INTEGRATION

### Flutter App Features:
- ✅ Phone authentication
- ✅ Profile management
- ✅ KYC submission
- ✅ Wallet management
- ✅ Game playing
- ✅ Chat messaging
- ✅ Friend management
- ✅ Tournament participation
- ✅ Live streaming
- ✅ Push notifications

### API Integration:
All Flutter screens connected to backend APIs via HTTP/WebSocket.

---

## 🎯 SUMMARY

**Total Features:** 50+
**Total APIs:** 150+
**Total Tables:** 40+
**User Flows:** 15 major flows
**Status:** ✅ Production Ready

**All systems operational and tested!** 🎉
