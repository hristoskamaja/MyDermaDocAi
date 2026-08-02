import '../models/recommendation.dart';
import 'api_client.dart';

/// Handles `/conditions/<id>/recommendations/` lookups.
class ConditionService {
  Future<List<Recommendation>> getRecommendations(int conditionId) async {
    final data = await ApiClient.get('/conditions/$conditionId/recommendations/');
    return (data as List)
        .map((e) => Recommendation.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
