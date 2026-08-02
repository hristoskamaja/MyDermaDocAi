import 'package:flutter/material.dart';

import '../screens/history_screen.dart';
import '../screens/home_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/scan/scan_flow_screen.dart';
import 'bottom_nav.dart';

/// Wraps Home / History / Profile with the persistent bottom nav and
/// handles nav state. The "Scan" nav item does not switch tabs — it
/// pushes the scan capture flow directly, per spec.
class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _tabIndex = 0;

  // Maps bottom-nav index -> tab page index (nav index 1 is "Scan" and
  // is handled separately via push, so it has no corresponding page).
  final _pages = const [
    HomeScreen(),
    HistoryScreen(),
    ProfileScreen(),
  ];

  void _onNavTap(int navIndex) {
    if (navIndex == 1) {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const ScanFlowScreen()),
      );
      return;
    }
    final pageIndex = navIndex < 1 ? navIndex : navIndex - 1;
    setState(() => _tabIndex = pageIndex);
  }

  int get _navIndex => _tabIndex < 1 ? _tabIndex : _tabIndex + 1;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _tabIndex, children: _pages),
      bottomNavigationBar: AppBottomNav(
        currentIndex: _navIndex,
        onTap: _onNavTap,
      ),
    );
  }
}
