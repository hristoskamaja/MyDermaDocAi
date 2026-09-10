/// Base URL for the DermaScanAI Django REST backend.
///
/// `10.0.2.2` is the special alias the Android EMULATOR uses to reach
/// `localhost` on the host machine running the Django dev server (it is
/// not a real network address — it's forwarded by the emulator).
///
/// If you are testing on a PHYSICAL phone instead of the emulator, this
/// must be changed to your computer's real LAN IP address, e.g.:
///   const String kApiBaseUrl = 'http://192.168.1.23:8000/api';
/// and:
///   1. Your phone must be connected to the same WiFi network as your
///      computer.
///   2. Django must be started with
///        python manage.py runserver 0.0.0.0:8000
///      (NOT just `runserver`) so it accepts connections from other
///      devices on the network, not only from localhost.
const String kApiBaseUrl = 'http://192.168.1.224:8000/api';

/// Resolves a possibly-relative media path (e.g. the `image` field on an
/// analysis, like `/media/analyses/xyz.png`) into a fully-qualified URL
/// by stripping the `/api` suffix from [kApiBaseUrl] and prefixing it.
String resolveMediaUrl(String path) {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  final host = kApiBaseUrl.replaceFirst(RegExp(r'/api/?$'), '');
  return '$host$path';
}
