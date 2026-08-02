import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/analysis.dart';
import '../providers/auth_provider.dart';
import '../services/analysis_service.dart';
import '../theme/app_theme.dart';
import '../widgets/severity_pill.dart';
import 'scan/scan_flow_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _analysisService = AnalysisService();
  late Future<List<AnalysisListItem>> _recentFuture;

  @override
  void initState() {
    super.initState();
    _recentFuture = _load();
  }

  Future<List<AnalysisListItem>> _load() async {
    final all = await _analysisService.getMyAnalyses();
    all.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return all.take(3).toList();
  }

  Future<void> _refresh() async {
    setState(() => _recentFuture = _load());
    await _recentFuture;
  }

  void _startScan() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const ScanFlowScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    final user = context.watch<AuthProvider>().currentUser;
    final greetName = user?.firstName ?? 'there';

    return Scaffold(
      backgroundColor: c.background,
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeroWithCta(c, greetName),
              const SizedBox(height: 8),
              _buildRecentScans(c),
              const SizedBox(height: 24),
              _buildTips(c),
              const SizedBox(height: 20),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Text(
                  'AI-generated estimates are not a medical diagnosis.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: c.textLight),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeroWithCta(AppColors c, String greetName) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 56),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [c.primary, c.primaryDeep],
            ),
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(28),
              bottomRight: Radius.circular(28),
            ),
          ),
          child: SafeArea(
            bottom: false,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Hello, $greetName',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'How does your skin look today?',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 15,
                  ),
                ),
              ],
            ),
          ),
        ),
        Positioned(
          left: 24,
          right: 24,
          bottom: -36,
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(20),
              onTap: _startScan,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: c.surface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: c.border),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.08),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: c.primarySoft,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Icon(Icons.camera_alt_rounded, color: c.primary, size: 26),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Scan your skin',
                            style: TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w800,
                              color: c.text,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Camera or gallery',
                            style: TextStyle(fontSize: 13, color: c.textMuted),
                          ),
                        ],
                      ),
                    ),
                    Icon(Icons.arrow_forward_ios_rounded, color: c.textLight, size: 16),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecentScans(AppColors c) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 56, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent scans',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: c.text),
          ),
          const SizedBox(height: 12),
          FutureBuilder<List<AnalysisListItem>>(
            future: _recentFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              if (snapshot.hasError) {
                return _infoBox(c, 'Could not load your recent scans.\n${snapshot.error}');
              }
              final items = snapshot.data ?? [];
              if (items.isEmpty) {
                return _infoBox(c, 'No scans yet. Take your first scan to see results here.');
              }
              return Column(
                children: items.map((a) => _scanRow(c, a)).toList(),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _infoBox(AppColors c, String text) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: c.surface2,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(text, style: TextStyle(color: c.textMuted)),
    );
  }

  Widget _scanRow(AppColors c, AnalysisListItem a) {
    final date = _formatDate(a.createdAt);
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.border),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  a.conditionName,
                  style: TextStyle(fontWeight: FontWeight.w700, color: c.text, fontSize: 15),
                ),
                const SizedBox(height: 4),
                Text(date, style: TextStyle(color: c.textMuted, fontSize: 12)),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (a.isLowConfidence)
            const SeverityPill(severity: '', isUncertain: true)
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                SeverityPill(severity: a.severity),
                const SizedBox(height: 4),
                Text(
                  '${(a.confidence * 100).toStringAsFixed(0)}%',
                  style: TextStyle(color: c.textMuted, fontSize: 12),
                ),
              ],
            ),
        ],
      ),
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso).toLocal();
      return DateFormat('MMM d, y').format(dt);
    } catch (_) {
      return iso;
    }
  }

  Widget _buildTips(AppColors c) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Better photos, better estimates',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: c.text),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _tipCard(c, Icons.wb_sunny_rounded, 'Good lighting',
                    'Scan in natural daylight, avoid harsh shadows.'),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _tipCard(c, Icons.crop_free_rounded, 'Fill the frame',
                    'Get close so the lesion fills most of the photo.'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _tipCard(AppColors c, IconData icon, String title, String body) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: c.primarySoft,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: c.primary),
          const SizedBox(height: 10),
          Text(title, style: TextStyle(fontWeight: FontWeight.w700, color: c.text, fontSize: 13)),
          const SizedBox(height: 4),
          Text(body, style: TextStyle(color: c.textMuted, fontSize: 12, height: 1.3)),
        ],
      ),
    );
  }
}
