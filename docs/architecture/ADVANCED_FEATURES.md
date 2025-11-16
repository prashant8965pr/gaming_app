# Advanced Features & Modules

## Overview

This document details **advanced, world-class features** that will differentiate our platform from competitors and create a premium gaming experience.

---

## Module K: Social & Community Features

### K.1 Friends & Social Network
**Location**: `backend/services/social_service/friends/`

#### Features:
- **Friend System**
  - Send friend request
  - Accept/reject friend request
  - Remove friend
  - Block/unblock user
  - Friend suggestions (mutual friends, played together)
  - Friend online status (real-time)

- **Friend Lists**
  - All friends
  - Online friends
  - Recently played with
  - Favorite friends (pin)
  - Blocked users

- **Friend Activities**
  - Live feed of friend activities
  - "John just won ₹500 in Ludo!"
  - "Sarah joined a tournament"
  - Achievement notifications

#### Database Tables:
```sql
CREATE TABLE friend_requests (
    id UUID PRIMARY KEY,
    sender_user_id UUID REFERENCES users(id),
    receiver_user_id UUID REFERENCES users(id),
    status VARCHAR(20), -- pending, accepted, rejected, cancelled
    created_at TIMESTAMP,
    responded_at TIMESTAMP,
    UNIQUE(sender_user_id, receiver_user_id)
);

CREATE TABLE friendships (
    id UUID PRIMARY KEY,
    user_id_1 UUID REFERENCES users(id),
    user_id_2 UUID REFERENCES users(id),
    created_at TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id_1, user_id_2)
);

CREATE TABLE blocked_users (
    id UUID PRIMARY KEY,
    blocker_user_id UUID REFERENCES users(id),
    blocked_user_id UUID REFERENCES users(id),
    reason TEXT,
    created_at TIMESTAMP
);

CREATE TABLE friend_activities (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR(50),
    activity_data JSONB,
    created_at TIMESTAMP,
    INDEX idx_user_created (user_id, created_at DESC)
);
```

#### APIs:
- `POST /social/friends/request` - Send friend request
- `POST /social/friends/accept/{request_id}` - Accept request
- `POST /social/friends/reject/{request_id}` - Reject request
- `DELETE /social/friends/{user_id}` - Remove friend
- `POST /social/friends/block/{user_id}` - Block user
- `GET /social/friends` - Get friends list
- `GET /social/friends/online` - Get online friends
- `GET /social/friends/suggestions` - Friend suggestions
- `GET /social/friends/activities` - Friend activity feed

---

### K.2 In-Game Chat System
**Location**: `backend/services/social_service/chat/`

#### Features:
- **Private Chat**
  - 1-on-1 messaging
  - Text, emojis, GIFs
  - Image sharing
  - Message history (30 days)
  - Read receipts
  - Typing indicators
  - End-to-end encryption

- **Group Chat**
  - Create group (up to 50 members)
  - Group admin controls
  - Add/remove members
  - Group name and icon
  - Mute notifications

- **Match Chat**
  - In-game chat during matches
  - Quick chat messages
  - Report toxic behavior
  - Auto-moderation (profanity filter)

- **Global Chat**
  - Public chat rooms by game
  - Moderated by admins
  - Auto-ban for spam/abuse

#### Database (MongoDB):
```javascript
// Collection: chat_messages
{
    _id: ObjectId,
    conversation_id: "uuid",
    sender_id: "uuid",
    message_type: "text", // text, image, gif, emoji
    content: "Hello!",
    attachments: [],
    is_read: false,
    read_at: null,
    created_at: ISODate,
    encrypted: true
}

// Collection: conversations
{
    _id: ObjectId,
    conversation_id: "uuid",
    type: "private", // private, group, match
    participants: ["uuid1", "uuid2"],
    group_name: null,
    group_icon: null,
    created_by: "uuid",
    created_at: ISODate,
    last_message: {...},
    last_activity: ISODate
}
```

#### APIs:
- `POST /chat/conversations` - Create conversation
- `GET /chat/conversations` - Get all conversations
- `POST /chat/messages` - Send message
- `GET /chat/messages/{conversation_id}` - Get message history
- `PUT /chat/messages/{message_id}/read` - Mark as read
- `DELETE /chat/messages/{message_id}` - Delete message
- `POST /chat/report` - Report message/user

---

### K.3 Clans/Guilds System
**Location**: `backend/services/social_service/clans/`

#### Features:
- **Clan Creation**
  - Create clan (₹500 fee)
  - Clan name (unique)
  - Clan tag (3-5 chars, unique)
  - Clan icon/banner
  - Clan description
  - Membership limit (50-200 members based on level)

- **Clan Roles**
  - Leader (1)
  - Co-Leader (up to 5)
  - Elder (unlimited)
  - Member (default)
  - Each role has permissions

- **Clan Features**
  - Clan treasury (shared wallet)
  - Clan chat
  - Clan events
  - Clan tournaments
  - Clan leaderboard (clan vs clan)
  - Clan wars
  - Recruitment system
  - Clan shop (exclusive items)

- **Clan Progression**
  - Clan XP (from member activities)
  - Clan level (1-50)
  - Unlock perks at each level
  - Clan trophies/achievements

#### Database Tables:
```sql
CREATE TABLE clans (
    id UUID PRIMARY KEY,
    clan_name VARCHAR(50) UNIQUE NOT NULL,
    clan_tag VARCHAR(5) UNIQUE NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    banner_url VARCHAR(500),
    leader_user_id UUID REFERENCES users(id),
    member_count INT DEFAULT 1,
    max_members INT DEFAULT 50,
    clan_level INT DEFAULT 1,
    clan_xp INT DEFAULT 0,
    total_trophies INT DEFAULT 0,
    treasury_balance DECIMAL(10,2) DEFAULT 0,
    is_recruiting BOOLEAN DEFAULT TRUE,
    join_type VARCHAR(20) DEFAULT 'open', -- open, invite_only, closed
    created_at TIMESTAMP,
    INDEX idx_clan_name (clan_name),
    INDEX idx_clan_tag (clan_tag)
);

CREATE TABLE clan_members (
    id UUID PRIMARY KEY,
    clan_id UUID REFERENCES clans(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member', -- leader, co_leader, elder, member
    joined_at TIMESTAMP,
    contribution_xp INT DEFAULT 0,
    last_active_at TIMESTAMP,
    UNIQUE(clan_id, user_id)
);

CREATE TABLE clan_wars (
    id UUID PRIMARY KEY,
    clan_1_id UUID REFERENCES clans(id),
    clan_2_id UUID REFERENCES clans(id),
    status VARCHAR(20), -- scheduled, in_progress, completed
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    clan_1_score INT DEFAULT 0,
    clan_2_score INT DEFAULT 0,
    winner_clan_id UUID REFERENCES clans(id),
    prize_pool DECIMAL(10,2),
    created_at TIMESTAMP
);

CREATE TABLE clan_events (
    id UUID PRIMARY KEY,
    clan_id UUID REFERENCES clans(id),
    event_type VARCHAR(50),
    event_name VARCHAR(200),
    event_data JSONB,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP
);
```

#### APIs:
- `POST /clans/create` - Create clan
- `GET /clans/search` - Search clans
- `GET /clans/{clan_id}` - Get clan details
- `POST /clans/{clan_id}/join` - Join clan
- `POST /clans/{clan_id}/leave` - Leave clan
- `POST /clans/{clan_id}/invite` - Invite player
- `PUT /clans/{clan_id}/members/{user_id}/role` - Update member role
- `DELETE /clans/{clan_id}/members/{user_id}` - Kick member
- `GET /clans/{clan_id}/wars` - Get clan wars
- `POST /clans/{clan_id}/wars/challenge` - Challenge another clan
- `GET /clans/leaderboard` - Global clan leaderboard

---

### K.4 Voice Chat System
**Location**: `backend/services/social_service/voice/`

#### Features:
- **In-Match Voice Chat**
  - Real-time voice during multiplayer matches
  - Push-to-talk or always-on
  - Individual volume control
  - Mute players
  - Voice quality settings (low/medium/high)

- **Clan Voice Channels**
  - Permanent voice rooms
  - Multiple channels per clan
  - Voice channel permissions

- **Party Voice Chat**
  - Create temporary party
  - Voice chat with friends
  - Party leader controls

#### Technology:
- **Agora.io** or **Twilio Programmable Voice**
- WebRTC for direct peer-to-peer
- Server for signaling

#### Database Tables:
```sql
CREATE TABLE voice_channels (
    id UUID PRIMARY KEY,
    channel_type VARCHAR(20), -- match, clan, party
    channel_name VARCHAR(100),
    clan_id UUID REFERENCES clans(id),
    max_participants INT DEFAULT 10,
    created_at TIMESTAMP
);

CREATE TABLE voice_sessions (
    id UUID PRIMARY KEY,
    channel_id UUID REFERENCES voice_channels(id),
    user_id UUID REFERENCES users(id),
    is_muted BOOLEAN DEFAULT FALSE,
    is_deafened BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP,
    left_at TIMESTAMP
);
```

#### APIs:
- `POST /voice/channels/create` - Create voice channel
- `POST /voice/channels/{channel_id}/join` - Join channel
- `POST /voice/channels/{channel_id}/leave` - Leave channel
- `PUT /voice/settings` - Update voice settings
- `GET /voice/token` - Get Agora token for WebRTC

---

## Module L: Content Creator & Streaming Features

### L.1 Live Streaming Integration
**Location**: `backend/services/streaming_service/`

#### Features:
- **Stream Your Gameplay**
  - One-click streaming to platform
  - Stream to YouTube/Twitch/Facebook simultaneously
  - Built-in overlay (stats, chat)
  - Stream quality settings
  - Mobile and web streaming

- **Watch Streams**
  - Browse live streams
  - Follow favorite streamers
  - Stream chat
  - Gifts/donations to streamers
  - Picture-in-picture mode

- **Streamer Features**
  - Streamer dashboard
  - Analytics (viewers, watch time, earnings)
  - Subscriber system
  - Subscriber-only chat
  - Emote system
  - Channel points/rewards

- **Monetization**
  - Ad revenue sharing (70/30 split)
  - Subscriptions (₹99/₹199/₹499 per month)
  - Donations/gifts
  - Sponsored streams
  - Affiliate links

#### Technology Stack:
- **RTMP Server**: OBS Studio compatible
- **HLS/DASH**: For playback
- **CDN**: CloudFlare Stream or AWS CloudFront
- **Video Processing**: FFmpeg

#### Database Tables:
```sql
CREATE TABLE streamers (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES users(id),
    channel_name VARCHAR(100) UNIQUE,
    channel_description TEXT,
    stream_key VARCHAR(100) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    subscriber_count INT DEFAULT 0,
    total_views INT DEFAULT 0,
    created_at TIMESTAMP
);

CREATE TABLE live_streams (
    id UUID PRIMARY KEY,
    streamer_id UUID REFERENCES streamers(id),
    title VARCHAR(200),
    game_code VARCHAR(50),
    thumbnail_url VARCHAR(500),
    stream_url VARCHAR(500),
    viewer_count INT DEFAULT 0,
    status VARCHAR(20), -- live, ended
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    total_views INT DEFAULT 0,
    peak_viewers INT DEFAULT 0
);

CREATE TABLE stream_subscriptions (
    id UUID PRIMARY KEY,
    streamer_id UUID REFERENCES streamers(id),
    subscriber_user_id UUID REFERENCES users(id),
    tier INT, -- 1, 2, 3
    amount DECIMAL(10,2),
    auto_renew BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(streamer_id, subscriber_user_id)
);

CREATE TABLE stream_donations (
    id UUID PRIMARY KEY,
    streamer_id UUID REFERENCES streamers(id),
    donor_user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2),
    message TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

#### APIs:
- `POST /streaming/channel/create` - Become a streamer
- `POST /streaming/live/start` - Start stream
- `POST /streaming/live/stop` - Stop stream
- `GET /streaming/live` - Get live streams
- `GET /streaming/{streamer_id}` - Get streamer profile
- `POST /streaming/{streamer_id}/subscribe` - Subscribe to streamer
- `POST /streaming/{streamer_id}/donate` - Send donation
- `GET /streaming/analytics` - Streamer analytics

---

### L.2 Replay & Highlights System
**Location**: `backend/services/content_service/replays/`

#### Features:
- **Automatic Replay Recording**
  - Every match auto-recorded
  - Stored for 30 days (free) / forever (premium)
  - Download replay file
  - Share replay link

- **Highlight Clips**
  - AI detects highlight moments
  - Manual clip creation
  - Clip editor (trim, speed up/slow down)
  - Add text overlays
  - Background music

- **Replay Viewer**
  - Watch from any player's perspective
  - Slow motion / fast forward
  - Frame-by-frame analysis
  - Free camera mode
  - Show/hide UI

- **Sharing**
  - Share to social media
  - Embed on website
  - Share in chat
  - Trending replays section

#### Database (MongoDB):
```javascript
// Collection: replays
{
    _id: ObjectId,
    match_id: "uuid",
    game_code: "ludo",
    players: [...],
    duration_seconds: 420,
    file_url: "s3://replays/...",
    file_size_mb: 15.5,
    thumbnail_url: "...",
    view_count: 0,
    like_count: 0,
    created_at: ISODate,
    expires_at: ISODate // null for premium users
}

// Collection: highlight_clips
{
    _id: ObjectId,
    replay_id: "ObjectId",
    creator_user_id: "uuid",
    clip_name: "Epic Comeback!",
    start_time_seconds: 180,
    end_time_seconds: 195,
    clip_url: "s3://clips/...",
    thumbnail_url: "...",
    view_count: 0,
    like_count: 0,
    share_count: 0,
    is_public: true,
    tags: ["comeback", "epic"],
    created_at: ISODate
}
```

#### APIs:
- `GET /replays/{match_id}` - Get replay
- `GET /replays/my-replays` - Get user's replays
- `POST /replays/{replay_id}/clip` - Create clip
- `GET /clips/trending` - Trending clips
- `POST /clips/{clip_id}/like` - Like clip
- `POST /clips/{clip_id}/share` - Share clip

---

## Module M: Advanced AI & Personalization

### M.1 AI Game Recommendations
**Location**: `backend/services/ai_service/recommendations/`

#### Features:
- **Personalized Game Suggestions**
  - Based on play history
  - Win rate analysis
  - Skill level matching
  - Time-of-day preferences
  - Friend activity

- **Smart Entry Fee Suggestions**
  - Optimal entry fee based on bankroll
  - Risk analysis
  - Expected ROI predictions

- **Tournament Recommendations**
  - Match schedule with user availability
  - Skill-appropriate tournaments
  - Prize pool optimization

#### ML Models:
- Collaborative filtering (similar users)
- Content-based filtering (game features)
- Hybrid recommendation system
- A/B testing framework

---

### M.2 Dynamic Difficulty Adjustment
**Location**: `backend/services/ai_service/difficulty/`

#### Features:
- **Adaptive Bot Difficulty**
  - AI analyzes player skill
  - Adjusts bot behavior in real-time
  - Keeps matches challenging but fair
  - Gradually increases difficulty

- **Personalized Challenges**
  - Custom daily challenges based on skill
  - Achievement difficulty scaling
  - Progressive learning curve

---

### M.3 Advanced Fraud Detection AI
**Location**: `backend/services/fraud_service/ml/`

#### Features:
- **Deep Learning Models**
  - LSTM for sequence pattern detection
  - Anomaly detection algorithms
  - Behavioral biometrics
  - Device fingerprinting

- **Real-Time Scoring**
  - Fraud probability score (0-100)
  - Risk categories
  - Automated actions based on score

- **Pattern Recognition**
  - Collusion networks
  - Multi-account rings
  - Bot farming detection
  - Chip dumping detection

#### ML Tech Stack:
```python
# requirements.txt
tensorflow==2.15.0
scikit-learn==1.3.2
xgboost==2.0.3
imbalanced-learn==0.11.0
```

---

### M.4 Intelligent Customer Support
**Location**: `backend/services/support_service/ai/`

#### Features:
- **AI Chatbot**
  - Natural language processing
  - Answer common questions
  - Escalate to human agent
  - Multi-language support

- **Smart Ticket Routing**
  - Categorize support tickets
  - Route to appropriate team
  - Priority assignment
  - SLA monitoring

- **Sentiment Analysis**
  - Analyze user sentiment
  - Flag angry/frustrated users
  - Proactive outreach

---

## Module N: Competitive & Esports Features

### N.1 Esports Tournament System
**Location**: `backend/services/esports_service/`

#### Features:
- **Professional Tournaments**
  - Bracket system (Single/Double elimination)
  - Swiss format
  - Round-robin
  - Seeding based on rank
  - Live brackets visualization
  - Match scheduling
  - Admin controls (reschedule, DQ, etc.)

- **Prize Pools**
  - Crowdfunding tournaments
  - Sponsored tournaments
  - Community contributions
  - Prize pool tracker

- **Tournament Broadcasting**
  - Official broadcast stream
  - Commentator mode
  - Spectator slots
  - Replay analysis

#### Database Tables:
```sql
CREATE TABLE esports_tournaments (
    id UUID PRIMARY KEY,
    tournament_name VARCHAR(200),
    game_code VARCHAR(50),
    format VARCHAR(50), -- single_elim, double_elim, swiss, round_robin
    tier VARCHAR(20), -- amateur, semi_pro, professional
    entry_fee DECIMAL(10,2),
    prize_pool DECIMAL(10,2),
    max_teams INT,
    registration_start TIMESTAMP,
    registration_end TIMESTAMP,
    tournament_start TIMESTAMP,
    tournament_end TIMESTAMP,
    status VARCHAR(20),
    sponsor_info JSONB,
    created_at TIMESTAMP
);

CREATE TABLE esports_teams (
    id UUID PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE,
    team_tag VARCHAR(5) UNIQUE,
    captain_user_id UUID REFERENCES users(id),
    team_logo_url VARCHAR(500),
    total_earnings DECIMAL(10,2) DEFAULT 0,
    world_rank INT,
    created_at TIMESTAMP
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES esports_teams(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50), -- captain, player, substitute
    joined_at TIMESTAMP,
    UNIQUE(team_id, user_id)
);

CREATE TABLE tournament_brackets (
    id UUID PRIMARY KEY,
    tournament_id UUID REFERENCES esports_tournaments(id),
    round_number INT,
    match_number INT,
    team_1_id UUID REFERENCES esports_teams(id),
    team_2_id UUID REFERENCES esports_teams(id),
    winner_team_id UUID REFERENCES esports_teams(id),
    scheduled_time TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### APIs:
- `POST /esports/tournaments/create` - Create tournament
- `POST /esports/teams/create` - Create team
- `POST /esports/tournaments/{id}/register` - Register team
- `GET /esports/tournaments/{id}/bracket` - Get bracket
- `GET /esports/leaderboard/teams` - Team leaderboard
- `GET /esports/upcoming` - Upcoming tournaments

---

### N.2 Ranking & Leaderboard V2
**Location**: `backend/services/ranking_service/`

#### Features:
- **Global Rankings**
  - Overall rank (all games)
  - Game-specific rank
  - Regional rankings
  - Age group rankings

- **Rank Tiers**
  - Bronze (0-999)
  - Silver (1000-1499)
  - Gold (1500-1999)
  - Platinum (2000-2499)
  - Diamond (2500-2999)
  - Master (3000-3499)
  - Grandmaster (3500-3999)
  - Legend (4000+)

- **Seasonal Rankings**
  - Reset every season (3 months)
  - Season rewards
  - Rank decay for inactivity
  - Placement matches

- **Leaderboard Features**
  - Real-time updates
  - Historical rankings
  - Rank change tracking
  - Percentile display

---

### N.3 Coaching & Training Mode
**Location**: `backend/services/training_service/`

#### Features:
- **Interactive Tutorials**
  - Step-by-step game guides
  - Practice scenarios
  - Skill challenges
  - Progress tracking

- **AI Coach**
  - Analyze gameplay
  - Identify mistakes
  - Suggest improvements
  - Personalized tips

- **Training Matches**
  - Practice against AI
  - No entry fee
  - Unlimited retries
  - Scenario builder

- **Pro Player Replays**
  - Watch top players
  - Learn strategies
  - Annotated replays
  - Study mode

#### Database Tables:
```sql
CREATE TABLE training_modules (
    id UUID PRIMARY KEY,
    game_code VARCHAR(50),
    module_name VARCHAR(200),
    difficulty VARCHAR(20),
    description TEXT,
    objectives JSONB,
    rewards JSONB,
    completion_time_avg INT,
    created_at TIMESTAMP
);

CREATE TABLE user_training_progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    module_id UUID REFERENCES training_modules(id),
    status VARCHAR(20), -- in_progress, completed, failed
    score INT,
    time_taken INT,
    attempts INT DEFAULT 1,
    completed_at TIMESTAMP,
    UNIQUE(user_id, module_id)
);
```

---

## Module O: Battle Pass & Progression

### O.1 Battle Pass System
**Location**: `backend/services/battlepass_service/`

#### Features:
- **Seasonal Battle Pass**
  - Free tier (available to all)
  - Premium tier (₹499 per season)
  - 100 levels per season
  - XP-based progression
  - Exclusive rewards

- **Rewards**
  - Bonus coins
  - Exclusive avatars
  - Custom emotes
  - Profile themes
  - Entry ticket bundles
  - XP boosters

- **Challenges**
  - Daily challenges (50 XP)
  - Weekly challenges (200 XP)
  - Season challenges (500 XP)
  - Challenge tracking

- **Premium Features**
  - Instant unlock tiers
  - 20% XP boost
  - Exclusive chat emotes
  - Priority matchmaking

#### Database Tables:
```sql
CREATE TABLE battle_pass_seasons (
    id UUID PRIMARY KEY,
    season_number INT,
    season_name VARCHAR(100),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    max_level INT DEFAULT 100,
    free_rewards JSONB,
    premium_rewards JSONB,
    is_active BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_battle_pass (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    season_id UUID REFERENCES battle_pass_seasons(id),
    current_level INT DEFAULT 1,
    current_xp INT DEFAULT 0,
    is_premium BOOLEAN DEFAULT FALSE,
    purchased_at TIMESTAMP,
    UNIQUE(user_id, season_id)
);

CREATE TABLE battle_pass_challenges (
    id UUID PRIMARY KEY,
    season_id UUID REFERENCES battle_pass_seasons(id),
    challenge_type VARCHAR(20), -- daily, weekly, seasonal
    challenge_name VARCHAR(200),
    challenge_description TEXT,
    challenge_objective JSONB,
    xp_reward INT,
    start_date TIMESTAMP,
    end_date TIMESTAMP
);

CREATE TABLE user_challenge_progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    challenge_id UUID REFERENCES battle_pass_challenges(id),
    progress INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    UNIQUE(user_id, challenge_id)
);
```

#### APIs:
- `GET /battlepass/current` - Get current season
- `GET /battlepass/my-progress` - User's battle pass progress
- `POST /battlepass/purchase` - Buy premium battle pass
- `GET /battlepass/challenges` - Get active challenges
- `POST /battlepass/claim-reward/{level}` - Claim reward

---

### O.2 Advanced Achievement System
**Location**: `backend/services/achievements_service/`

#### Features:
- **Achievement Categories**
  - Game Mastery (per game)
  - Social (friends, clans)
  - Competitive (tournaments, ranks)
  - Economic (earnings, spending)
  - Special Events
  - Secret achievements

- **Achievement Types**
  - One-time achievements
  - Progressive achievements (bronze/silver/gold)
  - Tiered achievements (levels 1-10)
  - Seasonal achievements

- **Achievement Rewards**
  - XP points
  - Bonus coins
  - Exclusive titles
  - Profile badges
  - Avatar frames

- **Showcase**
  - Featured achievements (pin 3)
  - Achievement rarity
  - Completion percentage
  - Achievement hunters leaderboard

#### Database Tables:
```sql
CREATE TABLE achievements (
    id UUID PRIMARY KEY,
    achievement_code VARCHAR(50) UNIQUE,
    achievement_name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    difficulty VARCHAR(20), -- easy, medium, hard, legendary
    icon_url VARCHAR(500),
    requirements JSONB,
    rewards JSONB,
    is_secret BOOLEAN DEFAULT FALSE,
    is_seasonal BOOLEAN DEFAULT FALSE,
    season_id UUID,
    created_at TIMESTAMP
);

CREATE TABLE user_achievements (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    achievement_id UUID REFERENCES achievements(id),
    progress INT DEFAULT 0,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP,
    is_featured BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, achievement_id)
);

CREATE TABLE achievement_tiers (
    id UUID PRIMARY KEY,
    achievement_id UUID REFERENCES achievements(id),
    tier_level INT,
    tier_name VARCHAR(50),
    requirement INT,
    reward JSONB
);
```

---

## Module P: Customer Support & CRM

### P.1 Advanced Ticketing System
**Location**: `backend/services/support_service/tickets/`

#### Features:
- **Ticket Creation**
  - Category selection (account, payment, technical, report)
  - Priority levels
  - File attachments
  - Screenshots
  - Auto-categorization (AI)

- **Ticket Management**
  - Ticket status tracking
  - Assignment to agents
  - SLA timers
  - Escalation rules
  - Canned responses
  - Internal notes

- **User Experience**
  - Ticket history
  - Real-time updates
  - Email notifications
  - In-app notifications
  - Rating & feedback

- **Agent Dashboard**
  - Ticket queue
  - Active tickets
  - SLA warnings
  - Performance metrics
  - Knowledge base access

#### Database Tables:
```sql
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE,
    user_id UUID REFERENCES users(id),
    category VARCHAR(50),
    priority VARCHAR(20), -- low, medium, high, urgent
    subject VARCHAR(200),
    description TEXT,
    status VARCHAR(20), -- open, in_progress, waiting, resolved, closed
    assigned_to UUID REFERENCES admin_users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    resolved_at TIMESTAMP,
    sla_due_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_assigned (assigned_to)
);

CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES support_tickets(id),
    sender_id UUID, -- user or admin
    sender_type VARCHAR(10), -- user, agent
    message TEXT,
    attachments JSONB,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

CREATE TABLE ticket_ratings (
    id UUID PRIMARY KEY,
    ticket_id UUID UNIQUE REFERENCES support_tickets(id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP
);
```

#### APIs:
- `POST /support/tickets/create` - Create ticket
- `GET /support/tickets` - Get user's tickets
- `GET /support/tickets/{ticket_id}` - Get ticket details
- `POST /support/tickets/{ticket_id}/reply` - Reply to ticket
- `POST /support/tickets/{ticket_id}/rate` - Rate support

---

### P.2 Live Chat Support
**Location**: `backend/services/support_service/livechat/`

#### Features:
- **Real-Time Chat**
  - Instant agent connection
  - Queue system
  - Average wait time display
  - Chat transfer between agents
  - Chat history saved

- **Chatbot First Tier**
  - AI handles common queries
  - Escalate to human agent
  - 24/7 availability
  - Multi-language support

#### Technology:
- **Socket.IO** for real-time
- **Dialogflow** or **Rasa** for AI chatbot

---

### P.3 CRM & User Segmentation
**Location**: `backend/services/crm_service/`

#### Features:
- **User Segmentation**
  - Behavioral segments
  - Demographic segments
  - Value-based segments (VIP, regular, at-risk)
  - Engagement level
  - Churn prediction

- **Campaign Management**
  - Targeted email campaigns
  - Push notification campaigns
  - In-app messages
  - Personalized offers
  - A/B testing

- **User Lifecycle**
  - New user onboarding
  - Activation campaigns
  - Retention campaigns
  - Win-back campaigns
  - VIP rewards

#### Database Tables:
```sql
CREATE TABLE user_segments (
    id UUID PRIMARY KEY,
    segment_name VARCHAR(100),
    segment_criteria JSONB,
    created_at TIMESTAMP
);

CREATE TABLE user_segment_mapping (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    segment_id UUID REFERENCES user_segments(id),
    added_at TIMESTAMP,
    UNIQUE(user_id, segment_id)
);

CREATE TABLE marketing_campaigns (
    id UUID PRIMARY KEY,
    campaign_name VARCHAR(200),
    campaign_type VARCHAR(50), -- email, push, in_app
    target_segment_id UUID REFERENCES user_segments(id),
    message_template JSONB,
    scheduled_at TIMESTAMP,
    status VARCHAR(20),
    sent_count INT DEFAULT 0,
    opened_count INT DEFAULT 0,
    clicked_count INT DEFAULT 0,
    conversion_count INT DEFAULT 0,
    created_at TIMESTAMP
);
```

---

## Module Q: Analytics & Business Intelligence

### Q.1 Advanced Analytics Dashboard
**Location**: `admin-panel/src/pages/analytics/advanced/`

#### Features:
- **User Analytics**
  - Cohort retention analysis
  - User lifetime value (LTV)
  - Customer acquisition cost (CAC)
  - Churn prediction
  - User journey funnel

- **Game Analytics**
  - Game popularity trends
  - Average session duration
  - Engagement metrics
  - Win rate distribution
  - Economy balance analysis

- **Financial Analytics**
  - Revenue forecasting
  - Payment method breakdown
  - Deposit/withdrawal patterns
  - Rake/commission tracking
  - Profitability per user

- **Real-Time Dashboard**
  - Live user count
  - Current active games
  - Real-time revenue
  - Geographic distribution
  - Server health metrics

#### Technology:
- **Google BigQuery** or **Amazon Redshift** for data warehouse
- **Metabase** or **Superset** for BI
- **Python** for data processing

---

### Q.2 A/B Testing Framework
**Location**: `backend/services/experiments_service/`

#### Features:
- **Experiment Management**
  - Create A/B tests
  - Define variants
  - Traffic allocation
  - Statistical significance
  - Automatic winner selection

- **Test Types**
  - UI/UX tests
  - Pricing tests
  - Feature tests
  - Algorithm tests

#### Database Tables:
```sql
CREATE TABLE ab_experiments (
    id UUID PRIMARY KEY,
    experiment_name VARCHAR(200),
    description TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20), -- draft, running, completed
    traffic_percentage INT,
    variants JSONB,
    success_metric VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE user_experiment_assignments (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    experiment_id UUID REFERENCES ab_experiments(id),
    variant VARCHAR(50),
    assigned_at TIMESTAMP,
    UNIQUE(user_id, experiment_id)
);

CREATE TABLE experiment_events (
    id UUID PRIMARY KEY,
    experiment_id UUID REFERENCES ab_experiments(id),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP
);
```

---

## Module R: Additional Advanced Features

### R.1 Daily Spin & Rewards V2
**Enhanced version with more engagement**

#### Features:
- **Lucky Spin Wheel**
  - Multiple wheels (Bronze, Silver, Gold)
  - Unlock higher tiers with activity
  - Grand prizes (iPhone, Gaming PC, etc.)
  - Spin tokens (earn or buy)

- **Scratch Cards**
  - Digital scratch cards
  - Instant prizes
  - Collect sets for bonuses

- **Login Streaks**
  - Enhanced rewards
  - Streak milestones (7, 30, 100, 365 days)
  - Comeback bonuses

---

### R.2 Gifting System
**Location**: `backend/services/gifting_service/`

#### Features:
- **Send Gifts**
  - Send coins to friends
  - Gift entry tickets
  - Gift battle pass
  - Gift premium subscription

- **Gift Cards**
  - Platform gift cards
  - Redeemable codes
  - Bulk purchases
  - Corporate gifting

---

### R.3 Loyalty Program (VIP System)
**Location**: `backend/services/loyalty_service/`

#### Features:
- **VIP Tiers**
  - VIP 1-10 based on activity
  - Exclusive benefits per tier
  - Faster withdrawals
  - Higher table limits
  - Personal account manager (VIP 8+)
  - Birthday bonuses

- **VIP Perks**
  - Cashback on losses
  - Exclusive tournaments
  - Priority support
  - Custom avatars
  - VIP-only events

#### Database Tables:
```sql
CREATE TABLE vip_tiers (
    id UUID PRIMARY KEY,
    tier_level INT UNIQUE,
    tier_name VARCHAR(50),
    required_points INT,
    perks JSONB,
    cashback_percentage DECIMAL(5,2)
);

CREATE TABLE user_vip_status (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES users(id),
    current_tier INT REFERENCES vip_tiers(tier_level),
    total_points INT DEFAULT 0,
    month_points INT DEFAULT 0,
    last_tier_update TIMESTAMP
);
```

---

## Updated Tech Stack for Advanced Features

### Additional Technologies:

```yaml
Backend:
  - Agora.io: Voice chat (₹100/month base + usage)
  - Twilio Video: Alternative voice/video
  - FFmpeg: Video processing
  - TensorFlow: ML models
  - Dialogflow: AI chatbot

Frontend:
  - WebRTC: Peer-to-peer connections
  - Video.js: Video player
  - OBS.js: Streaming

Infrastructure:
  - CloudFlare Stream: Video CDN (₹5/1000 min)
  - AWS MediaConvert: Video processing
  - BigQuery: Data warehouse (₹5/TB)
```

---

## Updated Cost Estimation

| Service | Monthly Cost |
|---------|--------------|
| Base Infrastructure (from before) | $1,650 |
| Voice Chat (Agora.io) | $200 |
| Video Streaming (CloudFlare) | $300 |
| BigQuery (Analytics) | $150 |
| AI/ML Services | $100 |
| **Total Advanced Features** | **$2,400/month** |

---

## Summary of Advanced Modules

| Module | Key Features | Priority |
|--------|--------------|----------|
| **K - Social** | Friends, Chat, Clans, Voice | High |
| **L - Streaming** | Live streaming, Replays | Medium |
| **M - AI** | Recommendations, Fraud AI | High |
| **N - Esports** | Pro tournaments, Teams, Coaching | Medium |
| **O - Progression** | Battle Pass, Achievements | High |
| **P - Support** | Tickets, Live Chat, CRM | High |
| **Q - Analytics** | BI, A/B Testing | Medium |
| **R - Extras** | Gifting, VIP, Enhanced Rewards | Low |

---

## Updated Implementation Timeline

**These advanced features add 3-4 months to development:**

- **Phase 11**: Social Features (Week 27-29)
- **Phase 12**: Streaming & Content (Week 30-32)
- **Phase 13**: Esports & Competitive (Week 33-35)
- **Phase 14**: Battle Pass & CRM (Week 36-38)

**New Total Timeline: 9-10 months**

---

**Document Version**: 2.0
**Last Updated**: November 16, 2025
**Total Features**: 50+ advanced features added
**New Modules**: 8 major modules (K through R)
