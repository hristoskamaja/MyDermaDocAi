import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  Future<void> _showChangePasswordDialog(BuildContext context) async {
    final formKey = GlobalKey<FormState>();
    final oldController = TextEditingController();
    final newController = TextEditingController();
    String? error;
    bool loading = false;

    await showDialog(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setState) {
            final c = context.colors;
            return AlertDialog(
              backgroundColor: c.surface,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Text('Change password'),
              content: Form(
                key: formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (error != null) ...[
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(10),
                        margin: const EdgeInsets.only(bottom: 12),
                        decoration: BoxDecoration(
                          color: c.highSoft,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(error!, style: TextStyle(color: c.high, fontSize: 12.5)),
                      ),
                    ],
                    TextFormField(
                      controller: oldController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Current password'),
                      validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: newController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'New password'),
                      validator: (v) {
                        if (v == null || v.isEmpty) return 'Required';
                        if (v.length < 8) return 'At least 8 characters';
                        return null;
                      },
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: loading ? null : () => Navigator.of(dialogContext).pop(),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: loading
                      ? null
                      : () async {
                          if (!formKey.currentState!.validate()) return;
                          setState(() {
                            loading = true;
                            error = null;
                          });
                          final auth = dialogContext.read<AuthProvider>();
                          final ok = await auth.changePassword(
                            oldPassword: oldController.text,
                            newPassword: newController.text,
                          );
                          if (ok) {
                            if (dialogContext.mounted) Navigator.of(dialogContext).pop();
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Password changed successfully.')),
                              );
                            }
                          } else {
                            setState(() {
                              loading = false;
                              error = auth.lastError ?? 'Could not change password.';
                            });
                          }
                        },
                  child: loading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2.2, color: Colors.white),
                        )
                      : const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    final auth = context.watch<AuthProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final user = auth.currentUser;

    return Scaffold(
      backgroundColor: c.background,
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Center(
            child: Column(
              children: [
                Container(
                  width: 84,
                  height: 84,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [c.primary, c.primaryDeep],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      user?.initials ?? '?',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  user?.fullName ?? '',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: c.text),
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? '',
                  style: TextStyle(fontSize: 13, color: c.textMuted),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          _settingsCard(
            c,
            children: [
              _settingsTile(
                c,
                icon: Icons.lock_outline_rounded,
                title: 'Change password',
                onTap: () => _showChangePasswordDialog(context),
              ),
              Divider(color: c.border, height: 1),
              _settingsSwitchTile(
                c,
                icon: Icons.dark_mode_outlined,
                title: 'Dark theme',
                value: themeProvider.isDark,
                onChanged: (v) => themeProvider.setDark(v),
              ),
            ],
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () async {
                await context.read<AuthProvider>().logout();
                if (context.mounted) {
                  Navigator.of(context).pushNamedAndRemoveUntil('/onboarding', (r) => false);
                }
              },
              icon: Icon(Icons.logout_rounded, color: c.high),
              label: Text('Log out', style: TextStyle(color: c.high)),
              style: OutlinedButton.styleFrom(side: BorderSide(color: c.high.withOpacity(0.4))),
            ),
          ),
        ],
      ),
    );
  }

  Widget _settingsCard(AppColors c, {required List<Widget> children}) {
    return Container(
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: c.border),
      ),
      child: Column(children: children),
    );
  }

  Widget _settingsTile(
    AppColors c, {
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      onTap: onTap,
      leading: Icon(icon, color: c.primary),
      title: Text(title, style: TextStyle(color: c.text, fontWeight: FontWeight.w600)),
      trailing: Icon(Icons.chevron_right_rounded, color: c.textLight),
    );
  }

  Widget _settingsSwitchTile(
    AppColors c, {
    required IconData icon,
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return ListTile(
      leading: Icon(icon, color: c.primary),
      title: Text(title, style: TextStyle(color: c.text, fontWeight: FontWeight.w600)),
      trailing: Switch(value: value, onChanged: onChanged, activeColor: c.primary),
    );
  }
}
