import 'package:flutter/material.dart';

import '../l10n/locale_context.dart';
import '../theme/app_theme.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    return Scaffold(
      backgroundColor: c.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Column(
            children: [
              const Spacer(flex: 3),
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [c.primary, c.primaryDeep],
                  ),
                  borderRadius: BorderRadius.circular(28),
                  boxShadow: [
                    BoxShadow(
                      color: c.primary.withOpacity(0.35),
                      blurRadius: 24,
                      offset: const Offset(0, 12),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.document_scanner_rounded,
                  color: Colors.white,
                  size: 46,
                ),
              ),
              const SizedBox(height: 32),
              Text(
                'DermaScanAI',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w800,
                  color: c.text,
                ),
              ),
              const SizedBox(height: 14),
              Text(
                context.tr('onboarding.tagline'),
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  height: 1.5,
                  color: c.textMuted,
                ),
              ),
              const Spacer(flex: 4),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pushReplacementNamed('/login');
                  },
                  child: Text(context.tr('onboarding.getStarted')),
                ),
              ),
              const SizedBox(height: 18),
              Text(
                context.tr('onboarding.disclaimer'),
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12, color: c.textLight),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
