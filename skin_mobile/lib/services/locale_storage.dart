/// Tiny in-memory holder for the current UI language ('en'/'mk'), so
/// [ApiClient] (a plain static class with no BuildContext) can attach a
/// `?lang=` query param to every request without needing Provider. Kept in
/// sync by LocaleProvider (which also persists the choice via
/// shared_preferences and reloads it on app start).
class LocaleStorage {
  static String current = 'en';
}
