# Phase 8: Admin Panel/Dashboard - Implementation Plan

**Status:** 🚀 In Progress
**Start Date:** November 16, 2025
**Estimated Duration:** 3-4 sessions

---

## 📋 Overview

Phase 8 focuses on building a comprehensive admin panel for platform management. This will enable administrators to manage users, approve KYC documents, process withdrawals, monitor transactions, manage games, and view analytics.

---

## 🎯 Goals

1. **Admin Authentication** - Secure role-based access control
2. **KYC Management** - Review and approve/reject KYC documents
3. **Withdrawal Management** - Process and approve withdrawal requests
4. **User Management** - View, edit, suspend/ban users
5. **Transaction Monitoring** - Monitor all financial transactions
6. **Game Management** - Create, edit, and manage games
7. **Session Monitoring** - View and manage active game sessions
8. **Analytics Dashboard** - Key metrics and insights
9. **Promo Code Management** - Create and manage promotional codes

---

## 🏗️ Architecture

### Backend (Already Exists - Partial)

**Existing Admin Endpoints:**
```
✅ GET  /api/v1/admin/kyc/pending
✅ POST /api/v1/admin/kyc/review
✅ GET  /api/v1/admin/withdrawals/pending
✅ POST /api/v1/admin/withdrawals/review
✅ POST /api/v1/admin/withdrawals/process-payout
✅ POST /api/v1/admin/wallet/adjust-balance
```

**Need to Add:**
```
🔲 GET  /api/v1/admin/dashboard/stats
🔲 GET  /api/v1/admin/users
🔲 GET  /api/v1/admin/users/{user_id}
🔲 PUT  /api/v1/admin/users/{user_id}/status
🔲 GET  /api/v1/admin/transactions
🔲 GET  /api/v1/admin/games
🔲 POST /api/v1/admin/games
🔲 PUT  /api/v1/admin/games/{game_id}
🔲 GET  /api/v1/admin/sessions
🔲 GET  /api/v1/admin/promo-codes
🔲 POST /api/v1/admin/promo-codes
🔲 PUT  /api/v1/admin/promo-codes/{code}
```

### Frontend (To Build)

**Admin Web App Structure:**
```
frontend-admin/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (Login)
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── kyc/
│   │   │   ├── pending/
│   │   │   └── history/
│   │   ├── withdrawals/
│   │   │   ├── pending/
│   │   │   └── history/
│   │   ├── users/
│   │   │   ├── page.tsx (List)
│   │   │   └── [userId]/
│   │   ├── transactions/
│   │   ├── games/
│   │   ├── sessions/
│   │   ├── promo-codes/
│   │   └── analytics/
│   ├── components/
│   ├── lib/
│   └── types/
```

---

## 📦 Phase Breakdown

### Session 1: Backend Enhancement + Admin Auth ⏳

**1.1 Database Schema Updates**
- [ ] Add `role` field to User model (user, admin, superadmin)
- [ ] Create migration for role field
- [ ] Add admin-specific tables (if needed)
- [ ] Seed initial admin user

**1.2 Admin Authentication**
- [ ] Update security module for role-based auth
- [ ] Create admin permission decorators
- [ ] Add admin login endpoint
- [ ] Test admin authentication

**1.3 Additional Admin Endpoints**
- [ ] Dashboard statistics endpoint
- [ ] User management endpoints (list, get, update status)
- [ ] Transaction monitoring endpoints
- [ ] Analytics endpoints

### Session 2: Admin Frontend Foundation

**2.1 Project Setup**
- [ ] Create frontend-admin directory
- [ ] Initialize Next.js 14 with TypeScript
- [ ] Configure Tailwind CSS
- [ ] Set up admin-specific API client

**2.2 Admin Authentication**
- [ ] Admin login page
- [ ] Admin auth store (Zustand)
- [ ] Protected route middleware
- [ ] Admin layout with sidebar

**2.3 Admin Dashboard**
- [ ] Dashboard page with key metrics
- [ ] Stats cards (users, transactions, revenue, active sessions)
- [ ] Recent activity feed
- [ ] Quick actions panel

### Session 3: KYC & Withdrawal Management

**3.1 KYC Management**
- [ ] Pending KYC list page
- [ ] KYC review modal with document viewer
- [ ] Approve/Reject/Request Resubmit actions
- [ ] KYC history page

**3.2 Withdrawal Management**
- [ ] Pending withdrawals list
- [ ] Withdrawal review modal
- [ ] Approve/Reject actions
- [ ] Process payout with UTR entry
- [ ] Withdrawal history page

### Session 4: User & Transaction Management

**4.1 User Management**
- [ ] Users list with search and filters
- [ ] User details page
- [ ] Edit user information
- [ ] Suspend/Ban user actions
- [ ] Manual balance adjustment
- [ ] User activity log

**4.2 Transaction Monitoring**
- [ ] All transactions list
- [ ] Advanced filters (type, status, date range)
- [ ] Transaction details view
- [ ] Export functionality

### Session 5: Game & Session Management (Optional)

**5.1 Game Management**
- [ ] Games list
- [ ] Create game form
- [ ] Edit game form
- [ ] Activate/Deactivate games
- [ ] Game analytics

**5.2 Session Monitoring**
- [ ] Active sessions list
- [ ] Session details view
- [ ] Force end session
- [ ] Session history

### Session 6: Promo Codes & Analytics (Optional)

**6.1 Promo Code Management**
- [ ] Promo codes list
- [ ] Create promo code form
- [ ] Edit promo code
- [ ] Activate/Deactivate codes
- [ ] Usage statistics

**6.2 Analytics Dashboard**
- [ ] Revenue charts (daily, weekly, monthly)
- [ ] User growth charts
- [ ] Game popularity charts
- [ ] Conversion funnel
- [ ] Export reports

---

## 🛠️ Technical Stack

### Backend
- **Framework:** FastAPI (existing)
- **Database:** PostgreSQL (existing)
- **ORM:** SQLAlchemy (existing)
- **Authentication:** JWT with role-based access

### Admin Frontend
- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Charts:** Recharts / Chart.js
- **Tables:** TanStack Table (React Table)
- **Forms:** React Hook Form
- **Notifications:** React Hot Toast

---

## 🔐 Security Considerations

1. **Role-Based Access Control (RBAC)**
   - Implement strict role checks on all admin endpoints
   - Use middleware to verify admin role
   - Log all admin actions

2. **Audit Trail**
   - Log all admin actions (KYC approvals, withdrawals, user modifications)
   - Track who did what and when
   - Store IP addresses and user agents

3. **Sensitive Data Protection**
   - Mask sensitive user data where appropriate
   - Implement data access logs
   - Secure document URL access

4. **Session Management**
   - Short session timeouts for admin users
   - Force re-authentication for critical actions
   - Multi-factor authentication (future)

---

## 📊 Key Features

### 1. Dashboard
- Total users (active, suspended, banned)
- Total revenue (today, week, month, all-time)
- Pending KYC count
- Pending withdrawal count
- Active game sessions
- Recent transactions
- User registrations chart
- Revenue trend chart

### 2. KYC Management
- Pending KYC queue with priority
- Document viewer (front, back, selfie)
- One-click approve/reject
- Rejection reason templates
- Request resubmit with notes
- Verification history
- Bulk actions

### 3. Withdrawal Management
- Pending withdrawals queue
- Bank details verification
- TDS calculation display
- Approve with processing
- Reject with refund
- Mark as completed with UTR
- Payout batch processing
- Withdrawal analytics

### 4. User Management
- Search by username, email, phone
- Filter by status, KYC status, registration date
- User details overview
- Edit profile information
- Suspend/Ban with reason
- View user transactions
- View game history
- Manual balance adjustment
- Send notifications

### 5. Transaction Monitoring
- All transactions in one view
- Filter by type, status, date range, user
- Transaction details popup
- Flagged transactions
- Export to CSV/Excel
- Transaction analytics

---

## 📈 Success Metrics

| Metric | Target | Priority |
|--------|--------|----------|
| Admin Pages | 15+ | High |
| API Endpoints | 20+ | High |
| Response Time | <2s | Medium |
| Security | Role-based + Audit | Critical |
| User Management | Full CRUD | High |
| KYC Processing | <1 min avg | High |
| Withdrawal Processing | <5 min avg | High |
| Analytics Dashboard | 10+ charts | Medium |

---

## 🚀 Deployment Plan

1. **Database Migration**
   - Run migration to add role field
   - Seed initial admin users
   - Test role-based access

2. **Backend Deployment**
   - Deploy enhanced admin endpoints
   - Test all admin APIs
   - Verify security

3. **Frontend Deployment**
   - Build admin frontend
   - Deploy to subdomain (admin.platform.com)
   - Configure environment variables
   - Test production deployment

---

## 📝 Implementation Notes

### Admin User Creation
```sql
-- Create first admin user (manual SQL for now)
UPDATE users
SET role = 'admin'
WHERE username = 'admin' OR email = 'admin@platform.com';
```

### Environment Variables (.env)
```
# Admin specific
ADMIN_JWT_SECRET=different_secret_for_admin
ADMIN_SESSION_TIMEOUT=3600
ADMIN_REQUIRE_2FA=false
```

### Role Hierarchy
```
superadmin > admin > user
```

**Permissions:**
- **superadmin**: All permissions + manage admins
- **admin**: KYC, withdrawals, users, transactions, games
- **user**: Regular user permissions

---

## 🎯 Priority Order

### Must Have (MVP)
1. ✅ Admin authentication
2. ✅ Dashboard with stats
3. ✅ KYC approval workflow
4. ✅ Withdrawal approval workflow
5. ✅ User management (view, status change)
6. ✅ Transaction monitoring

### Should Have
7. ⏳ Game management
8. ⏳ Session monitoring
9. ⏳ Manual balance adjustment UI
10. ⏳ Advanced analytics

### Nice to Have
11. 📋 Promo code management
12. 📋 Bulk operations
13. 📋 Export functionality
14. 📋 Email notifications
15. 📋 Activity logs viewer

---

## 📚 Reference Documentation

- **Backend Admin API:** `backend/api/v1/admin.py`
- **User Model:** `backend/models/user.py`
- **Frontend Reference:** Phase 7 implementation
- **API Contracts:** `docs/api/API_CONTRACTS.md`

---

## ⚠️ Known Limitations

1. **Role Field Missing:** User model needs role field (will add in Session 1)
2. **Admin Seeding:** No automated admin user creation (will add)
3. **Analytics Endpoints:** Not yet implemented (will add)
4. **Audit Logging:** Basic logging only (can enhance later)
5. **2FA:** Not implemented (future enhancement)

---

## 🎓 Next Steps

1. Add role field to User model
2. Create migration and apply
3. Build additional admin API endpoints
4. Create admin frontend foundation
5. Implement KYC approval UI
6. Implement withdrawal approval UI
7. Build user management interface
8. Add analytics dashboard

---

**Phase 8 Status:** 🚀 Ready to Begin
**Estimated Completion:** Session 3-4
**Next Action:** Add role field to User model and create migration

---

**Prepared by:** Claude Code
**Date:** November 16, 2025
