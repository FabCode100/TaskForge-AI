import 'package:flutter/material.dart';

class ForgeTheme {
  static const Color forgeOrange = Color(0xFFFF6A00);
  static const Color forgeGray = Color(0xFF1F1F1F);
  static const Color forgeGrayLight = Color(0xFF2A2A2A);

  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: forgeGray,
    primaryColor: forgeOrange,
    colorScheme: ColorScheme.dark(
      primary: forgeOrange,
      secondary: forgeOrange,
      surface: forgeGrayLight,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: forgeGrayLight,
      elevation: 1,
    ),
    cardTheme: CardThemeData(
      color: forgeGrayLight,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: forgeOrange,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    ),
    textTheme: const TextTheme(
      titleLarge: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
      bodyMedium: TextStyle(color: Colors.white70),
    ),
  );

  static final ThemeData lightTheme = darkTheme.copyWith(brightness: Brightness.light);
}
