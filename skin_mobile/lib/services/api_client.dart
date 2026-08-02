import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'api_config.dart';

/// Thrown whenever the API returns a non-2xx status code, or when the
/// request fails at the network layer.
class ApiException implements Exception {
  final int? statusCode;
  final String message;
  final dynamic body;

  ApiException(this.message, {this.statusCode, this.body});

  @override
  String toString() => message;
}

/// Persists and retrieves the JWT access/refresh tokens.
class TokenStorage {
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  static Future<void> saveTokens({
    required String access,
    required String refresh,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, access);
    await prefs.setString(_refreshKey, refresh);
  }

  static Future<void> saveAccessToken(String access) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, access);
  }

  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessKey);
  }

  static Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshKey);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessKey);
    await prefs.remove(_refreshKey);
  }
}

/// Thin HTTP wrapper around the DermaScanAI Django REST API.
///
/// Handles: base URL prefixing, JSON encode/decode, attaching the
/// `Authorization: Bearer <access>` header for authenticated requests,
/// and throwing [ApiException] on non-2xx responses or network errors.
class ApiClient {
  static Uri _uri(String path) => Uri.parse('$kApiBaseUrl$path');

  static Future<Map<String, String>> _headers({
    required bool auth,
    bool json = true,
  }) async {
    final headers = <String, String>{};
    if (json) headers['Content-Type'] = 'application/json';
    headers['Accept'] = 'application/json';
    if (auth) {
      final token = await TokenStorage.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  static dynamic _decode(http.Response response) {
    if (response.body.isEmpty) return null;
    try {
      return jsonDecode(response.body);
    } catch (_) {
      return response.body;
    }
  }

  static dynamic _handle(http.Response response) {
    final decoded = _decode(response);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }
    String message = 'Request failed (${response.statusCode}).';
    if (decoded is Map<String, dynamic>) {
      message = (decoded['detail'] ??
              decoded['error'] ??
              decoded['message'] ??
              _firstFieldError(decoded) ??
              message)
          .toString();
    }
    throw ApiException(message, statusCode: response.statusCode, body: decoded);
  }

  static String? _firstFieldError(Map<String, dynamic> decoded) {
    for (final entry in decoded.entries) {
      final value = entry.value;
      if (value is List && value.isNotEmpty) {
        return '${entry.key}: ${value.first}';
      }
      if (value is String) {
        return '${entry.key}: $value';
      }
    }
    return null;
  }

  static Future<dynamic> get(String path, {bool auth = true}) async {
    try {
      final response = await http
          .get(_uri(path), headers: await _headers(auth: auth))
          .timeout(const Duration(seconds: 30));
      return _handle(response);
    } on ApiException {
      rethrow;
    } on SocketException {
      throw ApiException(
        'Could not reach the server. Check your connection and the API base URL.',
      );
    } catch (e) {
      throw ApiException('Something went wrong: $e');
    }
  }

  static Future<dynamic> post(
    String path,
    Map<String, dynamic> body, {
    bool auth = true,
  }) async {
    try {
      final response = await http
          .post(
            _uri(path),
            headers: await _headers(auth: auth),
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 30));
      return _handle(response);
    } on ApiException {
      rethrow;
    } on SocketException {
      throw ApiException(
        'Could not reach the server. Check your connection and the API base URL.',
      );
    } catch (e) {
      throw ApiException('Something went wrong: $e');
    }
  }

  /// Multipart upload, used for `POST /analyses/scan-skin/`.
  static Future<dynamic> postMultipart(
    String path, {
    required String fieldName,
    required File file,
    bool auth = true,
  }) async {
    try {
      final request = http.MultipartRequest('POST', _uri(path));
      request.headers.addAll(await _headers(auth: auth, json: false));
      request.files.add(
        await http.MultipartFile.fromPath(fieldName, file.path),
      );
      final streamed = await request.send().timeout(
            const Duration(seconds: 60),
          );
      final response = await http.Response.fromStream(streamed);
      return _handle(response);
    } on ApiException {
      rethrow;
    } on SocketException {
      throw ApiException(
        'Could not reach the server. Check your connection and the API base URL.',
      );
    } catch (e) {
      throw ApiException('Something went wrong: $e');
    }
  }
}
