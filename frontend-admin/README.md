# Gaming Platform - Admin Panel

Admin panel for managing the gaming platform. Built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

### Implemented ✅
- **Dashboard** - Platform statistics and key metrics
- **User Management** - View, search, and manage users
- **KYC Management** - Review and approve KYC documents
- **Withdrawal Management** - Process withdrawal requests
- **Admin Authentication** - Secure role-based access control

### Coming Soon 🚧
- Transaction monitoring
- Game management
- Session management
- Analytics and reports
- Promo code management

## 📋 Tech Stack

- **Framework:** Next.js 14.0.4 (App Router)
- **Language:** TypeScript 5.3.3
- **Styling:** Tailwind CSS 3.4.0
- **State Management:** Zustand 4.4.7
- **HTTP Client:** Axios 1.6.2
- **Forms:** React Hook Form 7.49.2
- **Notifications:** React Hot Toast 2.4.1
- **Icons:** Lucide React 0.298.0
- **Charts:** Recharts 2.10.3
- **Tables:** TanStack Table 8.11.2

## 🏗️ Project Structure

```
frontend-admin/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Login page
│   │   └── dashboard/          # Protected dashboard
│   │       ├── layout.tsx      # Dashboard layout with sidebar
│   │       ├── page.tsx        # Dashboard home
│   │       ├── users/          # User management
│   │       ├── kyc/            # KYC approval
│   │       └── withdrawals/    # Withdrawal processing
│   ├── components/
│   │   ├── common/             # Reusable UI components
│   │   └── layout/             # Layout components
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Utility functions
│   ├── store/
│   │   └── authStore.ts        # Auth state management
│   ├── types/
│   │   └── index.ts            # TypeScript definitions
│   └── styles/
│       └── globals.css         # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend-admin
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Update `.env.local`:**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3001](http://localhost:3001)

### Build for Production

```bash
npm run build
npm start
```

## 🔐 Authentication

### Admin User Setup

Before logging in, you need to create an admin user in the database:

**Option 1: SQL Update (Manual)**
```sql
UPDATE users
SET role = 'admin'
WHERE username = 'your_username';
```

**Option 2: Via Backend Console**
```python
# Run the migration first
alembic upgrade head

# Then update a user's role
python -c "
from sqlalchemy import create_engine, update
from models.user import User
engine = create_engine('your_database_url')
with engine.connect() as conn:
    conn.execute(
        update(User).where(User.username == 'admin').values(role='admin')
    )
    conn.commit()
"
```

**Option 3: Seed Script (Recommended for Development)**
Create a seed script to set up initial admin users.

### Login

1. Navigate to http://localhost:3001
2. Enter admin username and password
3. You'll be redirected to the dashboard

### Roles

- **superadmin**: Full access + admin management
- **admin**: Full access to platform management
- **user**: Regular users (no admin access)

## 📡 API Integration

The admin panel connects to these backend endpoints:

### Authentication
- `POST /api/v1/auth/login` - Admin login
- `GET /api/v1/auth/me` - Get current user

### Dashboard
- `GET /api/v1/admin/dashboard/stats` - Dashboard statistics

### User Management
- `GET /api/v1/admin/users` - List users (with filters)
- `GET /api/v1/admin/users/:id` - User details
- `PUT /api/v1/admin/users/:id/status` - Update user status

### KYC Management
- `GET /api/v1/admin/kyc/pending` - Pending KYC documents
- `POST /api/v1/admin/kyc/review` - Review KYC

### Withdrawal Management
- `GET /api/v1/admin/withdrawals/pending` - Pending withdrawals
- `POST /api/v1/admin/withdrawals/review` - Review withdrawal
- `POST /api/v1/admin/withdrawals/process-payout` - Process payout

### Balance Adjustment
- `POST /api/v1/admin/wallet/adjust-balance` - Manual balance adjustment

## 🎨 UI Components

### Common Components
- **Button** - Customizable button with variants and loading states
- **Card** - Container component with header and content sections
- **Badge** - Status badges with color variants

### Layout Components
- **Sidebar** - Navigation sidebar with user info
- **Dashboard Layout** - Protected layout wrapper

## 🔧 Development

### Adding New Pages

1. Create page in `src/app/dashboard/`:
   ```tsx
   'use client';

   export default function NewPage() {
     return <div>New Page</div>;
   }
   ```

2. Add route to sidebar navigation in `src/components/layout/Sidebar.tsx`

### Adding API Endpoints

1. Add type definitions in `src/types/index.ts`
2. Add method in `src/lib/api.ts`
3. Use in components via the api singleton

### Styling

- Uses Tailwind CSS utility classes
- Dark mode support via `dark:` prefix
- Custom color palette in `tailwind.config.ts`
- Global styles in `src/styles/globals.css`

## 📊 Dashboard Metrics

The dashboard displays:

- **User Stats**: Total, active, new today, suspended
- **KYC Stats**: Pending, approved
- **Withdrawal Stats**: Pending count and amount
- **Transaction Stats**: Deposits/withdrawals today, total revenue
- **Session Stats**: Active game sessions

## 🔒 Security

- Role-based access control (RBAC)
- JWT token authentication
- Automatic logout on 401 responses
- Protected routes via layout
- Admin-only access validation

## 🚀 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project to Vercel
3. Set environment variables
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

### Build & Run

```bash
docker build -t admin-panel .
docker run -p 3001:3001 admin-panel
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `Gaming Platform Admin` |
| `NEXT_PUBLIC_APP_VERSION` | App version | `1.0.0` |

## 🐛 Troubleshooting

### Issue: Cannot login
- Ensure backend is running
- Check user has `admin` or `superadmin` role
- Verify API URL in `.env.local`

### Issue: 404 errors
- Check API endpoint paths match backend
- Verify CORS is enabled on backend

### Issue: Dashboard not loading
- Check browser console for errors
- Verify API token is valid
- Check network tab for failed requests

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand](https://docs.pmnd.rs/zustand)
- [React Hook Form](https://react-hook-form.com/)

## 👥 Contributors

Built by Claude Code for the Gaming Platform project.

## 📄 License

Proprietary - Gaming Platform Admin Panel
