# Admin Panel Quick Start Guide

Get the admin panel up and running in 5 minutes!

---

## Prerequisites

- Node.js 18+ installed
- Backend running on `http://localhost:8000`
- Database with migrations applied
- At least one admin user

---

## Quick Setup

### Step 1: Install Dependencies

```bash
cd frontend-admin
npm install
```

### Step 2: Verify Environment

The `.env.local` file should already exist with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Step 3: Start Development Server

```bash
npm run dev
```

The admin panel will start at: **http://localhost:3001**

### Step 4: Create Admin User

If you don't have an admin user yet:

**Option A: Quick SQL (Recommended)**
```sql
-- Replace 'yourusername' with an actual username from your database
UPDATE users SET role = 'admin' WHERE username = 'yourusername';
```

**Option B: Use the SQL script**
```bash
# Edit scripts/create_admin_user.sql and run it
```

### Step 5: Login

1. Open http://localhost:3001
2. Enter your admin username and password
3. Click "Sign In"
4. You should see the dashboard!

---

## Testing Features

### Quick Test Checklist

1. **Login** ✅
   - Navigate to http://localhost:3001
   - Login with admin credentials
   - Should redirect to dashboard

2. **Dashboard** ✅
   - Check statistics cards load
   - Verify numbers are displayed
   - Click action cards

3. **KYC Management** ✅
   - Go to KYC Approval
   - View pending documents (if any)
   - Test review modal

4. **Withdrawals** ✅
   - Go to Withdrawals
   - View pending requests (if any)
   - Test review modal

5. **Users** ✅
   - Go to Users
   - Search for users
   - View user details
   - Test status change

---

## Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

---

## Troubleshooting

### Cannot Login

**Check:**
1. Is backend running? `curl http://localhost:8000/health`
2. Does user have admin role? `SELECT role FROM users WHERE username = 'youruser';`
3. Is API URL correct in `.env.local`?

### Dashboard Shows No Stats

**Check:**
1. Open browser console (F12)
2. Look for API errors
3. Verify token in LocalStorage
4. Check backend logs

### 403 Forbidden Errors

**Solution:**
User doesn't have admin role. Run:
```sql
UPDATE users SET role = 'admin' WHERE username = 'yourusername';
```

---

## Production Deployment

### Build for Production

```bash
npm run build
npm start
```

### Environment Variables

For production, update `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

## Next Steps

1. ✅ Test all features (see ADMIN_PANEL_TESTING.md)
2. Create additional admin users
3. Configure production environment
4. Set up monitoring and logging

---

## Support

For detailed testing instructions, see:
- `docs/ADMIN_PANEL_TESTING.md` - Comprehensive testing guide
- `frontend-admin/README.md` - Full documentation
- `docs/PHASE_8_COMPLETE.md` - Feature list

---

**Ready to test!** 🚀

Open http://localhost:3001 and start managing your platform!
