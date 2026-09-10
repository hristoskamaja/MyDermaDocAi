import 'package:flutter/material.dart';

import '../models/analysis.dart';
import '../models/recommendation.dart';
import '../services/analysis_service.dart';
import '../services/api_client.dart';
import '../services/api_config.dart';
import '../services/condition_service.dart';
import '../theme/app_theme.dart';
import '../widgets/analysis_chat_section.dart';
import 'scan/scan_result_view.dart';

/// Detail view for a past scan, opened from History. Reuses the same
/// [ScanResultView] layout as a fresh confident scan result, fetched via
/// `GET /analyses/<id>/` (nested condition) + the recommendations
/// endpoint for that condition id.
class AnalysisDetailScreen extends StatefulWidget {
  final int analysisId;

  const AnalysisDetailScreen({super.key, required this.analysisId});

  @override
  State<AnalysisDetailScreen> createState() => _AnalysisDetailScreenState();
}

class _AnalysisDetailScreenState extends State<AnalysisDetailScreen> {
  final _analysisService = AnalysisService();
  final _conditionService = ConditionService();

  late Future<_DetailData> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<_DetailData> _load() async {
    final detail = await _analysisService.getAnalysisById(widget.analysisId);
    List<Recommendation> recs = [];
    try {
      recs = await _conditionService.getRecommendations(detail.condition.id);
    } catch (_) {
      // Non-fatal: show the analysis even if recommendations fail to load.
    }
    return _DetailData(detail, recs);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    return Scaffold(
      backgroundColor: c.background,
      appBar: AppBar(title: const Text('Scan details')),
      body: FutureBuilder<_DetailData>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            final message = snapshot.error is ApiException
                ? (snapshot.error as ApiException).message
                : 'Could not load this scan.';
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.error_outline_rounded, color: c.high, size: 40),
                    const SizedBox(height: 12),
                    Text(message, textAlign: TextAlign.center, style: TextStyle(color: c.textMuted)),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => setState(() => _future = _load()),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }
          final data = snapshot.data!;
          final detail = data.detail;
          final imageProvider = detail.image != null && detail.image!.isNotEmpty
              ? NetworkImage(resolveMediaUrl(detail.image!))
              : null;
          return ScanResultView(
            image: imageProvider,
            conditionName: detail.condition.name,
            severity: detail.condition.severity,
            confidence: detail.confidence,
            description: detail.condition.description,
            symptoms: detail.condition.symptoms,
            treatmentOverview: detail.condition.treatmentOverview,
            recommendations: data.recommendations,
            isLowConfidence: detail.isLowConfidence,
            trailing: AnalysisChatSection(analysisId: detail.id),
          );
        },
      ),
    );
  }
}

class _DetailData {
  final AnalysisDetail detail;
  final List<Recommendation> recommendations;
  _DetailData(this.detail, this.recommendations);
}
