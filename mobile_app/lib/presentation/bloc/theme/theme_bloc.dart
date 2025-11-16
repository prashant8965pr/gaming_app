import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/storage/local_storage.dart';
import 'theme_event.dart';
import 'theme_state.dart';

class ThemeBloc extends Bloc<ThemeEvent, ThemeState> {
  final LocalStorage _localStorage;

  ThemeBloc({required LocalStorage localStorage})
      : _localStorage = localStorage,
        super(ThemeState.initial()) {
    on<ChangeThemeModeEvent>(_onChangeThemeMode);
    on<ToggleThemeEvent>(_onToggleTheme);
    on<LoadSavedThemeEvent>(_onLoadSavedTheme);
  }

  Future<void> _onChangeThemeMode(
    ChangeThemeModeEvent event,
    Emitter<ThemeState> emit,
  ) async {
    emit(state.copyWith(themeMode: event.themeMode));
    await _localStorage.setThemeMode(_themeModeToString(event.themeMode));
  }

  Future<void> _onToggleTheme(
    ToggleThemeEvent event,
    Emitter<ThemeState> emit,
  ) async {
    final newThemeMode = state.isDarkMode ? ThemeMode.light : ThemeMode.dark;
    emit(state.copyWith(themeMode: newThemeMode));
    await _localStorage.setThemeMode(_themeModeToString(newThemeMode));
  }

  Future<void> _onLoadSavedTheme(
    LoadSavedThemeEvent event,
    Emitter<ThemeState> emit,
  ) async {
    final themeModeString = _localStorage.getThemeMode();
    final themeMode = _stringToThemeMode(themeModeString);
    emit(state.copyWith(themeMode: themeMode));
  }

  /// Convert ThemeMode to string
  String _themeModeToString(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light:
        return 'light';
      case ThemeMode.dark:
        return 'dark';
      case ThemeMode.system:
        return 'system';
    }
  }

  /// Convert string to ThemeMode
  ThemeMode _stringToThemeMode(String mode) {
    switch (mode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
        return ThemeMode.system;
      default:
        return ThemeMode.light;
    }
  }
}
