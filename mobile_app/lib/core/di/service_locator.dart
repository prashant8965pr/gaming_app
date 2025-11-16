import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:hive/hive.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../data/datasources/local/game_local_datasource.dart';
import '../../data/datasources/local/user_local_datasource.dart';
import '../../data/datasources/local/wallet_local_datasource.dart';
import '../../data/datasources/remote/auth_remote_datasource.dart';
import '../../data/datasources/remote/game_remote_datasource.dart';
import '../../data/datasources/remote/user_remote_datasource.dart';
import '../../data/datasources/remote/wallet_remote_datasource.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../data/repositories/game_repository_impl.dart';
import '../../data/repositories/user_repository_impl.dart';
import '../../data/repositories/wallet_repository_impl.dart';
import '../../domain/repositories/auth_repository.dart';
import '../../domain/repositories/game_repository.dart';
import '../../domain/repositories/user_repository.dart';
import '../../domain/repositories/wallet_repository.dart';
import '../../presentation/bloc/auth/auth_bloc.dart';
import '../../presentation/bloc/user/user_bloc.dart';
import '../../presentation/bloc/wallet/wallet_bloc.dart';
import '../../presentation/bloc/game/game_bloc.dart';
import '../../presentation/bloc/theme/theme_bloc.dart';
import '../network/dio_client.dart';
import '../storage/hive_config.dart';
import '../storage/local_storage.dart';
import '../storage/secure_storage.dart';

final sl = GetIt.instance;

/// Initialize all dependencies
Future<void> initDependencies() async {
  // ============== External Dependencies ==============

  // SharedPreferences
  final sharedPreferences = await SharedPreferences.getInstance();
  sl.registerLazySingleton<SharedPreferences>(() => sharedPreferences);

  // Hive
  await HiveConfig.init();
  sl.registerLazySingleton<Box>(() => Hive.box(HiveBoxes.user));
  sl.registerLazySingleton<Box>(
    () => Hive.box(HiveBoxes.wallet),
    instanceName: 'walletBox',
  );
  sl.registerLazySingleton<Box>(
    () => Hive.box(HiveBoxes.games),
    instanceName: 'gamesBox',
  );
  sl.registerLazySingleton<Box>(
    () => Hive.box(HiveBoxes.transactions),
    instanceName: 'transactionsBox',
  );
  sl.registerLazySingleton<Box>(
    () => Hive.box(HiveBoxes.cache),
    instanceName: 'cacheBox',
  );

  // Flutter Secure Storage
  const secureStorage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
  );
  sl.registerLazySingleton<FlutterSecureStorage>(() => secureStorage);

  // ============== Core ==============

  // Storage
  sl.registerLazySingleton<SecureStorage>(
    () => SecureStorage(sl<FlutterSecureStorage>()),
  );

  sl.registerLazySingleton<LocalStorage>(
    () => LocalStorage(sl<SharedPreferences>()),
  );

  sl.registerLazySingleton<CacheHelper>(
    () => CacheHelper(sl<Box>(instanceName: 'cacheBox')),
  );

  // Network
  sl.registerLazySingleton<Dio>(() => Dio());

  sl.registerLazySingleton<DioClient>(
    () => DioClient(
      dio: sl<Dio>(),
      secureStorage: sl<SecureStorage>(),
    ),
  );

  // ============== Data Sources ==============

  // Remote Data Sources
  sl.registerLazySingleton<AuthRemoteDataSource>(
    () => AuthRemoteDataSourceImpl(sl<DioClient>().dio),
  );

  sl.registerLazySingleton<UserRemoteDataSource>(
    () => UserRemoteDataSourceImpl(sl<DioClient>().dio),
  );

  sl.registerLazySingleton<WalletRemoteDataSource>(
    () => WalletRemoteDataSourceImpl(sl<DioClient>().dio),
  );

  sl.registerLazySingleton<GameRemoteDataSource>(
    () => GameRemoteDataSourceImpl(sl<DioClient>().dio),
  );

  // Local Data Sources
  sl.registerLazySingleton<UserLocalDataSource>(
    () => UserLocalDataSourceImpl(
      sl<Box>(),
      sl<CacheHelper>(),
    ),
  );

  sl.registerLazySingleton<WalletLocalDataSource>(
    () => WalletLocalDataSourceImpl(
      sl<Box>(instanceName: 'walletBox'),
      sl<Box>(instanceName: 'transactionsBox'),
      sl<CacheHelper>(),
    ),
  );

  sl.registerLazySingleton<GameLocalDataSource>(
    () => GameLocalDataSourceImpl(
      sl<Box>(instanceName: 'gamesBox'),
      sl<CacheHelper>(),
    ),
  );

  // ============== Repositories ==============

  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(
      sl<AuthRemoteDataSource>(),
      sl<UserLocalDataSource>(),
      sl<SecureStorage>(),
    ),
  );

  sl.registerLazySingleton<UserRepository>(
    () => UserRepositoryImpl(
      sl<UserRemoteDataSource>(),
      sl<UserLocalDataSource>(),
    ),
  );

  sl.registerLazySingleton<WalletRepository>(
    () => WalletRepositoryImpl(
      sl<WalletRemoteDataSource>(),
      sl<WalletLocalDataSource>(),
    ),
  );

  sl.registerLazySingleton<GameRepository>(
    () => GameRepositoryImpl(
      sl<GameRemoteDataSource>(),
      sl<GameLocalDataSource>(),
    ),
  );

  // ============== BLoCs ==============

  // AuthBloc - Factory to create new instance each time
  sl.registerFactory<AuthBloc>(
    () => AuthBloc(authRepository: sl<AuthRepository>()),
  );

  sl.registerFactory<UserBloc>(
    () => UserBloc(userRepository: sl<UserRepository>()),
  );

  sl.registerFactory<WalletBloc>(
    () => WalletBloc(walletRepository: sl<WalletRepository>()),
  );

  sl.registerFactory<GameBloc>(
    () => GameBloc(gameRepository: sl<GameRepository>()),
  );

  sl.registerFactory<ThemeBloc>(
    () => ThemeBloc(localStorage: sl<LocalStorage>()),
  );
}
