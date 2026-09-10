import 'package:flutter/material.dart';

import '../../models/recommendation.dart';
import '../../theme/app_theme.dart';
import '../../widgets/severity_pill.dart';

/// Shared "result" layout used both for a freshly confident scan result
/// and for the History detail screen (reusing the same visual layout,
/// per spec).
class ScanResultView extends StatelessWidget {
  final ImageProvider? image;
  final String conditionName;
  final String severity;
  final double confidence;
  final String? description;
  final String? symptoms;
  final String? treatmentOverview;
  final List<Recommendation> recommendations;
  final bool isLowConfidence;
  final String? primaryActionLabel;
  final VoidCallback? onPrimaryAction;
  final Widget? trailing;

  const ScanResultView({
    super.key,
    this.image,
    required this.conditionName,
    required this.severity,
    required this.confidence,
    this.description,
    this.symptoms,
    this.treatmentOverview,
    this.recommendations = const [],
    this.isLowConfidence = false,
    this.primaryActionLabel,
    this.onPrimaryAction,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    final pct = (confidence * 100).clamp(0, 100);

    final medical = recommendations
        .where((r) => r.type == RecommendationType.medicalConsult)
        .toList();
    final selfCare = recommendations
        .where((r) => r.type == RecommendationType.selfCare)
        .toList();
    final lifestyle = recommendations
        .where((r) => r.type == RecommendationType.lifestyle)
        .toList();

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: image != null
                  ? Image(image: image!, fit: BoxFit.cover)
                  : Container(
                      color: c.surface2,
                      child: Icon(Icons.image_rounded, color: c.textLight, size: 48),
                    ),
            ),
          ),
          const SizedBox(height: 18),
          if (isLowConfidence)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: SeverityPill(severity: severity, isUncertain: true),
            )
          else
            SeverityPill(severity: severity),
          const SizedBox(height: 10),
          Text(
            conditionName,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: c.text),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Text(
                'Confidence',
                style: TextStyle(color: c.textMuted, fontWeight: FontWeight.w600, fontSize: 13),
              ),
              const Spacer(),
              Text(
                '${pct.toStringAsFixed(0)}%',
                style: TextStyle(color: c.text, fontWeight: FontWeight.w800, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: (confidence).clamp(0.0, 1.0),
              minHeight: 10,
              backgroundColor: c.surface2,
              valueColor: AlwaysStoppedAnimation<Color>(
                isLowConfidence ? c.uncertain : c.primary,
              ),
            ),
          ),
          if (description != null && description!.trim().isNotEmpty) ...[
            const SizedBox(height: 20),
            Text(
              description!,
              style: TextStyle(color: c.textMuted, fontSize: 14, height: 1.5),
            ),
          ],
          if (symptoms != null && symptoms!.trim().isNotEmpty)
            _infoSection(c, 'SYMPTOMS', symptoms!),
          if (treatmentOverview != null && treatmentOverview!.trim().isNotEmpty)
            _infoSection(c, 'TREATMENT OVERVIEW', treatmentOverview!),
          if (recommendations.isNotEmpty) ...[
            const SizedBox(height: 26),
            if (medical.isNotEmpty)
              _recSection(c, 'SEE A DOCTOR', c.high, c.highSoft, medical),
            if (selfCare.isNotEmpty)
              _recSection(c, 'SELF-CARE', c.low, c.lowSoft, selfCare),
            if (lifestyle.isNotEmpty)
              _recSection(c, 'LIFESTYLE', c.primary, c.primarySoft, lifestyle),
          ],
          const SizedBox(height: 22),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: c.surface2,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: c.border),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.info_outline_rounded, color: c.textMuted, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'AI-generated estimate — not a medical diagnosis. Always '
                    'consult a dermatologist for concerning changes.',
                    style: TextStyle(color: c.textMuted, fontSize: 12.5, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
          if (primaryActionLabel != null && onPrimaryAction != null) ...[
            const SizedBox(height: 22),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onPrimaryAction,
                child: Text(primaryActionLabel!),
              ),
            ),
          ],
          if (trailing != null) ...[
            const SizedBox(height: 28),
            Divider(color: c.border),
            const SizedBox(height: 20),
            trailing!,
          ],
        ],
      ),
    );
  }

  Widget _infoSection(AppColors c, String title, String body) {
    return Padding(
      padding: const EdgeInsets.only(top: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: c.textMuted,
              fontWeight: FontWeight.w800,
              fontSize: 12,
              letterSpacing: 0.6,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: TextStyle(color: c.textMuted, fontSize: 14, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _recSection(
    AppColors c,
    String title,
    Color color,
    Color soft,
    List<Recommendation> items,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w800,
              fontSize: 12,
              letterSpacing: 0.6,
            ),
          ),
          const SizedBox(height: 10),
          ...items.map(
            (r) => Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: soft,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    r.name,
                    style: TextStyle(
                      color: c.text,
                      fontWeight: FontWeight.w700,
                      fontSize: 13.5,
                    ),
                  ),
                  if (r.description.trim().isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      r.description,
                      style: TextStyle(color: c.textMuted, fontSize: 12.5, height: 1.4),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
