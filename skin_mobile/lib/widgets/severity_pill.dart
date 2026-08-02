import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Small rounded pill showing a severity level (LOW/MEDIUM/HIGH) with the
/// matching color from AppColors, or an "Uncertain" badge in the
/// uncertain color when [isUncertain] is true (kept visually distinct
/// from severity colors so it never reads as a specific severity).
class SeverityPill extends StatelessWidget {
  final String severity;
  final bool isUncertain;

  const SeverityPill({
    super.key,
    required this.severity,
    this.isUncertain = false,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    if (isUncertain) {
      return _pill('Uncertain', c.uncertain, c.uncertainSoft);
    }

    final colors = AppColors.severityColors(c, severity);
    return _pill(_label(severity), colors[0], colors[1]);
  }

  String _label(String s) {
    switch (s.toUpperCase()) {
      case 'HIGH':
        return 'High';
      case 'MEDIUM':
        return 'Medium';
      case 'LOW':
        return 'Low';
      default:
        return s;
    }
  }

  Widget _pill(String label, Color fg, Color bg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: fg,
          fontWeight: FontWeight.w700,
          fontSize: 12,
        ),
      ),
    );
  }
}
