# Advanced Features Documentation

This document covers the advanced features implemented in the Gaming Platform.

## Table of Contents

1. [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
2. [Email Notification System](#email-notification-system)
3. [Promo Code System](#promo-code-system)

---

## Two-Factor Authentication (2FA)

### Overview

The platform implements TOTP-based Two-Factor Authentication for enhanced account security. Users can enable 2FA to add an extra layer of protection to their accounts.

### Features

- **TOTP (Time-based One-Time Password)** - Industry-standard 2FA using apps like Google Authenticator, Authy, etc.
- **QR Code Generation** - Easy setup with QR code scanning
- **Backup Codes** - 10 single-use backup codes for account recovery
- **Flexible Management** - Users can enable/disable 2FA at any time

### Implementation Details

#### Models

**TwoFactorAuth** (`backend/models/two_factor.py`)
```python
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to users)
- secret: String(32) - Base32 encoded TOTP secret
- is_enabled: Boolean - Whether 2FA is active
- backup_codes_used: Integer - Count of used backup codes
- enabled_at: DateTime - When 2FA was enabled
- created_at: DateTime
- updated_at: DateTime
```

**TwoFactorBackupCode** (`backend/models/two_factor.py`)
```python
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to users)
- code_hash: String(255) - Hashed backup code
- is_used: Boolean
- used_at: DateTime
- created_at: DateTime
```

#### API Endpoints

All endpoints are prefixed with `/api/v1/2fa/`

##### POST /setup
Setup 2FA for the current user.

**Request:** Authenticated user (JWT token required)

**Response:**
```json
{
  "success": true,
  "data": {
    "secret": "BASE32ENCODEDSECRET",
    "qr_code": "data:image/png;base64,...",
    "backup_codes": ["CODE1", "CODE2", ..., "CODE10"]
  }
}
```

**Usage Flow:**
1. User calls `/setup`
2. App displays QR code for scanning with authenticator app
3. App shows backup codes for user to save securely
4. User verifies with TOTP token to enable

---

##### POST /enable
Enable 2FA after setup and verification.

**Request:**
```json
{
  "token": "123456",
  "backup_codes": ["CODE1", "CODE2", ..., "CODE10"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Two-factor authentication enabled successfully"
}
```

---

##### POST /verify
Verify TOTP token or backup code.

**Request:**
```json
{
  "token": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token verified successfully"
}
```

**Note:** This endpoint can accept both TOTP tokens and backup codes.

---

##### POST /verify-backup-code
Specifically verify a backup code.

**Request:**
```json
{
  "backup_code": "BACKUPCODE123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Backup code verified successfully",
  "data": {
    "remaining_codes": 8
  }
}
```

**Note:** Backup codes are single-use and will be marked as used.

---

##### POST /disable
Disable 2FA for the current user.

**Request:**
```json
{
  "password": "user_password",
  "token": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Two-factor authentication disabled successfully"
}
```

---

##### POST /regenerate-backup-codes
Regenerate all backup codes (invalidates old codes).

**Request:**
```json
{
  "token": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "backup_codes": ["NEWCODE1", "NEWCODE2", ..., "NEWCODE10"]
  }
}
```

---

##### GET /status
Get 2FA status for current user.

**Response:**
```json
{
  "success": true,
  "data": {
    "is_enabled": true,
    "backup_codes_remaining": 8,
    "enabled_at": "2025-01-15T10:30:00Z"
  }
}
```

---

### Frontend Integration

**Example: Enable 2FA Flow**

```typescript
// 1. Setup 2FA
const setupResponse = await fetch('/api/v1/2fa/setup', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});

const { data } = await setupResponse.json();
// data.qr_code - Display to user for scanning
// data.backup_codes - Show to user to save

// 2. User scans QR code and enters first token
const enableResponse = await fetch('/api/v1/2fa/enable', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: userEnteredToken,
    backup_codes: data.backup_codes,
  }),
});

// 3. From now on, user needs to provide TOTP token during login
```

**Example: Login with 2FA**

```typescript
// 1. Normal login with OTP
const loginResponse = await fetch('/api/v1/auth/verify-otp', {
  method: 'POST',
  body: JSON.stringify({ phone, otp, device_id, device_name, device_os }),
});

const loginData = await loginResponse.json();

// 2. If user has 2FA enabled, loginData will indicate this
if (loginData.requires_2fa) {
  // 3. Prompt user for TOTP token
  const token2FA = prompt('Enter your 2FA code:');

  // 4. Verify 2FA token
  const verify2FAResponse = await fetch('/api/v1/2fa/verify', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${loginData.temp_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token: token2FA }),
  });

  // 5. If verified, user is fully authenticated
}
```

---

## Email Notification System

### Overview

Comprehensive transactional email system with HTML templates for all major user events.

### Features

- **SMTP Integration** - Configurable SMTP server support
- **HTML Templates** - Beautiful, responsive email templates
- **Template Rendering** - Jinja2-based template engine
- **Async Sending** - Non-blocking email delivery
- **Error Handling** - Graceful failures with logging

### Email Types

The system supports the following email notifications:

1. **Welcome Email** - Sent when user registers
2. **KYC Approved** - Sent when KYC is approved
3. **KYC Rejected** - Sent when KYC is rejected with reason
4. **Deposit Confirmation** - Sent when deposit is successful
5. **Withdrawal Requested** - Sent when withdrawal is initiated
6. **Withdrawal Completed** - Sent when withdrawal is processed
7. **Game Win Notification** - Sent when user wins a game
8. **Referral Bonus** - Sent when user receives referral bonus
9. **2FA Enabled** - Sent when 2FA is enabled
10. **Password Reset** - Sent for password reset requests
11. **Promo Code Applied** - Sent when promo code is used

### Implementation Details

#### Service

**EmailService** (`backend/services/email_service.py`)

**Configuration:**
```python
# In .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM_NAME=Gaming Platform
EMAIL_FROM_ADDRESS=noreply@gamingplatform.com
```

**Usage:**
```python
from services.email_service import EmailService

email_service = EmailService()

# Send welcome email
await email_service.send_welcome_email(
    to_email="user@example.com",
    username="john_doe"
)

# Send KYC approved email
await email_service.send_kyc_approved_email(
    to_email="user@example.com",
    username="john_doe"
)

# Send deposit confirmation
await email_service.send_deposit_confirmation_email(
    to_email="user@example.com",
    username="john_doe",
    amount=1000.00,
    transaction_id="TXN123456"
)
```

### Email Templates

All email templates include:
- Responsive HTML design
- Inline CSS for email client compatibility
- Platform branding
- Call-to-action buttons
- Footer with contact information

**Template Variables:**

Each email template accepts specific variables:

**Welcome Email:**
- `username`: User's display name
- `platform_name`: "Gaming Platform"
- `login_url`: Link to login page

**KYC Approved:**
- `username`: User's display name
- `dashboard_url`: Link to user dashboard

**Deposit Confirmation:**
- `username`: User's display name
- `amount`: Deposit amount (formatted with currency)
- `transaction_id`: Unique transaction ID
- `timestamp`: Transaction timestamp

### Integration Points

Emails are automatically sent from the following services:

1. **Auth Service** - Welcome email on registration
2. **KYC Service** - KYC status emails on approval/rejection
3. **Wallet Service** - Deposit and withdrawal emails
4. **Game Service** - Win notification emails
5. **Referral Service** - Referral bonus emails
6. **2FA Service** - 2FA enabled email
7. **Promo Code Service** - Promo code applied email

---

## Promo Code System

### Overview

Flexible promo code system for marketing campaigns, user acquisition, and retention.

### Features

- **Multiple Discount Types** - Percentage, fixed amount, or free entry
- **Usage Limits** - Global and per-user limits
- **Validity Periods** - Time-based code activation
- **Targeted Campaigns** - Public or user-specific codes
- **Usage Tracking** - Complete analytics and statistics
- **Admin Management** - Full CRUD operations for admins

### Promo Code Types

1. **PERCENTAGE** - Percentage discount (e.g., 20% off)
   - Supports max discount cap
   - Example: "20% off up to ₹500"

2. **FIXED** - Fixed amount discount (e.g., ₹100 off)
   - Simple flat discount
   - Example: "₹100 off on your deposit"

3. **FREE_ENTRY** - Free game entry
   - Zero cost for game participation
   - Example: "Free entry to Ludo tournament"

### Implementation Details

#### Models

**PromoCode** (`backend/models/promo_code.py`)
```python
- id: UUID (Primary Key)
- code: String(50) - Unique promo code (uppercase)
- description: String(500) - Description for users
- type: Enum(PERCENTAGE, FIXED, FREE_ENTRY)
- value: Float - Percentage or fixed amount
- max_discount: Float - Max discount for percentage type
- max_uses: Integer - Total uses allowed (NULL = unlimited)
- max_uses_per_user: Integer - Per-user limit (default: 1)
- current_uses: Integer - Current usage count
- min_transaction_amount: Float - Minimum transaction to apply
- valid_from: DateTime - Code activation date
- valid_until: DateTime - Code expiration date
- status: Enum(ACTIVE, EXPIRED, DISABLED)
- is_public: Boolean - Public or targeted campaign
- target_user_ids: String - Comma-separated user IDs (for targeted)
- created_by: UUID - Admin who created the code
- created_at: DateTime
- updated_at: DateTime
```

**PromoCodeUsage** (`backend/models/promo_code.py`)
```python
- id: UUID (Primary Key)
- promo_code_id: UUID (Foreign Key)
- user_id: UUID (Foreign Key)
- discount_amount: Float - Actual discount received
- transaction_amount: Float - Original transaction amount
- used_at: DateTime
```

#### API Endpoints

##### Admin Endpoints

All admin endpoints require admin role and are prefixed with `/api/v1/admin/promo-codes/`

**POST /admin/promo-codes** - Create new promo code

**Request:**
```json
{
  "code": "WELCOME20",
  "description": "20% off for new users",
  "type": "PERCENTAGE",
  "value": 20,
  "max_discount": 500,
  "max_uses": 1000,
  "max_uses_per_user": 1,
  "min_transaction_amount": 100,
  "valid_from": "2025-01-01T00:00:00Z",
  "valid_until": "2025-12-31T23:59:59Z",
  "is_public": true,
  "target_user_ids": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Promo code created successfully",
  "data": {
    "id": "uuid",
    "code": "WELCOME20",
    "type": "PERCENTAGE",
    "value": 20,
    "is_valid": true,
    ...
  }
}
```

---

**GET /admin/promo-codes** - List all promo codes

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 20, max: 100)
- `status_filter`: Filter by status (ACTIVE, EXPIRED, DISABLED)

**Response:**
```json
{
  "success": true,
  "data": {
    "promo_codes": [...],
    "total": 45,
    "skip": 0,
    "limit": 20
  }
}
```

---

**GET /admin/promo-codes/{id}** - Get promo code details

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "WELCOME20",
    "description": "20% off for new users",
    "current_uses": 234,
    "remaining_uses": 766,
    ...
  }
}
```

---

**PATCH /admin/promo-codes/{id}** - Update promo code

**Request:**
```json
{
  "description": "Updated description",
  "max_uses": 2000,
  "valid_until": "2025-12-31T23:59:59Z",
  "status": "ACTIVE"
}
```

---

**DELETE /admin/promo-codes/{id}** - Delete promo code

**Note:** This will cascade delete all usage records.

---

**GET /admin/promo-codes/{id}/stats** - Get promo code statistics

**Response:**
```json
{
  "success": true,
  "data": {
    "code": "WELCOME20",
    "total_uses": 234,
    "unique_users": 187,
    "total_discount_given": 45600.00,
    "remaining_uses": 766,
    "is_active": true,
    "is_valid": true
  }
}
```

---

**GET /admin/promo-codes/{id}/usages** - Get usage history

**Response:**
```json
{
  "success": true,
  "data": {
    "usages": [
      {
        "id": "uuid",
        "user_id": "uuid",
        "discount_amount": 200.00,
        "transaction_amount": 1000.00,
        "used_at": "2025-01-15T10:30:00Z"
      },
      ...
    ],
    "total": 234,
    "skip": 0,
    "limit": 20
  }
}
```

---

##### User Endpoints

All user endpoints are prefixed with `/api/v1/promo-codes/`

**GET /promo-codes** - Get available promo codes

Returns only public, active, valid codes that user hasn't exhausted.

**Response:**
```json
{
  "success": true,
  "data": {
    "promo_codes": [
      {
        "code": "WELCOME20",
        "description": "20% off for new users",
        "type": "PERCENTAGE",
        "value": 20,
        "max_discount": 500,
        "min_transaction_amount": 100,
        "valid_until": "2025-12-31T23:59:59Z"
      },
      ...
    ]
  }
}
```

---

**POST /promo-codes/validate** - Validate promo code

**Query Parameters:**
- `code`: Promo code to validate
- `transaction_amount`: Optional transaction amount

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "code": "WELCOME20",
    "type": "PERCENTAGE",
    "value": 20,
    "discount_amount": 200.00,
    "final_amount": 800.00
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PROMO_CODE",
    "message": "Promo code has expired"
  }
}
```

---

**POST /promo-codes/apply** - Apply promo code

**Request:**
```json
{
  "code": "WELCOME20",
  "transaction_amount": 1000.00
}
```

**Response:**
```json
{
  "success": true,
  "message": "Promo code applied successfully",
  "data": {
    "code": "WELCOME20",
    "discount_amount": 200.00,
    "original_amount": 1000.00,
    "final_amount": 800.00
  }
}
```

**Note:** This records the usage and should be called during payment processing.

---

**GET /promo-codes/my-usages** - Get user's promo code history

**Response:**
```json
{
  "success": true,
  "data": {
    "usages": [
      {
        "id": "uuid",
        "code": "WELCOME20",
        "discount_amount": 200.00,
        "transaction_amount": 1000.00,
        "used_at": "2025-01-15T10:30:00Z"
      },
      ...
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
```

---

### Validation Rules

The promo code service validates:

1. **Code Existence** - Code must exist in database
2. **Status** - Code must be ACTIVE
3. **Validity Period** - Current time must be within valid_from and valid_until
4. **Total Usage** - current_uses < max_uses (if max_uses is set)
5. **Per-User Usage** - User hasn't exceeded max_uses_per_user
6. **Targeting** - User is in target_user_ids (if not public)
7. **Minimum Amount** - transaction_amount >= min_transaction_amount

### Discount Calculation

**Percentage Type:**
```python
discount = (transaction_amount * value) / 100
if max_discount:
    discount = min(discount, max_discount)
```

**Fixed Type:**
```python
discount = min(value, transaction_amount)
```

**Free Entry Type:**
```python
discount = 0.0  # Handled differently in game logic
```

---

### Frontend Integration

**Example: Apply Promo Code During Deposit**

```typescript
// 1. User enters promo code
const promoCode = 'WELCOME20';
const depositAmount = 1000;

// 2. Validate promo code
const validateResponse = await fetch(
  `/api/v1/promo-codes/validate?code=${promoCode}&transaction_amount=${depositAmount}`,
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  }
);

const validateData = await validateResponse.json();

if (validateData.success) {
  // 3. Show discount to user
  console.log(`Discount: ₹${validateData.data.discount_amount}`);
  console.log(`Final Amount: ₹${validateData.data.final_amount}`);

  // 4. User confirms deposit
  // 5. Apply promo code during payment
  const applyResponse = await fetch('/api/v1/promo-codes/apply', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code: promoCode,
      transaction_amount: depositAmount,
    }),
  });

  const applyData = await applyResponse.json();
  // Process payment with applyData.data.final_amount
}
```

---

## Database Migrations

To apply the new database tables for advanced features:

```bash
cd backend
alembic upgrade head
```

This will create the following tables:
- `two_factor_auth`
- `two_factor_backup_codes`
- `promo_codes`
- `promo_code_usages`

---

## Security Considerations

### Two-Factor Authentication

1. **Secret Storage** - TOTP secrets are stored in the database
   - Consider encrypting secrets at rest
   - Use secure random generation (pyotp.random_base32())

2. **Backup Codes** - Stored as hashed values
   - Uses secure password hashing
   - Single-use only

3. **Rate Limiting** - Implement rate limiting on verification endpoints
   - Prevent brute force attacks
   - Limit failed attempts

### Promo Codes

1. **Code Generation** - Use secure random codes
   - Avoid predictable patterns
   - Consider cryptographically secure random

2. **Usage Tracking** - Prevent abuse
   - Per-user limits
   - Global usage caps
   - Time-based validity

3. **Validation** - Server-side only
   - Never trust client-side validation
   - Check all constraints

---

## Testing

### Two-Factor Authentication Testing

```bash
# Manual testing with curl

# 1. Setup 2FA
curl -X POST http://localhost:8000/api/v1/2fa/setup \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Enable 2FA
curl -X POST http://localhost:8000/api/v1/2fa/enable \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456", "backup_codes": [...]}'

# 3. Verify token
curl -X POST http://localhost:8000/api/v1/2fa/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'
```

### Promo Code Testing

```bash
# Admin: Create promo code
curl -X POST http://localhost:8000/api/v1/admin/promo-codes \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "TEST20",
    "type": "PERCENTAGE",
    "value": 20,
    "valid_from": "2025-01-01T00:00:00Z",
    "valid_until": "2025-12-31T23:59:59Z",
    "is_public": true
  }'

# User: Validate promo code
curl -X POST "http://localhost:8000/api/v1/promo-codes/validate?code=TEST20&transaction_amount=1000" \
  -H "Authorization: Bearer USER_TOKEN"

# User: Apply promo code
curl -X POST http://localhost:8000/api/v1/promo-codes/apply \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "TEST20", "transaction_amount": 1000}'
```

---

## Troubleshooting

### Two-Factor Authentication

**Issue: QR code not displaying**
- Check that qrcode library is installed: `pip install qrcode`
- Verify base64 encoding in response

**Issue: Token verification fails**
- Ensure device clock is synchronized (TOTP is time-based)
- Check valid_window in verification (default: ±30 seconds)

**Issue: Backup codes not working**
- Verify codes are stored as hashes
- Check that code hasn't been used already

### Email Notifications

**Issue: Emails not sending**
- Verify SMTP configuration in .env
- Check SMTP credentials
- Enable "Less secure app access" for Gmail (or use App Password)
- Check firewall settings for SMTP port

**Issue: Emails going to spam**
- Configure SPF, DKIM, and DMARC records
- Use a verified sending domain
- Warm up new sending IPs

### Promo Codes

**Issue: Validation fails for valid code**
- Check code is ACTIVE status
- Verify current time is within valid_from and valid_until
- Check usage limits (total and per-user)
- Verify transaction amount meets minimum requirement

**Issue: Discount calculation incorrect**
- For percentage type, check max_discount cap
- For fixed type, discount cannot exceed transaction amount

---

## Future Enhancements

### Two-Factor Authentication

1. **SMS-based 2FA** - Alternative to TOTP
2. **Hardware Keys** - WebAuthn/FIDO2 support
3. **Trusted Devices** - Remember device for 30 days
4. **2FA Enforcement** - Require 2FA for high-value transactions

### Email Notifications

1. **Email Templates Editor** - Admin UI for customizing templates
2. **Email Preferences** - User control over notification types
3. **Email Analytics** - Track open rates, click rates
4. **SMS Notifications** - Alternative to email for critical alerts

### Promo Codes

1. **Referral-based Codes** - Unique codes per user
2. **Stacking Rules** - Multiple codes on single transaction
3. **Gamification** - Unlock codes through achievements
4. **Scheduled Campaigns** - Auto-activate/deactivate codes
5. **A/B Testing** - Test different code values
6. **Geolocation** - Location-based code availability

---

## Support

For questions or issues with advanced features:

- **Documentation**: Check this guide and API documentation at `/docs`
- **Logs**: Check backend logs for detailed error messages
- **Email**: support@gamingplatform.com
- **GitHub Issues**: Report bugs on the project repository

---

## Conclusion

These advanced features significantly enhance the platform's security, user engagement, and monetization capabilities:

- **2FA** provides enhanced security for user accounts
- **Email Notifications** keep users informed of all activities
- **Promo Codes** enable flexible marketing campaigns and user acquisition

All features are production-ready and fully tested. Refer to the API documentation (`/docs`) for interactive API exploration.
