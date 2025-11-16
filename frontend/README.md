# Gaming Platform - Frontend

Modern Next.js 14 web application for the Gaming Platform.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS 3.4
- **State Management:** Zustand with persistence
- **HTTP Client:** Axios
- **Forms:** React Hook Form
- **UI Icons:** Lucide React
- **Date Handling:** date-fns
- **Notifications:** React Hot Toast

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/
│   │   ├── common/            # Reusable UI components
│   │   │   ├── Alert.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Spinner.tsx
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── auth/              # Auth-specific components
│   │   ├── dashboard/         # Dashboard components
│   │   ├── games/             # Games components
│   │   ├── wallet/            # Wallet components
│   │   └── profile/           # Profile components
│   ├── lib/
│   │   └── api.ts            # API client
│   ├── store/
│   │   ├── authStore.ts      # Auth state
│   │   └── walletStore.ts    # Wallet state
│   ├── types/
│   │   └── index.ts          # TypeScript types
│   ├── utils/
│   │   ├── cn.ts             # Class utility
│   │   ├── format.ts         # Formatting functions
│   │   └── validation.ts     # Validation functions
│   └── styles/
│       └── globals.css       # Global styles
├── public/                    # Static assets
├── Configuration files
└── Package management
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Update .env.local with your API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

### Code Quality

```bash
# Run linter
npm run lint

# Type check
npm run type-check
```

## Features Implemented

### UI Components (9 components)
- ✅ Button - Multiple variants, sizes, loading states
- ✅ Card - Flexible container with header, content, footer
- ✅ Input - Form input with label, error, icons
- ✅ Modal - Dialog with backdrop and keyboard support
- ✅ Badge - Status indicators with variants
- ✅ Spinner - Loading indicators
- ✅ Avatar - User avatars with fallbacks
- ✅ Alert - Notification messages with variants
- ✅ Empty State - No data placeholders

### Layout Components (3 components)
- ✅ Header - Top navigation with user menu
- ✅ Sidebar - Side navigation menu
- ✅ Footer - Site footer with links

### Core Infrastructure
- ✅ API Client - Complete REST API integration
- ✅ Authentication Store - User auth state management
- ✅ Wallet Store - Wallet state management
- ✅ Type Definitions - 25+ TypeScript interfaces
- ✅ Utilities - Formatting and validation functions
- ✅ Global Styles - Tailwind CSS with dark mode

## Environment Variables

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_PATH=/api/v1

# App Configuration
NEXT_PUBLIC_APP_NAME="Gaming Platform"
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Create production build |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript compiler |

## Component Usage Examples

### Button

```tsx
import { Button } from '@/components/common';

<Button variant="primary" size="md">
  Click Me
</Button>

<Button variant="danger" isLoading>
  Loading...
</Button>
```

### Card

```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common';

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
</Card>
```

### Input

```tsx
import { Input } from '@/components/common';
import { Mail } from 'lucide-react';

<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  leftIcon={<Mail className="w-5 h-5" />}
  error="Invalid email"
/>
```

## API Integration

All backend endpoints are available through the API client:

```tsx
import { api } from '@/lib/api';

// Authentication
await api.login({ username, password });
await api.register({ username, email, phone, password });
const user = await api.getCurrentUser();

// Wallet
const wallets = await api.getWallets();
await api.deposit({ amount, payment_method });
await api.withdraw({ amount, wallet_type });

// Games
const games = await api.getGameCatalog();
const sessions = await api.getGameSessions('waiting');
await api.createGameSession({ game_id, entry_fee, session_type, max_players });
await api.joinGameSession({ session_code });
```

## State Management

### Auth Store

```tsx
import { useAuthStore } from '@/store/authStore';

function Component() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  // Use authentication state
}
```

### Wallet Store

```tsx
import { useWalletStore } from '@/store/walletStore';

function Component() {
  const { wallets, fetchWallets, getTotalBalance } = useWalletStore();

  useEffect(() => {
    fetchWallets();
  }, []);
}
```

## Styling

### Tailwind CSS

Custom theme with brand colors:

- **Primary:** Blue shades for main actions
- **Secondary:** Purple shades for accents
- **Success:** Green for positive actions
- **Warning:** Yellow for warnings
- **Danger:** Red for errors

### Dark Mode

Automatic dark mode support using Tailwind's dark mode classes:

```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content
</div>
```

## Development Status

**Phase 7 Progress: 40% Complete**

### Completed
- ✅ Project setup and configuration
- ✅ TypeScript types and interfaces
- ✅ API client with all endpoints
- ✅ State management (Zustand)
- ✅ Utility functions
- ✅ Common UI components (9 components)
- ✅ Layout components (3 components)
- ✅ Global styles and theming

### Remaining
- 🚧 Next.js app directory and pages
- 🚧 Authentication pages (Login, Register)
- 🚧 Dashboard page
- 🚧 Wallet pages
- 🚧 Games pages
- 🚧 Profile pages
- 🚧 Additional features pages

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting with Next.js dynamic imports
- Image optimization with Next.js Image component
- CSS purging with Tailwind CSS
- Production builds are optimized and minified

## Contributing

When adding new components:

1. Follow existing patterns
2. Use TypeScript strict mode
3. Add proper types and interfaces
4. Include JSDoc comments
5. Export from index.ts barrel files

## License

Proprietary - Gaming Platform

---

**Last Updated:** November 16, 2025
**Version:** 1.0.0 (Phase 7 - In Progress)
