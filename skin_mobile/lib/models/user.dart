class AppUser {
  final int id;
  final String username;
  final String fullName;
  final String email;
  final String role;
  final String createdAt;

  AppUser({
    required this.id,
    required this.username,
    required this.fullName,
    required this.email,
    required this.role,
    required this.createdAt,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as int,
      username: json['username'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      email: json['email'] as String? ?? '',
      role: json['role'] as String? ?? '',
      createdAt: json['created_at'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'full_name': fullName,
      'email': email,
      'role': role,
      'created_at': createdAt,
    };
  }

  /// First name derived from fullName, used for personalized greetings.
  String get firstName {
    final trimmed = fullName.trim();
    if (trimmed.isEmpty) return username;
    return trimmed.split(RegExp(r'\s+')).first;
  }

  /// Initials derived from fullName, used for the avatar placeholder.
  String get initials {
    final trimmed = fullName.trim();
    if (trimmed.isEmpty) {
      return username.isNotEmpty ? username[0].toUpperCase() : '?';
    }
    final parts = trimmed.split(RegExp(r'\s+'));
    if (parts.length == 1) {
      return parts.first.substring(0, 1).toUpperCase();
    }
    return (parts.first.substring(0, 1) + parts.last.substring(0, 1))
        .toUpperCase();
  }
}
