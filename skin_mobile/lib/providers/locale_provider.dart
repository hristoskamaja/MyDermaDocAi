import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../l10n/app_strings.dart';
import '../services/locale_storage.dart';

/// EN/MK language toggle, persisted via shared_preferences - the Flutter
/// counterpart of skin_web/src/context/LanguageContext.jsx. Also mirrors
/// its choice into [LocaleStorage] so plain-Dart service classes (no
/// BuildContext) can read it too.
class LocaleProvider extends ChangeNotifier {
  static const _key = 'app_lang';

  String _lang = 'en';
  String get lang => _lang;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _lang = prefs.getString(_key) ?? 'en';
    LocaleStorage.current = _lang;
    notifyListeners();
  }

  Future<void> setLang(String lang) async {
    if (lang != 'en' && lang != 'mk') return;
    _lang = lang;
    LocaleStorage.current = lang;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, lang);
  }

  /// `context.watch<LocaleProvider>().t('home.recentScans')` - same
  /// dot-notation lookup as the web app's `t()`.
  String t(String key) => AppStrings.t(_lang, key);
}
