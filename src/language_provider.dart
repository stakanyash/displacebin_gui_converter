import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:ui';
import 'lang.dart';

class LanguageProvider extends ChangeNotifier {
  String _currentLanguage = "en"; // Язык по умолчанию
  Map<String, String> _localizedStrings = {};

  LanguageProvider();

  String get currentLanguage => _currentLanguage;
  Map<String, String> get localizedStrings => _localizedStrings;

  Future<void> loadSavedLanguage() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? savedLanguage = prefs.getString("language");

    if (savedLanguage != null) {
      setLanguage(savedLanguage);
    } else {
      detectAndSetLanguage(); // Если языка нет — определяем по системе
    }
  }

  void detectAndSetLanguage() {
    String systemLocale = PlatformDispatcher.instance.locale.languageCode;

    if (lang.containsKey(systemLocale)) {
      setLanguage(systemLocale);
    } else {
      setLanguage("en"); // Если язык не поддерживается, ставим английский
    }
  }

  Future<void> setLanguage(String langCode) async {
    if (!lang.containsKey(langCode)) return;

    _currentLanguage = langCode;
    _localizedStrings = lang[langCode]!;
    notifyListeners();

    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString("language", langCode);
  }
}
