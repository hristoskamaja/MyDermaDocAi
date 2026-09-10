import '../models/dermatologist.dart';
import 'api_client.dart';

/// Handles `/dermatologists/` lookups. Read-only from the mobile app - the
/// list itself is maintained by hand by an admin through the React admin
/// panel, never written to from here.
class DermatologistService {
  Future<List<Dermatologist>> getAll() async {
    final data = await ApiClient.get('/dermatologists/');
    return (data as List)
        .map((e) => Dermatologist.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
