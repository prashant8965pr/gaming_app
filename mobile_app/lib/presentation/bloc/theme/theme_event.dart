import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

/// Base class for all theme events
abstract class ThemeEvent extends Equatable {
  const ThemeEvent();

  @override
  List<Object?> get props => [];
}

/// Event to change theme mode
class ChangeThemeModeEvent extends ThemeEvent {
  final ThemeMode themeMode;

  const ChangeThemeModeEvent({required this.themeMode});

  @override
  List<Object?> get props => [themeMode];
}

/// Event to toggle theme (light/dark)
class ToggleThemeEvent extends ThemeEvent {
  const ToggleThemeEvent();
}

/// Event to load saved theme
class LoadSavedThemeEvent extends ThemeEvent {
  const LoadSavedThemeEvent();
}
