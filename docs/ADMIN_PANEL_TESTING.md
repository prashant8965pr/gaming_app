# Admin Panel Testing Guide

This guide will help you test all features of the admin panel.

---

## Prerequisites

Before testing, ensure you have:
- ✅ Backend running on `http://localhost:8000`
- ✅ Database with migrations applied
- ✅ At least one admin user created
- ✅ Frontend admin panel running on `http://localhost:3001`

---

## 1. Environment Setup

### Step 1.1: Verify Backend is Running

```bash
# Check if backend is accessible
curl http://localhost:8000/api/v1/health
# Should return: {"status":"ok"}
```

### Step 1.2: Create Admin User

If you don't have an admin user yet:

**Option A: SQL Update**
```sql
-- Update existing user to admin
UPDATE users SET role = 'admin' WHERE username = 'testuser';

-- Or create new admin user (if you have a user already)
-- First register via the main frontend, then:
UPDATE users SET role = 'admin' WHERE email = 'admin@test.com';
```

**Option B: Create via Backend Console**
```bash
cd backend

# Start Python shell
python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
import os

# Get database URL from environment
db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/gaming_db')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Find user and make admin
user = session.query(User).filter_by(username='testuser').first()
if user:
    user.role = 'admin'
    session.commit()
    print(f'User {user.username} is now an admin')
else:
    print('User not found')
"
```

### Step 1.3: Setup Frontend Environment

```bash
cd frontend-admin

# Create .env.local if not exists
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

The admin panel should now be running at: http://localhost:3001

---

## 2. Test Admin Authentication

### Test 2.1: Login Flow

1. **Navigate to Admin Panel**
   - Open: http://localhost:3001
   - You should see the login page

2. **Test Login**
   - Enter admin username
   - Enter password
   - Click "Sign In"
   - Should redirect to dashboard

3. **Verify Token Storage**
   - Open browser DevTools (F12)
   - Go to Application → Local Storage
   - Check for: `admin_token` and `admin-auth-storage`

4. **Test Protected Routes**
   - Try navigating to: http://localhost:3001/dashboard
   - Should stay on dashboard (not redirect to login)

5. **Test Logout**
   - Click logout button in sidebar
   - Should redirect to login page
   - Token should be cleared from localStorage

**Expected Results:**
- ✅ Login successful with valid credentials
- ✅ Dashboard loads with statistics
- ✅ Sidebar shows navigation links
- ✅ Logout clears session

---

## 3. Test Dashboard Statistics

### Test 3.1: Dashboard Load

1. **Navigate to Dashboard**
   - Click "Dashboard" in sidebar
   - Or go to: http://localhost:3001/dashboard

2. **Verify Statistics Cards**
   - Should see stats cards:
     - Total Users
     - Active Users
     - Total Revenue
     - Active Sessions
   - Check if numbers are displaying correctly

3. **Verify Secondary Stats**
   - Pending KYC count
   - Pending Withdrawals count
   - Today's Deposits
   - Today's Withdrawals

4. **Test Action Cards**
   - Click "View all →" on each action card
   - Should navigate to respective pages

**Expected Results:**
- ✅ All statistics load without errors
- ✅ Numbers are displayed correctly
- ✅ Action cards navigate to correct pages
- ✅ No console errors

---

## 4. Test KYC Management

### Test 4.1: KYC List View

1. **Navigate to KYC Management**
   - Click "KYC Approval" in sidebar
   - Or go to: http://localhost:3001/dashboard/kyc

2. **Verify KYC List**
   - Check if pending KYC documents are listed
   - Verify document information displays correctly
   - Check status badges

### Test 4.2: KYC Review Modal

1. **Open Review Modal**
   - Click "Review" button on any KYC document
   - Modal should open

2. **Verify Document Display**
   - User information should be visible
   - Document images should load (if URLs are valid)
   - Document type and number displayed

3. **Test Approval**
   - Select "Approve" action
   - Add optional admin notes
   - Click "Submit Review"
   - Should show success message
   - Document should disappear from pending list

4. **Test Rejection**
   - Open another document for review
   - Select "Reject" action
   - Enter rejection reason (required)
   - Add optional admin notes
   - Click "Submit Review"
   - Should show success message

5. **Test Request Resubmit**
   - Select "Request Resubmit" action
   - Enter reason (required)
   - Submit
   - Should show success message

**Expected Results:**
- ✅ KYC list loads correctly
- ✅ Modal opens and displays document info
- ✅ All three actions work correctly
- ✅ Rejection reason is required
- ✅ Success messages appear
- ✅ List refreshes after action

**Note:** If you don't have KYC documents in the database, you'll see "No pending KYC documents" message. This is expected.

---

## 5. Test Withdrawal Management

### Test 5.1: Withdrawals List View

1. **Navigate to Withdrawals**
   - Click "Withdrawals" in sidebar
   - Or go to: http://localhost:3001/dashboard/withdrawals

2. **Verify Withdrawal List**
   - Check if pending withdrawals are listed
   - Verify amount and bank details display
   - Check status badges
   - Verify stats cards (pending count, total amount)

### Test 5.2: Withdrawal Review Modal

1. **Open Review Modal**
   - Click "Review" button on any withdrawal
   - Modal should open

2. **Verify Amount Breakdown**
   - Requested Amount displayed
   - TDS amount shown
   - Processing fee shown
   - Final amount calculated correctly

3. **Verify Bank Details**
   - Account holder name
   - Account number
   - IFSC code
   - Bank name

4. **Test Approval**
   - Select "Approve" action
   - Add optional admin notes
   - Click "Submit Review"
   - Should change status to "processing"

5. **Test Completion**
   - For a withdrawal in "processing" status
   - Select "Mark as Completed"
   - Enter UTR number (required)
   - Submit
   - Should show success message

6. **Test Rejection**
   - Select "Reject" action
   - Enter rejection reason (required)
   - Submit
   - Should show success message
   - Amount should be refunded to user

**Expected Results:**
- ✅ Withdrawals list loads correctly
- ✅ Amount breakdown is accurate
- ✅ Bank details display correctly
- ✅ Approve → Processing workflow works
- ✅ Complete with UTR works
- ✅ Rejection with refund works

**Note:** If no withdrawals exist, you'll see "No pending withdrawals" message.

---

## 6. Test User Management

### Test 6.1: Users List View

1. **Navigate to Users**
   - Click "Users" in sidebar
   - Or go to: http://localhost:3001/dashboard/users

2. **Verify User List**
   - Users should be listed
   - User information displayed correctly
   - Status badges showing
   - Total count displayed

3. **Test Search**
   - Enter username in search box
   - List should filter in real-time
   - Try searching by email
   - Try searching by phone

4. **Test Filters**
   - Select "Active" from status filter
   - List should update
   - Select "Verified" from KYC status filter
   - List should update
   - Clear filters

5. **Test Pagination**
   - If more than 50 users exist:
   - Click "Next" button
   - Should load next page
   - Click "Previous" button
   - Should go back

### Test 6.2: User Details View

1. **Open User Details**
   - Click "View" button on any user
   - Should navigate to user details page

2. **Verify Profile Information**
   - Username, email, phone displayed
   - Date of birth, referral code shown
   - City, state, pincode visible (if available)

3. **Verify Account Status**
   - Status badge displayed
   - KYC status badge
   - Email/Phone verification status
   - Member since date
   - Last login date

4. **Verify Gaming Statistics**
   - Games played count
   - Games won count
   - Total winnings amount
   - Total spent amount
   - Level and experience points

5. **Verify Wallet Balances**
   - Each wallet type displayed
   - Balances shown correctly
   - Total balance calculated

6. **Verify Recent Transactions**
   - Transaction list displayed
   - Type, amount, status shown
   - Timestamps visible

### Test 6.3: User Status Management

1. **Open Status Change Modal**
   - Click "Change Status" button
   - Modal should open

2. **Test Status Change to Active**
   - Select "Active" button
   - Click "Update Status"
   - Should show success message
   - Status badge should update

3. **Test Status Change to Suspended**
   - Click "Change Status" again
   - Select "Suspended" button
   - Submit
   - Should update

4. **Test Status Change to Banned**
   - Select "Banned" button
   - Submit
   - Should update

5. **Verify Superadmin Protection**
   - If testing with a superadmin user
   - Status change should be blocked

**Expected Results:**
- ✅ User list loads and displays correctly
- ✅ Search works in real-time
- ✅ Filters update the list
- ✅ Pagination works (if applicable)
- ✅ User details page shows all information
- ✅ Status change works correctly
- ✅ Success messages appear
- ✅ Back button navigates correctly

---

## 7. Test Responsive Design

### Test 7.1: Desktop View (1920x1080)
- Dashboard grid should show 4 columns
- Sidebar fully visible
- All text readable
- No horizontal scroll

### Test 7.2: Tablet View (768x1024)
- Dashboard grid should show 2 columns
- Sidebar visible
- Cards stack appropriately

### Test 7.3: Mobile View (375x667)
- Dashboard grid shows 1 column
- Sidebar may need toggle (if implemented)
- All features accessible
- Touch targets adequate

**Test in Chrome DevTools:**
- Press F12 → Click device toolbar icon
- Test different screen sizes
- Verify all pages are responsive

---

## 8. Test Dark Mode

### Test 8.1: Enable Dark Mode

1. **Check System Preference**
   - Admin panel should follow system dark mode
   - On Windows: Settings → Personalization → Colors → Dark
   - On Mac: System Preferences → General → Appearance → Dark

2. **Verify Dark Mode Styling**
   - Background should be dark (gray-900)
   - Text should be light (white/gray-100)
   - Cards should have dark backgrounds
   - Borders should be visible
   - All components properly styled

**Expected Results:**
- ✅ Dark mode applies throughout
- ✅ Text is readable
- ✅ No light-colored elements
- ✅ Smooth transitions

---

## 9. Error Handling Tests

### Test 9.1: Network Errors

1. **Stop Backend**
   ```bash
   # Stop the backend server
   ```

2. **Try Loading Dashboard**
   - Should show loading spinner
   - Then show error or empty state

3. **Try Performing Actions**
   - Should show error toast messages

4. **Restart Backend**
   - Features should work again

### Test 9.2: Invalid Data

1. **Test Form Validation**
   - Try submitting KYC review without rejection reason
   - Should show error message
   - Try completing withdrawal without UTR
   - Should show error message

2. **Test Empty States**
   - If no KYC documents exist
   - Should show "No pending KYC documents"
   - If no withdrawals exist
   - Should show "No pending withdrawals"

**Expected Results:**
- ✅ Appropriate error messages
- ✅ Form validation works
- ✅ Empty states display correctly
- ✅ No crashes or blank screens

---

## 10. Performance Tests

### Test 10.1: Load Times

1. **Dashboard Load**
   - Should load within 2 seconds
   - Statistics should appear quickly

2. **User List Load**
   - Should load first 50 users quickly
   - Pagination should be smooth

3. **Modal Opening**
   - Modals should open instantly
   - No lag or delays

### Test 10.2: Real-time Updates

1. **Perform Action**
   - Approve a KYC document
   - List should refresh automatically

2. **Multiple Tabs**
   - Open admin panel in two tabs
   - Perform action in one tab
   - Refresh other tab to see update

**Expected Results:**
- ✅ Pages load quickly
- ✅ No performance issues
- ✅ Smooth interactions

---

## 11. Browser Compatibility

Test the admin panel in:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)

All features should work in all browsers.

---

## 12. Console & Network Check

### Test 12.1: Console Errors

1. **Open Browser DevTools (F12)**
2. **Go to Console Tab**
3. **Navigate through all pages**
4. **Check for errors**

**Expected:**
- No red errors (warnings are okay)
- No CORS errors
- No 404s for resources

### Test 12.2: Network Requests

1. **Open Network Tab in DevTools**
2. **Perform actions**
3. **Verify API calls**

**Check:**
- ✅ API calls go to correct endpoints
- ✅ Status codes are 200 for success
- ✅ Request payloads are correct
- ✅ Response data is valid

---

## Troubleshooting Guide

### Issue: Cannot Login

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check user has admin role: `SELECT role FROM users WHERE username = 'youruser';`
3. Check browser console for errors
4. Verify API URL in `.env.local`

### Issue: Dashboard Shows No Stats

**Solution:**
1. Check if API endpoint returns data:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/admin/dashboard/stats
   ```
2. Verify you have an admin token in localStorage
3. Check browser console for errors

### Issue: KYC/Withdrawals Not Loading

**Solution:**
1. Verify endpoint:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/admin/kyc/pending
   ```
2. Check if documents exist in database
3. Verify admin permissions

### Issue: Images Not Loading

**Solution:**
1. Check if image URLs are valid
2. Verify CORS settings on backend
3. Check if images are publicly accessible

### Issue: 403 Forbidden Errors

**Solution:**
1. Verify user has admin role
2. Check token is valid and not expired
3. Verify `is_admin` property works in User model

---

## Test Checklist

Use this checklist to track your testing:

### Authentication
- [ ] Login with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Token stored in localStorage
- [ ] Protected routes work
- [ ] Logout clears session

### Dashboard
- [ ] All stat cards load
- [ ] Numbers display correctly
- [ ] Action cards navigate correctly
- [ ] No console errors

### KYC Management
- [ ] KYC list loads
- [ ] Review modal opens
- [ ] Approve action works
- [ ] Reject action works
- [ ] Request resubmit works
- [ ] Rejection reason required

### Withdrawal Management
- [ ] Withdrawals list loads
- [ ] Review modal opens
- [ ] Amount breakdown correct
- [ ] Approve action works
- [ ] Complete with UTR works
- [ ] Reject with refund works

### User Management
- [ ] Users list loads
- [ ] Search works
- [ ] Filters work
- [ ] Pagination works (if applicable)
- [ ] User details page loads
- [ ] All user info displays
- [ ] Status change works

### General
- [ ] Responsive design works
- [ ] Dark mode works
- [ ] Error handling works
- [ ] No console errors
- [ ] Performance is good

---

## Next Steps After Testing

If all tests pass:
1. ✅ Admin panel is ready for production
2. Consider deploying to staging environment
3. Create admin user accounts for actual admins
4. Configure production environment variables

If tests fail:
1. Note which features don't work
2. Check backend logs for errors
3. Verify database has correct data
4. Review API responses in browser DevTools

---

**Happy Testing! 🎉**

If you encounter any issues, check the troubleshooting section or review the console/network logs for more details.
