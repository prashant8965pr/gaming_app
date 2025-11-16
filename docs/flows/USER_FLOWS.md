# User Flows & Sequence Diagrams

## Flow 1: User Onboarding & Registration

### Sequence Diagram
```
User → App → Backend → SMS Gateway → Database
 │       │       │           │           │
 │──1.Open App──→│           │           │
 │       │       │           │           │
 │←─2.Show Login Screen─────┤           │
 │       │       │           │           │
 │──3.Enter Phone+Click Send OTP───────→│
 │       │       │           │           │
 │       │──4.Validate Phone─→           │
 │       │       │           │           │
 │       │       ├──5.Check Rate Limit──→│
 │       │       │           │           │
 │       │       ├──6.Generate OTP───────→│
 │       │       │           │           │
 │       │       ├──7.Send OTP SMS───────→│
 │       │       │           │           │
 │       │←─8.OTP Sent Success──────────┤
 │       │       │           │           │
 │←─9.Show OTP Input Screen─┤           │
 │       │       │           │           │
 │──10.Enter OTP & Submit─────────────→ │
 │       │       │           │           │
 │       │       ├──11.Verify OTP────────→│
 │       │       │           │           │
 │       │       ├──12.Check if New User─→│
 │       │       │           │           │
 │       │       ├──13.Create User (if new)→│
 │       │       │           │           │
 │       │       ├──14.Generate Referral Code│
 │       │       │           │           │
 │       │       ├──15.Create Wallets────→│
 │       │       │           │           │
 │       │       ├──16.Give Signup Bonus─→│
 │       │       │           │           │
 │       │       ├──17.Generate JWT Tokens│
 │       │       │           │           │
 │       │       ├──18.Create Session────→│
 │       │       │           │           │
 │       │←─19.Return User Data + Tokens┤
 │       │       │           │           │
 │←─20.Navigate to Home Screen──────────┤
```

### Steps Detail:
1. **User opens app**
2. **App shows login screen** with phone input
3. **User enters phone** and clicks "Send OTP"
4. **Backend validates** phone format
5. **Check rate limit**: Max 3 OTPs per hour
6. **Generate 6-digit OTP** and store with 5-min expiry
7. **Send SMS** via Twilio/MSG91
8. **Return success** to app
9. **App shows OTP input** screen
10. **User enters OTP** and submits
11. **Backend verifies OTP** and attempts count
12. **Check if user exists** in database
13. **If new user**: Create user record
14. **Generate unique referral code** (e.g., JOHN1234)
15. **Create 3 wallets** (Cash, Winnings, Bonus)
16. **Credit signup bonus** (₹50 to Bonus wallet)
17. **Generate JWT tokens** (Access + Refresh)
18. **Create session record** with device info
19. **Return user data** and tokens
20. **Navigate to home screen**

---

## Flow 2: Add Money to Wallet

### Sequence Diagram
```
User → App → Backend → Payment Gateway → Database
 │      │       │           │               │
 │──1.Click Add Money──→    │               │
 │      │       │           │               │
 │←─2.Show Amount Selection─┤               │
 │      │       │           │               │
 │──3.Select ₹500 & Proceed────────→        │
 │      │       │           │               │
 │      │       ├──4.Validate Amount        │
 │      │       │           │               │
 │      │       ├──5.Create Payment Order──→│
 │      │       │           │               │
 │      │       ├──6.Call Razorpay API─────→│
 │      │       │           │               │
 │      │       │←─7.Return Order ID────────┤
 │      │       │           │               │
 │      │←─8.Return Gateway Details────────┤
 │      │       │           │               │
 │←─9.Open Razorpay Checkout─┤             │
 │      │       │           │               │
 │──10.Select UPI & Pay──────────────────→  │
 │      │       │           │               │
 │      │       │←─11.Payment Webhook──────┤
 │      │       │           │               │
 │      │       ├──12.Verify Signature      │
 │      │       │           │               │
 │      │       ├──13.Update Payment Status─→│
 │      │       │           │               │
 │      │       ├──14.Credit Wallet────────→│
 │      │       │           │               │
 │      │       ├──15.Create Transaction───→│
 │      │       │           │               │
 │      │       ├──16.Send Notification     │
 │      │       │           │               │
 │      │←─17.Payment Success Callback─────┤
 │      │       │           │               │
 │←─18.Show Success & Updated Balance──────┤
```

### Steps Detail:
1. **User clicks** "Add Money" button
2. **App shows** amount selection (₹100, ₹500, ₹1000, etc.)
3. **User selects** ₹500 and proceeds
4. **Backend validates** amount (min ₹10, max ₹1,00,000)
5. **Create payment order** in database
6. **Call Razorpay** createOrder API
7. **Razorpay returns** order_id and key
8. **Backend returns** gateway details to app
9. **App opens** Razorpay checkout UI
10. **User completes** payment via UPI/Card
11. **Razorpay sends webhook** to backend
12. **Verify payment signature** for security
13. **Update payment status** to "success"
14. **Credit ₹500** to Cash Wallet
15. **Create transaction** record
16. **Send push notification** "Money added successfully"
17. **Send callback** to app
18. **App shows** success message and updated balance

---

## Flow 3: Quick Match (1v1 Battle)

### Sequence Diagram
```
User → App → Backend → Matchmaking → Game Engine → WebSocket
 │      │       │           │             │            │
 │──1.Select Game (Ludo)───→│             │            │
 │      │       │           │             │            │
 │←─2.Show Entry Fee Options┤             │            │
 │      │       │           │             │            │
 │──3.Select ₹100 & Find Match───────→    │            │
 │      │       │           │             │            │
 │      │       ├──4.Check Wallet Balance │            │
 │      │       │           │             │            │
 │      │       ├──5.Deduct ₹100 from Wallet           │
 │      │       │           │             │            │
 │      │       ├──6.Add to Matchmaking Queue─────────→│
 │      │       │           │             │            │
 │      │       │           ├──7.Find Similar ELO Players
 │      │       │           │             │            │
 │      │←─8.Return Queue Position─────────────────────┤
 │      │       │           │             │            │
 │←─9.Show "Finding Opponents..." (Position: 3)───────┤
 │      │       │           │             │            │
 │      │       │           ├──10.Match Found (2 players)
 │      │       │           │             │            │
 │      │       │           ├──11.Create Match Record─→│
 │      │       │           │             │            │
 │      │       │           │             ├──12.Initialize Game State
 │      │       │           │             │            │
 │      │       │←─13.Notify Match Found──┤            │
 │      │       │           │             │            │
 │      │←─14.WebSocket: Match Found Event──────────────┤
 │      │       │           │             │            │
 │←─15.Show Match Details & "Join" Button─┤            │
 │      │       │           │             │            │
 │──16.Click Join Match────────────────────────────────→│
 │      │       │           │             │            │
 │      │       │           │             ├──17.Assign Position (1 or 2)
 │      │       │           │             │            │
 │      │       │           │             ├──18.Connect to WebSocket───→│
 │      │       │           │             │            │
 │      │←─19.Game Screen with Opponent Info───────────┤
 │      │       │           │             │            │
 │←─20.WebSocket: Game Started Event──────────────────┤
 │      │       │           │             │            │
 │←─21.Show "Your Turn" or "Opponent's Turn"──────────┤
```

### Steps Detail:
1. **User selects** game (Ludo)
2. **App shows** entry fee options (₹10, ₹50, ₹100, etc.)
3. **User selects** ₹100 and clicks "Find Match"
4. **Backend checks** if user has ₹100 in wallet
5. **Deduct ₹100** from wallet (locked until match ends)
6. **Add user** to matchmaking queue
7. **Matchmaking service** finds opponent with similar ELO (±200)
8. **Return queue position** to user
9. **App shows** "Finding opponents..." with position
10. **Match found** with 2 players of similar skill
11. **Create match record** in database
12. **Game engine** initializes game state
13. **Notify both players** via WebSocket
14. **App receives** match_found event
15. **Show match details**: opponent info, 10-sec join deadline
16. **User clicks** "Join Match"
17. **Assign player position** (Player 1 or Player 2)
18. **Establish WebSocket** connection for real-time gameplay
19. **Show game screen** with opponent details
20. **Receive game_started** event
21. **Show turn indicator**

---

## Flow 4: Gameplay (Turn-Based)

### Sequence Diagram
```
Player 1 → App → WebSocket → Game Engine → Database
    │       │        │            │            │
    │──1.Roll Dice (Click)─────→  │            │
    │       │        │            │            │
    │       │        ├──2.Validate Turn────────│
    │       │        │            │            │
    │       │        │            ├──3.Generate Dice (1-6)
    │       │        │            │            │
    │       │        │            ├──4.Update Game State──→│
    │       │        │            │            │
    │       │        │←─5.Broadcast Dice Result─┤         │
    │       │        │            │            │
    │←─6.Show Dice: 6────────────┤            │
    │       │        │            │            │
    │       │        │─(Same event to Player 2)→│
    │       │        │            │            │
    │──7.Select Token & Move─────→│            │
    │       │        │            │            │
    │       │        ├──8.Validate Move (Rules)│
    │       │        │            │            │
    │       │        │            ├──9.Apply Move to State
    │       │        │            │            │
    │       │        │            ├──10.Check Win Condition
    │       │        │            │            │
    │       │        │            ├──11.Update Turn (Player 2)
    │       │        │            │            │
    │       │        │            ├──12.Save Move Record──→│
    │       │        │            │            │
    │       │        │←─13.Broadcast Move Result─┤        │
    │       │        │            │            │
    │←─14.Update UI with Move────┤            │
    │       │        │            │            │
    │       │        │─(Same event to Player 2: "Your Turn")
```

### Steps Detail:
1. **Player 1 clicks** "Roll Dice"
2. **WebSocket validates** it's Player 1's turn
3. **Game engine generates** random dice value (1-6)
4. **Update game state** in memory and database
5. **Broadcast dice result** to both players
6. **Player 1 sees** dice value (e.g., 6)
7. **Player 1 selects** token and destination
8. **Validate move** against game rules
9. **Apply move** to game state
10. **Check** if player won (all tokens home)
11. **Update turn** to Player 2
12. **Save move** in database
13. **Broadcast move** to both players
14. **Both players' UI** updates with new positions

---

## Flow 5: Game Completion & Winnings

### Sequence Diagram
```
Game Engine → Database → Wallet Service → Notification → User
     │           │             │               │          │
     ├──1.Detect Win Condition │               │          │
     │           │             │               │          │
     ├──2.Calculate Final Scores               │          │
     │           │             │               │          │
     ├──3.Determine Winner & Ranks             │          │
     │           │             │               │          │
     ├──4.Save Match Result────→│               │          │
     │           │             │               │          │
     ├──5.Calculate Prize Distribution          │          │
     │           │   (₹100×2 = ₹200 pool)       │          │
     │           │   Platform fee: ₹20 (10%)    │          │
     │           │   Winner: ₹180 (90%)         │          │
     │           │             │               │          │
     ├──6.Call Wallet Service──────────────→   │          │
     │           │             │               │          │
     │           │             ├──7.Credit ₹180 to Winner  │
     │           │             │               │          │
     │           │             ├──8.Update Transaction────→│
     │           │             │               │          │
     │           │             ├──9.Update User Stats─────→│
     │           │             │               │          │
     │           │             ├──10.Update ELO Rating───→│
     │           │             │               │          │
     │           │←────11.Return Success───────┤          │
     │           │             │               │          │
     ├──12.Send Notification─────────────────────────────→│
     │           │             │               │          │
     ├──13.WebSocket: Game Over Event──────────────────→ User
     │           │             │               │          │
     │           │             │               │←─14.Show Result Screen
     │           │             │               │          │
     │           │             │               │          Winner sees:
     │           │             │               │          "You Won! ₹180"
     │           │             │               │
     │           │             │               │          Loser sees:
     │           │             │               │          "You Lost"
```

### Steps Detail:
1. **Game engine detects** all tokens of Player 1 reached home
2. **Calculate final scores** for ranking
3. **Determine** Winner (Rank 1) and Loser (Rank 2)
4. **Save match result** to database
5. **Calculate prize**:
   - Total pool: ₹100 × 2 = ₹200
   - Platform fee (10%): ₹20
   - Winner prize (90%): ₹180
6. **Call wallet service** to credit winnings
7. **Credit ₹180** to Winner's Winnings Wallet
8. **Create transaction record**
9. **Update user statistics**: games_won, total_winnings
10. **Update ELO rating**: Winner +30, Loser -30
11. **Wallet service** returns success
12. **Send push notification** to both players
13. **WebSocket sends** game_over event
14. **App shows** result screen with prize details

---

## Flow 6: Tournament Registration & Participation

### Sequence Diagram
```
User → App → Backend → Tournament Service → Database
 │      │       │             │                │
 │──1.Browse Tournaments─────→│                │
 │      │       │             │                │
 │      │       │             ├──2.Fetch Active Tournaments─→│
 │      │       │             │                │
 │      │←─3.Show Tournament List──────────────┤
 │      │       │             │                │
 │──4.Click Tournament Details───────→         │
 │      │       │             │                │
 │      │       │             ├──5.Get Tournament Details──→│
 │      │       │             │                │
 │      │←─6.Show Details (Entry: ₹50, Prize: ₹50,000)─────┤
 │      │       │             │                │
 │──7.Click "Register"───────────────→         │
 │      │       │             │                │
 │      │       │             ├──8.Check Eligibility        │
 │      │       │             │   - Already registered?     │
 │      │       │             │   - Tournament full?        │
 │      │       │             │   - Sufficient balance?     │
 │      │       │             │                │
 │      │       │             ├──9.Deduct ₹50 from Wallet──→│
 │      │       │             │                │
 │      │       │             ├──10.Create Registration────→│
 │      │       │             │                │
 │      │       │             ├──11.Increment Participant Count
 │      │       │             │                │
 │      │       │             ├──12.Add to Prize Pool──────→│
 │      │       │             │                │
 │      │←─13.Registration Successful──────────┤            │
 │      │       │             │                │
 │←─14.Show "Registered! Tournament starts in 2 hours"─────┤
 │      │       │             │                │
 │      │       │    [2 hours later]           │
 │      │       │             │                │
 │      │       │             ├──15.Tournament Start Time   │
 │      │       │             │                │
 │      │       │             ├──16.Create Matches (Pairings)
 │      │       │             │                │
 │      │       │             ├──17.Send Notification to All─→│
 │      │       │             │                │
 │←─18.Push: "Tournament started! Join your match"─────────┤
 │      │       │             │                │
 │──19.Open App & Join Match────────────→      │            │
 │      │       │             │                │
 │      │      [Player plays multiple rounds]  │            │
 │      │       │             │                │
 │      │       │             ├──20.Calculate Final Leaderboard
 │      │       │             │                │
 │      │       │             ├──21.Distribute Prizes───────→│
 │      │       │             │                │
 │←─22.Push: "Tournament ended! You ranked #25"────────────┤
```

### Steps Detail:
1. **User navigates** to Tournaments tab
2. **Backend fetches** active tournaments
3. **App displays** list of tournaments
4. **User clicks** on tournament for details
5. **Fetch tournament details** from database
6. **Show details**: Entry ₹50, Prize pool ₹50,000, 1000 players
7. **User clicks** "Register"
8. **Check eligibility**:
   - Not already registered
   - Tournament not full
   - Has ₹50 balance
9. **Deduct ₹50** from wallet
10. **Create registration** record
11. **Increment** current_participants count
12. **Add ₹50** to tournament prize pool
13. **Return** success response
14. **Show confirmation** and countdown
15. **Tournament start** time reached
16. **Create match pairings** (skill-based)
17. **Send notifications** to all participants
18. **User receives** push notification
19. **User opens app** and joins match
20. **After all rounds**: Calculate final leaderboard
21. **Distribute prizes** to top winners
22. **Send notification** with final rank

---

## Flow 7: Withdrawal Process

### Sequence Diagram
```
User → App → Backend → KYC Check → Wallet → Bank Transfer → Database
 │      │       │          │          │           │            │
 │──1.Click Withdraw Money─────→      │           │            │
 │      │       │          │          │           │            │
 │      │       ├──2.Check KYC Status─→           │            │
 │      │       │          │          │           │            │
 │      │       │←─3.KYC Verified─────┤           │            │
 │      │       │          │          │           │            │
 │      │       ├──4.Get Bank Accounts─────────────────────────→│
 │      │       │          │          │           │            │
 │      │←─5.Show Withdrawal Form (Balance, Bank)─┤            │
 │      │       │          │          │           │            │
 │──6.Enter ₹1000 & Submit─────────────────→      │            │
 │      │       │          │          │           │            │
 │      │       ├──7.Validate Amount (Min ₹100)   │            │
 │      │       │          │          │           │            │
 │      │       ├──8.Check Balance────→           │            │
 │      │       │          │          │           │            │
 │      │       ├──9.Calculate TDS (if applicable)│            │
 │      │       │          │  If winnings > ₹10K, 30% TDS      │
 │      │       │          │  Example: ₹1000, no TDS           │
 │      │       │          │          │           │            │
 │      │       ├──10.Create Withdrawal Request───────────────→│
 │      │       │          │          │           │            │
 │      │       ├──11.Deduct ₹1000 from Wallet───→            │
 │      │       │          │  (Status: Locked)    │            │
 │      │       │          │          │           │            │
 │      │←─12.Return Success (Status: Pending)────┤            │
 │      │       │          │          │           │            │
 │←─13.Show "Withdrawal request submitted. Processing in 2-3 days"
 │      │       │          │          │           │            │
 │      │      [Admin Approval Process]           │            │
 │      │       │          │          │           │            │
 │      │       ├──14.Admin Reviews Request───────────────────→│
 │      │       │          │          │           │            │
 │      │       ├──15.Admin Approves & Initiates Transfer─────→│
 │      │       │          │          │           │            │
 │      │       ├──16.Call Bank Transfer API─────────────────→│
 │      │       │          │          │  (IMPS/NEFT)           │
 │      │       │          │          │           │            │
 │      │       │←─17.Return UTR Number──────────┤            │
 │      │       │          │          │           │            │
 │      │       ├──18.Update Status: Success─────────────────→│
 │      │       │          │          │           │            │
 │      │       ├──19.Send Notification─────────────────→ User │
 │      │       │          │          │           │            │
 │←─20.Push: "Withdrawal successful! UTR: 123456789"──────────┤
```

### Steps Detail:
1. **User clicks** "Withdraw Money"
2. **Backend checks** KYC status
3. **KYC is verified** ✓
4. **Fetch user's** bank accounts
5. **Show withdrawal form** with balance and bank options
6. **User enters** ₹1000 and submits
7. **Validate**: Min ₹100, Max ₹1,00,000
8. **Check** if user has ₹1000 in withdrawable balance
9. **Calculate TDS**: None (winnings < ₹10,000)
10. **Create withdrawal request** with status "pending"
11. **Deduct ₹1000** from wallet (locked)
12. **Return success** response
13. **Show confirmation** message
14. **Admin reviews** in admin panel (fraud checks)
15. **Admin approves** and initiates transfer
16. **Call bank API** for IMPS/NEFT transfer
17. **Bank returns** UTR number
18. **Update status** to "success"
19. **Send push notification** to user
20. **User receives** notification with UTR

---

## Flow 8: Referral Flow

### Sequence Diagram
```
Referrer → App → Backend → Database ← New User (Referee)
   │        │       │         │           │
   │──1.Click "Refer & Earn"─→│           │
   │        │       │         │           │
   │←─2.Show Referral Code (JOHN1234) & Link───┤
   │        │       │         │           │
   │──3.Share Link via WhatsApp/Social──────→ Friend
   │        │       │         │           │
   │        │       │         │           │←─4.Friend Clicks Link
   │        │       │         │           │
   │        │       │         │           ├──5.Open App (Referral Code Pre-filled)
   │        │       │         │           │
   │        │       │         │←─6.Register with Code (JOHN1234)
   │        │       │         │           │
   │        │       │         ├──7.Create New User (Referee)
   │        │       │         │           │
   │        │       │         ├──8.Link to Referrer (JOHN1234)
   │        │       │         │           │
   │        │       │         ├──9.Credit ₹50 Bonus to Referee
   │        │       │         │           │
   │        │       │         ├──10.Create Referral Record (Status: Pending)
   │        │       │         │           │
   │        │       │         │           │──11.Referee Adds ₹100
   │        │       │         │           │
   │        │       │         │←─12.First Deposit Detected──┤
   │        │       │         │           │
   │        │       │         ├──13.Update Referral Status: Activated
   │        │       │         │           │
   │        │       │         ├──14.Credit ₹50 Bonus to Referrer
   │        │       │         │           │
   │        │       │         ├──15.Send Notification to Referrer
   │        │       │         │           │
   │←─16.Push: "Your friend joined! You earned ₹50"─────────┤
```

### Steps Detail:
1. **Referrer clicks** "Refer & Earn"
2. **Show referral code** (JOHN1234) and shareable link
3. **Referrer shares** link via WhatsApp/Facebook
4. **Friend clicks** referral link
5. **App opens** with referral code pre-filled
6. **Friend registers** using the code
7. **Create new user** account
8. **Link referee** to referrer in database
9. **Credit ₹50** to referee's bonus wallet (signup bonus)
10. **Create referral record** with status "pending"
11. **Referee adds** ₹100 (first deposit)
12. **System detects** first deposit
13. **Update referral** status to "activated"
14. **Credit ₹50** to referrer's bonus wallet
15. **Send notification** to referrer
16. **Referrer receives** "Friend joined" notification

---

## Flow 9: Daily Rewards & Tasks

### Sequence Diagram
```
User → App → Backend → Database
 │      │       │          │
 │──1.Open App Daily──────→│
 │      │       │          │
 │      │       ├──2.Check Last Login Date──→│
 │      │       │          │
 │      │       ├──3.Calculate Streak        │
 │      │       │    Day 1-6: +₹5 daily     │
 │      │       │    Day 7: Streak bonus ₹50│
 │      │       │          │
 │      │       │←─4.Return Reward Info─────┤
 │      │       │          │
 │      │←─5.Show "Daily Reward Available!"─┤
 │      │       │          │
 │──6.Click "Claim Reward"────────→         │
 │      │       │          │
 │      │       ├──7.Mark Today as Claimed──→│
 │      │       │          │
 │      │       ├──8.Credit Bonus Wallet────→│
 │      │       │          │
 │      │       ├──9.Update Streak Count────→│
 │      │       │          │
 │      │←─10.Show Success Animation────────┤
 │      │       │          │
 │←─11."₹5 added to Bonus Wallet! Streak: Day 3"───┤
 │      │       │          │
 │──12.View Tasks Tab─────────────→         │
 │      │       │          │
 │      │       ├──13.Get Available Tasks───→│
 │      │       │    - Play first game: ₹20 │
 │      │       │    - Win first game: ₹50  │
 │      │       │    - Complete profile: ₹10│
 │      │       │          │
 │      │←─14.Show Task List with Progress──┤
 │      │       │          │
 │      │    [User completes a task]        │
 │      │       │          │
 │      │       ├──15.Detect Task Completion│
 │      │       │          │
 │      │       ├──16.Auto-Credit Reward────→│
 │      │       │          │
 │←─17.Push: "Task completed! ₹20 bonus"────┤
```

---

## Flow 10: Fraud Detection & Auto-Ban

### Sequence Diagram
```
User → Game → Fraud Detection AI → Database → Admin
 │      │           │                 │         │
 │──1.Play Multiple Games─────→       │         │
 │      │           │                 │         │
 │      │      [AI monitors gameplay] │         │
 │      │           │                 │         │
 │      │           ├──2.Detect Suspicious Pattern        │
 │      │           │   - Win rate: 95% (abnormal)       │
 │      │           │   - Same opponent repeatedly        │
 │      │           │   - Unusually fast moves            │
 │      │           │                 │         │
 │      │           ├──3.Calculate Fraud Score: 89/100───→│
 │      │           │                 │         │
 │      │           ├──4.Create Fraud Alert (High Severity)→│
 │      │           │                 │         │
 │      │           ├──5.Check Auto-Ban Threshold (85+)  │
 │      │           │                 │         │
 │      │           ├──6.Auto-Ban User─────────→│
 │      │           │                 │         │
 │      │           ├──7.Freeze Wallet────────→│
 │      │           │                 │         │
 │      │           ├──8.Send Alert to Admin───────────→│
 │      │           │                 │         │
 │      │←─9.WebSocket: Account Suspended────┤  │
 │      │           │                 │         │
 │←─10.Show "Account suspended. Contact support"─┤
 │      │           │                 │         │
 │      │           │                 │         │──11.Admin Reviews
 │      │           │                 │         │
 │      │           │                 │←─12.Confirm Ban or Unban
 │      │           │                 │         │
 │      │           │                 │         (If false positive: Unban)
 │      │           │                 │         (If fraud: Permanent ban)
```

---

## Summary of Complete User Journey

```
Day 1: Registration → KYC → Add Money → Play Game → Win/Lose
Day 2: Login → Claim Daily Reward → Join Tournament → Play
Day 3: Refer Friend → Get Bonus → Play More → Level Up
Day 7: Withdraw Winnings → Check Leaderboard → Become VIP
```

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Total Flows Documented**: 10
**Next Steps**: Implement flows phase by phase
