import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../l10n/locale_context.dart';
import '../models/dermatologist.dart';
import '../services/dermatologist_service.dart';
import '../theme/app_theme.dart';
import '../widgets/page_hero_header.dart';

/// Simple, read-only list of dermatologists. The list itself is maintained
/// by hand by an admin through the React admin panel - nothing here is
/// scraped or auto-populated, so an empty list is an expected, normal
/// state (not an error) and must say so clearly.
class DermatologistListScreen extends StatefulWidget {
  const DermatologistListScreen({super.key});

  @override
  State<DermatologistListScreen> createState() =>
      _DermatologistListScreenState();
}

class _DermatologistListScreenState extends State<DermatologistListScreen> {
  final _dermatologistService = DermatologistService();
  late Future<List<Dermatologist>> _future;

  @override
  void initState() {
    super.initState();
    _future = _dermatologistService.getAll();
  }

  Future<void> _refresh() async {
    final next = _dermatologistService.getAll();
    setState(() => _future = next);
    await next;
  }

  Future<void> _call(String phone) async {
    final uri = Uri(scheme: 'tel', path: phone);
    await _launch(uri);
  }

  Future<void> _openWebsite(String website) async {
    var url = website.trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://$url';
    }
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    await _launch(uri);
  }

  Future<void> _launch(Uri uri) async {
    try {
      final ok = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!ok && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.tr('findDermatologist.linkError'))),
        );
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.tr('findDermatologist.linkError'))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    return Scaffold(
      backgroundColor: c.background,
      appBar: PageHeroHeader(
        title: context.tr('findDermatologist.title'),
        subtitle: context.tr('findDermatologist.subtitle'),
        showBackButton: true,
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<List<Dermatologist>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return _messageState(
                c,
                icon: Icons.error_outline_rounded,
                iconColor: c.high,
                text: '${context.tr('findDermatologist.loadError')}\n'
                    '${snapshot.error}',
              );
            }
            final items = snapshot.data ?? [];
            if (items.isEmpty) {
              return _messageState(
                c,
                icon: Icons.person_search_rounded,
                iconColor: c.textLight,
                text: context.tr('findDermatologist.empty'),
              );
            }
            return ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20),
              itemCount: items.length,
              itemBuilder: (context, index) => _dermatologistCard(context, c, items[index]),
            );
          },
        ),
      ),
    );
  }

  Widget _messageState(
    AppColors c, {
    required IconData icon,
    required Color iconColor,
    required String text,
  }) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            children: [
              Icon(icon, color: iconColor, size: 36),
              const SizedBox(height: 12),
              Text(
                text,
                textAlign: TextAlign.center,
                style: TextStyle(color: c.textMuted, height: 1.4),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _dermatologistCard(BuildContext context, AppColors c, Dermatologist d) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            d.name,
            style: TextStyle(
              fontWeight: FontWeight.w800,
              color: c.text,
              fontSize: 16,
            ),
          ),
          if (d.clinicName != null && d.clinicName!.trim().isNotEmpty) ...[
            const SizedBox(height: 3),
            Text(
              d.clinicName!,
              style: TextStyle(color: c.textMuted, fontSize: 13),
            ),
          ],
          if ((d.city != null && d.city!.trim().isNotEmpty) ||
              (d.address != null && d.address!.trim().isNotEmpty)) ...[
            const SizedBox(height: 10),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.place_outlined, color: c.textLight, size: 16),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    [d.city, d.address]
                        .where((s) => s != null && s.trim().isNotEmpty)
                        .join(' · '),
                    style: TextStyle(color: c.textMuted, fontSize: 13, height: 1.4),
                  ),
                ),
              ],
            ),
          ],
          if (d.notes != null && d.notes!.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.notes_rounded, color: c.textLight, size: 16),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    d.notes!,
                    style: TextStyle(color: c.textMuted, fontSize: 13, height: 1.4),
                  ),
                ),
              ],
            ),
          ],
          if ((d.phone != null && d.phone!.trim().isNotEmpty) ||
              (d.website != null && d.website!.trim().isNotEmpty)) ...[
            const SizedBox(height: 14),
            Row(
              children: [
                if (d.phone != null && d.phone!.trim().isNotEmpty)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _call(d.phone!),
                      icon: const Icon(Icons.call_rounded, size: 17),
                      label: Text(context.tr('findDermatologist.call')),
                    ),
                  ),
                if (d.phone != null &&
                    d.phone!.trim().isNotEmpty &&
                    d.website != null &&
                    d.website!.trim().isNotEmpty)
                  const SizedBox(width: 10),
                if (d.website != null && d.website!.trim().isNotEmpty)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _openWebsite(d.website!),
                      icon: const Icon(Icons.link_rounded, size: 17),
                      label: Text(context.tr('findDermatologist.website')),
                    ),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
