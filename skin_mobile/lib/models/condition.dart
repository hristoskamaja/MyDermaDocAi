/// Represents a skin condition, as nested in the analysis detail /
/// scan-skin responses: `{id, key, name, description, symptoms, severity,
/// category, image}`.
class Condition {
  final int id;
  final String key;
  final String name;
  final String? description;
  final String? symptoms;
  final String severity;
  final String category;
  final String? image;

  Condition({
    required this.id,
    required this.key,
    required this.name,
    this.description,
    this.symptoms,
    required this.severity,
    required this.category,
    this.image,
  });

  factory Condition.fromJson(Map<String, dynamic> json) {
    return Condition(
      id: json['id'] as int,
      key: json['key'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      symptoms: json['symptoms'] as String?,
      severity: json['severity'] as String? ?? 'LOW',
      category: json['category'] as String? ?? 'OTHER',
      image: json['image'] as String?,
    );
  }
}
