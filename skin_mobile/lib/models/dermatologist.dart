/// Represents a single entry in the manually-curated dermatologist
/// directory (`GET /dermatologists/`). This list is typed in by hand by an
/// admin through the React admin panel - it is never scraped or
/// auto-populated, so most fields beyond `name` are optional.
class Dermatologist {
  final int id;
  final String name;
  final String? clinicName;
  final String? city;
  final String? address;
  final String? phone;
  final String? website;
  final String? notes;

  Dermatologist({
    required this.id,
    required this.name,
    this.clinicName,
    this.city,
    this.address,
    this.phone,
    this.website,
    this.notes,
  });

  factory Dermatologist.fromJson(Map<String, dynamic> json) {
    return Dermatologist(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      clinicName: json['clinic_name'] as String?,
      city: json['city'] as String?,
      address: json['address'] as String?,
      phone: json['phone'] as String?,
      website: json['website'] as String?,
      notes: json['notes'] as String?,
    );
  }
}
