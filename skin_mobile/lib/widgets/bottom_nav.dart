import 'package:flutter/material.dart';

import '../l10n/locale_context.dart';
import '../theme/app_theme.dart';

/// Persistent bottom navigation bar shown on Home / History / Profile.
/// The "Scan" item does not represent a tab body — selecting it should
/// push straight into the scan capture flow (handled by the parent).
class AppBottomNav extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const AppBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    return Container(
      decoration: BoxDecoration(
        color: c.surface,
        border: Border(top: BorderSide(color: c.border)),
      ),
      child: SafeArea(
        child: BottomNavigationBar(
          currentIndex: currentIndex,
          onTap: onTap,
          backgroundColor: c.surface,
          elevation: 0,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.home_rounded),
              label: context.tr('nav.home'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.camera_alt_rounded),
              label: context.tr('nav.scan'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.history_rounded),
              label: context.tr('nav.history'),
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.person_rounded),
              label: context.tr('nav.profile'),
            ),
          ],
        ),
      ),
    );
  }
}
