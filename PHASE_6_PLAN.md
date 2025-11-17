# Phase 6: Critical Features - Implementation Plan

## 📋 Overview

**Timeline**: 4-6 weeks
**Priority**: 🔥🔥🔥 HIGHEST
**Goal**: Add tournament system, practice mode with tokens, and friend features

---

## 🎯 Part 1: Tournament System (Week 1-2)

### **Backend Components**

#### 1. Database Models
- `Tournament` model
  - id, name, description
  - game_id, tournament_type (single_elimination, double_elimination, round_robin)
  - entry_fee, prize_pool
  - max_participants, current_participants
  - start_time, end_time
  - status (upcoming, registration, live, completed, cancelled)
  - bracket_data (JSON)
  
- `TournamentRegistration` model
  - id, tournament_id, user_id
  - registration_time, status
  - seed_number, payment_status
  
- `TournamentMatch` model
  - id, tournament_id
  - round_number, match_number
  - player1_id, player2_id
  - winner_id, score_data
  - status (pending, in_progress, completed)
  - scheduled_time

#### 2. API Endpoints
```
GET    /api/v1/tournaments                    # List all tournaments
GET    /api/v1/tournaments/{id}                # Tournament details
POST   /api/v1/tournaments                     # Create tournament (admin)
PUT    /api/v1/tournaments/{id}                # Update tournament (admin)
POST   /api/v1/tournaments/{id}/register       # Register for tournament
DELETE /api/v1/tournaments/{id}/register       # Unregister
GET    /api/v1/tournaments/{id}/bracket        # Get tournament bracket
GET    /api/v1/tournaments/{id}/participants   # List participants
GET    /api/v1/tournaments/{id}/matches        # List matches
POST   /api/v1/tournaments/{id}/matches/{mid}  # Submit match result
GET    /api/v1/tournaments/my                  # My tournaments
```

#### 3. Business Logic
- Tournament bracket generation (single/double elimination)
- Auto-match scheduling
- Winner advancement
- Prize distribution on completion
- Notification system for matches

### **Flutter Components**

#### 1. Screens
- `tournaments_screen.dart` - List all tournaments (tabs: upcoming, live, completed)
- `tournament_details_screen.dart` - Tournament info, prize pool, participants
- `tournament_bracket_screen.dart` - Visual bracket display
- `tournament_registration_dialog.dart` - Register confirmation
- `my_tournaments_screen.dart` - User's registered tournaments

#### 2. Widgets
- `tournament_card.dart` - Tournament list card
- `bracket_widget.dart` - Bracket visualization
- `tournament_status_badge.dart` - Status indicator
- `prize_pool_widget.dart` - Prize distribution display

#### 3. BLoC
- `TournamentBloc` with events:
  - LoadTournamentsEvent
  - LoadTournamentDetailsEvent
  - RegisterForTournamentEvent
  - UnregisterFromTournamentEvent
  - LoadMyTournamentsEvent
  - LoadBracketEvent

---

## 🎮 Part 2: Practice Mode & Token System (Week 3-4)

### **Backend Components**

#### 1. Database Models
- `TokenWallet` model
  - id, user_id
  - balance (tokens)
  - total_earned, total_spent
  
- `TokenTransaction` model
  - id, user_id
  - amount, transaction_type (earn, spend)
  - source (daily_login, ad_watch, achievement, purchase, practice_game)
  - description, metadata
  
- Update `GameSession` model
  - Add `session_mode` (cash, practice)
  - Add `token_entry_fee`

#### 2. API Endpoints
```
GET    /api/v1/tokens/balance                 # Get token balance
GET    /api/v1/tokens/transactions             # Token transaction history
POST   /api/v1/tokens/earn                     # Earn tokens (daily, ads)
POST   /api/v1/games/sessions/create-practice # Create practice session
GET    /api/v1/games/{code}/practice-sessions # List practice sessions
POST   /api/v1/tokens/shop                     # Token shop (buy with cash)
```

#### 3. Business Logic
- Daily token rewards (100 tokens/day)
- Ad watch rewards (50 tokens/ad, max 5/day)
- Achievement completion rewards
- Practice game creation (token-based)
- Token purchase packages

### **Flutter Components**

#### 1. Screens
- `token_wallet_screen.dart` - Token balance, earn options, shop
- `practice_mode_screen.dart` - Practice games list
- `token_shop_screen.dart` - Buy token packages
- `earn_tokens_screen.dart` - Ways to earn (daily, ads, achievements)

#### 2. Widgets
- `token_balance_card.dart` - Display token balance
- `token_transaction_card.dart` - Transaction item
- `earn_token_card.dart` - Earn option card
- `practice_game_card.dart` - Practice session card
- `game_mode_selector.dart` - Cash vs Practice toggle

#### 3. Updates
- Add token display to `home_screen.dart`
- Add practice mode toggle to `game_details_screen.dart`
- Update `WalletBloc` to handle tokens

---

## 👥 Part 3: Friends System (Week 5-6)

### **Backend Components**

#### 1. Database Models
- `Friendship` model
  - id, user_id, friend_id
  - status (pending, accepted, blocked)
  - created_at, accepted_at
  
- `FriendRequest` model
  - id, sender_id, receiver_id
  - status (pending, accepted, rejected)
  - message, created_at

#### 2. API Endpoints
```
GET    /api/v1/friends                         # Get friends list
POST   /api/v1/friends/request                 # Send friend request
GET    /api/v1/friends/requests                # Get friend requests
POST   /api/v1/friends/requests/{id}/accept    # Accept request
POST   /api/v1/friends/requests/{id}/reject    # Reject request
DELETE /api/v1/friends/{id}                    # Remove friend
POST   /api/v1/friends/{id}/block              # Block user
GET    /api/v1/friends/search                  # Search users
POST   /api/v1/friends/{id}/invite-game        # Invite to game
GET    /api/v1/friends/{id}/stats              # Friend stats
GET    /api/v1/friends/leaderboard             # Friends leaderboard
```

#### 3. Business Logic
- Friend request notifications
- Online/offline status tracking
- Friend activity feed
- Private game invitations
- Friend vs Friend matches

### **Flutter Components**

#### 1. Screens
- `friends_screen.dart` - Friends list with tabs (all, online, requests)
- `add_friend_screen.dart` - Search and add friends
- `friend_profile_screen.dart` - Friend's profile and stats
- `friend_requests_screen.dart` - Pending requests
- `friend_leaderboard_screen.dart` - Friends ranking

#### 2. Widgets
- `friend_card.dart` - Friend list item with online status
- `friend_request_card.dart` - Friend request item
- `friend_invite_dialog.dart` - Invite friend to game
- `online_status_indicator.dart` - Online/offline dot

#### 3. BLoC
- `FriendBloc` with events:
  - LoadFriendsEvent
  - SendFriendRequestEvent
  - AcceptFriendRequestEvent
  - RejectFriendRequestEvent
  - RemoveFriendEvent
  - SearchUsersEvent
  - InviteFriendToGameEvent

---

## 📊 Database Schema Summary

### New Tables

```sql
-- Tournaments
CREATE TABLE tournaments (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    game_id UUID REFERENCES games(id),
    tournament_type VARCHAR(50),
    entry_fee INTEGER,
    prize_pool INTEGER,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    registration_start TIMESTAMP,
    registration_end TIMESTAMP,
    status VARCHAR(50),
    bracket_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tournament_registrations (
    id UUID PRIMARY KEY,
    tournament_id UUID REFERENCES tournaments(id),
    user_id UUID REFERENCES users(id),
    registration_time TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50),
    seed_number INTEGER,
    payment_status VARCHAR(50),
    UNIQUE(tournament_id, user_id)
);

CREATE TABLE tournament_matches (
    id UUID PRIMARY KEY,
    tournament_id UUID REFERENCES tournaments(id),
    round_number INTEGER,
    match_number INTEGER,
    player1_id UUID REFERENCES users(id),
    player2_id UUID,
    winner_id UUID,
    score_data JSONB,
    status VARCHAR(50),
    scheduled_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tokens
CREATE TABLE token_wallets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE token_transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    amount INTEGER,
    transaction_type VARCHAR(50),
    source VARCHAR(100),
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Friends
CREATE TABLE friendships (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    friend_id UUID REFERENCES users(id),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    UNIQUE(user_id, friend_id)
);

CREATE TABLE friend_requests (
    id UUID PRIMARY KEY,
    sender_id UUID REFERENCES users(id),
    receiver_id UUID REFERENCES users(id),
    status VARCHAR(50),
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sender_id, receiver_id)
);

-- Indexes
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_game ON tournaments(game_id);
CREATE INDEX idx_tournament_registrations_user ON tournament_registrations(user_id);
CREATE INDEX idx_friendships_user ON friendships(user_id);
CREATE INDEX idx_friend_requests_receiver ON friend_requests(receiver_id);
```

---

## 🎨 UI/UX Design Notes

### Tournament Screens
- **List View**: Card-based with countdown timer, prize pool, participants
- **Details**: Full info with tabs (Overview, Bracket, Participants, Rules)
- **Bracket**: Tree view with lines connecting matches
- **Registration**: Modal with entry fee confirmation

### Token Wallet
- **Balance Card**: Large token count with icon
- **Earn Section**: Cards for daily login, watch ads, achievements
- **Shop**: Token packages (100, 500, 1000, 5000)
- **History**: Transaction list with source icons

### Friends
- **List**: Avatar, username, online status dot, quick actions
- **Search**: Search bar with username/phone lookup
- **Requests**: Pending requests with accept/reject buttons
- **Profile**: Friend stats, recent games, invite button

---

## 🔧 Technical Considerations

### Real-time Features
- WebSocket for:
  - Tournament match updates
  - Friend online status
  - Friend game invitations

### Notifications
- Push notifications for:
  - Tournament starting soon
  - Your match is ready
  - Friend request received
  - Friend is online
  - Friend invited you to game

### Caching Strategy
- Cache tournaments list (5 min)
- Cache friends list (until update)
- Cache token balance (real-time)

### Performance
- Paginate tournament participants (50/page)
- Paginate friends list (100/page)
- Lazy load bracket (load round by round)

---

## 📝 Implementation Order

### Week 1: Tournament Backend
1. Create database models
2. Write migration scripts
3. Implement API endpoints
4. Add tournament services
5. Test bracket generation

### Week 2: Tournament Frontend
1. Create tournament screens
2. Build bracket widget
3. Implement tournament BLoC
4. Add registration flow
5. Test end-to-end

### Week 3: Token System Backend
1. Create token models
2. Implement token APIs
3. Add daily reward system
4. Create practice game logic
5. Add token shop

### Week 4: Token System Frontend
1. Create token wallet screen
2. Add practice mode UI
3. Update game screens
4. Implement token earning
5. Test practice games

### Week 5: Friends Backend
1. Create friendship models
2. Implement friend APIs
3. Add request system
4. Create invitation logic
5. Add online status tracking

### Week 6: Friends Frontend
1. Create friends screens
2. Build friend search
3. Implement friend BLoC
4. Add game invitation
5. Test all features

---

## ✅ Success Criteria

### Tournament System
- [ ] Users can view all tournaments
- [ ] Users can register for tournaments
- [ ] Bracket is generated automatically
- [ ] Matches are tracked correctly
- [ ] Winners receive prizes

### Token System
- [ ] Users have token wallet
- [ ] Daily login rewards work
- [ ] Practice games use tokens
- [ ] Token shop functional
- [ ] Transaction history accurate

### Friends System
- [ ] Users can search and add friends
- [ ] Friend requests work both ways
- [ ] Friends list shows online status
- [ ] Users can invite friends to games
- [ ] Friend leaderboard displays correctly

---

## 🚀 Ready to Start!

**First Task**: Create backend database models for tournaments, tokens, and friends.

Let's begin! 🎯
