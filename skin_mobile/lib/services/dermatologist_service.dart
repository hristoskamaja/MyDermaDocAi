import '../models/dermatologist.dart';
import 'api_client.dart';

/// Handles `/dermatologists/` lookups. Read-only from the mobile app - the
/// list can come from the admin typing rows in by hand, or from
/// scrape_dermatologists.py on the backend (see core/models.py).
class DermatologistService {
  /// Pass [latitude]/[longitude] (real GPS - see dermatologist_list_screen.dart)
  /// to have the backend sort results by distance and fill in each
  /// [Dermatologist.distanceKm]. Omit them to get the plain alphabetical list.
  ///
  /// [nearCity] is the manual fallback/override (same idea as the web app's
  /// city picker - see FindDermatologist.jsx): if given, it wins over
  /// lat/lng and the backend sorts by distance from that city's center
  /// (core/services/geo.py's _resolve_origin checks lat/lng first, so only
  /// pass one or the other from the caller side to keep behavior obvious).
  Future<List<Dermatologist>> getAll({
    double? latitude,
    double? longitude,
    String? nearCity,
  }) async {
    var path = '/dermatologists/';
    if (nearCity != null && nearCity.trim().isNotEmpty) {
      path = '/dermatologists/?near_city=${Uri.encodeQueryComponent(nearCity.trim())}';
    } else if (latitude != null && longitude != null) {
      path = '/dermatologists/?lat=$latitude&lng=$longitude';
    }
    final data = await ApiClient.get(path);
    return (data as List)
        .map((e) => Dermatologist.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
