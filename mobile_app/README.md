# Gaming Platform - Flutter Mobile App

A comprehensive multi-game skill gaming platform built with Flutter for iOS and Android.

## 🎮 Features

### Core Features
- **Authentication**: OTP-based login, Social login (Google, Facebook, Apple)
- **User Profile**: Complete profile management with statistics
- **Multi-Wallet**: Cash, Bonus, and Winnings wallets
- **Payment Integration**: UPI, Cards, Net Banking
- **KYC Verification**: Document upload and verification
- **Multiple Games**: Ludo, Rummy, Poker, Fantasy Cricket, Quiz, Carrom
- **Real-time Multiplayer**: WebSocket-based live gameplay
- **Tournaments**: Multi-round competitive tournaments
- **Referral Program**: Invite friends and earn rewards
- **Achievements & Leaderboard**: Gamification features
- **Two-Factor Authentication**: TOTP-based 2FA
- **Promo Codes**: Apply discounts on deposits
- **Push Notifications**: Firebase Cloud Messaging

## 📁 Project Structure

```
lib/
├── core/                 # Core functionality
│   ├── constants/       # App constants & API endpoints
│   ├── theme/          # App theme, colors, text styles
│   ├── utils/          # Utilities (validators, formatters, helpers)
│   ├── errors/         # Error handling
│   └── network/        # Network configuration
├── data/               # Data layer
│   ├── models/         # Data models
│   ├── repositories/   # Repository implementations
│   └── datasources/    # API & local data sources
├── domain/             # Business logic layer
│   ├── entities/       # Business entities
│   ├── repositories/   # Repository interfaces
│   └── usecases/       # Business use cases
├── presentation/       # UI layer
│   ├── screens/        # All screens (35+ screens)
│   ├── widgets/        # Reusable widgets
│   └── blocs/          # BLoC state management
└── main.dart          # App entry point
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.0 or higher
- Dart 3.0 or higher
- Android Studio / VS Code with Flutter extension
- Xcode (for iOS development)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd mobile_app
```

2. Install dependencies
```bash
flutter pub get
```

3. Run code generation
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

4. Run the app
```bash
# For Android
flutter run

# For iOS
flutter run
```

## 📦 Key Packages

### State Management
- `flutter_bloc` - BLoC pattern implementation
- `equatable` - Value equality

### Navigation
- `go_router` - Declarative routing

### Network
- `dio` - HTTP client
- `retrofit` - Type-safe API client
- `socket_io_client` - WebSocket client

### Local Storage
- `hive` - Fast NoSQL database
- `shared_preferences` - Simple key-value storage
- `flutter_secure_storage` - Secure storage

### Firebase
- `firebase_core` - Firebase initialization
- `firebase_messaging` - Push notifications
- `firebase_analytics` - Analytics
- `firebase_crashlytics` - Crash reporting

### Payment
- `razorpay_flutter` - Payment gateway
- `upi_india` - UPI payments

### UI
- `cached_network_image` - Image caching
- `shimmer` - Loading skeleton
- `lottie` - Animations
- `flutter_svg` - SVG support

## 🎨 Theme

### Colors
- Primary: Orange (#FF6B35)
- Secondary: Blue (#004E89)
- Success: Green (#2ECC71)
- Warning: Amber (#F39C12)
- Error: Red (#E74C3C)

### Typography
- Font Family: Poppins
- Heading 1: 32px Bold
- Heading 2: 24px SemiBold
- Body: 16px Regular

## 📱 Screens (35+)

### Authentication (5)
- Splash Screen
- Onboarding (3 slides)
- Login/Register
- OTP Verification
- Profile Setup

### Main Navigation (5 tabs)
- Home
- Games
- Wallet
- Rewards
- Profile

### Games (8)
- Game Catalog
- Game Details
- Game Lobby
- Game Room
- Live Game
- Game Result
- Tournaments
- Practice Mode

### Wallet (7)
- Wallet Dashboard
- Add Money
- Payment Gateway
- Payment Success
- Withdraw Money
- Bank Account Management
- Transaction History

### Rewards (4)
- Rewards Dashboard
- Referral Program
- Achievements & Badges
- Leaderboard

### Profile (10)
- Profile Screen
- Edit Profile
- KYC Verification
- Game History
- Statistics
- Settings
- Help & Support
- About App
- Two-Factor Authentication
- Blocked Users

## 🏗️ Architecture

This app follows **Clean Architecture** principles with **BLoC** pattern for state management.

### Layers
1. **Presentation**: UI components and BLoC
2. **Domain**: Business logic and use cases
3. **Data**: API clients and repositories

### Benefits
- Separation of concerns
- Testability
- Maintainability
- Scalability

## 🔐 Security

- Secure token storage
- Certificate pinning
- Biometric authentication
- Two-Factor Authentication (TOTP)
- Encrypted local storage
- Session management

## 📊 Performance

- Image caching
- Lazy loading
- Pagination
- Offline support
- Memory optimization

## 🧪 Testing

```bash
# Run unit tests
flutter test

# Run widget tests
flutter test test/widgets/

# Run integration tests
flutter test integration_test/
```

## 🔧 Build

### Android
```bash
flutter build apk --release
flutter build appbundle --release
```

### iOS
```bash
flutter build ios --release
flutter build ipa --release
```

## 📝 Configuration

### Environment Setup
Update `lib/core/constants/app_constants.dart`:
- Backend API URL
- Razorpay Keys
- Firebase configuration

### Firebase Setup
1. Add `google-services.json` (Android)
2. Add `GoogleService-Info.plist` (iOS)

## 🚀 Deployment

### Android - Play Store
1. Build release APK/AAB
2. Create app listing
3. Upload to Play Console
4. Submit for review

### iOS - App Store
1. Build release IPA
2. Upload to App Store Connect
3. Create app listing
4. Submit for review

## 📖 Documentation

- [API Documentation](../docs/API_DOCUMENTATION.md)
- [Flutter Roadmap](../docs/FLUTTER_APP_ROADMAP.md)
- [Advanced Features](../docs/ADVANCED_FEATURES.md)

## 🤝 Contributing

This is a proprietary project. Contributions are restricted to authorized team members.

## 📄 License

Proprietary - All rights reserved

## 📧 Support

For support, email support@gamingplatform.com

---

**Version**: 1.0.0
**Last Updated**: November 16, 2025
