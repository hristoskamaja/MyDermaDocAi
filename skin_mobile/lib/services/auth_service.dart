import '../models/user.dart';
import 'api_client.dart';

/// Handles registration, login, logout, current-user lookup and password
/// change against the `/jwt-auth/` endpoints, plus token persistence.
class AuthService {
  Future<AppUser> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final data = await ApiClient.post(
      '/jwt-auth/register/',
      {'email': email, 'password': password, 'full_name': fullName},
      auth: false,
    );
    await TokenStorage.saveTokens(
      access: data['access'] as String,
      refresh: data['refresh'] as String,
    );
    return AppUser.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<AppUser> login({
    required String email,
    required String password,
  }) async {
    final data = await ApiClient.post(
      '/jwt-auth/login/',
      {'email': email, 'password': password},
      auth: false,
    );
    await TokenStorage.saveTokens(
      access: data['access'] as String,
      refresh: data['refresh'] as String,
    );
    return AppUser.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<void> logout() async {
    final refresh = await TokenStorage.getRefreshToken();
    if (refresh != null) {
      try {
        await ApiClient.post('/jwt-auth/logout/', {'refresh': refresh});
      } catch (_) {
        // Ignore network/logout errors — clear local tokens regardless.
      }
    }
    await TokenStorage.clear();
  }

  Future<AppUser> me() async {
    final data = await ApiClient.get('/jwt-auth/me/');
    return AppUser.fromJson(data as Map<String, dynamic>);
  }

  Future<void> changePassword({
    required String oldPassword,
    required String newPassword,
  }) async {
    await ApiClient.post('/jwt-auth/change-password/', {
      'old_password': oldPassword,
      'new_password': newPassword,
    });
  }

  Future<bool> isLoggedIn() async {
    final token = await TokenStorage.getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
