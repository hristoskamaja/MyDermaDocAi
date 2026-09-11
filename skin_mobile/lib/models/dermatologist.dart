/// Represents a single entry in the dermatologist directory
/// (`GET /dermatologists/`). Rows can come from the admin typing them in
/// by hand through the React admin panel, or from scrape_dermatologists.py
/// on the backend - either way most fields beyond `name` are optional.
class Dermatologist {
  final int id;
  final String name;
  final String? clinicName;
  final String? city;
  final String? address;
  final String? phone;
  final String? website;
  final String? notes;

  /// Only present when the request included ?lat=&lng= (see
  /// DermatologistService.getAll) - how far this entry is from that point,
  /// in kilometers. Null otherwise (never guess/compute it client-side).
  final double? distanceKm;

  Dermatologist({
    required this.id,
    required this.name,
    this.clinicName,
    this.city,
    this.address,
    this.phone,
    this.website,
    this.notes,
    this.distanceKm,
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
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
    );
  }
}
