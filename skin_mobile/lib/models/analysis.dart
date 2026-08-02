import 'condition.dart';

/// Flat list item as returned by `GET /analyses/my-analyses/`.
/// Note: this shape gives flat `condition_name` / `severity` strings,
/// NOT a nested `condition` object (that only appears in the detail /
/// scan-skin responses).
class AnalysisListItem {
  final int id;
  final String analysisKey;
  final String conditionName;
  final String severity;
  final double confidence;
  final bool isLowConfidence;
  final String createdAt;

  AnalysisListItem({
    required this.id,
    required this.analysisKey,
    required this.conditionName,
    required this.severity,
    required this.confidence,
    required this.isLowConfidence,
    required this.createdAt,
  });

  factory AnalysisListItem.fromJson(Map<String, dynamic> json) {
    return AnalysisListItem(
      id: json['id'] as int,
      analysisKey: json['analysis_key'] as String? ?? '',
      conditionName: json['condition_name'] as String? ?? 'Unknown',
      severity: json['severity'] as String? ?? 'LOW',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      isLowConfidence: json['is_low_confidence'] as bool? ?? false,
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}

/// Detailed analysis as returned by `GET /analyses/<id>/` and nested
/// inside the `scan-skin` response's `analysis` key. This shape has a
/// nested `condition` object rather than flat strings.
class AnalysisDetail {
  final int id;
  final String analysisKey;
  final int? user;
  final Condition condition;
  final String? image;
  final double confidence;
  final bool isLowConfidence;
  final String createdAt;

  AnalysisDetail({
    required this.id,
    required this.analysisKey,
    this.user,
    required this.condition,
    this.image,
    required this.confidence,
    required this.isLowConfidence,
    required this.createdAt,
  });

  factory AnalysisDetail.fromJson(Map<String, dynamic> json) {
    return AnalysisDetail(
      id: json['id'] as int,
      analysisKey: json['analysis_key'] as String? ?? '',
      user: json['user'] as int?,
      condition: Condition.fromJson(
        json['condition'] as Map<String, dynamic>,
      ),
      image: json['image'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      isLowConfidence: json['is_low_confidence'] as bool? ?? false,
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}

/// The `prediction` block inside the `scan-skin` response.
class Prediction {
  final String conditionKey;
  final String conditionName;
  final String severity;
  final double confidence;
  final bool isLowConfidence;

  Prediction({
    required this.conditionKey,
    required this.conditionName,
    required this.severity,
    required this.confidence,
    required this.isLowConfidence,
  });

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      conditionKey: json['condition_key'] as String? ?? '',
      conditionName: json['condition_name'] as String? ?? 'Unknown',
      severity: json['severity'] as String? ?? 'LOW',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      isLowConfidence: json['is_low_confidence'] as bool? ?? false,
    );
  }
}

/// Full response of `POST /analyses/scan-skin/`.
class ScanResponse {
  final String message;
  final Prediction prediction;
  final AnalysisDetail analysis;

  ScanResponse({
    required this.message,
    required this.prediction,
    required this.analysis,
  });

  factory ScanResponse.fromJson(Map<String, dynamic> json) {
    return ScanResponse(
      message: json['message'] as String? ?? '',
      prediction: Prediction.fromJson(
        json['prediction'] as Map<String, dynamic>,
      ),
      analysis: AnalysisDetail.fromJson(
        json['analysis'] as Map<String, dynamic>,
      ),
    );
  }
}
