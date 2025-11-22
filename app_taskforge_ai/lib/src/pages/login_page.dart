import 'package:flutter/material.dart';
// dart:convert no longer needed here; kept intentionally commented for future use
// import 'dart:convert';
import 'package:provider/provider.dart';

import '../services/auth_service.dart';
import 'agents_list_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool loading = false;

  Future<void> doLogin() async {
    setState(() => loading = true);
    final auth = Provider.of<AuthService>(context, listen: false);
    try {
      final ok = await auth.login(_email.text, _password.text);
      if (ok) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Login successful')));
        Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const AgentsListPage()));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Login failed')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error')));
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SizedBox(
          width: 420,
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('TaskForge', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 12),
                  TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
                  const SizedBox(height: 8),
                  TextField(controller: _password, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: loading ? null : doLogin, child: loading ? const CircularProgressIndicator() : const Text('Login'))
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
