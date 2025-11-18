import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'core/di/service_locator.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'presentation/blocs/auth/auth_bloc.dart';
import 'presentation/blocs/wallet/wallet_bloc.dart';
import 'presentation/blocs/game/game_bloc.dart';
import 'presentation/blocs/chat/chat_bloc.dart';
import 'presentation/blocs/tournament/tournament_bloc.dart';
import 'presentation/blocs/token/token_bloc.dart';
import 'presentation/blocs/friends/friends_bloc.dart';
import 'presentation/blocs/rewards/rewards_bloc.dart';
import 'presentation/blocs/kyc/kyc_bloc.dart';

void main() async {
  // Ensure Flutter binding is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize dependency injection
  await initDependencies();

  // Set preferred orientations (portrait only)
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  // TODO: Initialize Firebase
  // await Firebase.initializeApp(
  //   options: DefaultFirebaseOptions.currentPlatform,
  // );

  // TODO: Initialize Firebase Crashlytics
  // FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

  // TODO: Initialize Firebase Messaging
  // await _initializeFirebaseMessaging();

  // Run the app
  runApp(const MyApp());
}

/// Main app widget
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (_) => sl<AuthBloc>(),
        ),
        BlocProvider<WalletBloc>(
          create: (_) => sl<WalletBloc>(),
        ),
        BlocProvider<GameBloc>(
          create: (_) => sl<GameBloc>(),
        ),
        BlocProvider<ChatBloc>(
          create: (_) => sl<ChatBloc>(),
        ),
        BlocProvider<TournamentBloc>(
          create: (_) => sl<TournamentBloc>(),
        ),
        BlocProvider<TokenBloc>(
          create: (_) => sl<TokenBloc>(),
        ),
        BlocProvider<FriendsBloc>(
          create: (_) => sl<FriendsBloc>(),
        ),
        BlocProvider<RewardsBloc>(
          create: (_) => sl<RewardsBloc>(),
        ),
        BlocProvider<KycBloc>(
          create: (_) => sl<KycBloc>(),
        ),
      ],
      child: MaterialApp.router(
        title: AppConstants.appName,
        debugShowCheckedModeBanner: false,

        // Theme
        theme: AppTheme.lightTheme(),
        darkTheme: AppTheme.darkTheme(),
        themeMode: ThemeMode.system,

        // Router
        routerConfig: AppRouter.router,

        // Locale
        locale: const Locale('en', 'IN'),
        supportedLocales: const [
          Locale('en', 'IN'),
          Locale('hi', 'IN'),
        ],

        // Builder for responsive design
        builder: (context, child) {
          return MediaQuery(
            data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
            child: child!,
          );
        },
      ),
    );
  }
}

/// Initialize Firebase Cloud Messaging
Future<void> _initializeFirebaseMessaging() async {
  // TODO: Implement Firebase Messaging initialization
  // final messaging = FirebaseMessaging.instance;

  // Request permission
  // final settings = await messaging.requestPermission(
  //   alert: true,
  //   announcement: false,
  //   badge: true,
  //   carPlay: false,
  //   criticalAlert: false,
  //   provisional: false,
  //   sound: true,
  // );

  // Get FCM token
  // final token = await messaging.getToken();
  // print('FCM Token: $token');

  // Handle foreground messages
  // FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  //   print('Got a message whilst in the foreground!');
  //   print('Message data: ${message.data}');

  //   if (message.notification != null) {
  //     print('Message also contained a notification: ${message.notification}');
  //     // TODO: Show local notification
  //   }
  // });

  // Handle background messages
  // FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  // Handle notification taps
  // FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
  //   print('A new onMessageOpenedApp event was published!');
  //   // TODO: Navigate to appropriate screen
  // });
}

/// Firebase background message handler
// @pragma('vm:entry-point')
// Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
//   await Firebase.initializeApp();
//   print('Handling a background message: ${message.messageId}');
// }
