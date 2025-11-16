import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

/// Theme state
class ThemeState extends Equatable {
  final ThemeMode themeMode;

  const ThemeState({required this.themeMode});

  /// Initial state with light theme
  factory ThemeState.initial() => const ThemeState(themeMode: ThemeMode.light);

  /// Copy with new theme mode
  ThemeState copyWith({ThemeMode? themeMode}) {
    return ThemeState(
      themeMode: themeMode ?? this.themeMode,
    );
  }

  @override
  List<Object?> get props => [themeMode];

  /// Check if dark mode is enabled
  bool get isDarkMode => themeMode == ThemeMode.dark;

  /// Check if light mode is enabled
  bool get isLightMode => themeMode == ThemeMode.light;

  /// Check if system mode is enabled
  bool get isSystemMode => themeMode == ThemeMode.system;
}
